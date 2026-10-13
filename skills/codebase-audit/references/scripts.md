# Bundled scripts

Stack-neutral, standard-library Python 3.9+ in the skill's `scripts/` directory. Use
them before writing anything by hand: they are the same on every run, which is what
makes drift measurable. Stack-specific extraction (import graphs, AST inventories) and
third-party tools are not bundled — see `scans.md`.

**Pass this file to every agent that runs a script**, with the skill's absolute path
filled in, so the agent calls `python -I <skill>/scripts/<name>.py` from the audited
repo (or with `--repo`).

## The contract

- **`--help` is the documentation**: what it computes and why, every argument with its
  default, a glossary of the output's `data` fields, caveats, and examples. Read it
  before the first run; for scripts with subcommands, read the subcommand's help
  (`patterns.py scan --help`).
- **Common flags go after the subcommand**: `--repo` (where it applies), `--out FILE`,
  `--format json|text`, `-v` (each step on stderr), `-vv` (also every git command with
  timing), `--debug` (traceback on failure), `--version`.
- **Output** is a JSON envelope: `tool`, `version`, `command`, `args`, `repo` (path,
  head, dirty files), `generated_at`, `duration_s`, `warnings`, `data`. `data` is
  deterministic — same inputs, byte-identical result.
- **Read `warnings` before `data`.** They carry everything that changes how to read the
  numbers: shallow history, a heuristic applied, files skipped, a cap that truncated a
  list, a glob that matched nothing.
- **Exit codes**: 0 ok · 1 a `--fail-on-*` condition was found · 2 usage · 3
  environment (git, paths, a failed command) · 4 input (missing or malformed file).
  Errors print a `hint:` line.
- **Save the exact command** you ran under the run's `work/scripts/commands.md`, and the
  output under `work/facts/`.

## Diagnosing a run

1. Nonzero exit: read the `error:` and `hint:` lines; rerun with `-vv` to see each git
   command and how long it took.
2. A number looks wrong: rerun with `-v` to see what was read, filtered and skipped;
   check the envelope's `args` (did the globs select what you meant?) and `warnings`.
3. A field's meaning is unclear: the help's field glossary; for baselines,
   `baseline.py explain FIELD`.
4. A pattern count looks wrong: `patterns.py show-pack NAME` lists exactly what is
   matched; `--max-hits` and the `hits` list show the anchors to spot-check.

## Catalogue

| Script | Who runs it | For |
|---|---|---|
| `fingerprint.py` | orchestrator, step 0 | scope fingerprint, profile hash, scope comparability |
| `history.py` | history extractor | churn, approximate complexity, hotspots, co-change, author classes, test-or-gate edits inside code commits |
| `patterns.py` + `packs/` | gates, security and performance extractors | anchored counts with ages: suppressions, skips, escape hatches, permissive flags, failure policy, timers, sync I/O |
| `manifest.py` | gates extractor | gate manifest validate / hash / diff (weakenings flagged); candidate relaxations in gate-config history |
| `isolate.py` | test strength, measurement | isolated worktree with linked dependencies, created and removed safely |
| `amplify.py` | performance extractor, judges | polling, broadcast, pool, memory and fan-out arithmetic from profile numbers — the only source of a `computed` status |
| `baseline.py` | baseline assembler, orchestrator | validate a baseline; compare two into deltas, ratchet breaches and trend; explain a field |

### fingerprint.py — `scope`, `profile`, `compare`

```
python -I <skill>/scripts/fingerprint.py scope --repo . --commit HEAD --include "src/**" --exclude "**/*.test.*" --tool node=v24.13.0
python -I <skill>/scripts/fingerprint.py profile docs/audits/<run>/profile.md
python -I <skill>/scripts/fingerprint.py compare old-scope.json new-scope.json --fail-on-incomparable
```

`compare` ignores the commit (a re-audit is expected at a newer one) and reports it as
`commit_changed`; any change to include, exclude, tools or extras makes the scopes not
comparable. The profile hash ignores `Source:` and `Confirmed by:` lines and the Scope
and Audit plan sections.

### history.py

```
python -I <skill>/scripts/history.py --repo . --include "src/**" --exclude "**/*.test.*" --out work/facts/history.json
python -I <skill>/scripts/history.py --repo . --range <base>..<head> --sections churn,authors,test-gate
python -I <skill>/scripts/history.py --repo . --module-map modules.json --sections cochange
```

