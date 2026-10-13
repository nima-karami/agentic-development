import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SCRIPT = os.path.join(SCRIPTS, "baseline.py")
sys.path.insert(0, SCRIPTS)
import baseline  # noqa: E402

FIELD_BASELINE = r"C:\my-github\conduit\docs\audits\baseline.json"


def sample():
    return {
        "schema": 1,
        "audit": {"date": "2026-10-01", "mode": "drift", "depth": "standard", "commit": "abc", "range": None,
                  "report": "docs/audits/x/report.md"},
        "profile": {"path": "docs/audits/x/profile.md", "hash": "p1", "dominant_attributes": ["latency"],
                    "unknowns": []},
        "scope": {"fingerprint": "f1", "include": ["src/**"], "exclude": [], "tools": {"node": "24"},
                  "scan_commands": {"graph": "node g.js"}},
        "architecture": {"violations_by_rule": {"R1": 2, "R2": 0}, "cycle_nodes": 0, "largest_scc": 0,
                         "hotspots_top20": [{"path": "a.ts", "churn": 3, "complexity": 9}],
                         "cochange_top": [{"a": "a.ts", "b": "b.ts", "ratio": 0.5}],
                         "parallel_abstractions": [{"concern": "http", "members": ["x", "y"], "status": "open"}]},
        "gates": {"manifest_hash": "g1", "required_checks": ["build", "test"],
                  "debt": {"suppressions": {"ts-ignore": {"count": 4, "median_age_days": 30}},
                           "skips": 1, "allowed_failures": 0, "exemptions": 0},
                  "escape_hatches": {"total": 10, "at_ingestion": 2}},
        "tests": {"sample_files": ["src/a.ts", "src/b.ts"], "eligible_untested": 3, "pseudo_tested": 1,
                  "kill_rate": 0.8},
        "verbosity": {"clone_families": 5, "cross_module_clones": 1, "dead_files": 2, "dead_exports": 9},
        "security": {"scanner_manifest_hash": "s1", "unguarded_mutating_entry_points": 0, "entry_points": 12,
                     "permissive_flags": 0, "secrets_live": 0, "reachable_known_cves": 0,
                     "unpinned_ci_actions": 2},
        "performance": {"flows": [{"name": "checkout", "fan_out": 4, "serial_depth": 2,
                                   "measured": {"p95_ms": 200, "bundle_kb": None}}],
                        "calls_in_loops": 1, "unbounded_reads": 0, "blocking_calls_on_critical_threads": 0,
                        "uncapped_caches": 0, "unpaired_lifecycles": 0, "clients_missing_timeouts": 0},
        "audit_quality": {"findings_sampled": 0, "confirmed": 0, "confirmed_share": None,
                          "refuted_by_verifier": 0},
        "accepted_exceptions": [{"what": "legacy", "anchor": "src/x.ts", "owner": "nima", "reason": "r",
                                 "expires": "2026-12-31"}],
    }


def run(*args):
    proc = subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr


class Files:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()

    def write(self, name, doc):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(doc if isinstance(doc, str) else json.dumps(doc))
        return path


class Base(unittest.TestCase):
    def setUp(self):
        self.files = Files()
        self.addCleanup(self.files.tmp.cleanup)

    def compare(self, old, new, *extra):
        code, out, err = run("compare", self.files.write("old.json", old), self.files.write("new.json", new), *extra)
        return code, (json.loads(out) if out.strip().startswith("{") else None), err


