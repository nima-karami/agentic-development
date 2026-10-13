import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SCRIPT = os.path.join(SCRIPTS, "amplify.py")
sys.path.insert(0, SCRIPTS)
import amplify  # noqa: E402
import _common as c  # noqa: E402


def run(*args):
    proc = subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr


def run_json(*args):
    code, out, err = run(*args)
    return code, (json.loads(out) if out.strip() else None), err


class PureCalcs(unittest.TestCase):
    def test_poll_rates(self):
        r = amplify.run_calc("poll", {"clients": 100000, "interval_s": 2, "budget_rps": 5000})
        self.assertEqual(r["results"]["requests_per_s"], 50000)
        self.assertEqual(r["results"]["requests_per_min"], 3000000)
        self.assertEqual(r["results"]["requests_per_day"], 4320000000)
        self.assertEqual(r["computed"], "breach")
        self.assertIn("100,000 clients x 1 req/poll / 2 s = 50,000 req/s", r["formulas"][0])

    def test_poll_requests_per_poll_and_ok(self):
        r = amplify.run_calc("poll", {"clients": 100, "interval_s": 10, "requests_per_poll": 2, "budget_rps": 100})
        self.assertEqual(r["results"]["requests_per_s"], 20)
        self.assertEqual(r["computed"], "ok")

    def test_no_budget(self):
        self.assertEqual(amplify.run_calc("poll", {"clients": 1, "interval_s": 1})["computed"], "no-budget")

    def test_broadcast_all_events(self):
        r = amplify.run_calc("broadcast", {"clients": 1000, "events_per_s": 5, "bytes_per_message": 100,
                                           "budget_msgs_per_s": 4000})
        self.assertEqual(r["results"]["messages_per_s"], 5000)
        self.assertEqual(r["results"]["egress_mbps"], 4.0)
        self.assertEqual(r["computed"], "breach")

    def test_broadcast_room(self):
        r = amplify.run_calc("broadcast", {"clients": 1000, "events_per_s": 5, "fanout": "room", "room_size": 10})
        self.assertEqual(r["results"]["messages_per_s"], 50)

    def test_broadcast_quadratic(self):
        r = amplify.run_calc("broadcast", {"clients": 1000, "per_client_actions_per_s": 1})
        self.assertEqual(r["results"]["messages_per_s"], 1000 * 999)
        self.assertAlmostEqual(r["results"]["messages_per_s_at_2x_clients"] / r["results"]["messages_per_s"], 4, 1)
        self.assertTrue(any("O(n^2)" in n for n in r["notes"]))

    def test_broadcast_room_linear(self):
        r = amplify.run_calc("broadcast", {"clients": 1000, "per_client_actions_per_s": 1, "fanout": "room",
                                           "room_size": 11})
        self.assertEqual(r["results"]["messages_per_s"], 10000)
        self.assertEqual(r["results"]["messages_per_s_at_2x_clients"], 20000)

    def test_broadcast_errors(self):
        for args in ({"clients": 10}, {"clients": 10, "events_per_s": 1, "fanout": "room"},
                     {"clients": 10, "events_per_s": 1, "room_size": 5},
                     {"clients": 10, "events_per_s": 1, "budget_egress_mbps": 5}):
            with self.assertRaises(c.UsageError):
                amplify.run_calc("broadcast", args)

    def test_pool_little_and_limits(self):
        r = amplify.run_calc("pool", {"rate_rps": 2000, "latency_ms": 50, "pool_size": 20, "instances": 10,
                                      "db_max_connections": 100})
        self.assertEqual(r["results"]["concurrency"], 100)
        self.assertEqual(r["results"]["pool_utilisation"], 0.5)
        self.assertEqual(r["results"]["total_connections_possible"], 200)
        self.assertEqual(r["computed"], "breach")

    def test_pool_saturated(self):
        r = amplify.run_calc("pool", {"rate_rps": 1000, "latency_ms": 100, "pool_size": 50})
        self.assertEqual(r["results"]["pool_utilisation"], 2)
        self.assertEqual(r["computed"], "breach")

    def test_pool_without_size(self):
        r = amplify.run_calc("pool", {"rate_rps": 100, "latency_ms": 10, "db_max_connections": 5})
        self.assertEqual(r["results"]["connections_needed_at_least"], 1)
        self.assertEqual(r["computed"], "ok")

    def test_memory(self):
        r = amplify.run_calc("memory", {"connections": 1024, "bytes_per_connection": 1048576, "budget_mb": 512})
        self.assertEqual(r["results"]["total_mib"], 1024)
        self.assertEqual(r["computed"], "breach")

    def test_memory_requires_measurement(self):
        with self.assertRaises(c.UsageError) as ctx:
            amplify.run_calc("memory", {"connections": 10})
        self.assertIn("profiled measurement", str(ctx.exception))

    def test_fanout(self):
        r = amplify.run_calc("fanout", {"rate_rps": 500, "calls_per_request": 8, "serial_depth": 4, "rtt_ms": 40,
                                        "budget_downstream_rps": 5000, "budget_latency_ms": 100})
        self.assertEqual(r["results"]["downstream_rps"], 4000)
        self.assertEqual(r["results"]["serial_latency_floor_ms"], 160)
        statuses = {k["name"]: k["status"] for k in r["checks"]}
        self.assertEqual(statuses, {"downstream_rps": "ok", "serial_latency_floor_ms": "breach"})

    def test_fanout_incomplete_serial(self):
        with self.assertRaises(c.UsageError):
            amplify.run_calc("fanout", {"rate_rps": 1, "calls_per_request": 1, "serial_depth": 2})
        with self.assertRaises(c.UsageError):
            amplify.run_calc("fanout", {"rate_rps": 1, "calls_per_request": 1, "budget_latency_ms": 5})

    def test_validation(self):
        for bad in (0, -3, float("inf"), "x", True):
            with self.assertRaises(c.UsageError):
                amplify.run_calc("poll", {"clients": bad, "interval_s": 1})

    def test_unknown_calc_and_arg(self):
        with self.assertRaises(c.UsageError):
            amplify.run_calc("nope", {})
        with self.assertRaises(c.UsageError):
            amplify.run_calc("poll", {"clients": 1, "interval_s": 1, "bogus": 2})

    def test_dashed_keys_accepted(self):
        self.assertEqual(amplify.run_calc("poll", {"clients": 10, "interval-s": 5})["results"]["requests_per_s"], 2)


