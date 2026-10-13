#!/usr/bin/env python3
"""Validate, compare and explain codebase-audit baseline.json files."""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import fnmatch
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402

TOOL = "baseline"
DIMENSIONS = ("architecture", "gates", "tests", "verbosity", "security", "performance")
MODES = ("drift", "inherited", "run")
DEPTHS = ("quick", "standard", "deep")


def _f(pattern, up_is_worse, rubric, means, diagnose, ratchet=None, absent_is_zero=False):
    return dict(pattern=pattern, up_is_worse=up_is_worse, rubric=rubric, means=means, diagnose=diagnose,
                ratchet=ratchet, absent_is_zero=absent_is_zero)


FIELDS: list[dict[str, Any]] = [
    _f("architecture.violations_by_rule.*", True, "rubric-architecture.md (declared rules)",
       "Count of violations of one declared architecture rule (key = rule id), production code only.",
       "Rerun the architecture scan for that rule id; list the offending edges and compare with the old list.",
       "a new violation of a declared rule", True),
    _f("architecture.cycle_nodes", True, "rubric-architecture.md (cycles)",
       "Number of modules that sit inside a dependency cycle.",
       "Rise means a new cycle: diff the strongly connected components against the previous graph.",
       "a new cycle between top-level modules"),
    _f("architecture.largest_scc", True, "rubric-architecture.md (cycles)",
       "Size of the largest strongly connected component of the module graph.",
       "Rise means an existing cycle absorbed more modules."),
    _f("gates.debt.suppressions.*.count", True, "rubric-gates.md (debt)",
       "Number of lint/type/test suppressions for one mechanism (key), production code only.",
       "git blame the added suppression lines; check whether they were added with the code they silence.",
       "suppressions rising", True),
    _f("gates.debt.suppressions.*.median_age_days", None, "rubric-gates.md (debt)",
       "Median age in days of the suppressions of one mechanism; null when blame was unavailable.",
       "Falling age means fresh suppressions are being added; rising age alone is not drift."),
    _f("gates.debt.skips", True, "rubric-gates.md (debt)", "Skipped tests (skip/xit/todo markers).",
       "grep the skip markers and blame the new ones.", "skips rising"),
    _f("gates.debt.allowed_failures", True, "rubric-gates.md (debt)",
       "CI jobs or steps allowed to fail without failing the pipeline.",
       "Diff the CI config for allow-failure / continue-on-error entries.",
       "a gate made non-blocking or relaxed"),
    _f("gates.debt.exemptions", True, "rubric-gates.md (debt)", "Paths or rules exempted from a gate.",
       "Diff the gate configs' ignore and exclude lists.", "a gate made non-blocking or relaxed"),
    _f("gates.escape_hatches.total", True, "rubric-gates.md (escape hatches)",
       "Type-system or contract escape hatches (any casts, ts-ignore, unsafe), production code only.",
       "Rise is more unsoundness; locate the new ones with the escape-hatch scan."),
    _f("gates.escape_hatches.at_ingestion", True, "rubric-gates.md (escape hatches)",
       "Escape hatches located at a trust boundary where untyped data enters.",
       "These are the most dangerous hatches; check each against the boundary's validation."),
    _f("tests.eligible_untested", True, "SKILL.md test strength", "Eligible units with no test importing them.",
       "List eligible files with no importing test file."),
    _f("tests.pseudo_tested", True, "SKILL.md test strength",
       "Functions in the sample whose body can be replaced with a default return while tests still pass.",
       "Rerun the mutation probe on tests.sample_files; compare surviving mutants by function.",
       "pseudo-tested count worsening on the fixed sample"),
    _f("tests.kill_rate", False, "SKILL.md test strength",
       "Share (0..1) of default-return mutants killed on the fixed sample; null when not measured.",
       "A drop with the same sample means weaker tests or new weakly tested code in the sample.",
       "kill rate worsening on the fixed sample"),
    _f("verbosity.clone_families", True, "rubric-verbosity.md",
       "Families of duplicated code at the configured token threshold.",
       "Rerun the clone detector with the stored command."),
    _f("verbosity.cross_module_clones", True, "rubric-verbosity.md",
       "Clone families spanning more than one top-level module.", "Same as clone_families, filtered to cross-module."),
    _f("verbosity.dead_files", True, "rubric-verbosity.md", "Files unreachable from declared entry points.",
       "Rerun the reachability scan; check entry-point list changes."),
    _f("verbosity.dead_exports", True, "rubric-verbosity.md", "Exports with no consumer.",
       "Rerun the dead-export scan; check test files count as consumers."),
    _f("security.unguarded_mutating_entry_points", True, "rubric-security.md (authorization)",
       "Mutating entry points with no authentication or authorization guard.",
       "Diff the entry-point inventory; the new route or handler is the finding.",
       "a new unguarded mutating entry point"),
    _f("security.entry_points", None, "rubric-security.md",
       "Total entry points inventoried (denominator for the guard counts).", "Context only."),
    _f("security.permissive_flags", True, "rubric-security.md (configuration)",
       "Permissive security configuration flags (CORS *, disabled verification, sandbox opt-outs).",
       "Grep the flag inventory; the added flag is the finding.", "a new permissive flag"),
    _f("security.secrets_live", True, "rubric-security.md (secrets)", "Secrets confirmed live.",
       "Any non-zero value is urgent regardless of trend."),
    _f("security.reachable_known_cves", True, "rubric-security.md (dependencies)",
       "Known CVEs in dependencies whose vulnerable code is reachable.",
       "Diff the advisory list; check whether a new dependency or call path made it reachable.",
       "a newly reachable known CVE"),
    _f("security.unpinned_ci_actions", True, "rubric-security.md (supply chain)",
       "CI actions referenced by tag or branch instead of a commit SHA.", "grep the workflow files for uses: refs."),
    _f("performance.calls_in_loops", True, "rubric-performance.md P2",
       "Remote or DB calls inside loops over results (N+1 candidates).",
       "Rerun the loop-call scan; confirm with a per-request query count.",
       "a new call-in-loop on a representative flow"),
    _f("performance.unbounded_reads", True, "rubric-performance.md P3", "Reads or list endpoints with no limit or cursor.",
       "Rerun the unbounded-read scan."),
    _f("performance.blocking_calls_on_critical_threads", True, "rubric-performance.md P4",
       "Synchronous blocking calls on a UI thread, event loop or tick loop.",
       "Rerun the blocking-call scan on the critical-thread paths."),
    _f("performance.uncapped_caches", True, "rubric-performance.md P8", "Caches with no size cap or TTL.",
       "Diff the cache inventory."),
    _f("performance.unpaired_lifecycles", True, "rubric-performance.md P9",
       "Listeners, timers or subscriptions added with no matching removal.", "Diff the lifecycle pairing scan."),
    _f("performance.clients_missing_timeouts", True, "rubric-performance.md P10",
       "HTTP or RPC clients constructed without a timeout.", "Rerun the resilience-config scan."),
    _f("performance.flows.*.fan_out", True, "rubric-performance.md P1",
       "Downstream calls issued by one representative flow.", "Trace the flow; compare call sites with the old trace."),
    _f("performance.flows.*.serial_depth", True, "rubric-performance.md P1",
       "Longest chain of awaited calls in one flow (latency floor = depth x round trip).",
       "Trace the flow; a rise means calls were serialized."),
    _f("performance.flows.*.measured.p95_ms", True, "rubric-performance.md P1/P13",
       "Measured p95 latency of a flow in ms; null when unmeasured.",
       "Rerun the identical measurement; compare environments before blaming code.",
       "a measured flow getting slower"),
    _f("performance.flows.*.measured.bundle_kb", True, "rubric-performance.md P5",
       "Measured client bundle size in KB; null when unmeasured.", "Rebuild and diff the bundle composition."),
    _f("audit_quality.findings_sampled", None, "SKILL.md audit quality", "Findings sampled for human confirmation.",
       "Context for confirmed_share."),
    _f("audit_quality.confirmed", None, "SKILL.md audit quality", "Sampled findings a human confirmed.",
       "Context for confirmed_share."),
    _f("audit_quality.confirmed_share", False, "SKILL.md audit quality",
       "Precision of the audit: confirmed / sampled. null (never 0) until a human has confirmed a sample.",
       "A fall means the audit method got noisier; revisit the judge and verifier briefs."),
    _f("audit_quality.refuted_by_verifier", None, "SKILL.md audit quality", "Findings the verifier refuted.",
       "Context only."),
]

