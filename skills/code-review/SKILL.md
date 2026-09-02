---
name: code-review
description: Use when a finished change needs an independent read before it is integrated — a diff, branch, lane, or PR judged against the plan and spec it was built from. Triggers - "review this diff", "review the branch before I merge", "check this change against the plan", the stage between a green gate and integration, reviewing a parallel lane's work before the merged tree, or hunting tests that cannot fail, leftover scaffolding, and byte-level corruption no gate can see.
allowed-tools: Read, Glob, Grep, Bash, Agent, Write
---

# Code Review

Independent, fresh-context review of **written code** — a pinned diff range against the
plan and spec it came from — before it is integrated. It produces severity-tagged,
anchored findings and an `APPROVE` / `REVISE` verdict, from an agent that did not write
the change.

## Core principle

**A green gate is evidence that the gate ran, not that the change is correct.** The
defect classes that reach integration are the ones gates are structurally blind to: a
test whose assertion cannot fail, a mock that replaced the subject it was meant to
observe, a byte no compiler renders, styling that lints clean and does nothing on
screen. Field record: every independent review of a green, gate-passing change found
real defects the gates missed — six for six in one series, eight for eight in the next;
one subagent's "clean verify" hid two real issues an independent re-run found.

The author cannot perform this review. Not for lack of skill — it holds the reasoning
that produced the code, so it reads its own intent into the lines and its own verify run
as proof. The review is therefore **dispatched to a fresh agent that receives the
artifact and none of the story**.

## When to use

- A change is complete and its gate is green, before merge or integration.
- A lane or task in a parallel build finishes, before the merged-tree gate.
- A diff arrives from another agent or session and must be judged on its own.

## When NOT to use — triage first

| Tier | When | What runs |
|---|---|---|
| **SKIP** | Non-behavioral: formatting-only, comment or prose text, a lockfile refresh, a regenerated artifact, a straight revert of an already-reviewed commit | Integrity scan only (Step 1); the skip and its reason recorded |
| **FULL** | Everything else — any behavior, test, build-config, dependency, or security-surface change | The whole pipeline |

There is no middle tier: a diff is either behavior-free or reviewed, and when it is
arguable, review it — misjudging a "formatting-only" diff is exactly how an invisible
byte lands. **Never skip for queue depth, elapsed time, a green gate, or a trusted
author.** Nor is review a repo-wide quality sweep; scope is the diff and what it touches.

## Hard rules

- **The reviewer is never the author** and never the agent that dispatched the build. It
  runs in a fresh context, on the judgment tier, never lower.
- **Neither the reviewer nor the dispatcher reads the author's narration** — not its
  report, not its verify transcript, not its rationale for why the change is correct —
  until the verdict is locked at the end of Step 3. The reviewer gets the diff range, the
  plan, the spec, and read-only tree access. The dispatcher judges severity, and reading
  the story first biases that judgment exactly the way it biases the review. A commit
  message that asserts correctness is a claim to check, not evidence.
- **Read-only.** The reviewer reports findings and fix directions; it never edits, never
  "just fixes" what it found, and never runs the gate to re-green anything.
- **Every finding carries a concrete anchor** — `path:line` inside the diff, a tree fact
  the reviewer verified itself, or, for a finding about something *absent*, the
  requirement it fails: `spec:AC-<n>` or `plan:<step>`. Unanchored advice ("add tests",
  "consider performance", "improve error handling") is dropped before the count.
- **Any `blocker` ⇒ `REVISE`.** No trading a blocker down to make the verdict come out.
- **Do not trust the diff's self-description.** A comment, a test name, or a doc line
  claiming behavior is a hypothesis; check it against the code and the tree.
- **A consistency claim requires a full search, not spot checks.** A negative claim
  ("nothing else uses this") requires a recursive search including ignored and hidden
  directories. Deleting as dead requires proving zero consumers through indirection.
- **Settled decisions travel forward and are never re-litigated.** A review that finds a
  decision from the spec or plan genuinely broken says so and re-locks it with the user
  (unattended: records a `Decisions Needed` item). It never silently redesigns.

## Step 0 — Triage and pin the range

Classify SKIP or FULL out loud with a one-line reason. Then pin the range by commit SHA
(`base..head`), not by branch name — a branch moves under a concurrent rebase and the
review then describes code nobody has. Uncommitted work is not reviewable; commit it
first. Record the range in the output.

## Step 1 — Assemble the packet and run the integrity scan

The packet is exactly four things: the pinned range, the plan, the spec, and read-only
tree access. If the plan or spec does not exist, say so — the reviewer scores those
dimensions `not-assessable` rather than inventing a standard.

