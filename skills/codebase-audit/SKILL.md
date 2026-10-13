---
name: codebase-audit
description: Use when auditing a whole existing codebase as built — especially one mostly written by coding agents — for architecture erosion, weakened or bypassed gates, unsound contracts, bloat, and — when the codebase profile calls for them — security and performance risks. Triggers - "audit this codebase", "audit the architecture", "security audit of the repo", "will this scale to N users", "performance audit", "has this repo drifted", "are the gates still respected", "check the contracts", "is this over-engineered", taking over a vibe-coded or agent-built repo, reviewing what a long unattended agent run produced, a periodic or triggered re-audit against a stored baseline. Not for a single diff or PR, and not for a design before it is built. Experimental.
allowed-tools: Read, Glob, Grep, Bash, Agent, Write
---

# Codebase Audit

A read-only audit of a whole codebase as it stands, across four structural
dimensions — **architecture**, **gate respect**, **contract design**, **verbosity** —
plus **security** and **performance** when the codebase profile calls for them. It
produces anchored, severity-tagged findings, a task list sized one change per task,
and a baseline the next audit measures drift against.

Status: experimental. The method is settled; thresholds, slice budgets and agent
counts are starting defaults to be tuned from field runs.

## Core principle

**An auditor never invents structure.** Every claim traces to an extractor's output or
to quoted code, and a model only judges what the tools surfaced. Local plausibility is
the failure mode of agent-written code: each change looks reasonable, every gate is
green, and the system still drifts — a second HTTP client, a catch that turns a failed
write into an empty list, a lint rule quietly downgraded to a warning. None of that is
visible to a reader skimming files, and all of it is visible to a graph, a manifest
diff, or an inventory. So the audit counts first, reads second, and judges last.

**No single agent can do this.** The candidates for even one dimension of a real repo
overflow a context, and an agent that reads code anchors on its first impressions. The
session that runs this skill **orchestrates only**: it dispatches fresh agents in
waves, they hand off through files on disk, and the orchestrator never reads the code
itself.

## When to use

- A repository written largely by agents needs a health check: is the architecture
  still the one it claims, are its checks still enforced, are its interfaces honest,
  has it bloated?
- You are taking over a codebase someone (or something) else built.
- A long unattended run produced more commits than anyone read.
- A trigger fired since the last audit (see Triggers), or the backstop interval passed.

## When NOT to use

- A single change before merge — that is diff review against its plan, a different
  job with a different packet.
- A design or plan before any code exists — that is a design review.
- Penetration testing, production load-testing programs, licence compliance, or
  AI-provenance forensics. Out of scope.
- A repo small enough to read in one sitting with nothing at stake. Read it.

## Arguments

```
codebase-audit [drift|inherited|run <base>..<head>] [<dimension> ...] [--depth quick|standard|deep]
```

- **Mode** defaults to `drift` when a baseline exists, else `inherited`.
- **Dimensions** default to the profile's audit plan: the four structural dimensions
  (`architecture gates contracts verbosity`) unless the profile rules one out;
  `security` whenever the profile lists any stakes; `performance` only when it states
  load, platform or budget constraints. Naming dimensions on the command line
  overrides the plan.
- **Depth** defaults to `standard`.

| Depth | Judges | Verification | Use for |
|---|---|---|---|
| `quick` (no measurement) | one per dimension, hotspots only | only High-or-above findings touching persisted data, money, auth or a trust boundary; the rest marked `unverified` | first look at an inherited repo |
| `standard` | one per dimension × slice; measurement wave for flagged performance candidates | every Critical and High finding | the default |
| `deep` | dimension × slice, plus a random control sample | every finding, plus a second judge on the top hotspots | before a major migration or after an incident |

## Hard rules

- **Read-only.** The audit produces findings and a task list. It never fixes, never
  refactors, and never re-runs a gate to re-green it. Remediation goes through the
  normal build pipeline as ordinary changes.
