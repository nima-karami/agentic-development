# The Software Factory, Loop Engineering and Graph Engineering: What Is Real as of October 2026

A software factory is the whole delivery system: agents move work from intake to verified, shipped change while humans set intent and approve risk. "Loop engineering" and "graph engineering" are not rival ideas. At best they are informal names for two control-flow layers inside a factory: the loop that repeats one task until a gate passes, and the graph that sends work between stages and gates. Neither term has a traceable origin or a stable definition I could confirm, so design around the concepts (loops, graphs, gates, persisted state), not around the words.

**Read this first: the limits of this research.** This session had no web search or web fetch. One research subagent was used, and it also had no web access. So:
- Claims about outside sources (papers, vendor posts, books) come from the author's background knowledge up to about early 2026. They are tagged **[unverified this session]**. Check them against the original before you cite them.
- Nothing could be verified about **June–October 2026** product changes (Claude Code, Codex, Cursor, Copilot, Devin, Factory.ai, Amp, LangGraph). Section 7 says this openly instead of guessing.
- An earlier draft leaned on internal field evidence from a real agent pipeline. That evidence was removed from this public version; where it mattered, only the general lesson is kept and the text says so.

## TL;DR

- **A software factory is a delivery system, not a prompt or a loop.** It needs intake, spec, planning, implementation, verification, review, merge/release, observability and feedback. Each stage has a deterministic gate and persisted state. A factory is only as trustworthy as its gates. Loops and graphs are how control moves inside it.
- **"Loop engineering" and "graph engineering" are not stable terms.** I found no traceable origin for either, so treat them as informal labels. The stable neighbouring terms are context engineering, harness engineering, agent orchestration and spec-driven development. Build on those, plus the old lineage (Cusumano's Japanese factories, 1991; Greenfield & Short, 2004), which is about process discipline and reuse, not autonomy.
- **A minimal factory can be small.** The smallest worthwhile version is a ticket-claiming agent that works in a per-issue git worktree, stops and asks structured questions when requirements are missing, and posts a verification report. The next step is to harden the usual weak points: gates outside the repo (shared deploy infrastructure), a "Done before merge" status leak, and verification that only ran locally with nothing exercised as live containers. Don't add more agents. (The internal example behind this was removed.)

## 1. Definitions and lineage

| Term | Meaning today | Origin / lineage | Stability | Tag |
|---|---|---|---|---|
| **Software factory (historical, Japan)** | Organisation-level process discipline: standard tools, reuse libraries, metrics and quality control applied to large-scale software production | Michael Cusumano, *Japan's Software Factories: A Challenge to U.S. Management* (Oxford University Press, 1991), studying Hitachi, Toshiba, NEC and Fujitsu from the 1970s–80s | Stable, academic | Established [unverified this session] |
| **Software Factories (Microsoft)** | Model-driven development: domain-specific languages, product-line architectures, templates and guidance packages that make families of similar systems | Jack Greenfield & Keith Short, *Software Factories* (Wiley, 2004) | Stable but mostly historical; lives on in DSL/code-generation tooling | Established [unverified this session] |
| **Software factory (agentic, 2025–26)** | Agents take work from intake to shipped, verified change; humans steer through specs, gates and approvals. "Dark factory" is borrowed from lights-out manufacturing and means no human looks at the code | Used by practitioners and vendors through 2025–26. Factory.ai uses it as a brand. Blog posts describe agent-only "factories" and "levels" of autonomy ending in a "dark factory" | Contested. The meaning ranges from "CI with an agent in it" to "no human reads code" | Emerging / partly marketing |
| **Loop engineering** | Designing the inner loop: an agent repeats a task until a check passes (tests, lint, type-check, a critic) | No traceable origin found. Closest anchors: Geoffrey Huntley's "Ralph Wiggum" technique (a shell `while` loop that re-feeds the same prompt file to a coding agent, mid-2025) and the general "agentic loop" in vendor docs | **Not stable.** Use "verified loop" or "retry-until-gate" instead | Speculative / informal |
| **Graph engineering** | Designing explicit control flow: state machines and DAGs of agent steps and gates, as in LangGraph | No traceable origin found. Most likely a back-formation from graph-based orchestration frameworks (LangGraph, 2024) | **Not stable.** Use "workflow graph" or "orchestration graph" | Speculative / informal |
| **Context engineering** | Choosing what goes into the model's context window at each step (instructions, retrieved files, memory, tool results) | Popularised mid-2025. Anthropic published "Effective context engineering for AI agents" (about Sept 2025) | Fairly stable | Established-emerging [unverified this session] |
| **Harness engineering** | Designing the environment around the model: tools, sandboxes, hooks, docs-as-code, linters, feedback signals, so agents succeed by default | Used in 2025–26 practitioner and vendor writing. Anthropic: "Effective harnesses for long-running agents" (about Nov 2025). An OpenAI post on "harness engineering" is recalled from early 2026 but not verified | Emerging, converging | Emerging [unverified this session] |
| **Agent orchestration** | Coordinating several agents or subagents: who does what, in what order, with what shared state | Generic industry term | Stable as a generic term | Established |
| **Spec-driven development** | A written, versioned spec is the source of truth. Agents plan and implement against it, and verification checks against it | GitHub Spec Kit and Amazon Kiro (both 2025) made it a product pattern | Emerging, fairly stable | Emerging [unverified this session] |

**Bottom line on terminology.** The 1991 and 2004 meanings share one idea with today's: *industrialise the process so output quality comes from the system, not from heroic individuals.* What changed is the worker. Cusumano's factories standardised human work, and Greenfield & Short generated code from models. The agentic factory has probabilistic workers, so **verification gates do the job that process discipline did before.** If someone sells you "loop engineering" or "graph engineering" as a discipline, ask for the definition. You will get one of the rows above.

## 2. Precise comparison

| Dimension | Loop ("loop engineering") | Graph ("graph engineering") | Software factory |
|---|---|---|---|
| Problem it solves | One task gets done correctly despite a stochastic worker | Many steps run in the right order with the right gates and branching | Work flows from intake to production reliably, at volume, with accountability |
| Unit of design | One prompt plus one gate plus a stop condition | Nodes (agent or deterministic steps), edges (transitions), shared state | Stages, gates, state stores, human touchpoints, metrics, feedback |
| Typical artefact | `PROMPT.md` + test command + max-iterations | State machine / DAG definition, checkpoint store | Intake labels, spec templates, CI gates, merge policy, dashboards |
| Main failure | Runaway cost, silent satisficing (weakening the check to pass it) | Deadlock, brittle branching, state drift between nodes | High-volume slop, gate decay, accountability gaps |
| Who owns it | One developer | Platform or tooling owner | Engineering leadership plus platform |
| Relation | Lives inside a graph node | Wires loops and gates together | Contains graphs and adds people, policy, metrics |

Where the related terms sit, from inner to outer layer:
- **Context engineering**: what the model sees in one step.
- **Loop**: repeating a step until a gate passes.
- **Harness engineering**: the tools, sandbox, hooks and docs that make loops succeed.
- **Graph / orchestration**: routing between steps and agents.
- **Spec-driven development**: the input contract for the whole thing.
- **Software factory**: all of it, plus intake, release, observability and humans.

Typical skills map onto this stack: repo hardening is harness, the feature spec is spec-driven, the architecture review is a pre-implementation gate, and the conductor is orchestration plus a loop.

## 3. Reference anatomy of a factory

```
 ┌─────────┐   ┌──────┐   ┌──────────┐   ┌───────────┐   ┌──────────┐   ┌────────┐   ┌─────────────┐
 │ INTAKE  │──▶│ SPEC │──▶│ PLAN /   │──▶│ IMPLEMENT │──▶│ VERIFY / │──▶│ REVIEW │──▶│ MERGE /     │
 │ triage  │   │      │   │ DECOMPOSE│   │ (loop)    │   │ QA       │   │        │   │ RELEASE     │
 └────▲────┘   └──┬───┘   └────┬─────┘   └─────┬─────┘   └────┬─────┘   └───┬────┘   └──────┬──────┘
      │        [gate]       [gate]          [gate]╲          [gate]       [gate]           [gate]
      │           │            │                ╲─retry─╯       │            │                │
      │           ▼            ▼                                 ▼            ▼                ▼
      │      BLOCKED → ask human (structured questions) → back to agent-ready                  │
      │                                                                                      ▼
      └──────────── FEEDBACK ◀── OBSERVABILITY (prod signals, escaped defects, cost) ◀────────┘
 Persisted state everywhere: ticket + labels, spec file, plan file, worktree/branch, PR, CI results, run log
```

| Stage | Agent role | Deterministic gate | Persisted state | Human touchpoint (and why) |
|---|---|---|---|---|
| Intake & triage | Classify, dedupe, check readiness, pick the repo | Issue has an `agent-ready` label, a `repo-*` label, acceptance criteria | Ticket, labels | A human labels work `agent-ready`. Choosing what is worth doing is a product call |
| Specification | Turn a vague idea into a spec with testable acceptance criteria and open questions | Spec template complete; every acceptance criterion testable; open questions empty or escalated | Spec file in repo or ticket | Owner approves the spec. The agent must not invent requirements |
| Planning & decomposition | Split into tasks, find files and dependencies, flag risk | Plan names files and tests per task; architecture rules check passes | Plan file, task list | Review needed for cross-service or schema changes, where errors are expensive |
| Implementation | Write code and tests in an isolated worktree | Build, type-check, lint, unit tests pass; diff stays inside allowed paths | Branch / worktree, commits | None, unless it hits the iteration or cost cap |
| Verification & QA | Run integration and e2e tests, deploy a preview, check every acceptance criterion against evidence | Tests green in a *real* environment; each criterion mapped to evidence; protected checks (test files, CI config) unchanged | CI results, preview URL, verification report | Human checks UX and visual quality in the preview. Agents still judge design poorly |
| Review | An independent reviewer agent (different context, ideally a different model) plus static analysis | No high-severity findings; required approvals | PR, review comments | A human owns the merge decision, because accountability can't be delegated |
| Merge & release | Rebase, resolve trivial conflicts, write release notes, bump versions | Merge queue green; status may move to Done only *after* merge | Main branch, tags, changelog | Release approval for production, matching the blast radius |
| Observability | Watch errors, performance, cost per change | Alert thresholds | Metrics, logs, run logs | On-call stays human |
| Feedback | Turn escaped defects and review findings into new tickets and new gate rules | A new rule or test exists for each escaped defect class | Backlog, CLAUDE.md / skills updates | A human chooses which lessons become policy |

A ticket-to-PR agent run shows this anatomy in miniature. In a hypothetical run, the agent claims a labelled issue, stops within minutes with a short list of numbered questions and no code changes (refusing to invent requirements), the issue owner answers later, and the agent re-claims the issue and opens a PR with a verification report. That is an intake → blocked-gate → implement → verify cycle, where most of the elapsed time is human wait. (The internal run that originally supported this was removed.)

## 4. What it takes to build one

**Codebase prerequisites**
- Fast, deterministic build and test commands that an agent can run without tribal knowledge. A shared skill library is worth building when operational details (env keys, table names, container exec incantations) otherwise live only in one person's head.
- Executable architecture rules: lint rules, import boundaries, scripts that fail the build. A good example is a small script that fails the build on hardcoded currency text.
- Agent docs that stay short. Keep a hard line ceiling (for example, about 150 lines) on each skill file and move bulk material into a `references/` folder, with a validation script that fails when the ceiling is exceeded.
- Ephemeral preview environments per change. Where they exist, they are the biggest asset.
**Verification infrastructure**
- Ephemeral preview environments per change. Preview stacks per change are one of the biggest assets a factory can have.
- Checks that agents can't edit, run on CI and not only on the agent's machine.
- Drift checks for generated artefacts. A docs-drift check can be dropped during a CI migration with nothing to preserve it, after which generated docs are silently missed.

**Team prerequisites**
- Someone answers blocked questions within hours. The factory's throughput is capped by human response time.
- A named owner for shared infrastructure. A preview deploy can fail on a shared credential or artifact-registry step owned by a platform team, not by the agent.
- Agreement that "Done" means merged and verified in a real environment.

**Maturity levels.** This is my synthesis. Public "levels" frameworks exist, but none could be verified this session.

| Level | Description | Trust signal needed to advance |
|---|---|---|
| L0 Assist | Human drives, agent suggests | — |
| L1 Verified loop | Agent completes one task until local gates pass; human reviews everything | More than 80% of loop outputs pass CI unchanged over 20+ tasks (internal target, not an industry figure) |
| L2 Ticket-to-PR | Agent claims labelled tickets, works in a worktree, asks when blocked, opens a PR with a verification report | Low rework rate on PRs; blocked-question quality is good |
| L3 Ticket-to-preview | L2 plus automated preview deploy and checks against acceptance criteria in a real environment | Preview checks catch what humans would have caught |
| L4 Supervised factory | Several stages chained; humans approve specs, merges and releases only | Escaped-defect rate no worse than the human baseline |
| L5 Dark factory | No human reads code | No credible, independently verified public evidence for general product code [unverified] |

**Smallest version worth building:** L2 → L3 on one repo with good preview environments.

## 5. Control flow: loops vs graphs vs conductor

| Pattern | Fits when | Failure modes | Defence |
|---|---|---|---|
| Retry-until-gate loop | One task with a cheap, trustworthy check | Runaway cost; satisficing (deleting or weakening tests, `skip`, broad `any` types) | Iteration and cost caps; protected test and CI files; a diff-scope gate |
| Critique-and-revise | Quality is judged, not binary (specs, reviews, UI copy) | Sycophantic convergence; critic and author share blind spots | Different context or model for the critic; a rubric with required evidence |
| Ralph-style re-runs (fresh context, same prompt, state on disk) | Long backlogs; context rot in long sessions | Drift from the plan; repeated work; it never stops | A plan/progress file as the source of truth; an explicit "done" check; a hard stop |
| Explicit graph (state machine / DAG) | Stages and gates are known and must be auditable | Brittleness; deadlock on unexpected states; graph-vs-reality drift | A "blocked → human" edge from every node; checkpointed state; timeouts |
| Conductor + subagents | Variable, exploratory work; parallelisable subtasks | Merge conflicts between parallel agents; the conductor's context fills up; silent subagent failure | One worktree per subagent; disjoint file ownership; subagents return structured results; the conductor verifies and doesn't trust |

**My recommendation:** use a *graph at the outside and loops at the inside.* Make stage transitions explicit and deterministic: labels, statuses, CI. Let agents loop only inside a stage, against that stage's gate. A conductor skill is fine as an implementation-stage engine, but it should not decide stage transitions on its own judgement. A label protocol (`agent-ready` → claimed → blocked / `agent-complete`) is already a small state machine, and that is the right shape.

## 6. Evidence: what has been published, and how solid it is

| Claim | Source (as recalled) | Date | Status |
|---|---|---|---|
| Experienced open-source developers were slower with AI tools (about 19%) while believing they were faster | METR randomised controlled trial | July 2025 | Established study, small sample, pre-agentic tools [unverified this session] |
| Large internal agent-generated codebases with "no human-written code" | OpenAI harness-engineering writing | About early 2026 | Vendor self-report [unverified this session] |
| Over 1,000 merged agent PRs per week at Stripe ("Minions") | Stripe engineering, as recalled | About early 2026 | Company self-report [unverified this session] |
| Merge rates of agent-authored PRs differ by tool | Academic datasets of agentic PRs (e.g. an "AIDev" dataset paper, 2025) | 2025 | Emerging research; merge rate ≠ correctness [unverified this session] |
| AI adoption tied to throughput gains and stability risks | DORA 2025 AI-assisted development report | 2025 | Survey-based [unverified this session] |

**What is missing everywhere:** I know of no independently audited figures for **cost per change**, **escaped-defect rate of agent changes compared with a human baseline**, or **share of agent PRs merged with zero human edits.** Treat any vendor number on these as marketing until it comes with a method. Merge counts measure volume, not value.

**Internal field evidence (removed):** the original draft cited dated runs from an internal agent pipeline. Those details were removed from this public version. The general lessons they supported:
- **Honest verification limits are a feature.** An agent run that states what it could not verify (for example, that nothing ran as live containers, or a config check could not run because no container daemon was available) is more trustworthy than one that reports a blanket pass.
- **Shared-infrastructure failures hide behind redaction.** A preview deploy can fail on a shared step whose output is hidden (for example by log suppression), so the agent cannot diagnose it. Also, a warning to "merge the PR before moving this to Done" is easily ignored when status automation is not tied to merge events.
- **Live endpoint checks are the L3 behaviour to aim for.** Re-verifying a fix against live health endpoints after deploy beats a local pass. Any pipeline sample of one or two completed issues supports no throughput conclusions.

## 7. What changed since June 2026

**I could not research this.** No web access was available. I won't list product features for June–October 2026 that I can't source. Check these yourself, newest first:
- The Claude Code changelog and docs (hooks, subagents, skills, background and scheduled agents, worktree support).
- OpenAI Codex release notes, the Cursor changelog (background agents), and GitHub changelog entries for the Copilot coding agent.
- Devin, Factory.ai, Amp and LangGraph release notes.

What I can report from field practice in that window (internal examples removed):
- **Cross-agent skills became a team practice.** Teams increasingly require skills that work with more than one coding agent, with a vendor-specific metadata file placed next to `SKILL.md` in a shared skills repo.
- **Ticket-claiming agents and posting bots are in production use** in some teams, Sept–Oct 2026 (internal example removed).
- **New failure mode seen: silent stale defaults.** A floating `latest` deploy tag can be frozen for months, so any consumer that omits the variable silently runs an old pipeline. Agents that pick up defaults will spread this kind of problem quickly.

## 8. Failure modes and anti-patterns

| Failure mode | Detect | Defend |
|---|---|---|
| High-volume slop | Rising review rework and revert rate; PR size growing | Cap PR size; require a verification report mapped to acceptance criteria |
| Silent satisficing | Diffs that touch test files or CI config; new `skip` or `xfail` | Protect those paths with a hook or CODEOWNERS; a diff-scope gate |
| Local-only verification | Report says "locally" or "no daemon" | Require preview or CI evidence before `agent-complete` |
| Status leak (Done before merge) | Ticket closed while PR open | Automation: Done only after a merge webhook |
| Gate decay | A check disappears during a CI migration | Treat gates as code with tests; review gate inventory every quarter |
| Stale floating defaults | Digest comparison | Pin exact versions; agents must never rely on `latest` |
| Runaway cost / loops | Iterations or tokens per task over budget | Hard caps; alert; escalate as "blocked" |
| Invented requirements | Spec or code covering things not in the acceptance criteria | Blocked-question protocol |
| Parallel merge conflicts | Conflicting PRs from sibling agents | Disjoint file ownership; a merge queue; serialise shared files |
| Out-of-repo blockers | Failure in infra the agent doesn't own | Fast escalation path to a named owner |

## 9. Mapping onto Claude Code and other harnesses

| Factory need | Claude Code primitive | Closest equivalents elsewhere (verify current names) |
|---|---|---|
| Repo conventions, agent docs | `CLAUDE.md` | `AGENTS.md` (Codex, Amp and others), Cursor rules, Copilot custom instructions |
| Reusable procedures | Skills (`SKILL.md`) | Codex skills / `agents/openai.yaml`, Cursor rules / commands |
| Independent reviewer, parallel workers | Subagents | Codex / Cursor background agents, Factory Droids, Devin sessions |
| Deterministic gates inside the loop | Hooks (pre/post tool use, stop) | CI checks; Cursor and Codex hook equivalents where present |
| Isolation per task | Git worktrees | Cloud sandboxes (Codex cloud, Copilot coding agent, Devin VMs) |
| Unattended runs | Headless / background / scheduled runs; GitHub Actions integration | Copilot coding agent (issue → PR), Codex cloud tasks, Devin |
| Multi-stage routing | Your conductor skill, or an external graph (labels + CI, or LangGraph) | LangGraph, Factory.ai, vendor "agent HQ"-style dashboards |

Keep it tool-agnostic: put the state machine in ticket labels and CI, not inside any one harness. A label protocol already works that way.

## 10. Build path

1. **Verified loop** (prerequisite: one-command test and lint). A skill that runs implement → test → fix with caps and protected test files.
2. **Ticket-to-PR** (prerequisite: acceptance-criteria template, `agent-ready` and `repo-*` labels). Worktree per issue, blocked-question gate, verification report.
3. **Ticket-to-preview** (prerequisite: reliable preview pipeline with a named owner). The agent deploys a preview and checks each acceptance criterion against live endpoints.
4. **Independent review stage** (prerequisite: a review rubric). Reviewer subagent with fresh context; human merges.
5. **Spec and plan stages upstream** (prerequisite: your spec and architecture-review skills turned into gates with pass/fail output).
6. **Feedback loop** (prerequisite: escaped-defect tracking). Each escaped defect becomes a new check or skill rule.

## 11. Recommendations

- **Don't adopt "loop engineering" or "graph engineering" as vocabulary.** Use stage, gate, loop, state.
- **Next 2 weeks:** add a "Done only after merge + preview evidence" rule. Protect test and CI paths with hooks. Add an iteration and cost cap to your conductor.
- **Next quarter:** make your spec and architecture-review skills emit machine-checkable pass/fail. Measure rework rate, time-to-unblock and revert rate on agent PRs. Collect 20+ `agent-complete` issues before you claim anything.
- **Front-end specific:** add visual-regression and accessibility checks to the preview gate. Keep human design review, because that is where agents are weakest.

## 12. Open problems

- Trustworthy, cheap verification of *intent*: tests prove behaviour, not that the right thing was built.
- Cost per change and escaped-defect baselines that are audited, not self-reported.
- Gate governance: who maintains the gates as the factory grows, and how gate decay gets caught.
- Parallel agents on shared files without merge chaos.
- Accountability for unattended merges.
- Design and UX quality judgement by agents.
