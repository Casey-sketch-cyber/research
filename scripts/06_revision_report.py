"""Export independently audited G2 reruns, budget projections and review response."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
from types import SimpleNamespace

import numpy as np
import pandas as pd
from scipy import ndimage
from tqdm import tqdm

from fea.config import config_hash, load_config
from fea.furniture.library import library, rectangles
from fea.furniture.candidates import generate_candidates
from fea.geometry.raster import rasterize, FURNISHABLE
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli, start_run, write_json, sha256_file
from fea.solve.cpsat import relaxed_capacity_bound
from fea.validate import validate_layout, _reachable


def table(frame):
    """Portable Markdown with no optional table dependency."""
    clean=frame.copy().fillna('')
    return '| '+' | '.join(clean.columns)+' |\n| '+' | '.join(['---']*len(clean.columns))+' |\n'+'\n'.join(
        '| '+' | '.join(str(v) for v in row)+' |' for row in clean.itertuples(index=False,name=None))


def freeze_configuration(selection,config_path="config/project.yaml"):
    """Record the empirically selected solver parameters, retaining YAML comments."""
    path=Path(config_path);text=path.read_text()
    text=re.sub(r'^  num_workers: .*$',f"  num_workers: {selection['workers']}",text,flags=re.M)
    text=re.sub(r'^  time_limit_s: .*$',f"  time_limit_s: {selection['time_limit_s']}",text,flags=re.M)
    if '  reachability_round_s:' not in text:
        text=text.replace('  reachability_max_iterations: 30','  reachability_max_iterations: 30\n  reachability_round_s: 5.0')
    path.write_text(text,encoding='utf-8')
    return load_config(path)


def stratified_subset(frame, count, seed):
    """Select an exact-size subset by NIA bin (and room count), with a fixed seed."""
    if count>=len(frame):return frame.copy()
    rng=np.random.default_rng(seed)
    columns=['nia_bin_2m2','n_rooms']
    groups={key:list(rng.permutation(g.index)) for key,g in frame.sort_values('unit_key').groupby(columns,sort=True)}
    quotas={k:len(v)*count/len(frame) for k,v in groups.items()}
    chosen={k:0 for k in groups};selected=[]
    while len(selected)<count:
        key=max(sorted(groups),key=lambda k:(quotas[k]-chosen[k])/max(quotas[k],1))
        selected.append(groups[key].pop());chosen[key]+=1
        if not groups[key]:del groups[key]
    return frame.loc[selected]


def projections(config,summary,frame):
    """Calibrate source-specific costs to measured parallel wall time, then add 15%."""
    original=Path('results/corpus/expA_sample_uncapped_G2.csv')
    if not original.exists():original.write_bytes(Path('results/corpus/expA_sample.csv').read_bytes())
    sample=pd.read_csv(original)
    concurrent=summary['concurrent_solves']
    factor=summary['wall_time_s']*concurrent/frame.solve_time_s.sum()
    unit_cost=(frame.groupby('source').solve_time_s.mean()*12/concurrent*factor/3600*1.15).to_dict()
    counts=sample.groupby('source').size().to_dict();before=dict(counts)
    duration=lambda n:sum(n[s]*unit_cost[s] for s in n)
    actions=[]
    for source,minimum in [('D1',500),('D2',200)]:
        if duration(counts)<=36:break
        reduction=min(max(0,counts[source]-minimum),math.ceil((duration(counts)-36)/unit_cost[source]))
        if reduction:counts[source]-=reduction;actions.append(dict(source=source,reduction=reduction,remaining=counts[source]))
    small=sample[(sample.source=='D3')&(sample.nia_m2<=20+1e-6)]
    large=sample[(sample.source=='D3')&(sample.nia_m2>20+1e-6)]
    if duration(counts)>36:
        minimum=len(small)+min(60,len(large))
        reduction=min(max(0,counts['D3']-minimum),math.ceil((duration(counts)-36)/unit_cost['D3']))
        if reduction:counts['D3']-=reduction;actions.append(dict(source='D3_large_only',reduction=reduction,remaining=counts['D3']))
    chosen=[]
    for source in ('D1','D2'):
        chosen.append(stratified_subset(sample[sample.source==source],counts[source],config['seed']))
    chosen.extend([small,stratified_subset(large,counts['D3']-len(small),config['seed'])])
    retained=pd.concat(chosen).sort_values(['source','nia_m2','unit_key'])
    retained['analysis_config_hash']=config_hash(config)
    retained.to_csv('results/corpus/expA_sample.csv',index=False)
    pd.DataFrame([dict(source=s,uncapped_units=before[s],retained_units=counts[s],
        measured_mean_solve_s=float(frame[frame.source==s].solve_time_s.mean()),
        calibrated_parallel_hours_per_unit_with_margin=unit_cost[s],
        uncapped_hours_with_margin=before[s]*unit_cost[s],retained_hours_with_margin=counts[s]*unit_cost[s]) for s in counts]).to_csv('results/pilot/runtime_projection.csv',index=False)
    all_units=pd.read_csv('results/corpus/corpus_units.csv')
    all_units['in_expA_sample']=all_units.unit_key.isin(retained.unit_key)
    all_units['analysis_config_hash']=config_hash(config)
    all_units.to_csv('results/corpus/corpus_units.csv',index=False)
    strata=all_units[all_units.include].groupby(['source','nia_bin_2m2','n_rooms']).agg(
        full_unique=('unit_key','size'),sampled=('in_expA_sample','sum')).reset_index()
    strata['config_hash']=config_hash(config);strata['code_hash']=summary['code_hash']
    strata.to_csv('results/corpus/sample_strata.csv',index=False)
    count_table=pd.read_csv('results/corpus/counts.csv')
    count_table['expA_sample']=count_table.source.map(counts)
    count_table['analysis_config_hash']=config_hash(config)
    count_table.to_csv('results/corpus/counts.csv',index=False)
    # K is a workload projection, not an observed K result. Its parametric solver
    # is not implemented/run at G2. Use the full 20 s cap, calibrated concurrency.
    settings=config['experiments']['K_kit_design']
    d3=all_units[(all_units.source=='D3')&all_units.include]
    lo,hi=settings['target']['nia_m2']
    target=d3[(d3.nia_m2>=lo-1e-6)&(d3.nia_m2<=hi+1e-6)]
    units={u['unit_key']:u for u in json.loads(Path('results/pilot/pilot_units.json').read_text())['units']}
    mapping=pd.read_csv('results/pilot/d3_regeneration_mapping.csv')
    mapping['retained_analysis_sample']=mapping.new_unit_key.isin(retained.unit_key)
    mapping['analysis_config_hash']=config_hash(config)
    mapping.to_csv('results/pilot/d3_regeneration_mapping.csv',index=False)
    mapping=mapping.set_index('old_unit_key')
    held=target.unit_key.map(lambda k:math.isclose(mapping.loc[k,'aspect_ratio'],settings['holdout']['aspect_ratio']) or
        mapping.loc[k,'entrance_position']==settings['holdout']['entrance_position'])
    train_count=int((~held).sum());holdout_count=int(held.sum())
    real_count=int(((all_units.source.isin(['D1','D2']))&all_units.include&(all_units.nia_m2<=20+1e-6)).sum())
    workloads=[]
    for household in settings['households']:
        combinations=math.prod(len(v['values']) for v in settings['variables'].values()
            if household in v.get('applies_to',settings['households']))
        second=math.ceil(combinations*settings['search']['stages'][0]['keep'])
        search=combinations*min(10,train_count)+second*min(30,train_count)+min(5,second)*train_count
        workloads.append(dict(household=household,combinations=combinations,train_shells=train_count,
            holdout_shells=holdout_count,real_plan_checks=real_count,kit_search_solves=search,
            flat_quality_search_solves=search,bespoke_solves=min(settings['bespoke_subsample'],train_count)*combinations,
            catalogue_and_kit_evaluation_solves=2*(len(target)+real_count),
            flat_kit_evaluation_solves=len(target)+real_count))
    kframe=pd.DataFrame(workloads)
    kcolumns=[c for c in kframe if c.endswith('_solves')]
    kcount=int(kframe[kcolumns].sum().sum())
    overrun=max(0,float(frame.solve_time_s.max())-summary['time_limit_s'])
    per_k=(settings['search']['time_limit_s']+overrun)*factor/concurrent
    kframe['projected_hours_with_margin']=kframe[kcolumns].sum(axis=1)*per_k/3600*1.15
    kframe.to_csv('results/pilot/expK_projection.csv',index=False)
    result=dict(config_hash=config_hash(config),code_hash=summary['code_hash'],
        measured_parallel_factor=factor,margin=.15,uncapped_expA_hours=duration(before),
        retained_expA_hours=duration(counts),source_counts_before=before,source_counts_after=counts,
        caps_applied=actions,D3_small_shells_preserved=len(small),expA_within_36h=duration(counts)<=36,
        expK_projected_solves=kcount,expK_projected_hours=float(kframe.projected_hours_with_margin.sum()),
        expK_within_two_day_timebox=bool(kframe.projected_hours_with_margin.sum()<=48),
        expK_projection_scope='full grid, repeated flat-quality search, per-unit bespoke grid and catalogue/kit/flat transfer evaluations; conservative 20 s cap scaled by pilot throughput',
        expK_caveat='No K solve was run; changed parametric domains and FCIq may change build/search cost. Recheck on a K pilot before its 2-day time box.',
        stopping_rule='Stop for review; no formal experiment is launched by this script.')
    write_json('results/pilot/projection_summary.json',result)
    return result


def zero_diagnosis(unit,household,layout,config,grid):
    """Bound possible service on full anchors before calling a zero genuine."""
    reached=_reachable(grid,np.zeros_like(grid.labels,bool),config['furniture']['meta']['walking_width'])
    items=library(config['furniture'],layout['strategy'])
    poses=generate_candidates(grid,items,config['raster']['orientations_deg'],grid.resolution)
    usable={}
    for name,item in items.items():
        accessible=False
        for x,y,angle in poses[name]:
            for state in item.states:
                _,strips,_=rectangles(state,grid.resolution,int(angle))
                if any(reached[y+dy:y+dy+h,x+dx:x+dx+w].any() for dx,dy,w,h in strips):accessible=True;break
            if accessible:break
        if accessible:
            for number in range(item.max_instances):usable[name+'#'+str(number+1)]=SimpleNamespace(item=item)
    bound=float(relaxed_capacity_bound(usable,household))
    thin=_reachable(grid,np.zeros_like(grid.labels,bool),grid.resolution)
    room_connected=bool(np.any(thin & (grid.labels==FURNISHABLE)))
    wider=rasterize(unit,grid.resolution,max_gap=.3)
    hypothetical=_reachable(wider,np.zeros_like(wider.labels,bool),config['furniture']['meta']['walking_width'])
    gap_evidence=int((hypothetical & ~reached & (grid.labels==FURNISHABLE)).sum())
    if gap_evidence>0 and not np.any(reached & (grid.labels==FURNISHABLE)):
        cause='source_gap_remaining'
    elif not room_connected:
        cause='room_not_connected_in_source'
    elif bound<=1e-12:
        cause='genuinely_infeasible'
    else:
        cause='search_fallback'
    return dict(unit_key=unit.unit_key,source=unit.source,household=household.name,strategy=layout['strategy'],
        cause=cause,full_anchor_empty_access_capacity_upper_bound=bound,
        reachable_furnishable_cells=int((reached & (grid.labels==FURNISHABLE)).sum()),
        diagnostic_030m_gap_new_furnishable_cells=gap_evidence,
        proof_scope='catalogue, independent empty access, full 0.10 m anchors, configured grid; not continuous-world impossibility')


def render_empty(units,config):
    """Review sheets for every frozen empty plan, showing all service approaches."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from fea.viz.corpus import draw_unit
    for source in ('D1','D2','D3'):
        subset=[u for u in units if u.source==source]
        fig,axes=plt.subplots(math.ceil(len(subset)/2),2,figsize=(12,4*math.ceil(len(subset)/2)),layout='constrained')
        for ax,unit in zip(axes.flat,subset):
            grid=rasterize(unit,config['raster']['resolution_m'])
            reached=_reachable(grid,np.zeros_like(grid.labels,bool),config['furniture']['meta']['walking_width'])
            draw_unit(ax,unit,short=True)
            ny,nx=reached.shape;ox,oy=grid.origin;r=grid.resolution
            ax.imshow(np.ma.masked_where(~reached,reached),origin='lower',extent=(ox,ox+nx*r,oy,oy+ny*r),
                cmap='Blues',vmin=0,vmax=1,alpha=.2,interpolation='nearest')
            for i,target in enumerate(grid.service_targets):
                points=np.argwhere(target)
                if len(points):
                    y,x=points.mean(axis=0);ax.text(ox+(x+.5)*r,oy+(y+.5)*r,str(i),
                        color='green' if (target & reached).any() else 'red',fontsize=10,fontweight='bold')
            passed=all((target & reached).any() for target in grid.service_targets)
            ax.set_title(f'{unit.unit_key} | NIA {unit.interior.area:.2f} m² | empty access {passed}',fontsize=9)
            x0,y0,x1,y1=unit.interior.bounds;ax.set_xlim(x0-.3,x1+.3);ax.set_ylim(y0-.3,y1+.3)
        for ax in list(axes.flat)[len(subset):]:ax.set_visible(False)
        fig.legend(handles=[Patch(facecolor='#156d9c',alpha=.2,label='reachable covered area'),
            Patch(facecolor='#d3d3d3',hatch='...',label='walkable kitchen')],loc='outside lower center',ncol=2)
        fig.savefig(f'results/pilot/empty_access_{source}.png',dpi=180);plt.close(fig)



