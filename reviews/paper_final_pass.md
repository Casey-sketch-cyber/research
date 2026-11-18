# Final text pass (draft v4)

**For:** Gemini, branch `gemini/paper-draft-v4`, PR against `main`. **From:** Claude, 2026-11-18.

Figures are final. Figure 1 and the graphical abstract are done (`reviews/ga_v5_review.md`). **Do not edit anything under `paper/figures/`.** This pass changes text in `paper/manuscript.md` only. Do not change any number.

## 1. Replace the Figure 1 legend [must]

The current legend is about 330 words. It contains a repository path, ``(`paper/figures/fig1/Figure1.pdf`)``, and code-formatted symbols. Replace the whole Figure 1 legend with the text below. You may polish the wording, but keep it at or under about 150 words and keep the facts.

> **Figure 1. A schedule-aware, verified framework for translating furniture into floor area**
> (A) Inputs: 2,619 compact homes (8–50 m² net internal area, NIA), four household schedules, and a furniture library of static and two-state transformable items (⇄).
> (B) The same 18 m² home for a couple under three strategies across night, workday and dinner slots: static (S0), form only (S1) and form + time (S2). In S2, the double wall bed is deployed at night and stowed (hatched) by day.
> (C) A constraint-programming optimizer (CP-SAT) finds the best layout for each strategy. An independent validator checks non-overlap, free clearances and walkable access of at least 0.6 m. The result is 31,428 verified layouts.
> (D) The functional capacity index (FCI) is the share of scheduled activity-hours a layout serves. Mapping a home's S0 and S2 scores onto the static reference curve gives its equivalent-area gain (ΔEA). The capacity gain splits into form (S1 − S0) and time (S2 − S1) effects.

Notes:
- The figure shows three of the six schedule slots (night, workday, dinner). The legend says so implicitly by naming them. Do not write "six" there.
- Definitions (A_min, support bounds, anchors) stay in STAR Methods.

## 2. Add a graphical abstract note [must]

The graphical abstract's "+3.5 m²" is the identified ΔEA of the same 18 m² couple home. The source is `results/expA_f1/analysis_p1/paired_equivalent_area.csv`: `unit_key D3:93a7c03b42e4b87306d4`, H3, `median_bin_cummax`, D3 reference, `delta_ea_m2 = 3.481462`.

- If the manuscript has a graphical-abstract section or note, state it there. Otherwise, add one sentence to `paper/NOTES_FROM_WRITER.md`, so that the number is traceable.
- In Results §1 or in the Figure 2 legend, where this home is introduced, you may add "(ΔEA = 3.48 m²)". Do this only if it reads naturally.

## 3. Final consistency checks [must]

1. **Title.** The author chose *Translating furniture into floor area shows where compact homes gain space* (already set in line 1). Keep the old options below it, labelled "not used". Make sure the Summary's first sentence and the keywords still contain "transformable furniture".
2. **Code formatting.** Remove backticks and repository paths from every figure and table legend and from the main text. Paths belong only in STAR Methods (data and code availability) or the supplement.
3. **Terminology** (PAPER_STORY §6) across the whole manuscript: FCI, S0/S1/S2 names, ΔEA, A_min, NIA, and the household names.
4. **References.** Every in-text citation appears in the reference list and the other way round (30 entries).
5. **Word count.** Summary ≤ 150 words; Highlights ≤ 85 characters each; main text ≤ about 4,800 words.

Update `paper/claims_map.md` and `paper/self_review.md` if anything changes, and list your edits in the PR description.
