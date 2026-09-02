# Skill authoring — the quality bar

Generated skills are committed, long-lived, and read by teammates and future sessions.
This is how to make them good rather than merely present. Read this before writing any
skill.

## The frontmatter carries the triggering

```yaml
---
name: <kebab-case-name>
description: <when to trigger + what it does>
allowed-tools: <only what the skill needs>
---
```

- **`description` is the primary trigger mechanism.** It's the only part always in
  context, so it must say both *what the skill does* and *specific contexts/phrases for
  when to use it*. Models tend to *under*-trigger skills, so lean slightly pushy: include
  the casual phrasings a real user would type, not just the formal name. But don't make it
  trigger on near-misses — name the contexts precisely.
- **`allowed-tools`** = only what the skill actually uses. Resolve the common
  planning-skill tension directly: a skill that "must not implement" still legitimately
  **writes its planning artifact** (a plan/spec file) and **runs setup commands** (cut a
  branch). So a kickoff/planning skill carries `Write` (for the plan file) and `Bash` (for
  branch/setup), but **not `Edit`** — the line is "no editing of source," not "no writing
  at all." Say so in the skill body too, so the boundary is explicit to its user.

## Progressive disclosure — three levels

1. **Metadata** (name + description) — always loaded. Keep tight.
2. **SKILL.md body** — loaded when the skill triggers. Keep under ~500 lines. If it grows
   past that, push detail into `references/` and point at it clearly.
3. **`references/`** — read on demand. This is where variants, catalogs, templates, and
   long detail live. Large reference files get a table of contents.

Mirror this in generated skills: the body is the workflow; the project's exhaustive
detail (a full repo map, a deploy runbook's failure modes) belongs in a reference file the
body points at, not inline.

## Voice — explain the why, don't stack MUSTs

Today's models have good theory of mind and respond to *reasons*, not volume. A skill that
explains why a step matters produces better results than one that shouts `ALWAYS`/`NEVER`.

- **Imperative and direct.** "Read every CLAUDE.md up the tree" — not "You should consider
  reading…".
- **Explain the why.** "Read *both* the parent and repo CLAUDE.md, because the parent
  carries cross-repo rules the repo can't see" — the reason makes the instruction robust to
  situations you didn't foresee.
- **All-caps MUST is a yellow flag.** If you're reaching for it, you probably haven't
  explained *why* the thing matters. Reframe as a reason. Reserve hard imperatives for
  genuine correctness/safety boundaries.
- **The strongest why is the project's own incident.** When a rule exists because
  something real went wrong, cite the incident in one anonymized clause — "a sampled
  'solid' once hid 41-vs-2 log-level chaos behind six spot checks", "green tests once
  shipped a visually destroyed screen". A rule carrying its scar is far harder for a
  future session to rationalize past than an abstract principle; the discovery profile's
  failure patterns are the source.
- **A rule that was being violated gets a gate, not adverbs.** If discovery shows an
  existing rule being skipped, the generated skill adds a checkable step at the violation
  point (a required proof, a diff-against-plan check) — "always remember to" is the
  phrasing of a rule that will be violated again.
- **Match the project's own voice.** If the project writes prose plainly (a humanize-writing
  convention), generated skills should read that way too.

## Right-sizing — the discipline that matters most

The failure this whole tool exists to prevent is over-generation: thousands of lines that
make intent *harder* to find and mostly get ripped out. Apply the same discipline to the
skills you generate.

- **Generate only archetypes the project needs**, not the whole catalog.
- **A skill's length is proportional to its job.** A copy-tweak kickoff doesn't need the
  full top-down design ladder; a multi-repo deploy does.
- **Cut speculative scope**, keep rigor. Don't add options nobody asked for; never trim
  validation, error handling, or correct placement to save lines.

## Project-specialization checklist

A generated skill has actually been *specialized* (not just templated) when:

- [ ] It names the project's **real** repos/ownership, branch rule, commit format — from
      the profile, not a placeholder.
- [ ] It points its user at the project's **actual** docs (the read-when index), not
      generic advice.
- [ ] It encodes the project's **"done" bar** and tooling loop with real commands.
- [ ] It's **self-contained within its vessel** — no references outside its own repo or
      plugin, and no machine paths. A plugin-internal shared reference file (one the plugin's
      skills point at for a common convention) is *allowed and preferred* over inlining the
      same fact N times — "self-contained" bars reaching *outside* the vessel, not sharing
      *inside* it.
- [ ] It bakes in **conventions, not instances** — the branch-naming rule, never a specific
      ticket number or branch.
- [ ] It's **named for its role**, survives the project maturing, and hands off to the
      neighbouring skills in the suite.
- [ ] Its `description` would trigger on the phrasings a real user of *this* project types.

If a generated skill still tells its user to "figure out the project's conventions," it
failed the only test that matters — go back and press the profile into it.

## Dogfood

This tool's own skill and reference files are an example of the bar: progressive
disclosure, reasons over MUSTs, right-sized. When in doubt about shape, mirror it.
