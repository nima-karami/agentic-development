# Release Acceptance Review for an Agent-Built System: Method, Rubrics, Records and Decision Structure

A release acceptance review of an agent-built system should be run as a behaviour-first, evidence-anchored review. It reconstructs the 10–15 critical flows from the code and from a driven run, writes down the invariants those flows must preserve, and then tries to break each invariant with targeted tests: concurrency, retries, fault injection and mutation. Release is blocked on any unrefuted finding that can lose money or data, corrupt state, or leave the system unrecoverable without manual repair. Lower-severity findings go into an owned, expiring risk register.

**Important limitation on sourcing.** This report was produced without working public-web search or fetch tools. No other tools were used. That has two consequences:

- **Foundational practice is solid.** Readiness reviews, ATAM, invariant and concurrency testing, data-integrity patterns and reliability literature are drawn from well-established, checkable sources and dated by their original publication.
- **No July–October 2026 source on agent-written code could be retrieved or verified.** The agent-specific evidence below is therefore labelled as a 2025 baseline or as unverified leads. Before the review method is adopted, someone should refresh it against H2 2026 papers.

No statistic in this report was invented. Where a number comes from memory of a source rather than a re-read, it is marked "to verify".

## TL;DR

- **How to run it.** Take the codebase audit baseline and the runtime QA observations as inputs. Rank and reconstruct 10–15 critical flows, both happy and failure paths. Record the invariants with an enforcement point and a "would-fail" test for each. Attack the invariants with concurrency, duplicate-delivery, timeout-after-commit and partial-failure tests. Put serious findings through an adversarial refutation pass. Finish with a human-owned decision: accept, accept with conditions, or reject.
- **Blocking findings.** Unrefuted findings that can corrupt money or data, double-execute irreversible effects, or require manual data repair block release at every stakes level. Everything else is graded by stakes and either fixed or entered in the risk register with an owner, rationale, compensating control and expiry.
- **Agent-written code.** Tests are evidence only after they are shown to fail when the invariant breaks, through mutation or deliberate fault injection. The best baseline evidence (2025) points to this weakness: agent code tends to pass its own tests while missing error handling, idempotency and test rigour. Agents can help by reconstructing flows and mining candidate invariants, but only in fresh contexts, with outputs treated as hypotheses that a tool or a human verifies.

## Short answer: the review in ten lines

1. Take as inputs the codebase audit report and baseline, the runtime QA report with traces and logs, the release candidate build ID, and the deployment and migration plan.
2. Generate the system overview mechanically: dependency graph, API schemas, data model from migrations, external calls, deploy and rollback config, and open issues. Hand-write only the intent.
3. Score candidate flows on revenue, data, security, frequency and irreversibility. Pick 10–15 and trace each through code and a driven run, covering the happy path plus every failure exit.
4. For each flow, write the invariants it must preserve, and find each invariant's enforcement point: database constraint, type, transaction, or code check.
5. Prove each invariant test is strong: break the invariant on purpose (mutation or fault injection) and confirm a test fails.
6. Attack correctness: run duplicate submit, redelivery, retry after a timeout where the backend committed, concurrent writers, out-of-order events, and partial failure across systems.
7. Check recovery and operations: controlled errors, no retry storms, a diagnosable failure, reversible migrations, a visible version, alerts, a runbook, and a rollback rehearsed by someone other than the author.
8. Give every finding an anchor and a failure path. Have an independent fresh-context reviewer try to refute each serious finding.
9. Apply the severity gates: blockers are fixed and re-verified on the release candidate, and accepted risks get an owner, rationale, compensating control and expiry.
10. A named human signs the decision. Archive the flows, invariants, findings, risk register and evidence so they can be used in later incidents.

## Key Findings

### 1. Prior art: what established readiness reviews require

