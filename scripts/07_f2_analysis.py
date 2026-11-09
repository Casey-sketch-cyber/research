"""F2 paired equivalent-area gains after accepted F1; original evidence stays intact."""
import os
for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[name]="1"
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from tqdm import tqdm
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase07_corrected import load_corrected
from phase07_paired_area import fit_reference,paired_gain,gain_summary
from phase07_statistics import adequate_crossing,interval

METHODS=["median_bin_cummax","mean_isotonic"]
OUTPUTS=["f0_curves","paired_equivalent_area","area_gain_summary","primary_effects","min_adequate_area","supplementary_tests"]
GAIN_STATS=["share_fully_functional_S0","share_fci_improved","share_known_positive_area_gain","share_delta_right_censored","median_delta_ea_positive_uncensored_m2"]
COMPARISONS=[(2,0),(2,1),(1,0)]


def subset_result(result, mask):
    return {key:values[mask] for key,values in result.items()}


def effect_summary(capacity, high, low):
    difference=capacity[:,high]-capacity[:,low]
    return np.array([difference.mean(),np.mean(difference>1e-9)])


def ci_fields(values, confidence, n, prefix):
    ci=interval(values,confidence) if n>=2 else (None,None,0,"insufficient_units")
    return {prefix+"_ci_lo":ci[0],prefix+"_ci_hi":ci[1],prefix+"_successful_bootstraps":ci[2],prefix+"_ci_status":ci[3]}


