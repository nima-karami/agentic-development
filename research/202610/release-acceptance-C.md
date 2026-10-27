# Release Acceptance Review for a Built, Mostly Agent-Written System

## Ten-line answer

Freeze an immutable release candidate and review **that artefact**, not a moving branch; attach build provenance, version identity, prior audit baseline, and runtime-QA evidence. citeturn17view10turn21view8  
Reconstruct a minimal as-built system map from code, schemas, manifests, build/deploy configuration, history, and traces; ask humans only for intent, business criticality, source-of-truth decisions, and known unknowns. citeturn21view0turn22view4turn21view3  
Deterministically rank candidate end-to-end flows by business effect, data/security impact, frequency, concurrency/retry exposure, external side effects, and irreversibility; the **10–15-flow budget comes from this research brief, not an industry standard**. citeturn17view4turn22view0  
For each selected flow, trace the real implementation from trigger to terminal state and prove both its normal path and the failures around every consequential side-effect boundary. citeturn21view3turn21view5turn17view9  
Extract candidate invariants from contracts, constraints, state machines, tests, business rules, and historical failures; require a domain owner to confirm which ones really must always hold. citeturn17view7turn20search3  
Demand executable evidence for invariants: constraints/assertions plus tests that exercise hostile inputs, operation sequences, duplicates, reordering or concurrency where relevant—and verify that deliberately breaking the invariant makes the test fail. citeturn20search0turn17view8  
Target the ambiguity agents and ordinary tests often miss: timeout-after-commit, duplicate submission/delivery, stale reads, partial distributed writes, ordering assumptions, retry amplification, restart, and rollback. citeturn21view5turn21view6turn18view11  
Judge the test suite by **which critical behaviours it can falsify**, not line coverage; reviewers should build small independent harnesses or fault injectors when existing tests cannot establish the required fact. citeturn20search0turn17view0  
Send every serious finding—with its code/test/trace anchor and concrete failure path—to a fresh reviewer whose job is to refute it; 2026 evidence makes independent verification especially important for long agent trajectories and agent-authored verification. citeturn17view0turn19view0  
A human with release authority decides **accept, conditional accept, or do not release**, against explicit blockers and a residual-risk register; every accepted risk has an accountable owner, rationale, controls, evidence, and revisit/expiry condition. citeturn18view9turn21view10

## Prior art and what changed in 2026

**Established practice.** The useful predecessors are not conventional code reviews. Google’s launch process treats readiness as a cross-functional reliability gate: reviewers look at architecture and dependencies, request and failure flows, retries/timeouts, monitoring, rollout and rollback, operational procedures, and whether launch mechanisms are repeatable. Google describes launch coordination as deliberately objective and scalable: the launch reviewer can act as a gatekeeper rather than merely advise the product team. citeturn17view4turn4view4 Google’s production-readiness practice similarly starts by learning what the service does, how it operates day to day, how it breaks and alerts, configuration divergence, monitoring weaknesses, and major operational risks rather than reviewing every implementation line. citeturn4view6

AWS’s Operational Readiness Review is closely aligned with the desired acceptance-review shape. ORR questions are informed by real incidents, near misses, and feared failure modes; the review records residual risk and action items, and specialist “Ops Champions” challenge teams’ answers, verify that claimed results are measurable, help determine risk severity, and participate in the review and retrospective. citeturn17view6turn22view1 AWS’s current Well-Architected guidance also frames operational readiness as a cross-functional activity involving development, operations and relevant specialists rather than a document-completion exercise. citeturn17view5

ATAM contributes a different and still valuable idea: **scenario-driven risk discovery rather than checklist compliance**. SEI describes ATAM as evaluating an architecture against quality goals, eliciting business drivers, turning them into scenarios, prioritising those scenarios with stakeholders, analysing architectural responses and surfacing risks, sensitivity points and trade-offs. A classical ATAM normally brings together a trained evaluation team, architects and stakeholder representatives and historically takes three to four days; that duration is ATAM’s published practice, not a recommended duration for this release review. citeturn22view0 For a system that is already built, the useful adaptation is to make the “scenario” executable: map it to code, a trace, an invariant, and an observable terminal result.

Taken together, mature practice says that acceptance evidence is broader than tests passing. Useful evidence includes an as-built architecture and dependency map, measurable behavioural observations, test/fault-injection results, monitoring and operational artefacts, deployment/rollback evidence, incident-derived questions, and explicit residual risks and actions. A review should involve the release decision-maker, independent reviewers, the service/runtime owner, operations or on-call representation, and whichever data/domain/security specialists own the consequences of the selected flows. The authoring engineer is useful for questions, but under the principles in this brief should not supply the conclusions that fresh reviewers are meant to reach independently. citeturn22view0turn22view1turn4view4

**Emerging in H2 2026.** What has changed is not that established reliability principles stopped applying; it is that **implementation authorship is becoming weaker evidence of system understanding**. Three recent results are particularly relevant.

First, DeepSWE, released in July 2026, showed why inherited or author-created tests cannot automatically be treated as faithful behavioural specifications. Its authors built 113 original long-horizon tasks with purpose-written functional verifiers. In an audit using an independent judge, the judge disagreed with SWE-Bench Pro’s inherited-test verdict on 32.4% of 789 audited rollouts, versus 1.4% of 735 DeepSWE rollouts; the authors explicitly caution that this is **judge/verifier disagreement, not a ground-truth verifier error rate**. The important release-review lesson is narrower: tests originally written to validate one implementation may not establish that an arbitrary implementation fully satisfies the intended behaviour. citeturn17view0

Second, ChainSWE, July 2026, tested agents on 304 dependent bug-fix instances in 100 chains across 54 Python repositories. Agent performance deteriorated as agent-produced state accumulated, with relative declines reaching roughly 70% at deep chain positions in several evaluated configurations. This is a benchmark result, not a measured production-defect rate, but it supplies concrete evidence that evaluating isolated changes can miss failures created by the accumulated codebase state that later work inherits. citeturn18view0turn18view1

Third, a September 2026 study of long-horizon agents analysed 2,518 trajectories and 6,967 labelled mistakes across software engineering, computer use and science. After the first mistake, agents recovered in only 30.5% of affected runs and never detected the error themselves in 38.5%; one wrong step made the immediately following step about 11–14 times likelier to be wrong. The study also found examples of runs judged successful that nevertheless took destructive or fabricated actions along the way. Its software-engineering subset is only part of the corpus, so those numbers must **not** be reported as production coding-agent defect rates; they instead support process-level, independent verification rather than trusting a successful-looking final outcome or the producing agent’s self-assessment. citeturn19view0

**Recommended synthesis.** For an agent-built release candidate, therefore, move confidence away from “the author understood and reviewed every line” and toward four externally checkable things: **observable flow behaviour, invariants with executable falsifiers, controlled failure/recovery, and operationally identifiable artefacts**. This is an adaptation of established readiness practice to the 2026 evidence, not a newly established industry standard. citeturn17view4turn22view1turn17view0turn19view0

