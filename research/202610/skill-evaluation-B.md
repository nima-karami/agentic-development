# Evaluating Agent Skills on a Small Budget: A Minimum Viable Practice (checked 27 Oct 2026)

A two-person team can afford one useful eval per skill: about 20 tasks, each run 3 times with the skill and 3 times without it, scored mostly by deterministic checks, plus a separate 20-query trigger test. That eval reliably catches broken skills, skills that never fire, and large regressions. It cannot detect the small quality gains that most skills actually deliver.

**Short answer (the minimum eval per skill)**
- **Trigger test:** 20 queries, 8–10 should fire and 8–10 near-misses that should not. Run each 3× and confirm firing from session logs.
- **Outcome test:** 15–25 tasks from real runs, with 3 runs per arm (skill on / skill off). Use deterministic graders first and a rubric judge only for prose artifacts.
- **Judge calibration:** label 30–50 artifacts yourself before trusting any model judge.
- **Analysis:** paired per-task differences with Wilson or Bayesian intervals; don't report bare percentages.
- **Cost:** roughly $5–$40 of model spend and 3–6 hours of human time per skill.
- **What it can tell you:** whether the skill fires, whether it breaks or hurts tasks, whether a new version or model regressed, and whether one skill is dramatically better than another (≥25–30 pp).
- **What it cannot tell you:** whether a skill gives a modest 5–10 pp lift. Published skill benchmarks find most software-engineering skills sit in that zone or at zero.

## TL;DR
- **Measure lift, not score:** run every case with and without the skill. In SWE-Skills-Bench (Han et al., arXiv:2603.15401), 39 of 49 public software-engineering skills gave zero pass-rate improvement, and the average pass rate across about 565 tasks moved only from 89.8% to 91.0%; 24 skills scored 100% both with and without the skill. Assume your skill adds nothing until a paired eval shows otherwise.
- **Small samples only detect big effects:** with 20 tasks × 3 runs, act only on large differences, regressions and trigger failures. Use Wilson or Bayesian intervals, because the CLT under-covers below a few hundred datapoints. Treat single LLM-judge verdicts as noisy: Yagubyan's "The Coin Flip Judge?" (arXiv:2606.13685, Apr 2026; GPT-4o-mini and GPT-4.1-mini judges) found pairwise preferences flip on 13.6% of re-runs on average, with 28% of questions exceeding a 20% flip rate.
- **Start with the right tool:** for Claude Code skills, use `claude plugin eval` (with/without baseline built in) plus skill-creator's trigger loop, checking trigger results against logs because of open harness bugs. For cross-vendor A/B tests, use promptfoo's Claude Agent SDK and Codex SDK providers, or Inspect AI for statistical control.

## Key Findings

**1. Tooling (verified to exist, 27 Oct 2026)**

