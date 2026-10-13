#!/usr/bin/env python3
"""Git-history extractor: churn, complexity, hotspots, co-change, author classes."""

from __future__ import annotations

import collections
import itertools
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402

CLASSES = ("human", "agent", "bot", "formatter", "dependency-update")
SECTIONS = ("churn", "complexity", "hotspots", "cochange", "authors", "test-gate")

DEFAULT_AGENT_PATTERN = (
    r"^(?:co-authored-by|assisted-by)\s*:.*\b(?:claude|copilot|codex|cursor|devin|gemini|aider|openhands)\b"
)
DEFAULT_BOT_PATTERN = r"\[bot\]|dependabot|renovate|github-actions"
DEFAULT_FORMATTER_PATTERN = (
    r"\b(?:prettier|reformat\w*|auto-?format\w*|format(?:ting)? (?:code|files|all)|lint[: -]*fix|"
    r"eslint --fix|biome (?:format|check)|gofmt|rustfmt|cargo fmt|autofix)\b|^style(?:\([^)]*\))?!?:"
)
DEFAULT_DEPS_PATTERN = (
    r"\b(?:bump|bumps|bumped|dependabot|renovate|lock ?file|deps|update dependenc\w*|"
    r"upgrade dependenc\w*)\b|^(?:chore|build)\(deps"
)
DEFAULT_TEST_GLOBS = [
    "**/test/**", "**/tests/**", "**/__tests__/**", "**/__snapshots__/**", "**/e2e/**",
    "**/*.test.*", "**/*.spec.*", "**/*_test.*", "**/test_*.*", "**/*Test.*", "**/*Tests.*", "**/*.snap",
]
DEFAULT_GATE_GLOBS = [
    ".github/**", ".gitlab-ci.yml", ".circleci/**", "azure-pipelines.yml", "bitbucket-pipelines.yml",
    "Jenkinsfile", ".pre-commit-config.yaml", ".husky/**", "lefthook.yml",
    "**/tsconfig*.json", "**/.eslintrc*", "**/eslint.config.*", "**/biome.json*", "**/.prettierrc*",
    "**/vitest.config.*", "**/jest.config.*", "**/pytest.ini", "**/tox.ini", "**/mypy.ini",
    "**/ruff.toml", "**/.ruff.toml", "**/.golangci.*", "**/package.json", "**/pyproject.toml",
    "**/Makefile",
]
NON_IMPL_GLOBS = [
    "**/*.md", "**/*.txt", "**/*.lock", "**/package-lock.json", "**/pnpm-lock.yaml", "**/yarn.lock",
    "**/*.png", "**/*.jpg", "**/*.jpeg", "**/*.gif", "**/*.svg", "**/*.ico", "**/*.pdf", "**/LICENSE*",
]

C_LIKE_EXT = {
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".java", ".js", ".jsx", ".mjs", ".cjs", ".ts",
    ".tsx", ".mts", ".cts", ".go", ".rs", ".cs", ".kt", ".kts", ".swift", ".scala", ".php", ".dart",
    ".m", ".mm", ".groovy", ".vue", ".svelte",
}
PYTHON_EXT = {".py", ".pyi"}
SHELL_EXT = {".sh", ".bash", ".zsh", ".ksh"}

_C_STRIP = re.compile(
    r"//[^\n]*|/\*.*?\*/|\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`", re.S
)
_PY_STRIP = re.compile(
    r"#[^\n]*|\"\"\".*?\"\"\"|'''.*?'''|\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'", re.S
)
_SH_STRIP = re.compile(r"(?:(?<=\s)|^)#[^\n]*|\"(?:\\.|[^\"\\])*\"|'[^']*'", re.S | re.M)
_C_TOKENS = re.compile(r"\b(?:if|for|while|case|catch)\b|&&|\|\||\?\?|\?(?![.:?])")
_PY_TOKENS = re.compile(r"\b(?:if|elif|for|while|except|case|and|or)\b")
_SH_TOKENS = re.compile(r"\b(?:if|elif|for|while|until|case)\b|&&|\|\|")

FAMILIES = {
    "c-like": (_C_STRIP, _C_TOKENS),
    "python": (_PY_STRIP, _PY_TOKENS),
    "shell": (_SH_STRIP, _SH_TOKENS),
}

