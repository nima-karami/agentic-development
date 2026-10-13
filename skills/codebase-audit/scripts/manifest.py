#!/usr/bin/env python3
"""Validate, hash, diff and git-trace the gate manifest. See --help."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402

TOOL = "manifest"

DESCRIPTION = """\
Make the gate manifest comparable and trace how gate configuration changed.

The manifest is built by an agent as JSON (CI jobs, scripts, hooks and instruction-file
commands collapsed into one canonical list). Diffing the manifest, not raw CI files,
means a migration that rewrites every line cannot hide one semantic change, and a
cosmetic rewrite is not reported as drift.

manifest file shape:
  {"gates": [{"id", "command", "workdir", "include", "exclude", "blocking",
              "triggers", "failure_policy", "thresholds", "version"}, ...],
   "local_commands": {"<name>": "<command>" | ["<command>", ...]}}
  required per gate: id (unique string), command (string), blocking (boolean).
  optional: workdir (string), include/exclude (string lists), triggers (string list or
  {event: [path filters]}), failure_policy (object, string or string list),
  thresholds (object name -> number|string), version (string|object|null).

subcommands:
  validate        schema-check a manifest, listing every problem (exit 4 if invalid)
  hash            canonical hash of the gates array plus a hash per gate
  diff            gate-by-gate diff of two manifests with weakening classification
  config-history  git history of gate-config files with candidate relaxations

Caveats: hashes and diffs describe the manifest as written. They are only as good as the
agent's extraction of it, and a gate's real behavior (what the command does) is not
inspected.
"""

EXAMPLES = """\
  python -I scripts/manifest.py validate docs/audits/2026-10-13/work/manifest.json
  python -I scripts/manifest.py hash manifest.json
  python -I scripts/manifest.py diff baseline-manifest.json manifest.json --fail-on-weakening
  python -I scripts/manifest.py config-history --repo . --path ".github/workflows/*.yml" ".eslintrc*" --range v1.0..HEAD"""

GATE_FIELDS = ("id", "command", "workdir", "include", "exclude", "blocking", "triggers",
               "failure_policy", "thresholds", "version")
REQUIRED_FIELDS = ("id", "command", "blocking")

DIFF_EPILOG = """\
classification rules (per field; "weakening" means unvalidated code or a failing result
can now get through):
  gate removed ............ weakening
  gate added .............. strengthening if blocking, else neutral/unknown
  blocking ................ true -> false weakening; false -> true strengthening
  failure_policy .......... gaining continue_on_error, allow_failure, warnings_only, ignore
                            (ignored exit codes) or retries (or more of them, or more ignored
                            codes) is weakening; losing them is strengthening
  include ................. a narrower set (entries removed; empty "everything" -> a list)
                            is weakening; a wider set is strengthening; both is unknown
  exclude ................. entries added is weakening; entries removed is strengthening
  triggers ................ events or filters removed is weakening; added is strengthening
  thresholds .............. a removed threshold is weakening, an added one strengthening.
                            Direction comes from the name: names containing max, warning,
                            complexity, limit, size, budget, duplicat, error, violation
                            are lower-is-stricter (a raised value is weakening); names
                            starting with min or containing cover, mutation, score, lines,
                            branches, functions, statements, threshold, pass, ratio,
                            percent are higher-is-stricter (a lowered value is weakening).
                            Any other name or a non-numeric value is neutral/unknown.
  command, workdir, version, local_commands ... neutral/unknown (a judge must read the change)
