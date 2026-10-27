# Research prompt: evaluating agent skills on a small budget

## Context

The findings will feed a lightweight evaluation practice for a suite of in-house
agent skills covering an agent-driven software delivery pipeline (product
requirements, spec, plan, design, build, verification, review, audit, release). The
skills were written from research syntheses and have no evals, benchmarks or A/B
results behind them. There is no budget for a large evaluation program: one or two
people, a few hours per skill, and model spend measured in tens of dollars per skill
rather than thousands. Sibling prompts survey existing third-party skills per stage;
this one is about how to measure any skill, in-house or third-party.

## Questions to answer

1. **Current tooling.** What evaluation harnesses exist for agent skills, plugins and
   agent configurations (from agent vendors and open source)? What does each measure:
   whether the skill triggers, task outcome, cost, regressions between versions?
2. **The minimum viable eval.** For one skill, how many tasks and how many repeated
   runs give a result worth acting on, given run-to-run variance? What can and cannot
   be concluded at small sample sizes? Cite the statistics, not rules of thumb.
3. **Judging outputs.** How reliable are model judges for stage artifacts (PRDs,
   specs, plans, design reviews, code reviews, audit findings)? How many human labels
   are needed to calibrate a judge, and which judge designs (pairwise, rubric,
   reference-based, checklist) hold up best?
4. **Reusable task sets.** Which public benchmarks or graded example sets map onto
   each stage closely enough to use as eval tasks? Note contamination risk and
   licensing.
5. **Field runs as evals.** How do teams turn real run logs, retros and incidents
   into regression cases, and how well does that work?
6. **A/B against a third-party skill.** The cheapest sound way to compare an in-house
   skill with an existing one on the same tasks, including blinding the judge.
7. **Triggering.** What evidence exists on evaluating and tuning a skill's
   description so it loads when it should and stays quiet otherwise?
8. **Costs.** Realistic token and time cost of each technique above.

## Evidence rules

- **Time window.** This is a fast-moving agent-tooling topic: prioritize sources
  from 2026, especially the second half (July–October 2026). Use older material only
  as a baseline for what changed, and say so. Statistics, measurement and evaluation
  methodology may come from any year.
- Link the exact repository, paper or page, with version and the date you checked.
- Separate **established practice**, **emerging**, and **opinion**. Mark every
  numeric threshold with its source.
- Treat vendor effectiveness claims as unverified unless independently replicated.
- Don't invent tools, benchmarks, numbers or quotes.

## Output I want

- A short answer up front, at most ten lines: the minimum eval a two-person team
  should run per skill, and what it can and cannot tell them.
- A **minimum eval kit per stage**: task source, number of tasks and repeats, judge
  design, human labels needed, pass criterion, estimated cost.
- A comparison table of evaluation harnesses: name · link · license · what it
  measures · effort to adopt · limits.
- A protocol for comparing an in-house skill with a third-party one.
- Common ways small evals mislead, with defenses.

## Out of scope

- General coding benchmarks and model comparisons not tied to a stage.
- Editor autocomplete and inline-completion tools.
- Hosted products with no readable prompts, except as a reference for the bar.
- Training or fine-tuning models.
- Large-scale benchmark programs that need dedicated infrastructure.
