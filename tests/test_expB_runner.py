"""B pilot selection and completed algorithm budgets are explicit."""
import importlib.util
from pathlib import Path
import pandas as pd
import pytest
spec=importlib.util.spec_from_file_location('b_runner',Path(__file__).parents[1]/'scripts/08_run_expB.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def test_pilot_is_outcome_free_and_row_order_invariant():
    sample=pd.read_csv('results/expB/instances.csv')
    a=r.select_pilot(sample);b=r.select_pilot(sample.sample(frac=1,random_state=5))
    pd.testing.assert_frame_equal(a,b)
    assert len(a)==12 and not a.duplicated(['source','household']).any()
    assert set(zip(a.unit_key,a.household))<=set(zip(sample.unit_key,sample.household))


def test_case_gate_keeps_invalid_outputs_and_requires_all_iterations():
    sample=pd.DataFrame([dict(unit_key='u',household='h')])
    rows=[dict(unit_key='u',household='h',algorithm=a,validator_pass=a!='greedy_footprint',fci_validator=0.,annealing_proposals=60000 if a=='simulated_annealing' else 0) for a in r.ALGORITHMS]
    frame=pd.DataFrame(rows)
    assert r.check_results(frame,sample)['invalid_outputs']==1
    frame.loc[frame.algorithm=='simulated_annealing','annealing_proposals']=59000
    with pytest.raises(ValueError,match='budget incomplete'):r.check_results(frame,sample)
    with pytest.raises(ValueError,match='missing or duplicated'):r.check_results(frame.iloc[:-1],sample)
