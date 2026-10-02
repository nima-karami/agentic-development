# Designing an Agent That Writes a Good Product Requirements Document

## Executive answer

The strongest conclusion from the research is that **there is no universal “product kickoff packet.”** Publicly documented strong product organizations use strikingly different artefacts: Amazon works backwards from a press release and FAQ; Intercom has used a one-page project brief centred on the customer job; Basecamp’s Shape Up pitch centres on problem, appetite, solution, rabbit holes, and explicit no-gos; Atlassian advocates a concise, collaborative, continuously updated requirements page. The convergence is in the **questions the artefacts force teams to answer**, not in their names or formats. citeturn13search1turn18search4turn14search3turn13search0

For the agent you are building, I would make the minimum kickoff output **two living artefacts, with a third logical register embedded in them**:

| Artefact | Status | What it is for |
|---|---|---|
| **Product brief / product charter** | **Essential** | Establishes the product thesis: whose problem, what progress they need, why this is worth doing, strategic context, evidence, major constraints, and—critically—what product you are *not* proposing. This is the human-intent document. |
| **Living PRD** | **Essential** | Turns that thesis into a bounded contract: goals and non-goals, product-level capabilities and requirements, material quality requirements, constraints, risks, success measures, first-release boundary, and unresolved questions. |
| **Evidence & decision register** | **Essential capability; separate document only for larger work** | Prevents an LLM from laundering guesses into facts. Every consequential claim is attributable to user input, observed evidence, a human decision, or an explicitly unvalidated assumption. For a small tool this can be a table inside the PRD; for a new product line it deserves its own maintained artefact. This recommendation is a synthesis of requirements traceability practice and current LLM-requirements research. citeturn13search3turn15search1 |

Everything else should be **conditional**.

A separate **vision/strategy statement** earns its own document when the initiative creates a new product line, changes the target market, spans multiple teams, or requires strategic choices that should outlive one release. Roman Pichler’s Product Vision Board, first created in 2011, captures vision, target group, needs, high-level product differentiation and business goals; that is a useful practitioner framework, but not an industry standard. citeturn17search1turn17search9

A **PR/FAQ** is an excellent alternative front end when customer value is deeply uncertain or the product is genuinely novel. But it is specifically an Amazon practice, not a prerequisite for “doing product properly.” Amazon publicly describes doing Working Backwards documents—including the press release and FAQ—before writing code; former Amazon executives Colin Bryar and Bill Carr documented the method in *Working Backwards* in 2021. citeturn13search1turn19search12

A **Lean Canvas** is useful when the unresolved question is the business model rather than just the product definition. Ash Maurya describes it as a startup-focused adaptation of the Business Model Canvas and a one-page model for testing a business model; it should not be mistaken for a PRD. citeturn18search3turn17search2

An **Opportunity Solution Tree** is useful once there is a defined outcome and actual discovery evidence. Teresa Torres explicitly warns against inventing opportunities from what the team merely thinks it knows; her method is built around customer stories and organizes an outcome into opportunities, possible solutions, and assumptions. An agent without user research may create a **hypothesis tree**, but should not present it as an evidence-backed opportunity tree. Torres’s *Continuous Discovery Habits* was published in 2021; her public OST guidance remains explicit about grounding opportunities in research. citeturn19search3turn13search6

A **positioning analysis** is worthwhile for a competitive or externally marketed product, but I would not require a generic positioning-statement template. April Dunford’s 2021 framework starts with the alternatives a customer would use if your product did not exist, then differentiated capabilities, resulting value, best-fit customers, and appropriate market category. That is much more useful to an agent than filling blanks in a slogan-like positioning sentence. citeturn18search2turn17search11

**Success measures are essential; a separate “North Star” document is not.** Amplitude’s North Star framework defines a single metric intended to capture customer value, remain influenceable by product/marketing, and lead business results. That is one practitioner/company framework rather than a universal requirement. Your agent should insist on a measurable conception of success but should not insist that every initiative have one canonical North Star Metric. citeturn18search1turn18search5

So the recommended ordering is:

**Vision/strategy, if genuinely needed → product brief or PR/FAQ → evidence/risk framing → living PRD → release boundary → downstream feature and architecture specifications.**

For a small internal tool, the **brief and PRD can collapse into one living page**. For a new product line, split them and maintain a substantive evidence/decision register.

The important historical shift is not “PRDs are obsolete.” It is that **the PRD has changed from a monolithic specification and sign-off artefact into a compact, living alignment and decision artefact**, while the underlying requirement disciplines of clarity, traceability, validation and change management still matter. The 2001 Agile Manifesto privileged working software, collaboration and responding to change over comprehensive documentation and rigid plans; Atlassian was publicly describing a one-page, link-rich, living requirements page by 2013 and its current guidance explicitly calls fully detailed upfront specifications and iron-clad sign-offs anti-patterns. ISO/IEC/IEEE 29148:2018, meanwhile, still defines requirements engineering as eliciting, analysing, verifying, validating, communicating, documenting, maintaining and tracing requirements throughout the lifecycle. These positions are complementary rather than contradictory. citeturn19search1turn13search8turn13search0turn13search3

## What the kickoff should produce

The agent should model kickoff as a progression from **intent → evidence → boundaries → requirements**, rather than as “fill every template that product people have invented.”

Here is how I would evaluate the candidate artefacts in your prompt.

| Candidate | Recommendation | When it earns its place | Evidence category |
|---|---|---|---|
| **Vision / strategy** | Essential **concept**; separate document conditionally | New product, major repositioning, multi-team initiative, long-lived strategic choice | Practitioner framework; Pichler, 2011 onward. citeturn17search1turn17search9 |
| **Product brief / one-pager** | **Essential** | Nearly every kickoff; can merge with PRD for small work | Common pattern, with company-specific implementations. Intercom publicly documented its one-page A4 brief in 2016; Atlassian advocates concise requirement pages. citeturn18search4turn13search8 |
| **PR/FAQ** | Optional substitute/companion to the brief | Novel customer proposition, high value uncertainty, need to explain product from customer perspective | **Amazon custom**, documented publicly and in *Working Backwards* (2021). citeturn13search1turn19search12 |
| **PRD** | **Essential** | Once problem, audience and broad boundary are sufficiently understood to state requirements | Widely adopted category; exact format varies. Atlassian current guidance is explicitly lean/living. citeturn13search0 |
| **Evidence & decision register** | **Essential capability** | Always; embed for small work, separate for complex work | This report’s synthesis from formal traceability practice and LLM grounding evidence. citeturn13search3turn15search1 |
| **Success metrics** | **Essential content** | Always, although “success” can initially be a qualitative decision criterion where measurement is immature | Broad product practice; North Star is only one implementation. citeturn18search1 |
| **Lean Canvas** | Optional | Business-model uncertainty is material: customer/revenue/cost/channel assumptions | **Ash Maurya framework**, not a generic PRD standard. citeturn18search3turn17search2 |
| **Opportunity Solution Tree** | Optional, discovery-dependent | There is a defined outcome and real customer evidence to organize | **Teresa Torres framework**; 2021 book/current guidance. citeturn19search3turn13search6 |
| **Positioning** | Conditional | External product where alternatives and differentiation affect who the product should serve | **Practitioner framework/opinion**, notably Dunford 2020–2021. citeturn17search11turn18search2 |
| **North Star definition** | Optional | Product benefits from one durable value metric across teams | **Amplitude framework**, not universal doctrine. citeturn18search1 |

