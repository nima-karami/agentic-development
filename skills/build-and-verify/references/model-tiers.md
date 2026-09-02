# Model tiers for dispatch

The session holds decisions. Judgment-heavy delegated work runs one tier below the
session; mechanical work two tiers below, with a floor at the mid tier; never
delegate upward. The bottom tier never builds against slow or flaky suites and never
writes a root-cause diagnosis.

| Tier | Models | Use |
|---|---|---|
| top | Fable | session/conductor judgment only; never product code, never content generation |
| high | Opus | judgment work: specs, plans, reviews, builders on real suites |
| mid | Sonnet | mechanical: transcript reading, file moves, fixtures, desk/dispatch sessions |
| low | Haiku | bulk classification only |

## Applying it to a build

| Work | Tier |
|---|---|
| Slice executor on a real suite, ambiguity the plan left open | one below the session, floor at high |
| Bulk edit to a locked signature, file moves, fixture generation | two below the session, floor at mid |
| Root-cause diagnosis, deviation analysis, design fork | session, or high — never mid or below |
| Driving the artifact and reporting observations | mid is fine; the reporting must be literal |

The session's own tier caps everything: never dispatch an executor on a stronger or
pricier model than the session runs on. The session model is fixed at kickoff and not
re-chosen mid-run.

## Field evidence

- A mid-tier builder spun roughly thirty minutes stuck on an end-to-end suite; the
  rule that followed — "any delegated builder runs the high tier" — held for every
  later run in that repository, across 84 dispatches with zero mid-tier builders.
- Mid-tier spec writers produced confidently wrong root causes: one spec blamed a
  missing focus attribute, and the builder disproved it by measurement (108 → 108).
- The top tier was mis-used once for a 126-word content task; it has been
  judgment-only since, and it never writes product code.
- The other repository ran a top-tier conductor with mid-tier spec writers for five
  runs and lost spec fidelity; it reverted.

## Delegation topology

`delegated` is the default: the session fans implementation out and keeps
architecture and taste. `solo` — the session builds inline — is worth it only when
the whole task fits one context and the exploration context would otherwise be
re-paid per executor. Four field runs deliberately chose `solo` on that reasoning,
two on explicit user instruction. Decide once, at the start, and record it; do not
re-decide mid-slice.
