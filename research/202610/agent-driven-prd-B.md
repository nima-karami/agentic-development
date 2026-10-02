# Agent-Written PRDs: A Kickoff Document Set, PRD Structure, Method, Rubric, and Handoff Contract

A product kickoff needs three documents, and an agent should write them in this order: a **one-page product brief** (problem, who it's for, why now, what it is and is not), a **PR/FAQ-style "working backwards" narrative** for new products only, and a **lean, living PRD** that turns the brief into testable requirements, explicit non-goals, success metrics and release slices. Positioning, Lean Canvas, opportunity solution trees and north-star definitions are tools you use while writing these documents. They aren't separate documents to hand over. The difference between a strong PRD and a long generic one is not length. A strong PRD is specific to this product, separates evidence from assumption, and every requirement can be traced to a problem and checked by a test.

**Note on sourcing.** This research session ran without live web access. The only tools available were Jira and Confluence, and they returned nothing relevant.\[1\]\[2\] All sources below are named and dated from the author's knowledge of the published literature. Each is labelled as **adopted practice**, **one company's custom** or **opinion/framework**, and anything I could not pin down is flagged. Check the flagged items before treating them as citations.

---

## TL;DR

- **Minimum kickoff set (in order):**
  1. **Product brief / one-pager.** Intent and boundaries, owned by the human.
  2. **PR/FAQ.** Only for new products or product lines, to test whether the value story holds up.
  3. **Lean PRD.** Problem, users/jobs, goals and non-goals, requirements with IDs, assumptions marked as such, metrics, release slices, open questions.

  Lean Canvas, positioning (Dunford), the opportunity solution tree (Torres) and the north-star metric feed *sections* of these documents.
- **Sections that earn their place:**
  - Problem with evidence
  - Target user and job
  - Goals with measurable outcomes
  - **Non-goals**
  - Requirements tied to goals
  - An **assumptions/risks register** split by Cagan's four risks
  - Release slicing
  - Open questions with owners

  Ceremony to avoid: long persona biographies, padded competitive surveys, boilerplate non-functional requirements ("the system shall be scalable"), and metrics with no baseline or source.
- **Agent method:** Ask the human only about things they own (intent, target user, success, constraints, appetite, non-goals). Ask one question at a time and offer a recommended default each time. Infer everything else and label it `[ASSUMPTION]`. Finish with a reviewer pass against the rubric below. LLM research shows models are sycophantic and make premature assumptions when instructions are underspecified. Structured elicitation and explicit assumption tagging are the defences with the best support.

---

## Key Findings

### 1. Which documents a kickoff needs

| Document | Purpose | Status | Source (date) | Verdict |
|---|---|---|---|---|
| **Product vision / strategy statement** | Long-horizon "where we're going and why". Strategy is the bet on how to get there. | Opinion/framework, widely adopted | Marty Cagan, *Inspired* 2nd ed. (2017) and *Empowered* (2020). Gibson Biddle's DHM model ("delight customers in hard-to-copy, margin-enhancing ways"), essays c. 2017–2019 | **Optional per product.** Usually lives at company or product-line level. For a new product line, add 3–5 sentences to the brief instead of a separate document. |
| **PR/FAQ (Working Backwards)** | Write the launch press release and FAQs before building, to test whether the customer value is compelling | One company's custom (Amazon), widely copied | Colin Bryar & Bill Carr, *Working Backwards* (2021). The usual format is a press release of about one page plus external and internal FAQs, a few pages in total. | **Essential for new products and product lines; skip for internal tools and incremental features.** Its strength is forcing a customer-facing value claim and confronting hard internal questions (cost, feasibility, dependencies) in the FAQ. |
| **Product brief / one-pager** | Short statement of problem, audience, why now, intended outcome, boundaries | Adopted practice (many company variants, no single canonical template) | Variants appear in Lenny Rachitsky's template collections (Lenny's Newsletter, c. 2021–2023; exact post not checked). Shape Up's "pitch" (Ryan Singer, Basecamp, 2019) is the best-specified public equivalent: Problem, Appetite, Solution, Rabbit holes, No-gos. | **Essential.** This is where the human's intent is fixed. |
| **PRD** | The requirements: what must be true for the product to succeed, and how we'll know | Adopted practice; form has changed over time | Cagan, "How to Write a Good PRD", SVPG (c. 2005); *Inspired* 2nd ed. (2017); Atlassian's Confluence PRD template | **Essential**, in lean, living form. |
| **Lean Canvas** | One-page business-model hypothesis: Problem, Customer Segments, Unique Value Proposition, Solution, Channels, Revenue Streams, Cost Structure, Key Metrics, Unfair Advantage | Framework, widely adopted in startups | Ash Maurya (2010); *Running Lean* (2010/2012; 3rd ed. 2022) | **Optional.** Useful as a viability check for a new product. Fold its Problem, Segments, UVP and Key Metrics boxes into the brief rather than shipping a separate canvas. |
| **Opportunity solution tree** | Visual map: desired outcome → opportunities (customer needs) → solutions → assumption tests | Framework, widely adopted in discovery | Teresa Torres, producttalk.org (c. 2016); *Continuous Discovery Habits* (2021) | **Optional as an artifact, very useful as a reasoning step.** It stops solution-first framing because an outcome must sit above every solution. |
| **Positioning statement** | What we're the best at, for whom, against which alternatives | Framework, widely used in B2B | April Dunford, *Obviously Awesome* (2019). Components: competitive alternatives, unique attributes, value (and proof), best-fit customer characteristics, market category, with relevant trends as an optional extra. | **Optional; essential if the product enters a crowded market.** "Competitive alternatives" includes "do nothing" and spreadsheets, which is exactly the alternative analysis a PRD needs. |
| **Success metrics / north star** | The single metric that best captures delivered customer value, plus input metrics | Vendor framework, widely adopted | Amplitude, *North Star Playbook* (c. 2019; John Cutler et al., authorship to be checked) | **Essential as a PRD section, not a separate document.** |

