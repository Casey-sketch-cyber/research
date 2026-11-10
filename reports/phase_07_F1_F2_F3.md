# Phase 7 — Current review implementation

Review: [phase07_review_A1A2](../reviews/phase07_review_A1A2.md), b3d1a71. Follow-up results are in [the accepted F1/F2 report](phase_07_F1_F2_results.md). No intermediate reviewer stop is required before G3.

- [x] Correct the two reviewed single-bed inventory caps and verify all H1/H2 candidate tables and primary bounds on 2619 units.
- [x] Re-solve all 15714 H3/H4 cases with frozen production budgets; independently validate and join compatible H1/H2 rows with their original provenance.
- [x] Complete F2 paired equivalent-area gain, median-bin primary reference and mean-isotonic sensitivity, censoring bounds and 1000 paired unit resamples.
- [x] Report mean FCI differences, bootstrap intervals and improvement shares as primary; retain Wilcoxon as supplementary. Report single-person real-plan adequate-area nonidentification.
- [x] Revalidate and visually inspect all 33 original layout examples and both corrected summary figures. Full F2 package accepted.
- [x] Implement mirrored left/right 0.60 m alternatives with shared family inventory; pass 153 full-suite regression tests.
- [x] Start F3 on the exact original 348 small units, H3 only, three strategies (1044 cases).
- [ ] Complete and independently analyse F3; retain negative changes and failed old-layout mappings.
- [ ] Run B on the frozen 200-pair sample with corrected evidence, then D/R/ablations, C, reduced H1/H3 K, HK, literature and G3.

## Observed state

F1 completed at 2026-11-10T03:13:28+00:00: 15714/15714 corrected solves, 18.498 hours. All corrected and combined cases validate, with no strategy-ordering failures. The combined evidence has 31428 cases over 2619 evaluable units. H1/H2 scores and actual original configuration hashes are preserved.

F2 completed 20 household/population groups, 40 reference groups including sensitivity. The initial numerical acceptance explicitly left visual review pending; the later results/expA_f1/analysis/package_acceptance.json records completion of the full package. Original example selection is unchanged.

F3 started at 2026-11-10T07:53:15+00:00, after F1/F2 acceptance and regression checks. It retains 120 seconds per solve, four solver workers, three concurrent jobs and 0.10 m anchors. Current run files are in results/expA_f3/. The solve and its final comparison are not yet complete; B has not started.

## Evidence and interpretation limits

Original A/A1 and fixed-left A2 remain historical records. Old H3/H4 outcomes are superseded by F1; the earlier FEA-minus-own-area saving definition is retired for every household. E1/E2/E3 membership evidence and the B sample are unchanged. Valid zero-score units remain included; at the 0.10 m raster, oblique kitchen openings can be lost.

Paired gains invert S0 and S2 on one curve. Equal scores give zero; unsupported unequal scores retain censoring and lower bounds. Positive uncensored medians, gain prevalence and censoring are reported separately. Pooled, real-plan and designed-shell evidence remain distinct.

F3 aliases share their original physical family limit; a side is fixed per item, not changed by time slot. The main right strip was 0.50 m and sofa_bed used front 0.50 m, so this exact 0.60 m variant is not a universal geometric superset. All physical mirror choices of an old layout are independently checked; losses will be retained rather than tuned away. See Q28.

## Reproducibility

F1 numerical source remained frozen through completion; its source is available at 022a790 and its exact numerical signature is in the run manifest. Only then were optional family-count constraints added independently to solver and validator. F3 records its own signature, override, driver and preflight hashes. Use 022a790 to reproduce F1, followed by the F3 implementation for the sensitivity. Active F3 numerical source is now frozen. Review files remain untouched.
