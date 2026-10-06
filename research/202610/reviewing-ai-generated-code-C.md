# How the Industry Reviews AI-Generated Code and AI-Heavy Codebases in H2 2026

## Executive summary

The evidence base in 2026 is much better than it was even a year ago, but it is uneven. We now have large observational studies of tens of thousands of agent-authored pull requests, the first peer-reviewed work specifically on agentic review, security, testing, rejection and reviewer burden, telemetry from commercial engineering platforms, public policies from major open-source projects, and unusually candid accounts from AI-forward companies. What we do **not** yet have is equally strong longitudinal evidence from banks, medical-device companies, automotive firms, or other highly regulated incumbents showing exactly how their internal AI-written-code pipelines work.

A useful way to read this report is therefore: `[measured]` means the claim is supported by numbers and a stated empirical method; `[first-hand]` means an organisation or practitioner describes what they actually do without a credible independent outcome measurement; `[vendor]` means the evidence comes from a company selling the relevant product or service and should not be treated as independently established; `[opinion]` means a recommendation, interpretation, or practitioner judgement. Where vendor numbers are included, I explicitly treat them as unverified unless there is independent corroboration.

### What has actually converged

**Human accountability has survived the transition to agentic coding, even where human keystrokes have not.** `[first-hand]` Anthropic says its Code Review system runs on nearly every internal PR, dispatching multiple review agents, but the system deliberately does not approve the PR: the merge decision remains human. LLVM's current policy is even more explicit: contributors may use AI, but they must personally review the generated material, understand it, be able to answer questions about it, and remain the accountable author. Google, meanwhile, reported in 2026 that a very large share of new code was AI-generated but still human-reviewed. citeturn6view0turn21search9turn23news37

**The emerging review architecture is “cheap deterministic checks → AI triage/review → selective deep human review”, not “replace review with another LLM”.** `[first-hand]` GitHub's 2026 guidance tells reviewers to inspect CI/gating changes early and specifically look for removed tests, disabled workflows, lowered coverage, ignored failures and duplicated utilities. Addy Osmani describes using agents for first-pass risk triage while retaining the human merge decision. `[measured]` An MSR 2026 study provides an important counterweight to vendor enthusiasm: among 3,109 PRs receiving comments, CRA-only — code-review-agent-only — PRs merged at 45.20%, versus 68.37% for human-only reviewed PRs; 60.2% of closed CRA-only PRs had only 0–30% of their reviewer comments classified as useful signal. citeturn6view1turn3view0turn17view3

**Small, focused changes have become a quality and review-capacity control, not merely a style preference.** `[measured]` Analysis of 33,707 agent-authored PRs found a two-regime distribution: 28.3% merged essentially immediately, while a costly tail generated iterative reviewer work and “ghosting”; a creation-time classifier using simple features such as patch size and file types achieved AUC 0.96 for identifying high-maintenance PRs. Another 2026 study found failed/non-merged agent PRs tend to touch more files and contain larger changes. `[first-hand]` LLVM explicitly advises new AI-assisted contributors to begin with small changes they fully understand. citeturn17view1turn17view2turn21search9

**The bottleneck has moved from production of code to verification of code.** `[measured]` The Stack Overflow 2026 Developer Survey, fielded June 23–August 5 with 30,903 valid responses across 169 countries, found 65.9% using coding assistants/agents and 26.2% using agent workflows. Yet only 6.6% said they trusted AI even for important decisions; 76.5% of respondents who validate AI answers run code locally, 63.9% compare against the existing codebase, and 53.0% inspect tests/security implications. `[vendor]` Faros's 22,000-developer/4,000-team telemetry paints an even harsher picture: as AI adoption rose within organisations, it reports large increases in review latency and engineering incidents. Those Faros figures are commercially produced and not independently replicated, but the direction of the bottleneck is consistent with independent PR studies. citeturn14view1turn14view2turn4view0turn18view3

**AI-generated code is increasingly reviewed for failure patterns that ordinary “does this diff look right?” review misses: gate manipulation, redundant implementation, superficial tests, unrequested scope, and security weaknesses.** `[measured]` MSR 2026 found measurable excess redundancy in AI-generated PRs; a separate study of 7,200 agent PRs and 6,620 human PRs across 818 repositories found agent changes can introduce serious CWE-class findings such as hard-coded credentials and command injection, although agents were not uniformly less secure than humans and actually did well on some small focused fixes. `[first-hand]` GitHub now explicitly tells reviewers to look for altered CI, skipped checks and plausible-looking but semantically wrong implementations. citeturn17view0turn20view1turn6view1

### What remains contested

**Whether sufficiently low-risk changes should bypass human review entirely is unresolved.** `[measured]` There clearly exists a large class of trivial agent PRs that merge with little interaction, but CRA-only review currently has substantially worse observed outcomes than human-only review in open-source data. `[opinion]` The likely end state is not one universal rule but a risk-tiered exception: genuinely low-blast-radius changes with strong deterministic oracles may auto-merge, while security, auth, migration, persistence, finance, deployment, test-infrastructure and architecture changes remain human-gated. citeturn17view1turn17view3

**Multiple independent AI reviewers are promising but not proven as a replacement for one good human.** `[vendor]` Anthropic's product explicitly uses several specialised agents and verification passes, and practitioners report complementary findings from different reviewers. `[measured]` The larger empirical record warns that review agents generate substantial noise; “more models” can therefore produce either useful diversity or reviewer-amplified spam. No 2026 study I found demonstrates that an all-AI multi-reviewer ensemble produces lower escaped-defect rates than a competent human plus deterministic gates. citeturn6view0turn17view3turn3view0

**There is still no converged “AI-heavy repository audit” discipline.** `[opinion]` Change-level practice is maturing much faster than codebase-level assurance. I found no broadly adopted 2026 equivalent of an “AI Codebase Audit Standard” specifying cadence, architecture metrics, provenance checks, duplication thresholds, mutation-score targets or architectural-drift rules. Public practice instead composes ordinary software-assurance techniques — static analysis, security scanning, test-quality analysis, dependency/licence controls, architecture review — with agent-assisted repository sweeps. That absence is itself one of the most important findings.

## Findings by research question

### Review architecture

The dominant architecture is becoming **layered rather than monolithic**. `[first-hand]` The strongest publicly documented pattern is: agent generates a change and usually runs its own tests; cheap deterministic checks run; an AI reviewer or reviewers inspect the diff; humans examine high-value findings and consequential portions of the change; required CI/security gates decide eligibility; a human owns the final decision. GitHub's May 2026 guidance specifically recommends looking at workflow/CI changes before spending time reading implementation details, because weakening the oracle makes every later signal suspect. Addy Osmani similarly argues for deterministic fast-fail checks before expensive semantic review. citeturn6view1turn3view0