- **Deterministic before model.** Anything a tool or a script can compute — graphs,
  cycles, complexity, churn, clones, dead code, suppressions, config diffs, scanner
  results, bundle size, measured timings — is computed by a tool or a script and
  never estimated by a model. Prefer an established tool for the stack; write a
  script only where none exists. A model's job starts where the output needs judgment,
  and it reads the tool's output rather than redoing it. A count a model produced by
  reading files is not a fact.
- **Tools run safely or not at all.** Pinned exact versions; nothing installed into
  the audited repo, its lockfile or its dependency directory; runs read-only against
  the tree or inside an isolated worktree; no uploading code or results to a remote
  service unless the user has approved that service; no tool that executes the
  project's code (tests, builds, load or profiling runs) except in isolation and
  never under concurrent load. A tool that cannot meet these is skipped and the gap
  listed under `NOT_COVERED`.
- **Keep the whole run, not just the merge.** Every brief sent, every reply received,
  every candidate, every dismissal, every refuted finding and every script run stays
  on disk, indexed for a human reviewer (`references/run-record.md`). The merge never
  edits an agent's output, and an audit whose record has gaps is not finished.
- **Scans are kept, not thrown away.** Every script and exact tool command an agent
  used is saved under the run's `work/scripts/`, with versions, so the next audit
  reruns the identical scan. A scan that cannot be rerun cannot measure drift.
- **Every finding carries an anchor** — `path:line`, a re-runnable scan output, or a
  quoted config key. No agent asserts a dependency edge from reading; edges come from
  the extracted graph only. Unanchored advice is dropped before counting.
- **Contract findings carry a caller-visible counterexample**: "the signature permits
  X, yet Y happens." No counterexample, no finding.
- **Unmeasured performance claims are capped at Medium.** A performance finding is
  `measured`, `computed` (arithmetic from the profile's own numbers proves the
  breach), or `candidate (unmeasured)` — and a candidate names the measurement that
  would settle it. No model ever states a latency, a count or a hit rate it did not
  get from a tool.
- **One owner per finding.** When two dimensions flag the same code, the rubric whose
  row names the *consequence* owns the finding and the other links to it — a spread
  of fetch mechanisms is architecture, two hundred parallel calls on a phone is
  performance; a missing bound before parsing is security, an unrefined type after it
  is contracts.
- **Violations are judged only against a declared rule or a measured cost.** When two
  conventions coexist and nothing declares which wins, that is an **authority
  conflict**, escalated as a decision — never resolved by the auditor, and never by
  prevalence. What is neither declared nor costly is taste, and taste is dropped.
- **Severity and confidence are separate fields.** Severity is impact × exposure.
  A low-confidence finding never ranks Critical until verified. Agent authorship never
  raises severity.
- **No absolute thresholds.** Zero tolerance for rules the repo itself declares;
  everything else ranks against the repo's own percentiles and its last baseline.
- **Cap findings and merge them by root cause.** Ten instances of one habit are one
  finding with ten anchors. A finding that recurs across audits becomes a proposed
  lint rule or structural test.
- **A judge never confirms its own finding.** Serious findings go to a fresh verifier
  that tries to refute them.
- **The rubric and the fixed test-strength sample sit outside the agent-editable
  path**, or a change to either is itself reported in the next audit.
- **Gate integrity.** Never weaken, narrow, mock out, skip, or defer a gate to get
  green. Gates are development discipline, not production-only. A gamed gate is a
  failed task.
- **Evidence rules.** A consistency claim requires a full search, not spot checks. A
  negative claim ("nothing uses X") requires a recursive search including ignored and
  hidden directories. Deleting as dead requires proving zero consumers through
  indirection. A claim about current behavior requires measurement, not inference
  from source. A regression claim requires reproducing at the pre-change baseline
  first.
