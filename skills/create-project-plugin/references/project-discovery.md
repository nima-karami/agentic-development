# Project discovery

Discovery produces one **profile** and five **inventories**. Every later step cites
them, so read widely, then distil, then show the profile to the user before generating
anything.

Fan out readers one tier below the session for breadth; read directly when the project
is small. Stop when you could write the profile and defend it — not when you have read
everything.

## What to read, in order

1. **Every always-loaded instruction file up the whole tree.** A repository checked out
   under a workspace inherits the parent's rules: the parent carries cross-repo
   conventions the repository cannot see, the repository-local one carries its own
   toolchain. Read *both*, never just the nearest. Walk from the working directory up
   to the drive root, and include the per-user one.
2. **The docs read-when index.** A matured project usually keeps an index — "read this
   file when your task matches this trigger". That index *is* the project's own map of
   where knowledge lives, and it becomes the read-when binding in the kickoff skill.
   **Capture the index, not the contents.**
3. **Existing skills.** Any kickoff, review, deploy or QA skill already installed for
   this project, in any vessel. Prior art: it shows the voice, what is already
   captured, and what is missing. In evolve mode it is the baseline you diff against.
4. **Git conventions.** The last ~50 subjects plus a few full messages: branch naming,
   subject format (ticket prefix? conventional commits?), trailer policy, how changes
   are described. Read the *pattern*, never copy an instance.
5. **Memory, tickets, plans, past run reports.** They reveal in-flight work, the "done"
   bar, and decisions not visible in code. Past run reports are the cheapest source of
   real failure patterns.
6. **The tooling loop.** How the project builds, tests, serves, verifies, and ships —
   the script definitions, the single verify command and what it actually runs, the dev
   server convention, the staging or preview flow. The build, QA and deliver archetypes
   need this exact.
7. **Recent session transcripts, when they exist.** The strongest evidence of what the
   suite must *gate*: user corrections, re-explanations, and rejected tool calls mark
   exactly where general behavior failed this project. Mine user text turns first
   (delegate the bulk reading), rank friction by cost, and classify each finding. A rule
   the user had to state twice is a rule the suite must enforce, not merely mention.

## The profile

Factual and durable — conventions, not instances.

```
## <Project> profile

- Repos / ownership:   <repo> owns <X>; <repo> owns <Y>  (or "single repo")
- Workspace shape:     single-repo | multi-repo workspace | monorepo
- Branch convention:   <rule>
- Commit convention:   <subject shape; trailer policy>
- Docs map:            <read-when index: trigger → doc path>
- Artifact homes:      specs | plans | decisions | run state | evidence | learnings
- "Done" bar:          <what must pass; the quality standard>
- Gate command:        <exact command, where it runs, what it covers>
- Tooling loop:        <build / test / serve / verify / ship, in order>
- Cross-cutting rules: <invariants a skill must not violate>
- Delivery flow:       <PR tooling, release script — or "none">
- Lifecycle stance:    pre-production | live users   ← decides the shim/flag stance
- Failure patterns:    <recurring friction, each tagged knowledge-gap or
                        enforcement-gap, with the gate it implies>
- Existing skills:     <what is already there, general or project-specific>
- Gaps to interview:   <what could NOT be inferred>
```

**Lifecycle stance is asked, never inherited.** "No compatibility shims, no flags to
stage a cutover, temporary feature loss is acceptable" is correct for a pre-launch
project and wrong for one with live users. It changes the spec, design-review and build
archetypes.

## Inventory 1 — homeless knowledge

List every operational fact that exists **only** in the always-loaded instruction file:
build gotchas, non-default ports, external toolchain requirements, request/response
contracts, deliberately dormant features, false-green gates.

For each: propose a home in the project's own documentation. Get approval, move them,
then point at the new location from the skill that needs it.

This inventory is why the suite shrinks the instruction file instead of duplicating it.
A fact with no home anywhere is the reason people say the agent "just knows" things — it
does not, and neither will the next teammate.

## Inventory 2 — exclusive-claim paths

The files two concurrent tasks cannot both edit: the application root or entry, route
tables, global styles, shared schemas, registries, dependency manifests, generated API
surface files. These are the files every feature wants to touch and the usual source of
silent conflicts.

Name them explicitly. They become the plan archetype's claim list and the build
archetype's serialization rule. When disjointness is uncertain, the emitted skills
serialize — merge corruption costs more than the wall-clock saved.

## Inventory 3 — the observability check

Answer one question with evidence: **can the real artifact be run and observed, and
how?**

- The exact launch path — command, working directory, ports, required environment.
- The project's own test affordance, if any: a debug handle, a control API, a seeded
  fixture mode, a headless driver config. These non-obvious affordances are the reason
  a QA skill earns its place; without them QA is a stranger poking a black box.
- Every variant the artifact ships to — brand, theme, locale, platform, viewport — so
  QA never verifies only the reference one.
- What the unit gate is structurally blind to here (rendering, wiring, byte-level
  corruption, real service contracts).

**If the artifact cannot be observed, do not emit a QA archetype.** Emit a finding:
observability is the blocker, and fixing it comes before the suite. A QA stage that
can only read unit output will report passes nobody saw.

## Inventory 4 — script candidates

Every mechanical routine noticed during discovery: workspace or ticket setup, teardown,
resource or port allocation, environment wiring, integrity scans, evidence capture,
release steps. For each record the trigger, the manual sequence it replaces, the
arguments it would take, and the failure it currently causes when done by hand
(half-created workspaces, forgotten teardown, colliding ports).

This inventory becomes the plugin's script-candidates file. **Write no scripts unless
the user asks.** The list exists because agents default to doing all of this by hand,
tool call by tool call, and that cost is invisible until someone counts it.

## Inventory 5 — conventions the suite adds rather than observes

The other four inventories record what the project *has*. This one records what the suite
**needs and the project does not have yet** — most often the run learnings file canon item
6 requires, sometimes an evidence directory, a run ledger, or a place for review verdicts.

This is the gap between two hard rules that otherwise contradict each other here: *bind
only to what exists* forbids asserting a directory the project lacks, and *homeless
knowledge gets a home first* covers facts stranded in the instruction file, not files the
suite itself introduces. Neither covers this case, so name it explicitly.

For each addition record:

| Field | Content |
|---|---|
| The convention | the file or directory, and its shape |
| Needed by | the archetype that cannot work without it, and which canon item or gate demands it |
| Proposed home | the exact path, matching the project's existing conventions |
| Why not observed | it does not exist yet, versus it exists under a different name |

Every entry lands in the proposal file rather than being written into the project, and
the skill that introduces it says so in its own body — so the addition is visible as an
addition and easy to overrule. In an emitted skill, an added convention that a canon item
asserts is carried as a project clause on that item (see `canon.md`), never as a silent
edit to the canon text.

An addition nobody approves is not a blocker: state the assumption, note that the file is
created by the stage that needs it at first use, and record it.

## Interview only for the gaps

Infer everything the reads above can give. Ask only what changes what you would
generate: an ambiguous ownership boundary, a "done" bar the docs do not state, the
lifecycle stance, which archetypes the project actually wants. Batch two to four
questions, each with a recommendation. A convention readable from the commit log is not
a question.

## Evolve mode

Re-run the reads to get the *current* profile, then add two diffs the bootstrap pass
does not need:

- **Skill against seed.** Each emitted skill versus the general skill it was pressed
  from. Seeds gain gates over time; a suite pressed from an old seed is missing all of
  them.
- **Binding against reality.** Every path, command and directory the suite names,
  checked to still exist. The change log on the instruction file and the docs directory
  since the suite was last touched is the fastest drift signal.
