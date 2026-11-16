# Reference expansion task

**For:** Codex (preferred: it can query the APIs) or another assistant with live web search. **Status:** v1, 2026-11-16, Claude.

## Why

- The manuscript can currently draw on the 24 references in `docs/RESEARCH_PLAN.md` §10 and about 15 strong records from `reports/novelty_check.md`.
- An iScience article usually needs a broader base (roughly 50–70 references in total) to establish context, methods and datasets.
- Add about **25–40 well-chosen references** for the gaps below. Do not try to maximise the count.

## Hard rules

1. **Never write a reference from memory.** Every entry must come from a live database record: OpenAlex, Crossref, Semantic Scholar, arXiv, or an official government or standards page.
2. **Verify every DOI.** `https://api.crossref.org/works/<DOI>` (or OpenAlex) must resolve, and the title, first author and year must match. Record the verification.
3. **Quality.** Prefer peer-reviewed journals and major conferences (2000–2026), official regulations and standard reference books. Avoid theses, institutional-repository copies, predatory venues and non-English sources unless a source is uniquely relevant (then say why).
4. **Read before citing.** Read at least the abstract. Write one line on what the paper establishes and how it relates to our study. Do not cite for claims the paper does not make.
5. **Respect the claims rules** in `docs/PAPER_STORY.md` §7. References support context; they do not create new claims.

## Gaps to fill (target counts)

| # | Gap | Where it is used | Target |
|---|---|---|---|
| G1 | Shrinking dwellings, micro-housing and housing affordability in dense cities (incl. Hong Kong subdivided units, co-living, micro-apartments) | Introduction P1 | 4–6 |
| G2 | Minimum space standards and their evidence base (e.g. national space standards, Parker Morris lineage, critiques of area-only rules, health and well-being effects of small or crowded homes) | Introduction P1–P2, Discussion D3 | 5–7 |
| G3 | Time-use and household activity schedules relevant to home use (time-use surveys, working from home and dwelling use) | Methods (households), Introduction P2 | 3–4 |
| G4 | Flexible, adaptable and transformable housing and furniture (beyond the records already screened) | Introduction P2, Discussion D2 | 4–6 |
| G5 | Computational floor-plan and furniture-layout generation (e.g. graph-based plan generation, learned layout synthesis, LLM layout tools) as the computational context | Introduction P2 | 4–6 |
| G6 | Floor-plan datasets and plan analytics (Swiss Dwellings, ResPlan, RPLAN-type datasets, plan-based building analysis) | Methods (data), Introduction | 2–4 |
| G7 | Methods we use: constraint programming / CP-SAT (OR-Tools), the bootstrap, isotonic or monotone regression, logistic dose–response curves, GraphSAGE | STAR Methods | 4–6 |
| G8 | Ergonomics and clearances: anthropometric and circulation dimensions for furniture use and walking access | Methods (furniture library) | 2–3 |

Also **complete the four entries marked "verify"** in RESEARCH_PLAN §10 (Xiong et al. TVCG; Fu et al. Magic Furniture; Bu & Che Mat volume and pages; the HK Ordinance citation form), and the Zeng et al. (SBF) record from `reports/novelty_check.md`.

## Output

On branch `codex/paper-refs`, open a PR. Do not edit `docs/` or `reviews/`. Deliver:

- `paper/references.bib`: BibTeX, one key per entry (`firstauthorYEARkeyword`), with DOI or URL.
- `paper/references_notes.csv` with the columns: `key, gap, title, first_author, year, venue, doi_or_url, verified_via, verified_on, abstract_read (yes/no), what_it_establishes (one line), how_we_use_it (one line)`.
- `paper/references_search_log.md`: queries run, databases, dates, counts retrieved and kept.
- Include the existing RESEARCH_PLAN §10 and the selected novelty_check entries in the `.bib` as well, verified the same way, so that `references.bib` is the single source for the manuscript.

Claude reviews the PR by spot-checking DOIs and relevance. After the merge, the manuscript writer replaces `[CITE: …]` placeholders using only `paper/references.bib`.