- **Model tier rule.** The session holds decisions. Judgment-heavy delegated work
  runs one tier below the session; mechanical work two tiers below, with a floor at
  the mid tier; never delegate upward. The bottom tier never builds against slow or
  flaky suites and never writes a root-cause diagnosis. **This skill's judging is the
  judgment-heavy exception: the judgment tier runs at the session's model, never
  above it** (`references/model-tiers.md`).
- **Concurrency hygiene.** Never run the full gate under concurrent subagent load.
  Never share temp or browser-profile directories across sessions. Never kill
  processes by image name. Verify a worktree's base commit before building on it.
  Never install dependencies in a directory you have not verified is the intended one.
- **Script over manual.** A mechanical routine that will repeat — the same shape of
  tool call more than a handful of times, the same setup/teardown twice — becomes a
  script that takes arguments. Durable scripts go in the project's scripts directory;
  one-offs to the OS temp dir. Doing it all by hand is the default, and it costs
  tokens and wall-clock.
- **Settled decisions travel forward and are never re-litigated here.** A locked
  decision found genuinely broken is re-locked with the user (or, unattended, recorded
  as a `Decisions Needed` item); it is never silently adapted around.
- **Over-production is a defect.** A small repo does not get twenty agents because the
  machinery exists. Pick the depth for the stakes.

## The agent layout

```
Orchestrator (session tier) — scope, dispatch, merge, report. Never reads code.
├─ Wave 1 · Extraction   mechanical tier, parallel; bulk tier for classification → work/facts/*
├─ Wave 2 · Context      judgment (ledger), mechanical (tests) → work/intent.md, work/tests.md
├─ Wave 3 · Judges       judgment tier, one per dimension × slice → work/findings/*
├─ Wave 4 · Measurement  mechanical tier, alone, isolated; standard/deep only → work/measurements/*
├─ Wave 5 · Verifiers    judgment tier; session tier for Critical → work/verdicts/*
└─ Merge                 orchestrator → report.md, tasks, baseline.json
```

| Tier | Does | Never does |
|---|---|---|
| **session** | scope, slicing, merge, final severity; verifies Critical findings | read code to "get oriented" |
| **judgment** | intent ledger, judges, verifiers — at the session's model | — |
| **mechanical** | extractors, test strength, measurement, baseline assembly | judge a candidate |
| **bulk** | high-volume classification: comment what-vs-why, commit author class, candidate pre-filtering | run suites, build, judge, or write a diagnosis |

The tiers are roles, not models. `references/model-tiers.md` maps them to concrete
models per harness and says what to do when the harness cannot dispatch subagents.

**Who reads the profile.** Step 0 writes a codebase profile; each agent gets only the
part its job needs, because context it does not need biases what it finds.

| Agent | Receives from the profile | Why |
|---|---|---|
| Extractors | scope only | they count; knowing the product biases what they look for |
| Intent ledger | identity | to know which documents describe the product |
| Test strength | stakes | to pick the risk sample — auth, money, persisted data first |
| Judges | the whole profile | criteria and severity depend on load, platform and stakes |
| Measurement | representative flows, load and constraints | to drive realistic flows at the profile's targets |
| Verifiers | nothing | they test whether a claim is true; context pulls them toward confirming |
| Merge | the whole profile | final severity and ordering |

**Hand-offs go through files, never context.** Before each dispatch, save the exact
brief under `work/briefs/` and log it; after, save the reply under `work/summaries/` and
log the outcome — failed and empty agents included (`record.py log`). Each agent writes
its output under the run's `work/` directory and returns a short summary; the orchestrator reads summaries
and the specific files it needs to merge. This keeps the orchestrator light, makes an
interrupted audit resumable, and keeps one agent's reasoning out of the next one's
context. **Concurrency cap: about four agents at once.** Test-strength work runs alone.
This fan-out is expected for this skill; it is the reason the skill exists.

A medium repo at `standard` depth is roughly twenty agents: four extractors, two
context agents, eight to twelve judges, a handful of verifiers.

## Bundled scripts

