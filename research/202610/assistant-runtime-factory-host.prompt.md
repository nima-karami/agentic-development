# Research prompt: can an open-source assistant runtime host a software factory?

## Context

I am designing a **software factory**: I give it intent in chat, and it returns
deployed, tested software. It runs in the cloud, unattended, with nothing on my
machine. A first survey (October 2026) covered pipelines, workflow engines,
sandboxes, observability and eval harnesses. Its verdict: nothing open-source
covers the whole thing, the agent layer is a commodity, and the scarce part is
the **gatekeeping and record-keeping spine**.

That survey skipped a category I care about: **always-on, open-source assistant
runtimes** such as **OpenClaw** (formerly Clawdbot / Moltbot) and **Hermes Agent**
(Nous Research), plus their forks and peers. These are personal agents that run
on a server, talk to me over chat, have skills, memory, cron, tools and
multi-provider model support, and in some cases claim to improve themselves. The
hypothesis to test: **one of these runtimes could be the host and operator of
the factory**, building, improving and monitoring the whole flow from inside
itself, so that I adopt a runtime instead of building one.

What the factory must have (requirement IDs refer to my PRD; the research does
not need the PRD, only this list):

- **Gated pipeline.** Stages intake → spec → plan → build → review → runtime QA
  → integrate → release → observe. A stage advances only on a deterministic
  gate (exit code captured by the system, never the agent's own report).
  (FR-7 to FR-9, FR-13)
- **State outside any conversation**, in files I control; resumable after a
  crash; concurrent items isolated. (FR-16, FR-17, FR-20)
- **Hard budget stops** per run and per stage, enforced outside the agent.
  (FR-57, NFR-3)
- **Run record**: append-only event log per run plus per-stage evidence
  (gate output, diffs, screenshots, transcripts, decisions, cost), traversable
  item → stage → attempt → evidence, readable by a second agent with no access
  to the runtime that produced it. (FR-25 to FR-30)
- **Notifications** when things go wrong, with run, stage, evidence reference,
  cost so far, and action needed. (FR-31, FR-32)
- **Dashboard**: token and cost per run / stage / model / product; the
  improvement-required queue; optimization hotspots. (FR-35 to FR-39)
- **Harness and model independence**: any coding harness or model that honours a
  stage contract can run that stage; cheaper models admitted on eval evidence.
  (FR-52 to FR-56)
- **Self-improvement under control**: the runtime may propose changes to its own
  skills, gates or evals, but they land only after passing an eval corpus and a
  human approval; gate and eval files are protected from the product loop.
  (FR-14, FR-46 to FR-50)
- **Owner direction at any time** via chat without stopping runs. (FR-21a)
- **Least privilege**: each stage holds only its credentials; release capability
  separate; secrets never in logs. (NFR-6, NFR-10)
- Archetypes: web app first; later desktop (Windows / macOS / Linux), agentic
  flows, MCP servers.

## Questions to answer

1. **What they are.** For OpenClaw, Hermes Agent, and the strongest peers
   (candidates: ZeroClaw, NanoClaw, PicoClaw, Nanobot, Letta, Paperclip,
   AutoGPT Platform, Agent Zero, Suna / Kortix, Archon; add any 2026 project
   that fits "always-on self-improving agent runtime"): license, latest release,
   maintainers and activity, architecture (gateway or daemon, channels, tools,
   skills, memory, cron, sub-agents, sandboxing), documented cloud deployment,
   model providers supported, and cost tracking per request.
2. **Fit to the list above, item by item.** For each requirement: provided
   natively / addable as a skill or plugin without forking / must live outside
   the runtime / contradicts the runtime's design. Be specific about budgets
   (is there any hard stop, or only soft limits?), run logs (format, location,
   completeness, whether tool output and exit codes are captured), isolation
   (per-session sandbox or shared host), and gates (does anything in the runtime
   refuse to proceed on an agent's say-so?).
3. **Self-improvement claims.** What exactly does "learns from experience" mean
   in each runtime: memory writes, skill generation, prompt edits, config edits?
   What triggers it, what reviews it, how is it versioned, can it be rolled back?
   What published evidence exists that self-generated skills help or hurt (for
   example the SkillsBench finding that self-generated skills gave negligible
   or negative gains), and any documented incidents of a runtime degrading
   itself.
4. **Security record, 2026.** Exposed instances, prompt-injection incidents,
   malicious skills on registries (ClawHub or equivalents), CVEs, and what each
   project changed in response. What the docs recommend for an internet-exposed,
   unattended deployment with repository and deploy credentials. Is that
   posture acceptable for an agent that holds a release capability?
5. **Operational evidence.** Reports from people running these runtimes
   unattended for days or weeks: reliability, memory growth, cost per day,
   runaway loops, lost state after restarts. Has anyone used one to build,
   deploy and QA software end to end? What did they report?
6. **Three architectures, compared.** (a) Factory *inside* the runtime: the
   runtime is the conductor and runs stages as its own skills and sub-agents.
   (b) Runtime as *front door*: it takes my direction and sends notifications,
   while an external pipeline owns gates, state, budgets and the run record.
   (c) Runtime as a *stage worker* only, behind a stage contract. For each:
   which requirements it satisfies, which it breaks, the lock-in if the project
   dies or relicenses, and the migration cost between (a) and (b).
7. **Verdict.** Adopt / extend / borrow ideas / avoid per runtime, with the
   specific missing requirements that drive the verdict, and the smallest
   composition that would let one of them host the factory if that is viable.

## Evidence rules

- Prefer primary sources: the project's own repo, LICENSE, docs, releases,
  security advisories and blog. Label user reports and security write-ups as
  secondary, and anecdotes as anecdotal.
- Date every claim. These projects change weekly; say which version you read.
- Tag each claim **verified** (read from a primary source), **reported**
  (secondary source), or **unverified**.
- Do not invent features, version numbers, CVE IDs, star counts or incidents.
  If something cannot be sourced, say so.
- Where sources disagree (for example on licenses, star counts, or whether a
  feature exists), show the disagreement instead of picking a side.

## Output I want

- An executive answer up front: can any of these runtimes host the factory, and
  what do they not offer that the factory needs, in a few sentences.
- A capability matrix: runtime × requirement, with the four-way fit rating
  from question 2 and a one-line note per cell.
- A self-improvement section answering question 3 per runtime, with evidence.
- A security and operations section answering questions 4 and 5.
- The three-architecture comparison from question 6 as a table, plus a
  recommendation and the trade-off that would change it.
- Per-runtime verdicts with license, maturity and the deciding gaps.
- Open problems nobody has solved.
- A full source list with dates.

## Out of scope

- Hosted closed assistants (ChatGPT agents, Claude.ai, Gemini) except as a
  one-line comparison point.
- Coding harnesses on their own (Claude Code, Codex CLI, OpenHands); they were
  covered in the first survey and are stage workers here, not hosts.
- Pricing comparisons beyond cost-per-day reports.
