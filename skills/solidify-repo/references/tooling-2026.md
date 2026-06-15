# Repository Solidification / Hardening — Tooling Reference (2026)

**Last verified: 2026-06-11.** Tooling moves fast; before relying on any recommendation, web-search the tool's GitHub releases / package registry page to confirm the latest version and maintenance status.

Selection priority (in order): active maintenance & release recency > adoption > speed > minimal config > clean CI exit codes > agent-friendly (deterministic, machine-readable) output.

## Quick-reference matrix

| Category | JS/TS | Python | Go | Rust | JVM (Java/Kotlin) | Ruby | PHP |
|---|---|---|---|---|---|---|---|
| Formatter | Biome (or oxfmt) | Ruff format | gofmt/`go fmt` | rustfmt | Spotless (google-java-format / ktfmt) | RuboCop / StandardRB | Laravel Pint |
| Linter | Biome / oxlint (+ESLint) | Ruff | golangci-lint v2 | Clippy | Checkstyle/PMD (Java); detekt (Kotlin) | RuboCop | PHPStan / Psalm |
| Dead-code | Knip / fallow | Ruff (F401/F841) + Vulture | golangci-lint (unused/deadcode) | Clippy / cargo-machete | detekt / PMD UnusedPrivate | RuboCop Lint/UnusedMethodArgument | PHPStan + Rector |
| Complexity | Biome / fallow | Ruff C901 (mccabe) | golangci-lint gocyclo/gocognit | Clippy cognitive_complexity | PMD CyclomaticComplexity / detekt | RuboCop Metrics | PHPMD / PHPStan |
| Duplication / repetition | fallow (or jscpd) | jscpd | jscpd / dupl | jscpd | PMD CPD | jscpd / flay | jscpd (phpcpd dead) |
| Type checker | tsc (TypeScript) | Pyright / ty / mypy | (compiler) | (compiler) | (compiler) | Sorbet/RBS (opt) | PHPStan/Psalm |
| Verify harness | npm script / just | just / nox | make / just | cargo-make / just | Gradle/Maven task | rake / just | composer script |
| SAST | Semgrep (+CodeQL) | Bandit (Ruff S) / Semgrep | gosec / govulncheck | cargo-audit / Clippy | SpotBugs+FindSecBugs / CodeQL | Brakeman | Psalm taint / Semgrep |
| Secret scan | gitleaks (+TruffleHog CI) | gitleaks | gitleaks | gitleaks | gitleaks | gitleaks | gitleaks |
| Dep/supply-chain | npm/pnpm audit + OSV-Scanner | pip-audit / uv | govulncheck + OSV | cargo-audit / cargo-deny | OWASP dependency-check / OSV | bundler-audit | composer audit |
| Pre-commit | Lefthook (or Husky+lint-staged) | pre-commit | Lefthook | Lefthook | Lefthook/pre-commit | Lefthook/Overcommit | Lefthook |
| E2E / runtime QA | Playwright (+ supertest API) | Playwright (pytest-playwright); Schemathesis (API) | chromedp / Playwright-go; httptest (API) | Playwright (JS) / fantoccini; reqwest+insta | Playwright-Java / REST Assured (API) | Capybara+Selenium / playwright-ruby; rack-test | Laravel Dusk / Playwright; Pest feature (API) |

---

## JavaScript / TypeScript (package.json)

**Consolidation flag:** Biome replaces Prettier (format) + ESLint (lint) + import-sorting in one Rust binary, single `biome.json`. oxlint (oxc) is the fastest linter. **Knip** covers dead-code/unused-deps/exports across files. **fallow** (`fallow-rs`) goes further and consolidates dead-code + duplication + complexity + circular deps + architecture boundaries into one zero-config Rust binary — a category Biome/ESLint cannot see across the module graph.

| Category | Tool | One-liner | Latest (2026) |
|---|---|---|---|
| Format+Lint | **Biome** | Single Rust binary: formatter + linter + import organize | v2.4 (Feb 2026), 500+ lint rules |
| Linter (fast) | **oxlint** | Rust linter, 50-100x faster than ESLint | v1.69.0 (Jun 2026) |
| Linter (plugins) | ESLint | Pluggable JS/TS linter; flat config only | v10.1.0 (Mar 2026) |
| Dead-code | **Knip** | Finds unused files/exports/deps across project | actively maintained |
| Dead-code+dupes+complexity | **fallow** | Rust graph analyzer: dead code, duplication, complexity, circular deps | 2.8x line (Jun 2026), near-daily releases |
| Duplication | **jscpd** v5 | Rust copy-paste detector, 223+ languages | maintained (npm updated Jun 2026) |
| Type check | **tsc** | TypeScript compiler `--noEmit` | TypeScript |

