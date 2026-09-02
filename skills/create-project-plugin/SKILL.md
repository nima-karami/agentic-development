---
name: create-project-plugin
description: Grow a project its own tailored suite of skills so generic workflow skills stop re-deriving the same project context every run. Use when the user wants to "set up project skills", "make a start-<project>-task", "bootstrap skills for this repo/workspace", "turn our conventions into a skill", package a project's skills as a plugin, or evolve/refresh existing project skills as the project matures. Trigger this whenever someone notices a generic skill keeps re-explaining the project to itself, or says the skills should grow up with the project.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, WebSearch, AskUserQuestion
---

# Create Project Plugin

Grow a project its own **tailored skill suite**, and keep it current as the project
matures. This is the factory behind skills like `start-trident-task`: a generic
kickoff skill, specialized until it *knows* the project's repos, conventions, docs,
and rules cold.

## Core principle — bake in what a generic skill keeps re-deriving

A generic workflow skill (`start-<generic>-task`, a generic review skill) has to
re-establish the same context on every run: *which repo, which branch convention,
which docs matter, who owns what, what "done" means here.* That work is real, it's
repeated, and the model does it slightly differently each time — so results drift.

A **project skill** presses those durable facts into the skill itself, once. Then
every future run starts at "what's the task" instead of "what is this project." The
whole value of this tool is producing skills that read as if written by someone who
knows the project intimately — because the reference the author consulted *was* the
project.

So the job is not "write a skill." It's: **extract a project's durable conventions
and press them into skills, in the right vessel, wired so they interconnect and stay
current.** Two failure modes to avoid at all costs:

- **Overfitting to today.** Don't hard-code a branch number, a ticket, a person, or
  a transient path. Bake the *convention* (the branch-naming rule), not the instance.
- **Re-deriving forever.** If a generated skill still says "figure out which repo
  this touches" with no project-specific help, you haven't specialized anything.

## A suite is a pipeline, not a pile

A mature suite is stages that hand off, not a menu of disconnected helpers. The shape
that works: the **kickoff routes by scale** (small → build directly; medium → plan →
build; large → spec → plan → review → build, then quality-pass, then delivery on
request), and each stage **locks its decisions with the user before the next descends**
— the spec owns *what*, the plan owns *how*, the build owns *doing*. Three wiring rules
make the pipeline hold:

- **Briefs travel forward explicitly.** A stage doesn't inherit the conversation that
  preceded it — the router hands each stage its inputs (repo/branch layout, confirmed
  intent, settled decisions, artifact paths). An unbriefed stage re-derives, or worse,
  guesses.
- **Settled decisions are never re-litigated downstream.** A stage that finds one
  genuinely broken says so and re-locks with the user — never silently adapts.
- **Cross-cutting rules bind pipeline-wide, stated once.** Evidence standards, tripwire
  patterns, commit conventions — put them where every stage can cite them (the router or
  a shared reference), phrased identically, not re-derived per skill.

## Gates beat restatement

When discovery (especially a session retro) shows a project rule that **exists in
writing and still gets violated**, the fix is a *gate* baked into the stage where the
violation happens — a required proof before a "done" claim, a diff-against-plan check
before a commit, a mandatory full-grep behind any consistency claim — never a louder
restatement of the rule. Distinguish the two failure kinds explicitly: a **knowledge
gap** (no rule exists → write the fact into the owning skill/doc) versus an
**enforcement gap** (rule exists, gets skipped → add the gate). Most of a suite's real
power comes from its gates.

## The three modes

Detect which one applies by checking whether the project already has a skill suite
(look for `.claude/skills/`, a `*-skills` plugin, or user-level `start-<project>-task`).
Confirm with the user rather than assuming.

| Mode | When | What it does |
|---|---|---|
| **bootstrap** | No suite yet | Discover the project, propose a suite from the catalog, generate the picked skills into their right vessels, wire pointers. |
| **add** | Suite exists, want more | Light re-discovery, generate the new archetype(s), wire them into the existing suite. |
| **evolve** | Suite exists, project has moved | Audit existing skills against *current* conventions, find drift, propose and apply updates. This is the "retro". |

Never fabricate a mode transition. If discovery shows a partial suite, say so and let
the user pick bootstrap-the-rest vs add-one vs evolve. A **lone pre-existing skill in a
different vessel** (e.g. a user-level `start-<project>-task` when you're bootstrapping a
workspace plugin) isn't a full suite, but it *is* an overlap — surface it and reconcile
(fold it into the new suite, supersede it, or leave it and cross-link), never silently
generate a duplicate beside it.

---

## Mode: bootstrap

### 1. Discover the project

