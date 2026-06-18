---
name: humanize-writing
description: "Use when writing or revising prose people will read — PR comments, review replies, tickets/user stories, dev subtasks, commit messages, standup/status updates, release notes/changelogs, code comments, docs/READMEs — or when asked to humanize, make it sound human, make it less robotic/AI, strip the jargon, or cut the wordiness. Applies both to authoring from scratch and rewriting existing text."
---

# Humanize Writing

## Overview

Agent-written prose drifts into a verbose, hedged, jargon-heavy register — long
preambles, filler adjectives (*leverage, robust, seamless, comprehensive*),
restated context, and stacked hedges. That register is a trained-in stylistic
default, not a requirement: the same content reads better in plain language matched
to where it lands.

**Core principle: write for the person who will read it, in the voice of the
surface it lives on. Cut what doesn't carry meaning; keep the words that do.**

This is about readability for humans — **not** evading AI-text detectors.

## When to use

- **Authoring** any human-read prose: PR comments, tickets, subtasks, commit
  messages, standup/status, release notes, code comments, docs.
- **Rewriting** on request: "humanize this", "make it sound human", "less AI",
  "too wordy", "strip the jargon".

**When NOT to use:** code, config, data, or machine-read output; or when the user
explicitly wants a formal/long-form register (e.g. a legal or compliance doc).

## Two modes, one method

- **Author (default):** about to write one of the surfaces → produce it in that
  surface's voice from the start.
- **Translate:** given existing text → rewrite it to the matching surface's voice.

Both run the same loop: identify the surface → apply its voice
(`references/surfaces.md`) → scan for tells (`references/tells.md`) → fix with
judgment.

## The method

1. **Name the surface.** Pick its voice from `references/surfaces.md`. If unsure
   which surface it is, infer from where the text will be posted, or ask.
2. **Write to that voice's shape.** Each surface has a different shape — a PR
   comment is a conversation, a subtask is a note, a changelog is a fact.
3. **Scan against `references/tells.md`.** For each hit, ask: does this word or
   phrase carry meaning *here*? Cut or replace filler; keep words that are genuinely
   the right ones.
4. **Read it back as the recipient.** If a person wouldn't say it that way in that
   context, fix it.

## Judgment rules — don't over-correct

- **Keep correct words.** "Robust", "comprehensive", etc. are fine when literally
  accurate. Kill the reflex, not the word.
- **Don't strip meaning.** Shorter isn't the goal; clearer is. Never delete a caveat
  that matters just to cut length.
- **Don't flatten into choppiness.** Plain is not telegraphic everywhere — match the
  surface.
- **Never detector-evasion.** Don't add errors, randomization, or "burstiness" to
  fool detectors. Write well; that's the whole job.

## Common mistakes

- One voice everywhere — a commit message and a PR comment shouldn't read alike.
- Over-explaining: restating the diff/spec, adding "Note that…", justifying every
  choice with a trailing clause.
- Hedge stacks: "I think it might be a good idea to maybe consider…".
- Marketing voice in factual contexts (release notes, docs): "seamlessly",
  "powerful", "effortless".
- Inflating a terse subtask into a paragraph.

## Set up in a repo (make the voice stick)

To make a repo *always* use this voice, add a pointer to its `CLAUDE.md` — don't
paste the rules inline (that bloats every conversation and drifts out of sync). The
pointer names the skill; the skill stays the single source of truth.

**Availability vs activation — two separate things:**

- This skill in `~/.claude/skills/` is already available in every repo on this
  machine. Personal use needs **no copy** — only the pointer.
- Copy it into the repo's `.claude/skills/humanize-writing/` only when it must
  travel: a teammate cloning the repo, or you on another machine.

**Steps:**

1. **Pointer (always).** Append this block to the repo's `CLAUDE.md` (create the
   file if missing); skip if an equivalent block already exists:

   ```markdown
   ## Writing voice
   When writing prose for people — PR comments, tickets, dev subtasks, commit
   messages, standup/status, release notes, code comments, docs — use the
   humanize-writing skill: plain language matched to the surface, no AI filler.
   ```

2. **Copy (only for portability).** Copy this skill's folder (`SKILL.md` +
   `references/`) into the repo's `.claude/skills/humanize-writing/` so it ships with
   the repo. Otherwise the personal copy already covers you.

## Reference files

- `references/surfaces.md` — each surface's voice, shape, and before/after.
- `references/tells.md` — filler words, AI-isms, hedges, and structural patterns to
  scan for (a checklist, not hard bans).