`scripts/` holds stack-neutral, standard-library tools for everything that repeats
across audits: history, pattern counts, the gate manifest, fingerprints, isolation,
performance arithmetic and baselines. **They come before any hand-written scan.** This
session runs only `fingerprint.py` (step 0), `record.py` (every dispatch, and the index
at the end) and `baseline.py` (step 7); every other
script is run by the agent whose step names it. Give each such agent
`references/scripts.md` with this skill's absolute path filled in — it holds the
contract, the catalogue, the commands and how to diagnose a run.

## Steps

### 0. Profile the codebase and freeze the scope

An audit judges code against what the system has to be. A list rendered without
virtualization is fine in a desktop tool and a defect on a phone; a query per request
is fine at two thousand users and an incident at a hundred thousand. So the first
artifact is `docs/audits/<date>-<mode>/profile.md`, per `references/profile.md`:

- **Identity** — what the system is, who uses it, platforms, how it is deployed.
- **Load and constraints** — concurrent users, request rates, data volume, device
  class, network, latency and memory budgets.
- **Stakes** — sensitive data, money, auth, safety, public surface, persisted data.
- **Dominant quality attributes** — the two or three that rank everything else.
- **Audit plan** — which dimensions run, why, and at what depth.
- **Scope** — commit SHA (a range for `run`), include and exclude globs (generated,
  vendored and fixture code out), tool versions, and a **scope fingerprint** hashing
  all of it.

Fill identity and stakes from the README, decision records and product docs. **Load
and constraints are asked for, never guessed** — docs rarely state them and a guess
silently miscalibrates every severity. Interactively, ask the user for whatever the
docs do not settle and have them confirm the dominant attributes. Unattended, write
`unknown`, judge as if the stakes were high, and list every unknown under
`NOT_COVERED`. Say the mode, dimensions, depth and dominant attributes out loud in one
line. Compute the scope fingerprint and the profile hash with `fingerprint.py`.

In `drift` mode, start from the baseline's profile: re-confirm it, and compare the
scope fingerprint before any number. A different scope produces phantom drift — either
restore the old scope or declare a new comparison point. A changed profile (two
thousand users became a hundred thousand) is also a new comparison point.

### 1. Wave 1 — extraction

Dispatch the extractors in one message, each with `references/scans.md` and the
profile's scope section only. They count; they do not judge.

| Extractor | Produces |
|---|---|
| **Graph** | typed import graph (static, build, runtime registration, test-only kept separate), cycles as strongly connected components, fan-in/out percentiles, violations of declared boundary rules |
| **History** | hotspots (churn × complexity over a year, rename-aware), cross-module co-change pairs, with bot, formatter and agent commits split from human ones; for `run`, only the run's range |
| **Gates** | the canonical gate manifest (see `references/rubric-gates.md`) diffed against the baseline; suppression, skip and escape-hatch counts by mechanism, directory and age; local-versus-CI command comparison |
| **Security** (when planned) | scanner manifest and pinned local reruns, entry-point graph, authorization matrix, client-trusted identity flows, limits, permissive flags with their history, supply-chain checks, agent configuration, secrets in tree and history |
| **Performance** (when planned) | fan-out per flow, calls in loops, unbounded reads, blocking calls on critical threads, timers and broadcast with **computed** amplification, cache inventory, lifecycle pairing, resilience config, instrumentation inventory, bundle stats from an existing artifact |
| **Inventories** | abstractions per concern class, ingestion points, public exports, catch-and-default sites, optional-then-guarded parameters, single-implementation interfaces, pass-through wrappers, dead exports and files, clone families |

Mechanical tier. Each gets `references/scripts.md` and starts from the bundled script
for its job — `history.py`, `patterns.py`, `manifest.py`, `amplify.py` — then adds
stack tools.
Each writes `work/facts/<extractor>.*` and a ten-line summary.
High-volume classification inside an extractor — tagging commits by author class,
sorting a comment sample into what versus why — is fanned out to the bulk tier in
batches; the extractor checks a handful of the bulk tier's labels before using them.

### 2. Wave 2 — context

