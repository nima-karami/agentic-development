# Judge brief

One judge per dimension × slice. Fill the slots and send the brief verbatim; change the
finding schema, the guardrails and the output contract for nothing.

**Never paste into a slot:** another judge's findings, this session's impressions of
the code, the authoring agent's run reports or commit narration, or a summary of "what
the audit has found so far." The judge gets facts and the tree, not a story.

## Slots

| Slot | Content |
|---|---|
| `{DIMENSION}` | architecture / gates / contracts / verbosity |
| `{SLICE}` | the slice name and its include globs |
| `{RUBRIC_PATH}` | the dimension's rubric file |
| `{FACTS}` | paths under `work/facts/` filtered to this slice |
| `{PROFILE}` | path to the run's `profile.md` (the whole profile) |
| `{INTENT}` | path to `work/intent.md` (the claim ledger and three-architectures table) |
| `{READING_SAMPLE}` | the files to read in full: new violations, slice hotspots, abstraction clusters, plus the control sample at `deep` |
| `{SEVERITY}` | the severity table and step rules from the skill |
| `{OUT}` | `work/findings/{DIMENSION}-{SLICE}.md` |

## The brief

> You are auditing one slice of a codebase, for one dimension only: **{DIMENSION}**,
> slice **{SLICE}**. You did not write this code and you have no account of why it is
> the way it is. You have read-only access to the tree.
>
> Read the profile at {PROFILE}: what the system is, its load and constraints, its
> stakes and its dominant quality attributes. It decides which rubric rows apply and
> how severe a finding is — skip a row whose `applies when` condition the profile
> rules out, and treat any `unknown` in load or stakes as high stakes.
>
> Read the rubric at {RUBRIC_PATH}. It is the only standard. Read the intent ledger at
> {INTENT}: it records what the repo itself declares, with authority ranked enforced
> rules > accepted decision records > instruction files > prose.
>
> The facts at {FACTS} were produced by tools. Treat each listed candidate as a
> hypothesis: for each, **confirm** it (it matches a rubric row and you verified the
> anchor in the tree), **dismiss** it with a one-line reason, or flag it as an
> **authority conflict** (two conventions, nothing declares which wins). Then read the
> files in {READING_SAMPLE} in full and add findings the tools could not see.
>
> Rules:
> 1. Every finding has a primary anchor `path:line` you opened yourself. Never assert a
>    dependency edge you did not find in the facts or in quoted code.
> 2. A violation needs a declared rule or a measured cost. If neither exists, it is an
>    authority conflict or it is taste. Drop taste.
> 3. For contracts: state a caller-visible counterexample — "the declaration permits X,
>    yet Y happens." No counterexample, no finding.
> 4. Read callers and the implementation, not just the signature.
> 5. Check the rubric row's over-engineering line before reporting. "This is
>    over-engineering" and "no finding" are valid outputs.
> 6. Severity per {SEVERITY}. Severity and confidence are separate. Who wrote the code
>    never changes severity.
> 7. Merge instances of one habit into one finding with several anchors.
> 8. Do not edit anything, run gates, or fix what you find.
> 9. Performance: never state a latency, count or hit rate you did not get from a tool
>    or compute from the profile's numbers; an unmeasured candidate is at most Medium
>    and names the measurement that would settle it.
>
> Write {OUT} in the schema below and reply with a five-line summary: counts by
> severity, candidates dismissed, authority conflicts, anything you could not assess.

## Finding schema

```
### F-{DIMENSION}-{SLICE}-<n> · <one-line claim>
- rubric: <row id, e.g. C4>
- anchors: <primary path:line> ; <supporting path:line or scan reference> ; …
- counterexample: <contracts: "the declaration permits X, yet Y happens"; others: the concrete failure path or measured cost>
- evidence: provable | strong-inference          # weak or style-only is not emitted
- status: measured | computed | candidate (unmeasured) | n/a     # performance; candidates cap at medium
- measurement needed: <performance candidates: the exact measurement that would settle it, else omit>
- also flagged by: <another dimension's row if it plausibly owns this; the owner is the row naming the consequence>
- severity: critical | high | medium | low
- confidence: high | medium | low
- exposure: <hotspot rank / fan-in / public or internal / persisted or not>
- why it matters: <one or two lines>
- counter-evidence considered: <what you checked that could have dismissed it>
- fix direction: <one change, sized for one task; name the lint rule or structural test that would stop recurrence, if one exists>
```

Authority conflicts use:

```
### AC-{DIMENSION}-{SLICE}-<n> · <the two conventions>
- conventions: <A, with call-site count and anchors> vs <B, same>
- sources: <what each source in the ledger says, if anything>
- decision needed: <the question a human must answer>
```

End the file with a `## Dismissed` list — every candidate you were given and did not
confirm, one bullet each: `<anchor or candidate id> — <reason>` — and a `## Not assessed`
list, one bullet each with its reason: `out of sample`, `row ruled out by profile`,
`profile-blocked`, `could not read`, or `out of time`. A candidate that appears in
neither your findings nor these lists is a gap in the run record.
