"""Audit saved A2 layouts and report paired form/time changes without new solves."""
import os
for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[name]="1"
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm
from fea.config import config_hash
from fea.geometry.unit import Unit
from fea.geometry.raster import rasterize
from fea.households import parse_households
from fea.validate import validate_layout
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase07_analysis import load_evaluable_solutions
from phase07_a2 import acceptance


def audit_job(job):
    serialized,hname,rows,config,cache,main_cache=job
    unit=Unit.from_dict(json.loads(serialized))
    grid=rasterize(unit,config["raster"]["resolution_m"],config["furniture"]["meta"]["walking_width"],config["raster"]["source_gap_close_m"])
    household=parse_households(config["households"],config["furniture"])[hname]
    output=[]
    for row in rows:
        path=Path(cache)/"shared"/row["layout_file"]
        layout=json.loads(path.read_text());checked=validate_layout(layout,grid,config,household)
        if not checked["pass"] or abs(checked["fci"]-row["fci_validator"])>1e-8:
            raise ValueError("Saved A2 layout failed independent revalidation")
        if layout["unit_key"]!=row["unit_key"] or layout["household"]!=hname or layout["strategy"]!=row["strategy"]:
            raise ValueError("A2 layout identity mismatch")
        old_path=Path(main_cache)/row["layout_file"];old=json.loads(old_path.read_text())
        if abs(old["fci"]-row["main_fci"])>1e-8:raise ValueError("Original A layout score mismatch")
        rechecked=validate_layout(old,grid,config,household)
        if rechecked["pass"]!=row["main_layout_valid_under_variant"]:raise ValueError("A2 warm-start validity mismatch")
        regret=checked["fci"]-rechecked["fci"] if rechecked["pass"] else None
        if regret is not None and regret < -1e-8:raise ValueError("A2 discarded a better validated incumbent")
        output.append(dict(unit_key=row["unit_key"],household=hname,strategy=row["strategy"],validator_pass=checked["pass"],
            fci_validator=checked["fci"],main_fci=row["main_fci"],main_valid_under_A2=rechecked["pass"],
            main_revalidated_A2_fci=rechecked["fci"],gain_over_revalidated_main=regret,
            main_score_changed_under_A2=abs(rechecked["fci"]-row["main_fci"])>1e-8,
            saved_A2_sha256=sha256_file(path),saved_main_sha256=sha256_file(old_path)))
    return output


def summarise(pairs,config):
    output=[]
    pools={"pooled":pairs,"real_plans":pairs[pairs.source.isin(["D1","D2"])],**{s:pairs[pairs.source==s] for s in sorted(pairs.source.unique())}}
    for pool,frame in pools.items():
        for household,group in frame.groupby("household"):
            bins=np.floor((group.nia_m2+1e-8)/2)*2
            groups=[("overall",None,group)]+[("area_bin",float(lo),group[bins==lo]) for lo in sorted(bins.unique())]
            for scope,lo,g in groups:
                cols=["form_main","time_main","form_A2","time_A2","delta_form","delta_time"]
                values=g[cols].to_numpy(float)
                values=np.column_stack([values,(g.time_main.to_numpy()>1e-8).astype(float),(g.time_A2.to_numpy()>1e-8).astype(float)])
                cols += ["time_positive_share_main","time_positive_share_A2"]
                seed=config["seed"]+int(hashlib.sha256(f"{pool}:{household}:{scope}:{lo}".encode()).hexdigest()[:8],16)
                rng=np.random.default_rng(seed)
                draws=values[rng.integers(0,len(g),size=(config["experiments"]["bootstrap"]["n"],len(g)))].mean(axis=1)
                alpha=(1-config["experiments"]["bootstrap"]["ci"])/2
                limits=np.quantile(draws,[alpha,1-alpha],axis=0) if len(g)>1 else np.full((2,len(cols)),np.nan)
                row=dict(pooling=pool,household=household,scope=scope,area_bin_lo=lo,area_bin_hi=lo+2 if lo is not None else None,n_units=len(g))
                for i,key in enumerate(cols):row.update({key:float(values[:,i].mean()),key+"_ci_lo":float(limits[0,i]),key+"_ci_hi":float(limits[1,i])})
                output.append(row)
    return pd.DataFrame(output)


