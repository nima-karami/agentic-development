import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SCRIPT = os.path.join(SCRIPTS, "isolate.py")
sys.path.insert(0, SCRIPTS)
import isolate as iso  # noqa: E402


def run(*args):
    return subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True, encoding="utf-8")


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_DATE="2026-01-01T00:00:00", GIT_COMMITTER_DATE="2026-01-01T00:00:00")
    return subprocess.run(["git", "-C", repo, "-c", "user.name=T", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True, env=env).stdout.strip()


class IsolateCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.cleanup)
        root = os.path.realpath(self.tmp.name)
        self.repo = os.path.join(root, "repo with space")
        self.dest = os.path.join(root, "audit wt")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q")
        with open(os.path.join(self.repo, "a.txt"), "w") as fh:
            fh.write("one\n")
        with open(os.path.join(self.repo, ".gitignore"), "w") as fh:
            fh.write("node_modules/\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "one")
        self.sha1 = git(self.repo, "rev-parse", "HEAD")
        with open(os.path.join(self.repo, "a.txt"), "w") as fh:
            fh.write("two\n")
        git(self.repo, "commit", "-q", "-am", "two")
        self.deps = os.path.join(self.repo, "node_modules")
        os.makedirs(os.path.join(self.deps, "pkg"))
        with open(os.path.join(self.deps, "pkg", "index.js"), "w") as fh:
            fh.write("x\n")

    def cleanup(self):
        if os.path.exists(os.path.join(self.dest, iso.MARKER_NAME)):
            run("remove", "--dest", self.dest)
        self.tmp.cleanup()

    def create(self, *extra, commit=None):
        return run("create", "--repo", self.repo, "--commit", commit or self.sha1, "--dest", self.dest, *extra)

    def require_links(self):
        proc = self.create("--link", "node_modules")
        if proc.returncode != 0:
            self.skipTest(f"this OS refused to create links: {proc.stderr.strip()}")
        return json.loads(proc.stdout)


class CreateTests(IsolateCase):
    def test_create_checks_out_pinned_commit_and_links(self):
        env = self.require_links()
        d = env["data"]
        self.assertEqual(d["sha"], self.sha1)
        self.assertEqual(d["worktree_head"], self.sha1)
        self.assertTrue(d["source_unchanged"])
        with open(os.path.join(self.dest, "a.txt")) as fh:
            self.assertEqual(fh.read().strip(), "one")
        link = os.path.join(self.dest, "node_modules")
        self.assertTrue(iso.is_link(link))
        self.assertTrue(os.path.isfile(os.path.join(link, "pkg", "index.js")))
        with open(os.path.join(self.dest, iso.MARKER_NAME), encoding="utf-8") as fh:
            marker = json.load(fh)
        self.assertEqual(marker["sha"], self.sha1)
        self.assertEqual(marker["links"][0]["name"], "node_modules")
        self.assertIn("created_at", marker)

    def test_dry_run_does_nothing(self):
        proc = self.create("--link", "node_modules", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dry-run:", proc.stderr)
        self.assertFalse(os.path.exists(self.dest))
        self.assertTrue(json.loads(proc.stdout)["data"]["dry_run"])

    def test_refuses_non_empty_dest(self):
        os.makedirs(self.dest)
        with open(os.path.join(self.dest, "x"), "w") as fh:
            fh.write("x")
        self.assertEqual(self.create().returncode, 4)
        self.assertTrue(os.path.exists(os.path.join(self.dest, "x")))

    def test_accepts_empty_existing_dest(self):
        os.makedirs(self.dest)
        proc = self.create()
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_refuses_dest_inside_repo(self):
        proc = run("create", "--repo", self.repo, "--commit", self.sha1, "--dest", os.path.join(self.repo, "wt"))
        self.assertEqual(proc.returncode, 4)
        self.assertIn("inside the audited working tree", proc.stderr)

    def test_refuses_dest_containing_repo(self):
        proc = run("create", "--repo", self.repo, "--commit", self.sha1, "--dest", os.path.dirname(self.repo))
        self.assertEqual(proc.returncode, 4)

    def test_refuses_missing_link_target(self):
        proc = self.create("--link", ".venv")
        self.assertEqual(proc.returncode, 4)
        self.assertFalse(os.path.exists(self.dest))

    def test_refuses_bad_link_names(self):
        self.assertEqual(self.create("--link", "../x").returncode, 4)
        self.assertEqual(self.create("--link", ".git").returncode, 4)

    def test_refuses_tracked_link_name(self):
        os.makedirs(os.path.join(self.repo, "tracked_dir"))
        with open(os.path.join(self.repo, "tracked_dir", "f"), "w") as fh:
            fh.write("x")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "three")
        proc = self.create("--link", "tracked_dir", commit="HEAD")
        self.assertEqual(proc.returncode, 4)
        self.assertIn("tracked", proc.stderr)

    def test_unresolvable_commit_exit_3(self):
        self.assertEqual(self.create(commit="nonexistent").returncode, 3)

    def test_not_a_repo_exit_3(self):
        with tempfile.TemporaryDirectory() as d:
            proc = run("create", "--repo", d, "--commit", "HEAD", "--dest", os.path.join(d, "wt"))
            self.assertEqual(proc.returncode, 3)

    def test_usage_exit_2(self):
        self.assertEqual(run("create", "--repo", self.repo).returncode, 2)

    def test_source_status_unchanged(self):
        before = git(self.repo, "status", "--porcelain")
        self.require_links()
        self.assertEqual(git(self.repo, "status", "--porcelain"), before)


class StatusAndRemoveTests(IsolateCase):
    def test_status_reports_links_and_clean_source(self):
        self.require_links()
        proc = run("status", "--dest", self.dest)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        d = json.loads(proc.stdout)["data"]
        self.assertTrue(d["head_matches_marker"])
        self.assertTrue(d["links_intact"])
        self.assertTrue(d["registered_worktree"])
        self.assertEqual(d["dirty_files"], [])
        self.assertTrue(d["source_clean"])
        self.assertTrue(d["links"][0]["is_link"])

    def test_status_flags_dirty_and_real_directory(self):
        self.require_links()
        with open(os.path.join(self.dest, "a.txt"), "w") as fh:
            fh.write("edited\n")
        iso.unlink_link(os.path.join(self.dest, "node_modules"))
        os.makedirs(os.path.join(self.dest, "node_modules"))
        env = json.loads(run("status", "--dest", self.dest).stdout)
        self.assertEqual(len(env["data"]["dirty_files"]), 1)
        self.assertFalse(env["data"]["links_intact"])
        self.assertTrue(env["data"]["links"][0]["is_real_directory"])
        self.assertTrue(any("real directory" in w for w in env["warnings"]))
        os.rmdir(os.path.join(self.dest, "node_modules"))

    def test_remove_leaves_target_intact(self):
        self.require_links()
        proc = run("remove", "--dest", self.dest)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        d = json.loads(proc.stdout)["data"]
        self.assertTrue(d["removed"])
        self.assertTrue(d["source_unchanged"])
        self.assertEqual(d["links_unlinked"][0]["name"], "node_modules")
        self.assertTrue(d["links_unlinked"][0]["target_intact"])
        self.assertFalse(os.path.exists(self.dest))
        self.assertTrue(os.path.isfile(os.path.join(self.deps, "pkg", "index.js")))
        self.assertNotIn(self.dest.replace("\\", "/"), git(self.repo, "worktree", "list").replace("\\", "/"))

    def test_remove_unlinks_unrecorded_nested_link(self):
        self.require_links()
        extra = os.path.join(self.tmp.name, "other-deps")
        os.makedirs(extra)
        with open(os.path.join(extra, "keep.txt"), "w") as fh:
            fh.write("k")
        nested = os.path.join(self.dest, "sub")
        os.makedirs(nested)
        iso.create_link(os.path.join(nested, "deps"), extra)
        proc = run("remove", "--dest", self.dest)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.isfile(os.path.join(extra, "keep.txt")))
        self.assertTrue(any("not in the marker" in w for w in json.loads(proc.stdout)["warnings"]))

    def test_remove_dry_run(self):
        self.require_links()
        proc = run("remove", "--dest", self.dest, "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dry-run: unlink", proc.stderr)
        self.assertTrue(iso.is_link(os.path.join(self.dest, "node_modules")))

    def test_remove_refuses_without_marker(self):
        os.makedirs(self.dest)
        with open(os.path.join(self.dest, "precious.txt"), "w") as fh:
            fh.write("keep")
        proc = run("remove", "--dest", self.dest)
        self.assertEqual(proc.returncode, 4)
        self.assertTrue(os.path.exists(os.path.join(self.dest, "precious.txt")))

    def test_remove_refuses_missing_dest(self):
        self.assertEqual(run("remove", "--dest", os.path.join(self.tmp.name, "nope")).returncode, 4)

    def test_status_refuses_without_marker(self):
        os.makedirs(self.dest)
        self.assertEqual(run("status", "--dest", self.dest).returncode, 4)

    def test_unlink_refuses_real_directory(self):
        real = os.path.join(self.tmp.name, "realdir")
        os.makedirs(real)
        with open(os.path.join(real, "f"), "w") as fh:
            fh.write("x")
        with self.assertRaises(iso.c.EnvError):
            iso.unlink_link(real)
        self.assertTrue(os.path.isfile(os.path.join(real, "f")))


if __name__ == "__main__":
    unittest.main()