A useful design principle for your Claude Code skill is therefore:

> **Do not make “document type” the unit of product thinking. Make “decision that must be made” the unit, and materialize separate documents only when scale or ownership requires them.**

That avoids a predictable template-agent pathology: a model will happily manufacture content to satisfy empty headings. Marty Cagan explicitly warns in his 2020 writing that supplementary documentation templates tend to accumulate material that is rarely read, and argues that the amount of discovery work should depend on the particular risk and consequence rather than treating every item identically. That is practitioner opinion, but it aligns well with the lean-documentation pattern seen at Atlassian. citeturn14search9turn13search0

The **product brief** should answer roughly these questions before the PRD starts elaborating them:

| Decision | Brief must make clear |
|---|---|
| Product thesis | What change are we trying to cause, for whom? |
| Problem/job | What are people struggling to accomplish today, and under what circumstances? |
| Existing alternative | What do they do without this product? |
| Evidence | Why do we believe this problem is real and important? |
| Value | What materially improves if we succeed? |
| Strategy | Why is this appropriate for this organization/product now? |
| Boundary | Who and what are explicitly not part of the product? |
| Appetite/constraints | What hard constraints shape the opportunity? |
| Outcome | What observable result would make the investment successful? |
| Uncertainty | What must be learned before some statements can be treated as requirements? |

JTBD is particularly useful at this level because it pushes the agent toward **circumstances, desired progress and motivations rather than invented demographics**. Christensen, Hall, Dillon and Duncan’s 2016 HBR treatment argues that the circumstances surrounding the customer’s desired progress can be more explanatory than buyer attributes, and that jobs can include functional, social and emotional dimensions. But an agent can only formulate a **job hypothesis** from a vague prompt; it cannot infer that customers really experience that job without evidence. citeturn16search0turn16search4

Intercom’s 2013–2016 Job Stories work provides a useful implementation pattern: describe the situation, motivation and desired outcome, and study how people solve the problem now. Intercom also explicitly based its one-page briefs on research and used job stories to prevent projects drifting away from the underlying problem. That is an **Intercom custom**, not proof that Job Stories are universally superior to personas or user stories. citeturn18search0turn18search4turn18search8

For an externally competitive product, the brief should also capture the **current alternative**, not merely a list of vendors. Dunford’s useful question is essentially: what would this customer do if this offering did not exist? That can expose spreadsheets, manual work, a generic platform, “do nothing,” or another product as the true alternative. citeturn17search11turn18search2

Most importantly for an LLM agent, every consequential statement should have an **epistemic status**. The exact taxonomy below is my recommendation rather than an established PM standard:

| Status | Meaning |
|---|---|
| `FACT` | Directly supplied by the human, or objectively established by an authoritative source/system. |
| `EVIDENCE` | An observation from research, analytics, interviews, support data, experiments, or another identified method. Must carry source and date. |
| `ASSUMPTION` | A belief that needs to be true but has not been adequately tested. |
| `DECISION` | A trade-off or choice explicitly approved by the responsible human; record owner and date. |
| `PROPOSAL` | An agent-generated recommendation awaiting human approval. |
| `OPEN` | An unresolved question whose answer could alter scope, requirements or success. |

That may seem bureaucratic, but it directly addresses one of the core LLM risks. ISO/IEC/IEEE 29148 defines traceability in terms of documenting where requirements derive from and where they flow down; the 2025 ReqInOne research likewise found direct whole-document LLM generation prone to hallucination and built a modular pipeline around extracting and structuring requirements from source material. citeturn13search3turn15search1

For product discovery, “validated” should **not** be a synonym for “the agent found supporting webpages.” User value and usability claims usually require evidence about the actual target population and context. Torres’s OST guidance explicitly warns that generating customer opportunities from the team’s own ideas injects bias and “half-truths”; her assumption-testing framework treats assumptions as beliefs to be evaluated through appropriate evidence such as observed behaviour, prototypes, data, surveys or engineering research spikes. citeturn13search6turn19search10

A good agent can therefore perform **desk discovery**—market structure, documented alternatives, standards, technical constraints, publicly available facts—but it must not pretend desk discovery has established customer demand.

## A PRD structure that earns its keep

I would give the skill a **core schema rather than a fixed prose template**. Every section must justify a decision downstream. Sections that do not affect a decision can disappear.

