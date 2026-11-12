# Phase 9b — Supporting room comparison and generalization

## Completed numerical work

R1 completed 16 independently validated outputs on four comparison envelopes × H1/H2 × S0/S2. R2 independently revalidated 10476 saved main layouts on 2619 units. R2/R3 performed no new solves; all signed gains and zero effects remain. This invocation took 0.178008 hours including reproduction, saved-layout checks and analysis.

Source values and PDF page/section references are in source_values.csv. R1 layouts and resumable R2 evidence are private cache artifacts linked by hashes. F11 is generated; full package acceptance additionally requires actual figure inspection.

## R1: approximate comparison, not exact reproduction

Bu & Che Mat report a 4 × 3 m bedroom and about 5–5.5 m² static activity area versus about 8 m² with folded furniture. This is a conceptual comparison, not an occupied-home area measurement. Their prose and Figure 10 disagree on bed width and wardrobe depth, and their activity estimate deducts clearances. Our prescribed body-only measure differs. Thus agreement or disagreement in a numerical ratio cannot establish exact reproduction.

| condition                     |   aspect_ratio | household               | strategy   |   free_activity_area_day_m2 |   gain_m2 |   gain_rel |   fci_validator |
|:------------------------------|---------------:|:------------------------|:-----------|----------------------------:|----------:|-----------:|----------------:|
| configured_D3_fallback        |       1.000000 | H1_single_commuter      | S0         |                    9.560000 |  0.000000 |   0.000000 |        0.687831 |
| configured_D3_fallback        |       1.000000 | H1_single_commuter      | S2         |                    9.560000 |  0.000000 |   0.000000 |        0.687831 |
| configured_D3_fallback        |       1.000000 | H2_single_remote_worker | S0         |                    9.480000 |  0.000000 |   0.000000 |        0.615385 |
| configured_D3_fallback        |       1.000000 | H2_single_remote_worker | S2         |                   10.540000 |  1.060000 |   0.111814 |        0.769231 |
| configured_D3_fallback        |       1.250000 | H1_single_commuter      | S0         |                    8.920000 |  0.000000 |   0.000000 |        0.846561 |
| configured_D3_fallback        |       1.250000 | H1_single_commuter      | S2         |                    8.920000 |  0.000000 |   0.000000 |        0.846561 |
| configured_D3_fallback        |       1.250000 | H2_single_remote_worker | S0         |                    9.480000 |  0.000000 |   0.000000 |        0.615385 |
| configured_D3_fallback        |       1.250000 | H2_single_remote_worker | S2         |                   10.860000 |  1.380000 |   0.145570 |        0.730769 |
| configured_D3_fallback        |       1.500000 | H1_single_commuter      | S0         |                    8.920000 |  0.000000 |   0.000000 |        0.846561 |
| configured_D3_fallback        |       1.500000 | H1_single_commuter      | S2         |                   10.100000 |  1.180000 |   0.132287 |        1.000000 |
| configured_D3_fallback        |       1.500000 | H2_single_remote_worker | S0         |                    8.840000 |  0.000000 |   0.000000 |        0.807692 |
| configured_D3_fallback        |       1.500000 | H2_single_remote_worker | S2         |                    8.320000 | -0.520000 |  -0.058824 |        1.000000 |
| paper_envelope_catalogue_only |       1.333333 | H1_single_commuter      | S0         |                    7.600000 |  0.000000 |   0.000000 |        1.000000 |
| paper_envelope_catalogue_only |       1.333333 | H1_single_commuter      | S2         |                    7.600000 |  0.000000 |   0.000000 |        1.000000 |
| paper_envelope_catalogue_only |       1.333333 | H2_single_remote_worker | S0         |                    7.600000 |  0.000000 |   0.000000 |        1.000000 |
| paper_envelope_catalogue_only |       1.333333 | H2_single_remote_worker | S2         |                    7.600000 |  0.000000 |   0.000000 |        1.000000 |

## R2: generalization of the body-only measure

| population   | household               |   n_units |   median_gain_m2 |   median_gain_rel |   share_negative |   share_zero |   share_below_reported_band |   share_near_reported_gain |   share_above_reported_band |
|:-------------|:------------------------|----------:|-----------------:|------------------:|-----------------:|-------------:|----------------------------:|---------------------------:|----------------------------:|
| real_plans   | H1_single_commuter      |      2109 |         0.000000 |          0.000000 |         0.031769 |     0.927454 |                    1.000000 |                   0.000000 |                    0.000000 |
| real_plans   | H2_single_remote_worker |      2109 |         0.000000 |          0.000000 |         0.025130 |     0.906591 |                    1.000000 |                   0.000000 |                    0.000000 |
| D3           | H1_single_commuter      |       510 |         0.000000 |          0.000000 |         0.178431 |     0.762745 |                    1.000000 |                   0.000000 |                    0.000000 |
| D3           | H2_single_remote_worker |       510 |         0.000000 |          0.000000 |         0.139216 |     0.654902 |                    1.000000 |                   0.000000 |                    0.000000 |

Near the reported approximate 60% means the descriptive predeclared 55–65% band, not source uncertainty. Area-bin summaries and associations with NIA, aspect ratio and compactness are included in the CSVs. Main objectives optimize functional service and transformation burden; daytime open space is not maximized, and beds are not forced to fold to reproduce the source ratio.

## R3 and interpretation boundaries

Bridge.csv uses the accepted P1 paired equivalent-area definition. Real plans use the real-plan reference and D3 uses D3; pooled-reference inversion is a separate sensitivity. Identified relative area gains and lower bounds are separate columns. Correlations exclude bound-only rows; triangles in F11 mark lower bounds, not exact estimates. Relative equivalent-area gain divides by NIA, while relative daytime body-free area gain divides by S0 body-free area: these are different denominators and concepts.

The primary daytime measure is continuous NIA minus the union of outward-rounded raster furniture bodies in the normal/day slot. It includes fixed-service space within NIA, does not deduct clearances and does not assert that all remaining area is accessible. Secondary furnishable-only and clearance-subtracted raster area fields preserve that distinction. R1 D3 fallbacks include kitchen/toilet pods unlike the bedroom; the known-bedroom envelope still uses our catalogue and schedules, so it is also approximate. No dimensions or search parameters were tuned to match the paper.

## Verification and next work

PASS: source checksum and numeric page references, full B/D/P1 prerequisite chain, corrected F1 membership, original H1/H2 layout hashes/configurations, every independent saved-layout score, no missing/duplicate paired records, and identified/bound separation. Visual review remains a distinct package gate. See Q32 for the source ambiguity. Next: prespecified ablations, C, reduced K, HK and literature screening before G3.

Reproduce: PYTHONPATH=src:scripts python scripts/09_run_expR.py; after actual figure review, add config/expR_visual_review.json and run --finalize.
