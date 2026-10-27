# Design Exploration, System Design and Architecture Skills: What Is Actually Proven (checked October 27, 2026)

No third-party skill for these three stages has design-quality evidence above P2, and none has any for architecture critique precision. Lift techniques and benchmarks rather than adopting any pack whole.

## TL;DR
- **Design exploration:** nothing proven. The best technique sources are Superpowers `brainstorming` (P1 for process cost and compliance only, measured by the author with a public harness) and Anthropic `frontend-design` (P4, vendor before/after screenshots). Adapt the "2–3 approaches, human picks, design doc" gate. Measure visual quality yourself with UI-Bench or Design2Code-style pairwise human preference.
- **System and architecture design:** Spec Kit `/plan` and BMAD `create-architecture` reach P2, but only end to end. In one independent 50-ticket benchmark, spec arms merged 40–42 tickets against 36 for no spec. No evaluation isolates the design artifact. On R2ABench, a MetaGPT-style architect→reviewer→refiner pipeline gave no consistent gain over direct prompting.
- **Architecture review and over-engineering:** no candidate publishes precision or acceptance rates for architecture critique. Lift Spec Kit's Simplicity/Anti-Abstraction gates with Complexity Tracking (P5 on their own effect), a severity-scaled ATAM risk pass (P1, small study), and a "cite a requirement ID per component" rule. Use R2ABench as your eval.

## Short answer (per stage)
| Stage | Best candidate | Proof | Verdict |
|---|---|---|---|
| Design exploration | Superpowers `brainstorming` (v7.0.1) | P1 for cost and compliance, author-run; nothing on design quality | Adapt |
| Design exploration (visual) | Anthropic `frontend-design` | P4 | Lift one technique |
| System design | Spec Kit `/speckit.plan` (1.2.0) / BMAD `create-architecture` (6.12.x) | P2 end to end only | Adapt the templates |
| Architecture review | None | Nothing proven | Lift ATAM risk-severity technique (P1, small) |
| Over-engineering | Spec Kit Articles VII/VIII gates | P5 for the gate itself | Lift |

## Key Findings
1. **Skills help on average, but design skills are unmeasured.** SkillsBench (arXiv 2602.12670) covers 87 tasks across 8 domains and 18 model–harness setups. Curated skills raised pass rates from 33.9% to 50.5% (+16.6pp, with per-configuration gains from +4.1 to +25.7pp). Self-generated skills scored −1.3pp, "comprehensive" skills scored −2.9pp, and bundles of 2–3 skills beat 4 or more. None of its tasks are design-stage tasks. Treat this as guidance for writing your skills (short, focused, human-curated), not as evidence for any design skill.
2. **The only controlled comparison of spec/design workflows is end to end, and it was run by a vendor.** The Uvik Software SDD Benchmark used 50 brownfield Python tickets, `claude-sonnet-5` in every arm, blind senior review, and published a CC BY 4.0 CSV. Merges out of 50: OpenSpec 42, BMAD 41, Kiro 41, Spec Kit 40, no-spec control 36. Defects per merged ticket were 0.46 with a spec and 0.86 without. The spec phase took 35.1% of tokens (over 40% for BMAD), and the median spec phase was 18 min (28 min for BMAD). Gains appeared only on feature and data-pipeline tickets and on tickets touching 3 or more files. Caveats: Uvik sells engineering services, and the page shows "Last updated: October 8, 2026" while stating a run date of October 15, 2026. Treat it as P2 with a provenance flag.
3. **Requirements-to-architecture generation fails on relations and traceability, and adding agents does not fix it.** R2ABench has 68 projects. Edge F1 never exceeded 0.1758. Edge hallucination (39.1%) and node hallucination (30.2%) were the dominant structural errors. Weak traceability and ASR omission were the most common semantic failures. The paper's example of an unsupported addition is Kafka, Redis and a service mesh. MetaGPT, OpenHands and Mini-SWE "reshap[e] the error profile rather than delivering a reliable end-to-end advantage". GPT-5 with direct prompting was the strongest semantic configuration.
4. **LLM architecture critique over-generates.** In Capilla et al.'s ATAM study (arXiv 2603.28914), with 7 student groups and an expert ground truth, MS Copilot "was able to identify additional risks and sensitivity points in most cases" and found more trade-offs than the students. However, it "tended to suggest risks for almost every scenario". The authors conclude that LLMs "outperform humans in the generation of candidate risks, but not necessarily in the evaluation activity". The nearest acceptance data comes from code review, not architecture. An ASE 2025 study of Atlassian's LLM review comments (arXiv 2510.05450) found code-design comments resolved at only 28.6%, against 43.3% for readability and 41.9% for code bugs. A July 2026 preprint on CodeRabbit found 56.3% of agentic reviews rejected, with false positives the top reason (reported secondhand via an Augment Code guide).
5. **Superpowers is the only pack with a public eval harness and evidence-driven changes.** v5.0.6 (25 Mar 2026) removed subagent spec/plan review loops. The author's regression tests ran 5 versions (v3.6.0–v5.0.4) with 5 trials each and "showed identical quality scores regardless of whether the review loop ran", while the loop added about 25 min. An inline self-review checklist replaced it and "catches 3-5 real bugs per run in ~30s". The harness (`prime-radiant-inc/superpowers-evals`, public) grades workflow compliance, not design quality. The headline claims also disagree: the v6 blog says "up to 50% faster and up to 60% cheaper", while the v6.0.0 release note says "roughly twice as fast" with "almost 50% fewer tokens".

