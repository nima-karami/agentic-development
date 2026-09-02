---
name: build-and-verify
description: Use when an approved plan, spec, or small direct change has to become working, committed code — "build it", "execute the plan", "implement this slice/task", picking up after a plan is approved, or a build handed to an agent in an automated pipeline. Triggers - implementing a slice, fanning executors out over a plan's parallel groups, isolated workspace vs in-place, red-first tests, running the gate, "is this actually done", commit hygiene before handoff.
allowed-tools: Read, Glob, Grep, Agent, Write, Edit, Bash, AskUserQuestion
---

# Build and Verify

Take one planned task — or one small direct change — to a **verified, committed** state.

## Core principle

Design already happened. The plan (or the spec, or the agreed intent) is the
contract, and this stage exists to keep execution honest against it — not to
re-decide anything. Speed comes from that: the executors' job is to get the slice in
front of a reviewer, not to prove each keystroke.

Two failure classes justify every rule below, and both are field-observed, not
theoretical:

1. **The gate said green and the thing was broken.** Lint, types and thousands of
   unit tests passed over a stylesheet where hover did nothing; a suite passed over a
   selector matching nothing, its timeout swallowed by an empty catch, comparing a
   string to itself; a red gate was reported green twice because the run was piped
   through a pager and the pager's exit code was read.
2. **The executor did something the plan never named.** One "implementing the plan"
   silently added a module, a required callback, and changed shared semantics — none
   of it agreed; another verified its work, was cut off before committing, and the
   work was lost.

So: evidence, not assertion; the plan's file map, not judgment in the worktree; and
a commit, because uncommitted work is not done.

## When to use

- An approved plan or spec is ready to build, slice by slice.
- A single task or slice is handed over for implementation and verification.
- A small direct change (bug fix, one-surface tweak) where the intent is already
  settled — run the same loop at LITE weight.

## When NOT to use

- The decision isn't settled yet. Specifying and planning are separate stages; this
  one executes them and never re-opens them.
- Nothing to run against. If the repository has no executable gate and no way to
  observe the artifact, establishing that is a different job and comes first.
- An audit, review, or QA-only pass over code someone else already landed.

## Hard rules

- **Gate integrity.** Never weaken, narrow, mock out, skip, or defer a gate to get
  green. Gates are development discipline, not production-only. A gamed gate is a
  failed task.
- **Done-claim gate.** No "done", "fixed", "passing", or "wired" without: the gate
  command run in this turn with its exit code captured directly (never through a pipe
  or pager); runtime proof for any user-facing behavior; the change list diffed
  against the plan. A report missing any of these bounces.
- **Evidence rules.** A consistency claim requires a full search, not spot checks. A
  negative claim ("nothing uses X") requires a recursive search including ignored and
  hidden directories. Deleting as dead requires proving zero consumers through
  indirection. A claim about current behavior requires measurement, not inference
  from source. A regression claim requires reproducing at the pre-change baseline
  first.
- **Concurrency hygiene.** Never run the full gate under concurrent subagent load.
  Never share temp or browser-profile directories across sessions. Never kill
  processes by image name. Verify a worktree's base commit before building on it.
  Never install dependencies in a directory you have not verified is the intended one.
- **Model tier rule.** The session holds decisions. Judgment-heavy delegated work
  runs one tier below the session; mechanical work two tiers below, with a floor at
  the mid tier; never delegate upward. The bottom tier never builds against slow or
  flaky suites and never writes a root-cause diagnosis.
- **Script over manual.** A mechanical routine that will repeat — the same shape of
  tool call more than a handful of times, the same setup/teardown twice — becomes a
  script that takes arguments. Durable scripts go in the project's scripts directory;
  one-offs to the OS temp dir. Doing it all by hand is the default, and it costs
  tokens and wall-clock.
- **Settled decisions travel forward and are never re-litigated here.** A locked
  decision found genuinely broken is re-locked with the user (or, unattended, recorded
  as a `Decisions Needed` item); it is never silently adapted around.
- **Over-production is a defect.** A slice does not get a worktree, four executors,
  and a design conversation because the machinery exists. Right-size (see the tier
  table).
- **The commit is the evidence.** A verified, uncommitted build is lost work, not a
  finished task. Commit before reporting.

## Steps

### 1. Read the contract and size the run

