# Composition playbook

The conductor's job is to invoke the right skill at each phase and route its output
into the ledger and the next phase. This file says, per phase, **what to pass in,
what to capture, and how to keep it autonomous.** Invoke each via the Skill tool.

Skills are invoked inside fresh-context subagents (Task) wherever they support it,
so heavy reads don't pollute the conductor thread. The conductor holds only the
ledger and the loop.

**Cost scales with tier.** `feature-spec` returns `TIER: LITE|FULL`. Use it:
- **LITE** → Spec → Build (one fresh-context subagent doing spec→build→verify) →
  Verify (gates+evidence) → Integrate. Skip Phase 1b, Phase 2, and code review.
- **FULL** → the full pipeline below: Spec → (Design review if novel structure) →
  Plan → Isolate → Build (per-phase subagents) → Verify + code review → Integrate.

**Where artifacts land** (keep them consistent, not scattered — a long run otherwise
sprawls into a tree that needs manual cleanup). Follow the repo's existing docs
convention if it has one; otherwise default to:
- Machine run-state → `./.autoloop/` at repo root, **gitignored** (transient).
- Specs → `docs/specs/YYYY-MM-DD-<slug>.md`. **Date-prefix, don't sequentially
  number** — parallel agents race on the next number; dates need no central counter.
  On ship, `git mv` the spec to `docs/specs/archive/` so the active set stays small.
- Plans → `docs/plans/YYYY-MM-DD-<slug>.plan.md` (a **separate** dir, not interleaved
  with specs).
- Run artifacts (report, audit, retro) → one folder per run:
  `docs/runs/YYYY-MM-DD-<name>/report.md`.

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
- **Stand up the end-to-end / observation harness.** `solidify-repo` establishes unit/
  lint/security gates and a verify command — it does **not** by itself give you a way
  to drive and *watch* the running artifact. The conductor must ensure one exists: for
  a UI, a browser/UI automation tool that can launch the app and capture what renders
  (screenshots, DOM, console, exit state); for a CLI/service/library, invoke it for
  real and capture stdout / exit code / HTTP response / generated files. The concrete
  tool comes from `solidify-repo`'s tooling reference. Wire this harness into the verify chain so
  Phase 5 can produce observation evidence, not just unit results.
- **Gate (hard refusal):** after this phase the repo must have both (a) runnable
  deterministic checks and (b) a way to run and observe the real artifact end-to-end.
  If either is missing and can't be stood up, **stop and report — do not run the loop
  unit-tests-only.** An autonomous loop with no eyes on the running artifact ships
  broken software that "passes."

## Phase 1 · Spec each item — `feature-spec` (autonomous mode)

- **In:** one wishlist item (paragraph) at a time, with an explicit signal that this
  is an unattended pipeline so it runs autonomously and does not ask questions.
- **Capture:** its handoff block verbatim into the ledger —
  `SPEC: <path>` · `TIER: LITE|FULL` · `DECISIONS_NEEDED: none | <n> (highest: …)`.
- **Route:** `DECISIONS_NEEDED` with `high` severity → copy into `blockers.md` as a
  queued decision (do not halt). A `LITE` feature now skips straight to Phase 4
  (build straight from the spec); only `FULL` continues to 1b/2.

## Phase 1b · Design review — `architecture-critic` (rare: FULL + novel structure)

- **When:** **only** FULL features that introduce genuinely new structure,
  cross-cutting boundaries, or non-trivial data/failure modeling. A routine FULL
  feature (e.g. a CRUD settings page) does **not** need an adversarial design
  review — skip it. This phase is the exception, not the norm.
- **In:** the spec from Phase 1.
- **Capture:** verdict + blockers. A REVISE verdict with blockers → loop the spec
  once (re-run Phase 1 with the feedback) before planning; if still blocked after
  one revision, quarantine and move on.
- **Big ambiguous bets:** if this is a large new subsystem or the brief is genuinely
  ambiguous (analogies, not a spec), don't let it auto-land on `main` — build it thin
  and reversible on a disposable branch and surface the open product decisions in the
  report. A throwaway branch you can discard beats a polished version of the wrong
  thing merged into `main`.

## Phase 2 · Plan — `superpowers:writing-plans` (FULL only)

- **When:** FULL features only. A LITE feature's spec is directly implementable —
  running a second planning pass on it duplicates the spec and burns tokens.