DIRECTION_WORD = {True: "up_is_worse", False: "up_is_better", None: "neutral"}


def field_table_text() -> str:
    lines = ["field table (up_is_worse: true = a higher number is worse, false = a lower number is worse,",
             "none = neutral; '*' stands for a dynamic key such as a rule id, mechanism or flow name):"]
    for f in FIELDS:
        ratchet = f"  RATCHET: {f['ratchet']}" if f["ratchet"] else ""
        lines.append(f"  {f['pattern']:<52} up_is_worse={str(f['up_is_worse']).lower():<5}{ratchet}")
    return "\n".join(lines)


def spec_for(path: str) -> dict[str, Any] | None:
    for f in FIELDS:
        if fnmatch.fnmatchcase(path, f["pattern"]):
            return f
    return None


def is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_nonneg_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def parse_date(value: Any) -> dt.date | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


class Checker:
    def __init__(self) -> None:
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []

    def error(self, path: str, message: str) -> None:
        self.errors.append({"path": path, "message": message})

    def warn(self, path: str, message: str) -> None:
        self.warnings.append({"path": path, "message": message})

    def check(self, value: Any, spec: Any, path: str) -> None:
        kind = spec if isinstance(spec, str) else spec[0]
        if kind == "int":
            if not is_nonneg_int(value):
                self.error(path, f"expected a non-negative integer, got {value!r}")
        elif kind == "str":
            if not isinstance(value, str):
                self.error(path, f"expected a string, got {value!r}")
        elif kind == "nullstr":
            if value is not None and not isinstance(value, str):
                self.error(path, f"expected a string or null, got {value!r}")
        elif kind == "date":
            if parse_date(value) is None:
                self.error(path, f"expected an ISO date YYYY-MM-DD, got {value!r}")
        elif kind == "ratio":
            if value is not None and not (is_number(value) and 0 <= value <= 1):
                self.error(path, f"expected null or a number between 0 and 1, got {value!r}")
        elif kind == "num0":
            if value is not None and not (is_number(value) and value >= 0):
                self.error(path, f"expected null or a non-negative number, got {value!r}")
        elif kind == "enum":
            if value not in spec[1]:
                self.error(path, f"expected one of {list(spec[1])}, got {value!r}")
        elif kind == "strs":
            if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                self.error(path, "expected a list of strings")
        elif kind == "strmap":
            if not isinstance(value, dict) or not all(isinstance(x, str) for x in value.values()):
                self.error(path, "expected an object whose values are strings")
        elif kind == "map":
            if not isinstance(value, dict):
                self.error(path, "expected an object")
                return
            for k in sorted(value):
                self.check(value[k], spec[1], f"{path}.{k}")
        elif kind == "list":
            if not isinstance(value, list):
                self.error(path, "expected a list")
                return
            for i, item in enumerate(value):
                self.check(item, spec[1], f"{path}[{i}]")
        elif kind == "obj":
            self.check_object(value, spec[1], path)

    def check_object(self, value: Any, fields: dict[str, Any], path: str) -> None:
        if not isinstance(value, dict):
            self.error(path, "expected an object")
            return
        for key, (sub, required) in fields.items():
            if key not in value:
                if required:
                    self.error(f"{path}.{key}", "required key is missing")
                continue
            self.check(value[key], sub, f"{path}.{key}")
        for key in sorted(value):
            if key in fields or key == "note" or key.endswith("_note"):
                continue
            self.warn(f"{path}.{key}", "unknown key (not in the baseline schema)")


