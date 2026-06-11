# Accessibility & i18n (UI features only)

These are the surfaces salience-driven specs silently drop. They are non-optional
for UI features, even small ones (a "Copy" button still needs an accessible name,
a result announcement, and a localized label).

## Accessibility (WCAG 2.2 mindset)

- **Keyboard operability** for everything — every action reachable and activatable
  without a pointer (Tab/arrow navigation, Enter/Space activate, Esc cancel).
- **Visible focus** — never remove the outline without replacing it; verify it
  survives forced-colors / high-contrast mode.
- **Accessible names** — icon-only controls need `aria-label`; form fields need
  labels.
- **Announce dynamic results** — use a live region (`aria-live="polite"`) for
  outcomes a sighted user sees but a screen-reader user wouldn't (e.g. "Copied",
  "Moved to Done", loading/busy/error).
- **Drag-and-drop alternative** — a non-dragging way to perform any drag action
  (WCAG 2.5.7), with keyboard pickup/move/drop + announcements.
- **Color is never the only signal** — pair color with text/icon; contrast ≥ 4.5:1
  for text.
- **Reduced motion** — comprehension must not depend on animation.
- **Focus management** — order matches the mental model; after an action focus lands
  somewhere sensible (e.g. the moved item in its new place).

## Internationalization

- **Externalize all user-facing strings** — never hardcode copy in component
  definitions (including "Copy"/"Copied!"-style microcopy).
- **Pluralization** — count-dependent strings use plural-aware formatting.
- **Locale formatting** — dates, numbers, currency are locale-aware; timestamps
  stored/declared in UTC/ISO-8601.
- **Text expansion** — layouts tolerate ~30%+ longer strings (short labels can be
  far worse); don't truncate meaning.
- **RTL** — layout mirrors for right-to-left; decide whether directional workflows
  reverse (a genuine ask-or-flag candidate).
- **Sorting/collation** — locale-aware where the feature sorts user-visible text.
