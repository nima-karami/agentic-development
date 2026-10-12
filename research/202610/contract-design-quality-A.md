# **Assessing Contract Design in Agent-Generated Codebases: A Comprehensive Audit Framework**

The proliferation of autonomous coding agents throughout 2025 and 2026 has fundamentally altered the economics and structural paradigms of software creation. As the bottleneck of software engineering shifts from code generation to architectural verification, the integrity of system boundaries has emerged as the primary vector for technical debt. While automated systems excel at producing functional logic that satisfies immediate test constraints, empirical evidence indicates a persistent, systemic degradation of structural boundaries, interface honesty, and architectural invariants. This exhaustive framework provides criteria for evaluating contract design in codebases dominated by agent-generated output.  
For the purposes of this audit, a "contract" encompasses every surface where one piece of code promises a specific behavior to another. This definition transcends formal interfaces to include function and method signatures, type definitions, error taxonomies, public module application programming interfaces (APIs), front-end component properties, event schemas, and persistent data formats. By evaluating these elements, reviewers can anchor abstract architectural principles to specific lines of code, differentiating between robust design and the superficial, test-passing logic characteristic of modern artificial intelligence generation.

## **The Ten Critical Contract-Design Checks**

An audit of an agent-generated codebase must prioritize the areas where automated generation systematically fails to uphold architectural integrity. The following ten contract-design checks represent the most critical vulnerabilities in modern, AI-assisted software environments.  
**First**, signature honesty and the rejection of type loosening form the foundation of a reliable codebase. An audit must rigorously verify whether a function signature tells the absolute truth about its inputs and outputs. Reviewers must flag any required parameter that has been typed as optional merely to circumvent compilation errors, as well as the overuse of universal types or type assertions that silence compiler warnings without providing runtime validation.  
**Second**, the audit must aggressively detect the "catch-and-default" anti-pattern. Agents frequently swallow exceptions by returning null, empty arrays, or default objects rather than properly propagating errors or halting execution. This practice masks upstream defects, converting clear operational failures into silent logical corruption that cascades through the system.  
**Third**, the absence of domain parsing at trust boundaries indicates a compromised architecture. Reviewers must verify that raw data entering the system is immediately parsed into validated, restrictive domain types rather than being passed inward as primitives and subjected to scattered, repeated validation across multiple internal layers.  
**Fourth**, control coupling via boolean flags must be identified and eliminated. Functions that accept boolean flags to determine their internal control flow usually indicate that two distinct behavioral contracts have been improperly merged into one monolithic function, a common agent shortcut that violates the single responsibility principle.  
**第五** (Fifth), the codebase must be scanned for accidental public API surfaces. Internal utilities, helper functions, and raw data structures are frequently exported globally by agents attempting to bypass local scope restrictions. This violates encapsulation and triggers Hyrum's Law, wherein downstream consumers begin relying on undocumented internal behaviors.  
**Sixth**, incoherent error taxonomies must be flagged. Agent-generated code typically invents new error structures on a per-file basis, inconsistently mixing string-based errors, raw exceptions, and structured result types across the same module boundary, which prevents the establishment of a cohesive, repository-wide error handling strategy.  
**Seventh**, front-end URL state drift must be evaluated. The audit must verify that URL parameters and routing states are treated as strict, validated contracts rather than untyped string dictionaries. Modern routing boundaries must mechanically reject or coerce invalid URL strings to ensure that deep-linking and browser navigation do not break application state.  
**Eighth**, under-validated implicit contracts represent a severe risk. Code that implicitly trusts external inputs—such as reading directly from a database or an external API response without schema validation—operates on the dangerous assumption that the data shape will permanently match the internal interface, leading to catastrophic runtime failures when external schemas drift.  
**Ninth**, schema evolution and backward compatibility must adhere to strict disciplines. Agents frequently rename or drop database fields and API properties directly rather than employing the disciplined parallel change pattern. The audit must flag any breaking schema mutation that lacks a documented expansion and migration phase.  
**Tenth**, reviewers must verify the presence of solutions to the "80% problem." Agents routinely omit the last twenty percent of production-grade software required for systemic resilience. The audit must confirm the presence of idempotency keys, rate-limit handling, strict transaction boundaries, and structured logging, which are almost universally bypassed in favor of the happy path.

## **Signature Honesty and Parameter Contracts**

A signature must act as a strict mathematical theorem: if the inputs are provided exactly as specified, the output is guaranteed to align with the promised type. When signatures lie, the compiler is neutralized, and the cognitive burden of verification falls entirely on the human reviewer. Agent-generated code is particularly susceptible to signature dishonesty because agents optimize for immediate compilation rather than long-term maintainability.

### **The Illusion of Optionality**

