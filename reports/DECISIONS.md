# Decision log

Append one line per decision: `D-NN | date | phase | decision | reason | approved by (reviewer / default assumption)`.

| ID | Date | Phase | Decision | Reason | Approved by |
|---|---|---|---|---|---|
| D-00 | 2026-11-05 | plan | Use only open datasets that need no application (D1, D2, D4, D5, D6) plus generated shells (D3) | 3-week timeline; no purchased data | author |
| D-01 | 2026-11-05 | 00 | Isolate the environment and defer GPU packages until the relevant experiment | Avoid changes to existing workloads; early phases use CPU | default assumption |
| D-02 | 2026-11-05 | publication | Retain research-related regions, datasets and provenance; omit private operational details, identifiers and personal information | Explicit publication boundary confirmed by author | author |
| D-03 | 2026-11-05 | 00 | Respect effective CPU and memory quotas rather than the host-wide totals | Prevent oversubscription and make runtime reporting interpretable | default assumption |
| D-04 | 2026-11-05 | 01 | Acquire the slow D1 archive through an alternate authorized execution environment, verify the official MD5 and SHA-256, then transfer the same bytes | Remote source transfer was slow; no alternate dataset or altered data is substituted | default assumption |
| D-05 | 2026-11-05 | 01 | Map every observed D1 area subtype explicitly; keep circulation walkable-only and kitchens/sanitary/service rooms fixed | Fill the plan's Phase 1 placeholders from observed labels; document conservative treatment of mixed kitchen/dining areas | default assumption for G1 review |
| D-06 | 2026-11-05 | 01 | Treat the released D2 net_area field as unverified; audit against paper-defined gross area and source geometry | Prevent silent use of normalized coordinates or inconsistent metadata as metric dimensions | default assumption for G1 review |
