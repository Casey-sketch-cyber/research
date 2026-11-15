# Gate G4 — Final figures, drafts and research package

The [G4 review](../reviews/G4_review.md) approved the computational package and requested six publication revisions. [Phase 12c report](phase_12c_polish.md)

| Requested change | G4 evidence |
| --- | --- |
| Publish the updated figures | [F10](../results/figures/g4/F10.pdf) plots the larger couple kit and optimized catalogue by area. [F12](../results/figures/g4/F12.pdf) uses the K3-ranked dimensions and gives the training and transfer comparisons. |
| Report the commuter conclusion | The [Results draft](../manuscript/draft_results.md#experiment-k--furniture-dimensions) states that no tested kit established an improvement over the optimized catalogue. F12 labels H1_kit_01 as an evaluated candidate. |
| Explain the couple's size trade-off | The [Results draft](../manuscript/draft_results.md#hong-kong-scenario--size-dependent-adequacy) reports Aₘᵢₙ of 15.39 versus 16.12 m², 51/120 versus 30/120 adequate at 13–16 m², and mean FCIq of 0.448 versus 0.500 below 13 m². |
| Record the selection rule and uncertainty | [Decision D-48](DECISIONS.md) records that H3_kit_02 ranks first by observed training mean FCIq. The paired contrast of +0.0021 [−0.0336, +0.0279] includes zero. |

- [Final summary, research answers and reproduction commands](FINAL_SUMMARY.md)
- [Methods draft](../manuscript/draft_methods.md) and [Results draft](../manuscript/draft_results.md)
- [F1–F12 and F3b publication figures](../results/figures/g4/) and [T1–T7 tables](../results/tables/g4/)
- [Scene and still files](../results/renders3d/) and [geometry audit](../results/renders3d/geometry_audit.csv)
- [Phase report and acceptance checks](phase_12_G4.md) and [G4 release manifest](../results/g4/release_manifest.json)

Run `python scripts/12_verify_g4.py --verify` to check the artifact hashes and G4 acceptance.