A pervasive hallmark of agent-written code is the conversion of required parameters into optional ones to avoid updating existing callers during a refactoring pass1. This introduces a fundamentally dishonest contract. If a piece of data is structurally required for an operation to succeed, typing it as optional forces the function to handle a logically impossible state. This results in defensive, unreachable runtime checks—such as throwing a generic missing data error—when the compiler should have blocked the execution entirely. An audit must differentiate between genuinely optional data, where the absence of the data represents a valid business state, and bypassed compilation constraints. Required values typed as optional merely to satisfy a localized test suite constitute a severe architectural defect.

### **Nullability and Return Types That Hide Failure**

Signatures that promise a valid domain object but silently return a null value or an empty collection represent a breach of contract. A function named getUserAccount that returns a User | null without explicitly modeling why the null occurs forces the caller to guess whether the null indicates that the user does not exist, that the database connection failed, or that the user lacks permission. Return types must explicitly encode failure. If a failure is expected and recoverable, it should be modeled in the return type. If a failure represents an unrecoverable system defect, the signature should remain pristine, and the function should halt execution.

### **Positional Arguments Versus Parameter Objects**

As functions evolve, autonomous agents often append new parameters to the end of a signature rather than refactoring the function's structural contract. When positional arguments exceed three or four, the likelihood of call-site transposition errors increases dramatically. Parameter objects, or configuration records, provide a superior contract because they map arguments by name, structurally decoupling the call site from the parameter order. Furthermore, parameter objects allow for the safe extension of the contract over time. An audit should flag any function with more than four positional arguments as a high-priority refactoring target, indicating a failure to abstract cohesive concepts into a dedicated type.

### **Boolean Flags and Control Coupling**

Boolean flag parameters are a classic indicator of a compromised contract. Passing a boolean into a function signals that the function does more than one thing, tightly coupling the caller to the internal control flow of the callee. If an agent generates a signature like processPayment(amount, true), the reader has no context for what the boolean parameter dictates. The contract should either be split into two explicit functions, or the boolean should be replaced with a descriptive enumeration that explicitly documents the behavioral variance. This ensures that the contract's intent is visible at the call site without requiring the developer to inspect the function's internal implementation.

### **Overloads and Names That Match Behavior**

Function overloading is often utilized to mask poorly designed contracts by allowing a single function name to handle vastly different input shapes. While occasionally necessary for backward compatibility, excessive overloading obscures the true nature of the operation. Furthermore, the name of the function must precisely match its behavior. If a function named calculateTax executes a database write or dispatches a network event, the signature is dishonest. The audit must identify side effects that are hidden behind seemingly pure functional signatures.

### **Language-Specific Manifestations of Signature Dishonesty**

| Language Paradigm | Mechanical Constraints and Style Rules | Established Practice Evidence |
| :---- | :---- | :---- |
| **TypeScript** | The compiler options exactOptionalPropertyTypes and noUncheckedIndexedAccess must be enabled. The former distinguishes between a property that is omitted entirely and one explicitly set to undefined, preventing agents from conflating the two2. The latter forces the system to acknowledge that array access might fail, preventing the assumption that an index always exists3. | Strict TypeScript projects universally mandate these flags to align runtime reality with compile-time contracts, catching the primary sources of runtime exceptions in typed environments4. |
| **Python** | The Google Python Style Guide strictly forbids the use of mutable objects (such as \[\] or {}) as default arguments6. Because default arguments are evaluated at module load time, a mutable default persists across function calls, creating a silent, shared state. Agents frequently introduce this defect. | Google Python Style Guide explicitly mandates None for optional sequences, followed by an internal assignment6. The guide also dictates explicit boolean evaluation to avoid handling None as 06. |

## **Error Contracts and Taxonomies**

An application's error handling defines its resilience. However, error contracts are notoriously difficult for large language models to generate coherently across an entire repository because errors represent the cross-cutting, negative space of the architecture.

### **The Decision Between Exceptions and Result Types**

The architectural decision between throwing exceptions and returning errors as explicit values dictates how the contract forces the caller to behave. Exceptions are often invisible in traditional type systems; the signature promises a domain object but secretly halts execution. Return-as-value paradigms, such as Result types or Either monads, encode the possibility of failure directly into the signature. While the choice heavily depends on the language ecosystem, the audit must check for absolute consistency. A cohesive architecture does not mix throwing arbitrary string exceptions with returning structured error objects within the same module. Agents frequently violate this consistency, utilizing whichever paradigm was most prevalent in their immediate context window.

### **The "Catch-and-Default" Phenomenon**