`[first-hand]` Anthropic is the clearest AI-forward example. Its March 9 Code Review announcement says the system is used on nearly every Anthropic PR. Several agents inspect a PR in parallel, candidate findings are themselves verified, issues are ranked, and the system generates summaries and inline comments. Review effort scales with PR complexity. Crucially, it does not emit an approval verdict; the human still approves or rejects. citeturn6view0

`[measured]` Open-source evidence argues against collapsing this into “LLM reviewer says LGTM”. Chowdhury et al.'s MSR 2026 study of 3,109 commented PRs found CRA-only reviewed changes substantially less likely to merge than human-only reviewed ones, and most closed CRA-only PRs contained very low-signal automated feedback. The authors' practical conclusion is augmentation rather than replacement. citeturn17view3

`[measured]` Ordinary CI remains very important. A study of 8,031 agent PRs that modified CI/CD configuration found such changes were only 3.25% of agent changes and were not, in aggregate, dramatically less reliable: build success was 75.59% for CI/CD-touching changes versus 74.87% for others. That is important because “agents always sabotage CI” is not supported as a general empirical claim. The more defensible claim is narrower: because an agent *can* change the mechanism used to judge it, those files deserve special scrutiny. citeturn19academia28

`[first-hand]` Formal verification remains exceptional. LLVM's policy notably cites an Alive2 proof as an example of a strong correctness signal, but there is no evidence that formal proofs are a normal gate for general agent-written product code. Similarly, held-out tests are foundational in coding-agent evaluation, but I did not find convincing public evidence that independent hidden tests are yet a normal production PR gate outside specialised environments. citeturn21search9

**Evidence grades used:** `[measured]`, `[first-hand]`, `[opinion]`.

### Division of labour

`[measured]` The industry has **not** moved to blind trust. In Stack Overflow's 2026 survey, only 6.6% of respondents said they trusted AI even for important decisions; 48.0% trusted it when results were easily verifiable, and another 16.3% limited trust to many tasks except important decisions. Current AI use was already substantial in reviewing code/PRs/design decisions at 40.5%, but only 19.9% reported AI use for production deploy/operation/troubleshooting — a strong indication that riskier, less reversible stages remain more human-heavy. citeturn14view1

`[first-hand]` Published practitioner practice increasingly separates **reading every token** from **owning the behaviour**. Osmani describes AI-first triage followed by human attention proportional to blast radius, expected lifespan and team exposure. The human focuses on intent, boundary conditions, surprising behaviour, architecture and irreversible decisions rather than mechanically re-reading every generated line. citeturn3view0

`[first-hand]` LLVM takes a stricter stance for external contributions: the contributor must read and review generated code before asking maintainers to spend review time on it, understand it well enough to answer questions, and disclose substantial tool-generated content. It bans autonomous agents that act directly in LLVM's collaborative spaces without human approval and similarly disallows automated review comments published without a human in the loop. citeturn21search9

`[measured]` Skill still matters even when agents do the implementation. A 2026 study of 22,953 PRs from 1,719 AI-assisted “vibe coders” found lower-experience contributors submitted changes with 2.15× as many commits and 1.47× as many files, received 4.52× as many review comments, had 31% lower acceptance rates, and remained open 5.16× longer than higher-experience contributors. That is one of the best pieces of evidence against the proposition that review expertise becomes unnecessary once generation quality gets good. citeturn18view3

Published “trust tiers” are more often principles than formal matrices. `[first-hand]` Anthropic scales review depth with size/complexity; LLVM asks contributors to reduce size/complexity when a contribution becomes “extractive”; Osmani proposes explicit risk tiers. `[opinion]` Across these sources, the de facto trust axes are not mainly “which model wrote it?” but blast radius, reversibility, size, test oracle strength, security sensitivity and whether the change alters its own validation machinery. citeturn6view0turn21search9turn3view0

I found **no credible public 2026 standard reviewer-to-agent ratio**, nor a widely adopted numerical rule such as one human per five agents. `[opinion]` Any such number currently depends far more on task granularity and gate quality than on agent count.

**Evidence grades used:** `[measured]`, `[first-hand]`, `[opinion]`.

### Codebase-level audit practice

Here the honest answer is: **the industry is much less mature than at PR review**.

`[measured]` There is empirical justification for repository-level re-auditing. Huang et al.'s *More Code, Less Reuse* found agent-generated PRs more likely to duplicate existing functionality, while reviewers' expressed sentiment toward those AI contributions was nevertheless more neutral/positive. That combination is dangerous: local plausibility can coexist with global redundancy. citeturn17view0

`[measured]` Security likewise cannot be inferred from a green test suite. The MSR study of 13,820 total agent/human PRs used four SAST engines and found agent changes introducing recognised weakness classes, with outcomes dependent on task type and change scope. That supports periodic repository-wide SAST rather than relying exclusively on the diff-time reviewer's semantic judgement. citeturn20view1

`[measured]` Tests are also an ambiguous proxy. Milanese et al. examined 6,582 human-agent PRs and 3,122 human-only PRs. Human-agent PRs included tests at roughly similar rates — 42.9% versus 40.0% — and had almost twice the test-to-source-line ratio, yet test-smell differences were negligible in practical effect. More test code therefore does not establish stronger behavioural assurance. citeturn18view1

`[opinion]` Based on what is actually published, a mature AI-heavy repository audit in late 2026 is best described as a **bundle of existing assurance mechanisms**, not a named AI-specific framework: duplicate/clone detection; dead-code and dependency analysis; security SAST/SCA/secret scanning; licence/provenance inspection; mutation or fault-injection testing where feasible; test-to-requirement review; architecture/dependency-boundary checks; inspection of CI/configuration changes; and incident/revert analysis.

`[opinion]` Cadence is not converged. The strongest triggers are event-driven rather than calendar-driven: a large agent-generated migration; rapid expansion in generated LOC; repeated near misses or reverts; major framework/dependency replacement; an auth/data-boundary change; a newly autonomous long-running agent; or signs that duplicate abstractions and cross-layer shortcuts are accumulating. I found no defensible empirical basis for “audit every month” versus “quarterly”.

The lack of a named standard matters. `[opinion]` A repository can pass every PR-level check while its architecture becomes less coherent one locally reasonable change at a time. None of the major 2026 datasets yet gives us a validated leading indicator for that long-horizon failure.

**Evidence grades used:** `[measured]`, `[opinion]`.

### Known failure modes

The strongest 2026 evidence lets us separate **documented phenomena** from things that are currently mostly reviewer folklore.

