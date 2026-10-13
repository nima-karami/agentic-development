#!/usr/bin/env python3
"""Pack-driven, language-neutral pattern counter for codebase audits.

See ``python -I scripts/patterns.py --help`` and each subcommand's ``--help``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402

PACKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "packs")
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TEXT = 200
EXAMPLES_PER_SKIP_REASON = 10
BLAME_RANGES_PER_CALL = 100
GROUP_DIMENSIONS = ("category", "dir", "ext", "age")
AGE_BUCKETS = ("<30d", "30-90d", "90-365d", ">365d")
SPECIAL_AGE_BUCKETS = ("uncommitted", "unknown")
DEFAULT_TEST_GLOBS = [
    "**/test/**",
    "**/tests/**",
    "**/__tests__/**",
    "**/__mocks__/**",
    "**/testdata/**",
    "**/fixtures/**",
    "**/e2e/**",
    "**/*.test.*",
    "**/*.spec.*",
    "**/test_*.py",
    "**/*_test.py",
    "**/conftest.py",
    "**/*_test.go",
    "**/*Test.java",
    "**/*Tests.java",
    "**/*Test.kt",
    "**/*_test.rs",
]
HASH_COMMENT_EXTENSIONS = (
    ".py", ".pyi", ".rb", ".sh", ".bash", ".yml", ".yaml", ".toml", ".pl", ".r", ".mk", ".cfg",
)
PACK_KEYS = {"name", "description", "version", "patterns", "limitations", "applies_to_tests"}
PATTERN_KEYS = {
    "id", "category", "regex", "flags", "extensions", "exclude_regex", "description", "rubric",
    "heuristic", "code_only",
}
PACK_FORMAT_HINT = (
    "pack format: {\"name\", \"description\", \"version\", \"patterns\": [{\"id\", \"category\", "
    "\"regex\", \"description\", \"flags\"?: \"i\", \"extensions\"?: [\".ts\"], "
    "\"exclude_regex\"?, \"rubric\"?, \"heuristic\"?, \"code_only\"?}]}; see "
    "`patterns.py scan --help`"
)

TOOL = "patterns"


@dataclass
class Pattern:
    id: str
    category: str
    regex: str
    description: str
    flags: str = ""
    extensions: List[str] = field(default_factory=list)
    exclude_regex: Optional[str] = None
    rubric: Optional[str] = None
    heuristic: bool = False
    code_only: bool = False
    pack: str = ""
    compiled: Optional["re.Pattern[str]"] = None
    compiled_exclude: Optional["re.Pattern[str]"] = None
    error: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "id": self.id,
            "category": self.category,
            "regex": self.regex,
            "description": self.description,
        }
        if self.flags:
            out["flags"] = self.flags
        if self.extensions:
            out["extensions"] = list(self.extensions)
        if self.exclude_regex:
            out["exclude_regex"] = self.exclude_regex
        if self.rubric:
            out["rubric"] = self.rubric
        if self.heuristic:
            out["heuristic"] = True
        if self.code_only:
            out["code_only"] = True
        return out


@dataclass
class Pack:
    name: str
    description: str
    version: str
    patterns: List[Pattern]
    source: str
    limitations: List[str] = field(default_factory=list)
    applies_to_tests: bool = False

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "applies_to_tests": self.applies_to_tests,
            "limitations": list(self.limitations),
            "patterns": [p.to_json() for p in self.patterns],
        }


@dataclass
class Hit:
    path: str
    line: int
    pattern: str
    text: str
    context: str
    in_tests: bool = False
    focus: bool = False
    blame: Optional[Dict[str, Any]] = None

    def to_json(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "path": self.path,
            "line": self.line,
            "pattern": self.pattern,
            "text": self.text,
            "context": self.context,
        }
        if self.in_tests:
            out["in_tests"] = True
        if self.focus:
            out["focus"] = True
        if self.blame is not None:
            out["blame"] = self.blame
        return out


@dataclass
class FocusEntry:
    path: str
    start: Optional[int] = None
    end: Optional[int] = None
    matched_files: int = 0


def _pack_error(source: str, message: str) -> c.InputError:
    return c.InputError(f"pack {source}: {message}", hint=PACK_FORMAT_HINT)


def _require_str(source: str, where: str, obj: Dict[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise _pack_error(source, f"{where}: '{key}' must be a non-empty string")
    return value


def _require_bool(source: str, where: str, obj: Dict[str, Any], key: str) -> bool:
    value = obj.get(key, False)
    if not isinstance(value, bool):
        raise _pack_error(source, f"{where}: '{key}' must be true or false")
    return value


def _check_keys(source: str, where: str, obj: Dict[str, Any], allowed: Iterable[str]) -> None:
    unknown = sorted(set(obj) - set(allowed))
    if unknown:
        raise _pack_error(
            source,
            f"{where}: unknown key(s) {', '.join(unknown)}; allowed: {', '.join(sorted(allowed))}",
        )


def _compile(pattern: Pattern) -> None:
    flags = re.IGNORECASE if "i" in pattern.flags else 0
    try:
        pattern.compiled = re.compile(pattern.regex, flags)
        if pattern.exclude_regex:
            pattern.compiled_exclude = re.compile(pattern.exclude_regex, flags)
    except re.error as exc:
        pattern.compiled = None
        pattern.compiled_exclude = None
        pattern.error = str(exc)


def validate_pack(obj: Any, source: str) -> Pack:
    """Validate a decoded pack and return it, raising InputError with a precise location."""
    if not isinstance(obj, dict):
        raise _pack_error(source, "top level must be a JSON object")
    _check_keys(source, "pack", obj, PACK_KEYS)
    name = _require_str(source, "pack", obj, "name")
    description = _require_str(source, "pack", obj, "description")
    version = obj.get("version")
    if not isinstance(version, (str, int)) or isinstance(version, bool) or str(version) == "":
        raise _pack_error(source, "pack: 'version' must be a non-empty string or integer")
    limitations = obj.get("limitations", [])
    if not isinstance(limitations, list) or not all(isinstance(x, str) for x in limitations):
        raise _pack_error(source, "pack: 'limitations' must be a list of strings")
    applies_to_tests = _require_bool(source, "pack", obj, "applies_to_tests")
    raw_patterns = obj.get("patterns")
    if not isinstance(raw_patterns, list) or not raw_patterns:
        raise _pack_error(source, "pack: 'patterns' must be a non-empty list")
    patterns: List[Pattern] = []
    seen: set = set()
    for index, raw in enumerate(raw_patterns):
        where = f"patterns[{index}]"
        if not isinstance(raw, dict):
            raise _pack_error(source, f"{where}: must be an object")
        label = raw.get("id") if isinstance(raw.get("id"), str) else None
        if label:
            where = f"patterns[{index}] (id '{label}')"
        _check_keys(source, where, raw, PATTERN_KEYS)
        pid = _require_str(source, where, raw, "id")
        if pid in seen:
            raise _pack_error(source, f"{where}: duplicate pattern id '{pid}'")
        seen.add(pid)
        category = _require_str(source, where, raw, "category")
        regex = _require_str(source, where, raw, "regex")
        pdesc = _require_str(source, where, raw, "description")
        flags = raw.get("flags", "")
        if not isinstance(flags, str) or any(ch != "i" for ch in flags):
            raise _pack_error(source, f"{where}: 'flags' must be \"i\" or omitted")
        extensions = raw.get("extensions", [])
        if (
            not isinstance(extensions, list)
            or not all(isinstance(e, str) and e for e in extensions)
        ):
            raise _pack_error(
                source,
                f"{where}: 'extensions' must be a list of non-empty strings "
                "(\".ts\" matches a suffix, \"Makefile\" matches a file name)",
            )
        exclude = raw.get("exclude_regex")
        if exclude is not None and (not isinstance(exclude, str) or not exclude):
            raise _pack_error(source, f"{where}: 'exclude_regex' must be a non-empty string")
        rubric = raw.get("rubric")
        if rubric is not None and (not isinstance(rubric, str) or not rubric):
            raise _pack_error(source, f"{where}: 'rubric' must be a non-empty string")
        pattern = Pattern(
            id=pid,
            category=category,
            regex=regex,
            description=pdesc,
            flags=flags,
            extensions=list(extensions),
            exclude_regex=exclude,
            rubric=rubric,
            heuristic=_require_bool(source, where, raw, "heuristic"),
            code_only=_require_bool(source, where, raw, "code_only"),
            pack=name,
        )
        _compile(pattern)
        patterns.append(pattern)
    return Pack(
        name=name,
        description=description,
        version=str(version),
        patterns=patterns,
        source=source,
        limitations=list(limitations),
        applies_to_tests=applies_to_tests,
    )


def shipped_pack_names() -> List[str]:
    if not os.path.isdir(PACKS_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(PACKS_DIR) if f.endswith(".json"))


def _looks_like_path(spec: str) -> bool:
    return "/" in spec or "\\" in spec or spec.lower().endswith(".json")


def load_pack(spec: str) -> Pack:
    """Load a shipped pack by name or a pack file by path."""
    if _looks_like_path(spec):
        path = spec
    else:
        names = shipped_pack_names()
        if spec not in names:
            raise c.InputError(
                f"no shipped pack named '{spec}'",
                hint=f"shipped packs: {', '.join(names) or '(none)'}; pass a path to use your own pack file",
            )
        path = os.path.join(PACKS_DIR, spec + ".json")
    c.log(1, f"loading pack {path}")
    return validate_pack(c.read_json(path), path)


def extension_matches(path: str, extensions: Sequence[str]) -> bool:
    if not extensions:
        return True
    base = path.rsplit("/", 1)[-1].lower()
    for ext in extensions:
        low = ext.lower()
        if low.startswith("."):
            if base.endswith(low):
                return True
        elif base == low:
            return True
    return False


def file_extension(path: str) -> str:
    base = path.rsplit("/", 1)[-1]
    dot = base.rfind(".")
    return base[dot:].lower() if dot > 0 else "(none)"


def code_view(line: str, hash_comments: bool, rust: bool = False) -> str:
    """Blank string-literal contents and trailing comments so a code-only pattern cannot match them."""
    stripped = line.lstrip()
    if not hash_comments and (stripped.startswith("*") or stripped.startswith("/*")):
        return ""
    quotes = '"' if rust else "'\"`"
    out: List[str] = []
    quote = ""
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
                out.append(ch)
            i += 1
            continue
        if hash_comments and ch == "#":
            break
        if not hash_comments and ch == "/" and i + 1 < n and line[i + 1] in "/*":
            break
        if ch in quotes:
            quote = ch
            out.append(ch)
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def scan_text(path: str, text: str, patterns: Sequence[Pattern]) -> List[Hit]:
    """Find every pattern match in a file's text; one Hit per regex match, in line order."""
    active = [
        p for p in patterns if p.compiled is not None and extension_matches(path, p.extensions)
    ]
    if not active:
        return []
    low = path.lower()
    hash_comments = low.endswith(HASH_COMMENT_EXTENSIONS)
    rust = low.endswith(".rs")
    needs_code_view = any(p.code_only for p in active)
    hits: List[Hit] = []
    for number, raw_line in enumerate(text.split("\n"), start=1):
        line = raw_line[:-1] if raw_line.endswith("\r") else raw_line
        if not line.strip():
            continue
        view = code_view(line, hash_comments, rust) if needs_code_view else line
        context = line.strip()[:MAX_TEXT]
        for pattern in active:
            subject = view if pattern.code_only else line
            if pattern.compiled_exclude is not None and pattern.compiled_exclude.search(line):
                continue
            for match in pattern.compiled.finditer(subject):
                hits.append(
                    Hit(
                        path=path,
                        line=number,
                        pattern=pattern.id,
                        text=match.group(0).strip()[:MAX_TEXT],
                        context=context,
                    )
                )
    return hits