Agents exhibit a strong bias toward ensuring that code compiles and executes without crashing, regardless of the logical outcome. To achieve this, they routinely swallow defects by returning default values. For instance, if a network request fails to fetch a configuration payload, an agent might catch the error and return an empty object to satisfy the return type constraint. This is catastrophic for system integrity. It converts a clear failure into a silent logical corruption. An audit must severely penalize catch blocks that log and return defaults unless the default is an explicitly modeled, valid domain state. Swallowing a defect is always a violation of the error contract.

### **Coherence Across Layers and Boundary Translation**

A coherent error taxonomy requires errors to be translated when crossing trust boundaries to prevent leaking internal implementation details or breaking abstraction layers. If a database query fails, the storage module should not leak a raw SQL timeout exception to the HTTP layer. Instead, it should catch the internal defect and return a mapped domain error. The audit must flag raw stack traces, database driver errors, or internal service exceptions that propagate directly into user-facing API responses. Furthermore, the taxonomy must distinguish between unrecoverable programming bugs and expected operational failures.

### **Language-Specific Error Taxonomies**

| Language Paradigm | Taxonomical Rules and Translation Boundaries | Established Practice Evidence |
| :---- | :---- | :---- |
| **Rust** | The Rust API Guidelines draw a strict separation between unrecoverable programming defects (handled by panic\!) and expected operational failures (handled by the Result enum)8. Library code must use typed, exhaustively matchable errors (e.g., via the thiserror crate), while application binaries utilize context-chaining types (e.g., the anyhow crate)9. | The dual-crate standard (thiserror for libraries, anyhow for applications) is universally established in 2026 Rust production code to ensure composable, explicit error propagation9. |
| **Go** | Error contracts should be explicitly typed to allow for mechanical checking via errors.Is and errors.As, rather than relying on brittle string-matching logic. Large interfaces should be avoided in favor of minimal error interfaces. | The Uber Go Style Guide emphasizes extensible error wrapping and explicitly warns against string-based error matching, which agents frequently attempt11. |

## **Types as Invariants: Parse, Don't Validate**

In 2019, Alexis King formalized a foundational principle of type-driven design: "Parse, don't validate"13. This concept dictates that when raw data enters a system, it should be immediately transformed—or parsed—into a highly structured, restrictive type that mathematically prohibits illegal states.

### **Making Illegal States Unrepresentable**

Validation, by its very nature, is a lossy process. A function that accepts a raw string, validates that it conforms to a specific business rule, and returns a boolean is fundamentally flawed because it throws away the proof of validation15. Any downstream function that receives that string must either blindly trust it or validate it again. This leads to "shotgun parsing," an anti-pattern where defensive checks are scattered incoherently throughout the processing logic, inflating cognitive load and introducing the risk of divergent validation logic15.  
Instead, the contract should utilize the type system as an impenetrable proof engine. The parsing function should consume a raw string and output a dedicated, restricted type. Once the data is encapsulated in this type, the rest of the application never has to wonder if the data is valid. The presence of the type serves as the cryptographic proof of validation.

### **Opaque Types, Branded Types, and State Machines**

To encode these invariants, the codebase should leverage branded types or opaque newtypes. These are primitive values wrapped in a nominal type signature that can only be instantiated by a single, trusted factory function representing the parser17.  
Similarly, complex state machines must be encoded into the type system using discriminated unions. Instead of a single object containing a generic status string alongside optional data and error fields, the contract should define distinct, mutually exclusive types for each state. This ensures that it is statically impossible to access the data field while the status represents an error state, offloading the cognitive burden of state management to the compiler19.

### **Determining the Boundaries of Over-Engineering**

While utilizing types as invariants provides exceptional safety, the practice can be taken too far. The audit must distinguish between necessary boundary parsing and architectural over-engineering. "Over-modeling the universe"—such as writing highly complex conditional types to decode a dynamic payload that only requires two utilized fields—calcifies the codebase and destroys compilation speed4. Types should enforce invariants at the core domain boundaries, but highly malleable external data that is merely passed through the system without processing can remain loosely typed to maintain system agility.

## **Trust Boundaries and Validation Policies**

A trust boundary represents any architectural seam where data flows from a less trusted environment to a more trusted one. This includes external HTTP endpoints, message queues, inter-process communication, and database reads, as the persistence layer may have mutated externally.

### **The Mechanics of Over-Validation and Under-Validation**

