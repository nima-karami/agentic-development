# The state ledger

The plan and progress live on disk, not in the conversation, so the run survives
compaction, interruption, and resumption. After any compaction or restart, the
Supervisor **re-reads this ledger before acting** — it is the single source of
truth, above any recollection.

Put the machine run-state in `./.autoloop/` at the repo root and **add it to
`.gitignore`** — it's transient run-state, not a committed artifact. Keep entries
terse and machine-greppable. (Human-readable artifacts go under `docs/`, not here —
follow the repo's docs convention if it has one; default: specs →
`docs/specs/YYYY-MM-DD-<slug>.md` (date-prefixed; `git mv` to `docs/specs/archive/`
on ship), plans → `docs/plans/YYYY-MM-DD-<slug>.plan.md`, run report →
`docs/runs/YYYY-MM-DD-<name>/report.md`. See `references/composition.md`.)

Keep the ledger lean — the Supervisor re-reads it every pass, so every file is a
recurring token cost. Five files, no more:

## Files

| File | Holds | Re-read on resume |
|---|---|---|
| `goal.md` | The real, user-visible outcome the whole wishlist serves (one paragraph) + the Phase 0 verify commands. The thing the Supervisor checks the finished set against. | yes |
| `tasks.yaml` | One entry per task: id, outcome, tier, deps, gates, evidence, commit, status, notes. The work queue — and the dependency graph lives here in `deps` (no separate plan file). | yes |
| `evidence/` | Test logs, run output, screenshots, verifier notes — the proof a task passed. | on demand |
| `blockers.md` | Quarantined/infeasible features + queued high-severity decisions, with reason and what would unblock. Surfaced in the final report. | yes |
| `gate-baseline.txt` | Phase 0 snapshot (hashes) of the gate definitions — test/lint/CI config and existing test files — that Phase 5 diffs against to detect weakened gates. | on demand |

No `plan.md` (the graph is `tasks.yaml`'s `deps`), no `changelog.md` (git history
records what changed), no `defects.md` (a failed gate goes in that task's `notes`).

## `tasks.yaml` shape

```yaml
- id: slugify
  outcome: "Exported slugify(str) producing URL-safe slugs per spec"
  tier: LITE                     # from feature-spec; gates how much pipeline it gets
  deps: []                       # ids that must be done first; [] = independent
  status: todo                   # todo | in_progress | done | blocked | needs-human-smoke
  gates:                         # executable; each must pass
    - "node --test test/slugify.test.js"
    - "node scripts/lint.js"
  evidence:                      # written by the executor, checked by the verifier
    - ".autoloop/evidence/slugify-test.log"
  commit: ""                     # set at Phase 6; the SHA is proof the work is committed, not just built
  notes: ""                      # last defect on a failed attempt; retry context

- id: api
  outcome: "Move endpoint persists ordering and enforces auth"
  tier: FULL
  deps: [schema]                 # runs only after schema is done -> sequential
  status: todo
  gates:
    - "pnpm test -- api/move.test.ts"
    - "runtime: move card in running app; order persists after reload"
  evidence:
    - ".autoloop/evidence/api-test.log"
    - ".autoloop/evidence/api-runtime.txt"
  commit: "a1b2c3d"              # the merged commit; recorded at Phase 6
  notes: ""
```

## Status semantics

- `todo` → ready when every id in `deps` is `done`.
- `in_progress` → an Executor is working it (or was, pre-compaction; on resume,
  treat a stale `in_progress` as todo and re-verify rather than trust it).
- `done` → a Verifier returned PASS **and** the listed evidence files exist **and** a
  `commit` SHA is recorded (verified-but-uncommitted is not done).
- `needs-human-smoke` → verified only against a mock/preview; the real-runtime check
  (FS/IPC/PTY/network) couldn't be driven autonomously. **Not** `done` — surfaced in
  the report for a human pass.
- `blocked` → quarantined after the retry limit, or genuinely infeasible. Has an
  entry in `blockers.md`. Never silently flips back to done.

The `notes` field carries the last failure's defect so a retry (fresh subagent) has
the context without a separate defects file.

## Gate kinds (layer them)

A single passing unit test is weak proof. Where the feature warrants it, combine:

- **Executable check** — unit/integration test command that exits non-zero on fail.
- **Regression check** — the pre-existing suite stays green (catches collateral
  breakage).
- **Runtime proof** — exercise the actual running behavior, not just the test; record
  the observation as evidence. Guards against tests that pass while the feature
  doesn't work.
- **Anti-gaming check** — the Verifier diffs the current gate definitions against
  the baseline pinned at Phase 0 (hash/snapshot of the test+lint+CI config and
  existing test files); a weakened, narrowed, deleted, or mocked-out existing gate
  fails the task. Newly added tests are fine.
