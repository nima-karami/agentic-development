# Software Engineering Best Practices for Human and AI-Agent Codebases

## Core conclusions

A codebase that works well for both humans and AI coding agents is not merely “clean.” It is **explicit, modular, typed, searchable, test-backed, convention-driven, and operationally reproducible**. The strongest evidence comes from repository-level benchmarks and agent evaluations: modern agents still struggle with **repository-wide comprehension**, **cross-file dependency retrieval**, and **issue reproduction**, while their performance improves when the codebase makes boundaries, dependencies, and verification signals easy to find and execute. RepoBench and RepoCoder show that repository-level tasks differ materially from single-file completion and depend on retrieving the right cross-file context; RepoGraph shows that explicit repository structure and dependency graphs improve agent performance; Rust-SWE-bench highlights repository-wide comprehension and issue reproduction as major bottlenecks; LongCodeBench shows that even million-token context windows do not remove long-context weakness. citeturn25view0turn25view3turn25view4turn24view3turn24view0turn26search0turn27view2

The major twist in 2025–2026 is that **documentation for agents helps only when it is concise, accurate, and operationally useful**. OpenAI, GitHub, and Anthropic all support repository instruction files such as `AGENTS.md`, `copilot-instructions.md`, and `CLAUDE.md`, and recommend layering contextual guidance close to the code being edited. But the best current independent evidence is mixed: the 2026 AGENTS.md evaluation found that **LLM-generated context files tended to reduce success rates and increase inference cost**, while **developer-written context files helped only marginally**, suggesting that verbose or requirement-heavy context files often become noise rather than guidance. OpenAI’s own Codex guidance explicitly recommends short, practical files; Anthropic’s docs say shorter files produce better adherence; GitHub supports repo-wide and path-specific instructions rather than one giant global memo. This is an **emerging and contested** area, not settled consensus. citeturn21view0turn22view0turn22view1turn22view2turn22view3

The stable, older consensus still holds: information hiding, deep modules, low coupling, high cohesion, explicit dependencies, meaningful names, small comprehensible units, clear interfaces, fast and reliable tests, and lightweight decision records all reduce maintenance cost. Parnas argued for information hiding and black-box specifications decades ago; Ousterhout emphasizes deep modules and simple interfaces; Fowler’s work on dependency injection, gateways, repositories, and ADRs remains directly relevant; Google’s engineering guidance continues to stress code health, test quality, and consistency over short-term convenience. The AI era does not replace these ideas. It increases their payoff. citeturn18search9turn18search1turn18search5turn31view0turn29search22turn29search2turn33search4turn17search11turn14search5

**Evidence tags used below**

**Established consensus** means long-standing practice supported by classic engineering literature, mainstream platform guidance, or multiple independent sources.  
**Emerging or contested** means the practice is actively recommended by vendors or early papers, but the empirical picture in 2025–2026 is still mixed or benchmark-sensitive. citeturn18search9turn18search5turn21view0turn22view1

## Structural and architectural patterns

**High cohesion, low coupling, and information hiding.**  
**What it is:** group code that changes together; hide implementation details behind small, stable interfaces.  
**Why it helps humans:** fewer ripple effects, lower cognitive load, clearer ownership, safer refactors.  
**Why it helps AI agents:** reduces the search surface and narrows the set of files that matter for a task.  
**Heuristic:** every module should have one dominant reason to change; if a change routinely touches three or more unrelated modules, the boundary is probably wrong. Prefer “deep” modules with simple public APIs over shallow wrappers that expose many moving parts.  
**Example:** expose `InvoicePolicy.calculate(invoice)` rather than leaking discount tables, tax rules, and rounding internals into callers.  
**Status:** **Established consensus.** Parnas ties maintainability to information-hiding modules and precise black-box specifications; Ousterhout argues for deep modules with simple interfaces and fewer dependencies. citeturn18search9turn18search1turn18search3turn18search5

**Constructor dependency injection over hidden service lookup.**  
**What it is:** pass required dependencies explicitly rather than resolving them from globals, ambient context, or service locators.  
**Why it helps humans:** dependencies are visible in signatures; testing is simpler; coupling is easier to reason about.  
**Why it helps AI agents:** the agent can infer seams from constructor parameters and interfaces instead of reverse-engineering hidden runtime wiring.  
**Heuristic:** required dependencies go in the constructor; setter injection is for rare optional dependencies; avoid service locator for normal application code.  
**Example:**  
```ts
class InvoiceService {
  constructor(
    private readonly repo: InvoiceRepo,
    private readonly tax: TaxCalculator,
  ) {}
}
```  
Fowler describes DI as separating configuration from use, and Spring explicitly notes that DI improves testability; Spring also says setter injection is mainly appropriate for optional dependencies. citeturn31view0turn9search7turn9search3

