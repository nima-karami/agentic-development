# Rubric — contract design

A contract is every surface one piece of code promises another: signatures, types,
error behavior, module public APIs, component props, API and event schemas, storage
formats. **A contract defect exists when the surface a caller sees permits, promises,
hides or couples something materially different from what the implementation
supports.** The strongest findings are contradictions, not style.

Every finding in this dimension carries:

- a **primary anchor** at the declared contract (`path:line`);
- a **supporting anchor** in the implementation, a caller, a schema or a semantic peer;
- a **caller-visible counterexample**: "the declaration permits X, yet Y happens."
  No counterexample, no finding.

## The failure-mechanism rule

Expected, caller-actionable outcomes belong in the contract (a result, a union, a typed
exception, a distinct return case). Unexpected failures — bugs, broken invariants,
infrastructure — propagate to a top-level handler and are not converted into domain
values. Null is acceptable only when absence is the normal, unambiguous answer. Follow
the language's grain: do not demand result types in an exception-grained language.

## Rows

### C1 · Hidden failure
- **Finding:** a catch that returns `[]`, `null`, `false` or a default; a resolved
  promise carrying a fake value; an error result ignored.
- **Detection:** returns inside catch and error branches; catch-to-default chains;
  discarded error values.
- **Severity:** High; **Critical** when it follows or masks a write and the caller
  proceeds as if it committed.
- **Over-engineering line:** a declared, tested, observable best-effort fallback is a
  legitimate contract.

### C2 · Unparsed trust boundary
- **Finding:** a cast or untyped value flowing inward from HTTP, storage, a queue, IPC,
  an external API or the URL; a validator that returns a boolean while code goes on
  using the unrefined value. Persisted data is a boundary — older versions wrote it.
- **Detection:** enumerate ingestion points first (the trust boundaries), trace the
  first consumer, flag casts with no parse in between.
- **Severity:** High.
- **Over-engineering line:** re-parsing values inner code already constructed.

### C3 · Incompatible evolution
- **Finding:** a field removed, renamed or retyped; a reused field number; a required
  field added; an enum extended with no unknown-value rule; a destructive migration
  while the previous version still reads the column.
- **Detection:** diff schemas against the baseline; compare migration order with the
  deploy model (lockstep, rolling, independent consumers, mobile clients).
- **Severity:** Critical with live consumers or persisted data; Medium for a lockstep
  single app.
- **Over-engineering line:** versioning and contract tests for a single-consumer
  lockstep endpoint.

### C4 · Dishonest optionality
- **Finding:** an optional parameter or field the body immediately guards, asserts or
  dereferences; a constructor that allows omission though no valid object exists
  without the value; null meaning absent, error and not-loaded at once; a parameter
  changed from required to optional in history without callers being updated.
- **Detection:** optional + immediate guard; required → optional diffs; nullable
  returns with several meanings.
- **Severity:** High when invalid objects cross layers; Medium internally.
- **Over-engineering line:** flagging an optional only because every current caller
  passes it — intentionally supported omission is fine.

### C5 · Escape-hatch density
- **Finding:** untyped values, type assertions, non-null assertions and ignore-comments
  clustered at boundaries.
- **Detection:** count per subsystem and at ingestion points; trend against baseline.
- **Severity:** Medium; High at trust boundaries.
- **Over-engineering line:** demanding zero.

### C6 · Incoherent error model
- **Finding:** the same failure class throws in one module, returns null in a sibling
  and `{success:false}` in a third; driver, ORM or SDK errors reach the API or UI;
  error bodies differ per endpoint; translation drops a distinction callers need
  (conflict vs unavailable).
- **Detection:** per-layer inventory of throw / result / null; compare semantic peers;
  find vendor error types above the adapter layer. Test: would swapping the vendor
  change unrelated callers' branches?
- **Severity:** High at public boundaries or when callers branch on retry or
  transaction; Medium inside.
- **Over-engineering line:** demanding identical syntax across layers; consistency
  means semantic correspondence.