| Failure mode | State of evidence in 2026 |
|---|---|
| Redundant helpers / missed reuse | **`[measured]`** MSR 2026 found more redundancy in agent-generated PRs. citeturn17view0 |
| Oversized / sprawling changes | **`[measured]`** Non-merged agent PRs are larger and touch more files; low-experience AI-assisted contributors produce materially larger review burdens. citeturn17view2turn18view3 |
| Unwanted scope / wrong task | **`[measured]`** Qualitative analysis of 600 failed agent PRs identified unwanted feature implementation, duplicates and misalignment among rejection patterns. citeturn17view2 |
| CI/test failure | **`[measured]`** Non-merged agent PRs disproportionately fail project CI; a separate 306-case qualitative study also identified failing CI/tests as a rejection class. citeturn17view2turn19academia27 |
| Gate weakening to “get green” | **`[first-hand]`** GitHub tells reviewers to look for deleted tests, lint suppression, coverage changes, `|| true`-style ignored failures and disabled workflows. I found guidance, not a population-level incidence estimate. citeturn6view1 |
| Tests that merely confirm the implementation | **`[first-hand]`** GitHub recommends requiring a regression test that demonstrably fails before the fix. **`[measured]`** Increased test volume in agent-assisted PRs does not itself imply materially better test quality. citeturn6view1turn18view1 |
| Security regressions | **`[measured]`** 7,200 agent PRs were found to introduce CWE-class issues including hard-coded credentials and command injection, although comparative performance was task-dependent rather than uniformly worse than humans. citeturn20view1 |
| Reviewer abandonment / “ghosting” | **`[measured]`** The 33,707-PR study documents a costly high-effort tail; rejection studies show substantial workflow/reviewer-interaction causes rather than simply bad code. citeturn17view1turn16view2 |
| Fabricated “verification succeeded” claims | **`[opinion]`** Plausible and frequently discussed, but I did not find a robust 2026 incident dataset that quantifies agents falsely claiming to have run tests. Treat it as a threat model, not an established frequency. |
| Licence contamination | **`[first-hand]`** LLVM explicitly makes contributors responsible for ensuring generated material does not reproduce code they lack the right to contribute. I found policy concern but no credible 2026 incidence estimate for contamination in merged agent PRs. citeturn21search9 |
| Prompt injection through issues/PR text | **`[first-hand]`** GitHub's 2026 review guidance treats untrusted issue, commit and PR text reaching privileged agents as a security concern. Public prevalence evidence remains weak. citeturn6view1 |

One important correction to popular discourse: `[measured]` **rejection rate is not the same as agent failure rate**. Peralta et al. analysed 11,048 closed agent PRs, narrowed to 9,799 human-reviewed PRs and manually examined 717 representative cases. Among rejected PRs, only 35.7% clearly reflected agentic failure; 31.2% were workflow constraints and 33.1% lacked enough observable rationale. Among merged PRs, 15.4% still required explicit reviewer feedback or direct commits. citeturn16view2

This is why raw merge rate is a poor quality metric.

**Evidence grades used:** `[measured]`, `[first-hand]`, `[opinion]`.

### Metrics

There are now three distinct metric families: **flow**, **quality**, and **verification burden**.

`[measured]` Academic studies provide unusually useful verification-burden measures: comments per PR, time open, files/commits touched, CI success, interaction count, acceptance and abandonment. The novice-versus-experienced study's 4.52× reviewer-comment difference and 5.16× resolution-time difference are particularly revealing because they measure work shifted onto reviewers rather than generation throughput. citeturn18view3

`[measured]` The 33,707-PR “Circuit Breaker” study shows why distributions matter more than averages. A large trivial population coexists with a disproportionate expensive tail; at a simulated 20% review budget, its classifier captured 69% of high-effort contributions. For an agent-first team, “percentage of PRs requiring more than N human minutes” is therefore likely more informative than median PR review time alone. citeturn17view1

`[vendor]` Faros's 2026 telemetry compared periods of lowest and highest AI adoption inside organisations covering about 22,000 developers and 4,000 teams. It reports task throughput +33.7% and PR merge rate +16.2%, but also code churn +861%, incidents-per-PR +242.7%, monthly incidents +57.9%, bugs/developer +54%, median time to first review +156.6%, average time in review +199.6%, and median review time +441.5%. It also reports a 31.3% rise in PRs merged without human *or agentic* review. These numbers are striking but **unverified outside Faros** and come from a vendor whose business is engineering analytics; they should be treated as a warning signal, not industry ground truth. citeturn4view0

`[vendor]` Anthropic publishes a different set of internal product metrics. It says substantive-review-comment coverage rose from 16% of PRs before its Code Review system to 54% after deployment. For PRs above 1,000 lines, it reports findings on 84% of reviews with a mean 7.5 findings; below 50 lines, 31% had findings with a mean 0.5. Average review cost is reported as roughly US$15–25 and average processing time about 20 minutes. These are useful operational numbers but remain self-reported vendor measurements without independent replication. citeturn6view0

`[measured]` Stack Overflow provides the best broad 2026 adoption/validation baseline rather than outcome data: 30,903 valid respondents, 65.9% using coding assistants/agents, 26.2% using agent workflows, and only 9.6% of validators saying they use AI answers as-is. citeturn14view1turn14view2

`[opinion]` The minimum useful dashboard for an agent-first shop is therefore: PR/diff size distribution; human review minutes per merged change; percentage auto-rejected before human review; comments or review turns per change; change failure/revert rate; escaped incidents; duplicate-code trend; mutation or equivalent oracle-strength trend; percentage of changes altering tests/CI together with production code; agent compute cost per *accepted* change; and cost per escaped defect. “Agent tokens used” and “LOC generated” are capacity figures, not success metrics.

**Evidence grades used:** `[measured]`, `[vendor]`, `[opinion]`.

### Process and policy

`[first-hand]` Open source has moved fastest toward explicit accountability rules. LLVM's current AI Tool Use Policy is unusually complete. Contributors may use AI tools, but must personally review their contribution, understand it, remain accountable, disclose substantial generated content, and avoid autonomous agents publishing directly into project spaces without human approval. It suggests an `Assisted-by:` commit trailer, recommends human-written PR descriptions, bans AI automation of `good first issue` tasks, and allows maintainers to mark burdensome contributions `extractive`. citeturn21search9

That last concept may matter more than AI disclosure itself. `[first-hand]` LLVM defines the practical problem in terms of maintainer economics: a contribution becomes extractive when its review cost exceeds its expected value. The remedy is to reduce size/complexity or increase demonstrated usefulness. This maps closely onto the empirical finding that a minority of agent PRs consume disproportionate human attention. citeturn21search9turn17view1

`[first-hand]` Open-source projects are nevertheless diverging sharply. In 2026, Godot publicly moved toward rejecting AI-authored contributions because maintainers said heavy AI users frequently could not repair or explain the code they submitted; Zig leadership similarly defended a strict prohibition. Debian took the opposite approach, allowing AI-assisted contributions subject to normal quality/legal responsibility and human accountability. These reports are based on project statements but the sources available here are secondary press coverage, so the policy direction is clearer than the comparative outcome evidence. citeturn21news44turn21news43turn21news45

