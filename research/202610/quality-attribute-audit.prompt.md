# Research prompt: auditing security and performance of an existing, mostly agent-written codebase

## Context

The findings will feed two new dimensions of an existing codebase audit: **security**
and **performance**. The audit already covers architecture, gate respect, contract
design and verbosity. It runs on a codebase as built, mostly written by coding agents,
and starts from a **codebase profile**: what the system is, its platforms, load,
constraints, stakes and two or three dominant quality attributes (for example "100k
concurrent players" or "low-end mobile clients"). The profile decides which criteria
apply and how severe a finding is. Reviewing a single diff, designing a system, and
general secure-coding or performance-engineering tutorials are out of scope.

The audit's method is fixed: deterministic extraction first, then a written rubric,
then model judgment on the candidates, then a fresh-context verifier that tries to
refute serious findings. **Anything a tool or script can compute is computed by one,
never estimated by a model**, and tools must run safely: pinned versions, nothing
installed into the audited repo, read-only or in an isolated worktree, fully local
unless approved. Every finding needs an anchor (`path:line`, a scan output, or a
measurement) and a concrete failure path. What's missing is the content of the two
new rubrics and the tools that feed them.

## Questions to answer

1. **From profile to criteria.** How do practitioners turn a system's quality
   attributes and context (load, platform, device class, network, deploy model, data
   sensitivity, money, auth) into concrete security and performance criteria for an
   audit? Cover quality-attribute scenarios, threat modeling at audit time (for
   example STRIDE or attack trees applied to existing code), performance budgets, and
   capacity targets. What is the minimum profile needed before either dimension can be
   judged at all?
2. **Security in an as-built codebase.** Which checks belong in an audit rubric rather
   than in a scanner: trust boundaries and the threat model, authorization placement,
   secrets handling, input parsing at ingestion points, dependency and supply-chain
   posture, sandboxing and process isolation (desktop/Electron, mobile, server),
   logging of sensitive data, and the coverage and configuration of existing scanners
   (static analysis, dependency, secret scanning)? For each: what a finding looks
   like, what is mechanically detectable, what needs judgment, and how severity should
   scale with the profile's stakes.
3. **Security failure patterns specific to agent-written code.** What is the current
   evidence (2025–2026) on the security weaknesses coding agents introduce or
   preserve — and on which ones a scanner already catches versus which need review?
   Separate measured findings from anecdote.
4. **Performance from static reading.** Which performance problems can an audit find
   from code, history and build output without running the system: request fan-out
   per screen or route, N+1 queries, unbounded lists and payloads, synchronous I/O on
   a hot path, render cascades and unnecessary re-renders, bundle and dependency
   weight, memory retention, polling versus push, missing pagination, caching and its
   invalidation? For each: the detection recipe, what it costs at different loads and
   device classes, and where it becomes premature optimization.
5. **Performance that must be measured.** Which claims need measurement before they
   become findings, and what is the cheapest credible measurement for an audit:
   profiling a representative flow, a short load test, bundle analysis, mobile
   throttling, a production telemetry read? How should an audit report a static
   candidate it could not measure?
6. **Platform specifics.** Separate guidance for web front-ends on mobile devices,
   desktop apps (Electron), backends serving many concurrent users, and real-time or
   multiplayer systems. What changes in the rubric between 2,000 and 100,000
   concurrent users?
7. **Other quality attributes.** Is there evidence that reliability/resilience,
   accessibility or observability deserve their own audit dimension, or are they better
   folded into the existing ones? Give a short recommendation per attribute.
8. **Deterministic tooling.** For every check in questions 2, 4 and 5, which
   established, locally runnable tools compute it (static analysis, dependency and
   secret scanners, bundle analyzers, query analyzers, profilers, load generators,
   browser performance tooling), per stack: JavaScript/TypeScript (web, Node,
   Electron), Python, JVM, Go. For each: what it measures, its false-positive
   profile, whether it executes project code, whether it sends data off the machine,
   and how to pin and run it without installing into the project. Where no tool
   exists, what a small custom script would compute.
9. **Severity calibration.** How should the same finding change severity with the
   profile (a lockstep desktop tool versus a public multi-tenant service)? Any
   published severity schemes worth adopting?

## Evidence rules

- Cite named, checkable sources: security standards and guidance (OWASP ASVS and
  related, NIST SSDF, platform security guides), performance guidance from browser,
  platform and framework vendors, published engineering case studies, and 2025–2026
  papers on agent-written code. Date each claim.
- Separate **established practice**, **emerging**, and **opinion**. Mark every numeric
  threshold or budget with its source and how it was derived.
- Treat vendor effectiveness claims as unverified unless independently replicated.
- Don't invent benchmarks, frameworks, product names, or statistics.

## Output I want

- A short answer up front: the ten security checks and the ten performance checks that
  matter most in an audit, each tied to the profile facts that make it apply.
- A tool table per stack: check · tool · what it measures · executes code? · leaves
  the machine? · how to run it pinned without installing into the project.
- Two rubric tables (security, performance): criterion · what a finding looks like ·
  mechanical or judgment · the tool or script that detects it · static or needs
  measurement · severity by profile ·
  where it becomes over-engineering or premature optimization · `applies when`
  condition on the profile.
- A minimal-profile checklist: the facts an audit must have before judging each
  dimension.
- Agent-specific failure patterns with defenses.
- A short verdict on reliability, accessibility and observability as dimensions.

## Out of scope

- Reviewing a single diff or PR (already covered).
- Architecture, gates, contracts and verbosity (already covered).
- Penetration testing, red-teaming, and production load-testing programs.
- Compliance certification (SOC 2, ISO 27001) beyond what changes an audit rubric.
