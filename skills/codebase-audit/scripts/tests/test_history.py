import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SCRIPT = os.path.join(SCRIPTS, "history.py")
sys.path.insert(0, SCRIPTS)
import history  # noqa: E402


class Repo:
    def __init__(self, root):
        self.root = root
        self.tick = 0
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Dev One")
        self.git("config", "user.email", "dev@example.com")
        self.git("config", "core.autocrlf", "false")

    def git(self, *args, env=None):
        full = dict(os.environ, **(env or {}))
        return subprocess.run(["git", "-C", self.root, *args], check=True, capture_output=True,
                              text=True, env=full).stdout

    def write(self, path, text):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    def commit(self, subject, files=None, body="", author=None, remove=(), rename=()):
        for path, text in (files or {}).items():
            self.write(path, text)
        for old, new in rename:
            os.makedirs(os.path.dirname(os.path.join(self.root, new)) or self.root, exist_ok=True)
            self.git("mv", old, new)
        for path in remove:
            self.git("rm", "-q", path)
        self.git("add", "-A")
        self.tick += 1
        date = f"2026-01-{self.tick:02d}T12:00:00+00:00"
        env = {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
        if author:
            env.update(GIT_AUTHOR_NAME=author, GIT_AUTHOR_EMAIL=f"{author}@bots.example")
        message = subject + (f"\n\n{body}" if body else "")
        self.git("commit", "-q", "--allow-empty", "-m", message, env=env)


def run_cli(repo, *args, expect=0):
    proc = subprocess.run([sys.executable, "-I", SCRIPT, "--repo", repo, *args],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == expect, f"exit {proc.returncode}, expected {expect}\n{proc.stderr}"
    return proc


def run_json(repo, *args):
    return json.loads(run_cli(repo, *args).stdout)


BRANCHY = "function f(a,b){ if (a && b) { for (;;) {} } return a ? 1 : 2 }\n"


def build_repo(tmp):
    r = Repo(tmp)
    r.commit("Add api and ui", {"src/api/a.ts": "const x = 1\n", "src/ui/u.ts": "const y = 1\n",
                                "test/a.test.ts": "it()\n", "README.md": "hi\n"})
    r.commit("Change api and ui", {"src/api/a.ts": BRANCHY, "src/ui/u.ts": "const y = 2\n"})
    r.commit("Tweak api and ui again", {"src/api/a.ts": BRANCHY + "// c\n", "src/ui/u.ts": "const y = 3\n"})
    r.commit("Third co-change", {"src/api/a.ts": BRANCHY + "// d\n", "src/ui/u.ts": "const y = 4\n"})
    r.commit("Fix with test", {"src/api/a.ts": BRANCHY + "// e\n", "test/a.test.ts": "it(1)\n"},
             body="Co-Authored-By: Claude <noreply@anthropic.com>")
    r.commit("chore(deps): bump lodash", {"package.json": "{}\n", "src/api/b.ts": "const z=1\n"}, author="dependabot[bot]")
    r.commit("style: prettier", {"src/ui/u.ts": "const y = 5\n"})
    r.commit("Update docs only", {"README.md": "hello\n"})
    return r


class PureFunctionTests(unittest.TestCase):
    def test_c_like_tokens_strip_comments_and_strings(self):
        text = 'const s = "if && ||"; // while for\n/* case */ if (a && b) { x = a ?? b; y = a?.b; z = c ? 1 : 2 }\n'
        got = history.measure_complexity(text, "x.ts", "tokens")
        self.assertEqual(got["complexity"], 1 + 1 + 1 + 1 + 1)
        self.assertEqual(got["basis"], "tokens")

    def test_python_tokens(self):
        text = '"""if for"""\n# while\nif a and b or c:\n    pass\nelif d:\n    pass\n'
        self.assertEqual(history.measure_complexity(text, "m.py", "tokens")["complexity"], 1 + 4)

    def test_shell_tokens(self):
        text = '# if\necho "a && b"\nif [ x ] && [ y ]; then :; fi\nfor i in 1; do :; done\n'
        self.assertEqual(history.measure_complexity(text, "s.sh", "tokens")["complexity"], 1 + 3)

    def test_unknown_extension_uses_lines(self):
        got = history.measure_complexity("a\n\nb\nc\n", "x.rb", "tokens")
        self.assertEqual((got["complexity"], got["basis"]), (3, "lines"))

    def test_none_mode(self):
        self.assertEqual(history.measure_complexity(BRANCHY, "x.ts", "none")["complexity"], 1)

    def test_module_of(self):
        self.assertEqual(history.module_of("src/foo/x.ts", 2, []), "src/foo")
        self.assertEqual(history.module_of("src/x.ts", 2, []), "src")
        self.assertEqual(history.module_of("x.ts", 2, []), "(root)")
        self.assertEqual(history.module_of("src/foo/x.ts", 2, [("src/**", "core")]), "core")

    def test_rename_resolution_is_time_aware(self):
        commits = [
            {"entries": [(None, "new.py", "1", "0")]},
            {"entries": [("old.py", "new.py", "0", "0")]},
            {"entries": [(None, "old.py", "5", "0")]},
        ]
        history.resolve_renames(commits)
        self.assertEqual([c["files"][0][0] for c in commits], ["new.py", "new.py", "new.py"])

    def test_classify_order(self):
        import re
        pats = {k: re.compile(v, re.I | re.M) for k, v in (
            ("agent-pattern", history.DEFAULT_AGENT_PATTERN), ("bot-pattern", history.DEFAULT_BOT_PATTERN),
            ("formatter-pattern", history.DEFAULT_FORMATTER_PATTERN), ("deps-pattern", history.DEFAULT_DEPS_PATTERN))}
        base = {"author": "a", "email": "a@x", "subject": "s", "message": "s"}
        self.assertEqual(history.classify(dict(base, message="s\n\nCo-authored-by: GitHub Copilot <x>"), pats)[0], "agent")
        self.assertEqual(history.classify(dict(base, author="renovate[bot]"), pats)[0], "bot")
        self.assertEqual(history.classify(dict(base, subject="Run prettier"), pats)[0], "formatter")
        self.assertEqual(history.classify(dict(base, subject="Bump lodash"), pats)[0], "dependency-update")
        self.assertEqual(history.classify(dict(base, subject="Add feature"), pats)[0], "human")

    def test_parse_log_with_rename(self):
        raw = "\x01abc\x022026-01-01T00:00:00+00:00\x02N\x02e@x\x02subj\x02subj\n\n\x03\n1\t2\t\0old\0new\0" \
              "3\t0\tplain.txt\0-\t-\tbin.png\0"
        entries = history.parse_log(raw)[0]["entries"]
        self.assertEqual(entries, [("old", "new", "1", "2"), (None, "plain.txt", "3", "0"), (None, "bin.png", "-", "-")])


class CliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = build_repo(cls.tmp.name).root
        cls.out = run_json(cls.repo, "--module-depth", "2", "--min-shared", "3")
        cls.data = cls.out["data"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_envelope_and_window(self):
        self.assertEqual(self.out["tool"], "history")
        w = self.data["window"]
        self.assertEqual(w["commits"], 8)
        self.assertEqual((w["first_commit_date"], w["last_commit_date"]), ("2026-01-01", "2026-01-08"))
        self.assertFalse(w["shallow"])

    def test_churn_and_complexity(self):
        a = self.data["files"]["src/api/a.ts"]
        self.assertEqual(a["commits"], 5)
        self.assertEqual(a["complexity_basis"], "tokens")
        self.assertEqual(a["complexity"], 1 + 4)
        self.assertEqual(a["score"], 5 * a["complexity"])
        self.assertEqual(a["rank"], 1)
        self.assertTrue(a["hotspot"])

    def test_class_counts_and_rules(self):
        counts = self.data["authors"]["counts_by_class"]
        self.assertEqual(counts, {"human": 5, "agent": 1, "bot": 1, "formatter": 1, "dependency-update": 0})
        rules = self.data["authors"]["rules"]
        self.assertEqual(rules["agent"]["rule"], "agent-pattern")
        self.assertEqual(rules["bot"]["rule"], "bot-pattern")

    def test_hotspots_exclude_classes_and_human_only(self):
        top_all = {r["file"]: r for r in self.data["hotspots"]["all"]["top"]}
        top_ex = {r["file"]: r for r in self.data["hotspots"]["excluding_classes"]["top"]}
        top_h = {r["file"]: r for r in self.data["hotspots"]["human_only"]["top"]}
        self.assertEqual(top_all["src/ui/u.ts"]["commits"], 5)
        self.assertEqual(top_ex["src/ui/u.ts"]["commits"], 4)
        self.assertEqual(top_h["src/api/a.ts"]["commits"], 4)

    def test_cochange_across_modules(self):
        pairs = self.data["cochange_files"]["pairs"]
        self.assertEqual(len(pairs), 1)
        p = pairs[0]
        self.assertEqual((p["a"], p["b"], p["shared"]), ("src/api/a.ts", "src/ui/u.ts", 4))
        self.assertEqual(p["ratio"], round(4 / 5, 3))
        mods = self.data["cochange_modules"]["pairs"]
        self.assertTrue(any(m["a"] == "src/api" and m["b"] == "src/ui" for m in mods))

    def test_test_gate_with_impl(self):
        tg = self.data["test_gate_with_impl"]
        subjects = [c["subject"] for c in tg["commits"]]
        self.assertIn("Fix with test", subjects)
        self.assertIn("chore(deps): bump lodash", subjects)
        self.assertIn("Add api and ui", subjects)
        self.assertNotIn("Update docs only", subjects)
        fix = next(c for c in tg["commits"] if c["subject"] == "Fix with test")
        self.assertEqual(fix["test_files"], ["test/a.test.ts"])
        self.assertEqual(fix["impl_files"], ["src/api/a.ts"])
        self.assertEqual(fix["class"], "agent")

    def test_text_format(self):
        text = run_cli(self.repo, "--format", "text").stdout
        self.assertIn("top hotspots (all", text)
        self.assertIn("classes: human=5", text)
        self.assertIn("test/gate-with-impl commits (hypothesis): 3", text)

    def test_determinism(self):
        again = run_json(self.repo, "--module-depth", "2", "--min-shared", "3")
        self.assertEqual(json.dumps(again["data"], sort_keys=True), json.dumps(self.data, sort_keys=True))

    def test_sections_subset_and_implied(self):
        data = run_json(self.repo, "--sections", "authors")["data"]
        self.assertIsNone(data["files"])
        self.assertIsNone(data["cochange_files"])
        self.assertIsNotNone(data["authors"])
        data = run_json(self.repo, "--sections", "hotspots")["data"]
        self.assertEqual(data["sections_computed"], ["churn", "complexity", "hotspots"])

    def test_range_restricts_commits(self):
        data = run_json(self.repo, "--range", "HEAD~3..HEAD")["data"]
        self.assertEqual(data["window"]["commits"], 3)
        self.assertEqual(data["window"]["range"], "HEAD~3..HEAD")

    def test_since_restricts_commits(self):
        data = run_json(self.repo, "--since", "2026-01-07")["data"]
        self.assertEqual(data["window"]["commits"], 2)

    def test_include_exclude_and_unmatched_glob_warns(self):
        out = run_json(self.repo, "--include", "src/**", "--exclude", "src/ui/**", "--include", "nothing/**")
        self.assertEqual(sorted(out["data"]["files"]), ["src/api/a.ts", "src/api/b.ts"])
        self.assertTrue(any("matched no tracked file: nothing/**" in w for w in out["warnings"]))

    def test_bulk_exclusion_reported(self):
        data = run_json(self.repo, "--bulk-threshold", "1")["data"]
        bulk = data["excluded_bulk_commits"]
        self.assertGreaterEqual(bulk["count"], 1)
        self.assertEqual(data["cochange_files"]["pairs"], [])

    def test_module_map(self):
        with tempfile.TemporaryDirectory() as t:
            mm = os.path.join(t, "m.json")
            with open(mm, "w") as fh:
                json.dump({"src/api/**": "backend", "src/ui/**": "frontend"}, fh)
            data = run_json(self.repo, "--module-map", mm)["data"]
        self.assertEqual(data["files"]["src/api/a.ts"]["module"], "backend")
        self.assertEqual(data["cochange_modules"]["pairs"][0]["a"], "backend")

    def test_max_list_truncation_warns(self):
        out = run_json(self.repo, "--max-list", "1")
        self.assertEqual(out["data"]["test_gate_with_impl"]["shown"], 1)
        self.assertEqual(out["data"]["test_gate_with_impl"]["truncated"], 2)
        self.assertTrue(any("test_gate_with_impl truncated" in w for w in out["warnings"]))

    def test_every_commit_human_warns_when_patterns_never_match(self):
        out = run_json(self.repo, "--agent-pattern", "zzzz", "--bot-pattern", "zzzz",
                       "--formatter-pattern", "zzzz", "--deps-pattern", "zzzz")
        self.assertTrue(any("every commit classified as human" in w for w in out["warnings"]))

    def test_out_file(self):
        with tempfile.TemporaryDirectory() as t:
            target = os.path.join(t, "deep", "h.json")
            proc = run_cli(self.repo, "--out", target)
            self.assertEqual(proc.stdout, "")
            with open(target, encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["tool"], "history")

    def test_help_documents_fields(self):
        text = run_cli(self.repo, "--help").stdout
        for needle in ("data fields:", "hotspots", "--bulk-threshold", "examples:", "exit codes:"):
            self.assertIn(needle, text)


class HistoryShapeTests(unittest.TestCase):
    def test_rename_aware_churn_and_deleted_files(self):
        with tempfile.TemporaryDirectory() as t:
            r = Repo(t)
            r.commit("one", {"src/a/old.ts": "const a = 1\nconst b = 2\nconst c = 3\n", "src/gone.ts": "x\n"})
            r.commit("edit", {"src/a/old.ts": "const a = 1\nconst b = 2\nconst c = 3\nconst d = 4\n"})
            r.commit("rename", rename=[("src/a/old.ts", "src/b/new.ts")])
            r.commit("edit new", {"src/b/new.ts": "const a = 1\nconst b = 2\nconst c = 3\nconst d = 5\n"})
            r.commit("remove", remove=["src/gone.ts"])
            data = run_json(t)["data"]
            self.assertEqual(list(data["files"]), ["src/b/new.ts"])
            self.assertEqual(data["files"]["src/b/new.ts"]["commits"], 4)
            self.assertEqual([d["file"] for d in data["deleted_at_head"]["files"]], ["src/gone.ts"])
            self.assertEqual(data["deleted_at_head"]["files"][0]["commits"], 2)

    def test_binary_file_skipped_for_complexity_with_warning(self):
        with tempfile.TemporaryDirectory() as t:
            r = Repo(t)
            r.commit("bin", {"src/x.ts": "if (a) {}\n"})
            with open(os.path.join(t, "src", "blob.dat"), "wb") as fh:
                fh.write(b"\0\1\2")
            r.commit("add blob")
            r.git("add", "-A")
            r.commit("blob", {})
            out = run_json(t)
            self.assertIsNone(out["data"]["files"]["src/blob.dat"]["score"])
            self.assertTrue(any("skipped for complexity (binary)" in w for w in out["warnings"]))

    def test_no_commits_in_window_warns(self):
        with tempfile.TemporaryDirectory() as t:
            r = Repo(t)
            r.commit("one", {"a.py": "x=1\n"})
            out = run_json(t, "--since", "2099-01-01")
            self.assertEqual(out["data"]["window"]["commits"], 0)
            self.assertTrue(any("no commits in the requested window" in w for w in out["warnings"]))

    def test_empty_repository_warns(self):
        with tempfile.TemporaryDirectory() as t:
            Repo(t)
            out = run_json(t)
            self.assertTrue(any("no commits" in w for w in out["warnings"]))

    def test_shallow_clone_warns(self):
        with tempfile.TemporaryDirectory() as t:
            src = os.path.join(t, "src")
            os.makedirs(src)
            r = Repo(src)
            r.commit("one", {"a.py": "x=1\n"})
            r.commit("two", {"a.py": "x=2\n"})
            clone = os.path.join(t, "clone")
            subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + src.replace("\\", "/"), clone],
                           check=True, capture_output=True)
            out = run_json(clone)
            self.assertTrue(out["data"]["window"]["shallow"])
            self.assertTrue(any("shallow clone" in w for w in out["warnings"]))


class ExitCodeTests(unittest.TestCase):
    def test_usage_errors(self):
        with tempfile.TemporaryDirectory() as t:
            Repo(t).commit("one", {"a.py": "x=1\n"})
            run_cli(t, "--sections", "bogus", expect=2)
            run_cli(t, "--exclude-classes", "nope", expect=2)
            run_cli(t, "--agent-pattern", "(", expect=2)
            run_cli(t, "--range", "notarange", expect=2)
            run_cli(t, "--range", "doesnotexist..HEAD", expect=2)
            run_cli(t, "--hotspot-pct", "150", expect=2)
            run_cli(t, "--complexity", "bogus", expect=2)

    def test_env_error_not_a_repo(self):
        with tempfile.TemporaryDirectory() as t:
            proc = run_cli(t, expect=3)
            self.assertIn("not a git repository", proc.stderr)

    def test_input_error_bad_module_map(self):
        with tempfile.TemporaryDirectory() as t:
            Repo(t).commit("one", {"a.py": "x=1\n"})
            run_cli(t, "--module-map", os.path.join(t, "missing.json"), expect=4)
            bad = os.path.join(tempfile.gettempdir(), "history_bad_map.json")
            with open(bad, "w") as fh:
                json.dump(["not", "a", "dict"], fh)
            try:
                run_cli(t, "--module-map", bad, expect=4)
            finally:
                os.remove(bad)


if __name__ == "__main__":
    unittest.main()