`[first-hand]` GitHub's own 2026 guidance recommends that the person submitting an agent-produced PR self-review it before imposing it on someone else. That increasingly appears to be the social norm: the human operator is treated as the author-of-record even if the agent produced almost all text. citeturn6view1

`[measured]` Provenance itself is becoming difficult to reconstruct after the fact. A 2026 census across more than 180 million Git repositories used multiple signals and found that bot-identity matching alone recovered only 3.3% of the Claude Code activity their broader detection method identified. In other words, relying on GitHub “bot” identity to infer AI authorship will miss most activity. citeturn19academia30

`[opinion]` This weakens the case for hidden, model-specific provenance inference and strengthens the case for explicit operational metadata: agent/tool, model if known, initiating human, task/run identifier, material generated, tests executed, and human reviewer. That metadata is more useful for incident analysis than an ornamental “AI generated” badge.

I found no defensible industry norm for agent PR review SLA, reviewer-to-agent ratio, or a universal maximum PR size. `[measured]` What the evidence supports instead is a monotonic relationship: bigger/more diffuse changes are more expensive to review and fail more often. citeturn17view1turn17view2turn18view3

**Evidence grades used:** `[measured]`, `[first-hand]`, `[opinion]`.

### Tooling landscape

By late 2026 the key distinction is no longer “AI reviewer versus static analyser”; it is **probabilistic reviewer versus deterministic oracle**.

| Tool/category | What it actually does | Evidence status |
|---|---|---|
| **Anthropic Code Review** | Runs multiple specialised review agents in parallel, verifies candidate findings, ranks them and comments on PRs; does not approve the PR. | `[vendor]` Detailed internal metrics exist, but effectiveness numbers are Anthropic's own. citeturn6view0 |
| **GitHub Copilot code review** | Reviews GitHub diffs and produces review comments; GitHub also documents agent-PR review workflows and security pitfalls. | `[vendor]` GitHub says Copilot code review has handled tens of millions of reviews and that agent involvement in GitHub reviews is now widespread; platform self-report, not an independent quality result. citeturn6view1 |
| **CodeRabbit** | AI PR reviewer producing line-level and summary feedback, with repository context. | `[vendor]` Widely visible in 2026 tooling comparisons, but I found no strong independent escaped-defect study that justifies vendor accuracy claims. Addy's practitioner survey includes it among the new review layer. citeturn3view0 |
| **Greptile** | Repository-aware AI code review using broader codebase context. | `[vendor]` Same caveat: product capability is clear; comparative production effectiveness is not independently settled. citeturn3view0 |
| **Cursor Bugbot** | Automated PR bug review attached to an agentic IDE/development environment. | `[vendor]` Product is an example of an agent reviewing agent-produced changes; independent outcome evidence remains thin. citeturn3view0 |
| **Qodo / PR-Agent family** | Automated PR description/review/improvement workflows; PR-Agent has an OSS lineage. | `[vendor]` Useful as a programmable reviewer, but I found no 2026 field evidence sufficient to rank it against human review. |
| **CodeQL / Semgrep / ordinary SAST** | Deterministic or rule/data-flow-oriented checks for specific vulnerability classes. | `[measured]` Multi-engine SAST research demonstrates why this independent layer remains valuable even with AI reviewers. citeturn20view1 |
| **Ordinary CI, linters, type checks, unit/integration tests** | Binary or reproducible gate based on program behaviour or syntax/type constraints. | `[measured]` CI outcome remains strongly associated with agent PR acceptance; these checks provide a different failure mode from LLM judgement. citeturn17view2turn19academia28 |

The independent result that matters most is not a leaderboard. `[measured]` The 2026 MSR analysis of code-review agents found low signal-to-noise when automated reviewers operated without humans. That should make teams sceptical of vendor precision/recall claims unless evaluations use real repository changes, report false positives and false negatives, and measure escaped defects or validated findings rather than “number of comments produced”. citeturn17view3

`[opinion]` Tool diversity can nevertheless be useful because correlated failure is the central risk. A compiler, type checker, test suite, SAST engine and LLM reviewer fail for different reasons. Two LLM reviewers built on similar frontier models may look diverse while sharing the same semantic blind spots.

**Evidence grades used:** `[measured]`, `[vendor]`, `[opinion]`.

### Incumbents versus AI-forward companies

The surprising result is how much the two camps already agree on the *shape* of control.

`[first-hand]` Large incumbents are rapidly increasing agent-generated code while retaining conventional ownership controls. Google said in its Q1 2026 remarks that engineers were beginning to orchestrate “fully autonomous digital task forces”; contemporaneous reporting put AI-generated new code at roughly 75%, still reviewed by human engineers. GitHub's public guidance similarly assumes agent-authored PRs but reinforces CI, author self-review and human judgement. citeturn10view1turn23news37turn6view1

`[first-hand]` AI-forward organisations go further on **review automation**, not necessarily on removing humans. Anthropic's internal stack is the clearest case: heavy AI generation followed by heavy AI review, then human ownership of the merge. The human role becomes specification, risk assessment, interpretation of reviewer findings, architecture and accountability. citeturn6view0

The divergence is therefore mostly about **where human attention is spent**. `[opinion]` Incumbents tend to graft agents onto existing PR/CI/security/change-management systems. AI-forward teams redesign the workflow around agents and increasingly treat human line-by-line reading as scarce capacity to be allocated. Open source, where reviewer labour is unpaid and especially scarce, is the segment most willing to reject the entire externalisation model and simply ban or constrain agent-generated submissions. LLVM explicitly frames this as avoiding “extractive” contributions. citeturn21search9turn21news44

Is either side demonstrably getting better outcomes? **No strong causal evidence yet.** `[measured]` Open-source agent PR studies establish acceptance, review effort and quality characteristics, but they are not randomised organisational comparisons. `[vendor]` Faros suggests organisations with aggressive AI adoption can degrade on quality/review measures; Anthropic reports dramatically wider review coverage after adding AI review. These results can both be true and are not directly comparable. citeturn4view0turn6view0

`[opinion]` The strongest inference is that successful AI-forward practice is not “less verification”; it is **more automated verification per unit of human attention**. The evidence is hostile to the simpler idea that generation quality alone eventually makes review unnecessary.

**Evidence grades used:** `[measured]`, `[first-hand]`, `[vendor]`, `[opinion]`.

### Regulated and safety-critical contexts

There is a significant policy gap here.