**Ports and adapters, hexagonal, onion, and clean architecture.**  
**What it is:** place domain logic behind ports or interfaces and connect infrastructure through adapters.  
**Why it helps humans:** infrastructure can change without rewriting domain logic; tests can target the domain in isolation.  
**Why it helps AI agents:** boundaries become obvious places to insert or modify behavior; adapters localize external integration changes.  
**Heuristic:** use this style when the system has real external volatility or multiple delivery/data mechanisms. Do not create ceremonial ports for trivial CRUD apps with one database and one UI.  
**Example:** `PaymentGateway` as a port, `StripePaymentGateway` as an adapter.  
**Trade-off:** this pattern helps both audiences when the boundary is real, but hurts both when it degenerates into one-interface-per-class boilerplate. Microsoft’s .NET guidance explicitly links Dependency Inversion and DDD to hexagonal / ports-and-adapters / onion / clean architecture. citeturn9search0turn29search13

**Facade and gateway boundaries for subsystems and foreign APIs.**  
**What it is:** provide a coarse, domain-oriented entry point over a complicated subsystem or third-party API.  
**Why it helps humans:** fewer call sites know vendor details; changes are concentrated.  
**Why it helps AI agents:** there is a single obvious file or class to inspect when a behavior involves the subsystem.  
**Heuristic:** every nontrivial external system should have one named boundary package or module, such as `billing_gateway`, `slack_adapter`, or `search_facade`; do not scatter raw SDK calls through business code.  
**Example:** `SlackClient.postOrderFailureAlert(orderId)` is better than twenty direct Slack SDK calls across the codebase.  
**Status:** **Established consensus.** Fowler describes a gateway as the single point that translates between your system’s terms and a foreign API, and remote facade as a coarse-grained facade over finer-grained objects. citeturn29search22turn29search3

**Strategy and replace-conditional-with-polymorphism for true variation points.**  
**What it is:** encapsulate interchangeable behaviors behind a stable interface instead of growing `if/else` or `switch` trees.  
**Why it helps humans:** variation is explicit and extensible; new behaviors do not bloat a central function.  
**Why it helps AI agents:** it gives the model a named extension point, which is easier than editing long conditional branches with hidden assumptions.  
**Heuristic:** use Strategy only when the variation is real, frequent, and semantically meaningful. If there are only two tiny branches that will never grow, a direct conditional is often clearer.  
**Example:** fraud scoring strategies by market, payment method, or experiment cohort.  
**Status:** **Established pattern; AI benefit is a synthesis.** Fowler’s refactoring catalog recommends replacing conditionals with polymorphism when behavior truly varies, while canonical Strategy definitions emphasize interchangeable families of algorithms. citeturn32search0turn32search2

**Repository pattern only at meaningful persistence boundaries.**  
**What it is:** an abstraction that mediates between the domain and data-mapping layers.  
**Why it helps humans:** persistence concerns stay out of the core model.  
**Why it helps AI agents:** persistence changes are easier to localize when the storage boundary is real and named.  
**Heuristic:** use repositories where the domain must be insulated from storage details; do not add pass-through repositories that merely mirror ORM CRUD with no domain value.  
**Example:** `OrderRepository.nextReadyForSettlement()` is valuable; `UserRepository.getById()` wrapping a one-line ORM query may be pure ceremony.  
**Status:** **Established consensus with a well-known overuse trap.** citeturn29search2turn29search13

**Organize by feature or use case once the codebase is large enough.**  
**What it is:** prefer feature folders or vertical slices over purely technical layers when most changes are user-story shaped.  
**Why it helps humans:** code that changes together lives together.  
**Why it helps AI agents:** fewer cross-folder hops are required to implement a feature change.  
**Heuristic:** for small systems, a simple layered structure is fine. Once most tasks span controller + service + model + test, move to feature slices such as `features/orders/create_order/*`.  
**Example:**  
```text
features/
  orders/
    create_order/
      handler.ts
      service.ts
      validation.ts
      repo_test.ts
```  
Jimmy Bogard’s vertical slice argument is exactly that architecture should couple along the axis of change; by contrast, layered architectures are often more beginner-friendly but cause more file-hopping per change. citeturn10search12turn10search19turn9search0

**Architectural style selection by AI-friendliness.**  
Layered architecture is often easiest to teach and audit, but feature changes can span many folders. Clean/onion/hexagonal improves explicit boundary clarity, but can create abstraction tax if over-applied. Vertical slice usually gives the best **change locality** for agent editing. Event-driven architecture is powerful for scalability and decoupling, but it is the hardest style for both humans and agents to debug unless contracts, replay tooling, and tracing are excellent, because control flow is temporal and nonlocal rather than lexical. Azure’s architecture guidance emphasizes the decoupling benefits of event-driven systems; the price is that you must restore observability and contract clarity elsewhere. citeturn10search0turn10search2turn10search17turn15search2turn15search6

## Code-level quality rules