class Validate(Base):
    def problems(self, doc):
        errors, warnings = baseline.validate_document(doc)
        return {e["path"]: e["message"] for e in errors}, warnings

    def test_valid_sample(self):
        errors, warnings = self.problems(sample())
        self.assertEqual(errors, {})
        self.assertEqual(warnings, [])

    def test_missing_optional_dimensions_warn_only(self):
        doc = sample()
        del doc["security"], doc["performance"]
        errors, warnings = self.problems(doc)
        self.assertEqual(errors, {})
        self.assertEqual(sorted(w["path"] for w in warnings), ["$.performance", "$.security"])

    def test_missing_required_and_bad_types(self):
        doc = sample()
        del doc["gates"]
        doc["audit"]["mode"] = "weird"
        doc["audit"]["depth"] = "deep!"
        doc["verbosity"]["dead_files"] = -1
        doc["verbosity"]["dead_exports"] = True
        doc["tests"]["kill_rate"] = 1.5
        errors, _ = self.problems(doc)
        self.assertIn("$.gates", errors)
        for path in ("$.audit.mode", "$.audit.depth", "$.verbosity.dead_files", "$.verbosity.dead_exports",
                     "$.tests.kill_rate"):
            self.assertIn(path, errors)

    def test_confirmed_share_rules(self):
        doc = sample()
        doc["audit_quality"]["confirmed_share"] = 0
        self.assertIn("$.audit_quality.confirmed_share", self.problems(doc)[0])
        doc["audit_quality"].update(findings_sampled=4, confirmed=2, confirmed_share=0.5)
        self.assertEqual(self.problems(doc)[0], {})
        doc["audit_quality"]["confirmed_share"] = 1.2
        self.assertIn("$.audit_quality.confirmed_share", self.problems(doc)[0])

    def test_exceptions_need_owner_reason_date(self):
        doc = sample()
        doc["accepted_exceptions"] = [{"what": "x", "anchor": "y", "expires": "soon"}]
        errors, _ = self.problems(doc)
        self.assertIn("$.accepted_exceptions[0].owner", errors)
        self.assertIn("$.accepted_exceptions[0].reason", errors)
        self.assertIn("$.accepted_exceptions[0].expires", errors)

    def test_unknown_keys_warn_notes_ignored(self):
        doc = sample()
        doc["extra"] = 1
        doc["gates"]["required_checks_note"] = "fine"
        doc["gates"]["escape_hatches"]["note"] = "fine"
        doc["gates"]["mystery"] = 1
        errors, warnings = baseline.validate_document(doc)
        self.assertEqual(errors, [])
        self.assertEqual(sorted(w["path"] for w in warnings), ["$.extra", "$.gates.mystery"])

    def test_run_mode_needs_range(self):
        doc = sample()
        doc["audit"]["mode"] = "run"
        self.assertIn("$.audit.range", self.problems(doc)[0])

    def test_non_object(self):
        self.assertIn("$", self.problems([])[0])

    def test_cli_exit_codes(self):
        good = self.files.write("good.json", sample())
        self.assertEqual(run("validate", good)[0], 0)
        bad = sample()
        bad["schema"] = 2
        code, out, _ = run("validate", self.files.write("bad.json", bad))
        self.assertEqual(code, 4)
        self.assertFalse(json.loads(out)["data"]["valid"])
        self.assertEqual(run("validate", os.path.join(self.files.tmp.name, "nope.json"))[0], 4)
        self.assertEqual(run("validate", self.files.write("junk.json", "{"))[0], 4)

    def test_cli_text(self):
        code, out, _ = run("validate", self.files.write("good.json", sample()), "--format", "text")
        self.assertEqual(code, 0)
        self.assertIn("valid", out)

    @unittest.skipUnless(os.path.exists(FIELD_BASELINE), "field baseline not present")
    def test_field_baseline_is_valid(self):
        code, out, _ = run("validate", FIELD_BASELINE)
        self.assertEqual(code, 0, out)


