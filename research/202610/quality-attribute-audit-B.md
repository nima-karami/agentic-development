# Security and Performance Dimensions for an Audit of an Agent-Written Codebase: Rubrics, Tools and Severity

The profile should decide which checks apply, and most checks should come from deterministic tools. For security, the checks that matter most are the ones scanners cannot do: authorization placement, trust boundaries and server authority. For performance, a small number of static patterns cover most cases: fan-out, N+1 queries, unbounded reads, blocking calls on hot paths and payload weight. Each static performance finding stays a "candidate" until it is measured against a budget that the profile sets.

A note on sourcing. This session had no web search tool. Standards, thresholds and tool behaviour below are therefore stated from established public documentation as I know it, with dates. The 2025–2026 figures on agent-written code came from a research subagent that also could not browse, so treat them as "verify before citing". Each one is labelled.

## TL;DR

- **Security:** about half of the rubric is judgment that no scanner covers. The main items are authorization placement, which identity the server trusts, trust-boundary inventory and Electron/IPC isolation. The other half is scanner coverage and configuration, which tools should compute: SAST, SCA, secrets, CI and IaC config. The best measured evidence on agent-written code (BaxBench, Feb 2025) says that pattern scanners catch the injection classes but miss the logic classes. Agent-written code produces exactly those logic classes: missing authz, resource exhaustion and hallucinated dependencies.
- **Performance:** about seven of the ten checks can be found statically from code, git history and build output. None of them should be reported above "candidate" severity unless one of two things holds. Either a cheap measurement exists (a bundle analyzer, a throttled Lighthouse run, EXPLAIN on realistic data, a 60-second k6 run against a local build), or the static arithmetic alone breaks a budget that the profile states. Most of the profile-driven severity comes from load (2k vs 100k concurrent users) and device class.
- **Other attributes:** fold reliability and resilience into performance, as one criterion group covering timeouts, retries, backpressure and reconnect storms. Fold observability into both dimensions as an enabling criterion: performance cannot be measured without it, and security cannot be detected without it. Make accessibility a separate, profile-gated dimension. Only switch it on when the profile includes public or regulated user-facing UI.

## Key Findings: the ten security and ten performance checks that matter most

### Top 10 security checks (and the profile facts that switch each on)

| # | Check | Applies when the profile says… |
|---|---|---|
| S1 | **Server authority / identity trust:** the server derives the actor identity from a verified session or token, never from a client-supplied ID | Multi-user, any auth, money or prizes, multiplayer |
| S2 | **Authorization placement:** every route, handler, IPC channel and resolver passes through one enforced check, with object-level checks for tenant- and user-owned data | Multi-tenant, any roles, personal data |
| S3 | **Trust-boundary inventory and audit-time threat model** (STRIDE per ingress point) | Always; depth scales with stakes |
| S4 | **Input parsing at ingestion points:** schema validation, size limits, safe deserialization, path handling | Public network exposure, file or upload handling, partner integrations |
| S5 | **Secrets handling:** nothing in the repo or its history, no secrets in client bundles, rotation path exists | Always |
| S6 | **Dependency and supply-chain posture:** lockfiles, known-vuln deps, install scripts, unpinned CI actions, hallucinated or typosquat packages | Always; severity rises with public distribution (web bundles, desktop installers) |
| S7 | **Process isolation and sandboxing:** Electron webPreferences and IPC validation, mobile WebView bridges, server container privileges | Desktop/Electron, hybrid mobile, server running untrusted input |
| S8 | **Sensitive data in logs and telemetry** | Personal data, auth tokens, payments, regulated data |
| S9 | **Scanner coverage and configuration:** which scanners run, on which paths, with which rules, and whether findings are suppressed wholesale | Always |
| S10 | **Abuse and resource-exhaustion controls:** rate limits, request size and time limits, unbounded work per request | Public endpoints, money, high concurrency |

### Top 10 performance checks

| # | Check | Applies when the profile says… |
|---|---|---|
| P1 | **Request fan-out per screen or route** (count of calls, serial chains) | Mobile web, high-latency networks, many concurrent users |
| P2 | **N+1 queries / per-item remote calls in loops** | Any DB- or API-backed server; severity scales with list size × concurrency |
| P3 | **Unbounded reads:** missing pagination or limits, `SELECT *` into memory, unbounded payloads | Data grows over time; multi-tenant |
| P4 | **Synchronous or blocking I/O on a hot path** (event loop, UI thread, async handler) | Node/Electron main process, Python asyncio, game loops |
| P5 | **JS bundle and dependency weight on the critical path** | Web on mobile, low-end devices, cold-start-sensitive desktop |
| P6 | **Render cascades / unnecessary re-renders** | Interactive SPAs, low-end mobile, real-time UIs |
| P7 | **Polling vs push, and broadcast fan-out** | Real-time/multiplayer, more than about 1k concurrent clients |
| P8 | **Caching and its invalidation** (missing, unbounded, or stale-by-design) | Read-heavy, repeated identical work |
| P9 | **Memory retention:** listeners, timers, global maps, closures | Long-lived sessions (desktop, kiosks, game servers, SPAs left open) |
| P10 | **Resilience under load:** timeouts, retry with jitter, pool sizes, backpressure, reconnect storms | Backends with dependencies; more than about 10k concurrent clients |

## Details

### 1. From profile to criteria

**Established practice: quality-attribute scenarios.** The SEI's six-part scenario has source, stimulus, artifact, environment, response and response measure (Bass, Clements and Kazman, *Software Architecture in Practice*, 4th ed., 2021). It is the most direct way to turn "100k concurrent players" into something testable. Write one scenario per dominant attribute. For example: "During a live draw (environment), 100k clients (source) submit a pick within 10 s (stimulus) to the game service (artifact). Every pick is accepted or rejected (response), with p99 below 500 ms and no lost writes (response measure)." Every performance criterion then inherits its threshold from that response measure, and every security criterion inherits its impact from what the scenario puts at stake. The 500 ms in this example is illustrative, not a standard.

