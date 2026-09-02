# The executor brief

One brief per parallel group. All of a slice's briefs go out in a single message.

A subagent inherits nothing: not the plan, not the conversation, not the workspace
path, not the settled decisions. Everything it needs is in the brief or it does not
exist. A brief that names a bare repository name instead of a full path sends the
executor to the main checkout on the default branch, where it commits to the wrong
tree.

## Template

```
## Workspace
Work only inside: <absolute path to the workspace>
Repository/package inside it: <name or subpath>
Branch: <branch name>   Base commit: <sha>
Verify the base commit before your first command. Every mutating command
(install, build, test, generate, delete) runs inside that path and nowhere else.

## Your tasks
<verbatim task text from the plan for this group — not a paraphrase>

## Inputs you consume
<the outputs other tasks produce that yours depend on: exact names, shapes, paths>

## File map for your files
<the plan's create/modify/delete entries for your files, with the one-line purpose each>

## Settled decisions (do not re-open)
<the locked decisions that bear on these tasks>

## How to check your work
<the plan's named check(s) for these tasks — the exact command>
Run only these. Do not run the full gate; the session runs it once at the end.

## Plan fidelity (mandatory)
Before you hand your group back, diff your whole change list against the files and
shapes the plan names for your tasks. Anything extra — especially any touch on
shared or foundational code the plan didn't name, or on a file another group owns —
is a stop-and-report, not a judgment call. Report the mismatch; do not absorb it.
A file created at a path the file map doesn't name stops you where you stand: report
it, never relocate it on your own judgment, never park it somewhere sensible for now.

## Deviation rule
If an assumption turns out wrong — the piece you build on is misaligned, a locked
signature doesn't fit reality — stop. Fixing the misaligned piece becomes the task,
and it is the session's call, not yours. Never bridge: no shim, adapter, second copy,
special case, catch-and-default, widened type, or fallback to route around the real
problem; no patching a leaf or derived value when the defect is in the source it
derives from. Lead your report with the fix that keeps the locked decision.

## Tests
A new test is shown failing before the fix exists, and the red must be an assertion
red: a missing-module or import error says nothing about the assertion, so observe the
red against present-but-wrong code. An import-red counts only for the step that creates
the file, and an assertion-red follows once it exists. Every fix is mutation-verified:
revert it, confirm the new test goes red, restore it. Report both observations.

## Evidence
Claims need evidence, not inference. A consistency claim needs a full search, not
spot checks; a negative claim needs a recursive search including ignored and hidden
directories; a claim about current behavior needs measurement; a regression claim
needs reproducing at the pre-change baseline. Attach the command and its output.

## Comments
Write zero comments by default. Before reporting done, re-read your own diff and
delete every comment that narrates, restates the line below it, or explains the
change. A comment survives only as a non-visible why, a load-bearing invariant, or a
published-API doc comment. Your report states `comments added: 0` or quotes each
survivor with its class.

## Report back
- change list (every path, marked new/modified/deleted)
- the named check's command, its exit code captured directly, and its output
- red-then-green and mutation-verify observations
- deviations, each as: what the plan said / what you found / the fix that keeps the
  locked decision
- anything you could not do, and why
Do not commit unless the brief says to. Do not push, merge, or open a request.
```

## Rules for writing briefs

- **Cite, don't recall.** State a code fact only with a `file:line` from a read that
  happened this session. A claim relayed from a report or from memory becomes a check
  the executor runs before building on it — restated-but-unverified claims were wrong
  three times in a single ticket, each caught downstream, never by the session.
- **Carry the file map, not a summary of it.** The fidelity diff is only as good as
  the list it diffs against.
- **Name the workspace path absolutely.** Never a repository name, never a relative
  path, never "the worktree".
- **One group per brief.** Two groups in one brief re-serializes them by hand and
  loses the disjointness the plan proved.
- **No architecture, no taste.** A brief never asks an executor to decide a boundary,
  an abstraction, an API shape, a name, or a UX call.
