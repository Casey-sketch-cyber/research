"""Resumable reproduction and saved-layout audit jobs for supporting analysis R."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from shapely.geometry import box,LineString,GeometryCollection
from fea.config import config_hash
from fea.data.d3_shells import load_d3
from fea.geometry.unit import Unit
from fea.geometry.raster import rasterize
from fea.households import parse_households
from fea.io import write_json,sha256_file
from phase09_activity_validator import daytime_area,relative_gain


def make_shells(config):
    """Configured fallback, plus the source's known envelope with our catalogue."""
    local=deepcopy(config);fallback=config['experiments']['R_single_room_test']['fallback_shells']
    local['shells_D3'].update(areas_m2=[fallback['area_m2']],aspect_ratios=fallback['aspect_ratios'],
        entrance_positions=['short_wall_corner'],window_positions=['opposite_short_wall'])
    shells=list(load_d3(local))
    if len(shells)!=3 or any(u.meta.get('generator_failure') for u in shells):raise ValueError('R fallback shell generation failed')
    for u in shells:u.meta['R1_condition']='configured_D3_fallback'
    opening=json.loads(Path('reports/schemas/D1_opening_dimensions.json').read_text())['openings']
    source=json.loads(Path('config/expR_source.json').read_text());facts={r['quantity']:r['value'] for r in source['source_values']}
    width,depth=facts['room_short_side'],facts['room_long_side'];room=box(0,0,width,depth);span=min(width,opening['ENTRANCE_DOOR']['median_width_m']);win=min(width,opening['WINDOW']['median_width_m'])
    entry=LineString([(0,0),(span,0)]);window=LineString([((width-win)/2,depth),((width+win)/2,depth)])
    shells.append(Unit('R1:paper_envelope','R1_envelope','R1:paper_envelope',
        {k:room if k=='furnishable' else GeometryCollection() for k in ['furnishable','walkable_only','storage_only','fixed_service','excluded']},
        room.boundary.difference(entry),[entry],[window],entry,float(facts['room_area']),1,
        dict(R1_condition='paper_envelope_catalogue_only',parameters=dict(gross_area_m2=facts['room_area'],aspect_ratio=depth/width,entrance_position='short_wall_corner',window_position='opposite_short_wall'),
            opening_dimension_source='D1 medians, not source paper',source_pdf_page=12,source_section='6.1',exact_reproduction=False)))
    return shells


def reproduction_job(job):
    """Two fresh strategies per shell/household; S2 may retain validated S0."""
    from fea.solve.cpsat import solve_layout
    serialized,name,base,settings,root,fingerprint=job;unit=Unit.from_dict(serialized);config=deepcopy(base)
    config['solver'].update({k:settings[k] for k in ['num_workers','time_limit_s']});config['raster']['anchor_stride_m']=settings['anchor_stride_m']
    household=parse_households(config['households'],config['furniture'])[name];digest=config_hash(config)
    grid=rasterize(unit,config['raster']['resolution_m'],config['furniture']['meta']['walking_width'],config['raster']['source_gap_close_m'])
    root=Path(root);stem=unit.unit_key.replace(':','_')+'_'+name.split('_')[0];rows=[];incumbent=None
    for strategy in ['S0','S2']:
        path=root/(stem+'_'+strategy+'.json');record=root/(stem+'_'+strategy+'_record.json')
        if path.exists() and record.exists():
            row=json.loads(record.read_text());layout=json.loads(path.read_text())
            if row['code_hash']!=fingerprint or row['config_hash']!=digest or row['layout_sha256']!=sha256_file(path):raise ValueError('R1 checkpoint differs')
            metric=daytime_area(layout,grid,config,household,unit.interior.area)
            if abs(metric['fci_validator']-row['fci_validator'])>1e-8 or abs(metric['free_activity_area_day_m2']-row['free_activity_area_day_m2'])>1e-8:raise ValueError('R1 independent resume audit differs')
        else:
            started=time.perf_counter();layout=solve_layout(unit,household,strategy,config,incumbent=incumbent)
            metric=daytime_area(layout,grid,config,household,unit.interior.area)
            layout['code_hash']=fingerprint;write_json(path,layout)
            row=dict(shell_id=unit.unit_key,condition=unit.meta['R1_condition'],aspect_ratio=unit.meta['parameters']['aspect_ratio'],household=name,strategy=strategy,
                nia_m2=unit.interior.area,**metric,elapsed_s=time.perf_counter()-started,solver_status=layout['solver']['status'],config_hash=digest,code_hash=fingerprint,
                layout_file=path.name,layout_sha256=sha256_file(path),exact_source_reproduction=False)
            write_json(record,row)
        incumbent=layout;rows.append(row)
    if rows[1]['fci_validator']+1e-8<rows[0]['fci_validator']:raise ValueError('R1 strategy order failed')
    source=json.loads(Path('config/expR_source.json').read_text());facts={r['quantity']:r['value'] for r in source['source_values']}
    for row in rows:
        row.update(gain_m2=row['free_activity_area_day_m2']-rows[0]['free_activity_area_day_m2'],
            gain_rel=relative_gain(rows[0]['free_activity_area_day_m2'],row['free_activity_area_day_m2']),
            reported_value_m2=facts['activity_area_static_low'] if row['strategy']=='S0' else facts['activity_area_flexible'],
            reported_static_upper_m2=facts['activity_area_static_high'],reported_gain_rel=facts['reported_relative_gain'],
            source_metric_comparable=False)
    return rows


