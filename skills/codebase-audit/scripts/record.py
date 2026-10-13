#!/usr/bin/env python3
"""Keep the codebase-audit run record: log agent dispatches and script runs, index the run, check it for gaps."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from typing import Any
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402

TOOL = "record"
STATUSES = ("ok", "failed", "empty", "partial")
DISPOSITIONS = ("merged", "kept", "downgraded", "refuted", "dropped", "duplicate")
SEVERITIES = ("critical", "high", "medium", "low")
CONFIDENCES = ("high", "medium", "low")
VERDICTS = ("CONFIRMED", "DOWNGRADE", "REFUTED")
REVIEW_NAME = "review.md"
INDEX_NAME = "index.json"
LEDGER_NAME = "ledger.jsonl"
GENERATED = (REVIEW_NAME, INDEX_NAME)
FINDING_FIELDS = ("severity", "confidence", "rubric", "anchors", "status", "evidence", "exposure")
REQUIRED_FINDING_FIELDS = ("severity", "confidence", "rubric", "anchors")
RUN_PATH_PREFIXES = ("work/", "verdicts/", "findings/", "summaries/", "briefs/", "facts/", "measurements/", "scripts/")

HEADING_RE = re.compile(r"^(#{1,6})\s*(.*?)\s*#*\s*$")
BOLD_HEADING_RE = re.compile(r"^\**\s*(dismissed|not\s+assessed)\b[^\n]*?\**\s*:?\**\s*$", re.I)
FINDING_HEAD_RE = re.compile(r"^(F|AC)-[A-Za-z0-9_.\-]*[A-Za-z0-9_]", re.I)
FIELD_RE = re.compile(r"^\s*[-*+]\s+\**\s*([A-Za-z][A-Za-z _-]*?)\s*\**\s*:\s*\**\s*(.*?)\s*$")
BULLET_RE = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$")
PATH_TOKEN_RE = re.compile(r"[\w@.\-/\\]*[\w@\-]\.[A-Za-z][A-Za-z0-9]{0,5}(?::\d+(?:-\d+)?)?")
ENV_PATH_KEYS = ("path", "file", "anchor", "source")
ENTRY_KEYS = ("ingestion", "entry_points", "entrypoints", "entrypoint", "entry-points")


class Collector:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        if message not in self.items:
            self.items.append(message)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def fwd(path: str) -> str:
    return path.replace("\\", "/")


def read_text(path: str, warns: Collector | None = None) -> str | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError as exc:
        if warns is not None:
            warns.add(f"{fwd(path)}: unreadable ({exc.strerror or exc})")
        return None


def run_dir(ns: argparse.Namespace) -> str:
    path = os.path.abspath(ns.run)
    if not os.path.isdir(path):
        raise c.InputError(f"--run is not a directory: {ns.run}", hint="create docs/audits/<date>-<mode>/ first")
    if ns.out and not inside(path, os.path.abspath(ns.out)):
        raise c.UsageError("--out must be inside --run: record.py writes only inside the run directory",
                           hint="drop --out or point it into the run directory")
    return path


def inside(root: str, path: str) -> bool:
    try:
        return os.path.commonpath([os.path.normcase(root), os.path.normcase(path)]) == os.path.normcase(root)
    except ValueError:
        return False


def run_relative(run: str, path: str) -> str:
    """Express ``path`` relative to the run directory with forward slashes; keep it as given when outside."""
    if os.path.isabs(path):
        full = os.path.abspath(path)
        return fwd(os.path.relpath(full, run)) if inside(run, full) else fwd(path)
    return fwd(os.path.normpath(path))


def run_path_exists(run: str, rel: str) -> bool:
    full = rel if os.path.isabs(rel) else os.path.join(run, rel)
    return os.path.exists(full)


# ---------------------------------------------------------------- ledger

def ledger_file(run: str) -> str:
    return os.path.join(run, LEDGER_NAME)


def read_ledger(run: str, warns: Collector | None = None) -> tuple[list[dict[str, Any]], list[int]]:
    path = ledger_file(run)
    events: list[dict[str, Any]] = []
    invalid: list[int] = []
    text = read_text(path) if os.path.exists(path) else None
    for number, line in enumerate((text or "").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            event = None
        if not isinstance(event, dict) or "event" not in event:
            invalid.append(number)
            if warns is not None:
                warns.add(f"{LEDGER_NAME}:{number}: not a ledger event, skipped")
            continue
        event["_line"] = number
        events.append(event)
    return events, invalid


class LedgerLock:
    """Serialises seq assignment between processes; plain appends need no lock."""

    def __init__(self, run: str) -> None:
        self.path = ledger_file(run) + ".lock"
        self.fd: int | None = None

    def __enter__(self) -> "LedgerLock":
        deadline = time.time() + 10
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                if time.time() > deadline or self._stale():
                    self._remove()
                    deadline = time.time() + 10
                time.sleep(0.02)

    def _stale(self) -> bool:
        try:
            return time.time() - os.path.getmtime(self.path) > 30
        except OSError:
            return False

    def _remove(self) -> None:
        try:
            os.remove(self.path)
        except OSError:
            pass

    def __exit__(self, *exc: Any) -> None:
        if self.fd is not None:
            os.close(self.fd)
        self._remove()


def append_event(run: str, event: dict[str, Any]) -> None:
    line = (json.dumps(event, ensure_ascii=False, sort_keys=False) + "\n").encode("utf-8")
    fd = os.open(ledger_file(run), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)


def clean_event(event: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in event.items() if not k.startswith("_")}


def dispatch_events(events: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {e["seq"]: e for e in events if e.get("event") == "dispatch" and isinstance(e.get("seq"), int)}


def warn_missing(env: c.Envelope, run: str, kind: str, paths: list[str]) -> None:
    for rel in paths:
        if not run_path_exists(run, rel):
            env.warn(f"{kind} does not exist in the run directory: {rel}")


def log_envelope(ns: argparse.Namespace, event: dict[str, Any], env: c.Envelope, run: str) -> int:
    env.data = {"ledger": LEDGER_NAME, "run": fwd(run), **({"seq": event["seq"]} if "seq" in event else {}),
                "event": clean_event(event)}
    c.write_output(env, ns, lambda d: f"logged {d['event']['event']}" + (f" seq {d['seq']}" if "seq" in d else ""))
    return c.EXIT_OK


def cmd_log_dispatch(ns: argparse.Namespace) -> int:
    run = run_dir(ns)
    env = c.Envelope(TOOL, c.args_dict(ns))
    brief = run_relative(run, ns.brief)
    inputs = [run_relative(run, p) for p in ns.input]
    warn_missing(env, run, "brief", [brief])
    warn_missing(env, run, "input", inputs)
    with LedgerLock(run):
        events, _ = read_ledger(run)
        seq = max(dispatch_events(events), default=0) + 1
        event = {"seq": seq, "event": "dispatch", "wave": ns.wave, "role": ns.role, "tier": ns.tier,
                 "model": ns.model, "brief": brief, "inputs": inputs, "started": now_iso(), "label": ns.label}
        append_event(run, event)
    c.log(1, f"dispatch seq {seq} role {ns.role}")
    return log_envelope(ns, event, env, run)


def cmd_log_done(ns: argparse.Namespace) -> int:
    run = run_dir(ns)
    env = c.Envelope(TOOL, c.args_dict(ns))
    events, _ = read_ledger(run)
    dispatches = dispatch_events(events)
    if ns.seq not in dispatches:
        raise c.InputError(f"no dispatch with seq {ns.seq} in {LEDGER_NAME}",
                           hint=f"known seqs: {sorted(dispatches) or 'none'}; log the dispatch first")
    if any(e.get("event") == "done" and e.get("seq") == ns.seq for e in events):
        env.warn(f"seq {ns.seq} already has a done event; this one is appended as a correction")
    outputs = [run_relative(run, p) for p in ns.output]
    summary = run_relative(run, ns.summary) if ns.summary else None
    warn_missing(env, run, "output", outputs)
    if summary:
        warn_missing(env, run, "summary", [summary])
    started = parse_time(dispatches[ns.seq].get("started"))
    duration = ns.duration_s if ns.duration_s is not None else (
        round((dt.datetime.now(dt.timezone.utc) - started).total_seconds()) if started else None)
    event = {"seq": ns.seq, "event": "done", "status": ns.status, "outputs": outputs, "summary": summary,
             "duration_s": duration, "tokens": ns.tokens, "finished": now_iso()}
    append_event(run, event)
    c.log(1, f"done seq {ns.seq} status {ns.status}")
    return log_envelope(ns, event, env, run)


def cmd_log_script(ns: argparse.Namespace) -> int:
    run = run_dir(ns)
    env = c.Envelope(TOOL, c.args_dict(ns))
    output = run_relative(run, ns.output) if ns.output else None
    if output:
        warn_missing(env, run, "output", [output])
    if ns.exit != 0 and not ns.note:
        env.warn("nonzero exit with no --note: check will flag this until a note explains it")
    event = {"event": "script", "command": ns.command, "exit": ns.exit, "output": output, "note": ns.note,
             "at": now_iso()}
    append_event(run, event)
    return log_envelope(ns, event, env, run)


def cmd_log_note(ns: argparse.Namespace) -> int:
    run = run_dir(ns)
    env = c.Envelope(TOOL, c.args_dict(ns))
    event = {"event": "note", "text": ns.text, "at": now_iso()}
    append_event(run, event)
    return log_envelope(ns, event, env, run)


def parse_time(value: Any) -> dt.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


# ---------------------------------------------------------------- markdown parsing

def split_paths(text: str | None) -> list[str]:
    return [part.strip() for part in re.split(r"\s*;\s*", text) if part.strip()] if text else []


def first_word(value: str | None, allowed: tuple[str, ...]) -> str | None:
    if not value:
        return None
    word = re.sub(r"[^a-z]", "", value.strip().lstrip("*`_ ").split(" ")[0].lower())
    return word if word in allowed else None


def classify_not_assessed(text: str) -> str:
    low = text.lower()
    if re.search(r"could not read|cannot read|can't read|unreadable|not readable|too large to read", low):
        return "could not read"
    if re.search(r"profile-blocked|blocked|unknown|no access|not available|unavailable|no `?gh`?", low):
        return "profile-blocked"
    if re.search(r"ruled out|profile rules|does not apply|not applicable|n/a|applies when", low):
        return "ruled out by profile"
    if re.search(r"sample|structurally|not read|skimmed|outside|remaining|the other \d+|beyond", low):
        return "out of sample"
    return "other"


def split_reason(text: str) -> tuple[str, str]:
    match = re.search(r"\s*(?:→|->|—>|:)\s+", text)
    if match:
        return text[:match.start()].strip(), text[match.end():].strip()
    return text.strip(), ""


def path_tokens(text: str) -> list[str]:
    tokens = []
    for raw in PATH_TOKEN_RE.findall(text.replace("`", " ")):
        token = fwd(raw).strip(".")
        if token and token not in tokens:
            tokens.append(token)
    return tokens


def parse_findings_text(text: str, rel: str, warns: Collector) -> dict[str, Any]:
    lines = text.splitlines()
    blocks: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    current_block: dict[str, Any] | None = None
    current_section: dict[str, Any] | None = None
    section_level = 0
    last_item: dict[str, Any] | None = None

    for number, line in enumerate(lines, 1):
        heading = HEADING_RE.match(line)
        pseudo = BOLD_HEADING_RE.match(line) if not heading and not BULLET_RE.match(line) else None
        if heading:
            level, title = len(heading.group(1)), heading.group(2).strip().strip("*").strip()
            current_block = None
            last_item = None
            if current_section is not None and level <= section_level:
                current_section = None
            if FINDING_HEAD_RE.match(title):
                current_section = None
                current_block = new_block(title, number)
                blocks.append(current_block)
            elif re.match(r"(dismissed|not\s+assessed)\b", title, re.I):
                kind = "dismissed" if title.lower().startswith("dismissed") else "not_assessed"
                current_section = {"kind": kind, "line": number, "items": []}
                section_level = level
                sections.append(current_section)
            continue
        if pseudo:
            kind = "dismissed" if pseudo.group(1).lower() == "dismissed" else "not_assessed"
            current_block = None
            last_item = None
            current_section = {"kind": kind, "line": number, "items": []}
            section_level = 6
            sections.append(current_section)
            continue
        if current_block is not None:
            field = FIELD_RE.match(line)
            if field:
                key = re.sub(r"[ _-]+", " ", field.group(1).strip().lower())
                if key in FINDING_FIELDS and key not in current_block["fields"]:
                    current_block["fields"][key] = field.group(2)
            continue
        if current_section is not None:
            bullet = BULLET_RE.match(line)
            if bullet and len(bullet.group(1)) <= 1:
                last_item = {"text": bullet.group(2).strip(), "line": number}
                current_section["items"].append(last_item)
            elif bullet and last_item is not None:
                last_item["text"] += " " + bullet.group(2).strip()
            elif line.strip() and last_item is not None and line.startswith((" ", "\t")):
                last_item["text"] += " " + line.strip()

    findings, conflicts = [], []
    for block in blocks:
        record = finish_block(block, rel, warns)
        (conflicts if record["kind"] == "authority_conflict" else findings).append(record)

    dismissed, not_assessed = [], []
    for section in sections:
        for item in section["items"]:
            candidate, reason = split_reason(item["text"])
            record = {"file": rel, "line": item["line"], "text": item["text"], "candidate": candidate,
                      "reason": reason or None, "anchors": path_tokens(item["text"])}
            if section["kind"] == "dismissed":
                dismissed.append(record)
            else:
                record["reason_group"] = classify_not_assessed(item["text"])
                not_assessed.append(record)
    return {"file": rel, "findings": findings, "authority_conflicts": conflicts, "dismissed": dismissed,
            "not_assessed": not_assessed,
            "has_dismissed": any(s["kind"] == "dismissed" for s in sections),
            "has_not_assessed": any(s["kind"] == "not_assessed" for s in sections)}


def new_block(title: str, line: int) -> dict[str, Any]:
    match = FINDING_HEAD_RE.match(title)
    ident = match.group(0) if match else title
    rest = title[len(ident):].lstrip(" \t·:—–-").strip()
    return {"id": ident, "title": rest, "line": line, "fields": {}}


def finish_block(block: dict[str, Any], rel: str, warns: Collector) -> dict[str, Any]:
    is_conflict = block["id"].upper().startswith("AC-")
    fields = block["fields"]
    record: dict[str, Any] = {"id": block["id"], "kind": "authority_conflict" if is_conflict else "finding",
                              "title": block["title"], "file": rel, "line": block["line"]}
    if is_conflict:
        record["conventions"] = fields.get("conventions")
        return record
    record["severity"] = first_word(fields.get("severity"), SEVERITIES)
    record["confidence"] = first_word(fields.get("confidence"), CONFIDENCES)
    record["rubric"] = fields.get("rubric") or None
    record["anchors"] = split_paths(fields.get("anchors")) or None
    record["status"] = fields.get("status") or None
    record["evidence"] = fields.get("evidence") or None
    record["exposure"] = fields.get("exposure") or None
    for name in REQUIRED_FINDING_FIELDS:
        if record[name] is None:
            warns.add(f"{rel}: finding {block['id']} has no usable '{name}' (recorded as null)")
    return record


def parse_verdict_text(text: str, rel: str, warns: Collector) -> dict[str, Any]:
    def grab(key: str) -> str | None:
        match = re.search(rf"^\W*{key}\s*:\s*(.*?)\s*$", text, re.I | re.M)
        return match.group(1).strip("*` ") if match else None

    verdict = first_word(grab("VERDICT"), tuple(v.lower() for v in VERDICTS))
    severity = first_word(grab("SEVERITY"), SEVERITIES)
    if verdict is None:
        warns.add(f"{rel}: no usable VERDICT line (recorded as null)")
    stem = os.path.splitext(os.path.basename(rel))[0]
    return {"finding_id": stem, "file": rel, "verdict": verdict.upper() if verdict else None,
            "severity": severity, "evidence": grab("EVIDENCE")}


def clean_cell(value: str) -> str:
    return re.sub(r"[`*]", "", value).strip()


def parse_merge_text(text: str, rel: str, warns: Collector) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    columns = {"raw": 0, "disposition": 1, "merged_as": 2, "reason": 3}
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", cell) or not cell for cell in cells):
            continue
        lowered = [clean_cell(cell).lower() for cell in cells]
        if "raw id" in lowered or "disposition" in lowered:
            columns = {name: lowered.index(label) for name, label in
                       (("raw", "raw id"), ("disposition", "disposition"), ("merged_as", "merged as"),
                        ("reason", "reason")) if label in lowered} or columns
            continue

        def cell(name: str) -> str:
            index = columns.get(name, -1)
            return clean_cell(cells[index]) if 0 <= index < len(cells) else ""

        raw, disposition = cell("raw"), cell("disposition").lower()
        if not raw:
            continue
        disposition_word = first_word(disposition, DISPOSITIONS)
        if disposition_word is None:
            warns.add(f"{rel}:{number}: unknown disposition '{disposition}' for {raw} (kept as written)")
        merged_as = cell("merged_as")
        rows.append({"raw_id": raw, "disposition": disposition_word or (disposition or None),
                     "merged_as": None if merged_as in ("", "—", "-", "–") else merged_as,
                     "reason": cell("reason") or None, "line": number})
    return rows


def parse_profile(text: str | None) -> dict[str, Any]:
    info: dict[str, Any] = {"present": text is not None, "hash": None, "commit": None, "dominant_attributes": [],
                            "stakes_paths": []}
    if text is None:
        return info
    info["hash"] = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    head = re.search(r"^#\s*Profile\b.*?@\s*([0-9a-f]{6,40})", text, re.I | re.M)
    info["commit"] = head.group(1) if head else None
    section = ""
    for line in text.splitlines():
        heading = HEADING_RE.match(line)
        if heading and len(heading.group(1)) <= 2:
            section = heading.group(2).lower()
            continue
        if section.startswith("dominant"):
            item = re.match(r"^\s*\d+[.)]\s+(.*?)(?:\s+[—–-]\s+.*)?$", line)
            if item and item.group(1).strip() and "<" not in item.group(1):
                info["dominant_attributes"].append(item.group(1).strip())
        elif section.startswith("stakes") or re.search(r"stakes path", line, re.I):
            for token in re.findall(r"`([^`]*[/*][^`]*)`|(?<![\w`])((?:[\w.\-]+/)+[\w.\-*]*)", line):
                value = fwd(token[0] or token[1]).strip()
                if value and value not in info["stakes_paths"]:
                    info["stakes_paths"].append(value)
    info["stakes_paths"].sort()
    return info


# ---------------------------------------------------------------- facts, history, hotspots

def read_json_lenient(path: str, rel: str, warns: Collector) -> Any:
    text = read_text(path, warns)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        warns.add(f"{rel}: not valid JSON ({exc.msg} at line {exc.lineno}), skipped")
        return None


def list_files(root: str, sub: str, suffix: str) -> list[str]:
    base = os.path.join(root, sub)
    found = []
    for folder, _, names in os.walk(base):
        for name in names:
            if name.lower().endswith(suffix):
                found.append(fwd(os.path.relpath(os.path.join(folder, name), root)))
    return sorted(found)


def collect_envelopes(run: str, warns: Collector) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    envelopes, script_warnings = [], []
    docs: dict[str, Any] = {}
    for rel in list_files(run, "work/facts", ".json") + list_files(run, "work/measurements", ".json"):
        doc = read_json_lenient(os.path.join(run, rel), rel, warns)
        if doc is None:
            continue
        docs[rel] = doc
        if isinstance(doc, dict) and isinstance(doc.get("warnings"), list) and "tool" in doc:
            envelopes.append({"file": rel, "tool": doc.get("tool"), "warnings": len(doc["warnings"])})
            script_warnings += [{"file": rel, "warning": str(w)} for w in doc["warnings"]]
    return envelopes, script_warnings, docs


def hotspot_paths(doc: Any) -> list[str]:
    root = doc.get("data", doc) if isinstance(doc, dict) else {}
    if not isinstance(root, dict):
        return []
    found: set[str] = set()

    def take(rows: Any, require_flag: bool) -> None:
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict):
                continue
            path = row.get("file") or row.get("path")
            flagged = row.get("hotspot", not require_flag)
            if isinstance(path, str) and flagged:
                found.add(fwd(path))

    files = root.get("files")
    if isinstance(files, dict):
        found.update(fwd(p) for p, row in files.items() if isinstance(row, dict) and row.get("hotspot") is True)
    elif isinstance(files, list):
        take(files, True)
    hotspots = root.get("hotspots")
    if isinstance(hotspots, dict):
        for variant in hotspots.values():
            if isinstance(variant, dict):
                take(variant.get("top"), True)
    for key, value in root.items():
        if key.startswith("hotspots_"):
            take(value, False)
    return sorted(found)


def string_paths(node: Any, out: set[str]) -> None:
    stack = [node]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str) and key.lower() in ENV_PATH_KEYS:
                    out.update(path_tokens(value))
                else:
                    stack.append(value)
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, str):
            out.update(path_tokens(item))


def entry_point_paths(docs: dict[str, Any]) -> tuple[list[str], list[str]]:
    paths: set[str] = set()
    sources: list[str] = []
    for rel, doc in sorted(docs.items()):
        name = os.path.basename(rel).lower()
        before = len(paths)
        if "ingestion" in name or "entry" in name:
            string_paths(doc, paths)
        elif isinstance(doc, dict):
            root = doc.get("data", doc)
            for key in ENTRY_KEYS:
                if isinstance(root, dict) and key in root:
                    string_paths(root[key], paths)
        if len(paths) > before:
            sources.append(rel)
    return sorted(paths), sources


def candidate_arrays(doc: Any) -> list[tuple[str, list[str]]]:
    arrays: list[tuple[str, list[str]]] = []
    stack: list[tuple[str, Any]] = [("", doc.get("data", doc) if isinstance(doc, dict) else doc)]
    while stack:
        key, item = stack.pop()
        if isinstance(item, dict):
            stack.extend((f"{key}.{k}" if key else k, v) for k, v in item.items())
        elif isinstance(item, list):
            paths = [fwd(row.get("path") or row.get("file")) for row in item
                     if isinstance(row, dict) and isinstance(row.get("path") or row.get("file"), str)]
            if paths:
                arrays.append((key, paths))
            else:
                stack.extend((key, v) for v in item if isinstance(v, (dict, list)))
    return sorted(arrays)


def match_paths(token: str, paths: Any) -> bool:
    bare = re.sub(r":\d+(?:-\d+)?$", "", token)
    return any(p == bare or p.endswith("/" + bare) for p in paths)


def stakes_match(token: str, patterns: list[str]) -> bool:
    bare = re.sub(r":\d+(?:-\d+)?$", "", token)
    for pattern in patterns:
        prefix = pattern.rstrip("*").rstrip("/")
        if c.glob_match(bare, [pattern]) or (prefix and (bare == prefix or bare.startswith(prefix + "/"))):
            return True
    return False


# ---------------------------------------------------------------- the run model

def load_run(run: str, warns: Collector) -> dict[str, Any]:
    events, invalid = read_ledger(run, warns)
    dispatches = dispatch_events(events)
    dones: dict[int, list[dict[str, Any]]] = {}
    for event in events:
        if event.get("event") == "done":
            dones.setdefault(event.get("seq"), []).append(event)

    findings_files = [parse_findings_text(read_text(os.path.join(run, rel), warns) or "", rel, warns)
                      for rel in list_files(run, "work/findings", ".md")]
    verdicts = [parse_verdict_text(read_text(os.path.join(run, rel), warns) or "", rel, warns)
                for rel in list_files(run, "work/verdicts", ".md")]
    merge_path = os.path.join(run, "work", "merge.md")
    merge_present = os.path.isfile(merge_path)
    merge = parse_merge_text(read_text(merge_path, warns) or "", "work/merge.md", warns) if merge_present else []
    envelopes, script_warnings, docs = collect_envelopes(run, warns)
    profile_text = read_text(os.path.join(run, "profile.md")) if os.path.isfile(os.path.join(run, "profile.md")) else None
    profile = parse_profile(profile_text)
    history_doc = docs.get("work/facts/history.json")
    return {"events": events, "invalid_lines": invalid, "dispatches": dispatches, "dones": dones,
            "findings_files": findings_files, "verdicts": verdicts, "merge": merge, "merge_present": merge_present,
            "envelopes": envelopes, "script_warnings": script_warnings, "docs": docs, "profile": profile,
            "history_present": history_doc is not None,
            "hotspots": hotspot_paths(history_doc) if history_doc is not None else []}


def agent_rows(model: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for seq, dispatch in sorted(model["dispatches"].items()):
        done = (model["dones"].get(seq) or [None])[-1]
        rows.append({"seq": seq, "wave": dispatch.get("wave"), "role": dispatch.get("role"),
                     "tier": dispatch.get("tier"), "model": dispatch.get("model"), "label": dispatch.get("label"),
                     "status": done.get("status") if done else "no done event",
                     "duration_s": done.get("duration_s") if done else None,
                     "tokens": done.get("tokens") if done else None, "brief": dispatch.get("brief"),
                     "inputs": dispatch.get("inputs") or [],
                     "summary": done.get("summary") if done else None,
                     "outputs": (done.get("outputs") or []) if done else []})
    return rows


def script_rows(model: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"command": e.get("command"), "exit": e.get("exit"), "output": e.get("output"), "note": e.get("note"),
             "ledger_line": e.get("_line")} for e in model["events"] if e.get("event") == "script"]


def find_gaps(run: str, model: dict[str, Any]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []

    def gap(kind: str, file: str, detail: str, fix: str, **extra: Any) -> None:
        gaps.append({"type": kind, "file": file, "detail": detail, "fix": fix, **extra})

    if not os.path.isfile(ledger_file(run)):
        gap("ledger_missing", LEDGER_NAME, "no ledger.jsonl in the run directory",
            "log every dispatch and script run with record.py log; an unlogged run cannot be reconstructed")
    for number in model["invalid_lines"]:
        gap("ledger_line_invalid", LEDGER_NAME, f"line {number} is not a JSON ledger event",
            "never edit the ledger by hand; append a corrected event with record.py log", line=number)
    for seq, dispatch in sorted(model["dispatches"].items()):
        done_events = model["dones"].get(seq) or []
        if not done_events:
            gap("dispatch_without_done", LEDGER_NAME, f"seq {seq} ({dispatch.get('role')}) was dispatched and never closed",
                f"record.py log done --seq {seq} --status ok|failed|empty|partial ...", seq=seq)
            continue
        done = done_events[-1]
        summary = done.get("summary")
        if not summary or not run_path_exists(run, summary):
            gap("done_without_summary", summary or LEDGER_NAME,
                f"seq {seq} has no summary file" + (f" ({summary} is missing)" if summary else ""),
                f"save the agent's reply to work/summaries/{seq}-<role>-<slug>.md and log done with --summary", seq=seq)
    for seq in sorted(s for s in model["dones"] if s not in model["dispatches"]):
        gap("done_without_dispatch", LEDGER_NAME, f"done event for unknown seq {seq}",
            "log the dispatch before the agent runs", seq=seq)

    merge_ids = {row["raw_id"] for row in model["merge"]}
    all_findings = [f for ff in model["findings_files"] for f in ff["findings"]]
    if not model["merge_present"]:
        if all_findings or model["verdicts"]:
            gap("merge_missing", "work/merge.md",
                f"{len(all_findings)} raw findings have no merge file at all",
                "write work/merge.md with one row per raw finding: Raw ID | Disposition | Merged as | Reason")
    else:
        for finding in all_findings:
            if finding["id"] not in merge_ids:
                gap("finding_without_merge_line", finding["file"], f"{finding['id']} has no row in work/merge.md",
                    f"add a row for {finding['id']}: merged, kept, downgraded, refuted, dropped or duplicate",
                    finding_id=finding["id"])
        for verdict in model["verdicts"]:
            if verdict["finding_id"] not in merge_ids:
                gap("verdict_not_in_merge", verdict["file"],
                    f"verdict for {verdict['finding_id']} but that ID is not in work/merge.md",
                    "add the finding to work/merge.md, or fix the verdict file name (verdicts/<finding-id>.md)",
                    finding_id=verdict["finding_id"])
        for row in model["merge"]:
            for token in merge_row_run_paths(row):
                if not (run_path_exists(run, token) or run_path_exists(run, "work/" + token)):
                    gap("merge_line_missing_file", "work/merge.md",
                        f"{row['raw_id']} points at {token}, which does not exist",
                        "fix the path in the merge row or restore the file", finding_id=row["raw_id"], target=token)
    for ff in model["findings_files"]:
        missing = [name for name, present in (("Dismissed", ff["has_dismissed"]),
                                              ("Not assessed", ff["has_not_assessed"])) if not present]
        if missing:
            gap("judge_file_missing_section", ff["file"], "no " + " or ".join(missing) + " section",
                "ask the judge to end the file with Dismissed and Not assessed lists (an empty list says 'none')",
                missing=missing)
    events = model["events"]
    for index, event in enumerate(events):
        if event.get("event") != "script" or event.get("exit") in (0, None):
            continue
        output, command = event.get("output"), str(event.get("command") or "")
        explained = bool(event.get("note")) or any(
            e.get("event") == "note" and ((output and output in str(e.get("text"))) or (command[:40] and command[:40] in str(e.get("text"))))
            for e in events[index + 1:])
        if not explained:
            gap("script_nonzero_unexplained", LEDGER_NAME,
                f"script exited {event.get('exit')} with no note: {command[:80]}",
                "log a note naming the command or its output path and why the failure is acceptable, or rerun it",
                ledger_line=event.get("_line"))
    gaps.sort(key=lambda g: (g["type"], g["file"], g["detail"]))
    return gaps


def merge_row_run_paths(row: dict[str, Any]) -> list[str]:
    tokens = []
    for text in (row.get("merged_as"), row.get("reason")):
        for token in re.findall(r"[\w.\-/]+\.(?:md|json|txt|jsonl)", text or ""):
            if token.startswith(RUN_PATH_PREFIXES) and token not in tokens:
                tokens.append(token)
    return tokens


# ---------------------------------------------------------------- index

def severity_rank(value: str | None) -> int:
    return SEVERITIES.index(value) if value in SEVERITIES else len(SEVERITIES)


def find_hits(model: dict[str, Any], entry_points: list[str]) -> list[dict[str, Any]]:
    stakes = model["profile"]["stakes_paths"]
    hits = []
    for ff in model["findings_files"]:
        for item in ff["dismissed"]:
            on = sorted({name for token in item["anchors"] for name, hit in (
                ("hotspot", match_paths(token, model["hotspots"])),
                ("entry point", match_paths(token, entry_points)),
                ("stakes path", stakes_match(token, stakes))) if hit})
            if on:
                hits.append({"file": item["file"], "line": item["line"], "candidate": item["candidate"],
                             "reason": item["reason"], "matched": on})
    return hits


def unreviewed_candidates(model: dict[str, Any], run: str) -> list[dict[str, Any]]:
    judge_text = "\n".join(read_text(os.path.join(run, ff["file"])) or "" for ff in model["findings_files"])
    rows = []
    for rel, doc in sorted(model["docs"].items()):
        if rel.startswith("work/facts/") and os.path.basename(rel) != "history.json":
            for key, paths in candidate_arrays(doc):
                unseen = sorted({p for p in paths if p not in judge_text})
                if unseen:
                    rows.append({"file": rel, "array": key or "(root)", "candidates": len(paths),
                                 "unreviewed": sum(1 for p in paths if p not in judge_text),
                                 "examples": unseen[:5]})
    return [r for r in rows if r["unreviewed"]]


def run_identity(run: str, model: dict[str, Any]) -> dict[str, Any]:
    name = os.path.basename(run.rstrip("/\\"))
    match = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)$", name)
    manifest: Any = None
    manifest_path = os.path.join(run, "manifest.json")
    if os.path.isfile(manifest_path):
        try:
            manifest = json.loads(read_text(manifest_path) or "")
        except json.JSONDecodeError:
            manifest = None
    audit = manifest.get("audit", {}) if isinstance(manifest, dict) else {}
    profile = model["profile"]
    return {"dir": name, "date": audit.get("date") or (match.group(1) if match else None),
            "mode": audit.get("mode") or (match.group(2) if match else None), "depth": audit.get("depth"),
            "commit": (manifest.get("commit") if isinstance(manifest, dict) else None) or profile["commit"],
            "profile_hash": profile["hash"], "dominant_attributes": profile["dominant_attributes"]}


def build_data(run: str, warns: Collector) -> dict[str, Any]:
    model = load_run(run, warns)
    entry_points, entry_sources = entry_point_paths(model["docs"])
    findings = [f for ff in model["findings_files"] for f in ff["findings"]]
    conflicts = [f for ff in model["findings_files"] for f in ff["authority_conflicts"]]
    dismissed = [d for ff in model["findings_files"] for d in ff["dismissed"]]
    not_assessed = [d for ff in model["findings_files"] for d in ff["not_assessed"]]
    agents = agent_rows(model)
    scripts = script_rows(model)
    gaps = find_gaps(run, model)
    by_id = {f["id"]: f for f in findings}
    merge_by_id = {row["raw_id"]: row for row in model["merge"]}
    verdict_attention = []
    for verdict in model["verdicts"]:
        if verdict["verdict"] in ("REFUTED", "DOWNGRADE"):
            finding = by_id.get(verdict["finding_id"])
            verdict_attention.append({
                **verdict, "finding_file": finding["file"] if finding else None,
                "finding_line": finding["line"] if finding else None,
                "claimed_severity": finding["severity"] if finding else None,
                "merge_disposition": (merge_by_id.get(verdict["finding_id"]) or {}).get("disposition")})
    verdict_attention.sort(key=lambda v: (severity_rank(v["claimed_severity"] or v["severity"]), v["finding_id"]))
    files = [{"path": rel, "size": os.path.getsize(os.path.join(run, rel))} for rel in all_run_files(run)]
    return {
        "run": run_identity(run, model),
        "sources": {"history": model["history_present"], "hotspot_paths": len(model["hotspots"]),
                    "entry_point_paths": len(entry_points), "entry_point_sources": entry_sources,
                    "profile": model["profile"]["present"], "stakes_paths": model["profile"]["stakes_paths"],
                    "merge": model["merge_present"], "ledger": os.path.isfile(ledger_file(run))},
        "counts": {"agents": len(agents), "scripts": len(scripts), "scripts_nonzero": sum(1 for s in scripts if s["exit"]),
                   "findings": len(findings), "authority_conflicts": len(conflicts), "dismissed": len(dismissed),
                   "not_assessed": len(not_assessed), "verdicts": len(model["verdicts"]), "gaps": len(gaps)},
        "agents": agents,
        "scripts": scripts,
        "judge_files": [{"file": ff["file"], "findings": len(ff["findings"]), "authority_conflicts": len(ff["authority_conflicts"]),
                         "dismissed": len(ff["dismissed"]), "not_assessed": len(ff["not_assessed"]),
                         "has_dismissed": ff["has_dismissed"], "has_not_assessed": ff["has_not_assessed"]}
                        for ff in model["findings_files"]],
        "findings": findings,
        "authority_conflicts": conflicts,
        "dismissed": dismissed,
        "not_assessed": not_assessed,
        "verdicts": model["verdicts"],
        "merge": model["merge"],
        "worth_a_human_look": {
            "verifier_refuted_or_downgraded": verdict_attention,
            "dismissed_in_hotspot_entry_or_stakes": find_hits(model, entry_points),
            "low_confidence": [f for f in findings if f["confidence"] == "low"],
            "authority_conflicts": conflicts,
            "unmeasured_performance": [f for f in findings if "unmeasured" in (f["status"] or "").lower()],
            "not_assessed_by_reason": group_by(not_assessed, "reason_group"),
            "unreviewed_candidates": unreviewed_candidates(model, run),
            "script_warnings": model["script_warnings"],
        },
        "envelopes": model["envelopes"],
        "gaps": gaps,
        "files": files,
        "parse_warnings": sorted(warns.items),
    }


def group_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        out.setdefault(row[key], []).append(row)
    return {k: out[k] for k in sorted(out)}


def all_run_files(run: str) -> list[str]:
    found = []
    for folder, _, names in os.walk(run):
        for name in names:
            rel = fwd(os.path.relpath(os.path.join(folder, name), run))
            if rel not in GENERATED and not rel.endswith(".lock"):
                found.append(rel)
    return sorted(found)


# ---------------------------------------------------------------- review.md

def link(label: str, rel: str | None, line: int | None = None) -> str:
    text = md_cell(label)
    if not rel:
        return text
    anchor = f"#L{line}" if line else ""
    return f"[{text}]({quote(rel, safe='/')}{anchor})"


def md_cell(value: Any) -> str:
    return "" if value is None else str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def fmt_duration(seconds: Any) -> str:
    if not isinstance(seconds, (int, float)):
        return "—"
    minutes, rest = divmod(int(seconds), 60)
    return f"{minutes}m{rest:02d}s" if minutes else f"{rest}s"


def render_review(data: dict[str, Any]) -> str:
    out: list[str] = []
    run, counts, worth = data["run"], data["counts"], data["worth_a_human_look"]
    out += [f"# Audit review: {run['dir']}", "",
            "Generated by `record.py index`. Do not edit; rerun it. Paths are relative to this file.", ""]

    by_role: dict[str, int] = {}
    by_model: dict[str, int] = {}
    for agent in data["agents"]:
        by_role[str(agent["role"])] = by_role.get(str(agent["role"]), 0) + 1
        by_model[str(agent["model"])] = by_model.get(str(agent["model"]), 0) + 1
    bad_agents = [a for a in data["agents"] if a["status"] in ("failed", "empty", "partial", "no done event")]
    out += ["## Run", "",
            f"- mode: {run['mode'] or 'unknown'} · depth: {run['depth'] or 'unknown'} · commit: {run['commit'] or 'unknown'}",
            f"- profile: {link('profile.md', 'profile.md') if data['sources']['profile'] else 'missing'}"
            f" · hash: {run['profile_hash'] or 'n/a'}"
            + (f" · dominant: {'; '.join(run['dominant_attributes'])}" if run["dominant_attributes"] else ""),
            "- agents dispatched: " + (f"{counts['agents']} (by role: "
                                      + ", ".join(f"{k} {v}" for k, v in sorted(by_role.items())) + "; by model: "
                                      + ", ".join(f"{k} {v}" for k, v in sorted(by_model.items())) + ")"
                                      if counts["agents"] else "0"),
            "- failed, empty, partial or unclosed agents: "
            + (", ".join(f"seq {a['seq']} {a['role']} ({a['status']})" for a in bad_agents) if bad_agents else "none"),
            f"- script runs: {counts['scripts']} ({counts['scripts_nonzero']} with nonzero exit)",
            f"- findings: {counts['findings']} raw · authority conflicts: {counts['authority_conflicts']} · "
            f"dismissed: {counts['dismissed']} · not assessed: {counts['not_assessed']} · verdicts: {counts['verdicts']}",
            f"- gaps from `check`: {counts['gaps']}"]
    for g in data["gaps"]:
        out.append(f"  - **{g['type']}** {link(g['file'], g['file'] if g['file'] in {f['path'] for f in data['files']} else None)}: "
                   f"{md_cell(g['detail'])} (fix: {md_cell(g['fix'])})")
    src = data["sources"]
    out += [f"- sources for the hotspot and entry-point checks: hotspots {src['hotspot_paths']} paths "
            f"({'work/facts/history.json' if src['history'] else 'no history.json'}), entry points "
            f"{src['entry_point_paths']} paths ({', '.join(src['entry_point_sources']) or 'no ingestion or entry-point fact file'}), "
            f"stakes paths {len(src['stakes_paths'])} ({'profile.md' if src['profile'] else 'no profile.md'})", ""]

    out += ["## Worth a human look", ""]
    out += ["### 1. Refuted or downgraded by a verifier", ""]
    if worth["verifier_refuted_or_downgraded"]:
        for v in worth["verifier_refuted_or_downgraded"]:
            sev = v["claimed_severity"] or "severity unknown"
            finding = link(v["finding_id"], v["finding_file"], v["finding_line"]) if v["finding_file"] else md_cell(v["finding_id"])
            out.append(f"- {finding} (claimed {sev}) → **{v['verdict']}**"
                       + (f" at {v['severity']}" if v["verdict"] == "DOWNGRADE" and v["severity"] else "")
                       + f" · {link('verdict', v['file'])} · evidence: {md_cell(v['evidence'])}"
                       + (f" · merge: {v['merge_disposition']}" if v["merge_disposition"] else ""))
    else:
        out.append("- none")
    out += ["", "### 2. Dismissed candidates in a hotspot, entry point or stakes path", ""]
    if worth["dismissed_in_hotspot_entry_or_stakes"]:
        for d in worth["dismissed_in_hotspot_entry_or_stakes"]:
            out.append(f"- {link(md_cell(d['candidate'])[:120], d['file'], d['line'])} ({', '.join(d['matched'])})"
                       + (f" · reason: {md_cell(d['reason'])[:160]}" if d["reason"] else ""))
    else:
        out.append("- none matched (match is by path suffix against the sources listed under Run; a dismissed item "
                   "with no path in its text cannot match)")
    out += ["", "### 3. Low-confidence findings", ""]
    out += [f"- {link(f['id'], f['file'], f['line'])} ({f['severity'] or 'severity unknown'}): {md_cell(f['title'])}"
            for f in worth["low_confidence"]] or ["- none"]
    out += ["", "### 4. Authority conflicts", ""]
    out += [f"- {link(f['id'], f['file'], f['line'])}: {md_cell(f['title'])}" for f in worth["authority_conflicts"]] or ["- none"]
    out += ["", "### 5. Performance candidates left unmeasured", ""]
    out += [f"- {link(f['id'], f['file'], f['line'])} ({f['severity'] or 'severity unknown'}): {md_cell(f['title'])}"
            for f in worth["unmeasured_performance"]] or ["- none"]
    out += ["", "### 6. Not assessed, by reason", ""]
    if worth["not_assessed_by_reason"]:
        for reason, items in worth["not_assessed_by_reason"].items():
            out.append(f"- **{reason}** ({len(items)})")
            out += [f"  - {link(md_cell(i['text'])[:160], i['file'], i['line'])}" for i in items]
    else:
        out.append("- none")
    out += ["", "### 7. Unreviewed candidates (heuristic)", "",
            "Candidates an extractor listed (arrays of objects with a path) whose path appears in no judge file. "
            "Substring match on the path; an extractor's own array name stands in for the dimension.", ""]
    out += [f"- {link(u['file'], u['file'])} · `{u['array']}`: {u['unreviewed']} of {u['candidates']} unreviewed "
            f"(e.g. {', '.join(u['examples'][:3])})" for u in worth["unreviewed_candidates"]] or ["- none"]
    out += ["", "### 8. Script warnings", ""]
    out += [f"- {link(w['file'], w['file'])}: {md_cell(w['warning'])}" for w in worth["script_warnings"]] or ["- none"]

    out += ["", "## Merge trace", ""]
    merged_ids = {row["raw_id"] for row in data["merge"]}
    finding_by_id = {f["id"]: f for f in data["findings"]}
    if data["merge"] or data["findings"]:
        out += ["| Raw ID | Disposition | Merged as | Reason |", "|---|---|---|---|"]
        for row in data["merge"]:
            finding = finding_by_id.get(row["raw_id"])
            raw = link(row["raw_id"], finding["file"], finding["line"]) if finding else md_cell(row["raw_id"])
            out.append(f"| {raw} | {md_cell(row['disposition'])} | {md_cell(row['merged_as'] or '—')} | {md_cell(row['reason'])} |")
        for finding in data["findings"]:
            if finding["id"] not in merged_ids:
                out.append(f"| {link(finding['id'], finding['file'], finding['line'])} | **no merge line** | — | |")
    else:
        out.append("No raw findings and no merge.md.")

    out += ["", "## Agents", ""]
    if data["agents"]:
        out += ["| seq | wave | role | model | status | duration | brief | summary | outputs |", "|---|---|---|---|---|---|---|---|---|"]
        for a in data["agents"]:
            out.append(f"| {a['seq']} | {md_cell(a['wave'])} | {md_cell(a['role'])} | {md_cell(a['model'])} | {md_cell(a['status'])} | "
                       f"{fmt_duration(a['duration_s'])} | {link(a['brief'], a['brief']) if a['brief'] else '—'} | "
                       f"{link(a['summary'], a['summary']) if a['summary'] else '—'} | "
                       f"{', '.join(link(o, o) for o in a['outputs']) or '—'} |")
    else:
        out.append("No dispatches in the ledger.")

    out += ["", "## Files", "", f"Every file in the run directory except {', '.join(GENERATED)}.", "",
            "| File | Bytes |", "|---|---|"]
    out += [f"| {link(f['path'], f['path'])} | {f['size']} |" for f in data["files"]]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- commands

def write_run_file(run: str, name: str, content: str) -> None:
    with open(os.path.join(run, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def text_index(d: dict[str, Any]) -> str:
    counts = d["counts"]
    lines = [f"{d['run']['dir']}: " + ", ".join(f"{k} {v}" for k, v in counts.items()),
             "wrote " + ", ".join(d["written"])]
    lines += [f"  gap {g['type']}: {g['file']}: {g['detail']}" for g in d["gaps"]]
    return "\n".join(lines)


def cmd_index(ns: argparse.Namespace) -> int:
    run = run_dir(ns)
    warns = Collector()
    data = build_data(run, warns)
    env = c.Envelope(TOOL, c.args_dict(ns))
    for message in data["parse_warnings"]:
        env.warn(message)
    write_run_file(run, REVIEW_NAME, render_review(data))
    full = c.Envelope(TOOL, c.args_dict(ns), warnings=list(env.warnings), data=data)
    write_run_file(run, INDEX_NAME, json.dumps(full.to_json(), indent=2, ensure_ascii=False) + "\n")
    c.log(1, f"wrote {REVIEW_NAME} and {INDEX_NAME} in {run}")
    env.data = {"run": data["run"], "counts": data["counts"], "gaps": data["gaps"],
                "written": [REVIEW_NAME, INDEX_NAME]}
    c.write_output(env, ns, text_index)
    return c.EXIT_OK


def text_check(d: dict[str, Any]) -> str:
    if not d["gaps"]:
        return "no gaps"
    return f"{len(d['gaps'])} gaps\n" + "\n".join(
        f"  {g['type']}: {g['file']}: {g['detail']}\n      fix: {g['fix']}" for g in d["gaps"])


def cmd_check(ns: argparse.Namespace) -> int:
    run = run_dir(ns)
    warns = Collector()
    model = load_run(run, warns)
    gaps = find_gaps(run, model)
    env = c.Envelope(TOOL, c.args_dict(ns))
    for message in sorted(warns.items):
        env.warn(message)
    by_type: dict[str, int] = {}
    for g in gaps:
        by_type[g["type"]] = by_type.get(g["type"], 0) + 1
    env.data = {"clean": not gaps, "gap_count": len(gaps), "by_type": dict(sorted(by_type.items())), "gaps": gaps}
    c.write_output(env, ns, text_check)
    return c.EXIT_CONDITION if ns.fail_on_gaps and gaps else c.EXIT_OK


# ---------------------------------------------------------------- parser

DESCRIPTION = """Keep the audit run record (references/run-record.md): an append-only ledger of agent dispatches,
script runs and decisions; a generated human review index; and a gap check.

