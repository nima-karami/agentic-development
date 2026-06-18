# Surfaces — voice + examples

Pick the surface, write to its voice. Before/after pairs show the target shape.

## PR comments / review replies

**Voice:** casual, first-person teammate. Contractions, "I", "can we". Get to the
point; one main ask. No preamble, no restating the whole diff, no trailing
justification clause.

- **Before:** "Nice catch on the unknown-ID crash. One thing though: the fix returns
  `null` when the API gives back `null`, but the actual bug was the API returning an
  empty array (`[]`) for unknown IDs, and I don't think that path is covered here —
  `[]` is truthy, so it'll still fall through and crash on `data[0]`. Can we
  explicitly handle the empty-array case (`if (!data.length) return null;`) and add a
  test that hits `getProfile()` with an unknown ID before we merge? Want to make sure
  the regression test actually exercises the branch that was broken."
- **After:** "This handles `null` but not the empty-array case — `[]` is truthy, so
  it still crashes on `data[0]`. Can we guard `if (!data.length) return null` and add
  a test for the unknown-ID path before merge?"

## User-story tickets

**Voice:** plain, neutral, structured. Standard story + concrete, testable
acceptance criteria. No filler adjectives, no motivational padding unless it's a real
requirement.

- **Keep:** title; "As a / I want / so that"; short description; bulleted acceptance
  criteria.
- **Cut:** "comfortably", "delightful", value-prop language that isn't a criterion.

## Dev subtasks / checklists

**Voice:** terse note-form. One action per item, imperative. No item with three
clauses stacked in parentheses — if an item needs a paragraph, it's not a subtask,
so split it.

- **Before:** "Add theme state + persistence (read/write the user's choice to
  storage, fall back to `prefers-color-scheme`) and expose it via the existing
  app/theme context."
- **After (two items):**
  - "Add theme state + persistence (storage, fallback to system)."
  - "Expose theme via app context."

## Commit messages

**Voice:** terse, imperative subject ("Fix X", "Add Y"), ~50 chars. Optional body
says *why*, wrapped ~72 chars. Never "This commit…".

- **Good:** subject `Fix getProfile crash on unknown IDs`; body explains the
  empty-array cause and the added test.

## Standup / status updates

**Voice:** casual, brief, first-person. Done / Today / Blocked, one line each. State
the blocker plainly; skip the softener.

- **Before:** "Blocked: Waiting on design approval … would be great to get sign-off
  so I'm not building against a moving target."
- **After:** "Blocked: need design sign-off on the toggle before I build the UI."

## Release notes / changelogs

**Voice:** plain, user-facing, factual — what changed and what it means for the user.
No hype adjectives. Group by Added / Fixed / Changed.

- **Good:** "Fixed: looking up an unknown user ID no longer crashes — it now returns
  no result instead."

## Code comments / docstrings

**Voice:** minimal. Comment the non-obvious *why*, never the *what*. No comment that
restates the code. Docstrings: one line of purpose, plus params/returns only when
non-obvious.

## Docs / READMEs

**Voice:** plain, direct, second person ("you"). Lead with what the reader does. No
marketing intro, no "powerful/seamless". Short sentences, concrete steps.