**Threat modeling at audit time (established practice, adapted).** The Threat Modeling Manifesto (2020) frames threat modeling as four questions: what are we working on, what can go wrong, what are we going to do about it, did we do a good job. On existing code, answer the first question by extraction, not by interview:

- Enumerate ingress points: routes, IPC channels, message consumers, file and URL handlers, cron jobs, webhooks, CLI arguments.
- Enumerate egress points and data stores.
- Draw boundaries where trust changes.

Then apply STRIDE per ingress point: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege. Use attack trees only for the one or two assets that carry the profile's stakes, such as money, prizes, admin access or another tenant's data.

**Performance budgets (established web practice).** Google's Core Web Vitals give "good" thresholds at the 75th percentile of page loads: LCP ≤ 2.5 s, INP ≤ 200 ms and CLS ≤ 0.1 (web.dev). INP replaced FID as a Core Web Vital on 12 March 2024. These thresholds were derived by Google from field data (CrUX) and user-experience research. They are vendor-set, but they are the de facto standard. The RAIL model (Chrome team) gives the long-task threshold of 50 ms and the 16 ms frame budget at 60 fps. The 16 ms figure is arithmetic: 1000 ms ÷ 60.

JS byte budgets are opinion, not standard. Alex Russell's "Performance Inequality Gap" series (2023–2024) argues for keeping critical-path JS to a few hundred KiB compressed for median Android devices. Use it as an explicitly labelled heuristic.

**Capacity targets (established SRE practice).** SLOs come from Google's *Site Reliability Engineering* (2016) and *The Site Reliability Workbook* (2018). Express capacity as peak concurrent users and peak request rate, with headroom. Little's Law (concurrency = throughput × latency) turns profile numbers into pool sizes and connection counts that a script can check against config.

**Minimum profile.** See the checklist in Recommendations. In short:

- **Security** cannot be judged without the asset list (what is valuable), the actor list (who is untrusted) and the exposure (public, partner or internal).
- **Performance** cannot be judged without peak load, the target device and network class, and at least one stated response measure.

If any of these are missing, the audit should emit "profile-blocked" rather than guess.

### 2. Security in an as-built codebase: what goes in the rubric vs the scanner

The general principle: scanners find **instances of known-bad patterns**. The rubric judges **properties of the whole system**: is there one auth chokepoint, is the server authoritative, is the scanner set adequate. OWASP ASVS 5.0 (released May 2025) is the best requirement catalogue for mapping criteria. Use Level 1 for low-stakes tools, Level 2 for most services handling user data, and Level 3 for money or high-assurance systems. NIST SSDF (SP 800-218 v1.1, Feb 2022) and its generative-AI profile (SP 800-218A, July 2024) support the posture criteria: provenance, dependency and scanner practices.