`[first-hand]` NIST's existing Secure Software Development Framework remains risk- and outcome-oriented: secure development processes, protection against tampering, producing well-secured software and responding to vulnerabilities. NIST SP 800-218A extends the SSDF for generative-AI and foundation-model development, but it is primarily about building AI systems/models; it is **not** a mature prescriptive standard for “how a bank must review code written by Claude/Codex”. citeturn22search0turn22search4

`[first-hand]` NIST was still evolving the underlying SSDF in 2026: a draft SSDF 1.2 was released in December 2025 for comment, describing updated secure and reliable development practices. The important regulatory pattern remains provenance-independent: demonstrate a defensible SDLC and objective assurance, rather than relying on who — human or AI — typed the source. citeturn22search18

`[first-hand]` The medical-device regime shows the same structure. FDA continues to recognise IEC 62304 for medical-device software lifecycle processes, ISO 14971 for risk management and related software-assurance standards. Its recognised-standards catalogue does not create a separate exemption or lighter review path for AI-authored implementation. The manufacturer's validation, risk management, cybersecurity and design-control obligations remain. citeturn22search1turn22search5

`[opinion]` For automotive, finance and other safety-critical environments, the defensible 2026 interpretation is therefore **tool provenance does not transfer accountability**. If AI generates a safety-relevant module, the organisation still needs the evidence required by the applicable software lifecycle, cybersecurity, validation, segregation-of-duties and change-control regime. In some settings AI use may actually increase the required evidence because the generator itself is not a qualified deterministic development tool.

I did **not** find a 2026 OSFI, FDA, NIST or ISO rule saying “AI-written source must receive two human reviewers”, nor an AI-specific formal-verification mandate. `[opinion]` Claims that regulators have already standardised review ratios or mandatory disclosure regimes for generated source should therefore be treated sceptically.

For a regulated shop, `[opinion]` the safest near-term pattern is an asymmetric trust model: AI may generate implementation aggressively, but it does not alter or waive safety/security requirements, acceptance criteria, test independence, traceability, segregation of duties or accountable sign-off.

**Evidence grades used:** `[first-hand]`, `[opinion]`.

### Open problems

**Review throughput is not solved.** `[measured]` The 33,707-PR study's expensive tail and the 22,953-PR experience study both show agent productivity can become reviewer load. `[vendor]` Faros reports the same phenomenon inside commercial teams through much longer review times. citeturn17view1turn18view3turn4view0

**AI reviewing AI is not solved.** `[measured]` Automated code reviewers can produce a great deal of low-signal feedback. `[vendor]` Multi-agent verification such as Anthropic's may suppress false positives, but independent production evidence is not yet strong enough to establish equivalence to expert human review. citeturn17view3turn6view0

**Runtime correctness is not solved by source review.** `[measured]` Security findings vary by task and scale, and green CI does not imply absence of semantic/security defects. `[opinion]` The more capable the agent becomes at producing plausible source and its own tests, the more valuable independent behavioural oracles — integration tests, contract tests, property-based tests, fuzzing, runtime assertions, canaries and production telemetry — become. citeturn20view1turn18view1

**Architecture is still poorly measured.** `[measured]` We can measure local redundancy and PR characteristics. We cannot yet reliably measure whether six months of locally correct agent changes have degraded conceptual integrity, introduced parallel abstractions, blurred ownership boundaries or made future changes harder. The 2026 redundancy result is an early proxy, not a complete architecture metric. citeturn17view0

**Long-horizon agent runs create an epistemic problem.** `[first-hand]` Practitioner guidance increasingly assumes humans will not read every generated line. `[measured]` Yet Stack Overflow respondents remain cautious about complex tasks, with only 16% rating AI performance on complex work “very well”; most users validate through execution and codebase context rather than trust alone. The unresolved question is how to know enough about a 10,000-line autonomous change to be accountable for it without manually reconstructing the entire trajectory. citeturn3view0turn14view1

**Provenance is not solved.** `[measured]` Repository mining shows agent activity is largely invisible if detection depends only on bot identities. `[first-hand]` LLVM therefore uses explicit disclosure/accountability rather than trying to infer authorship after the fact. citeturn19academia30turn21search9

**The commons problem is becoming real.** `[opinion]` Baltes, Cheong and Treude's 2026 *AI Slop and the Software Commons* argues that generation externalises costs onto reviewer capacity and community trust. That thesis is increasingly consistent with project policy: LLVM explicitly reasons in review-cost terms, and Google temporarily paused parts of its OSS vulnerability-reward intake on October 1 after a surge of automated invalid submissions was publicly reported. The latter is an incident concerning vulnerability reports rather than code PRs, but it demonstrates the same asymmetric economics: generation scales faster than expert verification. citeturn15search1turn21search9turn21news41

**Evidence grades used:** `[measured]`, `[first-hand]`, `[vendor]`, `[opinion]`.

## Segment comparison

| Dimension | Established companies | AI-forward companies | Open-source maintainers | Solo / small agent-first teams |
|---|---|---|---|---|
| **Review architecture** | `[first-hand]` Existing PR/CI/security stack plus AI generation/review; human sign-off usually retained. Google/GitHub exemplify this. citeturn10view1turn6view1 | `[first-hand]` More likely to use AI reviewer before human and multi-agent review. Anthropic is the strongest documented example. citeturn6view0 | `[first-hand]` Human-maintainer review remains central; some projects restrict or ban autonomous reviewers/contributors. LLVM explicitly bans unapproved autonomous participation. citeturn21search9 | `[first-hand]` Practitioners commonly use agents for generation plus first-pass review/triage, with the owner doing risk-focused final review. citeturn3view0 |
| **Gating order** | CI/type/lint/security → AI review where enabled → human approval/change management. | Agent tests → deterministic checks → one/multiple AI reviewers → human decision; potentially more autonomous for trivial work. | Contributor self-review → project CI → maintainer review; growing intolerance for review-externalising PRs. | Cheap checks first; AI reviewer; manual focus on risky regions. |
| **What humans read** | Security/business-critical/architecture paths; often ordinary PR review still required. | Increasingly sampled/risk-based rather than every line. | Frequently still the whole contribution, hence strong pressure to keep PRs small. | Usually tests, interfaces, stateful logic, security, migrations, unusual diffs. |
| **Metrics** | `[vendor]` Throughput, cycle time, review latency, incidents, churn. Faros provides telemetry but not independent causal evidence. citeturn4view0 | `[vendor]` Findings/review, reviewer coverage, review cost and time; Anthropic reports all four. citeturn6view0 | `[measured]` Merge/rejection, reviewer interaction, time-to-merge, CI outcome dominate research datasets. citeturn17view1turn16view2 | `[opinion]` Best metrics are human minutes, escaped defects/reverts, cost per accepted change, and PR-size distribution. |
| **AI provenance policy** | Inconsistent publicly; usually tool access/governance policies rather than commit-level labelling. | Often obvious operationally because agents are first-class participants; public disclosure practices vary. | Explicit policy emerging. LLVM requests disclosure of substantial generated content and accountable human authorship. citeturn21search9 | Easy to record run IDs/model/tool, but rarely externally required. |
| **PR size policy** | No universal AI-specific ceiling found. | Review depth increasingly scales with size/complexity. | Strong pressure toward small, understandable changes; LLVM explicitly invokes size/complexity in review-cost decisions. citeturn21search9 | `[opinion]` Small PRs are the cheapest practical safety mechanism. |
| **AI review tooling** | GitHub Copilot review, CodeRabbit, Greptile, conventional SAST/CodeQL and internal tools. | Multi-agent review systems, custom review agents, same deterministic tools underneath. | Bots tolerated selectively; some projects prohibit unsolicited AI comments. | Frontier coding agent plus a different reviewer model/tool is common practitioner practice. |
| **Auto-merge appetite** | Conservative outside low-risk domains. | Highest, especially where oracles are strong and changes reversible. | Generally lowest because reviewer/maintainer accountability is externalised. | Depends heavily on deployment reversibility and owner risk tolerance. |
| **Codebase-wide audit** | Mature traditional security/architecture tooling, but no public AI-specific standard. | More willingness to ask agents to sweep/refactor whole repos, but objective audit methodology remains immature. | Existing static analysis, test infrastructure, human subsystem ownership. | Often ad hoc; biggest opportunity for improvement. |
| **Best evidence on outcomes** | Weak public causal evidence; vendor telemetry dominates. | Detailed first-hand process, mostly vendor-produced performance numbers. | Strongest independent empirical dataset because GitHub activity is observable. | Rich anecdotes, weak population validity. |

