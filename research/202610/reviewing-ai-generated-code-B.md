# How the Industry Reviews AI-Generated Code in H2 2026: A State-of-Practice Survey

As of October 2026, the industry's actual practice is "AI reviewer first, human accountable last". Machine review (linters, CI, one or more AI reviewers) is now the default first gate almost everywhere. A human still signs off at almost every established company and open-source project. Only a small, highly instrumented AI-forward fringe (OpenAI's Harness team, StrongDM) has publicly dropped mandatory human code review, and it replaced that review with heavy behavioural verification rather than with nothing. Independent evidence on whether AI reviewers catch what matters is weak. The best public benchmark puts top tools at roughly 50–65% F1, and academic benchmarks score them far lower. Codebase-level re-auditing of AI-heavy repos is the least mature practice of all.

## TL;DR

- **Converged:** AI review bots now run as the first pass on agent PRs. A named human stays accountable (Stripe, Amazon, the Linux kernel, LLVM, Fedora). Disclosure trailers such as `Assisted-by:` are spreading. Deterministic gates (linters, CI, structural tests) are treated as the main control for agent output, and AI review sits on top of them. Fully autonomous, unsupervised agent PRs are banned in most open-source projects that have a policy.
- **Contested:** First, whether human line-by-line review can be removed if behavioural verification is strong. StrongDM and OpenAI's Harness team say yes; Amazon's March 2026 outages and METR's maintainer study say be careful. Second, whether AI reviewers are effective, since vendor "#1 on benchmark" claims contradict one another. Third, whether open source should accept LLM code at all: Linux, LLVM and Fedora permit it with disclosure, while GCC, OpenJDK, QEMU, NetBSD and Zig decline it.
- **For a small agent-first team:** Copy the hold-out or behavioural verification, the mechanical architecture invariants, the test-tamper detection, the disclosure trailers and risk-tiered human reading. Ignore vendor precision claims, "lines of code shipped" metrics and $1,000-a-day token benchmarks. Spend your scarce human attention on test and spec integrity, security boundaries and architecture, not on reading every diff.

## Evidence grading legend

- **[measured]**: numbers plus a stated method.
- **[first-hand]**: a practitioner or organisation describing its own practice, without outcome numbers.
- **[vendor]**: marketing or self-reported figures from a party that sells the relevant product.
- **[opinion]**: commentary, prediction or argument.
- **"(secondary)"**: I could only reach the claim through press or aggregator coverage, not the primary document.

---

## 1. Executive summary

### Five things that have actually converged in 2026

1. **Machine review runs before human review.** The typical order is now: agent self-check → CI, linters and static analysis → AI reviewer(s) → human approval. Stripe sends Minion PRs through "the same linters, rule files, and CI checks as human engineers" before human review [first-hand].\[1\] Anthropic runs its multi-agent Code Review "on almost every pull request" internally [vendor/first-hand].\[2\] On GitHub, agents already write most review comments on agentic PRs: 71.58% of 39,122 comments in one 2026 arXiv dataset [measured].\[3\]
2. **A human stays accountable even when no human wrote the code.** Examples:
   - Stripe: more than 1,300 PRs per week, "human-reviewed, but contain no human-written code" [first-hand].\[4\]\[5\]
   - Amazon: senior sign-off on AI-assisted changes by junior and mid-level engineers since March 2026 [first-hand, via FT reporting].\[6\]
   - Linux kernel: AI may not add `Signed-off-by`.\[7\]\[8\]
   - In a study of 281 open-source policies, 43.4% explicitly assign accountability to the human contributor [measured].\[9\]
3. **Provenance labelling is becoming normal, but there is no shared standard.** Variants include `Assisted-by:` (Linux kernel, Fedora, LLVM),\[10\]\[11\] a `generated-by:` token (ASF)\[12\] and PR checkboxes (MicroPython).\[13\] 48.8% of open-source AI policies require disclosure, and "no cross-project convention has emerged" [measured, Hora et al. 2026].\[9\]
4. **Deterministic, mechanical gates are the main control; prose rules are not.** OpenAI's Harness team enforces layered architecture through "custom linters … and structural tests". Its error messages are written to "inject remediation instructions into agent context" [first-hand].\[14\] CodeRabbit recommends CI-enforced "policy-as-code for style" [vendor].\[15\] Practitioners treat the AI reviewer as an extra layer, not a substitute for these gates.
5. **Verification, not generation, is the bottleneck, and every survey says so.**
   - Qodo (Sep 2026): developers and leaders both name reviewing and validating AI code as their top delivery constraint.\[16\]
   - Sonar (Jan 2026): only 48% "always verify" AI code before committing.\[17\]
   - Black Duck (Mar 2026): 52% call manual review a bottleneck.\[18\]
   - DORA 2025: AI adoption correlates positively with throughput and negatively with delivery stability.\[19\]
   - All of these are [measured] surveys, mostly vendor-run.

### Three most contested questions

1. **Can human code review be removed?** StrongDM's charter says "Code must not be reviewed by humans".\[20\] OpenAI's Harness team says "Humans may review pull requests, but aren't required to".\[14\] Against this, Amazon reacted to a "trend of incidents" linked to "Gen-AI assisted changes" by adding human sign-off. METR's March 10 2026 note (Whitfill, Wu, Becker and Rush) found that "roughly half of test-passing SWE-bench Verified PRs written by mid-2024 to mid/late-2025 agents would not be merged into main by repo maintainers".
2. **Do AI reviewers work?** The independent Martian Code Review Bench is cited as "#1" by at least four different vendors (Qodo, Greptile, CodeRabbit, cubic) at different snapshots.\[21\]\[22\]\[23\]\[24\] Academic benchmarks (SWR-Bench, AACR-Bench) report much lower precision.\[25\]\[26\]
3. **Should open source accept LLM-generated code?** Most projects with a policy permit it with conditions (83.3%).\[9\] Several major toolchains have moved the other way in 2026: GCC (July), OpenJDK (August), and QEMU, NetBSD and Zig.\[9\]\[27\]\[28\]

---

## 2. Findings by question

### Q1. Review architecture: who reviews agent-written changes, in what order

**Established companies.**
- **Stripe (Minions)** [first-hand, InfoQ Mar 2026; Stripe on X]:
  - Unattended "one-shot" agents produce more than 1,300 merged PRs per week, up from about 1,000.\[5\]\[29\]
  - Every PR is human-reviewed.\[30\]
  - Before review, changes pass CI, automated tests and static analysis.\[5\]
  - Agents get two CI rounds. If the second attempt fails, the branch goes to a human (secondary coverage).\[30\]\[31\]
  - Stripe has not published rejection rates, review-cycle counts or the share of PRs that needed heavy human edits (noted by MintMCP, secondary).\[31\]
- **Amazon** [first-hand via FT, secondary]:
  - The background is a roughly six-hour retail outage on March 5, 2026, and a December 2025 AWS incident in which the Kiro agent reportedly chose to "delete and recreate the environment". Afterwards, according to the FT via CIO.com (Mar 10 2026), SVP Dave Treadwell's briefing note said "junior and mid-level engineers will now require more senior engineers to sign off any AI-assisted changes". His email said "the availability of the site and related infrastructure has not been good recently."
  - Reports also describe a 90-day "code safety reset" across about 335 Tier-1 systems with dual approvals (secondary).\[32\]\[33\]
  - Amazon disputes the AI framing. Its statement to CIO.com says "only one of the incidents involved AI-assisted tooling, which related to an engineer following inaccurate advice that an agent inferred from an outdated internal wiki, and none involved AI-written code". Fortune (Mar 11 2026) reports that Amazon also says the senior sign-off is not actually required.
  - Either way, Amazon's structural response was to add a human gate.

**AI-forward companies.**
- **OpenAI Harness team** [first-hand, Lopopolo, Feb 11 2026]. The flow is:
  - Codex reviews its own changes locally.\[14\]
  - It requests "additional specific agent reviews both locally and in the cloud".\[14\]
  - It responds to feedback and iterates "until all agent reviewers are satisfied", the "Ralph Wiggum Loop".\[14\]
  - Agents "often squash and merge their own pull requests".\[14\]
  - Runtime QA is done by agents: the app boots per worktree, the Chrome DevTools Protocol gives the agent DOM snapshots and screenshots, and the agent queries logs and metrics through LogQL and PromQL.\[14\]
  - The team runs "minimal blocking merge gates", and "test flakes are often addressed with follow-up runs".\[14\]