Then run the **integrity scan** yourself before dispatch, mechanically over every added
or changed file: NUL bytes, a byte-order mark, mixed or flipped line endings, stray
control characters, non-UTF-8 sequences, and any file the diff shows as wholly rewritten
when only a few lines changed. This is the one defect class no gate catches — a literal
NUL byte in a source file passed the full gate twice in one project, and a BOM written by
a build lane was invisible to every check. It is mechanical and repeats every review, so
it belongs in a script that takes the range as an argument: `references/integrity-scan.md`
is that script, with the byte-level detections that actually work (a line-oriented search
for a NUL byte reports zero and bails on the file — it is the trap this class hides
behind). Hand the result to the reviewer as a fact, not as a task.

## Step 2 — Dispatch the fresh reviewer

Dispatch one fresh subagent with read-only tools over the tree, using the brief in
`references/reviewer-brief.md` verbatim with its slots filled. Change the rubric, the
finding format, and the verdict rule for nothing.

When the diff is too large for one reviewer to hold, split it by file group — never by
lowering the bar to fit one pass — dispatch one reviewer per group in a single message,
then merge the findings and dedupe by anchor. Do not pre-read the diff to "narrow" what
the reviewer looks at; pre-filtering reintroduces the bias the dispatch removes.

## Step 3 — Judge the findings and emit the verdict

Drop every finding with no concrete anchor before counting; a dropped finding never
produces a blocker. Do not re-grade severity to change the outcome. If you believe a
blocker is wrong, that disagreement goes through Step 4 with evidence — it does not
become an edit to the reviewer's report.

`REVISE` if any finding is a `blocker`; otherwise `APPROVE`, with `should-fix` and `nit`
items carried forward to the author. In a pipeline the verdict routes: `REVISE` returns
the diff to its author with the blocker list, `APPROVE` hands to the next stage.
Interactively the user may override a blocker; the override and its reason are recorded
with the change. End the review with this block:

```
REVIEW: APPROVE|REVISE
BLOCKERS: <n>
FINDINGS: <n>   # each: severity, file:line, what, why it matters, what would fix it
```

## Step 4 — The author receives the review

1. **Reproduce before acting.** Open the cited anchor and confirm the claim. A finding
   you have not reproduced is actionable neither to fix nor to dismiss.
2. **Disagree with evidence, not assertion.** Cite the command and its output, or the
   line that disproves the finding. "That is intentional" and "that is out of scope" are
   assertions.
3. **No performative agreement.** Do not restate the finding approvingly, and never
   accept a finding and then make a change that does not address it — that reads as
   compliance and ships the defect.
4. **Unclear findings stop the batch.** Findings are frequently related; implementing the
   understood half produces a wrong change. Ask, or re-dispatch for clarification.
5. **One finding at a time, each verified.** For a behavior fix, show the failure before
   the fix, then confirm it goes green.
6. **A fix is a change like any other.** It obeys the deviation rule, and it never
   weakens, narrows, mocks out, skips, or deletes a test or a gate to clear a finding.
   Gates are development discipline, not production-only; a gamed gate is a failed task.

## Step 5 — Re-review

Re-dispatch a **fresh** reviewer on the new range, carrying the original blocker list —
never the author's account of what it fixed. An author clearing its own blocker is not
clearance. Repeat until no blockers remain. If the same blocker survives two rounds, stop
and escalate: it is a decision problem, not a code problem.

## The rubric

Every dimension is marked `clear`, `findings`, or `not-assessable` (with a one-line
reason) — a dimension is never silently skipped because the diff "looks fine".

| # | Dimension | A finding looks like |
|---|---|---|
| 1 | Plan fidelity | A changed file absent from the plan's file map; a planned file untouched; a signature that drifted from the contract the plan fixed |
| 2 | Spec acceptance coverage | An acceptance criterion with no code path that satisfies it, or satisfied but with no test that would fail if it broke |
| 3 | Tests that cannot fail | An empty catch swallowing the assertion; a string compared to itself; a selector, matcher, or fixture that matches nothing in the product; an asserted property the element can never take |
| 4 | Mock replaces the subject | The double stands in for the thing under test, so the suite is blind — 190 tests once passed against a mock that had replaced the function they existed to cover |
| 5 | Byte and encoding integrity | A NUL byte, a BOM, mixed EOLs, a stray control character, a file rewritten wholesale by an EOL flip |
| 6 | Placement and naming | A file that does not sit where its siblings sit; a name describing transient state rather than the role it fills; a second top-level location for an existing concern |
| 7 | Dead code and scaffolding | Debug logging, commented-out blocks, an option nothing passes, a branch nothing reaches, an export nothing imports, a fixture left from development |
| 8 | Evidence for claims | A "the last remaining caller", "used everywhere", or "nothing depends on this" claim the diff acts on without a full recursive search behind it |
| 9 | Security-sensitive surface | Input crossing a trust boundary without validation; a secret, token, or personal datum in source, a log line, or a fixture; an authorization check moved, widened, or removed; unsafe dynamic execution or deserialization |
| 10 | The deviation rule | A shim or adapter around code that should have changed; a second copy because the original "did not quite fit"; a special case for one caller; a type widened to make a mismatch compile; a fallback or catch-and-default that exists because the primary path was not fixed |

