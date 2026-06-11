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

## 3. Data / interface contract   (non-UI especially)
- Inputs (shape, validation, trust boundary):
- Outputs (shape):
- Error shapes / failure responses:
- Invariants / consistency expectations:

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
