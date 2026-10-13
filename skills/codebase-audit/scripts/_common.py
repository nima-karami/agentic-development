"""Shared plumbing for the codebase-audit scripts.

Every script in this directory is stdlib-only Python 3.9+, read-only against the
audited repository unless its help says otherwise, and follows one contract:

* Output is a JSON envelope (see ``Envelope``) written to ``--out`` or stdout, so a
  later agent or a later audit can rerun the identical command and diff the result.
* Diagnostics go to stderr. ``-v`` explains each step, ``-vv`` also echoes every git
  command and its timing, ``--debug`` prints tracebacks.
* Exit codes are fixed across scripts:

  ====  ==========================================================================
  0     success
  1     the condition the caller asked to fail on was found (``--fail-on-*`` flags)
  2     usage error (bad or missing arguments)
  3     environment error (git missing, path is not a repository, a command failed)
  4     input error (an input file is missing, unreadable, or not the expected shape)
  ====  ==========================================================================
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import os
import re
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Sequence

VERSION = "0.1.0"

EXIT_OK = 0
EXIT_CONDITION = 1
EXIT_USAGE = 2
EXIT_ENV = 3
EXIT_INPUT = 4

EXIT_CODES_HELP = """exit codes:
  0  success
  1  a condition requested with a --fail-on-* flag was found
  2  usage error
  3  environment error (git missing, not a repository, a command failed)
  4  input error (missing, unreadable or malformed input file)"""


class AuditError(Exception):
    exit_code = EXIT_ENV

    def __init__(self, message: str, hint: str | None = None):
        super().__init__(message)
        self.hint = hint


class EnvError(AuditError):
    exit_code = EXIT_ENV


class InputError(AuditError):
    exit_code = EXIT_INPUT


class UsageError(AuditError):
    exit_code = EXIT_USAGE


_verbosity = 0


def log(level: int, message: str) -> None:
    """Write a diagnostic line to stderr when verbosity is at least ``level``."""
    if _verbosity >= level:
        stamp = _dt.datetime.now().strftime("%H:%M:%S")
        print(f"[{stamp}] {message}", file=sys.stderr, flush=True)


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr, flush=True)


@dataclass
class Envelope:
    tool: str
    args: dict[str, Any]
    repo: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)
    data: Any = None
    started: float = field(default_factory=time.time)

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        warn(message)

    def to_json(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "version": VERSION,
            "command": [os.path.basename(sys.argv[0])] + sys.argv[1:],
            "args": self.args,
            "repo": self.repo,
            "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "duration_s": round(time.time() - self.started, 3),
            "warnings": self.warnings,
            "data": self.data,
        }


def make_parser(
    prog: str,
    description: str,
    examples: str,
    with_repo: bool = True,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        epilog=f"examples:\n{examples.rstrip()}\n\n{EXIT_CODES_HELP}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_common_flags(parser, with_repo=with_repo)
    return parser


def add_common_flags(parser: argparse.ArgumentParser, with_repo: bool = True) -> None:
    if with_repo:
        parser.add_argument(
            "--repo",
            default=".",
            help="path to the audited git repository (default: current directory)",
        )
    parser.add_argument(
        "--out",
        help="write the JSON envelope here instead of stdout (parent dirs are created)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="json: the full envelope; text: a human summary on stdout (default: json)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="explain each step on stderr; repeat (-vv) to echo every git command",
    )
    parser.add_argument(
        "--debug", action="store_true", help="print a full traceback on failure"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")


def set_verbosity(level: int) -> None:
    global _verbosity
    _verbosity = level


def args_dict(ns: argparse.Namespace) -> dict[str, Any]:
    skip = {"func", "debug", "verbose", "format", "out"}
    return {k: v for k, v in vars(ns).items() if k not in skip}


def run_git(repo: str, args: Sequence[str], check: bool = True) -> str:
    cmd = ["git", "-C", repo, *args]
    log(2, "$ " + " ".join(cmd))
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise EnvError("git is not on PATH", hint="install git or fix PATH") from exc
    log(2, f"  exit {proc.returncode} in {time.time() - t0:.2f}s, {len(proc.stdout)} bytes")
    if check and proc.returncode != 0:
        raise EnvError(
            f"git command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}",
            hint="rerun with -vv to see every git command",
        )
    return proc.stdout


def repo_info(repo: str) -> dict[str, Any]:
    if not os.path.isdir(repo):
        raise EnvError(f"repository path does not exist: {repo}")
    top = run_git(repo, ["rev-parse", "--show-toplevel"], check=False).strip()
    if not top:
        raise EnvError(
            f"not a git repository: {repo}",
            hint="pass --repo pointing at the audited checkout",
        )
    head = run_git(repo, ["rev-parse", "--verify", "--quiet", "HEAD"], check=False).strip() or None
    dirty = run_git(repo, ["status", "--porcelain"], check=False).strip()
    return {
        "path": os.path.abspath(top),
        "head": head,
        "dirty_files": len(dirty.splitlines()) if dirty else 0,
    }


_glob_cache: dict[str, re.Pattern[str]] = {}


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a glob with ``**`` (any depth), ``*`` and ``?`` into a regex."""
    if pattern in _glob_cache:
        return _glob_cache[pattern]
    p = pattern.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    out = []
    i = 0
    while i < len(p):
        c = p[i]
        if p.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif p.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    rx = re.compile("^" + "".join(out) + "$")
    _glob_cache[pattern] = rx
    return rx


def glob_match(path: str, patterns: Iterable[str]) -> bool:
    path = path.replace("\\", "/")
    for pat in patterns:
        if _glob_to_regex(pat).match(path) or fnmatch.fnmatch(path, pat):
            return True
    return False


def select_paths(paths: Iterable[str], include: Sequence[str], exclude: Sequence[str]) -> list[str]:
    """Keep paths matching any include (all, when include is empty) and no exclude."""
    kept = []
    for p in paths:
        p = p.replace("\\", "/")
        if include and not glob_match(p, include):
            continue
        if exclude and glob_match(p, exclude):
            continue
        kept.append(p)
    return kept


def tracked_files(repo: str, include: Sequence[str] = (), exclude: Sequence[str] = ()) -> list[str]:
    out = run_git(repo, ["ls-files", "-z"])
    files = [f for f in out.split("\0") if f]
    selected = select_paths(files, include, exclude)
    log(1, f"{len(files)} tracked files, {len(selected)} after include/exclude")
    return selected


def read_json(path: str) -> Any:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise InputError(f"input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"input file is not valid JSON: {path}: {exc}") from exc


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_output(envelope: Envelope, ns: argparse.Namespace, text_summary: Callable[[Any], str] | None = None) -> None:
    payload = json.dumps(envelope.to_json(), indent=2, sort_keys=False, ensure_ascii=False)
    if ns.out:
        os.makedirs(os.path.dirname(os.path.abspath(ns.out)) or ".", exist_ok=True)
        with open(ns.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
        log(1, f"wrote {ns.out}")
    if ns.format == "text":
        print(text_summary(envelope.data) if text_summary else payload)
    elif not ns.out:
        print(payload)


def run_main(main: Callable[[list[str] | None], int], argv: list[str] | None = None) -> None:
    debug = "--debug" in (argv if argv is not None else sys.argv)
    try:
        sys.exit(main(argv))
    except AuditError as exc:
        print(f"error: {exc}", file=sys.stderr)
        if exc.hint:
            print(f"hint: {exc.hint}", file=sys.stderr)
        if debug:
            traceback.print_exc()
        sys.exit(exc.exit_code)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        sys.exit(130)