## Details

### Stage 1: Design exploration
| Name | Link (checked 2026-10-27) | License | What it does | Proof and evidence | Fit gaps | Verdict |
|---|---|---|---|---|---|---|
| Superpowers `brainstorming` | github.com/obra/superpowers `skills/brainstorming/SKILL.md`, v7.0.1 (commit 2ce8aa1, 21 Oct 2026) | MIT | Reads context first, then puts "several real alternatives" in a message of their own, recommends one, has the human pick, writes a design doc, runs self-review, then hands off to `writing-plans` | P1 (author-run, public harness) for process cost and compliance; P3 field reports (e.g., chardet 7.0.0). No design-quality or human-preference data | Aggressive triggering ("You MUST use this before any creative work"), and the terminal state forbids invoking other skills, which hijacks host workflows. v7.0.0 rewrote it 17 days ago, so it is unstable | **Adapt** |
| Anthropic `frontend-design` | anthropics/skills `skills/frontend-design/SKILL.md` (third-party audit at 683bc88 / dbd4588, Oct 2026; byte-identical copy in anthropics/claude-code `plugins/frontend-design`) | Conflicting reports: Apache 2.0 `LICENSE.txt` per one audit, "proprietary" per a review. Verify before copying | Grounds the design in the subject, writes a compact token plan (palette, type, layout, one signature element), reviews the plan against generic defaults, builds, then self-critiques | P4. Anthropic's blog shows only before/after screenshots, with no harness or preference study. Anthropic calls the skills demonstrations to test in your own environment | Produces one direction, not several. Does not consume an existing design system. Aesthetic-only, with no handoff artifact | **Lift one technique** |
| Design Lab / Design Variations (marketplace skills) | mcpmarket.com listings | Unknown | Generate 5 (Design Lab) or 16+ (Variations) on-system UI variants from detected Tailwind/CSS tokens; Design Lab adds a feedback overlay | P5 | Unknown authorship and scripts. Writes temporary files into the repo | **Ignore** (re-implement the idea) |
| b1rdmania/claude-brand-skills | github.com/b1rdmania/claude-brand-skills | Not verified | Brand → DESIGN.md pipeline; frontend skill asks for "3 structurally different variants to compare" | P5 (a SKILL-AUDIT.md of author gap notes only) | Bundles an image-generation CLI that calls multiple hosted models | **Ignore** |

