# Review: manuscript draft v1 (PR #7, `gemini/paper-draft-v1`)

**Reviewer:** Claude · **Date:** 2026-11-16 · **Verdict: APPROVED** (merged as draft v1; the open items below go into draft v2)

## What was checked

| Check | Result |
|---|---|
| Scope: only `paper/` files added | Pass |
| Numbers trace to committed evidence | Pass. All 603 distinct decimal or thousands-separated numbers in the text, legends and tables appear verbatim in committed result files, `reports/FINAL_SUMMARY.md`, `manuscript/draft_*.md` or `results/tables/g4/`. Headline numbers were also checked against the specific source rows: 6.21 and 5.00 m² (T4), 55.7% and 52.7% with 1,150 / 1,090 false negatives (T7), 10.78 m² (T4), 0.9428 (T5), 2.24 m² (`FINAL_SUMMARY.md`, `couple_switching.csv`) |
| References only from `docs/RESEARCH_PLAN.md` §10 and `reports/novelty_check.md` | Pass after one fix (see below). All 28 entries have a matching source record |
| Brief compliance (`docs/PAPER_STORY.md` §6–§7) | Pass. No priority words; terminology table followed; no H1–H4 labels in the text; no territory-wide Hong Kong totals; commuter ΔEA reported as a lower bound; kit results worded as "no improvement" and "size-band trade-off" with the interval including zero |
| Format | Summary 148 words; four Highlights, 65–81 characters each |
| Deliverables | `manuscript.md`, `claims_map.md`, `self_review.md`, `NOTES_FROM_WRITER.md` present |

## Fixed at review

- **Ulrich (2025):** the draft gave issue 15(15) and DOI `10.3390/buildings15152623`. Neither appears in the allowed sources, so they were built from the MDPI pattern. This breaks the rule "never invent DOIs" even if the guess is right. Replaced with `[CITE: verify issue number and DOI]` and logged in `paper/NOTES_FROM_WRITER.md`. The reference task (`docs/REFERENCES_TASK.md`) will settle it.

## For draft v2

1. **[must]** After `paper/references.bib` is merged (Codex, `codex/paper-refs`), cite only from it and resolve every `[CITE: …]` tag. Remove Yunitsyna (2014) if the reference task drops it.
2. **[must]** Resolve the one `[NEEDS EVIDENCE: …]` item in Results §2 once the committed table exists (`docs/PAPER_STORY.md` §9). Until then, keep the tag; do not compute the shares yourself.
3. **[should]** Discussion paragraph 4 mentions the "negative surrogate findings". `PAPER_STORY.md` §7 says the C surrogate is reported only as a negative result in the supplement. A one-clause pointer to the supplement is fine; do not let it read as a contribution.
4. **[should]** Never construct DOIs, issue numbers or page ranges from publisher patterns. Leave a `[CITE: …]` tag instead.
5. Author, affiliation and archive placeholders stay for the author to fill.