Read `references/project-discovery.md` and follow it. In short: read every
`CLAUDE.md`/`AGENTS.md` **up the whole tree** (a repo under a workspace inherits the
parent's rules), the docs read-when index, git-log conventions, existing skills, and
any memory. Produce a short **project profile**: repos and who owns what, branch/commit
conventions, the docs map, the "done" bar, and the tooling loop. You'll cite this
profile inside every skill you generate — so get it right, and show it to the user to
correct before generating anything. A wrong profile is the cheapest bug to fix here
and the most expensive one to fix after six skills embed it.

### 2. Propose the suite

Read `references/archetypes.md` — the catalog of skill types this tool knows how to
generate. Map the project profile onto it: recommend the archetypes this project would
actually use, skip the ones it wouldn't. Present the shortlist with a one-line reason
each, and let the user pick (they'll add more later — a suite grows, it isn't
front-loaded). Don't push the whole catalog onto a small project; right-sizing the
suite is as much the job as right-sizing each skill.

### 3. Decide the vessel for each picked skill

Read `references/scope-and-wiring.md`. For each skill decide: per-repo
(`<repo>/.claude/skills/`), per-user (`~/.claude/skills/`), or part of a workspace
**plugin** (`<project>-skills`) when it spans repos or must ship to a team. This is a
per-skill decision — a deploy skill that spans repos and a repo-local review skill land
in different places. When a project is multi-repo (like a workspace of sibling repos),
the plugin vessel is usually right and is what makes the suite installable and
interconnected.

### 4. Generate each skill

Read `references/skill-authoring.md` before writing any skill — it's the quality bar
that keeps generated skills from being bloated or musty. For each picked archetype:
start from the archetype's shape, fill it with the project profile, and write it to its
chosen vessel. Generated skills must be **self-contained** (no pointers to files
outside their own repo/plugin) and written in plain terms — they're committed work.

### 5. Wire and register

Per `references/scope-and-wiring.md`: create the plugin's `plugin.json` +
`.claude-plugin/marketplace.json` if you built a plugin, add the pointer block to the
project's `CLAUDE.md` so sessions know the suite exists, and cross-link skills that
hand off to each other (kickoff → spec → plan → execute). Tell the user exactly how to
install/activate what you built and how a teammate picks it up.

---

## Mode: add

Same as bootstrap steps 2–5, but skip full discovery — read the existing suite first
(it already encodes the project profile), refresh only what's stale, then generate the
new archetype(s) and wire them in alongside the existing ones. Match the shape and
voice of the skills already there so the suite stays one learnable pattern.

---

## Mode: evolve (the retro loop)

This is what makes the suite mature *with* the project instead of rotting.

1. **Re-run discovery** (`references/project-discovery.md`) to get the *current*
   profile.
2. **Diff against what the skills encode.** For each existing project skill, look for
   drift: conventions that changed (a new branch rule, a renamed doc, a new repo), file
   paths the skill references that no longer exist, steps that no longer match how the
   team works, and *new* recurring patterns that deserve their own skill or archetype.
   `git log` on the skill files and on `CLAUDE.md`/docs since the skill was last touched
   is the fastest drift signal.
3. **Propose a changelist** — per skill: keep / update (with the specific edit) /
   retire / split. Group it so the user can approve category by category.
4. **Apply** the approved changes, re-wire pointers, and note what changed so the next
   retro has a baseline.

Offer to leave behind a shippable **`retro` skill** (an archetype) so this loop travels
with the repo and the team can trigger it without this tool installed.

---

## A note on rigor

Generated skills are committed, long-lived, and read by teammates and future sessions.
Hold them to the same bar the project holds its code: correct placement, self-contained,
named for the role not the moment, additive-not-breaking when you evolve them. Being
lazy about *scope* (don't generate an archetype nothing needs) is good; being lazy about
*rigor* (a skill that overfits, or re-derives, or points at a file that moved) is not.

## Running unattended

The modes above have deliberate human gates — show the profile before generating, let the
user pick the suite, approve the changelist before applying. Those exist because a wrong
profile or an unwanted skill is cheap to catch here and expensive later. When there's **no
human** (a pipeline, an autonomous run), don't treat a gate as a dead stop: proceed on the
**safest defaulting assumption**, record each skipped gate and the assumption you made as
an explicit note in the output, and prefer generating into a scratch/proposed location the
user can review over writing straight into live vessels. The rule is *never block, always
leave a trail* — a human should be able to read back exactly which decisions you made on
their behalf and undo any of them.

## Reference files

- `references/project-discovery.md` — what to read to learn a project, and the profile to produce.
- `references/archetypes.md` — the catalog: one entry per skill type, with shape and scope defaults.
- `references/scope-and-wiring.md` — per-repo vs per-user vs plugin; how to package and register.
- `references/skill-authoring.md` — how to write a *good* project skill (the quality bar).
