# Writing guide for this repository

This is a copy of the `research-paper-story-writing` skill, for writers without access to Claude skills (Gemini, Codex, people). The canonical version is https://github.com/Casey-sketch-cyber/paperwrite/blob/main/skills/research-paper-story-writing/SKILL.md; if the two differ, follow the canonical version. Project-specific content is in [`PAPER_STORY.md`](PAPER_STORY.md).

# Research paper story writing

Based on Peng Sida's public paper-writing template (pengsida.notion.site, github.com/pengsida/learning_research) and its skill packaging (github.com/Master-cai/Research-Paper-Writing-Skills, MIT). Adapted for empirical, computational and policy-relevant journal papers, not only CV/ML conference papers. When quoting or adapting it in public, credit the source.

Core belief: a paper is accepted for its **story**: what new understanding readers gain, why it was not available before, and why the evidence is convincing. Get the story right before writing any sentence. Be meticulous ("如切如磋，如琢如磨"): revise the outline and the English sentences again and again, and judge whether readers will understand.

## 0. How to judge value (applies throughout)

- Judge incremental value, not absolute originality. State exactly what the paper **adds** relative to named prior work: overcomes a limitation, tests a claim at scale, gives a new metric/framework, gives new findings, reframes a problem, or offers a more effective method.
- Similar prior work is context, not a reason to stop. Name the closest work and give the precise remaining difference.
- Do not write "first", "novel" or "unprecedented" unless a documented literature search supports it. Prefer "we show/quantify/test".
- A conditional, honest result ("helps only for X under Y") is a contribution. Report negative results and failures plainly, and turn them into understanding.
- No paper is perfect. Do not stall on an unavailable validation. Bound the claim, state the scope, and use the evidence you have.

## 1. Workflow (in this order)

1. **Key content map** (Section 2). Fill it before any prose.
2. **Figure 1 sketch** (pipeline/teaser, or the graphical abstract for Cell Press), drawn with FigGenie or in PowerPoint (Section 6, Figures). It must show what is new, not the whole system.
3. **Story and Introduction outline**: think backward, then forward (Section 3). At the same time, list the evidence each claim needs (Section 6).
4. **Methods outline, then Methods draft.** Use `\todo{}` for open details.
5. **Results/Experiments outline, then draft**, with figures, tables and captions.
6. **Polish Figure 1 and make the teaser or graphical abstract.**
7. **Related work** (a separate section, or folded into the Introduction for journals).
8. **Adversarial review** (Section 9); revise the Introduction, Methods and Results.
9. **Abstract/Summary** (Section 4), written last from the finished story.
10. **Title** (Section 4).
11. **Repeat review and revision** until no major rejection risk remains.

Timeline for a deadline (start at least 4 weeks ahead):
- Week −4: fix the story, the contributions with their motivation, and the list of evidence; draft the Introduction.
- Week −3: freeze Figure 1; draft the Methods framework; send the Introduction and Methods to the supervisor.
- Week −2: draft Results, Abstract and Related work.
- Week −1: revise, polish figures, make the demo or graphical abstract.

## 2. Key content map (fill this first)

| Key content | Question to answer | Feeds |
|---|---|---|
| Task / question | What does the paper do, and for which application or decision? | Intro part 1 |
| Target quantity | Which metric, quantity or decision should improve? | Intro part 1 |
| Surface failure | What do current methods, standards or claims visibly fail to do? | Intro part 2 |
| Root cause | Why do they fail? Name the underlying technical or conceptual reason. | Intro part 2 |
| Our solution | What did we build or measure that removes that cause? | Intro part 3 |
| Why it works | What property of the solution addresses the root cause? | Intro part 3 |
| Extra contributions | Secondary findings, tools, scenarios | Intro part 4 |
| New understanding (新认知) | What do readers now know that they did not before? | Abstract, Intro, Discussion |
| Evidence | Which result supports each item above? | Results |

Introduction parts:
1. Task, application and target.
2. How current approaches work, their surface failure and its root cause.
3. Our solution and why it addresses the cause.
4. Extra contributions.
5. What the experiments or analyses show.