Deleted lines are part of the diff. A removed assertion, a dropped validation, or a
deleted test case is a finding as much as anything added.

## Severity and finding format

- `blocker` — wrong behavior, a defect the gate cannot catch, a security-surface
  regression, a plan or spec breach, or a test that cannot fail. Forces `REVISE`.
- `should-fix` — real but non-blocking: dead scaffolding, a weak assertion that still
  can fail, a naming or consistency defect, a file sitting oddly among its siblings.
- `nit` — preference. Cheap to state, never a reason to hold a change.

**Plan fidelity is graded precisely, because placement is a contract.** An unplanned
*file*, and any unplanned touch on shared or foundational code or on a file another
group owns, is a `blocker` — the plan's file map is what makes parallel lanes safe, so
a file outside it is a breach whether or not the code is good. An unplanned but
non-behavioral edit *inside* a file the plan does name is `should-fix`. Any `blocker`
still means `REVISE`.

```
[blocker] src/sync/reconcile.ts:118 — the retry path re-enters reconcile() with the
          same cursor, so a failed page repeats indefinitely.
          Why it matters: spec AC-4 requires a second reconcile to be a no-op; this
          loops instead. No test covers a second pass, so the gate stays green.
          Fix direction: advance the cursor before the retry, and add a test asserting
          the second reconcile issues zero writes.
```

A finding about something **absent** has no line to point at, so it anchors to the
requirement it fails — `spec:AC-<n>` or `plan:<step>`: `[blocker] spec:AC-7 — no code
path satisfies "the second reconcile is a no-op"; nothing in the range reads the stored
cursor.` That is a concrete anchor and counts; "add tests" still does not.

## Running unattended

Never ask; never block. An unclear finding is recorded as an open item at the safest
reading rather than guessed at. A blocker that cannot be fixed without reopening a
settled decision becomes a `Decisions Needed` entry and the change is quarantined — not
adapted around. If the reviewer dispatch fails or returns nothing usable, the verdict is
`REVISE` with the failure recorded; a review that did not happen never becomes an
`APPROVE` by default. Append one to three tagged bullets to the run's learnings file for
whatever this review taught about the process. **If the run has no learnings file, create
one at the project's convention rather than dropping the bullets**; if there is no run
directory at all, emit the bullets inline in the output and say that is why.

## Common mistakes

- **Reviewing your own diff inline** because you already have the context. That context
  is the defect the skill exists to remove.
- **Passing the build report in.** Handing the reviewer "here is what I did and why it is
  correct" converts the review into a proofread of a summary.
- **Letting the green gate stand for the review**, or skipping the review because the
  change is small and the suite passed.
- **Unanchored findings.** "Consider performance" helps nobody and inflates the count.
- **Severity theatre** — promoting nits to look thorough, or demoting a blocker to keep a
  lane moving. Both corrupt the verdict.
- **Fixing without reproducing**, then reporting fixed. The fix lands somewhere plausible
  and the finding survives.
- **Re-reviewing in the author's context** after fixes, which is where a self-cleared
  blocker gets ratified.

## Gotchas

- **The reviewer will wander** if given tree access and no boundary. Scope is the diff
  and what it directly touches; the tree is for verifying claims, not for auditing.
- **Complete against the plan and wrong against the spec** is a real state, and so is the
  reverse. Both dimensions are scored, always.
- **Concurrency corrupts evidence.** A gate run under concurrent load fabricates
  failures; a reviewer must not treat one as a finding without reproducing it quietly.
- **The integrity scan is the cheapest dimension and the only one nothing else covers.**
  It is also the easiest to quietly drop once it has been clean a few times.
- **A finding the author cannot reproduce is not automatically wrong.** It may depend on
  state the author's environment hides; resolve it with evidence from both sides.

## Reference files

- `references/reviewer-brief.md` — the reviewer prompt, its slots, and what must never be
  pasted into them.
- `references/integrity-scan.md` — the byte-level scan as a script taking base and head,
  and why the obvious one-liners miss what it catches.
