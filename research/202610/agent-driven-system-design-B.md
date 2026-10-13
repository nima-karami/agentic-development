# From PRD to System Architecture: A Method for an Architecture-Design Agent (October 2026)

An agent should not jump from a PRD straight to a stack. It should run a short, risk-driven loop. First, pull out quality-attribute scenarios and hard constraints, and get a human to confirm them. Next, model the domain into bounded contexts that own their data. Then produce two or three real candidate architectures, defaulting to a modular monolith, and score them in an explicit trade-off table against the confirmed scenarios. Have a human choose. Record the choice as C4 diagrams-as-code plus ADRs, plus fitness functions that keep the code honest. Finally, mark every high-risk assumption for a spike before feature specs are written.

**Important limitation of this report:** this session had no web search or fetch access. A research sub-agent hit the same limit. Everything below about established practice comes from well-known, named books, SEI reports and engineering write-ups that I am confident about. Every claim about LLM research and tooling is flagged by confidence. **I could not verify any development from June to October 2026**, and Section 7 says so plainly rather than inventing it.

## TL;DR

- **Method:** PRD → quality-attribute scenarios + constraints (human confirms) → domain and bounded contexts → 2–3 candidate options → ATAM-lite trade-off table (human decides) → C4 + ADRs + fitness functions → spike list → handoff. The agent can draft every step. Humans must own the priorities, the constraints, the final option choice and the risk acceptance.
- **Right-sizing:** scale depth by risk, not by how impressive the design looks. A small tool needs a one-to-two-page design and three to five ADRs. A product app needs C4 L1–L2, a data-ownership map, failure modes and about 8–15 ADRs. A multi-team platform needs a full arc42-shaped document, team/context alignment and conformance automation. The default answer for anything short of a multi-team platform is a modular monolith on managed services. Microservices, event sourcing or Kubernetes each need a scenario that requires them.
- **Agent-specific defences:** LLMs tend to produce generic, popular, over-engineered designs that look plausible but are not tied to the requirements. Counter this by making every component and technology trace back to a requirement or scenario. Force multiple options with an explicit "do nothing simpler?" option. Check technology currency against live sources, not training data. Run the user's existing fresh-context critic as an adversarial review. Make the design executable through architecture tests so drift is caught in CI.

## Key Findings

1. **The process is well established and agent-friendly at the drafting level.** SEI's Attribute-Driven Design (ADD; Cervantes & Kazman, *Designing Software Architectures*, 2016), quality-attribute scenarios (Bass, Clements & Kazman, *Software Architecture in Practice*, 4th ed., 2021) and ATAM (Kazman, Klein & Clements, SEI CMU/SEI-2000-TR-004, 2000) give a repeatable structure. The parts that cannot be delegated are *prioritisation* (which quality attribute wins), *constraint truth* (budget, team skills, compliance, existing platform), and *risk acceptance*. Those are stakeholder judgments, not analysis.
2. **Risk-driven depth is the established answer to right-sizing.** George Fairbanks' *Just Enough Software Architecture* (2010) argues that the effort spent on architecture should match the risk of failure. Martin Fowler's "MonolithFirst" (2015) and "Microservice Premium" (2015) argue that distribution carries a fixed tax that only pays off at scale and team size. Public reversals back this up: Segment's "Goodbye Microservices" (2018), Amazon Prime Video's video-monitoring rewrite from distributed serverless components to a single process (March 2023, reported ~90% infrastructure cost reduction), and Shopify's modular-monolith approach (Kirsten Westeinde, "Deconstructing the Monolith", 2019).
3. **The minimum useful documentation set is small:** C4 Context + Container diagrams as code, a data-ownership table, quality-attribute scenarios, ADRs for each significant decision, a risks/spikes list, and fitness functions. arc42 provides the full outline when the system is large.
4. **Evidence on LLM-generated architecture is thin and mostly exploratory.** The most-cited early study (Dhar, Vaidhyanathan & Varma, "Can LLMs Generate Architectural Design Decisions? An Exploratory Empirical Study", ICSA 2024, arXiv 2403.01709) found that LLMs can produce relevant design decisions but do not match human architects without help. Literature reviews from 2025 describe the field as early, with little rigorous evaluation. I could not verify a widely accepted system-design benchmark for LLMs. Treat any vendor claim of one with suspicion until you can check it.
5. **The strongest lever against drift is executable architecture.** Fitness functions (Ford, Parsons & Kua, *Building Evolutionary Architectures*, 2017; 2nd ed. 2022 with Sadalage) and architecture-test tools (ArchUnit for JVM, dependency-cruiser for JS/TS, import-linter for Python, Packwerk for Ruby, NetArchTest for .NET) turn the design's boundaries into CI failures. This matters even more when agents write the code.