**Recommended order:**
1. Brief: intent and boundaries, human-approved.
2. PR/FAQ: new products only, to stress-test value.
3. PRD: requirements.
4. Feature specs and architecture: your existing skill and design docs.

Positioning, Lean Canvas and the opportunity solution tree are **thinking tools the agent runs internally while drafting steps 1–3**.

**How the PRD has changed.**
- Cagan's c. 2005 SVPG paper described a fairly complete, up-front PRD.
- By *Inspired* 2nd ed. (2017) he argues that the classic PRD is a poor tool for discovery. He wants teams to test ideas with prototypes, with the spec following validated learning.
- Industry practice has moved to **short, living PRDs**: a few pages, linked to designs and tickets, revised as assumptions are tested. Atlassian's template is an example. It is a single Confluence page with a "what we're not doing" section and an open-questions table.
- Shape Up goes further. It replaces the PRD with a fixed-time "pitch" and accepts that scope will vary.
- **Implication for your agent:** the PRD should be short, versioned and explicitly provisional, not a contract. Downstream automation, though, needs more precision than human teams have relied on (see §7). The answer is a lean narrative plus a structured, ID'd requirements block.

### 2. What a good PRD contains

**Recommended structure.** S = small internal tool; M = standard product or feature set; L = new product line.

| # | Section | Purpose | What good looks like | Common mistake | S / M / L |
|---|---|---|---|---|---|
| 0 | **Header and status** | Version, owner, status (draft/reviewed/approved), last change, decision log link | One line per change in a changelog | No version, so downstream agents can't tell what's stale | S M L |
| 1 | **Problem statement** | Why this exists | A specific situation, who suffers, current workaround, cost of the status quo. Each claim tagged `[EVIDENCE: source]` or `[ASSUMPTION]`. | Describing the solution ("we need a dashboard") instead of the problem | S M L |
| 2 | **Target users and jobs** | Who it's for | 1–3 primary segments, each with a JTBD statement ("When [situation], I want to [motivation], so I can [outcome]", the Intercom/Klement-style job story) and the current alternative they "hire" | Invented personas with names, ages and hobbies that constrain nothing | S: 1 line; M L |
| 2a | **Anti-personas / not for** | Who we deliberately won't serve | "Not for teams over 50 seats; not for regulated healthcare data" | Omitted, which leads to scope creep through edge-case users | M L |
| 3 | **Goals and success metrics** | Outcomes, not outputs | 2–4 goals. Each has a metric, a baseline (or "unknown, to be measured in slice 1"), a target, a time frame and a data source. Plus guardrail metrics. | Vanity metrics or invented numbers ("increase engagement 30%") with no baseline | S: 1–2 goals; M; L adds north star |
| 4 | **Non-goals** | Things that could reasonably be goals but are deliberately excluded | Each non-goal is plausible and explains why it's excluded (Malte Ubl, "Design Docs at Google", industrialempathy.com, 2020) | Trivial non-goals ("we won't build a spaceship"), or "nothing" | S M L |
| 5 | **Scope and out-of-scope** | Boundaries of this release vs the product | In-scope capabilities list, out-of-scope list, "later" list. Shape Up–style **no-gos** and **rabbit holes** | Out-of-scope that silently reappears as requirements | S M L |
| 6 | **Alternatives and positioning** | Why this rather than what users do today | Competitive alternatives per Dunford, including "do nothing" | Feature-matrix padding against companies that don't compete | S: skip; M: short; L: full |
| 7 | **Functional requirements** | What the product must let users do | Stable IDs (FR-1…). Each is singular, verifiable, traced to a goal, with priority (MoSCoW) and evidence tag. Capability level, not UI level. | UI-level detail (belongs in feature specs), or untestable verbs ("support", "handle") | S M L |
| 8 | **Non-functional requirements / quality attributes** | Constraints on how well | Only NFRs that change the design, each with a measurable threshold ("p95 page load < 2s on 4G"; "WCAG 2.2 AA"; "data stays in EU") | Boilerplate lists ("secure, scalable, reliable") | S: 2–4; M; L |
| 9 | **Constraints** | Fixed facts: platform, stack, budget, deadline, legal, appetite | Each with its source (who set it) | Mixing constraints (fixed) with preferences | S M L |
| 10 | **Assumptions and risks** | What we believe without proof, and what could kill it | Register grouped by Cagan's four risks (value, usability, feasibility, business viability; *Inspired*, 2017). Each item has importance × evidence (Bland's assumption map) and a proposed test. | Risks listed with no mitigation or test, or the register omitted entirely | S: 3–5 items; M L |
| 11 | **Release slicing** | Smallest valuable release and what follows | Story-map backbone with horizontal slices (Jeff Patton, *User Story Mapping*, 2014). Slice 1 is a walking skeleton that delivers end-to-end value. | "MVP" = everything labelled Must | M L (S: one slice) |
| 12 | **Open questions** | Known unknowns | Table: question, owner, needed-by, blocking which requirement IDs | Questions with no owner, or unresolved ones hidden as assumptions | S M L |
| 13 | **Handoff block** | Machine-readable contract for downstream agents | See §7 | Missing, so downstream guesses | S M L |

