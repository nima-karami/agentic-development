# Role contracts

Every role owns **one stage** and emits **one handoff artifact**. Paths in
`<angle brackets>` are resolved during detection to the project's real locations —
never imposed.

Each role delegates *methodology* to the matching general skill and supplies only the
project bindings. It never restates the general skill's content.

---

## Orchestrator

- **Owns:** the queue. Selects what is dispatchable, launches roles, records results.
- **Reads:** the ledger only.
- **Emits:** dispatches, and ledger updates after every result.
- **Never:** writes production code, authors a plan, or grades work. Never waits on
  one task while another is dispatchable. Never resolves a design fork itself — it
  parks the question.
- **Isolation:** main context, kept deliberately small. It reads the ledger, not the
  codebase; the moment it starts reading source files its context fills and the run
  shortens.

## Spec

- **Owns:** request → specification.
- **Reads:** the request; **existing comparable features in the project**; the
  conventions and documentation routers.
- **Emits:** `<specs dir>/<project naming convention>`.
- **Delegates to:** `feature-spec`.
- **Never:** designs the implementation. A specification states behaviour, states,
  edge cases, defaults, and acceptance criteria — not file layout. Never invents a
  convention: it matches how existing features in this project are specified.
- **Isolation:** separate context.

Surveying existing features first is what makes the specification consistent with the
project rather than generically correct.

## Plan

- **Owns:** specification → implementation plan.
- **Reads:** the specification; the architecture router; the actual code it will
  touch.
- **Emits:** `<plans dir>/<project naming convention>`.
- **Never:** writes code. Never re-litigates the specification — if the specification
  is wrong or ambiguous, it parks the task back to spec rather than deciding.
- **Isolation:** separate context.

## Review

- **Owns:** critiquing the plan **before any code exists**.
- **Reads:** the plan, the specification, the architecture router.
- **Emits:** a verdict — approved, or a list of required changes; a decision record in
  `<decisions dir>` when it changes direction.
- **Delegates to:** `architecture-critic`.
- **Never:** authored the plan it reviews. Never rewrites the plan — it returns
  required changes and the plan role revises. Never approves by default when
  uncertain; uncertainty is a required change.
- **Isolation:** separate context, and never the context that produced the plan.

## Execute

- **Owns:** approved plan → code, for exactly one task.
- **Reads:** the approved plan, the specification's acceptance criteria, and only the
  routers relevant to what it touches.
- **Emits:** code in an isolated workspace, plus evidence of what it ran.
- **Delegates to:** `autonomous-build-loop` for loop discipline, test-first discipline
  for the code itself.
- **Never:** weakens, narrows, mocks, or suppresses a gate check to make progress.
  Never declares its own work verified. Never edits outside its declared claim. Never
  guesses at a design fork — it parks the question.
- **Isolation:** separate context **and** an isolated workspace.

## Verify

- **Owns:** grading the change against the specification.
- **Reads:** the change itself, the specification's acceptance criteria, the project's
  gate result, and direct observation of the running artifact.
- **Emits:** pass or fail, with evidence — captured output, recordings, logs, exit
  codes — and, on failure, the **real error output** rather than a summary of it.
- **Never:** reads the executing role's narration or reasoning. Never fixes what it
  finds — it reports and returns the task. Never passes on unit tests alone when the
  artifact can actually be run and observed.
- **Isolation:** separate context, receiving only the change and the specification.
  This is the whole reason the role exists: a verifier that sees the implementer's
  case for correctness grades the argument instead of the code, and agrees with it.

## Report

- **Owns:** assembling the human-facing artifact for review.
- **Reads:** evidence, the ledger, the emitted artifacts.
- **Emits:** `<runs dir>/<date>-<name>/` containing the report and its captured
  images and recordings.
- **Delegates prose style to:** `humanize-writing`.
- **Never:** re-grades anything. Never omits a parked or failed task to make the run
  look cleaner — the parked list is the most useful part of the report.
- **Isolation:** separate context.

## Retro

- **Owns:** proposing improvements to the loop itself.
- **Reads:** run reports, **the human's review comments on them**, the parked-task
  list, and the ledger's history of repeated failures.
- **Emits:** a proposal — concrete diffs to routers, bindings, acceptance-criteria
  templates, or the instruction file — for human approval.
- **Never:** applies its own changes. Never edits the general skills; its blast radius
  is this project's loop. Never proposes weakening a gate as the remedy for a check
  that keeps failing — a repeatedly failing check is a finding about the code or the
  binding, not about the check.
- **Isolation:** separate context; proposes only.

**Triggered by:** an explicit request, or accumulation — several completed runs, or a
failure pattern repeating across tasks.
