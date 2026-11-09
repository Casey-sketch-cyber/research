# Phase 7 — A1/A2 follow-up review

Review: [phase07_review_A1A2](../reviews/phase07_review_A1A2.md), b3d1a71, 2026-11-09. The author instructs implementation. This re-solve requirement supersedes the previous no-re-solve instruction. No further intermediate reviewer stop is required before G3.

- [x] F1: verify that the only main configuration change is single_bed=2 and wall_bed_single=2.
- [x] Verify H1/H2 candidate-table equality and unchanged primary FCI upper bounds on all 2619 evaluable units (15714 household/strategy checks). Preserve actual old configuration hashes when reusing results.
- [x] Start isolated H3/H4 × S0/S1/S2 re-solves on every evaluable unit with frozen production settings and independently revalidated original warm starts.
- [ ] Complete all 15714 re-solves, validate them and join unchanged H1/H2 rows with explicit provenance.
- [x] Implement and test F2 paired inverse-area gain: median-per-2-m²-bin cumulative-maximum reference, mean-isotonic sensitivity, support flags and censoring bounds.
- [x] Queue guarded numerical F2 analysis after accepted F1; use 1000 paired unit resamples, refitting both references in each draw.
- [ ] Finish F2 numerical analysis, actual figure inspection and corrected H3/H4 layout showcases.
- [ ] F3: implement and test mirrored left/right access with shared family limits; re-run the same 348 small units for H3 only (1044 cases).
- [ ] Continue B on the frozen 200-pair sample using corrected H3/H4 evidence, then D/R/ablations, C, H1+H3 K, HK, literature and G3.

## Observed execution state

F1 started at 2026-11-09T08:43:36+00:00. The saved snapshot at 2026-11-09T08:55:37+00:00 records 18/15714 completed cases in the small-home group. This is a dated snapshot, not a completed experiment. Results and isolated cache provenance are in results/expA_f1/. F2 continuation is waiting for this exact F1 input set. A failed or replaced F1 stops continuation.

H1/H2 verification found zero candidate-table or primary-bound differences. The proof also checks that their single sleep_1 demand occurs only at night; extra single beds cannot satisfy another demand. Instance counts and the scalar weights of secondary objectives may change, so this is not a claim of identical models or search traces.

Small homes retain 120 seconds, four solver workers and three concurrent jobs, with 0.10 m anchors; larger homes retain 30 seconds, one worker and fourteen concurrent jobs, with 0.20 m anchors. Every H3/H4 case invokes the unchanged solver. An original layout is used only after validation under the new caps; the new result cannot discard that valid FCI incumbent. There is no geometry repair, sample reduction or solve-budget reduction.

## F2 interpretation and checks

Both scores are inverted on the same source/household reference. Equal scores identify zero gain even if the individual inverses are unsupported. An unsupported S2 inverse with supported S0 gives a difference lower bound; two unequal unsupported scores give an unidentified nonnegative gain. Such cases are not relabelled as exact zero. Below-support values use the first observed bin midpoint and remain explicitly flagged. See Q27.

Tables separate the share already fully functional under S0, the share whose FCI improves, the share with known positive area gain, right censoring, the median among positive uncensored gains, and median identification bounds among FCI-improved units. The conditional median is not an unconditional median for censored gainers. References cover pooled, real-plan, D1, D2 and D3 evidence separately.

Mean paired FCI differences, bootstrap confidence intervals and improvement shares are the primary statistics. Wilcoxon and rank-biserial statistics remain supplementary because nonnegative ordering holds by construction. Adequate-area estimates retain unsupported and one-class flags; single-person real-plan nonidentification is reported explicitly, alongside source-labelled D3 and pooled fits. F2 numerical completion alone will not mark figures or corrected layout examples reviewed.

Related regression checks: 18 passed (F1 configuration/case gates, E1 membership, paired-area boundaries, paired analysis and reuse provenance). F1 and F2 driver dry runs passed. No corrected empirical F2 result is claimed yet.

## Superseded evidence and limitations

Original A, A1 and fixed-left A2 remain immutable historical evidence. H3/H4 outcomes from those runs are superseded pending corrected results. The old FEA-minus-own-area saving definition is retired for every household. H1/H2 original scores remain reusable only through the compatibility gate. E1/E2/E3 selection evidence and the B sample stay unchanged. Historical reports retain their original text and hashes; read this report and the current README for their present status.

The E2 audit found 8 of 20 sampled excluded units recoverable at 0.05 m. At 0.10 m, oblique kitchen openings are disproportionately lost. This is a limitation of the fixed raster and selection rule, not grounds for outcome-driven geometry repair.

The numerical solver and validator remain frozen during F1. F3 work must not alter the active F1 execution copy. The duplicated D-40 records are distinguished by date and scope: 2026-11-07 runtime reporting versus 2026-11-09 bed-count correction. Review files remain untouched.