def is_test_path(path: str, test_globs: Sequence[str]) -> bool:
    return c.glob_match(path, test_globs)


def age_bucket(days: int) -> str:
    if days < 30:
        return AGE_BUCKETS[0]
    if days < 90:
        return AGE_BUCKETS[1]
    if days < 365:
        return AGE_BUCKETS[2]
    return AGE_BUCKETS[3]


def lower_median(values: Sequence[int]) -> Optional[int]:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]


_FOCUS_LINE = re.compile(r"^(?P<path>.+?)(?::(?P<start>\d+)(?:-(?P<end>\d+))?)?$")


def _normalize_focus_path(path: str) -> str:
    path = path.strip().replace("\\", "/")
    return path[2:] if path.startswith("./") else path


def _focus_entry(spec: str, source: str) -> FocusEntry:
    match = _FOCUS_LINE.match(spec.strip())
    if not match or not match.group("path").strip():
        raise c.InputError(f"focus file {source}: cannot parse entry '{spec}'",
                           hint="entries are 'path' or 'path:start-end' (1-based, inclusive)")
    start = int(match.group("start")) if match.group("start") else None
    end = int(match.group("end")) if match.group("end") else start
    if start is not None and end is not None and (start < 1 or end < start):
        raise c.InputError(f"focus file {source}: bad line range in '{spec}'",
                           hint="ranges are 1-based and start <= end")
    return FocusEntry(_normalize_focus_path(match.group("path")), start, end)


