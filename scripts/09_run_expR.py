"""Supporting room comparison R after B and D, with independent saved-layout accounting."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[name]='1'
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
from tqdm import tqdm
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase07_corrected import load_corrected
from phase09_activity_jobs import make_shells,reproduction_job,generalization_job
from phase09_activity_analysis import assemble_generalization,bridge_to_p1,summarize,plot_results

ROOT=Path('results/expR')


def verify_d():
    path=Path('results/expD/acceptance.json')
    if not path.exists():return False
    gate=json.loads(path.read_text())
    if not gate.get('passed'):raise ValueError('D not accepted')
    for key in ['input_sha256','outputs']:
        for name,digest in gate[key].items():
            if sha256_file(Path(name))!=digest:raise ValueError('Accepted D evidence changed')
    return True


def verify_p1():
    root=Path('results/expA_f1/analysis_p1');package=json.loads((root/'package_acceptance.json').read_text());numeric=json.loads((root/'acceptance.json').read_text())
    if not package.get('passed') or not package.get('P1_complete') or not numeric['numerical_checks_passed']:raise ValueError('P1 incomplete')
    if sha256_file(root/'acceptance.json')!=package['numerical_acceptance_sha256']:raise ValueError('P1 acceptance differs')
    for name,digest in numeric['outputs'].items():
        if sha256_file(Path(name))!=digest:raise ValueError('P1 accepted output differs')


def finalize():
    gate=json.loads((ROOT/'acceptance.json').read_text());review_path=Path('config/expR_visual_review.json');review=json.loads(review_path.read_text())
    if not gate['numerical_checks_passed'] or not review['passed']:raise ValueError('R numerical or visual review not passed')
    for field in ['inputs','outputs']:
        for name,digest in gate[field].items():
            if sha256_file(Path(name))!=digest:raise ValueError('R accepted evidence changed')
    for name,digest in review['reviewed_files'].items():
        if sha256_file(Path(name))!=digest:raise ValueError('R visual review stale')
    expected={str(ROOT/'figures/F11_supporting_R.png'),str(ROOT/'figures/F11_supporting_R.pdf')}
    if set(review['reviewed_files'])!=expected:raise ValueError('R figure review incomplete')
    write_json(ROOT/'package_acceptance.json',dict(passed=True,R_complete=True,numerical_acceptance_sha256=sha256_file(ROOT/'acceptance.json'),
        visual_review_sha256=sha256_file(review_path),completed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
    print(json.dumps(dict(passed=True,R_complete=True)))


def main():
    parser=prepare_cli(__doc__);parser.add_argument('--wait',action='store_true');parser.add_argument('--finalize',action='store_true');args=parser.parse_args()
    config,digest,_=start_run(args,'09_run_expR')
    import fcntl
    lock=Path('.tmp/expR.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if args.dry_run:print('Would wait for D, run approximate R1, independently audit all H1/H2 S0/S2 layouts, join P1 and generate F11.');return
    if args.finalize:finalize();return
    while not verify_d():
        for path in [Path('results/expD/status.json'),Path('results/expB/analysis_status.json'),Path('results/expB/continuation.json')]:
            if path.exists() and json.loads(path.read_text()).get('status')=='failed':raise ValueError('Preceding phase failed; R remains unstarted')
        if not args.wait:raise ValueError('D not accepted')
        write_json(ROOT/'status.json',dict(status='waiting_for_D_acceptance'));time.sleep(20)
    started=time.perf_counter();verify_p1();frame,f1=load_corrected(config)
    source=json.loads(Path('config/expR_source.json').read_text());source_manifest=json.loads(Path('results/literature/fulltext_checks.json').read_text())
    if source['sha256']!=source_manifest['sha256'] or any(not r['page'] or not r['section'] for r in source['source_values']):raise ValueError('R source provenance missing')
    files=[Path(p) for p in ['config/expR_source.json','results/literature/fulltext_checks.json','results/expD/acceptance.json',
        'results/expA_f1/acceptance.json','results/expA_f1/solutions.csv','results/expA_f1/original_config_snapshot.json','results/expA/run.json',
        'results/expA_f1/analysis_p1/package_acceptance.json','results/expA_f1/analysis_p1/paired_equivalent_area.csv','results/corpus/corpus_units.csv',
        'scripts/09_run_expR.py','scripts/phase09_activity_jobs.py','scripts/phase09_activity_analysis.py','scripts/phase09_activity_validator.py',
        'scripts/phase09_metrics.py','scripts/phase07_corrected.py','tests/test_phase09_activity.py','tests/test_phase09_activity_analysis.py']]+sorted(Path('src/fea').rglob('*.py'))
    inputs={p.as_posix():sha256_file(p) for p in files}
    inputs[(Path(config['paths']['processed'])/'corpus_units.parquet').as_posix()]=sha256_file(Path(config['paths']['processed'])/'corpus_units.parquet')
    fingerprint=hashlib.sha256(json.dumps(dict(inputs=inputs,config_hash=digest),sort_keys=True).encode()).hexdigest()
    cache=Path(config['paths']['interim'])/'expR'/fingerprint[:16];cache.mkdir(parents=True,exist_ok=True)
    if (ROOT/'run.json').exists() and json.loads((ROOT/'run.json').read_text())['code_hash']!=fingerprint:raise ValueError('R inputs changed; preserve prior run')
    manifest=dict(status='running',config_hash=digest,code_hash=fingerprint,cache=cache.as_posix(),inputs=inputs,started_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'))
    write_json(ROOT/'run.json',manifest);write_json(ROOT/'status.json',dict(status='running_R1'))
    values=pd.DataFrame(source['source_values']);values['doi']=source['doi'];values['source_sha256']=source['sha256'];values.to_csv(ROOT/'source_values.csv',index=False)
    shells=make_shells(config);write_json(ROOT/'reproduction_shells.json',dict(units=[u.to_dict() for u in shells],exact_source_reproduction=False))
    production=json.loads(Path('results/expA_f1/run.json').read_text())['production_settings'];households=config['experiments']['R_single_room_test']['households']
    jobs=[(u.to_dict(),h,config,production['small'],str(cache/'R1'),fingerprint) for u in shells for h in households];r1=[]
    with ProcessPoolExecutor(max_workers=3) as pool:
        for future in tqdm(as_completed([pool.submit(reproduction_job,j) for j in jobs]),total=len(jobs),desc='R1 comparisons'):
            r1.extend(future.result());write_json(ROOT/'progress.json',dict(stage='R1',completed=len(r1),expected=len(jobs)*2))
    reproduction=pd.DataFrame(r1).sort_values(['condition','aspect_ratio','household','strategy']);reproduction.to_csv(ROOT/'reproduction.csv',index=False)
    write_json(ROOT/'status.json',dict(status='running_R2_saved_layout_audit'))
    selected=frame[frame.household.isin(households)&frame.strategy.isin(['S0','S2'])]
    if not selected.result_origin.eq('original_A_H1H2_verified_unaffected').all():raise ValueError('R2 expected original unaffected evidence')
    corpus=pd.read_parquet(Path(config['paths']['processed'])/'corpus_units.parquet',columns=['unit_key','unit_json']).set_index('unit_key')
    original=json.loads(Path('results/expA/run.json').read_text());original_config=json.loads(Path('results/expA_f1/original_config_snapshot.json').read_text())
    jobs=[(corpus.loc[key,'unit_json'],g.to_dict('records'),original_config,production,original['cache'],str(cache/'R2'),fingerprint) for key,g in selected.groupby('unit_key')];r2=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for future in tqdm(as_completed([pool.submit(generalization_job,j) for j in jobs]),total=len(jobs),desc='R2 saved-layout audit'):
            r2.extend(future.result());write_json(ROOT/'progress.json',dict(stage='R2',completed=len(r2),expected=len(selected)))
    audits=pd.DataFrame(r2).sort_values(['unit_key','household','strategy'])
    if len(audits)!=len(selected) or audits[['unit_key','household','strategy']].duplicated().any() or not audits.validator_pass.all():raise ValueError('R2 independent audit incomplete')
    audits.to_csv(ROOT/'layout_revalidation.csv',index=False)
    geometry=pd.read_csv('results/corpus/corpus_units.csv',low_memory=False);generalization=assemble_generalization(audits,geometry)
    area=pd.read_csv('results/expA_f1/analysis_p1/paired_equivalent_area.csv');bridge=bridge_to_p1(generalization,area)
    summaries,associations=summarize(generalization,bridge,source)
    for name,value in [('generalization',generalization),('bridge',bridge),('generalization_summary',summaries),('associations',associations)]:
        value['analysis_config_hash']=digest;value['analysis_code_hash']=fingerprint;value.to_csv(ROOT/(name+'.csv'),index=False)
    plot_results(reproduction,generalization,bridge,source,ROOT/'figures');write_json(ROOT/'status.json',dict(status='numerical_complete_visual_review_pending'))
    elapsed=time.perf_counter()-started
    point=summaries.query("population in ['real_plans','D3'] and scope == 'overall'")
    report=Path('reports/phase_09_R_results.md');report.write_text('\n'.join([
        '# Phase 9b — Supporting room comparison and generalization','','## Completed numerical work','',
        f"R1 completed {len(reproduction)} independently validated outputs on four comparison envelopes × H1/H2 × S0/S2. R2 independently revalidated {len(audits)} saved main layouts on {generalization.unit_key.nunique()} units. R2/R3 performed no new solves; all signed gains and zero effects remain. This invocation took {elapsed/3600:.6f} hours including reproduction, saved-layout checks and analysis.",'',
        'Source values and PDF page/section references are in source_values.csv. R1 layouts and resumable R2 evidence are private cache artifacts linked by hashes. F11 is generated; full package acceptance additionally requires actual figure inspection.','',
        '## R1: approximate comparison, not exact reproduction','',
        'Bu & Che Mat report a 4 × 3 m bedroom and about 5–5.5 m² static activity area versus about 8 m² with folded furniture. This is a conceptual comparison, not an occupied-home area measurement. Their prose and Figure 10 disagree on bed width and wardrobe depth, and their activity estimate deducts clearances. Our prescribed body-only measure differs. Thus agreement or disagreement in a numerical ratio cannot establish exact reproduction.','',
        reproduction[['condition','aspect_ratio','household','strategy','free_activity_area_day_m2','gain_m2','gain_rel','fci_validator']].to_markdown(index=False,floatfmt='.6f'),'','## R2: generalization of the body-only measure','',
        point[['population','household','n_units','median_gain_m2','median_gain_rel','share_negative','share_zero','share_below_reported_band','share_near_reported_gain','share_above_reported_band']].to_markdown(index=False,floatfmt='.6f'),'',
        'Near the reported approximate 60% means the descriptive predeclared 55–65% band, not source uncertainty. Area-bin summaries and associations with NIA, aspect ratio and compactness are included in the CSVs. Main objectives optimize functional service and transformation burden; daytime open space is not maximized, and beds are not forced to fold to reproduce the source ratio.','',
        '## R3 and interpretation boundaries','',
        'Bridge.csv uses the accepted P1 paired equivalent-area definition. Real plans use the real-plan reference and D3 uses D3; pooled-reference inversion is a separate sensitivity. Identified relative area gains and lower bounds are separate columns. Correlations exclude bound-only rows; triangles in F11 mark lower bounds, not exact estimates. Relative equivalent-area gain divides by NIA, while relative daytime body-free area gain divides by S0 body-free area: these are different denominators and concepts.','',
        'The primary daytime measure is continuous NIA minus the union of outward-rounded raster furniture bodies in the normal/day slot. It includes fixed-service space within NIA, does not deduct clearances and does not assert that all remaining area is accessible. Secondary furnishable-only and clearance-subtracted raster area fields preserve that distinction. R1 D3 fallbacks include kitchen/toilet pods unlike the bedroom; the known-bedroom envelope still uses our catalogue and schedules, so it is also approximate. No dimensions or search parameters were tuned to match the paper.','',
        '## Verification and next work','',
        'PASS: source checksum and numeric page references, full B/D/P1 prerequisite chain, corrected F1 membership, original H1/H2 layout hashes/configurations, every independent saved-layout score, no missing/duplicate paired records, and identified/bound separation. Visual review remains a distinct package gate. See Q32 for the source ambiguity. Next: prespecified ablations, C, reduced K, HK and literature screening before G3.','',
        'Reproduce: PYTHONPATH=src:scripts python scripts/09_run_expR.py; after actual figure review, add config/expR_visual_review.json and run --finalize.','']),encoding='utf-8')
    paths=[ROOT/p for p in ['source_values.csv','reproduction_shells.json','reproduction.csv','layout_revalidation.csv','generalization.csv','bridge.csv','generalization_summary.csv','associations.csv','figures/F11_supporting_R.png','figures/F11_supporting_R.pdf']]+[report]
    for name,expected in inputs.items():
        if sha256_file(Path(name))!=expected:raise ValueError('R input changed during execution')
    write_json(ROOT/'acceptance.json',dict(numerical_checks_passed=True,full_package_complete=False,inputs=inputs,outputs={p.as_posix():sha256_file(p) for p in paths},
        reproduction_cases=len(reproduction),independently_revalidated_main_layouts=len(audits),n_unit_household_pairs=len(generalization),
        config_hash=digest,code_hash=fingerprint,wall_time_this_invocation_s=elapsed))
    write_json(ROOT/'run.json',{**manifest,'status':'complete','wall_time_this_invocation_s':elapsed,'completed_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds')})
    print(json.dumps(dict(numerical_checks_passed=True,reproduction_cases=len(reproduction),independently_revalidated_main_layouts=len(audits),visual_review_pending=True)))


if __name__=='__main__':
    try:main()
    except Exception as error:
        write_json(ROOT/'status.json',dict(status='failed',exception_type=type(error).__name__))
        raise