def configure_render_style():
    """Make the kitchen hatch visible without altering measured numerical code."""
    import matplotlib.pyplot as plt
    from fea.viz import corpus
    from matplotlib.image import AxesImage
    # Equal z-order preserves insertion order: coverage sits above floor patches
    # and below furniture that is subsequently drawn. Default images sit underneath.
    AxesImage.zorder=1
    style={"figure.constrained_layout.h_pad":.15,"figure.constrained_layout.w_pad":.08,
           "figure.constrained_layout.hspace":.16,"figure.constrained_layout.wspace":.06}
    plt.rcParams.update(style)
    original=corpus.draw_geometry
    def contrasting_hatch(ax,*args,**kwargs):
        before=len(ax.patches)
        original(ax,*args,**kwargs)
        for patch in list(ax.patches)[before:]:
            if patch.get_hatch():patch.set_edgecolor('#858585')
    corpus.draw_geometry=contrasting_hatch
    return dict(style,kitchen_hatch_edgecolor='#858585',coverage_image_zorder=1)


def render_preparation_views():
    """Use the same geometry renderer with a complete walkable-kitchen legend."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from fea.viz.corpus import draw_unit,COLORS
    units=[Unit.from_dict(u) for u in json.loads(Path('results/corpus/sample_units.json').read_text())['units']]
    legend=[Patch(color=value,label=key.replace('_',' ')) for key,value in COLORS.items()]
    legend.append(Patch(facecolor='#d3d3d3',edgecolor='#858585',hatch='...',label='walkable kitchen'))
    legend.extend(Patch(color=value,label=key) for key,value in [('walls','#333333'),('door','#dc8c18'),('window','#167dcc'),('entrance','#bf2441')])
    for i,unit in enumerate(units):
        fig,ax=plt.subplots(figsize=(7,7),layout='constrained');draw_unit(ax,unit)
        fig.legend(handles=legend,loc='outside lower center',ncol=4,fontsize=8)
        fig.savefig(f'results/corpus/samples/{unit.source}_{i%8+1:02d}.png',dpi=300);plt.close(fig)
    fig,axes=plt.subplots(6,4,figsize=(16,23),layout='constrained')
    for ax,unit in zip(axes.flat,units):draw_unit(ax,unit,short=True)
    fig.legend(handles=legend,loc='outside lower center',ncol=4,fontsize=11)
    fig.savefig('results/corpus/sample_contact_sheet.png',dpi=180);plt.close(fig)


def export(config,selection,render=False):
    root=Path('results/pilot');arm=root/'benchmarks'/selection['selected_arm']
    for name in ('pilot_audit.json','pilot_runtime_projection.json','pilot_tests.json','pilot_access_notes.json','pilot_render_style.json'):
        old=Path('reports')/name;backup=root/'baseline_g2'/('report_'+name)
        if old.exists() and not backup.exists():backup.write_bytes(old.read_bytes())
    summary=json.loads((arm/'summary.json').read_text())
    assert summary['fresh_throughput_measurement']
    assert summary['input_hash']==sha256_file(root/'pilot_units.json'),'Pilot input changed after measurement'
    assert summary['config_hash']==config_hash(config),'Selected benchmark configuration differs'
    selection['config_hash']=config_hash(config)
    write_json(root/'benchmark_selection.json',selection)
    raw=pd.read_csv(arm/'cases.csv');rows=[];audit=[];zeros=[];manifest=[];empty=[]
    households=parse_households(config['households'],config['furniture'])
    units=[Unit.from_dict(u) for u in json.loads((root/'pilot_units.json').read_text())['units']]
    from fea.viz.layouts import render_layout
    import matplotlib.pyplot as plt
    style=configure_render_style()
    for unit in tqdm(units,desc='Export/revalidate/render'):
        grid=rasterize(unit,config['raster']['resolution_m'])
        checked_empty=validate_layout({'strategy':'S0','items':[],'service':{}},grid,config,households[config['households']['main_households'][0]])
        empty.append(dict(unit_key=unit.unit_key,source=unit.source,nia_m2=unit.interior.area,
            empty_layout_valid=checked_empty['pass'],failures=';'.join(checked_empty['violations'])))
        for _,row in raw[raw.unit_key==unit.unit_key].iterrows():
            layout=json.loads((Path(summary['cache'])/'shared'/row.layout_file).read_text())
            household=households[row.household]
            checked=validate_layout(layout,grid,config,household)
            agreement=abs(checked['fci']-layout['fci'])<1e-7 and abs(checked['fci']-layout['solver']['fci_solver'])<1e-7
            assert agreement
            layout['validator']=checked
            for obsolete in ('pass','violations','credits','unreachable_items'):
                layout.pop(obsolete,None)
            target=Path('results/layouts/pilot')/row.layout_file
            write_json(target,layout)
            if render:render_layout(unit,layout,config,household,target.with_suffix('.png'),grid)
            solver=layout['solver'];trace=solver.get('trace',[])
            stopped_at_bound=solver.get('termination')=='primary_bound_incumbent' or bool(trace and
                trace[-1].get('stopped_at_primary_bound') and trace[-1].get('reachability_failures')==0)
            values=row.to_dict();values.update(stopped_at_proved_bound=stopped_at_bound,
                algorithm='cp_sat',furnishable_area_m2=unit.classes['furnishable'].area,
                served_hours=checked['served_hours'],demanded_hours=checked['demanded_hours'],
                n_violations=len(checked['violations']),objective=layout['solver'].get('objective'),bound=layout['solver'].get('bound'))
            rows.append(values)
            lower_witness=[]
            for strategy in ('S0','S1','S2'):
                if strategy>=layout['strategy']:continue
                candidate=deepcopy(layout);candidate['strategy']=strategy
                lower=validate_layout(candidate,grid,config,household)
                value=float(raw[(raw.unit_key==unit.unit_key)&(raw.household==household.name)&(raw.strategy==strategy)].fci_validator.iloc[0])
                if lower['pass'] and lower['fci']>value+1e-7:lower_witness.append(strategy)
            audit.append(dict(unit_key=unit.unit_key,household=household.name,strategy=row.strategy,
                agreement=agreement,validator_pass=checked['pass'],missed_lower_strategy_improvement=';'.join(lower_witness)))
            if checked['pass'] and checked['fci']<=1e-12:zeros.append(zero_diagnosis(unit,household,layout,config,grid))
            for artifact in (target,target.with_suffix('.png')):
                if artifact.exists():manifest.append(dict(path=artifact.as_posix(),sha256=sha256_file(artifact),bytes=artifact.stat().st_size))
    frame=pd.DataFrame(rows);frame.to_csv(root/'pilot_solutions.csv',index=False)
    pd.DataFrame(audit).to_csv(root/'validation_audit.csv',index=False)
    pd.DataFrame(zeros,columns=list(zeros[0]) if zeros else ['unit_key','source','household','strategy','cause']).to_csv(root/'zero_service_diagnoses.csv',index=False)
    pd.DataFrame(manifest).to_csv(root/'layout_manifest.csv',index=False)
    access=pd.DataFrame(empty);access.to_csv(root/'empty_access_audit.csv',index=False)
    wide=frame.pivot(index=['unit_key','household'],columns='strategy',values='fci_validator').reset_index()
    wide['ordered']=(wide.S2>=wide.S1-1e-9)&(wide.S1>=wide.S0-1e-9)
    wide.to_csv(root/'ordering.csv',index=False)
    fallback_keys={(z['unit_key'],z['household'],z['strategy']) for z in zeros if z['cause']=='search_fallback'}
    frame['zero_service_fallback']=[(r.unit_key,r.household,r.strategy) in fallback_keys for r in frame.itertuples()]
    frame.assign(zero_service=frame.fci_validator<=1e-12).groupby(['source','strategy']).agg(
        n=('fci_validator','size'),mean_fci=('fci_validator','mean'),median_fci=('fci_validator','median'),
        validator_pass_share=('validator_pass','mean'),proved_bound_share=('stopped_at_proved_bound','mean'),
        final_at_proved_bound_share=('at_proved_bound','mean'),
        timeout_with_incumbent_share=('timeout_with_incumbent','mean'),zero_service_share=('zero_service','mean'),
        zero_service_fallback_share=('zero_service_fallback','mean')).reset_index().to_csv(root/'summary_by_group.csv',index=False)
    frame.groupby(['unit_key','source','nia_m2']).agg(n=('strategy','size'),valid=('validator_pass','sum'),
        mean_fci=('fci_validator','mean'),zero=('fci_validator',lambda x:int((x<=1e-12).sum()))).reset_index().to_csv(root/'summary_by_unit.csv',index=False)
    projection=projections(config,summary,frame)
    failed=access[~access.empty_layout_valid]
    badzero=sum(z['cause'] in ('source_gap_remaining','search_fallback') for z in zeros)
    criteria=dict(structural_failures=((failed.source=='D3').sum()==0 and failed.source.isin(['D1','D2']).sum()<=1),
        explained_valid_zeros=badzero==0,ordering=bool(wide.ordered.all()),
        validator_agreement=all(v['agreement'] for v in audit),budget=projection['expA_within_36h'])
    result=dict(selected_arm=selection['selected_arm'],config_hash=config_hash(config),code_hash=summary['code_hash'],
        input_hash=summary['input_hash'],
        report_code_hash=sha256_file(Path(__file__)),
        cases=len(frame),valid=int(frame.validator_pass.sum()),invalid=int((~frame.validator_pass).sum()),
        valid_zero_cases=len(zeros),zero_causes=pd.Series([z['cause'] for z in zeros],dtype='str').value_counts().to_dict(),
        structural_failure_units=failed[['unit_key','source','failures']].to_dict('records'),
        ordering_violations=int((~wide.ordered).sum()),missed_downward_improvements=sum(bool(v['missed_lower_strategy_improvement']) for v in audit),
        validator_agreement_rate=float(np.mean([v['agreement'] for v in audit])),
        criteria={k:bool(v) for k,v in criteria.items()},all_five_criteria_pass=all(criteria.values()),
        worker_quality_criterion_met=selection['worker_quality_criterion_met'],projection=projection)
    write_json('reports/g2_revision_audit.json',result)
    write_json('reports/pilot_audit.json',result)
    write_json('reports/pilot_runtime_projection.json',projection)
    notes_path=Path('reports/pilot_access_notes.json')
    notes=json.loads(notes_path.read_text()) if notes_path.exists() else {}
    if notes.get('code_hash')!=summary['code_hash']:
        write_json(notes_path,dict(basis='Current empty-access audit; complete visual diagnosis before release',
            config_hash=config_hash(config),code_hash=summary['code_hash'],
            units={r['unit_key']:'Pending visual diagnosis' for r in result['structural_failure_units']}))
    write_json('reports/pilot_render_style.json',dict(style=style,plots_follow_saved_json=True,config_hash=config_hash(config),code_hash=summary['code_hash']))
    gap_rows=pd.read_csv(root/'gap_connectivity_audit.csv')
    gap_rows[gap_rows.unit_key.isin([u.unit_key for u in units])].to_csv(root/'empty_space_summary.csv',index=False)
    if render:
        render_empty(units,config)
        render_preparation_views()
        from fea.viz.corpus import render_histogram
        render_histogram(pd.read_csv('results/corpus/corpus_units.csv'),Path('results/figures/F2_corpus_area'),config_hash(config))
    prepared_names={'fixed_service_diagnostic.csv','d3_regeneration_mapping.csv','gap_connectivity_audit.csv','empty_space_summary.csv'}
    input_digest=json.loads((root/'pilot_units.json').read_text())['config_hash']
    for name in ['pilot_solutions.csv','validation_audit.csv','zero_service_diagnoses.csv','layout_manifest.csv',
                 'empty_access_audit.csv','ordering.csv','summary_by_group.csv','summary_by_unit.csv',
                 'runtime_projection.csv','expK_projection.csv',*sorted(prepared_names)]:
        data=pd.read_csv(root/name)
        data['config_hash']=input_digest if name in prepared_names else config_hash(config)
        data['code_hash']=summary['code_hash']
        data['analysis_config_hash']=config_hash(config)
        data.to_csv(root/name,index=False)
    return result


def tests(config):
    result=subprocess.run([sys.executable,'-m','pytest','-q'],text=True,capture_output=True)
    output=result.stdout+result.stderr
    match=re.search(r'(\d+) passed in ([0-9.]+)s',output)
    if result.returncode or not match:raise RuntimeError('Regression test failure: '+output[-6000:])
    write_json('reports/g2_revision_tests.json',dict(config_hash=config_hash(config),command='python -m pytest -q',passed=int(match[1]),
        elapsed_s=float(match[2]),exit_code=result.returncode,tests_hash=hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path('tests').glob('*.py')))).hexdigest()))
    Path('reports/pilot_tests.json').write_bytes(Path('reports/g2_revision_tests.json').read_bytes())


def update_readme(audit,selection,checks):
    """Keep the review entry consistent with generated results."""
    path=Path('README.md')
    text=path.read_text()
    text=re.sub(r'\| G2 method & pilot \|[^\n]*',
        '| G2 method & pilot | Revision complete; awaiting the author-requested Claude review; see reports/GATE_G2_response.md |',text)
    text=re.sub(r'\| G1 data & corpus \|[^\n]*',
        '| G1 data & corpus | G1 review completed; G2 geometry refresh is recorded in current corpus artifacts |',text)
    status=(f"Start the review with [reports/GATE_G2_response.md](reports/GATE_G2_response.md). "
        f"The corrected pilot has {audit['valid']} valid and {audit['invalid']} invalid layouts out of {audit['cases']}, "
        f"{audit['validator_agreement_rate']:.0%} independent FCI agreement, and {checks['passed']} passing tests. "
        "The [artifact manifest](results/pilot/layout_manifest.csv), [audit](reports/g2_revision_audit.json), "
        "[benchmarks](results/pilot/benchmark_comparison.csv) and [reproduction instructions](docs/REPRODUCING.md) accompany the package.\n\n"
        f"Selected configuration: {selection['selected_arm']}. Exp. A projects to {audit['projection']['retained_expA_hours']:.3f} h "
        "including the 15% margin; Exp. K is estimated separately. "
        f"All five G2 continuation criteria pass: {audit['all_five_criteria_pass']}. "
        "The author requested another Claude review before proceeding. Phase 7, K and R remain unstarted; "
        "no FEA or hypothesis conclusion is claimed. Literature screening remains due at G3.\n")
    text=re.sub(r'Start the review with[\s\S]*?(?=\n## License)',lambda _:status,text)
    path.write_text(text,encoding='utf-8')



def preparation_reports():
    """Refresh earlier phase summaries while retaining their historical reports."""
    root=Path('results/pilot/baseline_g2')
    for name in ('phase_02_corpus.md','phase_05_candidates.md'):
        previous=Path('reports')/name; saved=root/('report_'+name)
        if previous.exists() and not saved.exists():saved.write_bytes(previous.read_bytes())
    corpus=json.loads(Path('reports/corpus_audit.json').read_text())
    acceptance=json.loads(Path('reports/phase02_acceptance.json').read_text())
    candidate=json.loads(Path('reports/candidates_audit.json').read_text())
    semantic=json.loads(Path('reports/g2_service_geometry_audit.json').read_text())
    assert acceptance['pass'] and candidate['pass'] and semantic['pass']
    counts=pd.read_csv('results/corpus/counts.csv').drop(columns=['config_hash','analysis_config_hash'],errors='ignore')
    phase2=f"""# Phase 02: Corpus construction — G2 geometry refresh

