# Figure 1 (framework) and graphical abstract: drawing specification

**For:** Codex, drawing in PowerPoint. **Status:** v1, 2026-11-16, Claude.

Deliver on branch `codex/paper-fig1` and open a PR. Put everything under `paper/figures/fig1/`:

- `Figure1.pptx` (editable)
- `Figure1.pdf` (vector export)
- `Figure1.png` (600 dpi)
- `GraphicalAbstract.pptx`, `GraphicalAbstract.png`
- `assets/` (every image and icon used)
- `ICON_CREDITS.md` (source URL and license for each icon)

## Purpose

Following WRITING_GUIDE §6, the framework figure exists to **show what is new**, not to explain every step. The text explains.

The three novel elements must stand out:

1. **Time slots:** the household's day is split into slots, and furniture may change state between them (S2).
2. **Independent validator:** every layout is checked for overlap, clearance and walkable access.
3. **Equivalent area:** functional differences are translated into m².

Inputs and generic steps stay visually quiet (grey). The novel elements get the accent colour and a thicker outline.

## Global style

- **Size:** full page width, 174 mm wide, height about 100–115 mm. Set the PowerPoint slide to 17.4 × 11 cm. Check the current iScience figure guidelines before export.
- **Font:** Arial (or Helvetica). Panel letters A–E bold 9 pt; titles 8 pt bold; body 6.5–7 pt. Nothing smaller than 6 pt at final size.
- **Colours** (identical to the data figures):
  - Strategies: S0 static `#0072B2` (blue), S1 form only `#E69F00` (orange), S2 form + time `#009E73` (green).
  - Furniture functions: sleep `#4C78A8`, work `#F58518`, dine `#54A24B`, storage `#B279A2`, lounge `#72B7B2`, fixed services `#BDBDBD`.
  - Text ink `#203048`, muted `#536278`, grid and lines `#DCE4ED`, card fill `#F1F5F9`.
  - Accent for novel elements: `#009E73` outline, 1.5 pt.
- **Shapes:** rounded rectangles (radius ~1.5 mm), 0.75 pt outlines, arrows 0.75 pt in `#536278` with small heads.
- **Sharing:** no photographs of people, no logos, no brand names, nothing on the canvas except our own drawings, the icons below and our own plan drawings and renders.

## Layout: five panels, left to right

```
┌────────────┬──────────────────────────────┬──────────────┬──────────────┬────────────┐
│ A Inputs   │ B Three furniture strategies │ C Verified   │ D From       │ E What we  │
│ (grey)     │   over a day (ACCENT)        │ optimisation │ function to  │ learn      │
│            │                              │ (ACCENT on   │ floor area   │ (grey)     │
│ Homes      │      Night  Workday  Dinner  │  validator)  │ (ACCENT)     │            │
│ Households │  S0  [plan] [plan]   [plan]  │              │              │ 3 question │
│ Furniture  │  S1  [plan] [plan]   [plan]  │ optimiser →  │ FCI formula  │ cards with │
│            │  S2  [plan] [plan]   [plan]  │ layout →     │ curve sketch │ mini plots │
│            │                              │ validator ✓✓✓│ ΔEA, A_min   │            │
└────────────┴──────────────────────────────┴──────────────┴──────────────┴────────────┘
   ~18%                 ~34%                     ~16%           ~18%          ~14%
```

### Panel A: Inputs (muted grey cards, stacked vertically)

1. **Homes** card.
   - Icon: floor-plan or house.
   - Two small plan thumbnails: one observed plan (the D1 29.97 m² showcase) and one generated shell (the D3 18.00 m² showcase).
   - Text: "2,109 observed plans (Swiss Dwellings, ResPlan) · 510 generated shells · Hong Kong model shells".
   - "Compact = 8–50 m² net internal area".
2. **Households** card.
   - Four small person icons labelled "single commuter", "single remote worker", "couple", "parent and child".
   - Under them, one schematic 24-hour bar: a horizontal bar split into coloured segments (sleep, work, dine, lounge) with moon, sun and plate icons above. Label it "daily activity schedule (schematic)". It does not need to match T3 exactly.
3. **Furniture** card.
   - Left: static icons (bed, desk, table, wardrobe).
   - Right: three transformable pieces, each drawn as two small states with a ⇄ arrow:
     - wall bed (down ⇄ up);
     - fold-down desk (open ⇄ folded);
     - drop-leaf table (open ⇄ closed).
   - Text: "bodies, clearances, reachable access".

### Panel B: Three furniture strategies over a day (main panel, accent)

A 3 × 3 grid of the **same home** (the D3 18.00 m² couple showcase, from row 2 of F3):

- Columns: Night, Workday, Dinner, with moon, sun and plate icons in the header.
- Rows:
  - **S0 Static** (blue row label): three identical plans.
  - **S1 Form only** (orange): transformable pieces in one state for the whole day.
  - **S2 Form + time** (green): state changes between slots. The wall bed is down at night and stowed (hatched) by day.
- Outline the S2 row in the accent green. Put a small "⇄ switch" badge between the Night and Workday cells of S2.
- Under the grid, one line: "Same home, same household: only the furniture strategy changes".

**Assets:** generate one clean plan image per cell from the saved layouts, rather than cropping F3:

- Use the plan colours and the hatched "stowed" style of F3, with no axes or titles, a transparent background, and SVG + PNG at 600 dpi. Save to `assets/plan_<strategy>_<slot>.svg`.
- Source: the D3 18.00 m² H3 showcase used in `results/figures/g4/F3.pdf` (find its key in `results/expA_f1/analysis/layout_selection.csv`; layouts are in `results/expA_f1/analysis/layouts/showcase/`). Use `src/fea/viz/` drawing helpers.
- *Optional inset* if space allows: one 3D still for S2 night and one for S2 workday, `results/renders3d/stills/showcase_18_S2_night.png` and `showcase_18_S2_day.png`, as small rounded thumbnails.

### Panel C: Verified optimisation (validator in accent)

A vertical flow:

1. Box "Optimiser (constraint programming)", gear or CPU icon, with the subtitle "best arrangement per strategy".
2. ↓ a small plan thumbnail (reuse one S2 cell).
3. Box **"Independent validator"** in accent, shield-with-check icon, with three check lines:
   - ✓ no overlapping furniture
   - ✓ clearances kept free
   - ✓ walkable access ≥ 0.6 m
4. A curved arrow from the validator back to the optimiser, labelled "rejects → re-solve".
5. Bottom note: "31,428 verified layouts (2,619 plans × 4 households × 3 strategies)".

### Panel D: From function to floor area (accent)

1. **FCI** formula box: "FCI = activity-hours served / activity-hours scheduled" (0–1).
2. **Curve sketch** (draw it; do not paste a data plot):
   - x-axis "net internal area (m²)", y-axis "FCI".
   - A rising blue step-like curve labelled "static homes (S0)".
   - Mark one home's S2 score as a green dot at its own area. Draw a horizontal dashed arrow from the dot to where the blue curve reaches that FCI, then a vertical drop to the x-axis.
   - Put a brace on the x-axis between the home's area and the dropped point, labelled **"equivalent-area gain ΔEA (m²)"**.
   - Add a horizontal dotted line at FCI = 0.95 labelled "adequate", with its crossing marked "A_min".
3. A small stacked bar: "S1 − S0 = form effect" (orange) + "S2 − S1 = time effect" (green).

### Panel E: What we learn (muted, three small cards)

Each card has an icon and a one-line question. Do not put numbers on these cards; the numbers belong in Results.

1. "Who gains, and at what size?" Mini thumbnail of `results/figures/g4/F5.png`, heavily simplified or just the icon.
2. "Does floor area predict function?" Ruler icon; mini thumbnail of F6.
3. "What does switching add in Hong Kong?" Mini thumbnail of F10.

Thumbnails are optional. If they look cluttered at this size, use icons only.

### Connectors

- A → B: one arrow ("arrange for each strategy").
- B ↔ C: B's plans feed C, and C returns verified plans.
- C → D: "verified scores".
- D → E.

Keep the arrows straight, with no crossings.

## Icons: sources and rules

Use only permissive icon sets that need no attribution in the figure. Download SVGs, recolour them in PowerPoint, and record each icon's set, name, URL and licence in `ICON_CREDITS.md`.

- **Tabler Icons** (MIT): https://tabler.io/icons
- **Lucide** (ISC): https://lucide.dev/icons
- **Phosphor Icons** (MIT): https://phosphoricons.com
- **Material Symbols** (Apache 2.0): https://fonts.google.com/icons

Suggested icons (verify the exact names on the site):

| Concept | Tabler / Lucide name ideas |
|---|---|
| home / plan | `home`, `layout-grid` / `house`, `layout-dashboard` |
| person / two persons / parent and child | `user`, `users`, `friends` / `user`, `users`, `baby` |
| bed | `bed`, `bed-flat` / `bed-double`, `bed-single` |
| desk / work | `desk`, `briefcase` / `lamp-desk`, `briefcase` |
| table / dining | `table`, `tools-kitchen-2` / `utensils` |
| wardrobe / storage | `box`, `archive` / `archive`, `package` |
| night / day / dinner | `moon`, `sun`, `tools-kitchen-2` / `moon`, `sun`, `utensils` |
| switch | `arrows-exchange` / `repeat`, `arrow-left-right` |
| optimiser | `settings`, `cpu` / `cog`, `cpu` |
| validator | `shield-check` / `shield-check` |
| ruler / area | `ruler-measure` / `ruler` |
| question | `help-circle` / `circle-help` |

If no suitable furniture icon exists, draw a simple top-view symbol: rectangles in the function colours, matching the plan drawings. That is preferable to a mismatched icon style. Use one icon set throughout.

## Graphical abstract (B)

iScience requires a graphical abstract. Check the current size rules; the Cell Press practice is a square, ≥1200 × 1200 px, with readable text and no panel letters.

Content, in a simple left-to-right story:

1. **Left:** one compact home plan (the S2 night and workday pair from Panel B) with a ⇄ switch badge. Caption: "Same home, furniture changes over the day".
2. **Middle:** the curve sketch from Panel D, simplified, with "equivalent floor area (m²)".
3. **Right:** two takeaway badges:
   - "Gains concentrate in two-person homes of mid size"
   - "Floor area alone misjudges function"
4. **Top:** the title line, matching the chosen paper title, short.

Use the same colours and icons as Figure 1.

## Acceptance checks (Codex self-check before the PR)

- [ ] Readable at 100% of 174 mm width; no text under 6 pt.
- [ ] S0/S1/S2 colours match the data figures exactly.
- [ ] The Panel B plans come from the saved validated layouts, not redrawn by hand.
- [ ] The three novel elements carry the accent; inputs are grey.
- [ ] Every icon is listed in `ICON_CREDITS.md` with a permissive licence.
- [ ] No numbers appear on the figure except the counts in Panels A and C, which must match T1 and T4.
- [ ] PDF export keeps vector text and shapes.