def parse_focus(text: str, source: str) -> List[FocusEntry]:
    """Parse a focus list: one 'path[:start-end]' per line, or JSON strings/objects."""
    body = text.strip()
    entries: List[FocusEntry] = []
    if body[:1] in ("[", "{"):
        try:
            decoded = json.loads(body)
        except json.JSONDecodeError as exc:
            raise c.InputError(f"focus file {source} looks like JSON but does not parse: {exc}") from exc
        if isinstance(decoded, dict):
            decoded = decoded.get("entries", decoded.get("focus"))
        if not isinstance(decoded, list):
            raise c.InputError(
                f"focus file {source}: JSON must be a list (or an object with an 'entries' list)",
                hint="items are 'path[:start-end]' strings or {\"path\", \"start\"?, \"end\"?} objects",
            )
        for item in decoded:
            if isinstance(item, str):
                entries.append(_focus_entry(item, source))
            elif isinstance(item, dict) and isinstance(item.get("path"), str):
                start, end = item.get("start"), item.get("end", item.get("start"))
                if start is not None and (
                    not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start
                ):
                    raise c.InputError(f"focus file {source}: bad start/end for {item['path']}")
                entries.append(FocusEntry(_normalize_focus_path(item["path"]), start, end))
            else:
                raise c.InputError(f"focus file {source}: unsupported item {item!r}")
    else:
        for raw in body.splitlines():
            raw = raw.strip()
            if raw and not raw.startswith("#"):
                entries.append(_focus_entry(raw, source))
    if not entries:
        raise c.InputError(f"focus file {source} contains no entries")
    return entries


def load_focus(path: str) -> List[FocusEntry]:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        raise c.InputError(f"cannot read focus file {path}: {exc}") from exc
    return parse_focus(text, path)


def focus_contains(entries: Sequence[FocusEntry], path: str, line: int) -> bool:
    for entry in entries:
        if entry.path != path and not ("*" in entry.path and c.glob_match(path, [entry.path])):
            continue
        if entry.start is None or (entry.start <= line <= (entry.end or entry.start)):
            return True
    return False


def parse_blame_porcelain(output: str) -> Dict[int, Tuple[str, int]]:
    """Map final line number to (sha, author-time) from ``git blame --line-porcelain``."""
    result: Dict[int, Tuple[str, int]] = {}
    sha = ""
    final = 0
    for raw in output.split("\n"):
        header = re.match(r"^([0-9a-f]{40}) \d+ (\d+)", raw)
        if header:
            sha, final = header.group(1), int(header.group(2))
        elif raw.startswith("author-time ") and sha:
            result[final] = (sha, int(raw[len("author-time "):]))
    return result


def _line_ranges(lines: Sequence[int]) -> List[Tuple[int, int]]:
    ranges: List[Tuple[int, int]] = []
    for line in sorted(set(lines)):
        if ranges and line == ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], line)
        else:
            ranges.append((line, line))
    return ranges


def blame_lines(repo: str, path: str, lines: Sequence[int]) -> Dict[int, Tuple[str, int]]:
    """Blame only the given lines of one file, batching ranges into few git calls."""
    result: Dict[int, Tuple[str, int]] = {}
    ranges = _line_ranges(lines)
    for offset in range(0, len(ranges), BLAME_RANGES_PER_CALL):
        chunk = ranges[offset: offset + BLAME_RANGES_PER_CALL]
        args = ["blame", "--line-porcelain"]
        for start, end in chunk:
            args += ["-L", f"{start},{end}"]
        args += ["--", path]
        result.update(parse_blame_porcelain(c.run_git(repo, args, check=False)))
    return result


UNCOMMITTED_SHA = "0" * 40


def apply_blame(
    repo: str, hits: Sequence[Hit], head_time: int, envelope: c.Envelope
) -> Dict[str, List[int]]:
    """Attach blame to hits in place; return known ages (days) per pattern id."""
    by_file: Dict[str, List[Hit]] = {}
    for hit in hits:
        by_file.setdefault(hit.path, []).append(hit)
    ages: Dict[str, List[int]] = {}
    failed_files: List[str] = []
    for path in sorted(by_file):
        file_hits = by_file[path]
        found = blame_lines(repo, path, [h.line for h in file_hits])
        c.log(1, f"blame {path}: {len(found)}/{len(file_hits)} lines resolved")
        unresolved = 0
        for hit in file_hits:
            entry = found.get(hit.line)
            if entry is None:
                hit.blame = {"sha": None, "date": None, "age_days": None, "bucket": "unknown"}
                unresolved += 1
                continue
            sha, author_time = entry
            if sha == UNCOMMITTED_SHA:
                hit.blame = {"sha": "uncommitted", "date": None, "age_days": None, "bucket": "uncommitted"}
                continue
            days = max(0, (head_time - author_time) // 86400)
            date = _iso_date(author_time)
            hit.blame = {"sha": sha[:10], "date": date, "age_days": days, "bucket": age_bucket(days)}
            ages.setdefault(hit.pattern, []).append(days)
        if unresolved:
            failed_files.append(path)
    if failed_files:
        envelope.warn(
            f"git blame returned nothing for {len(failed_files)} file(s) with hits "
            f"(first: {failed_files[0]}); their hits are bucketed 'unknown'"
        )
    uncommitted = sum(1 for h in hits if h.blame and h.blame["bucket"] == "uncommitted")
    if uncommitted:
        envelope.warn(
            f"{uncommitted} hit(s) are on uncommitted lines (working tree differs from HEAD); "
            "they have no age and are bucketed 'uncommitted'"
        )
    return ages


def _iso_date(epoch: int) -> str:
    import datetime as dt

    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).strftime("%Y-%m-%d")


