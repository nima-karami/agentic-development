# Workspace isolation: mechanisms and hazards

## The decision

| Situation | Workspace |
|---|---|
| 2+ executors working concurrently | isolated, one per group — mandatory |
| Long run; the main checkout must stay usable | isolated |
| Risky change you may want to throw away whole | isolated |
| Single short slice, no concurrency | in place, on a branch |
| Duplicating the workspace is disproportionate: expensive dependency install, native/linked builds, generated artifacts | in place, serialized |
| The environment has one of something the build needs — a fixed port, one emulator, one device, one profile directory, one database | in place, serialized; parallel lanes will serve each other's code |

Isolation you don't need is over-production. Isolation you skipped under concurrency
is corruption. When the situation is genuinely mixed, serialize in place: the
wall-clock saving is never worth a poisoned tree.

## Mechanisms, and how each fails

Three appeared in the field, plus one deliberate opt-out. All four are legitimate;
pick per repository, and verify the result either way.

1. **Harness-native isolation** (the agent framework creates and cleans up the
   workspace). Cheapest, and the harness can see and manage the state. **Failure
   mode:** it has silently based new workspaces on a stale commit rather than the
   current branch tip — one lane's work came back unmergeable and was discarded.
   *Always read the base commit back before building.*
2. **Manual checkout under the OS temp directory.** Keeps the repository tree clean
   and nothing can be committed by accident. **Failure mode:** shared temp paths.
   Sessions have collided in one scratch directory, and a cleanup step wiped another
   session's browser profiles. Namespace every path per session.
3. **Manual checkout under an ignored directory inside the project.** Convenient,
   colocated. **Failure mode:** if the directory is not actually ignored, its contents
   get committed. Verify the ignore rule before creating anything in it.
4. **Deliberate opt-out — work in place on a branch.** A written, recorded decision
   in the field, on cost grounds. Legitimate for a single-lane run. Not legitimate
   the moment a second executor starts.

## Pre-flight checklist (walk before the first mutating command)

- [ ] **Base commit verified.** Read the workspace's HEAD and confirm it is the
      commit you intended, not whatever the mechanism happened to pick.
- [ ] **Working directory verified.** Every mutating command names or runs inside the
      workspace path. A dependency install in an unverified directory has wiped the
      shared checkout's modules and broken a run mid-flight — four separate incidents
      in one corpus, plus one mirror case in another.
- [ ] **Linked/junctioned dependencies noted.** Where the workspace's dependency
      directory is a link into a shared one, a clean install or a delete in the
      workspace destroys the shared one. Know before you install whether this
      repository links.
- [ ] **Ignore rule confirmed** for any workspace created inside the project tree.
- [ ] **Temp and profile directories namespaced per session.** Never share a scratch,
      cache, download, or browser-profile directory with another session, and never
      delete a shared one on cleanup.
- [ ] **Ports and singletons checked.** A leftover process squatting the port
      produced a false "4 passed". Confirm nothing is already listening, and prefer a
      per-lane port over a reused server.
- [ ] **Process cleanup targets identifiers, not image names.** Killing by image name
      closed the user's real browser once. Track what you started; end only that.
- [ ] **Untracked local configuration copied in.** Environment files, local settings,
      and credentials are not in the repository, so a fresh workspace boots against
      defaults and "works" while proving nothing. Copy them, or know why you didn't.
- [ ] **Pre-commit tooling understood.** A staged-file stash-and-restore hook has
      silently reverted committed work — twice. Read the tree's status after every
      commit, not just before.

## Teardown

Remove the workspace only after the work is committed and the commit SHA is recorded;
the SHA is the evidence, and an uncommitted workspace deleted is lost work. Delete
only paths this session created, by absolute path. Leave shared directories alone
even when they look like garbage — they are usually another session's.
