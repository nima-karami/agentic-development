# Deciding Like a Principal Engineer: Judgment, Reversibility, and Process Proportional to Stakes

The right frame is **calibrated judgment, organised by a small number of classification questions**: how much is at stake, how hard the choice is to reverse, and how uncertain the situation is. A "framework" is the wrong unit. The evidence says expert intuition is reliable only in regular environments that give fast feedback (Kahneman & Klein, 2009). It also says decision *process* matters more to outcomes than decision *analysis* (Lovallo & Sibony, McKinsey, 2010). So elite decision-makers don't pick a framework and run it. They classify the decision, spend process in proportion to stakes and irreversibility, and use specific tools (pre-mortem, ADR, quality-attribute scenarios) only when the class calls for them.

## TL;DR
- **Judgment, structured by triage.** The core skill is spotting the two or three forces that dominate, pricing reversibility, and stopping analysis when more information won't change the choice. Frameworks are tools that judgment picks up; they don't replace it. Intuition can be trusted only where feedback is fast and the domain is regular, such as code review or debugging. It can't be trusted for rare, high-stakes choices like a platform migration or a vendor lock-in, where you need structure and outside views.
- **Classify first, then size the process.** Score every decision on reversibility, blast radius and uncertainty. Most decisions, which Bezos called "two-way doors," should be made fast by one owner and recorded in a line or two. Only one-way, high-blast-radius decisions earn RFCs, options analysis, pre-mortems and named decision rights.
- **Agents should decide reversible, local, convention-following choices alone.** They should *recommend* (options plus a pick) when a choice is costly to reverse or crosses a module or team boundary. They should *escalate* anything irreversible, anything that touches security, data, money or public contracts, or anything that conflicts with an existing ADR. LLMs are overconfident, sycophantic and biased toward popular stacks, and they don't self-correct without external feedback. So the controls that work are external: forced alternatives, explicit criteria, tests and tools as verifiers, and escalation rules.

## Key Findings

### 1. What the skill actually is
- **Intuition is valid only under specific conditions.** Kahneman & Klein (2009, *American Psychologist* 64(6)) concluded that skilled intuition needs "an environment that is sufficiently regular to be predictable" and "an opportunity to learn these regularities through prolonged practice." Confidence on its own is not evidence that an intuition is valid.
  - **In engineering:** a principal engineer's gut on code smells, API ergonomics or a flaky test is earned, because thousands of fast feedback loops trained it. Their gut on a three-year platform bet is not, because they've seen perhaps five such bets, each with years-long feedback delays.
- **Experts recognise rather than compare.** Gary Klein's Recognition-Primed Decision model (*Sources of Power*, 1998) found that experienced fireground commanders mostly don't weigh options side by side. They recognise the situation as a type, mentally simulate one course of action, and adopt it if it works.
  - **What separates elite from competent** is the size and accuracy of the pattern library, plus knowing when a situation is *not* a familiar pattern.
- **Process beats analysis.** Lovallo & Sibony ("The case for behavioral strategy," *McKinsey Quarterly*, 2010) studied 1,048 business decisions. They found the quality of the decision process (debate, surfacing dissent, considering alternatives) explained about six times more of the variance in ROI than the quantity of analysis did.
  - This is the strongest evidence that "how you decide" beats "how much you model."
- **Calibration is a measurable skill.** Tetlock's Good Judgment Project (*Superforecasting*, 2015) showed that forecasting accuracy, measured by Brier scores, is trainable. The best forecasters broke problems into parts, started from base rates (the outside view), and updated in small steps.
  - The transferable lesson for engineers: estimate with reference classes, state probabilities, and score yourself afterwards.
