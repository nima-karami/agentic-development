# Research brief: Error masking in agent-written code, and what fixes it (H2 2026)

## Why I am asking

Coding agents make failures disappear instead of surfacing them. The patterns are
familiar: broad catch blocks that log and continue, fallbacks that return a default
when the real path fails, optional chaining and null coalescing sprinkled until nothing
can throw, retries with no limit, "defensive" guards around code that should have been
fixed, and tests that pass because the subject was mocked away. The code looks careful
and the system quietly does the wrong thing. GitClear measured error-masking constructs
up 47% across 623 million changes from 2023 to 2026.

I want the state of practice for preventing, detecting and removing it, with evidence.
Sibling briefs cover the root cause (the additive bias of agents) and duplication; stay
on error handling and failure visibility here.

## Scope

- Time window: prioritise 2026, especially July to October.
- Subject: error masking introduced by coding agents in production code and in tests.
  Includes swallowed exceptions, silent fallbacks and defaults, over-defensive guards,
  unbounded retries, logging in place of handling, and tests that cannot fail (empty
  assertions, self-comparisons, mocked subjects, catch-and-pass around the assertion).
- Any language, with notes where the construct is language-specific.

## Questions to answer

1. **Taxonomy and frequency.** Which masking constructs do agents actually produce, how
   often, and in which contexts (new code versus edits, production versus tests)? Any
   measured breakdown, and how "error masking" was operationalised in each study.
2. **Why agents do it.** Candidates: a passing test suite is the reward and a thrown
   exception is a red; instruction phrases like "handle errors gracefully" or "make it
   robust" interpreted as "never throw"; training data full of tutorial-grade try/catch;
   risk aversion about changing the code that produces the error; no runtime
   observation, so a silent wrong answer looks identical to a right one. Which have
   evidence behind them?
3. **Prevention by instruction.** Rules that measurably reduced masking: "fail loudly",
   "no catch without a rethrow or a specific recovery", "no default values on failure
   paths", "errors are part of the contract", bans on broad exception types. Verbatim
   rules from real repositories, and whether anyone measured the effect.
4. **Prevention by design.** Typed error channels (result types, checked errors, error
   unions), crash-early conventions, structured logging that makes a swallowed error
   visible on a dashboard, contracts and invariants checked at boundaries. Evidence that
   any of these changed agent behaviour rather than just human behaviour.
5. **Detection in the loop.** Lint rules and static analysis for masking constructs
   (empty catch, catch-all, swallow-and-log, unbounded retry, nullish-coalescing on
   non-optional values), mutation testing to expose tests that cannot fail, coverage of
   error paths specifically, runtime canaries. Tools, thresholds, false-positive
   experience, and how agents responded when a rule was enforced (comply, or route
   around it with a different construct).
6. **Detection by review.** What AI reviewers and human reviewers catch here, and what
   they miss. Any benchmark or field data on masking findings per PR, or on review
   checklists that improved the catch rate.
7. **Cleanup.** How teams find and remove masking in an existing AI-heavy codebase:
   inventories of catch blocks, "make it throw and see what breaks" campaigns in
   staging, replacing fallbacks with explicit failure modes, strengthening weak tests
   first. Results and failure modes.
8. **Tests that cannot fail.** Treat separately: how common, how detected (mutation
   testing, assertion counting, "did the test ever fail" history), and what rules keep
   agents from producing them. Include the related finding that benchmark test suites
   themselves were flawed (OpenAI's 2026 audit of SWE-bench Verified found 59.4% of
   hard tasks had material test flaws).
9. **Counter-evidence.** Where "fail loudly" was wrong: user-facing paths that must
   degrade, batch jobs that must continue, integrations with flaky upstreams. How teams
   express "degrade here, crash there" so an agent follows it.
10. **Open problems.** Masking that is semantically valid but behaviourally wrong,
    detection in dynamically typed code, masking inside generated tests, and whether
    models are being trained against it.

## Evidence rules

- Prefer first-hand sources: engineering blogs with numbers, postmortems where a masked
  error caused an incident, tool documentation with stated rules, papers and preprints
  with reproducible setups, published instruction files from real repositories.
- Grade every substantive claim: `[measured]`, `[first-hand]`, `[vendor]`, `[opinion]`.
  A vendor claim needs an independent counter-source or an explicit "unverified" tag.
- Cite with title, author or organisation, date, and URL. Do not invent sources. Say
  "not found" rather than fill a gap. Quote rules verbatim with the repository they came
  from.
- Name real lint rules and analyzers by their rule identifiers where they exist.

## Output

A report of roughly 3,500 to 5,000 words:

1. **Executive summary:** the most common masking construct, the best-evidenced
   prevention rule, the detection setup that works, and the one counter-case every rule
   must allow for.
2. **Findings per question 1 to 10**, each ending with the evidence grades used.
3. **Construct table:** construct, why agents produce it, detection method (rule id or
   technique), prevention rule, evidence grade, source.
4. **Verbatim rules** from real repositories, with provenance.
5. **A recommended setup for a small agent-first team** across instruction, design,
   detection and cleanup, with the two numbers to track.
6. **Full source list.**
