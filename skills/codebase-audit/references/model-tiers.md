# Model tiers

The skill speaks only in tiers. This file maps them to models. The rule underneath is
the house canon: the session holds decisions; judgment-heavy delegated work runs one
tier below the session; mechanical work two tiers below, with a floor at the mid tier;
never delegate upward; the bottom tier never builds against slow or flaky suites and
never writes a root-cause diagnosis.

**This skill is the judgment-heavy exception.** Judging an unfamiliar codebase is the
work the audit exists for, and a wrongly judged or wrongly confirmed finding costs more
than the tokens saved. So the **judgment tier runs at the session's model** — the same
tier, never above it. Mechanical and bulk work stay below.

**The session's tier caps everything.** Choose the session model once, at the start of
the audit, and never dispatch above it. The top tier is not used for audits — its
cost buys nothing the session tier cannot do here.

## Roles to tiers

| Role | Tier | Why |
|---|---|---|
| Orchestrator: scope, slicing, merge, final severity | session | holds every decision |
| Verifier of a **Critical** finding | session | a falsely confirmed Critical is the most expensive error the audit can make |
| Intent ledger, judges, verifiers | judgment | the judgment-heavy core; runs at the session's model |
| Extractors, test strength, measurement, baseline assembly | mechanical | they write and run scans; the floor keeps them off the bottom tier because they execute tooling |
| Bulk classification (commit author class, comment what-vs-why, candidate pre-filter) | bulk | high volume, narrow labels, spot-checked by the extractor that asked |

## Claude Code

| Tier | Model | Dispatch |
|---|---|---|
| session | Opus | the session itself |
| judgment | Opus | subagent, `model: opus` |
| mechanical | Sonnet | subagent, `model: sonnet` |
| bulk | Haiku | subagent, `model: haiku` |

- Name `model` explicitly on every dispatch; an omitted model inherits the session's
  and silently runs every agent at session cost.
- The top tier (Fable) is never used by this skill.
- **Cost.** Judges and verifiers dominate the bill. To spend less, lower the depth or
  the number of slices — never the judges' model. If a budget forces mid-tier judges
  for a low-stakes dimension (verbosity is the usual candidate), record that in the
  profile's audit plan and in the report, and expect a lower `confirmed_share`.

## Codex

From OpenAI's Codex docs, fetched 2026-10-12 (models, subagents, skills pages at
learn.chatgpt.com/docs). The mapping below is an inference from the docs' own
positioning; re-check model names before relying on them — Codex retires models on a
short cycle.

| Tier | Model | Reasoning effort |
|---|---|---|
| session | `gpt-6.1-sol` | Extra High |
| judgment | `gpt-6.1-sol` | High |
| mechanical | `gpt-6.1-sol` | Medium |
| bulk | `gpt-6-luna` | High (the docs' suggested start for Luna) |

- **The top model (`gpt-6-astra`) is never used by this skill**, the same way the top
  tier is never used under Claude Code: its cost buys nothing the session tier cannot
  do here. Codex therefore has two models in play, and the tiers above Luna are
  separated by **reasoning effort**, not by model. Critical verifiers run at the
  session's effort.

- **Dispatch.** Codex spawns subagents when the prompt, a skill, or `AGENTS.md` asks
  for it explicitly — phrase each wave as "spawn a fresh agent per …". Each subagent
  runs in its own thread; the parent waits for all of them and receives summaries.
- **Binding a tier.** Cleanest: one custom agent file per tier in `.codex/agents/`
  (`name`, `description`, `developer_instructions`, `model`,
  `model_reasoning_effort`), then spawn by agent name. Otherwise set the model at
  spawn time; the fallback order is spawn value → `agents.default_subagent_model` →
  the parent's model.
- **Concurrency.** `agents.max_concurrent_threads_per_session` in
  `~/.codex/config.toml`; set it to about four for audits.
- **Install path.** Codex reads skills from `.agents/skills/` (repo, up to the git
  root) or `~/.agents/skills/`, not the Claude Code skills directory. Invoke with
  `$codebase-audit` or `/skills`.
- **Frontmatter.** Only `name` and `description` are documented; `allowed-tools` has
  no documented effect there.
- **Instruction files.** Codex reads `AGENTS.md`, not `CLAUDE.md`. A repo that keeps
  its rules in `CLAUDE.md` needs an `AGENTS.md` pointer or
  `project_doc_fallback_filenames = ["CLAUDE.md"]`, or the intent ledger misses them.
- **Unconfirmed:** whether subagents can spawn their own subagents, and the config
  values for effort levels above `low`.

## When the harness cannot dispatch subagents

The waves still run, **one at a time in the same session**, with discipline replacing
isolation:

1. Write every wave's output to `work/` exactly as a subagent would.
2. Before each judge pass, start from a clean context if the harness allows it (a new
   session or task reading only the files the brief lists); otherwise re-read only the
   brief's inputs and nothing else.
3. Never verify a finding in the same pass that produced it. Run the verifier pass as a
   separate session or task over `work/findings/`, with only the fields the verifier
   brief allows.
4. Mark the report `isolation: sequential` so a reader knows the judges shared a
   context, and expect a lower confirmed share.
