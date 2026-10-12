# Rubric — security

Runs when the profile lists any stakes (data, money, auth, a public surface,
untrusted input, an installer or updater). Scanners own pattern-finding — injection
sinks, weak crypto, known CVEs, secret patterns. **This rubric judges what scanners
cannot**: authorization, trust boundaries, isolation, the posture of the scanners
themselves, and the shortcuts taken to make things work. Type refinement at a
boundary (C2) and hidden failure (C1) stay in the contracts rubric; cite them, don't
restate them.

**Severity** is categorical and comes from the profile: exposure × attacker
precondition × asset × blast radius. Record confidence separately; a noisy scanner
lowers confidence, never severity. A missing profile fact makes a finding a
`candidate (unverified)` — it never lowers the standard. CVSS applies only to
scanner-reported CVEs (use its environmental adjustments); EPSS is a tiebreaker for
dependency CVEs. Agent authorship never raises severity.

The same missing object-level check is Low in a single-user desktop tool, Medium in an
internal multi-user tool, and Critical in a public multi-tenant or money-handling
service. Concurrency alone does not raise an authorization finding; it raises
resource-exhaustion impact (S10).

## Rows

### S1 · Server authority over identity
- **Finding:** an actor identity (`userId`, `playerId`, `tenantId`, a role) read from a
  client message or request body and used in a query or session state with no lookup
  from a verified session. Name the exploit path.
- **Detection:** taint from request and message inputs to queries and session writes;
  a client-trusted-identity flow script. Verdict is judgment.
- **Severity:** Low (single user) → Critical (money, multiplayer, multi-tenant).
- **Over-engineering line:** server authority for cosmetic client-only state.
- **Applies when:** the profile has more than one user, money, or multiplayer.

### S2 · Authentication and authorization placement
- **Finding:** the route / handler / IPC channel / resolver matrix shows a mutating
  entry point with no guard; object IDs reach reads or writes without an owner or
  tenant predicate; an internal path bypasses the gateway's enforcement; a check that
  fails open (cite C1).
- **Detection:** the matrix is mechanical (route → middleware → sink script, framework
  route dumps, decorator rules); object-level checks need judgment.
- **Severity:** Medium (internal) → Critical (public multi-tenant, money, admin).
- **Over-engineering line:** per-object access control in a single-user tool;
  identical checks repeated at every layer.
- **Applies when:** roles, owners, tenants, admin operations or private objects exist.

### S3 · Entry-point inventory and uncontrolled crossings
- **Finding:** an entry point — route, IPC channel, webhook, queue consumer, deep link,
  file handler, exported mobile component, scheduled job — whose crossing into
  privilege has no named control. Report it as a chain: caller → boundary → privileged
  action.
- **Detection:** the ingress extractor's `entry point → capability` graph; verdict is
  judgment (threat modeling applied to the as-built inventory).
- **Severity:** scales with exposure × asset value.
- **Over-engineering line:** threat-modeling internal batch jobs with no untrusted
  input; boundaries between modules of the same trust.
- **Applies when:** always; depth follows stakes.

### S4 · Bounds before parsing, safe deserialization
- **Finding:** a body, upload, archive or message buffered or parsed before size,
  depth or count limits; unsafe deserializers (`pickle`, unsafe YAML loaders, native
  object streams); a client-supplied filename or content type trusted. A schema with
  unbounded arrays or nesting does not count as a bound.
- **Detection:** limit-configuration extractor plus scanner rules; adequacy is
  judgment.
- **Severity:** Low (local CLI) → High (public or anonymous input).
- **Over-engineering line:** elaborate validation on fixed internal inputs.
- **Applies when:** external structured, file or message input exists.

### S5 · Secrets and key lifecycle
- **Finding:** a live credential in the tree, the history, a built client bundle or a
  log; one shared production or signing credential; no rotation path.
- **Detection:** secret scanner over tree **and** history; a grep of built bundles.
  Liveness, scope and rotation are judgment.
- **Severity:** High if live; Critical for production, payment or signing keys.
- **Over-engineering line:** treating publishable keys and public client IDs as
  secrets.
- **Applies when:** always.

### S6 · Supply chain, install and update trust
- **Finding:** no lockfile or floating references; a reachable known-exploited CVE;
  `curl | sh` or mutable download URLs in install or CI; unpinned CI actions or
  over-broad workflow permissions; **a dependency that does not exist in its registry
  or was first published very recently** (hallucinated or squatted names); an updater
  that does not verify what it downloads.
- **Detection:** lockfile and install-script scan, dependency scanner, CI workflow
  linter, a registry existence-and-age script. Reachability and the provenance level
  required are judgment.
- **Severity:** scales with distribution — a public bundle or installer is highest.
- **Over-engineering line:** maximal provenance machinery for a low-stakes prototype;
  chasing unreachable, development-only advisories.
