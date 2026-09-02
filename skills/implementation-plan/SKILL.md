---
name: implementation-plan
description: Use when a settled spec — or a small, clear request — has to become an implementation plan before any code is written. Triggers - "write the plan", "implementation plan", "plan the implementation", "break this into tasks/slices", "how should we build this", deciding file placement / signatures / task order, or preparing work for parallel executors or an unattended build agent.
allowed-tools: Read, Glob, Grep, Bash, Agent, Write, AskUserQuestion
---

# Implementation Plan

Turn a settled spec into an ordered, **right-sized** plan an executor can build
without guessing — or decide, out loud, that no plan is warranted.

## Core principle

The spec says *what*, in user terms. **Every technical judgment call happens here**:
architecture, data flow, contracts, placement, decomposition, ordering. Write for an
executor that has the repo but none of this conversation and questionable taste — it
should never have to choose a name, a placement, or an abstraction.

Two opposite failure modes, both seen repeatedly in the field:

1. **Over-production.** A plan that restates the spec at lower fidelity is a defect,
   not diligence. A three-sentence bug report once produced a four-figure-line spec
   plus a plan that added nothing.
2. **Under-specification.** Placeholders, "similar to task N", a consumer scoped
   without its producer, a signature that no task defines. Each one is a guess the
   executor makes badly.

Triage first, then be exact. Proportion is the skill; enumeration beats eloquence.

## When to use

- A spec (or settled intent) is agreed and the next step is code.
- Work is about to be split across parallel executors and needs a disjointness proof.
- A build is being handed to an unattended agent that has no one to ask.

## When NOT to use

- The spec already carries the file map and signatures — see SKIP.
- The change is one obvious edit (rename, copy tweak, dependency bump) — just do it.
- Behavior is still undecided — that belongs to the spec stage, not here.
- Implementing — this produces a plan; a different step builds from it. An
  independent design review happens after this, outside this skill.

## Modes

Default **interactive**. Switch to **autonomous** when the invoker says so, or when
there is plainly no human in the loop (running inside a detached or long-running
task). Explicit signal wins.

- **Interactive:** lock the levels **one at a time** (Step 2), each a short message,
  agreed before descending. Genuine forks go through a structured question, with
  options and a recommended default.
- **Autonomous:** **never ask.** Record each level and its reasoning in the plan, take
  the most conservative reversible default, and log every would-be question in
  `## Decisions Needed`, severity-tagged `high`/`normal`. Never halt on a flag.

## Hard rules

- **Triage before producing.** Declare the tier with a one-line reason before writing
  anything. Over-production is a defect: a stage whose artifact would restate the
  previous stage's artifact at lower fidelity is skipped and the skip recorded.
- **Settled decisions travel forward and are never re-litigated downstream.** A
  decision locked in the spec or in conversation is an input here, not an open
  question. If one is genuinely broken, say so and re-lock with the user — or,
  unattended, record a `Decisions Needed` item; never silently adapt.
- **No placeholders.** Each of these is a plan failure, because the executor will
  guess and guess wrong: "TBD" / "TODO" / "details later"; "add appropriate error
  handling / validation / edge cases" (name the errors and the handling); "write
  tests for the above" with no named behavior and key assertion; "similar to task N"
  (tasks are read in isolation — repeat the signatures); any type, function, or path
  referenced but defined in no task.
- **The executor never chooses a placement.** Every new or moved file has its folder
  and name fixed here. A file the plan didn't place is a stop-and-report, not an
  executor decision.
- **Never plan a file before it has a caller.** An interface or stub added so a later
  slice "doesn't have to invent it" is dead code carrying a guessed signature.
- **Producer/consumer scan is mandatory** (Step 3). Scoping a consumer without its
  producer is the highest-cost defect this stage can ship.
- **When parallel disjointness is uncertain, serialize.** Merge corruption costs more
  than the wall-clock saved.
- **Follow the project's existing plan-file convention; never invent a layout.** The
  convention is location, naming, and section order — that is its whole extent.
- **The plan file carries no boilerplate header** — no banner, no instruction to invoke
  a named workflow, no tooling advert. Such a header outlives the workflow that
  mandated it and sits, stale, in every plan file in the repo. **Where the two rules
  meet, this one wins:** a banner or "invoke workflow X" line carried by every existing
  plan file is stale boilerplate, not the convention, and is not copied forward.
