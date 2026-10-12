# Scans — detection recipes for the extractors

Each extractor counts; it does not judge. Recipes are stated language-agnostically
first; concrete tools follow per stack. **Detect the stack and look up current tools
before running anything** — the names below are examples known to work in late 2026,
not a fixed toolchain. When no tool exists, the recipe is small enough to script.

Write every output under `work/facts/`, machine-readable where possible (JSON or
TSV), plus a ten-line human summary. Save every script you wrote and every exact tool
command (with versions) under `work/scripts/`, so the next audit reruns the identical
scan; a script left in a temp directory is lost evidence.

## Tool-first, safely

1. **Order of preference:** the project's own configured tools (its linter, type
   checker, dead-code and security scanners, as the gate manifest records them) →
   an established tool for the stack → a script you write. A model reading files to
   count something is never on this list.
2. **Run the project's own tools with the project's own config** first; their output
   is what the gates see. Run an extra tool only to measure something the project's
   tools do not.
3. **Safety rules for any tool:**
   - pin the exact version (`npx --yes <tool>@<x.y.z>`, `pipx run <tool>==<x.y.z>`,
     a pinned container image) — never `latest`;
   - never install into the audited repo, its lockfile or its dependency directory;
     run from a cache, a temp directory or a container;
   - read-only against the tree; anything that writes or executes the project's code
     (tests, builds, profilers, load generators) runs in an isolated worktree, alone;
   - no network upload of code or findings to a third-party service without the
     user's approval; prefer tools that run fully locally;
   - no credentials: never feed a tool the project's secrets or environment files.
4. **If no safe tool exists**, write the smallest script that answers the question,
   save it under `work/scripts/`, and say in the summary that the number is from a
   custom script.

## Graph extractor

**Recipe.** Start from declared structure — workspaces, packages, build targets — then
descend to directories and files. Keep edge types separate: static import, build
reference, runtime registration (routing, dependency injection, plugin registries),
inheritance, test-only. Collapsing them hides real differences. Compute:

- strongly connected components; cyclic-node count; largest SCC;
- fan-in and fan-out per module, as repo percentiles;
- violations of any boundary rules the repo declares (lint config, structural tests,
  architecture tests), counted per rule.

**Tools.**

| Stack | Graph and boundary tools |
|---|---|
| JS / TS | dependency-cruiser, madge, eslint-plugin-boundaries, Nx module boundaries, Steiger (feature-sliced) |
| Python | import-linter, pydeps, grimp |
| JVM | ArchUnit, jdeps |
| .NET | NetArchTest, ArchUnitNET |
| Ruby | Packwerk |
| Go | `go list -deps`, go-arch-lint |
| Any | ctags or tree-sitter queries scripted into an edge list |

## History extractor

