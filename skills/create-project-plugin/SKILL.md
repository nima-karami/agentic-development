---
name: create-project-plugin
description: "Use when a project should get its own skills instead of re-teaching a general skill what the project is every session. Triggers - 'set up project skills', 'make a project-specific plugin', 'bootstrap skills for this repo/workspace', 'adapt the general skills to this repo', 'turn our conventions into a skill', 'package our skills as a plugin', 'bootstrap a start-<project>-task', the agent re-learns the codebase every session, or evolving / retro-ing a project's existing skill suite as it matures."
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, Agent, AskUserQuestion
---

# Create Project Plugin

Grow a project its own skill suite — one installable plugin whose skills carry the
project's conventions, gates, and artifact locations, and keep it current as the
project moves.

## Core principle

A general workflow skill knows methodology but not this project: not its gate
command, not where specs live, not which invariants must never break. So every
session re-derives the same context, slightly differently each time, and still gets
the project-specific parts wrong.

The fix is not to fork the general skills. Split what is being carried:

- **Method** — how to spec, plan, build, review, verify. General, and pressed into
  the emitted skill so it stands alone.
- **Bindings** — the gate command, the branch rule, the artifact paths, the
  read-when map. Project-specific, generated from discovery.
- **Content** — architecture, style guides, contracts, decision records. **Owned by
  the repository.** The plugin points at it by path and never copies it.

**The repository owns content; the plugin owns routing and method.** An emitted skill
is not a forwarder — it does not say "invoke the general spec skill"; it *is* this
project's spec skill. But it never restates what the project's own docs already say.

Two failure modes to avoid at all costs:

- **Overfitting to today.** A ticket number, a person, a branch, a machine path, a
  port baked into a skill is a bug with a delay fuse. Bake the *convention*.
- **Re-deriving forever.** A generated skill that still says "figure out which repo
  this touches" specialized nothing.

## When to use

- A project with real, non-obvious conventions that agents keep getting wrong.
- Work spanning several repositories or worktrees, where per-repository
  configuration cannot reach.
- A suite that already exists and has drifted from the project, or from the general
  skills it was pressed from.

## When NOT to use

- A new or small project with no established conventions. There is nothing to bind
  to, and the bindings would be invented rather than observed.
- A single one-off feature. Use the general skills directly.
- As a substitute for the project's documentation. A fact with no home in the
  repository gets a home *there*, not inlined here.

## Hard rules

1. **The repository owns content; the plugin owns routing and method.** Never copy
   architecture descriptions, style guides, contracts, or decision records into an
   emitted skill. Point at them by path. A copy becomes a second source of truth and
   silently drifts from the code it describes.
2. **Conventions inline, instances never.** The branch rule, the commit-subject
   shape, the gate command, the artifact locations and the "done" bar go inline in
   every skill that needs them — those are what a pointer would make the agent skip.
   A ticket key, a person, a port, a today-branch, an absolute machine path never do.
3. **Emitted skills are self-contained within the plugin.** No pointer outside the
   plugin except to paths inside the project's own repositories. A plugin-internal
   shared reference is allowed and preferred over inlining the same fact N times.
4. **Homeless knowledge gets a home in the repository first.** An operational fact
   living only in the always-loaded instruction file gets a proposed home in the
   project's docs, approved and moved, and *then* a pointer. This is why the suite
   shrinks the instruction file instead of duplicating it.
5. **Knowledge gap gets a fact; enforcement gap gets a gate.** A rule that exists in
   writing and is violated anyway needs a checkable step at the violation point — a
   required proof, a diff-against-plan check. Restating the rule louder is the
   failure mode.
6. **The canon is copied, never paraphrased.** Cross-cutting rules bind pipeline-wide
   and are injected identically from `references/canon.md`. Identical wording is what
   lets one search find every copy when a rule changes.
7. **Bind only to what exists.** Detect the project's real commands, directories and
   conventions. Never invent a convention the project does not have and never
   restructure the project to fit the suite. A stale binding is worse than none.
8. **Never weaken the project's gate.** The suite consumes the existing verification
   command as-is. Gates are development discipline, not production-only.
9. **The suite needs no rented infrastructure.** No emitted skill may require an
   external account, hosted service, or extra tool the project does not already run.
   Surface any unavoidable dependency and let the user decide.
