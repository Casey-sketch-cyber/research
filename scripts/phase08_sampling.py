"""Outcome-independent balanced source/area/household benchmark sampling."""
import numpy as np
import pandas as pd


def select_instances(evaluability,households,seed,total=200):
    """Keep area ties together and allocate a fixed-seed five/six pairs per stratum."""
    units=evaluability[evaluability.evaluable].sort_values("unit_key")[["unit_key","source","nia_m2"]].copy()
    if units.unit_key.duplicated().any():raise ValueError("Duplicate evaluable units")
    units["area_tercile"]=0;bounds=[]
    for source,frame in units.groupby("source",sort=True):
        values=frame.nia_m2.round(8).to_numpy()
        limits=np.quantile(values,[1/3,2/3])
        units.loc[frame.index,"area_tercile"]=np.searchsorted(limits,values,side="left")+1
        bounds.append(dict(source=source,lower_tercile_max_m2=float(limits[0]),middle_tercile_max_m2=float(limits[1])))
    pairs=units.merge(pd.DataFrame({"household":sorted(households)}),how="cross")
    keys=["source","area_tercile","household"]
    strata=list(pairs.groupby(keys,sort=True))
    if len(strata)!=len(units.source.unique())*3*len(households):raise ValueError("Missing required benchmark strata")
    rng=np.random.default_rng(seed);base,extra=divmod(total,len(strata))
    if base<1:raise ValueError("Too few cases to represent all strata")
    extras=set(rng.permutation(len(strata))[:extra]);selected=[];allocation=[]
    for i,(key,frame) in enumerate(strata):
        n=base+int(i in extras);frame=frame.sort_values(["unit_key","household"])
        if len(frame)<n:raise ValueError("Stratum cannot meet its frozen quota")
        chosen=frame.iloc[rng.choice(len(frame),n,replace=False)]
        selected.append(chosen);allocation.append(dict(zip(keys,key),eligible_pairs=len(frame),selected_pairs=n))
    result=pd.concat(selected).sort_values(["unit_key","household"]).reset_index(drop=True)
    result["strategy"]="S2"
    if len(result)!=total or result.duplicated(["unit_key","household"]).any():raise ValueError("Benchmark sample mismatch")
    return result,pd.DataFrame(allocation),pd.DataFrame(bounds)
