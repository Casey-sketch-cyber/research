# Phase 10 — Geometry-only surrogate

- [x] Freeze the D1 group split (70/15/15) and preserve D2 and D3 as external test sets.
- [x] Construct room/space component graphs and tabular features from Unit geometry and the configured household indicator.
- [x] Derive S0/S2 labels from the accepted corrected layouts. Fit the P1 area ruler on D1 training units only, and retain identified values and lower bounds.
- [x] Train area-only linear, histogram gradient boosting, MLP and GraphSAGE. Choose all hyperparameters on the D1 validation groups and log each trial.
- [x] Export per-household, target and test-set MAE, RMSE, R², Spearman and measured inference time, with denominators and support flags. Save GNN weights and inspect F8.

The feature extractor uses the known interior, room-class polygon components, opening lengths, and edges from adjacency or a shared door. Household type is a configured input. Source and group identifiers determine splits and reporting. All fitted preprocessing and the saving reference use D1 training data. The saving target uses the P1 paired equivalent-area gain, with the same training static ruler applied to every split. Censored target values are retained as lower bounds and the point-error metrics use identified labels. Exact zeros remain included. Inference timings refer to feature-ready inputs and include prediction and the inverse target scaling where used.

The grouped surrogate run and visual check are complete. See [accepted results](phase_10_C_results.md) and the [held-out metrics and split](../results/expC/).
