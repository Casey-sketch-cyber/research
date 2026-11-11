"""Run Exp. D after accepted full B; no new solves or chosen diagnostic cutoffs."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
from datetime import datetime,timezone
import json
from pathlib import Path
import time
import pandas as pd
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase07_corrected import load_corrected
from phase09_metrics import prepare_cases,analyze

ROOT=Path('results/expD')


def verify_b():
    """Require the frozen B execution plus full saved-layout audit, not just a pilot."""
    path=Path('results/expB/report_acceptance.json')
    if not path.exists():return False
    gate=json.loads(path.read_text())
    if not gate.get('passed') or not gate.get('full_B_analysis_complete') or gate['independently_revalidated']!=600:raise ValueError('Full B audit failed')
    for path,digest in gate['outputs'].items():
        if sha256_file(Path(path))!=digest:raise ValueError('B accepted output changed')
    for name,key in [('cases.csv','cases_sha256'),('run.json','run_sha256')]:
        if sha256_file(Path('results/expB')/name)!=gate[key]:raise ValueError('B run/case evidence changed')
    if sha256_file(Path('scripts/08_report_expB.py'))!=gate['implementation_sha256']:raise ValueError('B audit code changed')
    return True


def main():
    parser=prepare_cli(__doc__);parser.add_argument('--wait',action='store_true');args=parser.parse_args();config,digest,started=start_run(args,'09_run_expD')
    if args.dry_run:print('Would verify B, use all corrected F1 cases, and report fixed thresholds plus unselected continuous sweeps.');return
    while not verify_b():
        for name in ['analysis_status','continuation']:
            path=Path('results/expB')/(name+'.json')
            if path.exists() and json.loads(path.read_text()).get('status')=='failed':raise ValueError('B failed; D remains unstarted')
        if not args.wait:raise ValueError('Full B audit not complete')
        write_json(ROOT/'status.json',dict(status='waiting_for_B_acceptance'));time.sleep(20)
    started=time.perf_counter();write_json(ROOT/'status.json',dict(status='running'))
    frame,f1gate=load_corrected(config);corpus=pd.read_csv('results/corpus/corpus_units.csv',low_memory=False)
    inputs={p:sha256_file(Path(p)) for p in ['results/expB/report_acceptance.json','results/expA_f1/acceptance.json','results/expA_f1/solutions.csv','results/corpus/corpus_units.csv',
        'scripts/phase09_metrics.py','scripts/09_run_expD.py','scripts/phase07_corrected.py','tests/test_phase09_metrics.py']}
    cases=prepare_cases(frame,corpus,config);outputs=analyze(cases,config);outputs['indicators']=cases
    if cases.unit_key.nunique()!=2619 or len(cases)!=2619*4:raise ValueError('D differs from accepted sample')
    for name in ['confusion','threshold_sweeps']:
        rows=outputs[name]
        if not rows[['tp','tn','fp','fn']].sum(axis=1).eq(rows.n).all():raise ValueError('D confusion count mismatch')
    ROOT.mkdir(parents=True,exist_ok=True)
    for name,value in outputs.items():
        value['config_hash']=digest;value.to_csv(ROOT/(name+'.csv'),index=False)
    realcorr=outputs['correlations'].query("population == 'real_plans' and indicator == 'nia_m2'")[['household','strategy','n_valid','spearman']]
    realconf=outputs['confusion'][(outputs['confusion'].population=='real_plans') & (outputs['confusion'].tau==config['experiments']['adequacy_tau'])]
    fields=['household','strategy','indicator','threshold_m2','n','tp','tn','fp','fn','misclassification_rate']
    elapsed=time.perf_counter()-started
    report=Path('reports/phase_09_D_results.md')
    lines=['# Phase 9 — Conventional-indicator comparison results','','## Completed analyses','',
        f"All {cases.unit_key.nunique()} evaluable units and {len(cases)} unit-household pairs are retained from corrected F1. S0 and S2 use independent-validator FCI, with valid zero scores retained. No new solves were performed. Numerical analysis took {elapsed:.3f} seconds after B acceptance.",'',
        '- PASS: full B saved-layout audit and its hashes verified before analysis.',
        '- PASS: corrected F1 acceptance, configuration, sample membership and geometry metadata verified.',
        '- PASS: continuous associations, 2 m²-bin IQR, configured fixed-threshold confusion matrices and complete unselected threshold sweeps exported.',
        '- PASS: every confusion row sums to its available sample; missing continuous values are counted explicitly.','',
        '## Real-plan NIA correlations','',realcorr.to_markdown(index=False,floatfmt='.6f'),'','## Real-plan fixed-threshold confusion','',
        f"Truth-positive means model FCI ≥ {config['experiments']['adequacy_tau']}; predicted-positive means NIA at or above the configured area rule. TP/TN/FP/FN use this orientation. These are model-agreement comparisons, not legal compliance findings.",'',
        realconf[fields].to_markdown(index=False,floatfmt='.6f'),'','## Scope, missing cutoffs and limitations','',
        'Pooled, D1+D2 real-plan, D1, D2 and D3 tables remain separate. Pooled observations combine actual homes and generated shells and are not population weights. Spearman is undefined for constant inputs or fewer than three observations; no zero correlation is fabricated. IQR uses linear empirical quartiles, with singleton bins flagged.','',
        'The plan supplies 30/45/60 m² household-size thresholds and an 8 m² total-area comparison, but does not supply adequacy cutoffs for area/person or rooms/person. The latter are reported continuously and as all distinct observed-threshold confusion sweeps at the primary FCI threshold, plus the all-negative endpoint. No optimal cutoff is selected, and no unsourced housing rule is invented. The two specified rules are also evaluated at the configured FCI threshold sensitivities.','',
        'The corpus starts at approximately 8 m², so the 8 m² rule has essentially no negative-prediction support in this selected corpus; its limitations are visible in the confusion matrices. Rooms mean harmonized furnishable/habitable spaces, not bedrooms or a jurisdiction-specific census definition. Within a household, NIA and NIA/person have identical rank ordering by construction. These comparisons do not establish causal superiority or independent real-world validation of the FCI model.','',
        'No project/furniture/household defaults changed. Q31 records the threshold gap. Next: R and the prespecified ablations, then C, reduced K, HK and remaining literature screening before G3.','',
        'Reproduce: PYTHONPATH=src:scripts python scripts/09_run_expD.py','']
    report.write_text('\n'.join(lines),encoding='utf-8')
    paths=[ROOT/(name+'.csv') for name in outputs]+[report]
    for path,expected in inputs.items():
        if sha256_file(Path(path))!=expected:raise ValueError('D input changed during analysis')
    write_json(ROOT/'acceptance.json',dict(passed=True,n_units=cases.unit_key.nunique(),n_pairs=len(cases),config_hash=digest,
        input_sha256=inputs,outputs={p.as_posix():sha256_file(p) for p in paths},analysis_time_s=elapsed,
        independent_geometry_metadata_checked=True,chosen_cutoff=False,completed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
    write_json(ROOT/'status.json',dict(status='complete',n_units=cases.unit_key.nunique(),n_pairs=len(cases)))
    print(json.dumps(dict(passed=True,n_units=cases.unit_key.nunique(),n_pairs=len(cases),output_rows={k:len(v) for k,v in outputs.items()})))


if __name__=='__main__':
    try:main()
    except Exception as error:
        write_json(ROOT/'status.json',dict(status='failed',exception_type=type(error).__name__))
        raise