DESCRIPTION = """\
Mine git history for the signals the architecture and gate rubrics rank by (A3
hotspots, A4 hidden coupling, G11 test edits inside implementation commits). It reads
only `git log` and the checked-out files; nothing is written to the repository.

What it computes (choose with --sections):
  churn       commits, lines added and deleted per file, rename-aware (git log -M,
              old paths mapped to their HEAD name, time-aware). Merge commits are
              skipped. Files deleted at HEAD are reported separately.
  complexity  per file at HEAD, working tree. --complexity tokens: 1 + count of branch
              tokens (if for while case catch except elif && || ?? ? and or) after
              stripping comments and strings heuristically for C-like, Python and shell
              syntax by extension; other extensions fall back to non-blank lines.
              lines: non-blank lines. none: complexity 1 (score = commits).
  hotspots    score = commits x complexity, ranked; the top --hotspot-pct percent are
              flagged. Recomputed excluding --exclude-classes and for human-only.
  cochange    file pairs and module pairs that change in the same commit across a
              module boundary: shared commits, and shared / commits of the less-changed
              side. Commits touching more than --bulk-threshold files are excluded and
              counted. module = first --module-depth directory segments of the path
              (src/foo/x.ts -> src/foo; src/x.ts -> src) or --module-map.
  authors     every commit is classified human / agent / bot / formatter /
              dependency-update; first matching rule wins in this order: agent
              (full message incl. trailers), bot (author name/email), formatter
              (subject), dependency-update (subject), else human.
  test-gate   commits touching a test file or a gate/config file AND an implementation
              file. A HYPOTHESIS signal for G11: read the commit before calling it a
              finding. Package-manifest changes count as gate edits even when only
              dependencies changed; script sections cannot be told apart.

Window: --range base..head (run mode) or --since; otherwise the whole history. A
shallow clone is warned about because every number is then truncated.

data fields:
  window               first/last commit dates, commits analysed, range/since, shallow
  method               how each number was derived and its limits
  authors              counts_by_class, rules (pattern + examples per class), identities
  files                per file: commits, added, deleted, complexity, complexity_basis
                       (tokens|lines|none), loc, score, rank, hotspot, module, by_class
  hotspots             top --top for all / excluding_classes / human_only, plus the
                       hotspot cutoff size per list
  cochange_files       pairs: a, b, module_a, module_b, shared, commits_a, commits_b, ratio
  cochange_modules     same at module level
  test_gate_with_impl  total, shown, truncated, commits: sha, date, subject, class,
                       rule, files_in_commit, bulk, test_files, gate_files, impl_files
  excluded_bulk_commits  threshold, count, commits (capped by --max-list)
  deleted_at_head      files seen in history but absent at HEAD, with their churn

Caveats: churn counts commits, not effort. Token complexity is an approximation (no
parser; `?` in nullable types and regex literals add noise) and unknown extensions are
scored by line count, so scores mix scales (see complexity_basis). Rename detection is
git's similarity heuristic. Complexity is read from the working tree, not --range head.
Class rules are heuristics over messages, not identity proof.
"""

EXAMPLES = """\
  python -I scripts/history.py --repo . --include "src/**" --exclude "**/*.test.*" --out hist.json
  python -I scripts/history.py --repo . --range origin/main..HEAD --sections churn,authors,test-gate
  python -I scripts/history.py --repo . --since 2025-10-01 --module-depth 3 --top 30 --format text
  python -I scripts/history.py --repo . --module-map modules.json --complexity none --sections cochange"""


def hp(text: str) -> str:
    return text.replace("%", "%%")


