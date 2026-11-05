# Task L: Systematic literature confirmation

> Current decision: Q-12 authorizes continuation with narrowed claims; see reviews/G1_review_addendum_Q12.md. The stop and category counts below are the historical pre-review record. Remaining screening is due at G3.

**Historical status: STOP REQUIRED; retrieval attempted for all configured queries, screening PARTIAL.**

A new full-text-confirmed overlap with the broad C3 claim triggers docs/LITERATURE_SEARCH.md §5. Q-12 requires reviewer framing guidance before G1 corrections and Phase 5. This is not a completed systematic review.

## Completed work
- [x] Attempt all six queries against each configured source, save responses, dates, exact nonsecret URLs, hit counts and retry outcomes.
- [x] Preserve successful evidence across failed retries and merge by DOI or normalized title/year.
- [x] Read the API abstracts of the explicitly selected records and check the identified overlap's methods/results and key figures.
- [x] Export raw_hits.csv, screened.csv, query/response provenance, full-text checksum and the appended novelty-report section.
- [x] Apply the C3 stop rule and leave unreviewed records visibly pending.
- [ ] Complete screening of all remaining records; finish unresolved metadata/abstract retrieval after reviewer guidance.
- [ ] Resume G1 M1–M6/S1–S4 and Phases 5–6 only after the framing decision.

## Script-produced evidence counts
- Retrieved query records: 3451; unique after merging: 2928.
- Sources: openalex 406; semantic_scholar 4; crossref 3000; arxiv 41.
- Abstracts actually read: 20; A_overlap 1, B_related 15, C_irrelevant 4; full texts checked 1.
- Still pending: 2908; retrieved records without an API abstract: 1859. Pending is not a negative finding.

## Decision and evidence boundary
The checked paper is Bu & Che Mat (2026), DOI [10.13189/cea.2026.140514](https://doi.org/10.13189/cea.2026.140514). It analytically compares activity areas with fixed and folding furniture. This precedes broad C3, while the narrower whole-dwelling, time-weighted FEA optimizer may still be distinguishable. The authors identify their own comparison as conceptual/analytical; it must not be described as measured savings in occupied homes. The reviewer decides whether the proposed distinction is sufficient.

Exact evidence, proposed wording, all reviewed A/B papers and limitations are in the **Systematic confirmation (task L)** section of reports/novelty_check.md. The research plan was not rewritten and no project area-saving result was invented.

## Retrieval limitations and fixes
OpenAlex cursor continuation required authentication; switched to [documented public basic paging](https://help.openalex.org/api/paging/) (100/page), with no authentication bypass. Repeated HTTP 429 still left its Q1 incomplete (see retrieval_queries.csv). Earlier successful pages are retained, including when later retries fail. Crossref keyword results reach the configured cap and are not exhaustive. Only OpenAlex enforces the English filter at query time; language eligibility elsewhere and missing metadata remain unresolved. A redundant retry pass was stopped after the overlap was confirmed; all completed responses remain cached. Structured retry warnings are exported separately in retry_events.json because the initial cache format retained only the latest response per URL; these overlap with request-manifest attempts and must not be added together.

The paper's public PDF was downloaded with operating-system certificate verification after the Python client could not validate the publisher's chain. Its checksum and the exact pages/figures checked are in results/literature/fulltext_checks.json; the PDF and extracted text are private cache artifacts and are not committed.

## Validation and reproduction
Eight targeted literature/publication tests passed: query translation, abstract reconstruction, DOI/title-year merging, arXiv metadata, preservation of earlier successful responses after retry failures, and prevention of negative or read judgements for unreviewed/unavailable evidence. A DOI suffix containing values above 255 was a false-positive IPv4 finding; the scanner now validates octet ranges while preserving explicit private-term checks.

Run retrieval with `python scripts/00b_lit_search.py`. Export the saved evidence and decisions with `python scripts/00b_lit_search.py --cached-only --screening-decisions results/literature/screening_decisions.json`. API responses live in ignored data/interim/lit_cache/. Public tables contain bibliographic metadata and judgements, not copied abstracts.

Config hash: `a5d6bc0e20a07cce43e51c76759eec561b2b56b8c863af5a52435b1aca1ae0f4`.