| PRD section | Why it earns its place | What “good” looks like | Common failure |
|---|---|---|---|
| **Document state** | People and agents need to know what version they are consuming | Owner, status, last reviewed date, product/release scope, approvers/decision owners | A timeless-looking document whose authority is unclear |
| **Product thesis / problem** | Prevents requirements from becoming an arbitrary feature collection | Concise description of present situation, desired change and why it matters, tied to evidence | Restating the proposed solution as the “problem” |
| **Target users / customers / jobs** | Defines for whom requirements should optimize | Specific target group and relevant circumstances/jobs; evidence references; excluded segments where useful | Fictional persona biography or demographics invented by the model |
| **Goals / intended outcomes** | Establishes the test for product-level success | Few observable outcomes linked to the problem; distinguish user and business outcomes when relevant | “Build X,” “launch by Y,” or feature completion masquerading as outcome |
| **Non-goals and out-of-scope** | Protects the meaning of the product and the release | Concrete exclusions with rationale and, where appropriate, a condition for reconsideration | Vague “future considerations” list that commits nothing |
| **Product scope / capabilities** | Bridges product intent to feature-level work | Coarse capabilities and end-to-end product responsibilities, without detailed UI behaviour | Sneaking the feature spec into the PRD |
| **Functional requirements** | States product obligations downstream artefacts must satisfy | Individually identifiable, necessary, unambiguous enough to validate, traceable to need/evidence/decision | Long wish list of plausible features |
| **Quality / non-functional requirements** | Many decisive constraints are not features | Only material performance, security, privacy, reliability, accessibility, interoperability, data, operational or compliance expectations; measurable where a real threshold exists | Generic boilerplate such as “fast, secure, scalable and user-friendly” |
| **Constraints and dependencies** | Architecture and release choices cannot be judged without them | Hard platform, data, integration, policy, organizational, time/appetite or compatibility constraints; source and owner | Agent silently assumes deadline, platform or budget |
| **Assumptions and risks** | Exposes what can still invalidate the plan | Assumption, evidence level, consequence, risk category, proposed validation, owner | “Risk: users may not like it” with no consequence or next action |
| **Success measures** | Allows product success to be judged independently of shipping | Metric definition or observable criterion, rationale, baseline where known, source of any target | LLM invents “increase engagement 20%” because a template expects a target |
| **Release boundary** | Forces a coherent first product rather than an unbounded backlog | Smallest coherent end-to-end release, explicit deferred capabilities, rationale | “MVP” means every feature marked P0/P1 |
| **Open questions / decisions** | Prevents unresolved issues from becoming accidental implementation assumptions | Question, consequence, owner, blocking/non-blocking status; decisions retained with rationale | Questions disappear once prose is generated |
| **Trace and change metadata** | Makes the document safe for downstream agents | Stable requirement IDs, derivation links, change history and affected downstream artefacts | Updating prose while feature/architecture docs silently diverge |

This structure combines modern lightweight product practice with requirements-engineering discipline. Atlassian’s current PRD guidance includes goals, assumptions, user stories, supporting material, open questions and an explicit “what we’re not doing” section, while recommending collaborative, continuously updated documentation rather than comprehensive upfront specification. NASA’s 2023 “How to Write a Good Requirement” guidance—written for a much higher-assurance environment—adds useful reviewer criteria: requirements should be clear, necessary, feasible, at the right level, and should state the need rather than accidentally prescribing a design solution. ISO/IEC/IEEE 29148 adds lifecycle traceability and validation. citeturn13search0turn14search0turn13search3

That does **not** mean your PRD should read like a NASA system specification. NASA is a domain-specific, high-assurance source, not a SaaS-product template. The transferable lesson is the quality test for individual requirements; the product-level artefact can remain terse and linked. Atlassian’s 2013 guidance explicitly presented the requirement page as a “landing page” whose links progressively disclose interviews, prior discussions and technical documentation rather than reproducing everything. citeturn14search0turn13search8

Sections I would make **conditional rather than mandatory** include competitive analysis, positioning, migration strategy, detailed data governance, regulatory analysis, support/operations, business-model economics, internationalization and a metric tree. They belong when they materially change the product decision.

Sections or content I would treat as likely **ceremony** include fabricated persona backstories, copied corporate mission language, long market-history narratives with no decision consequence, generic lists of quality attributes, exhaustive screenshots of an already-specified solution, arbitrary target numbers, and a roadmap duplicated from another system. Cagan’s criticism of supplementary-document templates growing into unread overhead and Atlassian’s “just enough/living” approach both support resisting mandatory bulk. citeturn14search9turn13search0

**Right-sizing should alter depth, not conceptual completeness.**

For a **small internal tool**, the brief and PRD can be a single page or short living document. It may have one target role, one central job/problem, a few success signals, a short set of product requirements, only the quality constraints that can actually change implementation, explicit non-goals, a first-release slice and an assumption/open-question table. It does not need a Lean Canvas, formal positioning exercise, North Star workshop or elaborate persona set unless the work genuinely warrants them. This is a design recommendation, consistent with the lean-documentation practices above rather than a published industry size rule. citeturn13search8turn14search9

For a **new product line**, separate the strategic framing from the PRD. The strategic document should settle target market/customer, principal need, product category/thesis, differentiation and business objective; the PRD can then support multiple roles, material alternatives, product-wide constraints, key integration/data/security implications, release stages, measurable outcomes and a substantial evidence/risk register. Pichler’s Vision Board is one useful representation of exactly this strategic layer: vision, target group, needs, coarse product differentiation and business goals rather than detailed epics or stories. citeturn17search1turn17search9

The PRD should also **stop before feature-level behavioural specification**. Its job is to say what the product must enable and under what constraints. Your existing skill should own exact states, event flows, validations, interaction details, feature edge cases and feature acceptance criteria. Architecture should own how technical components satisfy those product obligations.

A useful litmus test is:

> **If changing the statement would change whether we should build the product, what the product is responsible for, what first release contains, or a constraint every solution must respect, it probably belongs in the PRD. If it merely determines how one feature behaves or how software is constructed, it belongs downstream.**

## Agent workflow from idea to reviewed PRD

The best-supported architecture is **not** “prompt once: write me a complete PRD.” Current requirements-engineering research is young—the 2025 systematic review by Ferrari and colleagues examined 74 LLM/requirements-engineering studies from 2023–2024, with much of the research concentrated on elicitation and validation—but direct-generation weaknesses such as hallucination, ambiguity and lack of controllability recur. ReqInOne, a 2025 SRS-generation agent, decomposes the task into separate stages rather than directly generating an entire specification; its evaluation is promising but modest and should not be treated as proof that autonomous requirements engineering is solved. citeturn15search6turn15search1

I would implement the product agent as the following state machine.

**Step 1 — Parse, but do not elaborate.**

From the one-paragraph idea, extract only statements actually present. Build the epistemic register immediately:

```text
FACT        Human explicitly says this product is internal.
FACT        Human says it is for support-team managers.
ASSUMPTION  Managers have difficulty seeing workload trends.
PROPOSAL    Existing alternative may be spreadsheets/manual reporting.
OPEN        What decision should improved workload visibility enable?
OPEN        Is this intended to replace or supplement the current reporting system?
```

The key rule is: **the first pass is lossless extraction, not creative completion**. ReqInOne’s modular extraction approach is relevant here; ISO traceability supplies the stronger conceptual reason—derived requirements should retain a derivation path. citeturn15search1turn13search3

**Step 2 — Find the highest-impact missing intent and ask the human.**