- **Judge decisions, not outcomes.** Annie Duke (*Thinking in Bets*, 2018) calls the error of judging a decision by how it turned out "resulting." A good process can produce a bad outcome. Reviews should ask whether the decision was sound given the information available at the time.
- **Satisficing is rational, not lazy.** Herbert Simon (1956) showed that bounded agents rationally pick the first option that clears an aspiration level. Gigerenzer's work on fast-and-frugal heuristics shows that simple rules can match or beat complex models in uncertain environments.
  - **For engineers:** set the acceptance bar first, then stop searching when an option clears it.

**Synthesis:** an elite engineering decision-maker (a) classifies the decision, (b) uses earned intuition where the domain is regular, (c) switches to the outside view and structure where it is not, (d) runs a process that surfaces dissent, and (e) records reasoning so they can calibrate later. Most of what the industry calls "frameworks" are aids for steps (b) to (e).

### 2. The decision playbook: classify, then size the process

Ask four questions about every decision.

| Axis | Low | High |
|---|---|---|
| **Reversibility**: the cost and time to undo | Revert a PR, flip a flag, swap a library behind an interface | Data model or schema in production, public API, vendor contract, language or framework, org-wide standard |
| **Blast radius**: who is affected | One file, module or team | Many teams, customers, security, compliance, money |
| **Uncertainty** (Cynefin-style) | Clear or complicated: known answer, or answerable by expertise | Complex: only discoverable by probing. Chaotic: act first |
| **Cost of delay**: what waiting costs | Little; nothing is blocked | A team is blocked, a market window or incident is live |

**Tiers and the process each gets:**

| Tier | Definition | Who decides | Process | Time-box | Record |
|---|---|---|---|---|---|
| **T0 Routine** | Reversible and local, with existing conventions | The implementer or agent | Follow the convention; no deliberation | Minutes | Commit message or PR description |
| **T1 Reversible, notable** | Reversible but visible, e.g. a new dependency, a module boundary, a UI pattern | Owner, after a quick check with a peer | 2–3 options and one stated criterion; pick and move | Up to 1 day | A short ADR or a "Decision:" line in the PR |
| **T2 Costly to reverse** | Weeks to undo, or cross-team: state library, API shape, database choice, service split | A named owner (the "D") with input from the people affected | A design doc or RFC with options, criteria, a 15-minute pre-mortem, and a written comment window | 1–2 weeks | A full ADR (context, options, decision, consequences, revisit trigger) |
| **T3 One-way door** | Months to undo, org-wide or contractual: vendor lock-in, rewrite, platform bet, data residency | Exec or architecture group with clear decision rights (RAPID or DACI) | Narrative doc, quality-attribute trade-off analysis, reference-class estimate, pre-mortem, staged commitment or real-option design | 2–6 weeks, but always time-boxed | ADR plus RFC, with review dates and kill criteria |

**Rules that make the table work:**
1. **Default down a tier.** Bezos's 2015 shareholder letter warns that large organisations tend to apply the slow "Type 1" process to reversible "Type 2" decisions, causing "slowness, unthoughtful risk aversion, failure to experiment sufficiently."
2. **Convert one-way doors into two-way doors where you can.** This is often the highest-leverage move available. Examples: put the vendor behind an adapter, run dual-writes before the migration, ship behind a flag, or start with a strangler fig rather than a rewrite.
3. **Stop when the information stops changing the answer.** Bezos's 2016 letter suggests most decisions should be made with about 70% of the information you wish you had. Treat this as a heuristic, not an evidence-backed threshold.
   - A practical stopping rule: if no plausible new fact would flip the choice, decide now.
4. **Disagree and commit.** Bezos (2016) describes this as a way to avoid stalls once the debate has been heard. It works only when the decision rights are clear.
5. **Set a revisit trigger, not a vague "we'll see."** Write down the observable condition that would reopen the decision, such as "p95 latency over 300 ms" or "a third team needs it."

