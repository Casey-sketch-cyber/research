# Phase 12 and 12b — final research package

The [third G3 review](../reviews/G3_review_round3.md) approves the K3 results and advances the project to G4.

## 1. What was done

- [x] Built F1–F12 as PDF and 300 dpi PNG pairs from accepted numerical evidence.
- [x] Built T1–T7 in CSV and Markdown.
- [x] Wrote the methods and results drafts with source paths beside quantitative claims.
- [x] Applied the review's H1 conclusion and H3 size-dependent comparison. Recorded the H3 mean ranking and paired interval in D-48.
- [x] Exported ten validated scenes for five dwellings. Rendered 30 stills and composed three F3b grids.
- [x] Overlaid the three normal-day S2 top views on their validated layouts.
- [x] Wrote the final summary, reproduction commands and G4 review entry.

## 2. Acceptance

| Check | Status and evidence |
| --- | --- |
| F1–F12 and three F3b panels in both formats | PASS. The [2D](../results/figures/g4/manifest_2d.json) and [3D](../results/figures/g4/manifest_3d.json) manifests bind the inputs and outputs. All 15 PDF pages were rendered for visual review. |
| Seven tables in both formats | PASS. [Table manifest](../results/tables/g4/manifest.json) |
| Thirty stills at 2400 × 1800 | PASS. Five dwellings × two strategies × three time slots. The images use a shared orthographic camera, lighting and scale within each dwelling. [Render manifest](../results/renders3d/render_manifest.json) |
| Three geometric overlays under 2 cm | PASS. The largest projected outline error was 2.79 mm across 17 furniture instances. [Per-instance errors](../results/renders3d/geometry_audit.csv) · [Overlays](../results/renders3d/audits/) |
| Traceable drafts and the four G3 review notes | PASS. [Methods](../manuscript/draft_methods.md) · [Results](../manuscript/draft_results.md) · [Review note mapping](GATE_G4.md) |
| Prior review evidence | PASS. Verified 295 round-2 files and 23 K3 publication files with `11d_report_k3.py --verify`. [K3 manifest](../results/g3_review_k3/release_manifest.json) |
| Regression tests | PASS. All 187 tests passed. [Test receipt](../results/g4/test_receipt.json) |

## 3. Key numbers

- H1_kit_01 ranked first by observed training mean, with +0.0013 FCIq [−0.0153, +0.0200]. It yielded 11/30 adequate training shells versus 13/30 for the optimized catalogue and 184/390 versus 246/390 in the scenario. The paper retains the catalogue for the commuter. [Paired effects](../results/g3_review_k3/paired_effects.csv)
- H3_kit_02 gives a mean training contrast of +0.0021 FCIq [−0.0336, +0.0279] and 5/30 versus 2/30 adequate. In the scenario it gives 51/120 versus 30/120 adequate at 13–16 m², with lower mean FCIq below 13 m² (0.448 versus 0.500). Aₘᵢₙ is 15.39 [14.67, 16.19] versus 16.12 [15.70, 16.57] m². [Paired effects](../results/g3_review_k3/paired_effects.csv) · [Area estimates](../results/g3_review_k3/hk_scenario_summary.csv)

## 4. Deviations

- The optional animation was omitted. F3b shows the night, workday and dinner states for each showcase in the two configured strategies.
- F10 shows the unweighted Hong Kong shell grid. The census lacks joint floor-area and household-size distributions for district weighting. [D6 coverage](schemas/D6.md)
- The publication figures use a new directory under `results/figures/`. This lets reviewers check the exact hashes of the earlier G3 packages. The environment report and its generator retain software versions and test results. New deliverables and the current environment files omit personal and machine identifiers.
- Two generated H1 shells illustrate the smallest part of the experimental area range. The four saved layouts and their normalized geometry are included to allow independent revalidation from a checkout. Furniture meshes illustrate the validator's body footprints. The release verifies the line-ending normalization against every original render input.

## 5. Decision

[D-48](DECISIONS.md) records the H3 ranking rule, paired interval and the area band used to report the Hong Kong trade-off.

## 6. Review

Review the figures, the numerical provenance in the drafts and the completeness of the package at [G4](GATE_G4.md). The reviewed gate controls further publication.

## 7. Runtime and resources

The measured run used 18.06 s for figures and tables, 4.58 s for scene export and 370.36 s for the 30 stills and 3 top views. Blender Cycles generated the stills. The rendering script supports a CPU run and the recorded run used CUDA. Geometry projection was checked for every furniture item in the three audited layouts. No new experimental solve or numerical setting change was needed. [Final summary and reproduction commands](FINAL_SUMMARY.md)

## Deliverables

[Figures](../results/figures/g4/) · [Tables](../results/tables/g4/) · [Still and scene evidence](../results/renders3d/) · [Visual review](../results/g4/visual_review.json) · [Review manifest](../results/g4/release_manifest.json)