The convergence is therefore real but bounded: `[opinion]` incumbents are adopting the **automation** of AI-forward teams with a lag, but many are not adopting their most aggressive **delegation of accountability**. Open source is diverging even further because reviewer time is an explicitly scarce commons.

## Notable changes during 2026

| Date | Development | Why it matters |
|---|---|---|
| **January 2, 2026** | `[measured]` *Early-Stage Prediction of Review Effort in AI-Generated Pull Requests* appears, based on 33,707 agent PRs. citeturn17view1 | Establishes the “cheap majority / expensive tail” model and shows review effort can be triaged before a human starts. |
| **January 21, 2026** | `[measured]` *Where Do AI Coding Agents Fail?* analyses roughly 33,000 agent PRs and manually classifies 600 failures. citeturn17view2 | Gives the field one of its first large empirical rejection taxonomies. |
| **January 29, 2026** | `[measured]` *More Code, Less Reuse* and testing-focused human/agent work appear. citeturn17view0turn18view1 | Moves debate beyond pass rate into redundancy, maintainability and test behaviour. |
| **February 27, 2026** | `[measured]` Study of 22,953 AI-assisted PRs finds novice contributors impose much higher reviewer load and lower acceptance. citeturn18view3 | Strong evidence that expertise remains economically important after code generation is automated. |
| **March 9, 2026** | `[vendor]` Anthropic launches/describes Code Review, a multi-agent reviewer used on nearly every internal Anthropic PR. citeturn6view0 | One of the clearest public examples of agents reviewing agent-written code at company scale. |
| **April 13–14, 2026** | `[measured]` MSR 2026 presents an unusually large cluster of studies on agent PR security, testing, CI, review, rejection, clones and post-merge quality. citeturn16view0turn20view1 | Marks the transition from anecdotal “vibe coding” debate to an empirical software-engineering research field. |
| **April 2026** | `[first-hand]` Google describes engineers orchestrating autonomous agent “task forces”; contemporaneous reporting says about 75% of new code is AI-generated and human-reviewed. citeturn10view1turn23news37 | Shows agentic coding is no longer confined to startups. |
| **May 7, 2026** | `[vendor]` GitHub publishes *Agent pull requests are everywhere. Here's how to review them.* citeturn6view1 | Mainstream platform guidance begins treating agent-specific failure modes — CI gaming, duplicate code, hallucinated correctness and prompt injection — as ordinary review concerns. |
| **May 21, 2026** | `[measured]` Peralta et al. show rejected PR ≠ failed agent: only 35.7% of rejected cases in their sample are clear agent failures. citeturn16view2 | Pushes teams away from simplistic merge-rate evaluation. |
| **June 11, 2026** | `[measured]` AIDev rejection study reports 46.41% of sampled fix PRs from Copilot, Devin, Cursor and Claude rejected, then qualitatively analyses 306 non-merges. citeturn19academia27 | Gives practical rejection causes including incorrect implementation and CI/test failure. |
| **June 15, 2026** | `[first-hand]` Addy Osmani publishes *Agentic Code Review*, advocating risk triage, deterministic gates and selective human attention. citeturn3view0 | Representative of the emerging practitioner consensus rather than a vendor-only workflow. |
| **June 23–August 5, 2026** | `[measured]` Stack Overflow fields its 2026 Developer Survey. citeturn14view2 | Captures broad developer behaviour after agent workflows became mainstream. |
| **Summer 2026** | `[first-hand]` Godot and Zig are publicly reported taking restrictive positions on AI-generated contributions, while other projects choose accountability/disclosure rather than bans. citeturn21news43turn21news44 | Open source splits over whether human responsibility is sufficient or AI contributions impose unacceptable review costs. |
| **September 2026** | `[first-hand]` Debian is reported adopting a permissive-but-accountable approach rather than a blanket AI ban. citeturn21news45 | Demonstrates there is no single open-source consensus. |
| **October 1, 2026** | `[first-hand]` Google pauses product submissions to its OSS Vulnerability Reward Program after reporting a major rise in invalid automated submissions. citeturn21news41 | A concrete example of verification capacity becoming the scarce resource. |
| **October 6, 2026** | `[measured]` Stack Overflow publishes its 2026 survey results: AI use is mainstream, but trust remains conditional and validation remains heavily human/tool mediated. citeturn13search3turn14view1 | Probably the best broad H2-2026 snapshot available as of this report's date. |

## What a small agent-first team should copy — and what to ignore

The evidence points toward a much more disciplined process than “have Claude write it, have another Claude review it”.

### Copy this

**Make deterministic gates sovereign.** `[opinion]` An agent should never be able to negotiate with the same test, coverage, security or CI requirement that judges its output. Changes to `.github/workflows`, test configuration, coverage thresholds, linters, compiler settings, security suppressions and test fixtures should automatically enter a higher review tier. This recommendation follows directly from GitHub's 2026 warning patterns and from the empirical importance of CI outcomes. citeturn6view1turn17view2