class Compare(Base):
    def test_identical_is_same_and_trusted(self):
        code, doc, _ = self.compare(sample(), sample(), "--fail-on-breach")
        self.assertEqual(code, 0)
        data = doc["data"]
        self.assertTrue(data["trusted"])
        self.assertEqual(set(data["trend"].values()), {"same"})
        self.assertEqual(data["breaches"], [])

    def test_worse_with_ratchet_breaches_exit_1(self):
        new = sample()
        new["architecture"]["violations_by_rule"]["R2"] = 3
        new["gates"]["debt"]["skips"] = 4
        new["tests"]["kill_rate"] = 0.6
        new["security"]["permissive_flags"] = 1
        code, doc, _ = self.compare(sample(), new, "--fail-on-breach")
        self.assertEqual(code, 1)
        fields = {b["field"] for b in doc["data"]["breaches"]}
        self.assertEqual(fields, {"architecture.violations_by_rule.R2", "gates.debt.skips", "tests.kill_rate",
                                  "security.permissive_flags"})
        self.assertEqual(doc["data"]["trend"]["architecture"], "worse")
        self.assertEqual(doc["data"]["trend"]["verbosity"], "same")
        skips = next(f for f in doc["data"]["fields"] if f["field"] == "gates.debt.skips")
        self.assertEqual((skips["old"], skips["new"], skips["delta"], skips["direction"]), (1, 4, 3, "worse"))
        self.assertTrue(skips["up_is_worse"])

    def test_without_flag_breach_exits_zero(self):
        new = sample()
        new["gates"]["debt"]["skips"] = 9
        self.assertEqual(self.compare(sample(), new)[0], 0)

    def test_better_trend(self):
        new = sample()
        new["verbosity"]["dead_exports"] = 1
        new["tests"]["kill_rate"] = 0.95
        doc = self.compare(sample(), new)[1]["data"]
        self.assertEqual(doc["trend"]["verbosity"], "better")
        self.assertEqual(doc["trend"]["tests"], "better")
        self.assertEqual(doc["breaches"], [])

    def test_noise_ignores_small_changes(self):
        new = sample()
        new["verbosity"]["dead_exports"] = 10
        within = self.compare(sample(), new, "--noise", "0.2")[1]["data"]
        entry = next(f for f in within["fields"] if f["field"] == "verbosity.dead_exports")
        self.assertEqual(entry["direction"], "same")
        self.assertTrue(entry["within_noise"])
        self.assertEqual(within["trend"]["verbosity"], "same")
        beyond = self.compare(sample(), new, "--noise", "0.05")[1]["data"]
        self.assertEqual(beyond["trend"]["verbosity"], "worse")

    def test_new_dynamic_key_counts_from_zero(self):
        new = sample()
        new["gates"]["debt"]["suppressions"]["eslint-disable"] = {"count": 2, "median_age_days": 1}
        data = self.compare(sample(), new)[1]["data"]
        self.assertIn("gates.debt.suppressions.eslint-disable.count", {b["field"] for b in data["breaches"]})

    def test_profile_hash_mismatch(self):
        new = sample()
        new["profile"]["hash"] = "p2"
        code, doc, err = self.compare(sample(), new)
        self.assertFalse(doc["data"]["comparable_profile"])
        self.assertFalse(doc["data"]["trusted"])
        self.assertTrue(any("profile hash differs" in w for w in doc["warnings"]))

    def test_scope_mismatch_flags_breaches_untrusted(self):
        new = sample()
        new["scope"]["fingerprint"] = "f2"
        new["gates"]["debt"]["skips"] = 3
        code, doc, _ = self.compare(sample(), new, "--fail-on-breach")
        data = doc["data"]
        self.assertFalse(data["comparable_scope"])
        self.assertEqual(code, 1)
        self.assertFalse(data["breaches"][0]["trusted"])
        self.assertTrue(any(f["field"] == "gates.debt.skips" for f in data["fields"]))

    def test_missing_profile_is_unknown_not_false(self):
        old = sample()
        del old["profile"]
        data = self.compare(old, sample())[1]["data"]
        self.assertIsNone(data["comparable_profile"])
        self.assertTrue(data["trusted"])

    def test_sample_files_removal_is_violation(self):
        new = sample()
        new["tests"]["sample_files"] = ["src/a.ts", "src/c.ts"]
        data = self.compare(sample(), new)[1]["data"]
        self.assertEqual(data["sample_files"], {"added": ["src/c.ts"], "removed": ["src/b.ts"], "violation": True})
        self.assertIn("tests.sample_files", {b["field"] for b in data["breaches"]})

    def test_sample_files_extension_is_fine(self):
        new = sample()
        new["tests"]["sample_files"].append("src/c.ts")
        data = self.compare(sample(), new)[1]["data"]
        self.assertFalse(data["sample_files"]["violation"])
        self.assertEqual(data["breaches"], [])

    def test_gate_removed_and_manifest_changed(self):
        new = sample()
        new["gates"]["required_checks"] = ["build"]
        new["gates"]["manifest_hash"] = "g2"
        data = self.compare(sample(), new)[1]["data"]
        self.assertEqual(data["gates"]["required_checks_removed"], ["test"])
        self.assertTrue(data["gates"]["manifest_hash_changed"])
        self.assertIn("gates.required_checks", {b["field"] for b in data["breaches"]})

    def test_parallel_abstraction_added_and_grown(self):
        new = sample()
        new["architecture"]["parallel_abstractions"][0]["members"].append("z")
        new["architecture"]["parallel_abstractions"].append({"concern": "cache", "members": ["a"], "status": "open"})
        data = self.compare(sample(), new)[1]["data"]
        self.assertEqual(data["parallel_abstractions"]["added"], ["cache"])
        self.assertEqual(data["parallel_abstractions"]["grown"], ["http"])
        self.assertEqual(len(data["breaches"]), 2)

    def test_dimension_new_and_off(self):
        old = sample()
        del old["security"]
        new = sample()
        del new["performance"]
        data = self.compare(old, new)[1]["data"]
        self.assertEqual(data["trend"]["security"], "new")
        self.assertEqual(data["trend"]["performance"], "off")

    def test_flow_p95_slower_is_breach(self):
        new = sample()
        new["performance"]["flows"][0]["measured"]["p95_ms"] = 350
        data = self.compare(sample(), new)[1]["data"]
        self.assertEqual([b["field"] for b in data["breaches"]], ["performance.flows.checkout.measured.p95_ms"])

    def test_unmeasured_to_measured_is_not_a_breach(self):
        old = sample()
        old["performance"]["flows"][0]["measured"]["p95_ms"] = None
        data = self.compare(old, sample())[1]["data"]
        self.assertEqual(data["breaches"], [])

    def test_expired_exceptions_use_new_audit_date(self):
        new = sample()
        new["audit"]["date"] = "2027-02-01"
        data = self.compare(sample(), new)[1]["data"]
        self.assertEqual(data["as_of"], "2027-02-01")
        self.assertEqual([e["what"] for e in data["expired_exceptions"]], ["legacy"])
        self.assertEqual(data["expired_exceptions"][0]["days_overdue"], 32)

    def test_as_of_override(self):
        data = self.compare(sample(), sample(), "--as-of", "2030-01-01")[1]["data"]
        self.assertEqual(len(data["expired_exceptions"]), 1)
        data = self.compare(sample(), sample(), "--as-of", "2026-12-31")[1]["data"]
        self.assertEqual(data["expired_exceptions"], [])

    def test_dropped_exceptions_listed(self):
        new = sample()
        new["accepted_exceptions"] = []
        data = self.compare(sample(), new)[1]["data"]
        self.assertEqual([e["what"] for e in data["dropped_exceptions"]], ["legacy"])

    def test_run_mode_refused_without_force(self):
        run_doc = sample()
        run_doc["audit"].update(mode="run", range="a..b")
        code, _, err = self.compare(sample(), run_doc)
        self.assertEqual(code, 4)
        self.assertIn("--force", err)
        code, doc, _ = self.compare(sample(), run_doc, "--force")
        self.assertEqual(code, 0)
        self.assertFalse(doc["data"]["comparable_mode"])
        self.assertFalse(doc["data"]["trusted"])

    def test_tool_changes_and_hotspots(self):
        new = sample()
        new["scope"]["tools"]["node"] = "26"
        new["architecture"]["hotspots_top20"] = [{"path": "z.ts", "churn": 1, "complexity": 1}]
        data = self.compare(sample(), new)[1]["data"]
        self.assertEqual(data["tool_changes"], [{"tool": "node", "old": "24", "new": "26"}])
        self.assertEqual(data["hotspots"], {"entered": ["z.ts"], "left": ["a.ts"]})

    def test_usage_and_input_errors(self):
        good = self.files.write("g.json", sample())
        self.assertEqual(run("compare", good, good, "--noise", "-1")[0], 2)
        self.assertEqual(run("compare", good, good, "--as-of", "yesterday")[0], 2)
        self.assertEqual(run("compare", good, os.path.join(self.files.tmp.name, "none.json"))[0], 4)
        bad = sample()
        del bad["tests"]
        self.assertEqual(run("compare", good, self.files.write("bad.json", bad))[0], 4)

    def test_deterministic(self):
        new = sample()
        new["gates"]["debt"]["skips"] = 3
        a = self.compare(sample(), new)[1]["data"]
        b = self.compare(sample(), new)[1]["data"]
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_text_output(self):
        new = sample()
        new["gates"]["debt"]["skips"] = 3
        code, out, _ = run("compare", self.files.write("o.json", sample()), self.files.write("n.json", new),
                           "--format", "text")
        self.assertEqual(code, 0)
        self.assertIn("BREACH gates.debt.skips", out)

    @unittest.skipUnless(os.path.exists(FIELD_BASELINE), "field baseline not present")
    def test_field_baseline_against_itself(self):
        code, out, _ = run("compare", FIELD_BASELINE, FIELD_BASELINE, "--fail-on-breach")
        self.assertEqual(code, 0)
        data = json.loads(out)["data"]
        self.assertEqual(data["breaches"], [])
        self.assertEqual(data["trend"]["security"], "off")