Writes ONLY inside the run directory given by --run (ledger.jsonl, review.md, index.json). --out, if
given, must also be inside --run. Never touches the audited repository.

subcommands:
  log dispatch|done|script|note   append one JSON event per line to <run>/ledger.jsonl
  index                           parse the run, write <run>/review.md and <run>/index.json
  check                           list gaps in the record; --fail-on-gaps exits 1 when any

paths: every path you pass is stored relative to --run with forward slashes.
Timestamps appear only in the ledger; index.json `data` has none, so rerunning `index` on an unchanged run
gives identical `data` and an identical review.md."""

GAP_GLOSSARY = """gap types (check.data.gaps[]: type, file, detail, fix):
  ledger_missing / ledger_line_invalid      no ledger, or a line that is not a JSON event
  dispatch_without_done                     an agent was dispatched and never closed
  done_without_summary                      a done event with no summary path or the file is missing
  done_without_dispatch                     a done event whose seq has no dispatch
  merge_missing                             findings exist but there is no work/merge.md
  finding_without_merge_line                a raw F-... finding absent from merge.md
  merge_line_missing_file                   a merge row cites a run file that does not exist
  judge_file_missing_section                a findings file lacks Dismissed or Not assessed
  verdict_not_in_merge                      a verdict file for a finding merge.md does not list
  script_nonzero_unexplained                a script exit != 0 with no note (own --note, or a later note event
                                            quoting its output path or the first 40 chars of its command)"""

INDEX_GLOSSARY = """index.json is the full envelope; `data` fields:
  run                 dir, date, mode, depth, commit (manifest.json, else profile), profile_hash, dominant_attributes
  sources             which inputs existed (history, ledger, merge, profile) and how many hotspot / entry-point /
                      stakes paths were available for matching
  counts              totals; agents[] and scripts[] are the ledger joined (dispatch + done by seq)
  judge_files[]       per findings file: counts and has_dismissed / has_not_assessed
  findings[]          id, title, file, line, severity, confidence, rubric, anchors[], status, evidence, exposure
                      (a missing field is null and a parse warning names the file and finding)
  authority_conflicts[], dismissed[], not_assessed[] (with reason_group), verdicts[], merge[]
  worth_a_human_look  the eight review.md lists; unreviewed_candidates is a HEURISTIC (see below)
  gaps[], files[], parse_warnings[]