@dataclass
class ScanResult:
    hits: List[Hit]
    files_scanned: int
    test_files_scanned: int
    skipped: Dict[str, List[str]]
    files_without_applicable_pattern: int
    encoding_error_files: List[str]


def read_text(abs_path: str, rel: str, skipped: Dict[str, List[str]], encoding_errors: List[str]) -> Optional[str]:
    try:
        size = os.path.getsize(abs_path)
    except OSError:
        skipped.setdefault("missing", []).append(rel)
        return None
    if size > MAX_FILE_BYTES:
        skipped.setdefault("too_large", []).append(rel)
        return None
    try:
        with open(abs_path, "rb") as fh:
            raw = fh.read()
    except OSError:
        skipped.setdefault("unreadable", []).append(rel)
        return None
    if b"\0" in raw[:8192]:
        skipped.setdefault("binary", []).append(rel)
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
        encoding_errors.append(rel)
    return text[1:] if text.startswith("﻿") else text


def scan_files(
    repo: str,
    files: Sequence[str],
    patterns: Sequence[Pattern],
    test_globs: Sequence[str],
    tests_mode: str,
) -> ScanResult:
    skipped: Dict[str, List[str]] = {}
    encoding_errors: List[str] = []
    hits: List[Hit] = []
    scanned = 0
    test_scanned = 0
    no_pattern = 0
    for rel in files:
        in_tests = is_test_path(rel, test_globs)
        if tests_mode == "only" and not in_tests:
            continue
        if not any(p.compiled is not None and extension_matches(rel, p.extensions) for p in patterns):
            no_pattern += 1
            continue
        text = read_text(os.path.join(repo, rel), rel, skipped, encoding_errors)
        if text is None:
            continue
        scanned += 1
        if in_tests:
            test_scanned += 1
        for hit in scan_text(rel, text, patterns):
            hit.in_tests = in_tests
            hits.append(hit)
    return ScanResult(hits, scanned, test_scanned, skipped, no_pattern, encoding_errors)


def counted_hits(hits: Sequence[Hit], tests_mode: str) -> List[Hit]:
    if tests_mode == "exclude":
        return [h for h in hits if not h.in_tests]
    return list(hits)


def dir_key(path: str, depth: int) -> str:
    parts = path.split("/")[:-1]
    return "/".join(parts[:depth]) if parts else "."


def tally(hits: Iterable[Hit], key) -> Dict[str, Dict[str, int]]:
    table: Dict[str, Dict[str, int]] = {}
    for hit in hits:
        row = table.setdefault(key(hit), {})
        row[hit.pattern] = row.get(hit.pattern, 0) + 1
    return {k: dict(sorted(v.items())) for k, v in sorted(table.items())}


def count_by(hits: Iterable[Hit], key) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for hit in hits:
        k = key(hit)
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def _skipped_json(skipped: Dict[str, List[str]]) -> Dict[str, Any]:
    return {
        reason: {"count": len(paths), "examples": sorted(paths)[:EXAMPLES_PER_SKIP_REASON]}
        for reason, paths in sorted(skipped.items())
    }


def resolve_files(repo: str, include: Sequence[str], exclude: Sequence[str], envelope: c.Envelope) -> List[str]:
    tracked = c.tracked_files(repo)
    for glob in include:
        if not c.select_paths(tracked, [glob], []):
            envelope.warn(f"--include glob '{glob}' matched no tracked file")
    for glob in exclude:
        if not c.select_paths(tracked, [glob], []):
            envelope.warn(f"--exclude glob '{glob}' matched no tracked file")
    selected = c.select_paths(tracked, include, exclude)
    c.log(1, f"{len(tracked)} tracked files, {len(selected)} after include/exclude")
    if not selected:
        envelope.warn("no files left to scan after --include/--exclude")
    return sorted(selected)


def load_packs(specs: Sequence[str], envelope: c.Envelope) -> Tuple[List[Pack], List[Pattern], List[Dict[str, str]]]:
    packs: List[Pack] = []
    owner: Dict[str, str] = {}
    for spec in specs:
        pack = load_pack(spec)
        if any(p.name == pack.name for p in packs):
            raise c.UsageError(f"pack '{pack.name}' given twice", hint="pass each --pack once")
        for pattern in pack.patterns:
            if pattern.id in owner:
                raise c.InputError(
                    f"pattern id '{pattern.id}' appears in both pack '{owner[pattern.id]}' and '{pack.name}'",
                    hint="pattern ids must be unique across the packs scanned together",
                )
            owner[pattern.id] = pack.name
        packs.append(pack)
    patterns = [p for pack in packs for p in pack.patterns]
    regex_errors = [
        {"pack": p.pack, "pattern": p.id, "error": p.error} for p in patterns if p.error
    ]
    for item in regex_errors:
        envelope.warn(f"pattern {item['pattern']} (pack {item['pack']}) skipped: regex does not compile: {item['error']}")
    return packs, patterns, regex_errors


