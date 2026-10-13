#!/usr/bin/env python3
"""Create, inspect and safely remove the isolated audit worktree. See --help."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import stat
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as c  # noqa: E402

TOOL = "isolate"
MARKER_NAME = ".audit-isolate.json"
IS_WINDOWS = os.name == "nt"
LINK_SCAN_DEPTH = 3

DESCRIPTION = """\
Create, inspect and remove the isolated worktree used by test strength and the
measurement wave. This is the one audit script that WRITES, so it is paranoid.

SAFETY RULES (enforced, not advisory):
  1. The audited checkout is never modified. Only git's own worktree metadata under the
     source repo's .git/worktrees is touched (by `git worktree add/remove/prune`);
     status reports the source `git status --porcelain` before and after so you can prove it.
  2. Dependency directories (node_modules, .venv ...) are LINKED into the worktree
     (Windows: directory junction; POSIX: symlink), never copied and never installed.
  3. Before the worktree is removed, EVERY link is unlinked first with an operation that
     removes only the link (Windows: rmdir on the junction; POSIX: unlink), and the link
     target is verified intact afterwards. Removing a worktree that still contains a link
     can delete the real dependency directory behind it. A real directory is never
     deleted in the place of a link.
  4. Refusals: destination exists and is non-empty; destination is inside (or contains)
     the source working tree; a link target does not exist or is not a directory; a link
     name is tracked at the commit or is a path rather than a name; remove on a directory
     without the .audit-isolate.json marker.
  5. --dry-run prints every action and performs none.

subcommands:
  create   git worktree add --detach DEST SHA, verify HEAD, link dependency dirs, write the marker
  status   marker, worktree HEAD, link integrity, dirty files, and the source repo's status
  remove   unlink links, verify targets, git worktree remove --force, prune

