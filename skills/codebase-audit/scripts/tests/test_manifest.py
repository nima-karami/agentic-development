import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SCRIPT = os.path.join(SCRIPTS, "manifest.py")
sys.path.insert(0, SCRIPTS)
import manifest as m  # noqa: E402


def gate(**over):
    base = {"id": "lint", "command": "npm run lint", "blocking": True}
    base.update(over)
    return base


def run(*args):
    return subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True, encoding="utf-8")


def git(repo, *args, date="2026-01-01T00:00:00"):
    env = dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    subprocess.run(["git", "-C", repo, "-c", "user.name=T", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True, env=env)


class ManifestFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, obj):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh)
        return path


class ValidateTests(ManifestFiles):
    def test_valid(self):
        p = self.write("a.json", {"gates": [gate()], "local_commands": {"lint": "npm run lint"}})
        proc = run("validate", p)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(json.loads(proc.stdout)["data"]["valid"])

    def test_lists_every_problem(self):
        p = self.write("a.json", {"gates": [
            {"id": "a", "blocking": "yes", "include": "src"},
            {"id": "a", "command": "x", "blocking": True, "thresholds": {"cov": True}, "bogus": 1},
        ]})
        proc = run("validate", p)
        self.assertEqual(proc.returncode, 4)
        data = json.loads(proc.stdout)["data"]
        msgs = [x["message"] for x in data["problems"]]
        self.assertFalse(data["valid"])
        self.assertTrue(any("gates[0]" in x and '"command"' in x and "required" in x for x in msgs))
        self.assertTrue(any('"blocking"' in x and "boolean" in x for x in msgs))
        self.assertTrue(any('"include"' in x and "array" in x for x in msgs))
        self.assertTrue(any("duplicates gates[0]" in x for x in msgs))
        self.assertTrue(any('"thresholds"' in x for x in msgs))
        self.assertTrue(any("bogus" in x and "known" in x for x in msgs))
        self.assertGreaterEqual(data["error_count"], 5)

    def test_unknown_field_is_warning_not_error(self):
        proc = run("validate", self.write("a.json", {"gates": [gate(bogus=1)]}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)["data"]["warning_count"], 1)

    def test_missing_file_exit_4(self):
        self.assertEqual(run("validate", os.path.join(self.tmp.name, "nope.json")).returncode, 4)

    def test_usage_exit_2(self):
        self.assertEqual(run("validate").returncode, 2)
        self.assertEqual(run().returncode, 2)

    def test_not_object(self):
        self.assertEqual(run("validate", self.write("a.json", [1])).returncode, 4)


class HashTests(ManifestFiles):
    def h(self, obj):
        return json.loads(run("hash", self.write("m.json", obj)).stdout)["data"]

    def test_stable_under_reordering_and_aliases(self):
        a = {"gates": [gate(id="a", include=["x", "y"], failure_policy={"continue-on-error": False}),
                       gate(id="b", command="npm  test")]}
        b = {"gates": [gate(id="b", command="npm test"),
                       gate(id="a", include=["y", "x"], failure_policy={})]}
        self.assertEqual(self.h(a)["gates_hash"], self.h(b)["gates_hash"])
        self.assertEqual(len(self.h(a)["gates_hash"]), 16)
        self.assertEqual(set(self.h(a)["gates"]), {"a", "b"})

    def test_changes_with_semantics(self):
        self.assertNotEqual(self.h({"gates": [gate()]})["gates_hash"], self.h({"gates": [gate(blocking=False)]})["gates_hash"])

    def test_invalid_exit_4(self):
        self.assertEqual(run("hash", self.write("m.json", {"gates": [{"id": "a"}]})).returncode, 4)

    def test_deterministic(self):
        p = self.write("m.json", {"gates": [gate()]})
        self.assertEqual(json.loads(run("hash", p).stdout)["data"], json.loads(run("hash", p).stdout)["data"])