- **Never weaken, narrow, mock out, skip, or defer a gate to get green.** Gates are
  development discipline, not production-only. A gamed gate is a failed task — the
  plan never schedules one, and never plans around a red gate by lowering it.
- **Every plan restates the deviation rule** in plain words: if a task's assumption
  turns out wrong, that task stops and fixing the misaligned piece becomes the work —
  never a shim, second copy, special case, widened type, or fallback routed around
  it.

## Step 0 — Triage (always first, state it out loud)

| Tier | When | What you produce |
|---|---|---|
| **SKIP** | The spec already is the plan: it names the files and the signatures; or one file / one obvious edit; or a bugfix whose root cause and fix site are already known; **or the work is already built** | No plan file. State the file map inline (3–6 lines) + the verification command + the deviation rule, record the skip and its reason, emit the handoff with `PLAN: inline` |
| **LITE** | One surface, roughly ≤3 files, no new seam or public contract, one executor, no parallelism | Locked decisions, file map, contracts for anything crossing a module boundary, 1–3 slices with their checks, verification, deviation rule. No architecture section, no sketches, no parallel groups |
| **FULL** | Multi-module, a new seam or public contract, parallel executors intended, or the spec was FULL | The whole template: all four levels, groups + claims, producer/consumer scan, script candidates, self-review |

When unsure between tiers, pick the smaller one — a section can always be deepened.
Padding a LITE plan is the same defect as a thin FULL one.

**Check the work isn't already built before you plan it.** A spec can arrive after the
fact — an earlier run, a lane that landed while the spec sat in a queue — and a plan for
existing work sends an executor to build it twice. Prove it in this order: the
version-control history of the spec file and of its slug; a tree search for the
identifiers the spec fixes (types, routes, flags, file names); then each acceptance
criterion against the code that would satisfy it. If built, SKIP and cite the commits.

**That SKIP has one exemption, and only that one.** When the reason is "already built",
the evidence of implementation — the commits, plus any spec detail deliberately reversed
or superseded downstream — replaces the inline file map. Every other SKIP still owes all
three.

## Step 1 — Ground it

- Read the spec **in full**. Its acceptance criteria are the coverage target in Step 6.
- **Detect the project's plan-file convention** — an existing plans directory, a
  per-task/run folder that already holds the spec and reports, or wherever the spec
  stage wrote. Follow it exactly — location, naming, section order, and nothing
  further. Following it never means reproducing a banner or an "invoke workflow X"
  line the existing plan files happen to carry; copy the shape, drop the boilerplate.
  If none exists: interactive, ask where; autonomous, put the plan beside the spec it
  implements. Create the directory at write time only, never while drafting.
- **Read the stack from the repository, not from the request.** Language and version
  floors, package manager, and the gate / test / build commands come from the
  manifests, lockfiles, and config in the tree — the invoker's description of them is
  a hint, not a source. Where the two disagree, the repo wins and the plan says so in
  one line.
- Read the repo's style authority in full before any name enters the plan — naming and
  placement are design, and a guessed convention gets baked into every task.
- Delegate the code reading that informs the plan — mapping call sites, checking
  sibling shapes, confirming conventions — to an agent one tier below the session,
  which returns cited findings: **repository-relative full paths with line numbers,
  never a shortened basename.** The session decides the structure; it does not read
  its way through the repo itself. Include the version-control history of any file
  whose encoded behavior the plan changes: a reverted commit's message has settled
  an assumption that nothing in the code stated.
- A claim about current behavior requires measurement, not inference from source. If
  the spec asserts something about how the system behaves today and the plan depends
  on it, verify it before planning around it. Specs assert things that measure false —
  a retired route, a deleted component, a field that never existed. Every claim that
  measures false is recorded in the plan's staleness section with what was measured
  and how the plan proceeds; planning quietly around it hides it from everyone
  downstream.

## Step 2 — Lock the levels, one at a time

**1. Architecture & data flow.** Who owns each piece, how data moves end to end,
where state lives, what crosses each seam. Draw an ASCII diagram whenever the flow
has more than three hops — a picture of the hops is cheaper to argue with than a
paragraph. Lock.

