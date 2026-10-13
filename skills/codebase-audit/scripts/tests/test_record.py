import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SCRIPT = os.path.join(SCRIPTS, "record.py")
sys.path.insert(0, SCRIPTS)
import record  # noqa: E402

FINDINGS_A = """# Contracts audit

### F-contracts-api-1 · Degraded read treated as empty
- rubric: C4
- anchors: src/api/read.ts:10 ; src/api/write.ts:22
- counterexample: the declaration permits X, yet Y happens
- evidence: provable
- severity: high
- confidence: high
- exposure: hotspot

### F-contracts-api-2 · Unvalidated cast
* **severity:** Medium
* **confidence:** LOW
* **rubric:** C2
* **anchors:** src/api/parse.ts:5

### F-contracts-api-3 · Bare finding with fields missing
- severity: low

### F-perf-api-1 · Loop query
- rubric: P1
- anchors: src/db.ts:7
- status: candidate (unmeasured)
- severity: medium
- confidence: medium

## Authority conflicts

### AC-contracts-api-1 · tabs vs spaces
- conventions: A vs B

## DISMISSED

- `updateSettings` cast (src/api/settings.ts:55): coerceSettings validates per field.
* hub fan-in -> declared public surface, src/core/hub.ts
  continuation line about src/core/hub.ts

## not  assessed

- src/legacy/** : out of sample, not read
- vendor dir: could not read, permission denied
- load tests: profile-blocked, load unknown
"""

FINDINGS_B = """### F-gates-all-1 · Build is not a gate
- rubric: G7
- anchors: package.json
- severity: critical
- confidence: high

## Dismissed

- nothing worth noting: none
"""

FINDINGS_NO_SECTIONS = """### F-bloat-all-1 · Clone family
- rubric: V1
- anchors: src/a.ts:1
- severity: low
- confidence: high
"""

MERGE = """| Raw ID | Disposition | Merged as | Reason |
|---|---|---|---|
| F-contracts-api-1 | merged | H1 | same root cause |
| F-contracts-api-2 | kept | M1 | |
| F-contracts-api-3 | dropped | — | unanchored |
| F-perf-api-1 | refuted | — | work/verdicts/F-perf-api-1.md |
| F-gates-all-1 | downgraded | M2 | verifier: guard at src/x.ts:3 |
| F-gates-all-9 | duplicate | — | of F-gates-all-1 |
| F-ghost-1 | refuted | — | work/verdicts/F-ghost-1.md |
"""

VERDICT = """VERDICT: REFUTED
SEVERITY: unchanged
EVIDENCE: src/db.ts:7 batches the query
NOTE: guarded
"""

HISTORY = {"tool": "history", "warnings": ["shallow clone"],
           "data": {"files": {"src/api/read.ts": {"hotspot": True}, "src/other.ts": {"hotspot": False}},
                    "hotspots": {"all": {"top": [{"file": "src/core/hub.ts", "hotspot": True}]}}}}
FACT_ENV = {"tool": "inventories", "warnings": ["glob matched nothing"],
            "data": {"catchAndDefault": [{"path": "src/api/read.ts", "line": 3}, {"path": "src/never/seen.ts", "line": 9}]}}


def run_cli(*args):
    proc = subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content if isinstance(content, str) else json.dumps(content))
    return path


class RunCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = os.path.join(self.tmp.name, "audits", "2026-10-12-inherited")
        os.makedirs(self.run_dir)

    def cli(self, *args):
        code, out, err = run_cli(*args, "--run", self.run_dir)
        return code, (json.loads(out) if out.strip().startswith("{") else None), err

    def snapshot(self):
        return {os.path.relpath(os.path.join(d, n), self.tmp.name): os.path.getmtime(os.path.join(d, n))
                for d, _, ns in os.walk(self.tmp.name) for n in ns}

    def ledger(self):
        with open(os.path.join(self.run_dir, "ledger.jsonl"), encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def build_run(self, with_gaps=False):
        r = self.run_dir
        write(r, "profile.md", "# Profile — demo @ abc1234\n\n## Stakes\n- Sensitive data: `src/auth/**` and src/payments/\n\n"
                               "## Dominant quality attributes\n1. latency — peak load\n2. integrity — money\n")
        write(r, "work/findings/contracts-api.md", FINDINGS_A)
        write(r, "work/findings/gates-all.md", FINDINGS_B)
        write(r, "work/verdicts/F-perf-api-1.md", VERDICT)
        write(r, "work/verdicts/F-gates-all-1.md", "VERDICT: DOWNGRADE\nSEVERITY: medium\nEVIDENCE: src/x.ts:3\n")
        write(r, "work/facts/history.json", HISTORY)
        write(r, "work/facts/inventories.json", FACT_ENV)
        write(r, "work/briefs/1-judge-contracts.md", "brief")
        write(r, "work/summaries/1-judge-contracts.md", "summary")
        write(r, "work/merge.md", MERGE)
        if with_gaps:
            write(r, "work/findings/bloat-all.md", FINDINGS_NO_SECTIONS)

    def log_ledger(self):
        self.assertEqual(self.cli("log", "dispatch", "--role", "judge", "--wave", "1", "--tier", "judgment", "--model", "opus",
                                  "--brief", "work/briefs/1-judge-contracts.md", "--input", "work/facts/history.json")[0], 0)
        self.cli("log", "done", "--seq", "1", "--status", "ok", "--output", "work/findings/contracts-api.md",
                 "--summary", "work/summaries/1-judge-contracts.md")


class LogTests(RunCase):
    def test_dispatch_assigns_monotonic_seq_and_fields(self):
        self.build_run()
        code, env, _ = self.cli("log", "dispatch", "--role", "judge", "--wave", "2", "--tier", "judgment", "--model", "opus",
                                "--brief", "work/briefs/1-judge-contracts.md", "--input", "a.json", "--label", "x")
        self.assertEqual(code, 0)
        self.assertEqual(env["data"]["seq"], 1)
        code, env, _ = self.cli("log", "dispatch", "--role", "verifier", "--wave", "3", "--tier", "mechanical",
                                "--model", "haiku", "--brief", "work/briefs/1-judge-contracts.md")
        self.assertEqual(env["data"]["seq"], 2)
        first = self.ledger()[0]
        self.assertEqual(set(first), {"seq", "event", "wave", "role", "tier", "model", "brief", "inputs", "started", "label"})
        self.assertEqual(first["inputs"], ["a.json"])
        _, env, _ = self.cli("log", "dispatch", "--role", "r", "--wave", "1", "--tier", "t", "--model", "m",
                             "--brief", "nope.md", "--input", "zzz.json")
        self.assertTrue(any("zzz.json" in w for w in env["warnings"]))
        self.assertTrue(any("nope.md" in w for w in env["warnings"]))

    def test_done_records_duration_and_validates_seq(self):
        self.build_run()
        self.log_ledger()
        done = self.ledger()[1]
        self.assertEqual(done["event"], "done")
        self.assertEqual(done["status"], "ok")
        self.assertIsInstance(done["duration_s"], int)
        code, _, err = self.cli("log", "done", "--seq", "99", "--status", "ok")
        self.assertEqual(code, 4)
        self.assertIn("seq 99", err)

    def test_done_missing_output_warns_not_fails(self):
        self.build_run()
        self.log_ledger()
        code, env, _ = self.cli("log", "done", "--seq", "1", "--status", "partial", "--output", "work/findings/missing.md")
        self.assertEqual(code, 0)
        self.assertTrue(any("missing.md" in w for w in env["warnings"]))

    def test_bad_status_is_usage_error(self):
        self.assertEqual(self.cli("log", "done", "--seq", "1", "--status", "weird")[0], 2)

    def test_missing_run_dir_is_input_error(self):
        code, _, err = run_cli("check", "--run", os.path.join(self.tmp.name, "nope"))
        self.assertEqual(code, 4)
        self.assertIn("hint", err)

    def test_script_and_note(self):
        self.assertEqual(self.cli("log", "script", "--command", "python x.py", "--exit", "2", "--output", "work/facts/x.json")[0], 0)
        self.assertEqual(self.cli("log", "note", "--text", "decision")[0], 0)
        events = self.ledger()
        self.assertEqual([e["event"] for e in events], ["script", "note"])
        self.assertEqual(events[0]["exit"], 2)

    def test_concurrent_dispatches_get_unique_seq(self):
        procs = [subprocess.Popen([sys.executable, "-I", SCRIPT, "log", "dispatch", "--run", self.run_dir, "--role", "judge",
                                   "--wave", "1", "--tier", "t", "--model", "m", "--brief", "b.md"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for _ in range(6)]
        for p in procs:
            self.assertEqual(p.wait(), 0)
        seqs = sorted(e["seq"] for e in self.ledger())
        self.assertEqual(seqs, [1, 2, 3, 4, 5, 6])

    def test_out_outside_run_is_refused(self):
        outside = os.path.join(self.tmp.name, "elsewhere.json")
        code, _, err = self.cli("check", "--out", outside)
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(outside))


class IndexTests(RunCase):
    def index(self):
        self.build_run()
        self.log_ledger()
        code, _, err = self.cli("index")
        self.assertEqual(code, 0, err)
        with open(os.path.join(self.run_dir, "index.json"), encoding="utf-8") as fh:
            return json.load(fh)

    def test_review_sections_in_order_with_links(self):
        self.index()
        with open(os.path.join(self.run_dir, "review.md"), encoding="utf-8") as fh:
            text = fh.read()
        order = [text.index(h) for h in ("## Run", "## Worth a human look", "## Merge trace", "## Agents", "## Files")]
        self.assertEqual(order, sorted(order))
        self.assertIn("(work/findings/contracts-api.md#L", text)
        self.assertIn("(work/verdicts/F-perf-api-1.md)", text)
        self.assertIn("(work/briefs/1-judge-contracts.md)", text)
        self.assertIn("contracts-api.md#L18) | dropped", text)

    def test_unmerged_finding_shown_in_trace(self):
        self.build_run()
        write(self.run_dir, "work/findings/extra.md", "### F-extra-1 · x\n- severity: low\n")
        self.cli("index")
        with open(os.path.join(self.run_dir, "review.md"), encoding="utf-8") as fh:
            self.assertIn("no merge line", fh.read())

    def test_findings_parsed_leniently(self):
        data = self.index()["data"]
        by_id = {f["id"]: f for f in data["findings"]}
        self.assertEqual(set(by_id), {"F-contracts-api-1", "F-contracts-api-2", "F-contracts-api-3", "F-perf-api-1", "F-gates-all-1"})
        lenient = by_id["F-contracts-api-2"]
        self.assertEqual((lenient["severity"], lenient["confidence"], lenient["rubric"]), ("medium", "low", "C2"))
        self.assertEqual(by_id["F-contracts-api-1"]["anchors"], ["src/api/read.ts:10", "src/api/write.ts:22"])
        bare = by_id["F-contracts-api-3"]
        self.assertIsNone(bare["confidence"])
        self.assertIsNone(bare["anchors"])
        self.assertTrue(any("F-contracts-api-3" in w and "contracts-api.md" in w for w in data["parse_warnings"]))
        self.assertEqual([c["id"] for c in data["authority_conflicts"]], ["AC-contracts-api-1"])

    def test_dismissed_and_not_assessed(self):
        data = self.index()["data"]
        dismissed = [d for d in data["dismissed"] if d["file"].endswith("contracts-api.md")]
        self.assertEqual(len(dismissed), 2)
        self.assertIn("continuation line", dismissed[1]["text"])
        groups = data["worth_a_human_look"]["not_assessed_by_reason"]
        self.assertEqual(set(groups), {"could not read", "out of sample", "profile-blocked"})

    def test_worth_a_look_lists(self):
        data = self.index()["data"]
        worth = data["worth_a_human_look"]
        self.assertEqual([v["finding_id"] for v in worth["verifier_refuted_or_downgraded"]], ["F-gates-all-1", "F-perf-api-1"])
        self.assertEqual([f["id"] for f in worth["low_confidence"]], ["F-contracts-api-2"])
        self.assertEqual([f["id"] for f in worth["unmeasured_performance"]], ["F-perf-api-1"])
        hits = {h["candidate"]: h["matched"] for h in worth["dismissed_in_hotspot_entry_or_stakes"]}
        self.assertEqual([m for k, m in hits.items() if k.startswith("hub fan-in")], [["hotspot"]])
        self.assertFalse(any("updateSettings" in k for k in hits))
        self.assertEqual(data["sources"]["hotspot_paths"], 2)

    def test_unreviewed_candidates_heuristic(self):
        worth = self.index()["data"]["worth_a_human_look"]
        rows = worth["unreviewed_candidates"]
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["file"], rows[0]["unreviewed"], rows[0]["candidates"]), ("work/facts/inventories.json", 1, 2))
        self.assertEqual(sorted(w["file"] for w in worth["script_warnings"]), ["work/facts/history.json", "work/facts/inventories.json"])

    def test_merge_parsed_with_every_disposition(self):
        merge = {m["raw_id"]: m for m in self.index()["data"]["merge"]}
        self.assertEqual({m["disposition"] for m in merge.values()}, {"merged", "kept", "downgraded", "refuted", "dropped", "duplicate"})
        self.assertIsNone(merge["F-contracts-api-3"]["merged_as"])
        self.assertEqual(merge["F-gates-all-1"]["merged_as"], "M2")

    def test_profile_and_run_identity(self):
        run = self.index()["data"]["run"]
        self.assertEqual((run["mode"], run["commit"]), ("inherited", "abc1234"))
        self.assertEqual(run["dominant_attributes"], ["latency", "integrity"])
        self.assertEqual(len(run["profile_hash"]), 12)

    def test_stakes_path_match(self):
        self.build_run()
        write(self.run_dir, "work/findings/gates-all.md", FINDINGS_B + "- login guard (src/auth/login.ts:4): fine\n")
        self.cli("index")
        with open(os.path.join(self.run_dir, "index.json"), encoding="utf-8") as fh:
            hits = json.load(fh)["data"]["worth_a_human_look"]["dismissed_in_hotspot_entry_or_stakes"]
        self.assertIn(["stakes path"], [h["matched"] for h in hits])

    def test_deterministic_data_and_review(self):
        first = self.index()
        with open(os.path.join(self.run_dir, "review.md"), encoding="utf-8") as fh:
            review = fh.read()
        self.cli("index")
        with open(os.path.join(self.run_dir, "index.json"), encoding="utf-8") as fh:
            second = json.load(fh)
        self.assertEqual(json.dumps(first["data"], sort_keys=True), json.dumps(second["data"], sort_keys=True))
        with open(os.path.join(self.run_dir, "review.md"), encoding="utf-8") as fh:
            self.assertEqual(review, fh.read())
        self.assertNotIn("started", json.dumps(first["data"]))

    def test_bad_files_warn_and_continue(self):
        self.build_run()
        write(self.run_dir, "work/facts/broken.json", "{not json")
        write(self.run_dir, "work/verdicts/F-x-1.md", "no verdict here")
        code, _, err = self.cli("index")
        self.assertEqual(code, 0)
        self.assertIn("broken.json", err)
        self.assertIn("F-x-1.md", err)

    def test_nothing_written_outside_run(self):
        self.build_run(with_gaps=True)
        self.log_ledger()
        before = self.snapshot()
        self.cli("index")
        self.cli("check", "--fail-on-gaps")
        changed = {p for p, m in self.snapshot().items() if before.get(p) != m}
        self.assertEqual(changed, {os.path.join("audits", "2026-10-12-inherited", n) for n in ("review.md", "index.json")})