class DiffTests(ManifestFiles):
    def diff(self, old, new, *extra):
        proc = run("diff", self.write("o.json", {"gates": old}), self.write("n.json", {"gates": new}), *extra)
        return proc, json.loads(proc.stdout)["data"]

    def classes(self, old, new):
        _, data = self.diff(old, new)
        return {(c["gate"], c["field"]): c["classification"] for c in data["changes"]}

    def test_identical(self):
        _, data = self.diff([gate()], [gate()])
        self.assertTrue(data["identical"])
        self.assertEqual(data["changes"], [])

    def test_removed_and_added(self):
        cls = self.classes([gate(id="a"), gate(id="b")], [gate(id="b"), gate(id="c"), gate(id="d", blocking=False)])
        self.assertEqual(cls[("a", None)], "weakening")
        self.assertEqual(cls[("c", None)], "strengthening")
        self.assertEqual(cls[("d", None)], "neutral/unknown")

    def test_blocking(self):
        self.assertEqual(self.classes([gate()], [gate(blocking=False)])[("lint", "blocking")], "weakening")
        self.assertEqual(self.classes([gate(blocking=False)], [gate()])[("lint", "blocking")], "strengthening")

    def test_failure_policy(self):
        def cls(b, a):
            return self.classes([gate(failure_policy=b)], [gate(failure_policy=a)])[("lint", "failure_policy")]
        self.assertEqual(cls({}, {"continue-on-error": True}), "weakening")
        self.assertEqual(cls({}, {"allow_failure": True}), "weakening")
        self.assertEqual(cls({}, {"retries": 2}), "weakening")
        self.assertEqual(cls({"retries": 1}, {"retries": 3}), "weakening")
        self.assertEqual(cls({}, {"ignore_exit_codes": [1]}), "weakening")
        self.assertEqual(cls({"allow_failure": True}, {}), "strengthening")
        self.assertEqual(cls({"retries": 3}, {"retries": 1}), "strengthening")

    def test_include_exclude(self):
        def cls(f, b, a):
            return self.classes([gate(**{f: b})], [gate(**{f: a})])[("lint", f)]
        self.assertEqual(cls("include", ["src/**", "lib/**"], ["src/**"]), "weakening")
        self.assertEqual(cls("include", [], ["src/**"]), "weakening")
        self.assertEqual(cls("include", ["src/**"], ["src/**", "lib/**"]), "strengthening")
        self.assertEqual(cls("include", ["a"], ["b"]), "neutral/unknown")
        self.assertEqual(cls("exclude", [], ["legacy/**"]), "weakening")
        self.assertEqual(cls("exclude", ["legacy/**"], []), "strengthening")

    def test_thresholds(self):
        def cls(b, a):
            return self.classes([gate(thresholds=b)], [gate(thresholds=a)])[("lint", "thresholds")]
        self.assertEqual(cls({"max-warnings": 0}, {"max-warnings": 20}), "weakening")
        self.assertEqual(cls({"max-warnings": 20}, {"max-warnings": 0}), "strengthening")
        self.assertEqual(cls({"coverage": 80}, {"coverage": 60}), "weakening")
        self.assertEqual(cls({"coverage": "80%"}, {"coverage": 90}), "strengthening")
        self.assertEqual(cls({"min_score": 50}, {"min_score": 40}), "weakening")
        self.assertEqual(cls({"coverage": 80}, {}), "weakening")
        self.assertEqual(cls({"weird": 1}, {"weird": 2}), "neutral/unknown")
        self.assertEqual(cls({"coverage": "high"}, {"coverage": "low"}), "neutral/unknown")

    def test_triggers_and_command(self):
        cls = self.classes([gate(triggers=["push", "pull_request"], command="a")],
                           [gate(triggers=["push"], command="b")])
        self.assertEqual(cls[("lint", "triggers")], "weakening")
        self.assertEqual(cls[("lint", "command")], "neutral/unknown")

    def test_fail_on_weakening_exit_1(self):
        proc, data = self.diff([gate()], [gate(blocking=False)], "--fail-on-weakening")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(data["weakening_count"], 1)
        self.assertEqual(self.diff([gate()], [gate(blocking=False)])[0].returncode, 0)
        self.assertEqual(self.diff([gate(blocking=False)], [gate()], "--fail-on-weakening")[0].returncode, 0)

    def test_local_commands_diff(self):
        o = self.write("o.json", {"gates": [gate()], "local_commands": {"lint": "eslint ."}})
        n = self.write("n.json", {"gates": [gate()], "local_commands": {"lint": "eslint . --quiet"}})
        data = json.loads(run("diff", o, n).stdout)["data"]
        self.assertEqual(data["local_command_changes"][0]["kind"], "changed")

    def test_invalid_input_exit_4(self):
        o = self.write("o.json", {"gates": [{"id": "a"}]})
        self.assertEqual(run("diff", o, o).returncode, 4)

    def test_text_format(self):
        o = self.write("o.json", {"gates": [gate()]})
        n = self.write("n.json", {"gates": [gate(blocking=False)]})
        self.assertIn("[weakening]", run("diff", o, n, "--format", "text").stdout)


class ConfigHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        r = cls.repo = cls.tmp.name
        subprocess.run(["git", "init", "-q", r], check=True)
        os.makedirs(os.path.join(r, ".github", "workflows"))
        ci = os.path.join(r, ".github", "workflows", "ci.yml")
        with open(ci, "w") as fh:
            fh.write("jobs:\n  lint:\n    run: npm run lint\n")
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "Add CI", date="2026-01-01T00:00:00")
        with open(ci, "a") as fh:
            fh.write("    continue-on-error: true\n    run2: eslint --max-warnings 50 || true\n")
        with open(os.path.join(r, "other.txt"), "w") as fh:
            fh.write("x\n")
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "Relax lint", date="2026-02-01T00:00:00")
        git(r, "commit", "-q", "--allow-empty", "-m", "Unrelated", date="2026-03-01T00:00:00")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def hist(self, *extra):
        proc = run("config-history", "--repo", self.repo, *extra)
        return proc, json.loads(proc.stdout)

    def test_history_and_candidates(self):
        proc, env = self.hist("--path", ".github/workflows/*.yml")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = env["data"]
        self.assertEqual([c["subject"] for c in data["commits"]], ["Relax lint", "Add CI"])
        newest = data["commits"][0]
        self.assertEqual(newest["date"][:10], "2026-02-01")
        f = newest["files"][0]
        self.assertEqual((f["file"], f["added"], f["removed"]), (".github/workflows/ci.yml", 2, 0))
        texts = [c["text"] for c in f["candidate_relaxations"]]
        self.assertEqual(len(texts), 2)
        self.assertIn("continue-on-error: true", texts[0])
        self.assertIn("|| true", texts[1])
        self.assertIn("max-warnings", " ".join(f["candidate_relaxations"][1]["patterns"]))
        self.assertEqual(data["commits"][1]["files"][0]["candidate_relaxations"], [])
        self.assertEqual(f["candidate_relaxations"][0]["line"], 4)

    def test_custom_pattern_and_no_defaults(self):
        _, env = self.hist("--path", ".github/workflows/*.yml", "--no-default-patterns", "--relax-pattern", "eslint")
        self.assertEqual(env["data"]["candidate_relaxation_count"], 1)

    def test_bad_regex_warns(self):
        _, env = self.hist("--path", ".github/workflows/*.yml", "--relax-pattern", "(")
        self.assertTrue(any("failed to compile" in w for w in env["warnings"]))

    def test_unmatched_glob_and_range(self):
        _, env = self.hist("--path", "nothing/*.yml")
        self.assertTrue(any("no commits" in w for w in env["warnings"]))
        _, env = self.hist("--path", ".github/workflows/*.yml", "nothing/**")
        self.assertTrue(any("matched no file" in w for w in env["warnings"]))
        _, env = self.hist("--path", ".github/workflows/*.yml", "--range", "HEAD~1..HEAD")
        self.assertEqual(env["data"]["commit_count"], 0)

    def test_truncation_warns(self):
        _, env = self.hist("--path", ".github/workflows/*.yml", "--max-commits", "1")
        self.assertTrue(env["data"]["truncated"])
        self.assertEqual(env["data"]["commit_count"], 1)
        self.assertTrue(any("truncated" in w for w in env["warnings"]))

    def test_deterministic(self):
        self.assertEqual(self.hist("--path", ".github/workflows/*.yml")[1]["data"],
                         self.hist("--path", ".github/workflows/*.yml")[1]["data"])

    def test_not_a_repo_exit_3(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run("config-history", "--repo", d, "--path", "x").returncode, 3)

    def test_missing_path_usage_exit_2(self):
        self.assertEqual(run("config-history", "--repo", self.repo).returncode, 2)

    def test_parse_log_stream_pure(self):
        text = "\x1eabc\x1f2026-01-01T00:00:00+00:00\x1fS\n\ndiff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1,0 +2,2 @@\n+skip me\n+fine\n-gone\n"
        f = m.parse_log_stream(text, [("skip", re.compile("skip"))])[0]["files"][0]
        self.assertEqual((f["added"], f["removed"]), (2, 1))
        self.assertEqual(f["candidate_relaxations"][0]["line"], 2)


if __name__ == "__main__":
    unittest.main()
