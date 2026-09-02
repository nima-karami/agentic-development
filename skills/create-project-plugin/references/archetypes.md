# Archetype catalog

One entry per stage the suite can carry. Each gives: the **seed** to press in, the
**inclusion rule**, the **bindings** the emitted skill must carry, the **gates** it
owns, and **shape notes** — the patterns proven in a hand-built suite, generalized.

A project takes the archetypes it needs and adds more as it goes. Never front-load the
catalog. Order below is pipeline order.

**Reading a seed.** Seeds are the lab's general skills, installed under the user's skills directory as `<seed-name>/SKILL.md` (with their `references/`). Open the seed and keep its signature patterns, not just
its steps: the triage tier declared before content, the one-level-at-a-time locking
ladder, the restate-and-wait-for-confirmation gate, the self-review before emitting,
the machine-parseable handoff block. A from-scratch generation loses exactly these.
When a seed has no readable file — some skills are harness-registered — reconstruct
from its description and observed behavior, say so in the report, and never block on it.

**Every emitted skill also carries** the canon items assigned in `references/canon.md`
plus the project-binding block. The gates listed per archetype below are *in addition*
to those.

**Two invocation shapes, and why every stage must say which artifacts it owns.** A
per-task stage can also be invoked **per item** by `loop`, once for each entry in a
backlog run. The same skill therefore runs many times inside one conductor's run, and a
file it legitimately owns per task — a run report, a run directory, an archive — becomes
a file it must *not* write when a conductor owns the run. Each archetype's entry below
states its artifacts; the emitted skill states, in its own body and its handoff block,
which of them it owns **per task** and which it hands to the conductor **per item**, and
how it tells the two cases apart when the invoker did not say. Left unstated, each item's
run silently overwrites the record of the one before it, and no per-skill review can see
it — which is why the suite-level write-ownership table in `packaging.md` exists.

---

## manage — the desk charter

- **Seed:** none. This is a session-role charter, not a stage.
- **Include when:** the project is a multi-repo workspace, or work routinely runs across
  several concurrent sessions. Skip for a single-repo solo project — there is no desk.
- **Bindings:** the board files (backlog, tickets, deferred list); the workspace
  lifecycle commands; the dev-server procedure and where the port or resource block is
  recorded; how to reach peer sessions.
- **Gates:** never read repository source, and never dispatch an agent to "ground" a
  board item in code — filing is a docs-mapping task, and an item whose truth lives in
  code is filed with *needs investigation — its own session*. Never design, shape
  options, or judge an implementation. Never modify the suite itself; a gap in a skill
  or script is reported to the user. Investigations only on an explicit ask.
- **Shape notes:** invoked once, it locks the role for the session, including after a
  compaction — say so, and say to re-read it whenever the role feels ambiguous, because
  ambiguity is where this session drifts into engineering. Runs at the mid tier: it is
  dispatch-and-file work. Give it chat-style rules, because the user reads this session
  constantly — routine operations act rather than ask, status answers are terse tables,
  and every line either changed a file, moved a process, or answered what was asked.
  Closing work goes through the close archetype, never a bare delete and never the
  teardown script alone; the distillation gate is the point.

## start — kickoff and router

- **Seed:** none. This is the front door, and it routes to everything else.
- **Include when:** always. The highest-value archetype in any suite.
- **Bindings:** the ticket or work-item source of truth (and which external system to
  *not* call); the workspace layout — folder-per-task, worktree-per-repo, or in-place;
  the branch rule; the read-when map; the exact setup command or, absent one, the
  ordered manual sequence.
- **Gates:** the **intent restatement** — restate the ask in one short paragraph
  (outcome, who it is for, what is out of scope) and do not proceed until the user
  confirms; a wrong restatement caught here is the cheapest fix in the workflow. A
  failed setup preflight is a stop, not something to quietly repair. Canon 3's evidence
  rules bind from here down the whole pipeline.
- **Shape notes:** two halves — **setup** (work item → workspace → branch, from the
  profile's real conventions) and **routing** (restate → ground on the read-when map →
  clarify → assess scale → route, handing the next stage an explicit brief). It sets up
  and routes; it never specs, plans, or builds. Ask for each input and wait for the
  reply; keep every message short and on one topic. Ground with a *focused* read — the
  files the change touches and the siblings showing the pattern — and stop when the task
  can be classified; the deep read belongs to the stage that needs it. Give it a
  **setup-only route** for "just scaffold it" asks, so the script stays the easy path.
  When the work has milestones, say a fresh session per milestone: one continuously
  compacted marathon costs multiples of what clean per-milestone sessions do.