Status: COMPLETE. Current geometry supersedes the G1 kitchen/service treatment; the earlier phase report is preserved under results/pilot/baseline_g2/.

## Current counts

{table(counts)}

The expA_sample column is the retained analysis sample after the approved G2 budget rule, if a cap is required. The uncapped G2 sample and conversion counts remain in expA_sample_uncapped_G2.csv and corpus_audit.json. All normalized geometries remain in the local processed corpus; the scalar publication table records the final analysis selection. The 24 preparation review views are sampled from the uncapped corpus and are not reselected for a later budget cap.

## Acceptance and geometry

The rebuilt uncapped corpus passed {sum(acceptance['checks'].values())}/{len(acceptance['checks'])} checks and {acceptance['pytest_summary']}. These checks precede analysis-only caps; all-eligible-D2/D3 sampling checks describe the uncapped preparation stage. Conversion config hash: {corpus['config_hash']}. The selected solver configuration has a separate analysis hash in final outputs.

Kitchens are walkable but not furnishable; fixtures and sanitary rooms remain blocked. Sanitary room boundaries and kitchen regions have separate access targets. All {semantic['included_units']} included geometries were checked: {semantic['empty_service_room_geometry']} empty sanitary geometries and {semantic['kitchen_furniture_overlap_units']} kitchen/furniture-class overlaps. D3 uses the corrected continuous 0.90 m entrance/pod passage check and empty-layout raster validation. Gap filling is circulation only and does not redefine NIA.

