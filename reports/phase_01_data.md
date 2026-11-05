# Phase 01: Data acquisition and schema inspection

**Status:** COMPLETE. The full run passed the checks in `reports/phase01_acceptance.json`.

## 1. Checklist (from PROCEDURES.md)
- [x] Download only D1, D2, D4 listings and D6, with resumable transfers and SHA-256 manifest.
- [x] Inspect actual file schemas, row counts and sanitized examples.
- [x] Enumerate all D1 entity types/subtypes and simulation column prefixes.
- [x] Inspect D2 keys and geometry types with a restricted pickle constructor allowlist.
- [x] Measure ABO dimensions/product-type coverage.
- [x] Inspect D6 fields and the official data dictionary.
- [x] Replace D1 subtype placeholders with observed, documented classes.

## 2. Acceptance checks
| Check | Result | Evidence |
|---|---|---|
| Manifest has checksums | PASS | `reports/data_manifest.csv`; acquisition complete with no errors |
| D1/D2/D4/D6 schema reports | PASS | `reports/schemas/D1.md` through `D6.md`; full source inspection |
| D1 mapping fully populated | PASS | `config/project.yaml`; exact observed-type coverage and disjointness test |
| Full-run integrity and tests | PASS | All eight checks true; seven tests pass in `reports/phase01_acceptance.json` |

## 3. Key numbers
| Quantity | Value | Evidence |
|---|---|---|
| D1 geometry rows / simulation rows | 3,255,905 / 367,678 | `reports/schemas/D1_summary.json` |
| D2 plans / nonpositive net_area / net_area exceeding area | 17,000 / 5,458 / 1,796 | `reports/schemas/D2_summary.json` |
| D2 nonpositive source gross area | 0 | `reports/schemas/D2_summary.json` |
| ABO listings / listings with dimensions | 147,702 / 43,338 | `reports/schemas/D4_summary.json` |
| ABO usable dimension triples | 43,002 | `reports/schemas/D4_summary.json` |
| D6 rows, including land total | 19 | `reports/schemas/D6_summary.json` |

### D1 classification reasoning

- Furnishable: sleeping, living, dining, ordinary rooms, in-unit office/studio and storage/cloak rooms can hold furniture. Physical built-in features are still subtracted in Phase 2. Only residential units are retained.
- Walkable-only: corridors, halls, foyers and lobbies preserve circulation rather than becoming furniture area.
- Fixed-service: kitchens, mixed kitchen/dining rooms, bathrooms, sanitary and laundry rooms. Mixed kitchen/dining rooms are conservatively excluded as a whole rather than inventing a kitchen boundary.
- Excluded: every other observed subtype, including exterior spaces, shafts, voids, stairs, plant/service areas, nonresidential specialist functions and unknown labels. Exact membership is explicit in the config; no unobserved labels were added.

## 4. Deviations from the plan
- Published examples will omit original source IDs, addresses, coordinates in the source frame and any personal data. Normalized room geometry is research data and may be published.
- Optional ATUS is deferred; no optional data are downloaded.
- Publication was initially delayed by missing write authorization. Repository-owner authorization was subsequently verified for the G1 package; the computational work and neutral commit authorship were preserved. No private account details are recorded here.
- The slow D1 transfer was completed through another authorized execution environment, checked against the publisher MD5 and transferred unchanged. The complete acquisition/schema/test run then passed in the computational environment; preliminary partial reports are superseded.
- D2 coordinates are normalized source coordinates, and its net_area field is inconsistent with source gross area. Phase 2 will expose a gross-area calibration assumption rather than treating those coordinates as metres. G1 must review this assumption; source declared areas themselves are not independently validated.
- The linked general IDDS PDF does not supply a specific SDU field dictionary. The official CSV supplies English/Chinese field names and SDU definitions directly, so those are used. D6 has no household-size or floor-area distribution; neither is inferred.

## 5. Decisions
- Public research geography and dataset attribution are retained, as explicitly confirmed by the author; unrelated equipment identifiers and connection details are excluded.

## 6. Open questions for the reviewer
- Review the D2 calibration assumption, conservative D1 room mapping and data-derived D3 opening widths at G1.

## 7. Runtime and resources
Per-source measured inspection times and software platform/version are in `reports/schema_runs/`. Acquisition verification time is in `reports/acquisition.json`. This final verification time is not the total elapsed time of the earlier interrupted network transfer; no complete end-to-end transfer timing is claimed.

## 8. Files added or changed
- Phase scripts 01, 02 and Phase 1 acceptance checker; constrained archive readers; schema/provenance reports; the observed D1 mapping; safety and mapping tests.
