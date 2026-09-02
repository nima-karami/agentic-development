# Pipeline — ledger, scheduling, concurrency

The pipeline is a **work queue with per-task stage state**, not a sequence. Several
tasks are in flight at different stages at once.

## Ledger

One file, outside version control, re-read on every orchestrator pass and after any
context compaction. It is the only durable truth about the run.

```yaml
- id: T-014
  title: <short imperative>
  stage: intake | spec | plan | review | execute | verify | integrate | report | done
  status: ready | running | blocked | parked
  attempts: 0
  deps: [T-009]
  claims:
    - <path or glob this task will write>
  artifacts:
    spec: <path>
    plan: <path>
    evidence: <dir>
  workspace: <isolated workspace path>
  note: <why parked / what it is waiting on>
```

`stage` is where the task is; `status` is whether it can move. The two are
independent — a task can be `verify` + `parked`.

## Scheduling

Each orchestrator pass:

1. **Re-read the ledger.** Always, and especially after compaction. Never act on a
   remembered queue.
2. **Reclaim orphans.** Any task marked `running` with no live worker returns to
   `ready` at its current stage.
3. **Select dispatchable tasks:** `status: ready`, dependencies `done`, and claims
   that do not conflict with anything currently running.
4. **Dispatch up to the concurrency limit**, in parallel.
5. **On each result**, advance the stage or handle the failure, then **write the
   ledger immediately** — before dispatching anything else.
6. Repeat until nothing is dispatchable and nothing is running.

**Never wait on a specific task.** If one task is in verification and another is ready
for spec, dispatch the second. The queue's job is to keep every stage busy.

## Concurrency by stage

| Stage | Parallel? | Why |
|---|---|---|
| spec, plan, review, report | Freely | Read-mostly; they write only their own artifact |
| execute | Yes, with isolation | Isolated workspace per task + non-overlapping claims |
| verify (per task) | Yes | Runs against the task's own workspace |
| **integrate** | **Never** | Merging into the shared tree and re-running the gate is the one serialization point |

Two independently-green tasks can still break each other once combined. Per-task
verification does not prove the integrated tree passes — only integration does, and
only one task integrates at a time.

## Claims and collisions

- Each task declares the paths it will write, before execute dispatches it.
- **Exclusive-claim paths** — application root, route tables, global styles, shared
  schemas, registries, dependency manifests — may be held by only one task at a time.
  These are the files every feature wants to touch, and the usual source of silent
  conflicts.
- Overlapping claims serialize **those two tasks only**. Everything else continues.
- A task whose claim cannot currently be satisfied returns to `ready` and is retried
  next pass. It does not block the pass, and it does not park.

## Failure handling

- **Verification fails** → the task returns to `execute`, `attempts` increments, and
  it carries the **real error output**, not a summary. A summarised failure makes the
  next attempt guess.
- **Attempts exhausted** (default 3 total) → `parked`, with the reason recorded. The
  queue continues.
- **Design fork discovered mid-execute** → park with the question stated. Never guess,
  and never resolve it silently to keep moving.
- **Integration fails** → the integrating task parks, the shared tree is restored to
  its last good state, and other tasks continue.
- **A parked task is never deleted and never hidden.** It appears in the report.

## Never

- Never halt the whole run because one task failed.
- Never mark a task `done` without verification evidence.
- Never let the orchestrator "just fix" a failing task itself — that collapses the
  isolation the pipeline depends on.