- **Trust boundaries and threat model**
  - Finding: "Ingress `ws://…/join` accepts `playerId` from the message body; the trust boundary is client→server, but identity crosses it unverified."
  - Mechanical: the ingress enumeration (route and IPC extraction scripts, framework route dumps).
  - Judgment: which boundaries matter and what crosses them.
  - Two hypothetical examples of exactly this class: a game server that accepts the player ID from the client message and acts on it as is, so one client can impersonate another player; and a local server that timestamps ticket purchases itself while a global server decides draw eligibility from that timestamp, creating a timing-attack vulnerability (the fix is to compare against the authoritative server's time). Neither would be flagged by SAST; both are S1/S3 findings. The internal examples that prompted these were removed.
- **Authorization placement**
  - Finding: "14 of 61 routes lack the `requireAuth` middleware; 3 of those mutate tenant data (path:line each)."
  - Mechanical: a route-to-middleware matrix script. Semgrep rules can flag handlers that lack a decorator.
  - Judgment: object-level authorization (does the query scope by tenant or owner?), and whether "public" routes are intentional.
  - Severity scales sharply with multi-tenancy and money.
- **Secrets handling**
  - Mechanical: Gitleaks or TruffleHog over the working tree *and full history*, plus a grep of built client bundles for key patterns.
  - Judgment: whether a found value is live, whether a "public" key (Firebase or Stripe publishable keys) is actually meant to be public, and whether a rotation path exists.
- **Input parsing at ingestion**
  - Mechanical: SAST taint rules (injection, path traversal, unsafe deserialization such as `pickle`, `yaml.load`, Java `ObjectInputStream`), plus a script listing body-size and upload limits.
  - Judgment: whether a schema validator (zod, pydantic, Bean Validation) actually sits on every ingress.
- **Dependency and supply-chain posture**
  - Mechanical: SCA (osv-scanner, govulncheck, pip-audit, npm audit), lockfile presence, install-script inventory, CI action pinning (zizmor, actionlint).
  - Judgment: reachability, and whether a vulnerable function is actually called (govulncheck does this for Go; most others don't).
  - Real-world precedent: a compromised transitive npm dependency whose malicious payload hijacks the browser to redirect crypto-wallet transfers, served from an internal registry mirror and pulled in through an external dependency of a client application. It shows why the rubric must check transitive lockfile contents and internal registry mirrors, not just direct dependencies.
- **Sandboxing and process isolation**
  - Electron's official Security checklist covers several items:
    - context isolation (default since Electron 12)
    - `nodeIntegration` off (default since 5)
    - renderer sandbox (default since 20)
    - no `webSecurity: false`
    - a CSP
    - validating IPC senders
    - restricting navigation and `window.open`
    - no `shell.openExternal` with untrusted input
    - current Electron version
  - Electronegativity (Doyensec) checks most of these mechanically.
  - Judgment: what each `ipcMain.handle` channel lets a compromised renderer do. For mobile, the platform guides (Android and Apple) plus OWASP MASVS cover exported components and WebView JS bridges. For servers, look at container user, capabilities and read-only filesystem (Trivy config, Checkov, hadolint).
- **Sensitive data in logs**
  - Mechanical: Semgrep rules matching logger calls with `password|token|authorization|email|card` arguments, and whole-request logging.
  - Judgment: data classification. This is a policy input the profile must supply.
- **Scanner coverage and configuration (a meta-check)**
  - Finding: "CodeQL runs only on `src/`; `services/payments/` excluded; 212 findings bulk-suppressed by a baseline file dated 2024."
  - Fully mechanical: parse CI config, scanner configs and suppression counts.
  - Judgment: whether the set of scanners matches the stack.

**Severity scaling.** The same missing authz check is low on a single-user offline desktop tool, high on an internal multi-user tool, and critical on a public multi-tenant or money-handling service (see §9).

### 3. Security failure patterns specific to agent-written code

**Measured findings.** These figures come from the subagent's recall and are not re-verified in this session; confirm them against the primary sources.

- **BaxBench** (ETH Zurich SRI Lab, LogicStar.ai et al., arXiv 2502.11844, Feb 2025): 392 backend tasks, each with functional tests and expert-written end-to-end exploits.
  - The best model reached about 62% functional correctness, and about half of the correct solutions were exploitable.
  - The weaknesses included missing authorization (CWE-284/863) and resource exhaustion (CWE-400). These are found by exploit, not pattern.
  - Implication: pattern SAST will under-report on agent code.
- **Veracode 2025 GenAI Code Security Report** (Jul 2025; vendor, own SAST):
  - More than 100 LLMs, 80 tasks, 4 CWEs. 45% of samples introduced a vulnerability.
  - XSS (about 86% failure) and log injection (about 88%) were worst. Java was worst by language (about 72%).
  - Security pass rate was flat across newer and larger models.
  - Caveats: only 4 CWEs, and the vendor's own tool.
- **Package hallucination** (Spracklen et al., "We Have a Package for You!", USENIX Security 2025):
  - 576,000 code samples from 16 LLMs. 19.7% of recommended packages did not exist.
  - The rate was about 5.2% for commercial models vs about 21.7% for open models.
  - 43% of hallucinated names recurred across all 10 re-runs. That repeatability is what makes "slopsquatting" exploitable.
  - SAST does not catch this. A registry-existence and age check does.
- **Fu et al.** (ACM TOSEM 2025): of 733 Copilot, CodeWhisperer and Codeium snippets found in real GitHub projects, about 29.5% of Python and 24.2% of JS snippets had CWEs, spanning 43 CWE types. These were found by CodeQL and language SAST, so the scanner-detectable share is real and non-trivial.
- **GitGuardian State of Secrets Sprawl 2025** (Mar 2025; vendor, correlational): 6.4% of Copilot-enabled repos leaked at least one secret vs 4.6% across all public repos.
- **Apiiro "4x Velocity, 10x Vulnerabilities"** (Sept 2025; vendor, proprietary method): privilege-escalation paths up about 322% and design flaws up about 153% in AI-assisted code at Fortune-50 firms. Treat as unverified and unreplicated.

**Anecdote (do not use for calibration, only for check design).**

- Prompt-injection "rules file" backdoors in agent config files (Pillar Security disclosure, Mar 2025).
- The Nx "s1ngularity" npm compromise (Aug 2025), whose payload invoked locally installed AI coding CLIs to hunt for secrets.
- Practitioner reports of agents disabling tests, stubbing auth "temporarily", or widening CORS to make an error disappear.

**Synthesis.**

- **Scanner-caught:** injection classes (CWE-78/79/89/94), weak crypto and randomness (CWE-327/330), hardcoded secrets (CWE-798), known-vuln dependencies.
- **Review-needed:**
  - missing or misplaced authz
  - client-trusted identity
  - unbounded resource use
  - permissive defaults chosen to "make it work" (CORS `*`, `verify=False`, `rejectUnauthorized: false`, `nodeIntegration: true`)
  - nonexistent or brand-new dependencies
  - error handlers that fail open
  - security controls present in one copy of duplicated code but missing in another

### 4. Performance from static reading

Each check below gives the recipe, its cost by load and device, and the point where acting on it becomes premature optimization.

- **P1 Fan-out.**
  - Recipe: extract data calls per route or screen (fetch/axios/SWR/React Query/tRPC call sites, reachable from each route component), and flag `await` inside loops or chains of dependent awaits.
  - Cost: each serial round trip costs one RTT. Lighthouse's mobile throttling assumes 150 ms RTT, so 6 serial calls is about 0.9 s before any server time. On desktop broadband it is negligible.
  - Premature when calls run in parallel, total fewer than about 4, and the profile is desktop/LAN.
- **P2 N+1.**
  - Recipe: an ORM access inside a loop over query results (Django `.all()` without `select_related`/`prefetch_related`, SQLAlchemy lazy loads, JPA `@OneToMany` lazy access in loops, Go `db.Query` in `for`). Confirm with query-count instrumentation.
  - Cost: linear in list size × concurrency, which pressures the connection pool.
  - Premature when lists are bounded and small (for example, a 5-item settings page).
- **P3 Unbounded reads.**
  - Recipe: list endpoints without `limit`/cursor; `findAll()`, `.all()`, `SELECT` without `LIMIT`; responses that serialize whole tables.
  - Cost: grows with data, not users, so it is a time bomb even at 2k users.
  - Premature only when the profile states a hard cap on the data.
- **P4 Blocking I/O on hot path.**
  - Recipe: lint for `fs.*Sync`, `child_process.execSync` and the Electron main process doing disk or crypto work; the Python `ASYNC` rules in Ruff (blocking calls in async functions); `time.sleep` in handlers; Java blocking calls in reactive chains.
  - Cost: in Node or Electron main, one blocked tick stalls every client or the whole UI. In Electron that means a frozen window.
  - Premature in one-shot CLIs and startup-only code.
- **P5 Bundle weight.**
  - Recipe: build once, then run a source-map-based analyzer. Diff against the budget, list the largest modules and duplicate packages.
  - Cost: JS parse and execute time scales with CPU. Low-end Android is several times slower than a developer laptop, which is why Lighthouse applies a 4× CPU slowdown on mobile.
  - Premature for Electron apps loading from disk (look at startup instead), and for internal desktop-only tools.
- **P6 Re-renders.**
  - Recipe: static lint (`react-hooks/exhaustive-deps`), context providers with object literals as `value`, inline object/array/function props to memoized children, large lists without virtualization.
  - Confirmation needs the React DevTools Profiler.
  - Premature for small trees. React's own docs say memoization is only worthwhile when re-renders are noticeably slow.
- **P7 Polling vs push.**
  - Recipe: `setInterval` + fetch, and the interval × client count.
  - Cost: 100k clients polling every 2 s is 50k req/s of mostly empty responses (arithmetic). On the push side, flag O(n) broadcast loops per event, which become O(n²) when every client's action is broadcast to all.
  - Premature at small n with long intervals.
- **P8 Caching.**
  - Recipe: repeated identical expensive calls per request; caches without TTL or size bound (`new Map()` at module scope, `functools.lru_cache(maxsize=None)`); cache writes with no invalidation on the corresponding mutation path.
  - Stale-cache bugs are correctness findings, too.
- **P9 Memory retention.**
  - Recipe: `addEventListener`/`on(` without matching removal, `setInterval` without clear in effects, module-level growing collections, IPC listeners registered per window.
  - Confirmation needs a heap snapshot diff.
  - Matters for long sessions; mostly irrelevant for request-scoped serverless.
- **P10 Resilience under load.**
  - Recipe:
    - HTTP clients without timeouts (Python `requests` without `timeout=` is a Bandit and Ruff rule)
    - retries without backoff or jitter
    - pool sizes vs the profile's concurrency (Little's Law)
    - WebSocket reconnect without jitter, which causes a thundering herd after a deploy

### 5. Performance claims that must be measured

The following need measurement before they become findings:

- any latency or frame-time claim
- "this re-renders too often"
- memory leak suspicions
- query slowness (plans depend on data distribution and indexes)
- throughput or capacity claims

Cheapest credible measurement for each:

- **Bundle:** a production build + analyzer. Deterministic and cheap.
- **Mobile web:** Lighthouse CLI against a local production build with its default mobile throttling. Run 3–5 times and report the median, because Lighthouse scores vary run to run (Google's own guidance on variability).
- **Queries:** `EXPLAIN (ANALYZE, BUFFERS)` on a seeded local DB, plus query-count capture for one request.
- **Server:** a 60–120 s k6 or Locust run against a local or isolated stack at a stepped arrival rate, recording p50/p95/p99 and the knee.
- **Hot spots:** a sampling profiler on one representative flow (py-spy, async-profiler, `go tool pprof`, `node --cpu-prof`).
- **Production telemetry read:** if read-only access to APM or RUM is approved, it outranks everything above.

**Reporting an unmeasured static candidate.** Report it as "Candidate, unmeasured", with:

- the anchor (path:line)
- the static arithmetic (for example "N+1: 1 + n queries, n = page size 50 → 51 queries/request")
- the budget it would breach *if* the assumption holds
- the exact measurement that would confirm or refute it

Severity is capped at Medium until measured, unless the arithmetic alone breaches a stated budget. A useful convention is for each finding to state its cost: who pays (end user, analytics, server, support, team) and how often. A cost that the orchestrator did not verify is marked "Not checked".

### 6. Platform specifics

- **Web front-ends on mobile:**
  - Budgets: Core Web Vitals at p75 and a labelled JS byte budget.
  - Checks: P1, P5, P6, image weight, third-party scripts.
  - Security: CSP, XSS sinks, token storage (localStorage vs httpOnly cookie), secrets in bundles.
- **Desktop (Electron):**
  - Performance: main-process blocking (P4), startup time (`require` cost at boot), renderer memory over long sessions (P9), number of BrowserWindows/BrowserViews.
  - Security dominates through the Electron checklist and IPC surface. A renderer XSS becomes RCE if isolation is off.
- **Backends with many concurrent users:**
  - Checks: P2, P3, P8, P10, connection-pool math, rate limits (S10), authz (S2).
- **Real-time and multiplayer:**
  - Checks: server authority (S1) is the top security check; tick or broadcast cost (P7); per-connection memory; reconnect storms; message validation and size limits (S4); rate limiting per connection.

**2,000 vs 100,000 concurrent users.** The rubric gains criteria rather than changing thresholds. The arithmetic below is derivation, not benchmark.

- **At 2k**, one well-sized instance and a single Postgres usually suffice. N+1 and polling are Medium unless lists are large.
- **At 100k**, the following become applicable:
  - per-connection memory (100k × 50 KB = about 5 GB per fleet just for socket state at that assumed size)
  - file-descriptor and ephemeral-port limits
  - DB connection limits (Postgres `max_connections` defaults to 100, so pooling and a pooler are mandatory)
  - broadcast fan-out cost
  - backplane and pub/sub for horizontal scale-out
  - sticky sessions
  - reconnect-storm jitter
  - cache-stampede protection
- **Severity shifts at 100k:** the same N+1 or polling pattern moves up one or two levels. Rate-limit absence becomes High because abuse is economically motivated at scale.

### 7. Other quality attributes

- **Reliability/resilience: fold into performance.** Timeouts, retries, backpressure and pool exhaustion share the detection recipes and the load model. Google SRE treats latency and availability as one SLO family. Make it a named criterion group ("P10 Resilience under load") rather than a dimension.
- **Observability: fold into both, as an enabling criterion.**
  - Performance: "can the flows in the profile's scenarios be measured in production" (traces, RED metrics).
  - Security: "are auth failures, privilege changes and admin actions logged without sensitive data". This is the OWASP Top 10 "Security Logging and Monitoring Failures" category, and ASVS has a logging chapter.
  - Observability gaps surface as security findings in practice: for example, transaction updates that overwrite `updated_at` make it impossible to trace steps, which argues for a system-wide audit trail, and a SIEM integration may be missing.
- **Accessibility: a separate dimension, gated on the profile.**
  - Its standard (WCAG 2.2, W3C Recommendation Oct 2023), tooling (axe-core, Lighthouse a11y) and failure modes don't overlap with security or performance.
  - The EU's European Accessibility Act has applied since 28 June 2025, which makes it a legal stake for consumer-facing products in the EU.
  - Deque reports that automated testing finds about 57% of accessibility issues (vendor study, 2021). Treat it as unverified. Either way, judgment is needed.
  - Skip it for internal tools or headless services.

### 8. Deterministic tooling per stack

**Safety rules common to all stacks:**

- Run tools from a pinned container digest or a pinned ephemeral runner, with the repo mounted read-only (`-v "$PWD":/src:ro`) and `--network none` wherever the tool supports an offline DB.
- Never run `npm install` or `pip install` in the audited tree. If a build is needed, build in a disposable git worktree, and use `npm ci --ignore-scripts` where possible.
- Ephemeral runners include `npx --yes pkg@x.y.z`, `uvx tool@x.y.z`, `pipx run tool==x.y.z` and `go run module@vX.Y.Z`.

**Tools that send data off the machine by default:**

- `npm audit` sends the dependency tree to the registry.
- `pip-audit` queries PyPI/OSV.
- osv-scanner queries osv.dev unless run with `--offline` and pre-downloaded DBs.
- Semgrep downloads registry rules for `--config p/…` and sends anonymous metrics unless `--metrics=off`. Use local rule files for full offline operation.
- TruffleHog *verifies* candidate secrets by calling provider APIs. Use `--no-verification`, or get approval.
- Trivy and Grype download vulnerability DBs. That is inbound, not code upload, but it still needs network.

**CodeQL licensing:** the CLI is free for open-source and academic use. Private-code use needs a GitHub Advanced Security licence. Check this before adopting it.

**Cross-stack**

| Check | Tool | What it measures | Executes project code? | Leaves the machine? | Pinned, no-install run |
|---|---|---|---|---|---|
| S5 Secrets (tree + history) | Gitleaks | Regex/entropy secrets in files and git history; moderate FPs (test fixtures) | No | No | `docker run --rm --network none -v "$PWD":/repo:ro zricethezav/gitleaks@sha256:… detect -s /repo` |
| S5 Secrets | TruffleHog | 800+ detectors; can verify liveness | No | Only if verification on | Pinned image; `--no-verification` |
| S6 SCA | osv-scanner | Known vulns from lockfiles (all ecosystems); low FP, no reachability except Go | No | Yes, unless `--offline` | `go run github.com/google/osv-scanner/v2/cmd/osv-scanner@vX` or pinned image |
| S6 SCA / SBOM | Trivy (fs), Syft + Grype | Vulns, licences, misconfig, SBOM | No | DB download | Pinned image, read-only mount |
| S6 CI posture | zizmor, actionlint | Unpinned actions, injection in workflows, excessive permissions | No | No | `uvx zizmor@X .github/workflows` |
| S7 Containers/IaC | hadolint, Checkov, Trivy config | Root user, privileged, open ports, IaC misconfig | No | No (Checkov: disable platform upload) | Pinned images |
| S1–S4, S8 SAST | Semgrep CE | Pattern and intra-file taint; FP moderate, tunable; custom rules for authz matrices and log-sinks | No | Rules/metrics only (see above) | `uvx semgrep@X --metrics=off --config ./rules` |
| S1–S4 SAST (deep) | CodeQL CLI | Inter-procedural taint; lower FP; compiled languages require a build | Build only (compiled langs) | No | Pinned CLI bundle; licence check |

**JavaScript / TypeScript (web, Node, Electron)**

| Check | Tool | Measures | Executes code? | Off-machine? | Run |
|---|---|---|---|---|---|
| S7 Electron | Electronegativity | Electron checklist violations (nodeIntegration, contextIsolation, openExternal…); some FPs on dynamic config | No | No | `npx --yes @doyensec/electronegativity@X -i /src` |
| S2, S4, S8 | Semgrep JS/TS rules; eslint-plugin-security | Sinks, `eval`, unsafe regex, child_process | No | No | Ephemeral npx with a standalone config (`--no-eslintrc`/flat config outside the repo) |
| S6 | lockfile-lint, osv-scanner, `npm ls` | Registry/host pinning, integrity hashes, vulns | No | osv: see above | npx pinned |
| P5 | source-map-explorer, webpack-bundle-analyzer / rollup-plugin-visualizer (static mode), size-limit | Bytes per module, duplicates, budget breaches; deterministic | Build runs project build | No | Build in worktree; `npx source-map-explorer@X dist/*.js --json` |
| P4, P6, P9 | ESLint (`no-sync` patterns, `react-hooks/exhaustive-deps`), custom AST script | Sync calls, effect deps, listeners without cleanup | No | No | npx pinned |
| P1 | Custom AST script (ts-morph/Babel) | Data calls per route, awaits in loops, serial chains | No | No | Script in the audit tooling repo |
| P5/P6 measured | Lighthouse CLI, Chrome DevTools Performance, React DevTools Profiler | CWV lab metrics, long tasks, render counts | Yes (runs app) | No (local URL) | `npx lighthouse@X http://localhost:… --preset=perf` (mobile default) |
| Node hot spots | `node --cpu-prof`, `--heap-prof`, Clinic.js, 0x | CPU flame graphs, event-loop delay, heap | Yes | No | Built-in flags; npx pinned |
| Load | k6, autocannon | Throughput, latency percentiles, knee | Hits running app | No (k6 Cloud is opt-in) | Pinned k6 image, local target |

**Python**

| Check | Tool | Measures | Executes code? | Off-machine? | Run |
|---|---|---|---|---|---|
| S4, S5, S8 | Bandit; Ruff `S` (flake8-bandit) rules | `pickle`, `yaml.load`, `subprocess(shell=True)`, `verify=False`, missing `timeout=`; moderate FP | No | No | `uvx bandit@X -r /src -f json` |
| S6 | pip-audit, osv-scanner | Vulns in requirements/locks | pip-audit may resolve deps (can run setup code if not given a lock with `--no-deps`/`-r` + `--disable-pip`) | Yes (queries) | `uvx pip-audit@X -r requirements.txt --disable-pip --no-deps` |
| P4 | Ruff `ASYNC` rules | Blocking calls inside `async def` | No | No | `uvx ruff@X check --select ASYNC,S` |
| P2 | nplusone, django-debug-toolbar, SQLAlchemy echo / event hooks; custom AST script | N+1 at runtime; ORM access in loops statically | Runtime ones: yes | No | Run in isolated env from worktree |
| Profile | py-spy, Scalene, memray, pyinstrument | CPU sampling, memory allocation | Yes (attaches/runs) | No | `uvx py-spy@X record -o prof.svg -- python app.py` |
| Load | Locust | Throughput, latency percentiles | Hits app | No | `uvx locust@X -f locustfile.py --headless` |

**JVM**

| Check | Tool | Measures | Executes code? | Off-machine? | Run |
|---|---|---|---|---|---|
| S1–S4 | SpotBugs + FindSecBugs; PMD; Semgrep | Injection, deserialization, crypto; FindSecBugs is FP-prone on taint | Needs compiled classes | No | Pinned jars with checksum, run against build output in worktree |
| S6 | OWASP Dependency-Check; osv-scanner; Trivy | CVEs via CPE matching (Dependency-Check: notable FPs from CPE mismatch) | No | NVD download | Pinned image, cached DB |
| P2 | Hibernate statistics (`hibernate.generate_statistics`), datasource-proxy; custom AST for lazy collections in loops | Query counts per request | Runtime: yes | No | Test profile in worktree |
| Profile | JDK Flight Recorder + JMC, async-profiler | CPU, allocation, lock contention | Yes | No | Built into JDK (`-XX:StartFlightRecording`) |
| Load | Gatling, k6 | Latency percentiles | Hits app | No | Pinned bundle |

**Go**

| Check | Tool | Measures | Executes code? | Off-machine? | Run |
|---|---|---|---|---|---|
| S6 | govulncheck | Vulns *reachable* from call graph; very low FP | No (static analysis; loads packages) | Queries vuln.go.dev unless `-db file://` | `go run golang.org/x/vuln/cmd/govulncheck@vX ./...` in worktree |
| S1–S5 | gosec; Semgrep; staticcheck | Injection, weak crypto, TLS `InsecureSkipVerify`, unchecked errors; gosec moderate FP | No | No | `go run github.com/securego/gosec/v2/cmd/gosec@vX ./...` |
| P4/P9 | staticcheck, `go vet`, custom: goroutine without ctx/cancel, unbounded channels | Leaks, misuse | No | No | `go run honnef.co/go/tools/cmd/staticcheck@vX` |
| Profile | pprof (CPU, heap, goroutine, block, mutex), `go test -bench`, trace | Hot spots, goroutine leaks | Yes | No | Built-in |
| Load | k6, vegeta | Latency percentiles | Hits app | No | `go run github.com/tsenart/vegeta@vX` |

**Custom scripts where no tool exists**, all read-only AST or regex, emitting path:line:

1. Route × auth-middleware matrix (S2).
2. Ingress inventory: routes, IPC channels, consumers, webhooks (S3).
3. Client-trusted-identity detector: request fields named `userId|playerId|tenantId|role` flowing into queries or session state without a session lookup (S1).
4. Registry existence and age check for every declared dependency, which flags packages that don't exist or were published in the last N days (slopsquatting defense).
5. Per-route data-call fan-out and serial-await counter (P1).
6. Loop-contains-query/remote-call detector (P2).
7. List-endpoint-without-limit detector (P3).
8. Interval × client-count polling calculator (P7).
9. Unbounded cache/collection detector (P8).
10. Listener/timer add-without-remove pairing (P9).
11. Pool-size vs profile concurrency check via Little's Law (P10).
12. Scanner-coverage report: which paths and languages each configured scanner covers, and suppression counts (S9).

### 9. Severity calibration

**Published schemes worth adopting.**

- **CVSS v4.0** (FIRST, Nov 2023) for scanner-sourced vulnerabilities. Its Environmental and Threat metric groups are the formal way to adjust a base score to the profile.
- **OWASP Risk Rating Methodology** (likelihood × impact, with business-impact factors) for rubric findings. It maps naturally onto profile facts: financial damage, reputational damage, non-compliance and privacy violation come straight from the profile's stakes.
- **CISA SSVC** (decision trees: exploitation, exposure, automatable, mission/well-being impact) if the audit needs act/track decisions instead of scores.
- **EPSS** (FIRST) to prioritize dependency CVEs by exploitation probability.
- **Performance** has no published severity standard. Use budget breach × path frequency × load tier (rubric below; labelled as this report's proposal).

**Same finding, different profile.** Take a missing object-level authorization check:

| Profile | Severity | Why |
|---|---|---|
| Single-user desktop tool, deployed in lockstep, no network | Info/Low | No other principal to escalate to |
| Internal multi-user tool, trusted staff | Medium | Insider misuse; audit trail matters |
| Public multi-tenant service with personal data | Critical | Cross-tenant disclosure is exploitable at scale |
| Real-money/prize game | Critical | Monetary motive raises likelihood; without monetary value in return, the probability of exploitation is lower |

## Rubric tables

### Security rubric

| Criterion | What a finding looks like | Mechanical / judgment | Detector | Static / measured | Severity by profile | Over-engineering when… | Applies when |
|---|---|---|---|---|---|---|---|
| S1 Server authority | Client-supplied `playerId`/`userId` used as identity (path:line), with exploit path | Judgment, script-assisted | Custom identity-flow script; Semgrep taint | Static | Low (single user) → Critical (money, multi-tenant) | Demanding server authority for cosmetic, client-only state | Multi-user, auth, money, multiplayer |
| S2 Authz placement | Route matrix shows unguarded mutating routes; queries not scoped by tenant | Mechanical matrix + judgment on object-level | Route × middleware script; Semgrep | Static | Med (internal) → Critical (public multi-tenant) | Per-object ACLs on a single-user tool | Any roles or multiple users |
| S3 Trust boundaries / threat model | Ingress list with STRIDE gaps; asset reachable across boundary without control | Judgment on mechanical inventory | Ingress inventory script | Static | Scales with exposure × asset value | Full STRIDE on internal batch jobs with no untrusted input | Always (depth by stakes) |
| S4 Input parsing | Unvalidated body/file/URL reaches sink; no size limits; unsafe deserialization | Mostly mechanical | Semgrep, CodeQL, Bandit, gosec, FindSecBugs | Static | Low (local CLI) → High/Critical (public) | Schema validation on internal function calls | Network-facing or file-ingesting |
| S5 Secrets | Live credential in tree/history/bundle | Mechanical + judgment (is it live, is it public-by-design) | Gitleaks, TruffleHog `--no-verification`, bundle grep | Static | High whenever live; Critical for prod/payment keys | Flagging publishable keys designed to be public | Always |
| S6 Supply chain | No lockfile; known-exploited CVE reachable; unpinned CI actions; package nonexistent or <30 days old | Mechanical; judgment on reachability | osv-scanner, govulncheck, pip-audit, zizmor, registry-age script | Static | Scales with distribution (public bundle/installer highest) + EPSS | Chasing unreachable dev-only CVEs in a lockstep internal tool | Always |
| S7 Isolation | `nodeIntegration: true`, `contextIsolation: false`, IPC handler runs arbitrary paths; container runs as root | Mechanical + judgment on IPC capability | Electronegativity, hadolint, Trivy config, Checkov | Static | High/Critical if renderer loads remote content | Hardening a sandbox that loads only local, signed content (still fix defaults, lower severity) | Electron, hybrid mobile, containers |
| S8 Sensitive logging | Token/password/PII passed to logger; full request bodies logged | Mechanical candidates + judgment on classification | Semgrep log-sink rules | Static | Med → High with regulated data | Redaction for non-sensitive internal IDs | Personal, auth or payment data |
| S9 Scanner coverage | Scanner absent for a language; paths excluded; mass suppression | Mechanical | CI/config parse script | Static | Med generally; High if high-stakes paths uncovered | Requiring three overlapping SASTs | Always |
| S10 Abuse/resource limits | No rate limit on auth or purchase; unbounded upload; regex DoS | Mechanical candidates + judgment | Semgrep, config scan; custom | Static (confirm by short local test) | Low (internal) → High (public, money) | Rate-limiting localhost-only admin tools | Public endpoints |

### Performance rubric

| Criterion | What a finding looks like | Mechanical / judgment | Detector | Static / measured | Severity by profile | Premature when… | Applies when |
|---|---|---|---|---|---|---|---|
| P1 Fan-out | Route makes 9 calls, 5 serial (path:line list) | Mechanical | Fan-out AST script; DevTools network panel | Static count, measured latency | Med on mobile/high-RTT; Low on desktop LAN | Fewer than about 4 parallel calls | Mobile, remote clients |
| P2 N+1 | ORM access in loop; 51 queries for a 50-row page | Mechanical candidate; measured count | AST script; nplusone; Hibernate stats; query log | Static → measured | Med at 2k; High at 100k or large lists | Bounded tiny lists | DB-backed servers |
| P3 Unbounded reads | List endpoint without limit; full-table serialization | Mechanical | Script; Semgrep | Static | High if data grows unbounded, at any load | Data has a stated hard cap | Growing datasets |
| P4 Blocking hot path | `readFileSync` in Electron main/IPC handler; `requests.get` in `async def` | Mechanical | ESLint, Ruff ASYNC, custom | Static; measure stall | High for Electron main and Node servers | Startup-only or CLI code | Event-loop/UI-thread runtimes |
| P5 Bundle weight | 1.4 MB compressed JS on entry; duplicate libs | Mechanical | source-map-explorer, size-limit | Measured (build) | High on low-end mobile; Low on Electron | Desktop/internal or behind-login admin tools | Web, especially mobile |
| P6 Re-renders | Context value literal re-renders 300-node tree per keystroke | Candidate mechanical; confirm by profiler | ESLint hooks rules; React Profiler | Needs measurement | Med on low-end mobile/real-time UIs | Small trees, no observed jank | Interactive SPAs |
| P7 Polling/broadcast | 2 s poll × 100k = 50k req/s; O(n) broadcast per event | Mechanical arithmetic | Interval script; profile numbers | Static arithmetic | Low at 2k/long interval → High at 100k | Few clients, long intervals | Real-time, many clients |
| P8 Caching | Unbounded module-level cache; no invalidation on update | Mechanical candidates + judgment | Custom script; Semgrep | Static | Med (memory/staleness); High if staleness affects money | Adding caches before measured repeat cost | Read-heavy |
| P9 Retention | Listener added per window, never removed | Candidate mechanical; heap diff confirms | Pairing script; heap snapshots | Needs measurement | High for long-lived desktop/kiosk/game server | Short-lived serverless | Long sessions |
| P10 Resilience | HTTP client without timeout; reconnect without jitter; pool 10 vs required 200 | Mechanical | Bandit/Ruff timeout rule; pool-math script | Static; confirm via short load test | Med at 2k → High at 100k | Single-dependency internal tools | Services with dependencies or many connections |

## Recommendations

**Minimal-profile checklist (block the dimension if any line is missing).**

*Security*

- [ ] Assets: what is valuable (money/prizes, PII, credentials, admin control, IP)
- [ ] Actors: who is untrusted (anonymous internet, authenticated users, other tenants, partners, local users)
- [ ] Exposure: public internet, partner network, internal only, offline
- [ ] Auth model: none, single-user, multi-user, multi-tenant, roles
- [ ] Deploy and distribution model: server, desktop installer (lockstep or auto-update), mobile store, web bundle
- [ ] Data classification for logs (is a policy present?)
- [ ] Regulatory stakes that change the rubric (payments, gaming, personal data), not certification

*Performance*

- [ ] Peak concurrent users and peak request/message rate
- [ ] Device class and network (for example "low-end Android, 4G"; "corporate desktop, LAN")
- [ ] At least one response measure per dominant attribute (for example p95 latency, CWV at p75, frame time, startup time)
- [ ] Data volume growth (rows per tenant per year)
- [ ] Session length (minutes vs days)
- [ ] Whether measurement is permitted: local run, isolated stack, read-only telemetry

**Agent-specific failure patterns and defenses**

| Pattern | Evidence status | Defense in the audit |
|---|---|---|
| Missing or misplaced authorization; client-trusted identity | Measured (BaxBench: authz/CWE-284/863 among exploited classes) | S1/S2 scripts + mandatory judgment; verifier tries to construct the exploit path |
| Injection/XSS/log injection | Measured (Veracode 2025, vendor; Fu et al. 2025) | Scanner-first (Semgrep/CodeQL); rubric only checks coverage (S9) |
| Hallucinated or brand-new dependencies | Measured (Spracklen et al., USENIX Sec 2025) | Registry existence + age script; lockfile review |
| Hardcoded secrets | Measured, correlational (GitGuardian 2025, vendor) | Gitleaks/TruffleHog over history and built bundles |
| Permissive defaults chosen to "make it work" (`verify=False`, CORS `*`, `nodeIntegration: true`) | Anecdote, plus mechanism consistent with measured data | Semgrep rule pack of "make-it-work" flags; `git log -S` to find when they appeared |
| Resource exhaustion / unbounded work | Measured (BaxBench CWE-400) | P3/S10 scripts |
| Duplicated code with inconsistent controls | Anecdote | Clone detection (for example jscpd) + diff of security-relevant calls across clones |
| Weakened tests or stubbed checks | Anecdote | History scan for deleted assertions or `skip` added in security-relevant tests |
| Prompt-injected agent config (rules files, MCP config) in repo | Anecdote (Pillar, Mar 2025) | Inventory `.cursor/`, `AGENTS.md`, `CLAUDE.md`, MCP configs; scan for hidden Unicode |

**Adoption order.**

1. Ship S9, S5, S6 and the S2 route matrix first. They are fully mechanical, high-yield and safe to run.
2. Add the ingress inventory and S1 script next. Those catch the class that measured studies say scanners miss.
3. On performance, ship P3, P4, P5 and P7 first: mechanical and cheap.
4. Keep P6 and P9 as candidates until a profiler run is approved.
5. Require the verifier to reproduce the static arithmetic or the exploit path for every High or Critical finding.

## Caveats

- **No live web verification in this session.** Standards, thresholds and tool flags are stated from established public documentation as of my knowledge. Pin and check each tool's current flags when building the runner.
- The agent-code statistics in §3 were relayed by a subagent without browsing. The Veracode, GitGuardian and Apiiro figures are vendor claims and are not independently replicated. Do not use them for severity calibration. Use them only to justify which checks exist.
- **Thresholds and labels:**
  - Core Web Vitals and RAIL values are vendor (Google) guidance derived from field data.
  - JS byte budgets are expert opinion.
  - Every load figure for 2k vs 100k is arithmetic from stated assumptions, not a benchmark.
  - The performance severity scheme is this report's proposal; no published standard exists.
- Internal examples were removed; the remaining examples are hypothetical and illustrate finding classes and conventions, not prevalence.
