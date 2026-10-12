# Rubric — performance

Runs when the profile states load, platform or budget constraints; otherwise it is
skipped and the reason recorded. Performance judged without a workload is opinion, so
the profile must supply, at minimum: **representative flows** (the top one to three
user or request paths), **client device and network class**, **peak concurrency and
request or message rate**, **data cardinalities** (row counts, list sizes, payload
sizes, hard caps), **at least one response target** (a latency or budget the system
must meet), **runtime shape** (single event loop or UI thread, worker pool,
serverless, long-lived process) and **session lifetime**. A row whose required fact is
missing becomes `profile-blocked` and is listed under `Not assessed`.

## Measurement status

A claim about current behavior requires measurement. Every finding carries a status:

| Status | Means | Severity ceiling |
|---|---|---|
| `measured` | the measurement wave (or approved telemetry) produced the number | none |
| `computed` | arithmetic from the profile's own numbers proves a breach — e.g. 100,000 clients × one request every 2 s = 50,000 requests/s against a documented quota | none |
| `candidate (unmeasured)` | the code shows the mechanism; impact is unknown | **Medium** |
| `profile-blocked` | a required profile fact is missing | not reported as a finding |

A `candidate (unmeasured)` must state: the anchor; the mechanism (the amplification or
lifecycle the code shows); the profile fact that activates the row; the budget it
would breach if the assumption holds; and **the exact measurement that would settle
it**. No invented milliseconds, item counts or hit rates — amplification is computed
by a script from profile numbers, never estimated by a model.

## Budgets

Use only budgets with a real source or the profile's own:

| Budget | Value | Applies to |
|---|---|---|
| Largest Contentful Paint, "good" | ≤ 2.5 s at the 75th percentile | public web UX |
| Interaction to Next Paint, "good" | ≤ 200 ms at the 75th percentile | public web UX |
| Cumulative Layout Shift, "good" | ≤ 0.1 at the 75th percentile | public web UX |
| Long task | 50 ms | any browser or renderer main thread |
| Frame budget | ~16 ms at 60 fps | animation, scrolling, game loops |
| Database connection limits | the database's documented default or configured limit | pool arithmetic |
| Anything else | the profile's stated targets | — |

Core Web Vitals are not a backend, desktop-shell or real-time budget. Lab tools'
diagnostic thresholds and example budgets are not requirements unless the profile
adopts them. No published performance severity standard exists; the scale below is
this skill's.

## Rows

Severity columns: **Desk** = lockstep desktop tool · **2k** = ~2,000 concurrent users ·
**100k** = ~100,000 concurrent users · **Mob** = low-end mobile client.