**Why Biome:** active (v2.4 Feb 2026, AWS/Google/Vercel adoption), 20-100x faster than ESLint+Prettier, zero-config, `biome ci` returns clean non-zero exit. Doesn't do type-aware lint (keep `tsc --noEmit`).

**Why fallow (new, watch closely):** purpose-built for human + AI-agent collaboration — deterministic, graph-based, machine-readable JSON/MCP output. Sub-second; benchmarks claim 3-36x faster than Knip and 20-33x faster than jscpd. Zero-config with 84-122 framework plugins, no Node runtime for static analysis. **Caveats:** very young (2.x release line, shipping near-daily as of June 2026 — APIs/output may churn); **JS/TS only**; **syntactic analysis only — no TypeScript type resolution**, so members consumed via interfaces/dynamic access can show as false-positive "unused" (filter test mocks; pair with `tsc`). Free static layer is open source; there is an optional **paid runtime layer** (hot/cold-path deletion evidence). Treat as a strong consolidation candidate, not yet a settled default.

**Install + config:**
```
npm install --save-dev --save-exact @biomejs/biome
npx @biomejs/biome init
npm install -g fallow        # or: npx fallow check   (no install)
```
```json
// biome.json
{ "$schema": "https://biomejs.dev/schemas/2.4.0/schema.json",
  "formatter": { "enabled": true, "indentStyle": "space" },
  "linter": { "enabled": true, "rules": { "recommended": true,
    "complexity": { "noExcessiveCognitiveComplexity": "warn" } } } }
```

**Pre-commit (Lefthook):**
```yaml
# lefthook.yml
pre-commit:
  parallel: true
  commands:
    check: { run: npx @biomejs/biome check --staged --no-errors-on-unmatched }
    dead:  { run: npx fallow audit --changed-since main --format json --quiet }
```

**CI:** `npx @biomejs/biome ci .` + `npx tsc --noEmit` + `npx fallow audit --since main --format json` (or `npx knip`) + `npx jscpd . --threshold 5`.

**Alternatives:** ESLint v10 + Prettier when you need type-aware rules or a specific plugin ecosystem (eslint-config-next, etc.); oxlint as a fast pre-pass alongside ESLint on large codebases; Knip instead of fallow when you want the more battle-tested dead-code tool without a paid upsell.

**Avoid / legacy:** TSLint (dead since 2019 → typescript-eslint); ESLint `.eslintrc` legacy config (removed entirely in ESLint v10, Feb 2026 → flat `eslint.config.js`); ts-prune (maintenance mode → Knip/fallow); standardjs (older).

**SAST/secrets/deps:** Semgrep (SAST); gitleaks (secrets); `npm audit`/`pnpm audit` + OSV-Scanner (deps); Dependabot/Renovate for automated PRs.

---

## Python (pyproject.toml / requirements.txt)

**Consolidation flag:** Ruff replaces Flake8 (+dozens of plugins) + Black (format) + isort + pydocstyle + pyupgrade + autoflake + Bandit (security via `S` rules) + mccabe (complexity `C901`) — one Rust binary, 10-100x faster, config in `pyproject.toml`. Ruff does **not** detect cross-file duplication — use jscpd for that.

| Category | Tool | One-liner | Latest (2026) |
|---|---|---|---|
| Lint+Format+Dead-code+Complexity+SAST | **Ruff** | One Rust tool: lint/format/imports/security/complexity | v0.15.16 (Jun 4 2026) |
| Type check | **Pyright** / **ty** (beta) / **mypy** | Static type checking | Pyright stable; ty beta; mypy 2.0 (May 2026) |
| Dead code (thorough) | Vulture | Finds unused code beyond unused imports | maintained |
| Duplication | **jscpd** | Copy-paste detection (Python supported) | maintained |
| Security (deep) | Bandit | Python SAST (also available as Ruff `S` rules) | maintained |
| Dep audit | **pip-audit** / uv | Scans deps vs PyPI advisory/OSV | maintained |

**Why Ruff:** dominant, backed by Astral (uv, ty), released ~weekly (v0.15.16 Jun 4 2026), Production/Stable, exit-code-clean. Single tool collapses the whole legacy chain.

**Type checker pick:** **Pyright** is the strongest correctness default for new projects — per the python/typing conformance dashboard (early March 2026), Pyright passes ~98% of the 139-test typing-spec conformance suite, while mypy fully passes only 57%. **ty** (Astral, beta, Dec 2025) is the up-and-comer: 10-100x faster than mypy/pyright (incremental re-check on PyTorch ty 4.7ms vs Pyright 386ms), but full-pass conformance is only ~15% — use it if you're already in the uv/Ruff toolchain or want raw speed, and pair with mypy/Pyright where correctness is critical. **mypy** stays where you depend on its plugins (Django-stubs, SQLAlchemy). Pyrefly (Meta, Rust, stable 1.0 May 2026) is another fast option with higher spec conformance than ty.