def render(frame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,3,figsize=(15,8),sharex=True,sharey=True)
    for i,h in enumerate(sorted(frame.household.unique())):
        for j,pool in enumerate(["pooled","real_plans","D3"]):
            ax=axes[i,j];d=frame[(frame.household==h)&(frame.pooling==pool)&(frame.scope=="area_bin")].sort_values("area_bin_lo")
            x=d.area_bin_lo.to_numpy()+1
            for key,label,color in [("delta_form","Change in form effect","#286c91"),("delta_time","Change in time effect","#b55b32")]:
                ax.plot(x,d[key],"o-",ms=3,color=color,label=label)
                ax.fill_between(x,d[key+"_ci_lo"].to_numpy(float),d[key+"_ci_hi"].to_numpy(float),alpha=.15,color=color)
            ax.axhline(0,color="black",lw=.6);ax.grid(alpha=.15)
            ax.set(title=pool.replace("_"," ")+" / "+h.split("_")[0],xlabel="Net internal area (m²)",ylabel="A2 minus main effect (FCI)")
            ax.legend(fontsize=8)
    fig.suptitle("Fixed-side bed-access sensitivity: paired unit-bootstrap 95% intervals");fig.tight_layout()
    for suffix in ["png","pdf"]:fig.savefig("results/figures/F4c_A2."+suffix,dpi=300,bbox_inches="tight")
    plt.close(fig)