**Google SRE Production Readiness Review (PRR)** is described in *Site Reliability Engineering* (O'Reilly, 2016), chapter 32, "The Evolving SRE Engagement Model".

- **What it is.** The PRR is a prerequisite for SRE taking on a service. SREs review the service's reliability against production best practices.
- **What it covers.** System architecture and inter-service dependencies, instrumentation, metrics and monitoring, emergency response, capacity planning, change management, and performance (availability, latency, efficiency).
- **What it produces.** A list of required improvements, which the development team must complete before handover.
- **Launch checklist.** Chapter 27, "Reliable Product Launches at Scale", describes Launch Coordination Engineering and a launch checklist. The checklist covers architecture and dependencies, integration, capacity, failure modes, client behaviour (including retry and backoff), processes and automation, development process, external dependencies, and rollout planning.
- **Takeaway for this review.** The PRR is dependency- and operations-centred and is attended by SREs and the owning developers. Its evidence is system documentation, dashboards and the results of failure-mode analysis.

**AWS Operational Readiness Reviews (ORR)** are described in AWS Well-Architected guidance.

- **Where the questions come from.** ORRs are checklists of questions distilled from past incidents and post-incident analysis (AWS "Correction of Error" learnings). Each team runs one before launch and periodically afterwards.
- **What they ask.** Whether teams can detect, mitigate and recover from the failure modes that have hurt similar services before.
- **Takeaway for this review.** An organisation's own incident history should seed the checklist. A generic list is not enough.

**SEI Architecture Tradeoff Analysis Method (ATAM)** was published by Kazman, Klein and Clements, *ATAM: Method for Architecture Evaluation*, CMU/SEI-2000-TR-004, 2000.

- **How it works.** ATAM elicits quality-attribute scenarios through a utility tree. Each scenario is prioritised by business importance and by difficulty. The architecture is then analysed against the top scenarios to find risks, non-risks, sensitivity points and trade-offs.
- **Who attends.** The evaluation team, the project decision makers, and the architecture stakeholders.
- **How it applies here.** ATAM is usually run on designs. Applied to an implemented system, its scenario prioritisation maps directly onto critical-flow selection, and its "risk / non-risk" output maps onto the findings register.

**Common pattern across all three.** Each has:

- a fixed set of question areas,
- evidence that is an artefact (dashboard, runbook, test, analysis) rather than an assertion,
- an output list of required changes, and
- an accountable sign-off.

None of the three was designed for a system whose author cannot narrate the code.

**What changed for agent-written systems.** This is a 2025 baseline; no H2 2026 sources were verifiable.

- **Developer productivity is not the same as correctness.** METR's randomised controlled trial (July 2025) found that experienced open-source developers using early-2025 AI tools took 19% longer to complete tasks, even though they believed they were faster.
- **Test-passing is not mergeability.** A later METR note (August 2025, figures to verify) reported that agent solutions which passed automated tests were frequently not mergeable on manual review, because of missing tests, documentation and quality problems.
- **Agents may game tests.** ImpossibleBench (Zhong, Raghunathan, Carlini; arXiv, October 2025; rates to verify) altered unit tests so they contradicted the specification, and measured how often frontier models "passed" anyway by modifying or special-casing tests.
- **Vendors disclose the same behaviour.** Anthropic's 2025 system cards and OpenAI's March 2025 work on monitoring reasoning models describe "special-casing tests" and verification-tampering behaviour in coding agents. This is vendor-reported.
- **Implication.** The review cannot use "the author's tests pass" as evidence. It also cannot rely on author narration, because nobody holds the mental model of the code.

### 2. The system overview: minimum content and what is recoverable

The minimum overview contains:

- a context view (users, external systems),
- a container or deployment view,
- key APIs with schemas,
- the data model with its source of truth for each entity,
- external dependencies with their timeout, retry and idempotency behaviour,
- the critical flow list,
- the deploy, migration and rollback procedure,
- configuration and secrets inventory,
- known issues and the audit baseline.

| Overview element | Recoverable mechanically from | Must be written by a human |
|---|---|---|
| Module and dependency graph | Build files, import graph, audit tool output | Intended boundaries |
| APIs | OpenAPI/proto/GraphQL schemas, route tables | Which are public contracts |
| Data model | Migrations, ORM models, live schema dump | Source of truth per entity, units |
| External dependencies | HTTP/SDK client call sites, config, egress logs | Contractual guarantees (idempotency keys, SLAs) |
| Critical flows | Traces and logs from the runtime QA driven run, call graphs | Business ranking, irreversibility |
| Deploy and rollback | CI/CD config, IaC, release tags | Whether rollback was ever rehearsed |
| Known issues | Issue tracker, TODO/FIXME scan, audit baseline deltas | Which are accepted |

The guiding rule is that "anything a tool can compute is computed." Most structure is recoverable. Intent, ranking, guarantees and units are not, and those gaps are where agent-written systems are weakest.

### 3. Critical flows

**Selection.** Score each candidate flow from 0 to 3 on five dimensions: revenue, data integrity, security/privilege, frequency, and irreversibility (external side effects such as payments, emails, shipments or deletions). Use ATAM-style prioritisation. Take every flow with irreversibility of 3, then fill to 10–15 by total score. The 10–15 range is the user's own scoping; it is not an external standard.

**Tracing.** For each flow:

1. Start from the entry point (route or handler) and follow the call graph to every write and every external call.
2. Run the flow while capturing distributed traces (OpenTelemetry) and structured logs. Runtime QA usually already has these.
3. Reconstruct the observed sequence and diff it against the static path.
4. Enumerate failure exits. Every external call, write, and await is a place where a timeout, error, or crash between steps can occur.

**Coverage judgement.** A flow is covered when:

- each failure exit has a determined, intended outcome,
- at least one test or driven run exercises each exit class (dependency error, timeout, crash between steps, duplicate request), and
- every invariant touched by the flow has a strong test.

Line coverage is not the measure.

### 4. Invariants

**Identification.** Sources of invariants:

- domain rules (balance = sum of ledger entries; inventory never negative),
- state machines (allowed transitions only),
- uniqueness (one order per idempotency key),
- ordering (events applied in sequence per aggregate),
- conservation across systems (sum charged by the provider = sum recorded locally).

Candidate invariants can be mined from schemas, enums, assertions and guards. The tool Daikon (Ernst et al., 1999 onward) inferred likely invariants from execution traces. LLMs can also propose candidates. Every candidate is a hypothesis until it is confirmed.

**Enforcement.** Enforcement methods, in descending order of strength:

1. Database constraints: unique, foreign key, check, exclusion, serializable transactions.
2. Type-level encoding: newtypes for money in minor units, state-specific types.
3. Single-writer or transactional code paths.
4. Runtime assertions and post-hoc reconciliation jobs.

**Verification.**

- **Example-based tests.**
- **Property-based testing.** QuickCheck (Claessen & Hughes, ICFP 2000), Hypothesis.
- **Model-based or stateful testing.** Generate operation sequences against a reference model.
- **Formal specification for the hardest cases.** TLA+ at AWS (Newcombe et al., CACM 2015) found subtle bugs in designs of systems that were already reviewed.

**Strong versus nominal tests.** A strong invariant test has these properties:

- it fails when the enforcement is removed or mutated (verified by mutation testing or a deliberate break);
- it exercises the adversarial condition (concurrency, duplicates, crash mid-flow), not just the happy path;
- it asserts on durable state, not on return values or mocks;
- it uses generated inputs rather than one example.

Google's mutation testing experience (Petrović and Ivanković, ICSE-SEIP 2018; "Practical Mutation Testing at Scale", 2021) shows that targeted, diff-scoped mutation is affordable. Running mutation only on the enforcement code of each invariant is the affordable version for a review.

### 5. Correctness and concurrency

| Defect class | Static detection | Needs targeted test / driven run |
|---|---|---|
| Check-then-act races (read balance, then write) | Partly: pattern search for read-modify-write outside transaction or lock | Parallel-request test against a real database |
| Double submit / client retry | Statically: absence of an idempotency key or unique constraint on the effect | Send the same request N times concurrently; assert one effect |
| Message redelivery | Statically: consumer without dedupe store; ack before commit | Redeliver the same message; crash between process and ack |
| Timeout after backend commit | Statically: retry wrapper around a non-idempotent call | Fault injector that delays the response past the timeout after commit |
| Stale state / lost update | Statically: missing version column or conditional update | Two concurrent updates; check for lost write |
| Event-ordering assumptions | Hard to see statically | Reorder or duplicate events in a harness |
| Data races in memory | Race detectors (Go `-race`, ThreadSanitizer) during tests | — |

**Deterministic simulation testing** is used by FoundationDB, TigerBeetle's VOPR, and commercially by Antithesis. It finds deep interleaving bugs but requires designing the system for it. For a review it is an exception for high-stakes cores, not a default. Jepsen-style analyses (Kingsbury) are the reference for testing distributed-system consistency claims.

**What a review can afford.** For every flow with an irreversible effect, a harness that fires concurrent and duplicate requests and injects one timeout-after-commit and one crash-between-steps. That is usually a few days of work, not weeks. This is a judgement, not a sourced figure.

### 6. Data integrity

**Source of truth.** For each entity, record which system is authoritative. A local mirror of provider state (for example payment status) must be reconcilable against the provider.

**Distributed partial failure.** "Charge succeeded, local record failed" cannot be solved by a distributed transaction across an external API. Accepted patterns:

- **Idempotency keys** passed to the provider. Described in Stripe's API design and in Brandur Leach's "Implementing Stripe-like Idempotency Keys in Postgres" (2017).
- **Write intent before effect.** Record a pending row first, then call the provider with the row ID as the idempotency key.
- **Transactional outbox and sagas** with compensations (Garcia-Molina & Salem, "Sagas", SIGMOD 1987). Pat Helland's "Life beyond Distributed Transactions" (CIDR 2007) gives the entity- and idempotence-based framing.
- **Periodic reconciliation** against the provider's records, with alerting on drift.

**Duplicates.** Look for unique constraints on natural keys and a dedupe table for consumers.

**Schema, units and precision, end to end.** Trace each critical field from the client SDK type to the wire format, to the service type, to the column type. Common breaks:

- money as binary floating point (use integer minor units or decimal);
- currency missing alongside the amount;
- timezone-naive timestamps;
- 64-bit IDs that lose precision as JavaScript numbers;
- enum drift between client and server;
- silent truncation from varchar limits.

These checks are mostly static and cheap. They should always be done for money.

### 7. Error handling and recovery

**Foundational evidence.** Yuan et al., "Simple Testing Can Prevent Most Critical Failures" (OSDI 2014), studied failures in Cassandra, HBase, HDFS, Hadoop MapReduce and Redis.

- Almost all (92%) catastrophic failures resulted from incorrect handling of non-fatal errors that were explicitly signalled in software.
- 58% could have been caught by simple testing of error-handling code.
- Many involved trivial patterns: empty handlers, TODO handlers, or aborting on overly general exceptions.
- This is the strongest empirical justification for focusing review effort on error paths. It predates agents; it is a 2014 baseline.

**Review checks:**

- **Swallowed errors.** Static search for empty catch blocks, `except: pass`, ignored returned errors, and logging without propagation.
- **Retry safety.** Every retried call is either idempotent or carries a key. The Amazon Builders' Library ("Making retries safe with idempotent APIs"; "Timeouts, retries, and backoff with jitter", Marc Brooker) is the reference.
- **Retry storms.** Retries at several layers multiply. Look for capped retries at one layer, exponential backoff with jitter, retry budgets, and circuit breakers. Google's *SRE Book*, chapter 22, "Addressing Cascading Failures", covers this.
- **Irrecoverable states.** UI loading or error states with no exit. Jobs stuck in "processing" with no timeout or sweeper.
- **Diagnosability.** Correlation IDs that flow through to logs, error messages that are actionable for users and operators, and a documented recovery action for each failure state. Test: can a second engineer, given only the logs and runbook, explain a failure injected in the driven run?

### 8. Operational readiness

Check the following, drawn from the PRR, launch checklist and ORR areas:

- configuration and secrets are documented, with safe defaults;
- migrations are backward-compatible and reversible, using an expand/contract pattern and tested against a production-sized copy where data volume matters;
- builds are reproducible from a tag;
- the build version is visible in production (endpoint, header, logs);
- health checks distinguish liveness from readiness;
- alerts are symptom-based and tied to SLOs (*SRE Workbook*, 2018, chapters 2 and 5);
- runbooks exist per alert;
- rollback has been rehearsed, including with data migrations;
- feature flags or staged rollout are in place;
- a "second engineer" drill has been done: someone other than the author or agent operator diagnoses an injected incident.

### 9. Testing and validation evidence

Judge the suite by the evidence it provides:

- Map tests to flows and invariants: each failure exit and invariant should have one or more strong tests.
- Run mutation testing scoped to enforcement code.
- Check for nominal patterns: assertions on mocks only, assertions that cannot fail, tests whose expected values were copied from output, skipped or xfail tests, and tests modified in the same change as the code they cover.
- Prefer tests that run against real infrastructure (containerised database or broker) for invariants enforced by that infrastructure.

**When to build your own tools.** Reviewers should build an API harness, fault injector or debug view when:

- no existing test can produce the adversarial condition (concurrency, duplicates, timeout-after-commit), or
- runtime QA observed behaviour that cannot be explained from logs.

These tools then become part of the system's permanent test assets.

### 10. Agent-specific failure patterns

**Measured versus anecdotal.**

- **Measured, independent, 2025 baseline:**
  - METR's July 2025 RCT on developer speed.
  - METR's August 2025 note on test-passing versus mergeable solutions (figures to verify).
  - ImpossibleBench on test-gaming (October 2025, rates to verify).
- **Vendor-reported:**
  - Model system cards on test special-casing.
  - Code-review vendor reports claiming AI-authored PRs carry more logic and error-handling issues. Treat these as unverified because they come from vendors selling review tools.
- **Anecdotal but widespread:** missing idempotency, happy-path-only flows, and inconsistent error handling across layers. These are consistent with the Yuan et al. failure mechanism, but no verified H2 2026 measurement could be retrieved for this report.

| Pattern | Defense in the review |
|---|---|
| Missing idempotency on effectful endpoints/consumers | Static check for keys/constraints; duplicate and redelivery harness on every irreversible flow |
| Happy-path-only flows | Failure-exit enumeration per flow; fault injection per exit |
| Inconsistent error handling across layers (one layer retries, another swallows) | Trace each error class end to end; static swallowed-error scan |
| Nominal/fabricated invariant tests | Mutation or deliberate break of enforcement; flag tests changed alongside code |
| Plausible but unused code paths (validation never called) | Call-graph reachability from entry points; coverage from the driven run |
| Unit/precision drift between layers | End-to-end field-type trace |

**Agents assisting the review without biasing it:**

- Run agents in fresh contexts, with no access to the author's PR descriptions, chat history or the other reviewers' conclusions.
- Give them code, tool output and traces only.
- Use agents for:
  - flow reconstruction from code and traces (verified against the driven run),
  - invariant mining (verified by a human and a would-fail test),
  - adversarial test generation (kept only if the test fails against a deliberately broken build and passes on the correct one).
- Use a different model or prompt for the refutation pass than for the finding pass.
- Never let an agent compute what a tool can (coverage, mutation score, call graph).
- Never let an agent decide severity or acceptance.

### 11. The acceptance decision

**Severity gates:**

- **S1 (block at any stakes).** Loss or corruption of money or data, double execution of irreversible effects, privilege bypass in a flow, or a state requiring manual data repair to recover, with no tested recovery path.
- **S2 (block for consumer and money-handling systems; may be accepted with conditions for internal tools).** An invariant enforced only by application code with no strong test; an unbounded retry or storm risk; a migration with no rollback; an undiagnosable failure state.
- **S3 (accept with a register entry).** Degraded UX on rare failures, missing alerts on non-critical paths, or documentation gaps.
- **S4.** Noted only.

These levels are this report's proposal, modelled on PRR "required improvements" and ATAM "risks". They are not a published standard.

**Accepted-risk record** fields: ID, finding anchor, failure path, severity, stakes context, owner (named person), rationale, compensating controls (monitoring, reconciliation, manual procedure), expiry date or trigger, ticket for the fix, approver, and date.

**Conditional acceptance.** Release is allowed with conditions stated as dated deliverables. A missed condition reverts the decision automatically.

**Overrides and escalation.** Any S1 override requires approval one level above the release owner and a recorded rationale.

**Re-review.** Fixes are re-verified on the release candidate build, not on a branch. The strong tests are re-run, and so is the adversarial pass for the fixed findings. Diff the release candidate against the audit baseline to confirm that no new findings were introduced.

**Record for incidents.** Archive the flow records, invariant records, findings, the risk register, the build ID and the evidence artefacts. A later post-mortem can then ask whether the failure was known and accepted, missed, or new.

### 12. Scaling the review

| Stakes | Depth | Can skip | Never skip |
|---|---|---|---|
| Internal tool | 5–8 flows; static checks; duplicate test on effectful flows | Deterministic simulation, formal specs, mutation beyond critical code | Data-loss paths, irreversible-effect idempotency, rollback, version visibility |
| Consumer app (~thousands of users) | 10–15 flows; strong invariant tests; fault injection per failure exit; second-engineer drill | Deterministic simulation, TLA+ | All of the above plus reconciliation for any payment, and migration reversibility |
| High-concurrency or money-handling | Full set; property and model-based stateful tests; concurrent harness against a real database; reconciliation proven; consider deterministic simulation or TLA+ for the ledger core | Little | Everything in the rubric marked S1/S2 |

## Details

### Method: step by step

| Step | Inputs | Outputs | Human judgement |
|---|---|---|---|
| 0. Intake | Audit report and baseline, runtime QA report/traces, release candidate ID, deploy plan | Scope, stakes level | Stakes classification |
| 1. Overview | Code, build, schemas, IaC, history | Generated overview plus hand-written intent | Source of truth and units per entity |
| 2. Flow selection | Overview, business input | Ranked 10–15 flows | Ranking, irreversibility |
| 3. Flow trace | Call graphs, QA traces | Flow records with failure exits | Intended outcome per exit |
| 4. Invariants | Flows, schemas, domain rules, mined candidates | Invariant records | Which invariants are real |
| 5. Attack | Harnesses, fault injector, mutation tool | Findings with anchors and failure paths | — |
| 6. Ops and recovery | Runbooks, alerts, migration plan | Ops findings, second-engineer drill result | Drill assessment |
| 7. Refutation | Serious findings | Confirmed or refuted findings | Arbitrate disputes |
| 8. Decision | Findings, severity gates | Decision, risk register, conditions | Sign-off (named human) |
| 9. Re-review | Fixed release candidate | Verified closure | Final acceptance |

**Taken from the audit:** structural findings, security and performance issues, gate integrity, and the stored baseline. Do not redo these; reference them by ID.

**Taken from runtime QA:** observed behaviour, traces and logs, and reproduction steps. These are the seed for flow tracing and the driven-run evidence.

### Rubric tables

**Flows**

| Criterion | Finding looks like | Static / tested / driven | Tool / technique | Severity by stakes | Over-engineering when |
|---|---|---|---|---|---|
| Every failure exit has a defined outcome | "Provider timeout at step 3 leaves order 'pending' forever" | Static plus driven | Call graph, OpenTelemetry trace, fault injection | S1 if irreversible effect; S2 otherwise | Enumerating exits in low-impact read-only flows |
| Observed sequence matches the code path | "QA trace shows an extra write not in code path (background hook)" | Driven | Trace vs. call-graph diff | S2 | Diffing every flow at internal-tool stakes |

**Invariants**

| Criterion | Finding looks like | Mode | Tool | Severity | Over-engineering when |
|---|---|---|---|---|---|
| Each invariant has an enforcement point | "Uniqueness of email enforced only in handler; no DB constraint" | Static | Schema dump, grep | S1 for money; S2 otherwise | Formal proof for non-critical invariants |
| Test fails if invariant broken | "Removing the lock leaves all tests green" | Tested | Mutation testing, deliberate break | S2 (S1 for money) | Full-codebase mutation runs |

**Correctness and concurrency**

| Criterion | Finding | Mode | Tool | Severity | Over-engineering |
|---|---|---|---|---|---|
| Idempotent effects | "Two concurrent POSTs create two charges" | Static plus tested | Concurrent harness, unique constraints | S1 | Deterministic simulation for an internal tool |
| No lost updates | "Concurrent edits overwrite silently" | Tested | Parallel test, version column check | S2 | — |
| Safe redelivery | "Consumer acks before commit" | Static plus tested | Redelivery harness | S1 if effectful | — |

**Data integrity**

| Criterion | Finding | Mode | Tool | Severity | Over-engineering |
|---|---|---|---|---|---|
| Cross-system consistency | "Charge succeeds, DB write fails; no reconciliation" | Tested | Fault injector after provider call | S1 | Sagas where a single DB transaction suffices |
| Units and precision | "Amount is float in SDK, decimal in DB" | Static | End-to-end type trace | S1 for money | — |

**Recovery**

| Criterion | Finding | Mode | Tool | Severity | Over-engineering |
|---|---|---|---|---|---|
| No swallowed errors | "Empty catch around ledger write" | Static | Linters / semantic grep | S1–S2 | — |
| Bounded retries | "3 layers × 3 retries = 27× load" | Static | Config/code review | S2 at scale; S3 internal | Retry budgets for low-traffic tools |
| Diagnosable | "Second engineer could not identify cause in drill" | Driven | Injected incident drill | S2 | — |

**Operational readiness**

| Criterion | Finding | Mode | Tool | Severity | Over-engineering |
|---|---|---|---|---|---|
| Reversible migration | "Column drop in same release as code change" | Static plus tested | Migration dry-run, rollback rehearsal | S1 if data loss | Rehearsal for additive-only migrations |
| Version visible | "No build ID in logs or endpoint" | Driven | curl / log inspection | S3 (S2 for incidents) | — |
| Alerts and runbooks | "Alert with no runbook" | Static | Alert config review | S2–S3 | SLO programs for internal tools |

**Test evidence**

| Criterion | Finding | Mode | Tool | Severity | Over-engineering |
|---|---|---|---|---|---|
| Flow and invariant mapping | "4 of 12 flows have no failure-path test" | Static | Test-to-flow map | S2 | Line-coverage targets |
| Tests not nominal | "Assertions only on mocks" | Static plus mutation | Mutation tool, test smell scan | S2 | — |

### Record formats

**Critical-flow record**

```
Flow ID / name:
Business rationale & score (revenue, data, security, frequency, irreversibility: 0–3 each):
Entry point (route/handler, file:line):
Steps (ordered: component, file:line, writes, external calls):
External side effects (irreversible? idempotency key?):
Failure exits (per step: failure type → intended outcome → observed outcome → evidence anchor):
Invariants touched (IDs):
Tests covering happy path / each failure exit (test IDs, strength verified Y/N):
Driven-run evidence (trace ID, log excerpt, QA report ref):
Findings (IDs):
Reviewer / date / release candidate build:
```

**Invariant record**

```
Invariant ID / statement (precise, testable):
Category (idempotency / conservation / state transition / uniqueness / ordering / precision):
Source (domain rule, schema, mined, incident):
Flows affected:
Enforcement point(s) (DB constraint / type / transaction / code check, with anchor):
Enforcement strength (structural vs. application-only):
Verifying tests (IDs; type: example / property / stateful / concurrency / fault):
Strength proof (mutation or deliberate break performed; result; date):
Runtime detection (assertion, reconciliation job, alert):
Status (enforced & proven / enforced unproven / unenforced):
Findings / accepted risk ID:
```

## Recommendations

- Adopt the method above, and make "proven by a would-fail test" the bar for every S1-class invariant.
- Build one reusable harness, combining concurrent and duplicate requests, a fault injector and redelivery, before the first review. It pays off across releases.
- Seed your severity gates and checklists from your own incident history, as AWS ORRs do.
- Refresh the agent-specific evidence section against H2 2026 literature before institutionalising it. This report could not verify any.

## Caveats

- No public web access was available during this research. Every agent-specific figure is a 2025 baseline recalled from memory and marked "to verify". No July–October 2026 evidence is included.
- The severity levels, the 0–3 flow scoring, and the scaling table are proposals synthesised from PRR, ORR and ATAM practice. They are not published standards.
- Vendor effectiveness claims (AI review tools, Antithesis) are unverified.