10. **Show the profile before generating.** A wrong profile is the cheapest bug to
    fix at this point and the most expensive after twelve skills embed it.
11. **No scripts unless asked.** Script candidates are listed, not written (Step 6).
12. **Never emit an archetype the project cannot support.** A project with no way to
    observe its running artifact gets a finding — "fix observability first" — not a
    QA skill that pretends.

## Modes

Detect by checking whether the project already has a suite: a project-scoped skills
directory, an installed suite plugin, a personal kickoff skill named for the project.
Confirm with the user rather than assuming; never fabricate a mode transition.

| Mode | When | What it does |
|---|---|---|
| **bootstrap** | No suite | Discover → propose → generate → wire → prove → record. All steps. |
| **add** | Suite exists, more wanted | Steps 3–8 only. Light re-discovery: the existing suite already encodes the profile; refresh what is stale. Match the shape and voice already there. |
| **evolve** | Suite exists, project moved | The retro. See below. |

A **partial** suite is not a mode — say so and let the user pick bootstrap-the-rest,
add-one, or evolve. A **lone pre-existing skill in a different vessel** (a personal
kickoff skill when you are bootstrapping a workspace plugin) is not a suite but it
*is* an overlap: surface it and reconcile — fold it in, supersede it, or leave it and
cross-link — never silently generate a duplicate beside it.

## Steps

### 1. Discover

Follow `references/project-discovery.md`. It produces the **project profile** plus
four inventories every later step consumes: homeless knowledge, exclusive-claim
paths, the observability check, and script candidates.

Delegate the reading breadth to agents one tier below this session; this session
holds the profile and the decisions. Stop when you could write the profile and defend
it, not when you have read everything.

**Show the profile to the user and get it corrected before generating anything.**

### 2. Propose the suite

Pick a **preset** (below) as the starting shortlist, then adjust against the profile.
Present the shortlist with a one-line reason each and let the user pick. A suite
grows; it is not front-loaded. Right-sizing the suite is as much the job as
right-sizing each skill.

### 3. Generate each skill

For each picked archetype, in this order:

1. **Seed** — read the general skill named in the catalog. Preserve its signature
   patterns: the triage tier, the lock-one-level-at-a-time ladder, the restate-and-
   wait gate, the self-review before emitting, the machine-parseable handoff block.
   These are what a from-scratch generation silently loses. When the seed has no
   readable file, reconstruct from its description and observed behavior, and say so.
2. **Specialize** — press the method in. The emitted skill is the project's skill for
   that stage, complete on its own.
3. **Bind** — fill the binding block from the profile: gate command, artifact
   locations, branch and commit conventions, read-when map, "done" bar.
4. **Inject canon** — copy the items `references/canon.md` assigns this archetype,
   verbatim, plus the binding block.
5. **Self-review** — against `references/skill-authoring.md`. A skill that still tells
   its reader to "figure out the project's conventions" goes back to step 2.

### 4. Wire, package, register

Wire per the rules below: the kickoff routes by scale, each stage's handoff block is
the contract with the next, and each skill's description names the neighbours it hands
to. Then package per `references/packaging.md` — the manifest with a starting semver,
the local marketplace manifest, the pointer block in the project's always-loaded
instruction file, and the retro directories inside the plugin so the learning history
travels with the suite. Tell the user the exact install steps and how a teammate picks
it up.

### 5. Prove it on one real task

Run the pipeline end to end on one small, real piece of work. A suite that has never
carried a task is a guess. Confirm three things specifically:

- Every handoff artifact appears where the binding says it will.
- The review and QA stages **fail a deliberately broken change**. A stage that passes
  everything is not a stage.
- A parked task does not stall the others.

Fix what the run exposes before recording. This step is the difference between a
generated suite and a working one.

### 6. Record

Two records. **Script candidates:** the mechanical routines discovery found — workspace
setup, teardown, resource allocation, integrity scans, evidence capture — into the
plugin's script-candidates file, each with the arguments it would take and the manual
sequence it replaces. **Write no scripts unless the user asks;** the list is the ask,
and agents doing these by hand tool call by tool call are the cost it makes visible.
**Decision record:** in the project's own convention — what was bound, what moved out
of the instruction file, what was deliberately left alone, which archetypes were
skipped and why. Then the first changelog entry at the starting version.

## Mode: evolve

