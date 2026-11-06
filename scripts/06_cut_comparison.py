"""Controlled G2 M9 comparison on the same 20 pilot units, H1 under S2."""
from __future__ import annotations

import os
for variable in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable]='1'
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time

import pandas as pd
from tqdm import tqdm

from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli,start_run,write_json


def run_case(job):
    serialized,config,mode=job
    from fea.solve import cpsat
    unit=Unit.from_dict(serialized)
    household=parse_households(config['households'],config['furniture'])['H1_single_commuter']
    original_cut,original_hint,original_init,original_check=cpsat.Model.cut,cpsat.Model.warm_start,cpsat.Model.__init__,cpsat.validate_layout
    started=time.perf_counter();state={'built':False,'first_cp_valid':None}
    def initialize(self,*args,**kwargs):
        original_init(self,*args,**kwargs);state['built']=True
    def checked(*args,**kwargs):
        value=original_check(*args,**kwargs)
        if state['built'] and value['pass'] and value['fci']>0 and state['first_cp_valid'] is None:
            state['first_cp_valid']=time.perf_counter()-started
        return value
    def exact_cut(self,problems,solver):
        count=0
        for problem in problems:
            variables=[]
            owners=set(problem['blockers'])
            if problem['instance_id']:owners.add(problem['instance_id'])
            for identity in sorted(owners):
                item=self.instances[identity]
                variables.extend([item.present,item.x,item.y,item.orientation])
                active=item.states[problem['variant'],problem['slot']]
                if not isinstance(active,int):variables.append(active)
            if problem['demand_id']:
                variables.extend(y for key,y in self.assignment.items() if key[:3]==
                    (problem['variant'],problem['slot'],problem['demand_id']) and key[-1]==problem['instance_id'] and solver.Value(y))
            variables=list({v.Index():v for v in variables}.values())
            if variables:self.model.AddForbiddenAssignments(variables,[[solver.Value(v) for v in variables]]);count+=1
        return count
    def cold_hint(self,layout,enforce_bound=True):
        if enforce_bound:return original_hint(self,layout,enforce_bound)
        # Initial greedy hint remains; subsequent iteration-specific hints are omitted.
    cpsat.Model.__init__=initialize;cpsat.validate_layout=checked
    if mode=='exact_cut_cold_restart':cpsat.Model.cut=exact_cut;cpsat.Model.warm_start=cold_hint
    try:
        layout=cpsat.solve_layout(unit,household,'S2',config)
    finally:
        cpsat.Model.cut,cpsat.Model.warm_start,cpsat.Model.__init__,cpsat.validate_layout=original_cut,original_hint,original_init,original_check
    sol=layout['solver']
    return dict(unit_key=unit.unit_key,source=unit.source,nia_m2=unit.interior.area,mode=mode,
        fci=layout['validator']['fci'],validator_pass=layout['validator']['pass'],iterations=sol['reach_iterations'],
        time_s=sol['time_s'],first_positive_including_greedy_s=sol.get('first_valid_time_s'),
        first_cp_valid_s=state['first_cp_valid'],cuts=sol.get('geometric_cuts',0))


def main():
    parser=prepare_cli(__doc__);args=parser.parse_args();config,_,_=start_run(args,'06_cut_comparison')
    selection=json.loads(Path('results/pilot/benchmark_selection.json').read_text())
    config['solver'].update(num_workers=selection['workers'],time_limit_s=selection['time_limit_s'],reachability_round_s=5.)
    config['raster']['anchor_stride_m']=.2
    if args.dry_run:print('Would compare exact no-goods/cold restarts with guarded geometric cuts/refreshed hints on 20 H1 S2 cases.');return
    units=json.loads(Path('results/pilot/pilot_units.json').read_text())['units']
    output=Path('results/pilot/cut_comparison');output.mkdir(exist_ok=True)
    rows=[];timings={}
    for mode in ('exact_cut_cold_restart','geometric_cut_refreshed_hint'):
        started=time.perf_counter()
        with ProcessPoolExecutor(max_workers=max(1,14//selection['workers'])) as pool:
            futures=[pool.submit(run_case,(u,config,mode)) for u in units]
            for future in tqdm(as_completed(futures),total=len(futures),desc=mode):
                rows.append(future.result());pd.DataFrame(rows).to_csv(output/'cases_PARTIAL.csv',index=False)
        timings[mode]=time.perf_counter()-started
    frame=pd.DataFrame(rows);frame.to_csv(output/'cases.csv',index=False)
    aggregate=frame.groupby('mode').agg(n=('fci','size'),mean_fci=('fci','mean'),median_fci=('fci','median'),
        mean_iterations=('iterations','mean'),median_iterations=('iterations','median'),
        mean_first_cp_valid_s=('first_cp_valid_s','mean'),mean_first_positive_including_greedy_s=('first_positive_including_greedy_s','mean'),
        valid=('validator_pass','sum')).reset_index()
    aggregate['wall_time_s']=aggregate['mode'].map(timings);aggregate.to_csv(output/'summary.csv',index=False)
    write_json(output/'protocol.json',dict(cases_per_arm=20,household='H1_single_commuter',strategy='S2',
        shared_geometry='corrected G2 pilot',greedy='enabled in both arms',search_round_s=5.,
        num_workers=selection['workers'],time_limit_s=selection['time_limit_s'],
        comparison='exact frontier-owner pose no-goods and initial hint only versus guarded geometric frontier cuts and refreshed hints',
        limitation='This isolates cuts/restarts under the revised geometry and common round schedule; it is not a rerun of the geometrically biased old pilot.',
        code_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    print(aggregate.to_string(index=False))


if __name__=='__main__':main()