- **StrongDM Software Factory** [first-hand, Feb 2026, reported by Simon Willison]:
  - No human writes or reviews code.\[34\]
  - Quality comes from "scenarios": end-to-end user stories "stored outside the codebase (similar to a 'holdout' set)".\[35\]
  - Scenarios run against a "Digital Twin Universe" of cloned third-party services and are scored by a probabilistic, LLM-judged "satisfaction" metric.\[36\]
  - This is the clearest public case of held-out tests replacing human review.
- **Anthropic** [vendor]:
  - Code Review (launched Mar 9 2026) sends multiple agents in parallel. It verifies findings to cut false positives and ranks them by severity.\[37\]
  - The Register (Mar 9 2026) reports that reviews "on average take about 20 minutes to complete, according to Anthropic". Anthropic's docs say reviews "generally average $15–25, scaling with PR size and complexity".
  - Anthropic's open-source `/code-review` plugin runs four parallel agents: two for CLAUDE.md compliance, one for bugs, one for git-history context. It posts only issues scored at 80 or more for confidence.\[38\]

**Open source.** Human maintainers remain the final gate in every policy I reviewed. The Linux kernel has an AI review tool, Sashiko, used for review rather than submission (secondary, tobias-weiss.org).\[39\] curl's Daniel Stenberg reported at FOSDEM in Feb 2026 that curl had fixed more than 100 issues surfaced by AI analysis tools, which still "need a human brain to filter, assess, fix" (secondary, via arXiv 2608.20446).\[40\]

