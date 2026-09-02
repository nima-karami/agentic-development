# Runtime QA report template

Fill and write to the run's report path (follow the project's run-artifact
convention — e.g. a per-run directory — rather than dropping a file at the repo
root). Evidence lives beside it in `evidence/`. Delete any section that genuinely
does not apply rather than writing "N/A"; **never** delete **Not covered**.

---

# Runtime QA · <what was tested>

**When:** <date>
**Tier:** SKIP | LITE | FULL — <one-line reason>
**Artifact:** browser app | CLI | HTTP API | desktop/packaged app | mobile | library
**Build under test:** <repo> at <path> `<branch>` @ `<short sha>` <+ any other repo whose build matters>
**Build identity confirmed from the running artifact:** <version banner / build stamp / asset hash / "not available — how it was confirmed instead">
**Environment:** <how it was launched: local dev servers, packaged build, emulator, preview URL> — <ports / URLs used>
**Isolation:** port(s) <n>, profile/user-data dir <path>, temp dir <path>, data store <path or "in-memory">
**Configurations driven:** <viewport / device / theme / locale / role / platform — every variant in scope, each marked driven or not>
**Teardown:** processes stopped, sessions closed, overrides cleared, temp dirs removed — <yes / what remains and why>

## Scope

One paragraph: the change or flow under test, where the acceptance criteria came
from, and why this pass was run. Name the variants in scope.

## Verdict

One line a reader can act on:
`Clean` · `Works, with <n> issues` · `Blocked at <step>` · `Blocked: <reason>`

## Criteria

One row per user-facing acceptance criterion. "Observed" means you saw it happen in
the running artifact, with evidence.

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | <criterion, as written in the spec> | observed pass / observed fail / not reached | `evidence/01-<name>.png` |

Criteria not reached are repeated in **Not covered** with the blocker.

## What happened

The path taken, in order, with evidence attached — the sequence a reader retraces,
not a transcript.

1. <step> — <result> · `evidence/01-<name>.png`
2. <step> — <result> · `evidence/02-<name>.png`

**Negative scenario:** <what was tried, what the artifact did>
**Relaunch scenario:** <what was stopped and restarted, what survived, what did not>
**Negative controls:** <which scenarios were deliberately made to fail, and that they did report a failure>

## Findings

Worst first. Drop the section entirely if there were none.

### 1. <what a user experiences, not what the code does>

**Severity:** blocks the flow · degrades it · cosmetic · latent (no user impact yet)
**Affects:** <which variants/configurations — and which were confirmed unaffected>
**Evidence:** `evidence/03-<name>.png` · `evidence/console.log` L<n>–<m> · `evidence/session.<ext>` @ <marker>

Repro, from a stated clean starting state:
1. <step>
2. <step>

Expected <x>, observed <y>.

**Cause (if found):** `<file>:<line>` — <the mechanism, one or two sentences>. Say
plainly if you did not find it; a guess dressed as a cause costs the next person more
than silence.

## Visual / design fidelity

Only when appearance was in scope.

**Baseline:** <pre-change build @ sha / design source / "none obtainable — fidelity not covered">
**Comparison:** `evidence/baseline-<name>.png` vs `evidence/after-<name>.png`
**States checked:** default, hover, focus, active, disabled, loading, empty, error,
long text, smallest and largest supported viewport — <which were checked>
**Result:** <matches / differs: what, where>

## What worked

Briefly, so the report shows coverage rather than only failures — and so a later
regression here is visibly a regression.

## Not covered

The gaps and why: blocked by a finding above, needs a backend not available locally,
needs a device or a real account, out of scope, no test affordance. A report silent
on its gaps reads as a clean bill of health.

## Environment faults

Symptoms that turned out to be the environment rather than the build, named as such.
If the project keeps a failure-signature table, add any new signature to it.

## Decisions needed

Criteria that could not be satisfied as written (unbuildable, contradicted by the
build, ambiguous) — severity-tagged `high`/`normal`. Never silently restate a
criterion as what was observed.

## Artifacts

- `evidence/` — <count> captures, numbered in the order they happened
- `evidence/console.log` — <what it holds>
- `evidence/session.<ext>` — <duration>, markers: <list> *(omit if not recorded)*
- <trace / har / stdout transcript / response log, as captured>

---

```
QA: <report path>
BUILD_UNDER_TEST: <repo> <branch>@<sha>
VERDICT: pass|fail|partial
NOT_COVERED: <list or "none">
```
