# Shaping Agent Output So Humans Understand and Decide Faster: An Evidence-Graded Guide for a Claude Code Skill

The most important finding: put the decision or conclusion first, then layer the detail, and make the reader do a little active work to check they understood. Of all the ideas below, only working-memory limits, signaling and coherence (cut what doesn't help), matching the format to the task (tables for looking up values, charts for patterns, diagrams for structure), and retrieval-based checks have strong, replicated evidence. Much of the rest, including BLUF, the Minto pyramid and executive summaries, is sound practitioner craft with little controlled testing behind it.

**Note on sourcing.** No live web search was available for this report. A research sub-task returned memory-based summaries only, and the tools connected in this session (an Atlassian workspace) held nothing relevant.\[1\]\[2\] Every claim below comes from the well-known primary literature as I know it. Figures I am less sure of are marked "(verify)". Check any quoted number against the original before you treat the skill as authoritative.

## TL;DR

- **Lead with the answer, keep it within working-memory limits, and disclose the rest on demand.** Working memory holds about 4 chunks (Cowan 2001), not 7±2. Cutting extraneous material and adding clear signaling are among the best-replicated design effects in multimedia learning (Mayer). BLUF, the pyramid structure and progressive disclosure are how you apply those findings to documents. Their evidence comes mostly from practitioners, but they fit the lab findings.
- **Pick the format from the task, not from taste.** Use tables to look up exact values and compare options on many attributes. Use charts that encode by position or length for trends and magnitudes (Cleveland & McGill 1984, replicated by Heer & Bostock 2010). Use diagrams for structure, flow and spatial relations (Larkin & Simon 1987). Use prose for argument, causation and nuance. A decorative visual hurts more than having no visual (the seductive-details effect).
- **Polished AI output invites over-reliance, so design for checking.** State confidence on a calibrated scale, say what was left out, show evidence the reader can verify, and ask for a small act of retrieval or prediction before the reader accepts a high-stakes decision. Cognitive forcing functions reduce over-reliance (Buçinca et al. 2021). Unguarded AI help improved practice performance but lowered later unaided exam scores (Bastani et al., PNAS 2025).

---

## Part A: The Skill

### A1. Ranked principles (by evidence × impact)

| Rank | Principle | Evidence label | Why it speeds things up |
|---|---|---|---|
| 1 | **Respect working-memory limits.** About 4 new chunks at once. Group related items and name the groups. | Replicated (Cowan 2001; cognitive load theory) | Material that goes over capacity has to be re-read and gets lost. Chunking turns many items into a few. |
| 2 | **Answer first, detail on demand** (BLUF, pyramid, progressive disclosure). | Practitioner, strongly supported indirectly (signaling, pre-training and segmenting principles) | The reader can stop once they have enough. The headline gives them a frame for fitting in the detail. |
| 3 | **Cut extraneous material** (coherence principle, seductive details). Don't say the same thing twice in two forms (redundancy). | Replicated (Mayer; seductive-details meta-analyses) | Every irrelevant item uses up attention and can pull the reader toward the wrong frame. |
| 4 | **Match the format to the task** (cognitive fit). Tables for values, position/length charts for patterns, diagrams for structure and flow. | Replicated (Vessey 1991; Cleveland & McGill 1984; Heer & Bostock 2010; Larkin & Simon 1987) | The wrong format makes the reader translate in their head. The right one turns the work into simple perception. |
| 5 | **Signal structure.** Headings, labels, highlights, consistent placement. | Replicated, moderate effect (Mayer signaling principle) | It lets readers scan and jump straight to the part they need. |
| 6 | **Make uncertainty explicit and calibrated.** Use numeric or standardized likelihood terms, give confidence separately, and say what was left out. | Replicated for numbers beating vague words (Dhami & Mandel; Friedman et al. 2018). Practitioner for the ICD 203 format. | The reader can weigh how much to trust a claim without reconstructing how it was made. |
| 7 | **Use worked examples and concrete cases for novices, less for experts.** | Replicated (worked-example effect; Kalyuga expertise reversal) | Novices learn the pattern faster from examples. For experts the same help just gets in the way. |
| 8 | **Make the reader generate something to check understanding** (predict, explain back, answer a question). | Replicated (testing effect; self-explanation; cognitive forcing) | It catches the illusion of understanding and makes the learning stick. |

### A2. Content-type → format decision table

| Content | Reader's job | Default format | Add when | Avoid |
|---|---|---|---|---|
| **Short answer / factual question** | Know X | 1–3 sentences, answer first | A link or "details:" section if they may need to verify | Preamble, restating the question |
| **Plan (implementation)** | Approve, adjust, sequence | BLUF line (goal + approach + biggest risk), then a numbered steps list, then risks/open questions | A dependency diagram if there are more than 5 steps with non-linear order | A wall of prose. Steps without done-criteria. |
| **Architecture / system design** | Build a mental model | One-paragraph summary, then a box-and-arrow diagram (C4 context/container level), then a component table (name, responsibility, interfaces) | A sequence diagram for any important runtime flow | A diagram with no legend or no labels on arrows. Decorative cloud icons. |
| **Code review** | Decide merge/block, learn what changed | Verdict + count by severity, then findings ordered by severity, each with file:line, issue, why it matters and a suggested fix, then the summary of the change | Diff snippets inline. Group findings by theme if there are many. | Equal weight for nits and blockers. Praise padding. |
| **Diff / change summary** | Understand the delta | "What changed / why / risk" in 3 lines, then a before/after table or a unified diff | A behavioural before/after example | Narrating the diff line by line |
| **Status update** | Is it on track? Do I need to act? | Status (on track / at risk / blocked) + the ask, first line. Then done / next / blockers as bullets. | A small table if there are several workstreams | Burying the blocker or the ask |
| **Research findings** | Believe and act on conclusions | Layered summary (A3.1) with a confidence label on each finding | A comparison table of sources/options. A chart if there is quantitative data. | Hiding disagreement between sources. False precision. |
| **Trade-off / decision between options** | Choose | Decision brief (A3.2): recommendation first, then an options × criteria table | A sensitivity note on what would change the recommendation | Pros/cons in paragraphs. Options with no recommendation. |
| **Quantitative comparison / trend** | See pattern or magnitude | A chart: dot or bar for comparison, line for trend | A table of exact values next to the chart if precision matters | Pie or 3D charts, dual axes, colour-only encodings |
| **Exact values / lookup** | Find a number | Table | Sorting by the decision-relevant column | Prose lists of numbers |
| **Process / workflow** | Follow or reason about steps | Numbered list. A flowchart if there are branches. | A swimlane diagram if several actors are involved | A flowchart for a linear 4-step process |
| **Complex model with parameters** (performance, cost, capacity) | Build intuition about sensitivity | An interactive explorable (sliders) *if* reuse justifies building it | A static "key scenarios" table as a fallback | Building interactivity for one-off content |
| **Teaching an unfamiliar concept** | Learn and transfer | Concrete worked example, then the general principle, then a check question | An analogy, but say where it breaks down | Abstract definition first with no example |

**Decision rule an agent can apply:**
1. What is the reader's *job*: know, decide, approve, learn, or monitor? Lead with whatever that job needs.
2. Does the content have **many items × many attributes**? Use a table.
3. Is it **quantitative and the pattern matters more than exact values**? Use a chart that encodes by position or length.
4. Is it **structure, flow, dependency, or spatial**? Use a diagram, and only if it has more than 4–5 elements or non-linear relations.
5. Is it **argument, causation, caveats, narrative**? Use prose.
6. Will the reader likely need **less than half of it**? Give a short answer with detail on demand: collapsed sections, links, "ask me for X".
7. Is it a **reusable model the reader will poke at many times**? Consider an interactive page. Otherwise don't.

### A3. Templates

#### A3.1 Layered summary (research findings, long reports, anything over one screen)
Use this when the reader may stop at any depth.
```
**Bottom line:** <one sentence: the answer / recommendation>
**Confidence:** <high/moderate/low> because <one clause on evidence quality>

**Key points** (≤4)
- <finding> — <evidence label>
- ...

**What this doesn't cover / what I couldn't verify:** <1–3 items>

<details> Detail sections, each headed by its own one-line conclusion
```
Each layer has to stand on its own. The test is that a reader who stops after any layer still has a correct, if less detailed, picture.

#### A3.2 Decision brief (trade-offs, approvals, design options)
Adapted from BLUF and commander's intent (purpose, key tasks, end state), with ICD 203 confidence language.
```
**Decision needed:** <what, by when, who>
**Recommendation:** <option> — <one-line reason>
**Intent:** <the goal the decision serves, so the reader can judge variants>

| Criterion (weight) | Option A | Option B | Option C |
|---|---|---|---|
| ... | ... | ... | ... |

**Key risk of recommended option:** <and mitigation>
**What would change my mind:** <observable condition>
**Confidence:** <level> — <basis>; **Not considered:** <scope limits>
```
"What would change my mind" is the most useful line for a fast decision-maker. It turns the recommendation into something they can test.

#### A3.3 Diagram selection guide
| Content | Diagram | Notes |
|---|---|---|
| System parts and connections | Box-and-arrow (C4 context/container) | Label every arrow with what flows along it. Keep to ≤7–9 boxes per view and nest anything deeper. |
| Runtime interaction over time | Sequence diagram | Best for request/response, async and race issues |
| Branching logic | Flowchart / decision tree | Only if there are 2 or more branches |
| State/lifecycle | State machine | Good for UI states and order/job status |
| Data model | ER diagram or table | A table is often enough for under 6 entities |
| Several actors in a process | Swimlane | |
| Hierarchy / decomposition | Tree / indented outline | An outline in a terminal |
| Timeline / plan | Gantt or ordered list with dates | |
| Quantities | Chart, not a diagram | See the Cleveland–McGill ranking |
In a terminal, prefer Mermaid source or a compact ASCII sketch. Never render a diagram that only says what one sentence would say.

#### A3.4 Comparison table
Use this for 2 or more options across 3 or more attributes.
- Put options in columns and criteria in rows when there are few options. Swap them when there are many options.
- Put the most decision-relevant criterion first. Sort rows by importance, not alphabetically.
- Use consistent units, and mark the winner per row (bold, or ✓) sparingly.
- Add a final "verdict" row and one line of text saying what the table means.
- Keep cells to a few words. If a cell needs a paragraph, move it to a footnote.

#### A3.5 Diff / before–after
`Before → After → Why → Risk` in a 4-row table or 4 lines. Show a behavioural example ("calling X now returns Y") before the code diff.

### A4. Anti-patterns and why they slow readers down

| Anti-pattern | Why it costs time | Evidence |
|---|---|---|
| **Wall of text** | There is no structure to scan, so the reader has to hold everything in working memory to find the point | Signaling principle (replicated). Web-reading eye-tracking (Nielsen, practitioner). |
| **Buried lede** | The reader processes detail with no frame and has to re-read once the conclusion arrives | Advance-organizer / pre-training research (replicated, moderate). BLUF (practitioner). |
| **Decorative diagram / seductive detail** | It draws attention and primes the wrong schema | Seductive-details effect (replicated, meta-analytic) |
| **Diagram + prose saying the same thing** | The reader processes the same content twice | Redundancy principle (replicated, but depends on expertise) |
| **Label far from what it labels** (legend at the bottom, code referenced 3 screens away) | Split attention: the reader has to search back and forth | Split-attention / spatial contiguity (replicated) |
| **False precision** ("37.4% faster" from one run) | It signals certainty that isn't there and misleads the decision | Practitioner, and consistent with calibration research |
| **Summary that hides uncertainty or disagreement** | The reader can't calibrate trust, so they either over-rely or re-verify everything | Automation-bias literature (replicated) |
| **Vague likelihood words** ("possibly", "may") | Readers' interpretations vary widely | Kent 1964; Dhami & Mandel (replicated) |
| **Equal weight for every item** (nits = blockers) | The reader has to do the triage themselves | Practitioner (code review) |
| **Pie/3D/dual-axis charts, colour-only encodings** | Angle, area and volume are judged less accurately than position or length | Cleveland & McGill 1984; Heer & Bostock 2010 (replicated) |
| **Over-scaffolding experts** | Experts have to reconcile redundant guidance with what they already know | Expertise reversal effect (replicated) |
| **Polished, confident tone with no visible evidence** | It invites skimming and acceptance without verification | Bansal et al. 2021; Lee et al. 2025 (single studies, consistent direction) |

### A5. Agent guidance by medium

**Terminal (Claude Code CLI)**
- First line: outcome or verdict ("Tests pass; 2 files changed; 1 risk to review"). Keep it to 3–6 lines before any detail.
- Use short bullets and fenced code. Tables only if they are narrow (≤4 columns), because wide tables wrap badly.
- Diagrams: Mermaid source or a small ASCII tree. Don't draw elaborate ASCII art.
- Defer to files: write long reports to a markdown file and print a summary plus the path.
- End with "Needs you:" followed by the concrete decision or action, if there is one.

**Chat**
- Answer in the first sentence. Use headers only if the reply is longer than about 3 short paragraphs.
- Offer depth instead of dumping it: "I left out X and Y; ask if you want them."
- One table at most per reply, unless the reply is a comparison.

**Doc (design doc, report, PR description)**
- Use the full layered structure: title that states the conclusion, a TL;DR, then sections each led by a one-line conclusion.
- Use collapsible sections for appendices. Put diagrams near the text that refers to them.
- For decisions, write a narrative memo with the reasoning written out, not slide-style fragments (Amazon's practice). The full sentences expose gaps in reasoning that bullets hide.

**Signaling confidence and omissions (all media)**
- Use one likelihood scale throughout. Map words to the ICD 203 bands: almost no chance 1–5%, very unlikely 5–20%, unlikely 20–45%, roughly even 45–55%, likely 55–80%, very likely 80–95%, almost certain 95–99%. Or give numbers directly.
- Keep **likelihood** ("likely the cache is stale") separate from **confidence** ("moderate confidence: inferred from logs, not reproduced").
- Always include a "Not checked / out of scope" line when the output summarizes something the reader can't see.
- Mark what was *verified* (ran the test, read the file) differently from what was *inferred*.

### A6. Comprehension checks (did they understand, not just read?)

These come from retrieval practice, self-explanation, prediction and cognitive forcing research. Scale them to the stakes. Keep them optional for routine output and use them by default for irreversible decisions or onboarding.

1. **Predict before reveal.** "Before I show the fix: which component do you think drops the event?" This applies cognitive forcing (Buçinca et al. 2021). It is the strongest guard against blind acceptance.
2. **Explain-back.** Ask the user to state the decision and its main risk in one sentence, then compare with the agent's version. This is the self-explanation effect (Chi), which the Dunlosky review rates as moderate utility.
3. **Change-impact question.** "If we double traffic, which part of this design breaks first?" This tests whether they have a working model, not just memory of the text.
4. **Spot-the-error / verify-one.** Point the reader at one specific claim they can check in under a minute: a file:line, a test command, a source.
5. **Teach-back for onboarding.** After an explanation of a codebase area, ask 2–3 short retrieval questions at the end of the session, and again on a later day (spacing).
6. **Decision replay.** For decision briefs, the "what would change my mind" line becomes a check: can the reader name a condition that would flip the choice?

Reading time, "looks good", or a thumbs-up does not show understanding. People reliably overrate how well they understand (Rozenblit & Keil 2002).

---

## Part B: Evidence Review

### B1. The science of comprehension and decision speed

**Working memory capacity.** Miller (1956), "The Magical Number Seven, Plus or Minus Two", is widely misquoted. Miller was partly playful, and his span figures included items that people had already chunked. Cowan (2001, *Behavioral and Brain Sciences*) reviewed evidence from tasks that prevent chunking and rehearsal and concluded that capacity is about **3–5 chunks, roughly 4**. **Label: replicated (Cowan). "7±2" as a design rule is folklore.**

**Chunking and expertise.** Chase & Simon (1973) found that chess masters recalled briefly shown game positions far better than novices, but the advantage largely disappeared for random positions. Later work (Gobet & Simon) found a small residual advantage. Expertise is stored as large, meaningful chunks. **Replicated.** Chi, Feltovich & Glaser (1981) found that physics experts sort problems by deep principle while novices sort by surface features. **Replicated.** *Design implication:* group information by meaningful structure (by risk, by subsystem), and name the groups.

**Cognitive load theory (Sweller).** Load is intrinsic (the complexity of the material), extraneous (caused by presentation) or germane (spent on learning). Design should minimize extraneous load. Effects derived from it include worked examples, split attention, redundancy and expertise reversal. **The core effects are replicated.** Critics argue the three-part load model is hard to measure directly, and recent versions of the theory have revised the "germane" category. **Label: theory contested in its details, effects replicated.**

**Expertise reversal (Kalyuga, Ayres, Chandler & Sweller 2003).** Guidance that helps novices (worked examples, integrated explanations) can hurt more knowledgeable learners. **Replicated.** *Implication:* adapt how much detail you give to the reader. A senior engineer reviewing their own codebase needs less scaffolding than one onboarding.

**Dual coding (Paivio) and multimedia learning (Mayer).** Paivio's theory holds that verbal and imagery codes are separate and add together. The finding that concrete words are remembered better than abstract ones is robust. Mayer's cognitive theory of multimedia learning yields principles tested in many experiments: multimedia (words + pictures beat words alone), coherence, signaling, redundancy, spatial and temporal contiguity, segmenting, pre-training, modality. Mayer's own summaries report median effect sizes that are mostly medium to large. Most studies are short lab experiments with students and explanatory science content, and independent meta-analyses tend to find smaller effects than the original lab studies. **Label: replicated, with boundary conditions.** The modality effect (narration beats on-screen text) is weaker in later work, so treat it as contested. Signaling has a meta-analytic effect that is positive but smaller than the others.

**Seductive details.** Interesting but irrelevant material lowers learning. Meta-analyses (Rey 2012; Sundararajan & Adesope 2020) find a reliable negative effect, small to moderate in size (verify the exact g). **Replicated.**

**Learning styles.** Pashler, McDaniel, Rohrer & Bjork (2008, *Psychological Science in the Public Interest*) found almost no studies with the design needed to test the "meshing" hypothesis, and the studies that did use it contradicted it. **Debunked.** Don't tailor format to "visual vs verbal learners". Tailor it to the *content* and to the reader's *prior knowledge*.

**Pre-attentive processing.** Treisman & Gelade (1980), feature integration theory: single features such as colour, orientation, size and motion "pop out" in parallel, while combinations of features need serial search. Healey & Enns (2012, *IEEE TVCG*) review its use in visualization. Wolfe's guided search model has refined the idea, and the strict line between pre-attentive and attentive processing is contested. **Label: replicated phenomenon, contested theory.** *Implication:* use one salient channel (e.g., red for blockers) for the one thing that has to stand out. Several salient channels compete with each other.

**"Visuals are processed 60,000× faster than text" / "90% of information is visual."** No primary research source has been found for these, and they appear to come from marketing material. **Debunked / unsourced.** "A picture is worth a thousand words" is a proverb. Larkin & Simon (1987) give the real answer: a diagram is *sometimes* better.

**Larkin & Simon 1987, "Why a Diagram is (Sometimes) Worth Ten Thousand Words."** A diagram and a sentence can contain the same information yet differ in how much work it takes to use it. Diagrams help when they group related information by location, which cuts search, and let readers infer things perceptually. They don't help when the task doesn't use those features. **A foundational theoretical analysis, widely supported.**

**Animation.** Tversky, Morrison & Bétrancourt (2002) found that animations often do no better than well-designed static graphics once you control for information content. **Replicated review finding.** *Implication:* animated or interactive content needs a reason.

**Ego depletion.** The large multi-lab replication (Hagger et al. 2016, 23 labs) found an effect near zero. **Contested / failed replication.** Don't design around "decision fatigue" claims drawn from it.

**Recognition-primed decision making (Klein).** Studies of fireground commanders and other experts found that experienced people usually don't compare options. They recognize the situation as typical, take the first workable option, and test it with mental simulation. **Replicated in naturalistic field studies, which are mostly qualitative.** *Implication:* experts decide faster when shown cues and patterns ("this looks like the N+1 query problem we had in X") than when given exhaustive option matrices. Novices benefit more from explicit comparison.

**Sensemaking.** Weick (1995) treats sensemaking as building plausible accounts in organizations. Pirolli & Card (2005) describe a two-loop model for intelligence analysts: a foraging loop (search, filter, collect) and a sensemaking loop (schematize, form hypotheses, present). Information foraging theory (Pirolli & Card 1999) says people follow "information scent". **Theoretical models with empirical support.** *Implication:* headings and summaries that give a strong, accurate scent let readers find the part they need quickly.

### B2. Presentation methods

| Method | Suits | Evidence | Label |
|---|---|---|---|
| **BLUF / Minto pyramid** (answer, then grouped supporting arguments, SCQA intro) | Decisions, recommendations, status | Military doctrine (Army writing standards, AR 25-50) and the Minto consulting tradition. Indirect support from advance organizers, pre-training and signaling. Few direct controlled trials. | Practitioner, theoretically supported |
| **Progressive disclosure / layered documents** | Long or mixed-audience content | Strong HCI practitioner tradition (Nielsen). Indirect support from segmenting and expertise reversal. | Practitioner + indirect lab |
| **Executive summaries** | Any document over about 2 pages | Common practice. Little controlled evidence on speed. A risk is that readers stop at the summary, so the summary must be accurate on its own. | Practitioner |
| **Tables vs prose** | Tables for many items × attributes and lookup. Prose for reasoning. | Vessey's cognitive fit (1991): tables beat graphs for symbolic/exact tasks, graphs beat tables for spatial/trend tasks. Replicated in decision-support research. | Replicated |
| **Diagrams** | Structure, flow, spatial and causal relations | Larkin & Simon 1987. Multimedia principle (Mayer). Diagrams must be explanatory, not decorative. | Replicated (with conditions) |
| **Data visualization** | Quantitative patterns | Cleveland & McGill (1984): accuracy ranked position on common scale > position on non-aligned scales > length, direction, angle > area > volume, curvature > shading, colour saturation. Heer & Bostock (2010) replicated the ranking via crowdsourcing. Tufte's data-ink ratio and chartjunk ideas are influential, but Bateman et al. (2010) found embellished charts were remembered better with no loss of accuracy. | Ranking replicated. Tufte's minimalism partly contested. |
| **Worked examples** | Teaching procedures and patterns to novices | Sweller & Cooper (1985); Renkl's research; fading of steps. Effect reverses with expertise. | Replicated |
| **Analogies** | Transferring structure from a known domain | Gentner's structure-mapping research: analogies work when the relational structure matches, and comparing two cases beats studying one (Gentner, Loewenstein & Thompson 2003). Risk of carrying over the wrong features. | Replicated (lab) |
| **Comparisons / diffs** | Change, choosing options | Comparison of cases aids schema learning (Gentner). Diffs are standard developer practice. Code review research (Bacchelli & Bird 2013) found understanding the change is the main challenge. | Replicated (comparison) / practitioner (diff format) |
| **Interactive explorables** (Bret Victor 2011) | Models with parameters, building intuition | Persuasive essays and examples, but little controlled evidence that they speed comprehension. Interactivity can add load. | Practitioner / thin evidence |

### B3. Decision-ready briefing in high-stakes fields

- **Military BLUF and commander's intent.** Army doctrine (ADP/FM 6-0) defines intent as the purpose, key tasks and desired end state. It lets subordinates act sensibly when the plan breaks down. **Practitioner (doctrine).** *Transfer:* every plan or task delegated to an agent, and every plan an agent proposes, should state its intent so variants can be judged.
- **Checklists (aviation, surgery).** Haynes et al. (2009, *NEJM*), the WHO Surgical Safety Checklist in 8 hospitals: death rate fell from 1.5% to 0.8%, and inpatient complications from 11.0% to 7.0%. **Single large pre/post study.** Later results are mixed: an Ontario-wide rollout (Urbach et al. 2014, *NEJM*) found no significant mortality reduction. **Label: contested at scale. Works best where it changes team communication, not as a box-ticking exercise.** *Transfer:* short, specific checklists for code review and release, covering the things people skip under pressure.
- **SBAR (Situation, Background, Assessment, Recommendation).** Systematic reviews (e.g., Müller et al. 2018, *BMJ Open*) find moderate evidence that it improves communication, especially over the phone, with weaker evidence on patient outcomes. **Replicated for communication, weak for outcomes.** *Transfer:* SBAR fits incident updates and escalations well.
- **Intelligence analysis.** Heuer's *Psychology of Intelligence Analysis* (1999) catalogues cognitive biases and proposes Analysis of Competing Hypotheses (ACH). Controlled tests of structured analytic techniques are sparse, and some find little gain in accuracy. Dhami, Mandel and colleagues found ACH did not reliably improve judgments, and Chang, Berdini, Mandel & Tetlock (2018) critique SATs as largely untested. **SATs: practitioner, contested.** Sherman Kent's "Words of Estimative Probability" (1964) showed that analysts read the same phrases very differently. ICD 203 (2015) standardizes likelihood terms and separates likelihood from confidence. Mandel, Dhami and Friedman et al. (2018) show that numeric probabilities communicate better and that rounding estimates loses accuracy. Tetlock's forecasting tournaments found that training in probabilistic reasoning improved accuracy. **Numeric beats verbal: replicated.**
- **Amazon six-pager.** In his 2017 shareholder letter, Bezos describes "narratively structured six-page memos" read in silence at the start of meetings, and notes that Amazon doesn't use PowerPoint. He argues full sentences force clearer thinking. **Practitioner (one company's practice).** *Transfer:* write decision docs as reasoned prose with a table for the options. A silent reading period, or a self-contained doc, means everyone starts from the same context.

**What transfers to software work:** answer and ask first (BLUF); state intent; use a standard short structure for recurring message types (SBAR for incidents, a decision brief for trade-offs); use calibrated likelihood plus a separate confidence statement; write prose for reasoning and tables for options; give a checklist for the steps people skip.

### B4. Learning fast

- **Dunlosky et al. (2013), *PSPI*.** Rated ten techniques. **High utility:** practice testing and distributed practice. **Moderate:** elaborative interrogation, self-explanation, interleaved practice. **Low:** summarization, highlighting, keyword mnemonic, imagery for text, rereading. **Replicated review.** Note that rereading and highlighting, the most common study habits, are among the weakest.
- **Testing effect.** Roediger & Karpicke (2006): after one week, students who repeatedly took tests on a passage recalled far more than those who repeatedly restudied it (about 61% vs 40%, verify), even though restudying looked better at the 5-minute test. **Replicated.**
- **Spacing.** Cepeda et al. (2006 meta-analysis; 2008): spaced study beats massed study. The best gap grows with how long you need to retain the material, at roughly 10–20% of the retention interval for intervals of about a week, and a smaller proportion for longer ones. **Replicated.**
- **Self-explanation.** Chi et al. (1989; 1994): students who explain examples to themselves learn more. **Replicated.**
- **Concept maps.** Nesbit & Adesope (2006, *Review of Educational Research*): studying and building concept maps beat reading text, lists or lectures, with moderate effects. Schroeder et al. (2018) found similar results (verify the exact g). **Replicated meta-analytically.**
- **Expert–novice gap.** Experts see deep structure (Chi 1981) and recognize patterns (Chase & Simon; Klein). Novices need explicit structure and worked examples.
- **Program comprehension.** Developers spend a large share of their time understanding code. Xia et al. (2018, *IEEE TSE*) measured about 58% of time spent on comprehension in a field study. **Single large field study.** Storey's work on cognitive models of comprehension, and Siegmund's fMRI and measurement studies, support top-down (hypothesis-driven) and bottom-up (line-by-line) strategies being mixed depending on familiarity. Bacchelli & Bird (2013, ICSE): developers expect code review to find defects, but its main outcomes are knowledge transfer and awareness, and understanding the change is the main difficulty.
- **Diátaxis** (Daniele Procida) separates tutorials (learning), how-to guides (tasks), reference (lookup) and explanation (understanding). **Practitioner framework.** It is a useful way to make an agent say which reader job it is serving.

**How an AI assistant can speed up learning without an illusion of understanding:** give a map before detail (a concept map or architecture sketch of the codebase); lead with worked examples that trace one real request through the system; ask the learner to predict and explain before revealing; schedule short retrieval checks across sessions; then fade the scaffolding as their skill grows. The **illusion of explanatory depth** (Rozenblit & Keil 2002) means people believe they understand mechanisms until asked to explain them step by step. Explaining is the check.

### B5. AI-specific risks

- **Automation bias and complacency.** Parasuraman & Manzey (2010, *Human Factors*) review errors of omission and commission with automated aids. These occur in experts as well as novices and aren't fixed by training alone. **Replicated.**
- **Explanations can increase over-reliance.** Bansal et al. (CHI 2021) found that AI explanations raised acceptance of AI recommendations whether or not they were correct, and did not beat simply showing the AI's confidence. **Single study (multi-task), consistent with related work.**
- **Cognitive forcing functions.** Buçinca, Malaya & Gajos (CSCW 2021): designs that make people decide before seeing the AI's answer, or that slow them down, reduced over-reliance compared with simple explainable-AI designs. Users liked them least. **Single study, replicated in direction by related work.** *Implication:* use forcing only where the stakes justify the friction.
- **Generative AI and critical thinking.** Lee et al. (CHI 2025, Microsoft Research/CMU) surveyed 319 knowledge workers and collected 936 examples. Higher confidence in GenAI was associated with less critical thinking, and higher self-confidence with more. Effort shifted toward verifying and integrating output. **Single self-report survey, correlational.**
- **Learning harm.** Bastani et al. (PNAS 2025) ran a field experiment with about 1,000 Turkish high-school students. Unguarded GPT-4 access ("GPT Base") improved practice performance by about 48%, and a tutor version with guardrails by about 127%. With access removed, GPT Base students did about 17% worse on exams than controls, while the tutor version largely avoided this harm. **Single large RCT (verify figures).**
- **Skill formation in coding.** Anthropic's study (Shen & Tamkin, early 2026) of developers learning an unfamiliar Python async library found that those with AI help scored lower on a later comprehension quiz, with the largest gap on debugging. They were not significantly faster. Participants who used the AI for conceptual questions or asked for explanations with the code kept more of their learning than those who handed the task over. **Single RCT (verify exact figures).**
- **Productivity perception gap.** METR (July 2025) ran an RCT with 16 experienced open-source developers on 246 issues. With early-2025 AI tools, they took 19% longer, yet believed they had been about 20% faster. **Single RCT.** *Implication:* self-reports of "this summary helped me" are unreliable, so build in objective checks.

**Design rules that follow:** show evidence the reader can check (file:line, command, quote). Separate verified from inferred claims. Calibrate confidence and state what was left out. For high-stakes items, ask for prediction or explanation before reveal. For learning contexts, default to explaining over doing, and ask before handing over a full solution.

## Caveats

- No live source verification was possible in this session. Figures marked "(verify)" and the 2025–2026 AI studies should be checked against the primary papers before the skill ships.
- Most of the multimedia-learning evidence comes from short lab studies with students. Transfer to expert engineers reading agent output is plausible, but this population hasn't been tested directly. Expertise reversal suggests the effects will be smaller for experts.
- BLUF, pyramid structure, progressive disclosure and executive summaries are well-reasoned practice with indirect support, not proven speed-ups. The skill should present them as defaults, not laws.
- The AI over-reliance literature is young, and many results are single studies. The direction is consistent across them: polish and fluency increase acceptance, and active engagement protects understanding.

## Sources

1. mcp\_\_Atlassian\_\_search
2. mcp\_\_Atlassian\_\_getAccessibleAtlassianResources
