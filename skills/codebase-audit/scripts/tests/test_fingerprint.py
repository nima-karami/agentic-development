import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SCRIPT = os.path.join(SCRIPTS, "fingerprint.py")
sys.path.insert(0, SCRIPTS)

PROFILE = """# Profile - x @ abc

## Identity
- What it is: a thing
- Users: devs
- Source: README.md#intro

## Load and constraints
- Concurrent users / sessions: unknown
- Network: LAN
- Source: user

## Stakes
- Sensitive data: none
- Money: <payments | none>
- Source: derived

## Dominant quality attributes
1. correctness - always
Confirmed by: unattended

## Audit plan
| Dimension | Runs? | Why |
| gates | yes | x |

## Scope
- Commit: abc
"""


def run(*args):
    return subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True, encoding="utf-8")


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_DATE="2026-01-01T00:00:00", GIT_COMMITTER_DATE="2026-01-01T00:00:00")
    return subprocess.run(["git", "-C", repo, "-c", "user.name=T", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True, env=env).stdout.strip()


class ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = cls.tmp.name
        git(cls.repo, "init", "-q")
        git(cls.repo, "commit", "-q", "--allow-empty", "-m", "one")
        cls.sha = git(cls.repo, "rev-parse", "HEAD")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def scope(self, *args):
        proc = run("scope", "--repo", self.repo, *args)
        return proc, (json.loads(proc.stdout) if proc.returncode == 0 else None)

    def test_head_resolves_and_warns(self):
        proc, env = self.scope("--commit", "HEAD", "--include", "src/**", "--exclude", "gen/**",
                               "--tool", "node=22", "--extra", "depth=standard")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        d = env["data"]
        self.assertEqual(d["scope"]["commit"], self.sha)
        self.assertTrue(d["resolved"]["was_symbolic"])
        self.assertTrue(any("resolved to" in w for w in env["warnings"]))
        self.assertEqual(len(d["fingerprint"]), 16)
        self.assertEqual(d["scope"]["tools"], {"node": "22"})

    def test_order_independent_and_deterministic(self):
        a = self.scope("--commit", self.sha, "--include", "b", "a", "--tool", "x=1", "--tool", "y=2")[1]["data"]
        b = self.scope("--commit", self.sha, "--include", "a", "--include", "b", "--include", "a",
                       "--tool", "y=2", "--tool", "x=1")[1]["data"]
        self.assertEqual(a, b)
        c = self.scope("--commit", self.sha, "--include", "a", "b", "--tool", "x=2", "--tool", "y=2")[1]["data"]
        self.assertNotEqual(a["fingerprint"], c["fingerprint"])

    def test_from_file(self):
        p = os.path.join(self.tmp.name, "scope-in.json")
        with open(p, "w") as fh:
            json.dump({"commit": self.sha, "include": ["a"], "tools": {"x": "1"}}, fh)
        _, env = self.scope("--from-file", p, "--exclude", "g")
        self.assertEqual(env["data"]["scope"]["include"], ["a"])
        self.assertEqual(env["data"]["scope"]["exclude"], ["g"])

    def test_errors(self):
        self.assertEqual(run("scope", "--repo", self.repo, "--commit", "nonexistent", "--include", "a").returncode, 3)
        self.assertEqual(run("scope", "--repo", self.repo, "--include", "a").returncode, 2)
        self.assertEqual(run("scope", "--repo", self.repo, "--commit", "HEAD", "--tool", "novalue").returncode, 2)
        self.assertEqual(run("scope", "--repo", self.repo, "--from-file", os.path.join(self.tmp.name, "missing.json")).returncode, 4)

    def test_empty_include_warns(self):
        _, env = self.scope("--commit", self.sha)
        self.assertTrue(any("include is empty" in w for w in env["warnings"]))


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def prof(self, text):
        p = os.path.join(self.tmp.name, "profile.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        proc = run("profile", p)
        return proc, json.loads(proc.stdout)

    def test_basic_and_unknown(self):
        proc, env = self.prof(PROFILE)
        d = env["data"]
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(d["complete"])
        self.assertEqual(d["unknown_fields"], [{"section": "Load and constraints", "field": "Concurrent users / sessions"}])
        self.assertEqual(d["ignored_sections"], ["Audit plan", "Scope"])
        self.assertEqual(d["placeholder_sections"], ["Stakes"])

    def test_ignored_content_does_not_change_hash(self):
        base = self.prof(PROFILE)[1]["data"]["profile_hash"]
        edited = PROFILE.replace("README.md#intro", "docs/other.md").replace("Source: user", "Source:   user, 2026-10-13")
        edited = edited.replace("| gates | yes | x |", "| gates | no | y |").replace("Commit: abc", "Commit: def")
        edited = edited.replace("Confirmed by: unattended", "Confirmed by: user, 2026-10-13")
        edited = edited.replace("- Users: devs", "-   Users:   devs  ")
        self.assertEqual(self.prof(edited)[1]["data"]["profile_hash"], base)

    def test_substantive_change_changes_hash(self):
        base = self.prof(PROFILE)[1]["data"]["profile_hash"]
        self.assertNotEqual(self.prof(PROFILE.replace("Network: LAN", "Network: mobile"))[1]["data"]["profile_hash"], base)

    def test_missing_section_warns(self):
        _, env = self.prof(PROFILE.replace("## Stakes", "## Something else"))
        self.assertFalse(env["data"]["complete"])
        self.assertEqual(env["data"]["missing_sections"], ["Stakes"])
        self.assertTrue(any("Stakes" in w for w in env["warnings"]))

    def test_missing_file_exit_4(self):
        self.assertEqual(run("profile", os.path.join(self.tmp.name, "nope.md")).returncode, 4)


class CompareTests(unittest.TestCase):
    base = {"commit": "a" * 40, "include": ["src/**"], "exclude": [], "tools": {"node": "22"}, "extra": {}}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, obj):
        p = os.path.join(self.tmp.name, name)
        with open(p, "w") as fh:
            json.dump(obj, fh)
        return p

    def compare(self, a, b, *extra):
        proc = run("compare", self.write("a.json", a), self.write("b.json", b), *extra)
        return proc, json.loads(proc.stdout)["data"]

    def test_comparable_with_new_commit(self):
        _, d = self.compare(self.base, dict(self.base, commit="b" * 40))
        self.assertTrue(d["comparable"])
        self.assertTrue(d["commit_changed"])
        self.assertEqual(d["differences"], [])

    def test_differences(self):
        b = dict(self.base, include=["src/**", "lib/**"], tools={"node": "24", "tsc": "5"}, extra={"depth": "deep"})
        proc, d = self.compare(self.base, b, "--fail-on-incomparable")
        self.assertEqual(proc.returncode, 1)
        self.assertFalse(d["comparable"])
        self.assertEqual({x["field"] for x in d["differences"]}, {"include", "tools.node", "tools.tsc", "extra.depth"})

    def test_accepts_scope_command_output(self):
        _, d = self.compare({"data": {"scope": self.base, "fingerprint": "x"}}, self.base)
        self.assertTrue(d["comparable"])

    def test_bad_input_exit_4(self):
        proc = run("compare", self.write("a.json", {"nope": 1}), self.write("b.json", self.base))
        self.assertEqual(proc.returncode, 4)


if __name__ == "__main__":
    unittest.main()