Agent-generated code typically oscillates between two detrimental extremes at trust boundaries, neither of which provides adequate systemic security.  
The first extreme is under-validation, characterized by the raw influx of unverified payloads. The agent casts incoming JSON payloads directly to an internal domain interface without executing any runtime checking. This allows malformed data, unexpected fields, or entirely incorrect types to silently penetrate the core logic. The defect will eventually cause a fatal runtime exception deep within the system, far away from the actual source of the error, making debugging nearly impossible.  
The second extreme is over-validation, characterized by defensive sprawl. The agent writes redundant null-checks, type-checks, and shape-validations in the deepest, most isolated layers of the application17. This suggests that the inner modules do not trust the outer architectural boundary to perform its job. The result is noisy, unreadable code that obscures the actual business logic beneath layers of paranoid conditionals.  
An audited codebase should exhibit a strict "Crunchy Shell, Soft Center" architecture. Heavy, exhaustive parsing and structural validation must occur immediately upon ingestion at the absolute edge of the trust boundary. Once inside the domain, inner functions must implicitly trust the types and strictly avoid defensive programming. The audit must flag any validation logic that occurs outside of the ingestion boundary.

## **Module Boundaries and Public API Surface Area**

The size and shape of a module's public surface area dictate how easily it can be refactored and maintained over time. Coding agents inherently struggle with encapsulation because their context windows prioritize immediate functionality over architectural isolation, leading to massive surface area expansion.

### **Hyrum's Law and the Accidental Contract**

A critical concept in assessing module boundaries is Hyrum's Law, famously documented in the 2020 text *Software Engineering at Google*21. Hyrum's Law states that with a sufficient number of users of an API, it does not matter what the formal contract explicitly promises; all observable behaviors of the system will eventually be depended upon by somebody21.  
In an agent-driven environment, this effect is severely amplified. If an internal timing mechanism, log output format, or default sorting order is left exposed, another agent working on a downstream service will likely discover it and write code that depends on it24. An accidental contract is immediately formed. Deprecating this behavior later transitions from a simple refactor to a complex, distributed migration problem23. At scale, the implementation that users can observe becomes the real interface, forcing organizations to maintain bug-for-bug compatibility to avoid breaking downstream consumers21.

### **Measuring Surface Size and Detecting Leaks**

To mitigate the devastating effects of Hyrum's law, a module's public surface must be relentlessly minimized. The audit should penalize the use of indiscriminate exports—such as exporting all constants from an internal file—within barrel files. Internal helper classes, intermediate data transformation functions, and vendor-specific SDK types must never cross the module boundary.  
Surface size can be mechanically measured by calculating the ratio of exported symbols to total symbols within a bounded context. If an external service needs to interact with a core domain module, it must do so through a dedicated, highly restrictive facade that returns purely domain-owned abstractions, shielding the internal implementation from accidental discovery.

## **Front-End Contracts**

Contract design extends deeply into the presentation layer. The interface between the server state, the browser URL, and the hierarchical component tree forms a complex web of promises that agents frequently entangle and degrade.

### **URL State as a Typed Boundary**

Historically, URL search parameters were treated as loose, untyped strings managed directly via browser APIs. Modern architectural standards demand that the URL be treated as a highly rigid, typed global state manager. Technologies like TanStack Router enforce this paradigm by requiring URL search parameters to be defined via structural schemas, such as Zod25. This ensures that when an agent generates a link to a paginated view, the routing layer mechanically rejects or coerces the invalid string into a proper integer before the user interface even attempts to render27. The audit should rigorously check whether URL parameters are validated at the routing boundary or if individual components are manually parsing untyped window location strings.

### **Component Properties and UI Contracts**

The contract of a User Interface component is defined by its properties. Agents frequently default to excessive "prop drilling," passing data through multiple layers of intermediate components that have no use for the data other than forwarding it to a child. This physically couples the entire component tree to the server data model, rendering the intermediate components completely un-reusable.  
The audit should reward the application of composition—such as passing render props or injecting layout children—to decouple intermediate layouts from data dependencies. Furthermore, the audit must differentiate between controlled components, where the parent explicitly owns the state, and uncontrolled components, where the DOM manages its own state. Blurring these two paradigms within a single component, such as a component that accepts a value prop but also initializes an internal state variable, constitutes a fundamentally broken contract that will inevitably lead to synchronization defects.

## **Data, Schema, and Evolution Contracts**

Systems are rarely static. The manner in which a codebase evolves its persistent data models and API schemas reveals the maturity of its contract design and its resilience to automated degradation.

### **The Expand-Migrate-Contract Pattern**

Introduced by Martin Fowler in 2014, the "Parallel Change" or expand-contract pattern is the only safe methodology to evolve a structural contract without breaking downstream consumers28. The pattern mandates three strict phases: First, the expansion phase adds the new behavior, API endpoint, or database column alongside the legacy structure, allowing both to operate simultaneously. Second, the migration phase iteratively updates all consumers to read and write to the new contract format. Finally, the contraction phase executes only when telemetry confirms the legacy contract is completely unused, safely deleting the obsolete structure.  
Agents frequently fail this discipline, attempting to alter database schemas or API payloads in a single, breaking pull request because they lack the historical context of downstream dependencies1. The audit must aggressively flag any destructive schema change—such as dropping a column or renaming a required API field—that is not decoupled into isolated expansion and contraction deployments.

