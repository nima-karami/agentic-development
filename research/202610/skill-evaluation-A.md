# Evaluating Agent Skills on a Small Budget

## Short answer

**Recommendation for a two-person team:** treat the first eval as a *screen*, not a benchmark: run **12 representative tasks × 3 independent trials per skill** for artefact-producing stages, and **10 tasks × 2 trials** for expensive build/test/audit stages. † This is deliberately below Anthropic’s practitioner starting point of 20–50 tasks; statistically, it can expose large regressions and recurring failure modes, but it cannot estimate a skill’s population success rate precisely. citeturn6view0turn7search5  
Always compare against a frozen baseline—skill off, previous version, or third-party skill—on **the same tasks**, and analyse at the *task* level rather than pretending repeated stochastic runs are independent tasks. citeturn8search6turn7search4  
Use executable/reference checks first, evidence-grounded checklists second, and an LLM judge only for qualities that cannot be checked deterministically. Recent agentic judge benchmarks still show material error even from frontier judges. citeturn18view0turn18view1  
For subjective artefacts, manually label **12–16 pilot cases per skill** † to find obvious judge failures; for a judge you intend to reuse, a **32-example calibration bank** has a recent empirical precedent, but it still does not statistically certify 90%+ accuracy. citeturn17view5turn7search5  
Test triggering separately with positive, indirect/contextual and negative-control prompts; current OpenAI and Anthropic skill architectures route heavily from skill metadata, especially name and description. citeturn3view0turn1search12turn2search3  
A small eval can justify action when a difference is **large, paired, consistent and explainable**; it cannot establish a small advantage, a universal pass rate, or immunity to unseen production cases.  
At current API prices, an artefact-stage pilot can plausibly stay around **single-digit to low-tens of US dollars**, while a paired build-agent A/B is more plausibly **US$20–50+**, before external tool or container charges. citeturn15search0turn15search2  
† Counts marked as recommendations are budget designs from this report, **not published statistical thresholds**; their limitations are quantified below.

## What the current evaluation tooling actually gives you

The 2026 tooling landscape has improved markedly for agents. The important change is that an “eval” increasingly means more than grading the final string: current systems can retain traces, tool calls, latency, token consumption, cost and—in some cases—whether a skill or tool was selected at all. OpenAI’s January 2026 skill-evaluation recipe explicitly separates outcome, process and style checks, and recommends direct, indirect/contextual and negative invocation cases; Anthropic’s January 2026 agent-evaluation guidance similarly distinguishes task, trial, grader, trace and outcome, and stresses repeated trials because agent outputs are stochastic. citeturn3view0turn6view0

I would classify the evidence as follows. **Established practice** is paired regression testing, deterministic graders where possible, versioned test cases, production failures becoming regressions, and tracing cost/tool behaviour alongside quality. citeturn3view0turn6view0turn14search9 **Emerging practice** is skill-specific routing evaluation, adaptive rubric generation, automated failure clustering and judge calibration against small anchor sets. citeturn14search0turn17view5 **Opinion/vendor claim** includes claims that a particular harness or “optimise” feature materially improves agent quality; absent independent replication, those should be treated as convenience claims rather than effectiveness evidence.

### Harness comparison

Versions below are the current tagged release, documented version, or repository state that I could verify on **27 October 2026**. “Adoption effort” is my estimate for a small engineering team, not a vendor claim.

