"""Compact B status from hash-matched case checkpoints, including pilot reuse."""
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import pandas as pd
from fea.io import prepare_cli,start_run,write_json


def main():
    args=prepare_cli(__doc__).parse_args();start_run(args,'08_status_expB')
    if args.dry_run:print('Would count unique completed B outputs and complete algorithm triplets from the active fingerprint.');return
    root=Path('results/expB');full=root/'run.json';path=full if full.exists() else root/'pilot'/'run.json'
    run=json.loads(path.read_text());sample=pd.read_csv(root/'instances.csv');allowed=set(zip(sample.unit_key,sample.household))
    records=[]
    for p in Path(run['cache']).glob('*_record.json'):
        row=json.loads(p.read_text())
        if row['code_hash']!=run['code_hash'] or (row['unit_key'],row['household']) not in allowed or row['algorithm'] not in run['algorithms']:raise ValueError('Unexpected B checkpoint')
        records.append(row)
    keys=[(r['unit_key'],r['household'],r['algorithm']) for r in records]
    if len(keys)!=len(set(keys)):raise ValueError('Duplicate B checkpoint')
    pairs=Counter((u,h) for u,h,a in keys)
    result=dict(observed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),stage=run['stage'],status=run['status'],
        expected_pairs=len(sample),expected_algorithm_outputs=len(sample)*3,completed_algorithm_outputs=len(records),completed_three_algorithm_pairs=sum(n==3 for n in pairs.values()),
        completed_by_algorithm=dict(Counter(r['algorithm'] for r in records)),invalid_outputs=sum(not r['validator_pass'] for r in records),
        basis='Unique completed checkpoints, including identical pilot results reused in full run; incomplete pairs remain partial.')
    continuation=root/'continuation.json'
    if continuation.exists() and json.loads(continuation.read_text()).get('status')=='failed':result['status']='failed'
    analysis=root/'analysis_status.json'
    if analysis.exists():result['analysis_status']=json.loads(analysis.read_text())['status']
    write_json(root/'status_snapshot.json',result);print(json.dumps(result))


if __name__=='__main__':main()
