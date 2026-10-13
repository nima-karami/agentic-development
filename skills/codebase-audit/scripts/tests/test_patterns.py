import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS)
import _common as c  # noqa: E402
import patterns as pt  # noqa: E402

SCRIPT = os.path.join(SCRIPTS, "patterns.py")

HEAD_DATE = "2026-06-01T12:00:00+0000"
OLD_DATE = "2024-01-10T12:00:00+0000"
MID_DATE = "2026-04-01T12:00:00+0000"


def git(repo, *args, date=HEAD_DATE):
    env = dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date,
               GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, env=env)


def write(repo, rel, content, mode="w"):
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if "b" in mode:
        with open(path, mode) as fh:
            fh.write(content)
    else:
        with open(path, mode, encoding="utf-8", newline="\n") as fh:
            fh.write(content)


def commit(repo, message, date):
    git(repo, "add", "-A", date=date)
    git(repo, "commit", "-m", message, date=date)


def make_repo(root):
    repo = os.path.join(root, "my repo")
    os.makedirs(repo)
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Tester")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "core.autocrlf", "false")
    write(repo, "src/old.ts", "export const a = 1;\n// @ts-ignore\nconst x: any = 1;\n")
    commit(repo, "old", OLD_DATE)
    write(repo, "src/mid.ts", "const y = z as Foo;\nconst w = q as unknown as Bar;\n// biome-ignore lint: reason\n")
    write(repo, "src/ingest.ts", "line1\nconst v = JSON.parse(s) as any;\nconst k = r as any;\n")
    commit(repo, "mid", MID_DATE)
    write(repo, "src/new.ts", "// eslint-disable-next-line\nconst n = u!.name;\n")
    write(repo, "test/a.test.ts", "// @ts-ignore\nit.skip('x', () => {});\nit.only('y', () => {});\n")
    write(repo, ".github/workflows/ci.yml", "jobs:\n  a:\n    steps:\n      - run: lint || true\n        continue-on-error: true\n")
    write(repo, "bin/blob.dat", b"\x00\x01@ts-ignore\x00", mode="wb")
    commit(repo, "head", HEAD_DATE)
    return repo


def run_cli(*args, cwd=None):
    proc = subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True,
                          encoding="utf-8", cwd=cwd)
    return proc


def scan_json(repo, *args):
    proc = run_cli("scan", "--repo", repo, *args)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


class PackValidation(unittest.TestCase):
    def base(self, **patch):
        pat = {"id": "p1", "category": "k", "regex": "x", "description": "d"}
        pat.update(patch)
        return {"name": "n", "description": "d", "version": "1", "patterns": [pat]}

    def test_valid_pack_loads(self):
        pack = pt.validate_pack(self.base(), "mem")
        self.assertEqual(pack.patterns[0].id, "p1")
        self.assertIsNotNone(pack.patterns[0].compiled)

    def test_missing_regex_names_location(self):
        obj = self.base()
        del obj["patterns"][0]["regex"]
        with self.assertRaises(c.InputError) as ctx:
            pt.validate_pack(obj, "mem")
        self.assertIn("patterns[0] (id 'p1')", str(ctx.exception))
        self.assertIn("'regex'", str(ctx.exception))
        self.assertTrue(ctx.exception.hint)

    def test_unknown_key_rejected(self):
        with self.assertRaises(c.InputError) as ctx:
            pt.validate_pack(self.base(extension=[".ts"]), "mem")
        self.assertIn("unknown key", str(ctx.exception))

    def test_bad_flags_and_duplicates(self):
        with self.assertRaises(c.InputError):
            pt.validate_pack(self.base(flags="x"), "mem")
        obj = self.base()
        obj["patterns"].append(dict(obj["patterns"][0]))
        with self.assertRaises(c.InputError) as ctx:
            pt.validate_pack(obj, "mem")
        self.assertIn("duplicate", str(ctx.exception))

    def test_bad_regex_is_recorded_not_raised(self):
        pack = pt.validate_pack(self.base(regex="("), "mem")
        self.assertIsNone(pack.patterns[0].compiled)
        self.assertTrue(pack.patterns[0].error)

    def test_not_an_object(self):
        with self.assertRaises(c.InputError):
            pt.validate_pack([], "mem")