**Guard clauses and early returns.**  
**What it is:** exit invalid or exceptional paths early instead of nesting the main path under multiple conditionals.  
**Why it helps humans:** flatter code is easier to scan.  
**Why it helps AI agents:** shallower control flow reduces ambiguity when an agent tries to reason about path conditions or edit only the happy path.  
**Heuristic:** prefer one level of indentation for the main path; refactor when nesting exceeds two levels; as a default target, keep cyclomatic complexity under roughly `10` and cognitive complexity under roughly `15` for routinely edited functions. Those numeric thresholds are a practical synthesis, not a universal law.  
**Example:**  
```python
def settle(invoice: Invoice) -> Receipt:
    if invoice.is_void:
        raise VoidInvoiceError(invoice.id)
    if not invoice.lines:
        raise EmptyInvoiceError(invoice.id)
    return gateway.charge(invoice.total())
```  
PEP 20 explicitly favors “flat” over “nested,” and Sonar’s cognitive-complexity work is specifically aimed at understandability rather than just execution-path count. citeturn37search0turn8search7turn8search19

**Small, purposeful functions rather than tiny wrappers.**  
**What it is:** functions should do one coherent thing, but not become trivial indirection.  
**Why it helps humans:** comprehension improves when a function name matches a meaningful unit of work.  
**Why it helps AI agents:** agents do better when there is a clear edit target, but worse when logic is fragmented into dozens of one-line wrappers with no information hiding.  
**Heuristic:** most application functions should fit in one screenful; extracted helpers should remove complexity or name a domain concept, not merely move three lines elsewhere. If a helper adds a jump without hiding any knowledge, inline it.  
**Example:** `calculate_refund_window(order, policy_clock)` is a good extraction; `get_total(order)` wrapping `order.total` is usually not.  
**Status:** **Established consensus; AI angle is a synthesis.** Ousterhout explicitly argues against thin abstractions that add interface surface without hiding complexity. citeturn18search1turn18search3turn18search5

**Limit parameter count and make illegal combinations unrepresentable.**  
**What it is:** avoid long parameter lists and “boolean soup.”  
**Why it helps humans:** fewer call-site mistakes and easier reading.  
**Why it helps AI agents:** clearer signatures reduce the chance of incorrect argument ordering or unnoticed coupling between flags.  
**Heuristic:** four parameters is a healthy soft limit; at five or more, consider a parameter object, a value type, or split the operation. Never stack multiple booleans when they encode a mode.  
**Example:** replace `render(user, true, false, true, None)` with `render(RenderRequest(user=user, include_history=True, format=HTML))`.  
This heuristic follows directly from explicitness, type-driven design, and the evidence that strong type and schema signals improve reasoning and tooling. citeturn12search0turn35search0turn27view2

**Names that encode the domain, not the implementation accident.**  
**What it is:** use consistent, semantically loaded names aligned with the domain.  
**Why it helps humans:** naming is how architecture becomes visible in code.  
**Why it helps AI agents:** models ground on names. Precise, repeated vocabulary is a high-value retrieval signal.  
**Heuristic:** pick one ubiquitous term per concept and use it everywhere. For API boundaries, favor established naming conventions and plain English. Avoid vague containers like `util`, `common`, `helpers`, or `misc`.  
**Example:** use `SettlementBatch`, `InvoicePolicy`, `PaymentAttempt`; avoid `DataManager`, `Utils`, `ServiceHelper`.  
Unmesh Joshi’s 2026 essay makes the AI-era case directly: code is both machine instruction and conceptual model, and vague or inconsistent vocabulary forces the model to guess. Google’s AIP naming guidance and Abseil’s warning against package names like `util` or `common` point in the same direction. citeturn28view0turn19search6turn5search2turn4search4

**Consistency beats local cleverness.**  
**What it is:** one dominant idiom per language, framework, and subsystem.  
**Why it helps humans:** fewer style dialects to parse.  
**Why it helps AI agents:** the model can imitate stable patterns instead of inferring which of five styles is preferred in a given file.  
**Heuristic:** formatter-enforced style, linter-enforced conventions, one testing idiom per stack, one dependency-injection idiom per codebase, one error-handling approach per boundary.  
**Example:** if you use constructor DI, do it everywhere in the service layer. Do not mix constructor DI, service locators, hidden globals, and decorator magic in the same slice.  
Google’s style guides and code review standard are fundamentally about sustained code health and readability, not aesthetics. citeturn17search11turn4search8turn4search14turn4search15

**Comments for intent, constraints, and caveats; code for mechanics.**  
**What it is:** comments should explain *why*, invariants, business rules, cross-system quirks, and security or performance constraints. Code should explain *how* where possible.  
**Why it helps humans:** intent survives refactors better than line-by-line narration.  
**Why it helps AI agents:** intent comments are valuable grounding; stale mechanical comments are harmful noise.  
**Heuristic:** comment exported APIs, nonobvious invariants, protocol assumptions, and exception semantics. Delete comments that merely restate code. Keep module and package docstrings as indexes of public surface area.  
**Example:**  
```python
def normalize_tax_id(raw: str) -> str:
    """Normalize user-entered tax IDs to the authority's checksum format.

    Required because upstream ERP rejects visually equivalent variants.
    """
```  
PEP 8 is blunt that comments contradicting code are worse than no comments, and PEP 257 recommends module and package docstrings that list exported surface area. citeturn11search0turn11search3

