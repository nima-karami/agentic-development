# **Release Acceptance Review for Agent-Authored Systems: A 2026 Framework**

The release acceptance review for an agent-built software system demands a fundamental departure from historical code-reading practices, shifting the validation burden entirely from human line-by-line inspection to automated behavioral verification. The process requires a prior codebase audit to compute structural conformance and a runtime QA pass to provide dynamic execution logs. Reviewers leverage tooling to reconstruct the system architecture and isolate 10 to 15 critical flows, which are subsequently traced through both happy and adversarial failure paths. System invariants—such as financial conservation or data isolation—are mathematically formalized, computationally mined via Large Language Models (LLMs), and verified using state-machine property testing. Concurrency, idempotency, and correctness are validated not by static inference, but through Deterministic Simulation Testing (DST) that compresses thousands of chaotic distributed interactions into reproducible fault scenarios. The review explicitly targets novel failure classes unique to 2026 agent-written systems, including silent feature drops, intent inversions, and hallucinated tests that tautologically validate buggy code. Ultimately, the human evaluator serves solely as the final arbiter of risk, adjudicating an automated adversarial pass and formalizing an explicit acceptance decision supported by a defensibility-ranked accepted-risk register.

## **1\. The Evolution of Release Readiness and Prior Art**

The discipline of assessing a system's readiness for production has historically relied on manual inspection, cross-functional workshops, and deliberate, human-paced architectural reviews. Foundational methodologies established by Google and Amazon Web Services (AWS) approached release readiness as an exercise in human collaboration and operational discipline. The Google Site Reliability Engineering (SRE) model popularized the Production Readiness Review (PRR), a phased lifecycle approach wherein SREs analyzed interservice dependencies, capacity planning, and emergency response capabilities before assuming operational responsibility1. The PRR was inherently collaborative, requiring design overviews and deep dives into request flows negotiated directly with the development team1. Concurrently, the AWS Operational Readiness Review (ORR) mechanism utilized curated checklists derived from past operational incidents to enforce best practices. This model relied on iterative inspection, often leveraging an "Ops Champion" to guide product teams through the evaluation of real incidents and near-misses to prevent recurrence3.  
In parallel, structural evaluations relied on the Architecture Tradeoff Analysis Method (ATAM) developed by the Software Engineering Institute (SEI). ATAM was designed to assess the consequences of architectural decisions against business drivers by gathering stakeholders to generate a "quality attribute utility tree"5. The process involved presenting the architecture—often utilizing the 4+1 view model—and brainstorming operational scenarios to identify risks and sensitivity points5.  
By the second half of 2026, the foundational assumptions of these methodologies have collapsed under the velocity of AI "vibe coding," wherein developers describe intent and coding agents instantly generate massive implementations7. Traditional QA processes, which assume deliberate authorship and slow, incremental change, cannot sustain agent throughput; human review becomes an immediate bottleneck8. Furthermore, agent-authored code introduces novel defect classes. Agents frequently construct syntactically flawless systems that quietly drop existing safeguards, invert business logic, or optimize exclusively for the "happy path" while swallowing critical errors7.  
Consequently, the 2026 release acceptance review eliminates subjective code reading and workshop-based design reviews. Instead, the review mechanism treats the agent-generated codebase as an untrusted black box. The evaluation shifts entirely to verifying behavioral contracts: asserting that the system honors its required state transitions under adversarial conditions, preserves data integrity during schema evolution, and correctly handles chaotic concurrent events.

## **2\. The Step-by-Step Acceptance Method**

The 2026 release acceptance review operates as the final gate before production deployment. It relies on two mandatory inputs: a prior codebase audit (which deterministically evaluates structural conformance, gate integrity, and security via fresh-context agents) and runtime QA (which drives the built system to report observed behaviors). The core principle is that anything computable is computed by a tool, never estimated by an LLM, while human judgment is reserved exclusively for risk adjudication.  
The method proceeds through the following structured steps:

> 1. **System Reconstruction:** Tooling parses the codebase audit artifacts and runtime QA telemetry to automatically map the system architecture, API contracts, and physical deployment topology.  
> 2. **Critical Flow Selection:** The human review team evaluates the reconstructed architecture to select the 10 to 15 execution paths that govern the system's core viability, prioritizing flows based on revenue impact, security boundaries, and data irreversibility.  
> 3. **Trace Verification:** Tooling overlays distributed traces from the runtime QA onto the selected flows, verifying that the system successfully navigates both expected operations and induced failures.  
> 4. **Invariant Formalization:** Fresh-context agents assist in mining potential invariants from the code and data. Reviewers formalize these invariants and verify that the test suite enforces them through rigorous, shrinking property-based tests.  
> 5. **Simulation and Fault Injection:** The built artifact is subjected to Deterministic Simulation Testing (DST) to expose race conditions, non-idempotent operations, and state corruption in a time-controlled, reproducible environment.  
> 6. **Data Integrity Audit:** The database migration sequence is computationally analyzed to ensure strict adherence to the expand-contract pattern, guaranteeing zero-downtime compatibility.  
> 7. **Test Evidence Adjudication:** The automated test suite is scrutinized to filter out tautological, AI-generated "hallucinated tests." The review team demands intent-based testing that asserts behavioral outcomes rather than merely verifying the existing buggy implementation.  
> 8. **Adversarial Pass:** All high-severity findings identified in the previous steps are subjected to an automated adversarial refutation. A separate agent context attempts to prove the finding is a false positive by finding an execution path that safely handles the defect.  
> 9. **The Acceptance Decision:** The human reviewer claims ownership of the final decision, categorizing unrefuted findings into hard blocking requirements or routing them to a defensibility-ranked accepted-risk register with defined compensating controls and expiration dates.

