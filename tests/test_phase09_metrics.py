"""Hand-counted agreement, threshold ties and geometry identity guards."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path('scripts').resolve()))
from phase09_metrics import confusion_counts,threshold_sweep,prepare_cases


def test_confusion_orientation_and_no_missing_as_negative():
    result=confusion_counts(np.array([1,1,0,0],bool),np.array([1,0,1,0],bool))
    assert [result[k] for k in ['tp','tn','fp','fn']]==[1,1,1,1]
    assert result['misclassification_rate']==.5
    with pytest.raises(ValueError):confusion_counts(np.array([1,np.nan]),np.array([True,False]))


def test_threshold_ties_and_endpoints_against_explicit_predictions():
    x=np.array([3.,1.,1.,2.,5.]);y=np.array([True,False,True,False,True])
    rows=threshold_sweep(x,y)
    assert [r['threshold'] for r in rows]==[1.,2.,3.,5.,None]
    for row in rows:
        expected=confusion_counts(y,np.zeros(len(x),bool) if row['threshold'] is None else x>=row['threshold'])
        for key,value in expected.items():assert row[key]==value
    with pytest.raises(ValueError):threshold_sweep([1,np.nan],np.array([True,False]))


def test_geometry_join_rejects_missing_units_and_wrong_source():
    frame=pd.DataFrame([dict(unit_key='u',household='H',source='D1',nia_m2=12.,strategy=s,fci_validator=v) for s,v in [('S0',.4),('S1',.5),('S2',.6)]])
    corpus=pd.DataFrame([dict(unit_key='u',source='D1',nia_m2=12.,n_rooms=1)])
    config={'households':{'households':{'H':{'persons':2}}}}
    result=prepare_cases(frame,corpus,config)
    assert result.iloc[0].area_per_person==6 and result.iloc[0].rooms_per_person==.5
    for changed in [corpus.assign(unit_key='v'),corpus.assign(source='D3')]:
        with pytest.raises(ValueError):prepare_cases(frame,changed,config)