| Harness / exact source | Version checked | Licence | What it can measure | Adoption effort | Important limit |
|---|---|---|---|---|---|
| **OpenAI Agent Evals + “Testing Agent Skills Systematically with Evals”** citeturn3view0turn1search6 | Current docs, checked 2026-10-27 | Hosted/commercial API; recipe itself is documentation | Skill triggered or not; task outcome; trace/process; tool use; rubric/style; dataset regression; model/prompt comparison | **Low** if already on OpenAI | The skill recipe is a pattern, not a public cross-vendor benchmark. Effectiveness claims should not be inferred from the docs. |
| **Google ADK / Gemini Enterprise Agent Evaluations** citeturn14search0turn14search10turn14search1 | ADK Python **v2.13.0, 2026-10-22** | **Apache-2.0** for ADK; Google Cloud evaluation service is commercial | Outcome, grounding, safety, tool/trajectory quality, reference scores, duration, model calls, tokens/cost; offline experiments and live monitoring | **Medium** | Strongest fit if the agent is already in ADK/Google Cloud; cloud-specific pieces add platform coupling. Vendor claims of metric effectiveness are unverified here. |
| **Agent Eval Harness**, `fullsend-ai/agent-eval-harness` citeturn14search2turn14search5turn24view0 | Changelog **v1.53.2, 2026-09-29** | **Apache-2.0** | Explicit skill mode; correctness/quality/cost; LLM and code judges; thresholds; pairwise A/B; MLflow traces; regression reports | **Low–medium** | Very close to this use case, but young and much less independently validated than generic test frameworks. Its “optimise” loop should be treated as experimental. |
| **Promptfoo**, `promptfoo/promptfoo` citeturn22search1turn22search8 | **v0.125.1, 2026-10-25** | **MIT** | Prompt/agent outputs, assertions, model comparison, latency/cost depending provider, CI regressions, red-team cases; explicit agent providers | **Low** | Excellent declarative A/B harness, but skill *routing* is something you must expose and grade yourself unless the agent provider returns the needed trace. |
| **DeepEval**, `confident-ai/deepeval` citeturn21search1turn21search9 | Python **v4.2.0** tagged 2026-08-24; repo active in Oct. | **Apache-2.0** | Black-box task outcome, complete trajectories, individual tool calls/steps/handoffs, model-judge metrics, regression tests | **Low–medium** | Rich metric catalogue makes it easy to create lots of scores without proving that those scores match human judgement. |
| **Inspect AI**, `UKGovernmentBEIS/inspect_ai` citeturn22search4 | `main` commit **72e7dce**, checked 2026-10-27 | **MIT** | Multi-turn/tool-use tasks, custom scorers, model-graded evals, reproducible environments; 200+ packaged evals | **Medium** | More of a general evaluation framework than a skill-routing harness; you need to build the stage-specific tasks and trace assertions. |
| **LangSmith evaluations** citeturn5search5turn5search2turn5search17 | Current service/docs, checked 2026-10-27 | Commercial hosted product/SDK ecosystem | Offline and online eval, datasets from traces, human/code/LLM graders, repetitions, pairwise experiments, cost; production trace → regression dataset | **Low** for LangChain users; **medium** otherwise | Strong production feedback loop but hosted/product coupling; comparative evaluator quality still depends on the judge you supply. |
| **Langfuse**, `langfuse/langfuse` citeturn21search3turn21search7turn23search1turn23search9 | **v4.70.1**, 2026-10-27 | Core **MIT Expat**; designated `ee/` areas under commercial enterprise licence | Traces, prompt versions, datasets/experiments, LLM-as-judge, code evaluators, manual labels, user feedback, cost | **Medium** self-hosted; **low** cloud | Better as the evaluation/observability substrate than as an opinionated skill benchmark. |
| **Phoenix**, `Arize-ai/phoenix` / `phoenix-evals` citeturn21search2turn22search3turn22search6 | Phoenix **v20.26.1**, 2026-10-25; Evals **v3.9.4**, 2026-10-24 | **Elastic License 2.0** | Dataset experiments, traces, code/LLM evaluators, tool-response checks, observability | **Medium** | ELv2 permits normal self-hosting but is not an OSI-style permissive licence; also not skill-routing-specific. |

For this particular suite, I would **not** start by adopting a large observability stack. A CSV/JSONL task set plus a small runner is enough if you already capture the agent’s trace. OpenAI’s skill recipe is unusually close to the desired structure: `prompt → run/trace/artifacts → checks → score`, with failures appended to a living regression set. citeturn3view0 Agent Eval Harness is the closest ready-made open-source implementation of that pattern, while Promptfoo is the least opinionated mature option if you want to compare arbitrary configurations. citeturn14search2turn22search8

## The minimum viable eval, statistically

### Tasks and repetitions are solving different uncertainty problems

A frequent mistake is to treat “20 tasks × 3 runs” as \(n=60\). It is not, for the question you normally care about.

The **tasks** estimate how the skill generalises across different work. The **repeats** estimate stochastic variation *conditional on each task*. Three executions of one PRD request do not give you three independent samples from the population of PRD work. For comparing two skills, keep tasks paired and aggregate repeats within each task; then compute uncertainty across tasks. Significance-testing guidance in NLP similarly stresses paired tests when systems are evaluated on the same items. citeturn8search6turn8search12

Anthropic’s January 2026 practitioner guidance says **20–50 simple tasks drawn from real failures is a good starting point**, precisely because early agent changes often have large effects. That is practical advice, not a sample-size theorem. citeturn6view0 With only a few hours per skill, my recommendation is therefore a two-step design:

**Pilot:** 12 tasks × 3 trials for cheap artefact stages, or 10 × 2 for expensive executable stages.  
**Escalate:** when the result is close enough to affect a decision, add tasks toward the 20–50 range before adding many extra repeats to every existing task. This prioritises uncertainty across work items over excessive estimation of one item’s stochastic success probability. Recent work on stochastic LLM evaluation also finds that uniform repetition is inefficient: standard error falls only with the square root of the repetition budget, while adaptive allocation of repeats to high-variance cases can reduce variance. citeturn7search4

### What the small sample can and cannot prove

For a binary pass rate, the ordinary Wald confidence interval is particularly unreliable at small \(n\); Brown, Cai and DasGupta recommend better-behaved alternatives such as the Wilson or Jeffreys intervals. citeturn7search5 Using a 95% Wilson interval gives a useful reality check:

| Observation | 95% Wilson interval | Interpretation |
|---|---:|---|
| **3/3** successes on one task | about **44%–100%** | Three repeats establish almost nothing about the task’s underlying success probability. |
| **12/12** tasks pass | about **76%–100%** | A perfect pilot is encouraging, but cannot establish a true 90–95% reliability level. |
| **18/20** tasks pass | about **70%–97%** | “90% observed” is much less precise than it sounds. |
| **27/30** pass | about **74%–97%** | Still a broad interval. |
| **45/50** pass | about **79%–96%** | Useful for trend/regression work; still not certification-grade precision. |

These intervals are arithmetic from the Wilson formula in Brown et al.; they assume the tasks themselves are independent samples from a meaningful target population, which hand-curated eval suites usually only approximate. citeturn7search5

The practical implication is important: **small evals are excellent for finding failures and detecting large deltas, but poor at establishing absolute reliability.** A result such as “the new skill found the missing dependency on 9 of 12 cases where the old one did so on 3 of 12” may be worth acting on. “83% versus 79%” almost certainly is not, absent substantially more data.

For an A/B expressed as task-level wins and losses, an exact sign test makes the power limitation vivid. Under an equal-win null, **six discordant tasks all favouring the same variant gives a two-sided \(p=0.03125\); five unanimous discordant tasks gives \(p=0.0625\)**. Those figures come directly from the exact binomial null, \(2(1/2)^m\). Thus a 12–20-task eval can demonstrate a *very consistent* advantage, but weak or mixed advantages will correctly remain inconclusive. For paired binary pass/fail outcomes, exact McNemar testing is the analogous design. citeturn8search12

Do not make “\(p<0.05\)” the promotion gate. Report the paired effect, confidence interval, raw per-task outcomes and practical importance. Small evals become misleading when “not statistically significant” is interpreted as “equivalent”.

### How much judge calibration is enough

There is **no established universal number of human labels** that makes an LLM judge safe for PRDs, specs, plans or reviews.

A useful current reference is Züfle et al. (September 2026), who selected a **32-item human-scored anchor set** to calibrate conversational judges, explicitly describing 32 as a compromise between noise in smaller sets and annotation cost. Calibration substantially brought different judge score distributions onto a common scale, but their domain was conversations, not software-delivery artefacts. citeturn17view5turn16view0

Statistically, even 32 labels are a *calibration screen*, not a certification. For example, 29 agreements out of 32 is about 91% observed agreement, yet its 95% Wilson interval is only about **76%–97%**. To estimate a true 90% agreement rate to roughly ±10 percentage points under the simple independent-binomial approximation requires about **35 labels**; ±5 points requires roughly **139**. Those are sample-size calculations from the standard binomial normal approximation, not recommendations for every deployment; artefact correlations and label ambiguity generally make the real problem harder. citeturn7search5

For this budget I would therefore use **12–16 human-labelled cases per skill as an error-finding pilot**, with both people independently labelling the ambiguous/must-pass subset, and build a **shared 32-case calibration bank per rubric family**—for example one bank for requirements/spec/design artefacts and another for review/audit artefacts. Those counts are budget recommendations, not validated universal thresholds.

### Which judge design to prefer

The evidence points to a hierarchy rather than a single “best judge”.

**Established practice:** use deterministic or reference-based checks whenever the property permits them. Tests, schema validators, required-section checks, trace assertions, exact tool-use rules and known vulnerability locations are preferable to asking a model for a holistic 1–10 score. Anthropic’s 2026 guidance explicitly recommends deterministic graders where possible, LLM graders where necessary, partial credit where appropriate, and expert calibration of LLM graders. citeturn6view0

**Emerging evidence:** when an LLM must judge, a **locked rubric decomposed into individual claims, with the judge required to cite evidence for each claim**, is more defensible than a single holistic score. Rulers, revised in September 2026, combines fixed criteria, evidence-grounded execution and calibration and reports stronger human agreement in most of four rubric-governed benchmark settings, plus greater stability under semantically equivalent rubric perturbations. citeturn16view1turn17view4

Recent evidence also says not to over-trust rubric judges. RuVerBench contains 2,458 human-annotated rubric-verification cases from long-form deep-research and agentic-coding settings. On its reported leaderboard, the best balanced accuracy shown is **94.7% for Deep Research and 89.4% for Agentic Coding**—good enough to be useful, not good enough to become ground truth. The authors also observe prompt sensitivity and an accuracy/efficiency trade-off from batching multiple rubric items into a single judge call. citeturn18view0turn18view1 Their self-voting study found that most stochastic gains arrived within **three to five judge votes**, with little improvement thereafter; importantly, voting removes sampling noise but cannot fix systematic judge errors. citeturn18view2