**Control flow for T2 and T3 decisions:**
1. **Frame.** State the problem, the decision being made, what is *not* being decided, the owner and the deadline.
2. **Generate options.** Require at least three, one of which is "do nothing or defer." Single-option proposals are the most common failure in both humans and agents.
3. **Set criteria.** Choose 3–5 quality attributes or forces, ranked, and write them down before evaluating options to prevent post-hoc rationalisation.
4. **Gather evidence.** Use a spike or prototype for complex uncertainty, a benchmark for complicated questions, and a reference class for cost and schedule.
5. **Run a pre-mortem.** Assume the decision failed 18 months from now, then ask why.
6. **Commit.** The owner decides, and dissent is recorded.
7. **Record.** Write the ADR.
8. **Review.** Check at the revisit trigger, and judge the process, not the outcome.

### 3. Framework table

Evidence ratings: **E** means empirical support, **P** means practitioner-validated with widespread, documented use, and **F** means famous but with little rigorous evidence.

| Framework | Question it answers | Best fit | Misuse / when it misleads | Cost | Evidence |
|---|---|---|---|---|---|
| **One-way vs two-way doors** (Bezos, 2015 letter) | How much care does this deserve? | Triage of every decision | Treating "reversible in theory" as cheap to reverse; ignoring how cost accumulates while you wait to reverse | Seconds | P |
| **Cynefin** (Snowden & Boone, HBR 2007) | Is this knowable by analysis, or only by probing? | Choosing analysis versus experiment; incident versus design mode | Endless debate about which domain you're in; using it as a taxonomy rather than as a prompt to act | Minutes | F/P: conceptual, little outcome evidence |
| **Cost of delay / CD3** (Reinertsen, *Principles of Product Development Flow*, 2009) | What does waiting cost per week? What order should work go in? | Sequencing work, tech-debt versus feature priority | False precision in dollar estimates; still useful when the estimates are rough | Hours | P, grounded in queueing theory |
| **WSJF** (SAFe's packaging of CD3) | Which item first? | Backlog ordering at portfolio level | Relative-point scoring of fuzzy components can be gamed and gives an illusion of rigour; critics note that its proxy for job size distorts the ratio | Hours per cycle | F |
| **Real options** (Baldwin & Clark, *Design Rules*, 2000; Sullivan et al., 2001) | What is it worth to keep a choice open, and what does that cost? | Modularity, abstraction layers, staged bets, "Tidy First?"-style investment (Beck, 2023) | Paying for options you'll never exercise, i.e. speculative generality and over-abstraction | Low as a mental model; high if modelled formally | P, with theoretical backing |
| **ATAM / quality-attribute scenarios** (Kazman, Klein & Clements, SEI, 2000) | Which architectural choices create sensitivity and trade-off points across quality attributes? | T3 architecture: availability versus latency versus cost versus modifiability | Running the full multi-day ceremony for a medium decision; the lightweight utility-tree scenarios carry most of the value | Full ATAM takes days and many stakeholders; scenarios alone take hours | P, with SEI case studies |
| **Wardley mapping** (Simon Wardley) | Where is each component on the evolution path from genesis to commodity? Build or buy? | Platform strategy, build versus buy, deciding what to commoditise | Maps that look rigorous but encode opinion; high learning cost; little outcome evidence | Days to learn, hours per map | F |
| **Build / buy / adopt-OSS** | Who should own this capability? | Any non-differentiating capability | Comparing build cost against licence cost while ignoring run cost, migration, lock-in and opportunity cost | Hours to days | P |
| **Pre-mortem** (Klein, HBR 2007) | How will this fail? | Every T2 and T3 decision | Becoming a ritual with no owner for the mitigations | 15–45 minutes | E: prospective hindsight (Mitchell, Russo & Pennington, 1989) |
| **Expected value / decision trees** | Which option has the best probability-weighted payoff? | Repeated bets, A/B decisions, incident-risk trade-offs | Fat-tailed outcomes where the mean misleads; made-up probabilities. Flyvbjerg's IT-project data shows heavy tails, so guard the downside, not just the mean | Hours | E for the method; inputs are often weak |
| **Reference-class forecasting** (Flyvbjerg; Kahneman's "outside view") | How long and how much, according to similar past projects? | Rewrites, migrations, platform builds | A reference class that is too narrow ("our case is special") | Hours | E |
| **Satisficing** (Simon, 1956) | When do I stop searching? | T0–T1 decisions, and library choice among adequate options | Applying it to one-way doors where the tail risk is large | Seconds | E |
| **RFC / design-doc process** (Rust RFCs, Python PEPs, Google design docs, Oxide RFDs) | How do we get the best input and a durable record before committing? | T2–T3 decisions and cross-team decisions | Using RFCs as approval gates or popularity contests; long-open RFCs causing paralysis; reviewer fatigue | Days of author time plus reviewer time | P |
| **ADR** (Nygard, 2011) | Why did we do this? | Every T1+ architectural decision; the cheapest durable memory | Writing ADRs after the fact as justification; never superseding outdated ones | 15–60 minutes | P |
| **RAPID** (Rogers & Blenko, "Who Has the D?", HBR 2006) / **DACI** (Intuit, popularised by Atlassian) | Who decides, who must agree, who is consulted? | Cross-team or exec decisions where ownership is ambiguous | Over-assigning "Agree" roles, which recreates consensus veto; running it for team-local decisions | 15 minutes | F/P: Bain cites correlations from its own surveys |
| **Kahneman, Lovallo & Sibony 12-question checklist** (HBR 2011, "Before You Make That Big Decision") | Is this recommendation contaminated by bias? | Reviewing a T3 proposal someone else wrote | Box-ticking | 30 minutes | E-adjacent, grounded in the bias literature |

### 4. Trade-off reasoning: heuristics that transfer

There is no general algorithm for trade-offs, but there *is* a general method: **name the forces, rank them for this context, find the cheapest option that satisfies the top-ranked force, and buy optionality on the rest.** The domain-specific part is knowing which forces exist. ATAM's quality-attribute scenarios are the most rigorous general way to surface them.

The heuristics below transfer across domains.

1. **Reversibility first.** When two options look equal, pick the one that is easier to undo.
   - *Example:* choose a managed Postgres you could self-host later over a proprietary serverless database with a non-standard query language.
2. **Rank the forces explicitly; "both" is not an answer.** CAP forces a choice only during a partition. Abadi's PACELC (2012) adds the everyday trade-off: *else*, latency versus consistency.
   - *Example:* a shopping cart chooses availability and latency, while a payment ledger chooses consistency. Write the ranking down per subsystem, not per company.
3. **Speed versus quality is mostly a false dichotomy at the system level.** DORA research (*Accelerate*, Forsgren, Humble & Kim, 2018) found that high performers achieve higher throughput *and* stability together.
   - The real trade-off is local, e.g. shipping without tests today. Its cost shows up as reduced deployment frequency later.
   - *Example:* invest in CI speed and feature flags rather than in more manual QA gates.
4. **Simplicity until the second (or third) concrete need.** Wait for real duplication before abstracting. Gall's law (*Systemantics*, 1975): complex systems that work evolved from simple systems that worked.
   - *Example:* don't build a design-system theming engine until a second brand actually exists.
5. **Price build cost and run cost over the full lifetime.** Most of a system's cost is maintenance and operation. Estimate cost per year over three years, including on-call and upgrades.
   - *Example:* a self-hosted search cluster is "free" next to an Algolia invoice until you add a share of an SRE's time.
6. **Local optimum versus org coherence: default to the paved road, and require a written justification to leave it.** McKinley's "Choose Boring Technology" (2015) gives each team a few "innovation tokens."
   - *Example:* a team wants a new frontend framework. Allow it only if it's spent as the team's innovation token *and* the team owns the support burden.
7. **Now versus later: discount the future honestly, but weight irreversible harm heavily.** Use cost of delay for "now." For "later," ask what it costs to defer this decision until you know more, which is real-options thinking.
   - *Example:* defer the microservices split; make module boundaries clean now, because that's the cheap option.
8. **Guard the tail, not just the mean.** Flyvbjerg & Budzier (HBR, 2011) found that IT projects have fat-tailed cost overruns.
   - *Example:* for a rewrite, plan for the 80th-percentile outcome of the reference class, not the median estimate.
9. **Coupling is the hidden currency.** Ousterhout (*A Philosophy of Software Design*) and Beck (*Tidy First?*) both frame design cost in terms of how much change propagates.
   - *Example:* when torn between two options, pick the one that keeps fewer modules needing to change together.
10. **Hyrum's law: every observable behaviour becomes a contract.** Treat anything public as a one-way door.
    - *Example:* adding a field to a public API response is cheap; removing it later is not.

### 5. Recurring CTO decisions: what good practice looks like

| Decision | Good practice | Key source or heuristic |
|---|---|---|
| **Technology and vendor selection** | Start from the paved road. Score 3+ options against pre-ranked criteria (fit, operability, team skill, ecosystem health, exit cost). Run a time-boxed spike on the riskiest criterion. Write the exit plan before signing. | McKinley, "Choose Boring Technology"; ADR |
| **Monolith vs services** | Default to a modular monolith. Split along team boundaries when deploy coupling or team contention (not traffic) becomes the bottleneck. | Fowler, "MonolithFirst" (2015); Conway's law; Skelton & Pais, *Team Topologies* (2019) |
| **Rewrite vs refactor** | Strongly prefer incremental replacement (strangler fig). A full rewrite needs a reference-class estimate, a frozen or dual-maintained old system, and kill criteria. | Spolsky, "Things You Should Never Do, Part I" (2000, on Netscape); Fowler, "StranglerFigApplication" |
| **Build vs buy** | Build only what differentiates. Buy or adopt commodity capabilities (Wardley's evolution axis is a useful lens here). Count integration, lock-in and run cost. | Wardley mapping; lifetime cost of ownership |
| **When to pay down tech debt** | Treat debt as interest: pay it where change frequency × pain is highest (hotspots), not where code is ugliest. Use cost of delay to compete it fairly against features. Distinguish prudent and deliberate debt from reckless debt. | Cunningham (1992), the debt metaphor; Fowler's Technical Debt Quadrant; Tornhill, *Your Code as a Crime Scene* |
| **Platform investment** | Build a platform when 3+ teams are solving the same problem. Treat it as a product with internal customers and adoption metrics, and make it optional-but-better rather than mandated. | *Team Topologies*, platform teams; Larson, *An Elegant Puzzle* |
| **Standardisation vs autonomy** | Standardise interfaces, observability, security and deploy paths. Leave implementation choices to teams. Provide an exception process via ADR. | Paved road plus innovation tokens |
| **Staffing a bet** | Fund in stages, with explicit milestones that buy information (real options). Staff with a small senior team first. Write kill criteria before you start. | Real options; reference-class forecasting |

### 6. Failure modes catalog

| Failure mode | How it shows up | Detection signal | Antidote |
|---|---|---|---|
| **Resume-driven development / novelty bias** | A new framework is proposed for a solved problem | The justification is "modern" or "industry is moving to"; no ranked criteria; the proposer leaves before the payoff | Innovation-token budget; require an exit-cost estimate and a named long-term owner |
| **Sunk cost / escalation of commitment** | "We've spent 9 months on this migration, we can't stop" | Arguments cite past spend, not future value; milestones slip without re-evaluation | Pre-committed kill criteria; ask "if we were starting today, would we fund this?" (Staw, 1976; Arkes & Blumer, 1985) |
| **Analysis paralysis** | RFC open for weeks, endless options | No owner or deadline; new comments don't change the ranking | Time-box by tier; a named "D"; the "would any plausible fact flip this?" stopping rule |
| **HiPPO (highest-paid person's opinion)** | The senior person speaks first, and debate ends | Dissent appears only in private | Written pre-reads (Amazon-style narrative memos); collect independent views before discussion; senior person speaks last |
| **Premature optimisation** | Caching layer, sharding or a micro-frontend before load exists | No measurement; the optimisation targets an imagined scale | Knuth (1974): measure first; set a performance budget and act when it's breached |
| **Cargo-culting big-tech practice** | Kubernetes, microservices or the "Spotify model" at 10 engineers | "Google does it"; the practice solves a problem you don't have | Ask what problem it solved for them and whether you have it. Jeremiah Lee's account of the Spotify model's limits (2020) is a cautionary example |
| **Single-option proposals** | The doc describes one solution in detail | No alternatives section, or a straw-man alternative | Require 3 options including "do nothing" |
| **Resulting** | Good decisions punished after bad luck, or vice versa | Reviews discuss outcomes only | Review against the ADR's information-at-the-time (Duke) |
| **Planning fallacy** | Rewrite estimated at 6 months | Inside-view bottom-up estimate only | Reference-class forecast; plan for P80 |
| **Heavyweight approval as a safety theatre** | Change advisory boards for every deploy | Lead time grows, but stability doesn't improve | *Accelerate* found external change approval correlated with worse delivery performance and no better stability; use peer review and automation instead |
| **Consensus veto** | Everyone is "Agree" in RAPID | Decisions stall on one holdout | Few Agree roles; disagree-and-commit |

### 7. Agents as decision-makers

**How LLM agents fail, with evidence:**
- **Overconfidence.** Kadavath et al. (2022, arXiv:2207.05221) found models "mostly" calibrated on multiple-choice formats, but calibration degrades in free-form and out-of-distribution settings, which is where engineering decisions live.
  - Xiong et al. (2023, arXiv:2306.13063) found that confidence stated in words is systematically overconfident, clustering at 80–100%.
  - Spiess et al. (2024, arXiv:2402.02047) found code models poorly calibrated about the correctness of their own code.
- **Sycophancy.** Sharma et al. (Anthropic, 2023, arXiv:2310.13548) found that state-of-the-art assistants "consistently exhibit sycophancy." An agent will tend to ratify the user's preferred option rather than challenge it.
- **Popularity bias.** Twist et al. (2025, arXiv:2503.17181, "LLMs Love Python") report that LLMs heavily default to Python and to well-established libraries even where those are a poor fit, and sometimes contradict their own recommendations.
- **Hallucinated dependencies.** Spracklen et al. (2024, arXiv:2406.10279) found about 19.7% of LLM-recommended packages didn't exist. This is a dependency-decision failure with supply-chain consequences.
- **No self-correction without external signal.** Huang et al. (2023, arXiv:2310.01798): "LLMs struggle to self-correct their responses without external feedback." Kamoi et al.'s 2024 survey reaches the same conclusion: self-correction works when tests, compilers or tools provide feedback.
- **Rarely asking.** HumanEvalComm (Wu & Fard, 2024, arXiv:2406.00215) found LLMs seldom ask clarifying questions on ambiguous requirements. ClarifyGPT (Mu et al., 2023) showed that detecting ambiguity and asking improves code correctness.
- **Over-engineering** is widely reported by practitioners but, as far as I found, not well quantified. Treat it as a plausible pattern, not an established finding.

**What helps:**
- **Forced alternatives and pre-stated criteria.** These counter single-option anchoring and popularity bias.
- **External verifiers rather than self-critique.** Use tests, type checks, benchmarks and package-registry lookups. Reflexion (Shinn et al., 2023) gains came from execution feedback.
- **Adversarial review by a separate instance.** Multiagent debate (Du et al., 2023, arXiv:2305.14325) improved reasoning and factuality. A reviewer agent prompted to argue against the proposal is a cheap approximation.
- **Reversibility tags and escalation rules.** These turn the human playbook into machine-checkable gates.

**Decide / Recommend / Escalate rules for an agent:**

*DECIDE alone (T0, and most T1) only if all of these hold:*
- the change is reversible by revert or flag;
- it is confined to the current task's module;
- it follows an existing convention or ADR;
- it adds no new runtime dependency;
- a test or tool can verify it.

*RECOMMEND (present 2–3 options, criteria, a pick and a confidence rating, then proceed only on approval or in a clearly marked reversible way) if any of these hold:*
- it adds a dependency (verify the package exists and is maintained);
- it introduces a new pattern or abstraction;
- it changes a module or public component API;
- it's an estimated multi-day effort to undo;
- the agent's choice differs from the user's stated preference (counter-sycophancy rule);
- it defaults to "the popular option" without a stated criterion.

*ESCALATE (stop and ask) if any of these hold:*
- it is irreversible or touches data: schema migrations on production data, deletes, data-format changes;
- it touches security, auth, secrets, privacy, payments or licensing;
- it affects a public or external contract;
- it conflicts with an existing ADR or standard;
- the requirements are ambiguous and two readings lead to different designs;
- the agent has failed verification twice;
- it introduces a new language, framework, datastore or vendor;
- its scope is larger than the task as specified.

**Minimum decision record** (for T1+, appended to the PR or ADR):
```
Decision: <one line>
Tier: T0/T1/T2/T3   Reversibility: easy | costly (<est. effort to undo>) | one-way
Context: <the force that made this a decision>
Options considered: <A, B, C incl. do-nothing>
Criteria (ranked): <1..3>
Chosen + why: <one or two sentences tied to criteria>
Confidence: low/med/high + what would change my mind
Verification: <tests/benchmarks/registry check run>
Revisit trigger: <observable condition>
Decided by: agent | human:<name>
```

## Recommendations
1. **Build one triage skill first.** It should classify reversibility, blast radius, uncertainty and cost of delay, output a tier, and route to the process for that tier. Every other skill hangs off this one.
2. **Make the T1+ template mandatory for agents.** That means three options, ranked criteria, a reversibility tag and a revisit trigger. It costs a few hundred tokens and directly targets the documented failure modes.
3. **Use verification over introspection.** Wire tests, type checks, a dependency-existence check and benchmarks into the decision loop. Don't rely on "review your answer."
4. **Add a separate adversarial-review step for T2+ decisions** using a fresh context prompted to find the strongest reason the proposal fails, which is a pre-mortem.
5. **Encode your org's paved road as ADRs the agent reads first.** Most good agent decisions are just "follow the existing decision"; deviations become recommendations.
6. **For yourself:** keep a decision journal with predictions and confidence ratings, and review it quarterly. That is the only way to build calibrated intuition for rare, high-stakes decisions.

## Caveats
- **Verification gap.** Live web search wasn't available during this research. Citations are from established literature and were cross-checked by a second research pass, but not re-fetched. Check exact quotes and figures against the originals before republishing, in particular the Twist et al. percentages, the Lovallo & Sibony "six times" figure, and the exact *Accelerate* wording on change approval.
- **Evidence quality varies.** Kahneman & Klein, Tetlock, pre-mortem/prospective hindsight, reference-class forecasting and DORA have empirical bases. Cynefin, WSJF, Wardley mapping and RAPID/DACI are widely used but have little rigorous outcome evidence. Bezos's 70% rule is an opinion in a shareholder letter.
- **The agent findings move fast.** Most LLM studies used 2023–2025 models, so calibration and sycophancy may differ in current models. The structural controls (external verification, escalation rules) are robust regardless.
- **Tier boundaries are judgment calls.** Expect to tune thresholds such as "multi-day to undo" for your codebase and team.