**Install + config:**
```
uv add --dev ruff        # or: pip install ruff
```
```toml
# pyproject.toml
[tool.ruff]
line-length = 88
[tool.ruff.lint]
select = ["E","F","I","C901","S","UP","B"]   # incl. mccabe complexity + bandit security
[tool.ruff.lint.mccabe]
max-complexity = 10
```

**Pre-commit (`pre-commit` framework — the Python ecosystem default):**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.16
    hooks: [ {id: ruff, args: [--fix]}, {id: ruff-format} ]
```

**CI:** `ruff check --output-format=github .` + `ruff format --check .` + `ty check` (or `pyright`) + `pytest` + `pip-audit` + `jscpd . --threshold 5`.

**Avoid / legacy:** Flake8, Black, isort, pydocstyle, pyupgrade, autoflake, pylint (mostly) → all replaced by Ruff for new projects; pip-tools mostly superseded by uv.

**SAST/secrets:** Bandit (or Ruff `S`); Semgrep; gitleaks.

---

## Go (go.mod)

**Consolidation flag:** golangci-lint aggregates 100+ Go linters (incl. unused/deadcode, gocyclo/gocognit complexity, govet, staticcheck, gosec, and **dupl** for duplication) behind one binary, one `.golangci.yml`, parallel + cached. v2 (Mar 2025) added a built-in `golangci-lint fmt` formatter and revamped config (`linters.default`).

| Category | Tool | One-liner | Latest (2026) |
|---|---|---|---|
| Format | **gofmt** / `golangci-lint fmt` | Canonical formatter (gofmt/goimports) | stdlib |
| Lint (+dead-code+complexity+dupl) | **golangci-lint v2** | Aggregates 100+ linters, parallel/cached | v2.12.2 (May 2026) |
| Duplication | **dupl** (via golangci-lint) / jscpd | Token-based clone detector | maintained |
| SAST | **gosec** | Go security checker, 30+ rules, CWE-mapped | actively maintained |
| Vuln scan | **govulncheck** | Official Go vuln scanner, reachability-aware | maintained by Go team |

**Why golangci-lint v2:** de-facto standard, active (v2.12.2 May 2026), fast, SARIF/JSON/checkstyle output, non-zero exit in CI. gosec + govulncheck + dupl bundle in. Complexity via gocyclo (`min-complexity`) and gocognit.

**Install + config:**
```
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest
go install golang.org/x/vuln/cmd/govulncheck@latest
```
```yaml
# .golangci.yml
version: "2"
linters:
  default: standard
  enable: [gosec, gocyclo, gocognit, dupl, unused, errcheck, govet]
  settings:
    gocyclo: { min-complexity: 15 }
    gocognit: { min-complexity: 20 }
    dupl: { threshold: 150 }
```

**Pre-commit (Lefthook):**
```yaml
pre-commit:
  commands:
    fmt:  { run: golangci-lint fmt }
    lint: { run: golangci-lint run }
```

**CI:** `golangci-lint run --out-format=github-actions` + `govulncheck ./...` + `go test ./...`.

**Alternatives:** staticcheck standalone (correctness-focused) if you want a lighter tool; revive as a configurable golint replacement.

**Avoid / legacy:** golint (deprecated/archived → revive or golangci-lint); gometalinter (dead → golangci-lint); golangci-lint v1 config (`enable-all`/`disable-all` → `linters.default`); deprecated linters like `wsl`/`gomodguard` v1 (→ `wsl_v5`/`gomodguard_v2`).

**Secrets/deps:** gitleaks; govulncheck + OSV-Scanner; Dependabot/Renovate.

---

## Rust (Cargo.toml)

**Consolidation flag:** The official toolchain ships rustfmt (format) + Clippy (lint, incl. cognitive_complexity & some dead-code) via rustup — no third-party formatter/linter needed. cargo-deny consolidates vuln + license + source + duplicate-dep policy. Source-level duplication detection isn't first-party — use jscpd (Rust is supported).

| Category | Tool | One-liner | Status |
|---|---|---|---|
| Format | **rustfmt** | Official formatter (`cargo fmt`) | ships w/ toolchain |
| Lint (+complexity) | **Clippy** | Official linter (`cargo clippy`), 700+ lints | ships w/ toolchain |
| Dead deps | **cargo-machete** | Fast unused-dependency detector | maintained |
| Duplication | **jscpd** | Copy-paste detection (Rust supported) | maintained |
| Vuln audit | **cargo-audit** | Scans Cargo.lock vs RustSec advisory DB | by RustSec WG |
| Policy/supply-chain | **cargo-deny** | Vuln + license + source + dup-dep policy | by Embark |

**Why Clippy+rustfmt:** first-party, always current with the compiler, zero-config, deterministic. `cargo clippy -- -D warnings` makes any lint fail CI. cargo-audit is the canonical RustSec frontend.

**Install + config:**
```
rustup component add clippy rustfmt
cargo install cargo-audit cargo-deny cargo-machete
```
```toml
# clippy config via Cargo.toml lints table
[lints.clippy]
cognitive_complexity = "warn"
# rustfmt.toml for format options
```

**Pre-commit (Lefthook):**
```yaml
pre-commit:
  commands:
    fmt:   { run: cargo fmt --check }
    lint:  { run: cargo clippy -- -D warnings }
