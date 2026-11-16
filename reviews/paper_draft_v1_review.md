# Manuscript draft v1 review

**Reviewer:** Claude, 2026-11-16. **Package:** PR #7 (`gemini/paper-draft-v1`, commit fb24e14): `paper/manuscript.md`, `claims_map.md`, `self_review.md`, `NOTES_FROM_WRITER.md`.

**Verdict: APPROVED AS DRAFT v1, merged.**

This is a strong first draft:

- The story follows `docs/PAPER_STORY.md`.
- The Introduction reasons from the gap to the root cause and then to the approach, without "first" or "novel" claims.
- The Results headings are claims.
- The Limitations are framed as scope, and the STAR Methods are complete enough to reproduce the work.

Revise the items below in **draft v2** on a new branch, `gemini/paper-draft-v2`.

## What I checked

- **All numbers in the Summary → Discussion.** I extracted 307 numerals and matched them against committed files. I then recomputed the high-risk ones directly:
  - S0 full-function shares per source (90.8/89.1/72.7/61.0%; D1, D2 and D3 splits): match `results/expA_f1/solutions.csv` and T4's "Full S0" column.
  - Area-cutoff confusion counts (S0 and S2; 940/52, 1,150/25, 789/66, 1,090/22): match `results/expD/confusion.csv`.
  - Hong Kong census counts: match `reports/phase_11_HK_results.md`.
  - Kit, HK and ablation figures: match `results/g3_review_k3/*` and `reports/phase_09_ablation_results.md`.

  No fabricated numbers were found.
- **STAR Methods.** The definitions of FCI, TB, ΔEA support cases, A_min, the validator, the bootstrap and the kit quality curves are correct and consistent with the code and the reviews.
- **Terminology and claims.** These follow PAPER_STORY §6–7.

## Required for v2 [must]

1. **Remove the `[NEEDS EVIDENCE]` tag in Results §2.** The full-function shares you cite are in T4 ("Full S0" column), which is your Table 3, so the claim is supported. Do not add adequacy shares or CIs unless a committed table provides them.
2. **Fix the misused citation.** Johanes et al. (2026) is about office fit-out layouts with CP-SAT and LLMs. It does not support "0.90 m wheelchair circulation". Remove the citation from that sentence; keep the sentence, citing our own sensitivity result (Figure S5).
3. **Fix an unsupported claim.** Results §4, "…preserved household rankings": no committed file states this. Either delete the phrase or replace it with what the ablation report states: the per-condition mean changes, with the drop-leaf table as the largest single-item reduction.
4. **Make the Weber et al. (2024) claim precise.** The paper reports that space efficiency beats envelope upgrades for a share of buildings that varies by city (see `reports/novelty_check.md` row 7). Write "for many buildings in the cities studied", not "across many urban building types".
5. **References.**
   - Several DOIs are truncated (Zeng et al.; Xiong et al. 2020; Mustafa & Ali).
   - Do not repair them by hand. After `codex/paper-refs` merges, regenerate the whole reference list from `paper/references.bib` only.
   - Drop Yunitsyna (2014) if it is not in the `.bib`; it is a repository copy.
6. **Split the Hong Kong kit paragraph** (Results §6, second paragraph, about 450 words of numbers). It breaks "one message per paragraph". Make two paragraphs:
   - (a) The commuter: no tested kit improves on standard dimensions. Give the HK adequate counts, 184 vs 246.
   - (b) The couple: the size-band trade-off. Give the training paired contrast and 5 vs 2; the HK A_min, 15.39 vs 16.12 m²; 51 vs 30 shells at 13–16 m²; and the loss below 13 m².

   Move the remaining detail to a new Supplementary Table S4, "Kit comparisons", and cite it: matched-search variants, held-out and observed-plan contrasts, bespoke capture, per-size counts.

## Recommended for v2 [should]

7. **Shorten the surrogate material in the Discussion.** Discussion P4 spends about 150 words on the GraphSAGE negative result. PAPER_STORY §7 places it in the supplement. Keep the transferability point and one sentence on the negative result, e.g. "geometry-only learned models did not reach the prespecified ranking criterion (Figure S4), so explicit search with validation remains necessary". Move the numbers to the Figure S4 legend.
8. **Lighten Results §1, P1.** Move the ABO counts (43,002 of 147,702) and the 94 zero-score layouts to STAR Methods. Keep in the main text the corpus, the households, the strategies and the 31,428 verified layouts.
9. **Introduction P2** (~330 words) carries four strands. Split it into two paragraphs:
   - (a) area rules and functional standards;
   - (b) transformable-furniture studies and computational layout methods.

   End (b) with the root-cause sentence.
10. **Word choice.** "Strictly conditional" → "conditional". "Confirming Özer and Jacoby's (2022)" → "consistent with". Prefer verbs with a calibrated strength.
11. **Main-text size.** About 4,800 words from Summary to Discussion is appropriate. Keep v2 at or below that.

## Not in scope for v2

- Figure 1 and the graphical abstract (Codex, `docs/FIGURE1_SPEC.md`).
- Author fields and the Zenodo DOI (the author).

## Addendum: second reviewer pass (Claude, 2026-11-16)

A second review session checked the same PR in parallel and briefly overwrote this file (commit a61e0d5); the text above is restored unchanged. Its findings that add to the list above:

- **Numbers:** an automated pass over the whole manuscript, including legends and tables, found all 603 distinct decimal or thousands-separated numbers verbatim in committed files. This agrees with the check above.
- **[must] Ulrich (2025):** the reference gives issue 15(15) and DOI `10.3390/buildings15152623`. Neither appears in `docs/RESEARCH_PLAN.md` §10 or `reports/novelty_check.md`; they were built from the MDPI pattern. Item 5 above (regenerate the list from `paper/references.bib`) fixes this. Until then, do not construct DOIs, issue numbers or page ranges from publisher patterns; leave a `[CITE: …]` tag.

A fix for the Ulrich entry was pushed to `gemini/paper-draft-v1` after the PR had already been merged, so it is **not** in `main`. Start v2 from `main` and ignore that later branch commit.