NIA retains the reviewed union-of-interior-classes definition. D1 gross area remains missing; D2 metric calibration remains an assumption, with the same scale and completeness filters. Geometry deduplication uses a 1e-6 m hash grid, keeps source/site grouping, and does not equate mirrors or quarter turns. D1 sampling remains stratified by NIA/room count with the approved site cap. D1/D2 projection caps, when needed, retain stratification; all valid D3 shells at NIA ≤20 m² are retained. See the G2 response for cap actions and final counts.

No FEA or hypothesis conclusion follows from preparation. Figures and numerical tables are regenerated by the committed scripts; the recorded conversion attempt timings exclude prior interrupted runs.
"""
    Path('reports/phase_02_corpus.md').write_text(phase2,encoding='utf-8')
    phase5=f"""# Phase 05: Rasterization and candidate generation — G2 refresh

Status: COMPLETE. The full 0.10 m anchor benchmark on {candidate['units']} uncapped review units passed all checks. This is a candidate-generation check; the G2 pilot separately compares 0.10/0.20 m anchors and selects the latter only under the declared score criterion.

Candidate generation: median {candidate['median_candidate_time_s']:.6f} s/unit, maximum {candidate['max_candidate_time_s']:.6f} s/unit. Rasterization median: {candidate['median_raster_time_s']:.6f} s/unit. Config hash: {candidate['config_hash']}. Tests: {candidate['tests'].strip().splitlines()[-1]}.

