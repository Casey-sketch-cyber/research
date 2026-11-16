# Reference consolidation task

**For:** Codex. **Status:** v2, 2026-11-16, Claude. The author decided that about 40 references are enough, so there is **no expansion**. The task is to consolidate and verify the existing references.

## Scope

1. Take the 24 references in `docs/RESEARCH_PLAN.md` §10.
2. Add the strong records proposed in `reports/novelty_check.md` ("Proposed citation additions" and "Citation proposals for review"). These include Zeng et al. (SBF), Bu & Che Mat, Elmurodov & Mametova, Freimane, Yunitsyna, Qaradaghi & Qaradaghi, Rakhmatillaeva, Ashkevari & Farhady, Chen, and the MAFC paper. Skip theses, repository copies and low-quality venues.
3. Complete the entries marked "verify": Xiong et al. TVCG; Fu et al. Magic Furniture; Bu & Che Mat volume and pages; the citation form of the HK Basic Housing Units Ordinance.
4. Within the same budget of about 40, it is acceptable to replace a weak record with the standard citation of a tool the Methods name, for example OR-Tools CP-SAT. Do this only if a slot is free; do not grow the list.

## Rules

- Every entry comes from a live database record (Crossref, OpenAlex, Semantic Scholar, arXiv) or an official page. Nothing from memory.
- Every DOI must resolve via `https://api.crossref.org/works/<DOI>` or OpenAlex, with matching title, first author and year.

## Output (branch `codex/paper-refs`, PR against `main`)

- `paper/references.bib`: the single source for the manuscript.
- `paper/references_notes.csv` with the columns `key, title, first_author, year, venue, doi_or_url, verified_via, what_it_establishes, how_we_use_it`.

Claude spot-checks DOIs and relevance before merging.