**2. Contracts & signatures.** Exact signatures of the public seams with **real
types**, error shapes, invariants, and validation at every trust boundary. When a
seam claims to mirror an existing precedent, verify it actually matches before
presenting it. For a genuinely novel seam, **sketch first**: two or three scratch
skeleton files in the repo's language — types, interfaces, signatures, no bodies —
written to the OS temp directory (or the project's own scratch convention, never a
new folder in the tree). Hand them over, take the pushback, write the plan from the
agreed shape. A sketch nobody argued with probably wasn't needed. Lock.

**3. File map — the placement contract.** Create / modify / delete, one line of
responsibility each. One responsibility per file; split by what changes together;
mirror the shape siblings already use; name for the role a thing fills; place by
owner, not by topic (a folder named after a data topic is the classic tell). Lock.

**4. Slices, groups, and claims.**

- A **task** is the ~10-minute unit: one deliverable, one executor, small enough that
  a wrong turn surfaces while it is still cheap to undo. Fold setup and scaffolding
  into the task whose deliverable needs them.
- A **slice** is a verifiable seam: the smallest group of tasks that leaves the tree
  in an independently checkable state, carrying a **named check** (the exact test,
  command, or observable flow that proves it). The clock sizes the task; the check
  sizes the slice — one task is a legitimate slice when one task reaches a check, and
  a group that cannot be checked on its own is not a slice, it gets split until every
  piece has its own.
- **Parallel groups:** tasks whose `Files:` sets do not overlap **and** that touch no
  shared entry file form the parallel groups. Write the partition into the slice:
  `**Parallel groups:** G1: T1, T3 · G2: T2 · Serial: T4`.
- **Exclusive claims:** a shared entry file is any file two tasks would both need to
  edit — the application root or composition entry, route tables, barrel/index
  exports, global stylesheets, shared schema or protocol definitions, registries and
  capability manifests, dependency manifests and lockfiles, generated output. Each
  gets exactly one owning task, which runs in the **serial lane** after the parallel
  groups. Every claimed path goes on the handoff's `CLAIMS` line.
- The **Interfaces** blocks are what make parallelism safe: an executor sees only its
  own task plus the `Produces` of the tasks it `Consumes`, so anything two groups
  share must be pinned here rather than read off a sibling's half-written code.
- On multi-milestone work, detail only the next milestone as buildable tasks; later
  milestones stay an outline until the earlier one has taught you something. Lock.

## Step 3 — Producer/consumer scan

For **every behavior the plan changes**, write one line naming: what **produces**
that data / event / state, what **consumes** it, and which side the plan touches.

- If the plan touches only one side, either bring the other side into scope or write
  an explicit line stating why it is unaffected — measured, not assumed.
- A negative claim ("nothing else consumes this") requires a recursive search
  including ignored and hidden directories, not spot checks.
- Every changed signature gets its call sites enumerated in the task that changes it.

The field case: a spec scoped the queue builder out, so a timing change in a consumer
was treated as not touching its producer, and nothing analysed what that did to
ordering. It was the most expensive defect in the corpus.

## Step 4 — Script candidates

Doing everything by hand is the default, and it costs tokens and wall-clock. Scan the
plan for mechanical routines that will repeat — the same shape of edit across more than
a handful of files, the same setup/teardown twice, fixture or data generation, bulk
renames, migrations. Each becomes a **named script with arguments** and its own task,
not a paragraph of manual instructions. Durable scripts go in the project's scripts
directory; one-offs to the OS temp directory. Count them on the handoff's
`SCRIPT_CANDIDATES` line; `0` is a legitimate answer, stated deliberately.

## Step 5 — Write the plan

Fill `references/plan-template.md`, scaled to the tier. Write it to the location
detected in Step 1.

## Step 6 — Self-review gate (before emitting anything)

Re-read the spec with fresh eyes and run all seven checks. Do not claim done with any
of them unresolved; fix inline.

| # | Check | Failure looks like |
|---|---|---|
| 1 | **Coverage** | A spec acceptance criterion with no slice implementing it |
| 2 | **Placeholder scan** | Any entry from the Hard rules list, in your own text |
| 3 | **Signature consistency** | A later task's `Consumes` not matching an earlier `Produces` byte for byte — `clearLayers()` in T3 vs `clearFullLayers()` in T7 is a bug now, not at build time |
| 4 | **Placement** | A path in a task's `Files:` that is absent from the file map or spelled differently; a new file that doesn't sit where its siblings sit |
| 5 | **Caller scan** | An export produced in one slice whose first caller lives in a later slice — move it to that slice |
| 6 | **Producer/consumer** | A changed behavior with only one side named |
| 7 | **Handoff arithmetic** | `SLICES` / `GROUPS` / `CLAIMS` asserted rather than counted from the body |