**Explicit failure modes and semantic errors.**  
**What it is:** propagate or model failures explicitly instead of swallowing them or returning ambiguous sentinel values.  
**Why it helps humans:** easier debugging, cleaner contracts, safer retries.  
**Why it helps AI agents:** agents rely heavily on stack traces, exception types, and explicit error channels to diagnose and patch failures.  
**Heuristic:** catch only exceptions you can handle meaningfully; otherwise log with context and re-raise. Use domain-specific error types at service boundaries. Prefer typed result channels for expected failures and reserve crashes for invariant violations.  
**Example:**  
```rust
fn load_config(path: &Path) -> Result<AppConfig, ConfigError> { ... }
```  
Python docs recommend catching specific exceptions and re-raising unexpected ones; Rust makes error acknowledgement explicit at compile time and distinguishes recoverable `Result` from panic paths. PEP 20 also says errors should never pass silently unless explicitly silenced. citeturn35search1turn36search2turn36search0turn36search8turn37search0

**Delete dead code aggressively.**  
**What it is:** remove unused imports, stale feature flags, obsolete adapters, and unreachable branches.  
**Why it helps humans:** less noise, fewer wrong clues.  
**Why it helps AI agents:** dead code is retrieval poison; agents often inspect whatever search returns first.  
**Heuristic:** enable safe autofixes for unused imports and basic dead code; require an owner and expiry for every feature flag.  
**Example:** run linters that remove unused imports automatically and flag unreachable code during pre-commit. Ruff can safely fix unused imports; Semgrep and CodeQL extend static analysis into broader bug and security patterns. citeturn20search3turn20search14turn20search1turn20search0

## AI-agent-specific repository design

**Optimize for context-window economy and change locality.**  
**What it is:** make the files needed for a single task physically and conceptually close.  
**Why it helps humans:** fewer jumps and less working-memory load.  
**Why it helps AI agents:** repository-level benchmarks consistently show that retrieving the right cross-file context is a central difficulty.  
**Heuristic:** prefer feature-local tests, validation, and mapping code near the feature. As a synthesis rule, keep hot-path files small enough to review in one pass, and avoid designs where a simple change requires editing five unrelated layers.  
**Example:** co-locate `create_order` handler, validation, domain service, and tests in one slice instead of scattering across `controllers/`, `services/`, `validators/`, `repositories/`, and `tests/functional/`.  
RepoBench, RepoCoder, RepoGraph, Rust-SWE-bench, and Anthropic’s context-engineering guidance all point in the same direction: agents perform better when they can progressively discover a relevant subset rather than drag the whole codebase into working memory. citeturn25view0turn25view3turn25view4turn24view3turn24view0turn27view0

**Prefer explicitness to magic.**  
**What it is:** reduce metaprogramming, hidden side effects, runtime monkey-patching, stringly-typed registries, and invisible code generation in the core application path.  
**Why it helps humans:** explicit code is easier to read, grep, and debug.  
**Why it helps AI agents:** agents depend on static cues—names, imports, signatures, schemas, and local control flow.  
**Heuristic:** if behavior cannot be found with ordinary file search and type navigation, it is probably too magical for a mixed human+agent codebase. Keep metaprogramming behind tight, well-documented boundaries.  
**Example:** prefer explicit route registration or typed plugin maps over `method_missing`-style dispatch in core business logic.  
PEP 20 captures the principle succinctly—explicit is better than implicit, readability counts, ambiguity should not invite guessing—and even metaprogramming advocates note readability, maintainability, and searchability pitfalls. citeturn37search0turn37search9

**Emit machine-readable signals everywhere you can.**  
**What it is:** types, schemas, OpenAPI specs, JSON Schema, protobuf definitions, structured config, and docstrings that tools can consume.  
**Why it helps humans:** better IDE support, stronger review signals, fewer broken assumptions.  
**Why it helps AI agents:** these are grounded constraints the model can rely on instead of inferring intent from prose or examples alone.  
**Heuristic:** every external boundary should have a machine-readable contract; every critical internal boundary should have typed inputs and outputs.  
**Example:** OpenAPI for HTTP, JSON Schema for payloads, protobuf or Avro for messages, typed config structs instead of raw dicts.  
TypeScript presents types as the route to “better tooling at any scale”; OpenAPI is explicitly a language-agnostic specification for HTTP APIs; JSON Schema is declarative validation and annotation for JSON; protobuf best practices even recommend smaller schema files for easier refactoring and maintainability. citeturn12search0turn12search22turn12search1turn12search5turn12search2turn12search6turn12search3