## **3\. System Overview and Automated Reconstruction**

A critical vulnerability in reviewing agent-written systems is reliance on human-authored documentation, which rapidly falls out of sync with the underlying codebase. The minimum system overview required for an effective review encompasses the high-level architecture views, external API contracts, internal data models, dependency graphs, and the explicit deployment and rollback mechanisms.  
In 2026, mature engineering teams recover this overview entirely from the code, build artifacts, and runtime history. Abstract Syntax Tree (AST) analysis extracts the data models and module boundaries directly from the source code10. The API contracts are reconstructed by analyzing the runtime QA logs, parsing the actual payloads, headers, and endpoints invoked during the driven run. The deployment topology is reverse-engineered from infrastructure-as-code manifests and CI/CD pipeline definitions.  
By utilizing executable code and dynamic telemetry to document the integration blocks, the review team receives an exact, computationally verified snapshot of the system as it truly exists11. Agents can safely assist in formatting this extracted data into human-readable topological maps, provided they are constrained to describing the deterministic output of the tooling without injecting generative assumptions.

## **4\. Establishing and Tracing Critical Flows**

Attempting to evaluate every execution path in a system generated by an LLM leads to superficial analysis and alert fatigue. The review must isolate and deeply interrogate the 10 to 15 critical flows that define the application's operational integrity.

### **Flow Selection Criteria**

Reviewers choose critical flows based on five unyielding vectors:

* **Revenue Impact:** Paths that process payments, calculate taxes, or govern subscription access.  
* **Data Lifecycle:** Operations that execute irreversible data creation, mutation, or deletion.  
* **Security Boundaries:** Authentication handshakes, session token generation, and authorization checks.  
* **Frequency:** High-throughput pathways that, if degraded, would consume the system's resource budget.  
* **Irreversibility:** Actions that cannot be safely undone through a standard database rollback.

### **Tracing and Coverage Evaluation**

Tracing these flows requires correlating the static codebase with the dynamic reality of execution. Tooling constructs call graphs from the static analysis and overlays them with distributed traces captured during the runtime QA phase. This sequence reconstruction maps the exact journey of a request from the client SDK, through the API gateway, across microservices, and into the persistence layer.  
Coverage is not judged by line execution, a metric easily gamified by agent-generated code8. Instead, coverage is evaluated based on the flow's behavioral contract. The review demands evidence that the system successfully navigates the "happy path" while definitively mitigating catastrophic failure paths12. The runtime QA must demonstrate that the system exhibits controlled behavior when it encounters invalid authentication tokens, database connection timeouts, or malformed data structures.

### **Critical-Flow Record Format**

To ensure uniform evaluation, each critical flow is documented using a standardized, machine-readable record that links the expected behavior to a concrete anchor in the evidence.

YAML  
flow\_id: "FLW-PAY-003"  
description: "Checkout and payment authorization via external provider"  
stakes: HIGH  
vectors: \[revenue, irreversibility\]  
entry\_point: "api.checkout.process"  
exit\_point: "ledger.transaction.commit"  
anchor\_trace: "trace\_id\_492b1\_qa\_run"  
coverage\_assessment:  
  happy\_path:  
    status: "VERIFIED"  
    evidence: "E2E\_intent\_test\_pay\_01 (Pass)"  
  failure\_paths:  
    \- condition: "Payment gateway timeout post-authorization"  
      expected\_behavior: "Queue for asynchronous reconciliation, do not double-charge"  
      observed\_behavior: "VERIFIED \- Outbox pattern engaged, retried with backoff"  
      evidence\_anchor: "DST\_Fault\_Inject\_NetDrop\_05"  
    \- condition: "Idempotency key collision on rapid double-click"  
      expected\_behavior: "Return 409 Conflict, process single charge"  
      observed\_behavior: "FAIL \- Agent code bypassed cache check under load"  
      evidence\_anchor: "Concurrency\_Test\_Harness\_02"  
adversarial\_refutation: "Failed. Double charge confirmed under 50ms latency simulation."

### **Table 1: Critical Flows Area Rubric**

| Criterion | What a finding looks like | Evidence Type | Tool/Technique | Severity (High Stakes) | Over-Engineering Threshold |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Happy Path Execution** | The system fails to complete the core business action under normal operating conditions. | Driven run | E2E Intent-based YAML testing8 | Blocker | Enforcing pixel-perfect visual regression on minor layout shifts. |
| **Data Isolation** | User A can access or mutate User B's records by manipulating URL parameters. | Tested / Driven | Multi-tenant permission matrix testing13 | Blocker | Validating tenant isolation on single-tenant, internal admin dashboards. |
| **Failure Path Resilience** | An external API timeout causes the application to crash or enter an infinite loading loop. | Tested | Fault injection proxies (e.g., Toxiproxy) | High Risk | Simulating the simultaneous collapse of multiple AWS availability zones for a low-stakes app. |

## **5\. System Invariants and Model-Based Verification**

Invariants constitute the mathematical and logical truths that a system must uphold regardless of external conditions. Examples include the conservation of money in a financial ledger, the uniqueness of identifiers, and the strict ordering of valid state transitions. AI coding agents, optimizing for localized logic, frequently introduce subtle refactoring changes that violate these global properties7.

### **Invariant Mining and Extraction**

Identifying these invariants relies on both human domain expertise and computational mining. Foundational tools like the Daikon system monitor runtime execution values to deduce likely invariants dynamically14. In 2026, this capability is vastly augmented by LLM-driven specification generation. Tools such as Autogram leverage telemetry data to propose bounding grammars, enabling the discovery of network invariants while constraining the LLM's non-determinism to ensure the generated specifications remain logically decidable16. Furthermore, frameworks like Path2Spec execute a divide-and-conquer strategy, forcing the agent to extract execution paths logically and generate path-specific preconditions and postconditions, significantly outperforming earlier baseline models17. Reviewers deploy these tools in a fresh context to mine the built system, presenting the human evaluator with a list of computationally derived invariants for formal approval.

