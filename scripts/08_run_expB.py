"""Fresh three-algorithm B comparison with a fixed runtime pilot and resumable cases."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[name]='1'
from concurrent.futures import ProcessPoolExecutor,as_completed
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm
from fea.config import config_hash
from fea.geometry.unit import Unit
from fea.geometry.raster import rasterize
from fea.furniture.library import library
from fea.furniture.candidates import generate_candidates
from fea.households import parse_households
from fea.solve.cpsat import solve_layout
from fea.validate import validate_layout
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase07_corrected import load_corrected
from phase08_algorithms import empty_layout,footprint,anneal

ALGORITHMS=['greedy_footprint','simulated_annealing','cp_sat']


def select_pilot(sample):
    """One median-area pair per source/household, without any outcome data."""
    chosen=[]
    for _,frame in sample.groupby(['source','household'],sort=True):
        middle=frame.nia_m2.median();frame=frame.assign(distance=(frame.nia_m2-middle).abs())
        chosen.append(frame.sort_values(['distance','unit_key']).iloc[0].drop('distance'))
    return pd.DataFrame(chosen).sort_values(['source','household']).reset_index(drop=True)


def run_pair(job):
    serialized,row,base,production,settings,cache,fingerprint=job
    unit=Unit.from_dict(json.loads(serialized));config=deepcopy(base)
    group='small' if row['nia_m2']<=20+1e-8 else 'large';budget=production[group]
    config['solver'].update({k:budget[k] for k in ['num_workers','time_limit_s']});config['raster']['anchor_stride_m']=budget['anchor_stride_m']
    household=parse_households(config['households'],config['furniture'])[row['household']]
    digest=config_hash(config);stem=row['unit_key'].replace(':','_')+'_'+row['household'].split('_')[0]
    seed=config['seed']+int(hashlib.sha256((row['unit_key']+'|'+row['household']).encode()).hexdigest()[:8],16)
    cache=Path(cache);outputs=[]
    for algorithm in ALGORITHMS:
        path=cache/(stem+'_'+algorithm+'.json');record=cache/(stem+'_'+algorithm+'_record.json')
        if path.exists() and record.exists():
            saved=json.loads(record.read_text())
            if saved['code_hash']!=fingerprint or saved['config_hash']!=digest or saved['layout_sha256']!=sha256_file(path):raise ValueError('B checkpoint provenance changed')
            outputs.append(saved);continue
        started=time.perf_counter()
        write_json(cache/(stem+'_progress.json'),dict(algorithm=algorithm,status='preparing',restart=0,iterations=0,updated_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
        grid=rasterize(unit,config['raster']['resolution_m'],config['furniture']['meta']['walking_width'],config['raster']['source_gap_close_m'])
        items=library(config['furniture'],'S2');candidates=generate_candidates(grid,items,config['raster']['orientations_deg'],config['raster']['anchor_stride_m'])
        prepared=time.perf_counter();empty=empty_layout(unit,household,grid,digest)
        def progress(restart,iterations,fci):
            write_json(cache/(stem+'_progress.json'),dict(algorithm=algorithm,status='running',restart=restart,iterations=iterations,best_fci=fci,updated_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
        if algorithm=='greedy_footprint':layout=footprint(empty,grid,items,candidates,household,config)
        elif algorithm=='simulated_annealing':layout=anneal(empty,grid,items,candidates,household,config,settings['annealing'],seed,progress=progress)
        else:layout=solve_layout(unit,household,'S2',config,incumbent=None,prepared=(grid,candidates))
        solved=time.perf_counter();checked=validate_layout(layout,grid,config,household)
        layout['algorithm']=algorithm;layout['code_hash']=fingerprint;layout['config_hash']=digest;layout['validator']=checked
        layout.update({k:checked[k] for k in ['fci','fci_by_variant','tb','served_hours','demanded_hours']});write_json(path,layout)
        info=dict(unit_key=unit.unit_key,source=unit.source,nia_m2=row['nia_m2'],household=row['household'],strategy='S2',algorithm=algorithm,
            validator_pass=checked['pass'],fci_validator=checked['fci'],tb=checked['tb'],violations=';'.join(checked['violations']),violation_count=len(checked['violations']),
            budget_group=group,preparation_time_s=prepared-started,algorithm_time_s=solved-prepared,final_validation_time_s=time.perf_counter()-solved,
            elapsed_time_s=time.perf_counter()-started,config_hash=digest,code_hash=fingerprint,layout_file=path.name,layout_sha256=sha256_file(path),
            status=layout.get('solver',{}).get('status','COMPLETE'),annealing_proposals=layout.get('annealing',{}).get('total_proposals',0),
            candidate_poses=sum(len(v) for v in candidates.values()),seed=seed if algorithm=='simulated_annealing' else config['seed'])
        write_json(record,info);outputs.append(info)
        write_json(cache/(stem+'_progress.json'),dict(algorithm=algorithm,status='complete',updated_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
    return outputs


def check_results(frame,sample):
    keys=['unit_key','household','algorithm'];expected={(r.unit_key,r.household,a) for r in sample.itertuples() for a in ALGORITHMS}
    actual=list(frame[keys].itertuples(index=False,name=None))
    if len(actual)!=len(expected) or len(set(actual))!=len(actual) or set(actual)!=expected:raise ValueError('B cases missing or duplicated')
    if not np.isfinite(frame.fci_validator).all() or not frame.fci_validator.between(0,1).all():raise ValueError('Invalid B metric')
    if not frame.loc[~frame.validator_pass,'fci_validator'].eq(0).all():raise ValueError('Invalid layouts must retain independent zero score')
    if not frame.loc[frame.algorithm=='simulated_annealing','annealing_proposals'].eq(60000).all():raise ValueError('B annealing budget incomplete')
    return dict(passed=True,cases=len(frame),pairs=len(sample),invalid_outputs=int((~frame.validator_pass).sum()),invalid_outputs_retained=True)


def execute(config,args):
    root=Path('results/expB');ready=json.loads((root/'readiness.json').read_text());sample=pd.read_csv(root/'instances.csv')
    if not ready['passed'] or sha256_file(root/'instances.csv')!=ready['sample_sha256'] or config_hash(config)!=ready['main_config_hash']:raise ValueError('B corrected readiness changed')
    for name,digest in ready['outputs'].items():
        if sha256_file(root/name)!=digest:raise ValueError('B reference audit changed')
    f3=Path('results/expA_f3/package_acceptance.json')
    if sha256_file(f3)!=ready['F3_package_sha256']:raise ValueError('F3 acceptance changed')
    main,gate=load_corrected(config)
    if gate['combined_sha256']!=ready['F1_solutions_sha256']:raise ValueError('B corrected baseline changed')
    spec_path=Path('config/expB_algorithms.yaml');settings=yaml.safe_load(spec_path.read_text())
    if settings['annealing']['iterations']!=20000 or settings['annealing']['restarts']!=3:raise ValueError('Reviewed B annealing counts changed')
    preflight=Path('results/expB/preflight.json');test=json.loads(preflight.read_text())
    if not test['passed']:raise ValueError('B scoring tests failed')
    for name,digest in test['implementation'].items():
        if sha256_file(Path(name))!=digest:raise ValueError('B tests are stale')
    pilot=select_pilot(sample);pilot_path=root/'pilot_instances.csv'
    if pilot_path.exists() and pilot_path.read_text()!=pilot.to_csv(index=False):raise ValueError('B pilot membership changed')
    pilot.to_csv(pilot_path,index=False)
    files=sorted(Path('src/fea').rglob('*.py'))+[Path('scripts/06_revision.py'),Path('scripts/phase08_algorithms.py'),Path('scripts/08_run_expB.py')]
    implementation={p.as_posix():sha256_file(p) for p in files}
    inputs=dict(main_config_hash=config_hash(config),sample_sha256=ready['sample_sha256'],readiness_sha256=sha256_file(root/'readiness.json'),
        pilot_sha256=sha256_file(pilot_path),settings_sha256=sha256_file(spec_path),preflight_sha256=sha256_file(preflight),implementations=implementation)
    fingerprint=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest();cache=Path(config['paths']['interim'])/'expB'/fingerprint[:16]
    selected=pilot if args.pilot else sample;destination=root/'pilot' if args.pilot else root
    if not args.pilot:
        accepted=json.loads((root/'pilot'/'acceptance.json').read_text())
        if not accepted['passed'] or accepted['code_hash']!=fingerprint:raise ValueError('Matching runtime pilot not accepted')
    manifest=dict(inputs=inputs,code_hash=fingerprint,cache=cache.as_posix(),settings=settings,stage='pilot' if args.pilot else 'full',
        expected_pairs=len(selected),expected_cases=len(selected)*3,strategies=['S2'],algorithms=ALGORITHMS,
        started_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'))
    previous=destination/'run.json'
    if previous.exists():
        saved=json.loads(previous.read_text())
        if saved['code_hash']!=fingerprint:raise ValueError('B run fingerprint changed; preserve original run')
        manifest['started_at_utc']=saved['started_at_utc']
    write_json(previous,{**manifest,'status':'running'})
    corpus=pd.read_parquet(Path(config['paths']['processed'])/'corpus_units.parquet',columns=['unit_key','unit_json']).set_index('unit_key')
    production=json.loads(Path('results/expA_f1/run.json').read_text())['production_settings'];rows=[];started=time.perf_counter()
    groups=[('pilot',selected,3)] if args.pilot else [('small',selected[selected.nia_m2<=20+1e-8],3),('large',selected[selected.nia_m2>20+1e-8],12)]
    for group,part,workers in groups:
        jobs=[(corpus.loc[r.unit_key,'unit_json'],r._asdict(),config,production,settings,str(cache),fingerprint) for r in part.itertuples(index=False)]
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for future in tqdm(as_completed([pool.submit(run_pair,job) for job in jobs]),total=len(jobs),desc='B '+group):
                rows.extend(future.result());write_json(destination/'progress.json',dict(completed_pairs=len(rows)//3,completed_cases=len(rows),expected_cases=len(selected)*3,elapsed_this_invocation_s=time.perf_counter()-started,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
    frame=pd.DataFrame(rows).sort_values(['unit_key','household','algorithm']);checked=check_results(frame,selected);frame.to_csv(destination/'cases.csv',index=False)
    elapsed=time.perf_counter()-started
    if args.pilot:
        estimates=[]
        for algorithm,g in frame.groupby('algorithm'):
            # Source/household coverage exists, but one pair per cell is a planning sample.
            means=g.set_index(['source','household']).elapsed_time_s
            total=sum(float(means.loc[r.source,r.household])/(3 if r.nia_m2<=20+1e-8 else 12) for r in sample.itertuples())
            estimates.append(dict(algorithm=algorithm,pilot_pairs=len(g),mean_elapsed_s=g.elapsed_time_s.mean(),max_elapsed_s=g.elapsed_time_s.max(),projected_parallel_hours=total/3600))
        pd.DataFrame(estimates).to_csv(destination/'runtime_projection.csv',index=False)
    write_json(destination/'acceptance.json',{**checked,'code_hash':fingerprint,'cases_sha256':sha256_file(destination/'cases.csv'),'all_proposals_completed':True})
    write_json(previous,{**manifest,'status':'complete','completed_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'wall_time_this_invocation_s':elapsed})
    print(json.dumps({**checked,'wall_hours':elapsed/3600}))


def main():
    parser=prepare_cli(__doc__);parser.add_argument('--pilot',action='store_true');args=parser.parse_args();config,_,_=start_run(args,'08_run_expB')
    if args.dry_run:print('Would run the immutable B pilot/full sample with fresh footprint, 60000-proposal annealing and standalone S2 CP-SAT.');return
    import fcntl
    with Path('.tmp/expB_execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);execute(config,args)


if __name__=='__main__':main()