## 1. The Process: Requirements to System Design

### Established practice

- **Quality-attribute elicitation.** SEI's Quality Attribute Workshop (Barbacci et al., SEI, 2003) and the six-part scenario form from *Software Architecture in Practice*: source, stimulus, environment, artifact, response, response measure. Example: "When 2,000 players submit answers within 3 seconds of a reveal (stimulus), during a live session (environment), the scoring service (artifact) records all answers (response) with p99 under 500 ms and zero lost writes (measure)." Scenarios without a response measure cannot be tested and should not drive architecture.
- **Utility tree and prioritisation.** ATAM ranks scenarios by business importance and architectural difficulty (H/M/L × H/M/L). Only high-high and high-medium scenarios should shape the structure.
- **Constraints.** These are separate from requirements: they are decisions already made (mandated cloud, existing identity provider, regulatory regime, team languages, budget, deadlines). arc42 Section 2 is dedicated to them.
- **Domain modelling and boundaries.** Eric Evans' *Domain-Driven Design* (2003), Vaughn Vernon's *Implementing DDD* (2013), Alberto Brandolini's EventStorming and the DDD Crew's Bounded Context Canvas. Bounded contexts are the most reliable seams for modules or services, because each owns its language, its invariants and its data. Team Topologies (Skelton & Pais, 2019) adds Conway's Law: boundaries should match how teams can own things within their cognitive load.
- **Option generation.** ADD iterates: choose a driver, choose design concepts (reference architectures, tactics, patterns, externally developed components), instantiate them, then record and analyse. Michael Keeling's *Design It!* (2017) offers lightweight workshop techniques that fit an agent loop well.
- **Trade-off evaluation.** ATAM's outputs are: sensitivity points (a property that strongly affects one quality attribute), trade-off points (a property that affects several attributes in opposite directions), risks and non-risks. A full ATAM is a multi-day stakeholder event. An "ATAM-lite" table is the practical agent version.
- **Documentation.** C4, arc42 and ADRs (Section 4).

### Which steps an agent can run alone vs. with a human

| Step | Agent alone | Human required | Why |
|---|---|---|---|
| Extract candidate quality attributes and scenarios from the PRD | Yes (draft) | **Confirm and prioritise** | Priorities are business judgments. PRDs usually leave non-functional requirements implicit. |
| List constraints | Draft from PRD and repo | **Confirm**, especially budget, compliance, team skills, existing platform | The agent cannot know organisational facts that are not written down. |
| Domain model / bounded contexts | Yes (EventStorming-style from PRD flows) | Review with a domain expert | Language and invariants live in people's heads. |
| Generate 2–3 options | Yes | No | Generation is cheap, so make it mandatory. |
| Trade-off table, sensitivity and trade-off points | Yes | Review | |
| **Choose the option** | Recommend | **Decide** | Accountability and risk appetite. |
| Write C4, ADRs, fitness functions | Yes | Skim and approve | |
| Identify spikes | Yes | Approve time-box | |
| Run spikes and update the design | Yes (agent can build throwaway spikes) | Review outcome | Reality check. |

## 2. Right-Sizing

**Principle (established):** match architectural effort to risk (Fairbanks, 2010). Treat distribution, eventual consistency and extra infrastructure as costs that a scenario has to justify (Fowler, 2015).

| Tier | Typical signals | Design depth | Default shape |
|---|---|---|---|
| **Small internal tool** | 1 team or person, <100 users, low data sensitivity, failure is tolerable | 1–2 pages: context, one container diagram, data table, 3–5 ADRs, top 3 risks | Single deployable, managed DB (or SQLite/hosted Postgres), platform SSO, PaaS hosting |
| **Single product app** | 1–2 teams, external users, money or PII, uptime matters | 5–12 pages: QA scenarios, C4 L1–L2, data ownership, integration contracts, failure modes, environments, 8–15 ADRs, fitness functions | Modular monolith with enforced module boundaries, one primary relational DB with schema-per-module, a queue only where a scenario needs async, managed identity |
| **Multi-team platform** | 3+ teams, independent release cadences, varied scaling profiles, regulatory zones | Full arc42-shaped doc, context map, team ownership, API/event contracts, SLOs, threat model, conformance automation | Services *along bounded contexts and team lines* (often a few coarse services plus a modular core), async events between contexts, platform team for paved roads |

