---
name: runtime-qa
description: Use when a change to user-facing behavior has to be proven by driving the real running artifact — a browser app, CLI, HTTP API, desktop/packaged app, or mobile build — instead of by unit output. Triggers - "does it actually work", "QA this", "smoke test it before the PR", "verify it against the running app", "prove it renders", reproducing a reported defect, checking acceptance criteria against a build, green tests but a blank screen or a dead button.
allowed-tools: Read, Glob, Grep, Bash, Write, Agent, WebSearch
---

# Runtime QA

Drive the real artifact through the spec's user-facing acceptance criteria and report
only what was observed.

## Core principle

Unit gates assert on internals. They are structurally blind to the defect class that
dominates real runs: the artifact builds, lints, typechecks, passes its suite, and
does the wrong thing — or nothing — in front of a user. Three lanes once shipped CSS
that passed lint, typecheck and ~2500 tests and did nothing on screen. This stage is
the only gate that catches that, and it is mandatory for any change to user-facing
behavior. **A green unit gate is not a substitute.**

The output is a report a human can act on without re-running anything, plus a
machine-parseable handoff block. A pass that was not observed is never reported.

## When to use

- A change to user-facing behavior is finished and needs proof before review, merge,
  or a done-claim.
- A spec's acceptance criteria need checking against a running build.
- A reported defect needs reproducing, or a fix needs confirming, in the real thing.
- A build looks green but a surface is suspected of being blank, dead, or wrong.

## When NOT to use

- The change has no observable surface (build config, docs, an internal refactor with
  no behavior delta). Record the skip and its reason; never stage a theatre pass.
- Authoring the harness the project lacks — that is a separate concern. This stage
  drives what exists and reports its absence as a finding.
- Exhaustive regression authoring. This is an observation pass, not a test suite.

## Hard rules

- **Never report a pass you did not observe.** A blocked step is reported as blocked,
  and by what. Half a flow honestly reported is useful; a full flow claimed on
  inference is not.
- **Never fake a pass from unit output.** When the artifact has no way to be observed,
  say so and stop.
- **A claim about current behavior requires measurement, not inference from source.**
  Reading the diff and concluding it works is not a QA pass.
- **State the build under test.** Repo, path, branch, short sha, for every repo whose
  build matters — and confirm it from the running artifact, not only from the tree. A
  report against the wrong build is worse than no report.
- **Always state what wasn't covered**, and why. A report silent on its gaps reads as
  a clean bill of health, and that is how a QA pass does damage.