### **Verification and Test Strength**

Once recorded, invariants must be continuously verified. Traditional example-based unit tests are insufficient. The review requires the deployment of property-based testing (utilizing libraries such as Hypothesis or QuickCheck), which shifts the paradigm from specific examples to asserting invariant properties across massive volumes of systematically varied inputs19. For temporal properties, state-machine testing (a subset of model-based testing) is required. The test framework tracks the evolving state of the system through a sequence of operations, validating pre- and post-conditions at every transition19.  
A critical task for the reviewer is differentiating between a "strong" and a "nominal" invariant test. A strong test leverages rapid data generation, adversarial edge-case bias, and automatic shrinking (reducing a failing test case to its simplest reproducible form)19. Conversely, a nominal test uses hardcoded values to traverse the happy path, a common artifact of AI-generated test suites designed merely to satisfy line-coverage metrics20.

### **Invariant Record Format**

YAML  
invariant\_id: "INV-STATE-014"  
domain: "Order Lifecycle"  
description: "An order state cannot transition from 'Pending' directly to 'Shipped' without passing through 'Paid'."  
enforcement\_mechanism: "Database constraint (State Machine) \+ Property-based state testing"  
test\_anchor: "tests/property/order\_state\_machine.py::test\_valid\_transitions"  
test\_strength: "STRONG"  
strength\_justification: "Hypothesis stateful test framework explores arbitrary sequences of API commands and shrinks failures to minimal reproducible transition chains."  
mining\_source: "Path2Spec static extraction \+ Human formalization"  
status: "VERIFIED"

### **Table 2: Invariants Area Rubric**

| Criterion | What a finding looks like | Evidence Type | Tool/Technique | Severity (High Stakes) | Over-Engineering Threshold |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Invariant Formalization** | Core business logic rules are implicit and lack programmatic enforcement. | Static / Mined | Daikon, Path2Spec, Autogram14 | High Risk | Mining transient, inconsequential UI state invariants. |
| **State Machine Enforcement** | The system permits an entity to bypass a mandatory authorization state. | Tested | Hypothesis / QuickCheck stateful testing19 | Blocker | Implementing strict state machines for stateless, read-only API facades. |
| **Test Strength** | The property test relies on a narrow band of nominal integers and lacks automatic shrinking. | Tested | Mutation testing / Property test frameworks19 | Medium Risk | Mandating exhaustive property generation for simple text localization formatting. |

## **6\. Correctness, Concurrency, and Deterministic Simulation**

Reviewing a built system for race conditions, stale state, and non-idempotent operations represents the most challenging phase of acceptance. In distributed environments, overlapping network requests and event-ordering assumptions produce chaotic interactions that traditional testing methodologies cannot reliably capture. Historically, Jepsen testing provided the gold standard for verifying distributed systems by interacting with user-visible APIs from the outside and injecting faults22. However, Jepsen tests are notoriously slow and complex to maintain.  
In 2026, the review relies heavily on Deterministic Simulation Testing (DST). Platforms such as Antithesis and TigerBeetle's Viewstamped Operation Replicator (VOPR) execute the entire system within a specialized simulated environment22. By separating the application's business logic from its dependency on system time and random number generation, DST frameworks gain total control over the environment's clock and physical interactions, such as storage latency and network partitioning22.  
During the review, DST executes thousands of discrete event simulations per second, violently faulting the system to expose duplicate executions (e.g., double submits or redelivered messages) and race conditions26. If the system state corrupts, the DST platform outputs the exact random seed that triggered the failure, allowing the engineering team to perfectly reproduce the bug23. In an agent-written system, static analysis is broadly incapable of verifying the correctness of complex concurrent operations; targeted fault injection within a DST environment is the only affordable and conclusive mechanism to validate correctness before release.

### **Table 3: Correctness and Concurrency Area Rubric**

| Criterion | What a finding looks like | Evidence Type | Tool/Technique | Severity (High Stakes) | Over-Engineering Threshold |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Race Conditions** | Concurrent writes to the same resource bypass locks, leading to lost updates. | Driven run | DST (Antithesis, VOPR)22 | Blocker | Deploying DST on entirely stateless, read-only content delivery networks. |
| **Idempotency** | A network timeout causes the client to retry, resulting in a duplicate database entry. | Tested | Concurrent double-submit API testing13 | Blocker | Requiring strict idempotency keys on naturally idempotent GET requests. |
| **Event Ordering** | Out-of-order asynchronous message delivery corrupts subsequent data processing steps. | Driven run | Network jitter simulation / DST | High Risk | Forcing total global ordering where simple causal ordering is mathematically sufficient. |

## **7\. Data Integrity and Schema Evolution**

The data integrity review ensures that the system correctly manages the source of truth across client SDKs, microservices, and persistence layers. Reviewers must scrutinize how the system handles schema changes, partial writes, and precision arithmetic.

### **The Expand-Contract Pattern**

Outages frequently occur when schema changes conflict with a running application—such as when an ALTER TABLE operation acquires a schema lock that blocks reads and writes, or when a column is dropped while old code is still attempting to query it28. To achieve zero-downtime deployments, the review mandates strict adherence to the expand-contract pattern (Parallel Change)29.  
The review tooling analyzes the migration scripts to ensure incompatible changes are broken into three distinct, version-controlled phases:

> 1. **Expand:** The schema is expanded to introduce the new structure (e.g., adding a new column) without modifying or removing the existing structure, preserving backward compatibility30.  
> 2. **Migrate (Transition):** Application code is updated to dual-write to both the old and new structures, while backfill operations migrate historical data30.  
> 3. **Contract:** Only after telemetry and code audits prove that the legacy structure is entirely unreferenced by the application does the final migration safely drop the obsolete elements30.

A critical finding in this domain occurs if a migration file attempts to rename a column or merge an expansion and contraction into a single deployment step, guaranteeing a temporary outage for in-flight requests29.

### **Floating-Point Precision Vulnerabilities**

In agent-written code, there is a high probability that the LLM will default to utilizing language primitives such as float or double for numerical calculations. Because these types utilize IEEE 754 floating-point representations, they cannot perfectly represent specific decimal fractions, leading to microscopic rounding errors (e.g., ![][image1] resolving to ![][image2])33. When these values are subjected to repeated arithmetic in financial systems, the errors accumulate, resulting in severe ledger drift. The review relies on static analysis to detect the usage of float or double in any financial or precision-critical execution path. The mandatory required change is the implementation of immutable arbitrary-precision decimal libraries, such as BigDecimal in Java or the decimal module in Python33.

### **Table 4: Data Integrity Area Rubric**

| Criterion | What a finding looks like | Evidence Type | Tool/Technique | Severity (High Stakes) | Over-Engineering Threshold |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Expand-Contract Compliance** | A schema migration script renames a live column in a single transaction. | Static | SchemaQuench, AST migration analysis28 | Blocker | Requiring expand-contract for tables in ephemeral, local developer databases. |
| **Floating-Point Precision** | Financial calculation logic relies on double primitives, leading to precision loss. | Static | AST primitive type scanners34 | Blocker | Banning floating-point math in non-critical analytical scoring or UI rendering. |
| **Partial Write Safety** | A distributed saga succeeds locally but fails externally, leaving state unsynchronized. | Tested | Distributed outbox pattern monitoring | Blocker | Implementing complex two-phase commits for non-essential telemetry logging. |

## **8\. Error Handling, Recovery, and Agent-Specific Patterns**

The review must assess how the system manages expected failures and whether it degrades gracefully without requiring manual database intervention. The emergence of agent-written systems in H2 2026 has introduced highly specific patterns of failure regarding error handling, as agents optimize for the immediate request context while failing to account for macro-level system resilience.

### **Agent-Specific Failure Classes**

> 1. **The Happy Path Bias:** Agents excel at constructing logic for the golden path. However, they frequently fail to implement robust try-catch structures for network timeouts or malformed payloads, resulting in applications that hang indefinitely or cache corrupt partial state9.  
> 2. **Silent Feature Drop:** When an agent is prompted to refactor or update a file, it will often silently remove previously existing safety mechanisms—such as offline fallbacks, rate limiters, or row-level security filters—simply because the user's prompt did not explicitly demand their preservation7. This represents the dominant regression risk in vibe-coded applications.  
> 3. **Intent Inversion:** An agent generates syntactically correct code that executes the exact opposite of the business requirement (e.g., querying oldest-first instead of newest-first). Because the code compiles and runs, structural audits miss this entirely; it is only caught through behavioral trace verification7.  
> 4. **Inconsistent Error Swallowing:** Agents frequently employ empty catch blocks or return generic HTTP 500 status codes without logging context, effectively destroying diagnostic visibility and leaving operators blind during an incident13.

Reviewers evaluate error recovery by actively inducing timeouts and network drops during the runtime QA. The system must exhibit controlled retry safety, utilizing exponential backoff and jitter to prevent retry storms that could overwhelm downstream services.

### **Agent Assistance in the Review**

While agents introduce these risks, they are also leveraged to assist the review. Provided they operate in a fresh context—completely isolated from the original authoring prompts to eliminate bias—agents can successfully reconstruct execution flows from traces, parse logs to identify swallowed errors, and generate adversarial test inputs for fuzzing15.

### **Table 5: Error Handling and Recovery Area Rubric**

| Criterion | What a finding looks like | Evidence Type | Tool/Technique | Severity (High Stakes) | Over-Engineering Threshold |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Silent Feature Drop** | An agent refactor eliminated a pre-existing rate-limiter on an authentication endpoint. | Static / Tested | Behavioral regression testing / Codebase Audit7 | High Risk | Flagging the removal of genuinely obsolete or deprecated code pathways. |
| **Retry Storms** | The application rapidly retries failed upstream requests without backoff. | Driven run | Telemetry rate-monitoring under induced fault | Blocker | Micro-tuning backoff jitter parameters beyond a reasonable millisecond variance. |
| **Swallowed Errors** | The agent implemented a generic catch that discards the stack trace. | Static | Linter / Log analysis | High Risk | Demanding verbose stack traces for expected client-side validation errors (400s). |

## **9\. Testing and Validation Evidence**

In the 2026 paradigm, the existence of a test suite is not inherent proof of system quality, as the same agent that authored the code frequently generates the tests. This creates a severe conflict of interest, resulting in hallucinated tests and tautological assertions8.  
An AI-generated tautological test merely validates the existing implementation, flaws included. For example, if a bug in a tax calculation method causes it to return a negative number, the agent will frequently generate a test asserting that the method *should* return a negative number, artificially inflating line-coverage metrics while verifying incorrect behavior21. Furthermore, agents operating without context will hallucinate DOM selectors or mock data that do not reflect the actual system structure37.  
The release acceptance review categorically rejects line coverage as evidence. Reviewers judge the test suite based on invariant coverage, behavioral contract alignment, and mutation resilience8. Modern workflows, such as the 9-stage vibe coding QA process, demand that intent-based tests are authored explicitly to capture human requirements before the agent generates the implementation, ensuring the tests act as a genuine behavioral boundary8. If the suite is deemed weak—relying on nominal inputs and lacking adversarial scenarios—the reviewers are empowered to construct their own validation harnesses, utilizing API fuzzers and fault injectors to stress the system independently.

