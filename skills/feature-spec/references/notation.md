# Acceptance-criteria notation

Pick by tier. **LITE:** declarative bullets are enough. **FULL:** add EARS for
behavioral/state rules and Gherkin for key acceptance flows. Don't impose EARS on a
small spec — that's its own over-production.

Keep everything **declarative** — describe observable behavior, not implementation
("When the user submits credentials", not "When the user clicks #submit").

## Declarative bullets (LITE, and as a baseline everywhere)

- Each criterion is observable and testable.
- 1–3 per user story.
- Cover happy path + the key non-happy states from the state catalog.

Example:
- The full, exact value is placed on the clipboard, even when the field shows a
  masked value.
- On failure, the user sees a clear message and can still copy manually.

## EARS (FULL — behavioral/state requirements)

Five patterns; each yields one testable "shall" statement:

- **Ubiquitous** — `The <system> shall <response>.`
- **State-driven** — `While <state>, the <system> shall <response>.`
- **Event-driven** — `When <trigger>, the <system> shall <response>.`
- **Unwanted behavior** — `If <condition>, then the <system> shall <response>.`
- **Optional feature** — `Where <feature is present>, the <system> shall <response>.`

Examples:
- *Event:* When a card is dropped on a different column, the board shall update the
  card's status, persist it, and announce the move via a live region.
- *Unwanted:* If a move fails to persist, then the board shall revert the card and
  show a retry affordance.
- *State:* While the export is generating, the system shall show a non-blocking
  in-progress indicator.

## Gherkin (FULL — key acceptance flows)

```gherkin
Feature: <name>
  Scenario: <observable outcome>
    Given <context>
    When <action>
    Then <observable result>
    And <additional observable result>
```

Use `Background` for shared setup. Reserve Gherkin for complex/high-risk flows;
simple rules stay as bullets or EARS.
