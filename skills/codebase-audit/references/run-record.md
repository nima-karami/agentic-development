# Run record

The report is the merged result; the run record is **everything the audit produced**,
kept so a human can check the merge, find what the judges dismissed, and see what no
agent ever looked at. Nothing an agent produces is discarded, and the merge never
edits an agent's output.

## Layout

```
docs/audits/<date>-<mode>/
  report.md         merged findings, decisions, task list (the orchestrator writes it)
  review.md         the human review index (record.py index generates it)
  profile.md
  ledger.jsonl      one line per event, appended with record.py log
  work/
    briefs/         the exact brief sent to each agent: <seq>-<role>-<slug>.md
    summaries/      exactly what each agent returned: <seq>-<role>-<slug>.md
    scripts/        scripts written for this run + commands.md (every command run)
    facts/          extractor outputs (JSON envelopes and summaries)
    intent.md  tests.md
    findings/       raw judge output, never edited
    measurements/   measurement output
    verdicts/       verifier output, never edited
    merge.md        every raw finding's disposition in the merge
```

## Rules

1. **Append-only.** Nothing under `work/` is deleted or rewritten after its agent
   finishes. A correction is a new file that names the one it corrects.
2. **Log every dispatch, twice.** Before dispatching: `record.py log dispatch` with the
   role, tier, model, brief path and inputs. After it returns: `record.py log done`
   with the outputs, status (`ok | failed | empty | partial`) and duration. Save the
   brief before dispatch and the agent's reply after. A failed or empty agent is
   recorded, never silently re-run.
3. **Log every script run** (`record.py log script`) with the command, exit code and
   output path, and copy the command into `work/scripts/commands.md`.
4. **Every candidate gets a disposition.** Each judge's file ends with a `Dismissed`
   list (candidate → reason) and a `Not assessed` list (with the reason: out of sample,
   row ruled out by the profile, profile-blocked, could not read). Candidates in the
   facts that no judge received are counted by `record.py index` as **unreviewed**.
5. **Every raw finding gets a merge line** in `work/merge.md`:

   | Raw ID | Disposition | Merged as | Reason |
   |---|---|---|---|
   | F-contracts-api-3 | merged | H1 | same root cause as F-contracts-api-1 |
   | F-verbosity-ui-7 | dropped | — | unanchored |
   | F-security-ipc-2 | refuted | — | verdicts/F-security-ipc-2.md |
   | F-architecture-core-4 | downgraded | M6 | verifier: guard at path:line |

   Dispositions: `merged`, `kept` (became its own merged finding), `downgraded`,
   `refuted`, `dropped` (with reason), `duplicate` (of which raw ID).
6. **The report links back.** Each merged finding lists its raw IDs, and the report
   ends with a pointer to `review.md`.

## record.py

```
record.py log dispatch --run DIR --role judge --wave 3 --tier judgment --model opus --brief work/briefs/12-judge-contracts-api.md --input work/facts/inventories.json ...
record.py log done     --run DIR --seq 12 --status ok --output work/findings/contracts-api.md --summary work/summaries/12-judge-contracts-api.md
record.py log script   --run DIR --command "python -I …/history.py …" --exit 0 --output work/facts/history.json
record.py log note     --run DIR --text "…"            # an orchestrator decision worth keeping
record.py index --run DIR                                # writes review.md and index.json
record.py check --run DIR --fail-on-gaps                 # exit 1 on any gap below
```

`check` reports, as gaps: a dispatch with no `done`; a `done` with no summary file; a
raw finding with no merge line; a merge line pointing at a missing file; a judge file
without `Dismissed` or `Not assessed` sections; a verdict for a finding that is not in
`merge.md`; a script run with a nonzero exit and no note explaining it. **Run `check`
before writing the handoff block; an audit with gaps is not finished.**

## review.md — what a human sees

Generated, never hand-written. Sections, in order:

1. **Run** — mode, depth, commit, profile hash, agents dispatched by role and model,
   failed or empty agents, total script runs, gaps from `check`.
2. **Worth a human look** — the items most likely to hide a missed problem:
   - findings refuted or downgraded by a verifier, High and above first;
   - dismissed candidates that sit in a hotspot, on an entry point, or on a stakes
     path from the profile;
   - low-confidence findings of any severity;
   - authority conflicts;
   - performance candidates left `candidate (unmeasured)`;
   - `Not assessed` entries, grouped by reason;
   - unreviewed candidates — produced by an extractor, never given to a judge —
     counted per extractor and dimension;
   - script warnings (from every envelope's `warnings`).
3. **Merge trace** — every raw finding → disposition → merged ID, from `merge.md`.
4. **Agents** — the ledger as a table: seq, wave, role, model, status, duration, brief,
   summary, outputs.
5. **Files** — every file in the run directory with its size, so nothing is hidden.
