# Instructions for Gemini (manuscript writer)

You are drafting the manuscript of this research project for **iScience** (Cell Press). The computations are finished and reviewed (gates G1–G4). Your job is to write the paper, not to run or change experiments.

## Read first, in this order

1. `docs/PAPER_STORY.md`: the story, outline, terminology, claims to avoid, and the evidence map. This is your brief.
2. `docs/WRITING_GUIDE.md`: how to write (story first, one message per paragraph, flow, self-review).
3. `reports/FINAL_SUMMARY.md`, `manuscript/draft_results.md` and `manuscript/draft_methods.md`: evidence-linked notes with the verified numbers.
4. `results/tables/g4/T1.md`–`T7.md` and the figures in `results/figures/g4/`.
5. `AGENTS.md`: the repository rules. The integrity rules apply to you too.

## Rules

- **Numbers:** every number must come from a committed file listed in `docs/PAPER_STORY.md` §8 or in the drafts above. If a number you need is missing, write `[NEEDS EVIDENCE: …]`. Never compute, estimate or round differently from the source.
- **References:** if `paper/references.bib` exists, cite only from it. Until then, use only `docs/RESEARCH_PLAN.md` §10 and the records in `reports/novelty_check.md`, and write `[CITE: what is needed]` for anything else. Never invent references, DOIs or page numbers. The verified list is being consolidated separately (`docs/REFERENCES_TASK.md`, about 40 references); do not add more.
- **Claims:** no "first", "novel" or "unprecedented". Follow `docs/PAPER_STORY.md` §7.
- **Terminology:** use the table in `docs/PAPER_STORY.md` §6 exactly.
- **Do not edit** `reviews/`, `results/`, `config/`, `src/`, `scripts/` or `docs/` (except to add notes in `paper/NOTES_FROM_WRITER.md`).
- **Language:** American English, plain and precise.

## What to produce (draft v1)

Create `paper/manuscript.md` with these sections:

- Title (give 2–3 options)
- Summary (~150 words)
- Highlights (3–4, ≤85 characters)
- eTOC blurb
- Introduction
- Results (claim-style subsection headings, figure and table callouts)
- Discussion, including "Limitations of the study"
- STAR Methods (Key resources table as a Markdown table; Resource availability; Method details; Quantification and statistical analysis)
- Figure legends, for Figures 1–6 and the supplementary figures

Also create:

- `paper/claims_map.md`: one line per claim in the Summary, Introduction and Discussion: `Claim | Evidence file | Status (supported / needs evidence / weakened)`.
- `paper/self_review.md`: the five-dimension self-review from `docs/WRITING_GUIDE.md` §9, answered, with any unresolved items.

Write in stages and commit after each: Introduction + Results → Discussion → STAR Methods → Summary, Highlights, title.

## Branch and review

- Work on branch `gemini/paper-draft-v1`, push it, and open a pull request against `main`. **Do not merge.**
- Claude reviews the PR. It is merged if it passes; otherwise you get a review file in `reviews/` and a PR comment.
- At the start of each session, `git pull` and check `reviews/` for feedback on your PR.