Caveat: anything the audited code does while running inside the worktree (tests, builds)
is outside this script's control; run only what the audit plan allows, and one thing at a
time per worktree.
"""

EXAMPLES = """\
  python -I scripts/isolate.py create --repo . --commit 3f2a9c1 --dest ../audit-wt --link node_modules --link .venv --dry-run
  python -I scripts/isolate.py create --repo . --commit 3f2a9c1 --dest ../audit-wt --link node_modules
  python -I scripts/isolate.py status --dest ../audit-wt
  python -I scripts/isolate.py remove --dest ../audit-wt"""


def is_link(path: str) -> bool:
    """True for symlinks and, on Windows, junctions and other reparse points."""
    if os.path.islink(path):
        return True
    if IS_WINDOWS:
        try:
            return bool(os.lstat(path).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except (OSError, AttributeError):
            return False
    return False


def unlink_link(path: str) -> None:
    """Remove only the link at path; refuses anything that is not a link."""
    if not is_link(path):
        raise c.EnvError(f"refusing to unlink {path}: it is not a link", hint="a real directory is never deleted in place of a link")
    if IS_WINDOWS:
        try:
            os.rmdir(path)
        except OSError:
            os.unlink(path)
    else:
        os.unlink(path)


def create_link(link_path: str, target: str) -> str:
    if IS_WINDOWS:
        proc = subprocess.run(["cmd", "/c", "mklink", "/J", link_path, target], capture_output=True, text=True)
        c.log(2, f"mklink /J exit {proc.returncode}: {(proc.stdout + proc.stderr).strip()}")
        if proc.returncode == 0 and is_link(link_path):
            return "junction"
        try:
            os.symlink(target, link_path, target_is_directory=True)
            return "symlink"
        except OSError as exc:
            raise c.EnvError(f"cannot link {link_path} -> {target}: {(proc.stderr or proc.stdout).strip()} / {exc}",
                             hint="junctions need no admin rights; check the paths are on a local NTFS volume") from exc
    try:
        os.symlink(target, link_path, target_is_directory=True)
    except OSError as exc:
        raise c.EnvError(f"cannot symlink {link_path} -> {target}: {exc}") from exc
    return "symlink"


def entry_count(path: str) -> int | None:
    try:
        return len(os.listdir(path))
    except OSError:
        return None


def norm(path: str) -> str:
    return os.path.normcase(os.path.realpath(path))


def is_inside(child: str, parent: str) -> bool:
    child, parent = norm(child), norm(parent)
    try:
        return os.path.commonpath([child, parent]) == parent
    except ValueError:
        return False


def porcelain(repo: str, extra: list[str] | None = None) -> list[str]:
    args = ["status", "--porcelain", "--untracked-files=normal"] + (extra or [])
    return sorted(line for line in c.run_git(repo, args).splitlines() if line)


def read_marker(dest: str) -> dict:
    path = os.path.join(dest, MARKER_NAME)
    if not os.path.isfile(path):
        raise c.InputError(f"{dest} has no {MARKER_NAME} marker: it was not created by isolate.py", hint="refusing to touch a directory this script did not create")
    marker = c.read_json(path)
    for key in ("repo", "sha", "links"):
        if key not in marker:
            raise c.InputError(f"marker {path} is missing key {key!r}")
    return marker


def write_marker(dest: str, marker: dict) -> None:
    with open(os.path.join(dest, MARKER_NAME), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(marker, fh, indent=2, sort_keys=True)
        fh.write("\n")


def validate_link_name(name: str) -> None:
    if not name or name in (".", "..", ".git") or "/" in name or "\\" in name or name.startswith("-"):
        raise c.InputError(f"--link must be a single top-level directory name, got {name!r}", hint="e.g. --link node_modules")


def cmd_create(ns: argparse.Namespace, env: c.Envelope):
    repo_path = env.repo["path"]
    dest = os.path.abspath(ns.dest)
    sha = c.run_git(repo_path, ["rev-parse", "--verify", "--quiet", f"{ns.commit}^{{commit}}"], check=False).strip()
    if not sha:
        raise c.EnvError(f"cannot resolve commit {ns.commit!r} in {repo_path}", hint="pass a reachable SHA")
    if is_inside(dest, repo_path):
        raise c.InputError(f"destination {dest} is inside the audited working tree {repo_path}", hint="choose a sibling or temp directory outside the repository")
    if is_inside(repo_path, dest):
        raise c.InputError(f"destination {dest} contains the audited repository", hint="choose a directory outside the repository")
    if os.path.lexists(dest) and (not os.path.isdir(dest) or os.listdir(dest)):
        raise c.InputError(f"destination {dest} exists and is not an empty directory", hint="choose a new path, or run 'remove' on a previous isolate")
    link_names = list(dict.fromkeys(ns.link or []))
    links = []
    for name in link_names:
        validate_link_name(name)
        target = os.path.join(repo_path, name)
        if not os.path.isdir(target):
            raise c.InputError(f"link target {target} does not exist or is not a directory", hint="dependencies must already be installed in the audited checkout; never install in the worktree")
        tracked = c.run_git(repo_path, ["ls-tree", "--name-only", sha, "--", name], check=False).strip()
        if tracked:
            raise c.InputError(f"{name!r} is tracked at {sha[:12]}: the worktree already contains it and cannot be linked over", hint="link only untracked dependency directories")
        links.append({"name": name, "target": os.path.realpath(target), "link_path": os.path.join(dest, name)})
    actions = [f"git -C {repo_path} worktree add --detach {dest} {sha}", f"verify worktree HEAD == {sha}"]
    actions += [f"link {l['link_path']} -> {l['target']} ({'junction' if IS_WINDOWS else 'symlink'})" for l in links]
    actions.append(f"write {os.path.join(dest, MARKER_NAME)}")
    before = porcelain(repo_path)
    env.data = {"dry_run": ns.dry_run, "repo": repo_path, "sha": sha, "dest": dest, "actions": actions,
                "links": [], "source_status_before": before, "source_status_after": None, "source_unchanged": None}
    if ns.dry_run:
        for a in actions:
            print(f"dry-run: {a}", file=sys.stderr)
        env.data["links"] = [{"name": l["name"], "target": l["target"]} for l in links]
        return c.EXIT_OK, lambda d: "dry-run, nothing done:\n" + "\n".join(f"  {a}" for a in d["actions"])
    c.log(1, f"creating worktree {dest} at {sha}")
    c.run_git(repo_path, ["worktree", "add", "--detach", dest, sha])
    marker = {"repo": repo_path, "sha": sha, "links": [], "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    write_marker(dest, marker)
    head = c.run_git(dest, ["rev-parse", "HEAD"]).strip()
    if head != sha:
        raise c.EnvError(f"worktree HEAD {head} does not match requested {sha}", hint=f"inspect with: isolate.py status --dest {dest}; remove with: isolate.py remove --dest {dest}")
    made = []
    for l in links:
        before_count = entry_count(l["target"])
        kind = create_link(l["link_path"], l["target"])
        made.append({"name": l["name"], "target": l["target"], "kind": kind})
        marker["links"] = made
        write_marker(dest, marker)
        c.log(1, f"linked {l['name']} ({kind}) -> {l['target']} ({before_count} entries)")
    after = porcelain(repo_path)
    env.data.update({"links": made, "source_status_after": after, "source_unchanged": before == after,
                     "marker": os.path.join(dest, MARKER_NAME).replace("\\", "/"), "worktree_head": head})
    if before != after:
        env.warn("the audited checkout's git status changed during create; inspect source_status_before/after")
    return c.EXIT_OK, lambda d: f"created {d['dest']} at {d['sha'][:12]} with {len(d['links'])} link(s); source unchanged: {d['source_unchanged']}"


def link_report(dest: str, marker: dict) -> list[dict]:
    out = []
    for l in marker["links"]:
        link_path = os.path.join(dest, l["name"])
        exists = os.path.lexists(link_path)
        out.append({
            "name": l["name"],
            "target": l["target"],
            "exists": exists,
            "is_link": exists and is_link(link_path),
            "is_real_directory": exists and not is_link(link_path) and os.path.isdir(link_path),
            "target_exists": os.path.isdir(l["target"]),
        })
    return out


def cmd_status(ns: argparse.Namespace, env: c.Envelope):
    dest = os.path.abspath(ns.dest)
    marker = read_marker(dest)
    head = c.run_git(dest, ["rev-parse", "HEAD"], check=False).strip() or None
    links = link_report(dest, marker)
    excludes = [f":(exclude){l['name']}" for l in marker["links"]] + [f":(exclude){MARKER_NAME}"]
    dirty = porcelain(dest, ["--", ".", *excludes])
    source = marker["repo"]
    source_status = porcelain(source) if os.path.isdir(source) else None
    registered = norm(dest) in {norm(line[len("worktree "):]) for line in c.run_git(source, ["worktree", "list", "--porcelain"], check=False).splitlines() if line.startswith("worktree ")}
    for l in links:
        if l["is_real_directory"]:
            env.warn(f"{l['name']} is a real directory in the worktree, not a link: dependencies were copied or installed here")
        if not l["exists"]:
            env.warn(f"link {l['name']} is missing from the worktree")
        if not l["target_exists"]:
            env.warn(f"link target for {l['name']} no longer exists: {l['target']}")
    if head != marker["sha"]:
        env.warn(f"worktree HEAD {head} differs from the marker sha {marker['sha']}")
    if source_status is None:
        env.warn(f"source repository {source} no longer exists")
    env.data = {
        "dest": dest, "marker": marker, "worktree_head": head, "head_matches_marker": head == marker["sha"],
        "registered_worktree": registered, "links": links, "links_intact": all(l["is_link"] and l["target_exists"] for l in links),
        "dirty_files": dirty, "source_repo": source, "source_status": source_status,
        "source_clean": source_status == [] if source_status is not None else None,
    }
    return c.EXIT_OK, lambda d: (f"{d['dest']} @ {str(d['worktree_head'])[:12]} (matches marker: {d['head_matches_marker']}); links intact: {d['links_intact']}; "
                                 f"dirty files: {len(d['dirty_files'])}; source status lines: {len(d['source_status'] or [])}")


def find_links(dest: str, marker: dict) -> list[dict]:
    """Links recorded in the marker plus any other link found up to LINK_SCAN_DEPTH levels deep."""
    found: dict[str, dict] = {}
    for l in marker["links"]:
        path = os.path.join(dest, l["name"])
        if os.path.lexists(path):
            found[norm_key(path)] = {"path": path, "name": l["name"], "target": l["target"], "origin": "marker"}

    def scan(directory: str, depth: int) -> None:
        try:
            entries = list(os.scandir(directory))
        except OSError:
            return
        for entry in sorted(entries, key=lambda e: e.name):
            if entry.name == ".git":
                continue
            if is_link(entry.path):
                key = norm_key(entry.path)
                if key not in found:
                    found[key] = {"path": entry.path, "name": os.path.relpath(entry.path, dest).replace("\\", "/"),
                                  "target": os.path.realpath(entry.path), "origin": "scan"}
            elif depth < LINK_SCAN_DEPTH and entry.is_dir(follow_symlinks=False):
                scan(entry.path, depth + 1)

    scan(dest, 1)
    return [found[k] for k in sorted(found)]


def norm_key(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


def cmd_remove(ns: argparse.Namespace, env: c.Envelope):
    dest = os.path.abspath(ns.dest)
    if not os.path.isdir(dest):
        raise c.InputError(f"destination {dest} does not exist or is not a directory")
    marker = read_marker(dest)
    source = marker["repo"]
    if not os.path.isdir(source):
        raise c.EnvError(f"source repository {source} no longer exists", hint="cannot run git worktree remove; delete the worktree by hand after unlinking its links")
    before = porcelain(source)
    links = find_links(dest, marker)
    actions = [f"unlink {l['path']} (origin: {l['origin']}; target {l['target']})" for l in links]
    actions += [f"verify link targets still exist", f"git -C {source} worktree remove --force {dest}", f"git -C {source} worktree prune"]
    env.data = {"dry_run": ns.dry_run, "dest": dest, "source_repo": source, "actions": actions, "links_unlinked": [],
                "source_status_before": before, "source_status_after": None, "source_unchanged": None, "removed": False}
    scan_only = [l for l in links if l["origin"] == "scan"]
    if scan_only:
        env.warn(f"{len(scan_only)} link(s) not in the marker were found in the worktree and will be unlinked (links only, targets untouched)")
    if ns.dry_run:
        for a in actions:
            print(f"dry-run: {a}", file=sys.stderr)
        return c.EXIT_OK, lambda d: "dry-run, nothing done:\n" + "\n".join(f"  {a}" for a in d["actions"])
    unlinked = []
    for l in links:
        target_before = entry_count(l["target"])
        unlink_link(l["path"])
        if os.path.lexists(l["path"]):
            raise c.EnvError(f"link {l['path']} still exists after unlink", hint="do not run git worktree remove; investigate manually")
        target_after = entry_count(l["target"])
        if not os.path.isdir(l["target"]) or target_after != target_before:
            raise c.EnvError(f"link target {l['target']} changed while unlinking (entries {target_before} -> {target_after})",
                             hint="stop: the dependency directory may have been damaged")
        unlinked.append({"name": l["name"], "target": l["target"], "target_entries": target_after, "target_intact": True})
        c.log(1, f"unlinked {l['name']}; target intact with {target_after} entries")
    env.data["links_unlinked"] = unlinked
    c.run_git(source, ["worktree", "remove", "--force", dest])
    c.run_git(source, ["worktree", "prune"])
    if os.path.lexists(dest):
        env.warn(f"{dest} still exists after git worktree remove; it was not deleted further")
    after = porcelain(source)
    env.data.update({"source_status_after": after, "source_unchanged": before == after, "removed": not os.path.lexists(dest)})
    if before != after:
        env.warn("the audited checkout's git status changed during remove; inspect source_status_before/after")
    return c.EXIT_OK, lambda d: f"removed {d['dest']}: {len(d['links_unlinked'])} link(s) unlinked, targets intact; source unchanged: {d['source_unchanged']}"


def build_parser() -> argparse.ArgumentParser:
    raw = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog="isolate.py", description=DESCRIPTION,
                                     epilog=f"examples:\n{EXAMPLES}\n\n{c.EXIT_CODES_HELP}", formatter_class=raw)
    parser.add_argument("--version", action="version", version=f"%(prog)s {c.VERSION}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="{create,status,remove}")
    safety = "SAFETY: the audited checkout is never modified; links are unlinked (never deleted through) before removal; --dry-run does nothing."

    def add(name, help_, desc, epilog, func, with_repo=False):
        sp = sub.add_parser(name, help=help_, description=f"{safety}\n\n{desc}", formatter_class=raw, epilog=f"{epilog}\n\n{c.EXIT_CODES_HELP}")
        c.add_common_flags(sp, with_repo=with_repo)
        sp.set_defaults(func=func)
        return sp

    sp = add("create", "create the isolated worktree and link dependencies",
             "git worktree add --detach DEST SHA, verify the worktree HEAD equals SHA, link each --link directory from the\n"
             "audited checkout (junction on Windows, symlink on POSIX; never copied, never installed), and write the\n"
             "DEST/.audit-isolate.json marker (repo, sha, links, created_at).\n"
             "data fields: dest, sha, repo, links[{name, target, kind}], worktree_head, marker, actions[], dry_run,\n"
             "source_status_before/after (git status --porcelain of the audited repo), source_unchanged.\n"
             "exit 4: refusal (DEST non-empty, DEST inside the repo or containing it, link target missing, link name tracked\n"
             "at the commit). exit 3: git failed or the worktree HEAD does not equal SHA (the marker is already written, so\n"
             "'remove' still works).",
             "examples:\n  python -I scripts/isolate.py create --repo . --commit HEAD --dest ../audit-wt --link node_modules --dry-run\n"
             "  python -I scripts/isolate.py create --repo . --commit 3f2a9c1 --dest ../audit-wt --link node_modules --link .venv",
             cmd_create, with_repo=True)
    sp.add_argument("--commit", required=True, metavar="SHA", help="commit to check out (resolved to a full SHA); the worktree is detached there")
    sp.add_argument("--dest", required=True, help="new directory for the worktree; must not exist or be empty, and must be outside the repository")
    sp.add_argument("--link", action="append", metavar="DIR_NAME", help="top-level dependency directory to link from the audited checkout (node_modules, .venv ...); repeatable")
    sp.add_argument("--dry-run", action="store_true", help="validate and print every action without doing any")

    sp = add("status", "inspect an isolated worktree",
             "Report the marker, the worktree HEAD (and whether it still matches the marker), whether each link is still a\n"
             "link (not a real directory) with an existing target, dirty files in DEST (the marker and links are excluded),\n"
             "and the source repo's `git status --porcelain` so the caller can confirm the audited checkout was not touched.\n"
             "data fields: marker, worktree_head, head_matches_marker, registered_worktree, links[{name, target, exists,\n"
             "is_link, is_real_directory, target_exists}], links_intact, dirty_files[], source_repo, source_status[], source_clean.",
             "example:\n  python -I scripts/isolate.py status --dest ../audit-wt", cmd_status)
    sp.add_argument("--dest", required=True, help="the isolated worktree directory (must contain the marker)")

    sp = add("remove", "unlink links, then remove the worktree",
             "Unlink every link (marker-recorded, plus any other link found up to 3 levels deep) with an operation that removes\n"
             "only the link, verify each target still exists with the same entry count, then `git worktree remove --force DEST`\n"
             "and `git worktree prune`. Refuses when DEST has no marker. Reports the source repo's status before and after.\n"
             "data fields: links_unlinked[{name, target, target_entries, target_intact}], removed, actions[], dry_run,\n"
             "source_status_before/after, source_unchanged.\n"
             "If a target looks damaged the script stops with exit 3 BEFORE running git worktree remove.",
             "examples:\n  python -I scripts/isolate.py remove --dest ../audit-wt --dry-run\n  python -I scripts/isolate.py remove --dest ../audit-wt",
             cmd_remove)
    sp.add_argument("--dest", required=True, help="the isolated worktree directory (must contain the marker)")
    sp.add_argument("--dry-run", action="store_true", help="print every action without doing any")
    return parser


def main(argv: list[str] | None = None) -> int:
    ns = build_parser().parse_args(argv)
    c.set_verbosity(ns.verbose)
    env = c.Envelope(tool=f"{TOOL} {ns.command}", args=c.args_dict(ns))
    if getattr(ns, "repo", None) is not None:
        env.repo = c.repo_info(ns.repo)
    code, text = ns.func(ns, env)
    c.write_output(env, ns, text)
    return code


if __name__ == "__main__":
    c.run_main(main)
