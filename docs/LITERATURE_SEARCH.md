# Task L: Systematic literature search (confirms the novelty check)

**Why:** `reports/novelty_check.md` is a web-based first pass. This task confirms it with a reproducible, documented search of free scholarly databases, standing in for Scopus or Web of Science, which the project cannot access.

**When:** run it first in your next session, before the G1 fixes (M1–M6). It should take about 1–2 hours. It does not block the engineering work unless the stop rule in §5 is triggered.

**Config:** `config/lit_search.yaml`. **Script:** `scripts/00b_lit_search.py` (one script, resumable, with API responses cached under `data/interim/lit_cache/`, which is git-ignored).

## 1. Retrieval

1. For every query in `config/lit_search.yaml`, query **OpenAlex** and **Semantic Scholar** with the boolean form, and **arXiv** with the boolean form translated to its syntax. Restrict publication years to `years`.
2. Query **Crossref** with the short keyword form, and use it to fill in missing DOIs, venues and years.
3. Respect rate limits: back off and retry on HTTP 429, wait at least 3 s between arXiv requests, and never run requests in parallel against one API.
4. Record per query and source: the exact request URL (with no email or key), the date, the hits reported, and the records retrieved.

## 2. Deduplication

Merge records by DOI, then by normalized title (lowercase, punctuation stripped) plus year. Keep the union of source and query IDs. Write `results/literature/raw_hits.csv` with columns `rec_id, doi, title, year, venue, type, authors_first3, sources, query_ids, cited_by, abstract_available, url`.

## 3. Screening

**Stage 1, title.** Remove records that are clearly off-topic: furniture manufacturing, wood science, ergonomics of seating, retail marketing, robotics hardware without layout, and office/healthcare facilities without dwellings. Keep anything uncertain. Log the reason for every removal.

**Stage 2, abstract.** For each remaining record, read the abstract, which must come from an API response; never write one. Assign:
- `KNOWN`: already in `already_known`.
- `A_overlap`: the abstract claims or reports what one of `claims` C2, C3 or C4 describes.
- `B_related`: relevant and worth citing, but doesn't do what the claim says.
- `C_irrelevant`.

For every A or B record, write one sentence on **what it does and does not do relative to the claim**. Assign `claim_affected` from C2, C3, C4 or H2.

**Stage 3, full text, for A only.** If an open-access full text exists (OpenAlex `open_access.oa_url`, arXiv), read the method and results and confirm or downgrade the A rating. If no full text is available, say so; don't infer.

Write `results/literature/screened.csv` with columns `rec_id, doi, title, year, venue, stage1, stage2, claim_affected, note, fulltext_checked`.

## 4. Report

Append a section **"Systematic confirmation (task L)"** to `reports/novelty_check.md`. Don't rewrite the earlier sections. It must contain:

1. A flow table: retrieved per source, after deduplication, after stage 1, after stage 2 (A / B / KNOWN / C), and full-text checked.
2. A table of every A and B record: citation, DOI, claim affected, and the one-sentence note.
3. An updated verdict for C2, C3, C4 and H2: **still appears novel / weakened / not novel**, with the records that decide it.
4. Any B record that should be added to RESEARCH_PLAN §10, listed as a *proposal* for the reviewer to accept. Don't edit RESEARCH_PLAN yourself.
5. Limitations: which sources failed or were rate-limited, and the total number of abstracts screened.

## 5. Stop rule

**Revised after Q-12.** Claims C2 and C3 have been narrowed (see `config/lit_search.yaml`). Single-room or conceptual numerical area gains are now `B_related`, not `A_overlap`.

Only a record that meets the **narrowed** C2 or C3 after a full-text check triggers the rule: either an optimization method that assigns furniture states from a time-of-day activity schedule in dwellings, or a quantification of whole-dwelling equivalent floor area across 10 or more plans. In that case, add it to `reports/QUESTIONS.md` and push, but **don't stop the engineering work**. The reviewer will respond at the next gate.

## 5a. Completing the screening (revised schedule)

Finish screening **in the background of the long Phase 7 runs**, not before the G1 fixes. It must be complete by Gate G3.

1. **Title screening:** all 2,908 pending records.
2. **Abstract screening:** every title-retained record with an API abstract.
3. **Records without an API abstract:** if the title is clearly relevant, try the Crossref or OpenAlex abstract once. Otherwise mark them `NO_ABSTRACT_TITLE_RELEVANT` and list them in the report. Don't guess their content.
4. **OpenAlex Q1:** retry once with polite backoff (it was incomplete because of HTTP 429). If it still fails, report the gap.
5. The Chinese-language search stays optional.

## 6. Optional: Chinese-language literature

CNKI has no free API; don't scrape it. If time allows, search OpenAlex with Chinese keywords (`可变家具 小户型`, `多功能家具 空间利用`), screen them the same way, and report them separately.

## 7. Integrity rules

- Every title, author, year, venue, DOI and abstract must come from an API response saved in the cache. Never complete a reference from memory.
- Screening judgements are yours and must be written as judgements ("abstract does not mention time-of-day use"), not as facts about the paper's full content unless the full text was read.
- Commit no API key, email address or personal identifier.