Do not dump a 20-question product-manager questionnaire. Ask the ambiguity whose answer would most change the shape of everything downstream.

The first questions should generally come from this set, but only when not already answered:

1. **Outcome:** “What change are you trying to create, and why does it matter now?”
2. **Primary target:** “Who most needs this, in what situation?”
3. **Boundary:** “Who or what should this explicitly *not* serve?”
4. **Hard constraints:** “Which constraints are already non-negotiable—time/appetite, platform, integrations, data, security/compliance, compatibility?”
5. **Evidence:** “What evidence do you already have—interviews, support cases, analytics, existing workflow, commitments?”
6. **Success:** “What would convince you this worked, and what failure would make it unacceptable?”

This ordering is my synthesis, not a published PM standard. The LLM research strongly supports making the policy explicit: the 2024 ACL CLAMBER benchmark, with roughly 12,000 ambiguous queries, found that then-current LLMs had limited ability both to recognize ambiguity and to ask high-quality clarifying questions; chain-of-thought and few-shot prompting yielded only marginal improvements and could increase overconfidence. At ICLR 2025, Zhang, Knox and Choi likewise showed that models often prematurely presuppose one interpretation; training that accounted for future conversation turns improved when models chose to clarify versus answer directly. citeturn15search8turn15search7

For your skill, that means **“ask when needed” cannot be an aspiration buried in the system prompt**. It should be a separate decision step.

**Step 3 — Establish the product thesis.**

Generate a compact draft with six fields:

```text
For:          [target role / customer + relevant circumstance]
Who need to:  [job / desired progress]
Today they:   [current alternative / workaround]
The product:  [coarse product proposition]
So that:      [user outcome + relevant business outcome]
It will not:  [first explicit boundaries]
```

Do not label that thesis “validated.” JTBD can help formulate the context and desired progress, and alternative-first positioning can help identify what behaviour or tool currently competes with the proposed product, but both are hypotheses until supported by relevant evidence. citeturn16search0turn17search11

**Human checkpoint: thesis and boundaries.** The agent should stop if the human’s intent is still materially ambiguous. The human—not the language model—owns the choices about target customer, strategic outcome and intentional exclusions.

**Step 4 — Research what can legitimately be researched without users.**

With permission and access, the agent can investigate the alternative landscape, documented workflows, standards, existing system constraints, known platform capabilities and public competitive claims. Dunford’s work usefully broadens “competition” to include the status quo and non-product alternatives, not merely companies with similar landing pages. citeturn17search11

But classify what the research can establish. A competitor’s documentation can establish that it offers a capability; it cannot establish that *your* users care about that capability. Search-volume data might be a signal; it is not proof of a job. A support-ticket theme can suggest an opportunity; Torres warns that such sources often lack the context supplied by a concrete customer story. citeturn13search6

**Step 5 — Generate an assumption and risk map before requirements.**

Use Cagan’s four-risk vocabulary as the default top-level sweep:

| Risk | Product-level question |
|---|---|
| **Value** | Will the target customer/user choose or care about this enough? |
| **Usability** | Can the intended users successfully get the value? |
| **Feasibility** | Can it be built under the known technology, skill and time constraints? |
| **Viability** | Does it work for the organization—policy, economics, legal/compliance, operations, partnerships, strategic fit? |

Cagan published this four-risk formulation in 2017 and reiterates that different initiatives have different risk profiles; he also explicitly cautions product managers against assessing feasibility without engineers or usability without designers. In other words, an agent can **identify** these risks, but should not claim that it has independently retired them. citeturn14search1turn14search9

I would add **ethical/safety risk as a fifth explicit check** rather than burying it in viability. Teresa Torres’s 2023 assumption taxonomy uses desirability, viability, feasibility, usability and ethical assumptions and describes assumption mapping in terms of importance versus strength of evidence. This is a particularly good fit for an agent: rank the beliefs on which the product depends, then surface the important ones supported by weak evidence. citeturn19search6turn19search10

**Step 6 — Create the brief, then ask for a scope decision.**

At this point the agent can produce the product brief. It should visually distinguish statements such as:

```text
[EVIDENCE]  31% of support cases in dataset X concerned...
[FACT]      The service must run inside the existing admin application.
[ASSUMPTION] Managers will change staffing decisions if trends are visible.
[PROPOSAL]  V1 should support weekly and daily workload views.
[DECISION]  V1 will not include forecasting. Approved by Jane, 2026-10-02.
```

The literal labels are optional; the semantic distinction should not be.

**Human checkpoint: scope/appetite.** Basecamp’s Shape Up pitch offers a useful company-specific technique here: explicitly state the *appetite*—how much investment the problem is allowed to consume—and *no-gos*, the use cases or functionality deliberately excluded to make the concept tractable. You do not need to adopt Shape Up wholesale for those two ideas to be useful. citeturn14search3

**Step 7 — Generate product requirements section by section.**

Do not ask the model to improvise a 4,000-word PRD in a single generation. Generate, critique and reconcile sections in a dependency order:

**intent → users/jobs → outcomes → boundaries → capabilities → functional obligations → quality/constraints → risks → metrics → release slice → open questions.**

Each substantive requirement should receive an ID and structured metadata, for example:

```yaml
id: PRD-FR-014
statement: >
  The product must allow an authorized support manager to compare
  workload over user-selectable reporting periods.
derives_from:
  - GOAL-02
  - JOB-01
source:
  type: human_decision
  ref: DEC-007
evidence_status: approved
release: v1
rationale: >
  Comparison is necessary to detect workload change rather than merely
  display a point-in-time total.
verification_intent: >
  Demonstrate that an authorized manager can obtain comparable workload
  values for each supported period.
```

The metadata is a recommended agent contract, not an industry standard. The qualities it is protecting—specificity, clarity, necessity, feasibility, traceability and verifiability—are well established in requirements engineering. citeturn13search3turn14search0

**Step 8 — Cut a coherent release, not merely a ranked feature list.**

For MVP definition, **story mapping is the best default among the methods in your prompt when the challenge is “what is the smallest coherent product?”** Jeff Patton’s 2014 *User Story Mapping* explicitly uses mapping to preserve the whole user journey, expose holes and slice an MVP/release rather than treating a backlog as a flat priority queue. citeturn16search1

Use **MoSCoW** when there is a fixed time boundary and genuine willingness to remove scope. The Agile Business Consortium’s 2026 guidance defines Must/Should/Could/Won’t Have this time and, in DSDM, explicitly warns against letting Musts consume everything; its typical recommendation is no more than about 60% Must-Have effort, preserving contingency. Those percentages are DSDM guidance, not universal laws. citeturn16search2

