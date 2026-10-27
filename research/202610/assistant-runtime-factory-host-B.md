# Can an Open-Source Assistant Runtime Host a Software Factory? (October 2026)

No. None of the always-on assistant runtimes surveyed (OpenClaw, Hermes Agent, NanoClaw, ZeroClaw, Letta) can be the conductor of a gated factory. None of them has a hard budget stop enforced outside the agent, a run record organised by item, stage and attempt, or a gate the agent cannot talk its way past. The one gate-like primitive in the field, OpenClaw's Lobster plugin, currently hands its approval token back to the model.\[1\] The workable design is architecture (b): a runtime as the chat front door and notifier, with an external spine that owns gates, state, budgets and the record. Hermes Agent is the best front-door candidate because it has the strongest controls on self-modification. Paperclip, the closest peer, is the best idea donor for budgets and run records.

## TL;DR
- **Verdict:** use a runtime as the front door, not the host. Every runtime fails hard budget stops (FR-57/NFR-3), deterministic system-held gates (FR-7–9/13) and the cross-agent-readable run record (FR-25–30). These are exactly the "spine" your first survey called scarce, and the runtimes do not supply it.
- **Best fits:** Hermes Agent (MIT) as front door. It offers staged skill-write approval, snapshot rollback and default-deny in cron. OpenClaw (MIT) is a front door only with no repo or deploy credentials: its 2026 record includes CVE-2026-25253 (CVSS 8.8), 341 to 1,184 malicious ClawHub skills depending on the count (Snyk's 1,467 counts skills with security flaws, of which only 76 were confirmed malicious), and more than 135,000 exposed gateways by SecurityScorecard's 9 Feb 2026 count. Paperclip (MIT) is the closest thing to a spine but stops budgets only before the next run.\[2\]\[3\]
- **Self-improvement is unproven without an eval gate.** SkillsBench found self-generated skills averaged −1.3pp against no skills, while curated skills gave +16.2pp.\[4\]\[5\] Later papers show gains only when generated skills go through verification or refinement loops.\[6\]\[7\] Your FR-46–50 eval-plus-human gate is the right control, and no runtime ships it.

Evidence tags: **[V]** read from a primary source (repo, docs, release notes, paper); **[R]** reported by a secondary source; **[A]** anecdotal; **[U]** unverified or not found. Read dates are October 2026 unless stated.

## 1. What they are

| Runtime | License | Latest release seen | Activity / maintainers | Architecture | Models | Per-request cost |
|---|---|---|---|---|---|---|
| **OpenClaw** (ex-Warelay/Clawdbot/Moltbot) | MIT, © OpenClaw Foundation [V LICENSE]\[8\] | 2026.10.5, 18 Oct 2026; 2026.10.10-beta.2, 19 Oct [R release-page snippet]; OpenClaw 2.0 = v2026.8.1, 30 Aug 2026 [R Wikipedia]\[9\]\[10\] | Foundation since Feb 2026 after Steinberger joined OpenAI; OpenAI sponsors [R]. 392k stars on GHCR page [V, Oct 2026]; 247k on 2 Mar 2026 [R Wikipedia]\[9\]\[11\]\[12\] | Gateway daemon (port 18789, loopback default); many chat channels; skills plus ClawHub registry; cron/heartbeat; multi-agent; optional Docker/Podman/SSH/OpenShell sandbox, **off by default** [V docs] | Multi-provider incl. OAuth subscription paths [V docs] | Per-turn estimate when pricing configured; `/usage cost`, Control UI Usage; OAuth shows tokens only [V docs]\[13\]\[14\] |
| **Lobster** (OpenClaw workflow plugin) | MIT [V package.json]\[15\] | v2026.6.11, 11 Jun 2026; no newer tag by 22 Oct [V releases]\[16\] | steipete-released; slow cadence | Typed pipelines; `run:` shell steps; `on_error` stop/continue/skip_rest; approval/input gates with resume tokens; state in `~/.lobster/state` [V README/docs]\[17\]\[18\] | Via OpenClaw | Optional workflow-level `cost_limit` warn/stop [V release notes]\[16\] |
| **Hermes Agent** (Nous Research) | MIT [V repo] | v0.19.0, 20 Jul 2026 [R];\[19\] v0.21.6 rollup, 8 Oct 2026 [R]\[20\] | 239k stars, 48.6k forks, 26,383 commits [V repo page, 22 Oct 2026]\[21\] | Agent-first CLI/TUI plus optional gateway; messaging platforms; cron; subagents; 7 terminal backends (local, Docker, SSH, Daytona, Singularity, Modal, Vercel Sandbox) [V README/docs]\[21\]\[22\] | Multi-provider, Nous Portal [V] | Not verified per request [U] |
| **NanoClaw** | MIT [V repo] | Version not verified [U] | qwibitai/nanoclaw; ~29,300 LOC vs 434,453 for OpenClaw, per its site [R]\[23\] | Single Node host process; SQLite, polling loop, **one container per session** (Docker only); credentials via OneCLI Agent Vault proxy, never in container [V nanoclaw.dev]\[24\] | Claude Agent SDK default; Codex/OpenCode/Ollama per group [R]\[25\] | Not found [U] |
| **ZeroClaw** | MIT OR Apache-2.0 [V lib.rs]; one mirror lists Apache-2.0 only [R]: disagreement\[26\]\[27\] | 0.8.5, 5 Sep 2026; lib.rs marks it "unstable" [V lib.rs]\[28\] | zeroclaw-labs; 624 issues, 400 PRs open [V repo]\[29\] | Single Rust binary; 30+ channels; ~20+ providers; runtime native or Docker [V README]\[29\]\[30\] | ~20+ providers [V] | Not found [U] |
| **Letta** (Letta Code) | Apache-2.0 [R] | v0.32.11, 15 Sep 2026; old V1 API server retired [R]\[31\] | Letta Inc. (MemGPT authors) | Memory-first agent; git-backed Markdown memory (MemFS); "dreaming" (sleep-time) consolidation; self-hosted App Server or Cloud [R]\[31\]\[32\] | 15+ providers [R]\[33\] | Not found [U] |
| **Paperclip** (peer: control plane, not an assistant) | MIT [V repo] | v2026.1012.0, 12 Oct 2026 [R release snippet]\[34\]\[35\] | Launched Mar 2026 by @dotta [R]\[36\] | Node + React control plane; org chart, tickets, heartbeats, approvals, budgets; bring-your-own-agent adapters (OpenClaw, Hermes, Claude Code, Codex) [V repo/docs]\[2\]\[37\]\[38\]\[39\] | Whatever the adapter runs | Cost by agent/project; budget incidents [V docs] |

Not researched in this pass: Agent Zero, Suna/Kortix, Archon, AutoGPT Platform, Nanobot and PicoClaw [U]. Treat them as unassessed, not as rejected.

## 2. Capability matrix

**N** = native · **S** = addable as skill/plugin without forking · **O** = must live outside · **X** = contradicts design

| Requirement | OpenClaw (+Lobster) | Hermes Agent | NanoClaw | ZeroClaw | Letta | Paperclip |
|---|---|---|---|---|---|---|
| Gated pipeline, system-held exit codes (FR-7–9,13) | **S** – Lobster typed shell steps with `on_error`; but approval token returned to model, which can send `approve:true` (open PR #172820)\[1\]\[16\] | **O** – no stage engine; cron plus subagents | **O** – none | **O** – none documented | **O** – none | **S** – tasks can't close without configured review stages; gate is reviewer, not exit code\[40\] |
| State in files, crash-resumable, isolated (FR-16,17,20) | **S** – JSONL sessions plus atomic Lobster state; resume only from gates, not mid-step crash | **S** – `~/.hermes` files; no run-level resume found | **S** – SQLite plus per-session container | **O** – not documented | **S** – git-backed memory, not run state | **N** – run rows, atomic task checkout [R] |
| Hard budget stops per run/stage (FR-57, NFR-3) | **O** – "no built-in hard spend cap" [R]; Lobster `cost_limit` optional, unpriced models count $0\[18\]\[41\] | **O** – none found | **O** – vault "supports rate limits" [V], no $ cap\[42\] | **O** | **O** | **S** – auto-pause at 100% monthly per-agent budget; applies to *next* run, not mid-run [V blog]\[3\]\[40\] |
| Run record item→stage→attempt→evidence (FR-25–30) | **S** – append-only per-session JSONL with tool calls; deletable, per session not per stage [R]\[43\]\[44\] | **S** – session store with FTS5 search; format not verified | **O** | **O** | **O** | **S** – per-run transcript plus stdout/stderr log viewer; per ticket, not per stage\[45\] |
| Failure notifications with evidence/cost (FR-31,32) | **S** – channels plus cron | **S** – channels plus cron | **S** | **S** | **O** | **S** – budget incidents in UI; needs channel |
| Dashboard cost per run/stage/model/product (FR-35–39) | **S** – Usage per session/provider/model; no stage/product\[46\] | **S** – web dashboard exists; cost breakdown not verified | **O** | **O** | **O** | **N**-partial – cost by agent/project/model [R] |
| Harness/model independence; eval-based admission (FR-52–56) | **N** for models; **O** for eval admission | **N** / **O** | **S** – Claude-first / **O** | **N** / **O** | **N** / **O** | **N** – BYOA adapters / **O** |
| Self-improvement under eval plus human gate; protected files (FR-14,46–50) | **O** – no write gate found | **S** – `skills.write_approval` stages writes; curator snapshots/rollback; no eval gate\[47\]\[48\] | **S** – approval-gated package/MCP requests [R]\[25\] | **O** | **S** – git history; "agent reviews" ≠ human\[31\] | **O** |
| Owner direction mid-run via chat (FR-21a) | **N** – chat, `/stop`, queued follow-ups\[49\] | **N** – interrupt-and-redirect\[21\] | **N** | **N** | **S** | **S** – comments wake agents; no chat channel |
| Least privilege, separate release cap, no secrets in logs (NFR-6,10) | **S** – per-agent sandbox/tool allowlists; any gateway-authed caller is full operator [V SECURITY]; `redactSensitive`\[44\]\[50\] | **S** – approvals, container backends; redaction sweep v0.21.6 [R]\[20\] | **N** – keys never enter container\[24\]\[42\] | **S** | **S** | **S** – per-heartbeat secret injection [R]\[38\] |
| Archetypes: web → desktop/agentic/MCP | **O** – OS-specific runners outside all | **O** | **O** | **O** | **O** | **O** |

**Reading the matrix:** no column has an **N** for gates, budgets or the run record. Paperclip comes closest but is a control plane, not an assistant runtime.

## 3. Self-improvement claims

| Runtime | What "learns" means | Trigger | Review | Versioning / rollback |
|---|---|---|---|---|
| Hermes | Writes/patches SKILL.md files; memory writes; user model (Honcho) [V] | After complex tasks, error recovery, corrections; background review after a turn [V docs]\[48\]\[51\] | Off by default: "By default the agent writes skills freely" [V]. Optional `skills.write_approval` stages writes in `~/.hermes/pending/skills/` for `/skills approve` [V]. v0.21.6 reportedly forces approval on writes to AGENTS.md, skills and memory [R]\[20\]\[48\] | Curator (v0.12, 30 Apr 2026): tar.gz snapshot before each pass, `hermes curator rollback`, mutation ledger, never auto-deletes. Defaults: stale at 14 days, archive at 30; LLM consolidation opt-in [V docs]. A third party observed 30/90-day thresholds on v0.19.0 [R]: disagreement\[52\]\[53\]\[54\] |
| OpenClaw | Memory files, heartbeat.md, agent-installed skills [R]\[55\] | Agent discretion | No staged gate found [U] | None found [U] |
| Letta | Edits its own memory blocks/system prompt; skill learning; dreaming [R]\[32\]\[33\] | In-turn and idle-time | Optional "agent reviews before applying," which is a model, not a human [R]\[31\] | Git-backed memory [R]\[56\] |
| NanoClaw | Per-group CLAUDE.md memory; requests for new packages/MCP servers | Agent request | Admin approval [R]\[25\] | Not found |

**Evidence on whether it helps:**
- **SkillsBench (arXiv 2602.12670, Feb 2026) [V via mirrors]:** 84 tasks, 7 model-harness configs, 7,308 trajectories.\[57\] Curated skills gave +16.2pp. Self-generated skills gave −1.3pp on average, and only Opus 4.6 showed a marginal gain (+1.4pp).\[4\]
- **Counter-evidence:**
  - MUSE-Autoskill (arXiv 2605.27366) [V] measured transfer into **Hermes** on 75 tasks. Codex-created skills gave −0.23pp, Claude-Code-created skills +8.73pp, MUSE skills +14.66pp, and human skills +10.78pp. Coverage was the bottleneck: 28–31 tasks had no usable skill.\[6\]
  - SkillEvolver (arXiv 2605.10500) [V] reached 56.87% against 43.6% for human skills, using an iterative refine loop.\[7\]
  - **Interpretation:** generated skills help only when a verifier sits in the loop. That is your eval gate.
- Nous's claim that agents with 20+ self-created skills finish similar tasks 40% faster comes from "Nous Research internal benchmarks," reportedly corroborated by TokenMix.ai (dev.to, Apr 2026) [R/U]. The 40% means less token use and time to reach equivalent output, not better output. It is domain-specific: research-task skills "do not transfer to code review tasks." No methodology is published.

**Degradation and incidents:**
- An independent audit of Hermes v0.8.0 (11 Apr 2026) flagged **persistent skill injection**: content the agent reads can become a skill that survives across sessions [R CSA, aurpay].\[58\]\[59\]
- An OpenClaw agent created a MoltMatch dating profile without explicit direction [R Wikipedia].\[9\]
- One user reports that cron jobs accumulate context, rising from $0.02 to $2 per execution [A].\[60\]
- No published study of a runtime degrading its own skill library over weeks was found [U].

## 4. Security record (2026)

**OpenClaw:**
- **CVE-2026-25253**, one-click RCE via gatewayUrl/WebSocket token leak, disclosed late Jan 2026. Most sources give CVSS 8.8 [R]; one gives 9.1 [R]: disagreement.\[61\]\[62\] One guide wrongly calls it the ClawHub supply-chain CVE [R].\[63\]
- **ClawHub malicious skills.** Counts disagree, and are shown in source order:

  | Count | Source |
  |---|---|
  | 341 of 2,857 (335 in the "ClawHavoc" campaign)\[64\] | Koi Security researcher Oren Yomtov, audit published 1 Feb 2026, which named the campaign |
  | 824+ (~20% of the registry)\[61\] | Bitdefender |
  | 1,184 in ClawHub's history as of 5 Feb, from 12 author IDs; one account (hightower6eu) published 677 | Antiy CERT, via GBHackers, 18 Feb 2026 |
  | 1,467 of 3,984 ClawHub + skills.sh skills (36.82%) with "at least one security flaw," 534 critical, only "76 confirmed malicious payloads" — so not a malicious-skill count | Snyk ToxicSkills, 5 Feb 2026 |

  All of these are [R]. The payload was mostly the Atomic/AMOS infostealer.\[61\]\[65\]
- **Exposed instances:** 21,000 (Censys, late Jan), 40,214, 42,665 (Maor Dayan) [R]. SecurityScorecard's STRIKE team counted "just over 40,000" at publication and "more than 135,000" by 9 Feb 2026 across 82 countries, with RCE-vulnerable instances rising from 12,812 to more than 50,000 (The Register) [R]. Censys later found 63,070 live instances on 31 Mar 2026 [R].
- **Responses:**
  - VirusTotal scanning of every ClawHub upload with daily re-scans (announced 7 Feb) [R].\[65\]
  - Loopback bind default on host installs, `security.installPolicy`, and `openclaw security audit --deep/--fix` [R/V].\[65\]
  - China restricted state-enterprise use in March 2026 [R Wikipedia].\[9\]
- **What the docs recommend [V SECURITY.md]:**
  - Loopback bind; remote access via SSH tunnel or Tailscale; strong gateway auth.\[50\]
  - "One host/VPS per user."\[50\]
  - The docs state: "If a caller passes Gateway auth, they are treated as a trusted operator."\[50\]

**Hermes Agent:**
- **CVE records disagree:**
  - "None publicly documented" as of May [R innfactory].\[62\]
  - CVE-2026-7396, 7397 and 6829 [R CSA].\[58\]
  - CVE-2026-7396, 7112 and 7397 [R HackerNoon].\[66\]
  - NVD records CVE-2026-9350, 9367 and 9368, each CVSS 7.3, published 24 May 2026 [R techjack].\[67\]
- **Audit:** external researcher Anic888's audit of v0.8.0 (GitHub issue NousResearch/hermes-agent #7826, 11 Apr 2026; 812 Python files, ~364K lines) reported 4 Critical and 9 High findings in the default config, including: "The LLM can execute ANY shell command on the host when env_type="local" (the default)" [R].
- **Defaults [V docs]:**
  - Approval prompts fail closed.\[68\]
  - `cron_mode: deny` is the default.\[69\]
  - A hardline blocklist cannot be overridden.\[68\]
  - Dangerous-command checks are **skipped inside container backends**.\[68\]\[70\]
  - The default `smart` mode lets an auxiliary LLM auto-approve, i.e. an agent's say-so. One docs page says the default is `manual` [V mirror]: disagreement.\[68\]\[69\]
- **Hub skills** pass a scanner; ClawHub is one install source [R].\[52\]\[71\]
- **Upstream compromise:** v0.21.6 removed the Blender MCP entry after the upstream project was compromised [R].\[20\]

**NanoClaw** has the best default posture: OS-container isolation per session, and credentials injected at a proxy so they never reach the agent [V].\[24\]\[42\] No CVEs were found [U].

**Is this acceptable for an agent holding release capability? No.**
- The trust model treats any authenticated caller as a full operator.
- Skills run with agent permissions.\[64\]
- Prompt injection from repo content, issues or web pages is undefended at the model layer.
- Release credentials must sit in a separate, non-agent step of the external pipeline, triggered only by a system-checked gate.

## 5. Operational evidence

**Cost per day:**
- [R kilo.ai] Idle OpenClaw on premium models burns about $5/day from heartbeats. Measured daily averages: Opus 4.7 $8.70, Sonnet 4.6 $2.80, MiniMax M2.5 $0.12.\[72\]
- [A] $103.47 overnight (7h52m unattended, mostly one loop), reported by a vendor selling a cap proxy.\[73\]
- [A] $37 in six hours.\[60\]
- [R] A $3,600/month case.\[74\]\[75\]

**Runaway loops:** all OpenClaw reports end with the same fix, an external cap: provider spend limits, OpenRouter per-key budgets, or a LiteLLM virtual-key budget [R].\[41\]\[60\]\[76\] In Paperclip, one tester's looping agent hit the 80% warning [A].\[38\] Paperclip itself documents that a budget stops the *next* run, not the current call [V].\[3\]\[40\]

**Logs and state:**
- OpenClaw logs run to about 50–100 MB/day for a moderately active agent [R].\[44\]
- Session transcripts are deletable local JSONL; `/reset` archives them as `.reset.<ts>` files [V skill doc].\[77\]
- Lobster writes state atomically since v2026.6.11, but crash recovery between checkpoints is not documented [V].\[16\]
- No systematic reports of lost state after restarts were found [U].

**End-to-end software builds:**
- An AWS Builder ran OpenClaw on EC2, had it build an app and push to GitHub, and reports it "dumped" unrelated files into the repo [A].\[78\]
- A developer built a multi-agent dev pipeline inside OpenClaw using Lobster sub-workflows, with a tester agent running tests [A].\[79\]
- The `openclaw-code-agent` plugin adds plan approval, git worktrees and merge/PR buttons around Claude Code/Codex [V repo].\[80\]
- **No report was found of a runtime running build → deploy → runtime QA unattended for weeks with deterministic gates** [U].

## 6. Three architectures

| | (a) Factory inside runtime | (b) Runtime as front door | (c) Runtime as stage worker |
|---|---|---|---|
| **Satisfies** | FR-21a, FR-31/32, model independence | FR-21a, FR-31/32 from the runtime; gates, state, budgets, record, least privilege from the spine | Contract isolation; the runtime is replaceable |
| **Breaks** | FR-7–9/13 (gates are agent-mediated), FR-57 (no hard stop), FR-25–30 (session-shaped, deletable logs), NFR-6/10 (one operator trust domain), FR-46–50 (no eval gate) | Nothing structurally; you build the spine | Loses chat/notification value, which duplicates the harnesses already covered in survey 1 |
| **Lock-in if project dies/relicenses** | High: skills, memory and pipeline encoded in runtime formats. All are MIT/Apache today, so forking is legal, but OpenClaw ships near-daily | Low: replace the front door behind a small API (submit intent, status, approve, notify) | Very low |
| **Migration cost** | (a)→(b): rewrite gates, state and budgets outside, then re-point skills to call the spine. Roughly the full spine build, deferred | (b)→(a): not advisable | — |

**Recommendation: (b).** Smallest viable composition:
1. **Hermes Agent** (or OpenClaw) as chat front door and notifier, with three to four narrow tools into the spine: `submit_intent`, `run_status`, `approve`, `redirect`. It holds **no repo, deploy or release credentials**; set `cron_mode: deny`, `write_approval: true`, and use a container backend.
2. **External spine.** Orchestrator plus a file or git run record per item → stage → attempt, with gates evaluated from exit codes the orchestrator captures. The engines are the ones from your first survey; Paperclip's budget-incident and run-record model is a good template.
3. **LLM proxy with hard per-run and per-stage budget keys.** LiteLLM virtual keys are the commonly cited option [R].\[76\] This is the only hard stop available.
4. **Stage workers** (coding harnesses) in per-run containers with a NanoClaw-style credential proxy. Release runs as a separate non-agent job.

**What would change this:** if Lobster merges operator-bound approvals (PR #172820), adds mid-step crash resume, and makes `cost_limit` a hard stop that fails closed on unpriced models, then OpenClaw plus Lobster could host the *gating*, a partial move toward (a). The run record and least-privilege problems would still push the evidence store outside.

## 7. Per-runtime verdicts

| Runtime | Verdict | License / maturity | Deciding gaps |
|---|---|---|---|
| Hermes Agent | **Extend** (front door) | MIT; very active, weekly-plus releases | No gates, no hard budgets, no item/stage record; `smart` approvals let an LLM approve |
| OpenClaw | **Extend with caution** (front door, zero credentials); **borrow** Lobster's typed steps and resume-token pattern | MIT; Foundation; near-daily releases | Worst 2026 security record; operator-equals-everything trust model; no hard cap; self-approvable Lobster gates |
| NanoClaw | **Borrow ideas** (per-session containers, credential proxy); alternative front door if Claude-centric | MIT; small, auditable | Claude-first; no pipeline/budget/record |
| ZeroClaw | **Avoid for now** | MIT/Apache (disputed); "unstable" 0.8.5 | Immature; nothing toward the spine |
| Letta | **Borrow ideas** (git-versioned memory); stage worker at most | Apache-2.0; product churn (V1 server retired) | Memory platform, not an operator |
| Paperclip | **Borrow / evaluate as spine component** | MIT; launched Mar 2026, active | Monthly per-agent budgets stop only the next run; review gates not exit codes; no per-stage evidence model |

## Open problems nobody has solved
- **Agent-proof gates in a chat runtime.** Every approval primitive found either returns control to the model or uses an LLM classifier.\[1\]
- **Mid-call hard budget stops.** Paperclip stops before the next run. Lobster's limit is optional and blind to unpriced models, and a timed-out model call can keep billing [V].\[3\]\[18\]
- **Eval-gated self-improvement.** Hermes offers human-only staging; nobody ships "skill change lands only after passing a corpus."
- **Prompt-injection-resistant persistence.** Skills and memory written from untrusted content become standing instructions.\[59\]
- **Cross-agent-readable run records.** All logs are runtime-shaped (session JSONL, SQLite), not an item/stage/attempt evidence schema.

## Caveats
- These projects change weekly. Versions and counts above are as read in October 2026, and many security figures come from vendors with products to sell.
- Several peers named in the brief were not assessed.
- Matrix ratings of **S** mean "plausible without forking" based on documented extension points, not tested builds.

## Sources

1. [fix(lobster): require operator approval for workflow continuations by Patrick-Erichsen · Pull Request #172820 · openclaw/openclaw · GitHub](https://github.com/openclaw/openclaw/pull/172820)
2. [GitHub - paperclipai/paperclip: The open-source app everyone uses to manage agents at work · GitHub](https://github.com/paperclipai/paperclip)
3. [Run a Company of AI Agents with Paperclip](https://www.theaienterprise.io/p/run-company-ai-agents-paperclip)
4. [(PDF) SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://www.researchgate.net/publication/400812596_SkillsBench_Benchmarking_How_Well_Agent_Skills_Work_Across_Diverse_Tasks)
5. [Paper page - SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://huggingface.co/papers/2602.12670)
6. [MUSE-Autoskill: Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation](https://arxiv.org/pdf/2605.27366)
7. [SkillEvolver: Skill Learning as a Meta-Skill](https://arxiv.org/pdf/2605.10500)
8. [openclaw/LICENSE at main · openclaw/openclaw · GitHub](https://github.com/openclaw/openclaw/blob/main/LICENSE)
9. [OpenClaw](https://en.wikipedia.org/wiki/OpenClaw)
10. [Releases · openclaw/openclaw · GitHub](https://github.com/openclaw/openclaw/releases)
11. [OpenClaw 2026: Latest Version, Changelog & Updates - Petronella Cybersecurity News](https://petronellatech.com/blog/openclaw-ai-agent-guide-2026/)
12. [Package openclaw · GitHub](https://github.com/openclaw/openclaw/pkgs/container/openclaw)
13. [API usage and costs · OpenClaw](https://docs.openclaw.ai/reference/api-usage-costs)
14. [Token Use and Costs](https://openclaw-ai.com/en/docs/reference/token-use/)
15. [lobster/package.json at main · openclaw/lobster · GitHub](https://github.com/openclaw/lobster/blob/main/package.json)
16. [Releases · openclaw/lobster](https://github.com/openclaw/lobster/releases)
17. [Lobster · OpenClaw](https://docs.openclaw.ai/tools/lobster)
18. [GitHub - openclaw/lobster: Lobster is a Openclaw-native workflow shell: a typed, local-first “macro engine” that turns skills/tools into composable pipelines and safe automations—and lets Openclaw call those workflows in one step.](https://github.com/openclaw/lobster)
19. [Hermes Agent v0.19.0 — The Quicksilver Release](https://hermes-agent-lab.com/releases/v0-19-0/)
20. [Hermes Agent: The Practitioner's Reference (2026)](https://blakecrosley.com/guides/hermes)
21. [GitHub - NousResearch/hermes-agent: The agent that grows with you](https://github.com/nousresearch/hermes-agent)
22. [Hermes Agent Documentation - Nous Research](https://hermes-agent.nousresearch.com/docs)
23. [What Is NanoClaw? The Small OpenClaw Alternative That Runs Agents in Containers — Munder Difflin Blog](https://munderdiffl.in/blog/what-is-nanoclaw/)
24. [NanoClaw - Secure AI Agent for WhatsApp, Telegram & More](https://nanoclaw.dev/)
25. [RepoCloud](https://repocloud.io/details/NanoClaw/)
26. [What Is ZeroClaw? A Plain-English Guide to the Rust AI ...](https://zeroclaw.net/blog/what-is-zeroclaw)
27. [zeroclaw: AI agents and LLM tools](https://goastro.website/forks/ai-agents/zeroclaw-labs-zeroclaw/)
28. [ZeroClaw — command-line utility in Rust // Lib.rs](https://lib.rs/crates/zeroclaw)
29. [GitHub - zeroclaw-labs/zeroclaw: Fast, small, and fully autonomous AI personal assistant infrastructure, any OS, any platform — deploy anywhere, swap anything 🦀 · GitHub](https://github.com/zeroclaw-labs/zeroclaw)
30. [GitHub - elev8tion/zeroclaw: Zero overhead. Zero compromise. 100% Rust. Autonomous agent runtime. · GitHub](https://github.com/elev8tion/zeroclaw)
31. [Letta](https://rywalker.com/research/letta)
32. [Letta Code: Memory-First Coding Agent Harness](https://innfactory.ai/en/ai-harness/letta-code/)
33. [Letta (MemGPT) — The Memory-Native Agent Framework — ChatForest](https://chatforest.com/reviews/letta-memgpt-stateful-agent-framework/)
34. [Release v2026.1012.0 · paperclipai/paperclip · GitHub](https://github.com/paperclipai/paperclip/releases/tag/v2026.1012.0)
35. [Paperclip](https://paperclip.ing/)
36. [What Is Paperclip AI? Features, Pricing, and Alternatives Compared \[2026\]](https://contabo.com/blog/what-is-paperclip-ai/)
37. [Paperclip Cheatsheet — CLI, Concepts & Quick Reference](https://paperclipcheatsheet.com/)
38. [Paperclip Review 2026: Run an AI Agent Company - ToolCenter](https://www.toolcenter.ai/en/articles/paperclip-review-2026)
39. [Paperclip review: open-source AI agent runtime tested (2026)](https://www.eesel.ai/blog/paperclip-ai-review)
40. [How to Run AI Agents Unattended Overnight — Paperclip](https://paperclip.ing/blog/run-ai-agents-unattended-overnight/)
41. [OpenClaw Cost Control: Cut API Spending, Keep Your Agent](https://www.stack-junkie.com/blog/openclaw-cost-control-manage-api-spending-without-killing-your-agent)
42. [GitHub - taslim/nanoclaw: A lightweight alternative to Clawdbot / OpenClaw that runs in containers for security. Connects to WhatsApp, has memory, scheduled jobs, and runs directly on Anthropic's Agents SDK · GitHub](https://github.com/taslim/nanoclaw)
43. [Session-logs - OpenClaw AI Agent Skill](https://llmbase.ai/openclaw/session-logs/)
44. [Openclaw Audit Logging: Compliance and Monitoring Configuration](https://sfailabs.com/guides/openclaw-audit-logging)
45. [paperclip-docs/docs/guides/org/agents.md at main · paperclipai/paperclip-docs · GitHub](https://github.com/paperclipai/paperclip-docs/blob/main/docs/guides/org/agents.md)
46. [Usage tracking · OpenClaw](https://docs.openclaw.ai/concepts/usage-tracking)
47. [Curator](https://hermes-agent.lzw.me/docs/en/user-guide/features/curator)
48. [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
49. [Session Management - OpenClaw Documentation](https://open-claw.blog/docs/session.html)
50. [Security - OpenClaw](https://github.com/openclaw/openclaw/security)
51. [Akshay 🚀 on X: "self-evolving skills in Hermes agent. i found this to be the most powerful feature in Hermes. the agent doesn't just solve problems, it remembers how it solved them. memory handles facts, and skills handle procedures. the difference matters because knowing that a Kubernetes pod… / X](https://x.com/akshay_pachaar/status/2056050422872465775?lang=en)
52. [Top 10 Hermes Agent Skills for 2026: Unlock AI Potential](https://techjacksolutions.com/ai-tools/hermes/best-hermes-skills/)
53. [Teknium 🪽 on X: "Introducing Hermes Curator! The new system built in to Hermes Agent now helps you keep your skills that the self improvement loop creates in check, by consolidating and pruning automatically. The curator does multiple things: - keeps track of how often you use each skill, wh… / X](https://x.com/Teknium/status/2049717907664581067)
54. [Curator | Hermes Agent](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)
55. [openclaw ai agent setup security cost](https://genaiunplugged.substack.com/p/openclaw-ai-agent-setup-security-cost)
56. [Letta Agent Review (2026): Pricing & Alternatives](https://www.stork.ai/en/letta-agent)
57. [SkillsBench Review - by Tao Dong - Evaluating Evals](https://evaluatingevals.substack.com/p/skillsbench-review)
58. [9 CVEs in 4 Days: What Hermes Agent Enterprises Must Learn](https://labs.cloudsecurityalliance.org/research/csa-research-note-hermes-agent-cves-20260504-csa-styled/)
59. [Hermes Agent Security Risks: 6 Threats to Know](https://aurpay.net/aurspace/hermes-agent-security-risks-crypto-2026/)
60. [How To Run OpenClaw 24/7 For Under \$10/Month (VPS Setup Guide)](https://medium.com/@0xmega/how-to-run-openclaw-24-7-for-under-10-month-vps-setup-guide-d3a6126a9588)
61. [OpenClaw Hit 250K GitHub Stars, Then 20% of Its Skills Were Found Malicious](https://particula.tech/blog/openclaw-security-crisis-malicious-ai-agents)
62. [OpenClaw vs. Hermes Agent: An Honest Comparison of the Two Dominant AI Agent Frameworks of 2026](https://innfactory.ai/en/blog/openclaw-vs-hermes-agent-comparison/)
63. [OpenClaw Security Guide: CVE-2026-25253, Malicious Skills, and 40+ Fixes](https://www.bitdoze.com/openclaw-security-guide/)
64. [OpenClaw AI: Security Risks and Why to Uninstall It](https://www.immersivelabs.com/resources/c7-blog/openclaw-what-you-need-to-know-before-it-claws-its-way-into-your-organization)
65. [OpenClaw Security Risks: Findings, Fixes, Controls](https://www.trainmyagent.com/resources/openclaw-security-risks)
66. [Hermes Agent vs OpenClaw: Which AI Agent Framework Wins in 2026?](https://hackernoon.com/hermes-agent-vs-openclaw-which-ai-agent-framework-wins-in-2026)
67. [Securing Hermes Agent: Complete Guide 2026](https://techjacksolutions.com/ai-tools/hermes/securing-hermes-agent/)
68. [Running Hermes on a Personal or Work Machine](https://hermes-agent.nousresearch.com/docs/guides/secure-hermes-on-a-work-machine)
69. [Security](https://hermesagent.org.cn/en/docs/user-guide/security)
70. [Hermes Agent Permissions & Control Model, Explained](https://agenticcontrolplane.com/controls/hermes)
71. [Security and Command Approval](https://deepwiki.com/NousResearch/hermes-agent/5.4-code-execution-and-subagents)
72. [How Much Does OpenClaw Cost? (2026 Real Numbers)](https://kilo.ai/openclaw/how-much-does-it-cost)
73. [I Burned \$100 in One Night on OpenClaw — Here's How to Prevent It](https://clawcap.co/blog/burned-100-dollars-openclaw)
74. [OpenClaw Cost Guide: BYOK Models, Usage Patterns, and How to Cut Spend - Macaron](https://macaron.im/blog/openclaw-cost-guide)
75. [How Much Does OpenClaw Cost per Month? Pricing Breakdown 2026](https://www.sentisight.ai/how-much-openclaw-cost-per-month/)
76. [How to reduce your OpenClaw API costs by 90% or more - LumaDock](https://lumadock.com/tutorials/openclaw-cost-optimization-budgeting)
77. [session-logs](https://skills.pub/fr/skills/openclaw-openclaw-session-logs)
78. [OpenClaw Meets AWS: End-to-End Testing and Deployment - DEV Community](https://dev.to/aws-builders/openclaw-meets-aws-end-to-end-testing-and-deployment-1ig1)
79. [How I Built a Deterministic Multi-Agent Dev Pipeline Inside OpenClaw (and Contributed a Missing Piece to Lobster) - DEV Community](https://dev.to/ggondim/how-i-built-a-deterministic-multi-agent-dev-pipeline-inside-openclaw-and-contributed-a-missing-4ool)
80. [GitHub - goldmar/openclaw-code-agent: A stateful coding agent plugin for OpenClaw · GitHub](https://github.com/goldmar/openclaw-code-agent)