Whole-cell collision, complete backing, door keepouts, storage-only item constraints, tall-item window exclusions and all-state anchor consistency remain enforced. Walls and fixed bodies block circulation; kitchen rooms are walkable and hatched in the revised figures. The half-diagonal distance test is superseded by exact-diameter even/odd disc erosion, independent traversal and dilation in both solver and validator. The 0.60/0.50 m and 0.90/0.80 m boundaries and bed-side access strips have regression coverage.

The candidate table uses full-resolution anchors. Final solver anchors use the G2 selected lattice while collisions/access retain a 0.10 m raster. The full-resolution sensitivity remains due. Furniture and household defaults are unchanged; no swept-motion feasibility is implied.
"""
    Path('reports/phase_05_candidates.md').write_text(phase5,encoding='utf-8')
    path=Path('reports/GATE_G1_response.md');previous=path.read_text()
    marker='> Historical G1 review response.'
    if not previous.startswith(marker):
        path.write_text(marker+' Current G2 geometry, sample counts and method corrections are documented in phase_02_corpus.md and GATE_G2_response.md.\n\n'+previous,encoding='utf-8')


def report():
    audit=json.loads(Path('reports/g2_revision_audit.json').read_text());selection=json.loads(Path('results/pilot/benchmark_selection.json').read_text())
    checks=json.loads(Path('reports/g2_revision_tests.json').read_text())
    assert json.loads(Path('reports/g2_blocker_geometry_types.json').read_text())['polygon_source_blockers_only']
    assert json.loads(Path('reports/g2_service_geometry_audit.json').read_text())['pass']
    visual=json.loads(Path('reports/pilot_visual_review.json').read_text())
    records=visual['reviews']
    access_notes=json.loads(Path('reports/pilot_access_notes.json').read_text())
    for failure in audit['structural_failure_units']:
        assert failure['unit_key'] in access_notes['units'] and 'Pending' not in access_notes['units'][failure['unit_key']]
    assert len(records)>=6
    for record in records+visual.get('preparation_reviews',[]):assert sha256_file(Path(record['path']))==record['sha256']
    reviewed={r['path'] for r in records}
    for unit in json.loads(Path('results/pilot/pilot_units.json').read_text())['units']:
        if unit['source']=='D3' and unit['gross_area_m2'] in (8,12):
            for strategy in ('S0','S2'):
                assert 'results/layouts/pilot/'+unit['unit_key'].replace(':','_')+'_H1_'+strategy+'.png' in reviewed
    summaries=[json.loads((Path('results/pilot/benchmarks')/a/'summary.json').read_text()) for a in selection['completed_arms']]
    assert len(summaries)==6 and all(s['completed_cases']==240 and s['fresh_throughput_measurement'] for s in summaries)
    assert all(s['input_hash']==audit['input_hash'] and s['code_hash']==audit['code_hash'] for s in summaries)
    rows=[dict(arm=s['arm'],workers=s['num_workers'],concurrency=s['concurrent_solves'],seconds_per_100=round(s['wall_time_per_100_cases_s'],3),
        median_FCI=round(s['fci_distribution']['0.5'],6),mean_FCI=round(s['mean_fci'],6),valid=s['validator_pass_cases'],
        median_iterations=s['median_iterations'],first_positive_valid_s=round(s['mean_first_valid_time_s'],3) if s['mean_first_valid_time_s'] is not None else '') for s in summaries]
    benchmarks=pd.DataFrame(rows)
    benchmarks.assign(config_hash=[v['config_hash'] for v in summaries],code_hash=[v['code_hash'] for v in summaries],
        input_hash=[v['input_hash'] for v in summaries]).to_csv('results/pilot/benchmark_comparison.csv',index=False)
    full=pd.read_csv(Path('results/pilot/benchmarks')/selection['completed_arms'][0]/'cases.csv')
    coarse=pd.read_csv(Path('results/pilot/benchmarks')/selection['completed_arms'][1]/'cases.csv')
    keys=['unit_key','household','strategy']
    anchors=full[keys+['source','nia_m2','fci_validator']].merge(coarse[keys+['fci_validator']],
        on=keys,suffixes=('_full','_coarse'),validate='one_to_one')
    assert len(anchors)==240
    anchors['delta_FCI']=anchors.fci_validator_coarse-anchors.fci_validator_full
    anchors.assign(full_config_hash=summaries[0]['config_hash'],coarse_config_hash=summaries[1]['config_hash'],
        code_hash=audit['code_hash'],input_hash=audit['input_hash']).to_csv('results/pilot/anchor_stride_comparison.csv',index=False)
    anchor_summary=anchors.groupby(['source','strategy']).agg(n=('delta_FCI','size'),
        mean_full_FCI=('fci_validator_full','mean'),mean_coarse_FCI=('fci_validator_coarse','mean'),
        mean_delta_FCI=('delta_FCI','mean'),min_delta_FCI=('delta_FCI','min'),max_delta_FCI=('delta_FCI','max'),
        improved=('delta_FCI',lambda x:int((x>1e-9).sum())),reduced=('delta_FCI',lambda x:int((x< -1e-9).sum()))).reset_index()
    anchor_summary.assign(full_config_hash=summaries[0]['config_hash'],coarse_config_hash=summaries[1]['config_hash'],
        code_hash=audit['code_hash']).to_csv('results/pilot/anchor_stride_summary.csv',index=False)
    gaps=pd.read_csv('results/pilot/gap_connectivity_audit.csv');mapping=pd.read_csv('results/pilot/d3_regeneration_mapping.csv')
    old=pd.read_csv('results/pilot/baseline_g2/pilot_solutions.csv');new=pd.read_csv('results/pilot/pilot_solutions.csv')
    selected_pair=full[keys+['source','nia_m2','fci_validator']].merge(new[keys+['fci_validator']],
        on=keys,suffixes=('_reference','_selected'),validate='one_to_one')
    assert len(selected_pair)==240
    selected_pair['delta_FCI']=selected_pair.fci_validator_selected-selected_pair.fci_validator_reference
    selected_pair.assign(reference_config_hash=summaries[0]['config_hash'],selected_config_hash=audit['config_hash'],
        code_hash=audit['code_hash'],input_hash=audit['input_hash']).to_csv('results/pilot/selected_reference_comparison.csv',index=False)
    paired=old[['unit_key','household','strategy','fci_validator','reach_iterations']].merge(new[['unit_key','household','strategy','fci_validator','reach_iterations']],on=['unit_key','household','strategy'],suffixes=('_old','_new'))
    paired.assign(config_hash=audit['config_hash'],baseline_config_hash=old.config_hash.iloc[0],
        code_hash=audit['code_hash']).to_csv('results/pilot/baseline_comparison.csv',index=False)
    diagnosis_text='\n'.join('- '+key+': '+value for key,value in access_notes['units'].items()) or 'No unit fails empty fixed-service access.'
    cut_summary=pd.read_csv('results/pilot/cut_comparison/summary.csv').drop(columns=['config_hash','code_hash'],errors='ignore').round(6)
    p=audit['projection']
    text=f"""# Gate G2 response