- **In:** the approved spec.
- **Out:** a step-by-step implementation plan with independent, checkpointed tasks.
- **Capture:** write the plan to `docs/plans/YYYY-MM-DD-<slug>.plan.md` and record
  that path in the task entry.

## Phase 3 · Isolate — `superpowers:using-git-worktrees`

- **When:** before building each feature; mandatory if any features run in parallel.
- **Out:** an isolated workspace/branch per feature so concurrent work can't collide.

## Phase 3b · Fan out — `superpowers:dispatching-parallel-agents`

- **When:** 2+ features whose dependency sets are disjoint (no shared files, no
  ordering between them). Dependent features never go here — serialize them.
- **In:** the set of independent, planned, isolated features.

## Phase 4 · Build — `superpowers:executing-plans` (or `superpowers:subagent-driven-development`) + `superpowers:test-driven-development`

- **In:** FULL → the plan from Phase 2; LITE → the spec directly. In the worktree
  from Phase 3 if isolating.
- **Subagent budget:** LITE → a **single** fresh-context subagent carries the
  feature from spec → build → verify (don't pay per-phase handoff cost on a small
  feature). FULL → per-phase subagents as the build skill dictates.
- **Subagent model:** build subagents run the **same or a cheaper/faster** model than
  the conductor — **never a stronger/pricier** one (see `goal.md`'s `conductor_model`).
  They implement to the approved spec/plan; architecture and taste calls stay with the
  conductor. A design fork the subagent hits goes to `blockers.md`, not resolved inline.
- **Discipline:** test-first per task; bring each to passing gates; write evidence
  (logs/output) to `.autoloop/evidence/`. The subagent runs every command **inside
  its own worktree** — never install/build/test against the shared main checkout (a
  stray `npm ci`/build in the wrong cwd can wipe the shared tree mid-run).
- **Commit before handing back.** The subagent's last step is to commit its work and
  report the commit SHA — verified-but-uncommitted work is lost when the subagent ends.
- **Capture:** evidence paths and the commit SHA into the task entry.

## Phase 5 · Verify — `superpowers:verification-before-completion` (+ `superpowers:requesting-code-review` for FULL/risky)

- **In:** the feature's spec/acceptance criteria + the diff. Verify **independently
  of how it was built** — evidence before assertions, and **in the real runtime**: a
  mock / preview / in-memory stand-in does not verify anything that crosses a host /
  IO / IPC / PTY boundary. If the run can't drive the real environment, record the
  task as `needs-human-smoke` (not `done`) and list it in the report.
- **Code review:** add `superpowers:requesting-code-review` only for FULL or
  otherwise risky features. A LITE feature gets the verification pass alone — one
  independent check is enough; a second review pass on a small change is waste.
- **Check:** all gates pass when run fresh; the diff meets the spec; adjacent
  functionality didn't regress; **the gates themselves weren't weakened/deleted/
  mocked** to pass — diff the current gate definitions against the baseline pinned
  in Phase 0; any relaxation of an existing check fails the task (newly *added*
  tests are fine).
- **Out:** PASS with evidence, or FAIL with concrete defects.
- **Route:** PASS → Phase 6. FAIL → record the defect in the task's `notes`, retry
  Phase 4 up to the retry limit (default 2 retries / 3 attempts), then quarantine.

## Phase 6 · Integrate — `superpowers:finishing-a-development-branch`

- **When:** a feature is verified PASS **and committed** (the commit SHA is recorded
  as evidence — uncommitted work doesn't exist).
- **Merge, then re-verify the merged tree.** Merge one branch at a time; after each
  merge (and any conflict resolution) run the **full verify on the merged tree
  before** fast-forwarding `main`. Never ff an unverified merge — per-feature verify
  in isolation misses cross-feature breakage and bad conflict resolutions. Starting
  each parallel subagent from `git reset --hard <base>` keeps rebases clean.
- **Out:** merged/PR'd per its guidance; record the commit SHA; mark the task `done`
  in `tasks.yaml`; the merge unblocks dependents. (Git history is the changelog.)

## Keeping it autonomous

- Pass every downstream skill the context that it is part of an **unattended**
  pipeline, so skills with an autonomous mode (e.g. `feature-spec`) use it and do
  not block on questions.
- Anything a skill would normally ask a human → it records as an assumption /
  queued decision; the conductor copies high-severity ones to `blockers.md` and
  continues.
- The loop never stops for input. It stops only when every feature is `done` or
  `blocked`.