## Review method and system overview

The review should consume the two preceding reviews rather than repeat them.

The **codebase audit** supplies the immutable audit baseline, architectural-conformance findings, gate/contract findings, deterministic structural measurements, security/performance findings already in scope there, and any unresolved risks. The acceptance review reopens one of those topics only when it is needed to establish a behavioural failure path—for example, a contract-design finding that turns out to permit a duplicate charge.

The **runtime-QA review** supplies the release/environment identity, scenarios driven, observed outcomes, screenshots or logs where applicable, trace/session/request IDs, observed failure states, and reproduction notes. It is observation evidence, not automatically an explanation of why the behaviour occurred.

The acceptance review then produces an as-built overview, selected-flow register, invariant register, independent validation artefacts, finding dossiers, adversarial-refutation outcomes, accepted-risk register, and final human decision.

**Step-by-step method**

| Stage | Inputs | Work | Output | Human judgement |
|---|---|---|---|---|
| **Freeze the candidate** | Commit, artefact/image, build pipeline, config and migration set | Produce or verify immutable artefact identity; record source revision, dependency/build inputs and evidence-run environment. SLSA provenance is an established format for recording where, when and how an artefact was produced. citeturn18view12 | RC identity manifest | Decide whether the evidence really applies to the thing intended for release. |
| **Ingest prior evidence** | Codebase-audit baseline; runtime-QA report | Deduplicate known findings; convert runtime observations into candidate flows/failure hypotheses; carry unresolved audit risks forward by ID. | Review input ledger | Decide which prior findings affect release behaviour and which are genuinely out of scope here. |
| **Reconstruct the system** | Source/index, API/event schemas, DB schemas/migrations, IaC, CI/CD, lockfiles, history, runtime traces | Deterministically extract routes, services, stores, dependencies, deployment units and call/data edges; compare them with documented intent. SEI has long treated architecture reconstruction as tool-assisted recovery of the as-built system. citeturn21view0 | Minimal system map with anchors | Resolve source-of-truth ownership, intended boundaries and business meaning that code alone cannot establish. |
| **Rank critical flows** | Route/event inventory, telemetry, money/data/security metadata, dependency map, QA scenarios | A script computes available objective factors—volume, observed fan-out, side-effect endpoints, retries, transaction boundaries, privilege boundary crossings. Humans supply non-computable business labels such as irreversibility or legal/customer consequence. | Ranked candidate-flow list | Select the review-budget subset and document overrides. |
| **Trace and challenge flows** | Selected flows, xrefs/call graph, traces/logs | Reconstruct happy path; enumerate meaningful failure paths at each side-effect/state-transition boundary; drive missing cases. OpenTelemetry traces are explicitly designed to represent end-to-end request paths as related spans across process/service boundaries. citeturn21view3 | Critical-flow records plus traces/tests | Decide whether the evidence proves each hop and terminal outcome or merely makes it plausible. |
| **Mine and verify invariants** | Contracts, constraints, state machines, API/schema definitions, tests, business documentation, incidents | Extract candidate properties; map every confirmed property to its enforcement and its falsifying tests; add property/state-machine/concurrency tests where needed. | Invariant records | Domain/data owner confirms that each candidate is genuinely an invariant and whether its enforcement is sufficient. |
| **Attack ambiguity and recovery** | Flow/invariant records | Duplicate, retry, reorder, delay, fail dependencies, simulate ambiguous completion, crash/restart selected components, and exercise migration/rollback boundaries as stakes warrant. | Targeted validation results | Decide whether unresolved ambiguity is tolerable at the system’s stakes. |
| **Challenge operations** | Config docs, dashboards, alerts, runbooks, deploy/rollback artefacts | Have someone other than the primary implementer identify the running version, diagnose a seeded failure and execute or explain the safe recovery path. | Operational-readiness evidence | On-call/operational owner judges whether they can actually support it. |
| **Adversarial pass and disposition** | Serious findings with anchors and failure paths | Give each to a fresh reviewer asked to disprove it using executable or observable evidence; rerun any disputed test. | Confirmed, weakened or refuted findings | Human severity/risk owner resolves surviving uncertainty. |
| **Rebuild, re-review and decide** | Fixes and surviving risk | Build a new immutable RC, rerun reproducer plus affected flow/invariant evidence, compare against baseline, then decide. | Signed decision package | Release authority owns acceptance. |

The order above is a **recommended synthesis**, not a published Google/AWS/SEI procedure; it combines their established launch/readiness/scenario ideas with the fixed principles in the research brief. citeturn17view4turn17view5turn22view0

**The minimum overview should be small enough to regenerate.** A prose architecture document is less valuable here than a linked evidence map.

| Overview element | Recover automatically or semi-automatically | What still needs human confirmation |
|---|---|---|
| **System context and deployable units** | Repository/module graph, build targets, containers/serverless units, IaC, service-discovery/config references and runtime topology. C4’s context/container views are a useful vocabulary; dynamic and deployment views can supplement them. citeturn21view2 | What the system is *for*, trust boundaries not expressed in config, and intended ownership. |
| **Key APIs, events and data models** | OpenAPI/protobuf/GraphQL definitions, route registrations, SDK generation, ORM/entity metadata, DB schema and migrations, queue/topic bindings. | Semantics, units, compatibility promises, business interpretation and which fields are authoritative. |
| **External dependencies** | Package/service configuration, IaC, client constructors, DNS/service names and observed outbound trace spans. | Business criticality, contractual behaviour, degraded-mode expectations and what happens when a dependency lies rather than merely fails. |
| **Critical-flow candidates** | Entry points, call/data graph and actual QA traces/log correlations. | Revenue/customer/data/irreversibility meaning and unexpected “hidden” manual workflows. |
| **Deployment, migration and rollback** | CI/CD definitions, deployment manifests, migration scripts, feature flags and rollback jobs. | Whether rollback is still *semantically* safe after new writes occur; database migration guidance explicitly distinguishes fallback from simply redeploying old code. citeturn16search1turn16search6 |
| **Release identity** | Commit, digest/package version, build provenance and service telemetry attributes. OpenTelemetry’s current service conventions recommend a `service.version` identifier; SLSA provenance records build inputs and producer. citeturn18view13turn18view12 | Which artefact is actually approved. |
| **Known issues** | Prior audit/QA results, issue tracker/release history, failed test evidence. | Which are understood, which are release-relevant and which residual risks somebody will actually accept. |
| **Intent and architectural history** | Commit/work-item history can help recover intended structure. An August 2026 industry case study found useful architectural signal in historical work items but explicitly notes that such artefacts capture only documented intent and can diverge from implemented reality. citeturn22view4 | Resolve implementation-versus-intent conflicts. Neither generated view should silently overwrite the other. |