- **Applies when:** third-party code, CI, downloaded binaries or auto-update exist.

### S7 · Process, sandbox and IPC isolation
- **Finding:** desktop shells loading remote content with OS access; context isolation
  or sandboxing off; raw IPC exposed to the renderer; IPC senders not validated;
  unrestricted navigation or external-open; an exported mobile component or webview
  bridge; containers running as root or privileged. Ask per channel: what can a
  compromised renderer do through this?
- **Detection:** configuration extractors for the shell, mobile manifest and container
  specs; capability per channel is judgment.
- **Severity:** High → Critical if any untrusted content can reach the privileged
  side; lower for local, signed content — but insecure defaults are still reported.
- **Over-engineering line:** new sandbox layers where input and privilege are the
  same.
- **Applies when:** a desktop shell, hybrid mobile app, plugin host or container
  exists.

### S8 · Sensitive data in logs, errors and telemetry
- **Finding:** a token, password, personal or payment datum reaching a logger, error
  report or telemetry sink; whole-request dump middleware; debug mode on in
  production config; log-record injection. Also: security events (auth failures,
  privilege changes, admin actions) **not** logged where the profile needs an audit
  trail.
- **Detection:** taint or sink rules from named fields to loggers; classification is
  judgment.
- **Severity:** follows data sensitivity and retention reach, not log level.
- **Over-engineering line:** redacting ordinary diagnostics until the system cannot be
  operated.
- **Applies when:** personal, auth, payment or proprietary data exists.

### S9 · Scanner coverage, configuration and freshness
- **Finding:** a language, path or the git history no scanner covers; broad excludes;
  bulk or stale suppressions and baselines; floating scanner or rule versions; a
  scanner whose findings nobody acts on. "Green but incomplete" is the failure to
  catch.
- **Detection:** build a **scanner manifest** — name, version, rule version, included
  and excluded paths, languages, lockfiles covered, history coverage, network mode —
  then rerun each scanner locally and pinned. Whether a scanner blocks a merge belongs
  to the gates rubric; link it.
- **Severity:** Medium; High when auth, payment or entry-point paths are uncovered.
- **Over-engineering line:** requiring overlapping scanners — more scanners do not add
  coverage.
- **Applies when:** always.

### S10 · Abuse and resource-exhaustion controls
- **Finding:** no rate limit on authentication, purchase or other costly paths;
  unbounded uploads; unbounded work per request; catastrophic regexes on input; no
  per-connection rate limit on real-time channels.
- **Detection:** scanner rules, configuration scan, a custom limit detector;
  sufficiency is judgment.
- **Severity:** Low (internal) → High (public, money, high concurrency).
- **Over-engineering line:** rate-limiting localhost-only admin tools.
- **Applies when:** public endpoints, money or real-time channels exist.

### S11 · Controls weakened to make it work
- **Finding:** certificate verification disabled, CORS `*`, insecure-skip flags, OS
  access enabled in a renderer, CSRF or auth stubbed "temporarily", security tests
  skipped or deleted. Use history search to find when each appeared.
- **Detection:** a rule pack of permissive-default flags plus a history scan; intent is
  judgment.
- **Severity:** that of the control it weakens (S2, S4, S7).
- **Over-engineering line:** flagging an override with a recorded, scoped
  justification.
- **Applies when:** the codebase is agent-maintained (and is worth checking anyway).

### S12 · Agent configuration and execution-hook integrity
- **Finding:** agent rule files, tool-server configs or instruction files telling an
  agent to skip confirmation or bypass checks; hidden Unicode in them; undeclared
  executable hooks or scripts that open network connections; committed agent
  permission modes that disable prompts.
- **Detection:** inventory script, hidden-Unicode and permission-mode search, review of
  hook scripts. Intent is judgment. Evidence for this class is incident reports, not
  measured rates — keep the check, don't claim a prevalence.
- **Severity:** Critical if it bypasses approvals for a shared or CI agent; High
  otherwise.
- **Over-engineering line:** flagging ordinary formatter hooks.
- **Applies when:** the codebase is agent-maintained.

## Agent-specific patterns worth weighting

Measured in 2025–2026 studies (single studies; treat figures as directional):
functionally correct code that is exploitable, especially access control and resource
exhaustion — functional tests never discharge a security finding; insecure setup
actions (downloads without integrity checks, information exposure); new injection,
deserialization and path-traversal weaknesses in agent patches — scan the whole
repository, not only diffs; hallucinated package names that recur across runs.
Anecdotal but cheap to check: permissive defaults and stubbed auth to get tests
passing (S11); duplicated code where only one copy kept a security check (compare
security-relevant calls across clone families); poisoned agent configuration (S12).