Status: READY_FOR_CLAUDE_REVIEW. Reviewed baseline: 67af2ee; requested corrections: a228786. No Phase 7, K or R experiment was started. The author requests another review even if the continuation criteria pass.

## Outcomes

- Fixed pilot: {audit['cases']} cases; {audit['valid']} valid and {audit['invalid']} invalid. Independent FCI agreement: {audit['validator_agreement_rate']:.0%}.
- Ordering violations after sharing: {audit['ordering_violations']}; missed feasible downward improvements: {audit['missed_downward_improvements']}.
- Anchor comparison at 8 workers / 60 s: mean FCI change (0.20 m minus 0.10 m) {anchors.delta_FCI.mean():+.6f}; source means {json.dumps({k:round(v,6) for k,v in anchors.groupby('source').delta_FCI.mean().items()},sort_keys=True)}. Passing the median selection rule does not establish equal quality for every source or case.
- Selected configuration versus the corrected full-anchor 8-worker reference: mean FCI change {selected_pair.delta_FCI.mean():+.6f}; by source {json.dumps({k:round(v,6) for k,v in selected_pair.groupby('source').delta_FCI.mean().items()},sort_keys=True)}. See selected_reference_comparison.csv; these finite-budget quality changes remain part of this review even if every continuation criterion passes.
- Valid zero-service cases: {audit['valid_zero_cases']}; causes: {json.dumps(audit['zero_causes'],sort_keys=True)}.
- Tests: {checks['passed']} passed; measured test runtime {checks['elapsed_s']:.2f} s.
- All five reviewer continuation criteria pass: **{audit['all_five_criteria_pass']}**. Criterion results: {json.dumps(audit['criteria'],sort_keys=True)}.

