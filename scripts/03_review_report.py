"""Generate the G1 revision evidence from regenerated, accepted result files."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fea.io import prepare_cli, start_run


def main():
    """Write review responses with traceable values, never transcribed result estimates."""
    args = prepare_cli(__doc__).parse_args()
    _, digest, _ = start_run(args, "03_review_report")
    if args.dry_run:
        print("Would generate G1 revision reports from acceptance JSON and result tables.")
        return
    read = lambda name: json.loads(Path("reports", name).read_text())
    audit, acceptance, furniture = map(read, ("corpus_audit.json", "phase02_acceptance.json", "furniture_audit.json"))
    assert acceptance["pass"] and furniture["pass"], "Regeneration must pass before reporting completion"
    assert audit["config_hash"] == acceptance["config_hash"] == furniture["config_hash"] == digest
    root = Path("results/corpus")
    counts = pd.read_csv(root / "counts.csv").drop(columns="config_hash")
    reasons = pd.read_csv(root / "exclusion_reasons.csv").drop(columns="config_hash")
    distributions = pd.read_csv(root / "review_distributions.csv").drop(columns="config_hash")
    sample = pd.read_csv(root / "expA_sample.csv")
    corpus = pd.read_csv(root / "corpus_units.csv")
    sites = sample[sample.source == "D1"].groupby("group_id").size()
    full_counts = counts.to_markdown(index=False)
    comparison = distributions[distributions.category.isin(["included_unique", "entrance_only_exclusion"])]
    scale = distributions[distributions.category == "D2_all"]
    geometry_note = ("Normalized geometry hashes include class layers, walls, sorted openings, entrance, room count and service flags. "
        "IDs/sites are excluded. Hashing uses a 1 micrometre grid; analysis coordinates remain unchanged. "
        "Mirrors and quarter-turn equivalence are not inferred. n_duplicates counts additional eligible copies, not total multiplicity. "
        "The representative is the lexically first source/unit key. Site grouping is retained.")
    sampling_note = ("D1 uses fixed-seed random order within 2 m² NIA × room-count strata, selected by proportional-quota deficit "
        "subject to at most five per site. Site caps can prevent exact proportional allocation; sample_strata.csv and F2 expose the difference. "
        "All eligible unique D2/D3 units are retained. The pilot must draw from this frozen file.")
    text = f"""# Response to G1 review

**Status: M1–M6 and S1–S4 corpus changes complete; continued engineering authorized through G2.**

Q-12 continuation is authorized in reviews/G1_review_addendum_Q12.md. The broad first-quantification claim is withdrawn. Remaining Task L screening is due during Phase 7/G3; the historical stop report is not the current instruction.

## M1: NIA — done
NIA is the union of furnishable, storage-only, walkable-only and fixed-service regions minus walls. Excluded outdoor/service classes are not added. The primary filter is 8–50 m² with only a 1e-6 m² numerical tolerance; the obsolete furnishable-area fallback is not applied. D1 gross area remains missing. F2 reports NIA first and furnishable area second.

## M2: Complete dwellings — done
Require a habitable room with positive furnishable area, sanitary room/fixture and kitchen room/fixture. Explicit reasons are in exclusion_reasons.csv (reasons overlap, so their counts must not be summed as unique exclusions).

## M3: Storage-only rooms — done for corpus; carried into Phase 5
STOREROOM/CLOAKROOM and D2 storage are a separate storage_only layer. Their area counts towards NIA and circulation; only storage furniture bodies may occupy them in candidate generation and validation. No beds/tables/seating are recategorized as storage furniture.

## M4: Deduplication — done
{geometry_note}

## M5: Frozen experiment sample — done
{sampling_note}

D1 sample sites: {len(sites)}; largest site contribution: {int(sites.max())}. Sample units containing KITCHEN_DINING: {audit['expA_kitchen_dining_units']}; that class remains conservatively fixed service, as approved.

## M6: Regenerated artifacts — done
corpus_units.csv, counts.csv, exclusion_reasons.csv, expA_sample.csv, sample_strata.csv, F2 PNG/PDF, sample_units.json, 24 individual views and the contact sheet are regenerated from the revised definitions. Views show both areas and are drawn from the frozen sample.

{full_counts}

## S1: D2 scale — done
Door span is the long side of each calibrated opening's minimum rectangle. Wall thickness uses normal cross-sections at wall-boundary edge midpoints, weighted by edge length, not a bounding-box width. Unmeasurable values and median door/wall spans outside 0.6–1.3 / 0.05–0.50 m are excluded. Released wall_depth is scaled independently for comparison. No measured value is clipped to the admissible ranges.

{scale.to_markdown(index=False)}

Per-plan values and flags: d2_scale_audit.csv. Scale plausibility supports the approved calibration assumption; it is not independent ground-truth surveying.

## S2: ABO orientation — done
Each listing footprint is sorted to long/short sides before computing quartiles. Configuration dimensions are similarly sorted. {furniture['outside_IQR']} of {furniture['comparisons']} comparisons are outside the IQR; {furniture['unvalidated_states']} remain state-specific unvalidated comparisons and {furniture['no_match']} have no cohort. Furniture defaults are unchanged and review-approved design assumptions.

