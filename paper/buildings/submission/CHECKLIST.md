# Buildings Stage 2b format audit

The audit covers `c10053e`, the merged Stage 1b manuscript approved in PR #22. The journal instructions were checked on 25 November 2026. [Buildings instructions for authors](https://www.mdpi.com/journal/buildings/instructions)

| Item | Result | Evidence |
| --- | --- | --- |
| LaTeX and Word templates | Pass | Local submission uses MDPI ACS archive published 12 November 2026, class **v6.5e** dated 9 November 2026, and Buildings Word template revision **3**, revised 5 August 2026 in its metadata. The public PDF and DOCX use standard formatting and the same approved content. |
| Article and section | Pass | Regular Article for “Architectural Design, Urban Science, and Real Estate.” |
| Abstract | Pass | One unstructured paragraph, 187 words. |
| Keywords | Pass | Seven, directly after the abstract. |
| Main section order | Pass | Introduction, Materials and Methods, Results, Discussion, Conclusions. |
| Back-matter order | Pass | Supplementary Materials, Author Contributions, Funding, IRB Statement, Informed Consent, Data Availability, Acknowledgments, Conflicts of Interest, References. |
| Authors, funder and AI statement | Pass | Three authors and original affiliations, corresponding email, grant 6026331014K, and the approved verbatim declaration in Acknowledgments. |
| Software, data and code | Pass | Software and versions in Section 2.11. Six data and code links retained. The study repository was verified accessible without authentication. [Study repository](https://github.com/liangdagongjue-code/research) |
| Acronyms in abstract, main text and first relevant artwork | Pass | Stage 1b expands CP-SAT in Section 2.5 and the Figure 1 caption. S0/S1/S2, NIA and FCI are explained at the applicable first mentions. LTS, ID and 3D follow the decisions in the Stage 2 review. |
| Main figures and tables | Pass | Figures 1–6 and Tables 1–4 follow first-citation order. Figure blocks follow the associated paragraphs. Tables are placed near the associated text, with the long tables on landscape pages. Table text is at least 8 pt. |
| Figure files | Pass | Six original vector PDFs and six 600 dpi PNGs. The optional graphical abstract is 1200 × 1200 pixels. |
| Supplement | Pass | Figures S1–S7 and Tables S1–S4 in first-citation order and with the approved legends. Table S4 is also supplied as the editable XLSX. Both keys cited in the supplement are present in the main references. |
| Bibliography | Pass | Thirty keys resolve against the 32-entry source and are numbered in first-citation order by the official ACS style. Unused entries are `johanes2026adaptable` and `yunitsyna2014universal`. |
| Citation placement | Pass | Numbered square brackets appear before sentence punctuation. |
| Number-comma style | Accepted | Main and supplementary text follow the approved style. Claude approved the existing four-digit comma labels in the artwork. See [review decisions](ISSUES.md). |
| Approved results and wording | Pass | The builds use the merged revision. All four main tables, front and back matter, primary result values and confidence intervals match the approved source. The 16 shared artwork and supplement files match Stage 2 byte for byte. |
| Build markers | Pass | The LaTeX PDF contains no unresolved citation keys, evidence tags or source repository paths. |
| Unused iScience sections | Pass | Highlights, eTOC blurb and Key Resources Table are excluded. |
| Cover letter | Pass | Significance, fit with the standing section, and both required declarations are present. The approved letter is dated 25 November 2026. |
| Package size | Pass | The local submission ZIP and its contents are below 120 MB. The 17-file LaTeX source ZIP independently recompiles to the same 33-page PDF text and bibliography. |

## Output inventory

| File | Submission ZIP bytes | GitHub review bytes |
| --- | ---: | ---: |
| BUILD.md | 2,708 | 2,708 |
| CHECKLIST.md | 4,876 | 4,876 |
| CoverLetter.docx | 13,353 | 13,353 |
| ISSUES.md | 1,147 | 1,147 |
| LaTeX_Source.zip | 1,680,452 | — |
| SupplementaryMaterials.pdf | 3,133,811 | 3,133,811 |
| TableS4.xlsx | 7,966 | 7,966 |
| figures/Figure1.pdf | 155,533 | 155,533 |
| figures/Figure1.png | 368,690 | 368,690 |
| figures/Figure2.pdf | 938,205 | 938,205 |
| figures/Figure2.png | 1,219,213 | 1,219,213 |
| figures/Figure3.pdf | 35,171 | 35,171 |
| figures/Figure3.png | 441,829 | 441,829 |
| figures/Figure4.pdf | 34,120 | 34,120 |
| figures/Figure4.png | 411,454 | 411,454 |
| figures/Figure5.pdf | 32,097 | 32,097 |
| figures/Figure5.png | 414,826 | 414,826 |
| figures/Figure6.pdf | 38,616 | 38,616 |
| figures/Figure6.png | 644,289 | 644,289 |
| figures/GraphicalAbstract.pdf | 89,874 | 89,874 |
| figures/GraphicalAbstract.tif | 226,010 | 226,010 |
| manuscript.docx | 3,345,833 | 3,351,743 |
| manuscript.pdf | 1,322,523 | 2,235,127 |