def build_parser():
    p = c.make_parser("history.py", DESCRIPTION, EXAMPLES)
    p.add_argument("--include", action="append", default=[], metavar="GLOB",
                   help="repeatable; only files matching a glob are analysed (default: all tracked files)")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                   help="repeatable; files matching a glob are dropped (default: none)")
    p.add_argument("--range", dest="rev_range", metavar="BASE..HEAD",
                   help="restrict history to this revision range (run mode); overrides --since")
    p.add_argument("--since", metavar="DATE",
                   help="only commits since this git date expression, e.g. 2025-10-01 or '12 months ago' (default: all history)")
    p.add_argument("--sections", default=",".join(SECTIONS),
                   help=hp(f"comma list of {', '.join(SECTIONS)} (default: all); hotspots implies churn and complexity"))
    p.add_argument("--complexity", choices=("tokens", "lines", "none"), default="tokens",
                   help="complexity measure (default: tokens)")
    p.add_argument("--hotspot-pct", type=float, default=10.0,
                   help="top share of ranked files flagged as hotspots, 0-100 (default: 10)")
    p.add_argument("--top", type=int, default=20, help="entries per hotspot list (default: 20)")
    p.add_argument("--module-depth", type=int, default=2,
                   help="directory segments that form a module (default: 2)")
    p.add_argument("--module-map", metavar="JSON",
                   help="JSON object of glob -> module name, first match wins; unmatched files use --module-depth")
    p.add_argument("--bulk-threshold", type=int, default=50,
                   help="commits touching more files than this are excluded from co-change (default: 50)")
    p.add_argument("--min-shared", type=int, default=3,
                   help="minimum shared commits for a co-change pair to be listed (default: 3)")
    p.add_argument("--max-pairs", type=int, default=200,
                   help="cap on listed co-change pairs per level, strongest first (default: 200)")
    p.add_argument("--agent-pattern", default=DEFAULT_AGENT_PATTERN,
                   help=hp("regex on the full commit message incl. trailers, case-insensitive, multiline "
                           f"(default: {DEFAULT_AGENT_PATTERN})"))
    p.add_argument("--bot-pattern", default=DEFAULT_BOT_PATTERN,
                   help=hp(f"regex on 'author name <email>', case-insensitive (default: {DEFAULT_BOT_PATTERN})"))
    p.add_argument("--formatter-pattern", default=DEFAULT_FORMATTER_PATTERN,
                   help=hp(f"regex on the subject, case-insensitive (default: {DEFAULT_FORMATTER_PATTERN})"))
    p.add_argument("--deps-pattern", default=DEFAULT_DEPS_PATTERN,
                   help=hp(f"regex on the subject, case-insensitive (default: {DEFAULT_DEPS_PATTERN})"))
    p.add_argument("--exclude-classes", default="bot,formatter,dependency-update",
                   help=f"comma list from {', '.join(CLASSES)} removed from the 'excluding_classes' hotspots "
                        "(default: bot,formatter,dependency-update)")
    p.add_argument("--test-glob", action="append", default=None, metavar="GLOB",
                   help="repeatable; test-file globs (default: common test dirs and *.test.*/*.spec.*/*_test.*/test_*)")
    p.add_argument("--gate-glob", action="append", default=None, metavar="GLOB",
                   help="repeatable; gate/config globs (default: CI dirs, lint/type/test configs, package manifests)")
    p.add_argument("--max-list", type=int, default=50,
                   help="cap on listed test-gate commits, bulk commits and deleted files (default: 50)")
    return p


def parse_log(raw: str) -> list[dict]:
    """Parse `git log --numstat -M -z` output produced with the header format used here."""
    commits = []
    for chunk in raw.split("\x01")[1:]:
        head, _, rest = chunk.partition("\x03")
        sha, date, name, email, subject, message = head.split("\x02", 5)
        tokens = rest.split("\0")
        entries = []
        i = 0
        while i < len(tokens):
            m = re.match(r"^(\d+|-)\t(\d+|-)\t(.*)$", tokens[i].lstrip("\n"), re.S)
            if not m:
                i += 1
                continue
            added, deleted, path = m.groups()
            if path == "" and i + 2 < len(tokens):
                entries.append((tokens[i + 1], tokens[i + 2], added, deleted))
                i += 3
            else:
                entries.append((None, path, added, deleted))
                i += 1
        commits.append({
            "sha": sha, "date": date[:10], "author": name, "email": email,
            "subject": subject.lstrip("\ufeff"), "message": message, "entries": entries,
        })
    return commits


def resolve_renames(commits: list[dict]) -> None:
    """Map every entry to its HEAD name. Commits must be newest first."""
    current: dict[str, str] = {}
    for commit in commits:
        resolved = []
        pending = []
        for old, new, added, deleted in commit["entries"]:
            head = current.get(new, new)
            resolved.append((head, added, deleted))
            if old:
                pending.append((old, new, head))
        for old, new, head in pending:
            current.pop(new, None)
            current[old] = head
        commit["files"] = resolved


def classify(commit: dict, patterns: dict[str, re.Pattern]) -> tuple[str, str, str]:
    """Return (class, rule, matched text) for one commit; first matching rule wins."""
    author = f"{commit['author']} <{commit['email']}>"
    for cls, rule, text in (
        ("agent", "agent-pattern", commit["message"]),
        ("bot", "bot-pattern", author),
        ("formatter", "formatter-pattern", commit["subject"]),
        ("dependency-update", "deps-pattern", commit["subject"]),
    ):
        m = patterns[rule].search(text)
        if m:
            return cls, rule, m.group(0).strip()[:80]
    return "human", "no-rule-matched", ""


def language_family(path: str) -> str | None:
    ext = os.path.splitext(path)[1].lower()
    if ext in C_LIKE_EXT:
        return "c-like"
    if ext in PYTHON_EXT:
        return "python"
    if ext in SHELL_EXT:
        return "shell"
    return None