class Explain(Base):
    def test_known_field(self):
        code, out, _ = run("explain", "gates.debt.skips")
        data = json.loads(out)["data"]
        self.assertEqual(code, 0)
        self.assertEqual(data["direction"], "up_is_worse")
        self.assertEqual(data["ratchet"], "skips rising")

    def test_dynamic_field(self):
        data = json.loads(run("explain", "performance.flows.checkout.fan_out")[1])["data"]
        self.assertIn("P1", data["rubric"])

    def test_unknown_field_suggests(self):
        code, _, err = run("explain", "gates.debt.skip")
        self.assertEqual(code, 2)
        self.assertIn("gates.debt.skips", err)

    def test_list_and_missing_arg(self):
        code, out, _ = run("explain", "--list")
        self.assertEqual(code, 0)
        self.assertGreater(len(json.loads(out)["data"]["fields"]), 20)
        self.assertEqual(run("explain")[0], 2)

    def test_every_pattern_resolves_to_itself(self):
        for f in baseline.FIELDS:
            probe = f["pattern"].replace("*", "x")
            self.assertEqual(baseline.spec_for(probe)["pattern"], f["pattern"])

    def test_help_prints_field_table(self):
        out = run("compare", "--help")[1]
        self.assertIn("up_is_worse=", out)
        self.assertIn("RATCHET", out)


if __name__ == "__main__":
    unittest.main()