**Over-engineering red flags:** microservices with one team. Event sourcing with no audit or temporal-query scenario. Kubernetes with no platform team. CQRS with no read/write asymmetry. A service mesh or multi-region setup with no availability scenario that needs it. Micro-frontends with one front-end team. "Future scale" given as the only justification.

**Under-engineering red flags:** no named owner for each data entity. No answer to "what happens when X is down?" No idempotency on payments or retries. Auth bolted on later. No environment strategy. No observability plan. No data migration or versioning story. Shared tables written by several modules.

**Opinion (mine):** the most valuable single rule for an agent is: *every component, store, queue and technology in the design must cite the scenario or constraint that forces it. Anything without a citation is removed or moved to "deferred options".*

## 3. Architecturally Significant Decisions

| Decision | Forces that decide it | Sensible default | Red flags |
|---|---|---|---|
| **Decomposition** (monolith / modular monolith / services) | Team count and autonomy, independent deploy/scale needs, fault isolation, domain clarity, ops maturity | Modular monolith with boundaries enforced in CI (Shopify-style), so modules can be extracted later | Services before boundaries are stable. "Distributed monolith" (services sharing a DB or deployed in lockstep). |
| **Data storage and ownership** | Consistency needs, query shapes, volume, compliance/residency, retention | One relational DB (Postgres is a common default) with each table owned by one module. Add specialised stores only for a proven query or volume need. | Several writers to one table. A store per service "because microservices". No backup/restore or migration plan. |
| **Sync vs. async** | Latency budget, coupling tolerance, burst absorption, need for the caller to know the outcome | Synchronous calls inside the monolith and for user-facing queries. Async (queue/events) for slow, bursty or cross-context side effects. Transactional outbox for reliable publishing (Chris Richardson, microservices.io). | Async everywhere with no tracing. Synchronous call chains across 3+ services. Dual writes without an outbox. |
| **State and consistency** | Invariants (money, inventory, scores), concurrency, offline/reconnect, real-time | Strong consistency inside an aggregate or context. Eventual consistency between contexts, with idempotency keys and sagas only where needed (Kleppmann, *Designing Data-Intensive Applications*, 2017). | Distributed transactions across services. Client-held authoritative state. No idempotency on retries. |
| **Identity and auth** | Existing IdP, B2B/B2C, SSO, multi-tenancy, regulatory | Buy: managed IdP or existing org IdP via OIDC. Authorise at the domain boundary. Model tenant ID from day one if multi-tenant. | Home-grown password storage. Authorisation only in the UI. Tenancy added later. |
| **Front-end architecture** | SEO/first-load needs, interactivity, team count, device/network conditions, design system | One app shell. Rendering per route (static/SSR for content and SEO, client-rendered for app-like screens). Server state through a query/cache library. Minimal global client state. Shared design system. | Micro-frontends with one team (Thoughtworks Technology Radar has warned about "micro frontend anarchy"). Global stores holding server data. SPA by default for content sites. |
| **Deployment and environments** | Release cadence, compliance, cost, ops skills, preview needs | Managed PaaS/containers. Environments: local, ephemeral preview per PR, staging, prod. Infra as code. Trunk-based development with feature flags. | Kubernetes with no platform owners. Hand-built snowflake environments. Long-lived environment branches. |
| **Observability** | SLOs, distributed flows, incident response | Structured logs, metrics and traces via OpenTelemetry from the first release. SLOs for the top 2–3 user journeys. | "Add logging later". No correlation IDs across async hops. |
| **Security boundaries** | Data classification, threat model, compliance, third parties | Trust boundaries drawn on the container diagram. Secrets manager. Least privilege per component. Lightweight STRIDE pass on each boundary. | Flat network trust. Secrets in env files in the repo. PII spread across stores. |
| **Build vs. buy** | Is it core or differentiating? Total cost of ownership, lock-in, compliance, time-to-market | Buy or use managed services for non-differentiating capabilities (auth, payments, email, search, observability). Build the domain core. | Building commodity infrastructure. Buying the core differentiator. No exit plan for critical vendors. |

Use vendor frameworks as checklists, not as architectures: AWS Well-Architected (six pillars, sustainability added 2021), Microsoft Azure Well-Architected Framework, Google Cloud Architecture Framework.

## 4. Documentation: What Works for Humans and Agents