## M1–M3 and M8: geometry and access

D3 tries ordered near-corner/wall placements, rejects bodies touching the entrance keepout, checks continuous 0.90 m disc connectivity to the main floor and pod door, then tests empty raster access. Parameter keys are retained. Rejected combinations are labelled generator_infeasible and excluded before sampling. The mapping has {len(mapping)} parameter combinations and {int((mapping.reason=='generator_infeasible').sum())} generator exclusions; see d3_regeneration_mapping.csv. Its new_sample flag records the uncapped geometry redraw; retained_analysis_sample records the later budget selection. All original pilot D3 parameters are preserved.

Kitchen rooms are walkable, not furnishable; fixtures and sanitary bodies remain blocked. Kitchen reachability is tested separately. A wall-aware morphological close adds circulation across source seams up to 0.15 m, without changing NIA. The complete D1/D2 blocker-type audit confirms that the loaded source blockers are polygonal; a separate raster regression preserves zero-thickness internal separators. In the full uncapped sample, {int(gaps.connectivity_changed.sum())} of {len(gaps)} units gain reachability to previously existing cells. Detailed staged pilot diagnostics are in fixed_service_diagnostic.csv; remaining valid zeros and explicit evidence are in zero_service_diagnoses.csv. The 0.30 m gap probe in that file is diagnosis only and is never used to optimize scores.

{diagnosis_text}

Solver and validator independently erode by an even/odd discrete disc, traverse reference positions and dilate by the same disc to recover covered access area. Exact 0.60/0.50 m and 0.90/0.80 m corridor boundaries, bed-side strips, rotated cases and irregular obstacles are tested. Both still share rasterization; validation therefore does not independently establish source geometry correctness.

## M4–M5 and M9: search and throughput

{table(benchmarks)}

Selected arm: **{selection['selected_arm']}**. Worker quality criterion met: {selection['worker_quality_criterion_met']}. The fastest 60 s worker arm must be within 0.01 median FCI of both corrected 8-worker references; 30 s is retained only if faster and within 0.01 of that selection as well. All distributions include invalid cases at zero, and individual case scores are published. The 8-worker exhaustive arm isolates corrected-geometry full anchors; the second arm isolates 0.20 m anchors. Collision and access remain 0.10 m. The full-anchor check remains required in resolution sensitivity.

Paired 0.20 m minus 0.10 m anchor differences, with 8 workers and 60 s held fixed:

{table(anchor_summary.round(6))}

The complete 240 paired changes are in anchor_stride_comparison.csv. Positive differences reflect finite-budget search outcomes, not a claim that the coarser feasible set contains the finer one.

