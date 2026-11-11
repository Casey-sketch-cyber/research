"""P1 support-aware area tables and pooled-reference sensitivity; no new solves."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[name]='1'
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase07_corrected import load_corrected
from phase07_p1_area import fit_reference,paired_gain,gain_summary
from phase07_statistics import interval

ROOT=Path('results/expA_f1/analysis_p1')
METHODS=['median_bin_cummax','mean_isotonic']
TABLES=['f0_curves','paired_equivalent_area','area_gain_summary']
STATS=['median_delta_ea_identified_positive_m2','median_among_fci_improved_lower_bound_m2','share_lower_bound_among_units']
REPORT=Path('reports/phase_07_P1_results.md')
FIGURE=ROOT/'figures/F4_paired_area_gain_P1'


def sub(result,mask):return {k:v[mask] for k,v in result.items()}


def group_job(job):
    reference_pooling,household,frame,options,seed,destination=job;destination=Path(destination)
    if (destination/'done.json').exists():
        done=json.loads((destination/'done.json').read_text())
        if all(sha256_file(destination/p)==h for p,h in done['outputs'].items()):return str(destination)
        raise ValueError('P1 cached result changed')
    frame=frame.sort_values('unit_key').reset_index(drop=True);area=frame.nia_m2.to_numpy(float);scores=frame[['S0','S2']].to_numpy(float)
    source=frame.source.to_numpy();bins=np.floor((area+1e-8)/2)*2;n=len(frame)
    targets=[reference_pooling]+(['real_plans'] if reference_pooling=='pooled' else [])
    masks={target:(np.isin(source,['D1','D2']) if target=='real_plans' else np.ones(n,bool)) for target in targets}
    strata={target:[None]+list(np.unique(bins[mask])) for target,mask in masks.items()}
    draws={(method,target,lo):np.full((options['n'],len(STATS)),np.nan) for method in METHODS for target in targets for lo in strata[target]}
    rng=np.random.default_rng(seed)
    for draw in range(options['n']):
        indices=rng.integers(0,n,size=n);bx,by,bb,bs=area[indices],scores[indices],bins[indices],source[indices]
        for method in METHODS:
            result=paired_gain(fit_reference(bx,by[:,0],method),by[:,0],by[:,1])
            for target in targets:
                target_mask=np.isin(bs,['D1','D2']) if target=='real_plans' else np.ones(n,bool)
                for lo in strata[target]:
                    mask=target_mask if lo is None else target_mask&(bb==lo)
                    if mask.any():
                        summary=gain_summary(sub(result,mask));draws[method,target,lo][draw]=[summary[k] if summary[k] is not None else np.nan for k in STATS]
        if (draw+1)%100==0:write_json(destination/'progress.json',dict(completed=draw+1,expected=options['n']))
    curves=[];cases=[];summaries=[]
    for method in METHODS:
        curve=fit_reference(area,scores[:,0],method);result=paired_gain(curve,scores[:,0],scores[:,1])
        curves.append(pd.DataFrame(dict(reference_pooling=reference_pooling,household=household,method=method,
            area_m2=curve['area'],fitted_fci_S0=curve['capacity'],reference_n_units=n,reference_min_nia_m2=area.min(),reference_max_nia_m2=area.max())))
        for target,mask in masks.items():
            case=frame.loc[mask,['unit_key','source','nia_m2','S0','S1','S2']].copy()
            case['pooling'],case['reference_pooling'],case['household'],case['method']=target,reference_pooling,household,method
            for key,value in sub(result,mask).items():case[key]=value
            cases.append(case)
            for lo in strata[target]:
                chosen=mask if lo is None else mask&(bins==lo)
                row=dict(pooling=target,reference_pooling=reference_pooling,household=household,method=method,
                    stratum='overall' if lo is None else 'area_bin',area_bin_lo=lo,area_bin_hi=None if lo is None else lo+2,
                    bootstrap_resamples=options['n'],**gain_summary(sub(result,chosen)))
                for index,key in enumerate(STATS):
                    ci=interval(draws[method,target,lo][:,index],options['ci']) if chosen.sum()>=2 and row[key] is not None else (None,None,0,'point_not_identified_or_insufficient_units')
                    row.update({key+'_ci_lo':ci[0],key+'_ci_hi':ci[1],key+'_successful_bootstraps':ci[2],key+'_ci_status':ci[3]})
                summaries.append(row)
    for name,table in zip(TABLES,[pd.concat(curves),pd.concat(cases),pd.DataFrame(summaries)]):table.to_csv(destination/(name+'.csv'),index=False)
    write_json(destination/'done.json',dict(reference_pooling=reference_pooling,household=household,outputs={name+'.csv':sha256_file(destination/(name+'.csv')) for name in TABLES}))
    return str(destination)


def render(summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data=summary[(summary.method==METHODS[0])&(summary.pooling==summary.reference_pooling)]
    households=sorted(data.household.unique());fig,axes=plt.subplots(4,3,figsize=(16,13),sharex=True,sharey=True)
    for i,h in enumerate(households):
        for j,pool in enumerate(['pooled','real_plans','D3']):
            ax=axes[i,j];d=data[(data.household==h)&(data.pooling==pool)&(data.stratum=='area_bin')].sort_values('area_bin_lo')
            overall=data[(data.household==h)&(data.pooling==pool)&(data.stratum=='overall')].iloc[0]
            x=d.area_bin_lo.to_numpy()+1;key='median_delta_ea_identified_positive_m2'
            ax.plot(x,d[key],'o-',ms=3,color='#286c91',label='Identified positive median')
            ax.fill_between(x,d[key+'_ci_lo'].to_numpy(float),d[key+'_ci_hi'].to_numpy(float),color='#286c91',alpha=.15)
            ax.plot(x,d.median_positive_lower_bound_m2,'^',ms=4,color='#b55b32',label='Lower-bound median (≥)')
            ax.set(title=f"{pool.replace('_',' ')} / {h.split('_')[0]}\nIdentified n={int(overall.n_identified_positive_gains)}; bound n={int(overall.n_lower_bound_positive_gains)}",
                xlabel='Net internal area (m²)',ylabel='Conditional gain / bound (m²)')
            ax.title.set_fontsize(10);ax.grid(alpha=.15)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=2,bbox_to_anchor=(.5,.96))
    fig.suptitle('Paired equivalent-area gain: identified values and lower bounds shown separately')
    fig.tight_layout(rect=(0,0,1,.93));FIGURE.parent.mkdir(parents=True,exist_ok=True)
    for extension in ['png','pdf']:fig.savefig(FIGURE.with_suffix('.'+extension),dpi=250,bbox_inches='tight')
    plt.close(fig)


def verify(tables,wide):
    cases=tables['paired_equivalent_area'];curves=tables['f0_curves'];count=0
    for (target,reference,h,method),g in cases.groupby(['pooling','reference_pooling','household','method']):
        base=wide[wide.household==h]
        ref=base if reference=='pooled' else base[base.source.isin(['D1','D2'])] if reference=='real_plans' else base[base.source==reference]
        expected=ref[ref.source.isin(['D1','D2'])] if target=='real_plans' else ref
        if set(g.unit_key)!=set(expected.unit_key) or g.unit_key.duplicated().any():raise ValueError('P1 target sample changed')
        original=base.set_index('unit_key').loc[g.unit_key]
        if not np.allclose(g[['S0','S1','S2']],original[['S0','S1','S2']],atol=1e-10,rtol=0):raise ValueError('P1 input scores changed')
        curve=fit_reference(ref.nia_m2,ref.S0,method)
        saved=curves[(curves.reference_pooling==reference)&(curves.household==h)&(curves.method==method)].sort_values('area_m2')
        if not np.allclose(saved.area_m2,curve['area']) or not np.allclose(saved.fitted_fci_S0,curve['capacity']):raise ValueError('P1 reference curve changed')
        result=paired_gain(curve,g.S0.to_numpy(),g.S2.to_numpy())
        for key,value in result.items():
            if not np.allclose(value,g[key],equal_nan=True,atol=1e-8,rtol=0):raise ValueError('P1 inverse classification differs')
        if g.loc[g.delta_gain_lower_bound_only,'delta_ea_m2'].notna().any():raise ValueError('Bound misreported as identified')
        count+=1
    if count!=48:raise ValueError('P1 requires 40 original and 8 pooled-reference sensitivity groups')
    summary=tables['area_gain_summary']
    for row in summary.itertuples(index=False):
        selected=cases[(cases.pooling==row.pooling)&(cases.reference_pooling==row.reference_pooling)&(cases.household==row.household)&(cases.method==row.method)]
        if row.stratum=='area_bin':selected=selected[np.floor((selected.nia_m2+1e-8)/2)*2==row.area_bin_lo]
        calculated=gain_summary({k:selected[k].to_numpy() for k in paired_gain(fit_reference([8,10],[.5,1]),[.5],[1])})
        for key,value in calculated.items():
            if value is None:
                if not pd.isna(getattr(row,key)):raise ValueError('Missing P1 statistic became a number')
            elif not np.isclose(value,getattr(row,key),atol=1e-8,rtol=0):raise ValueError('P1 summary differs from case classifications')
    return count


def finalize():
    path=ROOT/'acceptance.json';gate=json.loads(path.read_text())
    if not gate['numerical_checks_passed']:raise ValueError('P1 numerical gate incomplete')
    for name,digest in {**gate['inputs']['implementations'],**gate['outputs']}.items():
        if sha256_file(Path(name))!=digest:raise ValueError('P1 accepted evidence changed')
    for name,key in [('results/expA_f1/solutions.csv','solutions_sha256'),('results/expA_f1/acceptance.json','F1_acceptance_sha256'),('results/expA_f1/analysis/package_acceptance.json','frozen_F2_package_sha256'),('reviews/phase07_review_F.md','review_sha256')]:
        if sha256_file(Path(name))!=gate['inputs'][key]:raise ValueError('P1 source evidence changed')
    visual_path=Path('config/p1_visual_review.json');visual=json.loads(visual_path.read_text())
    if not visual.get('passed') or set(visual.get('hashes',{}))!={FIGURE.with_suffix('.png').as_posix()}:raise ValueError('P1 figure not reviewed')
    for name,digest in visual['hashes'].items():
        if sha256_file(Path(name))!=digest:raise ValueError('P1 reviewed figure changed')
    write_json(ROOT/'package_acceptance.json',dict(passed=True,P1_complete=True,numerical_acceptance_sha256=sha256_file(path),visual_review_sha256=sha256_file(visual_path),completed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
    print('P1 full package accepted')


def main():
    parser=prepare_cli(__doc__);parser.add_argument('--jobs',type=int,default=2);parser.add_argument('--finalize',action='store_true');args=parser.parse_args();config,_,_=start_run(args,'07_p1_analysis')
    if args.dry_run:print('Would classify all area support boundaries and add real-unit inversion on pooled curves, without re-solving or altering frozen F2/F3 evidence.');return
    if args.finalize:finalize();return
    solutions,gate=load_corrected(config);wide=solutions.pivot(index=['unit_key','household'],columns='strategy',values='fci_validator')
    wide=wide.join(solutions.drop_duplicates(['unit_key','household']).set_index(['unit_key','household'])[['source','nia_m2']]).reset_index()
    files=['scripts/07_p1_analysis.py','scripts/phase07_p1_area.py','scripts/phase07_paired_area.py','scripts/phase07_statistics.py','scripts/phase07_corrected.py']
    inputs=dict(solutions_sha256=gate['combined_sha256'],F1_acceptance_sha256=sha256_file(Path('results/expA_f1/acceptance.json')),
        frozen_F2_package_sha256=sha256_file(Path('results/expA_f1/analysis/package_acceptance.json')),review_sha256=sha256_file(Path('reviews/phase07_review_F.md')),
        bootstrap=config['experiments']['bootstrap'],seed=config['seed'],implementations={p:sha256_file(Path(p)) for p in files})
    fingerprint=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest();cache=Path(config['paths']['interim'])/'expA_p1'/fingerprint[:16]
    jobs=[]
    for pooling in ['pooled','real_plans','D1','D2','D3']:
        frame=wide if pooling=='pooled' else wide[wide.source.isin(['D1','D2'])] if pooling=='real_plans' else wide[wide.source==pooling]
        for household,group in frame.groupby('household',sort=True):
            seed=config['seed']+int(hashlib.sha256(('P1:'+pooling+household).encode()).hexdigest()[:8],16)
            jobs.append((pooling,household,group,inputs['bootstrap'],seed,str(cache/(pooling+'_'+household))))
    write_json(ROOT/'run.json',dict(status='running',inputs=inputs,cache=cache.as_posix(),expected_groups=20));paths=[]
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for future in tqdm(as_completed([pool.submit(group_job,job) for job in jobs]),total=len(jobs),desc='P1 reference groups'):
            paths.append(Path(future.result()));write_json(ROOT/'progress.json',dict(completed_groups=len(paths),expected_groups=20))
    tables={}
    for name in TABLES:
        table=pd.concat([pd.read_csv(p/(name+'.csv')) for p in sorted(paths)],ignore_index=True);table.to_csv(ROOT/(name+'.csv'),index=False);tables[name]=pd.read_csv(ROOT/(name+'.csv'))
    groups=verify(tables,wide);summary=tables['area_gain_summary'];render(summary)
    primary=summary[(summary.pooling=='real_plans')&(summary.reference_pooling=='real_plans')&(summary.method==METHODS[0])&(summary.stratum=='overall')]
    sensitivity=summary[(summary.pooling=='real_plans')&(summary.reference_pooling=='pooled')&(summary.method==METHODS[0])&(summary.stratum=='overall')]
    def report_table(frame):
        rows=[]
        for r in frame.itertuples(index=False):
            fmt=lambda x:'not identified' if pd.isna(x) else f'{x:.4f}'
            rows.append(dict(household=r.household,fci_improved=int(r.n_fci_improved),identified_positive=int(r.n_identified_positive_gains),bound_only_improved=int(r.n_lower_bound_among_fci_improved),positive_lower_bound=int(r.n_lower_bound_positive_gains),
                median_identified_positive_m2=fmt(r.median_delta_ea_identified_positive_m2),median_among_improved_lower_bound_m2='≥ '+fmt(r.median_among_fci_improved_lower_bound_m2)))
        return pd.DataFrame(rows).to_markdown(index=False)
    lines=['# Phase 7 — P1 support-aware equivalent-area results','','## Current reporting status','',
        'This analysis supersedes the area-gain tables, F4 area figure and area-gain summaries in the frozen F2 package. F1 scores, primary FCI effects, adequate-area analysis, layout checks and F3 sensitivity are unchanged. Historical F2 files retain their original hashes for provenance; their positive-uncensored area medians are not current identified estimates. Use results/expA_f1/analysis_p1/area_gain_summary.csv and F4_paired_area_gain_P1 for current reporting.','',
        'For unequal scores, an inverse at/below the lowest supported capacity or above the highest supported capacity makes the paired area difference a lower bound. Such observations are excluded from identified-positive medians. Equal scores still identify zero. Counts distinguish all support-limited improved units, strictly positive bounds and identified positive gains. The stored clamped comparison is diagnostic, not an identified estimate.','',
        '## Real-plan primary reference (D1+D2)','','The last column is a lower bound on the median among all FCI-improved units; it is distinct from the median conditional on identified positive gains. Bound-only counts include cases whose known lower bound is zero; positive-lower-bound counts omit those cases. Thus FCI improvement does not always identify a positive area gain. In particular, single-person values must retain the ≥ sign and their support explanation.','',report_table(primary),'',
        'H1 has no identified positive area gains on the real-plan median curve: its bound is the span between the lowest supported bin and full-capacity crossing. H2 has a mixture of identified and lower-bound cases. No missing smaller real plans are invented or extrapolated.','',
        '## Pooled-curve sensitivity for the same real plans','',
        'Refit the reference using pooled D1+D2+D3 units, then invert the same real-plan S0/S2 scores. This broadens observed NIA coverage through designed shells. The median-bin interpolation uses observed 2 m² bin midpoints, so its knot support is reported explicitly in f0_curves.csv and must not be confused with raw NIA endpoints. This sensitivity changes the reference population; generated small shells are not additional real homes.','',report_table(sensitivity),'',
        '## Resampling, figures and boundaries','',
        'Each of 1000 paired unit resamples refits the static curve. Pooled-reference sensitivity resamples the entire pooled set and evaluates its resampled real-plan subset, preserving overlap between the reference and target samples. Both median-bin cumulative-maximum and mean-isotonic methods are retained. Source-specific and 2 m²-bin tables accompany pooled, real-plan and D3 tables. Identified-median intervals require at least two units, an identified point estimate and at least 80% supported bootstrap draws. Bound-statistic intervals describe uncertainty in the bound, not identification of the underlying gain.','',
        'F4 uses blue circles/intervals only for identified positive medians and orange triangles for lower-bound positive medians. Every panel states the corresponding counts. A missing blue point means no identified positive median.','',
        'P1 is analysis only. The main right/left access rules, F1/F3 layouts, E1 selection and all B inputs remain unchanged. The 0.10 m raster can lose oblique kitchen openings; support restrictions and source composition remain interpretation limits.','',
        'Reproduce with python scripts/07_p1_analysis.py, inspect the new figure, record its hash in config/p1_visual_review.json, and run with --finalize. Numerical and complete-package acceptance are distinct.','']
    REPORT.write_text('\n'.join(lines),encoding='utf-8')
    write_json(ROOT/'run.json',dict(status='complete',inputs=inputs,completed_groups=20,reference_target_groups=groups,cache=cache.as_posix(),completed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
    output_paths=[ROOT/(name+'.csv') for name in TABLES]+[FIGURE.with_suffix('.png'),FIGURE.with_suffix('.pdf'),REPORT,ROOT/'run.json']
    write_json(ROOT/'acceptance.json',dict(numerical_checks_passed=True,reference_target_groups=groups,inputs=inputs,outputs={p.as_posix():sha256_file(p) for p in output_paths},full_package_complete=False))
    print(json.dumps(dict(numerical_checks_passed=True,reference_target_groups=groups)))


if __name__=='__main__':main()