That yields an important division of labour: **source/build/configuration reveal what exists; traces reveal what executed; history reveals some intent; humans establish what matters and what must never happen.** Architecture recovery research has made the same distinction for decades, and the 2026 work-item study reinforces that neither code nor documentation alone is complete. citeturn21view0turn22view4

For critical-flow selection, the **10–15** count is the review budget specified by this prompt; Google launch reviews, AWS ORRs and ATAM do not establish a universal 10–15-flow threshold. citeturn17view4turn17view5turn22view0 A deterministic ranking tool should collect what is measurable rather than having an LLM “score risk”: observed frequency and fan-out, whether money/inventory/unique data change, privilege boundary crossings, number of durable writes, external irreversible calls, retry/message-redelivery exposure, concurrency, and whether an operation has a compensating path. Humans annotate business impact and irreversibility where those cannot be computed.

Do not simply select the highest-traffic endpoints. The final set should deliberately cover the highest-consequence flows, the highest-frequency flows, flows crossing trust or ownership boundaries, irreversible/external-effect flows, duplicate/retry-sensitive asynchronous flows, a deployment/migration path where relevant, and at least one meaningful recovery/operator path. That selection principle is a synthesis of launch-risk, scenario and incident-derived readiness practice. citeturn17view4turn22view0turn22view1

A flow is not “covered” merely because a test invokes its endpoint. For this review, call it **behaviourally covered** only when evidence connects the initiating stimulus through every consequential state transition and side-effect boundary to a specified terminal outcome, and credible failures at those boundaries have either an observed/tested response or an explicitly accepted risk. Static call graphs answer “what can call what”; traces answer “what this run actually did”; neither alone establishes complete behavioural coverage. citeturn21view0turn21view3

## Behavioural verification rubric

The following severity and “over-engineering” guidance is a **recommended release-acceptance rubric**, not an external standard. Here, **Block** means the review should not accept the RC without correction or a genuinely stronger compensating control; **High** normally requires correction before release; **Medium** may enter the accepted-risk process; **Low** is ordinarily backlog material. Stakes can raise, but should rarely lower, a technically demonstrated finding.

**Critical flows**

| Criterion | What a finding looks like | Static, tested, or driven run? | Evidence-producing technique | Severity guidance by stakes | Where it becomes over-engineering |
|---|---|---|---|---|---|
| End-to-end implementation path is anchored | Flow document says “service validates then saves,” but the review cannot identify the handler, validation, durable write, external call or terminal response. | Static **plus** driven trace | Language/compiler xrefs or call/data graph; API/schema extraction; OpenTelemetry trace and correlated logs. citeturn21view3turn21view0 | High-stakes consequential hop unknown: **Block**. Reversible internal path: Medium. | Building a perfect whole-repository call graph when targeted xrefs and a real trace already establish the chosen flow. |
| Consequential boundary has failure behaviour | Payment/message/write succeeds but response is lost; flow definition contains only the happy path. | Targeted test/driven run | Failure stub/proxy, timeout-after-commit harness, DB/state diff, trace. Retry safety is specifically an idempotency problem when completion is ambiguous. citeturn21view5 | Money/unique data/irreversible effect: **Block** until outcome is safe or recoverable. | Exhaustively failing every dependency call when many calls are read-only and have identical failure semantics. |
| Terminal states are complete | User can remain “loading”; durable record remains `processing` indefinitely; operator cannot tell successful from unknown. | Driven run | Client/API harness plus dependency interruption, refresh/restart, durable-state query and telemetry check. | Persistent ambiguous state touching money/data: Block/High; cosmetic reversible state: Medium/Low. | UI fault matrices for low-value screens that use the same proven state component. |
| Flow evidence covers code actually shipped | Test drives fake in-memory adapters while release path uses different storage/message implementations. | Static + integration/driven | Map test wiring to production dependency graph; run selected flow against production-equivalent boundaries. | High when the substituted boundary carries the central correctness property. | Requiring full production infrastructure for pure deterministic modules. |

**Invariants**

| Criterion | What a finding looks like | Static, tested, or driven run? | Evidence-producing technique | Severity guidance by stakes | Where it becomes over-engineering |
|---|---|---|---|---|---|
| Invariant is precise and falsifiable | “Orders should be consistent” rather than “an order may transition only `pending → paid|cancelled`; never both.” | Human specification + static mining | Contract/state-machine extraction, domain-owner confirmation. Property-based testing traces to QuickCheck’s model of specifying laws/properties over generated inputs. citeturn20search3 | Missing definition for money/inventory/authorization invariant: **Block**, because no test can prove an unspecified property. | Formalising every UI preference or transient cache detail as an invariant. |
| Enforcement sits at the strongest practical boundary | Uniqueness checked only with `SELECT` before `INSERT`; no DB uniqueness constraint despite concurrent writers. | Static + concurrency test | Schema inspection; duplicate/concurrent test. PostgreSQL, for example, natively enforces `NOT NULL`, `UNIQUE`, primary/foreign-key and related constraints. citeturn17view7 | Persistent uniqueness/conservation failure: Block/High. | Duplicating a constraint at every layer when a lower authoritative boundary already makes the invalid state impossible and upper validation adds no user value. |
| Test would actually detect violation | Test asserts “result exists” but not conserved total, transition legality or duplicate count. | Tested | Deliberately mutate/remove enforcement; mutation testing runs tests against seeded code changes and exposes surviving changes that assertions fail to detect. citeturn20search0 | Nominal test for core invariant: High; Block where it is the only evidence for a critical invariant. | Whole-codebase mutation testing when targeted mutations around critical properties answer the acceptance question. |
| Sequence/concurrency variants are exercised where relevant | Property holds for one operation but fails under retry, reorder or concurrent operations. | Targeted/systematic test | Stateful property/model test; concurrency scheduler or controlled barriers. Coyote systematically explores scheduling and nondeterministic choices such as timeouts/failures. citeturn18view10 | High-stakes shared mutable state: Block/High. | Systematic scheduler modelling of stateless request handlers with no shared or external state. |

A **strong invariant test** therefore has an independent oracle for the semantic property, exercises states capable of falsifying it, crosses the real enforcement boundary, and—where the property is concurrency-sensitive—generates relevant operation sequences/interleavings. A practical additional quality test is to disable or mutate the key guard and confirm that the invariant test fails. Mutation testing is particularly useful here because ordinary code coverage records execution, not whether assertions can detect a changed result. citeturn20search0turn20search2

**Correctness and concurrency**

