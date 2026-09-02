# Project discovery

The goal of discovery is a **project profile**: the durable facts every generated
skill will cite. Skills are only as good as this profile, so read widely, then
distill, then show it to the user before generating anything.

## What to read (in order)

1. **Every `CLAUDE.md` and `AGENTS.md` up the whole tree.** A repo checked out under a
   workspace inherits the parent's rules — the parent carries cross-repo conventions the
   repo can't see, the repo-local one carries its own toolchain. Read *both*, never just
   the nearest. Start at the working directory and walk up to the drive root and to
   `~/.claude/CLAUDE.md`.
2. **The docs read-when index.** Most matured projects keep a `docs/` with an index
   ("read this file when your task matches this trigger"). That index *is* the project's
   own map of where knowledge lives — it tells you which docs a generated skill should
   point its future user at. Capture the index, not the contents.
3. **Existing skills.** Any `start-<project>-task`, review, deploy skill already in
   `~/.claude/skills/` or `<repo>/.claude/skills/`. These are prior art — they show the
   voice, the conventions already captured, and what's missing. In evolve mode they're
   the baseline you diff against.
4. **Git conventions.** `git log --oneline -50` and a few full messages: branch naming,
   commit-subject format (ticket prefix? conventional commits?), how PRs are described.
   These become the kickoff/review skills' rules. Read the *pattern*, never copy an
   instance.
5. **Memory and tickets.** Any `MEMORY.md` / auto-memory and local ticket/plan files
   (`docs/tickets/`, `docs/plans/`). They reveal in-flight work, the "done" bar, and
   decisions not visible in code.
6. **The tooling loop.** How the project builds, tests, serves, and verifies — the
   `package.json` scripts, a `verify` command, a dev-server convention, a staging/preview
   flow. Deploy and execution skills need this exact.
7. **Recent session transcripts, when they exist.** The JSONL under
   `~/.claude/projects/<dir>/` is the strongest evidence of what the suite must gate:
   user corrections, re-explanations, and rejected tool calls mark exactly where generic
   behavior failed this project. Mine user text turns first (cheap-model readers for
   bulk), rank friction by cost, and classify each finding as a knowledge gap (bake the
   fact in) or an enforcement gap (bake a gate in). A rule the user had to state twice
   in transcripts is a rule the suite must enforce, not merely mention.

Fan out subagents for breadth when the project is large or unfamiliar; read directly
when it's small. Stop when you could write the profile and defend it — not when you've
read everything.

## The profile to produce

Distill what you read into a short, cite-able profile. Keep it factual and durable —
conventions, not instances. Show it to the user to correct before generating.

```
## <Project> profile

- Repos / ownership:  <repo> owns <X>; <repo> owns <Y>; … (or "single repo")
- Workspace shape:    single-repo | multi-repo workspace | monorepo
- Branch convention:  <e.g. feature/<TICKET>-<slug>, ticket = real JIRA key>
- Commit convention:  <e.g. "TICKET: Capitalized imperative subject", no AI trailer>
- Docs map:           <the read-when index: which doc for which task>
- "Done" bar:         <what verify/test/review must pass; the quality standard>
- Tooling loop:       <build / test / serve / verify / deploy commands and order>
- Cross-cutting rules:<invariants a skill must not violate — e.g. "no sibling imports">
- Failure patterns:   <recurring friction from transcripts/retro, each tagged
                       knowledge-gap or enforcement-gap, with the gate it implies>
- Existing skills:    <what's already there, generic or project-specific>
- Gaps to interview:  <what you could NOT infer and must ask the user>
```

## Interview only for the gaps

Everything inferable from the reads above, infer — don't ask. Ask only what changes what
you'd generate: an ambiguous ownership boundary, a "done" bar the docs don't state, which
archetypes the project actually wants. Batch 2–4 questions with a recommendation each,
never a long interrogation. A convention you can read from `git log` is not a question.