### **Table 6: Test Evidence Area Rubric**

| Criterion | What a finding looks like | Evidence Type | Tool/Technique | Severity (High Stakes) | Over-Engineering Threshold |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Tautological Tests** | Tests lack assertions or simply assert that the code does whatever it currently does. | Static | LLM-as-a-judge / Mutation testing21 | Blocker | Manually auditing every single generated mock object in a massive suite. |
| **Intent-based Coverage** | Tests are tightly coupled to fragile DOM selectors rather than user workflows. | Static | DOM-independent YAML execution frameworks7 | Medium Risk | Abstracting test logic to the point where it becomes unreadable custom DSL. |
| **Adversarial Resilience** | The suite only verifies the golden path and ignores edge cases. | Tested | Fuzzing / AFL++15 | High Risk | Fuzzing tightly-coupled, internal typed APIs that never receive public input. |

## **10\. Operational Readiness**

Operational readiness evaluates the operability of the system from the perspective of the engineers who will maintain it. Drawing on established ORR principles, the review verifies that the system includes the necessary controls to detect, diagnose, and resolve production incidents without slowing down feature velocity4.  
Before release, the review must confirm:

* **Reproducible Builds:** The deployed artifact must deterministically match the audited source code.  
* **Configuration Management:** Secrets must be decoupled from the codebase, and all infrastructure configurations must be documented and version-controlled.  
* **Version Visibility:** Production telemetry and logs must explicitly broadcast the running commit hash and version.  
* **Health Signals:** Monitoring must prioritize out-of-SLO symptoms (e.g., increased latency, degraded success rates) over low-level causal alerts (e.g., CPU utilization), thereby reducing alert fatigue41.  
* **Rollback Paths:** The system must possess a documented, tested rollback procedure, with explicit acknowledgment of the points of no return inherent in database schema contractions31.  
* **Diagnostic Independence:** The telemetry must be legible enough that an operator completely unfamiliar with the original agent prompts can trace an incident to its root cause.

### **Table 7: Operational Readiness (ORR) Area Rubric**

| Criterion | What a finding looks like | Evidence Type | Tool/Technique | Severity (High Stakes) | Over-Engineering Threshold |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Health Signals** | Alerting is configured exclusively for resource utilization rather than user SLOs. | Static | Infrastructure-as-code review41 | Medium Risk | Mandating strict SLO definition for internal, low-traffic cron jobs. |
| **Rollback Paths** | A database schema contraction lacks a corresponding application rollback strategy. | Static | CI/CD pipeline review31 | Blocker | Requiring sub-second rollback capabilities for batch analytics warehouses. |
| **Configuration Safety** | Environment-specific toggles or API keys are hardcoded into the binary. | Static | Secret scanners / Source review | Blocker | Parameterizing trivial, non-sensitive constants (e.g., frontend styling). |

## **11\. The Acceptance Decision Structure**

The review process culminates in a formal acceptance decision owned by a human authority. To prevent subjective overrides and ensure accountability, mature organizations structure this decision around severity gates and a defensibility-ranked risk register.

### **Severity Gates and Blocking Rules**

Findings are categorized by severity based on the stakes of the system. Critical findings—such as broken financial invariants, failure to implement data isolation, floating-point precision loss, or reliance on tautological tests—are mandatory blockers. The release candidate is unequivocally rejected, triggering a re-review loop where the system is evaluated again after the agent implements required fixes. Medium-severity findings may allow for conditional acceptance, provided an immediate compensating control is implemented (e.g., adding an active runtime monitor for a suspected but unproven race condition).

### **The Accepted-Risk Register**

Technical debt and unmitigated hazards that are permitted into production must be formalized in the Accepted-Risk Register. In 2026, static, forgotten spreadsheets are insufficient. The register is a dynamic system structured to prevent the silent accumulation of risk42.

* **Ranked by Defensibility:** Hazards are ranked not by the date they were accepted, but by how defensible the original acceptance remains today42.  
* **Named Ownership:** Every accepted risk must have a single, named human owner on the record. "The team" is not an acceptable owner43.  
* **Rationale and Evidence:** The explicit reasoning chain and the evidence supporting the acceptance must be documented, ensuring auditors do not continually re-flag resolved decisions43.  
* **Expiry and Review:** Acceptances age out. Evidence older than a defined period (typically a quarter) causes the risk to automatically reopen, forcing the owner to re-evaluate the hazard before an auditor or an incident exposes it42.

## **12\. Scaling the Review**

Applying the entirety of this framework to every codebase creates paralyzing friction. The depth of the review must dynamically scale with the system's load profile and business stakes.

* **Internal Tools (Low Stakes):** For simple internal utilities or dashboards, a basic review is sufficient. The codebase audit, intent-based testing, and happy-path critical flow validation are required. Expensive operations like DST and exhaustive state-machine property testing can be safely skipped.  
* **Consumer Applications (Medium Stakes):** For applications handling moderate external traffic, the review escalates. The expand-contract schema pattern is mandatory to prevent deployment outages. Rigorous permission and data isolation checks are required13, and standard property-based testing must be implemented.  
* **High-Concurrency and Financial Services (High Stakes):** For systems handling monetary transactions or massive concurrency, no element of the framework can be skipped. DST/VOPR is mandatory to validate idempotency and correctness. Floating-point primitive scans are non-negotiable. Every system invariant must be mathematically defined, mined via tooling, and strictly verified through adversarial state-machine testing.

