# Verifier brief

One fresh verifier per serious finding (every Critical and High at `standard`; every
finding at `deep`). Its job is to **refute**. A judge never verifies its own finding.

**Pass the verifier:** the finding's claim line, rubric row, anchors and counterexample
— nothing else from the judge. **Never pass:** the judge's "why it matters",
"counter-evidence considered", confidence, or prose, and nothing from the codebase
profile. Those carry the judge's reasoning or the stakes, and a verifier that reads
them re-confirms instead of testing.

## Slots

| Slot | Content |
|---|---|
| `{CLAIM}` | the finding's one-line claim |
| `{ROW}` | the rubric row id and its full text, including the over-engineering line |
| `{ANCHORS}` | the anchors as written |
| `{COUNTEREXAMPLE}` | the counterexample or failure path as written |
| `{OUT}` | `work/verdicts/<finding-id>.md` |

## The brief

> Someone claims this about a codebase you have read-only access to:
>
> **{CLAIM}**
> Anchors: {ANCHORS}
> Counterexample: {COUNTEREXAMPLE}
> The standard it is judged against: {ROW}
>
> Try to prove the claim wrong. Specifically:
> 1. Open every anchor. Does the code at each one say what the claim needs it to say?
> 2. Hunt for counter-evidence: a guard or parse elsewhere on the path; a declared,
>    tested and observable fallback; a decision record or enforced rule that permits
>    it; a test that already pins the behavior; a caller pattern that makes the
>    counterexample unreachable; dynamic registration that makes "dead" code live.
> 3. Check the row's over-engineering line: is this one of the legitimate cases?
> 4. For a negative claim ("nothing validates this", "no consumer uses this"), run a
>    full recursive search including ignored and hidden directories before accepting it.
>
> Do not edit anything and do not run gates. Write {OUT}:
>
> ```
> VERDICT: CONFIRMED | DOWNGRADE | REFUTED
> SEVERITY: <unchanged, or the lower level for DOWNGRADE>
> EVIDENCE: <path:line or command output that decides it>
> NOTE: <one or two lines>
> ```
>
> Reply with the verdict line only.

## Using the verdicts

- `REFUTED` — dropped from the report and counted in the run summary.
- `DOWNGRADE` — kept at the verifier's severity, with its evidence attached.
- `CONFIRMED` — kept; still goes to the human for confirmation if Critical or High.
- No usable verdict (dispatch failed, empty output) — the finding stays `unverified`;
  it never becomes confirmed by default.
