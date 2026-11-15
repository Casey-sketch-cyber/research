# Phase 12c — Publication revisions

The [G4 review](../reviews/G4_review.md) approved the computational package and requested six revisions in a follow-up PR.

## 1. What was done

- [x] Emitted forward-slash source links in all seven publication tables.
- [x] Cited the area comparators in Methods and added reader-facing names in T7.
- [x] Marked the sparse F5 bins and recorded the closest-bin reference sensitivity.
- [x] Clarified the identified positive gain estimand in F9 and its caption.
- [x] Re-rendered the 10 m² showcase with the toilet enclosure cut away and added matched main-room details to the 29.97 m² showcase. Both figures explain their zero transformation burden.
- [x] Added the commuter and parent-and-child Hong Kong estimates.
- [x] Checked the revised package for reproducibility and publication privacy.

## 2. Acceptance

| Review item | Verification |
| --- | --- |
| Table links | PASS. Every relative link in the seven Markdown tables resolves with forward slashes. [Tables](../results/tables/g4/) |
| Area comparators | PASS. The Methods draft attributes the functional benchmarks and the area-only Hong Kong comparator. T7 contains their public names and the reviewed confusion counts. [Methods](../manuscript/draft_methods.md) · [T7](../results/tables/g4/T7.md) |
| F5 and reference sensitivity | PASS. Grey marks identify bins with fewer than 10 pairs. Upward triangles denote unbounded upper ends. The Results draft gives the sensitivity for the six smallest observed-plan couple pairs. [F5](../results/figures/g4/F5.pdf) · [Results](../manuscript/draft_results.md) |
| F9 estimand | PASS. The label identifies ΔEA and the note states that the subset of improved, identified pairs can change by condition. [F9](../results/figures/g4/F9.pdf) |
| Render visibility and caption | PASS. The cutaway exposes the furniture in showcase_10. The close-ups use identical framing and low walls to expose the main room in both strategies for showcase_30. Each figure identifies constant S2 states (TB = 0). [F3b, 10 m²](../results/figures/g4/F3b_10.pdf) · [F3b, 29.97 m²](../results/figures/g4/F3b_30.pdf) · [Render evidence](../results/renders3d/polish/manifest.json) |
| Hong Kong coverage in Results | PASS. Both added S0–S2 comparisons match the accepted scenario summary under the shared quality rule. [Scenario estimates](../results/g3_review_k3/hk_scenario_summary.csv) |
| Publication package | PASS. Four final PDF pages and all eight new presentation views were visually inspected. The release manifest binds the revised outputs and the previously validated geometry. [Visual review](../results/g4/visual_review.json) · [Release manifest](../results/g4/release_manifest.json) |

## 3. Key numbers

- At 16–18 m², the observed-plan couple bin has six matched units. The observed-plan reference gives a median gain lower bound of 16.6 m². The pooled reference identifies a median gain of 8.2 m². [Area summaries](../results/g3/area_summary.csv)
- For the commuter, the Hong Kong S0 and catalogue S2 fitted minimum adequate areas are 13.40 m² and 12.37 m². For the parent and child, they are 19.58 m² and 17.07 m². [Scenario estimates](../results/g3_review_k3/hk_scenario_summary.csv)

## 4. Scope

Six cutaway views and two detail views supplement the 30 originally audited stills. The main-room detail frames the combined furniture extent of the daytime S0 and S2 layouts. The presentation views use the approved scene sources and furniture states. [Presentation manifest](../results/renders3d/polish/manifest.json) · [Geometry audit](../results/renders3d/geometry_audit.csv)

## 5. Decisions

[D-49](DECISIONS.md) records the visual encoding for sparse bins and the matched view choices.

## 6. Review

The follow-up PR groups all six items for one review. [Gate G4](GATE_G4.md)

## 7. Runtime and resources

Rendering the eight accepted presentation views took 96.19 s with Blender Cycles. The publication revisions use the previously accepted experimental results. The final summary gives the full rebuild commands. After rendering the presentation views, `python scripts/12_make_figures.py --only polish` refreshes the four affected figures and their manifests. [Reproduction commands](FINAL_SUMMARY.md)