**Turn tests into an executable index of intended behavior.**  
**What it is:** keep tests readable, targeted, and runnable by commands that both humans and agents can invoke.  
**Why it helps humans:** tests are living regression protection.  
**Why it helps AI agents:** tests are the most trustworthy local grounding source after the code itself. SWE-bench literally evaluates issue resolution by fail-to-pass tests.  
**Heuristic:** every bug fix gets a regression test near the affected code; every public module has a smoke-path integration test; every repository advertises one fast verification command and one full verification command.  
**Example:** `pnpm test --filter @app/orders` for fast local checks and `pnpm verify` for full validation.  
SWE-bench’s evaluation is built around failing tests that pass after the correct patch, and GitHub’s cloud agent works in ephemeral environments where running tests and linters is first-class. citeturn24view4turn22view4

**Provide repository scaffolding, but keep it lean.**  
**What it is:** a small set of durable docs that explain how to build, test, navigate, and decide.  
**Why it helps humans:** lowers onboarding cost and reduces folklore.  
**Why it helps AI agents:** gives the agent a deterministic starting point.  
**Heuristic:** maintain four load-bearing artifacts:
- `README.md` for quick start and command entry points
- `ARCHITECTURE.md` for system map and boundaries
- concise repo and path-specific agent instructions
- `docs/adr/` for major decisions  
Keep instruction files short, operational, and path-scoped where possible.  
**Example:** a repo-level `AGENTS.md` with build/test commands and a `payments/AGENTS.md` describing PCI-safe patterns for only that subtree.  
OpenAI’s Codex layers AGENTS.md files by scope and says short, accurate files outperform long vague rules; GitHub supports path-specific instructions; Anthropic says shorter files produce better adherence; the 2026 AGENTS.md evaluation found that overly rich context files often increase cost and can reduce task success. The convergence is strong on **having some scaffolding**; the current conflict is about **how much**. citeturn22view0turn22view1turn22view2turn22view3turn21view0

**Standardize commands and make builds reproducible.**  
**What it is:** one-command setup, one-command fast verification, one-command full verification, pinned toolchains, hermetic or near-hermetic builds.  
**Why it helps humans:** fewer “works on my machine” failures and faster onboarding.  
**Why it helps AI agents:** agents often run in ephemeral containers or GitHub Actions-like environments and need deterministic commands.  
**Heuristic:** document `setup`, `test-fast`, `verify`, and `lint` exactly once; pin runtime and lockfiles; avoid undocumented environment dependencies. Where feasible, make builds hermetic.  
**Example:**  
```text
make setup
make test-fast
make verify
make lint
```  
Bazel documents hermeticity as isolation from hidden dependencies; Nix emphasizes reproducible, declarative systems; Reproducible Builds defines independently verifiable build outputs; GitHub’s cloud agent explicitly uses ephemeral environments that execute tests and linters. citeturn16search1turn16search2turn16search4turn22view4

## Types, contracts, testing, and verification

**Adopt static typing aggressively at system boundaries.**  
**What it is:** use compile-time types for public APIs, persistence seams, integration DTOs, and configuration.  
**Why it helps humans:** stronger review feedback and safer refactors.  
**Why it helps AI agents:** type signatures are compact, machine-readable context that sharply reduces ambiguity.  
**Heuristic:** even in dynamic languages, type your exported functions, API payloads, and config objects first. Internal leaf code can be looser than boundaries.  
**Example:** typed DTOs for HTTP requests and events, even if local implementation code is partially dynamic.  
TypeScript positions types as a scaling tool, and Rust ties its type system directly to compile-time elimination of bug classes. citeturn12search0turn12search22turn35search0

**Design interfaces around clients, not around implementation categories.**  
**What it is:** small, cohesive interfaces that expose what callers actually need.  
**Why it helps humans:** less accidental coupling and fewer fake abstractions.  
**Why it helps AI agents:** the agent has fewer irrelevant methods and fewer wrong extension points to choose from.  
**Heuristic:** define interfaces per use case or capability, not per noun with every conceivable method.  
**Example:** `Clock.now()` and `TransactionStore.append()` are often better than one giant `PlatformServices` interface.  
This follows from interface segregation, DI, and information-hiding principles, even when the exact interface split is project-specific. citeturn31view0turn18search9turn18search1

**Use contract-first development for external boundaries.**  
**What it is:** define the API or message schema before and alongside implementation.  
**Why it helps humans:** implementation can be reviewed against a stable contract.  
**Why it helps AI agents:** a formal spec is easier for a model to follow than prose-only instructions.  
**Heuristic:** HTTP APIs get OpenAPI; JSON payloads get JSON Schema; messages get protobuf or another versioned schema. Validate compatibility in CI.  
**Example:** consumer and provider contract validation for a payment webhook.  
OpenAPI exists specifically to carry information through the API lifecycle; JSON Schema exists to annotate and validate structure; protobuf guidance emphasizes evolvable separate schema files and compatibility discipline. Pact’s contract-testing docs make the practical case that contract tests can replace some brittle integration tests. citeturn12search1turn12search5turn12search2turn12search3turn19search1