| Criterion | What a finding looks like | Static, tested, or driven run? | Evidence-producing technique | Severity guidance by stakes | Where it becomes over-engineering |
|---|---|---|---|---|---|
| Duplicate execution is safe | Double-click, HTTP retry or redelivered message creates two charges/orders/jobs. | Static clue; **must test** consequential cases | Search for idempotency/request IDs and uniqueness; send identical operations concurrently and sequentially; replay delivery. AWS’s idempotent-API guidance explicitly treats safe retry after uncertain completion as a design requirement. citeturn21view5 | Duplicate irreversible effect: **Block**. Duplicate benign metric/cache write: lower. | Idempotency infrastructure for operations that are intrinsically pure/read-only. |
| Read-modify-write is concurrency safe | Two requests both read quantity/balance N and independently commit conflicting N−x results. | Static clue + concurrency test | Transaction/locking/atomic-operation inspection; controlled two-worker barrier; systematic scheduler for core algorithms. citeturn18view10 | Inventory/money/uniqueness: Block/High. | Model-checking every framework-managed collection when no business invariant depends on it. |
| Stale state is recognised | Authorization/state decision occurs on stale version and overwrites a newer transition. | Static + targeted test | Version/ETag/CAS/row-version inspection; inject stale reader/writer or delayed event. | Privilege, money, state-machine violation: Block/High. | Strong consistency everywhere merely to simplify reasoning where stale reads have no harmful consequence. |
| Event ordering is explicit | Consumer implicitly assumes FIFO globally although transport guarantees differ; old event overwrites newer state. | Static + reorder test | Event-schema sequence/version fields; harness delivers reordered and duplicated messages. Transactional-outbox guidance explicitly warns that duplicate delivery and ordering affect consistency. citeturn18view11 | Data corruption/state regression: High/Block. | Global ordering when ordering only matters per entity—test and enforce the smallest required scope. |
| Nondeterministic failure can be reproduced | “It failed once under concurrency” with no controllable reproduction. | Tested | Deterministic/systematic concurrency test around the narrow critical component. citeturn18view10 | Severity follows consequence; reproducibility absence raises uncertainty. | Rebuilding the entire distributed deployment inside a deterministic simulator for a modest, reversible application. |

Static review is good at identifying **suspicious structures**, not proving race freedom: non-atomic read/modify/write sequences, mutable shared state, check-then-act uniqueness, missing idempotency identifiers, retries around side effects, ordering assumptions, broad transaction boundaries, and operations performed outside a transaction. Actual harmful interleavings, ambiguous completions and transport behaviour need targeted execution. Systematic concurrency testing is especially attractive for a few high-stakes state machines because tools can control schedules rather than waiting for stress testing to stumble over the race. citeturn18view10

For a release review, the affordable baseline is usually deterministic duplicate/retry tests and a handful of deliberately orchestrated interleavings around the most important shared-state operations. Full deterministic simulation of a distributed system is justified only when concurrency itself is central to the product’s risk; it is not a prerequisite for an ordinary internal tool.

**Data integrity**

| Criterion | What a finding looks like | Static, tested, or driven run? | Evidence-producing technique | Severity guidance by stakes | Where it becomes over-engineering |
|---|---|---|---|---|---|
| Every business fact has a declared source of truth | Same “payment status” independently mutable in provider, DB and cache with no reconciliation rule. | Static reconstruction + human decision | Data-ownership map from schemas/writes; domain-owner adjudication; compare traces. Google SRE frames data integrity around users being able to rely on what was written/read, including consistency and durability. citeturn21view4 | Money/unique records: Block/High. | Declaring an authoritative source for purely derived, disposable data when regeneration is trivial. |
| Cross-system partial success is resolved | Charge succeeds; local transaction rolls back; subsequent retry may charge again. | Static **plus** failure test | Timeout/failpoint between external and local operations; provider query/reconciliation; idempotency-key replay. citeturn21view5 | **Block** for money or irreversible external side effects. | Distributed-transaction machinery where an idempotent operation plus explicit reconciliation safely meets the requirement. |
| DB + event dual write cannot silently diverge | DB commit succeeds but message publish fails, or rollback still emits event. | Static + targeted integration test | Transactional outbox/CDC or equivalent; kill publisher at boundaries and inspect both states. The outbox pattern exists specifically to avoid dual-write inconsistency and requires duplicate-safe consumers. citeturn17view9turn18view11 | Persistent downstream divergence: High/Block. | Outbox for notifications whose loss is knowingly non-critical and independently regenerable. |
| Reconciliation exists for systems that cannot be atomic | No way to detect orphaned external effects or missed local updates. | Tested/driven | Independent reconciliation query/report; deliberately create mismatch and demonstrate detection plus repair. | Money/inventory/unique data: High/Block. | Continuous reconciliation for low-value ephemeral data when retry/rebuild is deterministic. |
| Units, schema and precision survive end to end | Client sends dollars, backend interprets cents; float represents amounts requiring exact decimal semantics; SDK enum differs from storage. | Static + contract/property tests | Trace value through SDK/API/service/storage; boundary values; schema diff; round-trip/property tests. PostgreSQL’s current docs distinguish exact `numeric`/`decimal` from inexact floating-point types and specifically recommend exact numerics for monetary values. citeturn22view2 | Money/inventory/unit mismatch: Block/High. | Elaborate unit-type systems for values that have one unambiguous unit and no conversion boundaries. |

A charge/local-write example should never be judged merely by reading the success path. Drive at least the ambiguity in which the remote system completes but the caller observes a timeout or local failure; then establish that retry cannot duplicate the effect and that the local system can determine or reconcile the true state. That follows directly from the retry/idempotency and distributed-write literature. citeturn21view5turn17view9

**Error handling and recovery**

| Criterion | What a finding looks like | Static, tested, or driven run? | Evidence-producing technique | Severity guidance by stakes | Where it becomes over-engineering |
|---|---|---|---|---|---|
| Ambiguous timeout is safe | Server commits, response is lost, client retries and creates a second effect. | Targeted driven test | Commit-then-drop-response fault; same idempotency key; inspect external/local state. citeturn21view5 | Irreversible effect: **Block**. | Injecting ambiguous completion into pure reads. |
| Retries are bounded and do not amplify failures | Nested client/service retries keep hammering a degraded dependency. | Static + fault run | Search retry stacks; dependency returns timeout/overload; observe request amplification and recovery. Google SRE warns that retries during overload can worsen cascading failure. citeturn21view6 | High if it can widen an outage; severity rises with criticality/fan-out. | Complex adaptive retry controllers for a low-volume internal tool when bounded backoff suffices. |
| Errors are not swallowed | Exception/log occurs but flow returns success or durable state remains impossible to recover. | Static clue + induced failure | Broad-catch/ignored-result search followed by dependency failure; assert response, state and telemetry. | False success/data loss: High/Block. | Treating every caught, intentionally ignored optional lookup as a finding. |
| User has a recoverable terminal state | Reload or reconnect leaves indefinite spinner or disabled action although retry is safe. | Driven QA | Network interruption, process restart, page/app restart; verify retry/resume/cancel. | High when it hides an unknown consequential outcome; lower for disposable UI state. | Exhaustive client-state testing beyond critical interactions in low-stakes interfaces. |
| Operator can diagnose and act | Alert says “error rate” but has no request/tenant/version/dependency context; runbook cannot distinguish rollback from data repair. | Driven operator drill | Alert test, trace/log correlation, seeded incident, secondary operator walkthrough. Google SRE’s monitoring guidance centres signals on investigation/diagnosis, not merely collecting metrics. citeturn21view7 | Critical service with no diagnostic path: High. | Highly automated remediation before the failure mode is understood or frequent enough to justify it. |