```

**CI:** `cargo fmt --check` + `cargo clippy -- -D warnings` + `cargo test` + `cargo audit` (+ `cargo deny check`) + `jscpd src --threshold 5`.

**Alternatives:** cargo-udeps (thorough unused-deps, needs nightly) vs cargo-machete (fast, stable).

**Avoid / legacy:** No serious third-party formatter/linter competitors — rustfmt/Clippy are canonical. Don't hand-roll style checks.

**Secrets:** gitleaks. **Deps:** cargo-audit + cargo-deny + OSV-Scanner.

---

## JVM: Java / Kotlin (pom.xml / build.gradle)

**Consolidation flag:** Spotless is a single Gradle/Maven plugin that orchestrates formatters for Java (google-java-format or Palantir), Kotlin (ktfmt/ktlint), plus license headers — one `spotlessCheck`/`spotlessApply` entry point. detekt covers Kotlin lint + complexity + some dead-code in one tool. **PMD ships CPD** (Copy-Paste Detector) for duplication — same install as PMD.

| Category | Java | Kotlin | Latest (2026) |
|---|---|---|---|
| Format | **Spotless** + google-java-format (1.28.0) or Palantir (2.91.0) | Spotless + **ktfmt** (0.63) or **ktlint** (1.8.0, Dec 2025) | Spotless 8.6.0 (May 27 2026) |
| Lint / static analysis | **PMD** (7.25.0, May 29 2026) + **Checkstyle** (13.5.0, May 30 2026) | **detekt** (1.23.8 stable) | see versions |
| Duplication | **PMD CPD** (`pmd cpd --minimum-tokens 75`) | PMD CPD / detekt | bundled w/ PMD 7.25.0 |
| Bug/SAST | **SpotBugs** (4.9.8, Oct 2025) + **FindSecBugs** (1.14.0, Apr 2025) | detekt | — |
| Compile-time checks | **error-prone** (2.44.0, needs JDK 21+) | (compiler) | — |
| Dep audit | **OWASP dependency-check** (12.2.2, May 3 2026) | same | — |

**Why these:** Spotless (8.6.0, May 2026) is the actively-maintained format orchestrator and returns clean exit codes via `spotlessCheck`. PMD 7.25.0 and Checkstyle 13.5.0 (both May 2026) are actively maintained; PMD provides CyclomaticComplexity (reportLevel default 10) + UnusedPrivate* rules + CPD. detekt is the Kotlin standard — **note detekt 2.0 is still alpha; 1.23.8 is the stable line and in maintenance**, so pin to it. SpotBugs (4.9.8) + FindSecBugs (1.14.0) is the strongest Java SAST. error-prone (2.44.0) catches bugs at compile time (requires JDK 21+ since 2.43.0). PMD CPD is the canonical JVM duplication detector and the format other tools emulate.

**Install + config (Gradle):**
```kotlin
plugins {
  id("com.diffplug.spotless") version "8.6.0"
  id("io.gitlab.arturbosch.detekt") version "1.23.8"   // Kotlin
}
spotless {
  java { googleJavaFormat("1.28.0") }
  kotlin { ktfmt("0.63") }
}
```
```yaml
# detekt.yml — complexity ceilings
complexity:
  CyclomaticComplexMethod: { threshold: 15 }
  CognitiveComplexMethod: { threshold: 15 }
```

**Pre-commit (pre-commit framework or Lefthook):**
```yaml
pre-commit:
  commands:
    fmt:  { run: ./gradlew spotlessCheck }
    lint: { run: ./gradlew detekt }