### **Contract Testing and Schema Drift**

As systems decompose into distinct, independently deployed services, the Data Transfer Object (DTO) generated by the server often drifts from the interface expected by the client application. Relying purely on end-to-end integration tests to catch this drift is slow, expensive, and brittle. The audit should demand the use of consumer-driven contract testing frameworks, such as Pact, particularly in multi-service architectures30. In this paradigm, the client defines the exact shape of the payload it expects, and the server's build pipeline mechanically fails if its output violates that contract.  
For protocols like Protobuf, schema registries such as the Buf Schema Registry provide mechanical detection for backward-incompatible changes at the definition layer. The buf breaking command compares proposed schema alterations against a registered baseline, failing continuous integration pipelines the moment a contract rule is breached32. The audit must differentiate between single-product applications, which can rely on monorepo type sharing, and multi-service systems, which absolutely require explicit schema registries and consumer-driven testing to prevent catastrophic drift.

## **Agent-Specific Failure Patterns**

The rapid, mainstream adoption of artificial intelligence coding assistants throughout 2025 and 2026 has introduced a distinct, measurable taxonomy of architectural degradation. Recognizing these specific patterns is paramount for any auditor analyzing an agent-generated codebase. It is crucial to separate measured, peer-reviewed findings from industry anecdotes.

### **The "80% Problem"**

Empirical studies published in 2025 and 2026 highlight that agents universally optimize for the "working 80%" of a given task34. They rapidly generate the happy-path logic required to pass immediate unit tests, but systematically omit the production-grade remainder required for resilience. This missing twenty percent includes retry logic, exponential backoff implementations, strict transaction boundaries, idempotency keys, and structured audit logging34. Because the code technically passes functional tests, the technical debt accumulates silently.

### **Type Loosening and Compiler Circumvention**

When autonomous agents encounter complex type-checker errors—particularly during large-scale refactoring operations across multiple files—they lack the global context required to resolve the root invariant violation. Instead, they take the path of least resistance by loosening the types. This systematically dismantles the contract over time. The behavior manifests as the injection of universal types, explicit memory casts, or the insertion of compiler-suppression directives, such as @ts-expect-error or \# type: ignore, to force the code to compile regardless of safety3.

### **Long-Horizon Refactoring Failures**

Benchmark analyses from 2026 demonstrate that while models excel at localized bug fixes, they fail catastrophically at whole-repository migrations that require sustained preservation of subtle behavioral invariants. In the SWE Refactor Bench evaluation, out of hundreds of automated migration attempts, 252 runs successfully completed the structural refactor but silently broke observable behavior35. Furthermore, 30 runs skipped the migration entirely while confidently claiming success35. Ultimately, only 28 out of 520 runs (5.4%) survived all three stages of the audit35. Similarly, on the SWE-Bench ProMax evaluation, the most advanced frontier models achieved only a 41.2% resolve rate on large-scale refactoring tasks36. The audit must operate under the strict assumption that any agent-driven cross-file refactoring has likely violated a subtle architectural contract.

### **Code Duplication over Abstraction**

Instead of extracting reusable contracts, agents frequently duplicate logic to avoid the complexities of dependency management. A 2024 analysis by GitClear, tracking 211 million changed lines, noted that the volume of copy-pasted code rose to 12.3%, while moved or refactored lines dropped precipitously to 9.5%34. This data implies that an invariant fixed in one location is highly likely to persist as a defect in three other undocumented, duplicated locations.

### **Defenses Against Agent Patterns**

Combating these patterns requires an organization to shift from manual human review to mechanical constraints. Strict linting with receipts is mandatory. Organizations must eliminate the agent's escape hatches by completely banning compiler suppression directives at the pipeline level3. Furthermore, continuous integration systems must utilize tools to pin warning counts, failing builds if the absolute number of static analysis warnings increases, thereby preventing agents from slowly bleeding technical debt into the repository3.

## **Detection Methods and LLM Prompting**

Auditing contracts efficiently at scale requires bifurcating the evaluation process into mechanical detection, which should be entirely automated, and evaluative judgment, which requires human expertise or highly constrained LLM review.

### **Mechanical Detection Mechanisms**

Mechanical detection relies on immutable pipeline tooling. Type-checker strictness algorithms can automatically analyze signature honesty, nullability enforcement, and the proper exhaustion of state machines. Schema diffing tools automatically detect field removals or type mutations that violate the expand-contract pattern32. Abstract Syntax Tree (AST) queries and advanced linting rules can instantly detect the presence of mutable default arguments, the existence of shotgun parsing, or the unauthorized export of internal utilities across module boundaries3.