## spec — what, in the project's terms

- **Seed:** `feature-spec`.
- **Include when:** always.
- **Bindings:** where specs live and the naming convention; the project's own notation;
  its accessibility, internationalization and design-token bar; the "done" criteria; the
  lifecycle stance (shims and staged cutovers allowed, or not).
- **Gates:** triage the tier before any content, with a one-line reason. Run the fixed
  checklists for the feature type rather than letting salience pick coverage. Name both
  sides of every changed data flow — a consumer scoped in with its producer scoped out
  is a flagged decision, never a silent one. Claims about current behavior are measured,
  not inferred from source; unmeasurable ones are marked assumed and listed.
- **Shape notes:** keep the seed's tier caps and its handoff block shape. In interactive
  mode, lock the design levels one at a time; in autonomous mode never ask — every
  would-be question becomes a severity-tagged decision-needed entry and the run
  continues.

## plan — how, at file level

- **Seed:** `implementation-plan`.
- **Include when:** always.
- **Bindings:** where plans live and their format; the commit-sequence convention; the
  style authority to cite by path; the exclusive-claim paths from discovery; the
  executor tier the project actually dispatches to.
- **Gates:** no placeholders — an undefined type, "add appropriate error handling",
  "similar to task N" is a plan failure, because the executor will implement the
  placeholder. Every new or moved file has its folder decided in the plan; the executor
  never chooses a placement. Producer/consumer scan is mandatory. Parallel groups are
  proven file-disjoint, not asserted; when uncertain, serialize. A self-review before
  emitting: spec coverage, placeholder scan, signature consistency, placement, and a
  caller scan for every changed signature.
- **Shape notes:** calibrate task detail to the executor tier explicitly. A plan executed
  a tier lower carries exact paths, exact signatures, and test intents with expected
  failures — every judgment call made in the plan. Decide the full-code-bodies question
  deliberately: bodies maximize weak-executor safety but go stale and get copied blindly;
  signatures plus test intents is usually the better trade when execution runs under a
  gated build skill. Slices are sized by check, not by feature.

## design-review — fresh eyes before code

- **Seed:** `architecture-critic`.
- **Include when:** always, but it runs only on the large route at runtime.
- **Bindings:** the project's architectural invariants — ownership boundaries, contract
  seams, additive-not-breaking rules — as the lens the review applies.
- **Gates:** runs in a fresh context, never the plan's author, and never receives the
  design's backstory or the author's case for it. Every finding cites a concrete anchor
  in the design. Over-engineering is a finding, not a virtue. No architecture is
  mandated because it is idiomatic.
- **Shape notes:** advisory, not blocking — it emits a verdict and the user decides. Do
  not persist it as a project artifact by default; it is a review snapshot, not a
  record. Do not pair it with code review: this reads a design, that reads a diff.

## build — execute under the project's gates

- **Seed:** `build-and-verify`.
- **Include when:** always.
- **Bindings:** the exact gate command and where it runs; test conventions; the
  workspace layout and how executors address it; the commit convention; the known
  **false-green gates** from discovery (a lockfile that absorbs a local link, a config
  silently ignored when malformed, a linter that passes vacuously in one layout).
- **Gates:** canon 1–9 in full. Plus: **plan-fidelity** — every executor's brief ends
  with *diff your whole change list against the files and shapes the plan names for your
  tasks; anything extra, especially a touch on shared or engine-level code the plan did
  not name, is a stop-and-report, not a judgment call* — and the conductor runs the same
  comparison from the other side at slice end. **Placement drift is a blocker**, never
  relocated on the executor's own judgment. **The deviation rule:** when a step's
  assumption turns out wrong, that step stops and fixing the misaligned piece becomes
  the task — no shim, adapter, second copy, special case, catch-and-default, widened
  type, or fallback, and no patching a leaf or override when the defect is in the source
  it derives from. A deviation report **leads with the fix that keeps the locked
  decision**; a softened alternative may follow, never lead.
