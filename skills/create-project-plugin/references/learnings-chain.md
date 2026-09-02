# The learnings chain

How a suite improves itself: three hops, each with a gate. Without the gates the chain
breaks at the first one, and every lesson gets re-learned per run.

```
per slice  ──►  run learnings file      (canon 6: tagged bullets)
per task   ──►  plugin retro note       (close refuses teardown until it exists)
per period ──►  changelist + version    (retro applies, files the notes)
```

Each hop **reduces**. The learnings file is raw and long; the note is ≤15 lines; the
changelist is a handful of edits. A hop that does not reduce hands the next one the same
reading problem it was supposed to solve.

## Hop 1 — capture, per slice

Canon 6, in the build skill: after each task or slice, append one to three bullets to the
run's learnings file, each tagged with where its fix belongs.

```
[<skill-name>] | [<doc path>] | [instruction-file] | [memory] | [none]
```

Process observations only. Code debt goes to the repository's debt file — it is a
different queue with a different reader. **Without the tags the retro cannot route
them**, and an untagged bullet costs the retro the same reading a transcript would.

The run's setup creates this file empty, so its absence at close is a signal that the
build skill was skipped, not that nothing happened.

## Hop 2 — distil, at close

Before **anything** is torn down, write the note. The run's learnings file dies with the
workspace, so carrying it out first is the whole point.

Location: the plugin's `docs/retro/<id>.md`. Cap ~15 lines — the retro reads these
instead of re-mining transcripts, and a wall of prose costs it exactly what the
transcripts did.

```markdown
# <id> · <slug> · closed <date>
Scale: Medium · slices: 3 · reworked slices: 1

## Friction
- [plan] Plan named a new hook the target already had; the executor built both.
  → the plan stage needs a reuse check against the target repository.
- [none] Backend flake on one endpoint; not process.

## Worked
- Parallel groups on slice 2 — three executors, zero clobbers.
```

Keep each bullet's tag from the learnings file, or assign one here. The `## Worked`
section is not filler: it is what tells the next retro which investments are paying off
and must not be disturbed.

**The note is the gate.** Teardown does not run until the note exists — write it even
when it says "nothing notable". The distillation gate is the reason close is a skill and
not a script call; skipping it starves the retro. The desk role, if the suite has one,
restates the same rule from the other side: closing goes through the close skill, never a
bare delete and never the teardown script alone.

Writing the note is judgment work and stays in the session; running the teardown commands
is executor work.

## Hop 3 — promote, per period

Triggered by an explicit ask, or by accumulation — several closed tasks, or a failure
pattern repeating.

### 1. Read the notes first

`docs/retro/*.md` is, by construction, the **unaddressed** set: everything the last retro
landed has been moved to `docs/retro/applied/`. Read all of the top-level notes. They are
a few hundred lines total, pre-tagged, and written by sessions that knew what actually
hurt. Read the applied directory only to check whether a past fix stuck, never to
re-propose it.

Group the bullets by tag before touching a transcript. That grouping is usually most of
the changelist.

### 2. Sweep transcripts only for what the notes left open

Transcripts cover what sessions did not notice about themselves: failed done-claims,
token burn, corrections that never made it into a note, and every task closed without
one. Scope the sweep to the open questions rather than re-mining the window wholesale.

The gold is in **user text turns** — corrections, re-explanations, rejected tool calls,
anything said twice. Extract those first; read the surrounding assistant context only
around friction already found. Also count error results, compaction events, and delegated
token usage: the scale statistics tell the cost story the quotes do not.

Enumerating and sizing transcript files is mechanical work for an agent two tiers below
the session; the reading briefs carry the full method because each reader starts with no
context; synthesis stays in the session.

### 3. Classify — each kind has a different fix

| Kind | Signal | Fix |
|---|---|---|
| **Knowledge gap** | no rule carries the fact yet | write the fact into the skill, doc, or memory that owns it |
| **Enforcement gap** | the rule exists in writing and was violated anyway | add a **gate** at the point where the violation happens — a required proof, a checkable step, a mechanical check |
| **One-off** | user ambiguity or transient tooling | note it, do not legislate it |

Restating an existing rule louder is the failure mode. If the rule was already written and
still got skipped, more words are not the missing ingredient.

Collect the **counter-examples** as well — the runs that went cleanly and why.

### 4. Diff against existing homes

Before proposing anything, check where each theme already lives: the suite's other
skills, the instruction files, the project's docs, memory. A proposal that duplicates an
existing rule in a second place creates forked rules that drift apart. **Strengthen the
existing home, or move the rule — never fork it.**

### 5. Also diff skills against their seeds, and bindings against reality

Two checks the note-reading pass cannot produce:

- **Seed drift.** Each emitted skill against the general skill it was pressed from. Seeds
  gain gates over time; a suite pressed from an old seed is missing every one of them.
  Carry the improvements across, keeping this project's bindings. This is the one
  sanctioned exception to "no pointer outside the plugin": a seed is named **as a diff
  target only**, never invoked and never depended on. When a seed is not installed, skip
  that row and record the skip — never block the retro on it, and never hard-code a path
  to go looking.
- **Binding rot.** Every path, command and directory the suite names, checked to still
  exist. A renamed docs directory or a moved gate turns a skill into a confident liar, and
  nothing else in the suite looks for this.

### 6. Propose the changelist

Grouped by target so the user approves category by category:

```
### <target: skill / doc / instruction file / memory>
- keep     — <what, and why it is still right>
- update   — <the specific edit, quoted>
- add      — <the new rule or gate, and the violation point it sits at>
- retire   — <what goes, and what replaces it>
- split    — <the blob, and the two skills it becomes>
```

Never propose weakening a gate as the remedy for a check that keeps failing. A repeatedly
failing check is a finding about the code or about the binding, not about the check.

### 7. Apply, version, file

On approval:

1. Apply the approved edits. An unchecked box is a decision, not an oversight to absorb
   silently — ask if it looks accidental.
2. **Bump the plugin version** — minor for an added archetype or a re-wired pipeline,
   patch for a corrected gate or binding.
3. **Write the changelog entry**: version, date, and what changed grouped by skill. This
   is what the next retro diffs against; git history is not what it reads.
4. **File the notes.** A fully-applied note moves to `docs/retro/applied/`. A note whose
   items only partly landed stays at the top level with each landed bullet marked
   `✓ applied <date>`. What remains at the top level is then exactly the unaddressed set,
   which is the invariant the whole chain depends on.

## Cadence

There is no automation here, and that is deliberate — a scheduled retro with nothing to
promote burns a session. The signals worth acting on: several notes accumulated, the same
tag appearing in three notes, a gate-health re-audit showing drift, or the user asking.
The gate-health archetype's schedule is set by the retro; the retro's own schedule is set
by the notes piling up.
