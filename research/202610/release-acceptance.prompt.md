# Research prompt: release acceptance review of a built, mostly agent-written system

## Context

The findings will feed a **release acceptance review**: a structured way to understand,
validate and formally accept a built system before release, when line-by-line code
review is impractical because most of the code was written by coding agents. It is
organized around system behaviour and engineering risk, and ends with an explicit
acceptance decision backed by documented findings, required changes, tests, and
accepted risks.

It sits after two existing reviews and uses their output as input: a **codebase audit**
(architecture conformance, gate integrity, contract design, bloat, security and
performance, judged by fresh-context agents from deterministic tool output, with a
stored baseline) and **runtime QA** (driving the built system and reporting what was
observed). Reviewing a design before it is built, reviewing a single diff, and general
software-testing tutorials are out of scope.

The method principles are fixed: anything a tool or script can compute is computed by
one, never estimated by a model; reviewers judge in fresh contexts, isolated from
author narration and from each other's conclusions; serious findings go through an
adversarial pass that tries to refute them; every finding carries an anchor (code
location, test, measurement or trace) and a concrete failure path; humans own the
acceptance decision. What's missing is the content of the review and how to verify
behaviour, not just structure.

## Questions to answer

1. **Prior art.** What do established release and readiness reviews look like —
   production readiness reviews, operational readiness reviews, launch reviews, and
   architecture evaluations of an implemented system (ATAM-style)? What do they
   require, who attends, what evidence counts, and what has changed in 2026 for
   systems where agents wrote most of the code?
2. **System overview for review.** What is the minimum overview a review needs —
   architecture views, key APIs and data models, external dependencies, critical
   flows, deployment and rollback, known issues — and how much of it can be recovered
   from the code, build and history rather than written by hand?
3. **Critical flows.** How should reviewers choose the 10–15 flows that matter
   (revenue, data, security, frequency, irreversibility), and trace each through the
   actual code — happy path and failure paths? What tooling helps (call graphs,
   distributed traces, logs from a driven run, sequence reconstruction)? How is
   coverage of a flow judged?
4. **Invariants.** How do teams identify the invariants that must always hold
   (idempotency, conservation of money or inventory, valid state transitions,
   uniqueness, ordering), record them, and verify that each is actually enforced —
   by tests that would fail if it broke, property-based or model-based testing,
   runtime assertions, database constraints, or type-level encoding? What makes an
   invariant test strong rather than nominal?
5. **Correctness and concurrency.** Review methods for race conditions, duplicate
   execution (double submit, retried requests, redelivered messages), stale state,
   non-idempotent operations and event-ordering assumptions in a built system. Which
   are detectable statically, which need targeted tests (concurrency, fault
   injection, deterministic simulation), and what is affordable in a review?
6. **Data integrity.** How to review sources of truth, partial writes, distributed
   operations that succeed in one system and fail in another (e.g. a charge succeeds
   but the local record fails), reconciliation, duplicate detection, schema and unit
   consistency end to end (client SDK to service to storage), and precision mistakes.
7. **Error handling and recovery.** How to judge whether expected failures produce
   controlled behaviour and whether the system recovers without manual data repair:
   retry safety after a timeout where the backend completed, retry storms, swallowed
   errors, irrecoverable loading or error states, and whether a user or operator can
   diagnose and resolve a failure.
8. **Operational readiness.** What should be checked before release: documented
   configuration, safe and reversible migrations, reproducible builds, version
   visibility in production, health signals, alerting, runbooks, rollback paths, and
   whether someone other than the original engineer can diagnose an incident.
9. **Testing and validation evidence.** How should a review judge the test suite as
   evidence for acceptance — coverage of critical flows and invariants rather than line
   coverage — and when should reviewers build their own validation tools (API
   harnesses, fault injectors, debug views)?
10. **Agent-specific patterns.** What is the current (H2 2026) evidence on failure classes that
    agent-written systems carry into release — e.g. missing idempotency, happy-path-only
    flows, inconsistent error handling across a flow, fabricated or nominal tests for
    invariants? Separate measured findings from anecdote. How can agents assist the
    review itself (flow reconstruction, invariant mining, adversarial test generation)
    without biasing it?
11. **The acceptance decision.** How do mature teams structure the decision: severity
    gates (which findings block), accepted-risk registers (owner, rationale, expiry,
    compensating controls), override and escalation paths, conditional acceptance,
    re-review after fixes on the release candidate, and what is recorded for later
    incidents?
12. **Scaling the review.** How should depth scale with the system's stakes and
    load profile (internal tool, consumer app at a few thousand users, high-concurrency
    or money-handling service)? What can be skipped safely, and what never can?

## Evidence rules

- **Time window.** For anything about agents, agent-written code, AI-assisted review,
  and current tooling, prioritize sources from 2026, especially the second half
  (July–October 2026); use older material only as a baseline for what changed, and say
  so. Foundational, first-principles material — readiness review practice, invariant
  and concurrency testing, reliability engineering, data-integrity patterns — may come
  from any year; cite the original or the authoritative current edition.
- Cite named, checkable sources: published readiness and launch review practices from
  engineering organizations, SRE and reliability literature, testing research
  (property-based, model-based, concurrency and fault-injection testing), standards
  where relevant, and H2 2026 papers and first-hand accounts on agent-written systems.
  Date each claim.
- Separate **established practice**, **emerging**, and **opinion**. Mark every
  numeric threshold or checklist count with its source.
- Treat vendor effectiveness claims as unverified unless independently replicated.
- Don't invent benchmarks, frameworks, product names, or statistics.

## Output I want

- A short answer up front: how to run a release acceptance review of an agent-built
  system, in ten lines.
- A step-by-step method with inputs, outputs, and where a human must judge, including
  what it takes from a prior codebase audit and runtime QA.
- A rubric table per area (flows, invariants, correctness and concurrency, data
  integrity, recovery, operational readiness, test evidence): criterion · what a
  finding looks like · static, tested, or needs a driven run · the tool or technique
  that produces the evidence · severity guidance by stakes · where it becomes
  over-engineering.
- An invariant record format and a critical-flow record format.
- The acceptance decision structure: blocking rules, the accepted-risk record, the
  re-review loop.
- Agent-specific failure patterns with defenses, and how agents can assist the review
  without biasing it.

## Out of scope

- Reviewing a design before it is built (already covered).
- Reviewing a single diff or PR (already covered).
- Structural codebase health — architecture conformance, gates, contracts, bloat,
  security and performance rubrics (already covered by the codebase audit).
- Production load-testing programs, penetration testing, and compliance certification.
