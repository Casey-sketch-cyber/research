# Phase 05: Rasterization and candidate generation — G2 refresh

Status: COMPLETE. The full 0.10 m anchor benchmark on 24 uncapped review units passed all checks. This is a candidate-generation check; the G2 pilot separately compares 0.10/0.20 m anchors and selects the latter only under the declared score criterion.

Candidate generation: median 0.122848 s/unit, maximum 0.170088 s/unit. Rasterization median: 0.134132 s/unit. Config hash: 6b045c7aaf2423758dca393571baee8e1c4fae6e6c5344b5a087d6c94ad74bb7. Tests: 6 passed in 1.47s.

Whole-cell collision, complete backing, door keepouts, storage-only item constraints, tall-item window exclusions and all-state anchor consistency remain enforced. Walls and fixed bodies block circulation; kitchen rooms are walkable and hatched in the revised figures. The half-diagonal distance test is superseded by exact-diameter even/odd disc erosion, independent traversal and dilation in both solver and validator. The 0.60/0.50 m and 0.90/0.80 m boundaries and bed-side access strips have regression coverage.

The candidate table uses full-resolution anchors. Final solver anchors use the G2 selected lattice while collisions/access retain a 0.10 m raster. The full-resolution sensitivity remains due. Furniture and household defaults are unchanged; no swept-motion feasibility is implied.