class Cli(unittest.TestCase):
    def test_poll_json(self):
        code, doc, _ = run_json("poll", "--clients", "100000", "--interval-s", "2", "--budget-rps", "5000")
        self.assertEqual(code, 0)
        self.assertEqual(doc["tool"], "amplify")
        self.assertEqual(doc["data"]["computed"], "breach")
        self.assertEqual(doc["data"]["inputs"]["clients"], 100000)

    def test_text_prints_formula(self):
        code, out, _ = run("poll", "--clients", "10", "--interval-s", "5", "--format", "text")
        self.assertEqual(code, 0)
        self.assertIn("10 clients x 1 req/poll / 5 s = 2 req/s", out)

    def test_memory_missing_exit_2(self):
        code, _, err = run("memory", "--connections", "100")
        self.assertEqual(code, 2)
        self.assertIn("never a guess", err)

    def test_negative_exit_2(self):
        code, _, err = run("poll", "--clients", "-5", "--interval-s", "1")
        self.assertEqual(code, 2)
        self.assertIn("hint:", err)

    def test_missing_required_exit_2(self):
        self.assertEqual(run("poll", "--clients", "5")[0], 2)

    def test_help_documents(self):
        code, out, _ = run("--help")
        self.assertEqual(code, 0)
        for name in ("poll", "broadcast", "pool", "memory", "fanout", "batch"):
            self.assertIn(name, out)
        self.assertIn("computed", run("pool", "--help")[1])

    def test_deterministic(self):
        a = run_json("pool", "--rate-rps", "10", "--latency-ms", "20", "--pool-size", "5")[1]["data"]
        b = run_json("pool", "--rate-rps", "10", "--latency-ms", "20", "--pool-size", "5")[1]["data"]
        self.assertEqual(a, b)


class Batch(unittest.TestCase):
    def write(self, tmp, payload):
        path = os.path.join(tmp, "scenarios.json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(payload if isinstance(payload, str) else json.dumps(payload))
        return path

    def test_batch_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, [
                {"calc": "poll", "args": {"clients": 100000, "interval_s": 2, "budget_rps": 5000}, "label": "poll"},
                {"calc": "memory", "args": {"connections": 10, "bytes_per_connection": 1000}, "label": "mem"}])
            code, doc, _ = run_json("batch", "--file", path)
        self.assertEqual(code, 0)
        self.assertEqual(doc["data"]["summary"], {"breach": 1, "ok": 0, "no-budget": 1, "error": 0})
        self.assertEqual([r["label"] for r in doc["data"]["results"]], ["poll", "mem"])

    def test_batch_error_item_exit_2_but_all_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, [{"calc": "memory", "args": {"connections": 10}, "label": "bad"},
                                    {"calc": "poll", "args": {"clients": 1, "interval_s": 1}}])
            code, doc, err = run_json("batch", "--file", path)
        self.assertEqual(code, 2)
        self.assertEqual(doc["data"]["summary"]["error"], 1)
        self.assertIn("error", doc["data"]["results"][0])
        self.assertEqual(doc["data"]["results"][1]["computed"], "no-budget")
        self.assertIn("scenario 0", doc["warnings"][0])

    def test_batch_bad_shape_exit_4(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run("batch", "--file", self.write(tmp, {"calc": "poll"}))[0], 4)
            self.assertEqual(run("batch", "--file", self.write(tmp, "not json"))[0], 4)
            self.assertEqual(run("batch", "--file", os.path.join(tmp, "missing.json"))[0], 4)

    def test_batch_text_and_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(tmp, [{"calc": "poll", "args": {"clients": 1, "interval_s": 1}, "label": "x"}])
            out = os.path.join(tmp, "o", "r.json")
            code, text, _ = run("batch", "--file", path, "--format", "text", "--out", out)
            self.assertEqual(code, 0)
            self.assertIn("[x] poll", text)
            self.assertTrue(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()