def strip_code(text: str, family: str) -> str:
    """Remove comments and blank string contents, keeping newlines so line counts survive."""
    strip_rx, _ = FAMILIES[family]

    def blank(m: re.Match) -> str:
        s = m.group(0)
        if s[0] in "\"'`" and not s.startswith(('"""', "'''")):
            return s[0] * 2
        return "\n" * s.count("\n")

    return strip_rx.sub(blank, text)


def count_loc(text: str) -> int:
    return sum(1 for line in text.split("\n") if line.strip())


def measure_complexity(text: str, path: str, mode: str) -> dict:
    """Return complexity, basis and loc for a file's text under the chosen mode."""
    family = language_family(path)
    code = strip_code(text, family) if family else text
    loc = count_loc(code)
    if mode == "none":
        return {"complexity": 1, "basis": "none", "loc": loc}
    if mode == "lines" or family is None:
        return {"complexity": loc, "basis": "lines", "loc": loc}
    return {"complexity": 1 + len(FAMILIES[family][1].findall(code)), "basis": "tokens", "loc": loc}


def module_of(path: str, depth: int, module_map: list[tuple[str, str]]) -> str:
    for glob, name in module_map:
        if c.glob_match(path, [glob]):
            return name
    dirs = path.split("/")[:-1]
    return "/".join(dirs[:depth]) or "(root)"


def rank_files(rows: dict[str, dict], counts: dict[str, int], pct: float) -> tuple[list[dict], int]:
    """Rank files by commits x complexity; return rows and the hotspot cutoff size."""
    scored = [
        {"file": f, "commits": counts[f], "complexity": r["complexity"], "score": counts[f] * r["complexity"]}
        for f, r in rows.items() if r["complexity"] is not None and counts.get(f, 0) > 0
    ]
    scored.sort(key=lambda r: (-r["score"], -r["commits"], r["file"]))
    cutoff = min(len(scored), max(1, math.ceil(len(scored) * pct / 100))) if scored and pct > 0 else 0
    for i, row in enumerate(scored, 1):
        row["rank"] = i
        row["hotspot"] = i <= cutoff
    return scored, cutoff


def compile_pattern(name: str, pattern: str) -> re.Pattern:
    try:
        return re.compile(pattern, re.I | re.M)
    except re.error as exc:
        raise c.UsageError(f"--{name} is not a valid regex: {exc}", hint=f"fix the pattern: {pattern}") from exc


def read_text(repo: str, path: str) -> tuple[str | None, str | None]:
    full = os.path.join(repo, path)
    if not os.path.isfile(full):
        return None, "not a regular file"
    try:
        with open(full, "rb") as fh:
            blob = fh.read()
    except OSError as exc:
        return None, f"unreadable: {exc}"
    if b"\0" in blob[:8192]:
        return None, "binary"
    return blob.decode("utf-8", errors="replace"), None


def fetch_commits(repo: str, ns, env: c.Envelope, head: str | None) -> list[dict]:
    if head is None:
        env.warn("repository has no commits; every section is empty")
        return []
    args = ["log", "--no-merges", "--topo-order", "--numstat", "-M", "-z",
            "--format=%x01%H%x02%aI%x02%an%x02%ae%x02%s%x02%B%x03"]
    if ns.rev_range:
        base = ns.rev_range.split("..", 1)[0]
        if ".." not in ns.rev_range or not base:
            raise c.UsageError(f"--range must look like base..head, got {ns.rev_range!r}",
                               hint="e.g. --range origin/main..HEAD")
        probe = c.run_git(repo, ["rev-parse", "--verify", "--quiet", base + "^{commit}"], check=False)
        if not probe.strip():
            raise c.UsageError(f"--range base is not a known commit: {base}",
                               hint="fetch the base ref or pass a sha")
        args.append(ns.rev_range)
    elif ns.since:
        args.append(f"--since={ns.since}")
    commits = parse_log(c.run_git(repo, args))
    c.log(1, f"{len(commits)} non-merge commits parsed from git log")
    return commits