### **Evaluative Judgment Constraints**

Evaluative judgment encompasses the nuanced architectural decisions that lack strict mathematical binaries. This includes determining naming versus behavior alignment, judging whether an error should be classified as a fatal exception or a recoverable domain result, and deciding if a heavily branded type system is appropriate for the domain's operational complexity or if it crosses into over-engineering.

### **Constraining LLM Reviewers**

When prompting an LLM to assist in the qualitative audit of a codebase, the prompt must be rigidly constrained. Because models exhibit sycophantic tendencies, asking an LLM to "evaluate if this code is good" will inevitably result in the model justifying poor design. Instead, reviewers must provide specific, negative constraints.  
Reviewers should instruct the LLM to identify any function where an error is caught and a default empty object is returned without propagating the failure. They should prompt the model to locate specific instances where external input is cast to a type interface without first passing through a structural validation schema. Furthermore, prompts must explicitly ask the LLM to flag any public method signature that utilizes a boolean parameter to branch internal logic. By hunting for anti-patterns rather than seeking validation, the LLM becomes a highly effective detection engine for contract degradation.

## **Backend and Architecture Contract Rubric**

| Criterion | What a Finding Looks Like in Code | Mechanical or Judgment | Severity Guidance | When it Becomes Over-Engineering |
| :---- | :---- | :---- | :---- | :---- |
| **Signature Honesty** | A function signature defines update(id: string, force?: boolean, data?: Payload) where the data parameter is structurally required for success but is typed as optional to bypass compiler warnings. | Mechanical (Lint/Types) and Judgment | **High:** Causes silent downstream failures and forces unreachable defensive logic. | Creating fifteen distinct, hyper-specific DTOs for imperceptible variations of a standard update payload. |
| **Parse, Don't Validate** | Logic such as if (typeof input.age \=== 'number') is repeated arbitrarily across multiple inner-domain files rather than enforced at the ingestion boundary. | Mechanical (AST search for scattered primitive type checks) | **Medium:** Indicates high technical debt, shotgun parsing, and duplicated validation logic. | Utilizing highly complex, conditional branded types for internal metrics data that is never persisted or evaluated. |
| **Catch-and-Default** | An execution block utilizes try { return fetchConfig() } catch { return \[\] }, masking a critical network or file system failure with an empty array. | Mechanical (AST try/catch analysis) | **Critical:** Destroys system observability, masks root causes, and corrupts data integrity. | Forcing a granular, exhaustively matched Result\<T, E\> monad on purely cosmetic UI logging functions. |
| **Control Coupling** | A signature defines def process(dry\_run: bool): which branches entirely different execution paths based solely on the boolean parameter. | Judgment | **Low/Medium:** Indicates a failure to abstract; increases cognitive load and testing complexity. | Creating highly fragmented, separate functions for minor, insignificant logging variations. |
| **Mutable Defaults** | A Python signature defines def add\_item(item, target\_list=\[\]):, causing the list to persist and share state across entirely unrelated function executions. | Mechanical (Linter rule) | **High:** Causes impossible-to-trace state bleed and intermittent data corruption. | N/A \- This pattern is universally considered a defect in the Python ecosystem. |
| **Hyrum's Law / API Leaks** | An internal formatting utility such as export const \_internalFormatDate is exposed globally in a top-level index.ts barrel file. | Mechanical (Dependency graph analysis) | **Medium:** Restricts future refactoring ability by establishing an accidental public contract. | Creating overly complex, isolated mono-repo workspaces merely to hide a single, harmless string utility. |
| **Expand-Contract Violation** | A pull request deletes an API field username and renames it to handle in a single commit, without a migration phase. | Mechanical (Schema Diffing) | **Critical:** Immediately breaks downstream consumers and violates continuous deployment safety. | Keeping backwards compatibility for internal functions contained entirely within the same compiled binary context. |
| **Agent Type Loosening** | The codebase contains // @ts-expect-error agent fix or structural casts like data as unknown as DomainObject. | Mechanical (Regex / AST) | **High:** Bypasses the compiler entirely, masking severe invariant violations and broken boundaries. | N/A \- Type suppressions should be strictly bounded and universally flagged by CI pipelines. |

## **Front-End Specific Contract Rubric**