def main():
    args=prepare_cli(__doc__).parse_args();config,_,_=start_run(args,"07_a2_report")
    if args.dry_run:print("Would audit completed A2 and report paired form/time changes without new solves.");return
    root=Path("results/expA2");run=json.loads((root/"run.json").read_text())
    if run["status"]!="complete":raise ValueError("A2 not complete")
    frame=pd.read_csv(root/"solutions.csv");sample=pd.read_csv(root/"sample.csv");checked=acceptance(frame,sample.unit_key)
    for path,key in [("scripts/07_run_a2.py","driver_sha256"),("scripts/phase07_a2.py","helper_sha256"),("config/a2_overrides.yaml","override_sha256")]:
        if sha256_file(Path(path))!=run["inputs"][key]:raise ValueError("A2 frozen implementation changed")
    if config_hash(run["config"])!=run["inputs"]["config_hash"]:raise ValueError("A2 snapshot mismatch")
    main,gate=load_evaluable_solutions(config);selected=main[main.nia_m2<=20+1e-8].unit_key.unique()
    if set(selected)!=set(sample.unit_key):raise ValueError("A2 sample differs from E1 small units")
    original=main.set_index(["unit_key","household","strategy"]);indexed=frame.set_index(["unit_key","household","strategy"])
    if not np.allclose(indexed.main_fci,original.loc[indexed.index,"fci_validator"],atol=1e-8):raise ValueError("Paired baseline differs")
    if run["inputs"]["evaluability_sha256"]!=gate["evaluability_sha256"]:raise ValueError("A2 E1 digest differs")
    main_run=json.loads(Path("results/expA/run.json").read_text())
    corpus=pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",columns=["unit_key","unit_json"]).set_index("unit_key")
    jobs=[(corpus.loc[key,"unit_json"],h,g.to_dict("records"),run["config"],run["cache"],str(Path(main_run["cache"])/"small"/"shared")) for (key,h),g in frame.groupby(["unit_key","household"])]
    audits=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for rows in tqdm(pool.map(audit_job,jobs),total=len(jobs),desc="A2 saved-layout audit"):audits.extend(rows)
    audit=pd.DataFrame(audits);audit.to_csv(root/"layout_revalidation.csv",index=False)
    pairs=frame.pivot(index=["unit_key","household"],columns="strategy",values=["main_fci","fci_validator"])
    pairs.columns=[("main_" if a=="main_fci" else "A2_")+s for a,s in pairs.columns]
    pairs=pairs.join(frame.drop_duplicates(["unit_key","household"]).set_index(["unit_key","household"])[["source","nia_m2"]])
    for variant in ["main","A2"]:
        pairs["form_"+variant]=pairs[variant+"_S1"]-pairs[variant+"_S0"];pairs["time_"+variant]=pairs[variant+"_S2"]-pairs[variant+"_S1"]
    for effect in ["form","time"]:pairs["delta_"+effect]=pairs[effect+"_A2"]-pairs[effect+"_main"]
    pairs=pairs.reset_index();pairs.to_csv(root/"paired_effects.csv",index=False)
    summary=summarise(pairs,config);summary.to_csv(root/"effect_summary.csv",index=False);render(summary)
    negative=frame[frame.delta_fci < -1e-8].merge(audit,on=["unit_key","household","strategy"],suffixes=("","_audit"));negative.to_csv(root/"negative_changes.csv",index=False)
    visual_path=Path("config/a2_visual_review.json")
    visual=json.loads(visual_path.read_text()) if visual_path.exists() else {}
    visual_pass=bool(visual.get("passed")) and all(sha256_file(Path(p))==digest for p,digest in visual.get("hashes",{}).items())
    if visual and not visual_pass:raise ValueError("A2 visual review is stale")
    completed=datetime.fromtimestamp((root/"run.json").stat().st_mtime,timezone.utc).isoformat(timespec="seconds")
    columns=["pooling","household","n_units","form_main","form_A2","delta_form","delta_form_ci_lo","delta_form_ci_hi","time_main","time_A2","delta_time","delta_time_ci_lo","delta_time_ci_hi"]
    lines=["# Phase 7 — A2 one-side double-bed sensitivity","","## Completion and acceptance","",
        f"PASS: {len(frame)} cases across {len(sample)} evaluable small units. Saved-layout revalidation, exact sample/baseline matching, and within-A2 S2 >= S1 >= S0 all pass. No re-solve or numerical-code change was needed. Completion: {completed}; measured search wall time {run['wall_time_this_invocation_s']/3600:.6f} hours, distinct from reporting time.","",
        f"Valid zero cases: {checked['zero_cases']}. Status counts: {json.dumps(checked['status_distribution'],sort_keys=True)}. TIMEOUT_WITH_INCUMBENT denotes a valid retained solution, not proof of optimality or a missing result.","",
        "## Paired form and time effects","",
        "Form=S1-S0; time=S2-S1. Each contrast pairs the same unit and household across main and A2. Resample the paired unit vector 1,000 times; 95% percentile intervals describe this retained sample, not a housing population. All 2 m2 bins and source panels are in effect_summary.csv and F4c_A2.","",summary[summary.scope=="overall"][columns].to_markdown(index=False,floatfmt=".6f"),"",
        "## Limitations and negative changes","",
        f"Sample composition: {json.dumps(sample.source.value_counts().to_dict(),sort_keys=True)}. There are no D2 small units; the real-plan panel is D1 only and D3 dominates pooled results.","",
        f"There are {len(negative)} case-level FCI decreases. Of these, {int(negative.main_valid_under_A2.sum())} original layouts remain geometrically valid under A2 but their rescored service changes; {int((~negative.main_valid_under_A2).sum())} are invalid under A2. Every returned layout scores at least as well as its original layout when that original is valid and rescored under A2. No negative observation was replaced or discarded.","",
        "The fixed local-left convention removes the opposite-side service target. In the frozen main validator, the union of both clearance strips is a service approach region; either reachable strip can provide service. Reserving clearance on two sides is distinct from requiring both sides reachable. Removing the reachable side can reduce service even when a layout remains geometrically valid. Four rotations do not introduce mirrored item families. The sofa-bed override additionally replaces front-only 0.50 m access. Thus A2 is a fixed-side variant, not a universal relaxation or an optimized choice of accessible side. Main configuration and all outcomes remain unchanged (Q25).", "",
        "H4's static catalogue ceiling persists. S1-S0 gains must not be interpreted as pure time sharing; S2-S1 is reported separately. The time effect need not rise when static/form performance improves more strongly.","",
        "## Checklist and continuation","",
        "- [x] All selected small units, two households, three strategies, original solve budgets.",
        "- [x] Complete solve and independent saved-layout checks, with frozen provenance.",
        "- [x] Paired form/time changes, source and NIA-bin summaries, unit-bootstrap intervals.",
        "- [x] Preserve and explain negative changes without tuning to an expected direction.",
        ("- [x] F4c_A2 visually inspected; analysis ready for publication and B continuation." if visual_pass else "- [ ] Visual review of F4c_A2 before B continuation."),"",
        "Reproduce with: python scripts/07_a2_report.py after the frozen A2 run. This report does not authorize a new geometry/access rule or claim later experiments complete.",""]
    Path("reports/phase_07_A2.md").write_text("\n".join(lines),encoding="utf-8")
    write_json(root/"report_acceptance.json",dict(passed=True,completed_at_utc=completed,measured_wall_hours=run["wall_time_this_invocation_s"]/3600,
        solve_acceptance=checked,independently_revalidated=len(audit),main_revalidated_under_A2=len(audit),valid_original_incumbent_regressions=0,
        negative_changes=len(negative),geometry_valid_negative_cases=int(negative.main_valid_under_A2.sum()),analysis_script_sha256=sha256_file(Path(__file__)),
        evaluability_sha256=gate["evaluability_sha256"],inputs={p:sha256_file(Path(p)) for p in ["results/expA2/solutions.csv","results/expA2/run.json","results/expA2/sample.csv","results/expA/solutions.csv"]},
        outputs={p:sha256_file(root/p) for p in ["layout_revalidation.csv","paired_effects.csv","effect_summary.csv","negative_changes.csv"]},visual_review_pending=not visual_pass,visual_review_sha256=sha256_file(visual_path) if visual_pass else None))
    print(json.dumps(dict(passed=True,cases=len(frame),revalidated=len(audit),negative_changes=len(negative),wall_hours=run["wall_time_this_invocation_s"]/3600)))


if __name__=="__main__":main()