class ShippedPacks(unittest.TestCase):
    SAMPLES = {
        "suppress-biome-ignore": ("a.ts", "// biome-ignore lint/x: why"),
        "suppress-ts-ignore": ("a.ts", "// @ts-ignore"),
        "suppress-ts-expect-error": ("a.ts", "// @ts-expect-error"),
        "suppress-ts-nocheck": ("a.ts", "// @ts-nocheck"),
        "suppress-eslint-disable": ("a.ts", "/* eslint-disable no-console */"),
        "suppress-noqa": ("a.py", "x = 1  # noqa: E501"),
        "suppress-type-ignore": ("a.py", "x = 1  # type: ignore[attr]"),
        "suppress-pylint-disable": ("a.py", "# pylint: disable=unused-import"),
        "suppress-nolint": ("a.go", "x := 1 //nolint:errcheck"),
        "suppress-nosonar": ("A.java", "int a; // NOSONAR"),
        "suppress-suppresswarnings": ("A.java", '@SuppressWarnings("unchecked")'),
        "suppress-rust-allow": ("a.rs", "#[allow(dead_code)]"),
        "suppress-istanbul-ignore": ("a.js", "/* istanbul ignore next */"),
        "suppress-c8-ignore": ("a.js", "/* c8 ignore start */"),
        "skip-js-skip": ("a.ts", "describe.skip('x', () => {})"),
        "skip-js-x": ("a.ts", "xit('x', () => {})"),
        "skip-js-todo": ("a.ts", "it.todo('x')"),
        "skip-js-only": ("a.ts", "it.only('x', () => {})"),
        "skip-java-disabled": ("A.java", "@Disabled"),
        "skip-java-ignore": ("A.java", "@Ignore"),
        "skip-pytest-mark": ("a.py", "@pytest.mark.xfail"),
        "skip-unittest": ("a.py", "@unittest.skip('r')"),
        "skip-go-skip": ("a.go", "t.Skip(\"no\")"),
        "skip-rust-ignore": ("a.rs", "#[ignore]"),
        "ts-any-annotation": ("a.ts", "let x: any = 1;"),
        "ts-as-any": ("a.ts", "const x = y as any;"),
        "ts-any-generic": ("a.ts", "const x: Array<any> = [];"),
        "ts-as-unknown-as": ("a.ts", "const x = y as unknown as Foo;"),
        "ts-as-cast": ("a.ts", "const x = y as Foo;"),
        "ts-non-null-member": ("a.ts", "const x = y!.z;"),
        "ts-non-null-other": ("a.ts", "f(y!);"),
        "py-cast": ("a.py", "x = cast(int, y)"),
        "py-type-ignore": ("a.py", "x = 1  # type: ignore"),
        "rust-unwrap": ("a.rs", "let x = y.unwrap();"),
        "rust-expect": ("a.rs", 'let x = y.expect("boom");'),
        "go-empty-interface": ("a.go", "var x interface{}"),
        "flag-reject-unauthorized": ("a.ts", "{ rejectUnauthorized: false }"),
        "flag-verify-false": ("a.py", "requests.get(u, verify=False)"),
        "flag-insecure-skip-verify": ("a.go", "InsecureSkipVerify: true,"),
        "flag-node-tls-env": ("a.sh", "NODE_TLS_REJECT_UNAUTHORIZED=0 node x"),
        "flag-cors-wildcard": ("a.ts", "res.setHeader('Access-Control-Allow-Origin', '*')"),
        "flag-node-integration": ("a.ts", "nodeIntegration: true"),
        "flag-context-isolation-off": ("a.ts", "contextIsolation: false"),
        "flag-sandbox-off": ("a.ts", "sandbox: false"),
        "flag-web-security-off": ("a.ts", "webSecurity: false"),
        "flag-insecure-content": ("a.ts", "allowRunningInsecureContent: true"),
        "flag-csrf-off": ("a.ts", "CSRF: false"),
        "flag-csrf-exempt": ("a.py", "@csrf_exempt"),
        "flag-debug-true": ("a.py", "DEBUG = True"),
        "flag-shell-true": ("a.py", "subprocess.run(c, shell=True)"),
        "flag-eval": ("a.ts", "const r = eval(code);"),
        "flag-no-verify": ("a.sh", "git commit --no-verify"),
        "policy-continue-on-error": ("a.yml", "continue-on-error: true"),
        "policy-allow-failure": ("a.yml", "allow_failure: true"),
        "policy-or-true": ("a.sh", "npm test || true"),
        "policy-max-warnings": ("a.json", '"lint": "eslint . --max-warnings 50"'),
        "policy-pass-with-no-tests": ("a.json", '"test": "jest --passWithNoTests"'),
        "policy-exit-zero": ("a.sh", "eslint . --exit-zero"),
        "policy-retries": ("a.yml", "retries: 2"),
        "timer-set-interval": ("a.ts", "setInterval(() => tick(), 1000);"),
        "timer-constructor": ("a.py", "t = Timer(5, f)"),
        "timer-scheduled-annotation": ("A.java", "@Scheduled(fixedRate = 1000)"),
        "timer-py-schedule": ("a.py", "schedule.every(5).seconds.do(job)"),
        "timer-node-cron": ("a.ts", "cron.schedule('* * * * *', f)"),
        "timer-go-ticker": ("a.go", "t := time.NewTicker(time.Second)"),
        "timer-while-true": ("a.py", "    while True:"),
        "timer-while-true-c-like": ("a.ts", "while (true) {"),
        "timer-go-for-loop": ("a.go", "\tfor {"),
        "timer-rust-loop": ("a.rs", "    loop {"),
        "sync-node-fs": ("a.ts", "const s = readFileSync(p, 'utf8');"),
        "sync-node-process": ("a.ts", "execSync('ls');"),
        "sync-node-crypto-zlib": ("a.ts", "const k = pbkdf2Sync(a, b, 1, 2, 'x');"),
        "sync-py-requests-no-timeout": ("a.py", "r = requests.get(url)"),
        "sync-py-time-sleep": ("a.py", "time.sleep(1)"),
        "sync-java-thread-sleep": ("A.java", "Thread.sleep(100);"),
    }
    NEGATIVES = [
        ("ts-as-cast", "a.ts", "const x = y as const;"),
        ("ts-as-cast", "a.ts", "import { a as B } from './a';"),
        ("ts-as-cast", "a.ts", "  foo as Bar,"),
        ("ts-as-cast", "a.ts", "const x = y as unknown as Foo;" ),
        ("ts-as-cast", "a.ts", "// cast it as Foo"),
        ("ts-as-cast", "a.ts", "const s = 'as Foo';"),
        ("ts-non-null-other", "a.ts", "if (a !== b) {}"),
        ("ts-non-null-other", "a.ts", "if (!ok) return;"),
        ("ts-any-annotation", "a.ts", "const company: anyCompany = 1;"),
        ("flag-eval", "a.ts", "page.eval(x)"),
        ("py-cast", "a.py", "t.cast(x)"),
        ("rust-unwrap", "a.rs", 'let s = "x.unwrap()";'),
        ("sync-py-requests-no-timeout", "a.py", "r = requests.get(url, timeout=5)"),
        ("policy-or-true", "a.sh", "echo trueish"),
        ("skip-js-skip", "a.ts", "const skip = true;"),
    ]

    def test_every_shipped_pattern_has_description_and_sample(self):
        covered = set()
        for name in pt.shipped_pack_names():
            pack = pt.load_pack(name)
            for pattern in pack.patterns:
                self.assertTrue(pattern.description, pattern.id)
                self.assertIsNone(pattern.error, pattern.id)
                self.assertIn(pattern.id, self.SAMPLES, f"no positive sample for {pattern.id}")
                covered.add(pattern.id)
        self.assertEqual(covered, set(self.SAMPLES))

    def test_positive_samples_hit_their_pattern(self):
        everything = [p for n in pt.shipped_pack_names() for p in pt.load_pack(n).patterns]
        for pid, (path, line) in self.SAMPLES.items():
            hits = pt.scan_text(path, line + "\n", everything)
            self.assertIn(pid, {h.pattern for h in hits}, f"{pid} did not match {line!r}")

    def test_negative_samples_do_not_hit(self):
        everything = [p for n in pt.shipped_pack_names() for p in pt.load_pack(n).patterns]
        for pid, path, line in self.NEGATIVES:
            hits = pt.scan_text(path, line + "\n", everything)
            self.assertNotIn(pid, {h.pattern for h in hits}, f"{pid} wrongly matched {line!r}")

    def test_unique_ids_across_shipped_packs(self):
        ids = [p.id for n in pt.shipped_pack_names() for p in pt.load_pack(n).patterns]
        self.assertEqual(len(ids), len(set(ids)))