caveats: markdown is parsed leniently, so a badly formatted finding can be missed (check parse_warnings).
Dismissed-in-hotspot matching is by path suffix and needs a path in the dismissed text. Unreviewed candidates
are extractor arrays of objects with path/file whose path appears in no judge file; it is a heuristic, not proof."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="record.py", description=DESCRIPTION,
                                     epilog=GAP_GLOSSARY + "\n\n" + c.EXIT_CODES_HELP,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {c.VERSION}")
    top = parser.add_subparsers(dest="command", required=True, metavar="{log,index,check}")

    def sub(subs: Any, name: str, description: str, examples: str, epilog: str = "") -> argparse.ArgumentParser:
        p = subs.add_parser(name, description=description, formatter_class=argparse.RawDescriptionHelpFormatter,
                            epilog=(epilog + "\n\n" if epilog else "") + f"examples:\n{examples.rstrip()}\n\n{c.EXIT_CODES_HELP}",
                            help=description.splitlines()[0])
        c.add_common_flags(p, with_repo=False)
        p.add_argument("--run", required=True, help="the run directory, docs/audits/<date>-<mode>/ (required)")
        return p

    log = top.add_parser("log", help="append a ledger event: dispatch, done, script, note",
                         description="Append one event to <run>/ledger.jsonl (one write per line, append mode).")
    log_subs = log.add_subparsers(dest="event", required=True, metavar="{dispatch,done,script,note}")

    d = sub(log_subs, "dispatch",
            "Record a dispatch BEFORE sending the brief; the envelope returns the assigned seq.\n\n"
            "Event fields: seq (next monotonic number, assigned under a lock), event, wave, role, tier, model, brief,\n"
            "inputs[], started (UTC ISO), label. Missing brief/input paths warn but do not fail.",
            "  python -I scripts/record.py log dispatch --run docs/audits/2026-10-12-inherited --role judge --wave 3 \\\n"
            "      --tier judgment --model opus --brief work/briefs/1-judge-contracts.md --input work/facts/inventories.json")
    d.add_argument("--role", required=True, help="judge, verifier, extractor, ... (free text)")
    d.add_argument("--wave", type=int, required=True, help="dispatch wave number")
    d.add_argument("--tier", required=True, help="model tier name (e.g. judgment, mechanical)")
    d.add_argument("--model", required=True, help="the model actually used")
    d.add_argument("--brief", required=True, help="path of the saved brief, relative to --run")
    d.add_argument("--input", action="append", default=[], help="an input path; repeatable")
    d.add_argument("--label", help="short human label (default: none)")
    d.set_defaults(func=cmd_log_dispatch)

    dn = sub(log_subs, "done",
             "Record that a dispatched agent returned. Fails (exit 4) when --seq has no dispatch.\n\n"
             "Event fields: seq, event, status, outputs[], summary, duration_s (now minus the dispatch time unless\n"
             "--duration-s is given), tokens, finished. A missing output or summary path warns; check flags a\n"
             "missing summary later.",
             "  python -I scripts/record.py log done --run RUN --seq 1 --status ok \\\n"
             "      --output work/findings/contracts-all.md --summary work/summaries/1-judge-contracts.md")
    dn.add_argument("--seq", type=int, required=True, help="the seq returned by log dispatch")
    dn.add_argument("--status", required=True, choices=STATUSES, help="ok | failed | empty | partial")
    dn.add_argument("--output", action="append", default=[], help="an output path; repeatable")
    dn.add_argument("--summary", help="path of the saved agent reply (default: none)")
    dn.add_argument("--duration-s", type=int, help="override the computed duration in seconds")
    dn.add_argument("--tokens", type=int, help="tokens used, if known (default: none)")
    dn.set_defaults(func=cmd_log_done)

    sc = sub(log_subs, "script",
             "Record one script run. Event fields: command, exit, output, note, at.\n"
             "A nonzero --exit with no --note is a gap until a later note names the command or output path.",
             "  python -I scripts/record.py log script --run RUN --command \"python -I scripts/history.py ...\" \\\n"
             "      --exit 0 --output work/facts/history.json")
    sc.add_argument("--command", required=True, help="the exact command line that was run")
    sc.add_argument("--exit", type=int, required=True, help="the process exit code")
    sc.add_argument("--output", help="where its output was saved, relative to --run (default: none)")
    sc.add_argument("--note", help="why a nonzero exit is acceptable, or anything the reader needs (default: none)")
    sc.set_defaults(func=cmd_log_script)

    nt = sub(log_subs, "note", "Record an orchestrator decision worth keeping. Event fields: text, at.",
             "  python -I scripts/record.py log note --run RUN --text \"skipped perf rubric: profile rules out load\"")
    nt.add_argument("--text", required=True, help="the note")
    nt.set_defaults(func=cmd_log_note)

    ix = sub(top, "index",
             "Parse the run and write <run>/review.md (human index) and <run>/index.json (full envelope).\n\n"
             "Reads: ledger.jsonl; work/findings/*.md (### F-... blocks, ### AC-... conflicts, Dismissed and\n"
             "Not assessed lists); work/verdicts/*.md; work/merge.md; JSON envelopes under work/facts and\n"
             "work/measurements (their warnings); profile.md (stakes paths, dominant attributes, best effort);\n"
             "work/facts/history.json (hotspots). Stdout carries a compact summary; the full data is in index.json.\n"
             "review.md sections: Run, Worth a human look, Merge trace, Agents, Files.",
             "  python -I scripts/record.py index --run docs/audits/2026-10-12-inherited\n"
             "  python -I scripts/record.py index --run RUN --format text", INDEX_GLOSSARY)
    ix.set_defaults(func=cmd_index)

    ck = sub(top, "check", "List the gaps that make a run record incomplete.\n\n"
             "Run it before writing the handoff block; an audit with gaps is not finished.",
             "  python -I scripts/record.py check --run docs/audits/2026-10-12-inherited --fail-on-gaps\n"
             "  python -I scripts/record.py check --run RUN --format text", GAP_GLOSSARY)
    ck.add_argument("--fail-on-gaps", action="store_true", help="exit 1 when any gap is found (default: always exit 0)")
    ck.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    ns = build_parser().parse_args(argv)
    c.set_verbosity(ns.verbose)
    return ns.func(ns)


if __name__ == "__main__":
    c.run_main(main)