Two agents — the intent ledger at the judgment tier, test strength at the mechanical
tier — run one after the other or with test strength alone:

- **Intent ledger.** Reads enforced rules and structural tests, decision records,
  agent instruction files, and prose docs, and turns them into claims, each with
  scope, status, date and how it is enforced. Authority runs: enforced rules >
  accepted decision records > instruction files > prose. Conflicts between sources are
  listed, not resolved. Then it maps files to the components the claims name and
  writes the **three-architectures table** — observed (graph) versus claimed (ledger)
  versus enforced (rules) — as agrees / diverges / missing, with anchors. A stale
  agent instruction file is a finding: agents read it first and trust it most.
- **Test strength.** On a fixed, risk-selected sample — the profile's stakes first,
  then top hotspots, core domain, trust boundaries, code under newly relaxed gates — it
  counts eligible code with no tests, then finds **pseudo-tested methods**: empty the
  body or return a default and check whether the tests still pass. Full mutation
  testing only where the stack already has a tool. It records the sample's file list
  so the next audit re-reads the same files. It runs alone: parallel test runs
  fabricate results. **Mutation happens in an isolated worktree at the pinned commit
  (`isolate.py create` / `remove`),
  never in the checkout being audited**: verify the worktree's base commit, link the
  existing dependency directory rather than installing, restore every mutated file,
  and remove the worktree at the end — unlinking the dependency directory first, so
  the removal cannot delete the original through the link.

The orchestrator then **slices the repo**: modules or layers from the graph, sized so
one judge can read every candidate in its slice plus a reading sample. Starting budget:
about forty candidates and twenty-five files read per judge. Large repos get more
slices, never bigger judges.

### 3. Wave 3 — judges