def group_job(job):
    """Refit both references in the same paired unit resamples for one population."""
    pooling,household,frame,options,taus,seed,destination=job;destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    if (destination/"done.json").exists():
        done=json.loads((destination/"done.json").read_text())
        if all(sha256_file(destination/name)==digest for name,digest in done["outputs"].items()):return str(destination)
        raise ValueError("F2 checkpoint changed")
    frame=frame.sort_values("unit_key").reset_index(drop=True);area=frame.nia_m2.to_numpy(float);capacity=frame[["S0","S1","S2"]].to_numpy(float)
    n=len(frame);count=options["n"];bins=np.floor((area+1e-8)/2)*2;strata=[None]+list(np.unique(bins))
    references={method:fit_reference(area,capacity[:,0],method) for method in METHODS}
    point={method:paired_gain(curve,capacity[:,0],capacity[:,2]) for method,curve in references.items()}
    gain_draws={(method,lo):np.full((count,len(GAIN_STATS)),np.nan) for method in METHODS for lo in strata}
    effect_draws={(lo,high,low):np.full((count,2),np.nan) for lo in strata for high,low in COMPARISONS}
    amin_draws={(s,tau):np.full(count,np.nan) for s in range(3) for tau in taus};fit_statuses={key:Counter() for key in amin_draws}
    fits={(s,tau):adequate_crossing(area,capacity[:,s]>=tau-1e-9) for s,tau in amin_draws}
    rng=np.random.default_rng(seed)
    for draw in range(count):
        indices=rng.integers(0,n,size=n);bx,by,bb=area[indices],capacity[indices],bins[indices]
        for method in METHODS:
            result=paired_gain(fit_reference(bx,by[:,0],method),by[:,0],by[:,2])
            for lo in strata:
                mask=np.ones(n,bool) if lo is None else bb==lo
                if mask.any():
                    summary=gain_summary(subset_result(result,mask))
                    gain_draws[method,lo][draw]=[summary[key] if summary[key] is not None else np.nan for key in GAIN_STATS]
        for lo in strata:
            mask=np.ones(n,bool) if lo is None else bb==lo
            if mask.any():
                for high,low in COMPARISONS:effect_draws[lo,high,low][draw]=effect_summary(by[mask],high,low)
        for s,tau in amin_draws:
            fit=adequate_crossing(bx,by[:,s]>=tau-1e-9);fit_statuses[s,tau][fit["status"]]+=1
            if fit["a_min_m2"] is not None:amin_draws[s,tau][draw]=fit["a_min_m2"]
        if (draw+1)%100==0:write_json(destination/"progress.json",dict(bootstrap_completed=draw+1,bootstrap_expected=count))
    curves=[];cases=[];summaries=[];effects=[];minimum=[];tests=[]
    for method,curve in references.items():
        curves.append(pd.DataFrame(dict(pooling=pooling,household=household,method=method,area_m2=curve["area"],fitted_fci_S0=curve["capacity"])))
        result=point[method];case=frame[["unit_key","source","nia_m2","S0","S1","S2"]].copy()
        case["pooling"],case["household"],case["method"]=pooling,household,method
        for key,value in result.items():case[key]=value
        cases.append(case)
        for lo in strata:
            mask=np.ones(n,bool) if lo is None else bins==lo;row=dict(pooling=pooling,household=household,method=method,
                stratum="overall" if lo is None else "area_bin",area_bin_lo=lo,area_bin_hi=None if lo is None else lo+2,
                bootstrap_resamples=count,**gain_summary(subset_result(result,mask)))
            for i,key in enumerate(GAIN_STATS):row.update(ci_fields(gain_draws[method,lo][:,i],options["ci"],int(mask.sum()),key))
            summaries.append(row)
    for lo in strata:
        mask=np.ones(n,bool) if lo is None else bins==lo
        for high,low in COMPARISONS:
            point_effect=effect_summary(capacity[mask],high,low);row=dict(pooling=pooling,household=household,comparison=f"S{high}-S{low}",
                stratum="overall" if lo is None else "area_bin",area_bin_lo=lo,area_bin_hi=None if lo is None else lo+2,
                n_units=int(mask.sum()),mean_difference=float(point_effect[0]),share_improved=float(point_effect[1]),bootstrap_resamples=count)
            for i,key in enumerate(["mean_difference","share_improved"]):row.update(ci_fields(effect_draws[lo,high,low][:,i],options["ci"],int(mask.sum()),key))
            effects.append(row)
    for (s,tau),fit in fits.items():
        row=dict(pooling=pooling,household=household,strategy="S"+str(s),tau=tau,n_units=n,adequate_units=int((capacity[:,s]>=tau-1e-9).sum()),
            min_observed_nia_m2=float(area.min()),max_observed_nia_m2=float(area.max()),**fit)
        row.update(ci_fields(amin_draws[s,tau],options["ci"],n,"a_min_m2"))
        baseline=fits[0,tau]["a_min_m2"];row["delta_vs_S0_m2"]=baseline-fit["a_min_m2"] if baseline is not None and fit["a_min_m2"] is not None else None
        row.update(ci_fields(amin_draws[0,tau]-amin_draws[s,tau],options["ci"],n,"delta_vs_S0_m2"))
        for key in ["a_min_m2","delta_vs_S0_m2"]:
            if row[key] is None:
                row[key+"_ci_lo"]=row[key+"_ci_hi"]=None;row[key+"_ci_status"]="point_crossing_not_identified"
        row["bootstrap_fit_statuses"]=json.dumps(dict(fit_statuses[s,tau]),sort_keys=True);minimum.append(row)
    for high,low in COMPARISONS:
        difference=capacity[:,high]-capacity[:,low];difference[np.abs(difference)<1e-9]=0.;nonzero=difference[difference!=0]
        statistic,pvalue=stats.wilcoxon(difference,zero_method="wilcox",method="approx") if len(nonzero) else (0.,1.)
        ranks=stats.rankdata(np.abs(nonzero));rank=float((ranks*np.sign(nonzero)).sum()/ranks.sum()) if len(ranks) else 0.
        tests.append(dict(pooling=pooling,household=household,comparison=f"S{high}-S{low}",n_units=n,n_nonzero=len(nonzero),statistic=float(statistic),p_value=float(pvalue),rank_biserial=rank,
            interpretation="Supplement only: nonnegative ordering holds by construction; p-values and sign-based effects are not independent evidence of benefit."))
    tables=[pd.concat(curves),pd.concat(cases),pd.DataFrame(summaries),pd.DataFrame(effects),pd.DataFrame(minimum),pd.DataFrame(tests)]
    for name,table in zip(OUTPUTS,tables):table.to_csv(destination/(name+".csv"),index=False)
    write_json(destination/"done.json",dict(pooling=pooling,household=household,n_units=n,bootstrap_resamples=count,seed=seed,
        outputs={name+".csv":sha256_file(destination/(name+".csv")) for name in OUTPUTS}))
    return str(destination)


