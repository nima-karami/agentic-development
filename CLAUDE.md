# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

An **agentic-development lab**. The workflow it exists to support: drop in
research, then turn that research into reusable Claude Code **skills** (and, later,
tools) for agentic development. It is not an application — there is no build, test,
or lint toolchain. The artifacts are Markdown: research syntheses and skill
definitions.

## The two-source research convention

Research lives in `research/YYYYMM/<topic>-A.md` and `<topic>-B.md`. **Each topic
has two independent deep-research syntheses**, produced by different researchers:

- **A** tends to be cautious and evidence-grounded (named, checkable sources:
  vendor docs, papers, benchmarks).
- **B** tends to be confident and prescriptive (opinionated defaults, a single
  recommended stack). B's specific citations, product names, and benchmark IDs are
  sometimes fabricated — **verify B's concrete claims before relying on them.**

When working a topic, read **both** A and B, identify where they agree (the
high-confidence consensus) and where they diverge, and design from the consensus
rather than either document alone.

## The research → skill pipeline

A skill is authored from a research pair via the superpowers plugin:

1. `superpowers:brainstorming` — turn the research into an agreed design spec
   (clarifying questions one at a time, then a written, approved design).
2. `superpowers:writing-skills` — author the skill as **TDD for documentation**:
   - **RED:** run baseline pressure scenarios with subagents *without* the skill;
     document what they do unaided. If they don't fail, the skill isn't justified —
     surface that honestly and let the user decide whether to build anyway.
   - **GREEN:** write the `SKILL.md` targeting the observed gaps; re-run scenarios
     to confirm the desired behavior.
   - **REFACTOR:** close loopholes/rationalizations; re-test.

Topic → skill mapping so far: `agent-human-repo` → `solidify-repo`;
`agent-driven-architecture-design` → `architecture-critic`. The
`agent-driven-feature-spec` and `long-running-agents` pairs have no skill yet.

## Skills: structure, house style, and dual location

Each skill is `skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`,
`description`, `allowed-tools`). Match the established house style when writing or
editing skills:

- `description` starts with **"Use when…"** — triggering conditions and keywords
  only, never a workflow summary (a workflow summary makes Claude follow the
  description instead of reading the skill body).
- Body sections: Overview/core principle → When to use / When NOT to use → **Hard
  rules** → numbered Steps → reference tables (rubrics) → Common mistakes →
  Gotchas.
- **Language-agnostic methodology, not bundled tooling.** The skill encodes
  judgment and process; it tells the agent to detect the stack and look up current
  tools (via WebSearch) rather than hardcoding a toolchain that will go stale.
- **Pluralist, anti-over-engineering stance.** Skills treat over-engineering
  (prestige abstractions, premature layering) as a defect equal to
  under-structuring. Do not mandate specific architectures.
- **No "Provenance" sections and no cross-references to other skills.** (User
  preference — keep skills self-contained; don't cite the research docs or name
  sibling skills in the skill body.)

**Dual location — keep in sync manually.** The repository copy under `skills/` and
the *live* copy under `~/.claude/skills/<name>/` are independent files. Editing one
does not update the other. A skill only takes effect once copied to the user's
global skills directory:

```bash
cp skills/<name>/SKILL.md ~/.claude/skills/<name>/SKILL.md   # or cp -r for a new skill
```

When asked to "update the skill," update **both** copies unless told otherwise.

## Operating notes

- This is a public GitHub repo (`origin`). Git history is public — removing a file
  in a new commit does not erase it from history.
- Throwaway artifacts (test design docs, baseline scratch) must go to the OS temp
  dir, never the repo — keep the working tree to intended research/skill files only.