**Pairwise judging is useful but not intrinsically safe.** It avoids the calibration problem of absolute 1–10 scales and is a natural fit for A/B. But long-context pairwise judging exhibits position bias, and a 2026 software-engineering study found judge verdicts sensitive to position, verbosity, provenance and other irrelevant cues strongly enough to alter task-level conclusions; it recommends A/B order swapping and prompt perturbation checks. citeturn16view0turn16view3

For this pipeline I would use:

| Artefact | Primary grader | Secondary grader |
|---|---|---|
| PRD / spec / plan | Requirement/checklist coverage against source facts; evidence required | Blinded pairwise preference on clarity/actionability |
| Architecture/design | Structural/reference checks where available | Per-dimension evidence-grounded rubric |
| Build | Executable tests and acceptance criteria | LLM only for non-executable compliance |
| Verification | Hidden test outcomes, mutation/bug detection where possible | Rubric on test quality only |
| Review | Known human review findings/reference comments | Evidence-grounded finding classification |
| Audit | Ground-truth vulnerabilities/verifiers | LLM semantic validation of findings |
| Release | CI/release constraints and known-change checklist | Evidence-grounded completeness/readability review |

A checklist judge should be allowed to return **“insufficient evidence / cannot determine”** rather than being forced to manufacture a score. That is a design recommendation, not a published threshold.

## Minimum eval kit for each delivery stage

The table below is deliberately sized for the stated budget. Task/repeat counts marked **†** are this report’s minimum pilot recommendation rather than a claim that those values give adequate power for small effects. If the pilot produces a close decision, expand the number of distinct tasks first; Anthropic’s current practitioner reference point is 20–50 tasks. citeturn6view0

“Human labels” means artefact-level or pairwise labels used to check the automated judge, not every individual rubric item. Reuse a shared calibration bank where adjacent stages use the same judge protocol.

| Stage | Best small-budget task source | Pilot size | Judge design | Human calibration | Promotion/pass criterion | Approx. model cost* |
|---|---|---:|---|---:|---|---:|
| **Product requirements** | **Internal historical feature briefs → accepted PRDs**. I found no 2026 public set that directly and convincingly grades *PRD creation*. PRDBench/PACE-Bench contain PRDs but primarily evaluate downstream implementation, so they are inputs/proxies, not PRD gold standards. PACE-Bench’s October 2026 work is particularly useful for extracting atomic acceptance “Code Points” from final requirements. citeturn19search0turn20search0 | **12 × 3†** | Source-fact checklist: user problem, actors, constraints, acceptance conditions, explicit non-goals; require evidence for each. Pairwise only as secondary. | **12–16†** | No omitted must-have requirement or invented critical requirement relative to source; paired score must not regress baseline. | **US$7–18** |
| **Specification** | Internal accepted specs/RFCs first. **Hamblin et al. SpecBench**, arXiv:2605.30314 v1, tests identification of deficiencies in real RFC/design proposals from Kubernetes, React, Rust, TVM and vLLM; useful for *spec review*, not yet a direct spec-generation oracle. Paper licence **CC BY 4.0**; upstream RFC artefacts retain their own licences. citeturn20search4turn20search7 | **12 × 3†** | Locked requirement-by-requirement checklist; reference maintainer objections where available. | **12–16†** | No critical ambiguity/inconsistency missed relative to frozen reference; no new unsupported design commitment. | **US$8–20** |
| **Plan** | Internal tickets paired with the actual accepted change set is the closest match. **Agent Planning Benchmark v2**, 4,209 cases across 22 domains, is a useful diagnostic for decomposition, tool-chain and infeasibility reasoning, but it is **not software-delivery-plan-specific** and should only supplement internal cases. citeturn19search1turn19search5 | **12 × 3†** | Checklist against required work, dependencies, ordering, risks and verification; map plan items to actual files/components in reference change when possible. | **12–16†** | Candidate cannot omit a must-do workstream or introduce an impossible prerequisite; paired baseline comparison otherwise. | **US$7–18** |
| **Design** | **R2ABench**, arXiv:2604.06683, directly maps requirements/PRDs to expert-curated PlantUML architectures and supplies structural, semantic and anti-pattern evaluation. Paper is **CC BY 4.0**; confirm dataset-specific Figshare terms before redistribution. citeturn20search6 | **12 × 3†** | Structural graph/reference metrics first; evidence-grounded semantic rubric second. | **12†** | Structural validity plus no critical reference relationship/constraint regression against baseline. | **US$8–20** |
| **Build** | A small slice of **E2EDev** (ACL 2026), which provides fine-grained requirements plus executable BDD scenarios, or PRDBench/PACE-Bench where repository/setup cost is acceptable. E2EDev evaluates generated software through user-facing BDD interactions rather than generic code similarity. citeturn20search9turn20search0 | **10 × 2†** | Hidden executable tests/BDD are primary. LLM judge only for requirements not executable. | **4–8† spot checks** | No regression on must-pass acceptance tests; compare fraction of requirements completed and cost/latency as secondary metrics. | **US$10–25** single variant; **US$20–50+** A/B |
| **Verification** | Reuse E2EDev’s BDD cases for acceptance-test reasoning; **Microsoft TestExplora** is a stronger specialised source for repository-level proactive test generation and bug discovery, built from 2,389 tasks across 482 repositories with time-aware data collection intended to reduce leakage. citeturn12search2turn12search6 | **10 × 2†** | Executed tests, unique bugs exposed, known-fault detection; avoid “looks like a good test” as primary score. | **4–8†** | Must not reduce detection of seeded/known defects or introduce false-success tests; baseline comparison dominates prose quality. | **US$10–30** |
| **Review** | **SWE-PRBench**, arXiv:2603.26130, gives real pull requests with human annotations; public harness pipeline v0.4.1, **MIT** harness and **CC BY 4.0** dataset. It is the cleanest public match for this stage. citeturn20search2 | **12 × 3†** | Reference-based classification of findings first; blinded evidence-grounded judge for additional legitimate findings. | **16†** | No loss on confirmed human findings; track fabricated findings separately because an aggressive reviewer can look “thorough” while becoming unusable. | **US$8–20** |
| **Audit** | **VulnGym**, August 2026, is close to the desired repository-level vulnerability-finding task and deliberately uses recent advisories to mitigate leakage. **CWE-bench** from October 2026 is an excellent methodological bar—120 held-out audit-and-repair tasks across 73 CWE types—but its eval set is private, so it is not a reusable public set. citeturn19search2turn19search6 | **10 × 2†** | Ground-truth vulnerability sites + executable/security verifier where available; score both recall and false findings. | **4–8†** | No loss on known high-severity findings; false positives cannot be ignored. | **US$12–35** |
| **Release** | **ReleaseEval**, arXiv:2511.02713, gives 94,987 release notes from 3,369 projects and was explicitly designed around reproducible, licence-aware collection; it tests release-note generation, not full deployment readiness. Pair it with internal release incidents and runbooks for the gatekeeping part of the skill. citeturn19search3turn19search7 | **12 × 3†** | Reference/checklist for change coverage, breaking-change notices, migration/rollback requirements; deterministic CI/release state first. | **12†** | No omitted critical release action or known breaking change; prose quality is secondary. | **US$6–16** |

