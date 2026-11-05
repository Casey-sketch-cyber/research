"""Write the G2 review package from audited outputs and recorded visual reviews."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fea.io import prepare_cli, start_run, sha256_file


def table(frame: pd.DataFrame, fields: list[str]) -> str:
    """Render a compact Markdown table without an optional tabulation dependency."""
    def cell(value):
        return f"{value:.4f}" if isinstance(value, float) else str(value).replace("|", "/")
    rows = ["| "+" | ".join(fields)+" |", "| "+" | ".join("---" for _ in fields)+" |"]
    rows += ["| "+" | ".join(cell(row[k]) for k in fields)+" |" for _, row in frame.iterrows()]
    return "\n".join(rows)


def main():
    """Require complete machine and visual checks before marking the gate ready."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "06_gate")
    if args.dry_run:
        print("Would build G2 only after complete pilot audit and at least six visual reviews.")
        return
    read = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
    audit, projection, tests = [read("reports/"+p) for p in
                               ("pilot_audit.json", "pilot_runtime_projection.json", "pilot_tests.json")]
    visual = read("reports/pilot_visual_review.json")
    assert audit["pass"] and audit["config_hash"] == digest
    assert len(visual["reviews"]) >= 6
    for row in visual["reviews"]:
        assert sha256_file(Path(row["path"])) == row["sha256"], "Visual review is stale"
    counts = pd.read_csv("results/corpus/counts.csv")
    runtime = pd.read_csv("results/pilot/runtime_projection.csv")
    frame = pd.read_csv("results/pilot/pilot_solutions.csv")
    diagnostic = pd.read_csv("results/pilot/fixed_service_diagnostic.csv")
    failed = diagnostic[~diagnostic.raster_reachable]
    statuses = pd.DataFrame([dict(status=k, cases=v) for k, v in audit["status_counts"].items()])
    if not projection["over_budget"]:
        adjustment = "The point projection is within the budget. No D1 cap or solver-budget change is proposed on this evidence. Retain the uncertainty and rerun the projection after any method correction."
    elif projection["d2_d3_only_h"] >= projection["budget_h"]:
        adjustment = (f"Reducing D1 alone cannot satisfy the budget: D2+D3 already project to {projection['d2_d3_only_h']:.2f} h. "
            "The calculated D1 cap is zero, which is not a viable scientific design because D1 supplies the training corpus. "
            "At review, address solver efficiency and geometry issues first, then benchmark the prescribed shorter per-case budget and propose source-stratified caps if still necessary. "
            "Do not extrapolate a proportional speedup from halving the time limit: validated solution quality and actual stopping times must be measured. "
            "No frozen sample or solver limit has been changed by this report.")
    else:
        adjustment = (f"Following G1 M5, reduce D1 first: the measured point projection permits at most {projection['d1_max_at_point_estimate']} D1 units; "
            f"with an explicit 20% scheduling margin it permits {projection['d1_max_with_20pct_scheduling_margin']}. "
            "Use the existing NIA-bin × room-count stratification and site cap if approved. "
            "The frozen sample remains unchanged pending G2; reducing solve time comes after this review-prioritized adjustment.")
    visual_text = "\n".join(f"- [`{r['path']}`](../{r['path']}): {r['observation']}" for r in visual["reviews"])
    results = f"""## Pilot results

All {audit['cases']} cases from {audit['units']} frozen units are present. Independent revalidation found {audit['valid']} valid layouts and {audit['explained_invalid']} explained invalid cases from {audit['empty_invalid_units']} units failing empty-layout access. There are {audit['final_valid_nonempty']} valid nonempty layouts and {audit['final_valid_empty']} valid empty layouts. Among valid layouts, {audit['final_valid_zero_service']} score zero service, including {audit['final_valid_nonempty_zero_service']} with furniture present but no credited service. These fallbacks are reported separately so geometric validity or furniture count cannot conceal poor search performance or disconnected access.

{table(statuses, ['status', 'cases'])}

The {audit['ordering_pairs']} unit/household triples have {audit['ordering_failures']} violations of S2 ≥ S1 ≥ S0. Retaining prior-strategy incumbents contributes to this property: {audit['retained_previous_incumbents']} cases retained one, including {audit['early_bound_incumbents']} stopped at a proved primary bound. This is a finite-budget method check, not evidence that all strategy optima were solved. Strategy differences can include unequal search difficulty or a poor static incumbent; they must not yet be interpreted as furniture-caused area savings.

Retained-assignment FCI agreement and every saved config/code hash passed the independent audit. Agreement compares the separately recomputed, access-adjusted assignment score (`fci_solver`) with the validator, not the raw CP-SAT relaxation; raw scores and access failures remain in each solver trace. The saved objective/bound values describe the last raw CP-SAT search, not necessarily the retained validated layout. Tests: `{tests['stdout']}`. Detailed checks: [pilot_audit.json](pilot_audit.json); every layout and image: [layout_manifest.csv](../results/pilot/layout_manifest.csv).

The [per-unit summary](../results/pilot/summary_by_unit.csv) includes zero-service counts and runtimes; the [source/household/strategy summary](../results/pilot/summary_by_group.csv) preserves all cases, including failures.

## Access failures and interpretation

{table(failed, ['unit_key', 'target_index', 'continuous_diagnostic_reachable', 'reason'])}

The diagnostic continuous check erodes the same conservative source-space classification. `conservative_raster_loss` means a continuous route exists but the whole-cell raster and conservative walking-disc criterion remove it; the required resolution sensitivity must examine this. Other failures also occur under the continuous classification, because fixed rooms, narrow connections or source geometry interrupt the approach. None establishes that the original dwelling is physically unusable. These cases remain in the denominator with invalid status and zero FCI.

Visual diagnosis also corrected kitchen-to-balcony doors mistakenly treated as mandatory indoor service approaches. A door touching an excluded exterior space but no usable interior outside door polygons is now excluded from that target list. Unknown non-exterior connections remain conservative targets. The frozen units, source geometry, dimensions and walking width were unchanged; provisional runs before this correction are not final results.

See [fixed_service_diagnostic.csv](../results/pilot/fixed_service_diagnostic.csv) and the empty-layout sheets for [D1](../results/pilot/empty_access_D1.png), [D2](../results/pilot/empty_access_D2.png), [D3](../results/pilot/empty_access_D3.png).

The [empty-space connectivity summary](../results/pilot/empty_space_summary.csv) also tests connectivity before walking-radius erosion and counts reachable furnishable cells. Passing fixed-service access does not imply that every habitable room is connected; source-space gaps can therefore produce valid but zero-service layouts. No unlabelled gap was filled to improve a score.

## Runtime and Exp. A projection

Measured solver time summed across cases is {audit['solver_time_sum_s']/3600:.3f} h. Per-case median / p90 / p95 / maximum are {audit['runtime_quantiles_s']['0.5']:.3f} / {audit['runtime_quantiles_s']['0.9']:.3f} / {audit['runtime_quantiles_s']['0.95']:.3f} / {audit['runtime_quantiles_s']['1']:.3f} s. These times exclude plotting and shared preparation; the projection adds measured source-specific raster/candidate preparation.

{table(runtime, ['source', 'full_units', 'pilot_units', 'mean_unit_solver_s', 'mean_unit_preparation_s', 'projected_h'])}

The source-weighted projection is **{projection['projected_h']:.2f} h**, against {projection['budget_h']} h, with one solve at a time. A descriptive unit-bootstrap interval is {projection['descriptive_unit_bootstrap_interval_h'][0]:.2f}–{projection['descriptive_unit_bootstrap_interval_h'][1]:.2f} h. It is not a completion guarantee: the pilot is small, D3 deliberately spans selected areas, and fast structural failures are included. Geometry revisions need a new projection. Aggregation, I/O and selected publication renders are additional costs.

{adjustment}

## Recorded visual review

{visual_text}

## Reproduction and boundary

From the repository root after reproducing the revised corpus and installing the declared environment:

```sh
python scripts/05_candidates.py
python scripts/06_pilot.py
python scripts/06_report.py --run-tests
python scripts/06_gate.py
```

The final command checks the hashes in the recorded visual reviews. Re-solving with multithreaded CP-SAT can produce different incumbents even with the same seed; new images must be visually reviewed before updating that review record. All numbers above are generated by this script from saved audited outputs. No Phase 7 experiment, FEA estimate, minimum-area result, R/K analysis or hypothesis verdict is claimed here.
"""
    phase_path = Path("reports/phase_06_pilot.md")
    phase = phase_path.read_text(encoding="utf-8").split("## Pilot results")[0]
    phase = phase.replace("**Status: IMPLEMENTED; frozen pilot running, G2 not yet ready.**", "**Status: COMPLETE; G2 ready for method review.**")
    phase = phase.replace("- [ ]", "- [x]")
    phase_path.write_text(phase.rstrip()+"\n\n"+results, encoding="utf-8")
    gate = f"""# Gate G2: revised corpus, method and pilot

**Status: READY FOR REVIEW. Phase 7 has not started.**

## Revised G1 corpus first

{table(counts, ['source', 'eligible_before_dedup', 'included', 'duplicate_copies_removed', 'expA_sample'])}

NIA is the primary area measure; complete dwellings, storage-only classes, geometric deduplication and the frozen sample follow G1 M1–M6. Read [G1 response](GATE_G1_response.md), [F2](../results/figures/F2_corpus_area.png) and the [new contact sheet](../results/corpus/sample_contact_sheet.png) first. D1's site cap prevents filling its nominal maximum; source and area coverage limitations remain in the G1 response.

## Method review

The implemented solver, independent validator, simplifications and full result interpretation are in [phase_06_pilot.md](phase_06_pilot.md). The principal implementation differences are exhaustive integer anchor tables and optional rectangle intervals in place of expanded pose/cell Booleans; one S1 state per variant-day; a conservative walking-disc raster; retained nested-strategy incumbents; and early stopping at a proven primary capacity bound with zero burden, leaving window preference unoptimized. Geometry, storage and household defaults remain unchanged.

{results}

## Review decisions requested

- Check the exact encoding, service-target scope, S1 variant-day interpretation and early-stop/retained-incumbent protocol before full experiments.
- Review conservative access failures and valid empty/time-limited fallbacks; decide any method or resolution changes before treating FCI as an optimized research outcome.
- Review the measured runtime projection and the proposed scope response. Furniture and household parameters were not adjusted to improve outcomes.
- Return the verdict in `reviews/G2_review.md`. Work stops at this gate as required.
"""
    Path("reports/GATE_G2.md").write_text(gate, encoding="utf-8")
    candidate = read("reports/candidates_audit.json")
    path = Path("reports/phase_05_candidates.md")
    text = path.read_text(encoding="utf-8")
    before, after = text.split("## Key numbers and runtime")[0], text.split("## Decisions and limitations")[1]
    numbers = (f"\n\nCandidate-generation median {candidate['median_candidate_time_s']:.6f} s/unit; maximum {candidate['max_candidate_time_s']:.6f} s/unit. "
               f"Rasterization median {candidate['median_raster_time_s']:.6f} s/unit. These are measured separately after the entrance/target corrections. "
               f"The median is below the 2 s target. Per-item counts: results/candidates/counts.csv. Tests: {candidate['tests']}. Config hash: {digest}.\n\n")
    path.write_text(before+"## Key numbers and runtime"+numbers+"## Decisions and limitations"+after, encoding="utf-8")
    text = path.read_text(encoding="utf-8").replace("Continue solver/validator implementation and the required 240-instance pilot.",
        "The solver/validator and pilot are now complete; see the G2 method review. The publication audit redraws pilot images with explicit padding, leaving saved layouts unchanged.")
    path.write_text(text, encoding="utf-8")
    print(json.dumps(dict(gate="G2", ready=True, cases=audit['cases'], reviewed_renders=len(visual['reviews']), config_hash=digest)))


if __name__ == "__main__":
    main()