Use **RICE** for choosing among competing candidate investments where Reach, Impact, Confidence and Effort can be estimated with meaningful data. Intercom introduced its version publicly in 2018 and says real measurement should be used where possible and that the score is not a hard-and-fast rule. An LLM that invents reach and impact numbers defeats the point of the framework. citeturn14search2

Use **Kano** when you actually have customer-response data suitable for classifying needs into expected/must-be, performance and attractive/delighting qualities. The Kano model traces to Noriaki Kano and colleagues’ 1984 work; contemporary ASQ guidance still frames it as a way of interpreting customer needs. It is not a credible “agent guesses which feature is a delighter” algorithm. citeturn16search3turn3search1

My recommended default is therefore:

**story map for coherence → appetite/no-gos for the boundary → MoSCoW if a fixed delivery window needs explicit trade-offs → RICE only where comparative estimates have real inputs → Kano only when customer evidence exists.**

**Step 9 — Define success without fabricating precision.**

The agent can propose a measurement model:

```text
Goal:
Managers make better staffing decisions from workload visibility.

Candidate outcome signal:
Share of active managers who use workload comparison before staffing changes.

Candidate supporting measures:
Time to obtain the relevant trend.
Frequency of comparison use.
Data completeness / freshness.

Unknown:
Baseline.
Target threshold.
Causal relationship with staffing quality.
```

It **must not** convert that into “Increase staffing efficiency 20% in three months” unless that number came from a responsible human or defensible evidence. A false number makes a document look more rigorous while actually making it less grounded.

A North Star can be proposed where it genuinely captures delivered value, but Amplitude’s framework is one choice, not a requirement that the agent should force onto every internal tool or nascent product. citeturn18search1

**Step 10 — Run an independent reviewer pass and return unresolved decisions to the human.**

The review should not ask “does this look like a PRD?” It should ask:

* Does every major requirement trace to a problem, goal, constraint or approved decision?
* Which claims pretend to be evidence but are really inference?
* Which adjectives cannot be verified?
* Where did a requirement suddenly introduce a new user, integration or use case?
* Are any numeric targets unsourced?
* Are goals and requirements contradictory?
* Do the non-goals actually exclude plausible scope?
* Does V1 form a usable end-to-end slice?
* Is any high-consequence assumption being treated as settled?
* Did the PRD accidentally decide architecture or detailed UX?

ReqInOne’s results are useful here because the paper reports that direct generation can produce unsupported requirements and that ambiguity remains a problem even in more structured generation; its modular approach is evidence for using extraction, structuring and quality review rather than a single generative pass. citeturn15search1

**Final human checkpoint: baseline approval.** The resulting status should be something like `DRAFT`, `REVIEWED`, or `BASELINED/APPROVED`, not an implicit assumption that generated text became product intent by existing.

## Boundaries, discovery, and ask-versus-assume

The single most important improvement I would make over a typical PRD template is to treat **negative definition as a first-class product-management task**.

A product boundary should answer four different questions:

| Boundary | Example |
|---|---|
| **Target boundary** | “For support managers responsible for staffing decisions…” |
| **Excluded segment** | “Not intended as an individual-agent productivity scorecard.” |
| **Product responsibility boundary** | “Provides historical workload analysis; does not recommend or execute staffing changes.” |
| **Release boundary** | “Forecasting may be considered later but is explicitly outside V1.” |

That distinction matters because “non-goal” and “not in this release” are not equivalent. A **non-goal** says the product is deliberately not trying to optimize something. **Out-of-scope for V1** says it could fit the product but is deferred. Mixing the two makes future scope arguments almost inevitable.

Atlassian explicitly recommends a “what we’re not doing” section to keep work focused, and Basecamp’s no-gos formalize functionality or use cases intentionally excluded to fit the project’s appetite. Those are company practices, but together they show the value of making negative scope explicit. citeturn13search0turn14search3

I would make each important exclusion carry a **reason**:

```text
OUT-03
Not in V1: predictive staffing forecasts.

Reason:
The product thesis is initially about making historical workload visible.
Forecasting adds materially different data-quality and trust risks.

Revisit when:
Historical analysis has demonstrated sustained usage and the forecasting
value assumption has evidence.
```

This is much stronger than a graveyard called “Future Features.”

Also distinguish **excluded users** from **anti-personas**. Nielsen Norman Group defines an antipersona as a representation of a group that could *misuse* a product in ways that harm target users or the business. It is a threat/misuse design technique, not a fancy name for “people we are not targeting.” For ordinary scope, call them excluded or non-target segments; use antipersonas for plausible harmful/malicious misuse where consequence warrants it. citeturn17search0

A strong scope-creep rule for the agent is:

> **No new requirement joins the baseline merely because it is useful or logically adjacent.**

A proposed addition must answer:

```text
What changed?
What goal/job/constraint does this trace to?
What new evidence or decision justifies it?
Is it required for the currently approved release?
What does it displace, or has the appetite/scope formally changed?
Which downstream artefacts become stale?
Who approves the scope delta?
```

That is a synthesis of explicit no-go practice, agile living-document practice and requirements traceability/change management. ISO/IEC/IEEE 29148 describes requirements management as identifying, documenting, maintaining, communicating, tracing and tracking requirements through the lifecycle; Atlassian similarly treats updated requirements as expected rather than treating the original sign-off as immutable. citeturn13search3turn13search0

On **discovery without a team or users**, the agent needs firm epistemic limits.

It can reasonably perform:

| Agent can do alone | Status |
|---|---|
| Reformulate the supplied idea as possible user jobs/problems | **Hypothesis** |
| Identify logical assumptions | **Analysis** |
| Categorize risk | **Analysis** |
| Research publicly documented alternatives | **External evidence** |
| Research standards/platform constraints | **External evidence** |
| Find analogous workflows and products | **External evidence / inspiration** |
| Produce competing product-thesis options | **Proposal** |
| Suggest tests or interviews that would reduce uncertainty | **Proposal** |
| Identify missing product decisions | **Analysis** |

It cannot independently establish:

| Agent cannot establish from prose/web research alone | Required evidence |
|---|---|
| “Users have this problem” | Actual user/customer evidence or strong behavioural data |
| “This problem is important enough to change behaviour” | Behavioural/demand evidence |
| “Users will understand this workflow” | Usability evidence |
| “Customers will pay / organization can monetize” | Relevant viability evidence |
| “Engineering can deliver this inside the stated appetite” | Engineering assessment/prototype where material |
| “This metric target is realistic” | Baseline, historical/benchmark evidence or responsible human commitment |
| “This legal/compliance interpretation is definitely correct” | Qualified/legal authoritative assessment where consequential |

Cagan’s 2020 discussion explicitly argues that the type and strength of product discovery work should depend on both uncertainty and consequence, and that engineers/designers need to participate in feasibility/usability judgement; Torres’s assumption-testing material similarly ties different assumption categories to different types of evidence. citeturn14search9turn19search10

This also gives you a clean **ask-vs-assume policy**.

The agent should **always ask rather than silently infer** when a missing answer would alter:

* the desired product outcome;
* primary target user/customer;
* an intentional non-goal or product boundary;
* a hard constraint or appetite;
* a commitment, deadline or business priority;
* a numeric success target;
* acceptance of a significant risk;
* a strategic trade-off between plausible product directions.

It can **infer tentatively and present a recommendation** when the choice is low-consequence, reversible and derived from already-approved intent: terminology, document organization, likely alternative products to investigate, candidate quality attributes, candidate metrics, candidate release cuts, or possible open questions.

It should **never turn an inference into a factual customer claim**, particularly persona details, motives, frequency of behaviour, market demand, willingness to pay or arbitrary numerical objectives.

The best interaction pattern is, in my judgement, **one consequential decision at a time, ordered upstream to downstream**. Do not ask what latency threshold the user wants before you know whether latency is strategically material; do not ask which customer segment to prioritize after generating 30 requirements for an assumed segment. Clarification research does not establish “one question per turn” as a universal law, but it does establish the more important premise: models often fail to notice ambiguity and prematurely choose one interpretation, so deliberate clarification policy matters. citeturn15search8turn15search7

For a good product-agent UX, I would render a question like this:

> **I need one scope decision before writing requirements.**  
> You described this as a tool for support teams, but the product differs substantially depending on who makes the decision from its output.  
>   
> **Primary user:**  
> **Recommended default:** support managers who make staffing/operational decisions.  
> Alternative: individual support agents monitoring their own work.  
> Alternative: executives tracking service performance.  
>   
> Which is primary?

That is materially better than either “Please provide target audience” or silently choosing one.

## Reviewer rubric, failure modes, and defences

There is no evidence-backed universal PRD scorecard, so the following is a **recommended reviewer-agent rubric synthesized from product practice, ISO/NASA requirement qualities and the known LLM failure modes**. It should be treated as an engineering design for your skill, not as an externally standardized maturity model. citeturn13search3turn14search0turn15search1

Score each dimension **0–3**:

* **0 — absent or actively misleading**
* **1 — present but vague, unsupported or internally inconsistent**
* **2 — usable; minor gaps remain**
* **3 — explicit, evidence-aware, decision-relevant and traceable**

| Dimension | What a `3` requires |
|---|---|
| **Problem and intent** | Clear current problem/desired change; does not merely restate a solution; strategic reason is understandable |
| **Target and job** | Primary target is bounded; relevant situation/job is explicit; factual claims have evidence; non-targets are clear where material |
| **Goals and success** | Product outcomes are distinct from outputs; success measures connect to goals; no fabricated targets |
| **Boundaries** | Non-goals, product-responsibility limits and release out-of-scope are concrete enough to reject plausible additions |
| **Requirements quality** | Each requirement is necessary, understandable at the right level, traceable and capable of downstream verification |
| **Quality attributes and constraints** | Material NFRs/constraints are covered without generic boilerplate or invented thresholds |
| **Evidence, assumptions and risks** | Facts, evidence, assumptions, proposals and decisions cannot be confused; important weakly evidenced assumptions are visible |
| **Release coherence** | First release accomplishes an end-to-end user outcome; deferments are explicit rather than hidden |
| **Open questions and decisions** | Material unknowns are visible with consequence/owner; decisions preserve rationale |
| **Traceability and handoff** | Stable IDs connect goals → product requirements → future feature/architecture/test artefacts; document status/change state is clear |

I would use **hard readiness gates** rather than pretending that a score of, say, 24/30 automatically means “good.” Mark the PRD **NOT READY** if any of these occurs:

1. The primary problem, intended user or desired outcome remains materially ambiguous.
2. There is no meaningful non-goal/out-of-scope boundary.
3. A major user/customer claim is presented as fact with no source or evidence state.
4. A numeric success target was invented by the model.
5. A critical assumption/risk is concealed inside a confident requirement.
6. Requirements materially contradict each other.
7. The first release has no coherent user outcome.
8. A requirement introduces an unapproved new segment, integration, business obligation or product responsibility.
9. The PRD is deciding detailed interaction behaviour or architecture without an actual product constraint requiring it.
10. Downstream agents cannot tell which content is approved versus speculative.

These gates are intentionally asymmetric: a shorter PRD with explicit unknowns is better than an impressive-looking PRD full of unsupported certainty.

The main agent failure modes and the corresponding defences are:

| Failure mode | What it looks like | Defence |
|---|---|---|
| **Generic boilerplate** | Every product “must be intuitive, scalable, secure and high-performance” | Make every section pass a decision test: *what would we build differently because this sentence exists?* Allow `N/A`; never force content merely to fill a heading |
| **Invented personas** | “Sarah, 34, busy urban professional…” appears from a one-line idea | Permit persona/job claims only from supplied/researched evidence; otherwise label target/job as hypothesis; prefer role + circumstance over fictional biography |
| **Invented metrics** | “Increase retention 15%” with no baseline or owner | Separate metric proposal from target commitment; target remains `OPEN/TBR` until sourced |
| **Scope inflation** | Model generates every adjacent useful feature | Requirement admission rule: must trace to an approved goal/job/constraint/decision; everything else goes to `candidate/deferred` |
| **Solution-first framing** | Problem statement says “users need an AI dashboard” | Maintain separate problem and proposed-solution objects; ask what users do today and what progress they need |
| **Pseudo-validation** | “Competitor X has it, therefore users need it” | Distinguish external market evidence from user evidence; never upgrade inference to `validated` |
| **Premature certainty under ambiguity** | Agent silently picks one interpretation | Explicit ambiguity/impact pass before generation; ask the highest-consequence question |
| **One-shot PRD generation** | Smooth prose hides unsupported derivations and contradictions | Extract → frame → risk map → generate sections → requirement audit → contradiction/trace review |
| **Vague requirements** | “Fast,” “seamless,” “robust,” “appropriate,” “easy” | Reviewer flags unverifiable adjectives; ask for a real threshold only where the distinction matters |
| **False prioritization precision** | RICE/Kano numbers confidently guessed | Never score dimensions without evidence; use qualitative uncertainty or request data |
| **Stale document** | Feature specs and architecture reflect decisions the PRD no longer shows | Stable IDs, version/status, decision log, dependency links and change-impact check |
| **Architecture leakage** | PRD mandates React, Kafka, microservices, table schema, etc. | Ask whether the technology is an actual external/business constraint; if not, move the choice to architecture |
| **Human authority erosion** | Suggested product strategy silently becomes “approved requirements” | Distinct `PROPOSAL` and `DECISION` states; baseline requires explicit human acceptance |