**Recipe.** Over the last twelve months (the run's range for `run` mode), rename-aware:

- **churn** per file (commits and changed lines);
- **complexity** per file (cyclomatic or cognitive, any tool), then **hotspot score** =
  churn × complexity, ranked; top 5–10% are hotspots;
- **co-change**: for each pair of files or modules across a boundary, shared commits ÷
  commits of the less-changed one; bulk commits (more than ~50 files) excluded;
- **author classes**: split bot, formatter, dependency-update and agent commits from
  human ones by author identity, commit trailers and message patterns. Report hotspots
  with and without automated churn.

**Tools.** `git log --numstat --follow`, code-maat, CodeScene (if licensed), lizard /
radon / any complexity counter. Treat tool default thresholds as defaults, not
evidence.

## Gates extractor

**Recipe.** Build the canonical gate manifest (fields in `rubric-gates.md`) from CI
definitions, task runners, package scripts, pre-commit hooks, tool configs and the
agent instruction files. Read the required-checks list from the hosting platform's
API; it is not in source. Then:

- diff the manifest against the baseline's manifest, field by field;
- count suppressions by mechanism, directory and age (blame the line for its date);
- count skipped, focused and quarantined tests with age;
- count escape hatches (untyped values, casts, non-null assertions, ignore comments),
  separately at ingestion points;
- compare each gate's local command (scripts, hooks, instruction files) with CI's;
- resolve every command and path the instruction files name against the tree;
- list commits in range that touch tests or gate config **and** implementation.

**Patterns to count** (extend per stack):

| Kind | Examples |
|---|---|
| Suppressions | `@ts-ignore`, `@ts-expect-error`, `eslint-disable`, `# noqa`, `# type: ignore`, `//nolint`, `NOSONAR`, `@SuppressWarnings`, `#[allow(` |
| Skips | `.skip`, `xit`, `it.only`, `describe.only`, `@Disabled`, `@Ignore`, `pytest.mark.skip`, `xfail`, `t.Skip` |
| Failure policy | `continue-on-error`, `allow_failure`, `|| true`, `--max-warnings`, `--passWithNoTests`, retry counts |
| Escape hatches | `any`, `as X`, `!.`, `unknown as`, `cast(`, `unwrap()`, `# type: ignore` |

## Inventories extractor

**Recipe and tools per inventory.**

| Inventory | Recipe | Example tools |
|---|---|---|
| Abstractions per concern | list definitions and imports per concern class — HTTP client, error type, logger, state store, config loader, event bus, date library, validation library | grep/AST, package manifests (two libraries for one job) |
| Ingestion points | every place external data enters: request handlers, queue consumers, storage reads, external API clients, IPC, URL and search params, persisted client storage | AST queries on framework entry points |
| Public surface | exported symbols vs symbols imported from outside the module; wildcard re-exports | API Extractor, knip, ts-prune, `cargo public-api`, griffe, Go `apidiff` |
| Catch-and-default | catch / except / error branches whose body returns a literal, an empty collection, null, or nothing; `.catch(() => default)` | AST queries; Ruff `BLE001`/`S110`/`E722`; ESLint `no-empty`; Go `errcheck` |
| Optional-then-guarded | optional or nullable parameters guarded, asserted or dereferenced within the first lines of the body; required → optional changes in history | AST queries; `git log -p` on signatures |
| Single-implementation interfaces | interfaces and abstract types with one implementer | AST queries |
| Pass-through wrappers | bodies consisting of one call forwarding the same arguments | AST queries |
| Dead code | reachability from entry points, after listing dynamic registration | knip, ts-prune, vulture, jdeps, `deadcode` (Go) |
| Clone families | token or AST clones; mark clones crossing module boundaries | jscpd, PMD CPD, NiCad |
| Schemas | API, event and storage schemas with their versions; migration order | oasdiff, `buf breaking`, squawk, strong_migrations |
| Front-end | state-ownership marks per concept; fetch mechanisms per call site; raw search-param reads; raw primitives and hard-coded tokens; prop names across the component library | react-scanner, stylelint, AST queries |

## Security extractor

Runs when the security dimension is in the audit plan. **Pin every tool to its current
release at run time and record the version** — the commands below use `@<pin>`
placeholders on purpose; verify flags against the pinned version's help before use.

**Recipe.**

- **Scanner manifest** (S9): every scanner the project already runs, from the gate
  manifest — name, version, rule version, include/exclude paths, languages, lockfiles
  covered, git-history coverage, network mode, whether it blocks a merge. Then rerun
  each locally and pinned over the **whole repository**, not a diff.
- **Entry-point graph** (S3): routes, IPC channels, webhooks, consumers, deep links,
  file handlers, exported mobile components, scheduled jobs → the capability each
  reaches.
- **Authorization matrix** (S2): entry point → guard or middleware → sink, one row per
  mutating entry point. The highest-value custom script in this dimension; write it
  per framework and keep it in `work/scripts/`.
- **Client-trusted identity flows** (S1): identity fields from request or message
  inputs reaching queries or session writes.
- **Limits** (S4, S10): body, upload, archive, message and connection limits from
  configuration and code; unsafe deserializer calls.
- **Permissive flags and their history** (S11): the flag pack below, plus
  `git log -S '<flag>'` for when each appeared.
- **Supply chain** (S6): lockfiles present and integrity-pinned; install and CI
  scripts that download and execute; CI action pinning and permissions; a registry
  existence-and-first-publish-date check for every direct dependency (offline mirror
  or a read-only registry query — the only data sent is the package name).
- **Agent configuration** (S12): rule files, tool-server configs, instruction files and
  hooks; hidden-Unicode and permission-mode search.
- **Secrets** (S5): tree **and** history, plus built client bundles if an artifact
  exists.

**Permissive-flag pack** (extend per stack): `rejectUnauthorized: false`,
`verify=False`, `InsecureSkipVerify`, `NODE_TLS_REJECT_UNAUTHORIZED`,
`Access-Control-Allow-Origin: *` / `origin: '*'`, `nodeIntegration: true`,
`contextIsolation: false`, `sandbox: false`, `webSecurity: false`, `allowRunningInsecureContent`,
`csrf: false` / `@csrf_exempt`, `DEBUG = True`, `shell=True`, `eval(`.

**Tools.** Exec = executes project code. Leaves = sends data off the machine.

| Stack | Tool | Measures | Exec | Leaves | Run pinned, nothing installed in the repo |
|---|---|---|---|---|---|
| any | Semgrep CE | patterns and intra-file taint; local custom rules for the auth matrix and log sinks | no | no, with local rules and metrics off | `uvx semgrep@<pin> --metrics=off --config <local-rules> <src>` |
| any | Gitleaks | secrets in tree and history | no | no | pinned binary or digest-pinned image, repo mounted read-only |
| any | TruffleHog | secrets; optional liveness check | no | **yes if verification is on** — run with `--no-verification` unless approved | digest-pinned image |
| any | osv-scanner | known vulnerabilities from lockfiles | no | yes by default; `--offline` with a pre-staged database | pinned binary |
| any | Trivy (fs, config) or Syft + Grype | vulnerabilities, misconfiguration, SBOM | no | database download only (inbound) | digest-pinned image, cached database |
| any | CodeQL CLI | inter-procedural taint | build needed for compiled languages — prefer no-build extraction; isolate any build | no | pinned bundle with local query packs; check the license for private code |
| CI | zizmor, actionlint | workflow injection, unpinned actions, token permissions | no | no | `uvx zizmor@<pin> .github/workflows` |
| IaC | hadolint, Checkov | Dockerfile and infrastructure misconfiguration | no | disable Checkov's platform upload | digest-pinned images |
| JS/TS | Semgrep JS rules, eslint-plugin-security | sinks, eval, unsafe regex, child processes | no | no | `npx --yes <tool>@<pin>` with a config outside the repo (the ESLint plugin is noisy) |
| Electron | Electronegativity | shell hardening checklist (`nodeIntegration`, `contextIsolation`, `openExternal`, …) | no | no | `npx --yes @doyensec/electronegativity@<pin> -i <src>` |
| JS/TS | lockfile-lint | registry host and integrity pinning | no | no | `npx --yes lockfile-lint@<pin>` |
| Python | Bandit, Ruff `S` rules | pickle, unsafe YAML, `shell=True`, `verify=False`, missing timeouts | no | no | `uvx bandit@<pin> -r <src>` (high alert volume — triage) |
| Python | pip-audit | vulnerabilities from requirements | not with `--no-deps --disable-pip` on a locked file | yes (queries an advisory service) | `uvx pip-audit@<pin> -r <file> --disable-pip --no-deps` |
| JVM | SpotBugs + FindSecBugs | bytecode patterns | needs compiled classes — use CI artifacts or an isolated build | no | pinned jars with checksum (high taint false positives) |
| JVM | OWASP Dependency-Check | CVEs | no | database download | digest-pinned image (CPE mismatches) |
| Go | govulncheck | vulnerabilities reachable in the call graph | no (loads packages) | yes unless `-db file://` | `go run golang.org/x/vuln/cmd/govulncheck@<pin> ./...` |
| Go | gosec, staticcheck | injection, weak crypto, insecure TLS | no | no with modules pre-seeded (`GOPROXY=off`) | `go run github.com/securego/gosec/v2/cmd/gosec@<pin> ./...` |

Never use a tool's `@latest`, never install a scanner into the project, never send code
to a hosted scanning service without approval. Mobile-native tooling is not covered
yet; use the platform vendors' security guides and the OWASP mobile verification
standard by hand and list the gap.

## Performance extractor

Runs when the performance dimension is in the audit plan. Static only — it emits
candidates and computed amplification, never verdicts and never latencies.

**Recipe.**

- **Fan-out per flow** (P1): for each representative flow's entry point, the network,
  RPC and database sinks it reaches and whether they are serial, parallel or inside a
  loop. Custom AST extractor.
- **Calls in loops** (P2): queries and remote calls inside loops over results.
- **Unbounded reads** (P3): list endpoints without limit or cursor, find-all calls,
  missing request-size caps, clients that page through everything.
- **Blocking calls** (P4): synchronous file and process APIs reachable from handlers,
  the desktop-shell main process, async functions and tick loops.
- **Timers and broadcast** (P7): every interval, poll and broadcast site with its
  period; then **compute** `clients ÷ interval` and broadcast fan-out from the
  profile's numbers in a script.
- **Cache inventory** (P8): constructor, size cap, TTL, key composition, invalidation
  sites.
- **Lifecycle pairing** (P9): listeners, timers, subscriptions and per-connection
  structures without a matching removal.
- **Resilience config** (P10): HTTP client timeouts, retry policies, pool sizes,
  reconnect logic; then compute pool vs concurrency from the profile.
- **Instrumentation inventory** (P13): what records latency per route or flow.
- **Build artifact** (P5): bundle stats from an existing CI artifact if one exists;
  otherwise mark P5 for the measurement wave.

**Static helper tools:** ESLint rules for synchronous APIs and hook dependencies
(pinned, external config); Ruff `ASYNC` rules; staticcheck and `go vet` plus a
goroutine-without-cancel and unbounded-channel script; a missing-timeout rule set.

## Measurement wave

Runs at `standard` and `deep` only, after the judges, **alone**, for candidates the
judges marked as needing measurement — never more than the profile's representative
flows. Safety, every time:

- an isolated worktree or container at the pinned commit; the audited checkout is
  never touched;
- dependencies linked or installed from the lockfile with install scripts disabled
  (e.g. `npm ci --ignore-scripts`) **inside the isolated copy only**;
- outbound network blocked — the application itself may call third parties;
- nothing else running; record command, tool version, input profile, device or
  throttling settings and run count.

| Claim | Cheapest credible measurement |
|---|---|
| "this flow is slow" / "this is the bottleneck" | approved production telemetry for that route if it exists; otherwise one representative flow under a sampling profiler |
| "won't handle the target load" | a 60–120 s local load test with a stepped arrival rate up to the profile's target (open model); p50/p95/p99, errors, saturation; never a cloud mode |
| "the bundle is too large" | analysis of the production build artifact (stats, metafile, source maps); without an artifact, a dependency-weight candidate only |
| mobile web | a lab run against a local production build with the tool's default mobile throttling, 3–5 runs, report the median and the conditions; prefer field p75 data when it exists |
| "this re-renders too much" | a profiler trace of one representative interaction |
| "this leaks" | repeat a lifecycle and compare retained heap after garbage collection; heap snapshots pause the process — isolate |
| "this query is slow" | the database's analyzed query plan on seeded data plus a per-request query count |

| Stack | Tools (pin at run time) | Exec | Leaves |
|---|---|---|---|
| any | k6 (local mode only — never its cloud mode) | drives the app | no |
| JS/TS | source-map-explorer, the bundler's stats or metafile, size-limit; Lighthouse CLI against `localhost`; browser performance and memory profilers; `node --cpu-prof` / `--heap-prof`; Clinic.js; autocannon | building and profiling do | no (local URLs only) |
| Python | `cProfile`, py-spy (launch the process under it — no attaching to live processes), Scalene, memray; nplusone or ORM query logging; Locust headless | yes | no |
| JVM | JDK Flight Recorder with JMC or the `jfr` CLI, async-profiler; Hibernate statistics or a datasource proxy for query counts; Gatling | yes | no |
| Go | `pprof` (CPU, heap, goroutine, block, mutex), `go test -bench`, `go tool trace`; vegeta | yes | no |

A measured number replaces the candidate's status with `measured`; a measurement that
could not run leaves it `candidate (unmeasured)` and the reason goes under
`NOT_COVERED`.

## Contract examples by language

Kept here so the judge brief stays language-agnostic.

**TypeScript.** Strictness flags: `strict`, `exactOptionalPropertyTypes` (absent vs
`undefined`), `noUncheckedIndexedAccess`, `useUnknownInCatchVariables`. Lint:
`no-explicit-any`, `no-unsafe-*`, `no-non-null-assertion`, `consistent-type-assertions`,
`ban-ts-comment` (require descriptions), `no-floating-promises`,
`no-unnecessary-condition`, `switch-exhaustiveness-check`. Discriminated unions with a
`never` exhaustiveness check. Branded IDs are a convention — the tell is `as Brand`
outside the constructor. `package.json` `exports` restricts deep imports; `export *`
widens surface invisibly. Boundary parsing with a schema library (Zod, Valibot).

**Python.** `Optional[T]` means nullable, not omittable. Annotations are not enforced
at runtime, so JSON boundaries need a parsing library (Pydantic, attrs + cattrs).
Mutable default arguments. Keyword-only `*` instead of parameter objects.
`raise ... from` for translation. Ruff `FBT001-003` (boolean positional), `E722`,
`BLE001`, `S110`, `PGH003`, `ANN401`. mypy `--strict` or pyright strict. `NewType`,
`overload`. Surface: `__all__`; `_private` is convention only.

**Rust.** `Result` vs `Option` vs `panic!` (the Rust Book, ch. 9). `#[non_exhaustive]`,
`pub(crate)`, newtypes, serde with newtype constructors. Smell: `unwrap_or_default()`
on I/O results. `cargo public-api`, `cargo-semver-checks`.

**Go.** Errors as values; wrap with `%w`; `errors.Is` / `errors.As`. Wrapping a
lower-level error can make its identity part of your API. `errcheck`, `internal/`,
`apidiff` / `gorelease`, defined types (`type UserID string`). Smell: `_ = err`.

**Cross-language.** Protobuf: never reuse field numbers; `reserved`; `buf breaking`.
HTTP errors: RFC 9457 problem details. Deprecation: `Sunset` (RFC 8594) and
`Deprecation` (RFC 9745) headers. Events: schema-registry compatibility modes.
Consumer-driven contracts: Pact. Migrations: expand / contract when old versions still
read the data.
