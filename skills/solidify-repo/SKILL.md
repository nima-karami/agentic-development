---
name: solidify-repo
description: Solidify, harden, or prep a repository for human/agent collaboration. Audits a repo against an evidence-based rubric (instruction files, deterministic checks, a one-command verify harness, security gate) and applies fixes with per-category approval. Use when asked to "solidify", "harden", "prep for agents", "make agent-ready", or "audit a repo for AI/human collaboration".
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, WebSearch, WebFetch, AskUserQuestion
---

# Solidify a Repository for Human/Agent Collaboration

This skill prepares the repository in the current working directory so that both
human developers and AI coding agents can work in it effectively. It **audits**,
**reports**, then **applies fixes one category at a time, pausing for your
approval before each one.**

It is **language-agnostic**: detect the stack, then look up the *current* best
concrete tools for that stack with WebSearch rather than assuming a fixed
toolchain. The methodology is fixed; the tools are not.

`references/tooling-2026.md` is a **curated, maintained** per-stack reference
(formatter / linter / dead-code / complexity / duplication / SAST / secret-scan /
dep-audit / verify-harness picks, with consolidation flags and what to avoid). It is
the product of deeper research than an ad-hoc inline search will reproduce, so treat
its tool *selections* as the default — start from them, don't re-derive the toolchain
from scratch. Use WebSearch only to confirm the **current version and maintenance
status** of the chosen tool before installing (the file is dated; versions move).

## Scope (v1 — the four highest-leverage categories)

These four are the most strongly evidence-backed, most commonly-gotten-wrong
moves for agent-readiness. Do not silently expand scope beyond them.

1. **Instruction files** — `AGENTS.md` / `CLAUDE.md` / `.cursorrules` etc.
2. **Deterministic checks** — formatter + linter + dead-code + complexity, in pre-commit/CI.
3. **One-command verify harness** — a single `verify` returning exit 0/1.
4. **Security gate** — three distinct layers, all wired into the harness/CI:
   **SAST** (scans your code), **dependency/supply-chain audit** (scans your
   dependency tree for known-vulnerable packages), and **secret scanning** (catches
   committed credentials). These are not interchangeable — SAST never inspects your
   dependencies.

## Hard rules

- **Refuse to apply changes on a dirty working tree.** Audit is fine; applying is
  not. Tell the user to commit/stash first, so every change you make is reviewable.
- **One category at a time.** Show the plan/diff, get a yes/skip via
  AskUserQuestion, then apply. Never batch all four without consent.
- **Tool selection comes from `references/tooling-2026.md`, not your training.**
  Your training is stale and an inline search won't match the curated reference's
  depth. Take the picks from there; use WebSearch only to confirm each chosen tool's
  current version/maintenance for the detected stack before installing.
- **Self-verify before claiming done.** Run the new `verify` harness and confirm
  it is green. Evidence before assertions.

---

## Step 1 — Detect (read-only)

Run from the repo root. These commands are verified to work:

```bash
echo "--- git clean? (empty = clean; non-empty = DIRTY, do not apply) ---"
git status --porcelain

echo "--- stack manifests ---"
ls | grep -E 'package.json|pyproject.toml|go.mod|Cargo.toml|pom.xml|build.gradle|Gemfile|composer.json|requirements.txt' || echo none

echo "--- instruction files + size (lines) ---"
for f in AGENTS.md CLAUDE.md .cursorrules .github/copilot-instructions.md; do
  [ -f "$f" ] && echo "$f: $(wc -l < "$f") lines"
done

echo "--- CI present? ---"
ls .github/workflows/ 2>/dev/null || echo "no .github/workflows"

echo "--- existing test/lint/verify commands ---"
grep -oE '"(test|lint|verify|check|typecheck)"[[:space:]]*:[[:space:]]*"[^"]*"' package.json 2>/dev/null
[ -f Makefile ] && grep -E '^(test|lint|verify|check):' Makefile
[ -f justfile ] && grep -E '^(test|lint|verify|check):' justfile
```

If the tree is dirty, stop and ask the user to commit/stash before applying.

## Step 2 — Audit the four categories

Score each **Pass / Weak / Missing** with concrete evidence from Step 1.

