# Paper round 3 review: Figure 1 v3, graphical abstract, draft v3

**Reviewer:** Claude, 2026-11-18.

**Packages:**
- PR #12 (`codex/paper-fig1-v3`, e35df82)
- PR #13 (`gemini/paper-draft-v3`, e8724ca)

**Verdict:** both merged. Figure 1 is final. Draft v3 is accepted, with one legend fix. **The graphical abstract needs a redesign** (GA v4, below).

## Figure 1 v3: APPROVED (final)

The Panel D axes are now labelled ("FCI", "Area (m²)"). Nothing else to change.

## Draft v3: APPROVED

- The reference list is regenerated from `paper/references.bib`: 30 entries cited, with no `[CITE:]` or `[NEEDS EVIDENCE]` left.
- The main-text numbers are unchanged from v2. I diffed every decimal; the only differences are inside the arXiv DOI string.
- The new references are placed as requested.

**Fix in the next text pass:**
- The Figure 1 legend contains a repository path, ``(`paper/figures/fig1/Figure1.pdf`)``, and code-formatted symbols (`` `⇄ Switch` ``, `` `CP-SAT` ``, `` `✗` ``). Remove the path. Write the symbols as plain text.
- At about 330 words, the legend is long. Shorten panel A to the inputs and their counts, and keep the definitions in STAR Methods.

## Graphical abstract: redesign (GA v4, Codex, branch `codex/paper-ga-v4`)

**Why the current version does not work:**

1. **Inverted text hierarchy.** The axis labels ("Function served ↑", "Floor area →") are smaller and greyer than the in-plot labels ("Static", "Switched", "Static reference"). "Function served" also sits inside the plot area.
2. **The middle chart is abstract.** A step curve with two dots and dashed projections needs the Methods to decode. A graphical abstract must be understood in about five seconds by a non-specialist.
3. **Weak composition.** The chart is small, and the bottom ~20% of the canvas is empty.

**New design:** keep the three columns, replace the chart with a concrete statement, and fill the square.

| Column | Header | Content |
|---|---|---|
| Left | "Same 18 m² home" | The existing Night / Workday plan pair with the ⇄ badge. Enlarge the plans ~1.3×. |
| Middle | "Switching furniture" | One big number, **"+3.5 m²"**, in the accent green (largest text after the title). Below it, one line: "equivalent floor area in this home". Add a ruler icon or a simple outline of a slightly larger square behind the number. **No axes and no curve.** |
| Right | "Across 2,619 homes" | The two finding cards with shorter text: "Gains concentrate in mid-sized two-person homes" and "Floor area alone misjudges function". Use larger icons. |

**Source of the number:** `results/expA_f1/analysis_p1/paired_equivalent_area.csv`, with:
- `unit_key = D3:93a7c03b42e4b87306d4`
- household H3
- `method = median_bin_cummax`
- `pooling = reference_pooling = D3`

That row gives `delta_ea_m2 = 3.481462` (identified), shown rounded as "+3.5 m²". This is the same 18 m² home as Figure 1 Panel B. Record the source in the PPTX notes.

**Typography.** Exactly three text sizes at the 1,650 px canvas:
- title ≈ 64 px bold;
- column headers ≈ 48 px bold;
- everything else ≈ 40 px, regular or bold.

The big number may be ≈ 120 px. No text smaller than 40 px. One ink colour plus the accent green.

**Layout:**
- Content fills the canvas, vertically centred, with an even margin of about 60 px.
- The columns are equal width, and the arrows between them sit at the same height.

**Keep:** the title "When does transformable furniture save floor area?", the colours and the icons.

Export the PPTX, PDF and PNG (1,650 × 1,650 px) and update `ICON_CREDITS.md` if icons change.
