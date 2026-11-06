"""Run the preregistered G2 comparison arms sequentially without oversubscription."""
from pathlib import Path
import json
import hashlib
import subprocess
import sys

from fea.io import prepare_cli, start_run, write_json


def run_arm(workers,stride,limit,config_path='config/project.yaml',force_new=False):
    base=f'w{workers}_s{round(stride*100):02d}_t{limit}'
    import importlib.util
    spec=importlib.util.spec_from_file_location('revision_driver','scripts/06_revision.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    method=module.signature()
    inputs=hashlib.sha256(Path('results/pilot/pilot_units.json').read_bytes()).hexdigest()
    # Preserve published and interrupted measurements. A clean clone must actually
    # solve cases, rather than treating a committed summary as a local checkpoint.
    number=0
    while True:
        arm=base if number==0 else base+'_r'+str(number)
        directory=Path('results/pilot/benchmarks')/arm
        output=directory/'summary.json'
        if output.exists():
            summary=json.loads(output.read_text())
            complete_cache=len(list((Path(summary['cache'])/'shared').glob('*.json')))==240
            if not force_new and summary['code_hash']==method and summary['input_hash']==inputs and summary['fresh_throughput_measurement'] and complete_cache:
                return summary
        elif not directory.exists():
            break
        number+=1
    write_json('results/pilot/revision_progress.json',{'stage':'benchmark','arm':arm})
    command=[sys.executable,'scripts/06_revision.py','--workers',str(workers),'--stride',str(stride),
        '--limit',str(limit),'--arm',arm,'--config',config_path]
    subprocess.run(command,check=True)
    return json.loads(output.read_text())


def main():
    parser=prepare_cli(__doc__);parser.add_argument("--rerun",action="store_true");args=parser.parse_args()
    config,_,_=start_run(args,'06_revision_pipeline')
    arms=[(8,.1,60),(8,.2,60),(1,.2,60),(2,.2,60),(4,.2,60)]
    if args.dry_run:
        print(json.dumps({'arms':arms,'then':'30 s at selected worker count; no Phase 7'}));return
    summaries=[run_arm(*arm,config_path=args.config,force_new=args.rerun) for arm in arms]
    reference=summaries[0]['fci_distribution']['0.5']
    coarse_reference=summaries[1]['fci_distribution']['0.5']
    threshold=max(reference,coarse_reference)-.01
    trials=summaries[2:]
    eligible=[s for s in trials if s['fci_distribution']['0.5']>=threshold-1e-9]
    pool=eligible or [s for s in trials if s['fci_distribution']['0.5']>=max(t['fci_distribution']['0.5'] for t in trials)-1e-9]
    chosen60=min(pool,key=lambda s:s['wall_time_s'])
    shorter=run_arm(chosen60['num_workers'],.2,30,config_path=args.config,force_new=args.rerun)
    chosen=shorter if shorter['fci_distribution']['0.5']>=max(threshold,chosen60['fci_distribution']['0.5']-.01)-1e-9 and shorter['wall_time_s']<chosen60['wall_time_s'] else chosen60
    choice=dict(selected_arm=chosen['arm'],workers=chosen['num_workers'],time_limit_s=chosen['time_limit_s'],
        anchor_stride_m=.2,reference_exhaustive_median=reference,reference_coarse_median=coarse_reference,
        quality_threshold=threshold,worker_quality_criterion_met=bool(eligible),
        selection_rule='fastest eligible 60 s worker arm; accept 30 s only within 0.01 median FCI and faster',
        completed_arms=[s['arm'] for s in summaries]+[shorter['arm']],code_hash=chosen['code_hash'])
    write_json('results/pilot/benchmark_selection.json',choice)
    write_json('results/pilot/revision_progress.json',{'stage':'benchmarks_complete','selected_arm':chosen['arm']})
    print(json.dumps(choice))


if __name__=='__main__':main()