**Keep agent changes small enough that rejection is cheap.** `[measured]` Patch size and file type predict expensive review remarkably well; larger failed PRs are common, and inexperienced agent operators produce disproportionately larger review loads. Set your own threshold from data rather than copying an arbitrary 200/400/800-line number. citeturn17view1turn17view2turn18view3

**Require a human owner, not necessarily a human typist.** `[opinion]` The owner should be able to explain intent, invariants, failure modes and why the tests prove the desired behaviour. LLVM's model is a good one: the person who invokes the generator remains the author for accountability purposes. citeturn21search9

**Use a separate reviewer context from the implementation context.** `[opinion]` Let the coding agent self-check, but do not count that as independent review. Send the clean diff, requirements and relevant repository context to another reviewer instance — preferably a different model or at least a fresh trajectory — after deterministic tests. Anthropic's parallel review/verification architecture makes the same separation at larger scale, although its measured effectiveness claims remain vendor evidence. citeturn6view0

**Read tests before trusting implementation.** `[first-hand]` This is one of the better practitioner heuristics in 2026 because agents can generate implementation and confirming tests together. Verify the test's premise and, for a bug fix, ensure the regression test demonstrably fails against the previous revision. GitHub explicitly recommends this pattern. citeturn6view1

**Add repository-wide duplication and architecture checks to your normal QA rhythm.** `[measured]` Agent PRs measurably miss reuse opportunities. At minimum, periodically inspect clone growth, new utility/helper proliferation, dependency direction, dead interfaces and parallel abstractions. Do not wait for local PR review to reveal a global architectural trend. citeturn17view0

**Measure human verification cost, not agent throughput.** `[opinion]` The most informative number for your practice is probably `human verification minutes / accepted change`, segmented by risk and agent. Pair that with escaped defects/reverts and agent compute cost. The 2026 empirical literature repeatedly shows that generation volume can rise while review burden worsens. citeturn17view1turn18view3

**Keep a provenance ledger for runs that matter.** `[opinion]` Store task/run ID, model/tool, initiator, generated diff size, validation commands, independent reviewer, and merge owner. Repository mining shows that authorship cannot be reconstructed reliably from bot identities later. citeturn19academia30

**Create explicit trust tiers.** `[opinion]` A practical small-team scheme would be:

| Tier | Examples | Human treatment |
|---|---|---|
| Low risk | docs, generated snapshots, mechanical renames, isolated tests with strong oracle | AI review + deterministic green may be sufficient; sample periodically |
| Normal | ordinary feature/bug implementation | human reads intent, tests, API/data boundaries and AI-review findings; samples implementation |
| High risk | auth, permissions, money, persistence, migrations, concurrency, cryptography, deployment, dependency/security config | human reads line-by-line where feasible; independent tests/security checks; explicit approval |
| Meta-gating | CI, test harness, coverage, security rules, agent instructions/permissions | highest scrutiny because these changes alter how future agent work is judged |

This table is `[opinion]`, not a published industry standard, but it reflects the variables repeatedly identified in the 2026 evidence. citeturn3view0turn6view1turn17view1

### Ignore this

**Ignore “X% of our code is AI-written” as a quality metric.** `[opinion]` Google's reported ~75%, or any startup's 90–100%, tells you virtually nothing about escaped defects, architecture, review effort or cost per delivered outcome. citeturn23news37

**Ignore reviewer comment count as proof of review quality.** `[measured]` AI review agents can generate enormous quantities of low-signal feedback. A reviewer that posts eight comments is not necessarily better than one that posts one real defect. citeturn17view3

**Ignore green tests when the agent wrote or altered the oracle.** `[opinion]` Green only means what the test suite says it means. Review changed tests, fixtures and gating configuration as adversarially as production implementation.

**Ignore model-brand trust tiers unless your own data supports them.** `[measured]` Different agents show different merge/intervention patterns, but task, deployment mode and workflow explain much of the variation. The repository census also shows different agent products appearing in different kinds of work, making naive model-to-model production comparisons confounded. citeturn16view2turn19academia30

**Ignore the claim that humans must continue reading every generated line forever.** `[opinion]` That does not scale with the demonstrated change in generation throughput. The better target is strong independent oracles, small changes, explicit risk classification, architecture constraints and deep human inspection where the cost of being wrong warrants it.

**Also ignore the opposite claim that humans can stop understanding the codebase.** `[measured]` The clearest empirical signal points the other way: less experienced agent operators create materially more review overhead and have worse acceptance outcomes. Agents reduce implementation scarcity; they increase the relative value of specification, architecture, debugging and verification expertise. citeturn18view3

The core recalibration for an experienced agent-first developer is therefore not “become a faster human code reviewer”. `[opinion]` It is to become a **verification-system designer**: define what must be true, construct independent oracles, constrain blast radius, preserve architecture, route attention by risk, and maintain enough codebase understanding to recognise when every local check is green but the system is drifting.

## Full source list

**Addy Osmani.** “Agentic Code Review.” June 15, 2026. Practitioner account and synthesis.  
URL: `https://addyosmani.com/blog/agentic-code-review/` citeturn3view0turn15search31

**Anthropic.** “Bringing Code Review to Claude Code.” March 9, 2026. First-hand internal workflow plus vendor-reported product metrics.  
URL: `https://claude.com/resources/articles/code-review` citeturn6view0

**Andrea Griffiths / GitHub.** “Agent pull requests are everywhere. Here’s how to review them.” May 7, 2026. Vendor engineering guidance.  
URL: `https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/` citeturn6view1

**Faros AI.** “AI Engineering Report 2026: The Acceleration Whiplash” / report summary. 2026. Vendor telemetry covering approximately 22,000 developers and 4,000 teams.  
URL: `https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways` citeturn4view0

**Stack Overflow.** “2026 Developer Survey — AI.” Published October 6, 2026; survey fielded June 23–August 5, 2026.  
URL: `https://survey.stackoverflow.co/2026/ai` citeturn14view0

**Stack Overflow.** “2026 Developer Survey — AI data.” Detailed response distributions.  
URL: `https://survey.stackoverflow.co/2026/ai/data` citeturn14view1

**Stack Overflow.** “2026 Developer Survey — Methodology.” 30,903 valid responses from 169 countries.  
URL: `https://survey.stackoverflow.co/2026/methodology` citeturn14view2

**Stack Overflow.** “The results of the 2026 Developer Survey are here.” October 6, 2026.  
URL: `https://stackoverflow.blog/2026/10/06/the-results-of-the-2026-developer-survey-are-here/` citeturn13search3

**Dao Sy Duy Minh et al.** “Early-Stage Prediction of Review Effort in AI-Generated Pull Requests.” Submitted January 2, revised January 27, 2026; accepted MSR 2026. 33,707 agent PRs.  
URL: `https://arxiv.org/abs/2601.00753` citeturn17view1