def _split_csv(value: Optional[str], allowed: Sequence[str], flag: str) -> List[str]:
    if value is None:
        return []
    items = [v.strip() for v in value.split(",") if v.strip()]
    bad = [v for v in items if v not in allowed]
    if bad:
        raise c.UsageError(f"{flag}: unknown value(s) {', '.join(bad)}", hint=f"allowed: {', '.join(allowed)}")
    return items


def _head_commit_time(repo: str, envelope: c.Envelope) -> Optional[int]:
    out = c.run_git(repo, ["log", "-1", "--format=%ct", "HEAD"], check=False).strip()
    if not out.isdigit():
        envelope.warn("repository has no HEAD commit; --blame skipped")
        return None
    if c.run_git(repo, ["rev-parse", "--is-shallow-repository"], check=False).strip() == "true":
        envelope.warn(
            "shallow clone: git blame attributes lines to the shallow boundary commit, so ages are lower bounds"
        )
    return int(out)


def command_scan(ns: argparse.Namespace) -> int:
    envelope = c.Envelope(tool=TOOL, args=c.args_dict(ns))
    envelope.repo = c.repo_info(ns.repo)
    repo = envelope.repo["path"]
    group_by = _split_csv(ns.group_by, GROUP_DIMENSIONS, "--group-by")
    if ns.group_by is not None and "age" in group_by and not ns.blame:
        raise c.UsageError("--group-by age needs --blame", hint="add --blame (slow: runs git blame per file with hits)")
    if ns.max_hits < 0:
        raise c.UsageError("--max-hits must be >= 0")
    if ns.dir_depth < 1:
        raise c.UsageError("--dir-depth must be >= 1")
    if not group_by:
        group_by = ["category", "dir", "ext"] + (["age"] if ns.blame else [])

    packs, patterns, regex_errors = load_packs(ns.pack, envelope)
    focus_entries = load_focus(ns.focus_file) if ns.focus_file else []
    test_globs = DEFAULT_TEST_GLOBS + list(ns.test_glob or [])
    for pack in packs:
        if pack.applies_to_tests and ns.tests == "exclude":
            envelope.warn(
                f"pack '{pack.name}' targets test files but --tests is 'exclude'; its totals will be near zero. "
                "Rerun with --tests include or --tests only"
            )

    files = resolve_files(repo, ns.include or [], ns.exclude or [], envelope)
    result = scan_files(repo, files, patterns, test_globs, ns.tests)
    if ns.tests != "include" and result.test_files_scanned == 0 and ns.tests == "only":
        envelope.warn("--tests only matched no test files; check --test-glob")
    for reason, paths in sorted(result.skipped.items()):
        envelope.warn(f"{len(paths)} file(s) skipped ({reason}), e.g. {sorted(paths)[0]}")
    if result.encoding_error_files:
        envelope.warn(
            f"{len(result.encoding_error_files)} file(s) are not valid UTF-8; undecodable bytes were replaced"
        )

    in_scope = counted_hits(result.hits, ns.tests)
    in_scope.sort(key=lambda h: (h.path, h.line, h.pattern, h.text))
    test_hits = sorted(
        (h for h in result.hits if h.in_tests), key=lambda h: (h.path, h.line, h.pattern, h.text)
    )

    if focus_entries:
        scanned_paths = set(files)
        for entry in focus_entries:
            entry.matched_files = sum(
                1 for p in scanned_paths if p == entry.path or ("*" in entry.path and c.glob_match(p, [entry.path]))
            )
            if not entry.matched_files:
                envelope.warn(f"focus entry '{entry.path}' matches no scanned file")
        for hit in in_scope:
            hit.focus = focus_contains(focus_entries, hit.path, hit.line)

    ages: Dict[str, List[int]] = {}
    if ns.blame:
        head_time = _head_commit_time(repo, envelope)
        if head_time is not None:
            ages = apply_blame(repo, in_scope, head_time, envelope)

    data = build_data(ns, packs, patterns, regex_errors, result, in_scope, test_hits, focus_entries, ages, group_by)
    envelope.data = data
    c.write_output(envelope, ns, scan_text_summary)
    return c.EXIT_OK


def _totals(patterns: Sequence[Pattern], hits: Sequence[Hit], ages: Dict[str, List[int]], blamed: bool) -> Dict[str, Any]:
    by_pattern: Dict[str, Any] = {}
    counts = count_by(hits, lambda h: h.pattern)
    for pattern in sorted(patterns, key=lambda p: p.id):
        entry: Dict[str, Any] = {
            "count": counts.get(pattern.id, 0),
            "category": pattern.category,
            "pack": pattern.pack,
        }
        if pattern.rubric:
            entry["rubric"] = pattern.rubric
        if pattern.heuristic:
            entry["heuristic"] = True
        if pattern.error:
            entry["error"] = "regex did not compile; not counted"
        if blamed:
            entry["median_age_days"] = lower_median(ages.get(pattern.id, []))
        by_pattern[pattern.id] = entry
    categories = {p.id: p.category for p in patterns}
    by_category = count_by(hits, lambda h: categories[h.pattern])
    return {"total": len(hits), "by_pattern": by_pattern, "by_category": by_category}


