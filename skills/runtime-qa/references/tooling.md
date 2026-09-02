# Runtime QA tooling reference

Concrete names live here, never in `SKILL.md`. Picks below were current as of
**2026-06**; confirm the tool is still maintained and pin its latest stable version
before use (a docs MCP if one is available, otherwise the tool's own docs for that
version — never configure from memory of an older release). Prefer whatever the
project already has wired over introducing a new driver for one pass.

## Drivers by artifact type

Pick by **artifact type, not backend language** — the web driver is the same whether
the server is Python or Go.

| Artifact | Default | Alternatives / notes |
|---|---|---|
| Browser app | **Playwright** (bindings for JS/TS, Python, Java, .NET; out-of-process, multi-tab/cross-origin, trace viewer) | Cypress (better interactive DX, weaker multi-origin, paid parallelism); WebdriverIO for real-device grids. Avoid raw Selenium for greenfield; Puppeteer is Chrome-only. |
| Interactive browser driving from a shell/agent | **`playwright-cli`** — named sessions, `eval` in page, screenshot, video, tracing; a session name per pass keeps buffers and recordings together | Plain Playwright scripts when the pass is scripted rather than exploratory |
| Desktop / Electron | **Playwright** (Electron support is first-class) | The app's own automation port, if it exposes one |
| CLI | **bats-core** (TAP, drives the real binary, asserts stdout/exit) | Plain shell + explicit exit-code checks; `expect` for interactive prompts |
| HTTP API | The stack's real-request client (supertest, httpx, REST Assured, reqwest) plus **Schemathesis** for contract fuzzing | `curl`/`httpie` for a hand-driven pass; capture full request/response |
| Mobile | **Appium**, or the platform's own (XCUITest, Espresso) | Simulator/emulator screenshots + `xcrun simctl` / `adb logcat` for device logs |
| Library | A throwaway consumer project that imports the published/packed artifact | `npm pack` / `pip install .` into a temp venv — not the repo's own suite |

## Visual comparison

- **Playwright `toHaveScreenshot()`** — built-in, baselines committed in git; the
  default for scripted visual regression.
- **odiff / pixelmatch** — standalone image diff when the baseline came from
  somewhere else (a previous build, a design export).
- **Chromatic** (Storybook-native) or **Percy** — hosted review UIs; only where the
  project already uses them.
- Capture the baseline from the pre-change build or the design source *before*
  driving the new one. A parity check without a baseline is an opinion.

## Evidence capture

- Screenshots: `playwright-cli screenshot --filename=<abs path>` — always an absolute
  path into the run's evidence dir; a bare filename lands in the cwd.
- Recording: `video-start` / `video-chapter` / `video-stop`; one chapter per report
  step. Worth it for motion, timing, or a sequence; a still is better for anything
  static.
- Tracing: `tracing-start` / `tracing-stop` produces a Playwright trace with network
  and DOM snapshots — heavier, but shows ordering a video cannot.
- Console/log capture: read the page console *and* the app's own structured log
  buffer if it has one. `console.debug` is filtered out by many capture paths — read
  debug level deliberately.
- CLI/API: tee stdout and stderr to files and record exit codes separately; never
  read an exit code through a pipe or a pager (a red gate was reported green twice
  because the run was piped through a pager and the pager's exit code was read).

## Isolation mechanics

- **Ports:** derive per session rather than using the project default. Check the port
  is free first (`lsof -i :<port>` / `netstat -ano | findstr :<port>` / `ss -ltnp`) and
  identify anything already listening instead of reusing it. Watch for e2e configs
  with `reuseExistingServer: true` plus a hardcoded port — that combination makes
  concurrent lanes serve each other's code.
- **Browser profiles:** a distinct `--user-data-dir` (or a uniquely named driver
  session) per pass. Never share a profile directory between sessions.
- **Temp dirs:** create your own subdirectory under the OS temp dir and delete only
  that. A shared scratch root was once wiped by one session's cleanup, destroying
  other sessions' profiles.
- **Data:** an isolated database file/schema or in-memory store per session; state
  left behind is the most common cause of a result nobody can reproduce.
- **Teardown:** stop by pid or by the driver's session handle (`playwright-cli -s=<name>
  close`). Never `taskkill /IM <image>` or `pkill -f chrome` — one such teardown closed
  the user's real browser.

## Model tiers for delegated driving

| Tier | Models | Use |
|---|---|---|
| top | Fable | session/conductor judgment only; never product code, never content generation |
| high | Opus | judgment work: specs, plans, reviews, builders on real suites |
| mid | Sonnet | mechanical: transcript reading, file moves, fixtures, desk/dispatch sessions |
| low | Haiku | bulk classification only |

Judgment-heavy driving (exploratory passes, root-causing, visual fidelity calls) runs
one tier below the session; mechanical repetition (re-running a scripted scenario
across variants, collecting captures) two below, floor at the mid tier. Never delegate
upward. Field evidence: a mid-tier builder spun ~30 min stuck on an e2e suite; mid-tier
writers produced confidently wrong root causes. The bottom tier never drives a slow or
flaky harness and never writes a root-cause diagnosis.

## Sanity checks worth running before trusting a pass

- `git -C <path> rev-parse --abbrev-ref HEAD` and `--short HEAD` for every repo whose
  build matters; `git worktree list` to confirm the path really is the worktree you
  think it is.
- Build freshness: compare the build output's mtime against the commit, or read a
  version/build stamp from the running artifact.
- Grep the tree for the selector, route, or element your scenario asserts on before
  trusting a pass — a scenario once targeted a class that existed nowhere in the
  product and passed regardless.