def validate(ns) -> tuple[list[str], list[str]]:
    sections = [s.strip() for s in ns.sections.split(",") if s.strip()]
    bad = [s for s in sections if s not in SECTIONS]
    if bad or not sections:
        raise c.UsageError(f"unknown --sections value(s): {', '.join(bad) or '(empty)'}",
                           hint=f"choose from {', '.join(SECTIONS)}")
    if "hotspots" in sections:
        for needed in ("churn", "complexity"):
            if needed not in sections:
                sections.append(needed)
                c.log(1, f"--sections: hotspots needs {needed}, adding it")
    excluded = [s.strip() for s in ns.exclude_classes.split(",") if s.strip()]
    unknown = [s for s in excluded if s not in CLASSES]
    if unknown:
        raise c.UsageError(f"unknown --exclude-classes value(s): {', '.join(unknown)}",
                           hint=f"choose from {', '.join(CLASSES)}")
    if not 0 <= ns.hotspot_pct <= 100:
        raise c.UsageError("--hotspot-pct must be between 0 and 100")
    for name in ("top", "module_depth", "bulk_threshold", "min_shared", "max_pairs", "max_list"):
        if getattr(ns, name) < 1:
            raise c.UsageError(f"--{name.replace('_', '-')} must be at least 1")
    return sections, excluded


def load_module_map(path: str | None) -> list[tuple[str, str]]:
    if not path:
        return []
    raw = c.read_json(path)
    if not isinstance(raw, dict) or not all(isinstance(v, str) for v in raw.values()):
        raise c.InputError(f"--module-map must be a JSON object of glob -> module name: {path}",
                           hint='e.g. {"src/api/**": "api", "src/ui/**": "ui"}')
    return list(raw.items())


def accumulate_churn(commits: list[dict], in_scope) -> dict[str, dict]:
    churn: dict[str, dict] = {}
    for commit in commits:
        per_file: dict[str, list[int]] = {}
        for path, added, deleted in commit["files"]:
            if not in_scope(path):
                continue
            slot = per_file.setdefault(path, [0, 0])
            if added != "-":
                slot[0] += int(added)
                slot[1] += int(deleted)
        for path, (added, deleted) in per_file.items():
            row = churn.setdefault(path, {"commits": 0, "added": 0, "deleted": 0,
                                          "by_class": {k: 0 for k in CLASSES}})
            row["commits"] += 1
            row["added"] += added
            row["deleted"] += deleted
            row["by_class"][commit["class"]] += 1
    return churn


def measure_files(ns, env: c.Envelope, paths) -> tuple[dict[str, dict], dict]:
    rows: dict[str, dict] = {}
    skipped: collections.Counter = collections.Counter()
    for path in sorted(paths):
        text, reason = read_text(ns.repo, path)
        if text is None:
            skipped[reason.split(":")[0]] += 1
            c.log(1, f"complexity skipped {path}: {reason}")
            rows[path] = {"complexity": None, "basis": None, "loc": None}
            continue
        rows[path] = measure_complexity(text, path, ns.complexity)
    for reason, count in sorted(skipped.items()):
        env.warn(f"{count} file(s) skipped for complexity ({reason}); they get no score and no rank")
    bases = collections.Counter(r["basis"] for r in rows.values() if r["basis"])
    if ns.complexity == "tokens" and bases.get("lines"):
        env.warn(f"{bases['lines']} file(s) have an unrecognised syntax and were scored by non-blank line "
                 "count; their scores are on a different scale from token-based ones (see complexity_basis)")
    method = {
        "mode": ns.complexity,
        "tokens": "1 + count of branch tokens after heuristic comment/string stripping; "
                  "c-like: if for while case catch && || ?? ?; python: if elif for while except case and or; "
                  "shell: if elif for while until case && ||. Approximation, not a parser",
        "lines": "non-blank lines, comments removed where the syntax is known",
        "none": "complexity fixed at 1, score equals commits",
        "files_by_basis": dict(sorted(bases.items())),
        "read_from": "working tree at HEAD",
    }
    return rows, method


def compute_hotspots(ns, excluded, at_head, complexity_rows, files_out, env) -> dict:
    out = {"hotspot_pct": ns.hotspot_pct, "excluded_classes": excluded}
    variants = {
        "all": lambda r: r["commits"],
        "excluding_classes": lambda r: r["commits"] - sum(r["by_class"][k] for k in excluded),
        "human_only": lambda r: r["by_class"]["human"],
    }
    rank_all: dict[str, int] = {}
    for name, count_fn in variants.items():
        ranked, cutoff = rank_files(complexity_rows, {p: count_fn(r) for p, r in at_head.items()}, ns.hotspot_pct)
        if name == "all":
            rank_all = {r["file"]: r["rank"] for r in ranked}
            for r in ranked:
                files_out[r["file"]].update(score=r["score"], rank=r["rank"], hotspot=r["hotspot"])
        top = [dict(r, rank_all=rank_all.get(r["file"])) for r in ranked[:ns.top]]
        out[name] = {"files_ranked": len(ranked), "hotspot_cutoff": cutoff, "top": top}
    if not out["all"]["files_ranked"]:
        env.warn("no file could be ranked (no changed, readable files at HEAD in scope)")
    return out


