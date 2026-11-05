# Decision log

Append one line per decision: `D-NN | date | phase | decision | reason | approved by (reviewer / default assumption)`.

| ID | Date | Phase | Decision | Reason | Approved by |
|---|---|---|---|---|---|
| D-00 | 2026-11-05 | plan | Use only open datasets that need no application (D1, D2, D4, D5, D6) plus generated shells (D3) | 3-week timeline; no purchased data | author |
| D-01 | 2026-11-05 | 00 | Isolate the environment and defer GPU packages until the relevant experiment | Avoid changes to existing workloads; early phases use CPU | default assumption |
| D-02 | 2026-11-05 | publication | Retain research-related regions, datasets and provenance; omit private operational details, identifiers and personal information | Explicit publication boundary confirmed by author | author |
| D-03 | 2026-11-05 | 00 | Respect effective CPU and memory quotas rather than the host-wide totals | Prevent oversubscription and make runtime reporting interpretable | default assumption |
