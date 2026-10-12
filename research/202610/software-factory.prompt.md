# Research prompt: the software factory, loop engineering, and graph engineering

## Context

The findings will feed a suite of reusable agent skills for agentic development.
Parts of the pipeline are already covered: hardening a repo for agents, writing
a feature spec from a vague idea, reviewing an architecture before code, and a
conductor that drives a backlog to verified completion in one long, unattended
run.

What's missing is the whole picture. People increasingly talk about a
**"software factory"**: a system where agents take work from intake to shipped,
verified software with humans steering rather than typing. Alongside it appear
the terms **"loop engineering"** and **"graph engineering"**. It is unclear
whether these are three names for one idea, three layers of one stack, or
marketing words with no stable meaning. The question is what is real as of
October 2026, and what it would take to build one.

## Questions to answer

1. **Definitions and lineage.** What does "software factory" mean today, and how
   does it relate to earlier uses of the term? Older examples to check include the
   Japanese software factories of the 1970s–80s (Cusumano's work) and Microsoft's
   2004 "Software Factories" (Greenfield & Short); recent examples include
   agent-run "dark factory" setups. Who uses "loop engineering" and "graph
   engineering", where did each term come from, and is either one stable enough
   to design around? If a term is mostly hype or ambiguous, say so plainly.
2. **Differences.** A precise comparison of the three: what problem each
   addresses, what its unit of design is (a prompt, a loop, a graph of agents
   and gates, a whole delivery system), and where they overlap. Also show where
   they sit next to related terms: harness engineering, context engineering,
   agent orchestration, spec-driven development.
3. **Anatomy of a factory.** What are the parts of a working software factory?
   Intake and triage, specification, planning and decomposition, implementation,
   verification and QA, review, merge and release, observability, and feedback
   into the next cycle. For each stage: what the agent does, what the
   deterministic gate is, what state persists, and where a human must stay in the
   loop and why.
4. **What it takes to build one.** What the codebase, the tooling, the test and
   verification infrastructure, and the team need before a factory produces
   trustworthy output instead of high-volume slop. What maturity levels exist, and
   what is the smallest version that is worth building?
5. **Control flow.** Loops (retry-until-gate, critique-and-revise, ralph-style
   re-runs) versus explicit graphs (state machines, DAGs, LangGraph-style
   workflows) versus a conductor agent with subagents. When does each one fit,
   and how do they fail (runaway cost, drift, silent satisficing, deadlock,
   merge conflicts between parallel agents)?
6. **Evidence.** Which teams or companies have published real results from a
   factory-style setup: throughput, defect rates, cost per change, the share of
   changes merged without human edits? How much of what is claimed is verified,
   and how much is vendor marketing?
7. **What changed since June 2026.** I last researched long-running agents in
   June 2026. Focus on what is new since then: new harness features, new
   orchestration products, new evidence, and new failure modes.

## Evidence rules

- Cite named, checkable sources: vendor docs, papers, engineering blog posts,
  talks, repos. Give a date for every claim; this field moves monthly.
- Tag each claim as **established**, **emerging**, or **speculative/marketing**.
- Don't invent product names, benchmark IDs, statistics, or quotes. If you can't
  find a source, say the claim is unsourced.
- Where sources disagree, show the disagreement instead of picking a side.

## Output I want

- A short executive answer up front: what a software factory is, and how it
  differs from loop and graph engineering, in a few sentences.
- A comparison table of the three concepts.
- A reference anatomy of a factory (diagram plus a stage-by-stage table:
  agent role, gate, persisted state, human touchpoint).
- A build path in incremental stages, from a single verified loop to a
  multi-stage factory, with the prerequisite for each stage.
- Failure modes and anti-patterns, each with how to detect it and how to defend
  against it.
- A mapping onto Claude Code primitives (skills, subagents, hooks, workflows,
  background and scheduled agents, worktrees, CLAUDE.md), plus the closest
  equivalents in other harnesses. Keep it tool-agnostic where you can.
- Open problems: what nobody has solved yet.

## Out of scope

- Classic CI/CD and DevOps theory, except where agents change it.
- Low-code/no-code platforms.
- Product comparisons by pricing.
