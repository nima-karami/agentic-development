# The state ledger

The plan and progress live on disk, not in the conversation, so the run survives
compaction, interruption, and resumption. After any compaction or restart, the
Supervisor **re-reads this ledger before acting** — it is the single source of
truth, above any recollection.

Put the ledger in a stable, ignored-by-build location in the target repo, e.g.
`./.autoloop/`. Keep entries terse and machine-greppable.

## Files

| File | Holds | Re-read on resume |
|---|---|---|
| `goal.md` | The real, user-visible outcome the whole wishlist serves. One paragraph. The thing the Supervisor checks the finished set against. | yes |
| `plan.md` | The decomposition rationale + the dependency graph (which tasks block which). | yes |
| `tasks.yaml` | One entry per task: id, outcome, deps, gates, evidence paths, status. The work queue. | yes |
| `evidence/` | Test logs, run output, screenshots, verifier notes — the proof a task passed. | on demand |
| `defects.md` | Append-only: every FAIL with the concrete defect and which gate caught it. | on demand |
| `blockers.md` | Quarantined/infeasible features with the reason and what would unblock them. Surfaced in the final report. | yes |
| `changelog.md` | Append-only one-liner per completed task: what changed, what remains. The resumption summary. | yes |
| `gate-baseline.txt` | Phase 0 snapshot (hashes) of the gate definitions — test/lint/CI config and existing test files — that Phase 5 diffs against to detect weakened gates. | on demand |

## `tasks.yaml` shape

```yaml
- id: slugify
  outcome: "Exported slugify(str) producing URL-safe slugs per spec"
  deps: []                       # ids that must be done first; [] = independent
  status: todo                   # todo | in_progress | done | blocked
  gates:                         # executable; each must pass
    - "node --test test/slugify.test.js"
    - "node scripts/lint.js"
  evidence:                      # written by the executor, checked by the verifier
    - ".autoloop/evidence/slugify-test.log"

- id: api
  outcome: "Move endpoint persists ordering and enforces auth"
  deps: [schema]                 # runs only after schema is done -> sequential
  status: todo
  gates:
    - "pnpm test -- api/move.test.ts"
    - "runtime: move card in running app; order persists after reload"
  evidence:
    - ".autoloop/evidence/api-test.log"
    - ".autoloop/evidence/api-runtime.txt"
```

## Status semantics

- `todo` → ready when every id in `deps` is `done`.
- `in_progress` → an Executor is working it (or was, pre-compaction; on resume,
  treat a stale `in_progress` as todo and re-verify rather than trust it).
- `done` → a Verifier returned PASS **and** the listed evidence files exist.
- `blocked` → quarantined after the retry limit, or genuinely infeasible. Has an
  entry in `blockers.md`. Never silently flips back to done.

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