### Mapping for non-ML papers

Peng's template speaks of technical challenges, SOTA and ablations. Translate:

| ML/CV term | Empirical / computational science equivalent |
|---|---|
| Task | Research question plus the decision it informs (policy, design, practice) |
| SOTA method fails | Current standards, rules of thumb, prior studies or tools cannot answer the question, or answer it only in narrow cases |
| Technical reason | Why: missing variable (time, geometry, heterogeneity), small or unrepresentative samples, unverifiable outputs, a wrong unit of analysis |
| Our pipeline/technique | Metric, framework, model, dataset or corpus-scale analysis |
| Comparison experiments | Against alternative methods, baselines, existing rules, or published claims (including replication) |
| Ablations | Sensitivity analyses: assumptions, parameters, components removed |
| Demo / harder data | Application scenario, transfer to new data or setting, case study |

## 3. Introduction

**Backward first** (answer in writing):
1. What problem do we solve, and why is there no well-established solution? (most important)
2. What are our contributions: a new valuable task or question, a new metric, a new problem formulation, a new technique, or new evidence?
3. Why do they solve the challenge, and what new understanding do they bring? (most important)
4. How can describing prior approaches lead the reader naturally to this challenge and understanding?

**Then forward**: task → prior approaches and their challenge → our contributions → their advantages and new understanding → evidence.

Opening variants:
- **V1.** For a niche task: define the task ("X aims to estimate Y from Z"), then give its applications.
- **V2.** For a familiar task: open with the application directly.
- **V3.** For a new setting (recommended): the general task's importance, then "This paper focuses on the specific setting of ...".
- **V4.** When possible: state the unresolved failure and its reason in the first paragraph.

Challenge paragraphs, for an existing problem: "Traditional approaches [do X], [achieving Y]. However, they [limitation] because [reason]. To address this, recent work [does X']... However, [limitation] because [reason]." Each step leads to the challenge we actually solve. If our key insight has roots in older work, cite that lineage; it signals soundness.

For a new problem: "Achieving X requires meeting several challenges. First... Second... Finally..."

Solution paragraph:
> In this paper, we propose/quantify [name] for [task]. The basic idea is illustrated in Figure 1. Our key idea is [one sentence a reader can follow]. Specifically, [concrete steps]. In contrast to previous approaches, [advantage and why it works]. Another advantage is [...].

The Introduction must say concretely what was done, not only abstract insight.

Forbidden pattern: presenting a naive solution and then patching it step by step. It makes the work look incremental and obvious, even when it is not.

Then give a short evidence summary and a contributions list (2–4 items, each a verifiable claim).

## 4. Abstract / Summary and title

Before writing the abstract, answer:
- What is the problem, and why is it unsolved?
- What is the contribution?
- Why does it work?
- What is the advantage, and what is the new understanding?

Template V2 (recommended): task → challenge of prior approaches (around the challenge we solve) → one-sentence insight → one or two sentences on the contribution that realises it (name the technique; no step-by-step detail; no jumps) → benefits → key quantitative evidence.

Template V3, for several contributions: one sentence per contribution, each naming its advantage.

Title:
- Write the keywords down first.
- The title decides which reviewers you attract.
- Make it informative: technique, task and problem solved.
- Empirical journals (Cell Press style) favour a declarative finding ("X does Y only when Z") over a method name.

## 5. Methods

Pre-writing:
- List the modules. For each, answer: how does it work, why use it, and why does it work? A table or mind map helps.
- Sketch the pipeline figure.

Structure:
- **Overview:** setting in one or two sentences, then the core contribution ("Inspired by [..], we ... Our innovation is ..."), then the figure, then one sentence per subsection.
- **Each subsection** has three elements:
  1. **Motivation**, problem-driven: "A remaining challenge is...", "Previous methods have difficulty in..."
  2. **Design:** data structures plus the forward process. "Given [input], we first..., then..., finally obtain [output]."
  3. **Technical advantage:** why this design helps.
- Draft the design first, then add the motivation and the advantage.
- Implementation details (hyperparameters, normalisation, budgets) go at the end, or in STAR Methods or a supplement.