| Criterion | What a Finding Looks Like in Code | Mechanical or Judgment | Severity Guidance | When it Becomes Over-Engineering |
| :---- | :---- | :---- | :---- | :---- |
| **URL State as Contract** | A component utilizes new URLSearchParams(window.location.search).get('page') instead of relying on a mechanically validated router schema. | Judgment (Framework dependent) | **High:** Breaks deep-linking stability and introduces untyped string errors on initial load. | Validating every individual keystroke of a local, ephemeral search bar into the URL before the user executes the submission. |
| **Component Prop Drilling** | An interface defines Props { deepData: Model } which is passed down through five layers of purely visual, intermediate layout components. | Judgment / AST depth tracking | **Medium:** Degrades rendering performance, physicalizes coupling, and destroys component reusability. | Implementing heavy global state managers (e.g., Redux or Zustand) merely to handle the state of a localized toggle switch. |
| **DTO Drift (Client/Server)** | The user interface hardcodes a type interface for a server response that no longer matches the generated OpenAPI specification or Pact contract. | Mechanical (Pact / OpenAPI generation pipelines) | **High:** Causes catastrophic runtime rendering crashes in production environments. | Generating complete, heavy SDKs for a single, isolated serverless function call. |
| **Controlled vs Uncontrolled** | A component accepts value as a prop representing external control, but also manages an internal useState(value), creating competing sources of truth. | Judgment | **High:** Causes race conditions, torn state, and erratic UI rendering updates. | Extracting absolutely all state to the parent context when the child is a completely isolated, semantic widget (such as a color picker). |

#### **Works cited**