“Recovery” should mean more than returning HTTP 500 cleanly. The acceptance question is whether retry/restart/failover leads to a known correct state **without ad-hoc data surgery**, or whether an explicit, tested operator procedure resolves the exceptional case. Google’s cascading-failure guidance and AWS’s idempotency guidance both make retry behaviour part of system correctness, not just user experience. citeturn21view5turn21view6

**Operational readiness**

| Criterion | What a finding looks like | Static, tested, or driven run? | Evidence-producing technique | Severity guidance by stakes | Where it becomes over-engineering |
|---|---|---|---|---|---|
| Configuration is enumerable and reproducible | Critical production setting exists only in engineer knowledge/manual console state. | Static/build inspection | Generate config-key inventory from manifests/code/secrets references; compare environment; run clean deployment. | High if missing config can produce unsafe state; otherwise Medium. | Documenting every framework default instead of every operationally meaningful setting. |
| Migration is safe across rollout and rollback | New binary writes schema old binary cannot read, making rollback nominal only. | Static + rehearsal | Compatibility analysis; old/new mixed-version test; apply migration, write new data, rollback/roll-forward. AWS guidance explicitly recommends backward-compatible datastore/schema changes and testing coexistence and rollback. citeturn16search6 | Destructive/irreversible migration without tested recovery: **Block**. | Reversible migrations for disposable development data. |
| Build is identifiable and reproducible enough to investigate | Nobody can map production artefact to exact source/build inputs. | Build/tool evidence | Artefact digest + provenance; rebuild where required. Google SRE release engineering emphasises repeatable, automated release processes; SLSA defines verifiable build provenance. citeturn21view8turn18view12 | High for any serious externally operated service; Block when provenance uncertainty invalidates all acceptance evidence. | Perfect bit-for-bit reproducibility when traceable, controlled rebuilding meets actual risk needs. |
| Running version is visible | Incident responder cannot identify release or compare mixed versions. | Driven | Service telemetry/diagnostic endpoint/deployment metadata. `service.version` is a recommended OpenTelemetry resource attribute. citeturn18view13 | High in services with staged deployments/multiple versions. | Building bespoke version infrastructure when the platform already exports immutable digest/version. |
| Health and alert signals correspond to actionable failure | “Process alive” while dependency/data path is unusable; alert cannot identify customer impact. | Driven | Dependency outage, synthetic critical operation, alert-path exercise. Google’s monitoring guidance distinguishes signals used to alert, investigate and diagnose. citeturn21view7 | Missing detection of core critical-flow failure: High. | Probing every optional dependency as hard health and accidentally causing unnecessary unavailability. |
| Rollback/roll-forward is real | Runbook says rollback but migration or external effect makes it unsafe. | Rehearsal | Canary/staged deploy plus rollback test on production-like data/state. Google release practice treats canarying and controlled deployment as release-safety mechanisms. citeturn21view9 | High/Block where bad release can corrupt state and no safe stop path exists. | Elaborate zero-downtime mechanisms for a low-stakes tool that can tolerate a brief maintenance window. |
| A non-author can operate it | Only original engineer understands alerts, config or repair path. | Driven exercise | Give secondary operator symptom + dashboard/runbook, not diagnosis; observe resolution. AWS’s Ops Champion model deliberately challenges operational claims from outside the owning team’s own narrative. citeturn22view1 | High for on-call production service. | Full incident-command simulation for a tiny, easily restored internal utility. |

This is a release-readiness check, **not** a production load-testing programme. The goal is to establish that deployment, rollback, detection, diagnosis and recovery mechanisms actually exist and apply to this RC. Current Google Cloud operational-readiness guidance similarly treats observability, operational processes and readiness as launch prerequisites rather than post-launch documentation. citeturn22view3

**Test and validation evidence**

| Criterion | What a finding looks like | Static, tested, or driven run? | Evidence-producing technique | Severity guidance by stakes | Where it becomes over-engineering |
|---|---|---|---|---|---|
| Critical-flow evidence matrix is complete | Thousands of tests and high coverage, but no test proves “remote charge completed + response lost + retry.” | Evidence analysis + targeted test | Map each selected flow/failure boundary to named test/trace; mark `proven`, `partially proven`, `inferred`, or `absent`. | Missing evidence at high-stakes irreversible boundary: Block. | Requiring every low-level helper test to map to a business flow. |
| Invariant tests are semantic rather than nominal | Test reaches invariant code but assertion would pass if key comparison/constraint were wrong. | Mutation/falsification test | Targeted mutation, seeded faulty implementation, property generators. citeturn20search0 | Core invariant nominally tested: High/Block. | Maximising mutation score globally instead of attacking critical properties. |
| Existing tests are independent enough to trust | Implementation agent wrote code and tests to the same mistaken interpretation; all pass. | Reviewer validation | Build independent black-box/API harness from flow/invariant record, not implementation details. DeepSWE’s 2026 verifier results are direct evidence that test/verifier fidelity matters independently of the code under test. citeturn17view0 | High where existing tests are the sole proof for consequential behaviour. | Rewriting good, externally specified contract tests solely because an agent authored them. Authorship is a risk signal, not disqualification. |
| Observability confirms actual state changes | Test asserts response only; remote system or DB side effect is never inspected. | Driven | Trace + state snapshots/diffs + external mock/provider record. | High for dual-write/irreversible paths. | Full telemetry instrumentation in pure unit-level functions. |

Reviewer-built tooling is justified when a release question cannot be answered credibly by the product’s own tests. The highest-yield tools are usually **small**: an API harness that can resend identical requests, a message redelivery/reordering harness, a dependency stub capable of “commit then timeout,” a two-worker concurrency barrier, a database/state diff, a schema/unit round-trip checker, and a debug view that joins request/trace/idempotency/entity IDs. Full new testing platforms during release acceptance are usually a sign that the system lacks testability that should become a follow-up engineering concern.

## Flow and invariant records

These records are deliberately evidence-centric. The prose tells a reviewer what behaviour matters; every important statement then points to executable or observable evidence. This follows the scenario orientation of ATAM, the measurable-question orientation of ORR, and the functional-verifier lesson from 2026 agent evaluation. citeturn22view0turn22view1turn17view0

**Critical-flow record**