#### **Works cited**

> 1. Google SRE \- Production Readiness Review: Engagement Insight, [https\://sre.google/sre-book/evolving-sre-engagement-model/](https://sre.google/sre-book/evolving-sre-engagement-model/)  
> 2. Ben Treynor Sloss on sre and sre team responsibilities \- Google SRE, [https\://sre.google/in-conversation/](https://sre.google/in-conversation/)  
> 3. Operational Readiness Reviews (ORR) \- AWS Documentation, [https\://docs.aws.amazon.com/wellarchitected/latest/operational-readiness-reviews/wa-operational-readiness-reviews.html](https://docs.aws.amazon.com/wellarchitected/latest/operational-readiness-reviews/wa-operational-readiness-reviews.html)  
> 4. Operational Readiness Reviews (ORR) \- AWS Well-Architected, [https\://docs.aws.amazon.com/pdfs/wellarchitected/latest/operational-readiness-reviews/operational-readiness-reviews.pdf](https://docs.aws.amazon.com/pdfs/wellarchitected/latest/operational-readiness-reviews/operational-readiness-reviews.pdf)  
> 5. Enterprise architecture \- JC Olamendy's Thoughts, [https\://johnolamendy.wordpress.com/tag/enterprise-architecture/](https://johnolamendy.wordpress.com/tag/enterprise-architecture/)  
> 6. Architecting Complex, Long-Lived Scientific Software \- arXiv, [https\://arxiv.org/html/2304.13797v1](https://arxiv.org/html/2304.13797v1)  
> 7. Vibe Coding Testing: Add QA Without Slowing Down (2026), [https\://www\.shiplight.ai/blog/vibe-coding-testing](https://www.shiplight.ai/blog/vibe-coding-testing)  
> 8. How to Set Up a Vibe Coding QA Process (9-Stage Workflow, 2026), [https\://www\.shiplight.ai/blog/how-to-set-up-vibe-coding-qa-process](https://www.shiplight.ai/blog/how-to-set-up-vibe-coding-qa-process)  
> 9. Can Agents Design Libraries for Agents? \- arXiv, [https\://arxiv.org/pdf/2609.36730](https://arxiv.org/pdf/2609.36730)  
> 10. AST structure for a C\# code snippet produced by tree-sitter., [https\://www\.researchgate.net/figure/AST-structure-for-a-C-code-snippet-produced-by-tree-sitter\_fig3\_382231473](https://www.researchgate.net/figure/AST-structure-for-a-C-code-snippet-produced-by-tree-sitter_fig3_382231473)  
> 11. System Analysis and Design: Tutorial & Best Practices | Multiplayer, [https\://www\.multiplayer.app/distributed-systems-architecture/system-analysis-and-design/](https://www.multiplayer.app/distributed-systems-architecture/system-analysis-and-design/)  
> 12. Posts \- CoatiPress, [https\://coatipress.com/posts/](https://coatipress.com/posts/)  
> 13. How to Test Vibe-Coded Apps Before Launch (2026) | Shiplight AI, [https\://www\.shiplight.ai/blog/how-to-test-vibe-coded-apps-before-launch](https://www.shiplight.ai/blog/how-to-test-vibe-coded-apps-before-launch)  
> 14. The Daikon system for dynamic detection of likely invariants, [https\://www\.researchgate.net/publication/222412498\_The\_Daikon\_system\_for\_dynamic\_detection\_of\_likely\_invariants](https://www.researchgate.net/publication/222412498_The_Daikon_system_for_dynamic_detection_of_likely_invariants)  
> 15. Machine Learning-Driven Software Testing: Towards Autonomous, [https\://iarconsortium.org/srjmd/174/2913/machine-learning-driven-software-testing-towards-autonomous-bug-detection-in-2025-5080/](https://iarconsortium.org/srjmd/174/2913/machine-learning-driven-software-testing-towards-autonomous-bug-detection-in-2025-5080/)  
> 16. Invariant Discovery for Networked Systems, [https\://hhy.ee.princeton.edu/papers/2026\_preprint\_autogram.pdf](https://hhy.ee.princeton.edu/papers/2026_preprint_autogram.pdf)  
> 17. (PDF) Path2Spec: Path-Aware Specification Generation via Large, [https\://www\.researchgate.net/publication/414926350\_Path2Spec\_Path-Aware\_Specification\_Generation\_via\_Large\_Language\_Models](https://www.researchgate.net/publication/414926350_Path2Spec_Path-Aware_Specification_Generation_via_Large_Language_Models)  
> 18. Path2Spec: Path-Aware Specification Generation via Large ... \- arXiv, [https\://arxiv.org/html/2609.33438](https://arxiv.org/html/2609.33438)  
> 19. Comprehensive Guide to Property-Based Testing in Go \- DZone, [https\://dzone.com/articles/property-based-testing-guide-go](https://dzone.com/articles/property-based-testing-guide-go)  
> 20. Hypothesis Documentation, [https\://hypothesis.readthedocs.io/\_/downloads/en/hypothesis-python-4.57.1/pdf/](https://hypothesis.readthedocs.io/_/downloads/en/hypothesis-python-4.57.1/pdf/)  
> 21. Generating Tests With AI: Powerful Tool or Risky Shortcut?, [https\://thenewstack.io/using-ai-for-test-generation-powerful-tool-or-risky-shortcut/](https://thenewstack.io/using-ai-for-test-generation-powerful-tool-or-risky-shortcut/)  
> 22. Protocol-Aware Deterministic Simulation Testing \- TigerBeetle, [https\://tigerbeetle.com/blog/2026-08-20-protocol-aware-dst](https://tigerbeetle.com/blog/2026-08-20-protocol-aware-dst)  
> 23. What's the big deal about Deterministic Simulation Testing?, [https\://notes.eatonphil.com/2024-08-20-deterministic-simulation-testing.html](https://notes.eatonphil.com/2024-08-20-deterministic-simulation-testing.html)  
> 24. Deterministic simulation testing \- how it works and when to use it, [https\://antithesis.com/docs/resources/deterministic\_simulation\_testing/](https://antithesis.com/docs/resources/deterministic_simulation_testing/)  
> 25. Antithesis, [https\://antithesis.com/](https://antithesis.com/)  
> 26. sled simulation guide (jepsen-proof engineering) | sled-rs.github.io, [http\://sled.rs/simulation.html](http://sled.rs/simulation.html)  
> 27. A Tale Of Four Fuzzers \- TigerBeetle, [https\://tigerbeetle.com/blog/2025-11-28-tale-of-four-fuzzers](https://tigerbeetle.com/blog/2025-11-28-tale-of-four-fuzzers)  
> 28. Zero-Downtime Database Migrations: How-To Guide \- SchemaSmith, [https\://schemasmith.com/guides/zero-downtime-database-migrations.html](https://schemasmith.com/guides/zero-downtime-database-migrations.html)  
> 29. Zero-Downtime Schema Migrations: The Expand-Contract Pattern, [https\://talkingschema.ai/blog/zero-downtime-schema-migrations-complete-guide](https://talkingschema.ai/blog/zero-downtime-schema-migrations-complete-guide)  
> 30. Expand and Contract Method for Database Changes | by Jasmin Fluri, [https\://medium.com/@jasminfluri/expand-and-contract-method-for-database-changes-414d236f236f](https://medium.com/@jasminfluri/expand-and-contract-method-for-database-changes-414d236f236f)  
> 31. Zero-downtime schema changes with expand/contract pattern, [https\://koder.ai/blog/zero-downtime-schema-expand-contract](https://koder.ai/blog/zero-downtime-schema-expand-contract)  
> 32. EF Core Migrations Best Practices for Production \- Milan Jovanović, [https\://milanjovanovic.tech/blog/ef-core-migrations-best-practices](https://milanjovanovic.tech/blog/ef-core-migrations-best-practices)  
> 33. How to avoid floating point precision errors with floats or doubles in, [https\://stackoverflow.com/questions/5257166/how-to-avoid-floating-point-precision-errors-with-floats-or-doubles-in-java](https://stackoverflow.com/questions/5257166/how-to-avoid-floating-point-precision-errors-with-floats-or-doubles-in-java)  
> 34. Stop Using Double for Financial System in Java — BigDecimal The, [https\://medium.com/@samrat.alam/stop-using-double-for-financial-system-in-java-bigdecimal-the-right-way-209d58ac673a](https://medium.com/@samrat.alam/stop-using-double-for-financial-system-in-java-bigdecimal-the-right-way-209d58ac673a)  
> 35. Floating-Point Precision in Programming \- DEV Community, [https\://dev.to/dilanblog/understanding-floating-point-precision-in-programming-h7](https://dev.to/dilanblog/understanding-floating-point-precision-in-programming-h7)  
> 36. Claude Code Review 2026: A Developer-First Verdict \- AI Hive, [https\://aihive.global/blog/claude-code-review/](https://aihive.global/blog/claude-code-review/)  
> 37. Generating end-to-end tests with AI and Playwright MCP \- Checkly, [https\://www\.checklyhq.com/blog/generate-end-to-end-tests-with-ai-and-playwright/](https://www.checklyhq.com/blog/generate-end-to-end-tests-with-ai-and-playwright/)  
> 38. Generative AI in Software Testing: Reshaping the QA Landscape, [https\://testrigor.com/generative-ai-in-software-testing/](https://testrigor.com/generative-ai-in-software-testing/)  
> 39. An Empirical Evaluation of Spec-Driven Test Generation \- arXiv, [https\://arxiv.org/pdf/2608.17177](https://arxiv.org/pdf/2608.17177)  
> 40. OPS07-BP02 Ensure a consistent review of operational readiness, [https\://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/ops\_ready\_to\_support\_const\_orr.html](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/ops_ready_to_support_const_orr.html)  
> 41. Improve and Optimize Data Processing Pipelines \- Google SRE, [https\://sre.google/workbook/data-processing/](https://sre.google/workbook/data-processing/)  
> 42. Health & Safety Decision Platform \- OSHA Recordability, Hazards, [https\://decisionledgerai.com/solutions/health-safety](https://decisionledgerai.com/solutions/health-safety)  
> 43. Security Gates for AI-Written Code | Capabilities \- Provectus, [https\://provectus.com/capabilities/security-gates-for-ai-written-code/](https://provectus.com/capabilities/security-gates-for-ai-written-code/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE4AAAAVCAYAAADo49gpAAAC3klEQVR4Xu2XT4hOURjGX6FolDRFNPInkRXyZzIhCymKZCyENNmwsMDUiJoayYKi2JCdZGdhM4qZMmUjbCxQLERiZRZCUeJ5es/bd+75zrlz7/fl+9Lcp359333vv/d97rnvOVekUqVKlSaHZoID4Ca4BFZkdxfSGrA9DLZQzJm5swbWwpqKaD4YFD3vHFiW3Z3WbDACzoNZYDV4BXr9gxLqBgPgGfgDTmd3t0zMlTkzd9bAWlgTa8vTBtHjNoNVYFi0jn4wxTsuKhbLwud4sYPgNZjnxWKicbvATvBdmjPuBNgRBgtoIXgrmrOJtbCm414sFEfkPXAETHWxTvBUtJa1LhaV3eBWEF8PvoHdQTwl3qRZ43guH0JZ0bCwUI6WO2BMdATGxFf0PfgqOtpMZ0VH3SkvVqeV4IvUG2dGXAjiKbXTuGtSbxzFmj6DpUHcNB1cBQ9ETTQxjwnbjhWcMi6Mp9RO45hjyrhYPE/TwF3wG2zN7sqKidLd0KD/xTi+hmMSN6gR49izeQ5nWI7IpNiMW20cE+Kkw9fDhzPh4Uh8rtSad6gOMCpxg8oaxxmY17otet1cpQxKxVMqY1yP6BMNeQ4eRuLsQ4t5YkIpg1LxmPgwb4ArUnD9x8bJBhoaZEZwhimiMsal1MirSnECixnEmj6CriAeykw7I7WRzUkzdzFvPWIYzPDi28Av92viUF4g8YVhO43jkonN3M+VtbAmvy4atMj9mlhLPzjp/puOgr3edlSHwAewxG3zAuw3T6S28u4EL8BPsNHFfJUdoTE1ahxz46J1yIvxs4mjbb8Xuyzaz4fcNuvsAz9Ej6UHxjjY5I5Lik/gOngE9oia9lL088XEkXkfvBF9aqZj4JNoQgZv+li0qZdRo8ZR68A70c+/faKL+ouSHV38MuFb1Ou2bQHs527krf8yovvLRW+6RSaYiv+RmjGO4kzIvsSHz8+wSaMe0aZcqVKljP4CVlisNvQfZ1kAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAL8AAAAVCAYAAAAXbT+OAAAE5klEQVR4Xu1ZW8hWRRTdPxokahG/F7TCLCl8EBVvCBkRFkUYUQlRQU9eEEFUUBQEQXso6MUHg5KihxBD6EkJFLILEQVKDxaUYoUoBtaLRRdM12rP9sy3Pef7xr5hfGgWLP7/2+fMOnvvuc+IVFRUVFRUVFRUVFT8XzAOfAF8E3wNfKD3cV9MA3eIlt0M3t37+F+MgEvAPeBe8ElwTM8bCn6X36cW/aFfHqm+lta6Ddwg+g7zwbx4pOahtFbOPOTUinE7+A44xz8YBhQ9Au4CJ4DzwG/AZ+OXOrACPAzOBSeLavwBPhO9w0raAn4MzgRHwfdEg74leo/f43f5ffpBLfpF/wypvpbWmgF+Da4CbwWfAL8DF0fvpOahtFbOPOTUisF4t4G/gQvcs6GwFfwKvCOyvQh+C06NbB5M5iHwV3B+sN0LngdPgpOCjc5eAB8Mvwm+9yP4ePjN2eJ70e8a6A/9Wh/ZUnwtrTUW3AceDP8bXgE/lGZES8nDzdDKlQcip1YMznC/SObGbx9919kXgZfAp5w9Bhv/B+Bl8OFguws8C56WJlgmm5UST7cTwU9FpzH2aibCB0Y7R7NjoqNDqq+ltazDs+JjcPaLy6bkobRWzjzk1IrB2eAt0VnNlxsKs8GLcr3D/AA/xCT3AzvAqKjzBEedf0RHHI42Njv4imKAx6QZJbhubQuMfrECWZGpvpbWWi4as29kXBJeEa3s1DyU1sqZh5xaBrarTaLLJMbRVu4/wxzrctjb+4Gj/ieiyef/hFVIV0WZnd9pCyy2d/nk7aW1rDF1NTLafbwGby+t5eM1eHtKHnwZg7enaBm4N3lddB+TvfFbIgY53A9TRKdbLneOi25+R8IzVgIro19FzQr/twUWJyTFV9MtqcVKGdTIUvJAe2mtnHnIqUVwucOlzj3hd/bGz93/IIdvBI+Av4M7RXvrVNH1f7+Kug88Ku2BxQlJ8XW8lNfitDyokaXkgfbSWjnzkFNrBNwIroyeZ2/8XY28yz4IE0VnAW6CH5XrK8Tg7XHgMWJ7l0/eXlorZXnh4zV4e2ktH6/B21Py4MsYvD1Fa740yx1D9sZvJwJdDm939hiclnaKbpxGIju1LLnc9B6U7opiR2GH4WaoLTBqcTnFPUSqr6W1eNz4t3Q3Mp6upOahtFbOPOTUWgv+5MgTI/r9s2iMXG4PBUvYIdFTBANPCv4Kfw1s7NOlaeiWxLgSTI/2NcHG5F8UPQ0w8A7gpOjOn+AxGGeL+Ht2qmG+pfpaWutO8AdpYjEw/jjulDyU1sqZh5xabcg+8hMvifasmeE3Gzdv3L6Q5sZtVPSm8E9wabDRCV487JZmepoFnhO91LATH9rOgs+H38Qy0R5sWtT/UnQmMbSVS/W1pFZbOebjfXC/NBdMvhzh83AztHLlgcip5cGZg/vJRf7BMGBC3gA/Ap8WdZYjCK+eDezVh0WvxmcEGwNbJ/ouHePy5wR4SnrLEpxiz4CrwZdFr7ZZ1mYRYmF4h9f2z4kemb4qveu+FF+J0lqsWObngOjG723wM2kGAENKHkpr5cxDTi3DctFOfSWQs8bnkmHZY2DC7hd15CFpd6ILTPBjomU5G4zpfXwN7PFcKpH8vw08DaAWE8dr8Dak+lpai3Ez/hx5KK2VMw85tSoqKioqKioqKobDVZBF2/SxqZGMAAAAAElFTkSuQmCC>