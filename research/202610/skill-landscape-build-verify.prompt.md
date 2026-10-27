# Research prompt: existing skills for autonomous builds and requirements verification

## Context

The findings will feed a decision, stage by stage, to **adopt, adapt or replace**
in-house agent skills for an agent-driven software delivery pipeline (intake →
product requirements → spec → plan → design → build → verify → review → release).
The in-house skills were written from research syntheses and have no evals,
benchmarks or A/B results behind them. The goal is to find existing skills, prompt
packs and methods that already carry evidence they work, and take the proven parts
instead of rebuilding them.

This prompt covers three stages: **building end to end autonomously** (a long or unattended run that takes features from spec to working code), **verifying the result against its requirements** (acceptance criteria, runtime behaviour), and **code review** of agent-written changes. Sibling prompts cover product requirements and planning, design, security and audit, and how to evaluate skills cheaply.

## What counts as a candidate

- Agent skills in the open skill format (a folder with a `SKILL.md` plus optional
  scripts and references), plugins, and command or subagent packs for terminal
  coding agents.
- First-party skills and reference workflows published by agent and model vendors.
- Open methodology frameworks that ship agent prompts, templates or checklists for
  the stage.
- Stage components inside open-source autonomous coding harnesses, when they can be
  lifted out on their own.
- Research systems with released prompts and a published evaluation.

The source must be readable. Closed hosted products count only as a reference point
for what the bar is, not as candidates.

## What counts as proof

Place every candidate on this ladder and quote the evidence that puts it there:

- **P1 — evaluated against a baseline:** compared with no skill or an alternative on
  a stated task set, with numbers and a harness someone else could run.
- **P2 — independently evaluated:** an evaluation or replication by someone other
  than the author.
- **P3 — documented field use:** real projects with outcomes, including failures
  (case studies, retros, issue threads showing actual use).
- **P4 — adoption only:** installs, stars, forks, commit activity. Report it, but
  it is not evidence of quality and must not drive the ranking.
- **P5 — none.**

## Fit criteria

Judge each candidate that reaches P3 or better against these:

- Runs in a terminal coding agent that loads skills from files, and works in more
  than one vendor's agent or ports with little effort.
- Stack- and language-agnostic, or with the stack-specific part cleanly separable.
- No required hosted service, account or telemetry.
- Explicit human decision points; it never approves its own output.
- Produces an artifact the next stage can consume (a structured handoff).
- Cost: number of agent calls, rough token use, and the model tier it assumes.
- A license that allows copying and modification (name the license).
- Safety: scripts it runs, network calls, writes outside the repository, and any
  embedded instruction that would act as prompt injection on the host agent.

## Questions to answer

1. **Autonomous builds.** Which skills or harnesses drive long, unattended builds to
   completion: loop structure, progress and state files, context resets, stopping
   rules, human checkpoints? Which publish completion rates on long-horizon tasks
   with and without the harness?
2. **Requirements verification.** Which check a built change against its acceptance
   criteria independently of the agent that built it? Is there evidence they reduce
   false "done" claims, and how do they trace each criterion to evidence?
3. **Runtime verification.** Which drive the running system (browser, CLI, API) to
   prove behaviour rather than relying on unit tests? What do they report, and how
   are they evaluated?
4. **Code review.** Which review skills or agents publish precision and recall on
   real defects, or acceptance rates of their comments? Which benchmarks exist for
   AI code review, and how independent are they?
5. **Gate integrity.** Which defend against weakened tests, skipped checks and other
   ways an agent can make the gate pass without doing the work? Is there evidence
   that the defenses work?

## Evidence rules

- **Time window.** This is a fast-moving agent-tooling topic: prioritize sources
  from 2026, especially the second half (July–October 2026). Use older material only
  as a baseline for what changed, and say so. First-principles methods behind a
  stage (requirements engineering, design review, testing practice) may come from
  any year.
- Link the exact repository, path and version or commit, and the date you checked.
- Popularity is not proof. Directories and curated "awesome" lists are discovery
  sources, not evidence.
- Treat author and vendor effectiveness claims as unverified unless the harness is
  public (P1) or someone else replicated it (P2).
- Don't invent repositories, skills, benchmarks, numbers or quotes. If a stage has
  no candidate above P4, say so plainly; that is a useful finding.

## Output I want

- A short answer up front, at most ten lines: per stage, the best candidate and its
  proof level, or "nothing proven".
- Per stage, a candidate table: name · link · license · what it does · proof level
  and the evidence · fit gaps · verdict (**adopt as is / adapt / lift one technique /
  ignore**).
- Per stage, the specific techniques worth lifting even from candidates not worth
  adopting whole (rubrics, templates, checklists, gating rules, prompt structures),
  each with its proof level.
- Per stage, any published eval tasks, benchmarks or graded examples that could be
  reused to test an in-house skill for the same stage.
- Risks found in third-party skills during the search (unsafe scripts, injection,
  abandoned maintenance, license traps).

## Out of scope

- General coding benchmarks and model comparisons not tied to a stage.
- Editor autocomplete and inline-completion tools.
- Hosted products with no readable prompts, except as a reference for the bar.
