# Research brief: Why coding agents only add code, and what makes them subtract (H2 2026)

## Why I am asking

I run an agent-first development practice. The field observation, consistent across my
own repositories and across published telemetry, is that coding agents are additive:
they route around existing code instead of changing it, they layer new code on top of
old, and the line count of a codebase only ever goes up. Agents almost never delete,
merge, or simplify unless told to, and even then they resist. GitClear's analysis of
623 million changes (2023 to 2026) puts numbers on it: moved code (their refactoring
proxy) down 70%, changes to code older than a year down 74%, duplication up 81%, error
masking up 47%.

This brief is about the root cause and the countermeasures that have been shown to
work. Two sibling briefs cover the two most visible symptoms in depth (duplication and
error masking). Treat this as the umbrella: mechanism first, then interventions, with
an evidence grade on every claim.

## Scope

- Time window: prioritise 2026, especially July to October. Earlier material only as
  the baseline for "what changed".
- Subject: the additive bias of LLM coding agents in real repositories, and the
  refactoring avoidance that follows from it. Code-level behaviour, not chat behaviour.
- Agents in scope: terminal and IDE coding agents and autonomous PR agents, any vendor.
- Segments to compare where the evidence allows: agent vendors and labs (what they say
  causes it and what they changed), AI-forward teams that publish practice, established
  companies, open-source maintainers, academic studies.

## Questions to answer

1. **Mechanism.** What is the best-supported explanation for the bias? Candidates to
   test against evidence: training rewards that favour passing tests over minimal
   diffs; loss aversion learned from RLHF (touching existing code risks breaking it,
   adding code rarely does); context windows that make the existing code invisible;
   instruction-following that treats "add feature X" literally; a lack of
   whole-repo memory; diff-based review that never penalises growth. Which of these
   have been measured, and how?
2. **Evidence of the behaviour.** Published measurements of net line growth, delete-to-
   add ratios, refactor share, and "code older than N months touched" for agent-written
   versus human-written changes. Methodology and sample sizes for each.
3. **Prompt and instruction-level interventions.** Instruction-file rules, system
   prompts, or skill texts that measurably reduced additive behaviour. Examples:
   "prefer modifying existing code", "search before you write", "net negative lines
   when possible", explicit deletion budgets, "simplest change that passes" directives.
   Which were A/B tested, and what happened to correctness when growth was constrained?
4. **Workflow-level interventions.** Dedicated refactor passes after feature passes;
   a second agent whose only job is to remove code; "find-then-write" steps that
   require a repository search before any new symbol; planning stages that must name
   the existing code a change will modify; review gates that reject a change which
   adds a file where a sibling could have been edited. Evidence per pattern.
5. **Gate-level interventions.** Mechanical checks that have been used to counter the
   bias: net-line-delta budgets per PR, complexity ceilings, duplication thresholds,
   dead-code detection in CI, "new file requires justification" rules, size budgets
   per module. Which held up, which got gamed, and how the gaming looked.
6. **Model-level changes.** Have any vendors said they trained against this (minimal-
   diff rewards, refactoring benchmarks, deletion-aware evaluation)? Any benchmark
   that scores refactoring or code reduction rather than feature completion, and how
   current models do on it.
7. **Safe subtraction.** How teams let agents delete and refactor without breaking
   things: characterisation tests first, mutation testing as the safety net, behaviour-
   preserving refactor tooling (language-server renames and extracts) instead of
   free-text edits, staged refactors with a gate between each stage. Measured results.
8. **Counter-evidence.** Cases where constraining growth made things worse: churn,
   over-compression, clever code that broke later, agents deleting tests to meet a
   line budget. What the failure modes looked like and how they were caught.
9. **Open problems.** What practitioners say is still unsolved about getting agents to
   simplify, consolidate and delete.

## Evidence rules

- Prefer first-hand sources: engineering blogs with before/after numbers, talks,
  postmortems, vendor changelogs that name the behaviour, papers and arXiv preprints
  with reproducible setups, published instruction files from real repositories.
- Grade every substantive claim: `[measured]` (numbers plus method), `[first-hand]`
  (practitioner account, no numbers), `[vendor]` (marketing or self-reported),
  `[opinion]`. A vendor claim needs an independent counter-source or an explicit
  "unverified" tag.
- Cite with title, author or organisation, date, and URL. Do not invent sources. If a
  claim cannot be sourced, say so rather than fill the gap. Quote any instruction-file
  rule verbatim, with the repository it came from.
- Distinguish prompt-level fixes (cheap, fragile) from gate-level fixes (mechanical,
  gameable) from model-level fixes (out of a team's hands). Say which layer each
  intervention lives in.

## Output

A report of roughly 4,000 to 6,000 words:

1. **Executive summary:** the best-supported mechanism, the three interventions with
   the strongest evidence, and the two most common ways countermeasures get gamed.
2. **Findings per question 1 to 9**, each ending with the evidence grades used.
3. **Intervention table:** intervention, layer (prompt / workflow / gate / model),
   evidence grade, measured effect on growth, measured effect on correctness, known
   gaming, source.
4. **Verbatim instruction rules** collected from real repositories, with provenance.
5. **A recommended stack for a small agent-first team**, in priority order, with what
   to measure to know whether it is working.
6. **Full source list.**