- **Shape notes:** the session conducts and does not solo — one executor per parallel
  group, all of a slice's groups dispatched **in a single message** (a spawn that waits
  for a file-disjoint sibling is a violation), concurrency capped, serial lane after.
  Even quick listings go to an executor; the conductor reads reports, not the
  filesystem. A brief states a code fact only with a citation from a read that happened
  this session. Carry a comment contract if the project has one. Slice loop is fast
  because design was slow: per task only the plan's named checks, the full gate at the
  cadence the project chose, one commit per slice.

## code-review — the diff, by someone else

- **Seed:** `code-review`.
- **Include when:** always.
- **Bindings:** where the review verdict is recorded, if anywhere; the project's style
  authority by path; the integrity checks that matter for this stack.
- **Gates:** the reviewer is never the author and never the agent that dispatched the
  build, runs read-only in a fresh context, and never receives the author's narration of
  why the change is correct. Every finding carries a `path:line` anchor; unanchored
  findings are dropped. Any blocker forces a revise verdict — no trading a blocker down.
  Do not trust the diff's self-description: a comment, a test name or a doc line is a
  claim, not evidence.
- **Shape notes:** review against plan fidelity, spec acceptance criteria, tests that
  cannot fail (empty catch, self-comparison, mocked-away subject, selectors matching
  nothing), byte-level corruption, placement, dead code left behind, and consistency
  claims made without a full search. Re-review after fixes happens outside the author's
  context, which is where a self-cleared finding hides.

## qa — drive the real artifact

- **Seed:** `runtime-qa`.
- **Include when:** the artifact can actually be observed. **When it cannot, emit no QA
  skill** — emit the finding that observability must be fixed first. A QA role that
  cannot observe reports passes nobody saw, which is worse than no QA role.
- **Bindings:** the launch path (command, directory, ports, environment); the project's
  test affordance — debug handle, control API, seeded fixture mode — documented in a
  plugin reference file if it has real surface area; where evidence goes; every variant
  the artifact ships to; what the unit gate is blind to here.
- **Gates:** never report a pass not observed, and never fake one from unit output.
  State the build under test — repository, branch, short revision — for every repository
  involved. Always state what was not covered and why. Capture evidence as it happens,
  not afterwards, and *read* what was captured. Close every session, process, and
  temporary directory opened; never kill by image name.
- **Shape notes:** scope is settled and restated first, including every variant, never
  just the reference one. Design-fidelity work is verified by looking, side by side
  against a baseline captured *before* the original rendering is deleted. A report
  template in the skill's `references/` keeps reports comparable across runs; the report
  itself goes to a filename no other stage writes.

## deliver — the project's shipping flow

- **Seed:** none. Fully project-bound.
- **Include when:** the project has a delivery flow — pull-request tooling, a release
  or preview script, a staged deploy. Skip when committing to the trunk is the whole
  story. This rule decides, including for a single-repo app: the preset's shortlist is a
  default, not an exclusion.
- **Bindings:** the description format and voice; the creation tooling and its known
  footguns (auth scopes, argument quirks, comment-authorship marking); the title rule;
  the ordered cross-repo sequence when a release spans repositories.
- **Gates:** invoked only on explicit request — commit is the default endpoint of a
  build, and pipelines and merges are separate explicit asks. Verification content comes
  from the QA report, never from the author's confidence. Keep the draft out of the
  repository tree: a description file swept up by a wildcard stage is a real failure.
- **Shape notes:** reference sibling repositories by role and convention, never by
  absolute path, so the skill survives a checkout somewhere else. Name the "these must
  match" contracts between repositories, and the known failure modes in order.

## close — distil, then tear down

- **Seed:** none. Generalized from the hand-built suite's bookend.
- **Include when:** always. Even an in-place workflow needs the distillation half.
- **Bindings:** where the run's learnings file lives; where retro notes go (inside the
  plugin); the teardown command or sequence; how merge state is checked.
- **Gates:** **the note is the gate** — teardown does not run until the retro note
  exists, written even when it says "nothing notable". Branch authorship is checked
  before anything is removed: a last commit that is not the user's is a stop-and-ask, and
  no script checks this for you. Every branch must be an ancestor of the mainline before
  anything is touched; forcing past that is the user's call alone, never taken on the
  agent's own judgment.