**Ramtin Ehsani et al.** “Where Do AI Coding Agents Fail? An Empirical Study of Failed Agentic Pull Requests in GitHub.” January 21, 2026; MSR 2026.  
URL: `https://arxiv.org/abs/2601.15195` citeturn17view2

**Haoming Huang et al.** “More Code, Less Reuse: Investigating Code Quality and Reviewer Sentiment towards AI-generated Pull Requests.” January 29, 2026; accepted MSR 2026.  
URL: `https://arxiv.org/abs/2601.21276` citeturn17view0

**Roberto Milanese et al.** “Human-Agent versus Human Pull Requests: A Testing-Focused Characterization and Comparison.” January 29, 2026. 6,582 human-agent and 3,122 human PRs.  
URL: `https://arxiv.org/abs/2601.21194` citeturn18view1

**Sabrina Haque, Sarvesh Ingale and Christoph Csallner.** “Do Autonomous Agents Contribute Test Code? A Study of Tests in Agentic Pull Requests.” January 7, 2026.  
URL: `https://arxiv.org/abs/2601.03556` citeturn18view0

**Syed Ammar Asdaque et al.** “Novice Developers Produce Larger Review Overhead for Project Maintainers while Vibe Coding.” February 27, 2026; MSR 2026. 22,953 PRs from 1,719 contributors.  
URL: `https://arxiv.org/abs/2602.23905` citeturn18view3

**Kowshik Chowdhury et al.** “From Industry Claims to Empirical Reality: An Empirical Study of Code Review Agents in Pull Requests.” April 3, 2026; accepted MSR 2026.  
URL: `https://arxiv.org/abs/2604.03196` citeturn17view3

**Sien Reeve O. Peralta et al.** “Why Are Agentic Pull Requests Merged or Rejected? An Empirical Study.” May 21, 2026; accepted MSR 2026.  
URL: `https://arxiv.org/abs/2605.22534` citeturn16view2

**Mahmoud Abujadallah, Ali Arabat and Mohammed Sayagh.** “Understanding the Rejection of Fixes Generated by Agentic Pull Requests — Insights from the AIDev Dataset.” June 11, 2026.  
URL: `https://arxiv.org/abs/2606.13468` citeturn19academia27

**Taher A. Ghaleb.** “When AI Agents Touch CI/CD Configurations: Frequency and Success.” January 24, 2026. 8,031 agentic PRs and 99,930 workflow runs.  
URL: `https://arxiv.org/abs/2601.17413` citeturn19academia28

**Esteban Dectot-Le Monnier de Gouville, Mohammad Hamdaqa and Moataz Chouchen.** “When AI Writes Code: Investigating Security Issues in Agentic Software Changes.” MSR 2026, April 13–14, 2026. 7,200 agent PRs, 6,620 human PRs, four SAST engines.  
URL: `https://2026.msrconf.org/details/msr-2026-mining-challenge/24/When-AI-Writes-Code-Investigating-Security-Issues-in-Agentic-Software-Changes` citeturn20view1

**MSR 2026.** Conference programme / Mining Challenge programme. April 13–14, 2026. Useful index of the unusually broad 2026 empirical literature on agentic software engineering.  
URL: `https://2026.msrconf.org/program/program-msr-2026/` citeturn16view0

**Arsham Khosravani and Audris Mockus.** “Detecting AI Coding Agents in Open Source: A Validated Multi-Method Census of 180 Million Repositories.” June 23, 2026.  
URL: `https://arxiv.org/abs/2606.24429` citeturn19academia30

**Sebastian Baltes, Marc Cheong and Christoph Treude.** “AI Slop and the Software Commons.” April 17, 2026. Conceptual/practitioner-evidence paper on review externalities.  
URL: `https://arxiv.org/abs/2604.16754` citeturn15search1turn15search5

**LLVM Project.** “LLVM AI Tool Use Policy.” Current policy accessed October 6, 2026; page does not expose a reliable publication date in the retrieved material.  
URL: `https://llvm.org/docs/AIToolPolicy.html` citeturn21search9

**LLVM Project.** “LLVM Developer Policy.” Current policy, including code-review responsibilities and pointer to the AI contribution policy.  
URL: `https://llvm.org/docs/DeveloperPolicy.html` citeturn21search16

**Google / Alphabet, Sundar Pichai.** “Alphabet earnings, Q1 2026 — CEO remarks.” April 29, 2026. First-hand statement on agentic coding and autonomous engineering task forces.  
URL: `https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q1-2026/` citeturn10view1

**Business Insider.** “Google says 75% of the company's new code is AI-generated.” April 2026. Secondary reporting of Google's internal generation/review figure; used cautiously rather than as independent outcome evidence. citeturn23news37

**NIST, Booth et al.** “Secure Software Development Practices for Generative AI and Dual-Use Foundation Models: An SSDF Community Profile,” NIST SP 800-218A. July 26, 2024. Baseline rather than 2026-specific AI-written-code guidance.  
URL: `https://www.nist.gov/publications/secure-software-development-practices-generative-ai-and-dual-use-foundation-models-ssdf` citeturn22search0

**NIST.** “Secure Software Development Framework.” Current SSDF programme page.  
URL: `https://csrc.nist.gov/projects/ssdf` citeturn22search4

**NIST.** “Draft SSDF 1.2 Available for Comment.” December 17, 2025. Useful baseline for the assurance regime entering 2026.  
URL: `https://csrc.nist.gov/News/2025/draft-ssdf-version-1-2` citeturn22search18

**U.S. FDA.** “Recognized Consensus Standards: Medical Devices.” Current catalogue, including IEC 62304 and ISO 14971.  
URL: `https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfStandards/` citeturn22search1turn22search5

**PC Gamer.** Report on Godot's 2026 AI-authored-contribution policy change. Secondary source quoting project rationale; not used as outcome evidence.  
URL: `https://www.pcgamer.com/gaming-industry/open-source-game-engine-godot-will-no-longer-accept-ai-authored-code-contributions-we-cant-trust-heavy-users-of-ai-to-understand-their-code-enough-to-fix-it/` citeturn21news44

**Business Insider.** Report on Zig president Andrew Kelley's prohibition on AI-assisted code contributions, May 2026. Secondary policy evidence.  
URL: `https://www.businessinsider.com/zig-programming-language-ai-rules-2026-5` citeturn21news43

**The Verge.** Report on Debian's 2026 generative-AI contribution policy. Secondary policy evidence.  
URL: `https://www.theverge.com/tech/986789/linux-debian-generative-ai-policy` citeturn21news45

**ITPro.** “Google pauses open source bug bounty scheme over AI slop submissions.” October 5, 2026. Secondary report on the October 1 OSS VRP suspension; relevant as evidence of review/verification overload rather than code quality itself. citeturn21news41