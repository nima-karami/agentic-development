# Auditing Contract Design in an Agent-Written Codebase: Criteria, Rubric, and Detection

The contract checks that matter most in an audit are the ones where an interface says something the implementation doesn't do. Examples: an optional parameter that is really required, a return type that hides failure, a catch block that turns an error into a default value, a status string standing in for a state machine, or an untyped payload that crosses a trust boundary unparsed. About half of these can be pre-screened by machine (strict type-checker settings, lint rules, API-surface and schema diffing). The other half need judgment, and an LLM reviewer can apply that judgment consistently only if it gets a fixed rubric, has to cite a line, and is allowed to report "no finding."

## TL;DR

- **Ten checks to run first:**
  1. Optionality that lies: required values typed as optional, or nullable with no reason.
  2. Return types that hide failure, such as null, `-1`, `{}` or `false` used to mean "error."
  3. Swallowed errors and catch-and-default code.
  4. No consistent error taxonomy, and no translation of errors at layer boundaries.
  5. Unparsed data crossing trust boundaries (casts or `any` instead of parsing).
  6. Status strings or boolean clusters where a discriminated union or state machine belongs.
  7. Boolean-flag and long positional parameter lists.
  8. Public surface larger than intended: barrel re-exports, leaked internals, vendor types in signatures.
  9. Duplicated near-identical types (DTO drift) across layers.
  10. Schema and storage changes made without compatibility rules, migrations or contract tests.
- **What's mechanical and what needs judgment:** strictness flags (TypeScript `strict`, mypy/pyright strict, Rust/Go compilers), lint rules (`no-explicit-any`, blind-except, boolean-trap, exhaustiveness), and diff tools (API Extractor, cargo-semver-checks, `buf breaking`, OpenAPI diffing, Pact) find the candidates. Whether a finding is a defect depends on context: is the default honest, is the boundary real, is a richer type worth its cost. That part needs a constrained human or LLM reviewer.
- **Agent-specific evidence:**
  - *Duplication:* the best-measured effect is the rise in code duplication in AI-assisted code (GitClear 2024/2025, correlational).
  - *Error handling:* a vendor report (CodeRabbit, Dec 2025) says error-handling gaps are more common in AI-co-authored PRs.
  - *Type loosening:* reports of agents adding `any`, optional parameters or fallbacks to get code to compile are mostly anecdote plus lab disclosures about "special-casing tests."
  - *Defences:* strict compiler settings that agents can't relax, lint rules that fail CI, and written contract conventions in agent instruction files (AGENTS.md/CLAUDE.md).

## Key Findings

**1. Most contract defects are interfaces that misstate what the code does, not ugly interfaces.** Several design traditions agree on this:
- Bloch's API-design talk ("How to Design a Good API and Why it Matters," 2006) and *Effective Java* (3rd ed., 2018).
- Ousterhout's *A Philosophy of Software Design* (2018; 2nd ed. 2021).
- Fowler's refactoring catalog (*Refactoring*, 2nd ed., 2018).

They all treat the interface as a promise and penalise surprise. An audit should rank honesty violations (the type says X, the behaviour is Y) above style violations (the API could be nicer).

**2. "Parse, don't validate" and "make illegal states unrepresentable" are established practice, but only at the edges and at the core.**
- Alexis King's essay "Parse, don't validate" (2019) and Yaron Minsky's "make illegal states unrepresentable" (Jane Street, ~2010–2011) are widely adopted in typed functional programming, Rust and TypeScript.
- They pay off at trust boundaries and in central domain types (IDs, money, order or payment state).
- They become over-engineering when applied to short-lived local values, or when the type machinery costs more than the bugs it prevents.

**3. Error contracts fail mostly through inconsistency, not through choosing the "wrong" mechanism.** Each ecosystem has a well-defined default:
- *Rust:* `Result` with `?`; libraries define their own error types.
- *Go:* returned `error` values; wrapping with `%w` and `errors.Is`/`errors.As` since Go 1.13 (2019).
- *Java:* exceptions, with exception translation to the right abstraction (*Effective Java* Item 73) and "don't ignore exceptions" (Item 77).
- *TypeScript and Python:* exceptions by default; result types are opt-in.

The audit finding is usually that a codebase mixes three styles for the same kind of failure, or that low-level errors leak through several layers untranslated.