**Techniques worth lifting**
- **Approaches before design:** present 2–3 alternatives with trade-offs in a separate message, recommend one, and let the human choose. Then write the design doc and require human approval before planning (Superpowers; P1 for compliance only).
- **Plan-then-critique against defaults:** write the token plan first, then rewrite any part that "reads like the generic default" and state what changed and why (frontend-design; P4).
- **On-system variants:** read existing tokens (Tailwind config, CSS variables) and require structural differences between variants, not just reskins (Design Lab/Variations; P5). Pair this with a hard rule that every value must use a semantic token.
- **Inline self-review checklist** (placeholder scan, internal consistency, scope, ambiguity) instead of a reviewer subagent (Superpowers v5.0.6; P1, author-run).

**Eval assets:** Design2Code (484 real webpages, with a human pairwise protocol). UI-Bench (10 tools, 30 prompts, 300 sites, 4,000+ expert pairwise judgments, open prompts and framework). A generative-UI preference dataset (600 pairs, 12,000 labels, arXiv 2604.09876). WebUIProof (functional checks). WebDev Arena and Design Arena (hosted, so a reference for the bar only). None of these tests "diverge then converge" exploration, so you will need your own pairwise study: N directions with the skill against one without.

### Stage 2: System design
| Name | Link | License | What it does | Proof and evidence | Fit gaps | Verdict |
|---|---|---|---|---|---|---|
| GitHub Spec Kit `/speckit.plan` | github.com/github/spec-kit, `templates/plan-template.md` (1.2.0) | MIT (verify `LICENSE`) | Produces plan.md plus research, data-model, contracts and quickstart. Includes a Constitution Check and a Complexity Tracking table | P2 end to end (Uvik: 40/50 vs 36/50). P3: a 14-engineer pilot (arXiv 2605.01160) reported "Spec Kit did not eliminate the PRP"; its uncontrolled figures show hotfixes falling from 3–5 to 1–2 per sprint. Single-task comparison: 473 s, $2.84, 690 spec lines | No capacity or failure-mode sections. Python CLI. Gates are "advisory (prose)" | **Adapt** |
| BMAD `bmad-create-architecture` + implementation readiness check | github.com/bmad-code-org/BMAD-METHOD, v6.12.x (v6.12.0, 4 Sep 2026) | MIT | Architect persona turns the PRD into architecture.md (stack, APIs, DB schema), then epics and stories, then a cross-document readiness check | P2 end to end (Uvik 41/50; spec phase over 40% of tokens). P3 regressions: Discussion #979 says v6 architecture docs are worse than v4; Issue #872 reports a command that does not exist | Heavy persona overhead. Frequent renames (v6.11/v6.12) | **Lift** (readiness check, decision catalog) |
| MetaGPT-style architect→reviewer→refiner | As run in R2ABench | MIT | Multi-agent architecture generation | P1 (R2ABench): no consistent gain over direct prompting, and lower semantic scores for GPT-5 | Cost multiplier with no payoff | **Ignore** |

**Techniques worth lifting:** structured SRS input (FR/NFR/constraints/ASR, per ISO 29148) with evidence IDs. Require each component and edge to cite a requirement ID, because traceability is the top failure mode (R2ABench; P1 as a diagnosis). A data-model plus contracts split (Spec Kit; P2 end to end). A readiness check that cross-validates the PRD, architecture and stories (BMAD; P3).

**Eval assets:** R2ABench (68 projects, PlantUML references, layered L0–L2 scoring; the L2 judge is within one point of humans 72.77% of the time). ArchBench (an aggregation platform). SAKE (2,154 multiple-choice questions; tests knowledge only, not design).

