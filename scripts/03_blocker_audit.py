"""Audit the geometry types of source walls/separators used by G2 gap repair."""
from collections import Counter
from pathlib import Path
import json

import pandas as pd
from tqdm import tqdm
from shapely import from_wkt
from fea.io import prepare_cli,start_run,write_json
from fea.data.archives import read_geometry_pickle


def main():
    args=prepare_cli(__doc__).parse_args();config,digest,_=start_run(args,'03_blocker_audit')
    if args.dry_run:print('Would audit D1 blocker geometry types without exporting source identifiers or coordinates.');return
    path=Path(config['paths']['raw'])/'swiss_dwellings/extracted/geometries.csv'
    counts=Counter()
    columns=['unit_usage','apartment_id','entity_subtype','geometry']
    for frame in tqdm(pd.read_csv(path,usecols=columns,dtype={'apartment_id':'string'},chunksize=100000),desc='Blocker types'):
        rows=frame[(frame.unit_usage==config['corpus']['d1_unit_usage'])&frame.apartment_id.notna()&
            frame.entity_subtype.isin(['WALL','COLUMN','WINDOW','RAILING','SEPARATOR'])]
        kinds=rows.geometry.str.extract(r'^\s*([A-Z]+)',expand=False)
        for key,value in pd.DataFrame({'subtype':rows.entity_subtype,'geometry_type':kinds}).value_counts().items():counts[key]+=int(value)
    records=[dict(source='D1',subtype=k[0],geometry_type=k[1],n=v) for k,v in sorted(counts.items())]
    other=Counter()
    with (Path(config['paths']['raw'])/'resplan/extracted/ResPlan.pkl').open('rb') as stream:
        plans=read_geometry_pickle(stream)
    for plan in plans:
        for name in ('wall','window'):
            geometry=plan.get(name)
            if geometry is not None and not geometry.is_empty:other[name,geometry.geom_type.upper()]+=1
    records.extend(dict(source='D2',subtype=k[0],geometry_type=k[1],n=v) for k,v in sorted(other.items()))
    corpus=pd.read_parquet(Path(config['paths']['processed'])/'corpus_units.parquet')
    empty_service=0;kitchen_overlap=0;maximum_overlap=0.
    for row in corpus[corpus.include].itertuples():
        unit=json.loads(row.unit_json);meta=unit['meta']
        service=meta.get('service_room_geometry',meta.get('toilet_geometry'))
        if service is not None and from_wkt(service).is_empty:empty_service+=1
        if 'kitchen_region_geometry' in meta:
            region=from_wkt(meta['kitchen_region_geometry'])
            overlap=sum(region.intersection(from_wkt(unit['classes'].get(name,'GEOMETRYCOLLECTION EMPTY'))).area
                for name in ('furnishable','storage_only'))
            maximum_overlap=max(maximum_overlap,overlap)
            kitchen_overlap+=int(overlap>1e-7)
    semantic=dict(included_units=int(corpus.include.sum()),empty_service_room_geometry=empty_service,
        kitchen_furniture_overlap_units=kitchen_overlap,maximum_kitchen_overlap_m2=maximum_overlap)
    write_json('reports/g2_service_geometry_audit.json',dict(config_hash=digest,**semantic,
        **{'pass':empty_service==0 and kitchen_overlap==0}))
    assert empty_service==0 and kitchen_overlap==0, 'Service classification needs correction before release'
    unsupported=[r for r in records if r['geometry_type'] not in ('POLYGON','MULTIPOLYGON')]
    write_json('reports/g2_blocker_geometry_types.json',dict(config_hash=digest,records=records,
        polygon_source_blockers_only=not unsupported,unsupported=unsupported,
        scope='All identifiable D1 residential blocker records and all nonempty D2 wall/window layers. Synthetic line separators have a raster regression test.'))
    print(json.dumps({'polygon_source_blockers_only':not unsupported,'counts':records}))
    if unsupported:raise SystemExit('Nonpolygon source blockers require explicit loader preservation before release')


if __name__=='__main__':main()