\*Cost estimates are calculations from the token assumptions in the cost section below and current OpenAI API rates checked 27 October 2026; they are not vendor quotes for these benchmarks.

### The gaps are informative

There is a notable asymmetry in public evaluation data. Build, testing, review and security have increasingly strong executable or human-labelled 2026 benchmarks. **PRD generation, implementation planning and release-readiness decisions still lack comparably clean public oracles.** For those stages, forcing a tangential benchmark into the eval would create false confidence. Historical internal artefacts—especially ones with the eventual implementation, review comments, incident outcome or acceptance decision—are more valuable.

SpecBench also illustrates why names must be pinned to repository/paper identifiers: there is a separate 2026 project also called **SpecBench**, `WecoAI/SpecBench`, that measures reward hacking in long-horizon coding with visible versus hidden tests and is Apache-2.0 licensed. It is useful for the **build/verification boundary**, but it is not the Hamblin et al. RFC/specification-reasoning benchmark. citeturn23search2turn23search10

### Contamination and licensing

Public GitHub-derived data should be assumed to have **non-trivial contamination risk** unless the benchmark has a deliberate temporal or private holdout. The problem is especially acute for widely circulated issues, RFCs and pull requests. Recent benchmark designs increasingly address this: TestExplora uses time-aware collection, VulnGym selects recent advisories after model cutoffs to reduce leakage, and CWE-bench keeps injected evaluation vulnerabilities private. citeturn12search2turn19search2turn19search6

That means a public benchmark should ideally be only **one slice** of your small eval. A good 12-case pilot might contain several public/reference-rich cases, several internal ordinary cases and several real failures. Do not report the result as a benchmark score unless you used the benchmark’s official protocol.

Likewise, distinguish the **paper licence, benchmark code licence, dataset licence and upstream repository licences**. SWE-PRBench is unusually explicit—MIT harness, CC BY 4.0 dataset. citeturn20search2 For R2ABench, SpecBench and other benchmarks constructed from open-source project artefacts, a CC BY licence on the paper does not by itself relicense every upstream RFC or repository file. Internal reuse for an evaluation is usually operationally simpler than redistributing a derived dataset, but that is a legal/licensing question rather than an evaluation result.

## Turning field runs into the most valuable regression set

This is one of the strongest practices available at small budget because the data are already being generated.

