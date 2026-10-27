# Research prompt: existing skills for product requirements, specs and implementation plans

## Context

The findings will feed a decision, stage by stage, to **adopt, adapt or replace**
in-house agent skills for an agent-driven software delivery pipeline (intake →
product requirements → spec → plan → design → build → verify → review → release).
The in-house skills were written from research syntheses and have no evals,
benchmarks or A/B results behind them. The goal is to find existing skills, prompt
packs and methods that already carry evidence they work, and take the proven parts
instead of rebuilding them.

This prompt covers three stages: writing a **product requirements document**, writing a **feature spec**, and turning a spec into an **implementation plan** an agent can execute. Sibling prompts cover design, build and verification, security and audit, and how to evaluate skills cheaply.

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

1. **Product requirements.** Which skills or frameworks take a product idea to a
   PRD (problem, users, goals, non-goals, success metrics, scope boundaries)? How do
   they handle what the agent cannot know and must ask? Which have evidence that
   their PRDs beat an unprompted agent's, and judged how?
2. **Feature specs.** Which take a short or vague request to a behaviour spec
   (flows, states, edge cases, defaults, acceptance criteria)? Include spec-driven
   development frameworks. Is there evidence that a spec improves downstream build
   success compared with no spec, and evidence of where a spec becomes overhead?
3. **Implementation plans.** Which turn a spec into an executable plan (task
   breakdown, file map, test intents, ordering, parallel groups)? Is there evidence
   on plan granularity versus build success, or on plans written for a weaker
   executing model?
4. **Traceability.** Which carry requirement IDs from spec to plan to tests to
   verification, and does anyone show that this catches dropped requirements?
5. **Right-sizing.** Which scale depth to the size of the change (skip, light,
   full), and what evidence supports the thresholds they use?

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