**1. Instruction files.** Apply the **Discoverability Filter**: a fact an agent
could learn via Glob/Grep/Read in ~10 seconds does not belong in the file. Read
the file and flag every line that is discoverable (folder maps, tech-stack
summaries, "this is a monorepo"). A file over ~30 lines that is mostly structural
description scores **Weak/Missing**. Keep only *non-discoverable operational
gotchas* (build flags, mandatory contracts, timing constraints, "X is deprecated
but still imported").

**2. Deterministic checks.** Detect whether a formatter, linter, dead-code
detector, and complexity check exist and run in pre-commit/CI. Missing any →
**Weak**. None → **Missing**.

**3. Verify harness.** Is there a single command that runs the full check suite
and returns a clean exit code? Scattered/undocumented commands → **Weak**. None →
**Missing**.

**4. Security gate.** Score all **three** layers separately — a repo can have one
and be missing the others:
- **SAST** (e.g. Semgrep) — scans your source for vulnerable patterns.
- **Dependency/supply-chain audit** (e.g. `npm`/`pnpm audit`, OSV-Scanner) — scans
  your dependency tree against advisory DBs. A SAST pass does **not** cover this; a
  repo with Semgrep but no dep audit is still **Missing** this layer.
- **Secret scanning** (e.g. gitleaks) — catches committed credentials.

Any layer absent → **Weak**; none → **Missing**. This is the highest-risk category:
agents produce functionally-correct but insecure code, and pull in vulnerable
packages, far more often than humans — so "tests pass" is not "safe".

## Step 3 — Write the report

Write the report as a table of the four categories with score + evidence + the
specific change you propose for each — the artifact the user reviews before any edits.
Place it at `solidify-report.md` in the repo root, **unless the repo already has a
docs convention** for run artifacts (e.g. a `docs/runs/<date>-<name>/` layout), in
which case follow it rather than dropping a stray file at the root.

## Step 4 — Apply, one category at a time (gated)

For each category scored Weak/Missing, in this order, use **AskUserQuestion** to
get apply/skip, then apply only the approved ones:

1. **Instruction files** → rewrite to pass the Discoverability Filter. Delete
   discoverable content; keep/condense gotchas. Target a short file (~10 lines of
   real gotchas is a healthy result; an empty file is a valid result).
2. **Deterministic checks** → take the formatter/linter/dead-code/complexity/**duplication**
   picks for the detected stack from `references/tooling-2026.md`, `WebSearch` only to
   confirm each one's current version/maintenance, then install them, add config, and
   wire a pre-commit hook + a CI job. Enforce a sane complexity ceiling, and a
   duplication threshold (AI-generated code clones heavily), where supported.
3. **Verify harness** → create or normalize **one** entry point (`make verify`,
   `npm run verify`, or a `justfile` recipe) that runs format-check + lint +
   typecheck + tests + duplication + **security (all three layers below)**, exiting
   non-zero on any failure. Wire it as the CI gate.
4. **Security gate** → add **all three** layers, taking the stack's picks from
   `references/tooling-2026.md` (WebSearch only to confirm versions), and include
   each in the `verify` harness:
   - **SAST** — Semgrep is a strong language-agnostic default. It's the slowest
     layer, so running it in **CI only** (while the fast dep-audit + secret-scan stay
     in the local `verify`) is a fine speed tradeoff — as long as it still gates merges.
   - **Dependency/supply-chain audit** — the stack's native auditor (`npm`/`pnpm
     audit` for JS/TS, `pip-audit`, `govulncheck`, `cargo-audit`, etc.) plus
     OSV-Scanner as a cross-stack baseline. **Do not skip this thinking SAST covers
     it — it does not.**
   - **Secret scanning** — gitleaks (pre-commit + CI diff).

## Step 5 — Self-verify

Run the new `verify` command. Confirm exit 0. If the newly-added linters/SAST
surface pre-existing violations, **report them to the user** — do not silently
suppress rules to force green. Let the user decide: fix now, or baseline.

## Step 6 — Record the decision

Write an ADR to `docs/adr/` (create the dir if needed) capturing what was changed,
which categories were skipped, and why — so the prep is documented where the work
happened. One short file: Context / Decision / Consequences.

---

## Gotchas

- **Adding a linter to an existing repo floods you with violations.** That's
  expected. Separate "wire up the gate" from "fix the backlog" — propose a baseline
  (e.g. lint only changed files, or a ratchet) rather than blocking on a huge fixup.
- **`grep -E` on Windows Git Bash** works, but CRLF line endings can confuse
  size/line checks. `wc -l` is reliable; trust it over `grep -c`.
- **Don't add ports/adapters/hexagonal layering here.** That's tempting "agent
  readiness" theater and out of v1 scope — it adds files without earning their
  keep on most repos. Stick to the four categories.
- **"I added SAST, so security is done" is the trap.** SAST scans your code;
  it is blind to your dependencies. A repo with Semgrep but no `npm audit`/OSV-Scanner
  is wide open to a vulnerable or malicious package, and a repo with both but no
  gitleaks can still leak a committed key. The security gate is **not** satisfied
  until all three layers — SAST, dependency/supply-chain audit, and secret scanning —
  are wired into the harness. Treating any one as "security" is a partial gate.
- **The skill is the methodology; there is no bundled driver.** A language-agnostic
  detector script would go stale immediately — the detection lives in Step 1's
  probes and your judgment + WebSearch, on purpose.