**Balance the test pyramid, not the test monoculture.**  
**What it is:** many small fast tests, fewer integration tests, fewer still end-to-end tests.  
**Why it helps humans:** fast feedback without sacrificing realism.  
**Why it helps AI agents:** agents can safely iterate when there is a short, reliable inner loop and a narrower outer safety net.  
**Heuristic:** Google’s public rule of thumb—roughly `70/20/10` for unit/integration/e2e—is still a reasonable starting point, then tune it for the system. Keep small tests hermetic and cheap.  
**Example:** domain-policy tests at the bottom, repository and HTTP integration tests in the middle, checkout-happy-path browser tests at the top.  
Google’s testing guidance and Software Engineering at Google material both reinforce this shape and the distinction between test size and scope. citeturn5search3turn5search1turn13search3turn14search5

**Design for testability up front.**  
**What it is:** code structure should make isolation, dependency substitution, and deterministic verification natural.  
**Why it helps humans:** fewer late refactors to “make it testable.”  
**Why it helps AI agents:** an agent can patch and validate a module if the seams are already there.  
**Heuristic:** business logic should be instantiable without a full app container; time, randomness, I/O, and external services should be injectable or mockable.  
**Example:** pass a `Clock` into settlement logic instead of reading `Date.now()` deep in the function.  
Spring’s docs say DI makes plain objects testable without the container, and Fowler’s DI article is fundamentally about decoupling wiring from use. citeturn9search7turn31view0

**Add property-based tests to invariant-heavy code.**  
**What it is:** specify properties that must hold across many generated inputs rather than a few hand-picked examples.  
**Why it helps humans:** exposes edge cases you did not think of.  
**Why it helps AI agents:** a richer behavioral net makes autonomous edits safer and reveals hidden assumptions earlier.  
**Heuristic:** use property-based tests for parsers, normalizers, serializers, money/math logic, scheduling, and protocol/state transformation code.  
**Example:** a round-trip property: `decode(encode(x)) == x` for valid domain objects.  
Hypothesis describes property-based testing as checking whether tests hold for all inputs in a range and automatically shrinking failing examples to the simplest counterexample. citeturn13search1turn13search5turn13search19

**Use mutation testing selectively on critical areas.**  
**What it is:** deliberately mutate production code and check whether the tests fail.  
**Why it helps humans:** reveals weak tests that cover code without truly specifying behavior.  
**Why it helps AI agents:** stronger tests reduce the chance that an agent produces test-passing but semantically poor patches.  
**Heuristic:** do not run mutation testing everywhere on every commit. Use it for core domain libraries, security-sensitive logic, serialization, and rules engines.  
**Example:** mutation-score gates for core pricing or authorization code, not for every UI component.  
Stryker defines mutation testing as introducing code changes and expecting tests to fail; Google’s research describes it as one of the strongest test criteria but also computationally expensive. citeturn14search1turn14search10

## Tooling, automation, documentation, and knowledge capture

**Formatter + linter + static analysis as mandatory machine checks.**  
**What it is:** automatic formatting, lightweight bug-catching lint rules, and deeper semantic analysis in CI.  
**Why it helps humans:** fewer taste debates, earlier feedback, less review toil.  
**Why it helps AI agents:** machine-checkable rules let the agent self-correct before asking for review.  
**Heuristic:** run fast style and lint checks in pre-commit; run deeper semantic analysis in CI. Keep rule sets stable and documented.  
**Example:** Prettier or equivalent for formatting, Ruff/ESLint for fast feedback, Semgrep or CodeQL for higher-signal checks.  
Pre-commit exists specifically to catch simple issues before code review; Prettier recommends dividing formatting from linting concerns; GitHub’s CodeQL and Semgrep both position static analysis as automated guardrails integrated into CI/CD. citeturn15search0turn15search5turn20search0turn20search1

**Required status checks and machine-readable CI semantics.**  
**What it is:** branch protection backed by named checks that humans and agents can interpret consistently.  
**Why it helps humans:** merge criteria are unambiguous.  
**Why it helps AI agents:** the agent does not need to guess what “done” means.  
**Heuristic:** protect the default branch with required checks for formatting/linting, tests, and contract/schema validation; use stable job names.  
**Example:** `lint`, `unit`, `integration`, `contracts`, `build` as separate required checks.  
GitHub docs define status checks as the mechanism for communicating whether commits meet repository conditions. citeturn15search3turn15search11

