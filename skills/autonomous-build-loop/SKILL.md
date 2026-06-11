---
name: autonomous-build-loop
description: Use when driving a whole backlog/wishlist of features to completion in one long or unattended run — multiple features that each need specifying, implementing, and verifying with no human to babysit; a run expected to exceed a single context window (compaction will happen) or span sessions; a long-running/overnight agent that must keep rolling on its own without stopping early, dropping subtasks, faking progress, or declaring "done" on its own say-so. Keywords - wishlist, backlog grind, build all of these, autonomous loop, unattended, long-horizon, overnight run, kick off and walk away, agent went lazy / satisficed / premature completion.
allowed-tools: Read, Glob, Grep, Task, Write, Edit, Bash, Skill
---

# Autonomous Build Loop

Drive a list of features to **verified** completion in one long autonomous run.

## Core principle

You are the **conductor**, not the whole orchestra. This skill gets a run started,
reads the wishlist, and keeps it rolling — but the real work of each phase is done
by **skills you already have**. Do **not** reinvent spec-writing, repo hardening,
planning, isolation, TDD, or verification inline. Invoke the dedicated skill for
each and orchestrate their outputs.

Two things stay yours as conductor: the **loop** (select → build → verify → record
→ repeat until done-or-blocked) and the **state ledger on disk** that lets the run
survive compaction and resume. Everything else, delegate.

**Honest scope.** A strong model already finishes and self-verifies a small,
in-context build well — there it needs no protocol. This one earns its keep when
the run is too long or too many-featured to hold in one context, where working
memory degrades over hours or sessions. Its value is **composition, resumability,
and a verified stop condition** — not making the model "try harder."

## When to use

- A backlog/wishlist of several features built in one long or **unattended** run.
- A run expected to exceed a single context window, or to span sessions.
- The run must keep going with no human to answer questions or approve steps.

## When NOT to use

- A single feature, or a small batch that plainly fits one context — just build it
  (reach for the spec/TDD skills directly). This loop is overhead there.
- A human is actively supervising each step — use the interactive skills directly.

## Hard rules

- **Compose, don't reinvent.** Each phase below names the skill to invoke. Calling
  it is mandatory, not optional — do not hand-roll a spec, a verify harness, or a
  review you have a skill for.
- **"Implemented" is never "done."** A feature completes only when the verification
  skill confirms it against executable evidence — never on your own assertion.
- **The ledger on disk is the source of truth.** Never mark the wishlist complete
  from memory or prose. Re-read the ledger after any compaction before acting.
- **No executable gates → no feature work.** Ground the repo first (Phase 0).
- **Never weaken, delete, narrow, or mock-out a gate to make it pass.** A gamed
  gate is a failed task.
- **Fully autonomous: never call interactive question tools mid-run.** Downstream
  skills run in their non-interactive/autonomous mode — including ones that normally
  ask for approval (e.g. repo hardening): pass them the unattended signal and record
  would-be approvals as assumptions. Queue every decision to the ledger and keep
  going. Never halt on a single blocker — quarantine and continue.

## The loop (phases, each delegates to a skill)

Detailed playbook with inputs/outputs per skill: `references/composition.md`.
State files: `references/state-ledger.md`. Parallelism + unattended detach:
`references/parallel-and-detach.md`.

| Phase | What happens | Invoke (Skill tool) |
|---|---|---|
| **0 · Ground** | Ensure the repo has deterministic gates, a one-command verify harness, and a security gate. If missing/thin, establish them before any feature work. | `solidify-repo` |
| **1 · Spec** | Turn each wishlist item into a right-sized, buildable spec with acceptance criteria. Run it in **autonomous mode**; capture its `SPEC / TIER / DECISIONS_NEEDED` handoff into the ledger. | `feature-spec` |
| **1b · Review** *(design-heavy/FULL features only)* | Fresh-eyes architecture check on the spec before building. Record blockers. | `architecture-critic` |
| **2 · Plan** | Turn each spec into a concrete, step-by-step implementation plan. | `superpowers:writing-plans` |
| **3 · Isolate** | Give each feature an isolated workspace so parallel work can't collide. | `superpowers:using-git-worktrees` |
| **3b · Fan out** *(independent features)* | Run features with no shared deps concurrently. | `superpowers:dispatching-parallel-agents` |
| **4 · Build** | Execute each plan task-by-task, test-first. | `superpowers:executing-plans` / `superpowers:subagent-driven-development` + `superpowers:test-driven-development` |
| **5 · Verify** | Prove the feature works against its acceptance criteria, with evidence — independently of how it was built. | `superpowers:verification-before-completion` + `superpowers:requesting-code-review` |
| **6 · Integrate** | Land the verified work; decide merge/PR. | `superpowers:finishing-a-development-branch` |

### What you (the conductor) do between phases

1. **Plan the order.** From the specs, build the dependency graph: independent
   features → parallel (Phase 3b); dependent → sequential. Write it to the ledger.
   Treat spec-time independence as **provisional** — confirm features are truly
   disjoint against the Phase 2 plans' file lists before fanning out; when unsure,
   serialize.
2. **Select** every task whose deps are `done`; dispatch its phases.
3. **Record** each phase's output to the ledger (spec handoff, evidence paths,
   review verdicts, defects).
4. **On a failure**, append the defect and retry the feature up to a fixed limit
   (default: 2 retries, 3 attempts total); past the limit, **quarantine it to the
   blockers ledger and move to the next** —
   never loop forever, never halt the run. A genuinely infeasible feature is
   recorded as blocked with the reason, never faked or stubbed.
5. **Re-evaluate against the goal each pass. Stop only when every feature is
   verified-done or quarantined.** Then emit the final report: shipped (with
   evidence) / blocked (with reasons) / decisions queued during autonomy.

## Modes

- **In-session (default).** You are the conductor in this session, dispatching the
  skills above (in subagents via Task where they support it). Portable.
- **Detached / unattended.** To run the loop as a background or scheduled
  long-running task with a non-skippable completion gate, see
  `references/parallel-and-detach.md` (harness-specific).

## Common mistakes

- **Reinventing a phase you have a skill for.** Hand-writing a spec instead of
  calling `feature-spec`, or a verify step instead of the verification skill, is
  the primary failure of this skill. Delegate.
- **Running this on a small build.** If it fits one context, skip the loop and use
  the phase skills directly.
- **Skipping Phase 0.** Looping against gates that don't exist proves nothing.
- **Self-certifying.** "I implemented it" is not done; the verification skill's
  evidence is.
- **Holding plan/progress in the chat.** Compaction evicts it; the run then forgets
  finished work, repeats dead ends, or hallucinates completion. The ledger is truth.
- **Halting on the first blocker.** Defeats the unattended purpose — quarantine and
  continue.
- **Letting a downstream skill ask questions.** In a detached run a blocking prompt
  hangs everything; ensure each skill runs in its autonomous/non-interactive mode.

## Gotchas

- **The ledger is the contract, not your memory.** Re-read it on every resume.
- **A gamed gate is worse than a red one** — it hides a defect and poisons every
  later "done." The verification phase must confirm gates weren't weakened.
- **Parallel only for truly independent features.** Shared files or implicit
  ordering across worktrees cause merge corruption — when unsure, serialize.
- **Quarantine is success, not failure.** An honest "blocked: <reason>" beats a
  fake "done"; the point is a run that can't lie about what it finished.
