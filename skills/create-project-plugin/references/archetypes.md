# Archetype catalog

The skill types this tool knows how to generate. A project picks the ones it needs and
adds more as it goes — never front-load the whole catalog. Each archetype below gives: its
**intent**, the **generic seed** it specializes (if one exists), its **default vessel**
(per-repo / per-user / plugin — see `scope-and-wiring.md`), and the **shape** its
generated skill should have.

When specializing a skill that has a generic seed already installed (e.g. `feature-spec`,
`solidify-repo`), read that seed first and preserve its structure — you are pressing
project facts into a proven shape, not reinventing the workflow. Mine the seed for its
**signature patterns** — the parts that make it good, not just its steps (e.g. a
"lock-each-design-level before descending" ladder, a "restate and wait for confirmation"
gate). Those are exactly what a fresh from-scratch generation silently loses, so carry
them across deliberately.

**Locating a seed.** Seeds usually live at `~/.claude/skills/<name>/SKILL.md` or inside an
installed plugin under `~/.claude/plugins/`. But some skills are registered by the harness
and have **no file on disk** — you'll see the name and description in the available-skills
list but `find`/`Glob` turns up nothing. When that happens: reconstruct the seed's shape
from its visible metadata and, if you've seen it run, its observed behavior; otherwise
generate fresh from the archetype shape below and **tell the user the seed wasn't
readable** so they can graft in any signature pattern you couldn't recover. Never block on
an unreadable seed.

Order below follows a typical dev lifecycle; a project rarely wants all of it at once.