def build_data(
    ns: argparse.Namespace,
    packs: Sequence[Pack],
    patterns: Sequence[Pattern],
    regex_errors: List[Dict[str, str]],
    result: ScanResult,
    in_scope: List[Hit],
    test_hits: List[Hit],
    focus_entries: Sequence[FocusEntry],
    ages: Dict[str, List[int]],
    group_by: Sequence[str],
) -> Dict[str, Any]:
    categories = {p.id: p.category for p in patterns}
    data: Dict[str, Any] = {
        "method": (
            "line-oriented regex scan of tracked files; one hit per regex match; patterns marked code_only "
            "match a view of the line with string literals and trailing comments blanked; patterns marked "
            "heuristic list candidates, not confirmed defects"
        ),
        "tests_mode": ns.tests,
        "packs": [
            {
                "name": p.name,
                "version": p.version,
                "patterns": len(p.patterns),
                "applies_to_tests": p.applies_to_tests,
                "limitations": p.limitations,
            }
            for p in packs
        ],
        "totals": _totals(patterns, in_scope, ages, ns.blame),
    }
    if "category" in group_by:
        data["by_category"] = tally(in_scope, lambda h: categories[h.pattern])
    if "dir" in group_by:
        data["by_dir"] = tally(in_scope, lambda h: dir_key(h.path, ns.dir_depth))
    if "ext" in group_by:
        data["by_ext"] = tally(in_scope, lambda h: file_extension(h.path))
    if ns.blame and "age" in group_by:
        data["by_age"] = tally(in_scope, lambda h: (h.blame or {}).get("bucket", "unknown"))
    if focus_entries:
        focused = [h for h in in_scope if h.focus]
        data["focus"] = {
            "entries": len(focus_entries),
            "entries_without_files": sorted(e.path for e in focus_entries if not e.matched_files),
            "total": len(focused),
            "by_pattern": count_by(focused, lambda h: h.pattern),
            "by_category": count_by(focused, lambda h: categories[h.pattern]),
            "by_file": count_by(focused, lambda h: h.path),
        }
    data["tests"] = {
        "counted_in_totals": ns.tests != "exclude",
        "test_files_scanned": result.test_files_scanned,
        "total": len(test_hits),
        "by_pattern": count_by(test_hits, lambda h: h.pattern),
        "by_category": count_by(test_hits, lambda h: categories[h.pattern]),
    }
    shown = in_scope[: ns.max_hits]
    data["hits"] = [h.to_json() for h in shown]
    data["hits_shown"] = len(shown)
    data["hits_total"] = len(in_scope)
    data["hits_truncated"] = len(in_scope) > len(shown)
    if data["hits_truncated"]:
        data["hits_truncated_note"] = (
            f"{len(in_scope) - len(shown)} hit(s) omitted by --max-hits {ns.max_hits}; hits are sorted by "
            "path then line, so the omitted ones are the alphabetically last files. Counts above are complete"
        )
    data["files_scanned"] = result.files_scanned
    data["files_without_applicable_pattern"] = result.files_without_applicable_pattern
    data["files_skipped"] = _skipped_json(result.skipped)
    data["files_with_encoding_errors"] = {
        "count": len(result.encoding_error_files),
        "examples": sorted(result.encoding_error_files)[:EXAMPLES_PER_SKIP_REASON],
    }
    data["regex_errors"] = regex_errors
    return data


