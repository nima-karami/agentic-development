# Packaging the suite

The suite ships as **one plugin per project**, named `<project>-skills`. That is the
only vessel that is namespaced, installed once per machine, and therefore able to serve
every repository and worktree the project spans. Repository-local skills reach only the
repository they sit in; personal skills do not travel with the project.

## Layout

```
<project>-skills/
  .claude-plugin/
    plugin.json           name, version (semver), description, author
    marketplace.json      local install source — see below
  skills/
    start/SKILL.md
    spec/SKILL.md
    plan/SKILL.md
    design-review/SKILL.md
    build/SKILL.md
    code-review/SKILL.md
    qa/SKILL.md
      references/         everything the body points at: the project's test-affordance
                          surface, a QA report template, a long failure table
    close/SKILL.md
    retro/SKILL.md
    …                     one directory per included archetype
    _shared/              optional: depth facts cited by several skills — never the
                          canon or the binding block, which stay inline in each skill
  scripts/
    README.md             script candidates — arguments and what each replaces
  docs/
    retro/                per-task retro notes: the unaddressed queue
      applied/            notes the retro has landed
  CHANGELOG.md
  PROPOSED-<project>-changes.md   unattended runs only: every project-side edit as a
                                  ready-to-apply diff with its target path
  BOOTSTRAP-NOTES.md              unattended runs only: skipped gates and the assumption
                                  taken for each, what was regenerated and why,
                                  prove-it status, and generator defects found
```