- **C4 model (Simon Brown; c4model.com).** Context, Container, Component, Code. Established and notation-light. For system design, **Context and Container are mandatory, Component only for complex containers, and Code never.** Add C4's dynamic and deployment diagrams where the flow or topology carries risk.
- **arc42 (Gernot Starke & Peter Hruschka).** A 12-section template: goals, constraints, context, solution strategy, building blocks, runtime, deployment, cross-cutting concepts, decisions, quality, risks, glossary. Use it as the outline for large systems and as a checklist for smaller ones.
- **ADRs (Michael Nygard, "Documenting Architecture Decisions", 2011; MADR template; Olaf Zimmermann's Y-statements).** One decision per file: context, options, decision, consequences, status. Lightweight ADRs have long held "Adopt" on the Thoughtworks Technology Radar. ADRs are the best format for agents because they are atomic, greppable and supersedable.
- **Diagrams as code.** Mermaid (renders natively in GitHub, GitLab, Bitbucket and many doc tools, and LLMs write it fluently; C4 support exists but is limited). Structurizr DSL (one model, many views, so it stays consistent across C4 levels; best for medium and large systems). D2 (better layout and looks, less native rendering). Recommendation: **Mermaid for small and medium systems, Structurizr DSL once there are more than about 10 containers or several views of the same model.**
- **Fitness functions.** Executable checks for architectural properties: dependency rules, latency budgets, bundle-size budgets, coupling metrics.
- **Decision log.** An index of ADRs with status, kept in the repo.

**Minimum useful set (opinion, drawing on the above):** `architecture.md` (drivers, constraints, strategy, data ownership, risks), C4 L1+L2 as code, `adr/NNNN-*.md`, and a `fitness/` config (architecture tests plus budgets). Everything lives in the repo next to the code so agents can read it.

### Recommended design-document structure

| Section | Small | Medium | Large |
|---|---|---|---|
| 1. Summary and decision snapshot (BLUF) | ✔ | ✔ | ✔ |
| 2. Drivers: top quality-attribute scenarios (with measures), constraints, assumptions | top 3 | top 5–8 + utility tree | full utility tree |
| 3. Context (C4 L1) and external dependencies | ✔ | ✔ | ✔ + context map |
| 4. Domain model and bounded contexts | list | Bounded Context Canvas per context | context map + team ownership |
| 5. Containers (C4 L2): responsibilities, tech, interfaces | ✔ | ✔ | ✔ per context |
| 6. Data ownership and lifecycle (entity → owner, store, retention, PII class) | table | table + consistency rules | + residency, contracts |
| 7. Integration and communication (sync/async, contracts, versioning) | brief | ✔ | API/event catalogue |
| 8. Runtime views for 2–3 critical flows, including failure paths | 1 | 2–3 | per critical journey |
| 9. Deployment topology and environments | ✔ | ✔ | ✔ + regions/tenancy |
| 10. Cross-cutting: identity, security boundaries, observability, error handling | brief | ✔ | ✔ + threat model |
| 11. Options considered and trade-off table | short | ✔ | ✔ + ATAM-lite record |
| 12. ADR index | 3–5 | 8–15 | many, per context |
| 13. Risks, open questions, spikes | ✔ | ✔ | ✔ |
| 14. Fitness functions and conformance rules | optional | ✔ | ✔ enforced in CI |
| 15. Handoff: work breakdown by module, interface contracts | ✔ | ✔ | ✔ |

### Choosing diagram types

- **Who uses it, and what does it talk to?** C4 System Context.
- **What are the deployables and data stores, and how do they talk?** C4 Container. This is the diagram most worth getting right.
- **How does a critical flow behave, including failure?** Sequence diagram (Mermaid `sequenceDiagram`) or C4 dynamic view.
- **Where does it run?** C4 deployment diagram.
- **Lifecycles of key entities (orders, sessions, game rounds)?** State diagram.
- **Data ownership?** A table, not an ER diagram. An ER diagram only for the core aggregate.
- **Notation rules:** every diagram gets a title, a legend, labelled arrows with protocol and sync/async, and a technology on each container. Draw trust boundaries as dashed groups. One diagram, one question.

## 5. Technology Selection Without Training-Data Bias

**The problem (established for LLMs in general, opinion as applied here):** a model's prior favours what was most written about before its cutoff. That pushes it toward popular stacks, outdated versions and fashionable patterns.

Defences:
1. **Constraint-first filtering.** Start from what the team and organisation already run and know. Dan McKinley's "Choose Boring Technology" (2015) frames each new technology as spending one of a few "innovation tokens". The agent should list which tokens the design spends and why.
2. **Require a candidate set and criteria, not an answer.** For each significant choice, compare 2–3 options against the forcing scenarios plus: team familiarity, operational burden, maturity (release history, maintainers, licence), ecosystem fit, exit cost.
3. **Live currency checks.** Before committing, the agent must check official docs, release notes and end-of-life dates (e.g. endoflife.date), the package registry's release cadence, repository activity and licence changes, and the latest Thoughtworks Technology Radar ring. It should record the date checked in the ADR. If it cannot check, it must say "unverified as of <date>".
4. **Ask the repo.** In an existing codebase, scan manifests (package.json, go.mod, etc.) and infra config, and default to the incumbent unless a scenario forces a change.
5. **Name the popularity default explicitly.** Prompt the agent to write: "The popular default would be X. We choose / do not choose it because…" This makes the bias visible to the human reviewer.

## 6. Agents Designing Systems: Evidence, Failure Modes, Techniques

### Evidence (confidence-labelled)

- **Fairly confident:** Dhar, Vaidhyanathan & Varma, ICSA 2024 (arXiv 2403.01709). LLMs given ADR contexts produced relevant decisions but fell short of human quality. Few-shot prompting and fine-tuning helped smaller models.
- **Moderately confident (verify IDs before citing):** 2025 literature reviews of generative AI and LLMs in software architecture, e.g. Esposito et al., "Generative AI for Software Architecture: Applications, Trends, Challenges, and Future Directions" (arXiv, 2025). They describe research concentrated on decision support and early design, with little evaluation in industrial settings.
- **Practice signal (established by 2025):** spec-driven agent workflows that put an explicit requirements → design → tasks stage before code, e.g. AWS Kiro (public preview, July 2025) and GitHub Spec Kit (open-sourced, September 2025). These show the industry converging on a "design document as agent input" step. They are not evidence that the designs are good.
- **Not verified:** a standard, widely accepted benchmark for LLM *system design* quality. I found none I can cite. Do not assume one exists.

### Failure modes and defences

| Failure mode | Agent-specific? | Defence |
|---|---|---|
| Generic "reference architecture" not tied to the PRD | Strongly agent | Traceability rule: every element cites a scenario or constraint |
| Over-engineering to look senior (microservices, Kafka, Kubernetes, event sourcing) | Agent and human | Mandatory "simplest viable" option. Forcing scenario per pattern. Critic checks justification. |
| Popular or outdated tech defaults | Agent | Live currency checks and a dated "verified" field in ADRs |
| Making up organisational constraints, or assuming none | Agent | Explicit assumption list. Human checkpoint on constraints. |
| Missing non-functional requirements (failure, scale, security) | Both | Scenario template for each quality attribute. Failure-path runtime view required. |
| Undefined data ownership | Both | Data ownership table: one writer per entity |
| Confident prose hiding unknowns | Agent | Open-questions and spike sections required. Confidence label per decision. |
| Inconsistency between diagrams and text | Agent | Single model (Structurizr) or generated diagrams. Critic cross-checks. |
| Design rots once code starts | Both | Fitness functions and architecture tests in CI. ADR supersession workflow. |
| Sycophantic agreement with the user's preferred stack | Agent | Fresh-context adversarial review (the user's existing critic) |