Anthropic’s January 2026 guidance explicitly recommends mining the bug tracker and support queue for evaluation cases and says production monitoring, user feedback, A/B testing and human evaluation should complement offline automated evals. citeturn6view0 OpenAI’s skill-evaluation workflow similarly advocates a living dataset in which discovered trigger misses and output drifts become future cases. citeturn3view0 LangSmith’s current workflow supports turning real traces directly into offline datasets, creating the same production-to-regression loop operationally. citeturn5search5

For every meaningful bad run, preserve five things: the **input/context**, the **exact skill/model/configuration**, the **trace and artefact**, a **short human-written statement of what was wrong**, and a **grader that would catch the same class of failure next time**. Freeze any mutable external state needed to reproduce it. When possible, add a neighbouring “should still work” case so a local fix cannot win simply by becoming over-conservative.

The case should test the **symptom that mattered**, not an accidental implementation path. For example, if a planning skill failed because it omitted a database migration, the regression should check that the necessary migration appears in the plan, not require the exact same seven-step plan wording. Anthropic explicitly recommends grading outcomes rather than over-constraining the path when multiple valid agent trajectories exist. citeturn6view0

A simple case record is enough:

```text
case_id
stage
input / fixture
source = production | incident | public benchmark | synthetic
first_seen_version
should_trigger
must_pass_checks
reference evidence
optional rubric
observed_failure
severity
```

This creates a useful distinction between a **core regression set**, which should almost never change, and an **exploration set**, which can rotate as you search for new failures.

How well does this work? There is strong practitioner convergence that it is useful, but little independent causal evidence showing “production-log regression mining improves agent quality by X%.” A very recent October 2026 example, PACE-Bench, reports the same model moving its mean score from **59.4 to 63.0** across successive harness releases on a frozen task suite, with failure diagnosis used to guide refinement. That is encouraging **emerging evidence**, not a general effect size: it is one benchmark and one development process. citeturn20search0

The best reason to prefer field cases is more basic: they directly improve **distribution relevance**. A regression set composed of things that genuinely hurt your team tells you more about your skill suite than another ten benchmark items selected because they are convenient.

## A cheap, blinded A/B protocol and a separate trigger test

### Comparing the in-house and third-party skill

For a sound small-budget comparison, do not ask “which output do we like better?” after looking at both systems. Freeze the protocol before generating outputs.

**Recommendation:** choose 12–20 tasks † spanning ordinary, difficult and previously failed cases. Run both skills with the **same base model snapshot, reasoning setting, tool permissions, context, repository state and execution budget**. Where a provider offers a seed, record it, but do not assume it makes an agent fully deterministic. Repeat each condition three times for artefact stages; two times can be sufficient as a budget compromise for expensive build/security runs, with extra repetitions allocated only to unstable tasks. The rationale for adaptive rather than uniform extra repetition is supported by recent stochastic-evaluation work. citeturn7search4

For each task, package the output for judging as:

```text
Task context
Frozen rubric / reference facts

Candidate X
[artefact, with skill names / model names / timestamps removed]

Candidate Y
[artefact, with skill names / model names / timestamps removed]
```

Randomise whether in-house is X or Y **independently by task**. For subjective artefacts, run the comparison again with X/Y order reversed. If the same judge flips purely because order changes, mark that comparison unstable rather than taking a majority vote. Position sensitivity is empirically documented both in current long-conversation judge research and in 2026 software-engineering judge audits. citeturn16view0turn16view3

Do **not** show the judge the skill description, vendor, price, model name, generated rationale or prior score. Provenance and “refined version” cues are among the irrelevant signals shown to bias software judges. citeturn16view3

The scoring order should be:

**First, deterministic gates.** Did tests pass? Did the required tool execute? Were forbidden files touched? Did the artefact contain all externally checkable facts?

**Second, independent rubric checks.** Each criterion gets `pass / fail / cannot determine` plus cited evidence.

**Third, pairwise preference.** Ask which candidate is better *given the rubric*, not which seems more professional.

A frontier judge should not be asked to evaluate ten unrelated criteria in one giant call merely to save tokens. RuVerBench’s 2026 experiments found batching can trade away verification accuracy—particularly in coding trajectories—and found only diminishing gains after roughly three to five self-votes. citeturn17view1turn18view2 On this budget, one evidence-grounded judgement plus **order reversal on the subjective pairwise decision** is usually a better investment than five identical judge samples.

Then collapse repetitions into **one result per task per skill** before statistical comparison. For binary pass/fail use paired proportions/McNemar; for pairwise win/loss use an exact sign test; for a continuous rubric score use a paired bootstrap over tasks. Paired evaluation is the critical design choice because task difficulty is usually much larger than the A/B effect you are trying to detect. citeturn8search6turn8search12

Record cost and latency beside quality. A third-party skill that wins artefact quality by a negligible amount while doubling tool calls or repeatedly timing out may be worse operationally. Current agent-evaluation guidance from Google likewise recommends recording latency, token consumption, API cost and tool-call counts alongside quality. citeturn14search9

