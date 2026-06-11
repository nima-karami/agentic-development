---
name: feature-spec
description: Use when turning a vague or short feature idea into a full specification before implementation — a one-line/paragraph request like "add X", a wishlist item, or a feature handed off in an automated/unattended pipeline for a downstream agent to build. Triggers - "write a spec for…", "turn this idea into a spec", "flesh out this feature", specifying behavior / states / edge cases / defaults / acceptance criteria before coding.
allowed-tools: Read, Glob, Grep, Task, Write, AskUserQuestion
---

# Feature Spec

Turn a vague feature request into a complete, **right-sized** specification of what
to build and how it behaves — before any code.

## Core principle

A strong model already writes thorough specs when a feature is salient. Its three
real failures, confirmed by testing, are:

1. **It doesn't right-size.** It produces a 10-section spec for a one-click button
   and the same shape for a large feature. Over-production is a defect.
2. **Coverage is driven by salience, not a checklist.** It nails accessibility for
   an obvious copy button but silently omits a11y for a settings/download flow, and
   omits i18n almost always. The fix is *fixed checklists*, not more eloquence.
3. **Output isn't loop-ready.** Inconsistent structure, no tier label, assumptions
   buried in prose — an autonomous pipeline can't route on it.

So this skill's job is **proportion, uniform coverage, and a structured handoff** —
not teaching spec-writing. Enumeration beats eloquence.

## When to use

- A feature request is vague, one-line, or a paragraph and needs fleshing out
  before implementation.
- A wishlist item is being processed (interactively or by an unattended agent loop)
  and must become a buildable spec.

## When NOT to use

- The change is mechanical and obvious (rename, copy tweak, dependency bump) — just
  do it; a spec is over-production.
- Designing internal architecture/structure — that is a separate concern. This
  specifies behavior, not internal design.
- Implementing — this produces a spec; a different step builds from it.

## Modes

Default **interactive**. Switch to **autonomous** when the invoker says so (a parent
loop calls this non-interactively) or when there is plainly no human in the loop
(running inside a detached/long-running task). Explicit signal wins.

**In autonomous mode you MUST NOT call `AskUserQuestion`.** A blocking question in a
detached task hangs the pipeline. Convert every would-be question into a flagged
assumption (see Ask-or-flag).

## Step 0 — Triage (always first, state it out loud)

Before producing anything, classify and **announce the tier and feature type with a
one-line reason**:

| Tier | When | What you produce |
|---|---|---|
| **SKIP** | Trivial / single-component / bugfix | No spec. State 1–3 assumptions and stop. |
| **LITE** | One surface, one clear job | Core spine only; declarative acceptance criteria; self-audit. No reviewer subagent. |
| **FULL** | Multi-surface / novel / user-facing | Core spine + applicable modules + EARS/Gherkin + self-audit + reviewer subagent. |

**Feature type: UI or non-UI.** This gates the UI module. A backend/API/job feature
never gets an accessibility, i18n, or design-token checklist.

When unsure between tiers, pick the smaller one — you can always deepen a section.

## The pipeline

Fill the template in `references/template.md`. Scale depth to the tier; never pad a
LITE spec to look like a FULL one.

**Core spine (every non-SKIP feature):**

1. **Problem frame** — the job (JTBD / 5-Whys), actors, success outcomes, explicit
   non-goals.
2. **Behavior & states** — the states/transitions the feature moves through. For
   non-UI: lifecycle/status, partial/failure/retry states.
3. **Data / interface contract** (non-UI especially) — inputs, outputs, error
   shapes, invariants.
4. **Edge cases & failure modes** — concurrency, zero/one/many, limits, partial
   failure, retries/idempotency.
5. **Defaults vs. settings** — default the ~80% safe path; expose a setting only for
   durable/divergent preferences; record each default's rationale.
6. **Scope slicing** — MVP → v1 → vision + explicit Out-of-Scope.
7. **Acceptance criteria** — notation per `references/notation.md` (declarative for
   LITE; add EARS + Gherkin for FULL).