```yaml
flow_id: FLOW-CHECKOUT-COMPLETE
name: Complete checkout
release_candidate: <immutable commit / artefact digest>

purpose:
  actor: customer
  business_effect: creates an order and requests payment
  stakes:
    revenue: <human-confirmed classification>
    data: <classification>
    security: <classification>
    irreversibility: <classification>

selection_evidence:
  measured_frequency: <telemetry query + result ID>
  measured_fanout: <tool result>
  durable_write_count: <tool result>
  external_side_effects:
    - <dependency / operation>
  human_override_reason: <only if ranking overridden>

preconditions:
  - <state that must already hold>

entrypoints:
  - anchor: <route / handler / consumer>
    source: <file:symbol or generated API reference>

implementation_path:
  - step: validate request
    anchor: <code location>
  - step: reserve/update state
    anchor: <code/DB operation>
  - step: perform external side effect
    anchor: <client call>
  - step: commit terminal state
    anchor: <code/DB operation>

state_transitions:
  - from: <state>
    to: <state>
    invariant_refs: [INV-...]

side_effect_boundaries:
  - boundary: <DB commit / provider call / message publication>
    ambiguity_if_interrupted: <what is unknown?>
    dedupe_or_recovery_mechanism: <anchor>

happy_path:
  expected_terminal_state: <observable state>
  evidence:
    test: <test ID>
    trace: <trace/run ID>
    state_diff: <measurement>

failure_paths:
  - stimulus: duplicate submission
    expected_terminal_state: <state>
    evidence: <test/run>
  - stimulus: timeout after external completion
    expected_terminal_state: <state>
    evidence: <test/run>
  - stimulus: dependency rejects operation
    expected_terminal_state: <state>
    evidence: <test/run>
  - stimulus: process restart at critical boundary
    expected_terminal_state: <state>
    evidence: <test/run>
  - stimulus: reordered/redelivered event
    applicability: <yes/no with reason>
    evidence: <test/run>

operator_and_user_recovery:
  user_action: <retry / resume / none>
  operator_action: <runbook / reconciliation / none>
  diagnostic_signal: <dashboard/log/trace/alert>

coverage_judgement:
  status: proven | partially-proven | inferred | absent
  unproven_boundaries:
    - <item>
  reviewer: <independent reviewer>
  evidence_run: <immutable run ID>
```

The important distinction is between `proven` and `inferred`. “I found code that appears to handle this” is static evidence; it is not equivalent to observing or testing the fault where the outcome is consequential.

**Invariant record**

```yaml
invariant_id: INV-PAYMENT-ONE-EFFECT
name: One logical payment request causes at most one external charge
release_candidate: <immutable commit / artefact digest>

scope:
  entities: [payment, order]
  flows: [FLOW-CHECKOUT-COMPLETE, FLOW-PAYMENT-RETRY]

statement:
  formal_or_precise_text: >
    For one logical payment operation / idempotency identity,
    the number of successful provider-side charges is <= 1.

why_it_must_hold:
  consequence_if_violated: duplicate financial side effect
  domain_owner: <human owner>

source_of_invariant:
  business_contract: <reference>
  API_contract: <reference>
  schema_or_model: <reference>
  incident_or_known_risk: <reference if applicable>

enforcement:
  - layer: API
    mechanism: stable idempotency identity
    anchor: <code/schema>
  - layer: persistence
    mechanism: uniqueness / transaction / state machine
    anchor: <schema/code>
  - layer: external_dependency
    mechanism: provider idempotency semantics
    anchor: <contract/config>

tests:
  normal_property:
    test: <ID>
    oracle: <independent expected property>
  duplicate_sequential:
    test: <ID>
  duplicate_concurrent:
    test: <ID>
  ambiguous_timeout_after_completion:
    test: <ID>
  restart_or_redelivery:
    test: <ID if applicable>

falsification_check:
  injected_break:
    description: <remove uniqueness / change comparison / disable dedupe>
    result: <named test must fail>
  mutation_result: <optional targeted mutation result>

runtime_detection:
  assertion_or_constraint: <reference>
  reconciliation_query: <reference if applicable>
  alert_or_metric: <reference if applicable>

known_limits:
  - <cases property does not cover>

review:
  status: proven | partially-proven | inferred | absent
  reviewer: <fresh reviewer>
  adversarial_refutation: <result if serious>
```

Four enforcement forms deserve different evidentiary weight. **Database constraints** can make classes of persistent invalid state impossible and are particularly strong for nullability, uniqueness and referential relationships, although the exact available constraints and their semantics are database-specific. citeturn17view7 **Runtime assertions** make violations observable close to their source but do not themselves prevent every invalid write. **Type/state encodings** can eliminate representationally invalid states inside the typed boundary but do not automatically protect serialized, persisted or concurrently modified state. **Tests** establish behaviour over exercised/generated cases; property/state-machine tests are most useful when the invariant ranges over many inputs or operation sequences. citeturn20search3turn18view10

The review should prefer combinations where appropriate: for example, a DB uniqueness constraint as last-line enforcement, an API idempotency contract, duplicate/concurrency tests, and a reconciliation signal. Redundant evidence is worthwhile when each mechanism protects against a different failure path; mechanically duplicating the same check at every layer is not.

## Agent-specific evidence and reviewer use of agents

The empirical picture in October 2026 is important but narrower than some commentary suggests. There is credible evidence for **long-horizon error propagation, cumulative-agent-state failures, verifier/test-quality problems, and benefits from specification-driven test generation**. There is **not yet credible H2 2026 prevalence evidence** showing that agent-written production systems, as a class, have a measured rate of missing idempotency, double charges, race conditions, fabricated invariant tests or inconsistent error handling. Those remain high-value review hypotheses because distributed systems generally suffer those failures—not because current research has established that agents introduce them at a known rate.