**Sections that are mostly ceremony:**
- Long market-sizing in an internal PRD
- Narrative persona biographies
- "Background" sections that restate the problem
- Generic NFR checklists
- Exhaustive competitive grids
- Timelines that pretend to be estimates

ISO/IEC/IEEE 29148:2018, the requirements-engineering standard (first edition 2011), gives the quality bar for each requirement: necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct and conforming. For the set as a whole: complete, consistent, feasible, comprehensible and able to be validated. *(The standard is paywalled; this list is from secondary knowledge.)*

**Sizing:**
- **Small internal tool (1–2 pages).** Problem (3 sentences), one user/job, 1–2 goals, non-goals, 5–15 FRs, 2–4 NFRs, constraints, 3–5 assumptions, one release, open questions, handoff block. No PR/FAQ, positioning or north star.
- **New product line (6–12 pages plus PR/FAQ).** Everything above, plus:
  - Vision paragraph and anti-personas
  - Positioning/alternatives
  - North star with input metrics
  - Full four-risk register with tests
  - Multi-slice story map
  - Viability notes (cost and revenue assumptions only; detailed GTM and pricing are out of scope)

### 3. Boundaries: defining what the product is not

| Method | Source (date) | What it does | Use in agent |
|---|---|---|---|
| **Non-goals** | Google design-doc practice, described by Malte Ubl (2020); one company's custom, widely imitated | Lists plausible goals deliberately excluded | Required section. Reviewer checks each non-goal is something a reasonable stakeholder might have wanted. |
| **No-gos and rabbit holes, plus appetite** | Shape Up (Singer, 2019) | Appetite = fixed time budget (small batch of about 1–2 weeks, big batch of 6 weeks). No-gos are explicit exclusions; rabbit holes are known risk areas you defuse in advance. | **Ask the human for appetite.** It is the strongest single defence against scope creep, because scope must fit the time box rather than the reverse. |
| **Anti-personas** | Common UX practice; no single canonical origin I can trace | Names users you will disappoint on purpose | Include for M/L |
| **Story mapping** | Patton (2014) | Backbone of user activities; slices cut horizontally so each release is end-to-end | Primary MVP-cut tool |
| **MoSCoW** | Dai Clegg, Oracle (1994); adopted in DSDM | Must/Should/Could/Won't | Cheap and agent-friendly. Enforce a cap, e.g. Musts ≤ ~60% of effort (a DSDM guideline). "Won't (this time)" feeds out-of-scope. |
| **Kano** | Noriaki Kano et al. (1984) | Must-be, one-dimensional (performance), attractive, indifferent, reverse | Without real users the agent can only *hypothesise* Kano categories. Label them as assumptions. |
| **RICE** | Sean McBride, Intercom blog (c. 2016) | (Reach × Impact × Confidence) / Effort | Useful for ordering slices 2+. The Confidence term is a natural place to show evidence strength. Don't present RICE scores as objective when Reach is invented. |

