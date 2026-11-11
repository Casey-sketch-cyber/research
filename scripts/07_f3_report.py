"""Independently audit completed F3 and compare paired corrected-F1 effects."""
import os
for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
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
from fea.io import prepare_cli, start_run, write_json, sha256_file
from phase07_corrected import load_corrected
from phase07_f1 import check_cases
from phase07_f3 import HOUSEHOLDS, variant_config, mapped_incumbent

ROOT = Path("results/expA_f3")
FIGURES = ["results/figures/F4c_F3.png", "results/figures/F4c_F3.pdf"]
REPORT = "reports/phase_07_F3_results.md"


def audit_job(job):
    """Recompute the saved score and every physical old-layout side choice."""
    serialized, rows, main_config, variant, cache, main_cache, fingerprint = job
    unit = Unit.from_dict(json.loads(serialized))
    grid = rasterize(unit, variant["raster"]["resolution_m"], variant["furniture"]["meta"]["walking_width"], variant["raster"]["source_gap_close_m"])
    household = parse_households(variant["households"], variant["furniture"])[HOUSEHOLDS[0]]
    main_household = parse_households(main_config["households"], main_config["furniture"])[HOUSEHOLDS[0]]
    output = []
    for row in rows:
        path = Path(cache)/"shared"/row["layout_file"]
        old_path = Path(main_cache)/row["layout_file"]
        layout = json.loads(path.read_text()); old = json.loads(old_path.read_text())
        for item in [layout, old]:
            if any(item[k] != row[k] for k in ["unit_key", "household", "strategy"]):
                raise ValueError("Saved F3/F1 layout identity mismatch")
        if layout["config_hash"] != config_hash(variant) or layout["code_hash"] != fingerprint:
            raise ValueError("Saved F3 provenance differs")
        if old["config_hash"] != config_hash(main_config):
            raise ValueError("Saved F1 budget/configuration differs")
        checked = validate_layout(layout, grid, variant, household)
        main_checked = validate_layout(old, grid, main_config, main_household)
        if not checked["pass"] or not main_checked["pass"]:
            raise ValueError("Saved F3/F1 geometry failed independent revalidation")
        if any(abs(a-b)>1e-8 for a,b in [(checked["fci"],row["fci_validator"]), (checked["fci"],layout["fci"]), (checked["tb"],row["tb"]), (main_checked["fci"],row["main_fci"]), (main_checked["fci"],old["fci"])]):
            raise ValueError("Saved F3/F1 score differs from independent calculation")
        best, mapping = mapped_incumbent(old, grid, variant, household)
        for key in ["mirror_combinations", "valid_mappings"]:
            if mapping[key] != row[key]: raise ValueError("Mirror mapping counts differ")
        best_fci = mapping["best_mapped_fci"]
        if best_fci is None:
            if not pd.isna(row["best_mapped_fci"]): raise ValueError("Missing mapping was reported as valid")
        elif pd.isna(row["best_mapped_fci"]) or abs(best_fci-row["best_mapped_fci"])>1e-8:
            raise ValueError("Best independently rescored mirror differs")
        gain = None if best is None else checked["fci"]-best_fci
        if gain is not None and gain < -1e-8:
            raise ValueError("F3 discarded a better valid remapped baseline")
        output.append(dict(unit_key=row["unit_key"], household=row["household"], strategy=row["strategy"],
            validator_pass=True, main_validator_pass=True, fci_validator=checked["fci"], main_fci=main_checked["fci"],
            **mapping, gain_over_valid_mapping=gain,
            mapping_score_loss=best is not None and best_fci<main_checked["fci"]-1e-8,
            saved_F3_sha256=sha256_file(path), saved_F1_sha256=sha256_file(old_path)))
    return output


def paired_effects(frame):
    """Preserve every paired observation, including negative variant changes."""
    if not np.allclose(frame.delta_fci, frame.fci_validator-frame.main_fci, atol=1e-8, rtol=0):
        raise ValueError("F3 difference column does not match paired scores")
    pairs = frame.pivot(index=["unit_key","household"], columns="strategy", values=["main_fci","fci_validator"])
    pairs.columns = [("main_" if a=="main_fci" else "F3_")+s for a,s in pairs.columns]
    if pairs.isna().any().any(): raise ValueError("Incomplete paired strategies")
    pairs = pairs.join(frame.drop_duplicates(["unit_key","household"]).set_index(["unit_key","household"])[["source","nia_m2"]])
    for variant in ["main","F3"]:
        pairs["form_"+variant] = pairs[variant+"_S1"]-pairs[variant+"_S0"]
        pairs["time_"+variant] = pairs[variant+"_S2"]-pairs[variant+"_S1"]
    for effect in ["form","time"]:
        pairs["delta_"+effect] = pairs[effect+"_F3"]-pairs[effect+"_main"]
    return pairs.reset_index()


