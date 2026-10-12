# Codebase profile

Step 0's artifact: `docs/audits/<date>-<mode>/profile.md`. It states what the system
has to be, so the audit can judge what the code is against it. Keep it to one screen.
Every field carries its **source** (a doc anchor, "user, <date>", or "derived") —
an unsourced field is a guess, and guesses are not allowed in load and stakes.

## Template

```markdown
# Profile — <repo> @ <short sha>

## Identity
- What it is: <one sentence>
- Users: <who; internal, consumer, B2B, developers>
- Platforms: <desktop / mobile web / native mobile / server / CLI / library / embedded>
- Deploy model: <lockstep single artifact | rolling | independently deployed consumers | published library | installed client with old versions in the wild>
- Source: <anchors>

## Load and constraints
- Representative flows: <the top 1–3 user or request paths, by name and entry point | unknown>
- Concurrent users / sessions: <number or range | unknown>
- Request or event rate at peak: <… | unknown>
- Data volume: <rows, files, payload sizes | unknown>
- Client device class: <low-end mobile | mid | desktop | n/a | unknown>
- Network: <offline-first | mobile/unreliable | LAN | datacenter | unknown>
- Burst shape: <steady | spiky (events, launches) | unknown>
- Budgets / response targets: <latency, memory, bundle size, battery, cost — any stated | none stated>
- Runtime shape: <single event loop / UI thread / worker pool / serverless / long-lived process / tick loop>
- Session lifetime: <request-scoped | long-lived desktop session | always-on connection | kiosk>
- Key dependencies: <databases, caches, downstream services, with any documented limits>
- Telemetry: <production latency/error data exists, and whether reading it is approved | none>
- Source: <anchors / user>

## Stakes
- Sensitive data: <PII, credentials, health, none>
- Data classification for logs: <what may never be logged | not stated>
- Money: <payments, billing, prizes, none>
- Actors and auth model: <none | single user | multi-user | multi-tenant | roles; where auth lives>
- Trust zones: <public internet | partner | internal | offline; untrusted local input such as opened files, deep links, rendered content>
- Platform capabilities: <desktop shell with OS access, plugins, native helpers, container privileges>
- Distribution: <server | desktop installer, auto-update? | app store | web bundle>
- Agent-maintained: <yes | no>
- Safety or regulatory: <none | …>
- Public surface: <public API, published package, open ports, none>
- Persisted data users would lose: <what, where>
- Source: <anchors / inventories / user>

## Dominant quality attributes
1. <attribute> — <the scenario that makes it dominant, e.g. "100k concurrent players during a live event">
2. <…>
3. <…>
Confirmed by: <user, date | unattended — not confirmed>

## Audit plan
| Dimension | Runs? | Why |
|---|---|---|
| architecture | yes/no | … |
| gates | yes/no | … |
| contracts | yes/no | … |
| verbosity | yes/no | … |
| security | yes/no | on whenever any stake is listed |
| performance | yes/no | on only when load, platform or budget constraints are stated |
Depth: <quick | standard | deep> — <why>

## Scope
- Commit: <sha> (range for run mode: <base>..<head>)
- Include: <globs>
- Exclude: <globs — generated, vendored, fixtures>
- Tools: <name@version …>
- Fingerprint: <hash of commit + include + exclude + tools>
```

## Questions to ask the user

Ask only what the docs did not settle, in one message, with a default the user can
accept:

1. "What's the expected load at peak — concurrent users or sessions, and request
   rate? Which one to three flows matter most?"
2. "Which clients matter — desktop, mobile web, native? Any low-end devices or poor
   networks?"
3. "Is there any stated budget — latency, bundle size, memory, cost?"
4. "What data here would hurt to lose or leak — user data, money, credentials? Who
   are the users — just you, many, separate tenants, roles?"
5. "Here are the two or three quality attributes I think dominate: … — right?"

## Unattended

Write `unknown` for anything the docs do not state. Then:

- severity is not lowered for load or stakes that are `unknown`;
- every `unknown` is listed under `NOT_COVERED` in the handoff block;
- the dominant attributes are marked `not confirmed`.

## How the profile drives the audit

| Profile fact | Effect |
|---|---|
| Dominant attributes | raise severity one step for findings that hit them directly; order the task list by them |
| Deploy model | contract evolution findings: lockstep lowers, independent consumers and old installed clients raise |
| Platform and device class | front-end rows weigh state copies, fetch fan-out and bundle growth by device; a desktop-only internal tool lowers them |
| Load | coupling, hotspot and contract findings on hot paths rise with load; at small, known load they fall |
| Stakes | choose the test-strength sample; raise findings on persisted data, money, auth and trust boundaries; decide what `quick` depth still verifies |
| Public surface | public-surface and evolution rows apply at full severity only when something outside the repo consumes it |

## Per-agent slices

| Agent | Sections passed |
|---|---|
| Extractors | Scope |
| Intent ledger | Identity |
| Test strength | Stakes, Scope |
| Security and performance extractors | Scope, plus the trust-zone and representative-flow lists (what to inventory, not why) |
| Measurement | Representative flows, Load and constraints |
| Judges | the whole profile |
| Verifiers | none |
| Baseline assembler | Scope, Dominant quality attributes |
| Merge (orchestrator) | the whole profile |

## Rubric rows that depend on the profile

A row may state a condition: `applies when: <profile fact>`. The judge skips a row
whose condition the profile rules out and lists it under `Not assessed` with the
reason; it never reports a finding from a row that does not apply.
