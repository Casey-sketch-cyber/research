"""Reproduce G2 geometry diagnostics and parallel 240-case controlled benchmarks."""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import time

import os
for _variable in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[_variable]="1"

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.furniture.candidates import generate_candidates
from fea.furniture.library import library
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli, start_run, write_json
from fea.solve.cpsat import solve_layout
from fea.validate import validate_layout, _reachable


def signature():
    """Hash all numerical implementation files and this benchmark driver."""
    files=sorted(Path('src/fea').rglob('*.py'))+[Path('scripts/06_revision.py')]
    return hashlib.sha256(b''.join(str(p).encode()+p.read_bytes() for p in files)).hexdigest()


def access(unit, config, gap, masks=False):
    grid=rasterize(unit,config['raster']['resolution_m'],max_gap=gap)
    reached=_reachable(grid,np.zeros_like(grid.labels,bool),config['furniture']['meta']['walking_width'])
    result = dict(empty_access=all(np.any(t & reached) for t in grid.service_targets),
        reached_cells=int(reached.sum()),target_count=len(grid.service_targets),
        failed_targets=[i for i,t in enumerate(grid.service_targets) if not np.any(t & reached)],
        gap_added_m2=grid.gap_repair['added_circulation_m2'])
    return (result,grid,reached) if masks else result


def prepare_pilot(config):
    """Prepare only the frozen pilot while unchanged nonpilot source conversion finishes.

    D1 comes from a completed current-config source cache; D2 is directly rebuilt
    from the pinned release; D3 is regenerated. The later full-corpus preparation
    must reproduce these exact serialized units before benchmark results are used.
    """
    from fea.data.archives import read_geometry_pickle
    from fea.data.d1_swiss import opaque_id
    from fea.data.d2_resplan import from_plan
    from fea.data.d3_shells import load_d3
    from fea.geometry.normalize import normalize
    from fea.geometry.audit import describe
    old=json.loads(Path('results/pilot/baseline_g2/pilot_units.json').read_text())['units']
    keys={u['unit_key'] for u in old}
    directories=[p.parent for p in Path(config['paths']['interim']).glob('corpus/'+config_hash(config)[:12]+'*/D1.done.json')]
    if not directories:raise RuntimeError('Current-config D1 conversion must finish first')
    source=max(directories,key=lambda p:(p/'D1.done.json').stat().st_mtime)
    found={}
    with (source/'D1.jsonl').open() as stream:
        for line in stream:
            if any(key in line for key in keys if key.startswith('D1:')):
                unit=Unit.from_dict(json.loads(line)['unit']);found[unit.unit_key]=unit
    with (Path(config['paths']['raw'])/'resplan/extracted/ResPlan.pkl').open('rb') as stream:
        plans=read_geometry_pickle(stream)
    for plan in plans:
        if 'D2:'+opaque_id(plan['id']) in keys:
            unit=normalize(from_plan(plan));found[unit.unit_key]=unit
    for unit in load_d3(config):
        if unit.unit_key in keys:
            assert not unit.meta.get('generator_failure')
            found[unit.unit_key]=normalize(unit)
    units=[found[u['unit_key']] for u in old]
    assert len(units)==20
    write_json('results/pilot/pilot_units.json',dict(seed=config['seed'],config_hash=config_hash(config),units=[u.to_dict() for u in units]))
    pd.DataFrame([describe(u) for u in units]).to_csv('results/pilot/pilot_units.csv',index=False)
    print(json.dumps({'pilot_units':len(units),'full_corpus_equality_check':'required before publication'}))