def summarise(pairs,config):
    output=[]
    pools={"pooled":pairs,"real_plans":pairs[pairs.source.isin(["D1","D2"])],**{s:pairs[pairs.source==s] for s in sorted(pairs.source.unique())}}
    for pool,frame in pools.items():
        for household,group in frame.groupby("household"):
            bins=np.floor((group.nia_m2+1e-8)/2)*2
            groups=[("overall",None,group)]+[("area_bin",float(lo),group[bins==lo]) for lo in sorted(bins.unique())]
            for scope,lo,g in groups:
                cols=["form_main","time_main","form_F3","time_F3","delta_form","delta_time"]
                values=g[cols].to_numpy(float)
                values=np.column_stack([values,(g.time_main.to_numpy()>1e-8).astype(float),(g.time_F3.to_numpy()>1e-8).astype(float)])
                cols += ["time_positive_share_main","time_positive_share_F3"]
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
    fig, axes = plt.subplots(1,3,figsize=(15,4.8),sharex=True,sharey=True)
    for ax,pool in zip(axes,["pooled","real_plans","D3"]):
        d = frame[(frame.pooling==pool)&(frame.scope=="area_bin")].sort_values("area_bin_lo")
        x = d.area_bin_lo.to_numpy()+1
        for key,label,color in [("delta_form","Change in form effect","#286c91"),("delta_time","Change in time effect","#b55b32")]:
            ax.plot(x,d[key],"o-",ms=3,color=color,label=label)
            ax.fill_between(x,d[key+"_ci_lo"].to_numpy(float),d[key+"_ci_hi"].to_numpy(float),alpha=.15,color=color)
        n=int(frame[(frame.pooling==pool)&(frame.scope=="overall")].n_units.iloc[0])
        ax.axhline(0,color="black",lw=.6);ax.grid(alpha=.15)
        ax.set(title=pool.replace("_"," ")+f" / H3 (n={n})",xlabel="Net internal area (m²)",ylabel="Mirrored variant minus main effect (FCI)")
        ax.legend(fontsize=8)
    fig.suptitle("Either-side 0.60 m bed access: paired unit-bootstrap 95% intervals")
    fig.tight_layout()
    for path in FIGURES: fig.savefig(path,dpi=300,bbox_inches="tight")
    plt.close(fig)


def finalize():
    """Require numerical evidence and an explicit review of the exact figure."""
    path=ROOT/"report_acceptance.json"; gate=json.loads(path.read_text())
    if not gate["passed"] or gate["analysis_script_sha256"] != sha256_file(Path(__file__)):
        raise ValueError("F3 numerical acceptance/source is stale")
    for name,digest in {**gate["inputs"],**gate["outputs"]}.items():
        if sha256_file(Path(name)) != digest: raise ValueError("F3 accepted evidence changed")
    visual_path=Path("config/f3_visual_review.json"); visual=json.loads(visual_path.read_text())
    if not visual.get("passed") or set(visual.get("hashes",{}))!={FIGURES[0]}:
        raise ValueError("F3 exact figure needs visual review")
    for name,digest in visual["hashes"].items():
        if sha256_file(Path(name))!=digest: raise ValueError("F3 figure review is stale")
    result=dict(passed=True,full_F3_package_complete=True,
        independently_revalidated=gate["independently_revalidated"],
        main_revalidated_and_remapped=gate["main_revalidated_and_remapped"],
        numerical_acceptance_sha256=sha256_file(path), visual_review_sha256=sha256_file(visual_path),
        completed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        F3_solutions_sha256=gate["inputs"]["results/expA_f3/solutions.csv"])
    write_json(ROOT/"package_acceptance.json",result); print(json.dumps(result))


