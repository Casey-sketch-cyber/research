# Buildings Stage 2 format audit

The audit covers the author-approved manuscript at `3a1e040`. The journal instructions were checked on 25 November 2026. [Buildings instructions for authors](https://www.mdpi.com/journal/buildings/instructions)

| Item | Result | Evidence |
| --- | --- | --- |
| LaTeX and Word templates | Pass | MDPI ACS archive published 12 November 2026, class **v6.5e** dated 9 November 2026. Buildings Word template revision **3**, revised 5 August 2026 in its package metadata and served 6 August 2026. |
| Article and section | Pass | Regular Article for “Architectural Design, Urban Science, and Real Estate.” |
| Abstract | Pass | One unstructured paragraph, 187 words. |
| Keywords | Pass | Seven, directly after the abstract. |
| Main section order | Pass | Introduction, Materials and Methods, Results, Discussion, Conclusions. |
| Back-matter order | Pass | Supplementary Materials, Author Contributions, Funding, IRB Statement, Informed Consent, Data Availability, Acknowledgments, Conflicts of Interest, References. |
| Authors, funder and AI statement | Pass | Three authors and original affiliations, corresponding email, grant 6026331014K, and the approved verbatim declaration in Acknowledgments. |
| Software, data and code | Pass | Software and versions in Section 2.11. Six data and code links retained. The study repository was verified accessible without authentication. [Study repository](https://github.com/liangdagongjue-code/research) |
| Acronyms in abstract, main text and first relevant artwork | Fail | S0/S1/S2, NIA and FCI are explained at the applicable first mentions. CP-SAT is partially expanded, while LTS and the Table 1 ID heading are implicit. See [author review items](ISSUES.md). |
| Main figures and tables | Pass | Figures 1–6 and Tables 1–4 follow first-citation order. Figure blocks follow the associated paragraphs. Tables are placed near the associated text, with the long tables on landscape pages. Table text is at least 8 pt. |
| Figure files | Pass | Six original vector PDFs and six 600 dpi PNGs. The optional graphical abstract is 1200 × 1200 pixels. |
| Supplement | Pass | Figures S1–S7 and Tables S1–S4 in first-citation order and with the approved legends. Table S4 is also supplied as the editable XLSX. Both keys cited in the supplement are present in the main references. |
| Bibliography | Pass | Thirty keys resolve against the 32-entry source and are numbered in first-citation order by the official ACS style. Unused entries are `johanes2026adaptable` and `yunitsyna2014universal`. |
| Citation placement | Pass | Numbered square brackets appear before sentence punctuation. |
| Number-comma style | Fail | Main and supplementary text use the approved style. The inherited artwork contains a few four-digit values with commas. See [author review items](ISSUES.md). |
| Build markers | Pass | The LaTeX PDF contains no unresolved citation keys, evidence tags or source repository paths. |
| Unused iScience sections | Pass | Highlights, eTOC blurb and Key Resources Table are excluded. |
| Cover letter | Pass | Significance, fit with the standing section, and both required declarations are present. The approved letter is dated 25 November 2026. |
| Package size | Pass | The local review ZIP and its submission contents are below 120 MB. |

## Output inventory

Files in the verified local package. The source archive contains all TeX inputs and the six vector figure files.

| File | Bytes |
| --- | ---: |
| BUILD.md | 2,210 |
| CHECKLIST.md | 4,263 |
| CoverLetter.docx | 13,353 |
| ISSUES.md | 1,747 |
| LaTeX_Source.zip | 1,682,212 |
| SupplementaryMaterials.pdf | 3,133,811 |
| TableS4.xlsx | 7,966 |
| figures/Figure1.pdf | 155,533 |
| figures/Figure1.png | 368,690 |
| figures/Figure2.pdf | 938,205 |
| figures/Figure2.png | 1,219,213 |
| figures/Figure3.pdf | 35,171 |
| figures/Figure3.png | 441,829 |
| figures/Figure4.pdf | 34,120 |
| figures/Figure4.png | 411,454 |
| figures/Figure5.pdf | 32,097 |
| figures/Figure5.png | 414,826 |
| figures/Figure6.pdf | 38,616 |
| figures/Figure6.png | 644,289 |
| figures/GraphicalAbstract.pdf | 89,874 |
| figures/GraphicalAbstract.tif | 226,010 |
| manuscript.docx | 3,348,069 |
| manuscript.pdf | 1,329,020 |