def req(spec: Any) -> tuple[Any, bool]:
    return (spec, True)


def opt(spec: Any) -> tuple[Any, bool]:
    return (spec, False)


SCHEMA_FIELDS: dict[str, Any] = {
    "schema": req(("enum", (1,))),
    "audit": req(("obj", {
        "date": req("date"), "mode": req(("enum", MODES)), "depth": req(("enum", DEPTHS)),
        "commit": req("str"), "range": req("nullstr"), "report": req("str")})),
    "profile": opt(("obj", {
        "path": req("str"), "hash": req("str"), "dominant_attributes": req("strs"), "unknowns": req("strs")})),
    "scope": req(("obj", {
        "fingerprint": req("str"), "include": req("strs"), "exclude": req("strs"),
        "tools": req("strmap"), "scan_commands": req("strmap")})),
    "architecture": req(("obj", {
        "violations_by_rule": req(("map", "int")), "cycle_nodes": req("int"), "largest_scc": req("int"),
        "hotspots_top20": req(("list", ("obj", {"path": req("str"), "churn": req("int"), "complexity": req("int")}))),
        "cochange_top": req(("list", ("obj", {"a": req("str"), "b": req("str"), "ratio": req("ratio")}))),
        "parallel_abstractions": req(("list", ("obj", {
            "concern": req("str"), "members": req("strs"), "status": req(("enum", ("open", "accepted")))})))})),
    "gates": req(("obj", {
        "manifest_hash": req("str"), "required_checks": req("strs"),
        "debt": req(("obj", {
            "suppressions": req(("map", ("obj", {"count": req("int"), "median_age_days": req("num0")}))),
            "skips": req("int"), "allowed_failures": req("int"), "exemptions": req("int")})),
        "escape_hatches": req(("obj", {"total": req("int"), "at_ingestion": req("int")}))})),
    "tests": req(("obj", {
        "sample_files": req("strs"), "eligible_untested": req("int"), "pseudo_tested": req("int"),
        "kill_rate": req("ratio")})),
    "verbosity": req(("obj", {k: req("int") for k in
                              ("clone_families", "cross_module_clones", "dead_files", "dead_exports")})),
    "security": opt(("obj", {
        "scanner_manifest_hash": req("str"), **{k: req("int") for k in (
            "unguarded_mutating_entry_points", "entry_points", "permissive_flags", "secrets_live",
            "reachable_known_cves", "unpinned_ci_actions")}})),
    "performance": opt(("obj", {
        "flows": req(("list", ("obj", {
            "name": req("str"), "fan_out": req("int"), "serial_depth": req("int"),
            "measured": req(("obj", {"p95_ms": req("num0"), "bundle_kb": req("num0")}))}))),
        **{k: req("int") for k in ("calls_in_loops", "unbounded_reads", "blocking_calls_on_critical_threads",
                                   "uncapped_caches", "unpaired_lifecycles", "clients_missing_timeouts")}})),
    "audit_quality": req(("obj", {
        "findings_sampled": req("int"), "confirmed": req("int"), "confirmed_share": req("ratio"),
        "refuted_by_verifier": req("int")})),
    "accepted_exceptions": req(("list", ("obj", {
        "what": req("str"), "anchor": req("str"), "owner": req("str"), "reason": req("str"),
        "expires": req("date")}))),
}


