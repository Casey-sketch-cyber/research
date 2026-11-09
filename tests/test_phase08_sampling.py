import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from phase08_sampling import select_instances


def test_balanced_fixed_sample_ignores_row_order_and_excludes_invalid_units():
    frame=pd.DataFrame([dict(unit_key=f"{s}:{i:03}",source=s,nia_m2=8.+i,evaluable=True) for s in ["D1","D2","D3"] for i in range(24)])
    frame=pd.concat([frame,pd.DataFrame([dict(unit_key="excluded",source="D1",nia_m2=9.,evaluable=False)])],ignore_index=True)
    first,allocation,_=select_instances(frame,["H1","H2","H3","H4"],20261105)
    second,_,_=select_instances(frame.iloc[::-1],["H4","H3","H2","H1"],20261105)
    pd.testing.assert_frame_equal(first,second)
    assert len(first)==200 and not first.duplicated(["unit_key","household"]).any()
    assert "excluded" not in set(first.unit_key)
    assert len(allocation)==36 and set(allocation.selected_pairs)=={5,6}
    assert first.groupby(["source","nia_m2"]).area_tercile.nunique().max()==1
