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

**The conductor is the model you started on; delegate sideways or down, never up.**
Keep the **current session model** in the conductor's seat for the whole run — do
**not** auto-escalate to a "strongest available" model (that can silently jump to a
pricier tier the user never chose). The conductor's judgment is the scarce resource,
so don't spend it typing boilerplate. What is **non-delegable** stays with the
conductor: the **architecture** (boundaries, where a feature lives, which abstraction
earns its keep) and the **taste** calls (API shape, UX, naming, what "good" looks
like). *Implementation* delegates to subagents running the **same or a cheaper/faster
model — never a stronger or more expensive one** — they build to the spec and plan the
conductor approved, but they never get to make the architecture or taste call. A
subagent that hits a genuine design fork records it as a queued decision for the
conductor (`blockers.md`); it never resolves it inside its worktree. This topology
holds with no human present, which is why it's a principle and not a prompt. The
conductor model and execution mode are fixed once at kickoff in `goal.md` (see the
state ledger), not re-asked mid-run.

**Honest scope.** A strong model already finishes and self-verifies a small,
in-context build well — there it needs no protocol. This one earns its keep when
the run is too long or too many-featured to hold in one context, where working
memory degrades over hours or sessions. Its value is **composition, resumability,
and a verified stop condition** — not making the model "try harder."

**You must be able to *see* what you built.** Unit tests are necessary and not
remotely sufficient. An autonomous loop that can only read green unit output will
confidently ship software it never looked at — the feature "passes" while the app is
blank, the button does nothing, the layout is broken. So the loop is built around
**driving the real running artifact end-to-end and observing its actual output**, not
just asserting on internals. For anything with a UI that means a tool that can render
it and capture what a user would see; for a CLI/service/library it means invoking it
for real and capturing stdout / exit code / HTTP response. Without that capability
there is no honest stop condition — so the loop **requires it and refuses to run
without it** (see Hard rules / Phase 0).

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
- **No way to run and *observe* the real artifact → refuse to run the loop.** Phase 0
  must establish an **end-to-end harness that drives the running artifact and captures
  its actual output**, not just unit/lint gates. For anything with a UI, that is a
  browser/UI automation tool that can capture what renders (screenshots, DOM, console,
  exit state); for a CLI/service/library it is the stack-appropriate equivalent (invoke
  for real; capture stdout / exit code / HTTP response / generated files). Phase 0
  establishes the concrete tool via `solidify-repo` and its tooling reference. If no
  such harness exists and one
  cannot be stood up in Phase 0, **stop and report — do not proceed unit-tests-only.**
  `needs-human-smoke` is for a genuinely undriveable boundary (a physical device, an
  irreversible paid side effect), **never** for "we skipped setting up end-to-end QA."
- **Never weaken, delete, narrow, or mock-out a gate to make it pass.** A gamed
  gate is a failed task. Disabling a check as "production-only" or "just for now" is
  weakening it — the lint / dead-code / duplication / complexity gates run every loop
  precisely to stop an autonomous build from rotting the codebase.
- **"Verified" is not "landed." Commit, then verify the merge.** A feature is done
  only when its work is **committed** (record the commit SHA as evidence) *and* the
  branch is merged *and* the **merged tree** passes the full verify. Never
  fast-forward an unverified merge — per-feature verify in isolation misses
  cross-feature breakage and bad conflict resolutions. A passing build that was never
  committed is lost work, not a finished feature.
- **Verify in the real runtime, not a mock.** A check that only exercises a
  mock / preview / in-memory stand-in does not verify a feature that crosses a host /
  IO / IPC / PTY / network boundary. If the run can't drive the real environment,
  mark the task `needs-human-smoke` in the ledger and flag it in the report — never
  record mock-only verification as `done`.
- **Subagents act only inside their own worktree.** Never run install/build/test or
  any mutating command against the shared main checkout from a subagent — a stray
  `npm ci`/build in the wrong cwd can wipe the shared tree and break the run mid-flight.
- **Architecture and taste are the conductor's; subagents only implement.** Keep the
  current session model as conductor — don't escalate to a "strongest available"
  model. Delegate implementation to subagents on the **same or a cheaper model, never
  a stronger/pricier one**. Subagents build to the approved spec/plan; they never
  decide a boundary, an abstraction, an API shape, or a UX/naming call. A real design
  fork a subagent hits is queued for the conductor (`blockers.md`), never resolved in
  the worktree.
- **Fully autonomous: never call interactive question tools mid-run.** Downstream
  skills run in their non-interactive/autonomous mode — including ones that normally
  ask for approval (e.g. repo hardening): pass them the unattended signal and record
  would-be approvals as assumptions. Queue every decision to the ledger and keep
  going. Never halt on a single blocker — quarantine and continue.

## The loop (phases, each delegates to a skill)

Detailed playbook with inputs/outputs per skill: `references/composition.md`.
State files: `references/state-ledger.md`. Parallelism + unattended detach:
`references/parallel-and-detach.md`.

**Right-size to the feature's tier.** `feature-spec` tags each item **LITE** or
**FULL** — let that drive how much pipeline it gets. Spending FULL machinery
(separate plan, design review, code review, per-phase subagents) on a LITE feature
is exactly the token waste this skill must avoid — just as much a defect as
under-building a FULL one. The "Applies to" column says when each phase runs.

