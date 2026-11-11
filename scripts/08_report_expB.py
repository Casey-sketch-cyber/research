"""Independently validate B outputs and publish the three-algorithm comparison."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
from tqdm import tqdm
from fea.config import config_hash
from fea.geometry.unit import Unit
from fea.geometry.raster import rasterize
from fea.households import parse_households
from fea.validate import validate_layout
from fea.io import prepare_cli,start_run,write_json,sha256_file

ROOT=Path('results/expB')


def audit_job(job):
    serialized,rows,base,production,cache,fingerprint=job;unit=Unit.from_dict(json.loads(serialized));output=[]
    grid=rasterize(unit,base['raster']['resolution_m'],base['furniture']['meta']['walking_width'],base['raster']['source_gap_close_m'])
    for row in rows:
        config=deepcopy(base);settings=production[row['budget_group']]
        config['solver'].update({k:settings[k] for k in ['num_workers','time_limit_s']});config['raster']['anchor_stride_m']=settings['anchor_stride_m']
        h=parse_households(config['households'],config['furniture'])[row['household']]
        path=Path(cache)/row['layout_file'];layout=json.loads(path.read_text())
        if sha256_file(path)!=row['layout_sha256'] or row['code_hash']!=fingerprint or layout['code_hash']!=fingerprint:raise ValueError('B saved layout/fingerprint differs')
        if layout['config_hash']!=row['config_hash'] or config_hash(config)!=row['config_hash']:raise ValueError('B saved configuration differs')
        if any(layout[k]!=row[k] for k in ['unit_key','household','strategy','algorithm']):raise ValueError('B saved identity differs')
        checked=validate_layout(layout,grid,config,h)
        if checked['pass']!=row['validator_pass'] or checked['violations']!=layout['validator']['violations'] or abs(checked['fci']-row['fci_validator'])>1e-8 or abs(checked['tb']-row['tb'])>1e-8:raise ValueError('B independent validation disagrees')
        if row['algorithm']=='simulated_annealing' and (layout['annealing']['total_proposals']!=60000 or len(layout['annealing']['restarts'])!=3):raise ValueError('B saved annealing budget incomplete')
        output.append(dict(unit_key=row['unit_key'],household=row['household'],algorithm=row['algorithm'],valid=checked['pass'],
            fci_validator=checked['fci'],tb=checked['tb'],n_violations=len(checked['violations']),violation_types=';'.join(checked['violations']),layout_sha256=sha256_file(path)))
    return output


def summarize(frame):
    rows=[]
    for scope,key in [('overall',None),('source','source'),('household','household'),('budget_group','budget_group')]:
        groups=[('all',frame)] if key is None else frame.groupby(key)
        for label,g in groups:
            for algorithm,a in g.groupby('algorithm'):
                rows.append(dict(scope=scope,group=label,algorithm=algorithm,n_cases=len(a),validity_rate=float(a.validator_pass.mean()),
                    invalid_outputs=int((~a.validator_pass).sum()),mean_fci=float(a.fci_validator.mean()),median_fci=float(a.fci_validator.median()),
                    mean_preparation_s=float(a.preparation_time_s.mean()),mean_algorithm_s=float(a.algorithm_time_s.mean()),
                    mean_elapsed_s=float(a.elapsed_time_s.mean()),median_elapsed_s=float(a.elapsed_time_s.median()),max_elapsed_s=float(a.elapsed_time_s.max())))
    return pd.DataFrame(rows)


def paired_statistics(frame,count,confidence,seed):
    pairs=frame.pivot(index=['unit_key','household'],columns='algorithm',values='fci_validator')
    pairs=pairs.join(frame.drop_duplicates(['unit_key','household']).set_index(['unit_key','household'])[['source']]).reset_index()
    # Sample physical units within source, retaining all sampled households per unit.
    clusters=[[g.index.to_numpy() for _,g in part.groupby('unit_key')] for _,part in pairs.groupby('source')]
    rng=np.random.default_rng(seed);contrasts=[('cp_sat','greedy_footprint'),('cp_sat','simulated_annealing'),('simulated_annealing','greedy_footprint')]
    values=np.column_stack([pairs[a]-pairs[b] for a,b in contrasts]);draws=[]
    for _ in range(count):
        indices=np.concatenate([group[i] for group in clusters for i in rng.integers(0,len(group),size=len(group))]);draws.append(values[indices].mean(axis=0))
    lo,hi=np.quantile(np.asarray(draws),[(1-confidence)/2,1-(1-confidence)/2],axis=0)
    return pd.DataFrame([dict(comparison=a+' minus '+b,n_pairs=len(pairs),mean_difference=float(values[:,i].mean()),ci_lo=float(lo[i]),ci_hi=float(hi[i]),
        share_better=float((values[:,i]>1e-9).mean()),share_worse=float((values[:,i]<-1e-9).mean()),bootstrap_resamples=count,
        resampling='Physical-unit clusters within source; all sampled households retained') for i,(a,b) in enumerate(contrasts)])


def main():
    parser=prepare_cli(__doc__);parser.add_argument('--wait',action='store_true');args=parser.parse_args();config,_,_=start_run(args,'08_report_expB')
    if args.dry_run:print('Would wait if requested, independently revalidate all B layouts and report retained invalid scores, paired comparisons and runtime.');return
    while True:
        path=ROOT/'run.json';run=json.loads(path.read_text()) if path.exists() else {}
        continuation=json.loads((ROOT/'continuation.json').read_text())
        if continuation.get('status')=='failed':raise ValueError('B execution failed; do not analyse incomplete outputs')
        if run.get('status')=='complete':break
        if not args.wait:raise ValueError('Full B is not complete')
        write_json(ROOT/'analysis_status.json',dict(status='waiting_for_full_B'))
        time.sleep(20)
    write_json(ROOT/'analysis_status.json',dict(status='auditing'))
    for name,digest in run['inputs']['implementations'].items():
        if sha256_file(Path(name))!=digest:raise ValueError('B implementation changed')
    acceptance=json.loads((ROOT/'acceptance.json').read_text());frame=pd.read_csv(ROOT/'cases.csv');sample=pd.read_csv(ROOT/'instances.csv')
    if not acceptance['passed'] or acceptance['cases_sha256']!=sha256_file(ROOT/'cases.csv'):raise ValueError('B execution acceptance differs')
    spec=importlib.util.spec_from_file_location('b_driver','scripts/08_run_expB.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
    driver.check_results(frame,sample)
    if config_hash(config)!=run['inputs']['main_config_hash'] or sha256_file(ROOT/'instances.csv')!=run['inputs']['sample_sha256']:raise ValueError('B current inputs differ')
    meta=sample.set_index(['unit_key','household']);index=pd.MultiIndex.from_frame(frame[['unit_key','household']])
    if not np.allclose(frame.nia_m2,meta.loc[index,'nia_m2'],atol=1e-8,rtol=0) or not frame.source.to_numpy().tolist()==meta.loc[index,'source'].to_numpy().tolist():raise ValueError('B sample metadata differs')
    corpus=pd.read_parquet(Path(config['paths']['processed'])/'corpus_units.parquet',columns=['unit_key','unit_json']).set_index('unit_key')
    production=json.loads(Path('results/expA_f1/run.json').read_text())['production_settings']
    jobs=[(corpus.loc[key,'unit_json'],g.to_dict('records'),config,production,run['cache'],run['code_hash']) for key,g in frame.groupby('unit_key')]
    audits=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for values in tqdm(pool.map(audit_job,jobs),total=len(jobs),desc='B saved-layout audit'):audits.extend(values)
    pd.DataFrame(audits).to_csv(ROOT/'layout_revalidation.csv',index=False)
    exported=frame.rename(columns=dict(validator_pass='valid',violation_count='n_violations',violations='violation_types',elapsed_time_s='runtime_s'))
    exported.to_csv(ROOT/'algorithms.csv',index=False);summary=summarize(frame);summary.to_csv(ROOT/'algorithm_summary.csv',index=False)
    effects=paired_statistics(frame,config['experiments']['bootstrap']['n'],config['experiments']['bootstrap']['ci'],config['seed']);effects.to_csv(ROOT/'paired_algorithm_effects.csv',index=False)
    reference=pd.read_csv(ROOT/'corrected_main_reference.csv')
    comparison=frame[frame.algorithm=='cp_sat'].merge(reference[['unit_key','household','fci_validator','result_origin']],on=['unit_key','household'],suffixes=('_fresh','_historical'),validate='one_to_one')
    comparison['fresh_minus_historical']=comparison.fci_validator_fresh-comparison.fci_validator_historical
    comparison.to_csv(ROOT/'fresh_vs_historical_CP.csv',index=False)
    overall=summary[summary.scope=='overall'][['algorithm','n_cases','validity_rate','mean_fci','median_fci','mean_preparation_s','mean_algorithm_s','mean_elapsed_s','median_elapsed_s']]
    pilot_run=json.loads((ROOT/'pilot'/'run.json').read_text())
    report=Path('reports/phase_08_B_results.md');lines=['# Phase 8 — Algorithm comparison results','','## Completed benchmark','',
        f"The frozen {len(sample)} S2 pairs produced {len(frame)} algorithm outputs. All outputs were independently rescored from saved layouts; invalid outputs remain included with their validator score (zero). Three algorithms share candidate generation and the corrected main configuration. Measured wall time is {pilot_run['wall_time_this_invocation_s']/3600:.6f} hours for the pilot and {run['wall_time_this_invocation_s']/3600:.6f} additional hours for the full stage (sum {(pilot_run['wall_time_this_invocation_s']+run['wall_time_this_invocation_s'])/3600:.6f} hours). The full stage reuses identical pilot checkpoints; individual runtime statistics retain each actual execution once.",'',
        overall.to_markdown(index=False,floatfmt='.6f'),'','## Paired FCI comparisons','',effects.to_markdown(index=False,floatfmt='.6f'),'','## Settings, timing and scope','',
        'The greedy arm runs only descending-footprint, first-improving feasible wall-adjacent placement and exhausts its scan. Annealing runs all 20000 proposals × 3 restarts, initialized only by standalone greedy; its initialization is included in its own runtime. The penalty and geometric temperature schedule were frozen before B outcomes. Every new best found by fast scoring and every final output is independently validated. CP-SAT uses its normal internal initializer and the unchanged per-unit small/large budgets; no saved A/F1/F3 layout is supplied.','',
        'Each algorithm receives separately rebuilt raster/candidate inputs. Preparation, algorithm and final validation time are reported separately; runtime_s includes all three plus saving overhead. Times are observed under the recorded concurrent benchmark, not isolated latency measurements. Source, household and budget-group summaries are in algorithm_summary.csv. The original 200 pairs balance 36 strata, so the pooled mean describes this benchmark rather than a population-weighted housing stock.','',
        f"Fresh standalone CP-SAT differs from historical shared-strategy main evidence in {int((comparison.fresh_minus_historical.abs()>1e-8).sum())} pairs; {int((comparison.fresh_minus_historical < -1e-8).sum())} are lower. Preserve these differences: historical A used preceding/shared-strategy incumbents, whereas B measures fresh standalone S2. Corrected main references are retained for traceability, not substituted into B scores or used as baseline starting answers.",'',
        'This completes B numerical and saved-output checks; the remaining D/R/ablations, C, K, HK and literature work still precedes G3. Reproduce with scripts/08_continue_expB.py followed by scripts/08_report_expB.py.','']
    report.write_text('\n'.join(lines),encoding='utf-8')
    paths=[ROOT/p for p in ['algorithms.csv','algorithm_summary.csv','paired_algorithm_effects.csv','fresh_vs_historical_CP.csv','layout_revalidation.csv']]+[report]
    write_json(ROOT/'report_acceptance.json',dict(passed=True,full_B_analysis_complete=True,independently_revalidated=len(audits),
        cases_sha256=sha256_file(ROOT/'cases.csv'),run_sha256=sha256_file(ROOT/'run.json'),implementation_sha256=sha256_file(Path(__file__)),
        outputs={p.as_posix():sha256_file(p) for p in paths},completed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
    write_json(ROOT/'analysis_status.json',dict(status='complete',independently_revalidated=len(audits)))
    print(json.dumps(dict(passed=True,cases=len(frame),independently_revalidated=len(audits))))


if __name__=='__main__':
    try:main()
    except Exception as error:
        write_json(ROOT/'analysis_status.json',dict(status='failed',exception_type=type(error).__name__,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
        raise