| Harness | Link | License | Measures | Effort to adopt | Limits |
|---|---|---|---|---|---|
| `claude plugin eval` (Claude Code ≥ v2.1.269, shipped week of 7–11 Sep 2026) | code.claude.com/docs/en/plugin-evals | Proprietary (part of Claude Code) | Outcome (regex, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline` graders); triggering via `tool_used: Skill`; with/without Δ; cost estimate; CI gating (`--threshold`, `--model`, `--judge-model`) | Low: `claude plugin eval init` writes cases interactively | Claude only; no custom-code graders; earlier builds were described as early access; `llm` graders get noisier on long outputs (docs) |
| Anthropic skill-creator (evals, benchmark mode, description optimizer; updated 3 Mar 2026) | github.com/anthropics/skills/tree/main/skills/skill-creator | See repo | Old-vs-new skill comparison, assertions, benchmark with variance, trigger-rate optimization (`run_loop.py`) | Low | Uses its own `evals/evals.json` format, not shared with plugin eval. Open issues report the trigger harness reading 0% recall because it measures slash-command registration rather than auto-triggering (anthropics/claude-code #79998, #87915; anthropics/skills #1721). |
| OpenAI "Testing Agent Skills Systematically with Evals" pattern | developers.openai.com/blog/eval-skills | Docs/pattern | Whether Codex invoked the skill (process goals) and outcome, via `codex exec --json` plus deterministic checks on `command_execution` events | Medium (you write the runner) | A recipe, not a product. The OpenAI Evals platform becomes read-only on 31 Oct 2026 and shuts down on 30 Nov 2026; OpenAI points users to promptfoo. |
| promptfoo | promptfoo.dev/docs/guides/evaluate-coding-agents | MIT | Outcome, rubric and judge assertions, side-by-side comparison; `anthropic:claude-agent-sdk` and `openai:codex-sdk` providers, with skills loaded from `.claude/skills/` and `.agents/skills/` | Medium (YAML config) | Statistics are DIY. File-editing agents need `copy_working_dir: true`. Requires Node ^20.20 or ≥22.22. |
| Inspect AI (UK AISI) | inspect.aisi.org.uk | MIT | Outcome, model-graded scoring, `epochs` (repeats with reducers), sandboxes, can run external agents | Medium–high (Python) | Built for model evals; skill loading is your job |
| DeepEval | github.com/confident-ai/deepeval | Open source (sources disagree: MIT vs Apache 2.0; check repo) | Pytest-style metrics incl. task completion, tool correctness | Medium | Generic metrics; no skill-trigger notion |
| Braintrust | braintrust.dev | Proprietary SaaS (open-source autoevals library) | Experiments, span/trace scorers, CI gates | Low–medium | Hosted; costs money past the free tier |
| LangSmith | smith.langchain.com | Proprietary (open-source agentevals package) | Trajectory match, LLM judge, datasets | Low if on LangChain | Best fit for LangChain/LangGraph |
| Research harnesses: SkillsBench, SWE-Skills-Bench | arxiv.org/abs/2602.12670; github.com/GeniusHTX/SWE-Skills-Bench | Research | Paired skill vs no-skill lift with deterministic verifiers | High | Fixed task suites, not your pipeline |

*Established:* repeated trials, with/without baselines, deterministic graders first. *Emerging:* skill-specific CLIs such as plugin eval and skill-creator benchmark mode. *Opinion:* the vendor comparisons ranking Braintrust, LangSmith and DeepEval are marketing-adjacent and unreplicated.

**2. Statistics for small samples**
- **Error bars:** Anthropic's "Adding Error Bars to Evals" (Evan Miller, Anthropic, 1 Nov 2024, arXiv:2411.00640) recommends "conducting statistical inference on the question-level paired differences, rather than the population-level summary statistics," which it calls a "free" variance reduction. It also recommends clustered standard errors when questions are related; on real Anthropic data, clustered standard errors came out more than 3× the naive ones. Resampling each question several times reduces measurement error.
- **Which interval to use:** Bowyer, Aitchison and Ivanova (ICML 2025, PMLR 267, arXiv:2503.01747) show CLT methods below a few hundred datapoints are "usually dramatically underestimating uncertainty (i.e. producing error bars that are too small)," and that only Bayesian and Wilson intervals reach nominal coverage at small N; they ship the bayes_evals library for this.
- **What that means at your scale** (my calculation, Wilson 95%):
  - 20/20 passes still only bounds the true rate at ≥84%.
  - 10/10 bounds it at ≥72%.
  - 27/30 gives [0.74, 0.97].
- **Detecting a difference** (my calculation, standard two-proportion power): detecting 50% → 70% at 80% power needs about 90 independent trials per arm. Since 20 tasks × 3 runs is clustered, not 60 independent trials, a 20-task eval resolves only differences of about 25–30 pp or more.
- **Repeated runs:** count runs within a task as a cluster, not independent data. Use pass^k for reliability gates. Anthropic Engineering's "Demystifying evals for AI agents" (9 Jan 2026) shows 75% per-trial success gives only (0.75)³ ≈ 42% pass^3. Use pass@k only to check whether a task is solvable at all; the same post says "If a task has 0% pass@100, the task is broken."
- **Why bigger skill effects are rare:** the current SkillsBench (arXiv:2602.12670 v4, 14 Jun 2026; 87 tasks, 8 domains, 18 configurations) reports curated skills raising average pass rate from 33.9% to 50.5% (+16.6 pp), with gains ranging from +4.1 to +25.7 pp; an earlier version reported only +4.5 pp in software engineering, with 16 of 84 tasks negative. SWE-Skills-Bench measured +1.2 pp on average. Real effects in your domain are probably below what 20 tasks can resolve.

**3. Model judges**
- **Agreement:** the baseline is GPT-4 on MT-Bench (Zheng et al., 2023, arXiv:2306.05685) "achieving over 80% agreement, the same level of agreement between humans," alongside documented position, verbosity and self-enhancement biases.
- **Run-to-run noise** ("The Coin Flip Judge?", arXiv:2606.13685, Apr 2026; one provider's small judges, so this needs replication):
  - 14% mean pairwise flip rate on identical re-runs.
  - Cross-judge κ = 0.51.
  - Rewording the prompt template flipped the majority verdict in 25% of cases.
  - 11 repeated trials were needed to recover the 50-trial verdict with 95% probability.
- **Position flips by judge:** "Reliability without Validity" (arXiv:2606.19544) reports AB/BA flip rates from 0.035–0.038 (Gemini 3.1 Pro, Claude Opus 4.6) up to 0.12–0.19 (Haiku 4.5, GPT-4o-mini, Qwen3-8B) on MT-Bench. Cheap judges are noticeably less stable.
- **Stage-artifact evidence:** on DevBench software design (PRD → UML/architecture), GPT-4 judge agreement with the human majority was 60.4–83.2% depending on criterion and tie handling.
- **How many human labels:**
  - evalstats (arXiv:2609.35815) targets κ ≥ 0.61 between judge and human. In its example, 30 human labels plus 300 judge scores bought only about 17 extra effective human samples.
  - Practitioner math (dev.to blog, not peer-reviewed) puts the cost of a ±0.05 κ interval at about 200 labels when κ ≈ 0.6.
  - Practical reading: 30–50 labels tell you whether the judge is grossly wrong; they do not certify it.
- **Which judge designs hold up:** binary PASS/FAIL checklists over short excerpts are the most stable; the Claude Code docs recommend regex over long files and `llm` graders only for short outputs. Pairwise comparison is best for A/B tests, but only with order swapping. Reference-based judging with golden findings works for review and audit (Martian Code Review Bench matches against curated "golden comments" using three judge models). Use a judge from a different model family than the generator to avoid family self-preference (arXiv:2609.17857).

**4. Reusable task sets per stage** (contamination: anything built from public GitHub before 2025 should be assumed seen in training; prefer your own repos)
- **PRD → design:** DevBench (open-compass/DevEval) provides PRDs with UML and architecture references, judged by an LLM. R2ABench (arXiv:2604.06683) provides PRDs with expert PlantUML references. Check licenses before reuse.
- **Build / verification:** SWE-Skills-Bench (49 skills, about 565 tasks, pinned commits, execution-based acceptance tests) maps best. DevBench's environment-setup, implementation and test-generation tasks also fit.
- **Review:** Martian Code Review Bench (50 PRs, 173 golden comments with severity labels, MIT); SWR-Bench (1,000 verified PRs, FSE 2026); Code Review Agent Benchmark (arXiv:2603.23448, 234 review comments with executable tests). Vendor review benchmarks tend to favor their authors (DeepSource critique).
- **Spec, plan, audit, release:** no public graded set maps cleanly. Build your own from field runs.

**5. Field runs as evals**
- **Established practice:**
  - Anthropic recommends starting with 20–50 tasks drawn from real failures and graduating saturated capability evals into regression suites.
  - Husain and Shankar's error analysis: read about 100 traces, write open codes on the first failure in each, cluster them (axial coding), then build one eval per recurring failure mode. They recommend annotating at least 30 traces yourself.
- **Tool support:** `claude plugin eval` can replay a saved transcript (`context.history_file`) and seed fixtures via `scaffold_script`, so an incident becomes a case directly.
- **How well it works:** evidence is mostly practitioner reports. The main failure mode is overfitting to yesterday's incidents, so keep a held-out set.

**6. Triggering** (largely practitioner evidence; mark as emerging)
- **Skill-creator's method:** 20 queries, 60/40 train/test split, 3 runs per query, up to 5 iterations, selecting on test score. Anthropic publishes no accuracy numbers, and the harness bugs above mean results should be checked against session logs.
- **Description wording matters (one model only):** Seleznov's 650-trial Claude Code experiment (Opus 4.5; should-trigger queries only, so false triggers were not measured) found a directive description at 100% activation versus 87.5% for a passive "Use when…" description (OR 20.6).
- **Descriptions are a weak routing signal:** SkillRouter (arXiv:2603.22455) found routing on name+description alone loses 31–44 pp of accuracy versus full skill text. A Sep 2026 smart-contract-audit study (arXiv:2609.29454) calls triggering "a primary bottleneck," with at most 27 of 83 skills ever invoked.
- **Manipulation risk:** persuasive description text can bias which skill gets selected (arXiv:2605.11418), so don't over-tune toward "ALWAYS" phrasing.

**7. Costs** (documented points; the rest are my estimates)
- **Routing checks:** Kong's promptfoo routing run for one skill was 20 trials, about 523K tokens, about $0.86 and about 121 s (GitHub issue, Oct 2026).
- **Small outcome runs:** the plugin eval docs' sample shows one case × 6 runs at $0.41. That figure is illustrative.
- **Real build tasks:** agentic build tasks with tools typically cost $0.30–$2 per run (estimate). So 20 tasks × 6 runs comes to $36–$240, which is over budget for build and verification. Use 10–15 tasks or a cheaper model there.
- **Human time:** 30–50 judge labels take 1–2 h; error analysis on 100 traces takes "a few hours" (Husain).

## Details: Minimum Eval Kit per Stage

| Stage | Task source | Tasks × repeats/arm | Judge design | Human labels | Pass criterion | Est. cost* |
|---|---|---|---|---|---|---|
| PRD | Past feature requests + DevBench PRDs as format references | 15 × 3 | Checklist (required sections, measurable acceptance criteria, no invented scope), cross-family judge | 30 | Δ ≥ +25 pp on checklist pass and no task worse in all runs | $5–15 |
| Spec | Your PRDs → shipped specs | 15 × 3 | Reference-based: must cover the requirement IDs from the PRD (regex/trace check) + short-excerpt rubric | 30 | 100% requirement coverage on ≥ 90% of runs | $5–15 |
| Plan | Past specs with the actual plans/diffs | 15 × 3 | Checklist (steps map to spec items, ordering, test step present) | 30 | pass^3 ≥ baseline; no new failure modes | $5–15 |
| Design | DevBench/R2ABench PRDs + internal ADRs | 10–15 × 3 | Pairwise vs reference design with order swap, 3 judge samples | 40 (pairwise) | Wins ≥ 70% of order-swapped pairs | $10–25 |
| Build | Own repo tasks at pinned commits; SWE-Skills-Bench subset | 10–15 × 3 | Deterministic: tests pass, build green | 0–10 | Paired Δ on test pass; no regressions | $20–60 |
| Verification | Seeded-bug branches from past incidents | 15 × 3 | Deterministic: seeded bug detected (finding matches file/line) | 10 | Detection rate lower Wilson bound ≥ baseline | $15–40 |
| Review | Past PRs with known defects; Martian/SWR-Bench subset | 20 × 3 | Reference-based golden-comment matching; precision and recall | 30–50 | Recall up without precision falling >10 pp | $10–30 |
| Audit | Past audit findings / incidents as golden findings | 15 × 3 | Reference-based finding match + severity check | 30 | No missed critical golden finding across runs | $10–30 |
| Release | Past release checklists, changelogs, rollback incidents | 10 × 3 | Deterministic (required gates run, changelog regex) + checklist | 10 | pass^3 = 100% on gate checks | $5–15 |

*My estimates, assuming a mid-tier model; not sourced.

Add to every skill a 20-query trigger set (about $1–3, scaled from Kong's $0.86 per 20 trials).

## Recommendations: Protocol for In-House vs Third-Party Skill A/B

1. **Freeze the setup.** Pin the model, harness version and judge model (`--model` and `--judge-model` in plugin eval). Use identical tools, fixtures and a clean workspace per run (`copy_working_dir: true` in promptfoo).
2. **Use three arms on the same tasks:** no skill, in-house, third-party. The no-skill arm tells you whether either skill matters at all.
3. **Equalize triggering first.** Run the trigger set for both. If one under-triggers, either fix it or force invocation in a separate "forced" arm, so you compare content rather than descriptions.
4. **Pick tasks before seeing results:** 15–20 tasks from your own field runs, with 5 held out for a confirmation pass.
5. **Grade deterministically where possible.** For prose artifacts, use a pairwise judge from a third model family:
   - Strip skill names, headers and formatting tells.
   - Normalize length, or score length separately.
   - Run both A/B and B/A orders, and count disagreements between the two orders as ties.
   - Take 3 samples per pair.
6. **Validate the judge.** Hand-label 30 pairs blind and compute κ. If κ is below about 0.6, use human judgment for this comparison.
7. **Analyze per task.** Use paired per-task differences with a cluster bootstrap over tasks or a Bayesian paired model. Report the interval, not the winner.
8. **Decide by threshold:**
   - Adopt the third-party skill only if its lower bound beats in-house by your threshold.
   - Otherwise keep whichever is cheaper in tokens. SWE-Skills-Bench found token overhead ranging from −78% to +451% even where pass rates were identical.

## Caveats: How Small Evals Mislead, and Defenses
- **Reading noise as signal:** a 3/5 vs 4/5 difference is meaningless. Use Wilson or Bayesian intervals and paired analysis, and pre-commit to an effect size.
- **Treating repeated runs as independent:** this narrows intervals falsely. Cluster by task (Miller: naive standard errors can be more than 3× too small).
- **A high score without a baseline:** the model may pass without the skill. Always run the no-skill arm. Skill-creator's guidance is that passing without the skill means the model has outgrown it.
- **Silent non-triggering:** Δ ≈ 0 often means the skill never fired. Add a `tool_used: Skill` check and confirm in logs.
- **Judge drift and bias:** cheap judges flip more. Pin the judge, swap order, use a different model family, and re-check κ when you change models.
- **Overfitting descriptions and evals to the same queries:** select on held-out queries and refresh 20% of tasks from new field runs each quarter.
- **Contaminated public tasks:** public GitHub-derived sets inflate absolute scores. Use them for format only and score lift on private tasks.
- **Unverified vendor numbers:** vendor numbers such as trigger-rate gains and "production-ready κ" thresholds are unverified. Several of the 2026 judge-reliability and skill papers cited here are single-author or single-provider preprints awaiting replication.