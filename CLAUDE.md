# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

An **agentic-development lab**. The workflow it exists to support: drop in
research and field evidence, then turn them into reusable Claude Code **skills** for
agentic development. It is not an application — there is no build, test, or lint
toolchain. The artifacts are Markdown: research syntheses and skill definitions.

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

## The evidence → skill pipeline

Skills come from two evidence sources: a research pair, or **field retros** from the
projects that run the skills for real (their `docs/runs/*/report.md|retro.md`).
Authoring is TDD for documentation, done natively (the `superpowers` plugin is
**banned** here — do not invoke any of its skills):

1. **Design first.** Agree the skill's scope, handoff contract, and hard rules in
   conversation before writing. Specs and plans stay local and untracked.
2. **RED.** Baseline pressure scenarios with subagents *without* the skill. Field
   evidence (a retro documenting the failure in a real run) counts as RED. If nothing
   fails, say so and let the user decide whether to build anyway.
3. **GREEN.** Write `SKILL.md` targeting the observed gaps; run one pressure scenario
   per skill with a fresh subagent that has the skill text injected, judged against a
   checklist by a separate runner.
4. **REFACTOR.** Close the loopholes and rationalizations the GREEN run surfaced;
   re-test when the change is behavioral.

## The seed skills and the pipeline they form

```
request → feature-spec → implementation-plan → architecture-critic (FULL only)
        → build-and-verify → code-review → runtime-qa → integrate
```

`autonomous-build-loop` conducts that pipeline for a backlog; `solidify-repo` grounds
the repo first and re-audits for gate drift; `create-project-plugin` presses the seeds
into a **per-project plugin** (self-contained project skills + bindings + learnings
chain). Each stage ends with a **machine-parseable handoff block** (`SPEC:/TIER:`,
`PLAN:/…/CLAIMS:`, `BUILD:/GATE:/RUNTIME_PROOF:`, `REVIEW:/BLOCKERS:`,
`QA:/VERDICT:/NOT_COVERED:`) — keep those shapes stable; downstream stages grep them.

Origins: `agent-human-repo` → `solidify-repo`; `agent-driven-architecture-design` →
`architecture-critic`; `agent-driven-feature-spec` → `feature-spec`;
`long-running-agents` → `autonomous-build-loop`. `implementation-plan`,
`build-and-verify`, `code-review`, `runtime-qa` and `create-project-plugin` came from
the 2026-09 field retro across Conduit and Vega plus the hand-built Trident plugin.

## Skills: structure, house style, and dual location

Each skill is `skills/<skill-name>/SKILL.md` (+ optional `references/`) with YAML
frontmatter (`name`, `description`, `allowed-tools`). Match the house style:

- `description` starts with **"Use when…"** — triggering conditions and keywords
  only, never a workflow summary.
- Body sections: Overview/core principle → When to use / When NOT to use → **Hard
  rules** → numbered Steps → reference tables (rubrics) → Common mistakes →
  Gotchas → Reference files.
- **Language-agnostic methodology, not bundled tooling.** Detect the stack; look up
  current tools rather than hardcoding a toolchain.
- **No product, tool, or model names in the SKILL.md body.** Say "the gate command",
  "the judgment tier". Concrete names live only in `references/` files.
- **Pluralist, anti-over-engineering.** Over-production (a stage restating the
  previous stage's artifact) is a defect equal to under-structuring; triage with
  SKIP / LITE / FULL tiers.
- **Cross-cutting canon is worded identically wherever it appears** (gate integrity,
  done-claim gate, evidence rules, model-tier rule, script-over-manual, learnings
  tags, concurrency hygiene, over-production, settled decisions). Copy, don't
  paraphrase — one search must find every copy.
- **No "Provenance" sections. Single-purpose skills never name sibling skills.**
  Exception: orchestrator-class skills (`autonomous-build-loop`,
  `create-project-plugin`) compose the others and MUST name them.

**Dual location — keep in sync manually.** The repository copy under `skills/` and
the *live* copy under `~/.claude/skills/<name>/` are independent files:

```bash
cp -r skills/<name> ~/.claude/skills/   # after any edit; both copies must match
```

When asked to "update the skill," update **both** copies unless told otherwise.

## Operating notes

- This is a public GitHub repo (`origin`). Git history is public — removing a file
  in a new commit does not erase it from history.
- Throwaway artifacts (test design docs, GREEN scratch repos, subject outputs) go to
  the OS temp dir, never the repo.
- Field evidence lives in `G:\awby\projects\vega-life-os` (the worked example) and
  `G:\awby\projects\conduit`; re-read their `docs/runs` before improving a skill.