def _table(rows: List[List[str]], headers: List[str]) -> List[str]:
    widths = [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
    lines = ["  ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))]
    lines += ["  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(r)) for r in rows]
    return lines


def scan_text_summary(data: Dict[str, Any]) -> str:
    lines = [
        f"packs: {', '.join(p['name'] + ' v' + p['version'] for p in data['packs'])}",
        f"tests mode: {data['tests_mode']}   files scanned: {data['files_scanned']}   "
        f"hits counted: {data['totals']['total']}",
        "",
    ]
    rows = []
    for pid, entry in data["totals"]["by_pattern"].items():
        if entry["count"]:
            flag = "~" if entry.get("heuristic") else ""
            median = entry.get("median_age_days")
            rows.append([pid + flag, entry["category"], str(entry["count"]), "" if median is None else f"{median}d"])
    if rows:
        lines += _table(rows, ["pattern (~ heuristic)", "category", "count", "median age"])
    else:
        lines.append("no hits")
    if data["totals"]["by_category"]:
        lines += ["", "by category: " + ", ".join(f"{k}={v}" for k, v in data["totals"]["by_category"].items())]
    if "by_dir" in data:
        dirs = sorted(((sum(v.values()), k) for k, v in data["by_dir"].items()), reverse=True)[:10]
        lines += ["", "top dirs:"] + [f"  {n:5d}  {d}" for n, d in dirs]
    if "by_age" in data:
        lines += ["", "by age: " + ", ".join(f"{k}={sum(v.values())}" for k, v in data["by_age"].items())]
    if "focus" in data:
        lines += ["", f"focus: {data['focus']['total']} hit(s) in {data['focus']['entries']} entries"]
    tests = data["tests"]
    lines += ["", f"test files: {tests['total']} hit(s) in {tests['test_files_scanned']} files "
              f"({'included in totals' if tests['counted_in_totals'] else 'excluded from totals'})"]
    if data["hits_truncated"]:
        lines.append(f"hits truncated: showing {data['hits_shown']} of {data['hits_total']}")
    for reason, info in data["files_skipped"].items():
        lines.append(f"skipped ({reason}): {info['count']}")
    for err in data["regex_errors"]:
        lines.append(f"regex error: {err['pattern']}: {err['error']}")
    return "\n".join(lines)


def command_list_packs(ns: argparse.Namespace) -> int:
    envelope = c.Envelope(tool=TOOL, args=c.args_dict(ns))
    rows = []
    for name in shipped_pack_names():
        pack = load_pack(name)
        rows.append(
            {
                "name": pack.name,
                "version": pack.version,
                "patterns": len(pack.patterns),
                "applies_to_tests": pack.applies_to_tests,
                "description": pack.description,
            }
        )
    envelope.data = {"packs_dir": "scripts/packs", "packs": rows}
    c.write_output(
        envelope,
        ns,
        lambda d: "\n".join(f"{r['name']:18s} {r['patterns']:3d} patterns  {r['description']}" for r in d["packs"]),
    )
    return c.EXIT_OK


def command_show_pack(ns: argparse.Namespace) -> int:
    envelope = c.Envelope(tool=TOOL, args=c.args_dict(ns))
    pack = load_pack(ns.name)
    envelope.data = pack.to_json()
    for pattern in pack.patterns:
        if pattern.error:
            envelope.warn(f"pattern {pattern.id}: regex does not compile: {pattern.error}")

    def text(d: Dict[str, Any]) -> str:
        out = [f"{d['name']} v{d['version']}: {d['description']}"]
        out += [f"  limitation: {x}" for x in d["limitations"]]
        for p in d["patterns"]:
            marks = "".join(
                [" [heuristic]" if p.get("heuristic") else "", " [code-only]" if p.get("code_only") else ""]
            )
            ext = ",".join(p.get("extensions", [])) or "all files"
            out.append(f"  {p['id']} ({p['category']}, {ext}){marks}")
            out.append(f"      /{p['regex']}/  {p['description']}")
        return "\n".join(out)

    c.write_output(envelope, ns, text)
    return c.EXIT_OK


def introducing_commit(repo: str, path: str, literal: str) -> Tuple[Optional[Dict[str, str]], int]:
    out = c.run_git(
        repo,
        ["log", "-S" + literal, "--format=%H%x09%aI%x09%an%x09%s", "--reverse", "--", path],
        check=False,
    )
    rows = [r for r in out.split("\n") if r.strip()]
    if not rows:
        return None, 0
    sha, date, author, subject = (rows[0].split("\t", 3) + ["", "", ""])[:4]
    return {"sha": sha[:10], "date": date, "author": author, "subject": subject}, len(rows)


def command_first_seen(ns: argparse.Namespace) -> int:
    envelope = c.Envelope(tool=TOOL, args=c.args_dict(ns))
    envelope.repo = c.repo_info(ns.repo)
    repo = envelope.repo["path"]
    if ns.max < 1:
        raise c.UsageError("--max must be >= 1")
    pack = load_pack(ns.pack)
    target = next((p for p in pack.patterns if p.id == ns.pattern_id), None)
    if target is None:
        raise c.InputError(
            f"pack '{pack.name}' has no pattern '{ns.pattern_id}'",
            hint=f"pattern ids: {', '.join(p.id for p in pack.patterns)}",
        )
    if target.error:
        raise c.InputError(f"pattern {target.id}: regex does not compile: {target.error}")
    files = resolve_files(repo, ns.include or [], ns.exclude or [], envelope)
    test_globs = DEFAULT_TEST_GLOBS + list(ns.test_glob or [])
    result = scan_files(repo, files, [target], test_globs, ns.tests)
    hits = sorted(counted_hits(result.hits, ns.tests), key=lambda h: (h.path, h.line, h.text))
    examined = hits[: ns.max]
    cache: Dict[Tuple[str, str], Tuple[Optional[Dict[str, str]], int]] = {}
    results = []
    for hit in examined:
        key = (hit.path, hit.text)
        if key not in cache:
            c.log(1, f"git log -S on {hit.path}: {hit.text!r}")
            cache[key] = introducing_commit(repo, hit.path, hit.text)
        commit, touching = cache[key]
        results.append(
            {
                "path": hit.path,
                "line": hit.line,
                "text": hit.text,
                "introduced_by": commit,
                "commits_changing_literal": touching,
            }
        )
    if any(r["introduced_by"] is None for r in results):
        envelope.warn("some hits have no commit changing their text in this file's history: uncommitted, or history is shallow")
    if len(hits) > len(examined):
        envelope.warn(f"{len(hits) - len(examined)} hit(s) not examined (--max {ns.max})")
    envelope.data = {
        "pattern": target.id,
        "pack": pack.name,
        "method": (
            "git log -S<matched text> scoped to the file, oldest first; the oldest commit that changed the number "
            "of occurrences of that text in the file. It is where the text first appeared, not necessarily where "
            "this exact line was written; identical text in the same file shares one answer"
        ),
        "hits_total": len(hits),
        "hits_examined": len(examined),
        "results": results,
    }
    c.write_output(
        envelope,
        ns,
        lambda d: "\n".join(
            f"{r['path']}:{r['line']}  "
            + (f"{r['introduced_by']['date'][:10]} {r['introduced_by']['sha']} {r['introduced_by']['subject']}"
               if r["introduced_by"] else "(no introducing commit found)")
            for r in d["results"]
        ) or "no hits",
    )
    return c.EXIT_OK


SCAN_DESCRIPTION = """\
Count and list pattern hits (suppressions, skipped tests, escape hatches, permissive
flags, failure-policy settings, timers, blocking calls) across the tracked files of a
repository, driven by JSON pattern packs. An audit needs the numbers to be mechanical,
repeatable and anchored: every hit has a path and line, every count says how it was
computed, and nothing is silently dropped.

counting convention: production code only. Test files (default globs: test/, tests/,
__tests__/, fixtures/, e2e/, *.test.*, *.spec.*, test_*.py, *_test.go, *Test.java ...;
--test-glob adds more) are scanned but kept out of totals and reported in `tests`.

pack format (JSON; validated on load, errors name the pack, pattern index and key):
  {"name": str, "description": str, "version": str|int,
   "limitations": [str]?, "applies_to_tests": bool?,
   "patterns": [{"id": str, "category": str, "regex": str, "description": str,
                 "flags": "i"?, "extensions": [".ts", "Makefile"]?,
                 "exclude_regex": str?, "rubric": "G4"?,
                 "heuristic": bool?, "code_only": bool?}]}
  extensions: ".ts" matches a file-name suffix (so ".d.ts" works), a bare name such as
  "Makefile" matches that exact file name; omitted = every text file. exclude_regex drops
  a line that matches it. code_only matches against the line with string literals and
  trailing comments blanked. heuristic labels candidates that need a human read. Regexes
  are Python `re`, applied per line; a regex that does not compile is reported in
  `regex_errors` and skipped. Pattern ids must be unique across packs scanned together.

output `data` fields:
  packs         name, version, pattern count, limitations of each pack scanned
  totals        total; by_pattern {id: count, category, pack, rubric?, heuristic?, median_age_days?};
                by_category {category: count}. Every loaded pattern appears, with 0 if no hit
  by_category / by_dir / by_ext / by_age
                {group: {pattern id: count}} (--group-by; by_age needs --blame; dir depth --dir-depth)
  focus         hits (counted in totals) inside --focus-file ranges: total, by_pattern, by_category,
                by_file, entries_without_files
  tests         test-file hits: counted_in_totals, test_files_scanned, total, by_pattern, by_category
  hits          up to --max-hits {path, line, pattern, text (matched, <=200 chars), context (line,
                <=200 chars), focus?, blame?: {sha, date, age_days, bucket}}; hits_total,
                hits_shown, hits_truncated report any cap. Sorted by path, line
  files_scanned, files_without_applicable_pattern (skipped before reading: no pattern applies
                to that file type), files_skipped {reason: {count, examples}} (binary, too_large
                >2 MB, unreadable, missing), files_with_encoding_errors, regex_errors

caveats: this is a text scan, not a parse. A hit inside a string, comment or doc is still a
hit unless the pattern is code_only; heuristic patterns over-count; counts say how many
places exist, not how risky each is. Ages (--blame) are relative to the HEAD commit date,
use the author date of the blamed line, and are lower bounds in shallow clones; lines
changed in the working tree are bucketed 'uncommitted'. Renames and mass reformatting
reset age.
"""

SCAN_EXAMPLES = """\
  python -I scripts/patterns.py scan --pack suppressions --pack escape-hatches --repo . --blame
  python -I scripts/patterns.py scan --pack skips --tests only --group-by dir,age --blame
  python -I scripts/patterns.py scan --pack escape-hatches --focus-file ingestion.txt --include "src/**"
  python -I scripts/patterns.py scan --pack ./my-pack.json --max-hits 50 --format text"""


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="patterns.py",
        description=(
            "Language-neutral, pack-driven text scanner: counts and lists pattern hits with path:line anchors.\n"
            "Subcommands: scan, list-packs, show-pack, first-seen. Run `patterns.py <command> --help` for details.\n"
            "Shipped packs: " + ", ".join(shipped_pack_names())
        ),
        epilog=c.EXIT_CODES_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    root.add_argument("--version", action="version", version=f"%(prog)s {c.VERSION}")
    sub = root.add_subparsers(dest="command", metavar="{scan,list-packs,show-pack,first-seen}")
    sub.required = True

    def add(name: str, description: str, examples: str, with_repo: bool = True) -> argparse.ArgumentParser:
        parser = sub.add_parser(
            name,
            description=description,
            epilog=f"examples:\n{examples}\n\n{c.EXIT_CODES_HELP}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            help=description.split("\n", 1)[0],
        )
        c.add_common_flags(parser, with_repo=with_repo)
        return parser

    def add_selection(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--include", action="append", metavar="GLOB",
                            help="only scan tracked files matching this glob (repeatable; ** = any depth); default: all")
        parser.add_argument("--exclude", action="append", metavar="GLOB",
                            help="skip tracked files matching this glob (repeatable)")
        parser.add_argument("--tests", choices=("include", "exclude", "only"), default="exclude",
                            help="exclude (default): test files are scanned but counted only in `tests`; "
                                 "include: counted with everything else; only: scan test files only")
        parser.add_argument("--test-glob", action="append", metavar="GLOB",
                            help="extra glob that marks a file as a test file, added to the built-in defaults (repeatable)")

    scan = add("scan", SCAN_DESCRIPTION, SCAN_EXAMPLES)
    scan.add_argument("--pack", action="append", required=True, metavar="NAME|PATH",
                      help="shipped pack name (see list-packs) or path to a pack JSON file; repeatable")
    add_selection(scan)
    scan.add_argument("--focus-file", metavar="FILE",
                      help="text (one 'path' or 'path:start-end' per line, # comments) or JSON list of the same; "
                           "hits inside are also counted under `focus` (e.g. escape hatches at ingestion points)")
    scan.add_argument("--blame", action="store_true",
                      help="attach commit sha/date per hit via git blame (batched per file; slower), age buckets "
                           "<30d, 30-90d, 90-365d, >365d relative to the HEAD commit date, median age per pattern")
    scan.add_argument("--max-hits", type=int, default=500, metavar="N",
                      help="list at most N hits in `hits` (default 500); counts are never capped; 0 lists none")
    scan.add_argument("--group-by", metavar="LIST",
                      help="comma list of category,dir,ext,age selecting the by_* breakdowns "
                           "(default: category,dir,ext, plus age with --blame)")
    scan.add_argument("--dir-depth", type=int, default=2, metavar="N",
                      help="directory levels used by by_dir (default 2: 'src/server')")
    scan.set_defaults(func=command_scan)

    lst = add("list-packs", "List the shipped packs with description and pattern count.",
              "  python -I scripts/patterns.py list-packs --format text", with_repo=False)
    lst.set_defaults(func=command_list_packs)

    show = add("show-pack", "Print a pack's patterns so you can see exactly what is counted.",
               "  python -I scripts/patterns.py show-pack escape-hatches --format text\n"
               "  python -I scripts/patterns.py show-pack ./my-pack.json", with_repo=False)
    show.add_argument("name", metavar="NAME|PATH", help="shipped pack name or path to a pack JSON file")
    show.set_defaults(func=command_show_pack)

    first = add(
        "first-seen",
        "For each current hit of one pattern, find the commit that first introduced that text in the file.\n"
        "SLOW: runs `git log -S` (a full history walk) per distinct file+text, so it is capped by --max. Use it to date\n"
        "a handful of hits (a cluster, the newest suspicious ones), not to date every hit; for ages of all hits use\n"
        "`scan --blame`. Method: the oldest commit that changed the number of occurrences of the matched text in the\n"
        "file; with identical text repeated in one file, that is where the first copy appeared.\n"
        "output `data`: pattern, pack, method, hits_total, hits_examined, results [{path, line, text, "
        "introduced_by {sha, date, author, subject} | null, commits_changing_literal}].",
        "  python -I scripts/patterns.py first-seen --pack suppressions --pattern-id suppress-ts-ignore --max 10",
    )
    first.add_argument("--pack", required=True, metavar="NAME|PATH", help="shipped pack name or pack file path")
    first.add_argument("--pattern-id", required=True, metavar="ID", help="pattern id inside the pack (see show-pack)")
    first.add_argument("--max", type=int, default=20, metavar="N", help="examine at most N hits (default 20)")
    add_selection(first)
    first.set_defaults(func=command_first_seen)
    return root


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    c.set_verbosity(ns.verbose)
    return ns.func(ns)


if __name__ == "__main__":
    c.run_main(main)
