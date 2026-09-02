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
      references/         e.g. the project's test-affordance surface
      assets/             e.g. a QA report template
    close/SKILL.md
    retro/SKILL.md
    …                     one directory per included archetype
    _shared/              optional: conventions cited by several skills
  scripts/
    README.md             script candidates — arguments and what each replaces
  docs/
    retro/                per-task retro notes: the unaddressed queue
      applied/            notes the retro has landed
  CHANGELOG.md
```

Two placements are deliberate:

- **`docs/retro/` lives inside the plugin**, not in the project's docs, so the suite's
  learning history travels with the suite. A retro store outside the plugin means
  installing the suite elsewhere brings none of what it learned.
- **`CHANGELOG.md` exists from the first version.** A retro that says "record what
  changed in the suite's changelog" against a plugin that has none leaves git history as
  the only record, and git history is not what the next retro reads.

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

```json
{
  "name": "<project>-marketplace",
  "owner": { "name": "<author>" },
  "plugins": [{ "name": "<project>-skills", "source": "./<project>-skills" }]
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
