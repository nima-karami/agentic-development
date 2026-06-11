# agentic-development

A lab for turning research into reusable [Claude Code](https://claude.com/claude-code)
**skills** (and tools) for agentic development.

The loop: dump deep-research on an agentic-development topic, read it critically,
then distill it into a self-contained, tested skill that improves day-to-day work
with coding agents.

## Layout

```
research/YYYYMM/<topic>-A.md   # two independent research syntheses per topic
research/YYYYMM/<topic>-B.md
skills/<skill-name>/SKILL.md    # skills distilled from the research
```

### The two-source convention

Every research topic has an **A** and a **B** synthesis from independent
researchers. A tends to be cautious and evidence-grounded; B tends to be confident
and prescriptive (and B's specific citations are sometimes unreliable — verify
before trusting). Skills are designed from where the two agree.

## Skills

| Skill | Distilled from | What it does |
|-------|----------------|--------------|
| [`solidify-repo`](skills/solidify-repo/SKILL.md) | `agent-human-repo` | Audits a repo for human/agent collaboration — instruction files, deterministic checks, a one-command verify harness, and a security gate — and applies fixes with per-category approval. |
| [`architecture-critic`](skills/architecture-critic/SKILL.md) | `agent-driven-architecture-design` | Fresh-context adversarial review of a written design *before* code: a 7-dimension rubric, severity-tagged findings, and a PROCEED/REVISE verdict. |
| [`feature-spec`](skills/feature-spec/SKILL.md) | `agent-driven-feature-spec` | Turns a vague feature idea into a right-sized spec before implementation — triage tiers to avoid over-production, fixed checklists for uniform coverage, and a machine-parseable handoff block for autonomous pipelines. |
| [`autonomous-build-loop`](skills/autonomous-build-loop/SKILL.md) | `long-running-agents` | Conductor that drives a whole wishlist to *verified* completion in one long/unattended run — composes the other skills per phase, keeps state on disk for resumability, and scales pipeline depth to each feature's tier. |

## Using a skill

Skills are authored and version-controlled here, but only take effect once copied
into your global Claude Code skills directory:

```bash
cp -r skills/<skill-name> ~/.claude/skills/
```

Then invoke it from Claude Code (e.g. "solidify this repo", or "review this design
before I build it").

## How skills are built

Each skill is authored with the **superpowers** plugin for Claude Code:
`brainstorming` to turn research into an approved design, then
`writing-skills` (test-driven — baseline the behavior with subagents, write the
skill to close the gap, refactor until solid).

## License

[MIT](LICENSE)
