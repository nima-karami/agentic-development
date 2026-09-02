# Implementation plan template

Fill this in, scaled to the tier. Delete a section that genuinely doesn't apply and
say why in one line rather than leaving it blank. **Add no header, banner, or
"required sub-skill" line** — the plan file carries only its own content.

## FULL

````markdown
# <Feature name> — implementation plan

**Spec:** <relative path to the spec this implements>  **Tier:** FULL

## Goal
<one sentence — what this builds>

## Architecture
<2–3 sentences: the approach and why. Name the sketch directory if sketches were made.>

## Data flow
<ASCII diagram, or numbered hops end to end: who owns what, where state lives, what
crosses each seam. Draw it whenever the flow has more than three hops.>

## Settled decisions — do not re-litigate
<one line each, carried from the spec and from the level-locking conversation>

## Spec staleness        <!-- delete when every spec claim measured true -->
<one line per spec claim that grounding measured false — a retired route, a deleted
component, a field that never existed: what the spec claims, what was measured (path
and line), and how this plan proceeds instead. Planning silently around a stale claim
hides it from everyone downstream.>

## Global constraints
<one line each, exact values; every task implicitly includes these: the gate command;
version floors; the repo conventions the executor must follow, copied concretely from
the style authority — file/folder naming and role suffixes, type/function/constant
naming, comment policy, import and boundary rules. A weaker executor does not infer
conventions; this section is where they arrive.>

## Out of scope
<what this plan deliberately does not touch>

## Contracts
<exact signatures of the public seams with real types; error shapes; invariants;
validation at each trust boundary. No "TBD", no "similar to", no "appropriate error
handling".>

## Producer/consumer map
| Behavior changed | Produced by | Consumed by | Sides this plan touches |
|---|---|---|---|
| | | | |

<For any row where the plan touches one side only: one line stating why the other
side is unaffected — measured, not assumed.>

## File map
| Path | Action | Responsibility |
|---|---|---|
| `exact/path` | create / modify / delete | <one line> |

## Scripts
<mechanical routines the build should script rather than repeat by hand: the script
path, its arguments, what it replaces. State "none" deliberately if there are none.>

## Slices
<one block per slice — see the slice block below>

## Verification
<the gate rhythm, concretely: what runs per task, what runs per slice, what runs on
the merged tree. Exit codes are captured directly, never through a pipe or pager.>

## Deviation rule
If a task's assumption turns out wrong — the piece it builds on is misaligned, a
locked signature doesn't fit reality — that task **stops** and fixing the misaligned
piece becomes the work. Never a shim, second copy, special case, widened type,
fallback, or an override patched in place of its semantic source. Report leads with
the fix that keeps the locked decision.

## Decisions Needed        <!-- autonomous mode; delete when empty -->
- [high|normal] <question that materially changes the build> — default taken: <x>
````

### Slice block

````markdown
### Slice N: <name>

**Check:** <the exact test, command, or observable flow that proves this slice —
runnable on its own against the state these tasks leave behind>

**Parallel groups:** G1: T1, T3 · G2: T2 · Serial: T4
**Claims (serial lane):** `exact/shared/entry/file`

#### Task N.1: <name>        <!-- ~10 minutes: one deliverable, one executor -->

**Files:**
- Create: `exact/path/file.<ext>`
- Modify: `exact/path/existing.<ext>` (<which part>)
- Test: `exact/path/file.test.<ext>`

**Interfaces:**
- Produces: <exact signatures later tasks rely on>
- Consumes: <exact signatures from earlier tasks — an executor sees only its own
  task plus these, so names and types must be repeated here, not cross-referenced>

**Call sites:** <every existing caller of a signature this task changes>

**Steps:**
- [ ] Failing test: '<behavior, in the test's own name>' — key assertion:
      `<observable> == <expected>`
- [ ] Run `<the test command>` — expect FAIL (<why: module missing / behavior absent>)
- [ ] Implement the minimum to pass, within the signatures above
````

**A slice is the smallest group of tasks that reaches its check** — sometimes one
task, sometimes four. Size the tasks by the clock and the slice by the check; a group
with no check of its own is a milestone, and gets split until each piece has one.

**Test-first is the default step shape** — a test never watched failing proves
nothing. Two carve-outs, named per task, never assumed:

- **Port/vendoring tasks** (existing code moving) — the proof is byte-identical
  vendoring or the existing suite staying green, not a new failing test.
- **Visual-fidelity tasks** (ported or restyled user-facing surfaces) — the proof is
  a side-by-side against the reference, with the baseline captured in an **earlier**
  step than the one that removes the original. Green unit tests have shipped a
  visually destroyed screen; the plan schedules the looking.

## LITE

Same file, these sections only: **Goal**, **Settled decisions**, **Global
constraints**, **Contracts** (only for seams crossing a module boundary), **File
map**, **Producer/consumer map**, 1–3 **Slices** with their checks, **Verification**,
**Deviation rule**. No architecture section, no data-flow diagram, no sketches, no
parallel groups, no scripts section unless there is a real candidate.

## SKIP

No file. Inline, in the reply: the file map (3–6 lines), the verification command,
the deviation rule, and one line recording the skip and its reason.

One exemption: when the skip reason is **already built**, the evidence of
implementation replaces the file map — the commits that built it, plus any spec detail
deliberately reversed or superseded downstream. The verification command and the
deviation rule are still owed.