One fresh agent per dimension × slice, judgment tier, dispatched in batches of about
four. Each receives exactly: `references/judge-brief.md` with its slots filled, its
dimension's rubric file, the profile, the facts for its slice, the intent ledger, and
read-only tree access. Never the other judges' output, never this session's
impressions. A rubric row that names a condition ("applies when the profile names a
mobile client") is skipped, not reported, when the profile rules it out.

Each judge triages its candidates (confirm, dismiss with reason, or flag an authority
conflict), reads its reading sample — new violations, slice hotspots, parallel-
abstraction clusters, and at `deep` a random control sample — and writes findings in
the schema from the brief. "No finding" and "this is over-engineering" are valid
outputs.

### 4. Wave 4 — measurement

At `standard` and `deep`, for performance candidates a judge marked as needing
measurement — bounded by the profile's representative flows. One mechanical-tier agent,
**alone**, following the measurement protocol in `references/scans.md` (`isolate.py`
for the worktree): an isolated
worktree or container at the pinned commit, dependencies from the lockfile with install
scripts disabled inside the copy only, outbound network blocked, nothing else running.
Approved production telemetry outranks any lab number. A measured number moves the
candidate to `measured` with its value; a measurement that could not run leaves it
`candidate (unmeasured)` and goes under `NOT_COVERED`. `quick` depth never measures.

### 5. Wave 5 — verifiers

For every Critical and High finding (every finding at `deep`; at `quick`, only High or
above touching persisted data, money, auth or a trust boundary), dispatch a fresh
verifier — judgment tier, session tier for a Critical — with
`references/verifier-brief.md`: the finding's claim and anchors, the
rubric row, read-only tree access — not the judge's reasoning. The verifier re-derives
the anchor and hunts for counter-evidence: a guard elsewhere, a declared and tested
fallback, a decision record that settles it, a test that already pins the behavior. It
returns `CONFIRMED`, `DOWNGRADE` with the evidence, or `REFUTED`. Refuted findings are
dropped and counted.

### 6. Merge and calibrate

The orchestrator merges `work/findings/`, `work/measurements/` and `work/verdicts/`:
apply measured values to their candidates, apply the one-owner rule, drop unanchored and
refuted findings, merge by root cause, apply the severity table, cap the list. Record
every raw finding's disposition — merged, kept, downgraded, refuted, dropped with its
reason, duplicate — in `work/merge.md`; nothing leaves the report without a line there. Then a
human confirms Critical and High findings and a small random sample of the rest; the
**confirmed share** is the audit's measured precision and goes into the baseline.

Unattended, Critical and High findings are marked `unconfirmed` and queued for a
human — never confirmed by the model alone.

### 7. Write the outputs

- `docs/audits/<date>-<mode>/report.md` — findings by severity; the three-architectures
  table; authority conflicts as decisions needed; what was not covered and why.
- A task list in the report, each task sized as one change, each recurring finding
  paired with the lint rule or structural test that would stop it mechanically.
- `docs/audits/baseline.json` — per `references/baseline.md`, checked with
  `baseline.py validate` and, in drift mode, diffed with `baseline.py compare`; assembled by one
  mechanical-tier agent from `work/facts/`, `work/tests.md` and the profile, then
  parsed back to prove it is valid. The orchestrator does not hand-assemble it; it
  reviews the agent's list of fields it could not fill. Overwritten each audit;
  history lives in version control.
- `review.md` — the human review index, generated by `record.py index`: what is worth
  a human look below the line (refuted and downgraded findings, dismissed candidates
  on hotspots and stakes paths, low-confidence findings, authority conflicts,
  unmeasured candidates, not-assessed items, unreviewed candidates, script warnings),
  the merge trace, every agent, every file. Then `record.py check --fail-on-gaps`
  must pass before the handoff block is written.
- `work/` stays beside the report so the audit can be resumed or re-checked; the
  project decides whether to commit it.

End with this block:

```
AUDIT: drift|inherited|run <base>..<head>   depth=<quick|standard|deep>
FINDINGS: critical=<n> high=<n> medium=<n> low=<n>   unconfirmed=<n>   unmeasured=<n>
TREND: architecture=<better|same|worse|new> gates=… contracts=… verbosity=… security=<…|off> performance=<…|off>
TRIGGERS: <ratchets breached since baseline, or none>
NOT_COVERED: <dimensions, slices or checks skipped, and why>
```

## The modes

| Mode | Scope | What changes |
|---|---|---|
| **drift** | whole repo against the baseline | Profile re-confirmed first; every number diffed; same fixed sample re-read; the gate-manifest diff is the headline; expired accepted exceptions return as findings |
| **inherited** | whole repo, no baseline | The profile is built from scratch and the user is asked for load and stakes; intent is usually unrecorded — that absence is a finding, never a licence to infer a philosophy; claimed verification (README, scripts) re-run with exit codes kept; authority conflicts dominate; this run writes the first baseline |
| **run** | the run's commit range, rest of repo as context | First: test edits inside implementation commits, gate-config changes, instruction-file changes during the run; intent comes from the backlog and plans, never the run's own narration; compare with the pre-run baseline if one exists |

## Severity

| Level | Means | Examples |
|---|---|---|
| **Critical** | A containment mechanism verifiably failed | a required gate no longer runs; silent success around a write; an incompatible schema change with live consumers |
| **High** | A verified invariant breach with broad reach and change pressure | unparsed external input on a live path; a vendor error leaking through a public API; a layer violation in a top hotspot |
| **Medium** | Real drift whose cost today is maintenance risk | a parallel abstraction; inconsistent error handling between siblings; accidental surface inside a monorepo |
| **Low** | Local bloat; behavior is unambiguous | a pass-through wrapper; a boolean flag in private code; comment noise |

Severity is categorical and derived from the profile — exposure × precondition ×
asset × blast radius — with confidence a separate field. Industry vulnerability scores
apply only to scanner-reported CVEs, adjusted for this environment; they are not used
for rubric findings.

Raise one step for a top hotspot, persisted data, independently deployed consumers, a
public surface, or a direct hit on one of the profile's dominant quality attributes.
Lower one step for a declared, tested, observable fallback, private single-consumer
code, a lockstep deploy, or a concern the profile rules out. Never High without a
failure path or a measured cost. When the profile's load or stakes are `unknown`,
do not lower for them.

## Triggers

Run a drift audit when: a new violation of a declared rule lands; a gate is relaxed or
CI or tooling migrates; a major migration (framework, state mechanism, repo layout)
completes; an incident points at structure or test containment; a ratchet breaches (a
new cycle between top-level modules, suppressions rising, test strength falling on
core code, a new parallel abstraction); the profile changes (new platform, an order
of magnitude more load, new stakes such as payments); or the agent workflow changes
materially — start a new comparison point rather than blending regimes. Backstop: quarterly. No
interval has evidence behind it; the backstop is a management choice.

## Common mistakes

- **The orchestrator reads code "to get oriented."** It anchors every later judgment
  and burns the context the merge needs. Orient from the facts files.
- **One judge per dimension on a large repo.** It skims, samples badly, and reports
  the first patterns it saw. Slice.
- **Letting a judge verify its own findings**, or handing a verifier the judge's
  reasoning. Both re-confirm instead of testing.
- **Picking the winning convention by counting call sites.** The bigger one may be the
  old architecture. Report the conflict.
- **Treating a benchmark quantile or a blog threshold as a gate.** Rank against the
  repo; gate only on what the repo declares.
- **Calling a long file bloat without its churn.** Long, cold and cohesive is fine;
  long, hot and internally splitting is the finding.
- **Severity inflation.** A layer violation in a file nobody touches is Low.
- **Guessing load or stakes** to fill the profile. A guessed "small internal tool"
  quietly lowers every severity. Ask, or write `unknown` and judge as high stakes.
- **Handing the profile to everyone.** Extractors that know the product look for
  confirmation; verifiers that know the stakes confirm. Pass each agent its slice.
- **Reporting style as architecture.** If a formatter can fix it, it is not a finding.

## Gotchas

- **Bot and formatter commits poison hotspots.** Split them out or the top hotspot is
  the lockfile.
- **Dynamic registration hides consumers.** Framework routing, dependency injection and
  plugin registries make live code look dead. Check before calling it orphaned.
- **Parallel test runs fabricate results.** Test strength runs alone, with nothing else
  exercising the suite.
- **A scope change looks like drift.** Compare fingerprints before numbers.
- **Temporary migration seams look like erosion.** Record them as accepted exceptions
  with an owner, reason and expiry instead of re-reporting them every audit.
- **Hotspot-only sampling makes every repo look bad.** At `deep`, the random control
  sample is what tells you whether the hotspots are unusual.

## Reference files

- `references/profile.md` — the profile template, the questions to ask, and how the
  profile selects dimensions.
- `references/rubric-architecture.md` — architecture rows, front-end rows included.
- `references/rubric-gates.md` — the gate manifest, decay rows, the test-strength funnel.
- `references/rubric-contracts.md` — contract rows, front-end rows included.
- `references/rubric-verbosity.md` — verbosity rows.
- `references/rubric-security.md` — security rows S1–S12, the scanner layer, severity by profile.
- `references/rubric-performance.md` — performance rows P1–P13, measurement status, budgets, platform emphasis.
- `references/scans.md` — detection recipes per extractor, tools per stack (security and
  performance included), and the measurement protocol.
- `references/judge-brief.md` — the judge prompt, its slots, and the finding schema.
- `references/verifier-brief.md` — the verifier prompt and its verdicts.
- `references/baseline.md` — the baseline schema and the drift-comparison rules.
- `references/run-record.md` — the run directory layout, the append-only rules, the
  merge trace, and what `review.md` shows a human.
- `references/scripts.md` — the bundled scripts: contract, catalogue, commands,
  diagnosis. Passed to every agent that runs one.
- `references/model-tiers.md` — tiers mapped to concrete models per harness, and the
  fallback when subagent dispatch is unavailable.