**There is one directory for supporting files: `references/`.** A skill addresses one as
`references/<file>.md` relative to its own `SKILL.md`, and states that opening it is
required. Templates, report shapes and long tables all live there; do not invent a second
directory for them, and do not point at one from a body without creating it (see the
pointer-resolution step in the generator's Step 3).

**The two proposal files are the unattended mode's only write targets outside the
plugin — and they are inside it.** Steps that would write into the project (the pointer
block in its instruction file, the decision record, anything the prove-it run touches) go
into `PROPOSED-<project>-changes.md` instead, as diffs a human can apply; every gate
skipped and every assumption taken goes into `BOOTSTRAP-NOTES.md`. Use these exact names:
a second unattended run that invents its own filenames leaves two trails nobody finds.

Two placements are deliberate:

- **`docs/retro/` lives inside the plugin**, not in the project's docs, so the suite's
  learning history travels with the suite. A retro store outside the plugin means
  installing the suite elsewhere brings none of what it learned.
- **`CHANGELOG.md` exists from the first version.** A retro that says "record what
  changed in the suite's changelog" against a plugin that has none leaves git history as
  the only record, and git history is not what the next retro reads.

Both retro directories are empty at bootstrap and version control does not track empty
directories, so put a short `README.md` in each saying what it holds — otherwise the
learning store the layout is careful to place inside the plugin does not survive its
first commit.

## Manifest

`plugin.json` requires only `name` and `description`. Set `version` anyway and keep it
semver: without it every commit counts as a new version and an installed copy cannot be
told apart from the source.

```json
{
  "name": "<project>-skills",
  "version": "1.0.0",
  "description": "Tailored skills for <Project>: kickoff, spec, plan, review, build, QA, close, retro.",
  "author": { "name": "<author>" }
}
```

Start at `1.0.0` once the suite has passed its prove-it run. Bump **minor** when an
archetype is added or the pipeline is re-wired, **patch** when a gate or binding is
corrected. Every retro that applies a changelist bumps the version and writes the
changelog entry in the same change.

## The write-ownership table

The handoff block says what a stage **hands on**. Nothing in it says what a stage
**owns**, and two skills can each be perfectly correct on their own while writing the
same file. That conflict exists only *between* skills, so no per-skill review can see it,
and its symptom in production is silent data loss rather than an error.

So before packaging, tabulate every path the suite writes — run reports, run ledgers, QA
reports, evidence directories, review verdicts, retro notes, learnings files, archives —
and give each **exactly one owning skill**:

| Path | Owner | Others may |
|---|---|---|
| `<run dir>/report.md` | close (per task) | loop writes the ledger instead; qa and gate-health use their own filenames |
| `<run dir>/qa-report.md` | qa | — |
| `<run dir>/ledger.md` | loop | close appends its item's outcome under a conductor |
| `<retro dir>/<id>.md` | close | retro moves them to `applied/` |
| `<learnings file>` | build | close reads it, never writes it |

Rules for the table:

- **One owner per path.** A second writer is a defect, not a coincidence to note.
- **A split is allowed only when it is written into both skills.** A stage invoked in two
  shapes — once per task, and once per item under a conductor — legitimately writes
  different things in each. Say so in *both* bodies and in both handoff blocks: the
  per-task owner names what it hands to the conductor, and the conductor names what it
  takes over. A split assumed by one side and unknown to the other is the same bug.
- **A scheduled or out-of-pipeline stage gets its own directory or filename**, because it
  has no run slug and no business inside another run's directory.
- **Never let a per-item stage archive the conductor's live state.** That is what the
  next compaction resumes from, and archiving it after the first item ends the run.

Put the finished table in the plugin's `README.md` so the next retro can diff against it.

## Naming and the shadowing hazard

**Convention: bare archetype names inside the plugin, invoked `<project>-skills:<archetype>`.**
So `<project>-skills:spec`, `<project>-skills:build`. The manifest name is the
namespace; repeating the project inside the skill name makes the invocation stutter.

Why the namespace matters: skills with the same name resolve by precedence —
enterprise, then personal, then project, then bundled. A project-local `spec` skill can
therefore be **shadowed by a personal one with the same name**, silently, and the wrong
skill runs with no error to notice. Plugin skills are addressed with their namespace and
cannot collide, so several projects can each define a `spec` on one machine.

The one exception: a skill that must *also* be reachable outside the plugin — a personal
copy the user runs from anywhere — gets the suffixed form `<archetype>-<project>`,
because outside the plugin it lands in the flat namespace and needs to survive there.
Do not mix the two forms inside the plugin.

## Where the plugin directory lives

- **Single-repository project** → inside that repository, so the suite versions
  alongside the code it binds to and is reviewed in the same changes.
- **Multi-repository project** → its own directory or small repository beside the
  others, since no single repository owns the project.

Either way it installs **by path**, once per machine: add the directory holding the
marketplace manifest as a marketplace, then install the plugin from it. The marketplace
manifest works fine for a purely local, single-user plugin — the path can be a plain
directory. Team sharing just means putting the same manifest somewhere teammates reach.

The manifest lives at `<project>-skills/.claude-plugin/marketplace.json`, one directory
inside the plugin it advertises, so its `source` is the self-referencing `"./"`. A source
naming the plugin directory would only resolve if the manifest sat one level *above* it,
which is not the layout.

```json
{
  "name": "<project>-marketplace",
  "owner": { "name": "<author>" },
  "plugins": [{ "name": "<project>-skills", "source": "./" }]
}
```

**Verify the skills actually appear before calling it done** — check the installed
plugins on disk or have the user confirm the namespaced names show up. An install that
silently did nothing looks exactly like an install that worked.

## Supersession cleanup — and its order

When the plugin replaces existing copies (a workspace skills directory, per-repository
duplicates), the order is not optional:

1. Install and verify the plugin.
2. Back up anything git does not protect.
3. Check what references the old copies — instruction-file pointers, docs — and decide
   deliberately whether those pointers move or go.
4. Only then delete the old copies.

Deleting first leaves the user with nothing, because until the install is verified the
old copies are the only working set.

Two symptoms mean a non-plugin vessel is already failing: **hand-copying** (the same
skill duplicated into several repositories or worktrees — every copy is a future drift
bug) and **invisibility** (skills at a workspace root that sessions opened *inside* a
repository never see). The plugin is the fix, not more copying.

## Reach across repositories

A suite that sequences work across repositories — build one, bump another, push a third
— is the case that needs the plugin vessel. Reference sibling repositories by **role and
convention**, never by absolute path, so the skill survives a checkout in a different
location or on a different machine. When a skill genuinely needs a sibling's location at
runtime, have it discover that from the workspace layout or ask — never hard-code a path
that works on exactly one machine.

## Registering the suite with the project

Add a short block to the project's always-loaded instruction file: the suite's name,
when to reach for it, and the entry point. Point at the skills; never paste their
contents, which bloats every conversation and drifts out of sync.

Then rewrite that instruction file down to what must fire unconditionally — the gate and
its non-negotiability, commit hygiene, and the pointer to the suite. Everything
contextual moves to the docs the skills point at.

## Distribution caveat

Cloning a repository does not install its plugin. A repository can declare a marketplace
and enabled plugins in its shared settings so collaborators are prompted, but the
install stays an explicit per-machine step. For a solo project that is a one-time cost;
for a team, document it in the project's setup instructions.

## What never goes in the plugin

- Architecture descriptions, style guides, contracts, or decision records copied from
  the repository. Point at their paths.
- Anything discoverable from the tree in seconds.
- Machine paths, ticket keys, people's names, ports, or any other instance.
- Emitted scripts nobody asked for. `scripts/README.md` lists candidates; scripts get
  written on request.
- A `references/` pointer with no file behind it, and a second supporting directory
  alongside `references/`.