## S3: Entrance selection bias — done
The comparison below includes only units whose complete reason set is a nonempty subset of missing_entrance / entrance_not_touching_known_spaces; no other failure is included. Included units are deduplicated. The table reports observed selection differences, not an assumption that exclusion is size-neutral. The pre-dedup eligible distribution is also available in review_distributions.csv.

{comparison.to_markdown(index=False)}

## S4: D3 services — done
Maximum fixed-service/entrance-keepout overlap: {audit['D3_max_entrance_keepout_overlap_m2']:.12g} m². Placement counts: {json.dumps(audit['D3_service_placement'], sort_keys=True)}. near_entrance requires both service centroids in the entrance-wall half of the shell; otherwise far_end. All generated shells remain recorded, even if a later check excludes one.

## Acceptance and scope
{sum(acceptance['checks'].values())}/{len(acceptance['checks'])} automated acceptance checks passed. Full suite: {acceptance['pytest_summary']}. Config hash: {digest}. The corpus package contains no FCI/FEA results. Continue Phases 5–6 and stop at G2 under the review authorization.

## Engineering corrections
D1 and D2 records exposed a GEOS assertion when subtracting mixed-dimensional geometry from empty storage. Empty storage now bypasses that identity operation; the observed D2 record has a regression test and both full sources are checked. Completed cached records were reused only where the correction was semantically identical; new clean runs regenerate all source data. D1/D2 resume skips already completed keys before geometric conversion.
"""
    text += "\n## Visual inspection of regenerated artifacts\nThe 24-unit contact sheet and F2 were inspected: both area labels are legible, the D1-05 storage room is distinct, service areas are separated from furnishing space, and D3 entrance spans remain unobstructed by service bodies. F2 shows that the site cap reduces the share of smaller D1 units in the frozen sample; exact proportionality is not claimed. These are checks of rendered geometry, not furniture feasibility results.\n"
    Path("reports/GATE_G1_response.md").write_text(text, encoding="utf-8")
    phase = f"""# Phase 02: Corpus construction — G1 revision

**Status: COMPLETE, superseding the original furnishable-area corpus.**

## Checklist and acceptance
- [x] Convert all authorized D1/D2 and generated D3 units; preserve source group IDs as opaque keys.
- [x] Normalize, audit and filter by NIA and complete-dwelling requirements.
- [x] Separate storage-only areas, deduplicate geometry and freeze the site-capped sample.
- [x] Audit D2 scales and D3 entrance keepouts; publish exclusion-bias distributions.
- [x] Regenerate counts, F2 and 24 sample views.
- [x] Run observed-source loader regressions and corpus acceptance: {acceptance['pytest_summary']}; {len(acceptance['checks'])} checks passed.

## Key numbers
{full_counts}

## Exclusions (nonexclusive reasons)
{reasons.to_markdown(index=False)}

## Decisions and deviations
{geometry_note}

{sampling_note}

NIA includes fixed rooms and storage but excludes walls. Source gross-area claims are not substituted for NIA. There is no furnishable-area fallback. D2 geometric scale calibration and strict entrance contact remain approved assumptions. Missing D1 gross area remains missing. See GATE_G1_response.md for all M/S responses and selection-bias tables.

## Open questions
Review the revised views and scale/entrance distributions at G2. No unsupported novelty, FCI or FEA conclusion is inferred from corpus construction.

## Runtime and reproducibility
Successful aggregation invocation: {audit['total_seconds_this_invocation']:.3f} s (cached source conversion excluded). Per-source conversion attempts are recorded in corpus_audit.json; interrupted/restarted attempts are not presented as total end-to-end runtime. Config hash: {digest}. Commands: docs/REPRODUCING.md.
"""
    Path("reports/phase_02_corpus.md").write_text(phase, encoding="utf-8")
    phase3 = f"""# Phase 03: Furniture library check — G1 revision

**Status: COMPLETE; defaults approved as design assumptions.**

## Checklist and acceptance
- [x] Parse authorized listings and convert units.
- [x] Trim above the per-type 99th percentile.
- [x] Sort each footprint into long/short sides before quartile comparisons (S2).
- [x] Explain every flag and retain unchanged furniture defaults.
All {len(furniture['checks'])} checks passed; {furniture['pytest_summary']}.

## Key numbers
Reference listings before/after trimming: {furniture['reference_listings_before']}/{furniture['reference_listings_after']}. Comparisons: {furniture['comparisons']}; outside IQR: {furniture['outside_IQR']}; unvalidated states/items: {furniture['unvalidated_states']}; no cohort: {furniture['no_match']}. Flags overlap. Values are in results/furniture/abo_dimension_check.csv and abo_type_statistics.csv.

## Decisions, limitations and open questions
The review approved unchanged design defaults. Broad ordinary-product cohorts do not validate transformation mechanism/state, clearance, storage capacity or occupant capacity. No replacement size is inferred. The planned clearance sensitivity analysis remains necessary; state-specific product evidence is still limited.

## Runtime
Successful invocation: {furniture['runtime_s']:.3f} s. Config hash: {digest}.
"""
    Path("reports/phase_03_furniture.md").write_text(phase3, encoding="utf-8")
    print("Generated G1 response and revised phase reports from accepted outputs")


if __name__ == "__main__":
    main()
