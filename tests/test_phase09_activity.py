"""Hand-counted body areas and strict validation for the R metric."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path('scripts').resolve()))
from phase09_activity_validator import daytime_area,relative_gain
from test_metrics_validator import fixture


def test_static_area_uses_body_not_clearance_or_claimed_score():
    config,h,grid,layout=fixture();layout['fci']=1
    result=daytime_area(layout,grid,config,h,12.)
    assert result['furniture_body_day_m2']==pytest.approx(.9*2.)
    assert result['free_activity_area_day_m2']==pytest.approx(10.2)
    assert result['fci_validator']<1
    assert result['raster_furnishable_body_and_clearance_free_day_m2']<result['raster_furnishable_free_day_m2']


def test_stowed_body_and_invalid_layout_rejection():
    config,h,grid,layout=fixture();item=layout['items'][0]
    item.update(instance_id='wall_bed_single#1',type='wall_bed_single',x=1.6,y=0.)
    item['states']['normal']={s.name:'deployed' if s.name=='night' else 'stowed' for s in h.slots}
    layout['service']['normal']['night'][0]['by']=[item['instance_id']];layout['strategy']='S2'
    result=daytime_area(layout,grid,config,h,12.)
    assert result['furniture_body_day_m2']==pytest.approx(1.*.5)
    assert result['free_activity_area_day_m2']==pytest.approx(11.5)
    broken=deepcopy(layout);broken['items'][0]['x']=100
    with pytest.raises(ValueError):daytime_area(broken,grid,config,h,12.)


def test_relative_gains_are_signed_and_zero_denominator_is_undefined():
    assert relative_gain(5,8)==pytest.approx(.6)
    assert relative_gain(8,5)==pytest.approx(-.375)
    assert relative_gain(0,1) is None
