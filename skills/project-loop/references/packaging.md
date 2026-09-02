# Packaging the emitted loop

The loop ships as a **Claude Code plugin**. That choice is deliberate: plugin skills
are namespaced and installed per machine, so one loop serves every repository and
worktree a project spans. Repository-local skills (`.claude/skills/`) cannot — they
reach only the repository they sit in.

## Layout

```
<project>-loop/
  .claude-plugin/
    plugin.json
  skills/
    orchestrate/SKILL.md      role owners
    spec/SKILL.md
    plan/SKILL.md
    review/SKILL.md
    execute/SKILL.md
    verify/SKILL.md
    report/SKILL.md
    retro/SKILL.md
    architecture/SKILL.md     knowledge routers
    ui/SKILL.md
    stack/SKILL.md
    contracts/SKILL.md
  agents/                     optional: role definitions for isolated dispatch
  hooks/hooks.json            optional: project gates wired to events
  settings.json               optional: project defaults
```

`plugin.json` requires only `name` and `description`; `version` is optional but worth
setting, since without it every commit counts as a new version.

```json
{
  "name": "vega",
  "description": "VEGA Life OS engineering loop",
  "version": "0.1.0"
}
```

The manifest `name` is the namespace: skills are invoked as `vega:spec`, `vega:ui`.

## Where it lives

- **Single-repository project** → inside that repository (e.g. `vega-loop/`), so the
  loop versions alongside the code it binds to and is reviewed in the same pull
  requests.
- **Multi-repository project** → its own directory or small repository beside the
  others, since no single repository owns the project.

Either way it is installed **by path**, once per machine:

```
/plugin marketplace add <path-to-the-loop-directory>
```

## Namespacing and precedence

Skill precedence for identically-named skills is
**enterprise → personal → project → bundled**. A repository-local skill sharing a name
with a personal one can therefore be shadowed by it.

Plugin skills sidestep this entirely: they are addressed as `<plugin>:<skill>` and
cannot collide with personal, project, or built-in skills. This is the second reason
the loop ships as a plugin — several projects can each define a `spec` role on the
same machine without interfering.

## What does not go in it

- Architecture descriptions, style guides, contracts, or decision records copied from
  the repository. Point at their paths instead.
- Anything discoverable from the tree in seconds.
- Anything that duplicates a general skill's methodology.

## Distribution caveat

Cloning a repository does **not** auto-install its plugin. A repository can declare a
marketplace and enabled plugins in its shared settings so collaborators are prompted,
but installation stays an explicit per-machine step. For a solo project this is a
one-time cost; for a team, document it in the project's setup instructions.
