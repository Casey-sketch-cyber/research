# Draft v4 (final text pass) review (PR #16)

**Reviewer:** Claude, 2026-11-18. **Verdict: APPROVED, merged.** The manuscript text is ready for the author's fields and a submission check.

Checked:

- **Numbers.** No result number changed. A diff of all numerals before and after shows only the added "ΔEA = 3.48 m²" for the showcase home (from `paired_equivalent_area.csv`) and renumbered title options.
- **Figure 1 legend.** Replaced with the short version, 152 words, panels A–D matching the final figure.
- **Formatting.** No backticks remain, and the legends and main text contain no repository paths. Internal tokens (`work_1`, `dine_4` …) are rewritten in plain words that match `config/households.yaml` (for example, the guest-dinner day needs four-person dining).
- **Lengths.** Summary 148 words; Highlights 65–80 characters; Summary-to-Discussion about 4,680 words.
- **References.** The list is unchanged (30), and every listed entry is cited in the text.
- **Title and graphical abstract.** The title is as chosen by the author. The +3.5 m² source is documented in `paper/NOTES_FROM_WRITER.md`.

Remaining before submission (author):

1. Authors, affiliations, lead contact, author contributions, declaration of interests.
2. Make the repository public at submission (it already is) and mint a Zenodo DOI for the code and results. Put the DOI in the Key resources table and in Data and code availability.
3. Convert `paper/manuscript.md` to the submission format (Word or PDF via pandoc), with figures uploaded separately.
4. Write a cover letter.
