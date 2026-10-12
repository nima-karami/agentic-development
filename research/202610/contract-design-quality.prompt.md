# Research prompt: judging contract design in an existing codebase

## Context

The findings will feed one dimension of an audit of a whole codebase as built,
where most of the code is written by coding agents: **contract design**, the
shape and honesty of the interfaces between parts of the system. Architecture
boundaries are already covered. What's needed are criteria a reviewer can apply
to existing code and anchor to a line.

By "contract" I mean every surface one piece of code promises another:
function and method signatures, types, error behaviour, module public APIs,
component props, API and event schemas, and data and storage formats.

## Questions to answer

1. **Signature honesty.** What makes a signature tell the truth? Cover
   required vs. optional parameters (including a required value typed as
   optional to avoid fixing callers), nullability, boolean-flag parameters,
   parameter objects vs. positional arguments, overloads, return types that
   hide failure, and names that match behaviour.
2. **Error contracts.** How should a codebase decide between exceptions,
   result or either types, error codes, and null or default returns? What makes
   an error taxonomy coherent across layers? How should errors be translated at
   boundaries, and when is catch-and-default or swallowing a defect? What
   inconsistencies are worth flagging in an audit?
3. **Types as invariants.** When should a type encode an invariant (branded or
   opaque types, discriminated unions and state machines instead of status
   strings, parse-don't-validate, making illegal states unrepresentable)? Where
   is this worth it and where is it over-engineering?
4. **Trust boundaries and validation.** Where should data be validated and
   parsed (HTTP, storage, external APIs, IPC, message queues, user input), and
   where may inner code trust it? What do over-validation (defensive checks
   everywhere) and under-validation (raw payloads flowing inward, casts instead
   of parsing) look like in code?
5. **Module and public-API surface.** How small should a module's public
   surface be? Barrel files and re-exports, leaking internals, vendor and SDK
   types crossing boundaries, Hyrum's law. How do you measure surface size and
   detect accidental public API?
6. **Front-end contracts.** Component props design (required vs. optional,
   prop drilling vs. context, render props vs. composition, controlled vs.
   uncontrolled), the contract between UI and server state, design-system
   component APIs, and typed routes and URL state.
7. **Data, schema, and evolution contracts.** API and event schema design,
   versioning and backward compatibility, deprecation, contract testing
   (consumer-driven and schema diffing), DTO drift between layers, and
   storage-migration discipline. What should an audit check for in a single
   product app vs. a multi-service system?
8. **Agent-specific patterns.** What is the current evidence on how coding
   agents shape contracts: loosening types to make code compile, optional
   parameters added to avoid touching callers, catch-and-default fallbacks,
   duplicated near-identical types, inconsistent error handling across files?
   What practices or tooling counter them? Separate measured findings from
   anecdote.
9. **Detection.** For each criterion above, what can be detected mechanically
   (type-checker strictness, lint rules, API-surface diffing, schema diffing,
   AST queries) and what needs judgment? How should an LLM reviewer be prompted
   or constrained to judge contracts consistently?

## Evidence rules

- Cite named, checkable sources: language and type-system documentation,
  established books and essays on API and interface design, published style
  guides from large engineering organizations, contract-testing literature, and
  2025–2026 papers on agent-written code. Date each claim.
- Separate **established practice**, **emerging**, and **opinion**. Note where
  advice is language-specific (TypeScript, Python, Rust, Go, and so on) and
  where it is general.
- Don't invent benchmarks, frameworks, product names, or statistics.

## Output I want

- A short answer up front: the ten contract-design checks that matter most in
  an audit.
- A rubric table: criterion, what a finding looks like in code, mechanical or
  judgment, severity guidance, and where the criterion becomes over-engineering.
- A front-end section with its own rubric rows.
- Agent-specific failure patterns with defences.
- Language-agnostic phrasing, with language-specific examples kept separate.

## Out of scope

- System-level decomposition and service boundaries (already covered).
- Reviewing a single diff or PR (already covered).
- Security-specific API hardening beyond validation at trust boundaries.