**Keeping scope from creeping during elaboration:**
1. Freeze the brief (goals, non-goals, appetite) after the human approves it.
2. Any new requirement must cite the goal ID it serves. Requirements without a goal go to "Later" or "Open questions".
3. Track a scope delta in the changelog (added/removed FR IDs per revision).
4. A reviewer agent flags any FR that contradicts a non-goal or out-of-scope item.
5. Keep "fixed time, variable scope" (Shape Up): when scope grows, something in the slice must be cut.

### 4. From idea to requirements without a team or real users

What an agent can do on its own:
- **JTBD framing.**
  - Christensen's job theory: *Competing Against Luck*, 2016, with Hall, Dillon and Duncan.
  - Bob Moesta's demand-side "forces of progress": push of the situation, pull of the new solution, anxiety, habit (*Demand-Side Sales 101*, 2020).
  - Tony Ulwick's Outcome-Driven Innovation: *What Customers Want*, 2005; *Jobs to be Done: Theory to Practice*, 2016. Its job/outcome statements take the form "minimise the time it takes to…".

  The agent can *draft* jobs and forces as hypotheses.
- **Problem framing.** Restate the idea as a problem with no solution in it. Ask "what happens if we do nothing?"
- **Alternative analysis.** List what users do today: competitors, spreadsheets, manual workarounds, do nothing (Dunford's "competitive alternatives"). An agent with web access can check public competitor facts; without it, it should label them as unverified.
- **Opportunity solution tree.** Put a measurable outcome at the root. Generate several opportunities and several solutions per opportunity, so the requested solution is visibly one option among several.
- **Assumption mapping** (David Bland & Alexander Osterwalder, *Testing Business Ideas*, 2019). Sort assumptions by importance × evidence. Assumptions that are high-importance and low-evidence become the risk register and drive slice 1. Bland groups hypotheses as desirability/feasibility/viability. Cagan's four risks (*Inspired*, 2017) add **usability**. Use Cagan's four for software products.

**What it cannot do:** validate. An agent without users can only produce well-organised hypotheses. The document must say so.

**Marking evidence vs assumption.** Use inline tags on every factual claim and requirement:
- `[EVIDENCE: <source, date>]` — user-provided data, research, analytics, a cited document
- `[STAKEHOLDER: <name>]` — a decision or statement by the human owner (intent, not proof of market fact)
- `[ASSUMPTION: <risk type>, confidence L/M/H, test: <how to validate>]`
- `[INFERRED]` — the agent's reasoning from other facts in the doc

A reviewer can then count untagged claims, and the ratio of assumptions to evidence becomes a visible health metric. This tagging scheme is my synthesis of Bland's evidence axis and Torres's assumption tests, not a published standard.

### 5. Ask vs assume

**Principle:** at product level the human owns *intent*, and the agent owns *structure and completeness*.

**Always ask (the agent must not invent these):**
1. Problem and for whom: target user and the triggering situation
2. Desired outcome and how success would be recognised (even qualitatively)
3. Appetite and hard constraints: time, budget, platform, compliance, team
4. Non-goals the human already holds, and what they would be unhappy to see built
5. Any evidence they have: user complaints, data, prior attempts
6. New product or extension of an existing one (this decides whether a PR/FAQ is needed)

**Infer, labelled as assumption:**
- Secondary users and anti-personas
- Alternatives
- Likely NFRs from the context (e.g. a web app means accessibility and browser support)
- Risk register
- Slicing
- Candidate metrics
- Requirement wording

**How to present choices:**
- Ask **one question at a time** and give a **recommended default** with a one-line rationale ("I'd assume X because Y; confirm or change").
- Cap it at about 5–7 questions before the first draft.
- Batch low-stakes inferences into a single "assumptions I made — scan and correct" list rather than asking about each.
- Prefer multiple-choice questions to open ones when the option space is knowable.
- Draft early: a concrete draft gets better corrections than abstract questions.

**What research says:**
- **GATE.** Belinda Li, Alex Tamkin, Noah Goodman & Jacob Andreas, "Eliciting Human Preferences with Language Models", arXiv 2310.11589 (2023). When the LM led elicitation by asking users questions, the result was often more informative than prompts users wrote themselves, for similar or less user effort. This supports interviewing over "paste your requirements".
- **STaR-GATE.** Andukuri, Fränken, Gerstenberg & Goodman (2024). LMs can be trained to ask better clarifying questions. Off-the-shelf models don't do it reliably by default, so the skill must instruct it explicitly.
- **ClarifyGPT.** Mu et al. (2023). In code generation, detecting ambiguity first and asking targeted clarifying questions only when needed improved correctness. This supports *conditional* asking, not interrogating by default.
- **Multi-turn underspecification.** "LLMs Get Lost in Multi-Turn Conversation", Laban et al. (Microsoft/Salesforce, arXiv 2025). When task information arrives in pieces across turns, models make premature assumptions and fail to recover, and performance drops sharply (the authors report about 39% on average). **Implication:** gather intent first, then write the draft in one pass from a consolidated brief, rather than writing incrementally while the conversation is still going.
- **Sycophancy.** Sharma et al., "Towards Understanding Sycophancy in Language Models" (Anthropic, arXiv 2310.13548, 2023). Models tend to agree with users' stated views. **Implication:** the agent should be told outright to challenge the problem framing and say when the idea is solution-first. The human still decides.

### 6. Agent failure modes and defences

| Failure mode | What it looks like | Defence |
|---|---|---|
| **Generic boilerplate** | Sections that would fit any product ("users want an intuitive experience") | **Swap test.** The reviewer replaces the product name with a different product. Any sentence that still reads true is flagged for deletion or for making specific. |
| **Invented personas** | "Sarah, 34, marketing manager…" with no source | Allow only segments that come from the human or from evidence. Write jobs, not biographies. Tag them `[ASSUMPTION]`. |
| **Invented metrics and numbers** | "Reduce churn by 25%", market size figures with no source | Every number needs a source tag. If there is no baseline, the target is "measure baseline in slice 1". The reviewer rejects untagged numbers. |
| **Scope inflation** | Every plausible feature becomes a Must; enterprise SSO in an internal tool | Appetite cap, Must ≤ ~60%, every FR traces to a goal, non-goals generated *before* requirements |
| **Solution-first framing** | The PRD restates the requested solution as the problem | Write the problem section with solution words banned. Use an opportunity-solution tree with at least 3 alternative solutions considered. |
| **Confident requirements resting on no evidence** | Declarative "shall" statements resting on guesses | Evidence tags. The risk register must include the top 3 riskiest assumptions with tests. Slice 1 is designed to test them. |
| **Sycophancy** | Agrees that the idea is great and that every stakeholder wish is in scope | Explicit "devil's advocate" pass. The PR/FAQ internal FAQ must include "why might this fail?" |
| **UI/architecture leakage** | Button labels, database choices in the PRD | Rubric check: requirements stay at capability level. Design and architecture belong downstream. |
| **Premature assumption under underspecification** | Fills gaps silently (Laban et al., 2025) | An ask-first phase. Silent fills become explicit assumptions in a list the human reviews. |
| **Inconsistency across sections** | Non-goal contradicted by an FR; metric with no matching goal | A cross-reference check in the reviewer pass (IDs make this mechanical) |

**On the evidence for LLM-written requirements.** Krishna et al., "Using LLMs in Software Requirements Specifications: An Empirical Evaluation" (IEEE RE 2024; arXiv 2404.17842), compared SRS documents from GPT-4 and CodeLlama with ones written by entry-level engineers. They reported that GPT-4 drafts were broadly comparable and useful as a starting point, but needed human review for correctness and completeness. *(Treat the exact findings as needing verification.)* Elicitron (Ataei et al., 2024) used LLM-simulated users to surface latent needs. Synthetic users can widen brainstorming, but they are **not evidence**: tag their outputs `[INFERRED]`, never `[EVIDENCE]`.

### 7. Handoff downstream

Spec-driven tooling has converged on a layered chain:
- **GitHub Spec Kit** (open-sourced September 2025): constitution → specify → plan → tasks.
- **AWS Kiro** (July 2025): requirements.md written in EARS-style acceptance criteria, then design.md, then tasks.md.
- Birgitta Böckeler's analysis on martinfowler.com (2025) distinguishes "spec-first", "spec-anchored" and "spec-as-source" approaches. She warns that heavyweight specs create review overhead and can be ignored by the agent anyway. *(Treat the details as needing verification.)*

**Takeaway:** keep the PRD at the "what and why" level, and make the "what" machine-addressable.

**EARS** (Alistair Mavin et al., Rolls-Royce, IEEE RE 2009) gives five patterns:
- Ubiquitous: "The <system> shall…"
- Event-driven: "When <trigger>, the <system> shall…"
- State-driven: "While <state>…"
- Optional feature: "Where <feature>…"
- Unwanted behaviour: "If <condition>, then the <system> shall…"

Use EARS for capability-level FRs in the PRD. Your existing skill expands them into full states and edge cases.

**Handoff contract (the block at the end of the PRD):**

```yaml
prd_version: 1.3
status: approved            # draft | reviewed | approved
goals:        [{id: G1, outcome: ..., metric: ..., baseline: ..., target: ..., source: ...}]
non_goals:    [{id: NG1, text: ..., reason: ...}]
users:        [{id: U1, job: "When..., I want..., so I can...", evidence: ...}]
anti_users:   [...]
requirements:
  - id: FR-3
    text: "When a member submits an expense over the limit, the system shall route it to an approver."
    goal: G1
    priority: Must
    slice: 1
    evidence: ASSUMPTION(value, M, test: ...)
    acceptance_hint: "verifiable by ..."
nfrs:         [{id: NFR-1, attribute: performance, threshold: "p95 < 2s", applies_to: [FR-3]}]
constraints:  [{id: C1, text: ..., set_by: ...}]
assumptions:  [{id: A1, risk: feasibility, importance: H, evidence: L, test: ...}]
out_of_scope: [...]
open_questions: [{id: Q1, owner: ..., blocks: [FR-5]}]
slices:       [{id: S1, goal: ..., includes: [FR-1, FR-3], appetite: "2 weeks"}]
decisions_reserved_for_downstream: ["UI layout", "data store choice", ...]
```

**Right level of detail:**
- The PRD fixes **capabilities, boundaries, quality thresholds, constraints and priorities**.
- Feature specs own states, interactions and edge cases.
- Architecture owns components and technology choices, constrained by the NFRs and Cs.
- **Downstream may not:** add an FR or contradict an NG.
- **Downstream may:** raise a change request against an ID.

**Staying in sync:**
- The PRD is the single source of truth for IDs. Downstream artifacts reference IDs, never copy text.
- Changes bump `prd_version` and add a changelog line listing affected IDs.
- Downstream agents check the version on start and flag specs built on stale versions.
- Resolving an open question or invalidating an assumption updates the PRD first, then propagates.

---

## Recommendations: step-by-step agent method

1. **Intake.** Read the one-paragraph idea. Classify it as internal tool / feature set / new product line, which sets the S/M/L size.
2. **Restate and challenge (no questions yet).** Write a solution-free problem restatement and an outcome hypothesis. Note whether the idea is solution-first.
3. **🛑 Ask, one at a time with defaults (≤ ~6 questions):** target user and situation → desired outcome / success signal → appetite and hard constraints → known non-goals → available evidence → new or extension. Stop when the answers are enough. Don't fill gaps by asking more questions; the rest become assumptions.
4. **Internal framing pass (not shown unless asked):**
   - JTBD statements and forces
   - Alternatives, including do nothing
   - Mini opportunity-solution tree with at least 3 solutions
   - Assumption map across the four risks
   - Positioning/Lean Canvas boxes for L size only
5. **Draft the brief:** problem, users, outcome, non-goals, appetite, top risks.
6. **🛑 Human approves the brief.** Goals, non-goals and appetite are then frozen.
7. **PR/FAQ (L only).** Draft the press release and FAQ, including "why might this fail". **🛑 Human reviews.**
8. **Draft the PRD in one pass** from the consolidated brief:
   - Generate non-goals and out-of-scope **before** requirements
   - Write FRs in EARS with IDs, goal trace, MoSCoW and evidence tags
   - Only design-changing NFRs, with thresholds
   - Story-map slices, with slice 1 testing the riskiest assumptions
9. **Reviewer agent pass** against the rubric. Fix everything that fails automatically. Turn unresolved items into open questions.
10. **🛑 Human final review.** Present: a summary, an "assumptions I made" list to scan, open questions that need an owner, and the scope-delta versus the brief.
11. **Publish v1.0 with the handoff block.** Downstream skills consume IDs.

## Quality rubric (for a reviewer agent)

Score each item 0 (fail), 1 (partial) or 2 (pass). Items marked ★ are gates: any 0 on a gate blocks approval.

1. ★ **Problem is solution-free and specific.** It passes the swap test, and the current workaround is named.
2. ★ **Target user is a job, not a biography**, sourced or tagged.
3. ★ **Every goal has metric + baseline (or a "measure first" plan) + target + source.**
4. ★ **Non-goals are plausible.** At least 3 for M/L, each with a reason.
5. ★ **Every FR has an ID, traces to a goal, is singular and verifiable** (the 29148 characteristics), and uses no weak verbs ("support", "handle", "easy", "fast").
6. ★ **No FR contradicts a non-goal or out-of-scope item.**
7. **NFRs have measurable thresholds.** No boilerplate.
8. ★ **Every number and factual claim carries an evidence tag.** The count of untagged claims is 0.
9. **The assumptions register covers all four risks.** The top 3 have tests.
10. **Slice 1 is end-to-end, within appetite, and tests the riskiest assumption.** Musts ≤ ~60% of effort.
11. **Requirements stay at capability level.** No UI or architecture decisions.
12. **Open questions have owners and list the IDs they block.**
13. ★ **The handoff block is present and valid.** IDs are consistent across sections.
14. **Length is right-sized** (S ≤ 2 pages, M ≤ 5, L ≤ 12 plus PR/FAQ). Ceremony sections are absent.
15. **Version, status and changelog are present.**

Approve if all gates are 2 and the total is ≥ 80%.

## Caveats

- **No live web verification in this session.** Book titles, authors and years for the core frameworks are high-confidence. The following need checking before formal citation:
  - Precise dates for blog posts (Cagan's PRD paper, Intercom RICE, the Lenny collections, the North Star Playbook)
  - The specific numeric findings of the LLM papers (Krishna et al. 2024; Laban et al. 2025)
  - The Böckeler article details
- **Adoption vs custom:**
  - PR/FAQ (Amazon), Shape Up (Basecamp) and Google design-doc non-goals are **single-company customs** that have spread.
  - Cagan, Torres, Dunford, Maurya, Bland and Patton are **practitioner frameworks**: influential opinion, not empirical results.
  - ISO 29148 and EARS are **standards/RE literature**.
  - The evidence-tagging scheme, the rubric thresholds (≤60% Musts is DSDM's guideline; the page limits and the 80% pass mark are my own), and the handoff YAML are **my synthesis**, not published templates.
- There is no single canonical "PRD template". Published templates vary by company. Don't present any one of them as the standard.
- An agent without users produces **organised hypotheses, not validated requirements**. The PRD's honesty about this is a feature, not a weakness.

## Sources

1. mcp\_\_Atlassian\_\_search
2. mcp\_\_Atlassian\_\_searchConfluenceUsingCql