def prepare(config):
    """Keep the reviewed pilot keys, replacing D3 geometry with the same parameters."""
    root=Path('results/pilot')
    old=json.loads((root/'baseline_g2/pilot_units.json').read_text())
    keys=[u['unit_key'] for u in old['units']]
    frame=pd.read_parquet(Path(config['paths']['processed'])/'corpus_units.parquet')
    selected=frame.set_index('unit_key').loc[keys]
    units=[Unit.from_dict(json.loads(value)) for value in selected.unit_json]
    for before,after in zip(old['units'],units):
        if after.source=='D3':
            assert before['meta']['parameters']==after.meta['parameters']
            assert not after.meta.get('generator_failure'), 'Original pilot parameters generator_infeasible; report before replacing'
    new_units=[u.to_dict() for u in units]
    if list((root/'benchmarks').glob('*/run.json')):
        assert json.loads((root/'pilot_units.json').read_text())['units']==new_units, 'Full-corpus geometry differs from benchmark input'
    write_json(root/'pilot_units.json',dict(seed=config['seed'],config_hash=config_hash(config),units=new_units))
    selected.drop(columns='unit_json').reset_index().to_csv(root/'pilot_units.csv',index=False)
    mapping=[]
    original=pd.read_csv(root/'baseline_g2/expA_sample.csv')
    for _,row in frame[frame.source=='D3'].iterrows():
        unit=Unit.from_dict(json.loads(row.unit_json))
        mapping.append(dict(old_unit_key=row.unit_key,new_unit_key=row.unit_key if row.include else '',
            old_sample=row.unit_key in set(original.unit_key),new_sample=bool(row.in_expA_sample),
            reason='regenerated_same_parameters' if row.include else row.exclude_reason,
            **unit.meta['parameters'],candidate_attempts=unit.meta.get('candidate_attempts')))
    pd.DataFrame(mapping).to_csv(root/'d3_regeneration_mapping.csv',index=False)
    diagnostics=[]
    for before,after in zip(old['units'],units):
        row=dict(unit_key=after.unit_key,source=after.source,nia_m2=after.interior.area)
        for label,u,gap in [('old_geometry_corrected_width',Unit.from_dict(before),0),('new_geometry_no_gap',after,0),('new_geometry_closed_gap',after,.15)]:
            row.update({label+'_'+k:v for k,v in access(u,config,gap).items()})
        diagnostics.append(row)
    pd.DataFrame(diagnostics).to_csv(root/'fixed_service_diagnostic.csv',index=False)
    # Full frozen sample connectivity audit; source repair is never conditioned on FCI.
    connectivity=[]
    for _,row in tqdm(frame[frame.in_expA_sample].iterrows(),total=int(frame.in_expA_sample.sum()),desc='Gap audit'):
        unit=Unit.from_dict(json.loads(row.unit_json))
        a,before_grid,before_mask=access(unit,config,0,True)
        b,after_grid,after_mask=access(unit,config,.15,True)
        newly_reached=int((after_mask & ~before_mask & before_grid.walkable).sum())
        connectivity.append(dict(unit_key=unit.unit_key,source=unit.source,
            before_reached_cells=a['reached_cells'],after_reached_cells=b['reached_cells'],
            before_empty_access=a['empty_access'],after_empty_access=b['empty_access'],
            gap_added_m2=b['gap_added_m2'],newly_reachable_original_cells=newly_reached,connectivity_changed=newly_reached>0))
    pd.DataFrame(connectivity).to_csv(root/'gap_connectivity_audit.csv',index=False)
    print(json.dumps({'prepared_units':len(units),'D3_dropped':int(((frame.source=='D3')&~frame.include).sum())}))


def share(layouts,grid,config,household):
    """Revalidate each incumbent under each strategy before reporting differences."""
    original=deepcopy(layouts)
    for target in ('S0','S1','S2'):
        best=layouts[target]
        for source in ('S0','S1','S2'):
            candidate=deepcopy(original[source]);candidate['strategy']=target
            checked=validate_layout(candidate,grid,config,household)
            if checked['pass'] and (checked['fci']>best['fci']+1e-9 or
                (abs(checked['fci']-best['fci'])<1e-9 and checked['tb']<best['tb']-1e-9)):
                candidate.update({k:checked[k] for k in ('fci','fci_by_variant','tb','served_hours','demanded_hours')})
                candidate['validator']=checked
                candidate['solver']=deepcopy(layouts[target]['solver'])
                candidate['solver'].update(fci_solver=checked['fci'],shared_from_strategy=source,
                    own_search_fci=original[target]['fci'],shared_incumbent=True)
                best=candidate
        layouts[target]=best
    return layouts


def solve_triplet(job):
    serialized,hname,config,cache,code_hash=job
    unit=Unit.from_dict(serialized)
    household=parse_households(config['households'],config['furniture'])[hname]
    grid=rasterize(unit,config['raster']['resolution_m'],
        household.overrides.get('walking_width',config['furniture']['meta']['walking_width']),
        config['raster']['source_gap_close_m'])
    scale=household.overrides.get('global_clearance_scale',config['furniture']['meta']['global_clearance_scale'])
    candidates=generate_candidates(grid,library(config['furniture'],clearance_scale=scale),
        config['raster']['orientations_deg'],config['raster']['anchor_stride_m'])
    layouts,incumbent={},None
    for strategy in ('S0','S1','S2'):
        path=Path(cache)/(unit.unit_key.replace(':','_')+'_'+hname+'_'+strategy+'.json')
        if path.exists():
            layout=json.loads(path.read_text())
        else:
            layout=solve_layout(unit,household,strategy,config,incumbent,(grid,candidates))
            layout['code_hash']=code_hash
            write_json(path,layout)
        checked=validate_layout(layout,grid,config,household)
        assert abs(checked['fci']-layout['fci'])<1e-7
        layouts[strategy]=layout
        if checked['pass']:incumbent=layout
    layouts=share(layouts,grid,config,household)
    rows=[]
    for strategy,layout in layouts.items():
        checked=validate_layout(layout,grid,config,household)
        assert abs(checked['fci']-layout['fci'])<1e-7
        filename=unit.unit_key.replace(':','_')+'_'+hname.split('_')[0]+'_'+strategy+'.json'
        write_json(Path(cache)/'shared'/filename,layout)
        sol=layout['solver']
        rows.append(dict(unit_key=unit.unit_key,source=unit.source,nia_m2=unit.interior.area,household=hname,
            strategy=strategy,fci_validator=checked['fci'],fci_solver=sol['fci_solver'],tb=checked['tb'],
            validator_pass=checked['pass'],violations=';'.join(checked['violations']),n_items=len(layout['items']),
            solve_time_s=sol['time_s'],reach_iterations=sol['reach_iterations'],
            first_valid_time_s=sol.get('first_valid_time_s'),greedy_fci=sol.get('greedy_fci',0),
            geometric_cuts=sol.get('geometric_cuts',0),
            at_proved_bound=checked['pass'] and abs(checked['fci']-sol.get('primary_upper_bound',-1))<1e-8 and checked['tb']==0,
            timeout_with_incumbent=checked['pass'] and sol['time_s']>=config['solver']['time_limit_s']-.1,
            primary_upper_bound=sol.get('primary_upper_bound'),status=sol['status'],termination=sol.get('termination',''),
            shared_from_strategy=sol.get('shared_from_strategy',''),own_search_fci=sol.get('own_search_fci',layout['fci']),
            config_hash=config_hash(config),code_hash=code_hash,layout_file=filename))
    return rows


