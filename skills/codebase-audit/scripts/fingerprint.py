#!/usr/bin/env python3
"""Scope and profile fingerprints, and scope comparison. See --help."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402

TOOL = "fingerprint"

DESCRIPTION = """\
Fingerprint what an audit measured so a later audit can tell drift from a scope change.

A baseline's numbers are only comparable when the commit-independent scope is the same:
same include/exclude globs, same tool versions, same extra settings. A different scope
produces phantom drift, so compare fingerprints before numbers. The profile hash does
the same for the system's stated identity, load, stakes and quality attributes.

subcommands:
  scope    canonical scope object and its hash (resolves --commit through git)
  profile  hash of the profile's four substantive sections (ignores Scope, Audit plan
           and Source lines); lists fields still 'unknown'
  compare  field-level differences between two scope objects, with comparable true|false

Caveats: a hash says "same inputs", never "same behavior". The commit is part of the
scope object but is excluded from comparability (a re-audit is expected to be at a
newer commit); a changed commit is reported as commit_changed.
"""

EXAMPLES = """\
  python -I scripts/fingerprint.py scope --repo . --commit HEAD --include "src/**" --exclude "**/*.generated.*" --tool node=22.4.0 --extra depth=standard
  python -I scripts/fingerprint.py profile docs/audits/2026-10-13-baseline/profile.md
  python -I scripts/fingerprint.py compare baseline/scope.json work/scope.json"""

PROFILE_HASHED_SECTIONS = ("Identity", "Load and constraints", "Stakes", "Dominant quality attributes")
IGNORED_LINE_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?(source|confirmed by)(?:\*\*)?\s*:", re.I)
FIELD_LINE_RE = re.compile(r"^\s*[-*]\s*(?:\*\*)?([^:*]+?)(?:\*\*)?\s*:\s*(.*)$")
UNKNOWN_RE = re.compile(r"^\s*(?:<[^>]*\|\s*)?unknown\b", re.I)
PLACEHOLDER_RE = re.compile(r"<[^<>\n]{2,}>")
FULL_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def digest(value: Any) -> str:
    return hashlib.sha256(c.canonical_json(value).encode("utf-8")).hexdigest()[:16]


def parse_pairs(items: list[str] | None, flag: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items or []:
        key, sep, value = item.partition("=")
        if not sep or not key.strip():
            raise c.UsageError(f"{flag} expects NAME=VALUE, got {item!r}", hint=f"e.g. {flag} node=22.4.0")
        out[key.strip()] = value.strip()
    return out


def resolve_commit(repo: str, requested: str) -> str:
    sha = c.run_git(repo, ["rev-parse", "--verify", "--quiet", f"{requested}^{{commit}}"], check=False).strip()
    if not FULL_SHA_RE.match(sha):
        raise c.EnvError(f"cannot resolve commit {requested!r} in {repo}", hint="pass a reachable SHA, tag or branch, and --repo for the audited checkout")
    return sha


def build_scope(commit: str, include: list[str], exclude: list[str], tools: dict[str, str], extra: dict[str, str]) -> dict:
    return {
        "commit": commit,
        "include": sorted({g.replace("\\", "/") for g in include}),
        "exclude": sorted({g.replace("\\", "/") for g in exclude}),
        "tools": dict(sorted(tools.items())),
        "extra": dict(sorted(extra.items())),
    }


def cmd_scope(ns: argparse.Namespace, env: c.Envelope):
    include, exclude = list(ns.include or []), list(ns.exclude or [])
    tools = parse_pairs(ns.tool, "--tool")
    extra = parse_pairs(ns.extra, "--extra")
    commit = ns.commit
    if ns.from_file:
        loaded = c.read_json(ns.from_file)
        if not isinstance(loaded, dict):
            raise c.InputError(f"{ns.from_file} must contain a JSON object", hint="expected keys: commit, include, exclude, tools, extra")
        loaded = loaded.get("scope", loaded)
        commit = commit or loaded.get("commit")
        include = list(loaded.get("include", [])) + include
        exclude = list(loaded.get("exclude", [])) + exclude
        tools = {**(loaded.get("tools") or {}), **tools}
        extra = {**(loaded.get("extra") or {}), **extra}
        c.log(1, f"read scope from {ns.from_file}; command-line values were merged over it")
    if not commit:
        raise c.UsageError("a commit is required", hint="pass --commit SHA (HEAD is resolved to a SHA) or a --from-file with a commit key")
    resolved = resolve_commit(ns.repo, commit)
    if resolved != commit:
        c.log(1, f"resolved {commit!r} to {resolved}")
        env.warn(f"--commit {commit!r} resolved to {resolved}; the fingerprint pins that SHA")
    if not include:
        env.warn("include is empty: the scope covers every tracked file")
    scope = build_scope(resolved, include, exclude, tools, extra)
    env.data = {
        "fingerprint": digest(scope),
        "method": "sha256 of canonical JSON (sorted keys) of the scope object, first 16 hex",
        "resolved": {"requested": commit, "sha": resolved, "was_symbolic": resolved != commit},
        "scope": scope,
    }
    return c.EXIT_OK, lambda d: f"fingerprint {d['fingerprint']}\ncommit {d['scope']['commit']} (requested {d['resolved']['requested']})\ninclude {d['scope']['include']}\nexclude {d['scope']['exclude']}\ntools {d['scope']['tools']}\nextra {d['scope']['extra']}"


def split_sections(markdown: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    in_fence = False
    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        heading = None if in_fence else re.match(r"^##\s+(.+?)\s*#*\s*$", line)
        if heading and not line.startswith("###"):
            current = heading.group(1).strip()
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    return sections


def normalize_section_body(lines: list[str]) -> str:
    kept = []
    for line in lines:
        if IGNORED_LINE_RE.match(line):
            continue
        collapsed = " ".join(line.split())
        if collapsed:
            kept.append(collapsed)
    return "\n".join(kept)


def find_unknown_fields(section: str, lines: list[str]) -> list[dict]:
    found = []
    for line in lines:
        if IGNORED_LINE_RE.match(line):
            continue
        m = FIELD_LINE_RE.match(line)
        if m and UNKNOWN_RE.match(m.group(2)):
            found.append({"section": section, "field": m.group(1).strip()})
    return found


def cmd_profile(ns: argparse.Namespace, env: c.Envelope):
    try:
        with open(ns.profile, encoding="utf-8") as fh:
            markdown = fh.read()
    except OSError as exc:
        raise c.InputError(f"cannot read profile {ns.profile}: {exc}") from exc
    sections = split_sections(markdown)
    by_lower = {k.lower(): k for k in sections}
    hashed: dict[str, str] = {}
    unknown: list[dict] = []
    missing = []
    placeholders = []
    for wanted in PROFILE_HASHED_SECTIONS:
        actual = by_lower.get(wanted.lower())
        if actual is None:
            missing.append(wanted)
            env.warn(f"profile has no '## {wanted}' section; it is left out of the hash")
            continue
        lines = sections[actual]
        body = normalize_section_body(lines)
        hashed[wanted] = body
        unknown += find_unknown_fields(wanted, lines)
        if PLACEHOLDER_RE.search(body):
            placeholders.append(wanted)
            env.warn(f"section '{wanted}' still contains <placeholder> template text")
        if not body:
            env.warn(f"section '{wanted}' is empty")
    ignored = sorted(k for k in sections if k.lower() not in {s.lower() for s in PROFILE_HASHED_SECTIONS})
    c.log(1, f"hashed {len(hashed)} section(s); ignored sections: {ignored}")
    env.data = {
        "profile_hash": digest(hashed),
        "method": "sha256 of canonical JSON of {section: whitespace-normalized body}; Source: and Confirmed by: lines dropped; first 16 hex",
        "complete": not missing,
        "hashed_sections": sorted(hashed),
        "section_hashes": {k: digest(v) for k, v in sorted(hashed.items())},
        "missing_sections": missing,
        "ignored_sections": ignored,
        "placeholder_sections": placeholders,
        "unknown_fields": unknown,
        "unknown_count": len(unknown),
    }

    def text(d):
        lines = [f"profile_hash {d['profile_hash']} ({'complete' if d['complete'] else 'INCOMPLETE'}), {d['unknown_count']} unknown field(s)"]
        lines += [f"  unknown: {u['section']} / {u['field']}" for u in d["unknown_fields"]]
        lines += [f"  missing: {m}" for m in d["missing_sections"]]
        return "\n".join(lines)

    return c.EXIT_OK, text


def load_scope_object(path: str) -> dict:
    loaded = c.read_json(path)
    if isinstance(loaded, dict) and isinstance(loaded.get("data"), dict) and "scope" in loaded["data"]:
        loaded = loaded["data"]["scope"]
    elif isinstance(loaded, dict) and isinstance(loaded.get("scope"), dict):
        loaded = loaded["scope"]
    if not isinstance(loaded, dict) or "commit" not in loaded:
        raise c.InputError(f"{path} is not a scope object or a 'scope' command output", hint="produce it with: fingerprint.py scope --out FILE")
    return build_scope(str(loaded["commit"]), list(loaded.get("include") or []), list(loaded.get("exclude") or []),
                       dict(loaded.get("tools") or {}), dict(loaded.get("extra") or {}))


def compare_scopes(a: dict, b: dict) -> list[dict]:
    diffs = []
    for field in ("include", "exclude"):
        added, removed = sorted(set(b[field]) - set(a[field])), sorted(set(a[field]) - set(b[field]))
        if added or removed:
            diffs.append({"field": field, "kind": "set", "added": added, "removed": removed})
    for field in ("tools", "extra"):
        for key in sorted(set(a[field]) | set(b[field])):
            if a[field].get(key) != b[field].get(key):
                diffs.append({"field": f"{field}.{key}", "kind": "value", "before": a[field].get(key), "after": b[field].get(key)})
    return diffs


def cmd_compare(ns: argparse.Namespace, env: c.Envelope):
    a, b = load_scope_object(ns.a), load_scope_object(ns.b)
    differences = compare_scopes(a, b)
    commit_changed = a["commit"] != b["commit"]
    comparable = not differences
    if not comparable:
        env.warn("scopes differ: numbers from these audits are not comparable until the difference is explained")
    env.data = {
        "comparable": comparable,
        "commit_changed": commit_changed,
        "commits": {"a": a["commit"], "b": b["commit"]},
        "fingerprints": {"a": digest(a), "b": digest(b)},
        "differences": differences,
        "note": "commit is excluded from comparability: a re-audit at a newer commit is expected",
    }

    def text(d):
        lines = [f"comparable: {str(d['comparable']).lower()}; commit_changed: {str(d['commit_changed']).lower()}"]
        for diff in d["differences"]:
            if diff["kind"] == "set":
                lines.append(f"  {diff['field']}: +{diff['added']} -{diff['removed']}")
            else:
                lines.append(f"  {diff['field']}: {diff['before']!r} -> {diff['after']!r}")
        return "\n".join(lines)

    return (c.EXIT_CONDITION if ns.fail_on_incomparable and not comparable else c.EXIT_OK), text


def build_parser() -> argparse.ArgumentParser:
    raw = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog="fingerprint.py", description=DESCRIPTION,
                                     epilog=f"examples:\n{EXAMPLES}\n\n{c.EXIT_CODES_HELP}", formatter_class=raw)
    parser.add_argument("--version", action="version", version=f"%(prog)s {c.VERSION}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="{scope,profile,compare}")

    def add(name, help_, desc, epilog, func, with_repo=False):
        sp = sub.add_parser(name, help=help_, description=desc, formatter_class=raw, epilog=f"{epilog}\n\n{c.EXIT_CODES_HELP}")
        c.add_common_flags(sp, with_repo=with_repo)
        sp.set_defaults(func=func)
        return sp

    sp = add("scope", "canonical scope object and hash",
             "Build the canonical scope object {commit, include, exclude, tools, extra} and hash it. Lists are sorted and\n"
             "de-duplicated, backslashes become slashes, and a symbolic --commit (HEAD, a tag, a branch) is resolved to a\n"
             "full SHA through git, with a warning saying which SHA it resolved to. The fingerprint changes whenever any\n"
             "field changes, including the commit.\n"
             "data fields: fingerprint, scope{commit, include, exclude, tools, extra}, resolved{requested, sha,\n"
             "was_symbolic}, method.\n"
             "Command-line values are merged over --from-file (lists are unioned; tools/extra keys are overridden).",
             "examples:\n  python -I scripts/fingerprint.py scope --commit HEAD --include \"src/**\" --exclude \"**/generated/**\" --tool node=22.4.0 --out work/scope.json\n"
             "  python -I scripts/fingerprint.py scope --from-file scope-input.json",
             cmd_scope, with_repo=True)
    sp.add_argument("--commit", help="commit, tag or branch to pin (resolved to a full SHA); required unless --from-file has a commit key")
    sp.add_argument("--include", nargs="+", action="extend", metavar="GLOB", help="include globs (repeatable; default: none = every tracked file)")
    sp.add_argument("--exclude", nargs="+", action="extend", metavar="GLOB", help="exclude globs such as generated, vendored and fixture code")
    sp.add_argument("--tool", action="append", metavar="NAME=VERSION", help="a tool and its version; repeatable")
    sp.add_argument("--extra", action="append", metavar="KEY=VALUE", help="any other setting that changes what is measured (depth, sample seed ...); repeatable")
    sp.add_argument("--from-file", metavar="scope.json", help="start from a scope JSON file (a bare scope object or a 'scope' command output)")

    sp = add("profile", "hash of the profile's substantive sections",
             "Hash the Identity, Load and constraints, Stakes and Dominant quality attributes sections of profile.md (sections are\n"
             "'## ' headings, matched case-insensitively). Whitespace is normalized and blank lines dropped; the Scope and Audit\n"
             "plan sections, 'Source:' lines and 'Confirmed by:' lines are ignored so re-wording sources or confirming does not\n"
             "change the hash. Reports fields whose value is 'unknown', and warns on missing sections or leftover <placeholders>.\n"
             "data fields: profile_hash, section_hashes, complete, missing_sections, ignored_sections, placeholder_sections,\n"
             "unknown_fields[{section, field}], unknown_count, method.\n"
             "A changed profile hash means the system's stated purpose or constraints changed: re-baseline, do not diff numbers.",
             "example:\n  python -I scripts/fingerprint.py profile docs/audits/2026-10-13-baseline/profile.md", cmd_profile)
    sp.add_argument("profile", help="path to profile.md")

    sp = add("compare", "field-level differences between two scope objects",
             "Compare two scope objects (bare, or the output of 'scope'). comparable is true when include, exclude, tools and\n"
             "extra are identical; the commit may differ (reported as commit_changed).\n"
             "data fields: comparable, commit_changed, commits{a,b}, fingerprints{a,b}, differences[{field, kind, added, removed |\n"
             "before, after}], note.",
             "examples:\n  python -I scripts/fingerprint.py compare baseline/scope.json work/scope.json\n"
             "  python -I scripts/fingerprint.py compare a.json b.json --fail-on-incomparable", cmd_compare)
    sp.add_argument("a", help="first (baseline) scope JSON")
    sp.add_argument("b", help="second (current) scope JSON")
    sp.add_argument("--fail-on-incomparable", action="store_true", help="exit 1 when comparable is false")
    return parser


def main(argv: list[str] | None = None) -> int:
    ns = build_parser().parse_args(argv)
    c.set_verbosity(ns.verbose)
    env = c.Envelope(tool=f"{TOOL} {ns.command}", args=c.args_dict(ns))
    if getattr(ns, "repo", None) is not None:
        env.repo = c.repo_info(ns.repo)
    code, text = ns.func(ns, env)
    c.write_output(env, ns, text)
    return code


if __name__ == "__main__":
    c.run_main(main)
