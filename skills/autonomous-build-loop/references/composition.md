# Composition playbook

The conductor's job is to invoke the right skill at each phase and route its output
into the ledger and the next phase. This file says, per phase, **what to pass in,
what to capture, and how to keep it autonomous.** Invoke each via the Skill tool.

Skills are invoked inside fresh-context subagents (Task) wherever they support it,
so heavy reads don't pollute the conductor thread. The conductor holds only the
ledger and the loop.

## Phase 0 · Ground the repo — `solidify-repo`

- **When:** once, at the start, before any feature work.
- **In:** the target repo, plus the unattended signal — `solidify-repo` normally
  asks for per-category approval, so it must run promptless here: record would-be
  approval choices as assumptions in `blockers.md` rather than waiting.
- **Capture:** the resulting verify command(s) (test / lint / typecheck / runtime
  harness) into `goal.md` / per-task `gates`. These commands ARE the executable
  definition of done used in Phase 5.
- **Pin the gate baseline:** snapshot the gate definitions (hash the test/lint/CI
  config and existing test files) into the ledger now, so Phase 5 has a fixed
  baseline to diff against when checking that gates weren't weakened.
- **Gate:** if the repo has no runnable checks after this phase, stop and report —
  the whole loop depends on real gates existing.

## Phase 1 · Spec each item — `feature-spec` (autonomous mode)

- **In:** one wishlist item (paragraph) at a time, with an explicit signal that this
  is an unattended pipeline so it runs autonomously and does not ask questions.
- **Capture:** its handoff block verbatim into the ledger —
  `SPEC: <path>` · `TIER: LITE|FULL` · `DECISIONS_NEEDED: none | <n> (highest: …)`.
- **Route:** `DECISIONS_NEEDED` with `high` severity → copy into `blockers.md` as a
  queued decision (do not halt). `TIER: FULL` → eligible for Phase 1b.

## Phase 1b · Design review — `architecture-critic` (FULL/design-heavy only)

- **When:** features that introduce new structure, cross-cutting boundaries, or
  non-trivial data/failure modeling. Skip for LITE/localized features; on a
  borderline case, run it — a fresh-eyes review is cheap relative to a poisoned build.
- **In:** the spec from Phase 1.
- **Capture:** verdict + blockers. A REVISE verdict with blockers → loop the spec
  once (re-run Phase 1 with the feedback) before planning; if still blocked after
  one revision, quarantine and move on.

## Phase 2 · Plan — `superpowers:writing-plans`

- **In:** the approved spec.
- **Out:** a step-by-step implementation plan with independent, checkpointed tasks.
- **Capture:** plan path into the task entry.

## Phase 3 · Isolate — `superpowers:using-git-worktrees`

- **When:** before building each feature; mandatory if any features run in parallel.
- **Out:** an isolated workspace/branch per feature so concurrent work can't collide.

## Phase 3b · Fan out — `superpowers:dispatching-parallel-agents`

- **When:** 2+ features whose dependency sets are disjoint (no shared files, no
  ordering between them). Dependent features never go here — serialize them.
- **In:** the set of independent, planned, isolated features.

## Phase 4 · Build — `superpowers:executing-plans` (or `superpowers:subagent-driven-development`) + `superpowers:test-driven-development`

- **In:** the plan from Phase 2, in the worktree from Phase 3.
- **Discipline:** test-first per task; bring each task to passing gates; write
  evidence (logs/output) to `evidence/`.
- **Capture:** evidence paths into the task entry.

## Phase 5 · Verify — `superpowers:verification-before-completion` + `superpowers:requesting-code-review`

- **In:** the feature's spec/acceptance criteria + the diff. Verify **independently
  of how it was built** — evidence before assertions.
- **Check:** all gates pass when run fresh; the diff meets the spec; adjacent
  functionality didn't regress; **the gates themselves weren't weakened/deleted/
  mocked** to pass — diff the current gate definitions against the baseline pinned
  in Phase 0; any relaxation of an existing check fails the task (newly *added*
  tests are fine).
- **Out:** PASS with evidence, or FAIL with concrete defects.
- **Route:** PASS → Phase 6. FAIL → append to `defects.md`, retry Phase 4 up to the
  retry limit (default 2 retries / 3 attempts), then quarantine.

## Phase 6 · Integrate — `superpowers:finishing-a-development-branch`

- **When:** a feature is verified PASS.
- **Out:** merged/PR'd per its guidance; mark the task `done` in the ledger; append
  to `changelog.md`; the merge unblocks dependents.

## Keeping it autonomous

- Pass every downstream skill the context that it is part of an **unattended**
  pipeline, so skills with an autonomous mode (e.g. `feature-spec`) use it and do
  not block on questions.
- Anything a skill would normally ask a human → it records as an assumption /
  queued decision; the conductor copies high-severity ones to `blockers.md` and
  continues.
- The loop never stops for input. It stops only when every feature is `done` or
  `blocked`.