The greedy baseline sorts by descending footprint, takes the first improving feasible wall-adjacent pose, and is independently checked before hinting CP-SAT. Each search uses at most 3 s (also bounded by 15% of its total budget) for that warm start. Geometry constraints, lazy checks and validation share the total 30/60 s budget; CP search initially uses 5 s rounds so access can be checked promptly. A round returning UNKNOWN is retried with a doubled slice, up to the remaining total budget; it does not terminate the case early. After a solution-bearing round the slice resets to 5 s. Iterations are consequently not directly equivalent to the old single long search. First-valid timings refer to positive-FCI layouts, not the empty initial incumbent. The budget is checked between stages and solver calls; model construction and final validation are not preempted and may overrun it slightly. Runtime projections use the measured elapsed times.

In summary_by_group.csv, proved_bound_share records an actual early bound stop in the case's own search; final_at_proved_bound_share records whether the final, possibly shared layout attains the relaxed bound with zero burden. Timeout-with-incumbent uses recorded timeout status or elapsed time at the limit. These flags are not mutually exclusive after sharing; zero_service_fallback_share counts valid zeros specifically diagnosed as search_fallback.

All strategies exchange only layouts independently feasible under the receiving strategy. Scores and differences are reported after this exchange. The final validation audit searches again for missed downward improvements.

M9 uses geometric frontier witness rectangles. A cut requires at least one blocking body to stop covering its witness rectangle, or the failed assignment to be withdrawn, or its movable target pose to change. It removes ranges of poses, not one exact tuple. This guarded disjunction intentionally replaces unconditional reservation of every old bottleneck: that proposed shortcut could exclude a valid alternate route. Regression tests retain alternate routes/target relocation while excluding multiple blocking poses. Each restart is hinted with the previous layout minus offending items. A separate paired comparison holds revised geometry, greedy, lattice, round schedule and limits fixed on all 20 H1/S2 cases:

{table(cut_summary)}

First CP-valid time runs from case start to the first positive, independently checked CP-generated candidate. Greedy/incumbent checks do not trigger this event; their elapsed time is still included. Cases returning at an incumbent bound before CP have no such timing. Paired case records are in cut_comparison/cases.csv. The old pilot did not record time to first valid solution, so no retrospective timing is invented. The raw CP-SAT objective/bound describes its last solution-bearing search, not an optimality gap of a shared or retained layout.

## M6–M7: projections and sample rule

Measured parallel wall time calibrates source-specific mean solve costs, including preparation/queue overhead in the calibration factor. Exp. A projection with 15% margin: {p['uncapped_expA_hours']:.3f} h before caps, {p['retained_expA_hours']:.3f} h for the retained sample. Source counts: {json.dumps(p['source_counts_after'],sort_keys=True)}. Cap actions: {json.dumps(p['caps_applied'])}. Every valid D3 shell at NIA ≤20 m² is preserved ({p['D3_small_shells_preserved']}). D1/D2 floors and the 60 larger-D3 floor are enforced; no further reduction is authorized by this script.

Exp. K is projected separately: {p['expK_projected_solves']} solves, {p['expK_projected_hours']:.3f} h with 15% margin under the full workload in expK_projection.csv. {p['expK_caveat']} Within the planned two-day K time box: {p["expK_within_two_day_timebox"]}. These are explicit workload projections, not observed K results or guarantees.

## Visual review and limitations

{len(records)} current layout renders and {len(visual.get('preparation_reviews',[]))} preparation/contact views were inspected; paths, hashes and observations are in pilot_visual_review.json, including H1 S0/S2 at 8 and 12 m². Kitchen rooms have a light-grey hatch with a contrasting edge and an explicit legend. The presentation wrapper adjusts hatch contrast only, preserving the measured numerical implementation. Drawn lines guide through the covered area; they are not swept-motion trajectories. Multi-person access still uses one reachable point in the union of strips; the approved strict_access sensitivity is due on the future 200-instance Exp. B sample. Endpoint-only transformations, catalogue assumptions and the anchor-based window tie-break remain explicit limitations.

## Reproduction

After installing dependencies and supplying the pinned raw releases:

1. python scripts/03_build_corpus.py
2. python scripts/06_revision.py --prepare
3. python scripts/06_revision_pipeline.py
4. python scripts/06_cut_comparison.py
5. python scripts/06_revision_report.py --export --render --run-tests
6. Inspect the new images and update their factual visual-review record.
7. python scripts/06_revision_report.py --write-report

The optional prepare-pilot mode can overlap completed D1 / selected D2 conversion with later nonpilot conversion. Publication requires exact equality with the subsequent full-corpus pilot serialization. Cached benchmark cases may be resumed for results, but resumed throughput is explicitly ineligible for selection. Parallel CP-SAT incumbents may vary with scheduling despite a fixed seed. No FEA, minimum-area estimate or hypothesis verdict is inferred from this methods pilot.
"""
    Path('reports/GATE_G2_response.md').write_text(text,encoding='utf-8')
    Path('reports/phase_06_pilot.md').write_text('# Phase 6: corrected pilot and G2 response\n\n'+text.split('\n',1)[1],encoding='utf-8')
    Path('reports/GATE_G2.md').write_text('# Gate G2: revision ready for review\n\nSee [the complete response](GATE_G2_response.md), [phase report](phase_06_pilot.md), and [audit](g2_revision_audit.json). Formal experiments remain unstarted pending the author-requested Claude review.\n',encoding='utf-8')

    update_readme(audit,selection,checks)
    preparation_reports()


def main():
    parser=prepare_cli(__doc__);parser.add_argument('--export',action='store_true');parser.add_argument('--render',action='store_true')
    parser.add_argument('--run-tests',action='store_true');parser.add_argument('--write-report',action='store_true')
    args=parser.parse_args();config,_,_=start_run(args,'06_revision_report')
    if args.dry_run:print('Would audit the selected complete arm, render/review artifacts, and report A/K projections.');return
    if args.export:
        selection=json.loads(Path('results/pilot/benchmark_selection.json').read_text())
        config=freeze_configuration(selection,args.config);print(json.dumps(export(config,selection,args.render)))
    if args.run_tests:tests(config)
    if args.write_report:report()


if __name__=='__main__':main()
