# Research brief: Duplication and reuse loss in agent-written code, and what fixes it (H2 2026)

## Why I am asking

Coding agents write a second copy of a helper that already exists rather than finding
and reusing the first one. They add a new utility file beside the one that should have
been extended. Over months this compounds: near-duplicate functions with slightly
different signatures, parallel abstractions for the same concept, three date
formatters. GitClear measured duplicated code up 81% across 623 million changes from
2023 to 2026, and 40% of developers in Sonar's 2026 survey named unnecessary or
duplicated code as their main complaint about AI output.

I want the state of practice for preventing it, detecting it, and cleaning it up, with
evidence. A sibling brief covers the root cause (the additive bias of agents) and
another covers error masking; stay on duplication and reuse here.

## Scope

- Time window: prioritise 2026, especially July to October.
- Subject: duplication introduced by coding agents in real repositories: exact clones,
  near clones, semantic duplicates (same behaviour, different shape), parallel
  abstractions, and new files or modules created where an existing one should have been
  changed. Also the inverse: reuse loss, meaning existing helpers no longer get called.
- Any language, with notes where the practice is language-specific.

## Questions to answer

1. **Shape of the problem.** What kinds of duplication do agents actually produce, in
   what proportions? Exact versus near versus semantic clones; intra-PR versus cross-
   PR; helper functions versus whole modules versus test scaffolding. Any measured
   breakdown.
2. **Why it happens, specifically.** Beyond the general additive bias: retrieval
   failure (the agent did not find the existing code), context cost (finding is more
   tokens than writing), naming mismatch (searched for the wrong word), ownership
   caution (did not want to change a shared helper's signature), and reward (a new
   function passes tests just as well). Which of these have been measured or at least
   observed in traces?
3. **Prevention at write time.** Workflows and rules that make the agent find before it
   writes: mandatory repository search for an existing implementation before creating a
   symbol; plans that must list the existing code a change will touch; "extend, do not
   fork" rules; indexes or symbol maps given to the agent; retrieval tools wired into
   the agent loop. Which have before/after numbers?
4. **Detection in the loop.** Clone detection and semantic-duplicate detection used as
   a gate on agent PRs in 2026: tools, thresholds, false-positive rates, run time, how
   teams tuned them so agents did not just learn to rename variables past the detector.
   Include whole-repo AI reviewers that flag "this already exists" and any evidence of
   how well they do it.
5. **Cleanup after the fact.** How teams run consolidation passes on an AI-heavy
   codebase: finding clone families, choosing the survivor, migrating callers safely,
   proving behaviour is preserved. Agent-driven consolidation versus human-driven, with
   results and failure modes.
6. **Metrics.** What teams track to know whether duplication is rising or falling:
   clone percentage, helper count per concept, "new file per PR" rate, reuse ratio
   (calls to existing symbols versus new symbols per change). Published baselines and
   trends for agent-heavy repositories.
7. **Trade-offs and counter-evidence.** When duplication is the right call (decoupling,
   avoiding the wrong abstraction, test readability) and how teams keep agents from
   over-consolidating into premature abstractions. Cases where an anti-duplication rule
   caused harm.
8. **Open problems.** Semantic duplicate detection at scale, cross-repository
   duplication in multi-repo workspaces, duplication inside generated tests.

## Evidence rules

- Prefer first-hand sources: engineering blogs with numbers, talks, tool documentation
  with stated detection methods, papers and preprints with reproducible setups,
  published instruction files from real repositories.
- Grade every substantive claim: `[measured]`, `[first-hand]`, `[vendor]`, `[opinion]`.
  A vendor claim needs an independent counter-source or an explicit "unverified" tag.
- Cite with title, author or organisation, date, and URL. Do not invent sources. Say
  "not found" rather than fill a gap. Quote instruction-file rules verbatim with the
  repository they came from.
- Name real tools and state what each actually detects (token clones, AST clones,
  semantic similarity) and at what cost.

## Output

A report of roughly 3,500 to 5,000 words:

1. **Executive summary:** the dominant duplication type, the single most effective
   prevention step, the detection setup that works, and the metric to watch.
2. **Findings per question 1 to 8**, each ending with the evidence grades used.
3. **Tool table:** tool, what it detects, how it is run (pre-commit / CI / review bot),
   false-positive experience, evidence grade, source.
4. **Verbatim rules and workflow steps** from real repositories, with provenance.
5. **A recommended setup for a small agent-first team** across prevention, detection
   and cleanup, with the two numbers to track.
6. **Full source list.**