def summarize_authors(commits, ns, env) -> dict:
    counts = collections.Counter(cm["class"] for cm in commits)
    rules: dict[str, dict] = {}
    for cm in commits:
        slot = rules.setdefault(cm["class"], {"rule": cm["rule"], "commits": 0, "examples": []})
        slot["commits"] += 1
        if len(slot["examples"]) < 5:
            slot["examples"].append({"sha": cm["sha"][:10], "subject": cm["subject"], "matched": cm["matched"]})
    identities = collections.Counter(f"{cm['author']} <{cm['email']}>" for cm in commits)
    top_ids = sorted(identities.items(), key=lambda kv: (-kv[1], kv[0]))[:20]
    if commits and counts.get("human", 0) == len(commits):
        env.warn("every commit classified as human: no agent, bot, formatter or dependency signal "
                 "matched; check the patterns if the repo is known to be agent-built")
    return {
        "counts_by_class": {k: counts.get(k, 0) for k in CLASSES},
        "rules": {k: rules[k] for k in sorted(rules)},
        "patterns": {
            "agent-pattern (message)": ns.agent_pattern, "bot-pattern (author)": ns.bot_pattern,
            "formatter-pattern (subject)": ns.formatter_pattern, "deps-pattern (subject)": ns.deps_pattern,
        },
        "identities_top": [{"identity": k, "commits": v} for k, v in top_ids],
        "identities_total": len(identities),
    }