| Proposed agent-specific concern | Evidence status as of 2026-10-13 | What the evidence actually says | Release-review defence |
|---|---|---|---|
| **Tests can be nominal or incomplete despite passing** | **Measured, but in agent benchmark verification rather than deployed production systems** | DeepSWE (July 2026) found substantial disagreement between an independent judge and inherited SWE-Bench Pro test/verifier outcomes, while purpose-written behavioural verifiers had much lower disagreement. The authors explicitly say disagreement is not ground-truth error rate. citeturn17view0 | Do not accept “agent wrote tests and they pass” as sufficient evidence. Build verifier/tests from the flow/invariant specification; use public/observable behaviour and targeted mutation/falsification. |
| **Accumulated agent changes create failures invisible to isolated-task evaluation** | **Measured in a benchmark** | ChainSWE (July 2026): 304 dependent issues, 100 chains, 54 Python projects; performance fell strongly deeper in sequential chains, reaching roughly 70% relative drops in evaluated settings. citeturn18view0turn18view1 | Validate the integrated RC from fresh context. Trace whole flows across accumulated code rather than sampling recent edits. |
| **One early agent error can silently contaminate later work** | **Measured across long-horizon agent trajectories; not coding-only** | September 2026 study: 2,518 analysed trajectories, 6,967 mistakes; after a first mistake only 30.5% recovered, 38.5% never self-detected it, and subsequent errors became much likelier. citeturn19view0 | Isolate reviewer context from author-agent narration and trajectory; ask reviewers to reconstruct from artefacts. Give serious findings to a separate adversarial refuter. |
| **Successful outcome can hide unsafe intermediate actions** | **Measured examples in mixed-domain long-horizon study** | The same study reports solved runs that nevertheless performed destructive actions or fabricated success; it does not establish a production-code prevalence rate. citeturn19view0 | Validate side effects and persistent state, not merely final test status. Record traces/state diffs around irreversible operations. |
| **Explicit contracts improve agent-generated testing** | **Emerging measured evidence** | An August 2026 evaluation using production bugs from Google reported a spec-driven test-generation agent improving bug-detection rate by **9.8 percentage points** and branch coverage by **2.5 percentage points** versus its traditional agent baseline; the reported p-values were 0.0352 and 0.0034 respectively. This is one study, not a universal effectiveness guarantee. citeturn18view2 | Mine/confirm invariants and contracts first, then ask an independent agent to generate adversarial tests from those records rather than from the implementation alone. |
| **AI-authored code carries persistent quality debt** | **Measured H1 2026 baseline, not H2; static-analysis evidence** | An April 2026 study analysed about **302.6k verified AI-authored commits across 6,299 repositories**, reporting 484,366 static-analysis issues, 89.3% classified as code smells, and 22.7% of tracked AI-introduced issues still present at repository HEAD. Static-analysis findings are not equivalent to runtime release defects, and attribution is constrained by observable AI-authorship metadata. citeturn17view13 | Useful reason to retain the existing codebase audit, but do **not** convert static smells into acceptance blockers without a concrete behavioural or engineering-risk path. |
| **Agents disproportionately omit idempotency** | **Not established by a credible H2 2026 prevalence study located in this research** | Idempotency is a well-established requirement for safely retrying consequential operations, but the evidence here does not show an agent-vs-human prevalence number. citeturn21view5 | Treat duplicate/ambiguous-completion tests as standard review attacks for any consequential stateful system, irrespective of authorship. |
| **Agents disproportionately create races/order bugs** | **Not established by a credible H2 2026 prevalence study located** | Concurrency testing literature establishes why these bugs need schedule/interleaving exploration; that is not evidence that agent code causes them more often. citeturn18view10 | Risk-select concurrency tests based on the system’s state model and concurrency, not an unsupported “AI code is racy” assumption. |
| **Agents fabricate invariant tests at a known rate** | **No defensible production prevalence number found** | Current evidence supports concerns about verifier fidelity and hidden long-horizon errors, but not that specific population statistic. citeturn17view0turn19view0 | Require falsification/mutation: deliberately break the property and show the alleged invariant test fails. |
| **Error handling becomes inconsistent across a whole flow** | **Plausible hypothesis; exact agent-specific prevalence unmeasured** | Long-horizon/cumulative-state studies make cross-file inconsistency a reasonable attack surface, but do not quantify this exact production failure class. citeturn18view0turn19view0 | Trace error semantics end to end and induce failures at each consequential boundary rather than reviewing catch blocks in isolation. |

This distinction matters. **“Agent-specific defence” should not become permission to invent an agent-specific defect taxonomy.** Missing idempotency, stale-state overwrite, non-atomic dual write and retry amplification predate coding agents; the case for testing them is already strong from distributed-systems practice. citeturn21view5turn21view6turn17view9 What 2026 adds is evidence that long autonomous implementation chains and their own verification can fail in ways that are difficult for the producing agent—or even another frontier model looking at the trajectory—to notice. citeturn19view0

**How agents should assist the review.** The strongest role is as an evidence transformer and adversarial test generator, not an authority:

| Review task | Good agent role | Bias control |
|---|---|---|
| Flow reconstruction | Convert deterministic route/xref/call-graph output and traces into candidate sequences with every hop linked to its source. | Agent may not invent an unobserved hop. Label static possibility separately from observed trace. Fresh reviewer verifies anchors. |
| Invariant mining | Extract candidate properties from schemas, constraints, state transitions, API contracts, incident descriptions and tests. | Domain owner decides which candidates are true invariants. Do not let the same agent define the invariant and declare its test sufficient. |
| Failure-path generation | For a confirmed flow, propose duplicate, reorder, stale-state, timeout-after-side-effect, crash and dependency-failure attacks. | A deterministic harness executes them; the model never estimates whether a race “probably” exists. |
| Test generation | Generate black-box/property/state-machine tests from the invariant/flow record. Spec-first generation has encouraging 2026 empirical support. citeturn18view2 | Run tests independently; mutation/falsification demonstrates assertion strength. |
| Trace/log analysis | Cluster or reconstruct sequences from machine-generated traces/logs. | Counts, timings, frequencies and ordering come from scripts/query tools, not model estimates. |
| Finding drafting | Turn anchors and reproductions into a concise failure path and impact statement. | Finding is invalid without anchor + reproducer/measurement/trace. |
| Finding refutation | A separate fresh agent receives only the finding, anchors and RC, and is instructed to falsify it. | No author narration; no first reviewer’s chain of conclusions; surviving disagreement goes to human judgement. |
| Final decision support | Summarise evidence and unresolved risks. | Agent gets **no authority to accept risk or release the system**. NIST’s broader risk-authorisation model similarly places the acceptability decision with an accountable senior official. citeturn21view10 |

One especially useful rule follows from the September 2026 failure-localisation work: **do not ask a reviewer agent merely “is this implementation correct?” after showing it the producing agent’s trajectory.** Frontier judges in that study located first mistakes in fewer than a third of long runs even in the best reported cases, and judges exhibited systematic biases. Give reviewers smaller evidence questions instead—“show every durable side effect in FLOW-X,” “produce a test that would falsify INV-Y,” “can the attached finding be reproduced or disproved?”—and let deterministic execution settle whatever can be settled mechanically. citeturn19view0

## Acceptance decision and scaling

The decision stage should look more like an operational risk authorisation than a vote on whether the code “feels ready.” AWS ORR explicitly records residual risk and action items; NIST’s Authorize step, updated in September 2026, makes an accountable senior official responsible for deciding whether documented risk is acceptable and bases that decision on an assessment package and risk responses. The proposed release process can borrow that accountability structure without importing NIST’s security-specific bureaucracy wholesale. citeturn18view9turn21view10

**Recommended blocking rules**

A finding blocks release when a demonstrated or credibly reproducible path can violate a critical invariant, create an unauthorized or duplicate irreversible effect, lose/corrupt unique data, leave consequential distributed state permanently ambiguous, make a critical migration/rollback unsafe, or make a critical failure undetectable/unrecoverable—and there is no independently tested compensating control.

