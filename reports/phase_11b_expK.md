# Phase 11b — Reduced furniture-kit experiment

- [ ] Freeze eight dimension combinations per household for H1 and H3, with a 30-shell training pool, 15 held-out shells and 15 real plans.
- [ ] Implement and independently audit the quality-weighted service objective. The original catalogue and its validation rules remain the reference for feasible assignments.
- [ ] Measure a runtime pilot and confirm the 48-hour limit. Apply the approved training-size sequence 30, 24, 18 if the projection calls for it.
- [ ] Compare quality-aware successive halving with flat-quality halving, and evaluate the eight-candidate bespoke envelope on training shells.
- [ ] Run catalogue, selected kit and flat-quality kit on the three frozen sets under S0, S1 and S2. Report the separate form and time effects, support of adequate-area estimates, dimensions and quality trade-offs.
- [ ] Write kit.yaml and F12, and make the H1 and H3 kit configurations available to the Hong Kong scenario.

The reduced scope follows D-38 and D-39. The G2 round-3 review and workload projection use the reviewed small-home budget of 120 seconds and four solver workers per solve, with 0.10 m anchors. The earlier 20-second grid setting predates this planning decision. Identical saved evaluations can be reused across the three halving stages and bespoke comparison when their configuration, objective and evaluation mode match.

Dimension vectors span the configured range through deterministic maximin selection, seeded by the compact and full-size endpoints. A desk or table serving a demand receives the smaller of its width and depth quality values. A service requiring several items takes their minimum reachable quality. Storage uses the configured frontage capacity and the existing demand cap. Quality weights affect the optimization and a separate validator reconstructs the served credits. Flat-quality layouts are also scored with their physical quality values. The catalogue reference has unit service quality.

The fixed D3 training pool excludes the held-out aspect ratio and entrance level. The held-out pool contains shells with either excluded factor and the real-plan pool uses eligible NIA up to 20 m². Selection uses geometry before scores. Stage 1 uses ten shells, then the top 20% advance to the active training pool. The last stage can reuse evaluations for identical shells and objectives. Bespoke selects per shell among the eight dimension vectors and includes the confirmed uniform kit incumbent as a feasible candidate.
