"""Algorithm summaries retain invalid cases and cluster-paired contrasts."""
import importlib.util
from pathlib import Path
import pandas as pd
import pytest
spec=importlib.util.spec_from_file_location('b_report',Path(__file__).parents[1]/'scripts/08_report_expB.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def table():
    rows=[]
    for source,unit,household in [('D1','u1','h1'),('D1','u1','h2'),('D1','u2','h1'),('D2','u3','h1')]:
        for algorithm,score in [('cp_sat',.8),('simulated_annealing',.6),('greedy_footprint',.4)]:
            rows.append(dict(source=source,unit_key=unit,household=household,algorithm=algorithm,fci_validator=score,validator_pass=True,budget_group='small',preparation_time_s=1.,algorithm_time_s=2.,elapsed_time_s=3.))
    return pd.DataFrame(rows)


def test_cluster_paired_constant_contrast():
    effects=r.paired_statistics(table(),1000,.95,17)
    cp=effects[effects.comparison=='cp_sat minus simulated_annealing'].iloc[0]
    assert cp.n_pairs==4
    assert cp.mean_difference==pytest.approx(.2)
    assert cp.ci_lo==pytest.approx(.2) and cp.ci_hi==pytest.approx(.2)
    assert cp.share_better==1 and cp.share_worse==0


def test_invalid_scores_remain_in_summary():
    frame=table();frame.loc[0,['fci_validator','validator_pass']]=[0.,False]
    result=r.summarize(frame);cp=result[(result.scope=='overall')&(result.algorithm=='cp_sat')].iloc[0]
    assert cp.n_cases==4 and cp.invalid_outputs==1
    assert cp.validity_rate==pytest.approx(.75)
    assert cp.mean_fci==pytest.approx(.6)