def benchmark(config,args):
    config=deepcopy(config)
    config['solver'].update(num_workers=args.workers,time_limit_s=args.limit,reachability_round_s=5.)
    config['raster']['anchor_stride_m']=args.stride
    digest,code_hash=config_hash(config),signature()
    input_hash=hashlib.sha256(Path('results/pilot/pilot_units.json').read_bytes()).hexdigest()
    concurrent=max(1,14//args.workers)
    output=Path('results/pilot/benchmarks')/args.arm
    output.mkdir(parents=True,exist_ok=True)
    cache=Path(config['paths']['interim'])/'g2_revision'/(digest[:12]+'_'+code_hash[:12])/args.arm
    units=json.loads(Path('results/pilot/pilot_units.json').read_text())['units']
    jobs=[(u,h,config,str(cache),code_hash) for u in units for h in config['households']['main_households']]
    expected=len(jobs)*3
    manifest=dict(arm=args.arm,num_workers=args.workers,concurrent_solves=concurrent,time_limit_s=args.limit,
        anchor_stride_m=args.stride,collision_resolution_m=config['raster']['resolution_m'],
        config_hash=digest,code_hash=code_hash,input_hash=input_hash,expected_cases=expected,cache=str(cache))
    # Cache is a project-relative research artifact, never an operational path.
    write_json(output/'run.json',manifest)
    completed=[]
    prior_checkpoints=len(list(cache.glob('*.json')))
    started=time.perf_counter()
    with ProcessPoolExecutor(max_workers=concurrent) as pool:
        futures=[pool.submit(solve_triplet,job) for job in jobs]
        for future in tqdm(as_completed(futures),total=len(futures),desc=args.arm):
            completed.extend(future.result())
            pd.DataFrame(completed).to_csv(output/'cases_PARTIAL.csv',index=False)
    elapsed=time.perf_counter()-started
    frame=pd.DataFrame(completed).sort_values(['unit_key','household','strategy'])
    assert len(frame)==expected==240
    frame.to_csv(output/'cases.csv',index=False)
    valid=frame.fci_validator
    summary={**manifest,'completed_cases':len(frame),'resumed_checkpoints':prior_checkpoints,'fresh_throughput_measurement':prior_checkpoints==0,'wall_time_s':elapsed,'wall_time_per_100_cases_s':elapsed/len(frame)*100,
        'validator_pass_cases':int(frame.validator_pass.sum()),'distribution_includes_invalid_at_zero':True,'fci_distribution':{str(q):float(valid.quantile(q)) for q in (0,.1,.25,.5,.75,.9,1)},
        'mean_fci':float(valid.mean()),'median_iterations':float(frame.reach_iterations.median()),
        'mean_first_valid_time_s':float(frame.first_valid_time_s.mean()) if frame.first_valid_time_s.notna().any() else None,
        'shared_improvements':int((frame.fci_validator>frame.own_search_fci+1e-9).sum())}
    write_json(output/'summary.json',summary)
    print(json.dumps(summary))


def main():
    parser=prepare_cli(__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--prepare-pilot',action='store_true')
    parser.add_argument('--arm',default='w1_s20_t60')
    parser.add_argument('--workers',type=int,choices=[1,2,4,8],default=1)
    parser.add_argument('--limit',type=int,choices=[30,60],default=60)
    parser.add_argument('--stride',type=float,choices=[.1,.2],default=.2)
    args=parser.parse_args()
    config,_,_=start_run(args,'06_revision')
    if args.dry_run:
        print('Would prepare the unchanged pilot or benchmark all 240 cases with independent validation.');return
    if args.prepare_pilot:prepare_pilot(config)
    elif args.prepare:prepare(config)
    else:benchmark(config,args)


if __name__=='__main__':main()