```

**CI:** `./gradlew spotlessCheck detekt pmdMain cpdCheck checkstyleMain spotbugsMain test dependencyCheckAnalyze`.

**Alternatives:** ktlint (1.8.0, Dec 2025) instead of ktfmt if you want a linter+formatter with rule control; Palantir Java Format (2.91.0, lambda-friendly 120-col) instead of google-java-format; jscpd for duplication if you want one cross-language tool across a polyglot monorepo instead of PMD CPD.

**Avoid / legacy:** FindBugs (dead → SpotBugs); old Checkstyle/PMD 6.x (→ 7.x/13.x); relying on IDE-only inspections in CI.

**Secrets/deps:** gitleaks; OWASP dependency-check (12.2.2) or OSV-Scanner; Dependabot/Renovate. **SAST (deep):** CodeQL (Java is a CodeQL strength).

---

## Ruby (Gemfile)

**Consolidation flag:** RuboCop is linter + formatter + complexity (Metrics/* cops) in one gem. StandardRB wraps RuboCop with a zero-config, unconfigurable ruleset. For duplication, flay (structural similarity) or jscpd.

| Category | Tool | One-liner | Status |
|---|---|---|---|
| Lint+Format+Complexity | **RuboCop** (or **StandardRB**) | Linter/formatter w/ Metrics complexity cops | actively maintained |
| Duplication | **flay** / jscpd | Structural code-similarity detector | maintained |
| SAST | **Brakeman** | Rails static security scanner | actively maintained |
| Dep audit | **bundler-audit** | Scans Gemfile.lock vs ruby-advisory-db | maintained |

**Why RuboCop/StandardRB:** RuboCop is the ecosystem standard; StandardRB (built on RuboCop + rubocop-performance) gives an opinionated, no-config experience with monthly updates. Both exit non-zero on offenses. Brakeman is the canonical Rails SAST. bundler-audit is the standard gem-vuln check. flay/flog (Ryan Davis) cover duplication and per-method complexity scoring.

**Install + config:**
```ruby
# Gemfile (group :development, :test)
gem "rubocop", require: false        # or: gem "standard"
gem "brakeman", require: false
gem "bundler-audit", require: false
gem "flay", require: false
```
```yaml
# .rubocop.yml
AllCops: { NewCops: enable }
Metrics/CyclomaticComplexity: { Max: 10 }
Metrics/PerceivedComplexity: { Max: 10 }
```

**Pre-commit (Lefthook or Overcommit):**
```yaml
pre-commit:
  commands:
    lint: { run: bundle exec rubocop }
```

**CI:** `bundle exec rubocop` + `bundle exec brakeman -q -z` + `bundle exec bundler-audit check --update` + `bundle exec rspec` + `bundle exec flay lib`.

**Alternatives:** StandardRB when you want zero style debate; Reek/Flog/RubyCritic for deeper code-smell/complexity metrics.

**Avoid / legacy:** standalone `rubocop-` chaos without a base config; rails_best_practices is lower-priority now.

**Secrets/deps:** gitleaks; bundler-audit + OSV-Scanner; Dependabot/Renovate.

---

## PHP (composer.json)

**Consolidation flag:** PHPStan (or Psalm) is the static-analysis + dead-code + type-checking engine; Laravel Pint wraps PHP-CS-Fixer with zero-config presets for formatting. Rector handles automated refactors/dead-code removal. **phpcpd (sebastianbergmann) is abandoned/archived — use jscpd** for PHP duplication.

| Category | Tool | One-liner | Latest (2026) |
|---|---|---|---|
| Format | **Laravel Pint** | Zero-config PHP-CS-Fixer wrapper | v1.29.1 (Apr 20 2026) |
| Static analysis / type / dead-code | **PHPStan** (or **Psalm**) | Finds bugs/type errors w/o running code | PHPStan 2.2.x; Psalm 6.x |
| Duplication | **jscpd** (phpcpd dead) | Copy-paste detection (PHP supported) | maintained |
| SAST (taint) | **Psalm** taint analysis / Semgrep | SQLi/XSS taint tracking | maintained |
| Complexity | **PHPMD** | Mess detector incl. cyclomatic complexity | maintained |
| Dep audit | **composer audit** | Built-in vuln check vs PHP advisory DB | bundled w/ Composer |

**Why these:** PHPStan (2.x line, full PHP 8.5 support announced May 28 2026) is the most-adopted analyzer; use baseline on legacy and raise `level` (0→max) incrementally. Laravel Pint (1.29.1, Apr 2026, built on PHP-CS-Fixer) is the modern default formatter. Psalm (6.x, actively maintained in 2026) adds built-in taint analysis PHPStan lacks. `composer audit` ships with Composer. For duplication, phpcpd is no longer maintained, so jscpd is the live option.

**Install + config:**
```
composer require --dev phpstan/phpstan laravel/pint phpmd/phpmd
```
```neon
# phpstan.neon
parameters:
  level: 6
  paths: [src]
```

**Pre-commit (Lefthook):**
```yaml
pre-commit:
  commands:
    format: { run: vendor/bin/pint --test }
    stan:   { run: vendor/bin/phpstan analyse }
