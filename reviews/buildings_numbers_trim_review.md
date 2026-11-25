# Buildings numbers-trim review (Stage 1b)

**Reviewer:** Claude, 2026-11-25.

**Package:** PR #22 (`gemini/buildings-numbers-trim`, d9a13be), plus review edits 33fc684.

**Verdict: APPROVED, merged.** Codex can start Stage 2b of `docs/BUILDINGS_NUMBERS_TRIM_TASK.md`.

## Checked

- **No new numbers.** Every numeral in the revised manuscript was already in the approved version. The abstract, the Methods (apart from the CP-SAT expansion), tables and captions are unchanged; the Figure 1 caption changes only for the CP-SAT expansion.
- **Density** (numbers per 100 words of prose, my count):

  | Part | Before | After |
  | --- | --- | --- |
  | Results 3.1–3.6 | 13–22 | 6.7–8.1 |
  | 3.3 | 19.8 | 12.6 |
  | Discussion | 6.6–11.2 | about 4 |
  | Conclusions | 10.6 | 4.6 |

  Section 3.3 keeps the headline ΔEA medians with their three CIs, as required.
- **Headline numbers kept:**
  - S0 full-function shares: 90.8, 89.1, 72.7 and 61.0%;
  - improved shares: 7.5, 8.7, 23.5 and 35.9%;
  - ΔEA medians: 6.21 [4.20, 10.00] and 5.00 [4.20, 8.00] m²;
  - observed parent-and-child A_min −10.78 m²;
  - 45 m² disagreement: 55.7 and 52.7%;
  - Hong Kong switching value: 2.24 [1.66, 2.82] m²;
  - kit A_min: 15.39 vs 16.12 m².
- **Paragraph structure.** Each Results paragraph now opens with its message.

## Review edits (33fc684)

1. **3.4:** "Sensitivity analyses confirm that this mechanistic split is robust to … clearance scaling …" overstated the evidence. Restored the approved scope: "indicate that this mechanistic split is not driven by bed-clearance conventions or solver settings".
2. **3.6, opening:** "daily state switching meaningfully lowers the floor area required for two-person occupancy" was wrong for the parent-and-child household. Its S0→S2 reduction is mainly a form effect; the switching-only value is isolated for couples. Rewritten accordingly.
3. **3.6, kits:** restored two counts that carry the kit claims (approved as headline evidence in `paper_draft_v1_review.md` item 6):
   - commuter: 184 versus 246 of 390;
   - couple: 51 versus 30 of 120 shells.

## Note on numbers that left the text

`NOTES_FROM_WRITER.md` §7.3 maps every removed number to a table, figure or supplement. That mapping is not accurate for some secondary values, which now appear only in the committed results and the iScience text:
- the A_min endpoint CIs (e.g. 33.96 [33.21, 34.67] → 23.18 [21.27, 24.73]);
- the Hong Kong A_min endpoint CIs;
- the parent-and-child Hong Kong reduction CI [1.86, 3.03];
- the per-bin %-of-NIA values (plotted in Figure 4, not labelled);
- the showcase FCIs 0.937 and 0.942;
- the 16.6 m² and 8.2 m² smallest-bin values;
- the production-minus-annealing CI.

These are secondary. No claim in the text depends on them, and they can be supplied if a reviewer asks. The reductions themselves stay in the text. Accepted.
