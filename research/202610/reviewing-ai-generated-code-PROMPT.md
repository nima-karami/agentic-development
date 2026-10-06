# Research brief: How the industry reviews AI-generated code and codebases (H2 2026)

## Why I am asking

I run an agentic-development practice: most code in my projects is written by coding
agents, and I maintain my own review and QA skills for them. I want to recalibrate those
against what the wider industry actually does today, not against what vendors say.
Treat this as a state-of-practice survey with an evidence grade on every claim.

## Scope

- Time window: prioritise sources from 2026, especially July–October 2026. Older material
  only as baseline for "what changed".
- Subject: review of AI-generated code at two levels:
  1. Change-level review: PRs/diffs produced partly or wholly by agents.
  2. Codebase-level review: periodic audits of repositories where most code is
     AI-written (architectural drift, duplication, dead code, test quality, security
     posture, provenance).
- Segments, treated separately and then compared:
  a. Established companies (large tech, enterprise software, banks/regulated, consultancies).
  b. AI-forward companies (AI labs, agent-tooling vendors, startups founded 2023+ that
     describe themselves as agent-first or "no human writes code").
  c. Open-source maintainers (projects that have published AI-contribution policies).
  d. Solo and small-team practitioners publishing detailed accounts.

## Questions to answer

1. **Review architecture.** Who or what reviews agent-written changes: humans only, AI
   reviewer then human, multiple independent AI reviewers, agent self-review, hidden
   or held-out tests, formal verification, runtime/QA bots? What gating order is
   typical, and what is skipped?
2. **Division of labour.** What do humans still read line by line, what do they sample,
   what do they delegate entirely? Any published "trust tiers" (by change size, risk
   area, author model, test coverage)?
3. **Codebase-level audit practice.** How often, triggered by what, measuring what. Any
   named frameworks, checklists, or tooling for re-auditing an AI-heavy repo.
4. **Known failure modes being guarded against.** Tests that cannot fail, gates weakened
   to get green, duplicated helpers, silent scope creep, fabricated verification
   claims, security regressions, licence contamination. Which are documented with
   incident evidence and which are folklore.
5. **Metrics.** What do teams measure (review latency, defect escape rate, PR size,
   revert rate, reviewer load, cost per merged change) and any published numbers,
   with their methodology. Include 2026 industry surveys and reports if they exist.
6. **Process and policy.** PR-size norms for agent output, provenance labelling (AI
   authorship disclosure in commits/PRs), accountability rules, reviewer-to-agent
   ratios, review SLAs, bans or restrictions. Open-source policies on accepting
   AI-generated PRs, with named projects.
7. **Tooling landscape.** Named products and OSS tools used for AI code review in 2026,
   what each actually does, and independent evidence of effectiveness versus vendor
   claims. Note where a tool is itself an agent reviewing agents.
8. **Incumbents versus AI-forward.** Where do the two segments converge, where do they
   diverge, and is there evidence that either is getting better outcomes? Are
   incumbents adopting the AI-forward practices with a lag, or choosing differently?
9. **Regulated and safety-critical contexts.** Any guidance from regulators, standards
   bodies, or auditors on reviewing AI-written code (finance, medical, automotive,
   government).
10. **Open problems.** What practitioners say is still unsolved: review throughput,
    reviewer fatigue, verifying runtime behaviour, judging architecture, long-horizon
    agent runs that nobody fully reads.

## Evidence rules

- Prefer first-hand sources: engineering blogs, conference talks, postmortems,
  published policies, survey reports with stated methodology, peer-reviewed or
  arXiv papers with reproducible setups.
- Grade every substantive claim: `[measured]` (numbers plus method), `[first-hand]`
  (practitioner account, no numbers), `[vendor]` (marketing or self-reported),
  `[opinion]`. Do not let vendor claims stand without an independent counter-source
  or an explicit "unverified" tag.
- Cite with title, author or organisation, date, and URL. Do not invent sources. If
  a claim cannot be sourced, say so rather than fill the gap.
- Name real companies, projects, and tools. Anonymised "a large bank" is acceptable
  only when the source itself is anonymised.

## Output

A report of roughly 4,000–7,000 words, structured as:

1. **Executive summary:** the five things that have actually converged in 2026, and the
   three most contested questions.
2. **Findings per question 1–10**, each ending with the evidence grades used.
3. **Comparison table:** incumbents vs AI-forward vs open source, across review
   architecture, gating, metrics, policy, tooling.
4. **Timeline** of notable 2026 changes (policies, incidents, tools, reports).
5. **What a small agent-first team should copy, what it should ignore, and why.**
6. **Full source list.**
