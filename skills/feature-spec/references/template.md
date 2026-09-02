# Feature spec template

Fill this in. Scale each section to the tier — a LITE spec keeps the core spine and
drops the UI module and the formal-notation subsections; a FULL spec includes
everything applicable to the feature type. Delete sections that genuinely don't
apply, but say why in one line rather than leaving them blank.

```markdown
# Feature Spec: <name>

**Tier:** LITE | FULL   **Feature type:** UI | non-UI
**One-line request:** <the original ask, verbatim>

## 1. Problem frame
- Job (what the user is hiring this to do):
- Actors / roles:
- Success outcomes (observable):
- Non-goals (explicitly out of scope):

## 2. Behavior & states
- Primary flow (happy path):
- States / transitions the feature moves through:
  (UI: see state catalog. non-UI: lifecycle/status, in-progress, partial,
   failed, retrying, done, expired.)
- Current behavior (only when the feature changes something that exists) — one row
  per claim; every claim measured, or marked `ASSUMED` and mirrored into §13:

| Claim about today's behavior | How it was measured (command / log / test / observation) | Measured or ASSUMED |
|---|---|---|

## 3. Data / interface contract   (non-UI especially)
- Inputs (shape, validation, trust boundary):
- Outputs (shape):
- Error shapes / failure responses:
- Invariants / consistency expectations:
- Producers / consumers (FULL) — one row per data flow the feature changes:

| Data / state | Produced by | Consumed by | Both in scope? |
|---|---|---|---|

  A "no" in the last column is a flagged decision: say why the other side is safe to
  leave alone, or bring it into scope.

## 4. Edge cases & failure modes
| Condition | Expected behavior / recovery |
|---|---|
| Concurrency / double-submit | |
| Zero / one / many | |
| Limits exceeded | |
| Partial failure / retry / idempotency | |
| Stale or conflicting data | |

## 5. Defaults vs. settings
| Decision | Default | Configurable? | Rationale |
|---|---|---|---|

## 6. Scope slicing
- MVP (must):
- v1 (should):
- Vision (could):
- Out of scope:

## 7. Acceptance criteria
- Declarative bullets (LITE), and for FULL add EARS + Gherkin (see notation.md).

<!-- UI MODULE — include only when feature type = UI -->
## 8. State catalog (UI)
| Component | State | What the user sees | Action / CTA |
|---|---|---|---|

## 9. Interaction inventory (UI)
| Component | Actions | Pointer | Keyboard / shortcuts | Touch | Context menu | ARIA role/states |
|---|---|---|---|---|---|---|

## 10. Accessibility & i18n (UI)
- (walk accessibility-i18n.md)

## 11. Design tokens (UI)
- Semantic roles needed (not hex); theme variants (light/dark/high-contrast).
<!-- END UI MODULE -->

## 12. Assumptions
- Documented defaults taken instead of asking.

## 13. Decisions Needed   (autonomous mode)
- [high|normal] <question that materially changes the build> — default taken: <x>

## 14. Open questions   (interactive; only those that materially change the build)
```
```

## Self-audit (run before finishing)

List any section above you left empty or thin without justification, then fix it.
For UI features, confirm sections 8–11 are actually filled, not skipped because the
change "seemed small."

Also confirm:

- Every "currently does / doesn't" claim and every root-cause statement names how it
  was measured, or is marked `ASSUMED` and listed in §13. Inference from reading the
  source is not a measurement.
- No changed data flow in §3 names only one side, and every "both in scope? no" carries
  a written reason.
- The finished spec is within its tier's line budget (LITE ≤ ~80, FULL ≤ ~400 unless
  §13 justifies more). Over budget means the tier was wrong or the spec is padded.