def build(ns, env: c.Envelope) -> dict:
    sections, excluded = validate(ns)
    patterns = {name: compile_pattern(name, getattr(ns, name.replace("-", "_")))
                for name in ("agent-pattern", "bot-pattern", "formatter-pattern", "deps-pattern")}
    module_map = load_module_map(ns.module_map)
    test_globs = ns.test_glob if ns.test_glob is not None else DEFAULT_TEST_GLOBS
    gate_globs = ns.gate_glob if ns.gate_glob is not None else DEFAULT_GATE_GLOBS

    head = (env.repo or {}).get("head")
    if head is not None and not re.fullmatch(r"[0-9a-f]{40,64}", head):
        head = None
    shallow = c.run_git(ns.repo, ["rev-parse", "--is-shallow-repository"], check=False).strip() == "true"
    if shallow:
        env.warn("repository is a shallow clone: history is truncated and every churn, co-change and "
                 "class number covers only the fetched commits (git fetch --unshallow to fix)")

    all_tracked = [f for f in c.run_git(ns.repo, ["ls-files", "-z"]).split("\0") if f]
    tracked = set(all_tracked)
    c.log(1, f"{len(all_tracked)} tracked files, "
             f"{len(c.select_paths(all_tracked, ns.include, ns.exclude))} selected by include/exclude")
    for flag, globs in (("--include", ns.include), ("--exclude", ns.exclude)):
        for glob in globs:
            if not c.select_paths(all_tracked, [glob], []):
                env.warn(f"{flag} glob matched no tracked file: {glob}")

    def in_scope(path: str) -> bool:
        return bool(c.select_paths([path], ns.include, ns.exclude))

    commits = fetch_commits(ns.repo, ns, env, head)
    if head is not None and not commits:
        env.warn("no commits in the requested window; every section is empty")
    resolve_renames(commits)
    for commit in commits:
        commit["class"], commit["rule"], commit["matched"] = classify(commit, patterns)

    churn = accumulate_churn(commits, in_scope)
    at_head = {p: r for p, r in churn.items() if p in tracked}
    gone = {p: r for p, r in churn.items() if p not in tracked}
    c.log(1, f"{len(at_head)} changed files exist at HEAD, {len(gone)} were deleted or renamed away")

    method = {
        "churn": "git log --no-merges --topo-order --numstat -M; old paths mapped to HEAD names newest-first; "
                 "commits counted once per file; binary files add commits but no lines",
        "classification": "first matching rule wins: agent (message), bot (author), formatter (subject), "
                          "dependency-update (subject), else human",
        "cochange": "pairs in different modules within one non-bulk commit; module = "
                    f"{'module-map globs then ' if module_map else ''}first {ns.module_depth} directory segments",
        "test_gate": "hypothesis signal; package-manifest edits count as gate edits regardless of which "
                     "section changed; implementation = in-scope file that is not test, gate or "
                     f"documentation/lockfile/image ({', '.join(NON_IMPL_GLOBS)})",
    }

    complexity_rows: dict[str, dict] = {}
    if "complexity" in sections:
        complexity_rows, method["complexity"] = measure_files(ns, env, at_head)

    files_out = None
    if "churn" in sections or "hotspots" in sections:
        files_out = {}
        for path in sorted(at_head):
            row = at_head[path]
            cx = complexity_rows.get(path, {"complexity": None, "basis": None, "loc": None})
            files_out[path] = {
                "commits": row["commits"], "added": row["added"], "deleted": row["deleted"],
                "complexity": cx["complexity"], "complexity_basis": cx["basis"], "loc": cx["loc"],
                "score": None, "rank": None, "hotspot": False,
                "module": module_of(path, ns.module_depth, module_map), "by_class": row["by_class"],
            }

    hotspots = compute_hotspots(ns, excluded, at_head, complexity_rows, files_out, env) \
        if "hotspots" in sections else None
    authors = summarize_authors(commits, ns, env) if "authors" in sections else None

    cochange_files = cochange_modules = bulk_out = None
    if "cochange" in sections:
        cochange_files, cochange_modules, bulk_out = compute_cochange(commits, ns, in_scope, tracked, module_map)
        for block in (cochange_files, cochange_modules):
            if block["truncated"]:
                env.warn(f"co-change {block['unit']} pairs truncated to {ns.max_pairs} of "
                         f"{block['pairs_total']} (--max-pairs)")
        if bulk_out["truncated"]:
            env.warn(f"excluded_bulk_commits list truncated to {ns.max_list} of {bulk_out['count']} (--max-list)")

    test_gate = compute_test_gate(commits, ns, in_scope, test_globs, gate_globs) if "test-gate" in sections else None
    if test_gate and test_gate["truncated"]:
        env.warn(f"test_gate_with_impl truncated to {ns.max_list} of {test_gate['total']} commits (--max-list)")

    deleted_rows = [{"file": p, "commits": r["commits"], "added": r["added"], "deleted": r["deleted"]}
                    for p, r in sorted(gone.items(), key=lambda kv: (-kv[1]["commits"], kv[0]))]
    deleted_out = {"total": len(deleted_rows), "shown": min(len(deleted_rows), ns.max_list),
                   "truncated": max(0, len(deleted_rows) - ns.max_list), "files": deleted_rows[:ns.max_list]}
    if deleted_out["truncated"]:
        env.warn(f"deleted_at_head truncated to {ns.max_list} of {deleted_out['total']} files (--max-list)")

    dates = sorted(cm["date"] for cm in commits)
    window = {
        "first_commit_date": dates[0] if dates else None,
        "last_commit_date": dates[-1] if dates else None,
        "commits": len(commits), "range": ns.rev_range, "since": ns.since, "shallow": shallow,
        "merge_commits": "skipped",
    }
    return {
        "window": window, "method": method, "sections_computed": sorted(sections), "authors": authors,
        "files": files_out, "hotspots": hotspots, "cochange_files": cochange_files,
        "cochange_modules": cochange_modules, "test_gate_with_impl": test_gate,
        "excluded_bulk_commits": bulk_out, "deleted_at_head": deleted_out,
    }


def compute_cochange(commits, ns, in_scope, tracked, module_map):
    file_counts: collections.Counter = collections.Counter()
    module_counts: collections.Counter = collections.Counter()
    file_pairs: collections.Counter = collections.Counter()
    module_pairs: collections.Counter = collections.Counter()
    module_cache: dict[str, str] = {}
    bulk = []
    considered = 0

    def mod(path: str) -> str:
        if path not in module_cache:
            module_cache[path] = module_of(path, ns.module_depth, module_map)
        return module_cache[path]

    for cm in commits:
        if len(cm["files"]) > ns.bulk_threshold:
            bulk.append({"sha": cm["sha"][:10], "date": cm["date"], "subject": cm["subject"],
                         "files": len(cm["files"]), "class": cm["class"]})
            continue
        paths = sorted({p for p, _, _ in cm["files"] if p in tracked and in_scope(p)})
        if not paths:
            continue
        considered += 1
        mods = sorted({mod(p) for p in paths})
        file_counts.update(paths)
        module_counts.update(mods)
        for a, b in itertools.combinations(paths, 2):
            if mod(a) != mod(b):
                file_pairs[(a, b)] += 1
        for a, b in itertools.combinations(mods, 2):
            module_pairs[(a, b)] += 1

    def pairs_out(pairs, counts, unit):
        rows = []
        for (a, b), shared in pairs.items():
            if shared < ns.min_shared:
                continue
            row = {"a": a, "b": b}
            if unit == "file":
                row.update(module_a=mod(a), module_b=mod(b))
            row.update(shared=shared, commits_a=counts[a], commits_b=counts[b],
                       ratio=round(shared / min(counts[a], counts[b]), 3))
            rows.append(row)
        rows.sort(key=lambda r: (-r["shared"], -r["ratio"], r["a"], r["b"]))
        return {"unit": unit, "min_shared": ns.min_shared, "commits_considered": considered,
                "pairs_total": len(rows), "shown": min(len(rows), ns.max_pairs),
                "truncated": max(0, len(rows) - ns.max_pairs), "pairs": rows[:ns.max_pairs]}

    bulk_out = {"threshold": ns.bulk_threshold, "count": len(bulk), "shown": min(len(bulk), ns.max_list),
                "truncated": max(0, len(bulk) - ns.max_list), "commits": bulk[:ns.max_list]}
    return pairs_out(file_pairs, file_counts, "file"), pairs_out(module_pairs, module_counts, "module"), bulk_out


