# Canon — copy this text, do not paraphrase

Every emitted skill carries the canon items relevant to its stage, **verbatim**.
Identical wording is not a style preference: it is what lets a later retro find every
copy of a rule with one search, and what stops nine skills from drifting into nine
slightly different versions of the same gate.

Copy the numbered text below into the emitted skill's **Hard rules** section, then add
the project bindings from the second half of this file underneath.

## When an item asserts something this project does not have

Some items name a thing the project may lack — item 5 assumes a scripts directory, item 6
assumes a learnings file. **Never edit the item to fit.** Append a **project clause**
after the verbatim text, separated by ` — Project: `:

```
5. **Script over manual.** …one-offs go to the OS temp dir. Agents default to doing
   everything by hand; that costs tokens and wall-clock. — Project: this repository has
   no scripts directory yet; until it does, durable candidates are listed in the
   plugin's script-candidates file rather than written.
```

The separator matters: the canon text ahead of it is still byte-identical, so one search
for the canon wording still finds every copy across the suite, and one search for
` — Project: ` finds every place a project had to qualify it. A clause may narrow, defer,
or redirect an item; it may never weaken a gate the item sets. If the item is wrong for
this project in a way no clause can rescue, that is a finding, not an edit.

A convention the suite *introduces* rather than observes — the learnings file being the
usual one — is a project clause plus an entry in discovery's fifth inventory, so it lands
in the proposal file as an addition rather than being asserted as a fact.

---

## The nine

1. **Gate integrity.** Never weaken, narrow, mock out, skip, or defer a gate to get
   green. Gates are development discipline, not production-only. A gamed gate is a
   failed task.

2. **Done-claim gate.** No "done", "fixed", "passing", or "wired" without: the gate
   command run in this turn with its exit code captured directly (never through a
   pipe or pager); runtime proof for any user-facing behavior; the change list
   diffed against the plan. A report missing any of these bounces.

3. **Evidence rules.** A consistency claim requires a full search, not spot checks. A
   negative claim ("nothing uses X") requires a recursive search including ignored
   and hidden directories. Deleting as dead requires proving zero consumers through
   indirection. A claim about current behavior requires measurement, not inference
   from source. A regression claim requires reproducing at the pre-change baseline
   first.

4. **Model tier rule.** The session holds decisions. Judgment-heavy delegated work
   runs one tier below the session; mechanical work two tiers below, with a floor at
   the mid tier; never delegate upward. The bottom tier never builds against slow or
   flaky suites and never writes a root-cause diagnosis.

5. **Script over manual.** When a routine is mechanical and will repeat — the same
   shape of tool call more than a handful of times, or the same setup/teardown twice
   — write a script that takes arguments and run it instead. Durable scripts go in
   the project's scripts directory; one-offs go to the OS temp dir. Agents default to
   doing everything by hand; that costs tokens and wall-clock.

6. **Learnings capture.** After each task or slice, append one to three bullets to
   the run's learnings file, each tagged with where its fix belongs:
   `[<skill-name>]`, `[<doc path>]`, `[instruction-file]`, `[memory]`, or `[none]`.
   Process observations only; code debt goes to the repository's debt file. Without
   the tags the retro cannot route them.

7. **Concurrency hygiene.** Never run the full gate under concurrent subagent load.
   Never share temp or browser-profile directories across sessions. Never kill
   processes by image name. Verify a worktree's base commit before building on it.
   Never install dependencies in a directory you have not verified is the intended
   one.

8. **Over-production is a defect.** Triage before producing. A stage whose artifact
   would restate the previous stage's artifact at lower fidelity is skipped and the
   skip recorded.

9. **Settled decisions travel forward and are never re-litigated downstream.** A
   downstream stage that finds a settled decision genuinely broken says so and
   re-locks with the user (or, unattended, records a `Decisions Needed` item); it
   never silently adapts.

## Which archetypes carry which items

| Archetype | Canon items to inject |
|---|---|
| manage | 4, 5, 8 |
| start | 3, 4, 5, 8, 9 |
| spec | 3, 8, 9 |
| plan | 5, 8, 9 |
| design-review | 8, 9 |
| build | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| code-review | 1, 3, 8, 9 |
| qa | 1, 2, 3, 5, 7 |
| deliver | 1, 2, 3 |
| close | 3, 6 |
| gate-health | 1, 3, 8 |
| loop | all nine |
| retro | 3, 6, 8 |

`close` carries item 3 because its own gates — every branch an ancestor of the mainline,
a last commit that is the user's — are evidence claims about current state made
immediately before an irreversible delete, which is exactly what item 3 governs.

Injecting an item a stage cannot act on is noise; leaving one out where the stage can
violate it is the gap. When in doubt, inject — a stage that carries a rule it never
needs costs a few lines, a stage missing the rule it needed costs a run.

## The project-binding block

Under the canon, every emitted skill states the project's own bindings, phrased
identically across the suite. Fill from the discovery profile; drop lines the skill's
stage genuinely cannot use, and say in the skill which ones were dropped and why.

**It is always inline, in every skill, never behind a shared reference** — a pointer is
exactly what the agent skips, and identical wording is what lets one search find every
copy when a binding changes. Like the canon, it does not count against the body budget.

```
- Gate command: <exact command>, run from <where>, exit code read directly.
- Artifacts: specs at <path>; plans at <path>; run/ticket state at <path>;
  evidence at <path>; learnings at <path>.
- Branch: <naming rule>.  Commit subject: <shape>.  <trailer policy>
- "Done" here means: <the project's bar>.
- Read-when: <trigger> → <doc path>; <trigger> → <doc path>.
- Delegation: judgment work one tier below this session, mechanical work two below
  with a floor at the mid tier, never above the session.
```

## Model tier reference (names live here, never in a skill body)

| Tier | Models | Use |
|---|---|---|
| top | Fable | session/conductor judgment only; never product code, never content generation |
| high | Opus | judgment work: specs, plans, reviews, builders on real suites |
| mid | Sonnet | mechanical: transcript reading, file moves, fixtures, desk/dispatch sessions |
| low | Haiku | bulk classification only |

Field evidence behind the tiers: a mid-tier builder spun ~30 minutes stuck on an
end-to-end suite (banned as a builder since); mid-tier spec writers produced
confidently wrong root causes; the top tier was mis-used once for a 126-word content
task. A desk/manager session is the one role that runs happily at the mid tier — it
dispatches and files, and never reads source.

**Tiers are relative to the session, not absolute.** An emitted skill says "one tier
below this session", never a model name — the same suite must work when the user runs
it from a cheaper session.