**4. Hyrum's Law makes every observable behaviour part of the contract.** Hyrum Wright's observation appears in *Software Engineering at Google* (Winters, Manshreck & Wright, O'Reilly, 2020). Its consequence is that accidental public surface (barrel re-exports, exported helpers, vendor types in signatures) becomes a commitment. Surface size can be measured mechanically:
- TypeScript: Microsoft's API Extractor; knip or ts-prune for unused exports.
- Rust: `cargo public-api` and `cargo-semver-checks`.
- Go: `internal/` packages and `apidiff`/`gorelease`.
- Python: `__all__` plus griffe.

**5. Schema evolution has mature, mechanical tooling. Audits should check that it's wired in, not reinvent it.**
- Protobuf field-number rules, enforced by `buf breaking`.
- Confluent Schema Registry compatibility modes.
- OpenAPI diffing tools such as oasdiff.
- Consumer-driven contracts: Ian Robinson, "Consumer-Driven Contracts: A Service Evolution Pattern," martinfowler.com, 2006; implemented by Pact.
- The parallel-change / expand–contract migration pattern.

Missing tooling is the finding in a multi-service system. In a single product app, the main risks are DTO drift and unsafe migrations.

**6. The evidence on agents is uneven.**
- *Duplication* is the best-measured agent-associated contract problem. It shows up directly as near-identical types and DTOs.
- *Error handling:* claims that agents swallow errors more often rest mainly on a vendor report.
- *Type loosening:* claims that agents loosen types to compile, or add optional parameters to avoid touching callers, are mostly practitioner anecdote, consistent with lab disclosures that models sometimes game tests.

Treat these as patterns to look for, not as base rates.

## Rubric: Core Contract Criteria (language-agnostic)

Severity guidance: **High** means it can corrupt data, hide failures in production, or break consumers silently. **Medium** means it misleads callers or makes change risky. **Low** means friction or style.

| # | Criterion | What a finding looks like in code | Detection | Severity guidance | Where it becomes over-engineering |
|---|---|---|---|---|---|
| 1 | Optionality matches reality | A parameter typed optional, then immediately null-checked with a throw or a silent default, or always passed by every caller. A field optional in the type but required by every reader. | Mechanical candidates: find optional parameters that all call sites supply; unused-default analysis. Judgment: is the default meaningful? | High if the default hides a missing value (e.g., `tenantId = "default"`). Medium otherwise. | Making genuinely optional configuration required just to be "explicit." |
| 2 | Nullability is deliberate | Return type `T \| null` where null means both "not found" and "error"; nullable fields with no documented meaning; non-null assertions (`!`) scattered to silence the checker. | Mechanical: strict null checking; counting non-null-assertion and `!!` / `.unwrap()` usages. | High when null encodes failure; Medium when null is ambiguous. | Wrapping every value in Option/Maybe inside a function where it can't be absent. |
| 3 | Failure is visible in the signature | Functions that return `-1`, `false`, `{}`, `[]` or a sentinel object on error; `Promise<T>` that resolves with a fake value on failure. | Judgment, guided by AST queries: find return statements inside catch blocks. | High: callers can't tell success from failure. | Typed result values for failures that can only be programming bugs (those should crash). |
| 4 | Boolean-flag parameters | `render(data, true, false)`; a function whose body is `if (flag) {A} else {B}`. Fowler's "FlagArgument" (2011) and *Clean Code* (Martin, 2008) treat these as two functions merged into one. | Mechanical: Ruff `FBT001–003` (flake8-boolean-trap) in Python; custom AST rule elsewhere. Judgment: split or turn into an enum/options object. | Medium if public; Low if private. | Splitting a function whose flag is a real, named configuration value (`{ recursive: true }`). |
| 5 | Parameter objects vs. positional | Four or more positional parameters, especially adjacent parameters of the same type (`(string, string, string)`) that can be swapped silently. | Mechanical: parameter-count lint (`max-params`, Pylint `too-many-arguments`). Judgment on grouping. | Medium when adjacent same-typed parameters can be swapped. | Bundling two obvious parameters into an object; "bag of everything" option objects with 20 optional fields. |
| 6 | Overloads are coherent | Overloads or union parameters whose return type doesn't narrow with the input. Overloads that differ in behaviour, not just input shape (Bloch: "use overloading judiciously," *Effective Java* Item 52). | Judgment. | Medium. | Adding overloads where a single generic or union signature suffices. |
| 7 | Names match behaviour | `getUser()` that creates users, `validate()` that mutates, `isX()` with side effects, `tryX()` that throws. | Judgment (LLM-suitable). Mechanical hints: functions named `get*`/`is*` that write to storage or the network. | Medium; High if a "query" mutates persisted state. | Renaming wars over synonyms. |
| 8 | Error mechanism is consistent per failure kind | The same kind of failure (e.g., "not found") is signalled by throw in one module, null in another, and `{ error }` in a third. | Semi-mechanical: inventory of throw/return patterns per layer. Judgment for the taxonomy. | High when callers in the same layer must handle three styles. | Forcing a Result type through a codebase whose language and libraries are exception-based. |
| 9 | Coherent error taxonomy and boundary translation | Raw database or HTTP-client errors reach UI or API responses. API error bodies differ between endpoints. No distinction between expected (domain) and unexpected (bug or infrastructure) errors. Standards to compare against: *Effective Java* Item 73 (exception translation); RFC 9457 "Problem Details for HTTP APIs" (2023, replacing RFC 7807); Google AIP-193 (errors). | Semi-mechanical: grep for vendor error types above the data layer; schema check of error responses. | High at API boundaries (leaks internals, breaks clients); Medium internally. | Deep hierarchies of exception classes no caller distinguishes. |
| 10 | No swallowing or catch-and-default | `catch {}`, `except: pass`, `catch (e) { return [] }`, `.catch(() => null)`, `_ = err` in Go, `.unwrap_or_default()` on I/O results, a log-and-continue that leaves state half-written. | Mechanical: Ruff `E722`, `BLE001`, `S110`; ESLint `no-empty`, `@typescript-eslint/no-floating-promises`; `errcheck` in Go linters; Clippy lints in Rust. Judgment: is the fallback a documented degradation? | High when it hides data loss or wrong results; Low when it's a documented best-effort path (e.g., optional telemetry). | Banning all fallbacks; graceful degradation that is declared and tested is a legitimate contract. |
| 11 | Invariants encoded in types where valuable | IDs passed around as bare `string` and mixed up (`userId` passed as `orgId`). Money as `float`. `status: string` with ad-hoc comparisons. Objects where `isLoading`, `error` and `data` can all be set at once. | Mechanical hints: string-literal comparisons against a status field; `switch` statements without an exhaustiveness check. Judgment on value. | High for money, identity, authorisation state and lifecycle state; Low for local values. | Branded types for every string; type-level state machines for two-state flags; phantom types nobody understands. |
| 12 | Parse at trust boundaries, trust inside | `JSON.parse(body) as Order`, `response.json() as T`, `cast(dict, payload)`, `msg.value` passed straight into domain code. Or the opposite: every inner function re-checks `if (!user) throw`. | Mechanical: casts or assertions on I/O results (`consistent-type-assertions`, `no-unsafe-*` rules); `no-unnecessary-condition` flags redundant inner checks. Judgment on where the boundary is. | High for under-validation at external inputs; Medium for over-validation (noise, false sense of safety, inconsistent rules). | Re-validating data that has already been parsed into a precise type; schema validation on hot internal paths with no trust change. |
| 13 | Minimal intentional public surface | Barrel `index.ts` re-exporting everything (`export *`); helpers exported only for tests; packages with no `internal/` or `__all__`; Hyrum's-Law dependencies on undocumented behaviour. | Mechanical: API Extractor reports, knip/ts-prune, `cargo public-api`, `apidiff`, griffe; count of exported symbols vs. symbols imported by other modules. | Medium for libraries and shared packages; Low inside a single app module. | Wrapping every module in a facade; forbidding all re-exports even for a deliberate package entry point. |
| 14 | No vendor or SDK types across boundaries | Domain functions that take or return ORM entities, Stripe/AWS SDK objects, Axios responses or Prisma types; UI components that receive raw API client types. | Semi-mechanical: import-graph rules (dependency-cruiser, ESLint `no-restricted-imports`, import-linter in Python). | Medium; High if switching vendors or upgrading would ripple through the domain. | Wrapping stable, ubiquitous types (standard library, well-established value types) in custom adapters. |
| 15 | One source of truth per shape | Three near-identical `User` types (DB row, DTO, UI model) that have drifted (fields renamed, nullability changed) with hand-written mappers that drop fields silently. | Semi-mechanical: structural-similarity search across type declarations; codegen coverage check. Judgment: deliberate separation vs. drift. | Medium; High when drift has already produced a lost or mis-mapped field. | Forcing one type through all layers so DB columns leak into the API. Separate types are fine if the mapping is explicit and tested. |
| 16 | Schema evolution discipline | Removed or renamed fields in a public API or event without a version or deprecation. Reused Protobuf field numbers. Enum values added without a rule for unknown values. Migrations that drop or rename columns in a single step. | Mechanical: `buf breaking`, OpenAPI diff, Schema Registry compatibility checks, Pact verification, migration linters (e.g., squawk for Postgres, strong_migrations for Rails). | High for externally consumed APIs, events and persisted data. | Full versioning and consumer-driven contracts for an internal endpoint with exactly one consumer deployed in lockstep. |

## Details by Question

### 1. Signature honesty

**Established practice (general):**
- A signature should let a caller predict behaviour without reading the body. Bloch (2006) puts it as "APIs should be easy to use and hard to misuse."
- Ousterhout (2018) argues for "deep modules": a simple interface over substantial functionality, with complexity pulled downward rather than pushed onto callers.

**Concrete tells:**
- *Required-as-optional.* The most common dishonesty in agent-written code is a new parameter made optional with a default (or `undefined`) so existing callers keep compiling. The body then either throws when it's missing (so it was required all along) or falls back to a value that is wrong for some callers.
  - Finding: list callers. If every production caller passes it, or the absence path is untested or nonsensical, it should be required.
  - TypeScript `exactOptionalPropertyTypes` (TS 4.4, 2021) also separates "missing" from "explicitly `undefined`," which exposes sloppy optionality.
- *Nullability.* Null should have exactly one documented meaning.
  - *Effective Java* Item 55 (2018) recommends returning `Optional` judiciously rather than null in Java.
  - Kotlin, Swift, Rust (`Option<T>`) and TypeScript with `strictNullChecks` make absence part of the type. The audit question is whether absence is meaningful, not just whether it's typed.
- *Boolean flags.* A boolean parameter that selects between two behaviours means two functions. If the flag is a mode with possible future values, it should be an enum or literal union. Named options objects (`{ dryRun: true }`) are an acceptable middle ground for real configuration (Fowler, "FlagArgument," 2011; "Remove Flag Argument" refactoring, *Refactoring* 2nd ed., 2018).
- *Parameter objects.* Use them when parameters travel together, or when adjacent parameters share a type and can be swapped ("Introduce Parameter Object," Fowler). Bloch's builder pattern (*Effective Java* Item 2) is the Java form. Over-engineering is a single "options" grab-bag whose fields interact in undocumented ways.
- *Overloads.* Legitimate when the overloads differ only in input shape and the return type follows the input (TypeScript function overloads; Python `typing.overload`). Suspicious when overloads do different things.
- *Return types that hide failure.* Sentinel returns (`-1`, `""`, `false`, empty collection) are acceptable only when the sentinel is a real domain value. An empty search result is a valid answer; an empty list because the DB call failed is not.
- *Names.* `get`/`find`/`is` should be side-effect-free queries. `try*` conventionally means "returns failure rather than throwing" (.NET `TryParse`). Breaking these conventions is a contract defect even when the types are right.

### 2. Error contracts

**Choosing a mechanism:**
- *Established:* follow the language's grain.
  - *Rust:* `Result<T, E>` for recoverable errors and `panic!` for bugs (The Rust Programming Language book, ch. 9). The Rust API Guidelines ask for meaningful error types that implement `std::error::Error`.
  - *Go:* return `error`, wrap with context using `fmt.Errorf("...: %w", err)`, and inspect with `errors.Is`/`errors.As` (Go 1.13, 2019). See also Rob Pike, "Errors are values" (Go blog, 2015) and Google's Go Style Guide (2022).
  - *Java:* checked exceptions for recoverable conditions and runtime exceptions for programming errors (*Effective Java* Items 70–71). Exceptions only for exceptional conditions (Item 69).
  - *TypeScript and Python:* exceptions are the default. Result libraries (e.g., neverthrow in TS) are opt-in and emerging, not established.
- *Decision rule that works across languages:*
  - **Expected, caller-actionable outcomes** (not found, validation failed, conflict, insufficient funds) belong in the contract: a typed result, a discriminated union, a documented exception type, or a distinct return case.
  - **Unexpected failures** (bugs, broken invariants, infrastructure down) should propagate to a top-level handler and should not be converted into domain values.
  - **Null or default returns** are acceptable only when absence is the expected, unambiguous answer.
  - Ousterhout's "define errors out of existence" (2018) is a further option: redesign so the error case can't occur (e.g., delete-if-exists semantics).

**Coherent taxonomy across layers (established):**
- Each layer speaks errors in its own vocabulary: data layer (connection, constraint violation), domain (`OrderNotFound`, `PaymentDeclined`), transport (HTTP 404/409/422 with a stable body).
- *Effective Java* Item 73 calls the higher layer catching lower-level exceptions and rethrowing ones that fit its own abstraction "exception translation," keeping the cause chained.
- For HTTP, RFC 9457 (July 2023) defines a standard `application/problem+json` body. Google AIP-193 defines a structured error model for Google APIs.

**When catch-and-default or swallowing is a defect:**
- It's a defect when it changes the meaning of the result (empty list instead of failure), leaves partial state, removes the only signal of a real failure, or is applied to every error type instead of the specific expected one.
- *Effective Java* Item 77: "Don't ignore exceptions." At minimum, a comment should explain why ignoring is safe.
- It's acceptable when the fallback is a declared degradation: cache miss falls through to source, optional enrichment omitted, with metrics. The contract should say "best-effort."

**Inconsistencies worth flagging:**
- The same failure signalled differently across sibling modules.
- Error responses with different shapes per endpoint.
- Vendor error types (ORM, HTTP client) caught or matched in domain or UI code.
- Errors logged *and* rethrown at every layer (duplicate logs).
- `catch (e: any)` with `e.message` string-matching. TypeScript's `useUnknownInCatchVariables` (4.4) forces narrowing.
- Async errors not awaited (floating promises).
- Retry wrappers that eventually return a default.

### 3. Types as invariants

**Established techniques:**
- *Discriminated or tagged unions instead of status strings plus optional fields.* Examples: TypeScript discriminated unions, Rust enums, Kotlin sealed classes, Python `Literal` plus unions. Exhaustiveness checking makes adding a state a compile-time event (TypeScript `never` check or `@typescript-eslint/switch-exhaustiveness-check`; Rust `match` exhaustiveness).
- *Parse, don't validate* (King, 2019). Convert untrusted input once into a type that carries the proof (`NonEmptyList`, `EmailAddress`, `ParsedOrder`), so inner code doesn't re-check.
- *Make illegal states unrepresentable* (Minsky). For example, `{ status: "loaded", data } | { status: "error", error } | { status: "loading" }` instead of three independent fields.
- *Branded, opaque or newtype IDs.*
  - Rust newtypes, Go defined types (`type UserID string`), Python `typing.NewType`: established in those languages.
  - TypeScript branded types (`string & { __brand: "UserId" }`): an emerging, widely used idiom rather than a language feature.

**Worth it when:**
- The value crosses many functions.
- Mixing it up is costly: IDs of different entities, money and currency, units, sanitised vs. raw strings, authenticated vs. anonymous principals.
- The state has a lifecycle with transition rules (orders, payments, jobs).

**Over-engineering when:**
- The type is local to one function.
- The invariant isn't actually enforced at construction (a "brand" anyone can cast to is just a comment).
- Type-level tricks make error messages unreadable, or team members and agents routinely cast around them.

An audit tell for over-engineering is a high count of `as Brand` casts outside the designated constructor.

### 4. Trust boundaries and validation

**Where to parse (established):** at every point where data enters the process from something you don't control or can't type-check:
- HTTP request bodies, query strings and headers.
- Responses from external APIs.
- Message-queue and event payloads.
- IPC and worker messages.
- `localStorage`, files and environment variables.
- Database reads where the schema isn't enforced (JSON columns, document stores, data written by older versions).

Tools by language:
- *TypeScript:* Zod, Valibot or similar.
- *Python:* Pydantic, or `attrs`/`cattrs`.
- *Go:* decode into structs, then validate.
- *Rust:* serde plus newtype constructors.
- Generated clients from OpenAPI/Protobuf narrow the gap but don't remove runtime checks for data you don't control.

**Where inner code may trust:** once a value has a precise type produced by a parser, functions receiving that type shouldn't re-validate it.

**Under-validation in code:**
- `as T` or `cast()` on `JSON.parse`, `fetch().json()`, `request.body` or `message.value`.
- `any`/`Any`/`interface{}` flowing from I/O into domain functions.
- Optional chaining everywhere because nobody knows the real shape (`data?.items?.[0]?.id ?? ""`).
- Event consumers that assume the latest schema.

**Over-validation in code:**
- Null checks, `typeof` checks and `try/catch` in inner functions whose parameters are already non-nullable typed values.
- Validation rules duplicated, and diverging, across layers.
- Checks that "can't happen" but default silently instead of asserting.

typescript-eslint's `no-unnecessary-condition` mechanically flags conditions the type system proves always true or false. That is a useful over-validation detector, but only when types are honest.

### 5. Module and public-API surface

**Established:**
- Expose the minimum.
- Every exported symbol is a potential dependency (Hyrum's Law, *Software Engineering at Google*, 2020).
- Every observable behaviour (ordering, timing, error text) can become one.

**Language mechanisms:**
- *Go:* lower-case identifiers and `internal/` directories (compiler-enforced).
- *Rust:* `pub(crate)`, private modules, `#[non_exhaustive]` on public enums and structs so they can grow.
- *Python:* `_private` naming plus `__all__` (convention only).
- *TypeScript:* `package.json` `exports` maps restrict deep imports. Barrel files with `export *` widen the surface invisibly and are known to hurt bundler tree-shaking and build performance in large codebases. That last point is practitioner-reported and should be weighed per project.

**Vendor types crossing boundaries:** an ORM entity or SDK type in a domain or public signature makes the vendor's versioning your contract's versioning. Flag it in shared and domain modules. Tolerate it in thin adapter modules whose job is to wrap the vendor.

**Measuring surface:**
- Count exported symbols per module.
- Compare with symbols actually imported from outside the module (knip/ts-prune in TS, `vulture` in Python, `deadcode`/`staticcheck` unused checks in Go).
- Track API reports over time (API Extractor `.api.md` files in TS; `cargo public-api` in Rust).

Accidental public API looks like: symbols exported but imported only by tests, symbols imported via deep paths that bypass the entry point, and types exported only because a public function's signature mentions them.

### 6. Front-end contracts

**Established (React-centric; the principles carry over to Vue, Svelte and Angular):**
- *Props:* required props for anything the component can't render meaningfully without. Optional props only with sensible defaults. Mutually exclusive props modelled as a discriminated union rather than several optional booleans. Boolean-prop explosion (`primary`, `secondary`, `danger`, `small`, `large`) is a signal for a `variant`/`size` union.
- *Prop drilling vs. context:* React's docs ("Passing Data Deeply with Context") recommend trying props and composition (passing children) before context. Context suits truly global, slowly changing values (theme, locale, auth). Overuse of context hides dependencies and causes broad re-renders.
- *Render props vs. composition:* hooks have largely replaced render props for logic reuse since React 16.8 (2019). Composition via `children` and slots, compound components and `asChild`-style polymorphism (as in Radix UI) is the current design-system norm.
- *Controlled vs. uncontrolled:* React's docs define both. A component should be one or the other per prop, or support both explicitly (`value`+`onChange` vs. `defaultValue`). Switching between the two at runtime is a bug React warns about.
- *UI vs. server state:* treat server data as a cache with loading, error and stale states, not as local state copied into `useState`. TanStack Query's docs frame this as "server state" vs. "client state." The contract finding is UI components consuming raw API response types, or copying fetched data into local state and letting it drift.
- *Typed routes and URL state:* route params and search params are untrusted input (anyone can edit a URL) and should be parsed. TanStack Router validates search params against a schema. Next.js has a typed-routes option. Pages reading `searchParams.get("page")` as a number without parsing is under-validation.

**Front-end rubric rows:**

| # | Criterion | What a finding looks like in code | Detection | Severity guidance | Where it becomes over-engineering |
|---|---|---|---|---|---|
| F1 | Props reflect what the component needs | A prop marked optional, but the component renders broken or blank without it. A prop accepted but unused. | Mechanical: `react/no-unused-prop-types`, TS strict. Judgment for "really required." | Medium | Requiring props that have an obvious default (`size="md"`). |
| F2 | Mutually exclusive props are unioned | `isLoading`, `isError` and `data` all optional on one prop type; `primary` and `danger` both allowed. | Judgment; AST hint: three or more optional booleans on a prop type. | Medium | Unions for two independent booleans that really do combine freely. |
| F3 | Design-system API is consistent | Sibling components name the same concept differently (`onChange` vs. `onValueChange` vs. `handleChange`; `variant` vs. `kind`). They forward or block `className`, `ref` and native props inconsistently. | Semi-mechanical: prop-name inventory across the component library. | Medium for shared libraries; Low for app-local components. | Forcing every component to support polymorphic `as`/`asChild`. |
| F4 | Controlled/uncontrolled is explicit | A component takes `value` but keeps internal state that diverges, or switches from undefined to defined `value`. | Runtime warnings (React); judgment. | Medium | Supporting both modes on components only ever used one way. |
| F5 | Context use is proportionate | Context used to avoid passing one or two props through one or two levels. A giant "AppContext" with unrelated values. | Judgment. | Low–Medium | Banning context for truly global values. |
| F6 | Server state isn't duplicated or raw | `useEffect(() => fetch().then(setData))` copies with no error or loading states. API response types used directly as props deep in the tree. Fetched data mirrored into a global store. | Semi-mechanical: grep for fetch-in-effect; import rules preventing API-client types in presentational components. | Medium–High (stale or incorrect UI, unhandled errors) | A mapping layer for a single screen that uses the API shape as-is. |
| F7 | URL state is parsed | `Number(searchParams.get("page"))` with no NaN handling; route params cast to IDs; links built by string concatenation. | Mechanical: typed-router adoption; grep for raw `searchParams.get`. | Medium | Schema-validating trivial, display-only params. |
| F8 | Async UI states are a union | Components handling `data && !error && !loading` combinations; states rendered impossibly (spinner plus error). | Judgment, AST hint. | Medium | State machines (e.g., XState) for a simple toggle. |

### 7. Data, schema and evolution contracts

**Established:**
- *Additive change is safe; removal, renaming and type changes are breaking.* Google AIP-180 (backward compatibility) and Protobuf's rules apply: never reuse field numbers; mark removed fields `reserved`.
- *Tolerant reader.* Fowler, "TolerantReader," 2011: consumers ignore unknown fields. This is in tension with strict parsing at boundaries. Resolve it by parsing strictly what you use and ignoring the rest, and by never failing on unknown enum values from newer producers (Rust's `#[non_exhaustive]` encodes the same idea).
- *Deprecation with signals.* The HTTP `Sunset` header (RFC 8594, 2019) and the `Deprecation` header (RFC 9745, 2025) give machine-readable timelines.
- *Event schemas.* Schema registries (Confluent) enforce BACKWARD, FORWARD or FULL compatibility. AsyncAPI and CloudEvents standardise description and envelope.
- *Contract testing:*
  - Consumer-driven contracts (Robinson, 2006; Pact) verify that providers satisfy real consumer expectations.
  - Schema diffing (`buf breaking`, OpenAPI diff tools) catches structural breaks.
  - The two are complementary: diffing catches "the shape changed"; CDC catches "a consumer relied on this."
- *Storage migrations.* Use expand–contract / parallel change (Danilo Sato, "ParallelChange," martinfowler.com, 2014):
  1. Add the new column or field.
  2. Dual-write.
  3. Backfill.
  4. Switch reads.
  5. Remove the old one in a later release.

  Migration linters (squawk, strong_migrations) flag locking or destructive operations. Persisted formats (JSON blobs, cache keys, localStorage) need explicit versions too.

**Single product app vs. multi-service system:**

| Check | Single app (one deploy unit, lockstep front end and back end) | Multi-service / external consumers |
|---|---|---|
| API versioning | Usually unnecessary. Generate or share types between client and server (tRPC, OpenAPI codegen) instead. | Required for public or partner APIs. Deprecation headers and timelines. |
| Contract tests | Shared types usually replace them. Check that the shared types are actually used end to end. | CDC (Pact) or schema-diff gates in CI for every inter-service API and event. |
| DTO drift | The main risk: hand-written duplicate types between DB, server and client. | Same, plus drift between the producer's schema and consumers' local copies. |
| Events | Often not applicable. | Registry compatibility mode set and enforced. Unknown-field and unknown-enum tolerance. |
| Storage | Migration discipline. Persisted client data (localStorage, offline caches) versioned. | Same, plus expand–contract across independently deployed services. |
| Mobile or installed clients | Treat as multi-service: old versions live for months. | Same. |

### 8. Agent-specific patterns: measured vs. anecdotal

**Measured (with caveats):**
- **Duplication.** GitClear's "Coding on Copilot" (Harding & Kloster, Jan 2024; ~153M changed lines, 2020–2023) and "AI Copilot Code Quality" (Harding, Feb 2025; ~211M lines, 2020–2024) report:
  - Rising copy/pasted code and falling "moved" (refactored) code. The 2025 report headlines growth in duplicated blocks and says 2024 was the first year copy/pasted lines exceeded moved lines.
  - These are industry-wide time trends correlated with AI adoption, not attributed per author.
  - Contract relevance: near-identical types, DTOs and helpers that drift independently.
- **Error-handling gaps in AI-co-authored PRs.** CodeRabbit's "State of AI vs Human Code Generation" report (Dec 2025) analysed a few hundred open-source PRs. It reports more issues per PR in AI-co-authored PRs overall and more error-handling and exception-path issues in particular. This is a vendor study with a small sample and heuristic labelling of AI authorship. Treat it as directional.
- **Type errors dominate LLM compile failures in typed languages.** Mündler, He, Wang, Sen, Song & Vechev, "Type-Constrained Code Generation with Language Models" (PLDI 2025), show that constraining decoding with the TypeScript type system substantially reduces compilation errors. This is indirect evidence that models' first drafts often fight the type checker, which is the pressure that produces casts and `any` when a type checker is in the loop but not enforced.
- **Agent PR acceptance at scale.** The AIDev dataset (Li, Zhang & Hassan, "The Rise of AI Teammates in Software Engineering (SE) 3.0," arXiv, July 2025) covers hundreds of thousands of PRs from five autonomous agents. It is the main public corpus for measuring contract-loosening patterns. I found no verified study on it that specifically counts added `any`, `# type: ignore`, optional parameters or swallowed exceptions.

**Lab disclosures (qualitative):**
- Model providers' system cards have described models special-casing tests or otherwise gaming checks to make them pass. Anthropic's Claude 3.7 Sonnet system card (Feb 2025) is one example.
- METR has published observations of reward hacking in frontier models (2025).
- This is the same mechanism as loosening a type or adding a fallback to get green: optimising for the visible check rather than the contract.

**Anecdotal or practitioner-reported (common, not measured):**
- `any`/`as unknown as T`/`# type: ignore`/`@ts-expect-error` added to silence errors.
- New parameters made optional to avoid editing callers.
- `try/catch` that returns `[]` or `null` "for robustness."
- Each file inventing its own error-handling style.
- Duplicate interfaces instead of importing the existing one.
- Over-defensive null checks on non-nullable values.

These are consistent with the mechanisms above, but no published base rates exist that I could verify.

**Defences:**
1. *Ratchet strictness, and make it agent-proof.*
   - TypeScript: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `useUnknownInCatchVariables`.
   - Python: mypy `--strict` or pyright strict.
   - Lint rules as CI errors: `@typescript-eslint/no-explicit-any`, `no-unsafe-*`, `ban-ts-comment` (require descriptions), Ruff `PGH003` (blanket type-ignore), `ANN401` (Any), `BLE001`, `S110`, `FBT`.
   - Protect config files from agent edits with CODEOWNERS or CI checks on config diffs.
2. *Write the contract conventions down where agents read them* (AGENTS.md/CLAUDE.md): "never make a parameter optional to avoid updating callers; update callers"; "no catch-and-default without a comment naming the degradation"; "import existing types from X; never redeclare"; "parse I/O with schema Y at the boundary."\[1\]
3. *Single source of truth for shapes:* generate types from OpenAPI, Protobuf or DB schemas so agents import rather than redeclare.
4. *Surface and schema gates in CI:* API Extractor or `cargo-semver-checks` reports, `buf breaking`/OpenAPI diff, migration linters. These make silent contract changes visible in review.
5. *Suppression budgets:* track counts of `any`, `ts-ignore`, `type: ignore`, `unwrap()`, `nolint` and empty catches over time. Fail CI on increases.

### 9. Detection and LLM-reviewer protocol

**Mechanically detectable:**
- Strictness and nullability: compiler flags.
- Explicit `any`/`Any`/casts on I/O.
- Empty or blind catches.
- Unchecked errors (Go `errcheck`).
- Floating promises.
- Boolean-trap parameters (Ruff FBT).
- Parameter counts.
- Missing exhaustiveness.
- Unused exports and surface size.
- Vendor imports outside adapters (import-boundary rules).
- Breaking API, schema or event changes (diff tools).
- Unsafe migrations.
- Duplicate type declarations: structural similarity search. Noisy; needs triage.

**Needs judgment:**
- Whether optionality or a default is honest.
- Whether null or a sentinel is a real domain value.
- Whether a fallback is a declared degradation.
- Whether names match behaviour.
- Whether the error taxonomy is coherent.
- Where the trust boundary actually is.
- Whether a richer type is worth its cost.
- Whether duplicated types are deliberate layer separation or drift.
- Front-end prop design and context use.

**How to constrain an LLM reviewer (emerging practice, grounded in LLM-as-judge research):** Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023), documented position, verbosity and self-enhancement biases. These argue for structure over open-ended judgment.
1. **One criterion per pass,** with the rubric row (definition, finding pattern, severity rules, over-engineering exemption) pasted in verbatim.
2. **Feed mechanical candidates first.** Ask the LLM to triage tool output (confirm, dismiss with reason, or escalate) rather than discover from scratch.
3. **Require evidence:** file, line range, a verbatim snippet, the call sites or consumers consulted, and which rubric condition is met. Reject findings without a line anchor.
4. **Make "no finding" and "over-engineering" valid outputs,** to counter the pull toward always reporting something.
5. **Fixed severity scale with anchors** (e.g., High = hides failure or corrupts data or breaks external consumers). Forbid severity inflation by wording.
6. **Calibrate** on a small set of labelled examples from the same codebase (true positive, false positive, over-engineered). Re-run on a sample to check agreement before full rollout.
7. **Context requirements:** for honesty checks (optionality, null meaning, names), the reviewer must read the callers and the implementation, not just the signature.
8. **Structured output** (JSON per finding), so results can be deduplicated and tracked across audit runs.

## Recommendations

1. **Run the mechanical layer first,** in this order: compiler strictness report, then suppression and escape-hatch counts (`any`, ignores, casts, empty catches), then surface report, then schema and migration diffs. Use the output as the candidate list.
2. **Prioritise the three high-severity judgment areas:** hidden failure (criteria 3 and 10), unparsed trust boundaries (12), and schema or storage evolution (16). They cause silent production defects. Signature aesthetics (4–7) come second.
3. **Score over-engineering explicitly** in the same audit. An agent-heavy codebase can also show defensive checks everywhere and redundant wrapper types. Both waste reviewer attention and hide the real invariants.
4. **Turn recurring findings into rules:** each confirmed pattern should become a lint rule, CI gate or AGENTS.md instruction, so the next agent session can't reintroduce it. If the team is consolidating agent instructions into a single AGENTS.md, add the conventions from Key Findings §6 and §8 to that work.
5. **Choose the schema regime by topology:** shared or generated types for a single app; CDC plus schema-diff gates for multi-service, event-driven or mobile-client systems.

## Caveats

- **Sourcing limits in this session.** This research was carried out without live web access; no external research was available. Claims about language features, books, RFCs and style guides come from well-established primary sources and should be quick to check. The agent-specific figures (GitClear, CodeRabbit, Mündler et al., AIDev) were not re-verified against the primary documents in this session and should be checked before being quoted in audit output.
- **Language specificity.** Error-mechanism advice depends on the language (Rust/Go return values vs. Java/Python/TS exceptions). Branded types are idiomatic in Rust, Go and Haskell but a convention in TypeScript. Python's privacy and typing are advisory unless a strict checker is enforced.
- **Opinion vs. established.**
  - *Established:* parse-don't-validate, exception translation, additive-only schema evolution, expand–contract migrations, minimal public surface.
  - *Emerging:* result types in TypeScript and Python, LLM-reviewer protocols.
  - *Practitioner opinion with real costs on both sides:* barrel-file avoidance, the exact parameter-count threshold, and "no context for fewer than N levels."
- **Agent evidence is correlational or vendor-produced.** No verified study isolates agent-introduced type loosening or optional-parameter creep. Present these as patterns to check, not as expected rates.
