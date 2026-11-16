# Paper round 2 review: references, Figure 1, draft v2

**Reviewer:** Claude, 2026-11-16.

**Packages:**
- PR #8 (`codex/paper-refs`, f2d42cb)
- PR #9 (`codex/paper-fig1`, cf6145c)
- PR #10 (`gemini/paper-draft-v2`, f970fdf)

All three are merged. Two follow-ups remain: **Figure 1 v2** (declutter, Codex) and **draft v3** (references and legends, Gemini).

## PR #8 references: APPROVED

- 32 entries, each with its verification source recorded.
- I spot-checked five DOIs or records independently against Crossref and doi.org, and all matched:
  - Co-Layout: AAAI 40(17), 2026.
  - Mustafa & Ali: Sulaimani J. Eng. Sci. 9(2) 23–37.
  - HomeWorld: LNCS ECCV 2026.
  - CP-SAT-LP: Perron, Didier & Gay, LIPIcs CP 2023.
  - Ulrich: *Buildings* 15(15) 2623.
- The Ulrich DOI `10.3390/buildings15152623` is correct. I had also checked it against the article page during G4 polish.
- Minor: the `.bib` lists the Sulaimani authors with the family name "Qaradaghi", while Crossref lists "Chinaz Mustafa, Amjad Ali". Use the Crossref form in the manuscript so citation matching works (`Mustafa and Ali, 2022`).

## PR #10 draft v2: APPROVED

- Every v1 [must] and [should] item is addressed.
- I re-checked the new sensitivity numbers against `results/ablations/summary.csv`:
  - clearance −0.015989 → "−0.0160";
  - solver cap −0.010238 → "−0.0102".
- The main text is now 4,480 words; the Hong Kong kit paragraph is split; Table S4 is added; the surrogate material is reduced to one sentence.

## PR #9 Figure 1 and graphical abstract: APPROVED as v1; declutter in v2

- The science is right. Codex correctly fixed an error in my drawing brief (Q36): the ΔEA bracket must run between the inverses of the same home's S0 and S2 scores, not from the home's own area. Thanks.
- Panel B uses the verified layouts, the colours match the data figures, and the accent marks the three novel elements.
- **But the figure carries too much text.** Peng's template says the pipeline figure exists to make the novelty stand out, while the Methods text does the explaining (WRITING_GUIDE §6). Right now the panels read as paragraphs, and the 3 × 3 plans, which are the core idea, are small. This comes from my brief, which asked for too many labels. The v2 below fixes it.

## Figure 1 v2 (Codex, branch `codex/paper-fig1-v2`)

**Target:** at most about 40 words in the whole figure. No sentences; labels of 1–3 words. Whatever is removed is already in Table 1, the Methods or the legend.

1. **Delete Panel E** ("What we learn"). Findings belong in the Results, not in the pipeline. Re-letter the panels A–D.
2. **Make Panel B the hero** at about 45% of the width. Enlarge the nine plans by about 1.5×.
   - Keep only the column headers (moon, sun and plate icons plus "Night / Workday / Dinner") and the row labels "S0 Static", "S1 Form", "S2 Form + time".
   - Delete "Arrange for each strategy" and the two-line caption under the grid.
   - Keep the "⇄ Switch" badge.
   - Make the S2 change unmistakable: add a thin green outline around the wall bed in the S2 Night cell and around its stowed (hatched) footprint in the S2 Workday cell.
3. **Panel A (Inputs):** icons and thumbnails only.
   - Homes: the two plan thumbnails and one label, "2,619 plans". Delete the dataset names and the NIA line.
   - Households: the four person icons in a row, with no names, and the schedule bar with its three icons. Delete "Daily schedule (sketch)".
   - Furniture: the static icon row and the three transformable state pairs, as colour chips with ⇄, without item names. Delete "Bodies, clearances and reachable access".
4. **Panel C (Verified optimisation):**
   - "Optimiser" with its icon, subtitle "CP-SAT" only.
   - Validator: keep the shield and three short checks: "No overlap", "Clearances", "Access ≥ 0.6 m".
   - Replace "Reject and re-solve" with the loop arrow and a small ✗ icon.
   - Keep "31,428 verified layouts" as a single line, without the multiplication line.
5. **Panel D (Function → area):**
   - FCI as "served / scheduled activity-hours" (keep the fraction).
   - The curve with the S0 and S2 points and the ΔEA bracket.
   - The decomposition bar labelled only "Form" and "Time".
   - Delete "Verified scores", "Adequate if FCI ≥ 0.95" and the A_min text; these are defined in Methods.
6. **Typography:**
   - Panel titles 8 pt bold, labels 7 pt, nothing below 6.5 pt.
   - At most two text colours (ink and muted) plus the strategy colours.
7. **Graphical abstract:** change the title to match the paper's conditional message, e.g. "When does transformable furniture save floor area?". Change "in the model" to "in our model". Everything else stays.
8. Re-export the PPTX, PDF and PNG and update `ICON_CREDITS.md` if icons change.

## Draft v3 (Gemini, branch `gemini/paper-draft-v3`, after Figure 1 v2 merges)

1. **Regenerate the reference list from `paper/references.bib` only.** Fix the truncated DOIs this way, and remove `[CITE: verify …]` for Ulrich, Bu & Che Mat, Elmurodov & Mametova and Xiong et al. (2021; the `.bib` has the published year).
2. **Use the new entries where they fit:**
   - `perron2023cpsat` for CP-SAT;
   - `standfest2022swiss` for Swiss Dwellings;
   - `fu2024magic`, `li2026homeworld` and `nieciecki2026comfortable` in Introduction P3 (computational layout context).

   Do not add references beyond the `.bib`. For PyTorch, LightGBM, scikit-learn and GraphSAGE, list versions and URLs in the Key resources table without bibliography entries; the author capped the list at about 40.
3. Use "Mustafa and Ali (2022)" as Crossref lists it.
4. Rewrite the **Figure 1 legend** to match Figure 1 v2: four panels A–D, with the definitions moved from the figure into the legend.
5. Keep everything else. Do not change numbers.
