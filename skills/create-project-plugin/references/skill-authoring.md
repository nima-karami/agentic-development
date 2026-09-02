# The quality bar for an emitted skill

Emitted skills are committed, long-lived, and read by teammates and future sessions.
Hold them to the bar the project holds its code to. Read this before writing any skill,
and run the checklist before calling one done.

## Frontmatter

```yaml
---
name: <kebab-case archetype name>
description: <"Use when…" — triggering conditions and keywords only>
allowed-tools: <only what this skill actually uses>
---
```

- **The description is the trigger.** It is the only part always in context, so it must
  name the contexts and the casual phrasings a real user of *this* project types — not
  a workflow summary. A description that summarizes the workflow gets followed *instead*
  of the body being read.
- **`allowed-tools` is the boundary made real.** A planning skill legitimately writes
  its own artifact and runs setup commands, so it carries write and shell access but not
  source editing. State the boundary in the body too, so it is explicit to the reader.

## Structure

Same order every time, so the suite is one learnable pattern:

Overview / core principle → When to use / When NOT to use → **Hard rules** (canon +
project bindings) → numbered Steps → reference tables → Common mistakes → Gotchas →
Reference files.

Three levels of disclosure: metadata always loaded, body loaded on trigger (keep under
~350 lines), `references/` read on demand. The project's exhaustive detail — a full test-
affordance surface, a deploy runbook's failure table — goes in a reference file the body
points at, never inline.

## Voice

- **Imperative and direct**, with the reason attached. "Read both the parent and the
  repository instruction file, because the parent carries cross-repo rules the repository
  cannot see." The reason is what makes the rule hold in a situation you did not foresee.
- **All-caps MUST is a yellow flag.** Reaching for it usually means the *why* is missing.
  Reserve hard imperatives for genuine correctness boundaries.
- **Every sentence is a rule, a step, or a reason a rule exists.** No pep talk, no
  restating the request, no options the skill will not pursue.
- **Match the project's own voice.** If the project writes plainly, the skill does too.

## Self-contained, and what that means

- No pointer outside the plugin, except to paths inside the project's own repositories.
- **No machine paths.** An absolute path from the author's disk is the single most common
  defect in hand-built suites, and it fails silently for everyone else.
- A plugin-internal shared reference is allowed and preferred over inlining the same fact
  in six skills. "Self-contained" bars reaching *outside* the vessel, not sharing inside
  it.
- The skill **is** the project's skill for its stage. It never forwards to a general
  skill: a body that says "invoke the general planning skill, then apply our conventions"
  adds a hop and no knowledge, and breaks the moment that general skill is not installed.

## Conventions, not instances

Inline: the branch rule, the commit-subject shape, the gate command, the artifact
locations, the "done" bar, the read-when triggers. These are exactly what a pointer would
let the agent skip.

Never inline: a ticket key, a branch name, a person, a port number, a today-path, a
version that will change next week, or anything else true only this month.

Depth goes by pointer to the repository's own docs, **by path**, with the instruction that
opening the file is required — seeing the path is not reading it.

## The scar slot

A rule carrying a real incident is far harder to rationalize past than an abstract
principle. So each hard rule may carry one anonymized clause naming what went wrong.

**The scar slot is filled only from this project's own discovery or retro notes.** A scar
borrowed from another project is a decoration: the reader has no memory of it, nothing
confirms it, and the first session under pressure discounts the whole rule. An empty scar
slot is fine — the rule still stands on its reason.

## Parameters, not rules

These are choices, and the emitted skill states which choice this project made and why.
Presenting any of them as a universal rule is a defect:

| Knob | Default to ask about |
|---|---|
| Lifecycle stance | pre-production (shims and staged cutovers banned) vs live users (they are required) |
| Gate cadence | per slice, per task, or once at the end |
| Concurrency cap | how many executors run at once |
| Slice size | the review increment, in minutes of work |
| Retro note length | the cap that keeps notes readable in bulk |
| Delivery endpoint | commit, or a pull request by default |
| Plan detail | signatures and test intents, or full bodies |

The pre-production stance is the one that bites hardest: "no compatibility shims, no
flags to stage a cutover, temporary loss of a feature is never a risk" is correct
pre-launch and actively wrong with live users, and it appears in the spec, design-review
and build skills at once.

## Right-sizing

The failure this whole tool prevents is over-generation: thousands of lines that make
intent harder to find and mostly get ripped out.

- Generate only the archetypes the project needs.
- A skill's length is proportional to its job. A single-repo kickoff does not need the
  multi-repo workspace ladder.
- Cut speculative scope; never trim validation, gates, or correct placement to save
  lines. **Lazy scope is good; lazy rigor is not.**

## Checklist — run before calling any emitted skill done

- [ ] Description starts with "Use when…", names this project's real trigger phrasings,
      and summarizes no workflow.
- [ ] `allowed-tools` is exactly what the skill uses.
- [ ] Names the project's **real** repositories and ownership, branch rule, commit shape
      — from the profile, not a placeholder.
- [ ] States the exact gate command and the artifact locations for its stage.
- [ ] Points at the project's **actual** docs by path, and says the read is required.
- [ ] Carries its assigned canon items **verbatim**, plus the binding block.
- [ ] Carries the gates its archetype owns, at the point where the violation happens.
- [ ] Conventions inline; no instance, no machine path, no borrowed scar.
- [ ] Ends with the machine-parseable handoff block its stage owes the next one.
- [ ] Names the neighbouring stages it hands to and receives from.
- [ ] Every tuning knob it exercises is stated as this project's choice, with the reason.
- [ ] Works without any external account, hosted service, or tool the project does not
      already run.
- [ ] Under ~350 lines, with depth in `references/`.

A skill that still tells its reader to "figure out the project's conventions" failed the
only test that matters. Go back and press the profile into it.
