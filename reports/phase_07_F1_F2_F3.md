# Phase 7 — Current review implementation

Review: [phase07_review_A1A2](../reviews/phase07_review_A1A2.md), b3d1a71. Follow-up results are in [the accepted F1/F2 report](phase_07_F1_F2_results.md). No intermediate reviewer stop is required before G3.

- [x] Correct the two reviewed single-bed inventory caps and verify all H1/H2 candidate tables and primary bounds on 2619 units.
- [x] Re-solve all 15714 H3/H4 cases with frozen production budgets; independently validate and join compatible H1/H2 rows with their original provenance.
- [x] Complete F2 paired equivalent-area gain, median-bin primary reference and mean-isotonic sensitivity, censoring bounds and 1000 paired unit resamples.
- [x] Report mean FCI differences, bootstrap intervals and improvement shares as primary; retain Wilcoxon as supplementary. Report single-person real-plan adequate-area nonidentification.
- [x] Revalidate and visually inspect all 33 original layout examples and both corrected summary figures. Full F2 package accepted.
- [x] Implement mirrored left/right 0.60 m alternatives with shared family inventory; pass 153 full-suite regression tests.
- [x] Start F3 on the exact original 348 small units, H3 only, three strategies (1044 cases).
- [x] Complete and independently analyse F3; retain negative changes and failed old-layout mappings. See [F3 results](phase_07_F3_results.md).
- [ ] Run B on the frozen 200-pair sample with corrected evidence, then D/R/ablations, C, reduced H1/H3 K, HK, literature and G3.

## Observed state

F1 completed at 2026-11-10T03:13:28+00:00: 15714/15714 corrected solves, 18.498 hours. All corrected and combined cases validate, with no strategy-ordering failures. The combined evidence has 31428 cases over 2619 evaluable units. H1/H2 scores and actual original configuration hashes are preserved.

F2 completed 20 household/population groups, 40 reference groups including sensitivity. The initial numerical acceptance explicitly left visual review pending; the later results/expA_f1/analysis/package_acceptance.json records completion of the full package. Original example selection is unchanged.

F3 started at 2026-11-10T07:53:15+00:00, after F1/F2 acceptance and regression checks. It retains 120 seconds per solve, four solver workers, three concurrent jobs and 0.10 m anchors. Current run files are in results/expA_f3/. The solve completed at 2026-11-10T16:17:08+00:00: 1044 cases, zero invalid cases and ordering failures. Independent saved-layout audit, paired comparison, negative-change diagnosis and figure review have passed. All 1044 new layouts and their corrected F1 counterparts revalidate. Measured search time is 8.397508 hours. B input preparation passed for all 200 frozen pairs; the 12-pair runtime pilot has now passed and the full three-algorithm comparison is running.

## Evidence and interpretation limits

Original A/A1 and fixed-left A2 remain historical records. Old H3/H4 outcomes are superseded by F1; the earlier FEA-minus-own-area saving definition is retired for every household. E1/E2/E3 membership evidence and the B sample are unchanged. Valid zero-score units remain included; at the 0.10 m raster, oblique kitchen openings can be lost.

Paired gains invert S0 and S2 on one curve. Equal scores give zero; unsupported unequal scores retain censoring and lower bounds. Positive uncensored medians, gain prevalence and censoring are reported separately. Pooled, real-plan and designed-shell evidence remain distinct.

F3 aliases share their original physical family limit; a side is fixed per item, not changed by time slot. The main right strip was 0.50 m and sofa_bed used front 0.50 m, so this exact 0.60 m variant is not a universal geometric superset. All physical mirror choices of an old layout are independently checked; 59 losses were retained: 49 cases have no valid old-layout mirror mapping and 10 have a valid mapping with reduced rescored service. No better valid mapped incumbent was discarded. See Q28.

## Reproducibility

F1 numerical source remained frozen through completion; its source is available at 022a790 and its exact numerical signature is in the run manifest. Only then were optional family-count constraints added independently to solver and validator. F3 records its own signature, override, driver and preflight hashes. Use 022a790 to reproduce F1, followed by the F3 implementation for the sensitivity. F3 completed with its frozen numerical source. Review files remain untouched.

## F3 completion checklist

- [x] Exact 1044-case run complete with frozen inputs.
- [x] Independently revalidate saved F3 and corrected F1 layouts; repeat every physical mirror mapping and verify retained valid scores.
- [x] Paired form/time effects by source and 2 m² bins, 1000 paired unit-bootstrap intervals; retain all negative changes.
- [x] Inspect F4c_F3 and pass hash-bound package acceptance before B.
- [x] Revalidate all 200 frozen B main-reference layouts under their actual provenance and the corrected main rules (99 corrected H3/H4, 101 verified H1/H2).

## 2026-11-11 review: P1 and approved continuation

phase07_review_F.md approves F1/F2/F3 and requires no additional access variants. Continue B through G3 without another stop.

- [x] Reclassify lower-support clamped gains as lower bounds; identified-positive medians exclude them.
- [x] Report lower-bound counts by household/source/bin and retain ≥ notation for real-plan single-person summaries.
- [x] Add pooled-reference inversion for the same real-plan units with refitted paired bootstrap curves.
- [x] Publish new P1 tables/figure and inspect them; keep the frozen F2/F3 packages intact and explicitly supersede their old area summaries.
- [ ] Complete B fixed pilot and full benchmark; proceed with D/R/ablations, C, reduced K, HK and screening to G3.

P1 is accepted in results/expA_f1/analysis_p1/package_acceptance.json. See [the current area-gain report](phase_07_P1_results.md); all 48 reference/target groups, 1000 paired resamples per reference group and the inspected replacement figure are complete. Earlier F2 area summaries are historical, not current identified estimates. Claude approved F3 as a robustness check: its one-side variant changes both reserved space and access options and does not increase the time effect. No additional access variants will be introduced.
