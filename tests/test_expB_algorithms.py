"""Fast annealing states are checked against the separate full validator."""
from copy import deepcopy
from pathlib import Path
import sys
import numpy as np
import pytest
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from phase08_algorithms import Evaluator,anneal
from fea.furniture.library import library
from fea.furniture.candidates import generate_candidates
from fea.households import parse_households
from fea.validate import validate_layout
from test_metrics_validator import fixture


def prepared(name):
    config,_,grid,_=fixture();config=deepcopy(config)
    household=parse_households(config['households'],config['furniture'])[name]
    items=library(config['furniture']);candidates=generate_candidates(grid,items,anchor_stride_m=.2)
    empty=dict(strategy='S2',resolution_m=grid.resolution,items=[],service={})
    settings=yaml.safe_load(Path('config/expB_algorithms.yaml').read_text())['annealing']
    return config,household,grid,items,candidates,empty,settings


@pytest.mark.parametrize('name',['H1_single_commuter','H2_single_remote_worker','H3_couple_one_remote','H4_parent_child'])
def test_fast_geometry_and_service_match_validator(name):
    config,h,grid,items,candidates,empty,settings=prepared(name)
    e=Evaluator(grid,items,candidates,h,config,empty,settings);rng=np.random.default_rng(91)
    valid=invalid=0
    for count in range(30):
        genome=e.encode(empty)
        n=min(count%7,len(e.names))
        for i in rng.choice(len(e.names),n,replace=False):
            genome[i,0]=rng.integers(len(candidates[e.names[i]]))
            genome[i,1:]=rng.integers(len(items[e.names[i]].states),size=len(e.slots))
        result=e.evaluate(genome,materialize=True);checked=validate_layout(result['layout'],grid,config,h)
        assert checked['pass']==(result['violations']==0)
        if checked['pass']:
            valid+=1;assert checked['fci']==pytest.approx(result['fci']);assert checked['tb']==pytest.approx(result['tb'])
        else:invalid+=1;assert checked['fci']==0
    assert valid and invalid


def test_annealing_fixed_proposals_and_deterministic_output():
    config,h,grid,items,candidates,empty,settings=prepared('H3_couple_one_remote')
    settings={**settings,'iterations':100,'restarts':2}
    first=anneal(empty,grid,items,candidates,h,config,settings,73,initial=empty)
    second=anneal(empty,grid,items,candidates,h,config,settings,73,initial=empty)
    assert first['items']==second['items'] and first['service']==second['service']
    assert first['annealing']['total_proposals']==200
    assert first['validator']['pass'] and not first['annealing']['early_stop']