### Techniques that work (practitioner consensus, limited formal evidence)

1. **Several options plus explicit trade-off tables** (ADD/ATAM lineage). Score options against the prioritised scenarios, and name the sensitivity and trade-off points.
2. **Adversarial, fresh-context review.** The designer and the critic must not share context. The user's June 2026 critic fills this role. Feed it the PRD and the design, not the designer's reasoning.
3. **Design → spike → revise.** Each high-risk ADR gets "status: proposed, pending spike S-n". The spike is a time-boxed throwaway that tests one assumption (e.g. "Postgres LISTEN/NOTIFY handles 2,000 events/s for live scoring"). Only then does the ADR become "accepted".
4. **Executable architecture.** Generate architecture-test rules from the module/context map (ArchUnit, dependency-cruiser, import-linter, Packwerk) and budgets (latency, bundle size), and run them in CI so agent-written code that crosses boundaries fails the build.
5. **Evolutionary architecture.** Treat the design as a set of hypotheses. When reality pushes back, write a superseding ADR rather than silently editing the design. Re-run the critic on the changed parts.

## 7. What Changed Since June 2026

**I could not verify any new papers, tools or practices from June to October 2026**, because this session had no web access. I will not list items I cannot check. To close the gap, check:
- ICSA 2026 and ECSA 2026 (September) proceedings and arXiv cs.SE for "LLM architecture design", "architecture conformance LLM" and "architecture erosion LLM".
- Changelogs for Claude Code (skills, subagents, hooks), GitHub Spec Kit, AWS Kiro, Structurizr and the C4/arc42 sites.
- The latest Thoughtworks Technology Radar volume, for its current positions on spec-driven development and AI-generated architecture artefacts.

