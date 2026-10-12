# Research prompt: auditing the architecture of an existing, mostly agent-written codebase

## Context

The findings will feed a periodic **audit of a whole codebase as built**, where
most of the code is written by coding agents. The audit asks whether the
architecture is still coherent, whether the repo's gates are still respected,
whether the contracts are sound, and whether the code has bloated. It runs on
demand or on a trigger, produces anchored findings and a prioritized task list,
and keeps a baseline so the next audit can measure drift. Reviewing a design
before it is built and reviewing a diff before merge are already covered.

The principles of good architecture are well known (cohesion and coupling,
dependency direction, information hiding, YAGNI). What's missing is **method**:
how to recover and judge an architecture from code, which signals detect
erosion, and where judgment has to take over from tools.

## Questions to answer

1. **Recovering the real architecture.** How do practitioners reconstruct the
   actual module and dependency structure from code (architecture recovery,
   reflexion models, dependency-graph analysis, co-change and hotspot analysis)?
   How do you compare it with the documented or intended architecture (ADRs,
   architecture notes, agent instruction files) and report the drift? What works
   on a brownfield codebase with mixed styles, where it is unclear which
   convention is authoritative?
2. **Measuring erosion and conceptual integrity.** Which signals reliably
   indicate architectural erosion: cycles, layer violations, fan-in and fan-out,
   instability and abstractness, co-change coupling across modules, duplicate or
   parallel abstractions (two clients, two error types, two state mechanisms for
   one concern), one concept under several names? Which have published
   thresholds or evidence behind them, and which are folklore?
3. **Front-end architecture specifically.** How do you audit a front-end
   codebase's structure: component boundaries and layering, state placement
   (server, URL, local UI, global store), data-fetching and caching ownership,
   routing and feature-folder structure, design-system adherence? What erosion
   patterns are specific to front ends?
4. **Gate respect over time.** How do teams detect that a repo's checks have
   decayed: suppressions and skipped tests accumulating, lint rules downgraded,
   type strictness relaxed, paths excluded, required CI checks dropped in a
   migration, local gate commands diverging from CI? How do you measure whether
   tests actually constrain behaviour (mutation testing, assertion density,
   tests that pass with the implementation removed), and how do you make that
   affordable on a large codebase (sampling, targeting high-risk paths)?
5. **Verbosity and over-production.** How do you detect and judge code that is
   larger than it needs to be: speculative generality (one-implementation
   interfaces, unused extension points, config nobody sets), pass-through
   wrappers and shims, defensive-code bloat, comment noise that restates code,
   dead code and orphaned files, oversized files and functions? Which size or
   complexity thresholds have evidence, and when is length cohesion rather than
   bloat?
6. **Agent-specific patterns.** What is the current evidence on how
   agent-written codebases erode differently from human-written ones:
   duplication instead of reuse, pattern cargo-culting, over-engineering,
   inconsistent conventions, gate gaming? What do agent-first teams do about it
   (architecture encoded as structural tests and lint rules, recurring cleanup
   agents, per-domain quality scores)? Separate measured findings from anecdote.
7. **The audit method itself.** How should an LLM-assisted codebase audit be
   structured so its findings are trustworthy: deterministic evidence
   extraction first, then a rubric, then model judgment, then
   evidence-linked findings? What false-positive rates have been reported? How
   should severity be calibrated for findings on running code? How do you
   sample a codebase too large to read fully?
8. **Cadence, triggers, and scoring.** What triggers a re-audit (metric
   thresholds, incidents, large migrations, time)? Is there any credible
   whole-codebase or per-module health score, and what does it consist of?

## Evidence rules

- Cite named, checkable sources: software-architecture and maintenance research
  (architecture recovery, technical debt, code smells), tool documentation,
  published engineering case studies, and 2025–2026 papers on agent-written
  code. Date each claim.
- Separate **established practice**, **emerging**, and **opinion**. Mark any
  numeric threshold with its source and how it was derived.
- Name real tools by category and example, but treat vendor effectiveness
  claims as unverified unless independently replicated.
- Don't invent benchmarks, frameworks, product names, or statistics.

## Output I want

- A short answer up front: how to audit an agent-written codebase's
  architecture, in ten lines.
- A step-by-step audit method with inputs, outputs, and where a human must
  judge.
- A table of erosion and bloat signals: what each detects, how to detect it
  (mechanical vs. judgment), evidence strength, and any defensible threshold.
- A gate-decay checklist and a practical, affordable test-strength method.
- A front-end section with its own signals.
- A minimal baseline (the handful of numbers worth recording each audit so the
  next one can measure drift).
- Failure modes of the audit itself (false positives, over-reporting, judging
  style as architecture) and defences.

## Out of scope

- Reviewing a single diff or PR (already covered).
- Reviewing a design before it is built (already covered).
- Security auditing, licensing, and AI provenance.
- Detailed contract and API design. A companion research brief covers that.
