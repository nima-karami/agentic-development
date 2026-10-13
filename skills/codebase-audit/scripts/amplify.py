#!/usr/bin/env python3
"""Amplification arithmetic for the performance rubric: profile numbers in, `computed` statuses out."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any, Callable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402

TOOL = "amplify"
MIB = 1024 * 1024
SECONDS_PER_DAY = 86400


def arg(name: str, help_text: str, required: bool = False, integer: bool = False,
        choices: tuple[str, ...] | None = None, default: Any = None) -> dict[str, Any]:
    return dict(name=name, help=help_text, required=required, integer=integer, choices=choices, default=default)


def n(x: float) -> str:
    """Format a number for a formula line without float noise."""
    if abs(x - round(x)) < 1e-9:
        return f"{int(round(x)):,}"
    return f"{x:,.4f}".rstrip("0").rstrip(".")


def rnd(x: float) -> float:
    return round(x, 6)


class Calc:
    """Collects inputs, formulas, results and budget checks for one calculation."""

    def __init__(self, name: str, inputs: dict[str, Any]) -> None:
        self.name = name
        self.inputs = inputs
        self.formulas: list[str] = []
        self.results: dict[str, Any] = {}
        self.units: dict[str, str] = {}
        self.checks: list[dict[str, Any]] = []
        self.notes: list[str] = []

    def result(self, key: str, value: float, unit: str, formula: str) -> float:
        self.results[key] = rnd(value)
        self.units[key] = unit
        self.formulas.append(f"{key} = {formula} = {n(value)} {unit}")
        return value

    def check(self, name: str, value: float, budget: float | None, unit: str, breach_when: str = "above") -> None:
        if budget is None:
            return
        breached = value > budget if breach_when == "above" else value < budget
        self.checks.append({"name": name, "value": rnd(value), "budget": budget, "unit": unit,
                            "status": "breach" if breached else "ok",
                            "text": f"{name}: {n(value)} {unit} vs budget {n(budget)} {unit} -> "
                                    f"{'BREACH' if breached else 'ok'}"})

    def to_dict(self) -> dict[str, Any]:
        statuses = [k["status"] for k in self.checks]
        verdict = "no-budget" if not statuses else ("breach" if "breach" in statuses else "ok")
        return {"calc": self.name, "inputs": self.inputs, "results": self.results, "units": self.units,
                "formulas": self.formulas, "checks": self.checks, "computed": verdict, "notes": self.notes}


def positive(args: dict[str, Any], key: str) -> float | None:
    value = args.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise c.UsageError(f"{key} must be a number, got {value!r}", hint="pass a plain number in the stated unit")
    if not math.isfinite(value) or value <= 0:
        raise c.UsageError(f"{key} must be a positive number, got {value}",
                           hint="use the profile's figure; zero or negative values cannot be amplified")
    return float(value)


def need(args: dict[str, Any], key: str, why: str | None = None) -> float:
    value = positive(args, key)
    if value is None:
        raise c.UsageError(f"{key} is required" + (f": {why}" if why else ""),
                           hint=f"take it from the profile or a profiled measurement; see amplify.py {{calc}} --help")
    return value


def calc_poll(a: dict[str, Any]) -> dict[str, Any]:
    clients, interval = need(a, "clients"), need(a, "interval_s")
    k = positive(a, "requests_per_poll") or 1.0
    budget = positive(a, "budget_rps")
    cl = Calc("poll", {"clients": clients, "interval_s": interval, "requests_per_poll": k, "budget_rps": budget})
    rps = cl.result("requests_per_s", clients * k / interval, "req/s",
                    f"{n(clients)} clients x {n(k)} req/poll / {n(interval)} s")
    cl.result("requests_per_min", rps * 60, "req/min", f"{n(rps)} req/s x 60")
    cl.result("requests_per_day", rps * SECONDS_PER_DAY, "req/day", f"{n(rps)} req/s x 86,400")
    cl.check("requests_per_s", rps, budget, "req/s")
    cl.notes.append("Assumes every client polls on the stated interval with no jitter; real load is this average "
                    "plus synchronized bursts after a deploy or reconnect.")
    return cl.to_dict()


def broadcast_messages(a: dict[str, Any], clients: float) -> tuple[float, float, list[str], str]:
    fanout = a.get("fanout") or "all"
    if fanout not in ("all", "room"):
        raise c.UsageError(f"fanout must be 'all' or 'room', got {fanout!r}", hint="use --fanout all|room")
    room = positive(a, "room_size")
    if fanout == "room" and room is None:
        raise c.UsageError("room_size is required when fanout is 'room'", hint="add --room-size M")
    if fanout == "all" and room is not None:
        raise c.UsageError("room_size given but fanout is 'all'", hint="use --fanout room or drop --room-size")
    recipients = clients if fanout == "all" else room
    events, per_client = positive(a, "events_per_s"), positive(a, "per_client_actions_per_s")
    if events is None and per_client is None:
        raise c.UsageError("one of events_per_s or per_client_actions_per_s is required",
                           hint="events-per-s = server-originated events; per-client-actions-per-s = each client's "
                                "actions that are relayed to the others")
    formulas, total = [], 0.0
    if events is not None:
        part = events * recipients
        total += part
        formulas.append(f"server events: {n(events)} events/s x {n(recipients)} recipients = {n(part)} msgs/s")
    if per_client is not None:
        peers = recipients - 1
        part = clients * per_client * peers
        total += part
        formulas.append(f"client relays: {n(clients)} clients x {n(per_client)} actions/s x {n(peers)} peers "
                        f"= {n(part)} msgs/s")
    return total, recipients, formulas, fanout


def calc_broadcast(a: dict[str, Any]) -> dict[str, Any]:
    clients = need(a, "clients")
    size = positive(a, "bytes_per_message")
    b_msgs, b_mbps = positive(a, "budget_msgs_per_s"), positive(a, "budget_egress_mbps")
    if b_mbps is not None and size is None:
        raise c.UsageError("bytes_per_message is required to check an egress budget",
                           hint="message size must come from the profile or a sampled payload, never a guess")
    total, recipients, parts, fanout = broadcast_messages(a, clients)
    cl = Calc("broadcast", {k: a.get(k) for k in (
        "clients", "events_per_s", "per_client_actions_per_s", "fanout", "room_size", "bytes_per_message",
        "budget_msgs_per_s", "budget_egress_mbps")} | {"fanout": fanout})
    cl.formulas.extend(parts)
    cl.results["messages_per_s"] = rnd(total)
    cl.units["messages_per_s"] = "msgs/s"
    cl.formulas.append(f"messages_per_s = {n(total)} msgs/s")
    if size is not None:
        mbps = total * size * 8 / 1e6
        cl.result("egress_mbps", mbps, "Mbit/s", f"{n(total)} msgs/s x {n(size)} B x 8 / 1,000,000")
        cl.check("egress_mbps", mbps, b_mbps, "Mbit/s")
    cl.check("messages_per_s", total, b_msgs, "msgs/s")
    if positive(a, "per_client_actions_per_s") is not None:
        doubled, _, _, _ = broadcast_messages(a, clients * 2)
        cl.result("messages_per_s_at_2x_clients", doubled, "msgs/s",
                  f"{n(total)} msgs/s re-evaluated at {n(clients * 2)} clients")
        shape = ("O(n^2): every client action reaches every other client" if fanout == "all"
                 else "O(n x room_size): bounded by room size, linear in clients")
        cl.notes.append(f"Scaling shape of relayed client actions: {shape}; "
                        f"doubling clients multiplies messages/s by {n(doubled / total)}.")
    cl.notes.append("Counts delivered messages, not server-side batching or coalescing; egress excludes protocol framing.")
    return cl.to_dict()


def calc_pool(a: dict[str, Any]) -> dict[str, Any]:
    rate, latency = need(a, "rate_rps"), need(a, "latency_ms")
    pool, dbmax = positive(a, "pool_size"), positive(a, "db_max_connections")
    instances = positive(a, "instances") or 1.0
    cl = Calc("pool", {"rate_rps": rate, "latency_ms": latency, "pool_size": pool, "db_max_connections": dbmax,
                       "instances": instances})
    concurrency = cl.result("concurrency", rate * latency / 1000, "in-flight requests",
                            f"{n(rate)} req/s x {n(latency)} ms / 1000 (Little's law)")
    per_instance = cl.result("concurrency_per_instance", concurrency / instances, "in-flight requests",
                             f"{n(concurrency)} / {n(instances)} instances")
    if pool is not None:
        util = cl.result("pool_utilisation", per_instance / pool, "ratio",
                         f"{n(per_instance)} per instance / pool of {n(pool)}")
        cl.check("pool_utilisation", util, 1.0, "ratio")
        total = cl.result("total_connections_possible", pool * instances, "connections",
                          f"pool {n(pool)} x {n(instances)} instances")
        cl.check("total_connections_vs_db_max", total, dbmax, "connections")
    else:
        required = cl.result("connections_needed_at_least", math.ceil(concurrency), "connections",
                             f"ceil({n(concurrency)})")
        cl.check("connections_needed_vs_db_max", required, dbmax, "connections")
        if dbmax is not None:
            cl.notes.append("No pool size given: compared the in-flight minimum against the database limit only.")
    cl.notes.append("Assumes one connection per in-flight request and the stated mean latency; tail latency and "
                    "retries raise the real figure. Latency must be measured or profiled, not guessed.")
    return cl.to_dict()


def calc_memory(a: dict[str, Any]) -> dict[str, Any]:
    conns = need(a, "connections")
    per = need(a, "bytes_per_connection",
               "it must come from a profiled measurement (heap or RSS diff per connection), never a guess")
    budget = positive(a, "budget_mb")
    cl = Calc("memory", {"connections": conns, "bytes_per_connection": per, "budget_mb": budget})
    total = cl.result("total_bytes", conns * per, "bytes", f"{n(conns)} connections x {n(per)} B")
    mib = cl.result("total_mib", total / MIB, "MiB", f"{n(total)} B / 1,048,576")
    cl.check("total_mib", mib, budget, "MiB")
    cl.notes.append("--budget-mb is read as MiB (1,048,576 B). Excludes shared baseline memory, buffers that scale "
                    "with message rate, and per-connection send queues unless they are in the measured figure.")
    return cl.to_dict()


def calc_fanout(a: dict[str, Any]) -> dict[str, Any]:
    rate, calls = need(a, "rate_rps"), need(a, "calls_per_request")
    depth, rtt = positive(a, "serial_depth"), positive(a, "rtt_ms")
    b_down, b_lat = positive(a, "budget_downstream_rps"), positive(a, "budget_latency_ms")
    if (depth is None) != (rtt is None):
        raise c.UsageError("serial_depth and rtt_ms go together", hint="pass both --serial-depth D and --rtt-ms T")
    if b_lat is not None and depth is None:
        raise c.UsageError("budget_latency_ms needs serial_depth and rtt_ms",
                           hint="the latency floor is serial_depth x rtt_ms; supply both")
    cl = Calc("fanout", {"rate_rps": rate, "calls_per_request": calls, "serial_depth": depth, "rtt_ms": rtt,
                         "budget_downstream_rps": b_down, "budget_latency_ms": b_lat})
    down = cl.result("downstream_rps", rate * calls, "req/s", f"{n(rate)} req/s x {n(calls)} calls/request")
    cl.check("downstream_rps", down, b_down, "req/s")
    if depth is not None:
        floor = cl.result("serial_latency_floor_ms", depth * rtt, "ms", f"{n(depth)} serial calls x {n(rtt)} ms RTT")
        cl.check("serial_latency_floor_ms", floor, b_lat, "ms")
    cl.notes.append("The latency floor counts round trips only; it ignores server work and assumes the rest of the "
                    "calls run in parallel.")
    return cl.to_dict()


CALCS: dict[str, dict[str, Any]] = {
    "poll": dict(fn=calc_poll, help="Timer-driven client polling: clients x requests per poll / interval.",
                 args=[arg("clients", "number of concurrent clients (> 0)", True),
                       arg("interval_s", "seconds between polls (> 0)", True),
                       arg("requests_per_poll", "requests issued per poll (default 1)"),
                       arg("budget_rps", "request-rate budget in req/s (optional)")],
                 example="amplify.py poll --clients 100000 --interval-s 2 --budget-rps 5000"),
    "broadcast": dict(fn=calc_broadcast, help="Real-time fan-out: messages/s and egress; O(n^2) when every action "
                      "reaches everyone.",
                      args=[arg("clients", "number of concurrent clients (> 0)", True),
                            arg("events_per_s", "server-originated events per second delivered to each recipient"),
                            arg("per_client_actions_per_s", "actions per second per client that are relayed to the "
                                "other clients"),
                            arg("fanout", "recipients per event: all (every client) or room", choices=("all", "room"),
                                default="all"),
                            arg("room_size", "clients per room (required with --fanout room)"),
                            arg("bytes_per_message", "message size in bytes (from the profile; required for egress)"),
                            arg("budget_msgs_per_s", "message-rate budget in msgs/s"),
                            arg("budget_egress_mbps", "egress budget in Mbit/s")],
                      example="amplify.py broadcast --clients 100000 --per-client-actions-per-s 0.1 "
                              "--bytes-per-message 200 --budget-egress-mbps 10000"),
    "pool": dict(fn=calc_pool, help="Connection pool arithmetic with Little's law.",
                 args=[arg("rate_rps", "requests per second reaching the pool (> 0)", True),
                       arg("latency_ms", "mean time a connection is held per request, ms (> 0)", True),
                       arg("pool_size", "connections per instance"),
                       arg("db_max_connections", "database connection limit"),
                       arg("instances", "number of app instances sharing the database (default 1)")],
                 example="amplify.py pool --rate-rps 2000 --latency-ms 50 --pool-size 20 --instances 10 "
                         "--db-max-connections 100"),
    "memory": dict(fn=calc_memory, help="Per-connection memory x connection count (needs a profiled bytes figure).",
                   args=[arg("connections", "number of concurrent connections (> 0)", True),
                         arg("bytes_per_connection", "profiled bytes per connection; required, never guessed"),
                         arg("budget_mb", "memory budget in MiB")],
                   example="amplify.py memory --connections 100000 --bytes-per-connection 65536 --budget-mb 4096"),
    "fanout": dict(fn=calc_fanout, help="Downstream call fan-out and the serial-latency floor.",
                   args=[arg("rate_rps", "requests per second to the entry point (> 0)", True),
                         arg("calls_per_request", "downstream calls issued per request (> 0)", True),
                         arg("serial_depth", "longest chain of awaited calls (needs --rtt-ms)"),
                         arg("rtt_ms", "round-trip time per call in ms (needs --serial-depth)"),
                         arg("budget_downstream_rps", "downstream capacity in req/s"),
                         arg("budget_latency_ms", "latency target in ms")],
                   example="amplify.py fanout --rate-rps 500 --calls-per-request 8 --serial-depth 4 --rtt-ms 40 "
                           "--budget-downstream-rps 3000 --budget-latency-ms 200"),
}

RESULT_GLOSSARY = """data fields (single calculation): calc, inputs (echoed), results {name: number}, units {name: unit},
formulas [text with values substituted], checks [{name, value, budget, unit, status, text}],
computed (breach|ok|no-budget), notes. `computed` is the measurement status for the performance rubric: breach =
the profile's own numbers exceed the budget; ok = every supplied budget holds; no-budget = nothing to compare
against (not a pass). Batch: results [one per scenario, with label], summary {breach, ok, no-budget, error}."""


def flag(name: str) -> str:
    return "--" + name.replace("_", "-")


def add_calc_parser(subs: Any, name: str, spec: dict[str, Any]) -> None:
    p = subs.add_parser(name, help=spec["help"], description=f"{spec['help']}\n\nArithmetic only: no model estimates "
                        f"these numbers.\n\n{RESULT_GLOSSARY}",
                        epilog=f"examples:\n  python -I scripts/{spec['example']}\n\n{c.EXIT_CODES_HELP}",
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    c.add_common_flags(p, with_repo=False)
    for a in spec["args"]:
        kwargs: dict[str, Any] = dict(dest=a["name"], type=float, default=a["default"], help=a["help"])
        if a["choices"]:
            kwargs.update(type=str, choices=a["choices"], help=f"{a['help']} (default: {a['default']})")
        p.add_argument(flag(a["name"]), **kwargs)
    p.set_defaults(func=cmd_calc, calc=name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="amplify.py",
        description=("Amplification arithmetic for the performance rubric (P1, P7, P9, P10 and the 100k checks). "
                     "Turns profile numbers into `computed` statuses so no model ever estimates them. Every result "
                     "carries the formula with values substituted, units, the inputs, and a verdict against an "
                     "optional budget.\n\nCaveats: results are averages under the stated assumptions; inputs must "
                     "come from the profile or a profiled measurement."),
        epilog=c.EXIT_CODES_HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {c.VERSION}")
    subs = parser.add_subparsers(dest="command", required=True, metavar="{" + ",".join([*CALCS, "batch"]) + "}")
    for name, spec in CALCS.items():
        add_calc_parser(subs, name, spec)
    b = subs.add_parser(
        "batch", help="run many calculations from a JSON file",
        description=("Run many calculations in one call.\n\nSCENARIOS.json is a list: "
                     '[{"calc": "poll", "args": {"clients": 100000, "interval_s": 2}, "label": "chat poll"}]. '
                     "Arg names are the flag names with dashes or underscores. A bad scenario is reported with an "
                     "error and the run exits 2 after printing every result.\n\n" + RESULT_GLOSSARY),
        epilog=("examples:\n  python -I scripts/amplify.py batch --file scenarios.json --format text\n\n"
                + c.EXIT_CODES_HELP),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    c.add_common_flags(b, with_repo=False)
    b.add_argument("--file", required=True, help="JSON list of {calc, args, label}")
    b.set_defaults(func=cmd_batch)
    return parser


def run_calc(name: str, raw_args: dict[str, Any]) -> dict[str, Any]:
    spec = CALCS.get(name)
    if spec is None:
        raise c.UsageError(f"unknown calc: {name!r}", hint="one of: " + ", ".join(CALCS))
    known = {a["name"] for a in spec["args"]}
    args = {k.replace("-", "_"): v for k, v in raw_args.items()}
    unknown = sorted(set(args) - known)
    if unknown:
        raise c.UsageError(f"unknown argument(s) for {name}: {', '.join(unknown)}",
                           hint="valid: " + ", ".join(sorted(known)))
    for a in spec["args"]:
        if a["required"] and args.get(a["name"]) is None:
            raise c.UsageError(f"{a['name']} is required for {name}", hint=a["help"])
    return spec["fn"](args)


def text_one(d: dict[str, Any]) -> str:
    lines = [f"{d['calc']}: computed={d['computed']}"] + [f"  {f}" for f in d["formulas"]]
    lines += [f"  check {k['text']}" for k in d["checks"]]
    lines += [f"  note: {note}" for note in d["notes"]]
    return "\n".join(lines)


def cmd_calc(ns: argparse.Namespace) -> int:
    env = c.Envelope(TOOL, c.args_dict(ns))
    given = {a["name"]: getattr(ns, a["name"]) for a in CALCS[ns.calc]["args"]}
    env.data = run_calc(ns.calc, given)
    c.log(1, f"{ns.calc}: computed={env.data['computed']}")
    c.write_output(env, ns, text_one)
    return c.EXIT_OK


def text_batch(d: dict[str, Any]) -> str:
    out = []
    for r in d["results"]:
        head = r.get("label") or r.get("calc")
        out.append(f"[{head}] ERROR: {r['error']}" if "error" in r else f"[{head}] " + text_one(r))
    s = d["summary"]
    out.append(f"summary: {s['breach']} breach, {s['ok']} ok, {s['no-budget']} no-budget, {s['error']} error")
    return "\n".join(out)


def load_scenarios(path: str) -> list[Any]:
    scenarios = c.read_json(path)
    if not isinstance(scenarios, list) or not scenarios:
        raise c.InputError(f"{path} must be a non-empty JSON list of scenarios",
                           hint='shape: [{"calc": "poll", "args": {...}, "label": "..."}]')
    return scenarios


def run_scenario(index: int, scenario: Any, env: c.Envelope) -> dict[str, Any]:
    label = scenario.get("label") if isinstance(scenario, dict) else None
    try:
        if not isinstance(scenario, dict) or "calc" not in scenario or not isinstance(scenario.get("args", {}), dict):
            raise c.UsageError(f"scenario {index} must be an object with 'calc' and an 'args' object")
        result = run_calc(scenario["calc"], scenario.get("args", {}))
        return {"label": label, **result}
    except c.UsageError as exc:
        env.warn(f"scenario {index}{f' ({label})' if label else ''}: {exc}")
        return {"label": label, "calc": scenario.get("calc") if isinstance(scenario, dict) else None,
                "error": str(exc), "hint": exc.hint}


def cmd_batch(ns: argparse.Namespace) -> int:
    env = c.Envelope(TOOL, c.args_dict(ns))
    scenarios = load_scenarios(ns.file)
    c.log(1, f"{len(scenarios)} scenarios from {ns.file}")
    results = [run_scenario(i, s, env) for i, s in enumerate(scenarios)]
    summary = {"breach": 0, "ok": 0, "no-budget": 0, "error": 0}
    for r in results:
        summary["error" if "error" in r else r["computed"]] += 1
    env.data = {"results": results, "summary": summary}
    c.write_output(env, ns, text_batch)
    return c.EXIT_USAGE if summary["error"] else c.EXIT_OK


def main(argv: list[str] | None = None) -> int:
    ns = build_parser().parse_args(argv)
    c.set_verbosity(ns.verbose)
    return ns.func(ns)


if __name__ == "__main__":
    c.run_main(main)
