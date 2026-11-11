# Phase 9b — Published-room comparison and generalization

Status: implementation tested and queued before R outputs; execution waits for accepted B and D. Five R tests pass, four pre-existing layouts pass an end-to-end read/independent-area check, and all four planned comparison envelopes have verified 12 m² area. These are preflight checks, not completed R results.

## Checklist

- [x] Read PDF pages 12–14 and Figure 10; verify source checksum and record numeric values with PDF page and section.
- [ ] R1: solve S0/S2 for H1/H2 on the three configured fallback shells and the known 4 × 3 m bedroom envelope; preserve original household/catalogue settings and label the approximation.
- [ ] R2: independently revalidate all saved H1/H2 S0/S2 layouts on the 2619 evaluable units, and calculate daytime body-free floor area.
- [ ] R3: join current P1 paired equivalent-area gains, preserving identified values and bounds separately; real units use real reference, D3 uses D3, plus pooled-reference sensitivity.
- [ ] Produce F11, inspect it, and verify result hashes before declaring the package complete.

## Source and metric boundary

The source is conceptual/analytical. Page 12 §6.1 specifies a 12 m², 4 × 3 m room, but its bed width and wardrobe depth differ from Figure 10 on page 13. Several furniture/clearance details remain unspecified. Table 2 on page 14 uses clearance-inclusive activity areas, while this plan defines the floor area not covered by furniture bodies. The reported values therefore cannot be treated as an exact validation target for our body-only measure. Preserve 5–5.5 m² versus about 8 m² and roughly 60% with this qualification.

R1 uses the allowed 12 m² D3 fallback with ratios 1/1.25/1.5, a short-wall corner entrance and opposite short-wall window. An additional 4 × 3 m empty-bedroom envelope checks the known room shape using our unchanged catalogue; it is not an exact reconstruction of their furniture. D3 fallback includes its usual kitchen/toilet services, unlike a bedroom. Our layouts optimize whole-day functional service and burden, not free daytime area; a wall bed is not forced to fold just to match the source. No parameters are tuned to its reported gain.

The independent area checker first requires a valid saved layout, then reconstructs each active normal/day furniture body from configuration. Primary body-free NIA is continuous NIA minus outward-rounded raster furniture-body union area. It does not deduct clearances, fixed-service space or require every counted cell to be reachable. A secondary raster-furnishable-free measure is also retained. This naming prevents either quantity being presented as measured usable activity space.

R2 near 60% means 55–65%, a declared descriptive band, not the source's confidence interval. Negative and zero gains remain. No new solves are needed for R2/R3. The original F1/A evidence is immutable; no solver module is imported by the activity checker.