Check the methods afterwards:
- Reverse-outline them.
- Every sentence's purpose must be clear to the reader: why are we doing this?
- Keep terms consistent; never rename a concept midway.

## 6. Results / Experiments

Plan the evidence from the claims:
- **Claims → contributions → one validation analysis per contribution.**
- **Pipeline → modules and key parameters → one ablation or sensitivity analysis each.**

Answer three questions:
1. Is it better than, or different from, the alternatives? (comparisons and replication)
2. Does each component or assumption matter? (ablations and sensitivity)
3. How far does it go? (harder data, a new setting, an application scenario; this has large impact)

Writing the results:
- In journal Results, each subsection heading states a finding (a claim), and the text gives the evidence.
- Order the subsections by the story, not by the order the experiments were run.
- Captions state the setting, protocol and notation, plus at most one sentence of result. Do not repeat the discussion in captions.
- Report uncertainty (CIs, n), support limits, and failure cases.

Tables:
- Caption above the table.
- booktabs rules; no vertical lines; minimal horizontal lines.
- Metric direction and units in the headers; consistent decimals.
- One message per table; highlight key numbers subtly.

Figures:
- First impression decides reviews. Use a beautiful teaser or pipeline figure, clean result plots and tidy layout.
- The pipeline figure highlights what is new; the text makes it understandable.
- A framework figure is not there to make the reader understand; it is there to make the novelty stand out, and the text does the explaining (Peng Sida). So the figure holds pictures, shapes and short names (model names, two- or three-word panel titles), no explanatory sentences and, as a rule, no numbers: numbers go in the caption and the text. Mark what is new by colour and position, and leave everything else white and grey.
- Draw the pipeline and teaser figures with [FigGenie](https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill) (MIT): brief, spec, exemplars of the venue's Figure 1s, a hand-written SVG in pt, then `check.py` until the lint reports 0 errors and the rendered PNG has been looked at. Export PDF for the paper (`embed_fonts.py`, `export_pdf.py`) and an editable PowerPoint copy (`svg2pptx.py`), which keeps Peng Sida's practice of PowerPoint pipeline figures; strip the theme shadow that svg2pptx inherits. Follow its print rules (body 6.5 pt, at most three sizes, nothing below 6 pt) and give red/green verdicts a tick or cross as well. Its exemplar figures and parts are cut from other papers: study them, never paste them into a figure.
- Without FigGenie, draw the pipeline and teaser figures in PowerPoint (or Keynote): native shapes, text boxes and arrows, with result thumbnails embedded as images. Keep the editable `.pptx` in the repository next to the paper and export PDF for submission. Do not draw pipeline figures with plotting libraries or Mermaid; use scripts only for data plots.
- Place single-column figures in the right column where the layout allows.

## 7. Related work and Discussion

Related work:
1. List the closest papers first. Missing one is a common rejection reason.
2. Choose 2–4 topics.
3. For each topic: scope → representative approaches → limitation relevant to our challenge → how we differ (mechanism, assumption or scale, not marketing).

Discussion/Conclusion:
- Restate the problem and key idea, the strongest evidence, and the practical impact or new understanding.
- **Limitations are mandatory.** Frame them as scope boundaries set by the task or setting (data regime, assumptions, deployment scope) and the future work they suggest.
- Do not list technical defects. Something is a defect only if the work is worse than the current state of practice on a key metric; otherwise it is a scope boundary. When a scope boundary can be stated as a design choice in Methods ("X measures A, not B"), say it there, and keep the Limitations sentence short and pointed to future work.
- Focus the paper on its one central point and make that logic tight. A paper does not need to cover every angle.
- Distinguish a scope limitation from a defect, i.e. losing on a key metric versus the current state of the art. If there is a real defect, state it honestly and bound the claim.

## 8. Paragraph and sentence craft

