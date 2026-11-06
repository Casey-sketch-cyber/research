# Phase 05: Rasterization and candidate generation

**Status: COMPLETE.**

## Checklist and acceptance
- [x] Separate furnishable, storage-only, walkable, blocked and door keepout cells.
- [x] Physical-wall/window masks, entrance portal and fixed-service approach masks.
- [x] Vectorized summed-area rectangle queries for every grid anchor/orientation.
- [x] Body/clearance fit, complete backing and tall-item window exclusions.
- [x] All transformation states fit the same anchor; only storage furniture can occupy storage rooms.
- [x] Analytical desk-count, backing, keepout, storage and state-anchor tests.
- [x] Benchmark on 24 frozen-sample review units; all checks pass.

## Key numbers and runtime

Candidate-generation median 0.108766 s/unit; maximum 0.171069 s/unit. Rasterization median 0.105321 s/unit. These are measured separately after the entrance/target corrections. The median is below the 2 s target. Per-item counts: results/candidates/counts.csv. Tests: 6 passed in 1.11s. Config hash: 82d8d08d5c86d0a16688aa23f5568be927e5b7239aec81d2bdfa8935128f33de.

## Decisions and limitations
Cells must be fully covered by allowed space. Dimensions round outward to the 0.1 m grid; all states rotate about the same back-left anchor. Clearance strips omit corner extensions and may overlap other clearances. Bodies cannot occupy mixed-class circulation cells. A storage-only item has no capability other than storage. Window unions preserve both polygon and line openings.

Door swing squares occupy each possible room side. An exterior entrance portal is used only for walking-radius erosion and BFS seeding; it never admits furniture. Walls and fixed services remain blocked. Free-space distance to blocked cells is conservatively reduced by the blocked cell’s half diagonal, so a continuous passage at the exact walking-width threshold can vanish on the grid. Resolution sensitivity remains required.

## Open questions and next step
No parameter defaults changed. Candidate feasibility is a raster-level guarantee; reachability and simultaneous placement are checked in Phase 6. The new geometry tests exposed and fixed an initial line-window omission before publication. The solver/validator and pilot are now complete; see the G2 method review. The publication audit redraws pilot images with explicit padding, leaving saved layouts unchanged.