**Conditional UI module (only when feature type = UI):** load
`references/state-and-interaction.md` and `references/accessibility-i18n.md` and walk
their checklists — the state catalog, interaction inventory, accessibility, i18n,
and design tokens. These are the surfaces salience-driven specs silently drop.

## Ask-or-flag gate (the behavioral heart)

Same calibration in both modes: **act only when the answer materially changes what
gets built AND cannot be inferred** from repo, conventions, or sensible defaults.
Don't ask/flag about reversible preferences or standard conventions — assume and
note them.

- **Interactive:** batch the high-impact, non-inferable questions (≤5) via
  `AskUserQuestion`, each with options + a **recommended default** + a "use default"
  escape. Everything else → an **Assumptions** entry.
- **Autonomous:** **never ask.** Each would-be question becomes an assumption using
  the *most conservative, reversible* default, recorded in a prominent
  **`## Decisions Needed`** section, each entry **severity-tagged `high`/`normal`**.
  High-stakes/irreversible ambiguities: pick the safest default, tag `high`, and
  **continue — never halt.** The flags are the safety valve.

## Self-audit and review

- **Self-audit (every tier):** end by listing any template/checklist items you did
  not address, then fix them. Do not claim done with the list non-empty.
- **Reviewer subagent:** on FULL (and *always* in autonomous mode, where it's the
  only gate left), dispatch a fresh general-purpose agent via **Task** with read-only
  tools. Give it the spec + the template/checklist criteria and **not** your
  reasoning. Ask it to report missing coverage (states, edge cases, a11y/i18n,
  defaults, loop-handoff fields). Revise before finishing.

## Output and handoff

- **Interactive:** present the spec, then on the user's go write
  `docs/specs/<feature-slug>.md` in the target repo. Create the `docs/specs/` dir
  only at write time — never while drafting (no empty dirs left in the tree).
- **Autonomous:** write `docs/specs/<feature-slug>.md` directly and return a final
  message in this exact shape so the loop can parse it:

  ```
  SPEC: docs/specs/<slug>.md
  TIER: LITE|FULL
  DECISIONS_NEEDED: none | <n> (highest: high|normal)
  ```

  Clean specs route straight to implementation; specs with `high` flags get
  surfaced to a human.

## Hard rules

- **Triage before content.** Always declare tier + feature type first. No silent
  full-pipeline on a small feature; no silent thin spec on a big one.
- **Never call `AskUserQuestion` in autonomous mode.**
- **Run the checklists for the feature type — don't rely on salience.** If
  feature type = UI, a11y and i18n are non-optional sections, even when the change
  "seems too small to need them."
- **Document every assumption.** An assumption not written down is a silent bug.
- **Right-size depth to tier.** Padding a LITE spec is the same defect as a thin
  FULL spec.

## Common mistakes

- **Skipping triage and defaulting to FULL.** The #1 baseline failure. Declare the
  tier first and mean it.
- **Letting salience pick coverage.** "It's just a button" → a11y/i18n dropped. Walk
  the checklist for the feature type regardless.
- **Asking in autonomous mode.** Hangs the loop. Flag instead.
- **Burying decisions in prose.** In autonomous mode, high-stakes guesses must be in
  `## Decisions Needed`, severity-tagged, not scattered in paragraphs.
- **Over-asking interactively.** Questions that don't change the build, or re-ask
  inferable things, make the skill annoying. Assume and document those.

## Gotchas

- **Completeness comes from the checklist, not the prose.** The references exist so
  coverage is uniform across runs; load and walk them rather than free-styling.
- **The handoff line is a contract.** The `SPEC:/TIER:/DECISIONS_NEEDED:` block is
  what a parent loop greps. Keep its shape stable.
- **Right-sizing is the anti-over-engineering guard.** A spec heavier than the
  feature is itself the failure this skill prevents — apply it to your own output.