**Observability as debugging substrate, not just production ops.**  
**What it is:** traces, logs, and metrics that let you reconstruct what happened across async or distributed boundaries.  
**Why it helps humans:** faster incident analysis and better mental models.  
**Why it helps AI agents:** when autonomous debugging is involved, structured telemetry is the closest thing to runtime truth beyond tests.  
**Heuristic:** for distributed or event-driven systems, emit correlation IDs, meaningful structured logs, and distributed traces at all service boundaries.  
**Example:** every checkout request emits a trace spanning API, orchestration, payment, and fulfillment services.  
OpenTelemetry defines observability as understanding internal state through telemetry and emphasizes that distributed tracing is essential when behavior is hard to reproduce locally. citeturn15search6turn15search2turn15search10

**Keep docs in a layered hierarchy and link them to code and commands.**  
**What it is:** concise external docs for navigation and intent, with inline docs for public APIs and invariants.  
**Why it helps humans:** they can choose the right depth quickly.  
**Why it helps AI agents:** layered docs support progressive disclosure instead of flooding context.  
**Heuristic:** keep top-level docs short and index deeper docs. A strong default stack is:
- `README.md`: setup, key commands, repo layout
- `ARCHITECTURE.md`: system map, boundary rules, diagrams
- `docs/adr/`: significant decisions
- inline module/package docstrings and API docs  
**Example:** `ARCHITECTURE.md` contains a “Where to change what” section mapping use cases to folders and services.  
This structure reflects how OpenAI and Anthropic recommend keeping startup guidance concise and loading detail on demand. citeturn22view1turn22view3turn27view0

**Record intent with ADRs.**  
**What it is:** a short document for one meaningful architectural decision, including context and consequences.  
**Why it helps humans:** preserves the “why,” not just the “what.”  
**Why it helps AI agents:** helps the model avoid “fixes” that violate deliberate constraints invisible from the code alone.  
**Heuristic:** write ADRs only for significant, hard-to-reverse, or quality-attribute-affecting decisions; keep each ADR to a couple of pages and supersede rather than rewrite old ones.  
**Example:** “ADR-0042: Use outbox pattern for payment events to guarantee exactly-once publication semantics.”  
Fowler’s 2026 ADR entry, the ADR community site, AWS, and Azure all converge on the same idea: short records of one decision, its context, and ramifications, linked over time into a decision log. citeturn33search4turn33search1turn33search9turn33search15

## Anti-patterns, prioritized checklist, and the human-versus-agent trade-offs

**Anti-patterns that hurt humans, agents, or both**

| Anti-pattern | Why it hurts humans | Why it hurts agents | Better default |
|---|---|---|---|
| God files and god services | Too much context per edit; high cognitive load | Retrieval returns huge noisy files; edit target unclear | Split by cohesive domain or feature slice, not by arbitrary line count alone. Supported by information-hiding and repository-level retrieval evidence. citeturn18search9turn25view4turn24view3 |
| Generic folders like `util`, `common`, `helpers` | Ownership and purpose become vague | Search results are ambiguous; grounding weak | Name modules after domain capabilities. Google and Abseil explicitly discourage uninformative names. citeturn5search2turn4search4turn28view0 |
| Hidden service locators and ambient globals | Dependencies are invisible | Agents miss required wiring and side effects | Constructor DI, explicit parameters, typed config. citeturn31view0turn9search7 |
| Over-layered “clean” architecture for trivial apps | Boilerplate and indirection tax | Too many files per simple change | Use only as much architectural separation as change volatility justifies. citeturn9search0turn10search12 |
| Magic metaprogramming in core paths | Hard to grep, debug, and reason about | Static navigation and search degrade badly | Keep dynamic magic at framework edges; prefer explicit registration and generated code with sources checked in. citeturn37search0turn37search9 |
| Comments that narrate mechanics | Stale quickly | Become misleading grounding | Comment intent, invariants, and reasons; delete restatement comments. citeturn11search0turn11search3 |
| Swallowed errors and boolean/sentinel failure codes | Hard to debug and retry safely | Agents lose diagnostic signal | Specific exceptions or typed results with context. citeturn35search1turn36search2turn36search8 |
| Slow, flaky, non-hermetic tests | Developers stop trusting feedback | Agents cannot verify edits reliably | Fast inner-loop tests plus hermetic CI and stable commands. citeturn5search3turn16search1turn22view4 |
| Verbose AGENTS/CLAUDE context files | Humans stop maintaining them | Agents incur higher cost and may follow harmful noise | Keep instruction files short, operational, and path-scoped. citeturn21view0turn22view1turn22view2turn22view3 |
| Event-driven systems without tracing and contracts | Hard to reconstruct causality | Agents cannot localize failures in async flows | Add schemas, correlation IDs, traces, and replay/debug tools. citeturn10search0turn15search2turn15search6 |
| Pass-through repositories and abstraction cargo cults | More files, same complexity | More retrieval surface, no new signal | Introduce abstractions only when they hide meaningful knowledge. citeturn29search2turn18search1 |
| Dead code and expired feature flags | Misleads maintenance and review | Pollutes search and retrieval results | Use static analysis and expiry discipline. citeturn20search3turn20search14 |

**Prioritized checklist of highest-leverage practices**