The retro that keeps the suite maturing with the project rather than rotting.

1. **Read the plugin's retro notes first** — they are pre-tagged, they were written by
   sessions that knew what hurt, and what sits unfiled is by construction the
   unaddressed set. Sweep session transcripts only for what the notes left open.
2. **Classify** each finding: knowledge gap, enforcement gap, or one-off. Also collect
   the counter-examples — what went cleanly, and which investment paid for it.
3. **Diff each emitted skill against its current seed.** Seeds improve; a suite pressed
   from a six-month-old seed is missing every gate added since. Carry the improvements
   across, keeping the project bindings. In the same pass, **re-check every path binding
   still exists** — a renamed directory or a moved gate turns a skill into a confident
   liar, and nothing else in the suite looks for it.
4. **Diff against existing homes** before proposing anything, so a rule is strengthened
   or moved, never forked into a second place.
5. **Propose a changelist** grouped by category — keep / update (with the edit) / add /
   retire / split — for per-category approval.
6. **Apply, bump the version, write the changelog entry, file the notes.** An unchecked
   box is a decision, not an oversight to absorb silently.

Full procedure and note format: `references/learnings-chain.md`.

## Archetype catalog

Detail per archetype — bindings required, gates carried, shape notes — in
`references/archetypes.md`.

| Archetype | Seed pressed in | Included when |
|---|---|---|
| **manage** | none — desk charter | multi-repo workspace or multi-session work |
| **start** | none — kickoff and router | always |
| **spec** | the general spec skill | always |
| **plan** | the general planning skill | always |
| **design-review** | the general design-critic skill | always; FULL work only at runtime |
| **build** | the general build-and-verify skill | always |
| **code-review** | the general code-review skill | always |
| **qa** | the general runtime-QA skill | when the artifact can be observed |
| **deliver** | none — project-bound | when the project has a delivery flow |
| **close** | none — distillation gate and teardown | always |
| **gate-health** | the general repo-hardening skill, re-audit mode | always, scheduled by the retro |
| **loop** | the general autonomous-loop skill | when unattended runs are wanted |
| **retro** | none — the evolve mode, shipped | always |

## Presets

Two axes. Present the intersection as the shortlist, then adjust.

**By project shape:**

| Preset | Archetypes |
|---|---|
| `single-repo-app` | start, spec, plan, design-review, build, code-review, qa, close, gate-health, retro |
| `multi-repo-workspace` | the above **+ manage, deliver** |
| `library-or-cli` | the single-repo set **− qa** (no observable surface), with a contract/compatibility check folded into code-review |

**By methodology source:**

- `lab-seeds` (default) — the seeds in the catalog, read as templates and pressed in.
  The emitted suite has no runtime dependency on them, and none on any external plugin,
  account or service.
- `bring-your-own` — the user names an external flow. Map that flow's stages onto the
  catalog's archetypes instead of the seeds, keeping the catalog's inclusion rules,
  gates and handoff contracts. A stage the named flow has no equivalent for is
  reported, not invented.

Add `loop` to any preset when the user wants unattended runs.

## Pipeline wiring rules

- **The kickoff routes by scale.** Small (one obvious change in one place) → build.
  Medium (clear scope, a few files, no new seam) → plan → build. Large (a new or
  changed seam, cross-repo effects, real open decisions) → spec → plan →
  design-review → build. When in doubt, bias up. Setup-only is a route of its own:
  scaffold and stop.
- **Code-review then QA always follow build** for anything user-facing. Deliver runs
  only on explicit request; commit is the default endpoint. Close always runs.
- **Briefs travel forward explicitly.** A stage does not inherit the conversation
  before it. The router hands each stage: the workspace or worktree paths, the
  confirmed intent, the settled decisions, and the artifact paths it reads and
  writes. An unbriefed stage re-derives, or worse, guesses.
- **Settled decisions travel forward and are never re-litigated downstream.** A stage
  that finds one genuinely broken says so and re-locks — never silently adapts.
- **The handoff block is the contract.** Each stage ends with a machine-parseable
  block naming its artifact, its tier, and its verdict or counts. The next stage reads
  the block, not the prose. Keep the block's shape stable across versions.
- **The pipeline does not block on one task.** A task in QA must not stall another
  entering spec. A task that cannot progress parks with its reason recorded and the
  queue keeps moving.

