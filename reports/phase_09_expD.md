# Phase 9 — Conventional indicators and functional adequacy

Status: implementation tested and queued while B runs; numerical analysis is gated on accepted full B output. Three D tests pass (counts/missingness, tied cutoff sweeps, and geometry identity). No D numerical result is claimed before acceptance.

## Checklist

- [ ] Verify full B report acceptance and corrected F1 evidence.
- [ ] Join NIA and habitable-room counts to all 2619 evaluable units × four households.
- [ ] Report Spearman correlations with S0/S2 and FCI IQR within 2 m² bins, separately for real plans, generated shells and each source.
- [ ] Report binary confusion matrices for the configured Ulrich household-size thresholds and 8 m² area threshold at all configured FCI adequacy thresholds.
- [ ] For area/person and rooms/person, report complete observed-threshold sweeps at the primary FCI threshold, with no selected optimal cutoff or invented regulatory standard.
- [ ] Verify counts, ties, missingness and input/output hashes; publish script-generated results.

## Scope and interpretation

No new solve is needed. This measures agreement with model-based functional adequacy, not a legal determination of housing compliance. The plan supplies numerical cutoffs for Ulrich and the 8 m² comparison, but none for area/person or rooms/person. These two remain continuous indicators with explicit exploratory threshold sweeps. Every unique observed value is a cutoff, with adequate predicted at or above it; an additional above-maximum endpoint predicts no positives. No outcome-optimized cutoff is selected. Rooms are the harmonized count of furnishable/habitable spaces, not a bedroom-only or jurisdiction-specific census count.

All corrected F1 units remain, including valid zero scores. D1+D2 and D3 are distinguished. No new threshold is added to the frozen project configuration. See Q31.
