# Parallelism and unattended detach

## Parallel vs. sequential — driven by the dependency graph

The spec phase produces a *provisional* dependency graph. Spec-time independence is
a hypothesis — two features that sound unrelated can still touch the same files.
**Confirm disjointness against the Phase 2 plans' actual file lists before fanning
out**, and only then commit to parallel. Use the graph, don't guess:

- **Truly independent features** (disjoint files, no ordering between them) → run
  concurrently. Give each an isolated workspace via `superpowers:using-git-worktrees`,
  then fan out with `superpowers:dispatching-parallel-agents`.
- **Dependent features** (one needs another's output, or they touch shared files)
  → run **sequentially** in dependency order. A dependent task becomes selectable
  only when every task in its `deps` is `done`.
- **When unsure, serialize.** Mistaken parallelism causes merge corruption and
  hard-to-trace state collisions; the wall-clock saving isn't worth a poisoned run.

Each parallel feature lands through Phase 5 (verify) and Phase 6 (integrate)
independently; the conductor merges verified branches one at a time and re-runs the
regression gate after each merge to catch cross-feature breakage.

## Detached / unattended runs

The in-session conductor is the portable default. To genuinely "kick off and walk
away," run the loop as a detached/long-running task — this part depends on harness
features, so treat it as adaptation, not gospel.

What the detach needs, whatever the harness:

- **A durable driver.** A background or scheduled task that re-enters the loop,
  reads the ledger, advances one pass, and persists. The ledger (not the chat) is
  what survives between wake-ups — this is why state lives on disk.
- **A non-skippable completion gate.** Bind the verify harness to a stop hook so a
  feature (or the run) cannot be declared done while gates fail: the hook runs the
  checks and, on failure, blocks the stop and feeds the failure back into the loop.
  This is what removes "done" from the model's discretion.
- **Post-edit checks.** Optionally run formatters/linters on file-change hooks so
  trivial fixes don't burn loop iterations.
- **No interactive prompts anywhere.** Every downstream skill must run in its
  autonomous/non-interactive mode; a single blocking question hangs an unattended
  run indefinitely. Decisions go to `blockers.md`, never to a prompt.

If the harness lacks durable background execution or stop hooks, fall back to the
in-session conductor and accept that the run pauses when the session does —
resuming cleanly from the ledger when restarted.

## Resumption after compaction or restart

On any resume, before acting: re-read `goal.md`, `tasks.yaml`, and `blockers.md`.
Treat a stale `in_progress` task as `todo` and re-verify rather than trusting it was
finished. Never reconstruct progress from memory.