class PureFunctions(unittest.TestCase):
    def test_code_view_blanks_strings_and_comments(self):
        self.assertEqual(pt.code_view("a = 'x as any' // y as any", False), "a = '' ")
        self.assertEqual(pt.code_view("a = 1 # cast(x)", True), "a = 1 ")
        self.assertEqual(pt.code_view(" * as any", False), "")

    def test_extension_matching(self):
        self.assertTrue(pt.extension_matches("a/b.d.ts", [".ts"]))
        self.assertTrue(pt.extension_matches("a/Makefile", ["Makefile"]))
        self.assertFalse(pt.extension_matches("a/b.tsx.bak", [".ts", ".tsx"]))
        self.assertTrue(pt.extension_matches("a/b.anything", []))

    def test_age_bucket_edges(self):
        self.assertEqual([pt.age_bucket(d) for d in (0, 29, 30, 89, 90, 364, 365)],
                         ["<30d", "<30d", "30-90d", "30-90d", "90-365d", "90-365d", ">365d"])

    def test_lower_median(self):
        self.assertIsNone(pt.lower_median([]))
        self.assertEqual(pt.lower_median([5, 1, 9, 3]), 3)

    def test_parse_focus_text_and_json(self):
        entries = pt.parse_focus("# c\nsrc/a.ts\nsrc/b.ts:10-20\nsrc/c.ts:5\n", "f")
        self.assertEqual([(e.path, e.start, e.end) for e in entries],
                         [("src/a.ts", None, None), ("src/b.ts", 10, 20), ("src/c.ts", 5, 5)])
        entries = pt.parse_focus('["a.ts:1-2", {"path": "b.ts", "start": 3, "end": 4}]', "f")
        self.assertEqual([(e.path, e.start, e.end) for e in entries], [("a.ts", 1, 2), ("b.ts", 3, 4)])
        self.assertTrue(pt.focus_contains(entries, "a.ts", 2))
        self.assertFalse(pt.focus_contains(entries, "a.ts", 3))

    def test_parse_focus_errors(self):
        for bad in ("", "a.ts:9-2", "[1]", "[not json"):
            with self.assertRaises(c.InputError):
                pt.parse_focus(bad, "f")

    def test_parse_blame_porcelain(self):
        sha = "a" * 40
        out = f"{sha} 3 7 1\nauthor x\nauthor-time 1000\nsummary s\n\tcode\n"
        self.assertEqual(pt.parse_blame_porcelain(out), {7: (sha, 1000)})

    def test_line_ranges_merge(self):
        self.assertEqual(pt._line_ranges([5, 1, 2, 3, 9, 9]), [(1, 3), (5, 5), (9, 9)])

    def test_scan_text_exclude_regex_and_multiple_matches(self):
        pack = pt.validate_pack({"name": "n", "description": "d", "version": 1, "patterns": [
            {"id": "p", "category": "k", "regex": "foo", "description": "d", "exclude_regex": "ok"}]}, "m")
        hits = pt.scan_text("a.txt", "foo foo\nfoo ok\n", pack.patterns)
        self.assertEqual([(h.line, h.text) for h in hits], [(1, "foo"), (1, "foo")])


class CliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = make_repo(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_default_excludes_tests_and_reports_them_separately(self):
        out = scan_json(self.repo, "--pack", "suppressions", "--pack", "skips")
        data = out["data"]
        self.assertEqual(data["totals"]["by_pattern"]["suppress-ts-ignore"]["count"], 1)
        self.assertEqual(data["tests"]["by_pattern"]["suppress-ts-ignore"], 1)
        self.assertEqual(data["tests"]["by_pattern"]["skip-js-skip"], 1)
        self.assertFalse(data["tests"]["counted_in_totals"])
        self.assertTrue(all("test/" not in h["path"] for h in data["hits"]))
        self.assertTrue(any("targets test files" in w for w in out["warnings"]))

    def test_tests_include_and_only(self):
        inc = scan_json(self.repo, "--pack", "suppressions", "--tests", "include")["data"]
        self.assertEqual(inc["totals"]["by_pattern"]["suppress-ts-ignore"]["count"], 2)
        only = scan_json(self.repo, "--pack", "skips", "--tests", "only")["data"]
        self.assertEqual(only["totals"]["total"], 3 - 1)
        self.assertEqual({h["path"] for h in only["hits"]}, {"test/a.test.ts"})

    def test_binary_skipped_with_warning(self):
        out = scan_json(self.repo, "--pack", "suppressions")
        self.assertIn("binary", out["data"]["files_skipped"])
        self.assertTrue(any("skipped (binary)" in w for w in out["warnings"]))

    def test_blame_ages_relative_to_head(self):
        out = scan_json(self.repo, "--pack", "suppressions", "--pack", "escape-hatches", "--blame")
        data = out["data"]
        hit = next(h for h in data["hits"] if h["path"] == "src/old.ts" and h["pattern"] == "suppress-ts-ignore")
        self.assertEqual(hit["blame"]["bucket"], ">365d")
        self.assertEqual(hit["blame"]["date"], "2024-01-10")
        new = next(h for h in data["hits"] if h["path"] == "src/new.ts")
        self.assertEqual(new["blame"]["bucket"], "<30d")
        mid = next(h for h in data["hits"] if h["path"] == "src/mid.ts" and h["pattern"] == "suppress-biome-ignore")
        self.assertEqual(mid["blame"]["bucket"], "30-90d")
        self.assertIn(">365d", data["by_age"])
        self.assertEqual(data["totals"]["by_pattern"]["suppress-ts-ignore"]["median_age_days"], mid_or_old_days())

    def test_focus_counts(self):
        focus = os.path.join(self.tmp.name, "focus.txt")
        with open(focus, "w") as fh:
            fh.write("src/ingest.ts:2-2\nsrc/missing.ts\n")
        out = scan_json(self.repo, "--pack", "escape-hatches", "--focus-file", focus)
        data = out["data"]
        self.assertEqual(data["focus"]["by_pattern"], {"ts-as-any": 1})
        self.assertEqual(data["focus"]["entries_without_files"], ["src/missing.ts"])
        self.assertTrue(any("matches no scanned file" in w for w in out["warnings"]))
        flagged = [h for h in data["hits"] if h.get("focus")]
        self.assertEqual([(h["path"], h["line"]) for h in flagged], [("src/ingest.ts", 2)])

    def test_max_hits_truncation_reported(self):
        data = scan_json(self.repo, "--pack", "escape-hatches", "--max-hits", "2")["data"]
        self.assertEqual(data["hits_shown"], 2)
        self.assertTrue(data["hits_truncated"])
        self.assertGreater(data["hits_total"], 2)
        self.assertIn("omitted", data["hits_truncated_note"])

    def test_include_exclude_and_unmatched_glob_warning(self):
        out = scan_json(self.repo, "--pack", "suppressions", "--include", "src/old.ts", "--exclude", "nothing/**")
        self.assertEqual({h["path"] for h in out["data"]["hits"]}, {"src/old.ts"})
        self.assertTrue(any("nothing/**" in w and "matched no" in w for w in out["warnings"]))

    def test_custom_pack_with_regex_error(self):
        pack = os.path.join(self.tmp.name, "custom.json")
        with open(pack, "w") as fh:
            json.dump({"name": "custom", "description": "d", "version": "2", "patterns": [
                {"id": "good", "category": "k", "regex": "JSON\\.parse", "description": "d"},
                {"id": "bad", "category": "k", "regex": "(", "description": "d"}]}, fh)
        out = scan_json(self.repo, "--pack", pack)
        self.assertEqual(out["data"]["totals"]["by_pattern"]["good"]["count"], 1)
        self.assertEqual(out["data"]["regex_errors"][0]["pattern"], "bad")
        self.assertTrue(any("does not compile" in w for w in out["warnings"]))

    def test_large_file_skipped(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            write(repo, "src/huge.ts", "// @ts-ignore\n" + "x" * (2 * 1024 * 1024 + 10))
            commit(repo, "huge", HEAD_DATE)
            out = scan_json(repo, "--pack", "suppressions")
            self.assertEqual(out["data"]["files_skipped"]["too_large"]["count"], 1)
            self.assertTrue(any("too_large" in w for w in out["warnings"]))

    def test_encoding_errors_replaced_with_count(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            write(repo, "src/latin.ts", b"// caf\xe9\n// @ts-ignore\n", mode="wb")
            commit(repo, "latin", HEAD_DATE)
            out = scan_json(repo, "--pack", "suppressions")
            self.assertEqual(out["data"]["files_with_encoding_errors"]["count"], 1)
            self.assertTrue(any(h["path"] == "src/latin.ts" for h in out["data"]["hits"]))

    def test_determinism(self):
        args = ("--pack", "suppressions", "--pack", "escape-hatches", "--blame", "--tests", "include")
        first = scan_json(self.repo, *args)["data"]
        second = scan_json(self.repo, *args)["data"]
        self.assertEqual(json.dumps(first, sort_keys=False), json.dumps(second, sort_keys=False))

    def test_text_format(self):
        proc = run_cli("scan", "--repo", self.repo, "--pack", "suppressions", "--format", "text")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("suppress-ts-ignore", proc.stdout)
        self.assertIn("top dirs", proc.stdout)

    def test_list_and_show_pack(self):
        listing = json.loads(run_cli("list-packs").stdout)["data"]["packs"]
        self.assertEqual({p["name"] for p in listing}, set(pt.shipped_pack_names()))
        self.assertTrue(all(p["patterns"] > 0 and p["description"] for p in listing))
        shown = json.loads(run_cli("show-pack", "escape-hatches").stdout)["data"]
        self.assertEqual(shown["name"], "escape-hatches")
        self.assertTrue(all("regex" in p and "description" in p for p in shown["patterns"]))

    def test_first_seen(self):
        proc = run_cli("first-seen", "--repo", self.repo, "--pack", "suppressions",
                       "--pattern-id", "suppress-ts-ignore", "--max", "5")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)["data"]
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["path"], "src/old.ts")
        self.assertEqual(data["results"][0]["introduced_by"]["subject"], "old")
        self.assertTrue(data["results"][0]["introduced_by"]["date"].startswith("2024-01-10"))

    def test_first_seen_unknown_pattern_exit_4(self):
        proc = run_cli("first-seen", "--repo", self.repo, "--pack", "suppressions", "--pattern-id", "nope")
        self.assertEqual(proc.returncode, 4)
        self.assertIn("pattern ids", proc.stderr)

    def test_exit_codes(self):
        self.assertEqual(run_cli("scan", "--repo", self.repo).returncode, 2)
        self.assertEqual(run_cli("scan", "--repo", self.repo, "--pack", "nope").returncode, 4)
        self.assertEqual(run_cli("scan", "--repo", self.repo, "--pack", "suppressions", "--group-by", "zzz").returncode, 2)
        self.assertEqual(run_cli("scan", "--repo", self.repo, "--pack", "suppressions", "--group-by", "age").returncode, 2)
        self.assertEqual(run_cli("scan", "--repo", self.tmp.name, "--pack", "suppressions").returncode, 3)
        bad_focus = os.path.join(self.tmp.name, "bad.txt")
        with open(bad_focus, "w") as fh:
            fh.write("a.ts:9-2\n")
        self.assertEqual(run_cli("scan", "--repo", self.repo, "--pack", "suppressions", "--focus-file", bad_focus).returncode, 4)
        two = run_cli("scan", "--repo", self.repo, "--pack", "suppressions", "--pack", "suppressions")
        self.assertEqual(two.returncode, 2)

    def test_duplicate_pattern_ids_across_packs_is_input_error(self):
        pack = os.path.join(self.tmp.name, "dup.json")
        with open(pack, "w") as fh:
            json.dump({"name": "dup", "description": "d", "version": 1, "patterns": [
                {"id": "suppress-ts-ignore", "category": "k", "regex": "x", "description": "d"}]}, fh)
        proc = run_cli("scan", "--repo", self.repo, "--pack", "suppressions", "--pack", pack)
        self.assertEqual(proc.returncode, 4)
        self.assertIn("suppress-ts-ignore", proc.stderr)

    def test_invalid_pack_file_message(self):
        pack = os.path.join(self.tmp.name, "broken.json")
        with open(pack, "w") as fh:
            fh.write('{"name": "x"}')
        proc = run_cli("show-pack", pack)
        self.assertEqual(proc.returncode, 4)
        self.assertIn("description", proc.stderr)
        self.assertIn("hint:", proc.stderr)

    def test_help_documents_format_and_fields(self):
        text = run_cli("scan", "--help").stdout
        for needle in ("exclude_regex", "code_only", "hits_truncated", "production code only", "--focus-file",
                       "median"):
            self.assertIn(needle, text)


def mid_or_old_days():
    import datetime as dt
    head = dt.datetime(2026, 6, 1, 12, tzinfo=dt.timezone.utc)
    old = dt.datetime(2024, 1, 10, 12, tzinfo=dt.timezone.utc)
    return (head - old).days


if __name__ == "__main__":
    unittest.main()