```

**CI:** `vendor/bin/pint --test` + `vendor/bin/phpstan analyse --error-format=github` + `composer audit` + `vendor/bin/phpunit` + `jscpd src --threshold 5`.

**Alternatives:** PHP-CS-Fixer or PHP_CodeSniffer directly if you need fine-grained rules; Psalm instead of PHPStan if you want taint analysis as primary.

**Avoid / legacy:** raw PHPCS-only setups for new projects (→ Pint); PSR-2 (deprecated → PSR-12/PER); phpcpd (abandoned → jscpd); Phan is niche now.

**Secrets/deps:** gitleaks; `composer audit` + OSV-Scanner; Dependabot/Renovate. **Note:** Composer had CVE-2026-40176 / CVE-2026-40261 (CVSS 8.8 command-injection in the Perforce driver) disclosed in 2026 — keep Composer ≥ 2.9.6 / 2.2.27 LTS.

---

## Language-agnostic section

### One-command "verify" harness
- **Recommended convention:** a single `just verify` recipe (or `make verify`) that runs, in order, **format-check → lint → typecheck → test → duplication → security**, exiting non-zero on first failure. **`just`** (Rust, cross-platform, clean syntax, `just --list` discoverability) is the best general command runner for new polyglot repos in 2026; **Make** where a working Makefile or real file-dependency graph exists; **npm scripts** only for pure JS/TS repos.
- Example `justfile`:
```
verify: fmt-check lint typecheck test dupes security
fmt-check:   biome format . && ruff format --check .
lint:        biome check . && ruff check .
typecheck:   tsc --noEmit && ty check
test:        pytest && npm test
dupes:       jscpd . --threshold 5 --reporters console
security:    semgrep ci && gitleaks detect && osv-scanner -r .
```

### Code duplication / repetition (NEW first-class category)
LLM-generated code duplicates heavily, so clone detection belongs in any AI-collaboration hardening skill alongside dead-code and complexity.

| Tool | Scope | Why |
|---|---|---|
| **jscpd** v5 | Language-agnostic default | Rust rewrite, 223+ languages, single binary (no Node), 24-37x faster than v4, `--threshold N` fails CI, JSON/HTML/console/`ai` reporters, MCP server, emits pmd-cpd XML format. Actively maintained (npm updated Jun 2026). |
| **PMD CPD** | JVM-centric + ~18 langs | `pmd cpd --minimum-tokens 75 --dir src/`; Rabin-Karp; free, fast, integrates with every build tool; the format jscpd emulates. Best where you already run PMD. |
| **fallow** | JS/TS only | Reports "clone families" as part of consolidated dead-code/complexity audit; agent-friendly JSON/MCP. New (2.x, near-daily releases); syntactic-only. |
| SonarQube / DeepSource / Codacy | Platform / CI gate | Managed quality gates that block PRs above duplication thresholds; heavier, hosted. Use when you want a dashboard + policy enforcement, not just a CLI. |

- **Default:** jscpd as the cross-stack CLI; PMD CPD where PMD is already in the JVM build; fallow for JS/TS repos wanting one consolidated dead-code+dupes+complexity pass. **Note:** these are token/structural (Type-1/2/3) detectors; Type-4 semantic clones need heavier tools (CloneDR, Coverity) and are rarely worth it outside safety-critical code. Zero duplication is not the target — gate on a sane threshold (e.g., 3-5%).

### End-to-end / runtime QA (NEW category)
*(e2e section verified 2026-06-15.)* Unit tests assert on internals; they never prove the artifact actually runs and produces the right observable output. Agents routinely ship a green build that renders a blank screen, a dead button, or a 500. Pick by **artifact type**, not backend language — the web-UI driver is the same whether the backend is Python or Go.

**Web UI (any backend):**
| Tool | Why | Status |
|---|---|---|
| **Playwright** | Cross-stack default. Out-of-process (multi-tab/origin), parallel for free on any CI, official bindings for **JS/TS, Python, Java, .NET**, Trace Viewer, built-in `toHaveScreenshot()` visual snapshots. Clean non-zero exit + deterministic, machine-readable output → agent-friendly. Default for web **and Electron**. | v1.60.0 (May 2026); ~33M wk npm downloads, ~45% adoption, surpassed Cypress mid-2024 |
| **Cypress** | Best interactive debugging/DX for frontend-heavy apps. In-browser architecture limits multi-tab/cross-origin; parallelization needs paid Cloud (can exceed ~$30k/yr at large scale). | Maintained; ~6.5M wk downloads |
| **WebdriverIO** | W3C WebDriver; strong for cross-browser + mobile-web on real-device grids. | Maintained |

- **Avoid / legacy:** raw **Selenium WebDriver** for greenfield (older sync model; keep only for existing Selenium grids); **Puppeteer** for cross-browser E2E (Chrome-centric — fine for scraping/Chrome-only flows).
- **Visual regression** (catches "looks broken" that assertions miss): **Playwright `toHaveScreenshot()`** (built-in, baselines in git) is the default; **Chromatic** (Storybook-native — each story becomes a visual test; hosted parallel fleet) for component libraries; **Percy** (multi-framework, BrowserStack dashboard, cross-browser) when you want a hosted review UI.
- **Component testing:** Storybook + test runner, or Playwright component testing — exercise components in a real browser without booting the full app. Use for design systems.

**Mobile:**
- **Maestro** — fastest setup, YAML flows, low flakiness, cross-platform (iOS/Android/RN/Flutter/web). Default for most apps.
- **Detox** — gray-box, lowest flakiness for **React Native**; pick for pure RN.
- **Appium** — native depth, any language, Selenium-style; pick for deep native needs or existing Selenium infra. Heaviest setup/maintenance.

**API / service (no UI, or the backend of one):**
- **In-process integration** (fastest — drive the app's HTTP layer in-memory): JS/TS → **supertest**; Python → **httpx/requests + pytest** (or the Django/Flask test client); Go → **net/http/httptest**; JVM → **REST Assured / MockMvc**; Ruby → **rack-test**; PHP → **Pest/PHPUnit feature tests** (Laravel HTTP tests).
- **Schemathesis** — language-agnostic: generates property-based cases from the OpenAPI/GraphQL spec and finds boundary/type/constraint edge cases the happy path misses. Run against the running service.
- **Pact** — consumer-driven **contract** testing across services; add early in microservices to catch integration breaks before deploy. Cross-language.
- **k6** — load/perf + smoke, scriptable in JS, strong Grafana ecosystem, runs in CI. **Karate** bundles API + BDD + contract. Dev/manual exploration: **Bruno** or **Hoppscotch** (open-source, git-friendly Postman alternatives).

**CLI:**
- **bats-core** — Bash Automated Testing System, TAP-compliant; drives the real binary and asserts stdout/exit. Language-agnostic (it just runs commands). Default for CLI E2E.
- **expect / pexpect** (Python) — for interactive/PTY prompts. **cli-testing-library** (npm) — framework-agnostic input simulation.
- Native: invoke the built binary in the language's test framework and **snapshot the output** — `insta` (Rust), `syrupy` (Python), jest/vitest snapshots (JS).

**Library (no runnable artifact):** integration/example tests that exercise the **public API** for real (not internals) + snapshot tests of outputs. No browser/UI harness — match the artifact.

**Wiring & evidence:**
- Put fast checks (in-process API/integration, CLI) in the local `verify`; keep slow full-browser/mobile E2E in **CI** — still gating merges.
- Capture **observable evidence** a human or agent can inspect: Playwright trace + screenshot baselines, captured stdout/exit, HTTP response snapshots.
- Keep it a **thin real-exercise layer** that proves the artifact runs (smoke + critical paths), not an exhaustive E2E suite.

### Pre-commit frameworks (pick one default per ecosystem)
| Framework | Lang | Strengths | Default for |
|---|---|---|---|
| **Lefthook** | Go binary | Fastest, parallel by default, single YAML, language-agnostic, no Node runtime | Polyglot / Go / Rust / Ruby / PHP / monorepos |
| **pre-commit** | Python | Largest ecosystem of pre-built hooks, full env isolation | Python projects |
| **Husky + lint-staged** | Node | De-facto JS standard (~25M wk downloads) | JS/TS-only repos already on Node |

- **Default:** **Lefthook** for any polyglot repo. **pre-commit** for Python-centric repos. **Husky+lint-staged** only for pure-JS teams. Always also enforce checks in CI — hooks are bypassable with `--no-verify`.

### SAST
- **Best language-agnostic default: Semgrep** — 30+ languages incl. PHP/Terraform/Dockerfile, ~10s CI scans, YAML rules, SARIF output, generous free tier (note the Opengrep fork after some engine features moved behind a license).
- **CodeQL** — deeper whole-program/taint analysis; per the "Sifting the Noise" study (arXiv:2601.22952, 2025) on OWASP Benchmark v1.2 (2,740 Java cases), CodeQL F1 74.4% (precision 60.3%, recall 97.0%) vs Semgrep F1 69.4% (precision 56.3%, recall 90.4%). GitHub-native, slower (minutes), best nightly; no PHP/IaC. Many teams run both: Semgrep per-PR, CodeQL nightly.
- **Strongest stack-specific SAST:** JS/TS → Semgrep/CodeQL; Python → Bandit (or Ruff `S`); Go → gosec + govulncheck; Rust → cargo-audit + Clippy; Java → SpotBugs+FindSecBugs / CodeQL; Ruby → Brakeman; PHP → Psalm taint / Semgrep.

### Secret scanning
- **gitleaks** — fast, regex+entropy, MIT, `.gitleaks.toml`; best as pre-commit hook + CI diff scan; SARIF output. **Note:** original author Zach Rice (now at Aikido Security as of Feb 2026) launched a successor, **Betterleaks** (v1.1.0, Mar 2026; MIT, same rule format/CLI), citing reduced control over the gitleaks repo; its BPE token-efficiency filter reports higher recall than entropy. gitleaks still works but slowed after the move.
- **TruffleHog** — 800+ detectors with live credential verification; best in CI / scheduled history sweeps, slower. **Convention:** gitleaks (or Betterleaks) at the edge (pre-commit + PR diff), TruffleHog scheduled for verified history audits.
- Others: detect-secrets (baseline for brownfield repos), GitHub Secret Scanning / push protection.

### Dependency / supply-chain audit
| Scope | Tool |
|---|---|
| Language-agnostic | **OSV-Scanner** (Google, OSV.dev, 11+ ecosystems) |
| Per-stack | npm/pnpm audit (JS), pip-audit (Py), govulncheck (Go), cargo-audit/cargo-deny (Rust), OWASP dependency-check (JVM), bundler-audit (Ruby), composer audit (PHP) |
| Containers/SBOM | Grype + Syft (SBOM); Trivy (broad scanner — see caveat) |
| Automated update PRs | **Renovate** or **Dependabot** |

- **Recommendation:** OSV-Scanner as the cross-stack baseline + the native per-stack auditor + Renovate/Dependabot for automated upgrade PRs.

### Complexity ceilings (sane defaults + flags)
| Tool | Metric | Flag/config | Typical ceiling |
|---|---|---|---|
| Ruff | cyclomatic (mccabe) | `[tool.ruff.lint.mccabe] max-complexity` | 10 |
| Biome | cognitive | `noExcessiveCognitiveComplexity` | 15 (default) |
| fallow | cyclomatic + cognitive (maintainability index) | health thresholds in config | tool default |
| golangci-lint | cyclomatic / cognitive | gocyclo `min-complexity` / gocognit `min-complexity` | 15 / 20 |
| Clippy | cognitive | `cognitive_complexity` lint threshold | ~25 (default) |
| PMD | cyclomatic | CyclomaticComplexity `reportLevel` | 10 |
| detekt | cyclomatic / cognitive | `CyclomaticComplexMethod` / `CognitiveComplexMethod` threshold | 15 |
| RuboCop | cyclomatic / perceived | `Metrics/CyclomaticComplexity Max` | 6–10 |
| PHPMD | cyclomatic | `codesize` ruleset `reportLevel` | 10 |
| jscpd | duplication % | `--threshold N` | 3–5% |

---

## Cross-cutting takeaways
1. **Consolidate aggressively:** Ruff (Python), Biome (JS/TS), golangci-lint (Go), Clippy+rustfmt (Rust), Spotless+detekt (JVM), RuboCop (Ruby), PHPStan+Pint (PHP) each collapse multiple legacy tools. In JS/TS, **fallow** is an emerging single-binary consolidation of dead-code + duplication + complexity (watch its maturity).
2. **Duplication is now a first-class category.** AI-generated code clones heavily; gate on jscpd (cross-stack) / PMD CPD (JVM) / fallow (JS/TS) at a sane threshold (3–5%).
3. **Rust-based tools won 2025-2026:** Ruff, Biome, oxlint, ty, Pyrefly, jscpd v5, fallow — speed enables running checks on every commit.
4. **One `just verify` entry point** chaining format→lint→typecheck→test→dupes→security with non-zero exit is the agent-friendly contract.
5. **Pin CI actions to commit SHAs, not tags.** The Trivy supply-chain compromise (GHSA-69fq-xp46-6x23 / CVE-2026-33634, CVSS 9.4, Mar 19 2026) saw 76 of 77 `aquasecurity/trivy-action` tags force-pushed to credential-stealing payloads over ~12 hours — only the GitHub-immutable release was unaffected. Treat any tool/action referenced by mutable tag as a supply-chain risk.
6. **Treat brand-new tools (fallow, ty, Betterleaks) as candidates, not settled defaults** — verify each tool's release page before relying on the versions here.
7. **Runtime QA is a first-class category.** Green unit tests don't prove the artifact runs — drive the real thing and observe its output (Playwright for web/Electron, the stack's in-process integration for APIs, bats-core for CLIs) and capture evidence. Pick by artifact type, not backend language.