def validate_document(doc: Any) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return (errors, warnings), each a list of {path, message}."""
    ck = Checker()
    if not isinstance(doc, dict):
        ck.error("$", "baseline must be a JSON object")
        return ck.errors, ck.warnings
    ck.check_object(doc, SCHEMA_FIELDS, "$")
    if "profile" not in doc:
        ck.warn("$.profile", "missing: drift rule 0 (profile hash) cannot be applied to this baseline")
    for key in ("security", "performance"):
        if key not in doc:
            ck.warn(f"$.{key}", "dimension absent: allowed only when the profile ran without it")
    check_audit_quality(doc.get("audit_quality"), ck)
    check_run_range(doc.get("audit"), ck)
    return ck.errors, ck.warnings


def check_audit_quality(aq: Any, ck: Checker) -> None:
    if not isinstance(aq, dict):
        return
    sampled, confirmed, share = aq.get("findings_sampled"), aq.get("confirmed"), aq.get("confirmed_share")
    if is_nonneg_int(sampled) and sampled == 0 and share is not None:
        ck.error("$.audit_quality.confirmed_share", "must be null when findings_sampled is 0")
    if is_nonneg_int(sampled) and is_nonneg_int(confirmed) and confirmed > sampled:
        ck.error("$.audit_quality.confirmed", f"confirmed ({confirmed}) exceeds findings_sampled ({sampled})")


def check_run_range(audit: Any, ck: Checker) -> None:
    if isinstance(audit, dict) and audit.get("mode") == "run" and audit.get("range") is None:
        ck.error("$.audit.range", "must be set when mode is 'run'")


def flatten_numbers(node: Any, prefix: str, out: dict[str, Any]) -> None:
    if isinstance(node, dict):
        for k in sorted(node):
            if k == "note" or k.endswith("_note"):
                continue
            flatten_numbers(node[k], f"{prefix}.{k}" if prefix else k, out)
    elif isinstance(node, list):
        if prefix == "performance.flows":
            for flow in node:
                if isinstance(flow, dict) and isinstance(flow.get("name"), str):
                    rest = {k: v for k, v in flow.items() if k != "name"}
                    flatten_numbers(rest, f"{prefix}.{flow['name']}", out)
    elif is_number(node) or node is None:
        out[prefix] = node


def numeric_fields(doc: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for dim in (*DIMENSIONS, "audit_quality"):
        if isinstance(doc.get(dim), dict):
            flatten_numbers(doc[dim], dim, out)
    return {k: v for k, v in out.items() if spec_for(k) is not None}


def relative_change(old: float, new: float) -> float:
    if old == new:
        return 0.0
    if old == 0:
        return float("inf")
    return abs(new - old) / abs(old)


def field_entry(path: str, old: Any, new: Any, spec: dict[str, Any], direction: str) -> dict[str, Any]:
    return {"field": path, "old": old, "new": new, "delta": None, "relative_change": None,
            "up_is_worse": spec["up_is_worse"], "ratchet": bool(spec["ratchet"]),
            "direction": direction, "within_noise": False}


def diff_field(path: str, old: Any, new: Any, spec: dict[str, Any], noise: float) -> dict[str, Any]:
    if old is None or new is None:
        return field_entry(path, old, new, spec, "same" if old == new else "unmeasured")
    entry = field_entry(path, old, new, spec, "same")
    delta = new - old
    rel = relative_change(old, new)
    entry["delta"] = round(delta, 6)
    entry["relative_change"] = None if rel == float("inf") else round(rel, 6)
    if delta == 0:
        return entry
    if rel < noise:
        entry["within_noise"] = True
        return entry
    if spec["up_is_worse"] is None:
        entry["direction"] = "neutral"
    else:
        entry["direction"] = "worse" if (delta > 0) == spec["up_is_worse"] else "better"
    return entry


def dimension_present(old: dict[str, Any], new: dict[str, Any], path: str) -> bool:
    dim = path.split(".", 1)[0] + "."
    return any(k.startswith(dim) for k in old) and any(k.startswith(dim) for k in new)


def diff_numeric(old: dict[str, Any], new: dict[str, Any], noise: float) -> list[dict[str, Any]]:
    out = []
    for path in sorted(set(old) | set(new)):
        spec = spec_for(path)
        if path in old and path in new:
            out.append(diff_field(path, old[path], new[path], spec, noise))
        elif spec["absent_is_zero"] and dimension_present(old, new, path):
            out.append(diff_field(path, old.get(path, 0), new.get(path, 0), spec, noise))
        else:
            entry = field_entry(path, old.get(path), new.get(path), spec, "new" if path in new else "removed")
            out.append(entry)
    return out


def dimension_trend(dim: str, old_doc: dict[str, Any], new_doc: dict[str, Any],
                    fields: list[dict[str, Any]], breaches: list[dict[str, Any]]) -> str:
    if dim not in new_doc:
        return "off"
    if dim not in old_doc:
        return "new"
    mine = [f for f in fields if f["field"].split(".", 1)[0] == dim]
    if any(b["dimension"] == dim for b in breaches) or any(f["direction"] == "worse" for f in mine):
        return "worse"
    if any(f["direction"] == "better" for f in mine):
        return "better"
    return "same"


def ratchet_breaches(fields: list[dict[str, Any]], trusted: bool) -> list[dict[str, Any]]:
    return [{"dimension": f["field"].split(".", 1)[0], "field": f["field"],
             "rule": spec_for(f["field"])["ratchet"], "old": f["old"], "new": f["new"],
             "delta": f["delta"], "trusted": trusted}
            for f in fields if f["ratchet"] and f["direction"] == "worse"]


def concern_map(doc: dict[str, Any]) -> dict[Any, dict[str, Any]]:
    items = (doc.get("architecture") or {}).get("parallel_abstractions") or []
    return {p.get("concern"): p for p in items if isinstance(p, dict)}


def hotspot_paths(doc: dict[str, Any]) -> set[Any]:
    items = (doc.get("architecture") or {}).get("hotspots_top20") or []
    return {h.get("path") for h in items if isinstance(h, dict)}


def structural_findings(old: dict[str, Any], new: dict[str, Any], trusted: bool) -> dict[str, Any]:
    breaches: list[dict[str, Any]] = []

    def breach(dim: str, field: str, rule: str, old_v: Any, new_v: Any) -> None:
        breaches.append({"dimension": dim, "field": field, "rule": rule, "old": old_v, "new": new_v,
                         "delta": None, "trusted": trusted})

    old_sample = set((old.get("tests") or {}).get("sample_files") or [])
    new_sample = set((new.get("tests") or {}).get("sample_files") or [])
    sample = {"added": sorted(new_sample - old_sample), "removed": sorted(old_sample - new_sample)}
    sample["violation"] = bool(sample["removed"])
    if sample["removed"]:
        breach("tests", "tests.sample_files", "the test sample is extended, never replaced (drift rule 3)",
               sorted(old_sample), sorted(new_sample))

    old_gates, new_gates = old.get("gates") or {}, new.get("gates") or {}
    old_checks, new_checks = set(old_gates.get("required_checks") or []), set(new_gates.get("required_checks") or [])
    gates = {"manifest_hash_changed": old_gates.get("manifest_hash") != new_gates.get("manifest_hash"),
             "required_checks_removed": sorted(old_checks - new_checks),
             "required_checks_added": sorted(new_checks - old_checks)}
    if gates["required_checks_removed"]:
        breach("gates", "gates.required_checks", "a gate removed, made non-blocking, or relaxed",
               sorted(old_checks), sorted(new_checks))

    old_pa, new_pa = concern_map(old), concern_map(new)
    pa: dict[str, list[Any]] = {"added": sorted(set(new_pa) - set(old_pa), key=str),
                                "removed": sorted(set(old_pa) - set(new_pa), key=str), "grown": []}
    for concern in pa["added"]:
        breach("architecture", f"architecture.parallel_abstractions[{concern}]", "a new parallel abstraction",
               None, len(new_pa[concern].get("members") or []))
    for concern in sorted(set(old_pa) & set(new_pa), key=str):
        before, after = len(old_pa[concern].get("members") or []), len(new_pa[concern].get("members") or [])
        if after > before:
            pa["grown"].append(concern)
            breach("architecture", f"architecture.parallel_abstractions[{concern}]",
                   "a new parallel abstraction (existing concern gained members)", before, after)

    old_tools, new_tools = (old.get("scope") or {}).get("tools") or {}, (new.get("scope") or {}).get("tools") or {}
    tools = [{"tool": t, "old": old_tools.get(t), "new": new_tools.get(t)}
             for t in sorted(set(old_tools) | set(new_tools)) if old_tools.get(t) != new_tools.get(t)]
    hotspots = {"entered": sorted(hotspot_paths(new) - hotspot_paths(old), key=str),
                "left": sorted(hotspot_paths(old) - hotspot_paths(new), key=str)}
    return {"breaches": breaches, "sample_files": sample, "gates": gates, "parallel_abstractions": pa,
            "tool_changes": tools, "hotspots": hotspots}


def expired_exceptions(doc: dict[str, Any], as_of: dt.date) -> list[dict[str, Any]]:
    out = []
    for entry in doc.get("accepted_exceptions") or []:
        expires = parse_date(entry.get("expires")) if isinstance(entry, dict) else None
        if expires is not None and expires < as_of:
            out.append({**entry, "days_overdue": (as_of - expires).days})
    return sorted(out, key=lambda e: (e.get("expires", ""), e.get("what", "")))


def exception_key(entry: dict[str, Any]) -> tuple[str, str]:
    return (str(entry.get("what")), str(entry.get("anchor")))


def is_run_baseline(doc: dict[str, Any]) -> bool:
    audit = doc.get("audit") or {}
    return audit.get("mode") == "run" or audit.get("range") is not None


def hashes_match(old_v: Any, new_v: Any, label: str, env: c.Envelope) -> bool | None:
    if old_v is None or new_v is None:
        env.warn(f"{label} missing in {'old' if old_v is None else 'new'} baseline: comparability unknown")
        return None
    return old_v == new_v


def audit_brief(doc: dict[str, Any]) -> dict[str, Any]:
    audit = doc.get("audit") or {}
    return {k: audit.get(k) for k in ("date", "mode", "depth", "commit", "range")}


def compare_documents(old: dict[str, Any], new: dict[str, Any], noise: float, as_of: dt.date,
                      force: bool, env: c.Envelope) -> dict[str, Any]:
    comparable_mode = is_run_baseline(old) == is_run_baseline(new)
    if not comparable_mode and not force:
        raise c.InputError("one baseline is a run-mode (range) baseline and the other is whole-repo",
                           hint="run-mode numbers cover a commit range only; pass --force to diff anyway")
    if not comparable_mode:
        env.warn("run-mode baseline compared with a whole-repo baseline (--force): numbers cover different scopes")
    profile_ok = hashes_match((old.get("profile") or {}).get("hash"), (new.get("profile") or {}).get("hash"),
                              "profile.hash", env)
    scope_ok = hashes_match((old.get("scope") or {}).get("fingerprint"), (new.get("scope") or {}).get("fingerprint"),
                            "scope.fingerprint", env)
    if profile_ok is False:
        env.warn("profile hash differs: requirements changed; re-calibrate severity and declare a new comparison point")
    if scope_ok is False:
        env.warn("scope fingerprint differs: numbers are not comparable; diffs are shown but flagged untrusted")
    trusted = bool(profile_ok is not False and scope_ok is not False and comparable_mode)

    fields = diff_numeric(numeric_fields(old), numeric_fields(new), noise)
    structural = structural_findings(old, new, trusted)
    breaches = ratchet_breaches(fields, trusted) + structural.pop("breaches")
    breaches.sort(key=lambda b: (b["dimension"], b["field"], b["rule"]))
    trend = {d: dimension_trend(d, old, new, fields, breaches) for d in DIMENSIONS}

    kept = {exception_key(e) for e in new.get("accepted_exceptions") or [] if isinstance(e, dict)}
    dropped = [e for e in old.get("accepted_exceptions") or [] if isinstance(e, dict) and exception_key(e) not in kept]
    summary = {"fields_compared": len(fields),
               "worse": sum(f["direction"] == "worse" for f in fields),
               "better": sum(f["direction"] == "better" for f in fields),
               "breaches": len(breaches), "trusted_breaches": sum(b["trusted"] for b in breaches)}
    return {
        "comparable_profile": profile_ok, "comparable_scope": scope_ok, "comparable_mode": comparable_mode,
        "trusted": trusted, "old": audit_brief(old), "new": audit_brief(new), "noise": noise,
        "as_of": as_of.isoformat(), "trend": trend, "summary": summary, "breaches": breaches, "fields": fields,
        **structural,
        "expired_exceptions": expired_exceptions(new, as_of), "dropped_exceptions": dropped,
        "notes": ["trend: worse = a ratchet breached or any directional field moved the wrong way beyond noise; "
                  "better = some directional field improved and none worsened; off = dimension absent in NEW; "
                  "new = dimension absent in OLD",
                  "rule 2: if tool_changes is non-empty, rerun the old scripts before reading a count change as drift"],
    }


def load_baseline(path: str) -> dict[str, Any]:
    doc = c.read_json(path)
    errors, _ = validate_document(doc)
    if errors:
        first = errors[0]
        raise c.InputError(
            f"{path} is not a valid baseline ({len(errors)} problems; first: {first['path']}: {first['message']})",
            hint=f"run: baseline.py validate {path}")
    return doc


def explain_field(name: str) -> dict[str, Any]:
    spec = spec_for(name)
    if spec is None:
        close = difflib.get_close_matches(name, [f["pattern"] for f in FIELDS], n=4, cutoff=0.4)
        raise c.UsageError(f"unknown field: {name}",
                           hint="try: " + (", ".join(close) if close else "baseline.py explain --list"))
    return {"field": name, "pattern": spec["pattern"], "means": spec["means"],
            "up_is_worse": spec["up_is_worse"], "direction": DIRECTION_WORD[spec["up_is_worse"]],
            "ratchet": spec["ratchet"],
            "breach_when": "any move in the worse direction beyond --noise" if spec["ratchet"] else None,
            "rubric": spec["rubric"], "how_to_diagnose": spec["diagnose"],
            "counting": "production code only (tests excluded) unless the field name says otherwise"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="baseline.py",
        description=("Validate, compare and explain baseline.json files (schema and drift rules: "
                     "references/baseline.md). Takes no --repo: it reads baseline files only."),
        epilog=c.EXIT_CODES_HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {c.VERSION}")
    subs = parser.add_subparsers(dest="command", required=True, metavar="{validate,compare,explain}")

    def sub(name: str, description: str, examples: str) -> argparse.ArgumentParser:
        p = subs.add_parser(name, description=description, formatter_class=argparse.RawDescriptionHelpFormatter,
                            epilog=f"examples:\n{examples.rstrip()}\n\n{c.EXIT_CODES_HELP}",
                            help=description.splitlines()[0])
        c.add_common_flags(p, with_repo=False)
        return p

    v = sub("validate",
            "Check a baseline file against the schema.\n\n"
            "Why: a malformed baseline silently breaks the next drift comparison. Lists every problem with a\n"
            "JSON path. Required: schema, audit, scope, architecture, gates, tests, verbosity, audit_quality,\n"
            "accepted_exceptions. Optional: profile (warning if absent), security, performance (allowed when the\n"
            "profile ran without them). Unknown keys are warnings; keys named note or *_note are ignored.\n\n"
            "data fields: file, valid (bool), errors [{path, message}], warnings [{path, message}].\n"
            "Caveat: validates shape, not truth; it cannot know whether the numbers are right.",
            "  python -I scripts/baseline.py validate docs/audits/baseline.json\n"
            "  python -I scripts/baseline.py validate baseline.json --format text")
    v.add_argument("file", help="path to baseline.json")
    v.set_defaults(func=cmd_validate)

    cp = sub("compare",
             "Diff two baselines by the drift rules in references/baseline.md.\n\n"
             "Rules applied: 0 profile hash, 1 scope fingerprint, 3 sample files extended-never-replaced, 4 trend per\n"
             "dimension, 5 ratchet breaches, 6 expired exceptions (as of --as-of, default NEW's audit date),\n"
             "7 run-mode vs whole-repo baselines refuse unless --force. Rule 2 shows up as tool_changes.\n\n"
             "data fields: comparable_profile/comparable_scope/comparable_mode (true|false|null=unknown), trusted,\n"
             "trend {dimension: better|same|worse|new|off}, summary, breaches [{dimension, field, rule, old, new,\n"
             "delta, trusted}], fields [{field, old, new, delta, relative_change, up_is_worse, ratchet, direction,\n"
             "within_noise}], sample_files {added, removed, violation}, gates, parallel_abstractions, tool_changes,\n"
             "hotspots, expired_exceptions, dropped_exceptions.\n"
             "Caveats: breaches on non-comparable baselines are flagged trusted=false but still counted by\n"
             "--fail-on-breach; relative_change is null when OLD was 0 (infinite); a field absent in one baseline is\n"
             "'new'/'removed' except dynamic counts (rule id, mechanism) which count as 0.\n\n" + field_table_text(),
             "  python -I scripts/baseline.py compare old.json new.json\n"
             "  python -I scripts/baseline.py compare old.json new.json --noise 0.05 --fail-on-breach\n"
             "  python -I scripts/baseline.py compare old.json new.json --as-of 2026-12-01 --format text")
    cp.add_argument("old", help="the earlier baseline.json")
    cp.add_argument("new", help="the later baseline.json")
    cp.add_argument("--noise", type=float, default=0.0,
                    help="relative change (0.05 = 5%%) below which a move counts as same (default: 0)")
    cp.add_argument("--fail-on-breach", action="store_true", help="exit 1 when any ratchet is breached")
    cp.add_argument("--as-of", help="date (YYYY-MM-DD) for exception expiry (default: NEW's audit date)")
    cp.add_argument("--force", action="store_true", help="compare a run-mode baseline with a whole-repo one anyway")
    cp.set_defaults(func=cmd_compare)

    e = sub("explain",
            "Explain one baseline field: meaning, direction, ratchet rule, related rubric row, how to diagnose.\n\n"
            "FIELD is a dotted path such as gates.debt.skips or performance.flows.checkout.fan_out. Use --list for\n"
            "every known field pattern.\n\n"
            "data fields: field, pattern, means, up_is_worse, direction, ratchet, breach_when, rubric, how_to_diagnose.",
            "  python -I scripts/baseline.py explain tests.kill_rate\n"
            "  python -I scripts/baseline.py explain architecture.violations_by_rule.R1\n"
            "  python -I scripts/baseline.py explain --list")
    e.add_argument("field", nargs="?", help="dotted field path")
    e.add_argument("--list", action="store_true", help="list every field pattern with its direction")
    e.set_defaults(func=cmd_explain)
    return parser


def text_validate(d: dict[str, Any]) -> str:
    lines = [f"{d['file']}: {'valid' if d['valid'] else 'INVALID'} "
             f"({len(d['errors'])} errors, {len(d['warnings'])} warnings)"]
    lines += [f"  error   {p['path']}: {p['message']}" for p in d["errors"]]
    lines += [f"  warning {p['path']}: {p['message']}" for p in d["warnings"]]
    return "\n".join(lines)


def cmd_validate(ns: argparse.Namespace) -> int:
    doc = c.read_json(ns.file)
    env = c.Envelope(TOOL, c.args_dict(ns))
    errors, warnings = validate_document(doc)
    c.log(1, f"{ns.file}: {len(errors)} errors, {len(warnings)} warnings")
    for w in warnings:
        env.warn(f"{w['path']}: {w['message']}")
    env.data = {"file": ns.file, "valid": not errors, "errors": errors, "warnings": warnings}
    c.write_output(env, ns, text_validate)
    return c.EXIT_OK if not errors else c.EXIT_INPUT


def text_compare(d: dict[str, Any]) -> str:
    s = d["summary"]
    lines = [f"{d['old']['date']} -> {d['new']['date']}  trusted={d['trusted']}  "
             f"profile={d['comparable_profile']} scope={d['comparable_scope']} mode={d['comparable_mode']}",
             "trend: " + "  ".join(f"{k}={v}" for k, v in d["trend"].items()),
             f"fields compared {s['fields_compared']}: {s['worse']} worse, {s['better']} better, "
             f"{s['breaches']} ratchet breaches"]
    lines += [f"  BREACH {b['field']}: {b['rule']} (old {b['old']} -> new {b['new']})"
              + ("" if b["trusted"] else " [untrusted]") for b in d["breaches"]]
    lines += [f"  {f['direction']:<8} {f['field']}: {f['old']} -> {f['new']}"
              for f in d["fields"] if f["direction"] in ("worse", "better", "new", "removed")]
    if d["sample_files"]["removed"]:
        lines.append(f"  sample files removed: {d['sample_files']['removed']}")
    if d["gates"]["manifest_hash_changed"]:
        lines.append("  gate manifest hash changed: review the manifest diff")
    lines += [f"  EXPIRED exception: {e.get('what')} ({e.get('expires')}, owner {e.get('owner')})"
              for e in d["expired_exceptions"]]
    lines += [f"  tool changed: {t['tool']} {t['old']} -> {t['new']}" for t in d["tool_changes"]]
    return "\n".join(lines)


def parse_as_of(value: str) -> dt.date:
    parsed = parse_date(value)
    if parsed is None:
        raise c.UsageError(f"--as-of is not an ISO date: {value}", hint="use YYYY-MM-DD")
    return parsed


def cmd_compare(ns: argparse.Namespace) -> int:
    if ns.noise < 0:
        raise c.UsageError("--noise must be >= 0", hint="use a fraction such as 0.05 for 5%")
    as_of_override = parse_as_of(ns.as_of) if ns.as_of else None
    old, new = load_baseline(ns.old), load_baseline(ns.new)
    as_of = as_of_override or parse_date(new["audit"]["date"])
    env = c.Envelope(TOOL, c.args_dict(ns))
    env.data = compare_documents(old, new, ns.noise, as_of, ns.force, env)
    c.log(1, f"{env.data['summary']['fields_compared']} fields, {env.data['summary']['breaches']} breaches")
    c.write_output(env, ns, text_compare)
    return c.EXIT_CONDITION if ns.fail_on_breach and env.data["breaches"] else c.EXIT_OK


def text_explain(d: dict[str, Any]) -> str:
    if "fields" in d:
        return "\n".join(f"{f['pattern']:<52} {f['direction']}" for f in d["fields"])
    return (f"{d['field']}\n  means:     {d['means']}\n  direction: {d['direction']}\n"
            f"  ratchet:   {d['ratchet'] or 'not a ratchet'}\n  rubric:    {d['rubric']}\n"
            f"  diagnose:  {d['how_to_diagnose']}\n  counting:  {d['counting']}")


def cmd_explain(ns: argparse.Namespace) -> int:
    env = c.Envelope(TOOL, c.args_dict(ns))
    if ns.list:
        env.data = {"fields": [{"pattern": f["pattern"], "direction": DIRECTION_WORD[f["up_is_worse"]],
                                "ratchet": f["ratchet"], "rubric": f["rubric"]} for f in FIELDS]}
    elif ns.field:
        env.data = explain_field(ns.field)
    else:
        raise c.UsageError("explain needs a FIELD or --list", hint="e.g. baseline.py explain tests.kill_rate")
    c.write_output(env, ns, text_explain)
    return c.EXIT_OK


def main(argv: list[str] | None = None) -> int:
    ns = build_parser().parse_args(argv)
    c.set_verbosity(ns.verbose)
    return ns.func(ns)


if __name__ == "__main__":
    c.run_main(main)