Read the plan (or spec, or the stated intent) in full: slices, file map, locked
decisions, per-slice checks, parallel groups, exclusive claims. Then declare the tier
out loud in one line, with the reason.

| Tier | When | What you run |
|---|---|---|
| **LITE** | One slice, one surface, few files, no parallelism | In place on a branch, one builder (or inline), named check + gate + commit |
| **FULL** | Multiple slices or groups, shared/entry-file risk, user-facing behavior | Isolated workspace, executors per group, per-slice review, runtime proof |

When unsure, pick the smaller one and deepen if the slice fights back.

### 2. Choose the workspace and capture the baseline

**Isolate when** two or more executors will work concurrently; the run is long enough
that the main checkout must stay usable; or the change is one you may want to throw
away whole. **Work in place when** it is a single short slice with no concurrency, or
duplicating the workspace is disproportionate — an expensive dependency install,
native or linked builds, or machine-global singletons the environment only has one of
(a fixed port, one emulator, one device, one profile directory). Isolation you don't
need is over-production; isolation you skipped under concurrency is corruption.

Prefer the harness's own isolation mechanism when it has one, a manual checkout
otherwise; several mechanisms exist and they fail differently. **Whichever you use,
verify the base commit before building on it** — a native mechanism has silently
based new workspaces on a stale commit, and the work built there was unmergeable and
discarded. Walk `references/workspace-hazards.md` before the first mutating command;
it is short and every line on it destroyed a real run.

**Then write the baseline artifact — before any mutating command.** One file in the
run's evidence location holding two things: (a) the gate's result at the base commit
and its exact failure set, check by check; (b) hashes of the gate definitions — test,
lint and CI configuration plus the existing test files. Step 6's anti-gaming diff and
the attribution rule in Step 4 both read from it. Captured after the first edit it
proves nothing; reconstructed from memory it is not evidence.

### 3. Dispatch the slice's groups

The plan's grouping is the plan's, not yours to re-cut. **One executor per parallel
group, at most four concurrent, all of a slice's executors dispatched in a single
message** — spawning one and waiting for a file-disjoint sibling to report back is a
violation, not a style choice. A slice the plan left ungrouped runs as one executor.

- **Confirm disjointness against the plan's actual file lists before fanning out.**
  Independence stated at spec time is a hypothesis.
- **Serialize on shared entry files.** A global stylesheet, the app/root entry, a
  dependency or plugin registry, a route table, a protocol/type barrel — these are
  the collision points even when feature logic is disjoint. Anything the plan lists
  as an exclusive claim gets exactly one lane, and the touching groups run one after
  another, never together.
- **When unsure, serialize.** Merge corruption costs more than the wall-clock saved.
- Pick each executor's tier per the model tier rule above; the table and its field
  evidence are in `references/model-tiers.md`.
- Build every brief from `references/executor-brief.md`. A brief missing the
  workspace path, the file map entries, or the plan-fidelity rule will produce work in
  the wrong tree or work nobody asked for.

**Conductor vs executor.** The session decides; executors do. The session owns
architecture, naming, taste, and every judgment the plan left open. Everything
mechanical — reads of the tree, bulk edits to a locked signature, gate runs, driving
the artifact — goes to an executor, and the session reads the executor's report
rather than the filesystem. **The tell that the split has broken is the session
running its fifth file read in a row.** An executor that hits a genuine design fork
reports it back; it never resolves it in the worktree.

### 4. Build the slice, red-first

- **A new test is shown failing before the fix exists, and the red is an assertion
  red.** A missing module or an import error is evidence about the file system, not
  about the assertion — the red is observed against present-but-wrong code. An
  import-red counts only for the step that creates the file, and an assertion-red
  follows once it exists. A test never observed red proves nothing about what it
  tests; the field's unconditional-pass tests all entered this way.
- **Mutation-verify every fix**: revert the fix, confirm the new test goes red,
  restore. A test that stays green with the fix removed is not a test.
- Per task, the only check is the plan's named check for that task — seconds, not
  the full gate. The full gate runs once at the end (step 6). A gate on every rung is
  what made past runs crawl.
- **Attribution before blame.** Before calling anything a regression, reproduce it at
  the pre-change baseline recorded in Step 2. A gate run under concurrent load is not
  evidence — two concurrent runs reaped each other and produced a "24 passed / 47
  errors" that was mistaken for a regression for weeks. Suspect load, ports, stale
  processes and leftover servers *before* suspecting the diff. Attribution runs in
  both directions from the same artifact: a failure that reproduces at the base commit
  is not yours, and Step 6 says what to do with it.
