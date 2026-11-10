"""Accept corrected F2 evidence only after actual visual review and layout rescoring."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import numpy as np
import pandas as pd
from fea.config import config_hash
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli,start_run,sha256_file,write_json
from fea.validate import validate_layout
from phase07_corrected import load_corrected


def main():
    args=prepare_cli(__doc__).parse_args();config,_,_=start_run(args,"07_f2_acceptance")
    if args.dry_run:print("Would verify corrected metrics, all saved examples and actual visual-review hashes before permitting F3.");return
    root=Path("results/expA_f1/analysis");solutions,gate=load_corrected(config)
    numerical=json.loads((root/"acceptance.json").read_text())
    if not numerical["numerical_checks_passed"] or numerical["inputs"]["solutions_sha256"]!=gate["combined_sha256"]:raise ValueError("F2 numerical gate differs")
    for name,digest in numerical["outputs"].items():
        if sha256_file(root/name)!=digest:raise ValueError("F2 numerical artifact changed: "+name)
    for name,digest in numerical["inputs"]["implementations"].items():
        if sha256_file(Path(name))!=digest:raise ValueError("F2 numerical implementation changed: "+name)
    spec=importlib.util.spec_from_file_location("F2_audit_metrics","scripts/07_f2_analysis.py");module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    tables={name:pd.read_csv(root/(name+".csv")) for name in module.OUTPUTS};module.validate_outputs(tables,solutions)
    audit=pd.read_csv(root/"layout_audit.csv");selection=pd.read_csv(root/"layout_selection.csv");original_selection=pd.read_csv("results/expA/layout_selection.csv")
    keys=["unit_key","household","strategy","purpose"]
    if len(audit)!=33 or not selection[keys].equals(original_selection[keys]):raise ValueError("F2 changed the frozen example selection")
    visual_path=Path("config/f2_visual_review.json");visual=json.loads(visual_path.read_text())
    expected_images={row.file_stem+".png" for row in audit.itertuples()}|{str(root/"figures/F4b_corrected.png"),str(root/"figures/F4_paired_area_gain.png")}
    if not visual["passed"] or visual["reviewed_layouts"]!=33 or visual["reviewed_summary_figures"]!=2 or set(visual["hashes"])!=expected_images:raise ValueError("Actual F2 visual review incomplete")
    for name,digest in visual["hashes"].items():
        if sha256_file(Path(name))!=digest:raise ValueError("Visual artifact changed: "+name)
    original=json.loads(Path("results/expA_f1/original_config_snapshot.json").read_text());run=json.loads(Path("results/expA_f1/run.json").read_text())
    indexed=solutions.set_index(["unit_key","household","strategy"]);rows=[]
    for row in audit.itertuples():
        record=indexed.loc[row.unit_key,row.household,row.strategy];local=deepcopy(original if record.result_origin.startswith("original_") else config)
        arm=run["production_settings"][record.budget_group];local["solver"].update({name:arm[name] for name in ["num_workers","time_limit_s"]});local["raster"]["anchor_stride_m"]=arm["anchor_stride_m"]
        path=Path(row.file_stem);layout=json.loads(path.with_suffix(".json").read_text())
        unit=Unit.from_dict(json.loads((path.parent/(row.unit_key.replace(":","_")+"_unit.json")).read_text()))
        if config_hash(local)!=record.config_hash or layout["config_hash"]!=record.config_hash:raise ValueError("Example provenance changed")
        for extension in ["json","png","pdf"]:
            digest=getattr(row,"layout_sha256" if extension=="json" else extension+"_sha256")
            if sha256_file(path.with_suffix("."+extension))!=digest:raise ValueError("Example artifact changed")
        grid=rasterize(unit,local["raster"]["resolution_m"],local["furniture"]["meta"]["walking_width"],local["raster"]["source_gap_close_m"])
        checked=validate_layout(layout,grid,local,parse_households(local["households"],local["furniture"])[row.household])
        if not checked["pass"] or abs(checked["fci"]-record.fci_validator)>1e-8:raise ValueError("Example independent rescore failed")
        rows.append(dict(unit_key=row.unit_key,household=row.household,strategy=row.strategy,validator_pass=True,fci=checked["fci"]))
    pd.DataFrame(rows).to_csv(root/"independent_example_recheck.csv",index=False)
    primary=tables["primary_effects"];real=primary[(primary.pooling=="real_plans")&(primary.stratum=="overall")][["household","comparison","mean_difference","mean_difference_ci_lo","mean_difference_ci_hi","share_improved"]]
    gain=tables["area_gain_summary"];gain=gain[(gain.pooling=="real_plans")&(gain.stratum=="overall")&(gain.method=="median_bin_cummax")][["household","share_fully_functional_S0","share_fci_improved","share_known_positive_area_gain","median_delta_ea_positive_uncensored_m2","share_delta_right_censored"]]
    adequacy=tables["min_adequate_area"];single=adequacy[(adequacy.pooling=="real_plans")&adequacy.household.str.startswith(("H1_","H2_"))&(abs(adequacy.tau-.95)<1e-8)][["household","strategy","n_units","adequate_units","min_observed_nia_m2","a_min_m2","status"]]
    old=pd.read_csv("results/expA/solutions.csv",low_memory=False);comparison=[]
    for h in ["H3_couple_one_remote","H4_parent_child"]:
        for s in ["S0","S1","S2"]:
            new=solutions[(solutions.household==h)&(solutions.strategy==s)]
            prior=old[(old.household==h)&(old.strategy==s)&old.unit_key.isin(new.unit_key)]
            comparison.append(dict(household=h,strategy=s,units=len(new),old_mean_fci=prior.fci_validator.mean(),corrected_mean_fci=new.fci_validator.mean(),old_max_fci=prior.fci_validator.max(),corrected_max_fci=new.fci_validator.max()))
    pd.DataFrame(comparison).to_csv(root/"configuration_correction_summary.csv",index=False)
    text=["# Corrected F1/F2 results and acceptance","",f"F1 completed {gate['rerun']['completed_cases']} corrected cases in {run['wall_time_this_invocation_s']/3600:.3f} hours; all passed independent validation, with zero ordering failures. Joined evidence has {gate['combined']['completed_cases']} cases from {gate['combined']['units']} evaluable units. Original raw results remain unchanged.","",
        "F2 completed all 20 household/evidence groups and both reference methods, using 1000 paired unit resamples. Both summary figures and the same 33 original examples were visually inspected; all saved examples were independently rescored again after the optional F3 family-count guard was added. Numerical analysis and complete-package acceptance remain separate records.","",
        "## Effect of the reviewed configuration correction","",pd.DataFrame(comparison).to_markdown(index=False,floatfmt=".5f"),"",
        "## Primary paired effects in real plans (D1+D2)","",real.to_markdown(index=False,floatfmt=".5f"),"",
        "Mean paired differences, bootstrap intervals and shares improved are primary. S2 ≥ S1 ≥ S0 is enforced through validated incumbent reuse, so Wilcoxon and rank-biserial statistics are only supplementary.","",
        "## Paired area gains in real plans","",gain.to_markdown(index=False,floatfmt=".5f"),"",
        "The positive-area median conditions on positive uncensored gains; it is not the median over all homes or all possibly censored gainers. Tables also provide censoring bounds and lower-support flags. Equal capacity scores give zero paired gain. Pooled, real-plan, D1, D2 and designed-shell results remain separate; neither D3 nor the pooled mixture is a population sample.","",
        "## Single-person real-plan adequate-area support","",single.to_markdown(index=False,floatfmt=".4f"),"",
        "With almost all observed real homes adequate, minimum adequate area can be unidentified or outside observed support. These outcomes are retained as findings. D3 and pooled estimates are explicitly labelled in min_adequate_area.csv; independent logistic fits may show ordering reversals, which are retained.","",
        "## Limits and next experiment","",
        "The original E1 exclusions and E2 audit are unchanged: at the fixed 0.10 m raster, oblique kitchen openings can be lost. Valid zero-score units remain included. Old H3/H4 results and fixed-left A2 are historical; the old FEA-minus-own-area metric is retired.","",
        "F3 follows on the same 348 small units for H3 only, with mirrored left/right 0.60 m choices and shared family inventory. Main right strips were 0.50 m and sofa_bed used front 0.50 m, so the exact reviewed sensitivity is not a universal geometric superset. Original layouts are remapped and independently rescored; any losses are reported, not removed. Full K remains disabled; B and later phases follow the approved order.",""]
    report=Path("reports/phase_07_F1_F2_results.md");report.write_text("\n".join(text),encoding="utf8")
    write_json(root/"package_acceptance.json",dict(passed=True,full_F2_package_complete=True,F1_solutions_sha256=gate["combined_sha256"],
        numerical_acceptance_sha256=sha256_file(root/"acceptance.json"),visual_review_sha256=sha256_file(visual_path),examples_revalidated=len(rows),summary_figures_reviewed=2,
        example_audit_sha256=sha256_file(root/"independent_example_recheck.csv"),layout_manifest_sha256=sha256_file(root/"layout_manifest.json"),report_sha256=sha256_file(report),
        permits="F3 continuation under phase07_review_A1A2; not G3 or full-study acceptance"))
    print(json.dumps(dict(passed=True,examples_revalidated=len(rows),summary_figures_reviewed=2)))


if __name__=="__main__":main()