**Back-test candidates:** any completed system-design task with a written outcome (integration with the existing platform, operating modes, architecture of a new service, analytics events, risks and a recommended production approach) makes a good back-test: run the new skill on its inputs and compare the output with what the humans produced. For example, a sub-task that calls for reviewing and documenting failure scenarios, reconnection handling, state synchronization and data-integrity protections is a good candidate. A shared skills repository should also use an agent-neutral skill format (a `SKILL.md` with version metadata, per-agent configuration files, and `references/` for overflow) validated by a script in CI, so the skill works across coding agents. The specific internal examples were removed.

## Recommendations: The Step-by-Step Method

| # | Step | Inputs | Outputs | Checkpoint |
|---|---|---|---|---|
| 0 | **Intake and readiness check** | PRD, repo/platform context | Gaps list (missing NFRs, users, volumes, compliance) | **Human answers the gaps**, or the agent proceeds with marked assumptions |
| 1 | **Drivers** | PRD + answers | Quality-attribute scenarios with response measures, constraints, assumptions, utility tree, size tier (S/M/L) | **Human confirms priorities and tier** |
| 2 | **Domain and boundaries** | PRD flows | Event list, bounded contexts, data-ownership table, glossary | Domain expert review (M/L) |
| 3 | **Options** | Drivers + contexts | 2–3 candidates, always including the simplest viable one, each with C4 L2 sketch | — |
| 4 | **Trade-off analysis** | Options + scenarios | Scoring table, sensitivity/trade-off points, risks, live-verified tech comparisons | — |
| 5 | **Decision** | Analysis | Recommendation | **Human chooses and accepts risks** |
| 6 | **Document** | Chosen option | `architecture.md`, C4 as code, ADRs, runtime and failure flows, deployment view, fitness functions | — |
| 7 | **Adversarial review** | PRD + design only | Critic findings | Agent revises; human sees unresolved items |
| 8 | **Spikes** | High-risk ADRs | Spike results; ADRs accepted or superseded | Human approves time-boxes |
| 9 | **Handoff** | Accepted design | Handoff package (below) | **Human sign-off** |
| 10 | **Conformance loop** | Code changes | CI architecture-test results, superseding ADRs | Human approves any boundary change |

### The handoff contract

**Expected upstream from the PRD:** problem and goals, users and personas, core user journeys, functional scope and non-goals, success metrics, expected volumes and growth, availability and latency expectations (even rough ones), data sensitivity and compliance, integrations with existing systems, constraints (deadline, budget, team, mandated platform), and open product questions. If volumes, sensitivity or availability are missing, the agent must ask before designing, not guess silently.

**Passed downstream:**
- **To feature specs:** bounded contexts and module list with responsibilities. The owning module for each PRD feature. Data-ownership table. Interface contracts between modules (API/event shapes at signature level). Cross-cutting rules (auth model, error handling, observability conventions). The quality-attribute scenarios each feature must respect.
- **To implementation plans:** build order and walking-skeleton definition (thinnest end-to-end slice through every container). Spike list and results. Environment and deployment topology. Accepted ADRs as hard constraints and proposed ADRs as open items.
- **To the build pipeline:** fitness functions and architecture-test configs (allowed dependencies between modules, forbidden imports, budgets). Environment definitions. Required observability signals. A rule that changes breaking a fitness function need a superseding ADR.
- **Format:** Markdown + Mermaid/Structurizr in the repo, with stable IDs (QA-n, C-n, ADR-n, S-n, M-n) so downstream specs and plans can cite them and the critic can trace them.

## Caveats

- No live web verification was possible in this session. Book and SEI references are well established. LLM-research references are labelled by confidence and should be checked before you cite them. Developments from June to October 2026 are unknown here.
- Figures from public case studies (e.g. Prime Video's ~90%) are the companies' own claims about narrow workloads, not general rules.
- Defaults in the decision table are opinions grounded in the cited literature. They are a starting point for the "simplest viable" option, not a mandate.
