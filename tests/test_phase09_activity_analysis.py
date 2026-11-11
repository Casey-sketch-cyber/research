"""Guard the R bridge against treating support bounds as exact area savings."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path('scripts').resolve()))
from phase09_activity_analysis import bridge_to_p1,assemble_generalization


def test_bridge_keeps_bounds_undefined_and_checks_paired_scores():
    general=pd.DataFrame([dict(unit_key=u,household='H1',source=s,nia_m2=20.,fci_validator_S0=.5,fci_validator_S2=.7,gain_rel=.2) for u,s in [('a','D1'),('b','D3')]])
    records=[]
    for u,s,identified in [('a','D1',False),('b','D3',True)]:
        for pooling in (['real_plans','pooled'] if s=='D1' else ['D3','pooled']):
            records.append(dict(unit_key=u,household='H1',source=s,method='median_bin_cummax',pooling=pooling,reference_pooling=pooling,S0=.5,S2=.7,
                delta_ea_m2=2. if identified else np.nan,delta_ea_lower_bound_m2=2.,delta_gain_identified=identified,
                delta_gain_lower_bound_only=not identified,delta_lower_support_limited=not identified,delta_right_censored=False))
    area=pd.DataFrame(records);result=bridge_to_p1(general,area)
    assert len(result)==4
    assert result.loc[result.unit_key=='a','saving_rel_fea'].isna().all()
    assert result.loc[result.unit_key=='a','saving_rel_fea_lower_bound'].eq(.1).all()
    assert result.loc[result.unit_key=='b','saving_rel_fea'].eq(.1).all()
    with pytest.raises(ValueError):bridge_to_p1(general,area.assign(S2=.8))


def test_generalization_keeps_negative_gain_and_layout_pairing():
    rows=[]
    for strategy,free in [('S0',8.),('S2',6.)]:
        rows.append(dict(unit_key='a',household='H1',source='D1',nia_m2=12.,strategy=strategy,fci_validator=.5,
            free_activity_area_day_m2=free,raster_furnishable_free_day_m2=free,layout_sha256=strategy))
    geometry=pd.DataFrame([dict(unit_key='a',aspect_ratio=1.5,compactness=.7)])
    result=assemble_generalization(pd.DataFrame(rows),geometry)
    assert result.iloc[0].gain_m2==-2. and result.iloc[0].gain_rel==-.25
    with pytest.raises(ValueError):assemble_generalization(pd.DataFrame(rows[:1]),geometry)
