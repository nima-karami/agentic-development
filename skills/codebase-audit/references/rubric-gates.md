# Rubric — gate respect

Gates are the checks a change must pass: build, type, lint, test, coverage, structural
and architecture rules, required CI jobs. This dimension asks whether they are still
intact, still enforced, and still able to fail. Report **counts, ages and trends**, not
presence — every repo has some suppressions; the finding is the curve.

## The gate manifest

Build one canonical manifest per audit and diff **the manifest**, not the raw CI
files, so a migration that rewrites every line does not hide one semantic change.

| Field | Per gate |
|---|---|
| id | stable name across audits |
| command | exact command and flags |
| workdir | where it runs |
| include / exclude | globs it covers and skips |
| blocking | does a failure stop a merge? (read required checks from the hosting platform, not from source) |
| triggers | events and path filters that start it |
| failure policy | continue-on-error, allow-failure, retries, ignored exit codes, warnings-only |
| thresholds | coverage, max-warnings, mutation score, complexity limits |
| version | tool and config version |

Also record: the agent instruction files' named gate commands, local scripts and
pre-commit hooks, so local and CI can be compared.

## Rows

### G1 · Required gate weakened
- **Finding:** a type, lint, test or architecture job removed, made conditional,
  renamed without an equivalent, or no longer blocking.
- **Detection:** manifest diff against the baseline.
- **Severity:** Critical when unvalidated code can now merge.

### G2 · Failure semantics softened
- **Finding:** continue-on-error, allow-failure, ignored exit codes, retries hiding
  flakes, warnings-only mode, a raised max-warnings.
- **Detection:** manifest failure-policy and threshold fields.
- **Severity:** High.

### G3 · Path filters skip real code
- **Finding:** a gate does not run for files that change behavior. A path-filtered
  workflow that is skipped can also report no status at all.
- **Detection:** compare trigger filters with the source tree.
- **Severity:** High.

### G4 · Suppressions accumulating
- **Finding:** type-ignore, lint-disable and similar comments growing; many with no
  reason; clusters at trust boundaries.
- **Detection:** count by mechanism, directory and age; new-since-baseline list.
- **Severity:** Medium; High when clustered at ingestion points or in core domain.
- **Over-engineering line:** demanding zero suppressions.

### G5 · Skipped and focused tests
- **Finding:** skips, only-flags, expected-failure markers, quarantine lists.
- **Detection:** count with age.
- **Severity:** Medium; High for skips on core or boundary code.

### G6 · Strictness relaxed
- **Finding:** rule severity error → warn → off; compiler strictness flags dropped;
  per-module overrides; growing ignore patterns.
- **Detection:** manifest diff of severities and strictness flags.
- **Severity:** High.

### G7 · Excluded paths growing
- **Finding:** coverage, lint or type excludes widening; test globs that stopped
  matching after files moved, so a suite silently runs fewer tests.
- **Detection:** diff include/exclude sets; check every glob still matches files.
- **Severity:** High when production code fell out of a gate.
- **Over-engineering line:** excluding generated code is fine.

### G8 · Local gate differs from CI
- **Finding:** scripts, hooks or the agent instruction file name a weaker or different
  command than CI runs. Agents run the gate they are told about.
- **Detection:** compare commands and flags across scripts, hooks, instruction files
  and CI.
- **Severity:** High.

### G9 · Allowlists without owners
- **Finding:** baseline or accepted-violation files growing with no owner, reason or
  expiry.
- **Detection:** diff size and metadata.
- **Severity:** Medium.

### G10 · Tests that cannot constrain
- **Finding:** methods whose tests still pass with the body removed; zero-assertion or
  snapshot-only tests on logic; a mock that replaced the subject under test.
- **Detection:** the test-strength funnel below.
- **Severity:** High on core and boundary code; Medium elsewhere.
- **Over-engineering line:** chasing a perfect mutation score — equivalent mutants make
  it a bad target.

### G11 · Test edits inside implementation commits
- **Finding:** deleted assertions, loosened expectations, rewritten snapshots in the
  same commit as the code they judge.
- **Detection:** history scan for commits touching both.
- **Severity:** a **hypothesis signal**, not a finding, until a human or verifier reads
  the commit. Cheap to compute; weight it more in agent-heavy repos.

### G12 · Instruction file as a gate
- **Finding:** the agent instruction file names stale commands, paths or rules.
- **Detection:** every command and path it names is resolved against the tree.
- **Severity:** High — it is the most-read and least-maintained gate in an agent repo.

## The test-strength funnel

Coverage says a line ran, not that a test would notice it breaking. Never score covered
code as well tested.

1. **Screen.** Use coverage only to find eligible code with no tests at all.
2. **Pseudo-tested methods.** In an isolated worktree at the pinned commit — never the
   audited checkout; link the existing dependency directory instead of installing, and
   unlink it before removing the worktree — empty each sampled method's body or
   return a default value, run only the tests that import its module, restore. If they still pass, the method is
   pseudo-tested. One mutant per method: the cheapest strong signal, and it needs no
   tooling.
3. **Targeted mutation.** Where the stack has a mutation tool, run regular mutation on
   the fixed sample only, using per-test coverage and incremental modes to keep it
   affordable.
4. **Triage survivors.** A human or verifier dismisses equivalent and
   implementation-detail mutants.
5. **Record three numbers:** eligible-but-untested count, pseudo-tested survivors,
   kill rate on the fixed sample — plus the sample's file list.

**The fixed sample** is chosen once and kept across audits: top hotspots, core domain,
trust boundaries, code under gates relaxed since the last audit, code changed since
the last audit. Store it outside the agent-editable path or alert on its change.