Glob subset relations are not evaluated: include/exclude compare entry sets only."""

LOWER_STRICT_RE = re.compile(r"(max|warning|complexity|limit|size|budget|duplicat|error|violation)", re.I)
HIGHER_STRICT_RE = re.compile(r"(cover|mutation|score|lines|branches|functions|statements|threshold|pass|ratio|percent)", re.I)
MIN_RE = re.compile(r"(^min|[_\-.]min)", re.I)

DEFAULT_RELAX_PATTERNS = [
    r'"off"', r'"warn"', r"skip", r"exclude", r"ignore", r"continue-on-error",
    r"allow_failure", r"\|\| true", r"max-warnings", r"--no-verify", r"strict.*false",
]

POLICY_ALIASES = {
    "continue_on_error": "continue_on_error", "continue_on_failure": "continue_on_error",
    "allow_failure": "allow_failure", "allow_failures": "allow_failure",
    "ignore": "ignore", "ignore_exit_code": "ignore", "ignore_exit_codes": "ignore",
    "ignore_errors": "ignore",
    "retries": "retries", "retry": "retries", "max_retries": "retries",
    "warnings_only": "warnings_only", "warn_only": "warnings_only",
}
POLICY_BOOLEAN_KEYS = ("continue_on_error", "allow_failure", "warnings_only")


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


def _problem(gate_index: int | None, gate_id: Any, field: str, message: str, severity: str = "error") -> dict:
    if gate_index is None:
        where = "manifest"
    else:
        where = f"gates[{gate_index}]" + (f' (id "{gate_id}")' if isinstance(gate_id, str) and gate_id else "")
    return {"gate_index": gate_index, "gate": gate_id if isinstance(gate_id, str) else None,
            "field": field, "severity": severity, "message": f'{where}: field "{field}" {message}'}


def _check_string_list(problems: list, idx: int, gid: Any, field: str, value: Any) -> None:
    if not isinstance(value, list):
        problems.append(_problem(idx, gid, field, f"must be an array of strings, got {_type_name(value)}"))
        return
    for i, item in enumerate(value):
        if not isinstance(item, str):
            problems.append(_problem(idx, gid, field, f"entry {i} must be a string, got {_type_name(item)}"))


def _validate_gate(problems: list, idx: int, gate: dict, seen: dict) -> None:
    gid = gate.get("id")
    for field in REQUIRED_FIELDS:
        if field not in gate:
            problems.append(_problem(idx, gid, field, "is required"))
    for field in sorted(set(gate) - set(GATE_FIELDS)):
        problems.append(_problem(idx, gid, field, "is not a known gate field", "warning"))
    if "id" in gate:
        if not isinstance(gid, str) or not gid.strip():
            problems.append(_problem(idx, gid, "id", "must be a non-empty string"))
        elif gid in seen:
            problems.append(_problem(idx, gid, "id", f"duplicates gates[{seen[gid]}]"))
        else:
            seen[gid] = idx
    if "command" in gate and (not isinstance(gate["command"], str) or not gate["command"].strip()):
        problems.append(_problem(idx, gid, "command", "must be a non-empty string"))
    if "workdir" in gate and not isinstance(gate["workdir"], str):
        problems.append(_problem(idx, gid, "workdir", f"must be a string, got {_type_name(gate['workdir'])}"))
    if "blocking" in gate and not isinstance(gate["blocking"], bool):
        problems.append(_problem(idx, gid, "blocking", f"must be a boolean, got {_type_name(gate['blocking'])}"))
    for field in ("include", "exclude"):
        if field in gate:
            _check_string_list(problems, idx, gid, field, gate[field])
    trig = gate.get("triggers")
    if trig is not None:
        if isinstance(trig, dict):
            for event, filt in trig.items():
                if filt is not None and not isinstance(filt, (list, str, bool)):
                    problems.append(_problem(idx, gid, "triggers", f'event "{event}" must map to a path-filter list, string or null, got {_type_name(filt)}'))
        elif isinstance(trig, list):
            _check_string_list(problems, idx, gid, "triggers", trig)
        elif not isinstance(trig, str):
            problems.append(_problem(idx, gid, "triggers", f"must be an array, object or string, got {_type_name(trig)}"))
    policy = gate.get("failure_policy")
    if policy is not None:
        if isinstance(policy, list):
            _check_string_list(problems, idx, gid, "failure_policy", policy)
        elif not isinstance(policy, (dict, str)):
            problems.append(_problem(idx, gid, "failure_policy", f"must be an object, string or array of strings, got {_type_name(policy)}"))
    thresholds = gate.get("thresholds")
    if thresholds is not None:
        if not isinstance(thresholds, dict):
            problems.append(_problem(idx, gid, "thresholds", f"must be an object of name -> number|string, got {_type_name(thresholds)}"))
        else:
            for name, value in thresholds.items():
                if not isinstance(value, (int, float, str)) or isinstance(value, bool):
                    problems.append(_problem(idx, gid, "thresholds", f'"{name}" must be a number or string, got {_type_name(value)}'))
    if "version" in gate and not (gate["version"] is None or isinstance(gate["version"], (str, dict))):
        problems.append(_problem(idx, gid, "version", f"must be a string, object or null, got {_type_name(gate['version'])}"))


def validate_manifest(manifest: Any) -> list[dict]:
    """Return every schema problem (errors and warnings) in a manifest."""
    if not isinstance(manifest, dict):
        return [_problem(None, None, "(root)", f"must be a JSON object, got {_type_name(manifest)}")]
    problems: list[dict] = []
    for key in sorted(set(manifest) - {"gates", "local_commands"}):
        problems.append(_problem(None, None, key, "is not a known top-level field (known: gates, local_commands)", "warning"))
    gates = manifest.get("gates")
    if gates is None:
        problems.append(_problem(None, None, "gates", "is required"))
        gates = []
    elif not isinstance(gates, list):
        problems.append(_problem(None, None, "gates", f"must be an array, got {_type_name(gates)}"))
        gates = []
    seen: dict[str, int] = {}
    for idx, gate in enumerate(gates):
        if isinstance(gate, dict):
            _validate_gate(problems, idx, gate, seen)
        else:
            problems.append(_problem(idx, None, "(gate)", f"gate must be an object, got {_type_name(gate)}"))
    local = manifest.get("local_commands")
    if local is not None:
        if not isinstance(local, dict):
            problems.append(_problem(None, None, "local_commands", f"must be an object, got {_type_name(local)}"))
        else:
            for name, value in local.items():
                ok = isinstance(value, str) or (isinstance(value, list) and all(isinstance(v, str) for v in value))
                if not ok:
                    problems.append(_problem(None, None, "local_commands", f'"{name}" must be a string or array of strings, got {_type_name(value)}'))
    return problems


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "0", "no", "off")
    return bool(value)


def normalize_policy(policy: Any) -> dict:
    """Flatten a failure policy to canonical keys; falsy defaults are dropped."""
    raw: dict[str, Any] = {}
    if isinstance(policy, str):
        raw = {policy: True}
    elif isinstance(policy, list):
        raw = {item: True for item in policy}
    elif isinstance(policy, dict):
        raw = dict(policy)
    out: dict[str, Any] = {}
    for key, value in raw.items():
        norm = re.sub(r"[-\s]+", "_", str(key).strip().lower())
        canon = POLICY_ALIASES.get(norm, norm)
        if canon in POLICY_BOOLEAN_KEYS:
            if _truthy(value):
                out[canon] = True
        elif canon == "ignore":
            if isinstance(value, list):
                if value:
                    out[canon] = sorted({str(v) for v in value})
            elif _truthy(value):
                out[canon] = True
        elif canon == "retries":
            try:
                n = int(value)
            except (TypeError, ValueError):
                n = 1 if _truthy(value) else 0
            if n > 0:
                out[canon] = n
        elif value not in (None, False, 0, "", []):
            out[canon] = value
    return dict(sorted(out.items()))


def _normalize_filters(value: Any) -> Any:
    if value is None or value is False:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return sorted({str(v) for v in value})
    if isinstance(value, dict):
        return {str(k): _normalize_filters(v) for k, v in sorted(value.items())}
    return value


def normalize_gate(gate: dict) -> dict:
    workdir = str(gate.get("workdir") or ".").replace("\\", "/").rstrip("/") or "."
    thresholds = gate.get("thresholds") or {}
    return {
        "id": gate["id"],
        "command": " ".join(str(gate.get("command", "")).split()),
        "workdir": workdir,
        "include": sorted({str(v) for v in gate.get("include") or []}),
        "exclude": sorted({str(v) for v in gate.get("exclude") or []}),
        "blocking": gate.get("blocking"),
        "triggers": _normalize_filters(gate.get("triggers")),
        "failure_policy": normalize_policy(gate.get("failure_policy")),
        "thresholds": dict(sorted(thresholds.items())),
        "version": gate.get("version"),
    }


def normalize_local_commands(manifest: dict) -> dict:
    out = {}
    for name, value in sorted((manifest.get("local_commands") or {}).items()):
        out[name] = sorted(" ".join(v.split()) for v in value) if isinstance(value, list) else " ".join(value.split())
    return out


def normalized_gates(manifest: dict) -> list[dict]:
    return sorted((normalize_gate(g) for g in manifest["gates"]), key=lambda g: g["id"])


def digest(value: Any) -> str:
    return hashlib.sha256(c.canonical_json(value).encode("utf-8")).hexdigest()[:16]


def load_valid_manifest(path: str, env: c.Envelope) -> dict:
    manifest = c.read_json(path)
    problems = validate_manifest(manifest)
    errors = [p for p in problems if p["severity"] == "error"]
    for p in problems:
        if p["severity"] == "warning":
            env.warn(p["message"])
    if errors:
        raise c.InputError(
            f"{path} is not a valid manifest ({len(errors)} problem(s)):\n  " + "\n  ".join(p["message"] for p in errors),
            hint=f"run: manifest.py validate {path}",
        )
    return manifest


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().rstrip("%"))
        except ValueError:
            return None
    return None


def threshold_direction(name: str) -> str:
    if MIN_RE.search(name):
        return "higher-is-stricter"
    if LOWER_STRICT_RE.search(name):
        return "lower-is-stricter"
    if HIGHER_STRICT_RE.search(name):
        return "higher-is-stricter"
    return "unknown"


def classify_threshold(name: str, before: Any, after: Any) -> tuple[str, str]:
    direction = threshold_direction(name)
    b, a = _as_number(before), _as_number(after)
    if direction == "unknown" or b is None or a is None:
        return "neutral/unknown", f"threshold direction unknown or value non-numeric ({direction})"
    if a == b:
        return "neutral/unknown", "same numeric value"
    loosened = a > b if direction == "lower-is-stricter" else a < b
    return ("weakening" if loosened else "strengthening"), f"{direction}: {before} -> {after}"


def _set_change(before: list, after: list) -> tuple[list, list]:
    return sorted(set(after) - set(before)), sorted(set(before) - set(after))


def _classify_set(field: str, before: list, after: list) -> tuple[str, str, dict]:
    added, removed = _set_change(before, after)
    detail = {"added": added, "removed": removed}
    if field == "include":
        if not before and after:
            return "weakening", 'include narrowed from "everything" (empty) to a list', detail
        if before and not after:
            return "strengthening", 'include widened from a list to "everything" (empty)', detail
        if removed and not added:
            return "weakening", "include entries removed (narrowed)", detail
        if added and not removed:
            return "strengthening", "include entries added (widened)", detail
    elif field == "exclude":
        if added and not removed:
            return "weakening", "exclude entries added (widened)", detail
        if removed and not added:
            return "strengthening", "exclude entries removed (narrowed)", detail
    else:
        if removed and not added:
            return "weakening", f"{field} entries removed", detail
        if added and not removed:
            return "strengthening", f"{field} entries added", detail
    return "neutral/unknown", f"{field} entries both added and removed; judge must compare", detail


def _classify_triggers(before: Any, after: Any) -> tuple[str, str, dict]:
    if isinstance(before, dict) or isinstance(after, dict):
        bd = before if isinstance(before, dict) else {k: [] for k in before}
        ad = after if isinstance(after, dict) else {k: [] for k in after}
        added, removed = sorted(set(ad) - set(bd)), sorted(set(bd) - set(ad))
        modified = sorted(k for k in set(bd) & set(ad) if bd[k] != ad[k])
        detail = {"events_added": added, "events_removed": removed, "events_modified": modified}
        if removed and not added and not modified:
            return "weakening", "trigger events removed", detail
        if added and not removed and not modified:
            return "strengthening", "trigger events added", detail
        return "neutral/unknown", "trigger path filters or events changed; judge must compare", detail
    return _classify_set("triggers", before, after)


def _classify_policy(before: dict, after: dict) -> tuple[str, str, dict]:
    weak: list[str] = []
    strong: list[str] = []
    other: list[str] = []
    for key in sorted(set(before) | set(after)):
        b, a = before.get(key), after.get(key)
        if b == a:
            continue
        if key in POLICY_BOOLEAN_KEYS:
            (weak if a and not b else strong).append(key)
        elif key == "retries":
            (weak if (a or 0) > (b or 0) else strong).append(f"retries {b or 0}->{a or 0}")
        elif key == "ignore":
            if not b:
                weak.append("ignore")
            elif not a:
                strong.append("ignore")
            elif isinstance(a, list) and isinstance(b, list):
                added, removed = _set_change(b, a)
                if added and not removed:
                    weak.append("ignore (more exit codes)")
                elif removed and not added:
                    strong.append("ignore (fewer exit codes)")
                else:
                    other.append("ignore")
            else:
                other.append("ignore")
        else:
            other.append(key)
    detail = {"weakened": weak, "strengthened": strong, "other": other}
    if weak and not strong:
        return "weakening", "failure policy gained: " + ", ".join(weak), detail
    if strong and not weak and not other:
        return "strengthening", "failure policy lost: " + ", ".join(strong), detail
    return "neutral/unknown", "failure policy changed in mixed or unrecognized ways", detail


def _classify_thresholds(before: dict, after: dict) -> tuple[str, str, dict]:
    per_key = {}
    for key in sorted(set(before) | set(after)):
        if key not in after:
            per_key[key] = {"classification": "weakening", "rule": "threshold removed", "before": before[key], "after": None}
        elif key not in before:
            per_key[key] = {"classification": "strengthening", "rule": "threshold added", "before": None, "after": after[key]}
        elif before[key] != after[key]:
            cls, rule = classify_threshold(key, before[key], after[key])
            per_key[key] = {"classification": cls, "rule": rule, "before": before[key], "after": after[key]}
    classes = {v["classification"] for v in per_key.values()}
    if "weakening" in classes:
        overall = "weakening"
    elif classes == {"strengthening"}:
        overall = "strengthening"
    else:
        overall = "neutral/unknown"
    return overall, "per-threshold classification in detail", {"thresholds": per_key}


def _classify_field(field: str, before: Any, after: Any) -> tuple[str, str, dict]:
    if field == "blocking":
        if before and not after:
            return "weakening", "blocking true -> false", {}
        if after and not before:
            return "strengthening", "blocking false -> true", {}
        return "neutral/unknown", "blocking value changed", {}
    if field in ("include", "exclude"):
        return _classify_set(field, before, after)
    if field == "triggers":
        return _classify_triggers(before, after)
    if field == "failure_policy":
        return _classify_policy(before, after)
    if field == "thresholds":
        return _classify_thresholds(before, after)
    return "neutral/unknown", f"{field} changed; judge must read the change", {}


def diff_gates(old: dict, new: dict) -> list[dict]:
    """Gate-by-gate diff keyed by id; each change carries a classification."""
    changes: list[dict] = []
    old_g = {g["id"]: g for g in normalized_gates(old)}
    new_g = {g["id"]: g for g in normalized_gates(new)}
    for gid in sorted(set(old_g) | set(new_g)):
        if gid not in new_g:
            changes.append({"gate": gid, "kind": "removed", "field": None, "before": old_g[gid], "after": None,
                            "classification": "weakening", "rule": "gate removed"})
            continue
        if gid not in old_g:
            blocking = new_g[gid]["blocking"]
            changes.append({"gate": gid, "kind": "added", "field": None, "before": None, "after": new_g[gid],
                            "classification": "strengthening" if blocking else "neutral/unknown",
                            "rule": "blocking gate added" if blocking else "non-blocking gate added"})
            continue
        for field in GATE_FIELDS[1:]:
            before, after = old_g[gid][field], new_g[gid][field]
            if before == after:
                continue
            cls, rule, detail = _classify_field(field, before, after)
            change = {"gate": gid, "kind": "changed", "field": field, "before": before, "after": after,
                      "classification": cls, "rule": rule}
            if detail:
                change["detail"] = detail
            changes.append(change)
    return changes


def diff_local_commands(old: dict, new: dict) -> list[dict]:
    a, b = normalize_local_commands(old), normalize_local_commands(new)
    out = []
    for name in sorted(set(a) | set(b)):
        if a.get(name) != b.get(name):
            kind = "removed" if name not in b else "added" if name not in a else "changed"
            out.append({"name": name, "kind": kind, "before": a.get(name), "after": b.get(name),
                        "classification": "neutral/unknown",
                        "rule": "local command differs; compare against the CI gate command (G8)"})
    return out


def cmd_validate(ns: argparse.Namespace, env: c.Envelope):
    manifest = c.read_json(ns.file)
    problems = validate_manifest(manifest)
    errors = [p for p in problems if p["severity"] == "error"]
    for p in problems:
        if p["severity"] == "warning":
            env.warn(p["message"])
    gates = manifest.get("gates") if isinstance(manifest, dict) and isinstance(manifest.get("gates"), list) else []
    c.log(1, f"read {ns.file}: {len(gates)} gate(s), {len(errors)} error(s), {len(problems) - len(errors)} warning(s)")
    env.data = {
        "file": ns.file.replace("\\", "/"),
        "valid": not errors,
        "gate_count": len(gates),
        "error_count": len(errors),
        "warning_count": len(problems) - len(errors),
        "problems": problems,
    }
    for p in errors:
        print(f"error: {p['message']}", file=sys.stderr)

    def text(d):
        lines = [f"{d['file']}: {'valid' if d['valid'] else 'INVALID'} ({d['gate_count']} gates, {d['error_count']} errors, {d['warning_count']} warnings)"]
        lines += [f"  {p['severity']}: {p['message']}" for p in d["problems"]]
        return "\n".join(lines)

    return (c.EXIT_INPUT if errors else c.EXIT_OK), text


def cmd_hash(ns: argparse.Namespace, env: c.Envelope):
    manifest = load_valid_manifest(ns.file, env)
    gates = normalized_gates(manifest)
    c.log(1, f"normalized {len(gates)} gate(s) from {ns.file}")
    env.data = {
        "method": "sha256 of canonical JSON (sorted keys, no whitespace) of the normalized gates array sorted by id, first 16 hex",
        "gates_hash": digest(gates),
        "gate_count": len(gates),
        "gates": {g["id"]: digest(g) for g in gates},
        "local_commands_hash": digest(normalize_local_commands(manifest)),
    }

    def text(d):
        return "\n".join([f"gates_hash {d['gates_hash']} ({d['gate_count']} gates)"] + [f"  {k} {v}" for k, v in d["gates"].items()])

    return c.EXIT_OK, text


def cmd_diff(ns: argparse.Namespace, env: c.Envelope):
    old, new = load_valid_manifest(ns.old, env), load_valid_manifest(ns.new, env)
    changes = diff_gates(old, new)
    local = diff_local_commands(old, new)
    counts = {"weakening": 0, "strengthening": 0, "neutral/unknown": 0}
    for ch in changes:
        counts[ch["classification"]] += 1
    old_hash, new_hash = digest(normalized_gates(old)), digest(normalized_gates(new))
    c.log(1, f"{len(changes)} gate change(s), {len(local)} local command change(s)")
    env.data = {
        "old_gates_hash": old_hash,
        "new_gates_hash": new_hash,
        "identical": old_hash == new_hash,
        "counts": counts,
        "weakening_count": counts["weakening"],
        "changes": changes,
        "local_command_changes": local,
        "note": "classifications are mechanical rules (see 'diff --help'); a judge confirms each weakening",
    }

    def text(d):
        lines = [f"gates {d['old_gates_hash']} -> {d['new_gates_hash']}: {d['counts']}"]
        for ch in d["changes"]:
            field = " " + ch["field"] if ch["field"] else ""
            lines.append(f"  [{ch['classification']}] {ch['gate']} {ch['kind']}{field}: {ch['rule']}")
        for ch in d["local_command_changes"]:
            lines.append(f"  [local] {ch['name']} {ch['kind']}")
        return "\n".join(lines)

    code = c.EXIT_CONDITION if ns.fail_on_weakening and counts["weakening"] else c.EXIT_OK
    return code, text


def _flatten(values: list[list[str]] | None) -> list[str]:
    return [v for group in values or [] for v in group]


def parse_log_stream(text: str, patterns: list, max_line: int = 240) -> list[dict]:
    """Parse `git log -p -U0` output whose commits start with \\x1e and fields use \\x1f."""
    commits = []
    for record in text.split("\x1e"):
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        sha, date, subject = (header.split("\x1f") + ["", "", ""])[:3]
        files: dict[str, dict] = {}
        current: dict | None = None
        in_hunk = False
        new_line = 0
        old_path = None
        for line in body.split("\n"):
            if line.startswith("diff --git "):
                in_hunk, current, old_path = False, None, None
            elif not in_hunk and line.startswith("--- "):
                raw = line[4:].split("\t")[0]
                old_path = raw[2:] if raw.startswith("a/") else None
            elif not in_hunk and line.startswith("+++ "):
                raw = line[4:].split("\t")[0]
                path = raw[2:] if raw.startswith("b/") else old_path
                if path:
                    current = files.setdefault(path, {"file": path, "added": 0, "removed": 0, "candidate_relaxations": []})
            elif line.startswith("@@"):
                m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)
                new_line = int(m.group(1)) if m else 0
                in_hunk = True
            elif in_hunk and current is not None:
                if line.startswith("+"):
                    current["added"] += 1
                    added_text = line[1:]
                    hits = [name for name, rx in patterns if rx.search(added_text)]
                    if hits:
                        shown = added_text.strip()
                        current["candidate_relaxations"].append({
                            "line": new_line,
                            "text": shown if len(shown) <= max_line else shown[:max_line] + "...",
                            "patterns": hits,
                        })
                    new_line += 1
                elif line.startswith("-"):
                    current["removed"] += 1
        commits.append({"sha": sha.strip(), "date": date, "subject": subject,
                        "files": [files[k] for k in sorted(files)]})
    return commits


def cmd_config_history(ns: argparse.Namespace, env: c.Envelope):
    globs = _flatten(ns.path)
    pattern_sources = ([] if ns.no_default_patterns else list(DEFAULT_RELAX_PATTERNS)) + list(ns.relax_pattern or [])
    patterns = []
    for src in pattern_sources:
        try:
            patterns.append((src, re.compile(src, re.I)))
        except re.error as exc:
            env.warn(f"relax pattern {src!r} failed to compile and was skipped: {exc}")
    if c.run_git(ns.repo, ["rev-parse", "--is-shallow-repository"], check=False).strip() == "true":
        env.warn("shallow clone: history is truncated, older gate changes are invisible")
    args = ["-c", "core.quotepath=false", "log", "--no-renames", "-p", "-U0", "--no-color",
            "--format=%x1e%H%x1f%aI%x1f%s", f"--max-count={ns.max_commits + 1}"]
    if ns.range:
        args.append(ns.range)
    args += ["--", *[f":(glob){g}" for g in globs]]
    c.log(1, f"git log over {len(globs)} path glob(s), range {ns.range or 'HEAD'}, {len(patterns)} relax pattern(s)")
    commits = parse_log_stream(c.run_git(ns.repo, args), patterns)
    truncated = len(commits) > ns.max_commits
    if truncated:
        commits = commits[: ns.max_commits]
        env.warn(f"truncated to the newest {ns.max_commits} commits (raise --max-commits)")
    if not commits:
        env.warn("no commits touch these paths in this range: check the globs and --range")
    else:
        touched = sorted({f["file"] for cm in commits for f in cm["files"]})
        for g in globs:
            if not any(c.glob_match(f, [g]) for f in touched):
                env.warn(f"glob {g!r} matched no file changed in the examined history")
    env.data = {
        "paths": sorted(globs),
        "range": ns.range or "HEAD",
        "relax_patterns": pattern_sources,
        "note": "candidate_relaxations are added lines matching a relax pattern: candidates for a judge, not verdicts",
        "commit_count": len(commits),
        "truncated": truncated,
        "candidate_relaxation_count": sum(len(f["candidate_relaxations"]) for cm in commits for f in cm["files"]),
        "commits": commits,
    }

    def text(d):
        lines = [f"{d['commit_count']} commit(s), {d['candidate_relaxation_count']} candidate relaxation(s)" + (" [truncated]" if d["truncated"] else "")]
        for cm in d["commits"]:
            lines.append(f"  {cm['sha'][:9]} {cm['date'][:10]} {cm['subject']}")
            for f in cm["files"]:
                lines.append(f"      {f['file']} +{f['added']} -{f['removed']}")
                for cand in f["candidate_relaxations"]:
                    lines.append(f"        ? L{cand['line']}: {cand['text']}")
        return "\n".join(lines)

    return c.EXIT_OK, text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manifest.py", description=DESCRIPTION,
        epilog=f"examples:\n{EXAMPLES}\n\n{c.EXIT_CODES_HELP}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {c.VERSION}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="{validate,hash,diff,config-history}")

    def add(name: str, help_: str, desc: str, epilog: str, func, with_repo: bool = False):
        sp = sub.add_parser(name, help=help_, description=desc, formatter_class=argparse.RawDescriptionHelpFormatter,
                            epilog=f"{epilog}\n\n{c.EXIT_CODES_HELP}")
        c.add_common_flags(sp, with_repo=with_repo)
        sp.set_defaults(func=func)
        return sp

    sp = add("validate", "schema-check a manifest",
             "Check a manifest against the schema and list every problem (gate and field named), not just the first.\n"
             "data fields: valid, gate_count, error_count, warning_count, problems[{gate, gate_index, field, severity, message}].\n"
             "Unknown fields are warnings (hash and diff ignore them); everything else is an error.",
             "example:\n  python -I scripts/manifest.py validate work/manifest.json\nexit 4 when invalid.", cmd_validate)
    sp.add_argument("file", help="manifest JSON file")

    sp = add("hash", "canonical hash of the gates array",
             "Hash the normalized gates array so two audits can tell in one comparison whether any gate changed.\n"
             "Normalization: gates sorted by id; include/exclude/triggers sorted; whitespace collapsed in commands;\n"
             "workdir slashes unified; failure-policy aliases (continue-on-error, allow_failure, retry ...) mapped to one\n"
             "key set with falsy defaults dropped; thresholds key-sorted. Hash = sha256 of canonical JSON, first 16 hex.\n"
             "data fields: gates_hash, gate_count, gates{id: hash}, local_commands_hash (kept separate), method.\n"
             "Caveat: equal hashes mean equal manifests, not equal real-world gates.",
             "example:\n  python -I scripts/manifest.py hash work/manifest.json", cmd_hash)
    sp.add_argument("file", help="manifest JSON file")

    sp = add("diff", "gate-by-gate diff with weakening classification",
             "Diff two manifests keyed by gate id. Each change lists before/after and a classification of weakening,\n"
             "strengthening or neutral/unknown, with the rule that produced it (G1, G2, G6, G7 detection).\n"
             "data fields: old_gates_hash, new_gates_hash, identical, counts, weakening_count, changes[{gate, kind\n"
             "(added|removed|changed), field, before, after, classification, rule, detail}], local_command_changes[].\n"
             "Classifications are mechanical: a judge confirms each weakening against the real config.",
             "examples:\n  python -I scripts/manifest.py diff baseline/manifest.json work/manifest.json\n"
             "  python -I scripts/manifest.py diff old.json new.json --fail-on-weakening   # exit 1 on any weakening\n\n" + DIFF_EPILOG,
             cmd_diff)
    sp.add_argument("old", help="older (baseline) manifest JSON")
    sp.add_argument("new", help="newer (current) manifest JSON")
    sp.add_argument("--fail-on-weakening", action="store_true", help="exit 1 when any change is classified weakening")

    sp = add("config-history", "git history of gate-config files with candidate relaxations",
             "List the commits that touched gate-config files (CI workflows, lint/type/test config, hooks) with per-file\n"
             "lines added/removed, plus candidate relaxations: added lines matching a relax pattern, with the line text.\n"
             "These are candidates for a judge, not verdicts: 'skip' also matches a legitimate skip step.\n"
             "data fields: commits[{sha, date, subject, files[{file, added, removed, candidate_relaxations[{line, text,\n"
             "patterns}]}]}], commit_count, candidate_relaxation_count, truncated, relax_patterns, paths, range.\n"
             "Read-only; renames show as delete plus add (--no-renames) so a moved config reads as churn.\n"
             "Default relax patterns (case-insensitive regex): " + ", ".join(DEFAULT_RELAX_PATTERNS),
             'examples:\n  python -I scripts/manifest.py config-history --path ".github/workflows/*.yml" "tsconfig*.json"\n'
             '  python -I scripts/manifest.py config-history --path "**/.eslintrc*" --range v2.0..HEAD --relax-pattern "noEmit"',
             cmd_config_history, with_repo=True)
    sp.add_argument("--path", action="append", nargs="+", metavar="GLOB", required=True,
                    help="git pathspec glob(s) of gate-config files; repeatable, accepts several values")
    sp.add_argument("--range", help="git revision range such as a..b (default: all history reachable from HEAD)")
    sp.add_argument("--relax-pattern", action="append", metavar="REGEX",
                    help="extra regex (case-insensitive) marking an added line as a candidate relaxation; repeatable")
    sp.add_argument("--no-default-patterns", action="store_true", help="use only --relax-pattern values")
    sp.add_argument("--max-commits", type=int, default=500,
                    help="cap on commits examined, newest first (default: 500; truncation is warned)")
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
