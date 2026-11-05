# Open questions

Codex adds questions here between gates, each with the default assumption it is using in the meantime.

| # | Date | Phase | Question | Default assumption in use | Answer |
|---|---|---|---|---|---|
| Q-01 | 2026-11-05 | 00 | Author-led novelty check is absent. Has the requested search been completed? | Do not claim novelty has been established; engineering work can proceed. | Pending author/reviewer |
| Q-02 | 2026-11-05 | 02 planning | D3 specifies entrance/window positions but no opening widths. Which widths should be used? | Use the measured residential D1 opening-record medians, with counts and quantiles in `reports/schemas/D1_opening_dimensions.json`; report clipping if a shell wall is shorter. These are geometric spans, not verified accessibility clear widths. | Explicit data-derived default proposed for G1 |
| Q-03 | 2026-11-05 | 02 planning | The minimum furnishable area excludes the smallest gross-area D3 shells, but Phase 11 requires them. | Retain all generated shells with explicit inclusion flags; main-corpus filtering and later gross-area scenario selection are separate. No thresholds are silently changed. | Default documented for G1 |
| Q-04 | 2026-11-05 | 04 planning | Research Plan mentions scenario households of up to three people; the configured scenario household types cover one or two. | Use only the configured households and report the coverage limitation; do not create a new household without review. | Pending reviewer |
| Q-05 | 2026-11-05 | 10 planning | Research Plan describes mixed-source grouped splits, whereas PROCEDURES makes D2/D3 extra test sets. | Follow the stated precedence: D1 grouped split, D2/D3 external test sets. | Default from PROCEDURES |
| Q-06 | 2026-11-05 | 01 | ResPlan polygons use normalized source coordinates; released net_area is nonpositive in some records and can exceed area. | Do not treat raw coordinates as metres or use net_area for calibration. Propose scaling the interior/structure footprint to the paper-defined gross area field; expose this assumption and the complete scale audit for G1. | Pending reviewer |
| Q-07 | 2026-11-05 | 01 | D6 lacks household-size and dwelling-area distributions. | Do not infer distributions from aggregate counts; apply PROCEDURES' territory-level fallback unless the approved data already supply more detailed distributions. | Default from PROCEDURES |
