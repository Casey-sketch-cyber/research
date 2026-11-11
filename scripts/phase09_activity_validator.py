"""Independent daytime area accounting; deliberately no solver/candidate imports."""
from __future__ import annotations
import math
import numpy as np
from fea.geometry.raster import FURNISHABLE,STORAGE_ONLY
from fea.validate import validate_layout,_rectangles,_mask


def daytime_area(layout,grid,config,household,nia_m2):
    """Validate first, then reconstruct body union for the normal daytime slot.

    Primary quantity is body-free NIA, not clearance-free or accessible activity area.
    Fixed-service space remains in NIA; the furnishable-only secondary measure does not.
    """
    checked=validate_layout(layout,grid,config,household)
    if not checked['pass']:raise ValueError('Invalid layout cannot produce an activity-area estimate')
    if not math.isfinite(nia_m2) or nia_m2<=0:raise ValueError('Positive finite NIA required')
    raw=dict(config['furniture']['static_items'])
    if layout['strategy'] in ['S1','S2']:raw.update(config['furniture']['transformable_items'])
    scale=household.overrides.get('global_clearance_scale',config['furniture']['meta']['global_clearance_scale'])
    bodies=np.zeros(grid.labels.shape,bool);reserved=np.zeros_like(bodies)
    for item in layout['items']:
        spec=raw[item['type']];state=item['states']['normal']['day']
        anchor=tuple(round((float(item[k])-grid.origin[i])/grid.resolution) for i,k in enumerate(['x','y']))
        body_rect,clear_rects,_=_rectangles(spec,state,grid.resolution,item['orientation_deg'],scale)
        body,inside=_mask(grid.labels.shape,anchor,body_rect)
        if not inside:raise ValueError('Active body outside independently validated grid')
        bodies|=body;reserved|=body
        for rect in clear_rects:
            clear,inside=_mask(grid.labels.shape,anchor,rect)
            if not inside:raise ValueError('Active clearance outside independently validated grid')
            reserved|=clear
    body_area=float(bodies.sum()*grid.resolution**2)
    if body_area>nia_m2+1e-7:raise ValueError('Raster furniture area exceeds continuous NIA')
    free=grid.labels==FURNISHABLE
    return dict(validator_pass=True,fci_validator=checked['fci'],tb=checked['tb'],
        furniture_body_day_m2=body_area,free_activity_area_day_m2=float(nia_m2-body_area),
        raster_furnishable_free_day_m2=float((free & ~bodies).sum()*grid.resolution**2),
        raster_furnishable_body_and_clearance_free_day_m2=float((free & ~reserved).sum()*grid.resolution**2),
        counted_nia_includes_fixed_service=True,metric='body_free_NIA_normal_day')


def relative_gain(before,after):
    """Keep signed gains; undefined relative gain when the original area is zero."""
    if not math.isfinite(before) or not math.isfinite(after):raise ValueError('Finite areas required')
    return (after-before)/before if before>1e-9 else None