- **One paragraph, one message.** The first sentence states the message: the pyramid principle, with the claim on top and support below.
- **Self-contained nouns.** Define every new term before use. Ask whether the reader knows this word at this point.
- **Sentence flow.** Each sentence continues the previous one through cause, contrast, consequence, refinement or example. If it does not, add a transition. A new noun appearing abruptly breaks flow.
- Transition words:
  - cause: thus, therefore, as a result
  - contrast: however, in contrast, although
  - example: for instance, such as
  - addition: moreover, furthermore
  - summary: in short, overall
- **Reverse outlining after each section.** Write the thesis, every topic sentence and the support points. Check that topic → thesis and support → topic. Rewrite or delete paragraphs that do not map.
- If flow stays weak, add temporary headers and explicit transitions while revising, and remove them later.

### Writing with LLM help (outline first)

- Outline coarse to fine: section → subsection → paragraph → sentence. Know what every sentence will say before writing English. Chinese outlines are fine.
- Write each sentence from its outline line, then polish with mixed Chinese and English prompts ("把这句改得更学术、更简洁: ..."), or ask for word choices. Finally polish it yourself.
- Refine the outline while writing: clear paragraphs come from repeatedly revised outlines.

### Revision loop for any section or paragraph

1. **Encode** the raw text into a high-level outline.
2. **Analyse:** does the outline express what we want to say (design and motivation)? Is the logic smooth? An LLM can help find jumps.
3. **Improve** the outline.
4. **Decode** it back into English.

For sentence flow, check each pair of sentences:
- Does the second continue the first?
- If not, is there a transition?
- Is any new noun abrupt?

## 9. Adversarial self-review (before every submission)

Append this question list to the draft and answer each item with evidence from the paper. Mark each `pass`, `needs revision` or `needs new analysis`.

1. **Contribution:**
   - What new knowledge do readers gain?
   - Is the failure we address meaningful and not trivial?
   - Is the idea non-obvious, or is the gain predictable?
   - Which novelty type do we claim: task, metric, pipeline, module, design choice, finding or insight?
2. **Clarity:**
   - Is the work reproducible from the text?
   - Does every module have a motivation?
   - Are terms and notation consistent?
   - Does each paragraph carry one message?
3. **Strength of results:**
   - Is the gain or finding meaningful, not marginal?
   - Is it consistent across datasets and settings?
   - Are failures reported?
4. **Completeness:**
   - Are the key comparisons, baselines and metrics present?
   - Are the sensitivity analyses there?
   - Is the data challenging and representative enough?
5. **Soundness:**
   - Is the setting realistic?
   - Are any assumptions unreasonable?
   - Is it robust without per-case tuning?
   - Do the benefits outweigh the new limitations?

**Hard rule:** every claim, especially in the Abstract and Introduction, must be correct and supported by a result. Otherwise add evidence, or weaken or remove the claim. Every number must trace to a committed result file.

Before submission, ask the supervisor or co-authors for as many critiques as possible. Each fixed critique is one fewer reviewer objection.

## 10. Venue formats (verify against the live author guide)

**Cell Press / iScience:**
- Summary of about 150 words, one paragraph, no references.
- Highlights: 3–4 bullets of 85 characters or fewer each.
- eTOC blurb and graphical abstract.
- Introduction → Results, with claim-style subsection headings → Discussion, including a "Limitations of the study" subsection.
- STAR Methods at the end: key resources table; resource availability (lead contact, materials, data and code availability); method details; quantification and statistical analysis.
- Supplemental information.
- Editors look for interdisciplinary significance and what the field now understands differently. ML components need strong benchmarking.

**MDPI:** Abstract of 200 words or fewer, IMRaD, Data Availability statement.

**CV/ML conferences:** Abstract → Introduction with a contributions list → Related work → Method → Experiments (comparison, ablation, demo) → Conclusion with limitations.

## 11. Output contract for each drafting or revision request

1. A compact outline of the section (3–7 bullets), in Chinese if the user writes Chinese.
2. Revised paragraphs in English, each labelled with its role: opening, challenge, method, advantage, evidence or limitation.
3. A claim–evidence map, one line per claim: `Claim: ... | Evidence: <figure, table or result file> | Status: supported / needs evidence / weaken`.
4. A short self-check covering one message per paragraph, flow, terminology consistency, unsupported claims and missing evidence.