**The gate leaves an artifact.** A check that reports nothing cannot be told apart
from a check that never ran. In autonomous mode, report all seven as a compact block
placed immediately before the handoff block, one line per check, format
`#n <check>: ok | fixed: <what> | n/a: <why>`:

```
#1 Coverage: ok
#2 Placeholder scan: fixed: named the two errors T2.1 left as "appropriate handling"
#3 Signature consistency: ok
#4 Placement: ok
#5 Caller scan: fixed: moved the exported builder down into Slice 2
#6 Producer/consumer: ok
#7 Handoff arithmetic: n/a: inline SKIP, no counted body
```

An `n/a` always carries its reason; a blank one is a skipped check wearing a label.
Interactive mode may compress the block to the summary line alone.

**A SKIP runs this gate too**, against the inline output: check 1 (coverage — every
acceptance criterion has somewhere to be built) and check 6 (producer/consumer). Then,
whatever the tier, one line: `Self-review: <n>/7 applicable — <reason>`. A gate kept
silent because there is no file is how a SKIP ships an uncovered criterion.

A plan revised after this gate — a narrowed scope, a task absorbed into another —
gets each touched slice re-read end to end against its own check before the revision
stands. Two edits that each looked fine once left no task enabling what the slice's
check assumed was already on.

## Step 7 — Handoff

**Interactive:** present the plan, write the file on the user's go, then emit the
block. **Autonomous:** write the file, report the Step 6 checks, and end with exactly
this block directly beneath them, so the loop can parse it without re-reading prose:

```
PLAN: <path or "inline">
TIER: SKIP|LITE|FULL
SLICES: <n>
GROUPS: <n>            # file-disjoint parallel groups
CLAIMS: <comma-separated exclusive paths>   # shared entry files two tasks can't both edit
SCRIPT_CANDIDATES: <n>  # mechanical routines that should be a script, listed in the plan
```

**Emit it exactly once, as the last thing you write** — after every scan and the
self-review are complete, never mid-work. A block emitted early is a false signal to
whatever greps it: the loop reads the stage as finished and moves on with numbers that
were still changing.

## Common mistakes

- **Defaulting to FULL.** The reflex failure. Most changes are LITE; a real share are
  SKIP. Declare the tier first and mean it.
- **A plan that is the spec, reworded.** If you can't point to a technical decision
  the plan makes that the spec didn't, it is SKIP.
- **Full implementation code in tasks.** It goes stale the moment the first slice lands
  and gets copied blindly by exactly the executor this plan is written for. Exact paths,
  exact signatures, named test behaviors with key assertions — not bodies.
- **Parallel groups asserted, not proven.** Two features that sound unrelated still
  touch the same files. Disjointness is checked against the actual `Files:` sets.
- **Leaving shared entry files unclaimed.** They are where independent lanes collide.
- **Asking in autonomous mode.** It hangs the pipeline. Flag and continue.
- **Slices sized by feature, or by the clock.** "The whole settings screen" is not a
  slice; it is a milestone with no verifiable middle. The clock sizes tasks — ~10
  minutes each — while the slice is sized by the check it can actually reach.

## Gotchas

- **Locking levels one at a time is the point.** A plan assembled whole and handed
  over for approval hides exactly the decisions worth arguing.
- **The handoff block is a contract.** Downstream stages grep it. Keep its shape
  stable and its numbers honest.
- **Right-sizing applies to your own output.** A plan heavier than the work is the
  failure this skill exists to prevent.
- **Detect the plan location; don't standardize it.** Two repos with a plans folder
  each still disagree on its path. Follow what is there.
- **Delegated code reading is cheaper than reading the repo yourself, but only with
  citations.** A finding without a repository-relative full path and a line number is
  not a finding; a basename matches four files in most repos and sends the executor to
  the wrong one.

## Reference files

- `references/plan-template.md` — the plan document skeleton, the slice/task block,
  and the LITE variant.