Complexity is a language-neutral token count; files of unknown type fall back to line
counts and are flagged — exclude stylesheets and data files from hotspot ranking.
Author classes come from configurable regexes; the default agent pattern matches
co-author and assisted-by trailers. Merge commits are skipped. Test-or-gate edits are a
hypothesis signal for a judge, never a finding.

### patterns.py — `scan`, `list-packs`, `show-pack`, `first-seen`

```
python -I <skill>/scripts/patterns.py scan --repo . --pack suppressions --pack escape-hatches --blame --out work/facts/patterns.json
python -I <skill>/scripts/patterns.py scan --repo . --pack escape-hatches --focus-file work/facts/ingestion.txt
python -I <skill>/scripts/patterns.py scan --repo . --pack skips --tests only --group-by dir,age
python -I <skill>/scripts/patterns.py first-seen --repo . --pack permissive-flags --pattern-id <id>
```

Packs: `suppressions`, `skips`, `escape-hatches`, `permissive-flags`, `failure-policy`,
`timers`, `sync-io`; a project-specific pack is any JSON file in the same format (see
`scan --help`). Tests are excluded by default and counted separately. `--focus-file`
takes `path` or `path:start-end` lines (entry points from the inventories extractor).
Ages are relative to the HEAD commit date. `first-seen` is slow; cap it with `--max`.

### manifest.py — `validate`, `hash`, `diff`, `config-history`

```
python -I <skill>/scripts/manifest.py validate work/facts/gate-manifest.json
python -I <skill>/scripts/manifest.py diff <baseline-run>/work/facts/gate-manifest.json work/facts/gate-manifest.json --fail-on-weakening
python -I <skill>/scripts/manifest.py config-history --repo . --path "biome.json" ".github/workflows/**" "tsconfig*.json"
```

The agent builds the manifest (fields in `rubric-gates.md`); the script makes it
comparable. `diff --help` lists the weakening rule per field. `config-history` returns
candidate relaxations — labelled candidates, including expected noise such as
excluding dependency directories.

### isolate.py — `create`, `status`, `remove`

```
python -I <skill>/scripts/isolate.py create --repo . --commit <sha> --dest <OS-temp>/audit-wt --link node_modules --dry-run
python -I <skill>/scripts/isolate.py status --dest <OS-temp>/audit-wt
python -I <skill>/scripts/isolate.py remove --dest <OS-temp>/audit-wt
```

The only script that writes, and only outside the audited checkout. Links are
junctions on Windows and symlinks elsewhere — never copies, never installs. `remove`
unlinks every link before any git call and aborts if a link target changes. Run
`status` before and after the work and confirm the source repo's status is unchanged.
Exit 4 is a refusal (non-empty destination, destination inside the repo, missing link
target, no marker).

### amplify.py — `poll`, `broadcast`, `pool`, `memory`, `fanout`, `batch`

```
python -I <skill>/scripts/amplify.py poll --clients 100000 --interval-s 2 --budget-rps 20000 --format text
python -I <skill>/scripts/amplify.py pool --rate-rps 5000 --latency-ms 40 --pool-size 20 --instances 8 --db-max-connections 100
python -I <skill>/scripts/amplify.py batch --file work/facts/scenarios.json --out work/facts/amplify.json
```

Every result shows the formula with values substituted, and `computed: breach | ok |
no-budget`. Inputs come from the profile or from a measurement — `memory` refuses to
run without a measured bytes-per-connection. `batch` takes a list of
`{"calc", "args", "label"}` so the performance extractor computes everything in one
call.

### baseline.py — `validate`, `compare`, `explain`

```
python -I <skill>/scripts/baseline.py validate docs/audits/baseline.json
python -I <skill>/scripts/baseline.py compare <old>/baseline.json docs/audits/baseline.json --fail-on-breach --format text
python -I <skill>/scripts/baseline.py explain gates.debt.suppressions
```

`compare` implements the drift rules in `baseline.md`: profile and scope comparability
first, then per-field old / new / delta / direction, ratchet breaches (each marked
`trusted: false` when the comparison is not like-for-like), per-dimension trend, and
expired accepted exceptions. Comparing a `run`-mode baseline with a whole-repo one is
refused unless `--force`.