| ID | Row | Status it can reach statically | Desk / 2k / 100k / Mob | Premature when | Applies when |
|---|---|---|---|---|---|
| P1 | **Call fan-out per screen or route** — N downstream calls, serial chains, awaits in loops; report `rate × fan-out → downstream work` | count computed; latency needs measurement | Low / Med / High if downstream is fragile / Med–High (serial round trips) | parallel calls on a LAN or desktop; merging calls only to lower a count | representative flows make network, DB or RPC calls |
| P2 | **N+1 queries or calls** — a query or remote call inside a loop over results | candidate; confirm with a per-request query count (frameworks may batch) | Low / Med / High / Med | N provably tiny and the path cold | DB- or API-backed collections drive lookups |
| P3 | **Unbounded reads and payloads** — list endpoints without limit or cursor, find-all, no request size cap, clients accumulating every page | mechanism static; magnitude needs data size | Low / Med / High / High | physically bounded sets (enums, config tables) | data or input can exceed a small known bound |
| P4 | **Blocking work on a latency-critical thread** — synchronous file or process calls in handlers, the desktop-shell main process, async functions, tick loops | static semantics; impact measured | Low–Med (frozen window if main process) / Med / High / Med | startup-only code, one-shot CLIs | single event loop, UI thread or tick loop |
| P5 | **Bundle and startup weight** — large initial chunk, duplicated libraries, a heavy package for a small feature, eager loading before the first window | measured from a build artifact (building is executing project code — isolate it) | Low (measure startup instead) / Low / Low / High | desktop, internal or behind-login tools; a large package tree-shaking mostly removes | a client artifact or startup time is a dominant attribute |
| P6 | **Render cascades and main-thread work** — unstable context values, inline props to memoized children, unvirtualized long lists, effect-to-state loops | needs a profiler trace; lint only seeds the candidate | Low / Low / n.a. / Med–High | small trees; blanket memoization | interactive web or desktop UI |
| P7 | **Polling and broadcast amplification** — timers × client count; O(n) broadcast per event (O(n²) when every action reaches everyone) | computed: clients ÷ interval | Low / Low–Med / High / Med (battery) | few clients, long intervals; push is not automatically better for rare updates | periodic client work or real-time channels |
| P8 | **Cache safety** — module-level caches with no size cap or TTL; no invalidation on the write path; a key missing the tenant or auth dimension. A missing cache alone is not a finding | unsafe cache static; "needs a cache" measured | Low / Med / High (Critical if a wrong key leaks data) / Med | caching cheap or rarely reused work | caches or repeated expensive work exist |
| P9 | **Memory and resource retention** — listeners or timers never removed, growing global maps, uncapped per-connection queues, per-window IPC listeners | candidate by lifecycle pairing; "leak" requires a repeated heap diff | Med–High (long sessions) / Med / High (× connections) / High | bounded intentional caches; request-scoped serverless | long-lived process, session or connection |
| P10 | **Resilience under load** — HTTP clients without timeouts, retries without backoff and jitter, pool size vs concurrency, reconnect storms after deploy, no backpressure or load shedding | config static; confirm with a short load test | Low / Med / High / Med | a single-dependency internal tool | services with dependencies or many connections |
| P11 | **Hot-path algorithmic and serialization cost** — nested scans over profile-sized collections, per-tick sorting or encoding, thousands of tiny dispatches | candidate; confirm with a profile | Low / Low / High on tick or main thread / Med | big-O cleanup of a small cold list | frequent operations or large N |
| P12 | **Image, font and third-party script weight** — unoptimized hero images, render-blocking third-party scripts, no priority on the largest element | measured (page weight, LCP) | Low / Low / n.a. / Med–High | authenticated internal dashboards | consumer web, mobile |
| P13 | **Targets cannot be checked** — a stated latency target exists but nothing records latency by route or flow | static (instrumentation inventory) | Low / Med / High / Med | offline single-user tools | the profile states a response target |

**At ~100,000 concurrent users** the rubric gains checks rather than changing
thresholds: per-connection memory × connection count (from a profiled bytes-per-
connection figure, never a guess), file-descriptor and port limits, database
connection limits and mandatory pooling, broadcast fan-out and the backplane,
reconnect and stampede protection, backpressure and load shedding, and evidence of
capacity. P2, P7 and P10 rise one to two levels. Tight real-time latency or expensive
messages can make 2,000 users severe too.

## Platform emphasis

| Platform | Weigh up | Weigh down |
|---|---|---|
| Web on mobile | P1, P5, P6, P12, polling and battery, memory; Core Web Vitals at p75 | server-only dependency weight |
| Desktop shell | P4 on the main process, startup module cost, P9 over long sessions, window and process count, IPC chatter | network transfer budgets |
| Backend with many users | P1, P2, P3, P8, P10, pool arithmetic, serialization, overload behavior, tail latency | browser metrics |
| Real-time / multiplayer | P7, P11, the 100k checks, per-client send queues, interest filtering, reconnect jitter, the tick loop | average HTTP latency |

## Agent-specific patterns

No measured evidence on performance specifically. Expected, not measured: missing
bounds (no pagination, size cap or TTL — resource exhaustion is measured as a missed
*security* class), per-item remote calls in loops, defaults chosen to make it work (no
timeouts, find-all), and parallel fetch mechanisms (architecture AF3). Never claim a
prevalence.
