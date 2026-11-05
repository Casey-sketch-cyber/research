# G1: Data, corpus, furniture and household review

**Date:** 2026-11-05. **Status:** READY FOR REVIEW; publication awaits repository
write access. This is not reviewer approval. Phases 5 onward have not started.

Configuration hash: `bf9718204e1947d63b4d00260c3fc8f3fb1f88322676810f0288f8f29530a3f6`.
The Phase 0 environment report retains the initial configuration hash; subsequent
data and preparation artifacts use the current hash after the documented mapping
and acquisition settings were filled. Furniture and household defaults were not changed.

## 1. Completed scope
- [x] Phase 0: isolated Python 3.11 environment and sanitized dependency evidence.
- [x] Phase 1: authorized D1, D2, D4 and D6 acquisition, checksums, full schema inspection and D1 subtype mapping.
- [x] Phase 2: full D1/D2 conversion, D3 generation, filtering, exclusions, area histogram and 24 sample renders.
- [x] Phase 3: every furniture footprint/state compared with explicitly limited ABO reference cohorts.
- [x] Phase 4: household parsing, demand-hour checks and generated Table T3.
- [ ] Reviewer assessment of the geometry, modelling assumptions and flagged furniture states.
- [ ] Repository publication with a writable connection.

## 2. Acceptance evidence
| Stage | Result | Evidence |
|---|---|---|
| Environment | PASS | [Environment](ENVIRONMENT.md), [Phase 0](phase_00_environment.md), dependency lock |
| Data and subtype mapping | 8 checks passed | [Data manifest](data_manifest.csv), [schema reports](schemas/), [acceptance](phase01_acceptance.json), `config/project.yaml` |
| Corpus | 16 checks passed | [Acceptance](phase02_acceptance.json), [counts](../results/corpus/counts.csv), [exclusions](../results/corpus/exclusion_reasons.csv), [Phase 2](phase_02_corpus.md) |
| Visual artifacts | Generated and inspected; human review pending | [24-unit contact sheet](../results/corpus/sample_contact_sheet.png), [individual samples](../results/corpus/samples/), [F2 PNG](../results/figures/F2_corpus_area.png), [F2 PDF](../results/figures/F2_corpus_area.pdf) |
| Furniture | 5 checks passed | [Audit](furniture_audit.json), [comparison CSV](../results/furniture/abo_dimension_check.csv), [interpretation](../results/furniture/interpretation.md) |
| Household schedules | 4 checks passed | [Audit](households_audit.json), [T3 CSV](../results/tables/T3_households.csv), [T3 readable table](../results/tables/T3_households.md) |
| Complete test suite | 23 passed, no skips; 37.00 seconds | [Test output](G1_tests.json); command `python -m pytest -q` |

## 3. Main preparation results
| Source | Converted/generated | Included | Excluded |
|---|---:|---:|---:|
| D1 Swiss Dwellings | 46,830 | 11,598 | 35,232 |
| D2 ResPlan | 17,000 | 1,978 | 15,022 |
| D3 generated shells | 510 | 420 | 90 |

These counts come from `corpus_audit.json` and the corpus CSV. The main
furnishable-area filter stays at 8–45 m²; it was not relaxed to raise inclusion.
All generated shells are retained with flags for the later gross-area scenario.

The furniture audit compares 24 footprints. Fourteen are outside their reference
IQR, fifteen are explicitly unvalidated states/items, and four have no matching
cohort; flags overlap. Every item has a documented keep-pending-review reason.
None of these comparisons establishes that the transformation mechanism, its
clearance, storage or occupant capacity is empirically valid.

T3 contains five households, six alternative-day variants and 36 slot rows.
Weighted demanded hours are 18.9, 26, 26, 28 and 26 for H1–H5 respectively. These
are activity-weighted requirements, not elapsed time or measured behaviour.
H5 is reserved for ablations. Optional ATUS calibration was deferred.

## 4. Decisions required from the reviewer
1. **D1 area and class semantics.** Gross area remains missing. The separate
   known-interior area is not a substitute for gross area. Containment uses the
   constructed interior because the release provides no verified independent
   whole-unit outline. Review mixed kitchen/dining classification and samples
   without labelled fixed-service rooms.
2. **D2 metric scale.** Approve or revise calibration to the paper-defined gross
   `area` using the union of inner/structure/opening geometry. Released `net_area`
   is inconsistent and unused. Unexplained detached inner components are excluded.
3. **Entrances and numerical exclusions.** Strict contact tolerance leaves source
   gaps excluded. Review that policy before considering physical padding. Three
   D1 topology failures and one D2 area-preservation failure are explicit exclusions.
4. **D3 geometry.** Door/window spans use measured D1 geometric medians, not verified
   clear widths. Services use feasible corner/wall placement; in narrow shells the
   toilet can lie at the far end. Review all eight sampled D3 layouts and the
   separation between gross-area scenario selection and main-corpus filtering.
5. **Furniture and schedules.** Accept or revise the author design assumptions,
   especially transformation states lacking direct data. No furniture or household
   override is active. FCI must average per-variant ratios by frequency, preserving
   simultaneous duplicate demands and capacity-based storage credit.
6. **Later scenario scope.** D6 supplies district counts but lacks household-size
   and dwelling-area distributions. Use the documented territory-level fallback
   unless approved evidence supplies them. Configured households cover one or two
   people; no three-person household was invented.

The full question log, including the outstanding author-led novelty check, is
[QUESTIONS.md](QUESTIONS.md). Decisions and their approval status are in
[DECISIONS.md](DECISIONS.md). Nothing here establishes a research hypothesis,
area saving, minimum adequate dwelling size or carbon benefit.

## 5. Runtime and reproduction
Successful corpus invocation: 927.19 seconds; D1 conversion 906.64 seconds,
D2 conversion 267.01 seconds and D3 generation 5.08 seconds, with independent
sources overlapped. Furniture check: 10.623 seconds; schedule check: 0.632 seconds.
These are recorded successful runs, not total project effort, installation time
or earlier failed/debugging attempts. Peak memory was not measured. No GPU
training was performed.

Use [REPRODUCING.md](../docs/REPRODUCING.md). Raw data and complete normalized
geometry are intentionally untracked; authorized source URLs, pinned revisions
and checksums are recorded. The public package contains code, configs, sanitized
provenance, scalar results and local-coordinate samples.

## 6. Publication and continuation
Publication checks inspect the staged bytes for private endpoints, credentials,
operational identifiers, personal/session terms and local paths; image/PDF metadata
was also reviewed. New commits use a nonpersonal author and committer identity.
No raw archives or operational files are included. Existing upstream history is
not rewritten. GitHub itself may retain authentication/push audit metadata; file
sanitization does not promise anonymity from the hosting service.

The current connection does not grant write access, so this report does not claim
that the package has been uploaded. Local commits preserve the complete review
package while publication is pending.

Per `AGENTS.md`, stop at G1. The reviewer should create `reviews/G1_review.md` with
`Verdict: APPROVED` or `Verdict: CHANGES_REQUESTED` and numbered [must]/[should]
items. Continue only under the repository's review protocol. No approval file has
been fabricated and the solver/pilot work remains unstarted.