## The learnings chain

Three hops, each with a gate, and the whole reason the suite improves:

1. **Capture** — canon 6: per-slice tagged bullets into the run's learnings file.
2. **Distil** — at close, a ≤15-line note with `## Friction` and `## Worked` sections
   into the plugin's retro directory. **Teardown is refused until the note exists**,
   even when it says "nothing notable" — skipping it starves the retro.
3. **Promote** — the retro reads the notes, classifies, applies on approval, bumps the
   version, writes the changelog entry, and files applied notes away so what remains is
   exactly the unaddressed set.

Procedure, note format and changelist format: `references/learnings-chain.md`.

## Running unattended

The gates above exist because a wrong profile or an unwanted skill is cheap to catch
here and expensive later. With no human, never treat a gate as a dead stop:

- Proceed on the **safest defaulting assumption** and record each skipped gate with the
  assumption made.
- **Generate into a proposed location** for review rather than writing straight into
  live vessels.
- Never call an interactive question tool; a would-be question becomes a recorded
  decision-needed item.
- **Never block, always leave a trail** — a human must be able to read back exactly
  which decisions were made on their behalf, and undo any of them.

## Model routing

This skill is an orchestrator. The session holds the profile, the suite shortlist, the
judgment calls inside each generated skill, and the changelist. Discovery reading,
transcript mining and first drafts go one tier below the session; bulk listing and
mechanical edits two below with a floor at the mid tier; never above the session.
Concrete model names are in `references/canon.md`. The tell that this is being broken:
this session running its fifth directory listing in a row instead of reading a report.

## Common mistakes

- **Copying the project's documentation into the plugin.** The most common failure and
  the hardest to detect later, because the copy looks authoritative while going stale.
- **Emitting forwarders.** A skill whose body is "read the general spec skill, then
  apply our conventions" adds a hop and no knowledge. Press the method in.
- **Front-loading the whole catalog.** Twelve skills nobody asked for are twelve
  bindings to keep current.
- **Paraphrasing the canon**, so a rule change means finding nine wordings instead of
  one. **Baking in an instance** — a branch, a ticket, a port, a machine path — each of
  which works for exactly one week.
- **Generating a QA skill for an unobservable artifact**, so the suite ships a stage
  that can only lie.
- **Skipping the prove-it run.** A suite that has never carried a task is a guess, and
  its first real user finds the broken handoff.
- **Copying another project's incident scars.** A scar is load-bearing because it is
  *this* project's; a borrowed one is a decoration a session will rationalize past.

## Gotchas

- **A pointer costs a read the agent can skip.** State that opening the file is
  required and that seeing the path is not reading it. The irreducible
  never-get-this-wrong lines stay inline; point for the depth. And the always-loaded
  instruction file is the only thing guaranteed to load at all — a skill fires when its
  description matches, which is not certain, so rules that must never be missed stay in
  the instruction file with a pointer to the suite.
- **Per-task verification passing does not mean the integrated tree passes.** Two
  independently-green tasks can break each other on merge. Integration is a
  serialization point, and the suite must have one.
- **A stale binding is worse than no binding.** No binding makes the agent look; a
  stale one makes it confidently open nothing. The retro's path re-check exists for
  this alone.
- **Plugin skills are namespaced; loose ones are not.** A project-local skill sharing a
  name with a personal one can be shadowed by it, silently, and the wrong skill runs.
  The plugin vessel sidesteps this; installing it stays an explicit per-machine step,
  which belongs in the project's setup instructions. See `references/packaging.md`.
- **The pre-production stance is a parameter, not a rule.** "No compatibility shims, no
  flags to stage a cutover, temporary feature loss is acceptable" is right for a
  pre-launch project and actively wrong for one with live users. Ask; do not inherit.

## Reference files

- `references/project-discovery.md` — what to read, and the profile and inventories to produce.
- `references/archetypes.md` — the catalog: seed, inclusion rule, bindings, gates, shape per archetype.
- `references/packaging.md` — layout, manifests, install, versioning, namespacing, multi-repo reach.
- `references/skill-authoring.md` — the quality bar for an emitted skill.
- `references/learnings-chain.md` — capture → distil → promote, note and changelist formats.
- `references/canon.md` — the nine cross-cutting rules to copy verbatim, and the tier table.