- **Shape notes:** state the two invocation shapes explicitly — per task it owns the run
  report and the archive; under a conductor it writes the item's outcome into the
  conductor's ledger and touches neither the report nor the conductor's live state, and
  says which case it took in its handoff block. This is a procedure, not a delete. Ask
  **once** whether anything in
  the working artifacts should survive, and default to delete — keeping by reflex is how
  repositories fill with stale plans. A constraint that genuinely outlives the task
  belongs in the repository's docs as a line, not as an archived plan. Say explicitly
  what close never touches: the ticket records themselves, and the state of the main
  checkouts.

## gate-health — re-audit the gates

- **Seed:** `solidify-repo`, in its re-audit mode.
- **Include when:** always. Gates erode silently; nothing else in the suite watches them.
- **Bindings:** the gate definitions and where they live; the previous audit report; the
  project's waiver conventions.
- **Gates:** re-score every category against the *current* rubric, not the one the
  earlier report used. Diff against the previous scores and account for every change.
  List checks that became advisory or non-gating — a check that runs and cannot fail is
  a check that stopped working. List warning counts that grew: one class going 1 → 12 →
  17 is drift with a date on it. List every documented claim the gate does not actually
  keep, and every standing waiver that contradicts the gate rule.
- **Shape notes:** "the repo already satisfies every category" is a claim requiring the
  delta audit, not a reason to skip it. Never disable, downgrade, narrow or defer a
  check as production-only or just-for-now: the repository is worked by humans and
  agents together, and a check that stops looking is how the tree rots. Scheduled by the
  retro, not by vibes.

## loop — the unattended conductor

- **Seed:** `autonomous-build-loop`.
- **Include when:** the user wants unattended or overnight runs. Skip otherwise; an
  unused loop skill is twelve bindings to keep current for nothing.
- **Bindings:** where the run ledger lives (outside every repository, so there is nothing
  to accidentally commit); the backlog source; the gate cadence the project chose; the
  concurrency cap; where run reports go.
- **Gates:** all nine canon items. Plus: no executable gates means no feature work —
  ground the repository first. No way to run and observe the real artifact means the loop
  refuses to run. Never relay an executor's gate claim as its own. An emptied self-made
  queue is not completion when the mandate was time-or-scope. Never call an interactive
  question tool; would-be questions become ledger entries. Retry a blocked item at most
  twice, then quarantine it with the reason and move on — an honest blocked beats a fake
  done.
- **Shape notes:** it states the per-item split from its own side — which artifacts it
  owns as conductor, and that it tells each per-task stage a conductor is running — so
  the contract is written at both ends rather than assumed at one. The ledger on disk is
  the source of truth and is re-read after every compaction; chat memory never is. Right-size the topology per item rather than fanning
  out by default: fanning out one group re-pays exploration context for no gain.

## retro — improve the suite

- **Seed:** none. This is the evolve mode, shipped so the suite matures without this
  generator installed.
- **Include when:** always. Without it the suite has no drift model, and every lesson is
  re-learned per run.
- **Bindings:** the retro-note directory and its applied subdirectory (both inside the
  plugin); the suite's changelog; the instruction files, docs and memory the changelist
  can target; where session transcripts live.
- **Gates:** read the notes before touching a transcript — they are pre-tagged and were
  written by sessions that knew what hurt; sweep transcripts only for what the notes left
  open. Diff each theme against where it already lives before proposing anything: a
  proposal that duplicates an existing rule in a second place creates drift, so
  strengthen or move, never fork. Never propose weakening a gate as the remedy for a check
  that keeps failing — a repeatedly failing check is a finding about the code or the
  binding.
- **Shape notes:** the seed-drift diff is the one place an emitted skill names a general
  skill. It names seeds **as diff targets only** — never invoking one, never depending on
  one being installed — and says so in as many words, with a skip-and-record rule for a
  seed it cannot find and no hard-coded machine path to look for it at. Beyond that,
  classify knowledge gap / enforcement gap / one-off, because each has a
  different fix. Collect counter-examples too: they show which investments are paying off
  and should not be disturbed. Apply on approval, bump the version, write the changelog
  entry, and file applied notes away so the top level is exactly the unaddressed set.
  Full procedure in `learnings-chain.md`.

---

## Adding an archetype

A recurring project workflow none of these covers is a signal to add an archetype, not
to force-fit one. Give it the same entry shape — seed, inclusion rule, bindings, gates,
shape notes — and add it here so the next project benefits. The catalog grows the same
way a project's suite does.
