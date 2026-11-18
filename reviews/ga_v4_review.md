# Graphical abstract v4 review (PR #14)

**Reviewer:** Claude, 2026-11-18. **Verdict: APPROVED, merged.** The redesign works:

- the concrete +3.5 m² replaces the abstract curve;
- the hierarchy is clear;
- the canvas is filled;
- the number matches `paired_equivalent_area.csv` (3.481462 m², identified).

Make one last small PR (`codex/paper-ga-v5`) with these fixes. Item 1 is about accuracy.

1. **Meaning of the number [must].** ΔEA compares S2 with **static** furniture (S0). It includes both changing form and switching over time. As drawn, "Switching furniture" + "equivalent floor area in this home" suggests switching alone.
   - Change the middle header to "With transformable furniture".
   - Change the subline to "equivalent floor area gained vs static furniture".
   - Keep the ⇄ badge on the left: it shows how this home uses the furniture.
2. **Duplicate icon.** The ruler is both the big middle icon and the icon of the "Floor area alone misjudges function" card. Give that card a different Tabler icon, e.g. `scale` (balance) or `alert-triangle`. Record it in `ICON_CREDITS.md`.
3. **Card alignment.** In the second card the text sits at the bottom, far from its icon; in the first card it is centred. Use the same vertical layout in both cards: icon, then text right under it, with the block centred.
4. **Font sizes.**
   - The subline under +3.5 m² uses a condensed face and is below the 40 px minimum. Use Arial at ≥40 px.
   - The text in the finding cards is also below 40 px. Raise it to ~40 px; the cards have room.
