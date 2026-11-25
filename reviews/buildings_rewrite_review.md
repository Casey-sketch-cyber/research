# Buildings rewrite review (Stage 1)

**Reviewer:** Claude, 2026-11-25.

**Package:** PR #20 (`gemini/buildings-rewrite`, e45bc40), plus review edits cb3a50f.

**Verdict: APPROVED, merged.** Codex can start Stage 2 (`docs/BUILDINGS_REWRITE_TASK.md`).

## What I checked

- **Numbers.** I extracted every numeral from `paper/buildings/manuscript.md`, `supplementary_legends.md` and `cover_letter.md`. Every one appears in the iScience text (`paper/manuscript.md` on `main`); the only new tokens are section numbers. Nothing is fabricated or re-rounded.
- **References.** 30 Pandoc keys are cited, all present in `paper/references.bib`. The two unused entries (`johanes2026adaptable`, `yunitsyna2014universal`) were also unused in the iScience version.
- **MDPI requirements.**
  - The abstract is 187 words in one paragraph, and there are 7 keywords.
  - Sections are in the order 1–5 and the back matter is in MDPI order.
  - The funder and grant number are exact. The AI declaration is verbatim in Acknowledgments. The code link is unchanged.
  - Figures 1–6, Tables 1–4, Figures S1–S7 and Tables S1–S4 are cited in order of first appearance.
- **Story and claims.** The Introduction opens from housing regulation and ends with RQ1–RQ3, the contributions and a roadmap. Methods now hold the definitions. Discussion 4.2 (implications) rests on the Results. The Limitations keep the scope framing. There are no "first" or "novel" claims.
- **Cover letter.** It argues fit with the section "Architectural Design, Urban Science, and Real Estate" and includes both required MDPI statements. It does not mention any special issue.

## Review edits (made directly, cb3a50f)

1. **Results 3.1, first paragraph.** It repeated the corpus counts from Section 2.2. I replaced it with three sentences that point back to Methods.
2. **4.1.** "strictly conditional" → "conditional" (same rule as `paper_draft_v1_review.md` item 10).
3. **Introduction P4.** "Yet none ties …" → "Yet none of these methods ties …", so the claim is limited to the cited work.
4. **4.2.** Calibrated three new evaluative phrases that went beyond the evidence:
   - "highest return" → "best targeted at" (as in the iScience text);
   - "high-leverage investments" → "matter most for this household";
   - "single highest-impact transformable piece" → stated as the drop-one test result it is.

## Notes for Stage 2 (Codex), not blocking

- **Length.** The main text is about 10,500 words without tables (Methods ~4,200, Results ~3,500). MDPI has no limit, so no cut is required.
- **Table 1, row D5 (ATUS, "omitted").** Carried over from the iScience version; leave it.
- **Cover letter date.** Set it on the submission day.
- **Title.** Stays as is unless the authors pick one of the alternatives in `NOTES_FROM_WRITER.md`.