| Phase | What happens | Invoke (Skill tool) | Applies to |
|---|---|---|---|
| **0 · Ground** | Ensure deterministic gates, a one-command verify harness, a security gate, **and an end-to-end harness that drives and observes the real running artifact**. Establish them if missing; **refuse to proceed if the artifact can't be exercised and observed.** | `solidify-repo` + stand up the e2e/runtime harness | **once per run** |
| **1 · Spec** | Turn each item into a right-sized, buildable spec. Run **autonomous**; capture its `SPEC / TIER / DECISIONS_NEEDED` handoff. | `feature-spec` | every feature |
| **1b · Design review** | Fresh-eyes architecture check before building. | `architecture-critic` | **only FULL features that introduce new structure/boundaries** — usually skip |
| **2 · Plan** | Turn the spec into a step-by-step implementation plan. | `superpowers:writing-plans` | **FULL only** — LITE builds straight from the spec |
| **3 · Isolate** | Isolated workspace so parallel work can't collide. | `superpowers:using-git-worktrees` | any feature run in parallel (Phase 3b); else optional |
| **3b · Fan out** | Run independent features concurrently. | `superpowers:dispatching-parallel-agents` | 2+ **confirmed-independent** features |
| **4 · Build** | Implement test-first; write evidence. | `superpowers:executing-plans` / `superpowers:subagent-driven-development` + `superpowers:test-driven-development` | every feature — **LITE: one fresh-context subagent does spec→build→verify; FULL: per-phase** |
| **5 · Verify** | Prove it works against acceptance criteria, with evidence, **in the real runtime** (not a mock), independent of how it was built. | `superpowers:verification-before-completion` (+ `superpowers:requesting-code-review`) | every feature — **code review FULL/risky only** |
| **6 · Integrate** | Commit (record the SHA), merge, then **verify the merged tree before ff-merge**. | `superpowers:finishing-a-development-branch` | every feature |

### What you (the conductor) do between phases

1. **Plan the order.** From the specs, build the dependency graph: independent
   features → parallel (Phase 3b); dependent → sequential. Write it to the ledger.
   Treat spec-time independence as **provisional** — confirm features are truly
   disjoint against the Phase 2 plans' file lists before fanning out; when unsure,
   serialize. Shared entry files (global stylesheet, app/root entry, DI or plugin
   registry, route table) are near-universal collision points even when feature
   *logic* is disjoint — route merges that touch them through one serial lane.
   For a **large new subsystem or genuinely ambiguous brief** (analogies, not a
   spec), don't auto-land it on `main`: build it thin and reversible on a disposable
   branch, keep it off `main`, and surface 2–3 explicit product decisions + your pick
   in the report so the user can course-correct cheaply (you can't ask mid-run).
2. **Select** every task whose deps are `done`; dispatch its phases.
3. **Record** each phase's output to the ledger (spec handoff, evidence paths,
   review verdicts, defects).
4. **On a failure**, append the defect and retry the feature up to a fixed limit
   (default: 2 retries, 3 attempts total); past the limit, **quarantine it to the
   blockers ledger and move to the next** —
   never loop forever, never halt the run. A genuinely infeasible feature is
   recorded as blocked with the reason, never faked or stubbed.
5. **Re-evaluate against the goal each pass. Stop only when every feature is
   verified-done or quarantined.** Then **write the final report to
   `docs/runs/<date>-<name>/report.md`** (follow the repo's docs convention if it has
   one; not just the chat, which vanishes after an unattended run): shipped (with
   evidence + commit SHAs) / blocked (with reasons) / `needs-human-smoke` items /
   decisions queued during autonomy.

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
- **Applying FULL machinery to LITE features.** A separate plan, design review, code
  review, and per-phase subagents on a one-surface feature burns tokens for nothing.
  Let the tier gate the pipeline.
- **Skipping Phase 0.** Looping against gates that don't exist proves nothing.
- **Self-certifying.** "I implemented it" is not done; the verification skill's
  evidence is.
- **Fast-forwarding an unverified merge.** Per-feature verify in a worktree doesn't
  prove the *merged* tree is green; a conflict resolution or cross-feature clash can
  break `main`. Verify after merge, before ff.
- **Calling mock verification "done."** A preview/mock host can't exercise real
  FS/IPC/PTY paths; mark those `needs-human-smoke`, don't claim them verified.
- **Treating green unit tests as a working app.** Unit tests assert on internals; they
  say nothing about whether the thing actually renders, responds, or runs. A loop that
  never drives and *looks at* the real artifact ships blank screens and dead buttons
  that "pass." Stand up the end-to-end/observation harness in Phase 0 or don't start.
- **Leaving verified work uncommitted.** A passing build that was never committed is
  lost the moment the subagent is cut off. Commit is the last build step; the SHA is
  the evidence.
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
  ordering across worktrees cause merge corruption — when unsure, serialize. Watch
  the shared entry files (global styles, app root, registries, route tables): even
  "independent" features routinely collide there, so merge through them serially.
- **Quarantine is success, not failure.** An honest "blocked: <reason>" beats a
  fake "done"; the point is a run that can't lie about what it finished.