class CheckTests(RunCase):
    def gap_types(self, *extra):
        code, env, _ = self.cli("check", *extra)
        return code, env, {g["type"] for g in env["data"]["gaps"]}

    def test_every_gap_type_once(self):
        self.build_run(with_gaps=True)
        self.log_ledger()
        self.cli("log", "dispatch", "--role", "verifier", "--wave", "2", "--tier", "t", "--model", "m", "--brief", "work/briefs/1-judge-contracts.md")
        self.cli("log", "dispatch", "--role", "judge", "--wave", "2", "--tier", "t", "--model", "m", "--brief", "work/briefs/1-judge-contracts.md")
        self.cli("log", "done", "--seq", "3", "--status", "failed")
        self.cli("log", "script", "--command", "python -I x.py --flag", "--exit", "3", "--output", "work/facts/x.json")
        self.cli("log", "script", "--command", "python -I y.py", "--exit", "1", "--note", "advisory only")
        with open(os.path.join(self.run_dir, "ledger.jsonl"), "a", encoding="utf-8") as fh:
            fh.write("garbage line\n" + json.dumps({"seq": 42, "event": "done", "status": "ok"}) + "\n")
        write(self.run_dir, "work/verdicts/F-unlisted-1.md", VERDICT)
        code, env, types = self.gap_types("--fail-on-gaps")
        self.assertEqual(code, 1)
        expected = {"dispatch_without_done", "done_without_summary", "finding_without_merge_line", "merge_line_missing_file",
                    "judge_file_missing_section", "verdict_not_in_merge", "script_nonzero_unexplained", "ledger_line_invalid",
                    "done_without_dispatch"}
        self.assertEqual(types, expected)
        for gap in env["data"]["gaps"]:
            self.assertTrue(gap["file"] and gap["fix"])
        by = {g["type"]: g for g in env["data"]["gaps"]}
        by["judge_file_missing_section"] = next(g for g in env["data"]["gaps"] if g["file"].endswith("bloat-all.md") and g["type"] == "judge_file_missing_section")
        self.assertEqual(by["dispatch_without_done"]["seq"], 2)
        self.assertEqual(by["merge_line_missing_file"]["target"], "work/verdicts/F-ghost-1.md")
        self.assertEqual(by["judge_file_missing_section"]["missing"], ["Dismissed", "Not assessed"])
        self.assertEqual(sum(1 for g in env["data"]["gaps"] if g["type"] == "script_nonzero_unexplained"), 1)

    def test_merge_missing_gap(self):
        write(self.run_dir, "work/findings/a.md", "### F-a-1 · x\n- severity: low\n")
        self.assertIn("merge_missing", self.gap_types()[2])

    def test_clean_run_has_no_gaps_and_exit_zero(self):
        r = self.run_dir
        write(r, "work/findings/a.md", "### F-a-1 · x\n- severity: low\n- confidence: high\n- rubric: R\n- anchors: a.ts:1\n\n"
                                       "## Dismissed\n\n- none\n\n## Not assessed\n\n- none\n")
        write(r, "work/merge.md", "| Raw ID | Disposition | Merged as | Reason |\n|---|---|---|---|\n| F-a-1 | kept | M1 | |\n")
        write(r, "work/briefs/b.md", "b")
        write(r, "work/summaries/s.md", "s")
        self.cli("log", "dispatch", "--role", "judge", "--wave", "1", "--tier", "t", "--model", "m", "--brief", "work/briefs/b.md")
        self.cli("log", "done", "--seq", "1", "--status", "ok", "--summary", "work/summaries/s.md")
        code, env, types = self.gap_types("--fail-on-gaps")
        self.assertEqual((code, types), (0, set()))
        self.assertTrue(env["data"]["clean"])

    def test_gaps_exit_zero_without_flag(self):
        code, _, types = self.gap_types()
        self.assertEqual(code, 0)
        self.assertIn("ledger_missing", types)

    def test_later_note_explains_nonzero_script(self):
        self.cli("log", "script", "--command", "python -I x.py", "--exit", "1", "--output", "work/facts/x.json")
        self.assertIn("script_nonzero_unexplained", self.gap_types()[2])
        self.cli("log", "note", "--text", "work/facts/x.json is empty on purpose")
        self.assertNotIn("script_nonzero_unexplained", self.gap_types()[2])

    def test_text_format(self):
        code, out, _ = run_cli("check", "--run", self.run_dir, "--format", "text")
        self.assertEqual(code, 0)
        self.assertIn("ledger_missing", out)


class PureFunctionTests(unittest.TestCase):
    def test_parse_merge_unknown_disposition_warns(self):
        warns = record.Collector()
        rows = record.parse_merge_text("| Raw ID | Disposition | Merged as | Reason |\n|--|--|--|--|\n| F-1 | maybe | - | r |\n", "m.md", warns)
        self.assertEqual(rows[0]["disposition"], "maybe")
        self.assertEqual(len(warns.items), 1)

    def test_not_assessed_classifier(self):
        self.assertEqual(record.classify_not_assessed("x could not read"), "could not read")
        self.assertEqual(record.classify_not_assessed("row ruled out by the profile"), "ruled out by profile")
        self.assertEqual(record.classify_not_assessed("zzz"), "other")

    def test_help_documents_gaps(self):
        code, out, _ = run_cli("--help")
        self.assertEqual(code, 0)
        self.assertIn("dispatch_without_done", out)


if __name__ == "__main__":
    unittest.main()