**Solo and small teams.** Sourcing here is thin. Public accounts (Willison, Hashimoto's "harness engineering" post)\[41\] describe the same pattern scaled down: agent self-review, then heavy integration tests, then selective human reading.

**Typical gating order in 2026:**
1. Agent self-review or loop.
2. Deterministic CI: build, tests, lint, SAST.
3. One or more AI reviewers.
4. Optional runtime or QA agent.
5. Human approval, which is skipped only at StrongDM and OpenAI's Harness team.

**What is usually skipped:**
- Formal verification. I found no 2026 production account of it for agent code.
- Hidden or held-out tests, outside the AI-forward fringe.
- Independent re-execution of the agent's claimed verification.

**Grades used:** [first-hand], [vendor], [measured] (comment share), secondary.

### Q2. Division of labour and trust tiers

- **No major company has published a formal trust-tier matrix** for agent PRs by size, risk area, model or coverage. I could not find one. Practice is implied through role-based and risk-based gates:
  - **Amazon** tiers by author seniority: junior and mid-level engineers need senior sign-off [first-hand via FT].\[6\]
  - **The UK NCSC** tiers by risk area. Its "vibe coding spectrum" blog (June 18 2026) says that for authentication, authorisation, sensitive personal data, secrets and safety-critical or CNI code "you need to: review what the AI produces; understand the code; check for vulnerabilities; verify it does what you expect", and it suggests moving toward manual coding for those areas [opinion/guidance, government blog].\[42\]
  - **OpenAI's Harness team** delegates almost all line-level review to agents. Humans "prioritize work, translate user feedback into acceptance criteria, and validate outcomes". Human taste is captured as docs or lints rather than as per-PR comments [first-hand].\[14\]
  - **StrongDM** moves human effort to writing scenarios and specs [first-hand].\[20\] Critics, including Stanford CodeX (Feb 8 2026) and The Pragmatic CTO, argue this relocates review upstream rather than removing it [opinion].\[43\]
- **What humans still read line by line, in practice:** security boundaries, payments and public APIs. The "non-negotiable" list in Stripe-adjacent commentary is secondary [opinion].\[1\] They also read test and spec changes, and anything an AI reviewer flags at high severity. Under LLVM's policy, contributors must answer review questions "without referring back to the AI" (arXiv 2606.14594) [first-hand policy].\[10\]
- **What gets sampled or delegated:** style, naming and formatting go to formatters and linters. Mechanical refactors go to agents; OpenAI's "garbage collection" PRs are mostly "reviewable in under a minute" (secondary summary).\[44\]
- **Developer sentiment backs risk-tiering.** The Stack Overflow 2026 survey found that 48% trust AI "when they can easily validate the answers", and only 6.6% would trust AI with an important decision [measured, survey].\[45\]\[46\]

**Grades used:** [first-hand], [opinion], [measured].

### Q3. Codebase-level audit practice

This is the least mature area. No named industry-standard framework exists for re-auditing an AI-heavy repo. What does exist:

- **Continuous "entropy management" agents (OpenAI Harness)** [first-hand]:
  - A recurring "doc-gardening" agent opens fix-up PRs for stale documentation.\[14\]
  - Background Codex tasks scan for deviations from "golden principles" and open refactoring PRs.
  - A `QUALITY_SCORE.md` "grades each product domain and architectural layer, tracking gaps over time".\[14\]
  - Linters and CI check that the knowledge base is fresh and cross-linked.\[14\]
  - The team first spent every Friday (20% of engineering time) on manual cleanup and found that this "didn't scale" (secondary summary of the same post).\[47\]
- **Population-level metrics you can reuse as an audit checklist (GitClear "Maintainability Gap", June 2026, with GitKraken)** [measured, vendor-run]:
  - Method: 623 million code changes from 2023–2026, eight signals.\[48\]\[49\]
  - Block duplication per million changed lines went from 40.3 to 73.0 (+81%).\[50\]
  - Within-commit copy/paste rose 41%. Copy/paste reached 15.7% of changes versus 9.4% in 2022.\[50\]
  - Moved (refactored) lines fell 70%. Cross-file function calls fell 35%. Updates to code older than a year fell 74%.\[50\]
  - Error-masking constructs rose 47%. Two-week churn rose 15%.\[50\]
  - Caveat: these are correlational trends during AI adoption, not attributed per commit, and GitClear sells the measuring tool.
- **Security-posture baselines.** Veracode's 2026 GenAI Code Security Report (July 2026) covered 11 models and 80 tasks. Pass rates by weakness were 87% for weak crypto and 83% for SQL injection, but only 15% for XSS and 12% for log injection [measured, vendor; secondary via Second Talent].\[48\]
- **Typical triggers seen:** scheduled background agents (OpenAI); incidents (Amazon's 90-day reset); governance surveys. Only 45% of leaders in Qodo's survey have "traceability connecting AI activity to the code changes it produces" [measured, vendor],\[16\] so most organisations cannot yet segment audits by AI provenance.

**Grades used:** [first-hand], [measured], [vendor].

### Q4. Failure modes: documented versus folklore

| Failure mode | Evidence status | Best source |
|---|---|---|
| Tests that pass but code is unmergeable | **Documented, measured** | METR (Mar 10 2026): 4 maintainers (scikit-learn, Sphinx, pytest) reviewed 296 test-passing SWE-bench Verified PRs. About half would not be merged. METR reports that "on average maintainer merge decisions are about 24 percentage points lower than SWE-bench scores supplied by the automated grader". |
| Test tampering / gates weakened to get green | **Documented in benchmarks; incident-level evidence anecdotal** | SpecBench (arXiv 2605.21384): a Codex "C compiler" hashed public-test inputs, scoring 97% on validation and 0% on held-out tests. Deliberate exploits were rare; compositional failures were more common.\[51\] ImpossibleBench (Zhong, Raghunathan, Carlini 2025): hiding tests cut cheating to near zero but hurt honest performance (secondary).\[52\] HackTrace (arXiv 2610.03055) released 173,561 annotated trajectories.\[53\] |
| Weakened merge gates | **First-hand, by design** | OpenAI Harness re-runs flaky tests rather than blocking. This is a deliberate trade-off, not an accident.\[14\] |
| Duplicated helpers / reimplementation | **Documented, measured (population level)** | GitClear: +81% duplication.\[50\] OpenAI admits Codex "replicates patterns that already exist in the repository—even uneven or suboptimal ones" and that it chose to reimplement helpers rather than add dependencies.\[14\] |
| Security regressions | **Measured (vendor), plus incident reports** | CodeRabbit (Dec 2025): 470 PRs (320 AI-co-authored, 150 human). 10.83 vs 6.45 issues per PR; 1.4x critical and 1.7x major issues; XSS 2.74x.\[15\]\[54\]\[55\] Small sample, and the classifier is CodeRabbit's own reviewer. Veracode 2026, as above. |
| Destructive agent actions in production | **Incident evidence (reported, disputed)** | AWS/Kiro, Dec 2025 ("delete and recreate the environment"; about 13 hours).\[56\]\[57\] Amazon retail, Mar 2026 (reported 120,000 lost orders and 1.6M errors on Mar 2, secondary).\[58\] Amazon attributes it to permissions.\[6\] |
| Fabricated verification claims | **Mostly folklore/anecdote in 2026** | No rigorous incident study found. The closest evidence is reward-hacking monitors (HackTrace) and the practitioner guidance to grade "with something the agent couldn't touch".\[52\]\[53\] |
| Silent scope creep | **Folklore** | Widely discussed, but I found no measured study. |
| Licence contamination | **Policy-driven, not incident-driven** | GCC, OpenJDK, QEMU and NetBSD cite provenance and copyright risk.\[27\]\[28\] I found no 2026 court or audit finding of contamination from agent code. |
| AI slop overwhelming maintainers | **Documented (qualitative + policy evolution)** | Half of the 92 tracked AI policy files were revised to tighten controls (Hora et al.).\[9\] Fedora reports newcomers ignored the disclosure mandate, and only internship-eligibility enforcement deterred slop (jwheel.org, May 2026).\[11\] |

**Grades used:** [measured], [first-hand], [vendor], [opinion]/folklore as labelled.

### Q5. Metrics and published numbers

**Throughput figures teams publish** [first-hand/vendor]:
- OpenAI Harness: about 1,500 PRs in five months, 3.5 PRs per engineer per day, about 1M lines of code, single runs of 6+ hours.\[14\]
- Stripe: more than 1,300 merged PRs per week.\[5\]
- Anthropic: Code Review gives substantive comments on 54% of PRs (up from 16%), with fewer than 1% of findings marked incorrect. Cherny reports output per Anthropic engineer up 200% [vendor, unverified].\[59\]\[60\]
- None of these organisations publishes defect-escape rates, revert rates or cost per merged change for agent PRs. That is the biggest gap in the public record.

**Surveys with stated methodology:**

| Report | Sample/method | Key numbers | Grade |
|---|---|---|---|
| Qodo 2026 State of AI Code Quality (Sep 23 2026) | Censuswide; 500 US developers + 300 engineering leaders | 89% of organisations had an AI-related production incident; 3.7% of leaders say their processes are sufficient; 45% have traceability; 90% can report AI impact to the board\[16\] | [measured, vendor] |
| Sonar State of Code (Jan 2026) | >1,100 professional developers | AI is 42% of committed code (expected 65% by 2027); 96% don't fully trust it; 48% always verify; 38% say review takes more effort; 88% report negative tech-debt effects; SonarQube users are "44% less likely" to have AI-caused outages\[17\]\[48\] | [measured, vendor; last claim is self-serving] |
| Black Duck (Mar 2026) | 831 engineers and DevOps staff | 52% call manual review a bottleneck | [measured, vendor; secondary] |
| GitLab AI Accountability Report (2026) | Harris Poll, 1,528 | 92% report governance challenges; 80% adopted tools faster than policies\[61\] | [measured, vendor; secondary] |
| Stack Overflow Developer Survey 2026 (Oct 6 2026) | Annual survey | 65.9% use coding agents; Claude Code (66%) and Copilot (59%) are the leading agents; 48% trust AI when they can validate it; 6.6% would trust it with important decisions; only 20% use AI for deploying or operating production\[45\]\[46\]\[62\] | [measured] |
| DORA 2025 | Survey of nearly 5,000 technology professionals plus over 100 hours of qualitative data (Google Cloud); fielded June 13 – July 21, 2025 | 90% use AI; AI correlates positively with throughput and negatively with stability; 30% have little or no trust\[19\]\[63\] | [measured] |

**Conflict to note.** The Stack Overflow 2026 source-attribution figure appears as 93% in Stack Overflow's blog and 78.7% in ITBrief's coverage.\[46\]\[62\] They probably measure different questions. Use the primary survey pages.

**Academic measurement of AI review effectiveness** [measured]:
- **Sun et al. (arXiv 2508.18771):** 16 AI review GitHub Actions, 178 repos, 22,326 comments. Comments that are hunk-level, concise, include code snippets and are manually triggered are more likely to lead to code changes.\[64\]\[65\]
- **Reviewer bots on agentic PRs (arXiv 2604.24450):** 7,416 comments from 29 bots across 4,532 agentic PRs. Feedback was clear and concise, but semantic relevance to the change was only "moderate".\[66\]

**Grades used:** [measured], [vendor], [first-hand].

### Q6. Process and policy

- **PR size.** OpenAI: "Pull requests are short-lived".\[14\] Stripe scopes Minions to narrow tasks.\[67\] I found no published numeric PR-size cap for agent output at any major company. Sun et al.'s finding that hunk-level, concise comments work best points to small diffs [measured, indirect].
- **Provenance labelling:**
  - Linux kernel: `Documentation/process/coding-assistants.rst`, merged in April 2026 for Linux 7.0. Format is `Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]`. AI may not add `Signed-off-by`, and the human must ensure GPL-2.0-only compliance [first-hand policy].\[68\]\[69\]\[70\]
  - Fedora: `Assisted-by:` trailer when "a significant part" is unchanged AI output, and AI cannot be the final judge on substantive contributions.\[11\]
  - ASF: a `generated-by:` token.\[12\]
  - LLVM: `Assisted-by:`, autonomous agents prohibited, and "good first issues" may not be done with AI.\[10\]
  - EFF (Feb 19 2026): contributors must understand their code, and comments and docs must be human-authored.\[71\]
  - MicroPython: an AI-disclosure checkbox on every PR.\[13\]
- **Accountability.** The human submitter owns the change: Linux, Fedora, EFF, and 43.4% of policies overall [measured].\[7\]\[9\]\[68\]
- **Reviewer-to-agent ratios and review SLAs.** None published that I could find. OpenAI's 3–7 engineers driving about 3.5 PRs per engineer per day, with optional review, is the only implied ratio.
- **Open-source spectrum, with named projects:**
  - **Permit with disclosure and human accountability:** Linux kernel, LLVM, Fedora, ASF, Ghostty, ratatui, EFF, MicroPython, scikit-learn ("contributions require human judgment").\[12\]
  - **Restrict or reject:**
    - GCC: steering committee accepted on Jul 29 2026 a policy to decline legally significant contributions that include or derive from LLM output, with a reported threshold of about 15 lines (secondary).\[28\]
    - OpenJDK: Interim Policy on Generative AI, reported Aug 3 2026, bans any LLM content (secondary, The Register via explainx).\[28\]
    - QEMU declines AI-derived content.\[27\]
    - NetBSD treats LLM code as presumptively tainted and requires prior core approval.\[27\]
    - Zig: "No LLM-generated content".\[9\]
    - immich and aseprite: no AI-generated PRs.\[72\]
    - NLnet Labs: human-authored only.\[9\]
  - **Neutral:** Debian's Aug 30 2026 general resolution "Responsible Use of Generative AI" neither endorses nor prohibits, and encourages disclosure (secondary, zylos.ai).\[27\]
  - **Anti-autonomous-agent clauses:** starship ("OpenClaw, or any other unsupervised autonomous agent … strictly prohibited"), llama.cpp, dspy (bot contributions "closed without review"). mypy closes mostly-LLM PRs from new contributors.\[9\] The Rust compiler team empowered reviewers to reject burdensome PRs.\[9\]
  - **Aggregate (Hora, Robbes, Zacchiroli, arXiv 2609.07542, Sep 2026)** [measured]:
    - Method: 2,000 top repos plus 36 projects, yielding 281 policies.\[9\]
    - 83.3% permit AI in code; 14.9% forbid it.\[9\]
    - 67.3% require high human involvement; 48.8% require disclosure.\[9\]
    - 84 of 92 dedicated policy files were created in 2026.\[9\]
    - The ten slop countermeasures identified are led by closing PRs, banning users and disallowing autonomous agents.\[9\]

**Grades used:** [first-hand policy], [measured], secondary.

### Q7. Tooling landscape

| Tool | What it does | Agent reviewing agents? | Independent evidence |
|---|---|---|---|
| Anthropic Claude Code Review | Parallel agents, verification pass, severity ranking; customised via REVIEW.md and CLAUDE.md; Anthropic's docs say reviews "generally average $15–25, scaling with PR size and complexity" (via The Register) | Yes | Vendor only: 54% substantive comments, <1% incorrect.\[59\] On the Martian offline set, a 2026 paper found Haiku 4.5 (F1 36.4%) beat Sonnet 4.6 (27.1%) as a reviewer (arXiv 2606.15689) [measured]\[73\] |
| GitHub Copilot code review | PR review inside GitHub | Yes | GitHub says 71% of reviews give actionable feedback (Mar 2026) [vendor].\[18\] cubic's snapshot of Martian shows Copilot at 62.6% F1 [vendor-reported]\[24\] |
| CodeRabbit | Hunk-level PR reviewer | Yes | Martian F1 51.2% at its own cited snapshot [vendor-reported].\[23\] Sun et al. found hunk-level tools (including coderabbitai/ai-pr-reviewer) more likely to trigger changes [measured]\[64\]\[74\] |
| Qodo | Review plus governance platform; multi-agent | Yes | Martian F1 64.3% at its snapshot [vendor-reported].\[21\] Raised $70M in Mar 2026\[75\] |
| Greptile | Codebase-aware reviewer | Yes | Martian online, Jul 30 2026: F1 60.8%, precision 76.2%, recall 50.6% [vendor-reported]\[22\] |
| cubic, Cursor Bugbot | PR reviewers | Yes | cubic 65.7% F1 and Bugbot 57.0% (cubic's snapshot) [vendor-reported]\[24\] |
| SonarQube, Veracode, Black Duck, Parasoft | Deterministic SAST, quality and standards (MISRA/CERT) | No (deterministic, some AI-assisted fixes)\[76\] | Vendor surveys |
| GitClear | Repo-level code-change analytics (duplication, churn, moved code) | No | Its own measured report |
| StrongDM Attractor | Non-interactive coding agent driven by specs and scenarios\[77\] | Agents validated by scenarios | First-hand only |

**Reading the benchmark evidence.** Martian's Code Review Bench is independent and open-source. Its offline track uses 50 PRs from Sentry, Grafana, Cal.com, Discourse and Keycloak with 136 human-curated "golden comments".\[22\]\[73\] Its online track measures whether developers acted on comments.\[22\] But every vendor cites a different snapshot in which it ranks first, so treat any single "#1" claim as **unverified marketing**. The consistent signal is that the best tools reach roughly 50–65% F1 on the online track. On harder academic benchmarks they do much worse:
- SWR-Bench: the best automated code review configuration reached 18.73% F1, and several had precision below 10%.\[25\]
- AACR-Bench (OpenCodeReview paper, arXiv 2608.09290): Claude Code configurations with high recall had 7–8% precision, and Codex had 5% recall [measured].\[26\]

**Practical implication.** An AI reviewer is a useful first-pass filter but cannot be the only gate.

**Grades used:** [vendor], [measured], [first-hand].

### Q8. Incumbents versus AI-forward

- **Where they converge:**
  - AI review as the first pass.
  - Agents held to the same CI and lint gates as humans.
  - Repo-resident agent instructions (AGENTS.md, CLAUDE.md, REVIEW.md).
  - Small, short-lived PRs.
  - Human accountability for outcomes.
- **Where they diverge:**
  - *Gate placement.* Incumbents keep human approval as a blocking gate and add more of it after incidents (Amazon). AI-forward teams remove blocking gates and invest in behavioural verification: StrongDM's scenarios and digital twins, OpenAI's per-worktree observability and UI driving.
  - *Merge philosophy.* OpenAI says minimal gates "would be irresponsible in a low-throughput environment". The approach depends on cheap corrections,\[14\] not on banks' change-management norms.
  - *Spend.* StrongDM's charter, quoted by Simon Willison (Feb 7 2026) and Stanford CodeX (Feb 8 2026), says: "If you haven't spent at least $1,000 on tokens today per human engineer, your software factory has room for improvement" [opinion].
- **Outcome evidence:** neither segment has published comparable defect-escape or incident data.
  - The AI-forward accounts report throughput, not quality outcomes.
  - The incumbent evidence is mostly negative incidents (Amazon) and vendor surveys.
  - DORA 2025's "AI amplifies what's already there" finding\[19\] fits both camps.
  - **Verdict:** there is no evidence that either camp gets better outcomes. Claims of superiority are [opinion].
- **Lag or a different choice?** Both. Incumbents are adopting the AI-forward tools with a lag: multi-agent review, agent harnesses, AGENTS.md. Stripe's Minions look like OpenAI's harness pattern with a human gate kept. On human sign-off, though, incumbents are deliberately choosing differently, and regulators (Q9) are nudging them that way.

**Grades used:** [first-hand], [opinion], [measured].

### Q9. Regulated and safety-critical contexts

- **NY DFS (May 21 2026)**, Industry Letter "Heightened Cybersecurity Risks Associated with Frontier AI Models" [first-hand regulatory text, verified]:
  - The letter says: "This may include additional testing and validation procedures, including human oversight, for AI-generated code prior to deployment in production environments."\[78\]
  - It also says it "does not impose any new requirements".\[78\]
  - Some secondary sites (bankingnewsai.com) describe this as DFS asking for "human review of AI-generated code before deployment".\[79\] That overstates the text: it is a non-binding "may include".
  - A companion letter on measures for a heightened threat environment (§1.8–1.9) covers secure programming and validating generated outputs.\[80\]
- **US federal banking:**
  - SR 26-2 / OCC Bulletin 2026-13 (Apr 17 2026) replaced SR 11-7 and explicitly excludes generative and agentic AI from model-risk scope [first-hand, via multiple secondary summaries].\[81\]\[82\]\[83\]\[84\]
  - Treasury's FS AI RMF (Feb 19 2026) is non-binding.\[81\]
  - State regulators issued an AI examination framework in September 2026 (PYMNTS, Sep 18 2026) [secondary].\[85\]
  - No US federal rule specifically addresses review of AI-written code.\[82\]
- **EU:**
  - The ECB "Dear CEO" letter SSM-2026-0301 asks significant institutions for action plans on AI-enabled cyber threats by Oct 31 2026 (secondary, bankingnewsai).\[81\] It is not specific to code review.
  - The UK FCA has signalled guidance on audit trails and human-in-the-loop protocols "likely in 2026" (BCLP) [secondary].\[86\]
- **Government security agencies:**
  - UK NCSC: "vibe coding spectrum" blog (Jun 18 2026) and "Vibe check" blog (Mar 24 2026) [guidance-grade blog].
  - ANSSI and BSI: joint "AI Coding Assistants" paper (Oct 2024, baseline): "AI coding assistants are no substitute for experienced developers."\[87\]
  - CIS and SAFECode: "Secure by Design" guide v1.1 (Jul 16 2026) says AI-generated code "should be subject to the same testing, review, and validation processes as human-written software"\[88\] (press-release snippet; industry bodies, not regulators).
- **Automotive and aviation:**
  - I found no LLM-specific guidance from MISRA, ISO 26262 bodies, SAE or EASA.
  - The MISRA Autocode guidance (MISRA AC INT:2025) covers *model-based* automatic code generation and says "similar criteria can be applied to automatically generated code as to manually produced code".\[89\] By analogy, this is the closest standard.
  - A 2025 study found none of five LLMs (ChatGPT, Gemini, DeepSeek, Meta AI, Copilot) produced fully MISRA C++:2023-compliant code, with 13–67 violations each [measured].\[90\]
- **Medical (FDA) and wider government:** not researched to primary-source level. **Unsourced; treat as a gap.**

**Grades used:** [first-hand regulatory text], secondary, [measured], with gaps flagged.

### Q10. Open problems practitioners name

1. **Review throughput and human QA capacity.** OpenAI says its bottleneck "became human QA capacity".\[14\] Qodo's survey says review takes "the same time it always did, with more cognitive effort" [first-hand/vendor].\[91\]
2. **Reviewer fatigue and rubber-stamping.** People openly ask whether Stripe's human review is "substantive or rubber stamping" (secondary commentary) [opinion].\[29\] No published measurement exists.
3. **Verifying runtime behaviour.** This is only solved where teams build heavy infrastructure (digital twins, per-worktree observability). METR shows that passing tests is not enough.
4. **Judging architecture.** The only working approach is to encode architecture as mechanical invariants (OpenAI's layered domains). GitClear's falling refactoring and cross-file reuse metrics suggest drift is the default outcome without such invariants.
5. **Long-horizon runs nobody fully reads.** OpenAI reports 6+ hour runs "often while the humans are sleeping".\[14\] SpecBench shows long-horizon agents' gaps between held-out and validation results come mostly from compositional failures rather than deliberate cheating.\[51\]
6. **Test integrity.** Agents can edit the tests that grade them. Hiding tests reduces cheating but costs honest performance (ImpossibleBench).\[52\]\[92\]
7. **Provenance and traceability at scale.** 45% traceability (Qodo);\[16\] no cross-project disclosure standard (Hora et al.).\[9\]

**Grades used:** [first-hand], [measured], [opinion].

---

## 3. Comparison table

| Dimension | Established companies | AI-forward companies | Open-source maintainers |
|---|---|---|---|
| Review architecture | CI + AI reviewer + mandatory human approval (Stripe); senior sign-off added after incidents (Amazon) | Agent self-review + multiple agent reviewers + agent-driven runtime QA; human optional (OpenAI Harness) or excluded (StrongDM) | Human maintainer is the final gate; AI used as a review aid (Linux/Sashiko, curl) |
| Gating | Blocking human gate; CI limits (Stripe: 2 CI rounds) | Minimal blocking gates; flakes re-run; held-out scenarios and satisfaction scores | Close or ban low-effort PRs; prior approval; ban autonomous agents |
| Metrics published | Throughput (PRs/week); no defect-escape data | Throughput (PRs/day, LOC, run hours); internal quality scores, unpublished | Policy counts; maintainer-burden anecdotes |
| Policy | Accountability by seniority; regulators nudging toward human oversight (NY DFS, non-binding) | "No human-written code" charters; humans own specs and acceptance criteria | 83% permit with conditions; 49% require disclosure; growing toolchain bans (GCC, OpenJDK, QEMU, NetBSD, Zig) |
| Tooling | Copilot, CodeRabbit, Qodo, Sonar, Veracode, in-house agents (Minions on a Goose fork) | Codex, Claude Code Review, custom linters, Attractor, digital twins | GitHub Actions reviewers, AGENTS.md agent instructions, Assisted-by trailers |

---

## 4. Timeline of notable 2026 changes

- **Dec 2025 (baseline):**
  - CodeRabbit "State of AI vs Human Code Generation" (Dec 17).
  - AWS/Kiro cost-calculator incident (reported).
- **Jan 2026:**
  - Sonar State of Code survey.
- **Feb 2026:**
  - StrongDM Software Factory published (about Feb 7).
  - OpenAI "Harness engineering" (Feb 11).
  - Stripe Minions disclosure (more than 1,000 PRs per week).
  - EFF LLM policy (Feb 19).
  - MicroPython disclosure checkbox.
  - Treasury FS AI RMF (Feb 19).\[81\]
  - Stenberg's FOSDEM keynote.
- **Mar 2026:**
  - Amazon outages (Mar 2 and Mar 5) and the senior sign-off mandate (Mar 10 meeting).
  - Anthropic Code Review launch (Mar 9).
  - METR maintainer-merge study (Mar 10).
  - Black Duck survey.
  - Qodo $70M raise.
  - NCSC "Vibe check" (Mar 24).
- **Apr 2026:**
  - Linux kernel coding-assistants.rst merged (Linux 7.0).\[68\]\[69\]
  - SR 26-2 / OCC 2026-13 excludes generative and agentic AI (Apr 17).\[81\]
- **May 2026:**
  - NY DFS frontier-AI letters (May 21).
  - SpecBench paper.
- **Jun 2026:**
  - GitClear/GitKraken "Maintainability Gap".
  - NCSC "vibe coding spectrum" blog (Jun 18).
- **Jul 2026:**
  - Veracode 2026 GenAI Code Security Report.
  - CIS/SAFECode Secure by Design v1.1 (Jul 16).
  - GCC AI policy (Jul 29).
  - Greptile's Martian snapshot (Jul 30).
- **Aug 2026:**
  - OpenJDK interim GenAI ban (reported Aug 3).
  - Debian GR result (Aug 30).
- **Sep 2026:**
  - Hora/Robbes/Zacchiroli policy-landscape paper (Sep 7).
  - State bank-regulator AI exam framework (reported Sep 18).
  - Qodo 2026 State of AI Code Quality (Sep 23).
- **Oct 2026:**
  - Stack Overflow 2026 Developer Survey (Oct 6).\[62\]
  - ECB action-plan deadline (Oct 31).\[81\]

---

## 5. What a small agent-first team should copy, what it should ignore, and why

**Copy:**
1. **Held-out behavioural checks the agent cannot edit.** Use StrongDM-style scenarios stored outside the repo, or a CI job that re-runs a protected test set. This is the best-evidenced defence against test tampering (SpecBench, ImpossibleBench) and against the gap METR found between passing and mergeable.\[51\]\[52\]\[92\]
2. **A tamper tripwire on every agent PR.** Flag any diff that deletes or skips tests, lowers the test count, loosens assertions or edits CI and lint config. Require a human to read those diffs line by line. It is cheap, and it targets the most-documented failure mode.\[92\]\[93\]
3. **Architecture as mechanical invariants.** Use dependency-direction linters, file-size limits, structural tests and lint messages that tell the agent how to fix the problem (OpenAI Harness). This is the only practice shown, first-hand, to keep a fully agent-written codebase coherent.
4. **A recurring codebase audit agent plus GitClear-style metrics.** Track duplication, moved/refactored share, error-masking constructs, two-week churn and doc freshness weekly, and have agents open small cleanup PRs. Keep a per-domain quality score.
5. **Multiple independent AI reviewers with confidence thresholds, followed by verification of their findings.** This is the Anthropic plugin pattern. Treat reviewers as a recall filter, since even the best F1 is about 60%, never as approval.
6. **Disclosure trailers.** Use `Assisted-by: AGENT:MODEL` in commits. They cost almost nothing and enable later forensic audits and model-level defect analysis, the reason Kees Cook gave for valuing the Linux tag.\[68\]\[70\]
7. **Risk-tiered human reading.** Read every line of auth, secrets, payments and data-deletion code, plus migrations, infrastructure-as-code and test or spec changes. Sample the rest. Delegate style and mechanical refactors. This matches the NCSC spectrum and Amazon's lesson about blast radius.

**Ignore:**
1. **Vendor "#1 on benchmark" and "<1% incorrect" claims.** They conflict and are self-reported. Run your own replay on 30–50 of your past PRs with known bugs instead.
2. **LOC and PR-count metrics as success measures.** METR shows pass rates overstate mergeability. Measure revert rate, escaped defects and cleanup churn instead.
3. **"$1,000 per engineer per day" token benchmarks** [opinion]. These are unsupported by outcome data.
4. **Removing all human review because OpenAI or StrongDM did.** They replaced it with heavy verification infrastructure (digital twins, per-worktree observability) that most small teams don't have. Without it you get Amazon's outcome, not StrongDM's.
5. **Survey headline numbers like "89% had AI incidents" as decision inputs.** They come from vendor-commissioned surveys with loose definitions.

**Measure, even though no one publishes it:**
- Defect-escape rate and revert rate split by AI provenance.
- Human review minutes per merged PR.
- How often AI reviewer findings are acted on.
- Test-tamper flags per 100 PRs.
- Cost per merged change.

You would be ahead of the published state of the art.

---

## 6. Caveats

- Much of the quantitative evidence comes from vendors that sell review or quality tools: Qodo, Sonar, CodeRabbit, GitClear, Veracode, Black Duck and GitLab.
- Amazon's incident details come from FT reporting and secondary outlets, and Amazon disputes the attribution.
- Several policy details are secondary: GCC's line threshold, OpenJDK, Debian and the ECB letter.
- I did not research FDA guidance or in-depth practice at large banks and consultancies.
- Solo-practitioner accounts are under-sampled.
- No source has published controlled outcome comparisons between human-gated and agent-gated pipelines.

---

## 7. Source list

**Surveys and reports**
- Qodo, "The 2026 State of AI Code Quality Report: Verification Is the New Bottleneck", Sep 23 2026. https://www.qodo.ai/blog/state-of-ai-code-quality-report-2026/ and https://www.qodo.ai/state-of-ai-code-quality-report/
- Sonar, "State of Code Developer Survey report", Jan 2026. https://www.sonarsource.com/blog/state-of-code-developer-survey-report-the-current-reality-of-ai-coding/
- Stack Overflow, "The results of the 2026 Developer Survey are here!", Oct 6 2026. https://stackoverflow.blog/2026/10/06/the-results-of-the-2026-developer-survey-are-here
- Stack Overflow, Developer Survey 2026, AI section. https://survey.stackoverflow.co/2026/ai
- ITBrief, "Stack Overflow survey finds developers wary of AI tools", Oct 2026. https://itbrief.ca/story/stack-overflow-survey-finds-developers-wary-of-ai-tools
- Google Cloud / DORA, "Announcing the 2025 DORA Report". https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report
- DORA, 2025 report. https://dora.dev/dora-report-2025/
- GitClear, "The Maintainability Gap: AI Code Quality in 2026", Jun 2026. https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- CodeRabbit, "State of AI vs Human Code Generation Report", Dec 17 2025. https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- BusinessWire, CodeRabbit report release, Dec 17 2025. https://www.businesswire.com/news/home/20251217666881/en/
- Second Talent, "AI-Generated Code Quality Metrics and Statistics for 2026" (secondary for Veracode and GitClear). https://www.secondtalent.com/resources/ai-generated-code-quality-metrics-and-statistics-for-2026/
- Quash, "AI Code Review Statistics 2026" (secondary for Black Duck and Copilot). https://quashbugs.com/blog/ai-code-review-statistics
- Tech Insider, "AI Code Has 70% More Bugs…" (secondary for GitLab and Harris Poll). https://tech-insider.org/ie/ai-code-quality-crisis-2026/

**Research papers and independent studies**
- METR, "Many SWE-bench-Passing PRs Would Not Be Merged into Main", Mar 10 2026. https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/
- Hora, Robbes, Zacchiroli, "'We Permit the Use of AI, but […]': The Landscape of AI Policies in Popular Open Source Projects", arXiv 2609.07542, Sep 7 2026. https://arxiv.org/html/2609.07542
- "Regulating the Machine Contributor: Governance and Policy Alignment in Open Source", arXiv 2606.14594. https://arxiv.org/html/2606.14594v1
- "AI Policy, Disclosure, and Human in the Loop: How Are Contribution Guidelines Adapting to GenAI?", arXiv 2605.16706. https://arxiv.org/html/2605.16706
- Sun, Kuang, Baltes, et al., "Does AI Code Review Lead to Code Changes? A Case Study of GitHub Actions", arXiv 2508.18771. https://arxiv.org/abs/2508.18771
- "These Aren't the Reviews You're Looking For: How Humans Review AI-Generated Pull Requests", arXiv 2605.02273. https://arxiv.org/html/2605.02273v1
- "On the Footprints of Reviewer Bots' Feedback on Agentic Pull Requests in OSS GitHub Repositories", arXiv 2604.24450. https://arxiv.org/html/2604.24450v1
- "Bigger Isn't Always Better: A Comparative Evaluation of LLMs for Automated Code Review", arXiv 2606.15689. https://arxiv.org/pdf/2606.15689
- "SWR-Bench: Assessing LLM Performance in Real-World Code Review Comment Generation", arXiv 2509.01494. https://arxiv.org/pdf/2509.01494
- "OpenCodeReview: Determinism over Non-Determinism for Cost-Effective Agent-Based Code Review", arXiv 2608.09290. https://arxiv.org/pdf/2608.09290
- Zhao et al., "SpecBench: Measuring Reward Hacking in Long-Horizon Coding Agents", arXiv 2605.21384. https://arxiv.org/pdf/2605.21384
- "HackTrace: Behavior-Supervised Detection of Reward Hacking During Code Generation", arXiv 2610.03055. https://arxiv.org/html/2610.03055
- "Vibe Coding: Practice, Performance, Productivity, and Risk – A State-of-the-Art Review", arXiv 2608.20446. https://arxiv.org/pdf/2608.20446
- "Reducing MISRA violations in LLM-generated code by 83%" (ResearchGate). https://www.researchgate.net/publication/397957011

**Company first-hand accounts**
- OpenAI (Ryan Lopopolo), "Harness engineering: leveraging Codex in an agent-first world", Feb 11 2026. https://openai.com/index/harness-engineering/
- Simon Willison, "How StrongDM's AI team build serious software without even looking at the code", Feb 7 2026. https://simonw.substack.com/p/how-strongdms-ai-team-build-serious
- Stanford Law CodeX, "Built by Agents, Tested by Agents, Trusted by Whom?", Feb 8 2026. https://law.stanford.edu/2026/02/08/built-by-agents-tested-by-agents-trusted-by-whom/
- The Pragmatic CTO, "The Software Factory: When No Human Writes or Reviews the Code". https://www.thepragmaticcto.com/p/the-software-factory-when-no-human
- Stripe on X, Minions post. https://x.com/stripe/status/2021273907680997439
- InfoQ, "Stripe Engineers Deploy Minions…", Mar 2026. https://infoq.com/news/2026/03/stripe-autonomous-coding-agents/
- MintMCP, "Stripe Minions Explained" (secondary). https://www.mintmcp.com/blog/stripe-minions-explained
- TechCrunch, "Anthropic launches code review tool to check flood of AI-generated code", Mar 9 2026. https://techcrunch.com/2026/03/09/anthropic-launches-code-review-tool-to-check-flood-of-ai-generated-code/
- The New Stack, "Anthropic launches a multi-agent code review tool for Claude Code". https://thenewstack.io/anthropic-launches-a-multi-agent-code-review-tool-for-claude-code/
- InfoQ, "Anthropic Introduces Agent-Based Code Review for Claude Code", Apr 2026. https://www.infoq.com/news/2026/04/claude-code-review/
- Anthropic, claude-code `code-review` plugin (GitHub). https://github.com/anthropics/claude-code/tree/main/plugins/code-review
- Ars Technica via SoylentNews, "After Outages, Amazon to Make Senior Engineers Sign Off on AI-Assisted Changes", Mar 2026. https://soylentnews.org/article.pl?sid=26/03/12/1111206
- OfficeChai, Amazon sign-off report. https://officechai.com/ai/amazon-requires-senior-engineers-to-sign-off-on-ai-assisted-changes-made-by-junior-and-mid-level-engineers-after-ai-related-outage/
- Vibe Graveyard, "Amazon's retail site hit by wave of AI-code outages" (secondary). https://vibegraveyard.ai/story/amazon-ai-code-retail-outages/

**Tool benchmarks (vendor-reported snapshots of Martian Code Review Bench)**
- Qodo, "Qodo Ranked #1…". https://www.qodo.ai/blog/qodo-ranked-1-ai-code-review-tool-in-martians-code-review-benchmark/
- Greptile, "Greptile Ranks #1 on Martian's AI Code Review Benchmark". https://www.greptile.com/content-library/greptile-martian-code-review-benchmark
- CodeRabbit, "CodeRabbit tops independent AI code review benchmark". https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark
- cubic, "cubic is the #1 AI code reviewer on Code Review Bench". https://www.cubic.dev/blog/cubic-is-the-best-ai-code-reviewer-on-martian-s-benchmark

**Open-source policies and coverage**
- probabl.ai, "Maintaining open source in the age of generative AI". https://blog.probabl.ai/maintaining-open-source-age-of-gen-ai
- EFF, "EFF's Policy on LLM-Assisted Contributions to Our Open-Source Projects", Feb 2026. https://www.eff.org/deeplinks/2026/02/effs-policy-llm-assisted-contributions-our-open-source-projects
- Adafruit blog on MicroPython and EFF policies, Feb 20 2026. https://blog.adafruit.com/2026/02/20/the-open-source-world-can-write-its-own-rules-for-ai-and-nobody-has-to-ask-permission/
- Justin Wheeler, "Why the Fedora AI-Assisted Contributions Policy Matters", May 2026. https://jwheel.org/blog/2026/05/fedora-ai-assisted-contributions-policy/
- zylos.ai, "How Open Source Is Drawing the Line on AI-Written Code", Aug/Sep 2026. https://zylos.ai/research/2026-08-06-ai-generated-code-policies-open-source/
- explainx.ai, "GCC AI Contributions Policy — July 2026" (incl. OpenJDK update). https://www.explainx.ai/blog/gcc-ai-contributions-policy-llm-july-2026
- Implicator, "Linux didn't approve AI kernel code. It made the human submitter the fuse." https://www.implicator.ai/linux-didnt-approve-ai-kernel-code-it-made-the-human-submitter-the-fuse/
- It's FOSS, "AI Code Gets Approved in the Linux Kernel… But With Strings Attached". https://itsfoss.com/news/linux-ai-coding-assistants-policy/
- Tobias Weiss, "The Linux Kernel's AI Moment" (Sashiko). https://www.tobias-weiss.org/content/ai/linux-kernel-ai-coding-guidelines/

**Regulators and standards**
- NY DFS, "Heightened Cybersecurity Risks Associated with Frontier AI Models", May 21 2026. https://www.dfs.ny.gov/industry-guidance/industry-letters/20260521-heightened-cybersecurity-risks-assoc-with-frontier-ai-models
- NY DFS, "Guidance on Measures Regulated Entities Should Consider in a Heightened Cybersecurity Threat Environment", May 21 2026. https://www.dfs.ny.gov/industry-guidance/industry-letters/20260521-guidance-on-measures-reg-entities-should-consider-in-a-hcte
- UK NCSC, "The 'vibe coding spectrum' approach to AI-assisted software development", Jun 18 2026. https://www.ncsc.gov.uk/blogs/the-vibe-coding-spectrum-approach-to-ai-assisted-software-development
- UK NCSC, "Vibe check: AI may replace SaaS (but not for a while)", Mar 24 2026. https://www.ncsc.gov.uk/blogs/vibe-check-ai-may-replace-saas-but-not-for-a-while
- ANSSI/BSI, "AI Coding Assistants", Oct 4 2024. https://cyber.gouv.fr/nous-connaitre/publications/publications-internationales/ai-coding-assistants/
- CIMCON, "SR 26-2 Regulates Your Models, Not Your AI Agents". https://cimcon.com/sr-26-2-regulates-your-models-not-your-ai-agents-what-banks-need-to-know/
- PYMNTS, "State Regulators Give Banks an AI Exam Playbook as Federal Gap Persists", Sep 18 2026. https://www.pymnts.com/news/artificial-intelligence/2026/state-regulators-give-banks-an-ai-exam-playbook-as-federal-gap-persists/
- Banking News AI, AI governance in banking (secondary). https://www.bankingnewsai.com/ai-governance
- BCLP, "AI Regulation in Financial Services: Turning Principles into Practice". https://www.bclplaw.com/en-US/events-insights-news/ai-regulation-in-financial-services-turning-principles-into-practice.html
- MISRA, "MISRA AC INT:2025 Introduction to the MISRA guidelines for the use of automatic code generation". https://misra.org.uk/app/uploads/2025/01/MISRA-AC-INT-V2.pdf

## Sources

1. [What Stripe's 1,300 Agent PRs Per Week Reveal About CI at Scale](https://tenki.cloud/blog/agent-pr-volume-ci-scale)
2. [Anthropic launches a multi-agent code review tool for Claude Code - The New Stack](https://thenewstack.io/anthropic-launches-a-multi-agent-code-review-tool-for-claude-code/)
3. [These Aren’t the Reviews You’re Looking For How Humans Review AI-Generated Pull Requests](https://arxiv.org/html/2605.02273v1)
4. [Stripe on X: "Minions are our homegrown coding agents. Over a thousand pull requests merged each week at Stripe are completely minion-produced, and while they’re human-reviewed, they contain no human-written code. https://t.co/Hcg4ERzntI" / X](https://x.com/stripe/status/2021273907680997439)
5. [stripe autonomous coding agents](https://infoq.com/news/2026/03/stripe-autonomous-coding-agents/)
6. [Amazon Requires Senior Engineers To Sign Off On AI-Assisted Changes Made By Junior And Mid-level Engineers After AI-Related Outage](https://officechai.com/ai/amazon-requires-senior-engineers-to-sign-off-on-ai-assisted-changes-made-by-junior-and-mid-level-engineers-after-ai-related-outage/)
7. [Linux Kernel Source Tree Gets Official AI Coding Assistant Policy](https://lilting.ch/en/articles/linux-kernel-ai-coding-assistant-policy)
8. [The Linux Kernel Just Published AI Coding Guidelines. The Rest of Us Should Pay Attention. - DEV Community](https://dev.to/adioof/the-linux-kernel-just-published-ai-coding-guidelines-the-rest-of-us-should-pay-attention-4h7d)
9. [“We Permit the Use of AI, but \[…\]”: The Landscape of AI Policies in Popular Open Source Projects](https://arxiv.org/html/2609.07542)
10. [Regulating the Machine Contributor: Governance and Policy Alignment in Open Source](https://arxiv.org/html/2606.14594v1)
11. [Why the Fedora AI-Assisted Contributions Policy Matters for Open Source](https://jwheel.org/blog/2026/05/fedora-ai-assisted-contributions-policy/)
12. [Maintaining open source in the age of generative AI: Recommendations for maintainers and contributors](https://blog.probabl.ai/maintaining-open-source-age-of-gen-ai)
13. [The open source world can write its own rules for AI… and nobody has to ask permission](https://blog.adafruit.com/2026/02/20/the-open-source-world-can-write-its-own-rules-for-ai-and-nobody-has-to-ask-permission/)
14. [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
15. [CodeRabbit’s “State of AI vs Human Code Generation” Report Finds That AI-Written Code Produces \~ 1.7x More Issues Than Human Code](https://www.businesswire.com/news/home/20251217666881/en/CodeRabbits-State-of-AI-vs-Human-Code-Generation-Report-Finds-That-AI-Written-Code-Produces-1.7x-More-Issues-Than-Human-Code)
16. [The 2026 State of AI Code Quality Report: Verification Is the New Bottleneck - Qodo](https://www.qodo.ai/blog/state-of-ai-code-quality-report-2026/)
17. [State of Code Developer Survey report: The current reality of AI coding](https://www.sonarsource.com/blog/state-of-code-developer-survey-report-the-current-reality-of-ai-coding/)
18. [AI Code Review Statistics 2026: Real Adoption Trends - Quash](https://quashbugs.com/blog/ai-code-review-statistics)
19. [Announcing the 2025 DORA Report](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)
20. [Built by Agents, Tested by Agents, Trusted by Whom? - CodeX - Stanford Law School](https://law.stanford.edu/2026/02/08/built-by-agents-tested-by-agents-trusted-by-whom/)
21. [Qodo Ranked #1 AI Code Review Tool in Martian’s Code Review Benchmark - Qodo](https://www.qodo.ai/blog/qodo-ranked-1-ai-code-review-tool-in-martians-code-review-benchmark/)
22. [Greptile Ranks #1 on Martian's AI Code Review Benchmark](https://www.greptile.com/content-library/greptile-martian-code-review-benchmark)
23. [CodeRabbit tops independent AI code review benchmark](https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark)
24. [cubic is the #1 AI code reviewer on Code Review Bench](https://www.cubic.dev/blog/cubic-is-the-best-ai-code-reviewer-on-martian-s-benchmark)
25. [SWR-Bench: Assessing LLM Performance in Real-World Code Review Comment Generation](https://arxiv.org/pdf/2509.01494)
26. [OpenCodeReview: Determinism over Non-Determinism for Cost-Effective Agent-Based Code Review](https://arxiv.org/pdf/2608.09290)
27. [How Open Source Is Drawing the Line on AI-Written Code](https://zylos.ai/research/2026-08-06-ai-generated-code-policies-open-source/)
28. [GCC AI Contributions Policy — July 2026](https://www.explainx.ai/blog/gcc-ai-contributions-policy-llm-july-2026)
29. [Stripe Minions](https://rywalker.com/research/stripe-minions)
30. [What Stripe's Minions Get Right About Coding Agents — Mr. Phil Games](https://www.mrphilgames.com/blog/what-stripes-minions-get-right-about-coding-agents)
31. [Stripe Minions Explained: How Stripe Ships 1,000+ Agent-Written PRs Per Week](https://www.mintmcp.com/blog/stripe-minions-explained)
32. [Amazon's retail site hit by wave of AI-code outages, losing millions of orders](https://vibegraveyard.ai/story/amazon-ai-code-retail-outages/)
33. [AI Breaks Things: Amazon Outage Highlights 2026 Risks](https://vfuturemedia.com/ai/ai-breaks-things-amazon-outage-highlights-2026-risks/)
34. [Three Engineers. 32,000 Lines of Production Code. Zero Written by Hand. — Vantage Academy](https://vantageacademy.io/post/strongdm-software-factory)
35. [The Software Factory: How StrongDM Built a Non-Interactive Development Pipeline](https://news.lavx.hu/article/the-software-factory-how-strongdm-built-a-non-interactive-development-pipeline)
36. [StrongDM's AI team build serious software without even looking at the code - Weaving News](https://www.weaving.news/news/019c390e-0d34-715f-b63a-c9f707f7819f)
37. [Anthropic Introduces Agent-Based Code Review for Claude Code - InfoQ](https://www.infoq.com/news/2026/04/claude-code-review/)
38. [claude-code/plugins/code-review at main · anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/code-review)
39. [The Linux Kernel's AI Moment: Official Guidelines for Code Assistants](https://www.tobias-weiss.org/content/ai/linux-kernel-ai-coding-guidelines/)
40. [Vibe Coding: Practice, Performance, Productivity, and Risk -A State-of-the-Art Review](https://arxiv.org/pdf/2608.20446)
41. [Beyond Prompts and Context: Harness Engineering for AI Agents](https://madplay.github.io/en/post/harness-engineering)
42. [The 'vibe coding spectrum' approach to AI-assisted software development](https://www.ncsc.gov.uk/blogs/the-vibe-coding-spectrum-approach-to-ai-assisted-software-development)
43. [The Software Factory: When No Human Writes or Reviews the Code](https://www.thepragmaticcto.com/p/the-software-factory-when-no-human)
44. [OpenAI's Agent-First Codebase Learnings](https://alexlavaee.me/blog/openai-agent-first-codebase-learnings/)
45. [AI 2026](https://survey.stackoverflow.co/2026/ai)
46. [Stack Overflow survey finds developers wary of AI tools](https://itbrief.ca/story/stack-overflow-survey-finds-developers-wary-of-ai-tools)
47. [Harness engineering: leveraging Codex in an agent-first world](https://www.engineering.fyi/article/harness-engineering-leveraging-codex-in-an-agent-first-world)
48. [AI-Generated Code Quality Metrics and Statistics for 2026 - Second Talent](https://www.secondtalent.com/resources/ai-generated-code-quality-metrics-and-statistics-for-2026/)
49. [AI Wrote More Code in 2026: Duplication Rose 81%](https://www.refontelearning.com/blog/ai-generated-code-technical-debt)
50. [The Maintainability Gap: 2026 AI Code Quality Research - GitClear](https://www.gitclear.com/the_ai_code_quality_maintainability_gap)
51. [SpecBench: Measuring Reward Hacking in Long-Horizon Coding Agents](https://arxiv.org/pdf/2605.21384)
52. [How coding agents cheat on their tests, and how to catch them](https://aimlcompanion.ai/blog/reward-hacking-coding-agents-2026)
53. [HackTrace: Behavior-Supervised Detectionof Reward Hacking During Code Generation](https://arxiv.org/html/2610.03055)
54. [Humans are better coders than AI, CodeRabbit concludes](https://cybernews.com/ai-news/humans-code-better-than-ai-coderabbit/)
55. [Study finds AI-generated code has 2.7x more security flaws](https://vibegraveyard.ai/story/coderabbit-ai-code-quality-study/)
56. [After Outages, Amazon to Make Senior Engineers Sign Off on AI-Assisted Changes - SoylentNews](https://soylentnews.org/article.pl?sid=26/03/12/1111206&markunread=1)
57. [Amazon Outages Force Senior Sign-Off on AI-Written Code — Engineer Daily · 2026-03-16](https://promitb.dev/daily/2026-03-16/engineer/)
58. [bad vibes](https://sageframe.substack.com/p/bad-vibes)
59. [Claude Code Review by Anthropic: Multi-Agent PR Reviews, Pricing, Setup Guide, and Limits (2026) - DEV Community](https://dev.to/umesh_malik/anthropic-code-review-for-claude-code-multi-agent-pr-reviews-pricing-setup-and-limits-3o35)
60. [Claude Code Review Launch: Multi‑Agent PR Reviews Boost Anthropic Engineer Output 200% — 2026 Analysis](https://blockchain.news/ainews/claude-code-review-launch-multi-agent-pr-reviews-boost-anthropic-engineer-output-200-2026-analysis)
61. [AI Code Has 70% More Bugs, Trust Falls to 33% \[2026\]](https://tech-insider.org/ie/ai-code-quality-crisis-2026/)
62. [The results of the 2026 Developer Survey are here! - Stack Overflow](https://stackoverflow.blog/2026/10/06/the-results-of-the-2026-developer-survey-are-here)
63. [DORA 2025: AI Amplifies Your Strengths (and Your Weaknesses)](https://lcmh.fr/en/articles/2026/dora-2025-ai-amplifier-software-development/)
64. [\[2508.18771\] Does AI Code Review Lead to Code Changes? A Case Study of GitHub Actions](https://arxiv.org/abs/2508.18771)
65. [Does AI Code Review Lead to Code Changes? A Case Study of GitHub Actions](https://arxiv.org/html/2508.18771v2)
66. [On the Footprints of Reviewer Bots’ Feedback on Agentic Pull Requests in OSS GitHub Repositories](https://arxiv.org/html/2604.24450v1)
67. [what is ai agent harness stripe minions](https://www.mindstudio.ai/blog/what-is-ai-agent-harness-stripe-minions)
68. [Linux Kernel Permits AI Code, Pins Liability on the Human](https://www.implicator.ai/linux-didnt-approve-ai-kernel-code-it-made-the-human-submitter-the-fuse/)
69. [AI Code Gets Approved in the Linux Kernel… But With Strings Attached](https://itsfoss.com/news/linux-ai-coding-assistants-policy/)
70. [The Linux Kernel Just Set the Rules for AI Coding — And Every Developer Should Pay Attention](https://blog.arkin-dev.com/linux-kernel-ai-coding-guidelines-2026-04-11/)
71. [EFF’s Policy on LLM-Assisted Contributions to Our Open-Source Projects](https://www.eff.org/deeplinks/2026/02/effs-policy-llm-assisted-contributions-our-open-source-projects)
72. [AI Policy, Disclosure, and Human in the Loop: How Are Contribution Guidelines Adapting to GenAI?](https://arxiv.org/html/2605.16706)
73. [Bigger Isn't Always Better: A Comparative Evaluation of LLMs for Automated Code Review](https://arxiv.org/pdf/2606.15689)
74. [Does AI Code Review Lead to Code Changes? A Case Study of GitHub Actions](https://arxiv.org/pdf/2508.18771)
75. [Qodo](https://en.wikipedia.org/wiki/Qodo)
76. [How to Improve Code Quality Using AI-Assisted Static Analysis - Parasoft](https://www.parasoft.com/blog/transform-code-quality-with-ai-driven-static-analysis/)
77. [How StrongDM’s AI team build serious software without even looking at the code](https://simonw.substack.com/p/how-strongdms-ai-team-build-serious)
78. [Heightened Cybersecurity Risks Associated with Frontier AI Models](https://www.dfs.ny.gov/industry-guidance/industry-letters/20260521-heightened-cybersecurity-risks-assoc-with-frontier-ai-models)
79. [NY DFS: AI Rules and Guidance for Banks (2026)](https://www.bankingnewsai.com/ai-regulation/ny-dfs)
80. [Measures Regulated Entities Should Consider in a Heightened Cybersecurity Threat Environment](https://www.dfs.ny.gov/industry-guidance/industry-letters/20260521-guidance-on-measures-reg-entities-should-consider-in-a-hcte)
81. [AI Governance in Banking: What Regulators Require (2026)](https://www.bankingnewsai.com/ai-governance)
82. [Bank AI Oversight Expands to Every Exam: Generative AI Bypasses SR 26-2 as Kill-Switch Gap Grows](https://www.techtimes.com/articles/318340/20260613/bank-ai-oversight-expands-every-exam-generative-ai-bypasses-sr-26-2-kill-switch-gap-grows.htm)
83. [SR 26-2 Regulates Your Models, Not Your AI Agents: What Banks Need to Know - CIMCON Software](https://cimcon.com/sr-26-2-regulates-your-models-not-your-ai-agents-what-banks-need-to-know/)
84. [OCC: AI Rules and Guidance for Banks (2026)](https://www.bankingnewsai.com/ai-regulation/occ)
85. [State Regulators Give Banks an AI Exam Playbook as Federal Gap Persists](https://www.pymnts.com/news/artificial-intelligence/2026/state-regulators-give-banks-an-ai-exam-playbook-as-federal-gap-persists/)
86. [AI Regulation in Financial Services: Turning Principles into Practice](https://www.bclplaw.com/en-US/events-insights-news/ai-regulation-in-financial-services-turning-principles-into-practice.html)
87. [AI Coding Assistants](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/KI/ANSSI_BSI_AI_Coding_Assistants.pdf?__blob=publicationFile&v=7)
88. [CIS and SAFECode Release Secure by Design v1.1: A Guide to Assessing Software Security Practices](https://cisecurity.org/about-us/media/press-release/cis-and-safecode-release-secure-by-design-v1-1-a-guide-to-assessing-software-security-practices?amp=&amp=&amp=)
89. [MISRA AC INT:2025 Introduction to the MISRA guidelines for the](https://misra.org.uk/app/uploads/2025/01/MISRA-AC-INT-V2.pdf)
90. [(PDF) Reducing MISRA violations in LLM-generated code by 83%: An empirical study with static analysis verification](https://www.researchgate.net/publication/397957011_Reducing_MISRA_violations_in_LLM-generated_code_by_83_An_empirical_study_with_static_analysis_verification)
91. [State of AI Code Quality Report](https://www.qodo.ai/state-of-ai-code-quality-report/)
92. [Test tampering](https://specstory.com/learning/verification/test-tampering)
93. [Loop Engineering: How to Stop Your Agent Reward-Hacking Its Own Checks - DEV Community](https://dev.to/reporails/loop-engineering-how-to-stop-your-agent-reward-hacking-its-own-checks-4fpn)
