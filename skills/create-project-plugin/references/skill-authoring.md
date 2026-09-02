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
- **Budget the description to ~400 characters.** Every skill in the suite has one and all
  of them are loaded on every turn, so a twelve-skill suite at 700 characters each is
  ~8,400 characters of permanent overhead. Cut in this order: repeated phrasings of the
  same trigger; generic keywords a user would type against any project; the
  neighbour-naming clause, down to bare stage names. Cut the distinctive project
  phrasings last — they are the only reason the skill fires at the right moment.
- **`allowed-tools` is the boundary made real.** A planning skill legitimately writes
  its own artifact and runs setup commands, so it carries write and shell access but not
  source editing. It is the **union across the skill's modes**: a skill that asks the user
  questions interactively and is forbidden to ask them in an autonomous run still lists
  the question tool, because it uses it in one mode. State the per-mode boundary in the
  body, so the union does not read as a defect to whoever audits the frontmatter alone.

## Structure

Same order every time, so the suite is one learnable pattern:

Overview / core principle → When to use / When NOT to use → **Hard rules** (canon +
project bindings) → numbered Steps → reference tables → Common mistakes → Gotchas →
Reference files.

Three levels of disclosure: metadata always loaded, body loaded on trigger, `references/`
read on demand.

**The body budget is ~350 lines, and it excludes the canon block and the project-binding
block.** Both are injected verbatim and neither is the author's to trim, so counting them
would penalise exactly the archetypes that carry the most canon and need the most method
— `build` and `loop`. Both stay **inline in every skill**: the canon because identical
wording is what lets one search find every copy (hard rule 6), the binding block because
a pointer is what the agent skips (hard rule 2). Neither moves to a shared reference.

Everything else counts. The project's exhaustive detail — a full test-affordance surface,
a deploy runbook's failure table, a report template — goes in a reference file the body
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

- No pointer outside the plugin, except to paths inside the project's own repositories —
  and the retro's seed-drift diff, which names general skills as **diff targets only**,
  never invokes one, and skips with a recorded note when a seed is not installed.
- **No machine paths.** An absolute path from the author's disk is the single most common
  defect in hand-built suites, and it fails silently for everyone else.
- A plugin-internal shared reference is allowed and preferred over inlining the same fact
  in six skills — but for **depth facts only**. The canon and the project-binding block
  are always inline in every skill; a pointer is exactly what the agent skips there.
  "Self-contained" bars reaching *outside* the vessel, not sharing inside it.
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

The scar clause is not the only thing that may follow a rule: a **project clause** on a
canon item (` — Project: …`) is a separate, separately authorized appendage — see
`canon.md`. Both go *after* the rule's own text; neither ever edits it.

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
- [ ] Description is within ~400 characters.
- [ ] `allowed-tools` is the union of what the skill uses across its modes, and the body
      states the per-mode boundary.
- [ ] Names the project's **real** repositories and ownership, branch rule, commit shape
      — from the profile, not a placeholder.
- [ ] States the exact gate command and the artifact locations for its stage.
- [ ] Points at the project's **actual** docs by path, and says the read is required.
- [ ] **Every `references/` path this skill names exists and is non-empty.** A dangling
      pointer fails silently: the reader follows it, finds nothing, and invents the
      artifact format. Resolve them, do not eyeball them.
- [ ] **Every artifact this skill writes is one no sibling skill also writes** — or the
      split is stated in both skills, including which invocation shape owns which file.
- [ ] Carries its assigned canon items **verbatim**, plus the binding block.
- [ ] Carries the gates its archetype owns, at the point where the violation happens.
- [ ] Conventions inline; no instance, no machine path, no borrowed scar.
- [ ] Ends with the machine-parseable handoff block its stage owes the next one.
- [ ] Names the neighbouring stages it hands to and receives from.
- [ ] Every tuning knob it exercises is stated as this project's choice, with the reason.
- [ ] Works without any external account, hosted service, or tool the project does not
      already run.
- [ ] Under ~350 lines excluding the canon and binding blocks, with depth in
      `references/`.

A skill that still tells its reader to "figure out the project's conventions" failed the
only test that matters. Go back and press the profile into it.
