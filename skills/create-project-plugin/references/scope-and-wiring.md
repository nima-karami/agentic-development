# Scope and wiring

Where a skill lives, and how it connects to the rest of the suite. This is a **per-skill**
decision — one suite routinely spans all three vessels.

## The three vessels

| Vessel | Path | Use when | Trade-off |
|---|---|---|---|
| **Per-repo skill** | `<repo>/.claude/skills/<name>/` | The skill is about *one* repo and should travel with it, be committed, and picked up by any session opened there. | Auto-discovered, zero install. Invisible outside that repo. |
| **Per-user skill** | `~/.claude/skills/<name>/` | The skill is *your* personal on-ramp (a kickoff you run everywhere), not something the team needs. | Private, always available to you. Doesn't travel with the repo or team. |
| **Workspace plugin** | a `<project>-skills` plugin | The skill spans repos, must ship to a team, or a set of skills should install and version together. | Installable, interconnected, shareable. Needs a manifest and an explicit install. |

### Choosing

- One repo, personal → **per-repo** or **per-user** (per-user if it's your habit across
  many projects; per-repo if the team benefits and it's repo-specific).
- Spans sibling repos in a workspace (a deploy that builds A, bumps B, pushes C) →
  **plugin**. A per-repo skill can't see its siblings; a plugin owned by the workspace can.
- Team should get the whole suite in one step → **plugin**.

Two symptoms mean the current vessel is already failing and the plugin is overdue:
**hand-copying** (`.claude/` folders copied into worktrees or fresh checkouts, the same
skill duplicated into several repos — every copy is a future drift bug), and
**invisibility** (skills at a workspace root that sessions opened *inside* a repo or
worktree never see). A workspace-level `.claude/skills/` has exactly this blind spot;
the plugin is the fix, not more copying.

When unsure between per-repo and plugin for a multi-repo *project*, prefer the plugin —
it's the only vessel that lets skills reference the workspace as a whole and hand off to
each other across repos.

## Building a workspace plugin

A minimal Claude Code plugin is a directory with a manifest and a `skills/` folder:

```
<project>-skills/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── start-<project>-task/SKILL.md
    ├── deploy-<project>/SKILL.md
    └── …
```

`plugin.json`:

```json
{
  "name": "<project>-skills",
  "version": "0.1.0",
  "description": "Tailored skills for the <Project> workspace.",
  "author": { "name": "<author>" }
}
```

To make it installable across a team, add a marketplace manifest at the repo/workspace
root that points at the plugin:

```
.claude-plugin/marketplace.json
```

```json
{
  "name": "<project>-marketplace",
  "owner": { "name": "<author>" },
  "plugins": [
    { "name": "<project>-skills", "source": "./<project>-skills" }
  ]
}
```

The local install flow (verified working) is two user-run commands:

```
/plugin marketplace add <path-to-workspace-root>     # where marketplace.json lives
/plugin install <plugin-name>@<marketplace-name>
```

Verify the plugin's skills actually appear before calling it done — check the installed
plugins/marketplaces on disk or have the user confirm the prefixed skill names show up.
The marketplace manifest works fine for a **local, single-user** plugin too (the path can
be a non-git workspace directory); genuine team sharing just means the same manifest in a
location teammates can reach.

**Supersession cleanup is part of the migration, and it's ordered.** When the plugin
replaces existing copies (workspace `.claude/skills/`, per-repo duplicates): delete the
old copies only **after** the install is verified — until then they're the only working
set, and deleting first leaves the user with nothing. Back up before deleting anything in
a location git doesn't protect. Repo-*committed* copies of a generic skill are removed
only when the plugin (or a user-level copy) is genuinely the distribution now — check
what references them (`AGENTS.md`/`CLAUDE.md` pointers) before pulling them out, and
remove or keep those pointers deliberately.

**Version the plugin.** Bump `plugin.json`'s semver whenever the suite changes shape (a
skill added, a pipeline re-wired) so an installed copy can be told apart from the source.

## Wiring the suite together

Generated skills are more than a pile — they hand off and reference shared facts.

- **CLAUDE.md pointer.** Add (or update) a short block in the project's `CLAUDE.md` that
  names the suite and when to reach for it, so every session knows it exists. Point to the
  skill; don't paste its contents (that bloats every conversation and drifts out of sync).
- **Cross-links between skills.** Where one skill ends and another begins (kickoff → spec
  → plan → execute → review → deploy), name the next skill so the handoff is explicit.
- **Shared conventions live once.** If several skills cite the same branch rule or docs
  map, and they're in a plugin, factor it into a shared reference file the skills point at
  — so evolving a convention is one edit, not N. Per-user/per-repo skills that can't share
  a file should still phrase the convention identically so a future retro can find them.
- **Never cross-reference outside the vessel.** A committed skill must be self-contained:
  no pointers to a sibling repo's files, a workspace doc it can't see, or your machine's
  paths. State the fact inline instead. This is what keeps a skill working when someone
  clones just that repo.

## Interconnection across repos

A multi-repo deploy/release skill is the common case that *needs* the plugin vessel: it
references several repos by role and sequences work across them. Keep the repos referenced
by their **role and convention** (build the shell, bump the proxy) rather than by absolute
path, so the skill survives a checkout in a different location. If it must know a sibling's
location at runtime, have it discover that from the workspace layout or ask, rather than
hard-coding a path that only works on one machine.