### Stage 3: Architecture design and review
| Name | Link | License | What it does | Proof | Verdict |
|---|---|---|---|---|---|
| ATAM-with-LLM prompts (Capilla et al., arXiv 2603.28914) | Anonymized reproducibility kit | CC BY-NC-ND (paper) | Prompted risk, sensitivity-point and trade-off passes over a utility tree | P1 (small: 7 groups, expert ground truth); LLM over-generates risks | **Lift** (add a 0–3 severity scale and keep only items rated 2 or higher) |
| GADR (arXiv 2608.17694) | Paper | Not stated | Multi-agent extraction of Nygard ADRs from meeting transcripts | P1 (5 transcripts, 4 senior architects; beat zero-shot and few-shot on stability). RAG enrichment added unfaithful content | **Lift** (extract-then-verify, no RAG embellishment) |
| ADR context strategy (arXiv 2604.03826) | Zenodo replication package | Open | Tests how much prior ADR history to feed | P1: last 3–5 ADRs ≈ full history | **Lift** |

No skill reports precision or acceptance rates for architecture critique. Plan to measure your own: log each finding, record whether a human accepted it, and target at least the 28.6% design-comment resolution baseline from the Atlassian ASE 2025 study (arXiv 2510.05450).

### Over-engineering
- **Spec Kit Articles VII/VIII:** "Maximum 3 projects", use frameworks directly, and justify any violation in Complexity Tracking. P5 for the gate's own effect. It is the best-structured counter available, so **lift** it.
- **Evidence the problem is real:** R2ABench node and edge hallucination plus unsupported infrastructure. An incident study of 547 confirmed GitHub failures (arXiv 2605.30777) includes an "Unwarranted Abstraction" category, defined as "over-engineering of trivial tasks by injecting unnecessary design". Hora and Robbes (arXiv 2602.00409, MSR 2026) found coding agents add mocks in 36% of test commits against 26% for non-agents.
- **Process-level YAGNI:** Uvik found specs do not pay back on 1–2-file, bug-fix or refactor tickets. Superpowers dropped review subagents that added time without quality. **Gate the design stage by ticket size** (3 or more files, or a new feature).

### Handoff
- **Superpowers:** the committed design doc at `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` goes through human approval, then `writing-plans` writes `docs/superpowers/plans/...`. This handoff is strong because it is a file plus a gate.
- **Spec Kit:** spec.md, then plan.md plus data-model and contracts, then tasks.md. Unresolved items are marked `[NEEDS CLARIFICATION]`.
- **BMAD:** PRD.md, then architecture.md, then sharded stories, then the readiness check.
- **What preserves decisions:** an ADR per decision (Nygard format, feeding the last 3–5), requirement-ID trace links on each component, and a drift check after build. Uvik found merged code diverged from its own spec in 7.9% of spec-arm tickets.

## Recommendations
1. Write in-house design skills as short, focused files (SkillsBench) and evaluate them before adopting anything. Use R2ABench for system design, and a 20-prompt pairwise human study (UI-Bench protocol) for design exploration.
2. Adapt Superpowers' approaches-gate and inline self-review. Do not adopt its trigger language.
3. Add to the plan template: a Simplicity/Anti-Abstraction gate with Complexity Tracking, a capacity and failure-mode section (no candidate has one), and requirement-ID traceability.
4. Run architecture review as candidate generation followed by a severity filter, with human acceptance logged as the precision metric.

## Caveats and Risks
- **License traps:** Anthropic `frontend-design` licensing is reported inconsistently. Marketplace design skills (Design Lab, Variations, bencium's "Not specified") lack clear licenses.
- **Prompt-injection-like instructions:** Superpowers' "You MUST use this before any creative work" and "the ONLY skill you invoke after brainstorming is writing-plans" override host routing. Its persuasion-style pressure language is deliberate.
- **Maintenance churn:** Superpowers v7.0.0 brainstorming rewrite (10 Oct 2026). Its evals submodule broke installs and was removed in v6.0.2. BMAD v6.11/v6.12 renames, with v6 architecture regressions reported.
- **Scripts and network:** b1rdmania bundles a multi-model image-generation CLI. Design Lab writes temporary lab files. A 2026 study documents skill-induced agent failures (arXiv 2608.11888).
- **Evidence quality:** Uvik is a single vendor-run benchmark with a date inconsistency. Superpowers' numbers are author-run and internally inconsistent. Every academic study cited here is small (n ≤ 68 projects).