def compute_test_gate(commits, ns, in_scope, test_globs, gate_globs) -> dict:
    hits = []
    cap = 15
    for cm in commits:
        paths = sorted({p for p, _, _ in cm["files"]})
        tests = [p for p in paths if c.glob_match(p, test_globs)]
        gates = [p for p in paths if p not in tests and c.glob_match(p, gate_globs)]
        impl = [p for p in paths if p not in tests and p not in gates
                and in_scope(p) and not c.glob_match(p, NON_IMPL_GLOBS)]
        if (tests or gates) and impl:
            hits.append({
                "sha": cm["sha"][:10], "date": cm["date"], "subject": cm["subject"], "class": cm["class"],
                "rule": cm["rule"], "files_in_commit": len(paths), "bulk": len(paths) > ns.bulk_threshold,
                "test_files": tests[:cap], "test_files_total": len(tests),
                "gate_files": gates[:cap], "gate_files_total": len(gates),
                "impl_files": impl[:cap], "impl_files_total": len(impl),
            })
    return {
        "signal": "hypothesis: commits touching tests or gate config together with implementation; read before judging",
        "test_globs": list(test_globs), "gate_globs": list(gate_globs),
        "total": len(hits), "shown": min(len(hits), ns.max_list), "truncated": max(0, len(hits) - ns.max_list),
        "commits": hits[:ns.max_list],
    }


def text_summary(data: dict) -> str:
    w = data["window"]
    lines = [f"window: {w['first_commit_date']} .. {w['last_commit_date']}, {w['commits']} commits"
             f"{', range ' + w['range'] if w['range'] else ''}{', SHALLOW' if w['shallow'] else ''}"]
    if data["authors"]:
        lines.append("classes: " + ", ".join(f"{k}={v}" for k, v in data["authors"]["counts_by_class"].items()))
    if data["hotspots"]:
        for name in ("all", "excluding_classes", "human_only"):
            block = data["hotspots"][name]
            lines.append(f"top hotspots ({name}, {block['files_ranked']} ranked, cutoff {block['hotspot_cutoff']}):")
            for r in block["top"][:10]:
                lines.append(f"  {r['rank']:>3}. {r['file']}  commits={r['commits']} "
                             f"complexity={r['complexity']} score={r['score']}")
    if data["cochange_files"]:
        block = data["cochange_files"]
        lines.append(f"top co-change file pairs ({block['pairs_total']} total, bulk commits excluded: "
                     f"{data['excluded_bulk_commits']['count']}):")
        for r in block["pairs"][:10]:
            lines.append(f"  {r['shared']:>3} shared, ratio {r['ratio']}: {r['a']} <-> {r['b']}")
    if data["test_gate_with_impl"]:
        lines.append(f"test/gate-with-impl commits (hypothesis): {data['test_gate_with_impl']['total']}")
    lines.append(f"deleted at HEAD: {data['deleted_at_head']['total']} files")
    return "\n".join(lines)


def main(argv=None) -> int:
    ns = build_parser().parse_args(argv)
    c.set_verbosity(ns.verbose)
    env = c.Envelope(tool="history", args=c.args_dict(ns))
    env.repo = c.repo_info(ns.repo)
    env.data = build(ns, env)
    c.write_output(env, ns, text_summary)
    return c.EXIT_OK


if __name__ == "__main__":
    c.run_main(main)