Several of these are directly supported by current LLM research rather than mere caution. CLAMBER’s 2024 results show that models can fail both to recognize ambiguity and to generate appropriate clarification; ReqInOne’s 2025 work identifies hallucination and controllability issues with direct SRS generation and instead decomposes the task; the 2025 systematic review shows that LLM-assisted requirements engineering is an active but still young research area rather than a mature substitute for stakeholder participation. citeturn15search8turn15search1turn15search6

For wording quality, NASA’s 2023 requirement checklist is surprisingly useful even for ordinary software when used selectively. It asks whether requirements are necessary, feasible, clear, appropriately scoped and written in terms of what is needed rather than prematurely specifying how to implement it. It also explicitly calls out assumptions and unresolved values. Again, NASA’s process overhead should not be copied; the linguistic tests are what transfer. citeturn14search0

For persona hallucination specifically, contemporary Nielsen Norman Group guidance describes personas as representations of **real information about the target audience** and cautions against creating them from analytics alone without new research. This is a useful antidote to the LLM tendency to create plausible fictional people merely because a template has a “Personas” heading. citeturn17search4

For scope inflation, require an explicit trace from requirement to upstream need. ISO/IEC/IEEE 29148 formally treats traceability as the derivation path upward and flow-down path downward; that is exactly the property that allows a reviewer agent to ask “why does `PRD-FR-027` exist?” rather than judging it by how plausible it sounds. citeturn13search3

The rubric should therefore reward **epistemic honesty more than completeness**. A strong PRD can say:

> `OPEN — We do not yet know the maximum acceptable report-generation delay. Existing research establishes that current reports take several minutes manually, but no user evidence establishes a sub-second requirement. Architecture should not optimize to an arbitrary latency target until this is resolved.`

That is much more valuable than:

> `NFR-12 — The platform shall respond within 200ms at the 99th percentile.`

when the model invented 200 ms.

## Downstream handoff and evidence map

The PRD should end in a **machine-consumable handoff contract**, not merely prose. This is where your existing feature-spec skill and future architecture/build agents can connect cleanly.

I would define the canonical handoff like this:

```yaml
product:
  id: PROD-001
  prd_version: 0.7
  status: reviewed
  owner: product-owner
  reviewed_at: 2026-10-02

intent:
  thesis_ref: THESIS-001
  target_refs: [TARGET-001]
  goal_refs: [GOAL-001, GOAL-002]
  non_goal_refs: [NONGOAL-001, NONGOAL-002]

release:
  id: RELEASE-V1
  in_scope:
    - CAP-001
    - CAP-002
  explicitly_out:
    - CAP-007
    - CAP-009

requirements:
  functional:
    - PRD-FR-001
    - PRD-FR-002
  quality:
    - PRD-NFR-001
    - PRD-NFR-002

constraints:
  - CONST-001
  - CONST-002

unresolved:
  blocking:
    - OPEN-004
  non_blocking:
    - OPEN-009

risks:
  - RISK-003
  - RISK-006

decisions:
  - DEC-005
  - DEC-011
```

The exact YAML is a proposed interface, not a product-management convention. The underlying traceability is established requirements practice. ISO/IEC/IEEE 29148 explicitly covers tracing requirements both upward to source needs and downward to implementation; that makes stable IDs particularly useful when autonomous agents are consumers. citeturn13search3

The **feature-spec contract** should be:

> Every feature-level behaviour, state and acceptance criterion must trace to one or more PRD requirements or approved release goals. The feature-spec agent may *elaborate* behaviour but may not silently create a new product responsibility, target segment, integration or requirement. If elaboration uncovers a missing product-level decision, it emits a **PRD change request** rather than guessing.

That creates a clean ownership boundary between your two skills:

```text
PRD:
Why this product exists
Who it serves
What outcomes matter
What it is responsible for
What it explicitly is not
What constraints every valid solution must respect

Feature specification:
Exactly how a bounded capability behaves
States
Transitions
User/system interactions
Validation
Feature edge cases
Acceptance criteria
```

The **architecture contract** should be:

> Architecture receives product requirements, quality requirements, external constraints, dependencies and unresolved feasibility risks. It chooses the implementation. Where architecture discovers that a PRD requirement is infeasible or disproportionately costly, it raises a feasibility finding against that requirement instead of silently weakening it.

This maps cleanly onto NASA’s transferable distinction between requirements stating what is needed and solution design supplying how, and onto Cagan’s insistence that feasibility judgment requires engineering involvement. citeturn14search0turn14search9

Architecture decisions can then carry their own mappings:

```text
ADR-014 satisfies:
  PRD-NFR-003
  PRD-NFR-008
  CONST-002

ADR-014 introduces:
  new constraint CONST-011

PRD impact:
  none / review required
```

The **autonomous-build contract** should be stricter still. A build agent should consume only requirements belonging to an approved/baselined release. `ASSUMPTION`, `PROPOSAL` and unresolved blocking items are not silently convertible into implementation requirements. Where a necessary detail is absent, the pipeline should either delegate to the appropriate downstream spec agent or surface an exception, not invent a product decision.

The sync rule should be:

> **Intent flows downward; discoveries and conflicts flow upward.**

A product-level change should update the PRD first when it alters target user, goal, non-goal, product responsibility, baseline requirement, material NFR/constraint, success definition or release boundary. Downstream feature and architecture artefacts should retain links rather than copy upstream rationale wholesale. Atlassian’s living-page approach and ISO’s requirements-management model both support this pattern: maintain a canonical source and trace linked elaborations rather than freezing or duplicating everything at kickoff. citeturn13search8turn13search3