**Compose as a pipeline, not a menu.** When a project takes several lifecycle archetypes,
wire them as routed stages (see SKILL.md's "A suite is a pipeline"): the kickoff assesses
scale and routes — small → execution directly; medium → implementation-plan → execution;
large → feature-spec → implementation-plan → architecture-review → execution — then
quality-pass, then delivery on the user's explicit request. Each skill's description names
its pipeline neighbors so handoffs trigger naturally.

---

## 1. `kickoff` — start-`<project>`-task

- **Intent:** the front door for a new task — pick repo, find the ticket, cut the
  branch, then design top-down before any code. The single highest-value archetype.
- **Seed:** a generic `start-<generic>-task` if one exists.
- **Vessel:** per-user usually (it's your personal on-ramp), or plugin for a shared team.
- **Shape:** setup half (repo → ticket → branch, using the project's *actual* repo list
  and branch/commit conventions from the profile) then a routing half (restate intent and
  get it confirmed → read only what the task matches via the docs map → clarify → assess
  scale → route to the pipeline stage that matches, handing it an explicit brief). Bake in
  the project's docs read-when index so the skill tells its user exactly which doc to read
  for which task. In a full pipeline suite the kickoff is the *router*, not the designer —
  design conversations live in the spec and plan stages it routes to. It's also the natural
  home for cross-cutting evidence rules the whole pipeline cites (a consistency claim needs
  the full grep, not a sample; a negative claim needs a recursive search; a sibling's
  pattern is re-read from current code, not memory).

## 2. `feature-spec` — spec a feature to the project's bar

- **Intent:** turn a vague request into a right-sized, buildable spec before code.
- **Seed:** the generic `feature-spec` skill.
- **Vessel:** per-user or plugin.
- **Shape:** the generic spec flow, plus the project's own notation, accessibility/i18n
  bar, and "done" criteria pulled from the profile — so specs land at the project's
  standard, not a generic one.

## 3. `implementation-plan` — plan a change the project's way

- **Intent:** turn a spec into an ordered, file-level implementation plan.
- **Seed:** the strongest generic planning skill available (e.g. a writing-plans skill) —
  keep its signature moves when specializing: a file-structure section that locks
  decomposition before tasks, per-task Interfaces blocks (Consumes/Produces with exact
  signatures, so tasks read in isolation stay consistent), a banned-placeholders list
  ("TBD", "add appropriate error handling", "similar to Task N"), and a self-review
  (spec coverage / placeholder scan / signature consistency across tasks).
- **Vessel:** per-user or plugin.
- **Shape:** the project's plan file format and location (e.g. `docs/plans/`), its
  commit-sequence convention, its style-guide conventions copied concretely into a Global
  constraints section, and its "settled decisions don't get re-litigated" rule. **Calibrate
  task detail to the executor tier explicitly with the user:** a plan executed by a weaker
  model carries exact paths, exact signatures, and test intents with expected failures —
  every judgment call (names, placement, abstractions) made in the plan, none left to the
  executor. Decide the full-code-bodies question deliberately (bodies maximize weak-model
  safety but go stale in committed plans and get copied blindly; signatures + test intents
  is usually the better trade when execution runs under a gated build skill).

## 4. `execution` — build to a plan under the project's gates

- **Intent:** execute a plan test-first and keep the gates green.
- **Seed:** a generic executing-plans / TDD / autonomous-loop skill if present.
- **Vessel:** per-user or plugin.
- **Shape:** the project's exact verify command, test conventions, and the "commit is the
  last build step" rule. Cite the tooling loop from the profile precisely — including any
  known **false-green gates** (a linter that passes vacuously in some layout, a lockfile
  that silently absorbs a local link) discovered in the profile's failure patterns. Two
  gates earn their place in almost every execution skill:
  - **The done-claim gate** — no "done"/"wired" on user-visible behavior without driving
    the real artifact once and reporting what was observed; work whose deliverable is
    *looks* is verified by looking (side-by-side against the reference, captured before
    the old rendering is deleted), never by green tests alone.
  - **Subagent plan-fidelity** — every delegated executor's brief ends with "diff your
    change list against the files the plan names; anything extra — especially shared or
    engine-level code — is stop-and-report, not a judgment call," and deviation reports
    lead with the fix that keeps the locked decision, never with the escape hatch.

## 5. `architecture-review` — fresh-eyes design check

- **Intent:** critique a design/boundary before it's built or merged.
- **Seed:** a generic `architecture-critic` if present.
- **Vessel:** per-user or plugin.
- **Shape:** the project's architectural invariants (the cross-cutting rules from the
  profile — ownership boundaries, contract seams, additive-not-breaking rules) as the
  lens the review applies.

## 6. `deploy-release` — the project's release/preview runbook

- **Intent:** a repeatable deploy or preview-stack flow, baked from the project's docs.
- **Seed:** none — generate from the profile's tooling loop and any deploy doc.
- **Vessel:** **plugin** when it spans repos (build repo A, bump repo B, push branch C);
  per-repo only if the whole flow lives in one repo.
- **Shape:** ordered steps with the real commands, the branch/artifact naming rules, the
  known failure modes, and the "these must match" contracts. This is the archetype most
  likely to need multi-repo interconnection — see `scope-and-wiring.md`.

## 7. `onboarding` — orient in this project

- **Intent:** a "get oriented" skill for a new session or teammate — the architecture
  map, who owns what, the docs read-when index, where things live.
- **Seed:** none — generate from the profile and docs map.
- **Vessel:** plugin (team-facing) or per-repo.
- **Shape:** a guided tour that points at the project's own diagrams/docs rather than
  restating them, so it stays current as those update.

## 8. `plugin-packaging` — package this project's skills as a plugin

- **Intent:** wrap a project's loose skills into an installable, shareable plugin with a
  marketplace manifest.
- **Seed:** none — this is `scope-and-wiring.md`'s packaging steps as a repeatable skill.
- **Vessel:** the project itself (it acts on the project's own skills).
- **Shape:** collect the project skills, generate `plugin.json` +
  `.claude-plugin/marketplace.json`, document install. Generate this only when a project
  has enough skills that manual packaging is a chore.

## 9. `retro` — review and update the project's own skills

- **Intent:** the evolve loop as a shippable skill, so the suite matures with the project
  without this tool installed.
- **Seed:** none — this is `SKILL.md`'s evolve mode distilled into a standalone skill.
- **Vessel:** plugin or per-repo (it should travel with the project).
- **Shape:** two evidence streams, then a changelist. (1) Re-read the profile and diff
  against what the skills encode. (2) **Mine recent session transcripts** — enumerate the
  project's `~/.claude/projects/<dir>/*.jsonl` in the window, extract user text turns
  first (corrections and re-explanations are the gold; delegate bulk reading to
  cheap-model subagents), rank friction by cost, and classify each finding knowledge-gap
  vs enforcement-gap. Then propose keep/update/retire/split per skill, grouped for
  per-category approval; apply; and record what changed and when, so the next retro
  diffs against a baseline instead of re-mining the same window. Emit this whenever a
  project adopts the suite seriously, so drift gets caught on a cadence, not by accident.

## 10. `runtime-qa` — drive the real artifact and report

- **Intent:** hands-on verification in the real runtime — a browser, a CLI invocation, a
  live service — producing an evidence-backed report a human can read without re-running
  anything. This is the skill the execution archetype's done-claim gate calls.
- **Seed:** none — generate from the profile's tooling loop and any test/automation
  affordances the project exposes (a debug handle, a control API, a seeded fixture mode:
  the non-obvious affordances are the reason this skill earns its place).
- **Vessel:** plugin or per-repo.
- **Shape:** settle and restate the scope (including every variant the change ships to —
  brand/theme/locale/platform — never just the reference one) → bring the artifact up the
  project's documented way → drive it, capturing evidence as you go (screenshots/output
  before navigating away) → report with repro steps per finding, severity framed by user
  impact, and explicit statement of what was *not* covered. Never report a pass that
  wasn't observed.

## 11. `quality-pass` — simplify + conventions over a diff

- **Intent:** post-build quality review of changed code — reuse, simplification,
  efficiency, right altitude — plus a conventions pass driven by the project's actual
  style authority. Quality only; bugs found in passing are reported, not fixed here.
- **Seed:** a generic simplify/cleanup skill if present (often harness-registered with no
  readable file — reconstruct from observed behavior and say so).
- **Vessel:** plugin or per-repo.
- **Shape:** two passes over the diff with file:line findings before any edit: structure
  (dead machinery — with consumers proven through indirection layers before deletion —
  courier params, redundant split pairs, wrong-layer logic) and conventions (read the
  repo's style guide *every run*, never infer from an open file; naming, placement,
  comment policy, type discipline). Behavior-preserving, provably: if the diff touches
  user-visible surfaces, end with a real click-through — a "simplify" pass silently
  removing animations is the failure this guards.

## 12. `delivery` — PRs and review conventions

- **Intent:** the project's pull-request flow: description format, creation tooling,
  comment/reply etiquette — invoked only on explicit request, since committing is the
  default endpoint of a build.
- **Seed:** a generic pr-description skill if present; keep its section format and
  style rules, change where the artifact lives.
- **Vessel:** plugin (it cites cross-repo ticket and tooling conventions).
- **Shape:** the ticket-key title rule, the body sections and voice, verification content
  sourced from the runtime-qa pass, and the project's tooling facts — auth scopes, known
  CLI footguns, comment-authorship marking. Keep the draft out of the repo tree (a
  description file swept up by `git add -A` is a real failure mode); stage it in scratch
  space or chat.

---

## Adding a new archetype

If a project has a recurring workflow none of these cover, that's a signal to add an
archetype — not to force-fit an existing one. Give it the same entry shape (intent /
seed / vessel / shape) and add it here so future projects benefit. The catalog is meant
to grow the same way a project's suite does.