- **The deviation rule.** When a step's assumption turns out wrong — the piece it
  builds on is misaligned, a locked signature doesn't fit reality — that step
  **stops**, and fixing the misaligned piece becomes the task. Never bridge: no shim,
  adapter, second copy, special case, catch-and-default, widened type, or fallback
  written to avoid touching the real problem, and no patching a leaf or derived value
  when the defect is in the source it derives from. The report **leads with the fix
  that keeps the locked decision**; a softened alternative may follow, never lead.

### 5. Plan-fidelity diff

Before anything is handed back, diff the whole change list against the files and
shapes the plan names. Anything extra — especially a touch on shared or foundational
code the plan didn't name, or on a file another group owns — is a **stop-and-report,
not a judgment call**. Placement drift is a blocker, not a nit: a file created at a
path the file map doesn't name stops that executor where it stands; it is never
relocated on the executor's own judgment and never parked somewhere sensible for now.
The session runs the same comparison from the other side before the slice is handed
over.

### 6. Gate, runtime proof, and the done-claim gate

Run the full gate once, at the end of the task, with nothing else running.

- **Capture the exit code directly.** Never pipe the run through a pager, a tail, or
  a formatter and read that command's status.
- **Diff the gate definitions against the baseline artifact** written in Step 2. A
  weakened, narrowed, deleted, or mocked-out existing gate fails the task. New tests
  are fine. Without this diff, "green" only means someone made it green.
- **Runtime proof for any user-facing behavior**: drive the real artifact and record
  what it actually did — rendered output, console state, real stdout, exit code, HTTP
  response, generated file. Unit output is not a substitute; three lanes once shipped
  styling that passed lint, types and ~2500 tests and did nothing on screen. If the
  artifact genuinely cannot be driven here, say so explicitly in the handoff and name
  what wasn't covered; never infer a pass.
- **Know where this repository's gate lies.** Gates have been green over a literal NUL
  byte in a source file (twice), a byte-order mark, silent data loss, a mock that
  replaced the subject wholesale so 190 tests were blind, and a leftover process
  squatting a port producing a false "4 passed". If a gate is wrong, fixing the gate
  is the task.
- **A red gate has three branches, and only one of them is "fix it".** A failure the
  slice caused is fixed forward, in its own commit, and the gate re-run until green. A
  failure the slice did **not** cause — proved by reproducing it at the base commit,
  the same procedure as the attribution rule in Step 4 — is **reported, never
  silenced, and never fixed in-slice when the fix would touch a file outside the
  plan's file map**: report it as a before/after diff of the failure set against the
  baseline artifact, emit `GATE: fail <exit code> <command>` with the reason
  `pre-existing: <check>` in the deviation list, and put the fix up as a proposed
  follow-up task. A drive-by fix outside the file map is placement drift like any
  other. A failure you cannot attribute either way belongs to the slice until the
  baseline says otherwise.

### 7. Commit

- **Read the working-tree status before staging, every time.** Build and gate runs
  re-dirty tracked files — lockfiles that re-resolve local paths, generated API
  reports that reorder themselves. Those get restored, not committed; a *real*
  contract change in one of them is read and committed deliberately.
- **One commit per slice** by default. Split by task with staged hunks only when the
  slice is big enough that one commit would hide a wrong turn.
- Follow the project's own message convention (read recent history if it isn't
  written down). Never invent a different one. **The repository's documented
  convention outranks any session- or harness-level attribution or trailer default**;
  where they conflict, follow the repository and say in the report which default you
  overrode and why.
- Commit is the endpoint. Pushing, opening a pull request, or merging is a separate,
  explicit request.

### 8. Learnings and handoff

Append one to three bullets to the run's learnings file, each tagged with where its
fix belongs: `[<skill-name>]`, `[<doc path>]`, `[instruction-file]`, `[memory]`, or
`[none]`. Process observations only; code debt goes to the repository's debt file.
Without the tags the retro cannot route them. Write them right after the slice, while
the friction is fresh — this is the session's judgment call, not an executor's.

The report itself states **the tier you declared in Step 1** and **quotes the
working-tree status you read before staging**, short form — the two facts a reader
cannot recover from the commit alone.

Then end the stage with exactly this block:

