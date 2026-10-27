# Existing Skills for Security Analysis, Codebase Audits, and Release Readiness: An Evidence-Graded Buy-vs-Build Review

## TL;DR

- **Security analysis is the only stage with P1/P2 evidence worth adopting**: Trail of Bits' open skills (notably `fp-check`) plus the peer-reviewed finding that an agent triaging scanner output can cut SAST false positives from 98.3% to 6.3% (Claude Sonnet 4 + SWE-agent, ISSTA 2026) are the strongest proven building blocks; the proven pattern is **scanner-finds, agent-triages, tool-confirms**, not agent-only hunting (which runs 82–95% false positives).
- **Codebase audit and release readiness have nothing proven above P4 (adoption only)**: every production-readiness and whole-repo audit skill found is a checklist with installs/stars but no eval, replication, or documented field outcome — so for those two stages the decision is **adapt/lift techniques**, not adopt, and you should build your own eval from reusable benchmarks (RepoProbe, DriftBench, the architecture-erosion datasets) rather than trust any skill's self-description.
- Adopt `fp-check` and the Anthropic `/security-review` false-positive prompt as-is; lift the Semgrep-MCP "deterministic tool + LLM judgment" pattern; treat all vendor effectiveness numbers (OpenAI Aardvark 92%, Anthropic's Frontier Red Team finding more than 500 previously unknown high-severity flaws in open-source libraries including Ghostscript, OpenSC, and CGIF with Claude Opus 4.6) as unverified marketing because their harnesses are not public; and gate every exploit-running tool (Shannon, Buttercup) behind an explicit human authorization step.

---

## Short answer per stage (≤10 lines)

- **Security analysis — threat modelling:** Best candidate STRIDE-GPT (open, MITRE-mapped output). Proof level **P4** for the tool itself; the STRIDE-via-LLM method has **P3** academic case studies. Verdict: lift the template.
- **Security analysis — vuln finding / scanner triage:** Best candidate Trail of Bits `fp-check` + the ISSTA 2026 "Sifting the Noise" method. Proof level **P2** (independent peer-reviewed eval of the triage pattern on OWASP/Vul4J/OSS-Fuzz). Verdict: **adopt `fp-check`, adopt the triage pattern.**
- **Combining scanners + agents:** Best candidate Semgrep MCP + LLM triage. Proof level **P1/P2** (Semgrep's own harness + the independent ISSTA study). Verdict: adopt the pattern.
- **Codebase audit:** Best candidate Trail of Bits `audit-context-building`; otherwise keez97 architecture skills. Proof level **P4** (routing-only eval or self-run A/B). Verdict: lift techniques; nothing proven to adopt whole.
- **Release readiness:** Multiple SKILL.md checklists exist. Proof level **P5/P4** (adoption only, no eval). Verdict: **nothing proven** — build your own from SRE PRR first principles.
- **Dual use:** Shannon (AGPL, XBOW 96.15%) and Buttercup (AIxCC 2nd) run real exploits; both must be human-gated.

---

## Stage 1 — Security analysis

### What the evidence actually shows

The single most important, independently verified finding for this pipeline: **an LLM agent that triages the output of a deterministic scanner is effective, while an LLM that hunts for vulnerabilities on its own is not.** Two bodies of evidence converge on this.

1. **Agent-only hunting has very high false-positive rates.** Semgrep's research team tasked Claude Code (Sonnet 4) and OpenAI Codex (o4-mini) with finding vulnerabilities in 11 real open-source Python web apps with simple prompts and no scaffolding. Claude Code found 46 real vulnerabilities at a 14% true-positive rate (86% FPR); Codex found 21 at an 18% TPR (82% FPR). On IDOR — the class the models were *best* at — a follow-up study still found 78–88% of Claude's findings were false positives. This is P3 documented field evidence from a named, reputable source, and it is a warning, not an endorsement.

2. **Scanner-output triage by an agent is strongly effective and peer-reviewed.** "Sifting the Noise" (Xiong & Zhang, *Proc. ACM Softw. Eng.*, ISSTA 2026, arXiv:2601.22952) compared Aider, OpenHands, and SWE-agent on filtering SAST false positives. The best configuration (Claude Sonnet 4 + SWE-agent) reduced the OWASP Benchmark residual FPR from over 98% to 6.3% (a 92.1% reduction), and reached up to 93.3% FP-identification on real-world Java CodeQL alerts (Vul4J). On a contamination-free post-cutoff C/C++ set (OSS-Fuzz), it identified 95.5% of FPs at 95.5% precision versus 36.4% for vanilla prompting. This is **P1/P2**: public harness, replication artifact (Zenodo DOI), ablations, and a cost table.

   Crucial caveats the paper itself raises, which you must carry into any in-house skill:
   - Gains are **backbone- and CWE-dependent**: agentic scaffolding helps Claude Sonnet 4 and GPT-5 but gave *no* net gain for DeepSeek Chat.
   - Residual FPs concentrate in policy/crypto CWEs (CWE-327, CWE-328, CWE-614), not injection classes.
   - **Aggressive auto-suppression is dangerous**: even the best config wrongly suppressed 22.25% of *true* positives, with miss rates >50% for weak-crypto/trust-boundary classes. The paper's own conclusion: agents should be decision-support, never unconditional auto-suppression. This directly supports the "explicit human decision point" fit criterion.

3. **A second independent study agrees directionally.** QASecClaw (arXiv:2605.01885) reports its multi-agent SAST filter eliminated 88.6% of standalone-SAST false positives at a 3.1% recall loss. Named academic preprint; corroborates the pattern.

### Candidate table — security analysis

| Name · link · license | What it does | Proof level & evidence | Fit gaps | Verdict |
|---|---|---|---|---|
| **Trail of Bits `fp-check`** (github.com/trailofbits/skills, plugins/fp-check; CC-BY-SA-4.0; checked 27 Oct 2026) | SKILL.md that verifies a suspected finding through standard/deep paths ending in 6 mandatory evidence gates → TRUE/FALSE POSITIVE verdict with documented evidence; explicitly "not for hunting" | **P4 directly** (install counts ~5.5K; routing-style evals only for sibling skills), but it *operationalizes* the **P1/P2** triage pattern from ISSTA 2026 | No bundled benchmark; CC-BY-SA copyleft on the text; stack-agnostic; runs in Claude Code/Codex/Cursor | **Adopt as is** — it is the cleanest file-form of the one proven pattern; add your own eval |
| **Anthropic `claude-code-security-review`** (`/security-review` + GitHub Action; github.com/anthropics/claude-code-security-review) | Diff-aware PR security review with a false-positive filtering sub-task; ">80% confidence of exploitability" gate | **P3** (field use; Anthropic help-center guidance), vendor FP claims unverified | README states it "is not hardened against prompt injection…only…trusted PRs"; diff-only scope | **Lift one technique** (the FP-filter prompt + confidence gate) |
| **Trail of Bits `semgrep-rule-creator` / `static-analysis`** (same repo) | CodeQL/Semgrep/SARIF toolkit + custom-rule authoring | **P4** (adoption); underlying Semgrep is deterministic/proven | Stack-specific parts separable | **Adopt** for the deterministic leg of the hybrid |
| **STRIDE-GPT** (github.com/mrwadams/stride-gpt) | LLM threat model → STRIDE table, attack tree, MITRE ATT&CK mapping, Mermaid DFD; multi-provider | **P4** for tool; **P3** for STRIDE-via-LLM method (academic case studies, e.g. Auspex arXiv:2503.09586, STRIDE-AI arXiv:2605.17163) | Hosted-UI oriented but prompts readable; needs an API key; output is a reusable template | **Lift the template** (threat-table schema + MITRE mapping) |
| **Vulnhuntr** (github.com/protectai/vulnhuntr; AGPL-3.0) | Python-only recursive call-chain vuln discovery with PoC + 1–10 confidence | **P3** (named disclosed zero-days: Ragflow RCE, gpt_academic, FastChat) but no detection/FP-rate benchmark | AGPL-3.0 (copyleft trap for proprietary use); Python-only; agent-only hunting = high FP class | **Lift one technique** (call-chain-from-user-input decomposition) |
| **OpenAI Codex Security CLI** (github.com/openai/codex-security; Apache-2.0, Jul 2026) | Apache-2.0 CLI/SDK wrapper for find-validate-patch; SARIF export, CI gating | **P4** client is open; **scanning engine is closed/gated** so the "92% on golden repos" (Aardvark) figure is **unverified** | Intelligence layer not readable → fails "readable source" bar as a candidate; reference point only | **Ignore** as candidate (closed engine); keep as the-bar reference |
| **Anthropic Claude Code Security** (hosted, Opus 4.6) | Whole-repo scan + adversarial verification + human-reviewed patches | Reference only; "500+ zero-days" is a vendor claim with no public harness; SonarSource reported Opus 4.6 *generated* 55% higher vuln density | Closed/hosted | **Ignore** as candidate; reference for the bar |

### Techniques worth lifting (security)

- **Six-gate false-positive verification rubric** (`fp-check`: attacker control → reachability → validation → API contract → environment → impact), each with documented evidence. **Proof: P4 as packaged, operationalizes a P1/P2 pattern.**
- **">80% exploitability confidence, skip theoretical issues" filter prompt** (Anthropic `/security-review`). **Proof: P3.**
- **Scanner-union → agent-triage → never auto-suppress** workflow, with cross-file navigation and multi-turn interaction as the capabilities that actually drive the gain (ablations show removing cross-file navigation collapses accuracy from 96% to 44%). **Proof: P1/P2 (ISSTA 2026).**
- **CWE-aware routing**: trust agent triage for injection classes; force human review for crypto/policy classes where miss rate exceeds 50%. **Proof: P1/P2.**
- **STRIDE table + MITRE ATT&CK mapping schema** as a structured handoff artifact. **Proof: P3 (method).**

### Reusable eval tasks / benchmarks (security)

- **OWASP Benchmark v1.2** (2,740 Java cases, labeled TP/FP) — ready-made for testing a triage skill's residual FPR; used by ISSTA 2026.
- **Vul4J** (79 reproducible real Java vulns) and **OSS-Fuzz post-cutoff C/C++ slices** — contamination-aware real-world triage tests.
- **CWE-Bench-Java** (iris-sast; 120 manually-vetted CVEs across 4 CWEs) — the IRIS baseline; CodeQL detects 27, IRIS+GPT-4 detects 55 (+28, FDR −5pp). Good for measuring detection uplift.
- **RealVuln** (arXiv:2604.13764; Apache-2.0; 26→140 repos, 796→4,138 labeled entries + FP traps; interactive dashboard) — three-tier scanner comparison; Claude Sonnet 4.6 led general-purpose LLMs at F3=51.7 (recall 0.498, precision 0.785); Semgrep F3=17.7. Directly reusable to grade an in-house scanner.
- **SastBench** (arXiv:2601.02941; 299 TPs / 2,438 FPs) — purpose-built for agentic SAST triage.
- **CyberGym** (UC Berkeley; 1,507 vulns across 188 projects) and **CVE-Bench / BountyBench / SEC-bench** — vulnerability *reproduction/exploitation* benchmarks; relevant only if you build a PoC-confirmation leg. Note CyberGym leaderboard numbers (90%+) are largely self-reported.

---

## Stage 2 — Combining scanners and agents

The evidence ranks the arrangements clearly:

1. **Deterministic scanner finds → agent triages the alerts (best-proven).** ISSTA 2026 (P1/P2) and QASecClaw (P2) both show large FP reductions at modest recall cost *when the backbone is strong*. Semgrep's own 2026 product data claims its MCP server integrated with Claude Code "reduces false positives by 50% while finding 8x more true positives compared to running Semgrep alone" (its "Operationalizing AI-Powered Detection" post reports 8.2x more true positives and a 54% false-positive-rate reduction versus a Claude Opus 4.6-only baseline across 90+ vulns in four repos), and that Semgrep AI "performed 90% better on recall compared to just using Claude Code" on IDOR, lifting precision from 22% (Claude Code alone, where 88% of IDOR findings were false positives) to 61% — vendor numbers (treat as P3/author-claim) but directionally consistent with the independent studies.
2. **Agent proposes → deterministic tool confirms (strong for exploitable classes).** This is the "No Exploit, No Report" design (Shannon) and the PoV-validation design (Buttercup, Aardvark): the agent hypothesizes, a sandbox/compiler/fuzzer proves it. Buttercup reported 90% accuracy in AIxCC because "every candidate is reproduced and proven before it is reported." Evidence is P3 (competition/field), and it eliminates the FP problem by construction for memory-safety/web classes.
3. **Agent-only (no deterministic tool).** Worst: 82–95% FPR (Semgrep study, P3). Avoid as a gate.

**Recommendation:** adopt arrangement (1) as the default pipeline leg and (2) where a cheap deterministic oracle exists (compile, run test, fuzz). Never use (3) as an approval gate.

---

## Stage 3 — Codebase audits (whole-repository)

**Finding: nothing is proven above P4.** The dedicated subagent search confirmed that every whole-repo audit skill is adoption-only, with one partial exception that measures the wrong thing.

### Candidate table — codebase audit

| Name · link · license | What it does | Proof level & evidence | Fit gaps | Verdict |
|---|---|---|---|---|
| **Trail of Bits `audit-context-building`** (github.com/trailofbits/skills; CC-BY-SA-4.0) | Function-by-function pre-audit comprehension (First Principles + 5 Whys) producing architectural context | **P4** — has a with/without-plugin eval, but it scores **routing/dispatch** ("dispatches-not-inlines" 1.00 over 3 runs), not audit quality; uses ~2× the turns of a bare agent | Eval doesn't measure finding quality; copyleft text | **Adapt** — strong structure, build a real quality eval |
| **Trail of Bits `supply-chain-risk-auditor`, `differential-review`, `spec-to-code-compliance`** (same repo) | Dependency-advisory audit; git-history-aware diff review; code-vs-spec compliance | **P4** (installs only; no published eval) | Separable, multi-agent-friendly | **Adapt / lift** |
| **keez97 `claude-architecture-skills`** (github.com/keez97/claude-architecture-skills; MIT; ~7 stars) | Architecture review skills with a self-run A/B harness in `benchmarks/*.json` | **P4** self-run only: author reports architecture-workflow 97.8% vs 49.3% baseline, but 5 prompts/skill, author-graded, unreplicated, labeled "Internal Benchmark Results" | Tiny sample; no independent check | **Lift the eval harness idea**, not the numbers |
| **ksimback `tech-debt-skill`**, **BenSheridanEdwards `ArchitectPlaybook`**, **levnikolaevich `claude-code-skills`** (Codebase/Architecture Auditor) | Nine-dimension tech-debt audit with repeat-run baseline drift; opinionated architecture/documentation-drift audits | **P5** (no eval) | Read-only, file-cited; promising structure | **Lift techniques** (drift-vs-baseline mode, severity rubrics) |

### Techniques worth lifting (codebase audit)

- **Drift-against-a-baseline run mode** (tech-debt-skill, ArchitectPlaybook): store a prior audit and diff against it. **Proof: P5.**
- **First-Principles + 5-Whys per-function context pass before bug-hunting** (`audit-context-building`). **Proof: P4.**
- **Nine-category maturity framework** (Trail of Bits code-maturity-assessor) as an audit rubric — but it is scoped to smart contracts; re-derive for general code. **Proof: P4.**
- **Absence ledger** (confirmed / not-found / unverified) to avoid hallucinated coverage claims. **Proof: P5.**

### Reusable eval tasks / benchmarks (codebase audit)

- **RepoProbe** (arXiv:2608.04783) — architecture-aware repository-comprehension Q&A grounded in real GitHub Discussions, with a Checklist-Based Verification Protocol; directly reusable to grade an audit skill's architectural understanding and to catch the "premature edit" failure mode.
- **Architecture-erosion datasets**: Li et al. (arXiv:2306.08616, v6 2026) ships 606 labeled architecture-violation review comments (OpenStack Nova/Neutron, Qt Base/Creator); GPT-4o 2-shot F1=0.851 vs SVM 0.808. And arXiv:2602.07609 evaluates LLMs on 980 ADRs across 109 repos for architectural-decision violations (strong on explicit/code-inferable, weak on implicit/deployment). Both are LLM-pipeline evals, **not** agent/skill evals — so they are reusable *tasks*, not proof of any skill.
- **VulnGym / JITVUL** (arXiv:2503.03586) — repository-level, just-in-time detection with caller/callee retrieval; reusable for test-health/drift-style audits.

---

## Stage 4 — Release readiness review

**Finding: nothing proven — P5/P4 only.** Numerous SKILL.md release/production-readiness skills exist, all checklist-ware with no eval, replication, or documented outcome. This is itself a useful result: this stage is where your in-house skill has the least competition and the most need for a first-principles foundation.

### Candidate table — release readiness

| Name · link · license | What it does | Proof level & evidence | Fit gaps | Verdict |
|---|---|---|---|---|
| **apexscaleai `prod-readiness-review`** (lobehub-listed; SKILL.md) | Evidence-driven go/no-go for Next.js + React Native: rollback, monitoring, SLOs, runbooks, load tests, migrations; pass/fail/unknown checklist | **P4** (listing only, ~7 interactions) | Stack-specific (web/mobile); no eval | **Lift the checklist** |
| **Taimoorkhan1122 `prod-readiness`** (github.com/Taimoorkhan1122/prod-readiness) | Read-only whole-repo audit → SHIP / FIX THEN SHIP / HOLD, with confirmed/not-found/unverified absence ledger and per-lens subagents | **P5** (0 stars/forks at check; no license shown; no eval) | License unclear → **license trap**; unverified | **Lift the verdict schema + absence ledger** |
| **DNYoussef `production-readiness`** (skillstore-listed) | Pre-deploy audit (quality, security, docs, rollback) for Claude/Codex | **P4**, rated "⚠️ 38 Poor"; **unsafe**: runs `npx claude-flow` with no pinned version/source → supply-chain + code-exec risk | Unsafe script; High-Risk tag | **Ignore** (safety) |
| **oyedsamu `Production-Readiness-Skills`**, **aiappsgbb `threadlight-production-ready`** | 24-skill readiness suite; 13-pillar scored review with waivers and `--gate-preview` | **P5** (no eval) | Evidence-asking structure is good | **Lift techniques** (pillar scoring + waivers) |
| **shshell lab "release-readiness" pattern** (tutorial) | Read-only go/no-go from Git/CI/tests/migrations/security/observability/rollback; "assess" separated from "publish" | **P5** (tutorial, not a shipped evaluated skill) | Reference design | **Lift the contract** (read-only; must not tag/push/deploy) |

### Techniques worth lifting (release readiness)

- **Explicit GO / CONDITIONAL / NO-GO (or SHIP/FIX-THEN-SHIP/HOLD) verdict with a residual-risk register.** **Proof: P5.**
- **Read-only separation of "assess" from "publish"**: the skill must never tag, push, deploy, or mutate release state — a natural human decision point. **Proof: P5.**
- **Evidence-over-advice rule**: require repo evidence (existing runbooks, CI scripts, infra code) rather than generic recommendations; mark anything unverifiable as "unknown." **Proof: P5.**
- **Pillar scoring with explicit waivers** (threadlight) as the structured handoff. **Proof: P5.**
- **First-principles foundation**: Google SRE Production Readiness Review (interservice deps, capacity, emergency response) and AWS Operational Readiness Review (incident-derived checklists). These are durable, any-year methods — your in-house framework already references them, which is the right base to build on. **Proof: first-principles, not benchmarked.**

### Reusable eval tasks / benchmarks (release readiness)

There is **no published benchmark** for agentic release-readiness review. You will have to construct one. Practical options: seed a repo with known release blockers (missing rollback, unhandled failure path, silent migration) and score the skill's recall against that hand-labeled set — the same construction RealVuln and the OWASP Benchmark use for security. **DriftBench** (arXiv:2605.10990, 880 pairs) and **SkillJuror** (arXiv:2606.11543) are reusable for testing whether the skill itself drifts, not for release content.

---

## Stage 5 — Dual-use (exploit-running / live-attack) candidates

These carry real capability evidence but must be gated because they attack running systems:

| Name · link · license | Capability & evidence | Gating in the tool |
|---|---|---|
| **Shannon / Shannon Lite** (github.com/KeygraphHQ/shannon; AGPL-3.0) | Autonomous web pentester; **96.15% (100/104) on a hint-free, source-aware XBOW variant** — self-reported but the agent is open-source and replicable. "No Exploit, No Report" discards unproven hypotheses. | Requires explicit authorization confirmation before running; non-production guidance; mutative-effect and cost warnings; AGPL copyleft. A Claude Code skill wrapper exists (`/shannon <target>`) that first confirms authorization. |
| **Buttercup** (github.com/trailofbits/buttercup; AIxCC 2nd place) | Fully autonomous cyber-reasoning system: finds + patches vulns, reproduces every bug before reporting (**~90% accuracy**, 219 competition points, "exclusively non-reasoning LLMs"), now runnable on a laptop. | Fully autonomous with no human in the loop by design — so for your pipeline you must *add* a human gate; built for OSS-Fuzz-style targets. |
| **Vulnhuntr** (AGPL-3.0) | Generates PoC exploits for Python findings (see Stage 1). | No live-attack execution (static), but emits working PoCs — treat output as sensitive. |

**AIxCC context (P3, competition-grade):** Team Atlanta's **Atlantis** won (arXiv:2509.14589; 392.76 points, more than 170 ahead of second-place Trail of Bits with Buttercup); four of seven finalist CRSs were open-sourced under OSI licenses. Per DARPA's official Final Competition Winners Announcement, in the scored final the seven CRSs "identified 86% of the competition's synthetic vulnerabilities, an increase from 37% at semifinals, and patched 68% of the vulnerabilities identified," and teams also discovered 18 real, non-synthetic vulnerabilities disclosed to maintainers. These are the highest-credibility open autonomous security systems available, but they are heavyweight harnesses, not liftable SKILL.md files — mine them for architecture (deterministic decomposition + LLMs only where tools fall short), not for drop-in skills.

---

## Risks found in third-party skills during the search

- **Prompt-injection exposure:** Anthropic's own `claude-code-security-review` README warns it "is not hardened against prompt injection attacks and should only be used to review trusted PRs." Any skill that reads untrusted diffs/issues inherits this.
- **Unsafe scripts / supply chain:** DNYoussef `production-readiness` runs `npx claude-flow` with no pinned version or install-source constraint — `npx` can download and execute arbitrary package code during an "audit." Rated "Poor." **Do not run.** Similar `curl | bash` lines appear in some devcontainer templates (benign in the Trail of Bits case — Claude Code's own installer — but verify each).
- **License traps:** Trail of Bits skills are **CC-BY-SA-4.0** (share-alike copyleft on the skill text — derivatives must stay CC-BY-SA). Vulnhuntr, Shannon, and Buttercup are **AGPL-3.0** (network-copyleft — a real constraint for proprietary/SaaS use). OpenAI Codex Security CLI is Apache-2.0 but its scanning engine is proprietary and gated. Taimoorkhan1122 `prod-readiness` showed **no license** → unusable until clarified.
- **Abandoned/thin maintenance & fake-evidence risk:** keez97's "97.8% vs 49.3%" and most readiness skills' claims are **self-run or absent** — popularity (Trail of Bits 7.6K stars) and self-reported leaderboard rows (CyberGym 90%+) are **not** quality evidence per the brief.
- **Model-side regression:** SonarSource's "Why Claude Opus 4.6 requires verification" analysis (Feb 20 2026) reported that vulnerability density in code *generated* by Opus 4.6 increased 55% versus the previous version, with a 278% increase in path-traversal vulnerabilities and critical bugs up 336% (from 11 to 48 per million lines of code) — a reminder that the same frontier model marketed as a great finder can also be a worse writer, so the verify stage cannot trust the build stage's model.
- **Skill drift:** installed skills silently drift between `~/.claude/skills` and `~/.agents/skills` (tools like skill-checkup/skill-drift exist precisely because of this); pin and audit any adopted skill.

---

## Bottom line for the adopt/adapt/replace decision

- **Security analysis:** **Adopt** `fp-check` and the scanner-triage pattern (the only P1/P2 evidence in the whole review); adopt a deterministic scanner (Semgrep/CodeQL) as the finding leg; **lift** the STRIDE-GPT threat template and Anthropic's FP-filter prompt. Replace any in-house agent-only vuln-hunting gate — the evidence says it will run 80%+ false positives.
- **Codebase audit:** **Adapt** Trail of Bits `audit-context-building` for structure, **lift** drift-vs-baseline and absence-ledger techniques, and build a real quality eval on RepoProbe + the architecture-erosion datasets. Nothing is proven enough to adopt whole.
- **Release readiness:** **Replace/build** from SRE PRR + AWS ORR first principles, lifting the GO/NO-GO + residual-risk-register + read-only-assess techniques from the checklist skills. There is no proven candidate and no published benchmark — constructing your own labeled blocker set is the highest-value next step.