- **Close what you opened.** Every process, browser session, emulator, temp dir, and
  override you created is torn down at the end, by handle or pid — never by killing
  processes by image name (one teardown by image name closed the user's real browser).
- **Never weaken, narrow, mock out, skip, or defer a gate to get green.** Gates are
  development discipline, not production-only. A gamed gate is a failed task. That
  includes loosening a scenario until it passes.
- **Concurrency hygiene.** Never run the full gate under concurrent subagent load, and
  never share a temp or browser-profile directory across sessions. Verify a worktree's
  base commit before building on it; never install dependencies in a directory you have
  not verified is the intended one.
- **Settled decisions travel forward and are never re-litigated.** A criterion found
  genuinely unbuildable (a spec asserted behavior on relaunch that nothing could ever
  write) is reported as a finding and re-locked with the user — or, unattended,
  recorded as a `Decisions Needed` item. Never silently adapt the criterion to what
  the build happens to do.
- **Capture as you go, not afterwards.** You cannot go back for the screenshot of a
  state you have navigated away from.
- **When a routine repeats — the same launch/teardown twice, the same driving call
  more than a handful of times — write a script that takes arguments and run it.**
  Durable scripts go in the project's scripts directory; one-offs to the OS temp dir.

## Step 0 — Triage and scope

Declare a tier and a one-line scope before driving anything. A pass aimed at the
wrong flow is worse than none, because the report reads as coverage.

| Tier | When | What you drive |
|---|---|---|
| **SKIP** | No observable surface changed | Nothing. Record the skip and the reason. |
| **LITE** | One surface, one flow, single configuration | The changed flow, one negative, evidence per criterion. |
| **FULL** | Multi-surface, persistence/migration involved, a variant matrix (theme, locale, role, viewport, platform), or a defect being reproduced | Full scenario set, every variant the change ships to, the relaunch scenario, visual baseline comparison. |

If the change touches anything brand-, theme-, locale-, or role-varied, **every
variant it ships to is in scope**, named in the scope line. Fixing one configuration
while the others stay broken is a repeat failure — one happened to satisfy an
assumption the rest didn't.

## Step 1 — Identify the build under test

Before anything launches:

- Resolve which checkout/worktree holds the change, and record repo, path, branch and
  short sha for each repo whose build matters. Verify a worktree's base commit — a
  worktree cut from a stale commit produces a report about code nobody shipped.
- Confirm the artifact was built from that sha, then confirm the *running* artifact's
  identity — version banner, build stamp, served asset hash. **A leftover process
  listening on the port once produced a false pass on a build never launched.**
- Note anything uncommitted — uncommitted work is not the build under test.

## Step 2 — Find the launch path and the project's test affordance

Read the project's own documentation for how the artifact comes up — run/dev-loop doc,
instruction file, scripts directory, CI config. Never reconstruct the launch from
memory or a guessed convention: ports, start order, required local config files and
their silent-failure modes are exactly what that doc owns.

Then look for a **documented test affordance**: a control handle or debug global the
app installs, a diagnostics flag, a structured log buffer, a test/seed API, a
subcommand that emits machine-readable state, fixture entry points. Where one exists,
prefer it to clicking — it drives the app semantically, reaches states the UI has no
button for, and separates "the system can do this" from "the UI can ask for it".

**If none is documented, do not invent one, and do not assume one exists.** Record
"no documented test affordance" as a finding for the project, and drive the user
surface instead.

## Step 3 — Isolate the session

Every run gets its own: port (or port block), user-data/profile directory, temp
directory, and data store. Derive them per session; never reuse a fixed default and
never share a profile or temp dir across sessions.

- A hardcoded port with reuse-an-existing-server behavior meant **six parallel lanes
  could not run end-to-end at all** — each would have served another lane's code.
- Before binding, check the port is actually free; if something is already listening,
  find out what it is rather than reusing it.
- Record the ports and paths used in the report — a reader retracing your steps needs
  the same URLs.
- **A process you did not start is not yours.** Read-probe it for identity — version
  banner, state or health endpoint, what it is serving — and never mutate it: no
  restart, no stop, no config change, no data write. It may be the user's own work.

Driving is executor work: dispatch it one tier below the session for judgment-heavy
passes, two below for mechanical repetition, floor at the mid tier. The bottom tier
never drives a slow or flaky harness and never writes a root-cause diagnosis.

## Step 4 — Derive the scenarios

One scenario per user-facing acceptance criterion, in the order a user would hit
them. Then add, always:

1. **A negative scenario.** The bad input, the denied permission, the empty state, the
   failure path — the criterion's inverse. Most "it works" reports only ever drove the
   happy path.
2. **A restart/relaunch scenario.** Stop the artifact, start it again, verify the
   state that was supposed to survive. Specs routinely assert behavior on relaunch
   that in-process tests can never observe, and at least one such criterion turned out
   to have nothing that could ever write the state it read.
3. **A negative control for any scenario that passes suspiciously easily.** Make the
   asserted thing false — break the selector's target, remove the data, point at a
   state where it must fail — and confirm it reports a failure. A passing assertion
   and an absent one look identical in a summary; two end-to-end sections once passed
   no matter what, one targeting an element that existed nowhere in the product.

Criteria you cannot reach (needs a backend you don't have, a real device, a signed-in
account) are not silently dropped — they go to **Not covered** with the blocker named.

## Step 5 — Drive, capturing evidence as you go

Match the driving approach to the artifact type (rubric below). While driving:

- **Screenshot/record into the run's evidence directory as each state happens**,
  numbered in the order they occurred so the report reads as a sequence.
- **Read the artifact's own logs at every step**, filtered to what you are exercising,
  and save the lines that back each finding. Errors that never reach the screen live
  there. Read debug-level output deliberately — many capture paths filter it out, and
  some failures are only visible there.
- **Inspect what you captured.** A screenshot taken is not a screenshot read: one run
  produced a wrong graph in every canvas capture, lane after lane, because nobody
  compared the image to the criterion in words. State, per criterion, the expectation
  and what the evidence shows. A recording earns its place for motion, timing, or a
  sequence; a still is better for anything static.
- Root-cause when it is cheap — searching for the log line you saw often turns "the
  screen is blank" into a one-line fix. Say plainly when you did not find the cause; a
  guess dressed as a cause costs the next person more than silence.

## Step 6 — Visual and design fidelity

Behavior checks never prove looks. Where the change touches appearance, layout, or a
rebuilt/ported surface:

- **Capture the baseline first — before the change is applied or from the pre-change
  build** — and compare side by side. A parity check without a baseline is an opinion.
  One port shipped visually wrong because its reference was deleted in the same commit
  that replaced it, leaving nothing to compare against.
- Where the reference is a design source rather than a previous build, say which.
- Check the states assertions don't reach: hover/focus/active, disabled, loading,
  empty, error, long text, smallest and largest supported viewport.
- If no baseline can be obtained, say so and mark the fidelity check **not covered**
  rather than issuing a verdict on it.

## Step 7 — Write the report and emit the handoff

Fill `references/report-template.md` and write it to the run's report path (follow the
project's run-artifact convention; never drop a stray file at the repo root).

**`QA:` is a filesystem path, always.** If the write fails — a blocked tool, a
read-only path, a directory that does not exist — write the report to another writable
path inside the run directory (a shell heredoc when the editing capability is the thing
that is blocked) and name *that* path in the slot. Prose in the slot ("see above", "not
written") breaks every stage that greps it; a report that exists nowhere on disk is a
report that did not happen.

Then end your output with exactly this block:

```
QA: <report path>
BUILD_UNDER_TEST: <repo> <branch>@<sha>
VERDICT: pass|fail|partial
NOT_COVERED: <list or "none">
```

`pass` = every in-scope criterion observed working. **An observed failure outranks
incomplete coverage:** `fail` whenever anything in scope was observed broken, however
much else went unreached. `partial` only when nothing in scope was observed broken and
something was unreached, blocked, or unobservable — the no-harness case included.
Severity is about the user, not the code. Every finding carries a repro from a stated
starting state, and evidence by path.

## Step 8 — Close what you opened

Stop recordings, close driver sessions by their handle, terminate the processes you
started by pid, clear any overrides you set (or the next session inherits them and
chases a ghost), and remove your temp/profile directories — only yours. The report's
header states that teardown ran. An open session outlives the run, and its working
directory can block deleting the run folder.

Then append one to three learnings bullets to the run's learnings file, each tagged
with where its fix belongs: `[<skill-name>]`, `[<doc path>]`, `[instruction-file]`,
`[memory]`, or `[none]`. Process observations only; product defects go in the report.
If that write fails too, fall back the same way the report does — another writable path
inside the run directory, named as a path.

## No harness, no launch path, no way to observe

If the artifact cannot be launched, or cannot be observed once launched:

1. Say so explicitly and stop driving. Do not substitute unit output, do not narrate
   the source as if it were behavior, do not infer a pass.
2. Report what blocked it: no launch path, no affordance, a missing local config, a
   backend that exists only when deployed, no device.
3. Emit `VERDICT: partial` with every criterion under `NOT_COVERED`, and a Verdict
   line of `Blocked: <reason>`.
4. Name the missing capability as a finding for the project, so it can be fixed once
   rather than re-discovered every run.

## Rubric — artifact type → how you drive it

| Artifact | Launch | Driving approach | Evidence |
|---|---|---|---|
| **Browser app** | Dev server or built bundle on an isolated port, isolated browser profile | Browser-automation capability: navigate, interact, evaluate in the page, read the console; prefer the app's control affordance over clicking | Numbered screenshots, console log, recording/trace when timing matters |
| **CLI / script** | Invoke the built entry point in a temp working directory | Real invocations with real arguments, including the failure paths | Captured stdout+stderr, exit codes, listing/diff of files produced |
| **HTTP API / service** | Start on an isolated port with an isolated data store | Real requests over the wire, not in-process handler calls | Request/response transcript with status codes and headers |
| **Desktop / packaged app** | Launch the packaged or dev build with an isolated user-data directory | Desktop-capable automation driver, or the app's own control affordance | Window screenshots, main and renderer logs |
| **Mobile** | Install the build on a simulator/emulator or device | Device automation driver | Screen captures or recording, device log |
| **Library (no runnable artifact)** | None | Exercise the public API from a fresh consumer script outside the repo's own suite | The script and its real output |

## Rubric — what unit gates are blind to, and the runtime check that catches it

| Defect class | Why the gate misses it | Runtime check |
|---|---|---|
| **Dead styling** — a rule overridden, hover doing nothing, a token that resolves to nothing | Lint/typecheck/unit assert on structure and text, never on rendered pixels | Drive the surface; capture before and after the interaction and compare the two images |
| **Wrong content on screen** — right component, wrong data or wrong chart | Assertions check that it rendered, not what it rendered | Read each capture against the criterion in words before recording a pass |
| **Silent data loss** — the write no-ops, the record never persists | The boundary that loses the data is the boundary that was mocked | Perform the action in the real artifact, relaunch it, re-read the data |
| **Scenarios that cannot fail** — empty catch swallowing a timeout, a selector matching nothing, a value compared to itself | A passing assertion and an absent one look identical in the summary | Negative control: make the asserted thing false and confirm a failure is reported |
| **Byte-level corruption** — a NUL byte, a BOM, mixed line endings | Compilers and suites tolerate it; it surfaces at load or parse time | Launch the built artifact and exercise the path that loads the affected file |
| **Stale build under test** — a leftover process serving the previous build | Output is byte-identical to a real pass | Verify build identity from the running artifact, not from the repo |
| **Restart-only behavior** — persistence, migration, first-run | In-process tests never terminate the process | The relaunch scenario |
| **Cross-variant breakage** — a theme, locale, role, or viewport the change never considered | Suites run one configuration | Drive every variant the change ships to; name each in coverage |

## Unattended runs

Never ask, never block, never halt. A would-be question becomes the most conservative
assumption, recorded in the report. A criterion that cannot be satisfied as written
becomes a severity-tagged `Decisions Needed` entry — not a halt, and not a criterion
quietly restated as whatever the build did. Drop the tier before dropping honesty, and
let the handoff block carry the flags.

## Common mistakes

- **Reporting a pass from green unit output.** The failure this stage exists to
  prevent. Drive it or report it uncovered.
- **Not naming the build.** A precise report against an unknown or stale build is
  noise, and reusing whatever was already on the port manufactures a false pass.
- **Driving only the happy path.** No negative, no restart, no variant, then "covered".
- **Capturing evidence nobody reads.** Screenshots filed without comparing them to the
  criterion let the wrong output ship, run after run.
- **Silence about gaps.** Omitting what you couldn't reach turns a partial pass into
  an implied clean bill of health.
- **Adapting the criterion to the build.** When a criterion is unbuildable, that is
  the finding — not a reason to quietly restate the criterion as what you observed.
- **Leaving the session open, or killing by image name.** One closes nothing, the
  other closes the user's real browser.
- **Padding a LITE pass into a FULL matrix.** Over-production is a defect too.

## Gotchas

- **Path-reference every claim.** A finding whose only evidence is "I saw it" costs
  the next person a full reproduction.
- **A screenshot proves what was on screen, not that it was right.** Only the
  side-by-side against a baseline settles appearance.
- **The handoff block is a contract** downstream stages grep. Keep its shape stable,
  and never emit `pass` with a non-empty blocker.
- **An environment fault is still worth reporting**, named as such — and added to the
  project's failure-signature table, which only stays useful if passes feed it.

## Reference files

- `references/report-template.md` — the report shape to fill.
- `references/tooling.md` — drivers, capture and isolation tooling, tier names.
  Confirm the picks are current before relying on them.