def main():
    parser=prepare_cli(__doc__); parser.add_argument("--finalize",action="store_true")
    args=parser.parse_args(); config,_,_=start_run(args,"07_f3_report")
    if args.dry_run: print("Would verify completed F3 provenance, independently rescore F1/F3 layouts and all mirror mappings, and report paired effects."); return
    if args.finalize: finalize(); return
    run=json.loads((ROOT/"run.json").read_text()); gate=json.loads((ROOT/"acceptance.json").read_text())
    if run["status"]!="complete" or not gate["passed"]: raise ValueError("F3 has not passed execution acceptance")
    inp=run["inputs"]; variant=json.loads((ROOT/"config_snapshot.json").read_text())
    input_paths={"results/expA_f3/solutions.csv":gate["solutions_sha256"],"results/expA_f3/sample.csv":inp["sample_sha256"],
        "results/expA_f3/preflight.json":inp["preflight_sha256"],"results/expA2/sample.csv":inp["original_A2_sample_sha256"],
        "results/expA_f1/solutions.csv":inp["F1_solutions_sha256"],"results/expA_f1/analysis/package_acceptance.json":inp["F2_package_sha256"],
        "scripts/07_run_f3.py":inp["driver_sha256"],"scripts/phase07_f3.py":inp["helper_sha256"],"config/f3_overrides.yaml":inp["override_sha256"]}
    for name,digest in input_paths.items():
        if sha256_file(Path(name))!=digest: raise ValueError("F3 input/provenance changed: "+name)
    sources=sorted(Path("src/fea").rglob("*.py"))+[Path("scripts/06_revision.py")]
    signature=hashlib.sha256(b"".join(str(p).encode()+p.read_bytes() for p in sources)).hexdigest()
    if signature!=inp["F3_numerical_signature"]: raise ValueError("Frozen numerical implementation changed")
    if config_hash(config)!=inp["main_config_hash"] or config_hash(variant)!=inp["variant_config_hash"] or config_hash(variant_config(config))!=config_hash(variant):
        raise ValueError("F3 variant/configuration differs")
    fingerprint=hashlib.sha256(json.dumps(inp,sort_keys=True).encode()).hexdigest()
    frame=pd.read_csv(ROOT/"solutions.csv"); sample=pd.read_csv(ROOT/"sample.csv")
    check=check_cases(frame,sample.unit_key,HOUSEHOLDS)
    if not frame.config_hash.eq(config_hash(variant)).all() or not frame.code_hash.eq(fingerprint).all(): raise ValueError("F3 row provenance differs")
    main,accepted=load_corrected(config); selected=main[main.nia_m2<=20+1e-8].drop_duplicates("unit_key").set_index("unit_key")
    if set(selected.index)!=set(sample.unit_key): raise ValueError("F3 small-unit membership changed")
    if not frame.source.eq(frame.unit_key.map(selected.source)).all() or not np.allclose(frame.nia_m2,frame.unit_key.map(selected.nia_m2),atol=1e-8,rtol=0): raise ValueError("F3 source/area metadata differs")
    original=main.set_index(["unit_key","household","strategy"]); indexed=frame.set_index(["unit_key","household","strategy"])
    if not np.allclose(indexed.main_fci,original.loc[indexed.index,"fci_validator"],atol=1e-8,rtol=0): raise ValueError("F3 baseline differs from corrected F1")
    main_run=json.loads(Path("results/expA_f1/run.json").read_text()); small=main_run["production_settings"]["small"]
    main_config=deepcopy(config);main_config["solver"].update({k:small[k] for k in ["time_limit_s","num_workers"]});main_config["raster"]["anchor_stride_m"]=small["anchor_stride_m"]
    corpus=pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",columns=["unit_key","unit_json"]).set_index("unit_key")
    jobs=[(corpus.loc[key,"unit_json"],g.to_dict("records"),main_config,variant,run["cache"],str(Path(main_run["cache"])/"small"/"shared"),fingerprint) for key,g in frame.groupby("unit_key")]
    audits=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for rows in tqdm(pool.map(audit_job,jobs),total=len(jobs),desc="F3 saved-layout and mirror audit"): audits.extend(rows)
    audit=pd.DataFrame(audits);audit.to_csv(ROOT/"layout_revalidation.csv",index=False)
    pairs=paired_effects(frame);pairs.to_csv(ROOT/"paired_effects.csv",index=False)
    summary=summarise(pairs,config);summary.to_csv(ROOT/"effect_summary.csv",index=False);render(summary)
    negative=frame[frame.delta_fci < -1e-8].merge(audit,on=["unit_key","household","strategy"],suffixes=("","_audit"))
    negative["diagnosis"]=np.where(negative.valid_mappings_audit==0,"no_valid_old_layout_mapping","valid_mapping_with_reduced_service_score")
    if (negative.valid_mappings_audit.gt(0)&~negative.mapping_score_loss).any(): raise ValueError("Unexplained negative F3 case")
    negative.to_csv(ROOT/"negative_changes.csv",index=False)
    columns=["pooling","n_units","form_main","form_F3","delta_form","delta_form_ci_lo","delta_form_ci_hi","time_main","time_F3","delta_time","delta_time_ci_lo","delta_time_ci_hi"]
    counts=frame.status.value_counts().to_dict(); missing=int((negative.valid_mappings_audit==0).sum()); valid=int((negative.valid_mappings_audit>0).sum())
    lines=["# Phase 7 — F3 mirrored double-bed access","","## Completed run and independent checks","",
        f"Completed {run['completed_at_utc']}: {len(frame)} cases, {len(sample)} original small units, H3 only, all three strategies. Measured search wall time: {run['wall_time_this_invocation_s']/3600:.6f} hours. All saved F3 layouts and all paired corrected-F1 layouts independently revalidate. Every physical left/right mapping was repeated and matches the run records; no better valid mapped incumbent was discarded.","",
        f"Zero invalid cases; zero strategy-ordering failures; {check['zero_cases']} valid zero-score cases. Status counts: {json.dumps(counts,sort_keys=True)}. A time limit with a valid incumbent is a completed budgeted solve, not proof of optimality.","",
        "## Paired form and time effects","",
        "Main denotes the corrected F1 result for the same unit and household. Form = S1-S0; time = S2-S1. Each of 1,000 bootstrap draws resamples the entire paired unit vector; 95% percentile intervals describe this retained benchmark. Single-unit bins have no confidence interval. The side choice is fixed for each physical item across slots and aliases share the original family inventory cap.","",
        summary[summary.scope=="overall"][columns].to_markdown(index=False,floatfmt=".6f"),"",
        "Source and 2 m²-bin estimates, positive time-effect shares and intervals are in effect_summary.csv; F4c_F3 displays the changes. These are sensitivity results; the main configuration and corrected F1/F2 estimates are unchanged.","",
        "## Negative results and scope","",
        f"Retained all {len(negative)} negative case-level changes: {missing} corrected main layouts have no valid physical side mapping, and {valid} have a valid mapping whose service score falls under the exact variant. The latter retain at least their independently rescored mapped score. Details and both layout hashes are in negative_changes.csv and layout_revalidation.csv.","",
        "The main right clearance strip was 0.50 m; the variant uses 0.60 m on the chosen side. Sofa beds change from front 0.50 m to side 0.60 m. Thus mirrored side choices fix the fixed-left restriction, but this exact variant remains neither a universal geometric superset nor a guarantee of larger time effects. Main access uses the union of the clearance strips as a reachable service region; the side retained can change service. Negative effects are preserved without tuning or replacement (Q28).","",
        f"Sample composition: {json.dumps(sample.source.value_counts().to_dict(),sort_keys=True)}. Real plans contain D1 only in this small-unit subset; D3 shells dominate pooled estimates. Findings do not establish population-wide gains. E1/E2/E3 selection and the 0.10 m raster limitation are unchanged. Original fixed-left A2 remains a superseded historical run.","",
        "## Reproduction and completion","",
        "Run python scripts/07_f3_report.py after the frozen F3 solve. This audits results without new solves. Inspect F4c_F3, record its exact hash in config/f3_visual_review.json, then run the same script with --finalize. report_acceptance.json is numerical acceptance; package_acceptance.json is the final figure-and-evidence gate. B follows on the frozen 200-pair sample using the main corrected configuration; it is not covered by this report.",""]
    Path(REPORT).write_text("\n".join(lines),encoding="utf-8")
    output_paths=[str(ROOT/p) for p in ["layout_revalidation.csv","paired_effects.csv","effect_summary.csv","negative_changes.csv"]]+FIGURES+[REPORT]
    input_paths.update({str(p):sha256_file(p) for p in [ROOT/"run.json",ROOT/"acceptance.json",ROOT/"config_snapshot.json",Path("scripts/phase07_corrected.py"),Path("scripts/phase07_f1.py")]})
    result=dict(passed=True,independently_revalidated=len(audit),main_revalidated_and_remapped=len(audit),valid_mapped_incumbent_regressions=0,
        negative_changes=len(negative),negative_without_valid_mapping=missing,negative_with_rescored_mapping=valid,solve_acceptance=check,
        analysis_script_sha256=sha256_file(Path(__file__)),inputs=input_paths,outputs={p:sha256_file(Path(p)) for p in output_paths},
        numerical_completed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    write_json(ROOT/"report_acceptance.json",result)
    print(json.dumps({k:v for k,v in result.items() if k not in ["inputs","outputs"]}))


if __name__=="__main__": main()