### C7 · State as strings
- **Finding:** `status: string` with optional fields; independent loading / error /
  data flags permitting contradictions; interchangeable primitive IDs or money as
  floats; the same guard repeated in inner code because the type does not carry it.
- **Detection:** comparisons on a status field; non-exhaustive switches; clusters of
  three or more mutually dependent optionals; adjacent same-typed ID parameters.
- **Severity:** High for identity, money, authorization, lifecycle; Low for local
  values.
- **Over-engineering line:** branded types for every string; a type-level state
  machine for two states; brand casts scattered outside the constructor.

### C8 · Accidental public surface
- **Finding:** wildcard re-export barrels; helpers exported only for tests; vendor
  types in exported signatures; symbols consumed only through deep imports.
- **Detection:** exported vs externally imported symbols; API-surface snapshot diff.
- **Severity:** High for published libraries; Medium in a monorepo; Low in a private
  app.
- **Over-engineering line:** a universal export cap; penalizing barrels for existing.

### C9 · Data-shape drift
- **Finding:** several hand-written near-identical shapes with diverging optionality; a
  mapper that silently drops a field.
- **Detection:** structural similarity across type declarations; mapper field
  coverage.
- **Severity:** Medium; High once a field has already been lost.
- **Over-engineering line:** collapsing every layer into one model leaks storage
  columns into the API. Separate shapes with an explicit mapping are fine.

### C10 · Names that lie
- **Finding:** `get` / `is` / `find` that writes or creates; `try` that throws; `parse`
  that returns the unrefined value.
- **Detection:** query-named functions that reach writes or the network, then a read
  of the body.
- **Severity:** Medium; High when the hidden effect is destructive or external.
- **Over-engineering line:** synonym renaming for its own sake.

### C11 · Flag and positional parameters
- **Finding:** `f(x, true, false)`; adjacent same-typed parameters; overloads that
  change meaning.
- **Detection:** boolean parameters with literal arguments at call sites.
- **Severity:** Low; High when the flag switches safety, persistence or transaction
  semantics.
- **Over-engineering line:** an options object for two parameters; splitting a named
  configuration flag.

## Front-end rows

### CF1 · Props honesty and variants
- **Finding:** an optional prop the body dereferences; an accepted prop nothing uses;
  boolean variant props (`primary`, `danger`, `loading`) or optional `href` +
  `onClick` allowing impossible combinations.
- **Detection:** optional prop + unguarded use; count of boolean or optional props per
  component; branching on mutually exclusive props.
- **Severity:** Medium; High in a shared design system.
- **Over-engineering line:** requiring props with obvious defaults; a union for
  booleans that genuinely combine.

### CF2 · Dual authority on inputs
- **Finding:** a value prop plus internal state that can diverge; a prop copied into
  state by an effect.
- **Detection:** local state seeded from a value prop; prop-to-state copy effects.
- **Severity:** High for data entry; Medium otherwise.
- **Over-engineering line:** supporting both a value and a default value is fine; dual
  ownership is the defect.

### CF3 · URL state unparsed
- **Finding:** a search param cast straight to a domain type with no handling for
  absent or malformed values; parse and default logic duplicated per page. A typed
  route string is not a valid domain ID — route typing is syntax, parsing is meaning.
- **Detection:** raw search-param reads followed by casts.
- **Severity:** High when the URL drives business operations; Medium otherwise.
- **Over-engineering line:** schema-validating cosmetic params.

### CF4 · UI ↔ server-state contract
- **Finding:** raw API response types as presentational props; fetched data copied into
  local or global state; "no data" meaning initial, empty and failed at once.
- **Detection:** an import rule forbidding API-client types in presentational
  components; state-shape analysis.
- **Severity:** Medium to High.
- **Over-engineering line:** a mapping layer for one screen that uses the API shape
  as-is.

### CF5 · Design-system API inconsistency
- **Finding:** sibling components naming one concept differently (`onChange` /
  `onValueChange`, `variant` / `kind`); inconsistent forwarding of class names, refs
  and native props.
- **Detection:** prop-name inventory across the component library.
- **Severity:** Medium to High for a shared library; Low app-local.
- **Over-engineering line:** polymorphic escape hatches on every component.