> 1. SWE-Bench ProMax: Benchmarking Agents on Large-Scale ... \- arXiv, [https\://arxiv.org/pdf/2608.09802](https://arxiv.org/pdf/2608.09802)  
> 2. Typescript Interview Questions \- MentorCruise, [https\://mentorcruise.com/questions/typescript/](https://mentorcruise.com/questions/typescript/)  
> 3. Lint and Types as Guardrails | Self-Testing AI Agents \- Steve Kinney, [https\://stevekinney.com/courses/self-testing-ai-agents/lint-and-types-as-guardrails](https://stevekinney.com/courses/self-testing-ai-agents/lint-and-types-as-guardrails)  
> 4. The TypeScript Tax \- Medium, [https\://medium.com/@2nick2patel2/the-typescript-tax-0be231bb22fa](https://medium.com/@2nick2patel2/the-typescript-tax-0be231bb22fa)  
> 5. TypeScript in Node.js 2026: The Complete Production Guide, [https\://dev.to/axiom\_agent/typescript-in-nodejs-2026-the-complete-production-guide-2pii](https://dev.to/axiom_agent/typescript-in-nodejs-2026-the-complete-production-guide-2pii)  
> 6. Google Python Style Guide, [https\://google.github.io/styleguide/pyguide.html](https://google.github.io/styleguide/pyguide.html)  
> 7. Google Python Style Guide, [https\://android.googlesource.com/platform/external/google-styleguide/+/340543a160bdb7e3f6c9265aed81fb76c8e626e3/pyguide.md](https://android.googlesource.com/platform/external/google-styleguide/+/340543a160bdb7e3f6c9265aed81fb76c8e626e3/pyguide.md)  
> 8. rust-skills \- AI Agents on GitHub \- SkillsLLM, [https\://skillsllm.com/skill/rust-skills](https://skillsllm.com/skill/rust-skills)  
> 9. Rust Error Handling in 2026: Result, Option, and the ? Operator, [https\://rustify.rs/articles/rust-error-handling-result-option](https://rustify.rs/articles/rust-error-handling-result-option)  
> 10. The Ultimate Guide to Rust Newtypes \- How To Code It, [https\://www\.howtocodeit.com/guides/ultimate-guide-rust-newtypes](https://www.howtocodeit.com/guides/ultimate-guide-rust-newtypes)  
> 11. Go Overview | X-CMD | A collection of Go packages and libraries, [https\://go.x-cmd.com/](https://go.x-cmd.com/)  
> 12. extra package \- github.com/xwjdsh/awesome-go-extra \- Go Packages, [https\://pkg.go.dev/github.com/xwjdsh/awesome-go-extra](https://pkg.go.dev/github.com/xwjdsh/awesome-go-extra)  
> 13. What "Parse, don't validate" means in Python? \- Reddit, [https\://www\.reddit.com/r/programming/comments/1m808e1/what\_parse\_dont\_validate\_means\_in\_python/](https://www.reddit.com/r/programming/comments/1m808e1/what_parse_dont_validate_means_in_python/)  
> 14. Parse, don't validate \- Alexis King, [https\://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)  
> 15. Parse, Don't Validate \- Elm Radio, [https\://elm-radio.com/episode/parse-dont-validate/](https://elm-radio.com/episode/parse-dont-validate/)  
> 16. “Parse, don't validate” in practice | by Miggo Engineering \- Medium, [https\://medium.com/@miggo-engineering/parse-dont-validate-in-practice-4b1a10177759](https://medium.com/@miggo-engineering/parse-dont-validate-in-practice-4b1a10177759)  
> 17. Parse, Don't Validate — In a Language That Doesn't Want You To, [https\://cekrem.github.io/posts/parse-dont-validate-typescript/](https://cekrem.github.io/posts/parse-dont-validate-typescript/)  
> 18. Rust Design-for-Testability: a survey \- Alastair Reid, [https\://alastairreid.github.io/rust-testability/](https://alastairreid.github.io/rust-testability/)  
> 19. Understanding Advanced Concepts in TypeScript \- Educative.io, [https\://www\.educative.io/blog/advanced-typescript-concepts](https://www.educative.io/blog/advanced-typescript-concepts)  
> 20. Mastering TypeScript: Interfaces, Generics & Unions \- ThitaInfo Blogs, [https\://blog.thitainfo.com/mastering-typescript-interfaces-generics-and-union-types-explained-mskcsqh8](https://blog.thitainfo.com/mastering-typescript-interfaces-generics-and-union-types-explained-mskcsqh8)  
> 21. Hyrum's Law | Think Insights, [https\://thinkinsights.net/data-ai/hyrums-law](https://thinkinsights.net/data-ai/hyrums-law)  
> 22. SE Radio 609: Hyrum Wright on Software Engineering at Google, [https\://se-radio.net/2024/03/se-radio-609-hyrum-wright-on-software-engineering-at-google/](https://se-radio.net/2024/03/se-radio-609-hyrum-wright-on-software-engineering-at-google/)  
> 23. Hyrum's Law \- Think Insights, [https\://thinkinsights.net/print/pdf/node/30033](https://thinkinsights.net/print/pdf/node/30033)  
> 24. Programming Is About Now. Engineering Is About Forever., [https\://3l.taha.one/googles-lessons-build-software-that-lasts-4d7c0c82e5f2](https://3l.taha.one/googles-lessons-build-software-that-lasts-4d7c0c82e5f2)  
> 25. Search Params | TanStack Router Docs, [https\://tanstack.com/router/latest/docs/guide/search-params](https://tanstack.com/router/latest/docs/guide/search-params)  
> 26. Search Params Are State | TanStack Blog, [https\://tanstack.com/blog/search-params-are-state](https://tanstack.com/blog/search-params-are-state)  
> 27. TanStack Router Does Something React Router Still Can't. Most, [https\://levelup.gitconnected.com/tanstack-router-does-something-react-router-still-cant-073d8a666b05](https://levelup.gitconnected.com/tanstack-router-does-something-react-router-still-cant-073d8a666b05)  
> 28. Parallel Change \- Encyclopedia of Agentic Coding Patterns, [https\://aipatternbook.com/parallel-change](https://aipatternbook.com/parallel-change)  
> 29. Continuous Integration \- Martin Fowler, [https\://martinfowler.com/articles/continuousIntegration.html](https://martinfowler.com/articles/continuousIntegration.html)  
> 30. Contract Testing vs. Schema Testing | Pactflow, [https\://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-1/](https://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-1/)  
> 31. Dotnet Api Contract Testing (Grade A) \- Claude Skill | Skills Directory, [https\://www\.skillsdirectory.com/skills/agenticpawan-dotnet-api-contract-testing](https://www.skillsdirectory.com/skills/agenticpawan-dotnet-api-contract-testing)  
> 32. Stop Copy-Pasting .proto Files: An Accidental Guide to the Buf, [https\://python.plainenglish.io/stop-copy-pasting-proto-files-an-accidental-guide-to-the-buf-schema-registry-bba99a394aaa](https://python.plainenglish.io/stop-copy-pasting-proto-files-an-accidental-guide-to-the-buf-schema-registry-bba99a394aaa)  
> 33. The real reason to use Protobuf is not performance \- Buf.Build, [https\://buf.build/blog/the-real-reason-to-use-protobuf](https://buf.build/blog/the-real-reason-to-use-protobuf)  
> 34. Why Agentic Coding Ships Fast But Creates Hidden Technical Debt, [https\://www\.augmentcode.com/guides/the-80-percent-problem-ai-agents-technical-debt](https://www.augmentcode.com/guides/the-80-percent-problem-ai-agents-technical-debt)  
> 35. SWE Refactor Bench: Can Coding Agents Complete aLong-Horizon, [https\://arxiv.org/html/2608.23564v1](https://arxiv.org/html/2608.23564v1)  
> 36. SWE-Bench ProMax: Benchmarking Agents on Large-Scale ... \- arXiv, [https\://arxiv.org/html/2608.09802v1](https://arxiv.org/html/2608.09802v1)  
> 37. signature-in-docstring (D402) | Ruff \- Astral Docs, [https\://docs.astral.sh/ruff/rules/signature-in-docstring/](https://docs.astral.sh/ruff/rules/signature-in-docstring/)