Finally, manually inspect **all disagreements that could reverse the decision**, not a random handful of easy successes. For a small eval, targeted adjudication is much more valuable than pretending the automated judge is authoritative.

### Evaluating whether the skill triggers

Trigger quality should be a **separate binary-classification eval**, because an excellent skill that is never loaded and a mediocre skill that fires on everything can have similar end-to-end averages.

Current skill systems make this especially important. OpenAI’s skill documentation exposes name/description during capability discovery, and its evaluation recipe explicitly recommends direct, indirect, contextual and `should_trigger=false` cases. citeturn3view0turn1search3 Anthropic similarly describes skill name and description as part of the discovery/routing mechanism. citeturn2search3

Use four kinds of case:

| Case type | Example for a planning skill | What failure means |
|---|---|---|
| Direct positive | “Make an implementation plan for this ticket.” | False negative if the skill does not load |
| Indirect positive | “Before anyone codes this, work out the sequence of changes and dependencies.” | Description is too literal/narrow |
| Contextual positive | User asks for another task, but repository state makes planning explicitly necessary under your intended policy | Skill/context integration miss |
| Negative/confounder | “Summarise this existing implementation plan” or “fix this typo” | False positive; description is too broad |

Balance positives and negatives and report the **confusion matrix**, not just “trigger accuracy”. Anthropic’s current guidance likewise recommends positive and negative cases for behaviours that must trigger selectively. citeturn6view0

Keep a **held-out trigger set** while editing the description. Otherwise you are simply prompt-engineering against the test examples. After each description revision, rerun the frozen cases and inspect both false negatives and false positives.

There is emerging research suggesting the metadata really matters. The June 2026 Agent Skill Evaluation and Evolution survey reports SkillRouter experiments in which routing with only skill names/descriptions was materially worse than configurations with fuller skill content, with reported routing-accuracy drops of roughly **31–44%** in that benchmark setting. This is useful evidence that routing metadata is an optimisation problem of its own, but it should not be treated as an expected real-world effect size for your agents. citeturn0search5

OpenAI also reports a Glean deployment anecdote in which skill-based routing initially reduced triggering by about **20%** and was recovered through negative examples and edge-case refinement. That is a vendor/partner case study, not an independent experiment, so it is evidence of a plausible failure mode rather than an effectiveness estimate. citeturn1search15

## Costs, misleading results, and the practice I would actually adopt

### Realistic spend

Costs vary more with agent trajectory length than with the eval framework itself. To make the estimates auditable, here is a current pricing yardstick rather than a claim that you should use this particular model.

As of **27 October 2026**, OpenAI lists GPT‑5.6 Sol at **US$4/M input tokens and US$20/M output tokens** under its current promotional pricing, available at least through 21 November 2026. Current standard pricing also lists GPT‑6.1 Terra at **US$1/M input and US$5/M output**, so using a cheaper judge can reduce grading cost substantially. citeturn15search0turn15search2

Using GPT‑5.6 Sol purely as a conservative arithmetic example:

| Technique | Assumption | Approx. API spend | Human time, small-team estimate |
|---|---|---:|---:|
| Trigger-only test | 24–40 short routing prompts †; about 3k input + 300 output tokens each | **<US$1** | ~20–45 min |
| Artefact pilot | 12 tasks × 3 = 36 runs †; roughly 15k–40k input + 3k–8k output/run | **~US$4–12** for generation | ~1–3 h to prepare/review |
| One rubric judgement/run | about 8k input + 1k output | roughly **US$0.05/judgement** at the stated rates | negligible automated; calibration dominates |
| Three-vote LLM judge | Same judgement ×3 | roughly **3× judge spend** | no extra human time, but does not fix systematic errors |
| Blinded artefact A/B | 12 × 3 × 2 = 72 agent runs † plus pairwise judges | roughly **US$10–25** under the above trajectory assumption | ~2–4 h including adjudication |
| Executable build A/B | 10 × 2 × 2 = 40 runs †; roughly 75k–200k input + 10k–20k output/run | roughly **US$20–50+** | ~2–5 h if environments already exist |
| Field-failure regression | Existing production run; one replay after case creation | usually **well below a fresh suite’s cost** | ~15–60 min per useful incident case |
| Full 32-case human calibration bank | LLM cost trivial relative to annotation | usually **<US$5** in judge calls | likely several person-hours; artefact length dominates |

The assumptions and counts marked † are planning estimates from this report, not vendor benchmarks. Tool charges, web search, sandboxes, paid MCP services, CI compute and long cached repository contexts can all materially change the total. Current OpenAI pricing explicitly charges some tools separately from model tokens. citeturn15search0

The key budget insight is that **judge tokens are rarely the expensive part**. Agent executions, environment setup and human adjudication are. That argues for spending human effort on a small number of high-information labels and model budget on paired repetitions, rather than building elaborate scoring infrastructure.

### How small evals most often lie to you