```
BUILD: <branch>@<sha>          # commit SHA is the evidence; uncommitted work is not done
GATE: pass|fail <exit code> <command>   # exit code captured directly, never via a pipe
RUNTIME_PROOF: <path | "none: <reason>">
DEVIATIONS: <n>                 # one line; the detail goes in the list below the block
LEARNINGS: <path>               # tagged bullets appended this task
```

`DEVIATIONS: <n>` stays a single line inside the fence — a downstream stage parses it
and a multi-line value breaks that parse. Immediately after the fence, list each
deviation: what the plan said / what was found / the fix that keeps the locked
decision. A `pre-existing: <check>` from Step 6 is listed here too.

An independent review of this diff happens after this stage, outside this skill. Do
not pre-empt it and do not narrate why the change is correct — the reviewer gets the
diff, not your defense of it.

## Running unattended

No human means no blocking questions — a prompt in a detached run hangs the pipeline
until it is killed.

- **Never call an interactive question tool.** Every would-be question becomes an
  assumption on the safest, most reversible reading, recorded as a `Decisions Needed`
  item in the handoff.
- A locked decision that turns out broken is re-locked *on paper*: record what was
  found, the fix that keeps the decision, and proceed on the safest assumption.
- Retry a failing slice at most twice, then record it blocked with the reason and
  what would unblock it. An honest "blocked" beats a fake "done"; never stub, fake,
  or narrow scope to manufacture a green.
- **Leave a trail.** The baseline artifact, the gate output, the commit SHA, the
  deviations and the learnings all land on disk. After an unattended run the chat is
  gone and the files are the only record.
- Assume compaction. Re-read the plan and the run's state files before acting on
  anything you "remember".

## Common mistakes

- **Reporting green from a piped run.** The pipe's exit code is not the gate's. This
  put a red gate in two reports as passing.
- **Fanning out sequentially.** Dispatching group two only after group one returns
  wastes the entire point of the grouping.
- **The session doing the work.** Five file reads in a row, a bulk rename, a manual
  edit sweep — that is executor work being paid for at the session's tier.
- **Isolating by reflex.** A worktree for a two-file slice costs a dependency install
  and buys nothing.
- **Working in place under concurrency.** The mirror mistake, and far more expensive:
  a stray install in the wrong directory has wiped the shared checkout mid-run.
- **Absorbing a deviation.** Writing a shim, a second copy, or a widened type so the
  slice can finish is how a plan quietly stops describing the code.
- **Trusting an executor's report.** One reported a clean gate and a passing
  end-to-end run; an independent re-run found two real issues. Check the diff.
- **Claiming a fix without mutation-verifying it**, or accepting an import-red as the
  red. Both leave a test that may pass over a deleted feature.
- **Stopping at "verified".** Verified and uncommitted is lost work the moment the
  session ends.
- **Ending the turn on "should I commit?"** Acceptance of the slice is the go-ahead;
  asking again is a stall, not politeness.

## Gotchas

- **Concurrency fabricates failures and destroys state.** Four runs lost a workspace's
  linked dependency directory; one cleanup wiped a shared scratch directory holding
  other sessions' browser profiles; one kill by image name closed the user's real
  browser. Scope destructive commands to paths verified this session; target processes
  by the identifier you started.
- **A gamed gate is worse than a red one.** It hides the defect and poisons every
  later "done" built on top of it.
- **The handoff block is a contract.** A downstream stage greps it. Keep its shape
  exactly as written, including a `none: <reason>` when there is no runtime proof.
- **A slice's own check passing is not the gate passing.** That trade is deliberate —
  the end-of-task gate exists to catch what the named checks missed. Don't quietly
  promote a named check into a done-claim.
- **Byte-level damage is invisible to every gate.** Stray control bytes, a
  byte-order mark, and mixed line endings have all shipped green. If something
  behaves impossibly, look at the bytes.
- **A long multi-milestone build wants a fresh session per milestone**, resuming from
  the plan on disk. One compaction marathon burned roughly two million tokens doing
  what clean per-milestone sessions do cheaper.

## Reference files

- `references/executor-brief.md` — the brief template every executor gets, and the
  rules it must carry.
- `references/model-tiers.md` — concrete tier table and the field evidence behind it.
- `references/workspace-hazards.md` — isolation mechanisms, their failure modes, and
  the pre-flight checklist.