1. **Make the repository easy to navigate by change locality.** Prefer feature slices or clear ownership boundaries so most tasks touch a small, obvious set of files. citeturn10search12turn25view4turn24view3  
2. **Expose dependencies explicitly.** Constructor DI, typed config, no hidden globals or service locators in normal app code. citeturn31view0turn9search7  
3. **Put machine-readable contracts at every external boundary.** OpenAPI, JSON Schema, protobuf, typed DTOs, typed configs. citeturn12search1turn12search2turn12search3turn12search0  
4. **Keep tests fast, runnable, and trustworthy.** Publish one fast command and one full verification command; maintain a healthy test pyramid. citeturn5search3turn14search5turn22view4  
5. **Add a regression test for every bug fix.** Treat tests as the primary executable specification for future humans and agents. citeturn24view4  
6. **Use precise domain names consistently.** Enforce one vocabulary per bounded context; ban `util/common/helpers` as dumping grounds. citeturn28view0turn5search2  
7. **Flatten control flow.** Guard clauses, low nesting, explicit error paths, and bounded complexity budgets. citeturn37search0turn8search7turn35search1  
8. **Provide lean repository guidance.** `README.md`, `ARCHITECTURE.md`, ADRs, and short path-aware agent instructions; avoid giant instruction files. citeturn22view1turn22view2turn22view3turn21view0  
9. **Automate formatting, linting, and static analysis in pre-commit and CI.** Prefer machine-checked rules over code review reminders. citeturn15search0turn15search5turn20search0turn20search1  
10. **Make builds and verification reproducible.** Pin toolchains, lock dependencies, aim for hermeticity where feasible. citeturn16search1turn16search2turn16search4  
11. **Instrument distributed systems.** Without traces and structured logs, both human and agent debugging degrade sharply. citeturn15search2turn15search6  
12. **Use advanced verification where risk justifies it.** Property-based testing for invariants; mutation testing on critical logic. citeturn13search5turn13search19turn14search1turn14search10

**Convergence versus conflict summary**

| Practice | Human optimization | AI optimization | Convergence or conflict | Resolution |
|---|---|---|---|---|
| Clear names and ubiquitous language | Improves comprehension and onboarding | Improves retrieval and grounding | Strong convergence | Standardize vocabulary per bounded context. citeturn28view0 |
| Small cohesive modules | Lowers cognitive load | Reduces context needed per task | Strong convergence | Split by reason to change, not by arbitrary size alone. citeturn18search9turn18search1 |
| Deep abstractions | Hide complexity from callers | Give agents stable edit seams | Mostly convergence | Avoid shallow wrappers that add files without hiding knowledge. citeturn18search1turn18search3 |
| Vertical slices | Changes live together | Fewer file hops for agent edits | Often convergence | Prefer for product and use-case driven codebases. citeturn10search12turn10search19 |
| Clean/hexagonal layering | Clarifies boundaries | Can over-expand edit surface if excessive | Potential conflict | Apply only where boundary volatility or testing needs justify it. citeturn9search0turn29search13 |
| Rich repository instruction files | More prose can help onboarding | Too much context can lower success and raise cost | Real conflict in 2026 evidence | Keep them short, operational, and path-scoped. citeturn21view0turn22view1turn22view2turn22view3 |
| Metaprogramming and dynamic magic | Can reduce boilerplate for experts | Harms searchability and static reasoning | Frequent conflict | Reserve for framework edges; prefer explicit core logic. citeturn37search0turn37search9 |
| Event-driven decoupling | Helps scalability and organization | Harder nonlocal reasoning across async flows | Conflict unless tooling is strong | Add schemas, replay, tracing, and observability from day one. citeturn10search0turn15search2turn15search6 |
| Strong typing and schemas | Safer refactors, better tooling | Strong machine-readable constraints | Strong convergence | Type boundaries first, internals second. citeturn12search0turn12search1turn12search2 |
| Tests and CI gates | Protect code health | Provide executable guardrails | Strong convergence | Keep the fast path reliable and the full path authoritative. citeturn14search5turn24view4turn15search3 |

**Open questions and limitations**

The strongest evidence on agent-specific repository practices is still young. In particular, the value of `AGENTS.md`-style files is **not settled**: vendor docs recommend them, but the best public 2026 evaluation finds only marginal benefit from human-written files and a negative effect from LLM-generated ones in the tested settings. Repository-level agent research is also benchmark-sensitive and still heavily centered on a few languages and ecosystems, especially Python and, increasingly, Rust. For numeric heuristics such as target function length, file size, or acceptable abstraction depth, this report therefore gives **synthesized engineering defaults** rather than universal standards. citeturn21view0turn22view1turn24view0turn26search0

The practical bottom line is simple: **optimize the codebase so that the next correct change is easy to locate, easy to reason about, easy to implement, and easy to verify.** That is what humans need. It is also, more and more, what agents need. citeturn28view0turn24view4turn27view0