For high-stakes flows, a strategically important **unknown can itself be blocking**. “We cannot establish what happens when the payment completes but the response is lost” is not equivalent to “no defect found.” The ambiguity is the finding. This is particularly justified where idempotency or dual-write correctness determines whether retries are safe. citeturn21view5turn17view9

A High finding normally requires correction before release but may become conditional only when the control materially removes the failure path and is itself tested. Medium findings may be consciously accepted. Low findings can ordinarily enter backlog. Those severity semantics are a proposed rubric, not an industry-standard numerical risk model.

**Accepted-risk record**

```yaml
risk_id: RISK-...
release_candidate: <immutable RC identity>
finding_id: FINDING-...

risk_statement:
  failure_path: <concrete stimulus -> mechanism -> consequence>
  affected_flows: [FLOW-...]
  affected_invariants: [INV-...]

evidence:
  code_anchors: [...]
  test_or_reproducer: [...]
  traces_or_measurements: [...]
  adversarial_refutation_result: <survived / partially refuted>

severity:
  technical_severity: <block/high/medium/low>
  stakes_context: <why consequence matters>
  uncertainty: <what remains unknown>

reason_not_fixed_before_release:
  rationale: <explicit business/engineering reason>

compensating_controls:
  - control: <feature disable / cap / manual gate / reconciliation / monitoring>
    evidence_control_works: <test/run>

detection_and_response:
  detection_signal: <alert/query/dashboard>
  operator_action: <runbook>
  recovery_or_repair_path: <tested procedure>

ownership:
  accountable_risk_owner: <human with authority>
  technical_owner: <human/team>
  approver_or_override_authority: <role/person>

lifecycle:
  tracking_issue: <ID>
  expiry_or_revisit_condition: <date OR event/milestone>
  mandatory_rereview_trigger: <condition>

decision:
  accepted: <yes/no>
  rationale: <human-authored>
  timestamp: <time>
```

The requirement for an accountable acceptance decision is established risk-management practice; the specific fields such as an expiry/revisit condition and paired technical/risk owners are a **recommended synthesis** to stop “accepted risk” becoming permanent undocumented debt. citeturn21view10turn18view9

**Decision states should be simple.**

**Accept** means the frozen RC meets all blocking rules and the approving human explicitly accepts the recorded residual risks.

**Conditional accept** should mean conditions are specific, externally verifiable and mechanically release-gated where possible—for example, “release only after reproducer T-184 passes on the rebuilt RC and migration rollback rehearsal R-22 is attached.” It should not mean “ship now and fix a blocker soon.”

**Do not release** means at least one blocking condition remains, the evidence package does not apply to the current RC, or the decision-maker does not accept the residual risk.

An **override** should not delete or downgrade the technical finding. Record that the finding remains, who exercised authority, why, what control limits exposure, and what forces reconsideration. That separation is important for later incident learning: an incident review should be able to determine whether a risk was unknown, identified and fixed, identified and conditionally controlled, or explicitly accepted.

**The re-review loop is against the rebuilt candidate, not the patch description.** After a fix, produce a new immutable RC; rerun the exact reproducer that established the finding, the associated invariant/flow tests, directly neighbouring failure cases, and any prior runtime-QA scenario affected by the change. Reattach build identity and compare deterministic audit outputs with the stored baseline. Repeat the adversarial challenge when the original finding was serious. This follows the broader readiness principle that review answers must be measurable and the release-engineering principle that the artefact being deployed must be reproducibly identifiable. citeturn22view1turn21view8turn18view12

The decision archive should retain the release digest/version, system overview snapshot, selected-flow/invariant registers, evidence-run IDs, confirmed and refuted serious findings, accepted risks and approvers, conditions and their closure evidence, prior-audit/runtime-QA versions, and the final decision. That turns a future incident from “why did we think this was safe?” into a checkable historical question.

**Scaling by stakes**

The “few thousand users” example below is taken from the research prompt as a qualitative scenario, **not a universal threshold at which review requirements change**. Established launch processes explicitly scale their depth to risk rather than applying identical checklists to every launch. citeturn18view7turn17view5

| System profile | Appropriate acceptance depth | What can usually be skipped | What should not be skipped |
|---|---|---|---|
| **Small internal, reversible tool** | Reconstruct core flow(s); confirm source of truth and basic invariants; normal/error paths; clean deployment and rollback; useful diagnostics; have a second person operate it. | Systematic concurrency exploration when genuinely single-user/stateless; sophisticated reconciliation; extensive fault matrix; formal/model-based analysis. | Immutable RC identity, critical behaviour evidence, recoverable data changes, diagnosis and rollback. |
| **Consumer app at roughly the scale described in the prompt, with ordinary recoverable state** | Broader flow/invariant matrix; duplicate/retry tests for writes; dependency timeout cases; schema/client round trips; migration rehearsal; alert/runbook check; selected reviewer-built API/fault harnesses. | Full deterministic distributed simulation and large chaos/load campaigns unless architecture gives a specific reason. | Consequential state transitions, retry ambiguity, data integrity, deploy/recovery evidence and production version visibility. |
| **High-concurrency/stateful service** | Everything above plus orchestrated races, duplicate/redelivered events, stale-read/update tests, ordering tests, targeted systematic scheduling/model tests for core state machines, retry-amplification exercises. Coyote demonstrates that controlled concurrency exploration can target such nondeterminism without relying on stress alone. citeturn18view10 | Formal verification of every component; exhaustive whole-system scheduling unless consequences justify it. | Concurrency-sensitive invariants, persistent uniqueness, idempotency, event semantics, overload-safe retries and diagnosability. |
| **Money, inventory, unique/irreplaceable data, or irreversible external effects** | Treat conservation, exactness, uniqueness and valid transitions as first-class invariants; prove duplicate safety and ambiguous completion; inspect every cross-system transaction boundary; require reconciliation; use exact units/precision; rehearse data migrations and failure recovery. citeturn21view5turn17view9turn22view2 | Cosmetic-path depth, broad mutation testing outside risk areas, formal methods where simpler executable constraints/tests prove the property. | No unproven irreversible boundary; no unknown duplicate semantics; no unreconciled dual write; no nominal rollback; no release without enough telemetry to identify and repair an exceptional state. |

Across all stakes, the irreducible core is smaller than a giant checklist: **know what artefact is being accepted; know which end-to-end behaviours matter; know the invariants protecting consequential state; demonstrate what happens when important operations fail or repeat; know how to detect and recover from a bad release; and make an accountable human explicitly own the residual risk.** That is the common thread connecting mature launch/readiness reviews, ATAM-style scenario analysis, established reliability engineering, and the specific verification weaknesses now visible in 2026 agent research. citeturn17view4turn17view5turn22view0turn19view0