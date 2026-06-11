# UI states & interaction inventory (UI features only)

Walk these for every screen/component the feature touches. The point is uniform
coverage — do not skip a row because the feature "seems small."

## State catalog (the UI Stack, expanded)

For each component, specify what the user sees, the copy, and the action/CTA in
every state that can occur:

- **Ideal / populated** — the normal, data-present state.
- **First-run / blank slate** — never used yet; explain the purpose + one primary
  CTA (imperative verb).
- **Empty after action** — cleared/completed/no-results; distinct from first-run.
- **Loading** — prefer skeletons over spinners; place where content will appear;
  render chrome immediately.
- **Partial** — some data present while more loads, or sparse data.
- **Error (component-level)** — inline message + cause + constructive next step +
  retry.
- **Error (page-level)** — full recovery state + retry path.
- **Offline / degraded** — show connectivity status; say which actions are queued
  or unavailable.
- **Permission-denied** — explain scope (whole feature vs. one item) + next valid
  action (e.g. request access).
- **Not-found** — the target no longer exists; recovery path.
- **Saving / in-progress / failed-save** — optimistic update + rollback + toast.
- **Limit reached** (if applicable) — warning that is not color-only; advisory vs.
  enforced.

## Interaction inventory

For each interactive object, fill a row:

| Component | Actions/affordances | Pointer (click/drag/hover/right-click) | Keyboard (tab/arrows/enter/esc/shortcuts) | Touch (tap/long-press/swipe) | Context menu | ARIA role/states |
|---|---|---|---|---|---|---|

Rules of thumb:
- **Every drag action needs a non-drag pathway** (menu action, detail action, and a
  keyboard pathway) — drag alone is neither discoverable nor accessible.
- Distinct visual states for default / hover / focus / selected / disabled /
  dragging; focus must be visible and selection must not rely on color alone.
- Destructive or state-changing actions: confirm and/or offer undo.
- Decide where global controls live (search/filter/settings belong to the surface
  that owns the mental model, not buried in a sub-component).