| Failure mode | Why it misleads | Defence |
|---|---|---|
| **Pseudo-replication** | 12 tasks × 5 stochastic runs are reported as \(n=60\), artificially shrinking uncertainty. | Aggregate within task; bootstrap/test over distinct tasks. citeturn8search6turn7search4 |
| **One run per task** | A lucky or unlucky trajectory is mistaken for skill quality. | Use repeated trials; inspect tasks whose outcomes flip. Anthropic explicitly defines trials separately because agent outputs vary. citeturn6view0 |
| **Judge is treated as ground truth** | Frontier rubric judges still make substantial errors on long agentic material. | Human-calibrate; require evidence; preserve “cannot determine”; audit disagreements. citeturn18view0turn18view1 |
| **Holistic 1–10 scoring** | Criteria drift together and the judge’s internal scale is poorly calibrated. | Lock a decomposed rubric; evidence-ground each item; calibrate the score mapping if an absolute score is truly needed. citeturn16view1 |
| **Unblinded A/B** | Skill name, vendor, order, formatting or “new version” cues change judge preference. | Strip provenance; randomise A/B; reverse order; human-adjudicate unstable pairs. citeturn16view3 |
| **Too many criteria in one judge call** | Batching is cheap but can dilute attention on long coding/agent traces. | Judge high-risk requirements separately; batch only low-risk mechanical checks. citeturn17view1turn18view2 |
| **Benchmark contamination** | The agent may recall public issues/RFCs rather than perform the stage skill. | Mix in recent/private/internal cases; prefer temporal/private holdouts; record case provenance. citeturn19search2turn19search6 |
| **Overfitting the description to trigger tests** | Routing improves on the examples you kept rewriting against while unseen false positives rise. | Freeze a held-out trigger slice and retain negative controls. citeturn3view0turn6view0 |
| **Only happy-path tasks** | The suite measures formatting on familiar requests, not whether the skill knows when or how to intervene. | Include ordinary cases, indirect requests, real failures and cases where the correct behaviour is to stay quiet. citeturn3view0 |
| **Optimising the rubric instead of the outcome** | A verbose artefact can score highly while downstream execution fails. | Wherever possible, add a downstream/executable check: architecture graph, accepted code change, hidden test, human PR finding or release incident. |
| **Suite saturation** | Once every case passes, the metric stops discriminating and regressions hide behind a ceiling. | Keep the core regression set but continually add real failures and harder cases. Anthropic specifically warns about eval saturation. citeturn6view0 |
| **“No significant difference” = “same”** | Small suites have little power for modest effects. | Report effect and CI; call the result *inconclusive* when both a meaningful gain and loss remain plausible. citeturn7search5turn8search6 |
| **Ignoring cost and trajectory** | A slightly better final artefact may require loops, excessive tool calls or several times the tokens. | Gate on outcome first, but always report tokens, latency and tool counts next to it. citeturn14search9 |

### The lightweight practice I would standardise

For nine skills, I would build **one common harness and one schema**, not nine evaluation projects. Each case contains the input fixture, trigger expectation, must-pass checks, optional reference, optional rubric and provenance. Every run records skill/version, model snapshot, final artefact, trace, token/cost data and grader results. That structure aligns closely with OpenAI’s current skill-eval recipe and Anthropic’s task/trial/grader/trace decomposition. citeturn3view0turn6view0

The initial suite for each stage should contain roughly a dozen high-information cases, not dozens of synthetic near-duplicates. Start with real historical work and a small number of the public stage-aligned examples above. Run the skill against a frozen baseline. Human-check the automated judge on the cases that matter. When a field run fails, add it. When the score saturates, add harder cases rather than merely celebrating 100%.

The decision output for every proposed skill change can fit on one page:

```text
Skill / version:
Baseline:
Task set version:
Distinct tasks:
Trials per task:

Trigger:
  false negatives:
  false positives:

Outcome:
  candidate wins / ties / losses:
  paired effect:
  confidence interval:
  critical regressions:

Variance:
  tasks with mixed repeated outcomes:

Judge validation:
  human-labelled cases:
  judge disagreements:
  order-sensitive comparisons:

Efficiency:
  median tokens:
  median latency:
  median tool calls:
  estimated cost:

Decision:
  promote | reject | inconclusive
Reason:
  ...
New regression cases added:
  ...
```

That is enough infrastructure to create a genuine learning loop without pretending to run a benchmark programme.

The central conclusion is therefore somewhat counter-intuitive: **do not spend the small budget trying to obtain a precise “skill score”. Spend it making comparisons paired, failures reproducible, judges auditable, triggers explicit and cases increasingly representative of real work.** The statistical evidence says a 10–20-task suite cannot support fine distinctions; the 2026 agent-evaluation evidence says stochasticity, routing and judge error are all material; and the current tooling is finally good enough that capturing those dimensions no longer requires a large evaluation platform. citeturn7search5turn7search4turn18view1turn3view0