def generalization_job(job):
    """Revalidate four immutable H1/H2 layouts per unit, retaining original provenance."""
    serialized,records,base,production,original_cache,root,fingerprint=job
    unit=Unit.from_dict(json.loads(serialized));root=Path(root);checkpoint=root/(unit.unit_key.replace(':','_')+'.json')
    if checkpoint.exists():
        value=json.loads(checkpoint.read_text())
        if value['code_hash']!=fingerprint:raise ValueError('R2 checkpoint code differs')
        for name,digest in value['layout_hashes'].items():
            if sha256_file(Path(original_cache)/name)!=digest:raise ValueError('R2 source layout changed')
        return value['rows']
    grid=rasterize(unit,base['raster']['resolution_m'],base['furniture']['meta']['walking_width'],base['raster']['source_gap_close_m']);rows=[];hashes={}
    for record in records:
        settings=production[record['budget_group']];config=deepcopy(base)
        config['solver'].update({k:settings[k] for k in ['num_workers','time_limit_s']});config['raster']['anchor_stride_m']=settings['anchor_stride_m']
        h=parse_households(config['households'],config['furniture'])[record['household']]
        relative=(Path(record['budget_group'])/'shared'/record['layout_file']).as_posix();path=Path(original_cache)/relative;layout=json.loads(path.read_text())
        if record['config_hash']!=config_hash(config) or layout['config_hash']!=record['config_hash'] or layout['code_hash']!=record['code_hash']:raise ValueError('R2 saved configuration/source signature differs')
        if any(layout[k]!=record[k] for k in ['unit_key','household','strategy']):raise ValueError('R2 saved identity differs')
        metric=daytime_area(layout,grid,config,h,unit.interior.area)
        if abs(metric['fci_validator']-record['fci_validator'])>1e-8:raise ValueError('R2 independent FCI differs')
        hashes[relative]=sha256_file(path)
        rows.append(dict(unit_key=unit.unit_key,source=unit.source,household=h.name,strategy=record['strategy'],nia_m2=unit.interior.area,
            **metric,layout_sha256=hashes[relative],source_config_hash=record['config_hash'],source_code_hash=record['code_hash'],analysis_code_hash=fingerprint))
    if len(rows)!=4:raise ValueError('R2 requires both strategies and both single-person households')
    write_json(checkpoint,dict(code_hash=fingerprint,layout_hashes=hashes,rows=rows))
    return rows