The resulting document graph can be thought of as:

```text
Evidence / human intent
        ↓
Product thesis
        ↓
Goals + non-goals
        ↓
Product requirements + constraints
        ↓
Release boundary
       ↙ ↘
Feature specs     Architecture decisions
       ↘          ↙
      Implementation + tests
              ↓
       Product evidence
              ↓
       PRD / decision updates
```

That is a better mental model for an agentic toolchain than “write a PRD, then throw it over the wall.”

Finally, the most important sources and how much weight I would give them are below. This separation matters because a surprising amount of product-management literature consists of useful but proprietary practitioner frameworks rather than standards or controlled evidence.

| Source | Date | Evidence type | What it legitimately supports |
|---|---:|---|---|
| **Manifesto for Agile Software Development** | 2001 | Widely influential primary declaration | Collaboration/change over comprehensive fixed documentation; does **not** say “do not document.” citeturn19search1 |
| **ISO/IEC/IEEE 29148, Requirements Engineering** | 2018 | International engineering standard | Requirements quality, elicitation, validation, verification, lifecycle management and traceability. citeturn13search3 |
| **NASA, “How to Write a Good Requirement”** | Updated 2023 | High-assurance engineering guidance | Useful quality checks for individual requirements; not a SaaS PRD template. citeturn14search0 |
| **Atlassian, Agile Requirements Documentation** | 2013 | Company practice / practitioner guidance | Concise linked requirement page, assumptions, goals, strategic fit, living documentation. citeturn13search8 |
| **Atlassian, current PRD guide** | Current 2026 | Company practice / practitioner guidance | Agile/living PRD, collaboration, goals, assumptions, out-of-scope, anti-patterns of exhaustive upfront specification. citeturn13search0 |
| **Bryar & Carr, *Working Backwards*** | 2021 | Practitioner book by former Amazon executives | Amazon’s Working Backwards/PRFAQ practice; company custom, not universal process. citeturn19search12 |
| **Amazon public Working Backwards description** | Current Amazon source, accessed 2026 | Company primary source | Amazon says its product development starts with Working Backwards documents, including press release and FAQ, before coding. citeturn13search1 |
| **Intercom, Job Stories / one-page brief** | 2013, 2016 | Company practice | Research-centred Job Stories and a concise A4 project brief; useful precedent, not standard. citeturn18search0turn18search4 |
| **Basecamp, *Shape Up*: “Write the Pitch”** | *Shape Up* practice, current online edition | Company method | Problem, appetite, solution, rabbit holes and explicit no-gos as a scoping system. citeturn14search3 |
| **Jeff Patton, *User Story Mapping*** | 2014 | Practitioner book | End-to-end shared understanding and slicing coherent MVP/releases rather than flat feature prioritization. citeturn16search1 |
| **Christensen, Hall, Dillon & Duncan, JTBD** | 2016 | Practitioner/management research article | Customer progress in circumstances; functional/social/emotional job framing. citeturn16search0 |
| **Marty Cagan, “The Four Big Risks”** | 2017 | Practitioner framework/opinion | Value, usability, feasibility and business viability as a useful risk taxonomy. citeturn14search1 |
| **Intercom, RICE** | 2018 | Company-created prioritization framework | Reach, Impact, Confidence, Effort; use real measurements and judgment rather than treating score as law. citeturn14search2 |
| **Agile Business Consortium, MoSCoW** | Updated May 2026 | Formal DSDM/agile practitioner guidance | Must/Should/Could/Won’t, particularly for fixed-time projects; DSDM contingency guidance. citeturn16search2 |
| **Kano et al., Attractive/Must-Be Quality** | 1984 | Foundational quality-management research | Customer-reaction categories underlying the Kano model; should be evidence-based rather than guessed. citeturn3search1turn16search3 |
| **Teresa Torres, *Continuous Discovery Habits*** | 2021 | Practitioner book/framework | Outcomes → customer opportunities → solutions → assumptions; continuous discovery and research-centred OST. citeturn19search3turn13search6 |
| **Teresa Torres, assumption testing** | 2023, subsequently updated | Practitioner framework | Desirability/viability/feasibility/usability/ethical assumptions and evidence-based assumption testing. citeturn19search6turn19search10 |
| **Roman Pichler, Product Vision Board** | First created 2011; current guidance 2026 | Practitioner framework | Distinguishing vision/product strategy from detailed requirements; target group, needs, product differentiation, business goals. citeturn17search1 |
| **April Dunford, positioning framework** | 2020–2021 | Practitioner framework | Alternatives-first positioning; differentiation → value → best-fit customer → market category. citeturn17search11turn18search2 |
| **Nielsen Norman Group, antipersonas** | 2022 | UX practitioner guidance | Antipersonas are misuse/threat actors, not merely people outside the target segment. citeturn17search0 |
| **Amplitude, North Star Framework** | Current playbook, 2024–2026 | Company/practitioner framework | One way to connect customer value and product strategy through a leading metric; not proof that every PRD needs one. citeturn18search1 |
| **Zhang et al., CLAMBER, ACL** | 2024 | Peer-reviewed LLM research | LLMs struggle to recognize ambiguity and generate high-quality clarification reliably. citeturn15search8 |
| **Zhang, Knox & Choi, ICLR** | 2025 | Peer-reviewed LLM research | Models often prematurely assume an interpretation; training for future conversational consequences improved clarifying-question behaviour in the studied setting. citeturn15search7 |
| **Zhu, Cordeiro & Sun, ReqInOne** | 2025 | Research preprint | Evidence for modular, source-grounded requirements generation over naive full-document prompting; promising but not conclusive industrial validation. citeturn15search1 |
| **Ferrari et al., LLMs for Requirements Engineering systematic review** | 2025 | Systematic literature review/preprint | Reviews 74 primary studies from 2023–2024 and shows an emerging field heavily focused on elicitation/validation, with the evidence base still developing. citeturn15search6 |

The resulting design principle for your skill is therefore:

**A good PRD agent is not primarily a document writer. It is an intent-preserving, evidence-aware requirements editor.** It should be conservative about facts, aggressive about exposing uncertainty, unusually good at saying “not in this product,” and structured so every downstream agent can tell the difference between **what the human decided, what evidence supports, what the agent proposed, and what nobody yet knows**. That synthesis fits both modern lean product practice and the older but still valuable requirements-engineering emphasis on derivation, validation, traceability and lifecycle change. citeturn13search0turn13search3turn15search1