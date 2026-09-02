---
name: project-loop
description: "Use when a project should get its own engineering loop — project-bound roles that carry features from request through spec, plan, review, build, verification, and report, plus a retrospective that improves the loop. Triggers - 'set up an agentic loop for this project', 'project-specific skills or plugin', 'adapt the general skills to this repo', 'the agent re-learns the codebase every session', onboarding agents to a mature project whose conventions have drifted from general defaults, or needing several features in flight at once."
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, AskUserQuestion
---

# Project Loop

## Overview

A general skill knows methodology but not this project: not its gate command, not
where its specs live, not which invariants must never break. A mature project has
drifted from every default, so each session the agent re-derives the same context and
still gets the project-specific things wrong.

The fix is not to copy the project into a set of forked skills. The loop **topology**
— who does what, and what each stage hands the next — is general. Only its
**bindings** are project-specific.

**Core principle: generate bindings, never content. The repository owns what is true
about the project; the loop owns who acts, when to read what, and what each stage
hands to the next.**

The emitted loop is a namespaced bundle installed once per machine, so it works across
every repository and worktree a project spans. See `references/packaging.md`.

## When to use

- A project with real, non-obvious conventions that agents keep getting wrong.
- Work that spans several repositories or worktrees, where per-repository
  configuration cannot reach.
- A backlog that needs several features in flight at once rather than one at a time.

**When NOT to use:**

- A new or small project with no established conventions — there is nothing to bind
  to yet, and the bindings would be invented rather than observed.
- A single one-off feature. Use the general skills directly.
- As a substitute for the project's own documentation. If a fact has no home in the
  repository, the fix is to give it one there — not to inline it here.

## Hard rules

1. **The repository owns content; the loop owns routing.** Never copy architecture
   descriptions, style guides, contracts, or decision records into the loop. Point to
   them by path. A copy becomes a second source of truth and silently drifts from the
   code it describes.
2. **One role, one stage, one handoff.** Every emitted role owns exactly one stage and
   emits exactly one artifact. A role that both writes a plan and reviews it is a blob
   role — split it. Reviewer and author are never the same role.
3. **The pipeline never blocks on a single task.** Tasks advance independently. One
   task in verification must not stall another entering spec. A task that cannot
   progress parks and the queue keeps moving.
4. **Isolate by role.** Roles that must not inherit each other's reasoning run in
   separate contexts. The verifying role sees the change and the specification — never
   the implementing role's narration of why it believes the work is correct.
5. **Bind only to what exists.** Detect the project's real commands, directories, and
   conventions. Never invent a convention the project does not have, and never
   restructure the project to fit the loop.
6. **Never weaken the project's gate.** The loop consumes the project's existing
   verification command as-is. Narrowing, mocking, or deferring a check to make the
   loop pass defeats the loop's only source of truth.
7. **Homeless knowledge gets a home in the repository.** When detection finds an
   operational fact recorded nowhere but the always-loaded instruction file, propose a
   home for it in the project's documentation and point at it. Do not inline it.

## Steps

### 1 — Detect

Read the project before writing anything. Establish, with evidence:

- Every repository and worktree the project spans.
- The single verification command, and what it actually runs.
- Where the project already puts specifications, plans, decision records, run
  reports, and autonomous-run state. **These become the handoff artifacts.**
- The always-loaded instruction file: its size, and which of its contents are
  operational facts versus content duplicated from elsewhere.
- How the real artifact is launched and observed, beyond unit tests.

### 2 — Inventory homeless knowledge

List every operational fact that exists only in the instruction file: build gotchas,
non-default ports, external toolchain requirements, request/response contracts,
deliberately dormant features. For each, propose a home in the project's own
documentation. Get approval, move them, then point at the new locations.

This step is why the loop shrinks the instruction file instead of duplicating it.

### 3 — Bind the pipeline

Map each role's handoff to a real path in the project, using the naming convention the
project already uses. Where a stage has no existing artifact home, propose one
consistent with its neighbours rather than importing a foreign layout.

Identify the project's **exclusive-claim paths** — application root, route tables,
global styles, shared schemas, registries — the files that two concurrent tasks cannot
both edit. See `references/pipeline.md`.

### 4 — Emit the loop

Write the role owners and the knowledge routers. Roles come from
`references/roles.md`; each is bound to the paths and commands found in step 1.
Knowledge routers are trigger plus pointer plus invariants only — never prose copied
from the documents they point at.

Rewrite the always-loaded instruction file down to what must fire unconditionally: the
gate and its non-negotiability, commit hygiene, and a pointer to the loop. Everything
contextual moves to a router that loads on demand.

### 5 — Prove it on one real task

Run the loop end to end on one small, real piece of work. A loop that has never
carried a task is a guess. Confirm each handoff artifact appears where it should, the
verifying role fails a deliberately broken change, and a parked task does not stall
the queue.

### 6 — Record

Write a short decision record in the project's own convention: what was bound, what
was moved out of the instruction file, and what was deliberately left alone.

## Role contracts

Each role owns one stage and one handoff. Full contracts in `references/roles.md`.

| Role | Owns | Isolation |
|---|---|---|
| Orchestrator | Schedules the queue, dispatches roles, updates the ledger | Main context |
| Spec | Request → specification, in the project's conventions | Separate |
| Plan | Specification → implementation plan | Separate |
| Review | Critiques the plan before code exists | Separate; never the plan's author |
| Execute | Plan → code, one task, isolated workspace | Separate |
| Verify | Grades the change against the specification | Separate; never sees Execute's reasoning |
| Report | Assembles evidence for human review | Separate |
| Retro | Reads reports and human comments; proposes loop changes | Separate; proposes only |

## Common mistakes

- **Copying the project's documentation into the loop.** The most common failure and
  the hardest to detect later, because the copy looks authoritative while going stale.
- **Making the orchestrator do the work.** It schedules and dispatches. When it starts
  writing code itself, isolation is gone and the context fills.
- **A blocking pipeline.** Running the queue strictly one task at a time is simpler to
  write and defeats the purpose. Verify the parallel path actually works.
- **Letting the verifying role read the implementing role's justification.** It then
  grades the narration instead of the change, and agrees with it.
- **Emitting roles for stages the project cannot support.** A project with no way to
  observe its running artifact does not get a verification role that pretends
  otherwise — fix the observability first.
- **Inventing conventions.** A layout the project does not use will be ignored by
  every human working in it, and the loop's artifacts will drift out of the places
  people look.

## Gotchas

- **The always-loaded instruction file is the only thing guaranteed to load.** Routers
  load when their trigger matches, which is not certain. Rules that must never be
  missed stay in the instruction file; only contextual depth moves to routers.
- **A pointer costs a read the agent can skip.** State that opening the file is
  required and that seeing the path is not reading it. Keep the irreducible
  never-get-this-wrong lines inline; point for the detail.
- **Per-task verification passing does not mean the integrated tree passes.** Two
  independently-green tasks can break each other on merge. Integration is a
  serialization point.
- **A stale binding is worse than no binding.** When the project moves a directory or
  renames its gate, the loop points at nothing. The retrospective role exists partly
  to catch this.
- **Bundle skills are namespaced; local ones are not.** A locally-installed skill with
  the same name as a personal one may be shadowed by it. Namespacing avoids the
  collision entirely.

## Reference files

- `references/roles.md` — the full contract for each role: what it owns, reads,
  emits, and must never do.
- `references/pipeline.md` — ledger schema, scheduling, concurrency and collision
  rules, retry and parking behaviour.
- `references/packaging.md` — the emitted bundle's layout, manifest, installation,
  and how it reaches multiple repositories.