def decomposition_module():
    spec=importlib.util.spec_from_file_location("F2_decomposition","scripts/07_decomposition.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def render_gain(frame,output):
    """Conditional positive-gain medians; censoring and prevalence remain in tables."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    frame=frame[(frame.method==METHODS[0])&(frame.stratum=="area_bin")];households=sorted(frame.household.unique())
    panels=[("pooled","Pooled"),("real_plans","Real plans: D1+D2"),("D3","Designed shells: D3")]
    fig,axes=plt.subplots(len(households),3,figsize=(16,3.3*len(households)),squeeze=False,sharex=True,sharey=True)
    value="median_delta_ea_positive_uncensored_m2"
    for row,household in enumerate(households):
        for column,(pooling,title) in enumerate(panels):
            ax=axes[row,column];data=frame[(frame.household==household)&(frame.pooling==pooling)].sort_values("area_bin_lo");x=data.area_bin_lo.to_numpy()+1
            ax.plot(x,data[value],"o-",color="#286c91",ms=3,lw=1)
            ax.fill_between(x,data[value+"_ci_lo"].to_numpy(float),data[value+"_ci_hi"].to_numpy(float),color="#286c91",alpha=.18)
            ax.set(title=title+"\n"+household.replace("_"," "),xlabel="Net internal area (m²)",ylabel="Median positive ΔEA (m²)");ax.title.set_fontsize(9);ax.grid(alpha=.15)
    fig.suptitle("Paired equivalent-area gain: positive, uncensored units only; 95% unit-bootstrap intervals")
    fig.tight_layout(rect=(0,0,1,.97));output.parent.mkdir(parents=True,exist_ok=True)
    for extension in ["png","pdf"]:fig.savefig(output.with_suffix("."+extension),dpi=300,bbox_inches="tight")
    plt.close(fig)


def validate_outputs(tables,solutions):
    """Audit saved inversions against accepted scores, including equal/censored pairs."""
    curves=tables["f0_curves"];cases=tables["paired_equivalent_area"];wide=solutions.pivot(index=["unit_key","household"],columns="strategy",values="fci_validator")
    if len(list(cases.groupby(["pooling","household","method"])))!=40:raise ValueError("Expected all 40 F2 reference groups")
    for (pooling,household,method),frame in cases.groupby(["pooling","household","method"]):
        allowed={"D1","D2"} if pooling=="real_plans" else set(solutions.source) if pooling=="pooled" else {pooling}
        expected=solutions[(solutions.household==household)&solutions.source.isin(allowed)].drop_duplicates("unit_key")
        if frame.unit_key.duplicated().any() or set(frame.unit_key)!=set(expected.unit_key):raise ValueError("F2 population membership changed")
        indexed=frame.set_index(["unit_key","household"])
        for s in ["S0","S1","S2"]:
            if not np.allclose(indexed[s],wide.loc[indexed.index,s],rtol=0,atol=1e-10):raise ValueError("F2 changed input FCI")
        curve=curves[(curves.pooling==pooling)&(curves.household==household)&(curves.method==method)].sort_values("area_m2")
        refit=fit_reference(frame.nia_m2,frame.S0,method)
        if not np.allclose(curve.area_m2,refit["area"]) or not np.allclose(curve.fitted_fci_S0,refit["capacity"]):raise ValueError("F2 saved reference differs from prescribed fit")
        result=paired_gain(refit,frame.S0.to_numpy(),frame.S2.to_numpy())
        for key,values in result.items():
            if not np.allclose(values,frame[key].to_numpy(),atol=1e-8,rtol=0,equal_nan=True):raise ValueError("F2 paired identity or support flags differ: "+key)
    for frame in tables.values():
        if np.isinf(frame.select_dtypes(include="number").to_numpy()).any():raise ValueError("F2 output contains infinity")
        for lo in [key for key in frame if key.endswith("_ci_lo")]:
            hi=lo[:-2]+"hi"
            if not frame[lo].isna().eq(frame[hi].isna()).all() or (frame[lo]>frame[hi]).any():raise ValueError("F2 interval endpoints inconsistent")


def main():
    parser=prepare_cli(__doc__);parser.add_argument("--jobs",type=int,default=4);args=parser.parse_args();config,_,_=start_run(args,"07_f2_analysis")
    if args.dry_run:print("Would require accepted F1, refit both paired-area references in unit bootstraps and regenerate primary statistics/adequacy/decomposition.");return
    solutions,gate=load_corrected(config);root=Path("results/expA_f1/analysis");root.mkdir(parents=True,exist_ok=True)
    numerical=decomposition_module();wide=numerical.paired_effects(solutions)
    files=["scripts/07_f2_analysis.py","scripts/phase07_corrected.py","scripts/phase07_f1.py","scripts/phase07_paired_area.py","scripts/phase07_statistics.py","scripts/07_decomposition.py"]
    inputs=dict(solutions_sha256=gate["combined_sha256"],F1_acceptance_sha256=sha256_file(Path("results/expA_f1/acceptance.json")),
        evaluability_sha256=gate["input_provenance"]["evaluability_sha256"],bootstrap=config["experiments"]["bootstrap"],taus=config["experiments"]["tau_sensitivity"],seed=config["seed"],
        implementations={name:sha256_file(Path(name)) for name in files})
    fingerprint=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest();cache=Path(config["paths"]["interim"])/"expA_f2"/fingerprint[:16];jobs=[]
    for pooling in ["pooled","real_plans","D1","D2","D3"]:
        frame=wide if pooling=="pooled" else wide[wide.source.isin(["D1","D2"])] if pooling=="real_plans" else wide[wide.source==pooling]
        for household,group in frame.groupby("household",sort=True):
            seed=config["seed"]+int(hashlib.sha256((pooling+household).encode()).hexdigest()[:8],16)
            jobs.append((pooling,household,group,inputs["bootstrap"],inputs["taus"],seed,str(cache/(pooling+"_"+household))))
    write_json(root/"run.json",dict(status="running",inputs=inputs,expected_groups=len(jobs)));paths=[]
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for future in tqdm(as_completed([pool.submit(group_job,job) for job in jobs]),total=len(jobs),desc="F2 groups"):
            paths.append(Path(future.result()));write_json(root/"progress.json",dict(completed_groups=len(paths),expected_groups=len(jobs)))
    tables={}
    for name in OUTPUTS:
        frame=pd.concat([pd.read_csv(path/(name+".csv")) for path in sorted(paths)],ignore_index=True)
        if name=="supplementary_tests":
            order=np.argsort(frame.p_value.to_numpy());frame["p_holm_all_tests"]=np.nan
            frame.loc[order,"p_holm_all_tests"]=np.minimum(1.,np.maximum.accumulate(frame.p_value.to_numpy()[order]*(len(frame)-np.arange(len(frame)))))
        frame.to_csv(root/(name+".csv"),index=False);tables[name]=pd.read_csv(root/(name+".csv"))
    validate_outputs(tables,solutions)
    wide.to_csv(root/"form_time_effects.csv",index=False)
    summary=numerical.summarize(wide,inputs["bootstrap"]["n"],inputs["bootstrap"]["ci"],config["seed"])
    summary.to_csv(root/"form_time_by_area.csv",index=False);numerical.render_f4b(summary,root/"figures/F4b_corrected")
    render_gain(tables["area_gain_summary"],root/"figures/F4_paired_area_gain")
    amin=tables["min_adequate_area"].pivot(index=["pooling","household","tau"],columns="strategy",values="a_min_m2")
    amin[(amin.S2>amin.S1+1e-8)|(amin.S1>amin.S0+1e-8)].reset_index().to_csv(root/"adequacy_fit_reversals.csv",index=False)
    write_json(root/"run.json",dict(status="complete",inputs=inputs,completed_groups=len(paths),reference_methods=METHODS,
        primary_statistics="Paired mean FCI differences, bootstrap confidence intervals and shares improved. Wilcoxon is supplementary because scores are ordered by construction.",
        resampling="Complete unit vectors; both references refitted in each resample; shared indices for strategies and thresholds.",
        interval_policy="Percentile interval with at least 80% supported draws and at least two observed units. Positive-area median conditions on uncensored positive gains; identification bounds also reported.",
        adequacy="One-class, separation, nonincreasing and out-of-support crossings withheld. Real-plan single-person nonidentification is reported; D3/pooled estimates are labelled by evidence source.",
        limitations="Empty-raster E1 selection unchanged; at 0.10 m, oblique kitchen openings can be lost. Designed shells are not a population sample. Independent logistic crossings may reverse.",
        visual_review="pending",corrected_layout_showcases="pending"))
    outputs={p.relative_to(root).as_posix():sha256_file(p) for p in sorted(root.rglob("*")) if p.is_file() and p.name not in ["acceptance.json","progress.json"]}
    write_json(root/"acceptance.json",dict(numerical_checks_passed=True,inputs=inputs,reference_groups=40,outputs=outputs,
        full_F2_package_complete=False,pending=["actual figure inspection","corrected H3/H4 layout showcases and inspection"],permits="Corrected numerical analysis only; not G3 acceptance."))
    print(json.dumps(dict(numerical_checks_passed=True,groups=len(paths),reference_groups=40,visual_review="pending")))


if __name__=="__main__":main()
