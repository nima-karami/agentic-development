# Can an open-source assistant runtime host a software factory?

**Research snapshot: 2026-10-22, America/Toronto.** In this report, **verified** means I found the claim in a project’s own repository, documentation, release notes, security advisory, or an academic primary source; **reported** means it comes from an issue author, independent security researcher, news report, or user account; **unverified** means I could not establish it from the sources reviewed. Versions and project status are dated because several of these projects are changing extraordinarily quickly.

## Executive answer

**[verified · 2026-10-22] None of the always-on assistant runtimes reviewed can safely host the factory *as the authoritative conductor* without you building the scarce part you were trying not to build.** OpenClaw, Hermes, Moltis, ZeroClaw, NanoClaw, Nanobot, Letta and Agent Zero are good at the agent-runtime layer: conversations, channels, sessions, tools, memory, cron, model routing and, increasingly, sandboxing. They do **not** natively provide your combination of system-owned deterministic stage gates, hard per-stage/per-run spend cut-offs, an independent item→stage→attempt→evidence ledger, and stage-scoped/release-separated credentials. OpenClaw is particularly illustrative: it now has a sophisticated gateway, durable state, cost reports and security policy, but its own security model says a Gateway is one trust boundary, while your factory requires several mutually constrained trust domains. citeturn23search0turn23search13turn15search0

**[verified · 2026-10-22] The two projects closest to the missing “spine” are not really personal-assistant runtimes.** Paperclip is becoming an agent control plane with task locks, run history, budgets, scoped connections, approvals, evals, versioned skills and rollback; Archon has explicitly become a deterministic/repeatable coding-workflow engine with durable workflows and an SDLC pack. Paperclip nevertheless fails your strongest budget requirement today: a documented reproduction showed `hardStopEnabled` allowed a $0.50 budget to reach $5.11 because the current run was only costed after completion. Archon, meanwhile, is a workflow/harness system rather than the always-on personal operator you were hoping to adopt. citeturn20search3turn20search1turn15search2

**[verified · 2026-10-22] The architecture I would actually ship is therefore (b), “runtime as front door.”** Use OpenClaw if ecosystem/channel breadth and integrations matter most, or Moltis if you value a smaller, security-oriented trusted runtime. Keep the factory’s gates, canonical state, spend authority, evidence ledger and release capability outside it. Paperclip is the most interesting candidate for the higher-level control plane, while Archon is the most directly relevant candidate for the deterministic SDLC/workflow layer. The assistant can tell the factory what you want and tell you what went wrong, but it should not be able to declare that its own work passed. citeturn20search8turn15search2turn19search8turn23search0

**[verified · 2026-10-22] Hermes changes the answer least, despite being the strongest “self-improving” example.** It really does have an automatic post-turn learning loop that can create/update memory and skills; current Hermes also supports staging those writes for human approval. But Hermes has already had a bug report in which that background reviewer was biased toward writing “learnings” and misclassified material between stores. More importantly, general 2026 evidence is hostile to blind self-improvement: SkillsBench found that one-shot self-generated skills provided no average gain, whereas curated skills improved average pass rate by 16.2 percentage points; later systems such as SkillRevise improve the picture precisely by adding execution, deterministic verification, iterative revision and selection. That is almost an empirical argument for the governance model already in your PRD. citeturn23search12turn23search14turn23search6turn22search0turn22search6

My ranking for the role you actually need is:

| Role | Best current choice | Why |
|---|---|---|
| Chat/operator front door | **OpenClaw** | Richest gateway/channel/model ecosystem; good session/cost/security tooling. citeturn15search0turn23search0turn23search13 |
| Security-first front door | **Moltis** | Small Rust server, explicit sandbox backends, auth/vault/scoped controls and observability; still explicitly alpha. citeturn18search0turn19search1turn19search8turn19search9 |
| Self-learning experimental operator | **Hermes** | The most real self-improvement loop of the group, now with write approval; governance is still weaker than your PRD. citeturn23search8turn23search12 |
| External agent control plane | **Paperclip** | Closest existing approximation to governance/record-keeping spine; hard budgets are not yet hard enough. citeturn20search3turn20search1 |
| Deterministic SDLC engine | **Archon** | Most directly aligned with deterministic/repeatable coding workflows and durable SDLC runs. citeturn15search2 |
| Stage worker | **Any of the above behind a contract** | Once the pipeline owns the contract, runtime-specific memory/chat semantics cease to be correctness-critical. |

## Runtime landscape and capability matrix

**[verified · 2026-10-22]** The inventory below distinguishes “open repository” from clean permissive licensing. In particular, AutoGPT Platform is under PolyForm Shield rather than an OSI-style permissive licence, even though Classic and other repository material remain MIT. Kortix’s current licensing/white-label story is sufficiently non-standard and has changed enough that I would require a licence review before making it infrastructure. citeturn21search1turn2search2turn8search2

| Runtime | Licence and current release | Maintainer/activity | Runtime shape, cloud and models | Native cost accounting |
|---|---|---|---|---|
| **OpenClaw** | **MIT**; current train **2026.10.3**; **2026.9.33** extended-stable shipped 2026-10-15. **Verified.** citeturn15search0 | OpenClaw Foundation/community; highly active. Current maturity scorecard rated the project overall 68%, with alpha quality / beta completeness as of 2026-09-19. **Verified.** citeturn23search9 | Persistent Gateway/daemon; many chat channels; tools/plugins/skills, memory, sessions, cron and delegated work; model/harness plugins are swappable. Runs locally or on servers; hardened remote exposure is documented. **Verified.** citeturn4view0turn23search0 | **Yes, accounting; no hard spend gate.** Transcript-derived tokens and estimated cost can be broken down by provider, model, agent, channel and token type. **Verified.** citeturn23search13turn23search5 |
| **Hermes Agent** | **MIT**; **v0.22.3**, released **2026-10-21**. **Verified.** citeturn15search1 | Nous Research; extraordinarily active release train. **Verified.** citeturn15search1turn23search8 | CLI/gateway/desktop agent; channels, tools, memory, searchable history, skills, cron, sub-agents and plugin system. Execution backends have included local, Docker, SSH, Singularity and cloud/sandbox services. Multi-provider. **Verified.** citeturn23search8turn10search0 | **Partial.** Current releases expose provider/subscription usage information, but I did not find a documented, immutable per-factory-stage cost ledger or spend authority. **Unverified for exact PRD fit.** citeturn15search1 |
| **Moltis** | **MIT**; **20261019.01**, released **2026-10-19**. **Verified.** citeturn18search0turn18search1 | moltis-org / Fabien Penso and contributors; active through October. **Verified.** citeturn18search1turn18search8 | Single Rust personal-agent server; memory, messaging, MCP, tool policies and multiple providers. Docker/Podman, Apple Container, WASM, Vercel and Daytona sandbox choices; explicit cloud/VPS documentation. **Verified.** citeturn19search1turn19search3turn19search11 | **Tokens yes; cost no.** Moltis deliberately exports model/token observations and lets Langfuse infer cost; it does not compute its own cost. **Verified.** citeturn19search4turn19search16 |
| **ZeroClaw** | Dual **MIT/Apache-2.0**; **v0.8.6**, released **2026-10-18**. **Verified.** citeturn16search0turn4view2 | ZeroClaw Labs; repo identifies original creator and current project leadership; 0.8.6 alone covered hundreds of commits and dozens of contributors. **Verified.** citeturn16search0 | Rust daemon/CLI, channels and WebAssembly plugin host, tools, providers, live configuration/events and agent lifecycle now owned by daemon; SOP/run-control work has been expanding. **Verified.** citeturn16search0turn8search11 | I did not verify a native authoritative per-request dollar ledger suitable for the factory. **Unverified.** |
| **NanoClaw** | **MIT**; **v2026.10.0**, released **2026-10-09**. **Verified.** citeturn17search2turn17search3 | NanoCo / `nanocoai`, originated by Gavriel Cohen and contributors; actively developed. **Verified.** citeturn17search2 | One host coordinating per-agent-group containers, memory and schedules. Claude Agent SDK is native; Codex, OpenCode and Ollama/provider variants are supplied as installable skills/modules. Channels are likewise “skills over features.” **Verified.** citeturn17search2turn17search1 | No factory-grade cost ledger or hard spend controller established from primary material reviewed. **Unverified.** |
| **Nanobot** | **MIT**; **v0.3.5**, released **2026-09-15**. **Verified.** citeturn16search1 | HKUDS; maintainers listed as Xubin Ren and Yongru Chen. **Verified.** citeturn16search1 | Python Gateway owns execution, sessions, tools, memory and security for browser/TUI/chat; supports automations, MCP, multiple models/providers and multi-agent workflows. Optional OS sandbox mechanisms. **Verified.** citeturn16search1turn8search9 | Per-round context/token visibility exists; I did not establish an authoritative dollar-spend controller. **Unverified.** citeturn16search1 |
| **Letta / Letta Code** | **Apache-2.0** project family; Letta Code **v0.34.19** was current when read on **2026-10-22**. **Verified.** citeturn23search2turn6search8 | Letta; active Code and Agent SDK lines. **Verified.** citeturn23search2turn6search12 | Stateful-agent harness centred on durable memory/identity. Agents can run interactively or always-on and can rewrite memory, skills, prompts and even the harness via “mods”; chat integrations are available. **Verified.** citeturn23search2 | No hard per-stage/per-run spend enforcement matching the requirement was established. **Unverified.** |
| **Paperclip** | **MIT**; **v2026.1012.0**, released **2026-10-12**. **Verified.** citeturn20search0turn20search8 | Paperclip Labs and large contributor base; active. **Verified.** citeturn20search8 | Node server + React control plane for teams of agents: tasks, heartbeats, budgets, permissions, scoped secrets, skills/evals, approvals, run history, sandbox adapters and multiple coding agents/harnesses. As of 2026.1012, outside assistants can attach over MCP as authenticated people. **Verified.** citeturn20search0turn20search3 | **Yes, but not a reliable in-run hard stop.** Company/agent/project costs and limits are native; issue #11276 demonstrates overshoot until a run ends. **Reported · 2026-08-12.** citeturn20search1 |
| **AutoGPT Platform** | `autogpt_platform/`: **PolyForm Shield**; Classic/rest mostly **MIT**. Platform beta **v0.8.4**, released **2026-10-14**. **Verified.** citeturn21search0turn21search1 | Significant Gravitas; active commercial/open-repository platform. **Verified.** citeturn21search1 | Visual graph/workflow platform, scheduled/triggered agents, Copilot/chat, blocks, integrations and hundreds of models. Self-hosting is available without a licence fee, but that does not make the Platform licence permissive. **Verified.** citeturn21search1 | Run/turn charging, wallet and cost caps exist in platform semantics; v0.8.4 fixed several cost-attribution bugs. Exact hard stage-budget guarantees were not established. **Verified/Unverified fit.** citeturn21search0 |
| **Agent Zero** | **MIT**; **v2.14**, released **2026-10-13**. **Verified.** citeturn2search1turn7view1 | Agent Zero project / Agent Zero s.r.o.; active. **Verified.** citeturn7view1 | Dockerized agent computer with browser/terminal, projects, skills/plugins, subagents and host bridge; LiteLLM-based model access. VPS deployment is documented. **Verified.** citeturn2search5turn16search7 | No authoritative hard budget or factory cost ledger established. **Unverified.** |
| **Kortix / Suna** | Current project is branded **Kortix**. Licence story is **ambiguous enough to treat as a procurement risk**: current official material talks about remaining open source while also describing separate white-label terms/provider conditions; older Suna material/forks reported Apache-2.0. **Reported disagreement · 2026-10-22.** citeturn8search2turn2search2 | Kortix team; current release line observed around **v0.14.4**. **Verified release line; date not confidently established.** citeturn8search6 | AI operating environment with agents, skills, company memory and connectors; notably gives sessions isolated cloud computers/branches and lands changes through human-approved change requests. Self-host/VPS path documented. **Verified.** citeturn8search2turn8search29 | Some budget/usage features exist; exact factory hard-stop semantics were not established. **Unverified.** |
| **Archon** | **MIT**; **v0.12.1**, released **2026-10-17**. **Verified.** citeturn15search2turn2search3 | coleam00/Archon community; very active 2026 rewrite/release train. **Verified.** citeturn15search2 | Now explicitly a harness/workflow builder for deterministic, repeatable coding. YAML workflows combine agents/scripts/decisions; bundled SDLC flows, server, GitHub forge and Slack chat plugins. v0.12.1 supports durable workflows even without a DB. **Verified.** citeturn15search2turn2search31 | No comprehensive dollar hard-budget controller matching your PRD established. **Unverified.** |
| **PicoClaw** | **MIT**; **v0.3.1**, released **2026-07-03**. **Verified.** citeturn8search0turn8search4 | Sipeed/community. **Verified.** citeturn8search0 | Very small Go personal-assistant runtime/gateway, multi-channel, skills and provider support, deliberately optimized for tiny footprint. **Verified.** citeturn8search0 | No factory-grade cost ledger established. **Unverified.** |

The capability matrices use your four-way distinction strictly:

**N — native:** the runtime substantially satisfies the requirement as stated.  
**P — plugin/extension:** feasible without forking, but you must supply trusted non-agent logic. A prompt-only “skill” does **not** count as a deterministic gate.  
**E — external:** the authoritative mechanism should live outside the runtime.  
**C — contradicts:** default architecture is materially at odds with the requirement.

All matrix judgements are **verified synthesis · 2026-10-22** from the cited primary material; a judgement is about the *full wording of your requirement*, not whether the project has something with a similar name.

| Runtime | Deterministic gated pipeline | Durable state / isolated items | Hard run/stage budget | Independent run/evidence record | Least privilege / release separation |
|---|---|---|---|---|---|
| **OpenClaw** | **P** — shell outcomes/exit status can be captured, but stage advancement is not a native system-owned SDLC primitive. citeturn5search16 | **P** — durable Gateway session/state exists, now heavily SQLite-backed; factory item/stage isolation is yours. citeturn23search7 | **E** — usage/cost accounting is rich, but no verified spend kill switch. citeturn23search13 | **P** — transcripts are durable, but are conversations/tool records, not the required evidence DAG. citeturn5search10 | **E/P** — sandbox/tool profiles help, but docs explicitly define one trust boundary per Gateway; split privileged release into another boundary. citeturn23search0 |
| **Hermes** | **P** — plugin/tool control can implement gates; agent skills themselves are not trustworthy gates. | **P** — durable sessions/memory and profiles, but factory-item semantics need another layer. citeturn15search1turn23search1 | **E** — turn/iteration controls are not monetary hard-stop authority. | **P** — session history/JSONL-style surfaces can feed a ledger, but no exact evidence hierarchy was found. | **E/P** — docs/security work increasingly treats OS/container isolation as the important boundary; stage credential brokerage remains yours. citeturn10search0 |
| **Moltis** | **P** — `BeforeToolCall`/tool policy and execution outcomes are useful substrate, not an SDLC state machine. citeturn19search17 | **P** — persistent sessions with per-session/per-command sandbox scopes; factory item model still custom. citeturn19search2 | **E** — tokens exported, dollars deliberately not computed. citeturn19search4 | **P** — OTEL and persistent state are good raw material; evidence DAG is not native. | **P** — strong sandbox/vault/scoped-key ingredients, but separate release authority must still be modelled explicitly. citeturn19search8 |
| **ZeroClaw** | **P** — daemon-owned run/SOP control is promising but not your nine-stage gate protocol. citeturn16search0turn0search6 | **P** — daemon now owns agent/config/event lifecycle; product-item isolation is custom. | **E** | **P** | **P/E** |
| **NanoClaw** | **P** — scheduled tasks even support optional script gates, but full factory progression is not native. citeturn17search1 | **P** — per-agent-group filesystem, memory and container is a strong isolation primitive. citeturn17search1 | **E** | **P** | **P** — containers are a meaningful boundary; release credentials still need a separately scoped service. |
| **Nanobot** | **P** | **P** — persistent Gateway sessions and recovery are native. citeturn16search1 | **E** | **P** | **P/E** — optional sandboxing, rather than stage capability separation, is the main primitive. |
| **Letta Code** | **P** | **P** — durable identity/memory is one of Letta’s strongest capabilities; item/stage semantics are not. citeturn23search2 | **E** | **P** | **E/P** |
| **Paperclip** | **P** — enforced review/approval gates exist, but your “stage advances solely from captured deterministic gate result” still needs a workflow adapter. citeturn20search3 | **N** — tasks, runs, locks, persistent context and crash-safe workspace recovery are control-plane concepts. citeturn20search0turn20search3 | **E for your requirement** — native budgets exist but demonstrated in-flight overshoot makes them insufficient as the final monetary authority. citeturn20search1 | **P/N** — run history, artifacts, activity, task threads and action attribution are close, but your exact immutable item→stage→attempt→evidence contract should be explicit. citeturn20search3turn20search7 | **P** — scoped secrets, grants and permission boundaries are native; release should still be its own capability. citeturn20search0turn20search3 |
| **AutoGPT Platform** | **P** — graph/node control can encode deterministic branches, but is not your prescribed trusted SDLC state machine. | **P/N** — workflow/run state is native. citeturn21search1 | **E** — platform has cost caps, but exact hard per-stage semantics were not demonstrated. citeturn21search0 | **P** | **P** |
| **Agent Zero** | **P** | **P** | **E** | **P** | **P/E** — Docker isolates the agent computer, but not factory role/capability semantics. citeturn2search5 |
| **Kortix** | **P** — human-approved change requests are real control-plane gates, but they are not deterministic test exit-code gates. citeturn8search2 | **N/P** — isolated session computers and branches are unusually well aligned with concurrent product items. citeturn8search2 | **E** | **P** | **P** |
| **Archon** | **N/P** — deterministic/repeatable YAML workflows with scripts/decisions are the closest native substrate; bind each stage transition explicitly to a verifier result. citeturn15search2turn2search3 | **N** — v0.12.1 explicitly supports durable workflow state, including DB-less operation. citeturn15search2 | **E** | **P** | **P** — recent release work explicitly refuses some implicit credential borrowing and separated provider binaries, a good design direction. citeturn15search2 |
| **PicoClaw** | **P** | **P** | **E** | **P/E** | **E/P** |

The rest of the requirement set is similarly revealing:

| Runtime | Structured failure notifications | Required dashboard | Harness/model independence | Controlled self-improvement | Owner direction while runs continue | Web/desktop/agentic/MCP reach |
|---|---|---|---|---|---|---|
| **OpenClaw** | **P** — channels are excellent; factory incident payload is yours. | **P** — strong usage/cost views, no native improvement queue/hotspot model. citeturn23search13turn23search15 | **N** — model and harness plugins are first-class. citeturn15search0 | **P** — editable skills/memory, but no mandatory eval→approval→promotion loop. | **N** | **N/P** — channels, browser/nodes/MCP/plugins provide broad reach. |
| **Hermes** | **P/N** | **P** | **N** | **P** — unusually close now that skill/memory writes can be staged for approval, but mandatory eval-corpus promotion is absent. citeturn23search12turn23search4 | **N** | **N/P** |
| **Moltis** | **P** | **P** — Prometheus/OTEL can provide model/provider usage; factory analytics are custom. citeturn19search16 | **N** | **P/E** — memory/skills exist; no Hermes-style verified autonomous eval loop. | **N** | **N/P** — MCP and remote sandboxes are strong foundations. citeturn19search13 |
| **ZeroClaw** | **P** | **P** | **N** | **P** | **N** | **N/P** |
| **NanoClaw** | **P** | **E** — deliberately no monitoring/debugging UI in its minimal philosophy. citeturn17search2 | **P** — Claude is native; alternatives are installed as skills. citeturn17search2 | **P** — the agent can alter/extend its fork, but that is code modification, not governed learning. | **N** | **P** |
| **Nanobot** | **P** | **P** — context/token visibility exists, factory KPI surface does not. | **N** | **P/E** | **N** | **N/P** — MCP and multi-agent workflows native. citeturn16search1 |
| **Letta Code** | **P** | **E/P** | **N/P** | **C/P** — deliberate self-rewriting of prompts/skills/harness is attractive for experimentation but directly conflicts with your “protected gates/evals + explicit promotion” unless constrained externally. citeturn23search2 | **N** | **P** |
| **Paperclip** | **N/P** — blockers, threshold alerts, approvals and task state are native. | **P/N** — cost/work dashboards are strong; your stage/model/product optimization views need schema work. citeturn20search3 | **N** — explicitly bring-your-own agent/runtime/model. citeturn20search0turn20search3 | **P/N** — evals, saved test runs, skill versions/restore and governed skill updates are unusually close; make eval pass + human approval non-bypassable. citeturn20search0turn20search3 | **N** | **N/P** |
| **AutoGPT Platform** | **N/P** | **P/N** | **N** | **P/E** | **N** | **N/P** |
| **Agent Zero** | **P** | **E/P** | **N** via LiteLLM-style backend abstraction. | **P** | **N** | **P** |
| **Kortix** | **P/N** | **P** | **N** | **P** — branch/change-request approval is a useful pattern for proposed self-changes. citeturn8search2 | **N** | **N/P** |
| **Archon** | **P** — Slack/attention queue integration is available. citeturn15search2 | **P** | **N/P** — current provider-plugin architecture deliberately decouples harnesses. citeturn15search2 | **E** — workflow definitions should be treated as controlled code, not self-edited runtime memory. | **P** — chat plugin exists, but this is not primarily an always-on personal assistant. | **N/P** |
| **PicoClaw** | **P** | **E** | **N/P** | **P** | **N** | **P** |

The most important distinction in those tables is **“can be written as a plugin” versus “already gives you the spine.”** OpenClaw could certainly host a large trusted plugin that implements a run state machine, writes JSONL evidence, brokers credentials, verifies exit codes and enforces promotion. Hermes could be extended similarly. But once that extension owns the gates, records, budgets and policy, you have in substance built the factory runtime inside someone else’s process. The hypothesis “adopt a runtime instead of building one” has then failed even though the integration technically works.

## Self-improvement: what “learns from experience” actually means

**[verified · 2026-10-22] Hermes is the one project in this set for which “self-improving” is a concrete runtime mechanism rather than mostly branding.** Its documentation says memory stores compact durable knowledge and skills store longer procedures; after turns, a background self-improvement review can decide to save memory or create/update a skill. The current write-approval mechanism can stage those mutations so the user can inspect, approve or reject them. Skills can also be protected/pinned, although an issue filed in May shows that pin/protection state is profile-local rather than a clean globally versioned promotion model. citeturn23search12turn23search14turn23search4turn23search1

The trigger is not mystical: **[verified · 2026-07-26]** Hermes has a configurable skill-creation nudge interval; setting it to zero disables the background trigger, and enabling `skills.write_approval` sends background skill mutations to a pending area for approval. citeturn23search20

There is already a cautionary failure mode. **[reported · 2026-05-22]** issue #30220 described the built-in reviewer as being prompted to actively find a skill update, discouraging “nothing to save,” and consequently putting information into the wrong memory/skill/user stores. That is a real example of an attempted learning mechanism degrading the runtime’s own persistent knowledge rather than improving it. The issue was subsequently closed through project work, but it demonstrates exactly why the learning loop cannot also be its own judge. citeturn23search6

**[verified · 2026-06-11]** Hermes materially improved its governance during 2026: project maintainers documented that memory/skill write-approval now intercepts foreground and background mutations and provides pending/diff/approve/reject flows. That makes Hermes substantially more attractive for experimentation than it was early in the year. It still does **not**, from the material reviewed, give you the stronger policy “a proposed skill change must pass corpus X at threshold Y, the evaluator is protected from the agent, then a human must approve the exact digest that passed.” citeturn23search4

**[verified · 2026-10-22] Letta Code uses a broader and more aggressive meaning of learning.** Its own description says agents evolve by rewriting their memory, skills, prompts and even the harness itself through mods. This is a powerful research/product model, but it is almost the inverse of the software-factory trust model: your PRD deliberately wants the agent able to *propose* mutations while keeping gates and evals in a separately protected domain. Unless you put that boundary around Letta, the mechanism is self-configuration rather than controlled self-improvement. citeturn23search2

**[verified · 2026-10-22] OpenClaw’s persistence should not be confused with an evidence-backed automatic learning algorithm.** It has long-term memory, skills/plugins, sessions and an enormous extension surface, but I did not find a primary-source OpenClaw mechanism equivalent to Hermes’s automatic post-session skill-review loop that also evaluates and promotes improved skills. Its strength is that the runtime gives agents persistent things they can read and modify, not that it proves those modifications make the agent better. citeturn4view0turn23search0

**[verified · 2026-10-22] NanoClaw’s “self modification” is closer to agent-assisted software maintenance.** The runtime deliberately says “skills over features”: adding channels or alternative runtimes can copy implementation modules into your NanoClaw fork, and the native Claude-based agent has the tooling to modify/extend the codebase itself. That is useful for a personal agent, but a factory should treat the resulting code diff as an ordinary change request, not as trusted learning merely because the agent authored it. citeturn17search2

**[verified · 2026-10-22] Paperclip has the most factory-compatible ingredients for learning governance.** The project exposes evals and saved test runs, skill version history and restore, skill policies, approval/review machinery, and the October release states that agents can safely update company skills. Its development documentation also describes durable version pins and preservation of versions referenced by active/recovering runs. This is much closer to “candidate artefact → evaluated version → durable pin → rollback” than assistant memory is. citeturn20search0turn20search3turn20search7

But there is an important difference between **having all those components** and making the policy mandatory. **[unverified · 2026-10-22]** I did not establish that Paperclip currently makes it impossible for every kind of self-generated skill/config change to become active unless it first passes a designated regression corpus and then receives human approval on the same immutable digest. I would therefore treat FR-46–FR-50 as an extension, not as solved.

The independent research evidence supports that conservatism:

| Evidence | Result | Factory implication |
|---|---|---|
| **SkillsBench v1, Feb 2026** | Curated skills improved average pass rate by **16.2 percentage points** across its benchmark; self-generated skills provided **no benefit on average**. **Verified.** citeturn22search0turn22search1 | “Agent writes a skill, therefore retain it” is not an acceptable promotion rule. |
| **SkillsBench later revision, Jun 2026** | The self-generated condition remains separately evaluated in the current paper; the project’s current benchmark has expanded task packaging. **Verified.** citeturn22search5turn22search19 | Keep a fixed eval corpus and benchmark versions; do not infer improvement from the model’s narrative. |
| **SkillRevise, May–Sep 2026** | Execution-grounded, iterative revision with re-execution and verifier-based selection substantially outperformed one-shot skill creation; the paper reports SkillsBench success increasing from **36.05% to 61.63%** in its tested setting. **Verified paper result, not independent replication.** citeturn22search6turn22search10 | Self-improvement becomes plausible when the *verifier*, not the self-description, selects versions. |
| **SkillHEX, Aug 2026** | Reports improvements from bounded hypothesis-driven skill evolution under repeated evaluation. **Verified paper claim.** citeturn22search3 | Iteration can help, but only as an optimization loop around an external scoring signal. |
| **SkillLearnBench / SkillEvolBench, 2026** | New benchmarks explicitly measure continual skill learning and whether episodic experience can become reusable procedural knowledge. **Verified.** citeturn22search20turn22search23turn22search7 | This remains an active research problem, not a settled runtime feature. |

So I would implement “self-improvement” as an ordinary software supply chain:

`observed failure → proposed skill/gate/eval diff → isolated candidate version → regression + targeted evals → compare to incumbent → human approval → signed/pinned promotion → rollback pointer`

The learning agent can write the proposal. It should not own the score, evaluator corpus, promotion bit or history.

## Security and unattended operations

The security record matters more here than for a normal chatbot because an unattended software factory combines three unusually dangerous capabilities: it consumes adversarial content, executes code, and eventually needs access to a deployment path.

**[verified · 2026-10-22] OpenClaw’s current security documentation is unusually explicit about the limitation.** A Gateway is one trusted boundary. Mutually untrusted operators/agents should use separate Gateways, credentials and preferably OS users/hosts. The hardened guidance emphasizes loopback binding by default, authentication, sender pairing/allowlists, tool restrictions, sandboxing, network controls and the built-in `openclaw security audit`. This is good security engineering, but it also tells you not to use “one OpenClaw instance containing all factory roles” as a privilege boundary. citeturn23search0

OpenClaw has had substantial 2026 security churn. **[verified · 2026]** project advisories include CVE-2026-8305 affecting BlueBubbles webhook authentication, fixed in 2026.2.12; CVE-2026-100574 for an SSRF issue before 2026.8.1; and CVE-2026-100580 for a cron-policy case/bypass issue before 2026.7.1 that could turn attacker-steered agent behaviour into persistent command execution. citeturn9search0turn9search8turn9search16

There is also a supply-chain problem around skills. **[reported · 2026-06-23]** Palo Alto Networks Unit 42 summarized several early-2026 analyses of ClawHub, including Bitdefender estimates of malicious inventory and Koi’s identification of hundreds of malicious skills; Unit 42 also reported finding evasive malicious skills that remained available after marketplace scanning measures such as VirusTotal/ClawScan had been introduced. Exact counts vary between researchers and snapshots, so I would **not** use any single “X% of ClawHub is malicious” number as a stable fact. The durable conclusion is that installing an agent skill is executable-supply-chain intake, not prompt customization. citeturn9search2

**[reported · 2026-01-27]** security researcher Jamieson O’Reilly was reported to have found exposed Moltbot/OpenClaw deployments leaking private messages, credentials and API keys; maintainers issued a fix and publicly cautioned users against casual public exposure. I did not find a primary, current census that I am comfortable quoting as an authoritative number of exposed instances, so widely circulated exposure counts are intentionally omitted here. citeturn18news43

A further factory-specific issue is record hygiene. **[verified · 2026-10-22]** OpenClaw diagnostics perform secret masking, but its persisted conversational/tool transcripts are not generally a secret-redacted evidence store: documentation warns that arguments/results/conversation content can persist as supplied. A factory therefore cannot simply declare “the OpenClaw transcript is my FR-25–FR-30 record” while also promising NFR-10. An external evidence writer must select/redact what becomes durable evidence. citeturn5search10

**[verified · 2026-10-22] Hermes has also moved substantially toward explicit security policy.** Current guidance layers sender allowlists/pairing, dangerous-command approval, file-write restrictions, container isolation, MCP credential filtering and prompt-injection scanning. Its 0.21.6 release fixed an email sender-parsing case in which a crafted display name could pass an allowlist. citeturn10search0turn15search1

**[reported · 2026-08-03]** a Hermes GitHub issue documents a claimed real-world incident in which an unauthenticated Telegram DM attacker caused an exposed agent to install a backdoor/proxy. Because this is an issue report rather than a maintainer incident report or forensic publication, I treat the event as **reported rather than verified**; it is nonetheless exactly the failure mode that makes a long-lived release credential unacceptable inside a messaging agent. citeturn10search12

**[verified · 2026]** Hermes has also had a published CVE in its skills/injection guard path, and the project has repeatedly hardened authorization and isolation during the year. citeturn10search11

**[verified · 2026-10-22] Moltis has the strongest security-first design of the personal-runtime group I reviewed, but its own docs still call it alpha.** It offers human approval for dangerous commands, explicit sandbox backends, channel authorization, rate limiting, scoped API access, an encrypted-vault design and network/SSRF controls. Its deployment guide explicitly says not to expose an unauthenticated instance, and the main docs advise isolated environments, scoped/rotated secrets and strong network controls. citeturn19search8turn19search3turn19search9

Its changelog also records real security corrections: **[verified · 2026-09-02]** Moltis fixed session keys sharing sandbox containers/persisted homes and replaced shell-based remote node execution with structured, allowlisted process invocation. That is good evidence that the project is finding and tightening meaningful boundaries, but it also reinforces its own alpha designation. citeturn19search5

**[verified · 2026-10-22] NanoClaw’s major architectural advantage is that isolation is ordinary OS/container isolation rather than an LLM instruction.** Agent groups have separate workspaces/memory/containers and only explicitly supplied mounts. That makes NanoClaw a more attractive *worker* than a shared-host runtime. citeturn17search1

NanoClaw is not incident-free. **[reported/verified advisory · 2026]** its advisories have included authorization problems around approval/self-modification paths, including an `add_mcp_server` flow, plus later path/installer findings. These matter because NanoClaw intentionally makes code modification and feature installation part of the agent experience. citeturn10search3turn10search10turn10search26

**[verified · 2026-03-27] Nanobot had an especially relevant advisory: a zero-click indirect prompt-injection path through email could cause attacker-controlled content to reach an agent with system tools.** Its present deployment guidance recommends Docker or OS sandboxing, a dedicated limited user and avoiding root/sensitive-data deployment without review. citeturn8search16turn8search9turn8search32

**[verified · 2026-09/10] ZeroClaw fixed CVE-2026-101885 in v0.8.5, involving traversal of a plugin WASM path.** v0.8.6 subsequently moved further toward daemon-owned identity/runtime policy and tightened plugin/sandbox/credential boundaries. citeturn10search9turn10search25turn16search0

**[verified · 2026] Letta’s older server line had an information-disclosure advisory affecting LocalSandbox execution through 0.16.8: spawned processes could inherit the server environment, including sensitive database/API variables.** The current Letta Code line has moved substantially since that server architecture, so this should not be lazily described as a current v0.34.19 vulnerability; it is, however, a useful historical example of why “sandboxed command” is not equivalent to “stage has only its own credentials.” citeturn11search25turn23search2

**[verified · 2026] Kortix/Suna published fixes for XSS and broken-access-control issues during its rapid development.** Combined with its current isolated-computer/branch design, I view Kortix’s security ideas as interesting but not sufficiently settled for a privileged release control plane. citeturn8search10turn8search21turn8search2

**[verified · 2026-10-17] Archon v0.12.1 is a useful example of the kind of bug that matters in a factory.** v0.12.0 release binaries could cause provider processes started inside a target repository to load that repository’s `.env`, undoing Archon’s intended environment stripping and potentially changing which provider credential was used. v0.12.1 stopped release binaries/provider plugins from loading target-repository `.env`/`bunfig.toml`; the same release also tightened the rule that per-user runs without credentials refuse instead of borrowing the host login. citeturn15search2

### What unattended operation evidence actually exists

The evidence is far weaker than the feature lists.

**[reported · 2026-08-12] Paperclip has one of the best concrete long-running budget reports.** An operator reproduced a $0.50 company hard budget being exceeded by a single $5.11 run because current cost remained zero until the run completed. The author correctly notes that concurrency makes maximum overshoot worse. This is directly disqualifying for NFR-3 if Paperclip is your sole spend authority. citeturn20search1

**[reported · 2026-08-27] Paperclip issue #12304 provides unusually useful multi-week operational data.** On the reporter’s instance, Hermes-backed runs hitting `max_turns` grew from 1/30 in the week of August 3 to 52/217, or 24%, in the week of August 24, yet every one was recorded as `status=succeeded` / `stopReason=completed` because Hermes asked the model to summarize when the iteration budget was exhausted. The team consequently forwarded truncated work as successful for weeks. This is almost a textbook demonstration of why your gate cannot equal the worker’s reported status. citeturn20search2

**[reported · 2026-02-02] NanoClaw had a production incident caused by invoking its agent SDK without a `maxTurns` bound; the report describes 21 duplicate messages in 32 seconds.** This is a small incident, but it is direct evidence that “agent loop limits” must be enforced structurally rather than left to a conversational convention. citeturn0search19

**[reported · 2026-10-03] ZeroClaw dogfooding captured several ZeroCode processes left at roughly one CPU core after losing their terminal, on incidents observed October 2 and October 3.** That is not a model runaway, but it is useful unattended-runtime evidence: process lifecycle and cleanup failures remain mundane failure modes even in otherwise sophisticated agent systems. citeturn16search6

**[reported · 2025–2026] Agent Zero users have reported memory/index inconsistency severe enough to cause FAISS lookup errors and attempts to clear/rebuild memory.** This is anecdotal issue-tracker evidence, not a reliability benchmark. citeturn16search10

**[reported · 2026-01] OpenClaw/Moltbot users publicly described always-on personal deployments doing recurring daily tasks such as calendar/Notion/Todoist-derived audio recaps.** That establishes real continuous use, but it is not evidence of reliable unattended software release engineering, and the same early reporting emphasized credential exposure and prompt-injection risk. citeturn18news43

**[reported · 2026-04-12] Moltis has ordinary user reports of long model calls timing out before completion with self-hosted OpenAI-compatible backends.** Again, that is useful anecdote, not fleet reliability data. citeturn18search11

**[unverified · 2026-10-22] I did not find a credible standardized data set for “cost per unattended day” across these runtimes.** There are anecdotes and provider-specific bills, but not enough comparable primary evidence to responsibly state “OpenClaw costs $X/day” or “Hermes costs $Y/day.” Model choice, context growth, cron frequency, web/tool use and runaway behaviour dominate that number. Claims to a representative cost/day should therefore be treated skeptically.

**[unverified · 2026-10-22] I also did not find a strong independent report of any personal-assistant runtime completing the whole chain you defined—chat intent → spec → plan → implementation → independent review → deployed runtime QA → integration → production release → post-release observation—with external deterministic gates and a complete independently readable evidence record.** Archon now advertises an SDLC path extending from work intake through PR/merge, and Paperclip clearly runs coding teams and artifacts, but that is not evidence that the stronger factory contract has been demonstrated end-to-end. citeturn15search2turn20search3

### Is any of this acceptable for a runtime that holds release capability?

**[verified synthesis · 2026-10-22] No, not as a long-lived capability available to the conversational agent.** This is not an indictment of a specific implementation; it follows from their documented trust models and 2026 incident classes. A process that continuously consumes Telegram/email/web/repository content and can execute tools should not also hold an evergreen production-deploy secret. OpenClaw explicitly recommends separate Gateways for separate trust boundaries; Moltis recommends scoped secrets and isolated deployment; Hermes relies heavily on OS/container isolation; Nanobot has already demonstrated indirect prompt injection from email. citeturn23search0turn19search9turn10search0turn8search16

The release pattern should instead be:

`build/review agent → immutable candidate digest → external release gate → short-lived release identity scoped to that digest/environment → deploy service → credential expires`

The conversational runtime can request that transition and receive its result. It should not possess the credential that makes its own request authoritative.

## Architecture comparison

| Architecture | Requirements it satisfies well | Requirements it breaks or weakens | Project lock-in | Migration implications |
|---|---|---|---|---|
| **Factory inside the assistant runtime** | Excellent owner chat, notifications, cron, memory, tool dispatch and sub-agent UX. Models/harnesses are often swappable. OpenClaw/Hermes/Moltis can physically run a large amount of the work. citeturn23search8turn4view0turn18search0 | The hard parts become custom: system-owned stage state machine, hard spend cut-off, immutable evidence graph, protected gates/evals and release-capability isolation. OpenClaw’s single-Gateway trust model particularly conflicts with multi-boundary least privilege. citeturn23search0 | **High.** Stage state, conversations, memory semantics, plugin hooks and control flow become runtime-specific. A dead/relicensed project means extracting correctness-critical logic from its data/plugin model. | **A→B: high initially.** You must externalize stage IDs, retries, evidence, budgets and auth that were hidden in skills/sessions. Once externalized, migration becomes easy—which is another way of saying you have moved to architecture B. |
| **Runtime as front door; external factory owns truth** | Meets owner-direction/notification requirements while preserving independent deterministic gates, resumable run state, spend authority, evidence ledger and credential separation. You can replace the assistant without changing factory correctness. | Slightly more infrastructure and some duplicated state: conversation state in runtime, authoritative work state outside it. The integration must correlate chat requests with run/item IDs. | **Low.** Define a small command/event protocol: `create-item`, `status`, `cancel`, `approve`, `evidence`, `incident`. OpenClaw↔Moltis↔Hermes replacement is then an adapter change. | **B→A: technically easy but architecturally regressive.** You would move trusted state/gates back into runtime plugins and increase coupling. **A→B** is the worthwhile migration. |
| **Runtime as stage worker only** | Strongest harness/model independence and least privilege. Each worker gets one checkout, stage contract, credentials and budget; the pipeline believes only its files/stdout/exit status. Crashes/retries are tractable. | Loses much of the reason to choose a personal assistant: memory/channels/cron become peripheral. Owner chat needs another front door. | **Very low.** Worker contract can be as small as input manifest + workspace + permitted tools + output manifest + exit code. | Easy replacement. A Hermes/OpenClaw/Agent Zero stage can be swapped for Claude Code, Codex, OpenHands or a conventional script without changing factory state. |

**[verified synthesis · 2026-10-22] Architecture (b) is the recommendation.** Its key benefit is not just security; it makes the runtime *non-authoritative*. A malicious webpage, a bad skill, an LLM hallucination, a corrupted memory file or a runtime regression can make the assistant request foolish things, but it cannot falsify the deterministic gate that says whether a stage passed. That is exactly the property your PRD is organized around. The 2026 Paperclip `max_turns` misreport is a particularly clear empirical example of why worker completion semantics should not be the control-plane gate. citeturn20search2

The trade-off that would change my recommendation is very specific. I would reconsider architecture (a) if a runtime shipped all of the following as **system-owned primitives**, not agent conventions:

1. A versioned workflow state machine whose transitions can require signed/captured verifier results and cannot be advanced by model text.
2. Pre-authorized monetary budgets enforced synchronously across **all** model/sub-agent/harness calls, including nested external tools.
3. An append-only, exportable event/evidence schema independent of conversational transcripts.
4. Capability-brokered credentials, including a separately scoped release identity unavailable to ordinary build/review agents.
5. Immutable/protected gate and eval versions, with self-generated changes entering only through eval + approval + promotion.
6. Recovery semantics for a crash at every transition and concurrent item/attempt isolation.

**[verified synthesis · 2026-10-22] Paperclip plus Archon is substantially closer to that list than any assistant runtime alone.** Paperclip already owns control-plane concepts—tasks, locks, approvals, costs, permissions, history, versions and evals—while Archon owns increasingly deterministic workflow/provider execution. Neither solves hard monetary interruption by itself today. citeturn20search3turn20search1turn15search2

## Runtime verdicts and smallest viable composition

| Runtime | Verdict | Maturity / licence | Deciding gaps |
|---|---|---|---|
| **OpenClaw** | **Extend as front door; do not adopt as factory conductor.** | MIT; extremely active; own Sep 2026 scorecard still calls overall quality alpha / completeness beta. citeturn23search9turn15search0 | No native factory state machine or monetary kill switch; conversational transcript ≠ sanitized evidence ledger; one Gateway is one trust boundary. Its excellent cost accounting, channels and harness abstraction make it a very good operator shell. citeturn23search0turn23search13turn5search10 |
| **Hermes Agent** | **Extend experimentally as front door or worker; borrow its governed-learning ideas.** | MIT; v0.22.3; extremely active. citeturn15search1 | Best native learning loop, now with write approval, but no mandatory eval-backed promotion; history includes self-improvement misclassification and security incidents/reports. It still lacks authoritative gates/budgets/evidence. citeturn23search4turn23search6turn10search12 |
| **Moltis** | **Adopt/extend if security-first front door is more important than ecosystem breadth.** | MIT; 20261019.01; docs explicitly say alpha. citeturn18search1turn19search9 | Best-looking security architecture of the small personal runtimes—sandbox options, vault, approvals, rate limits, scoped API access—but no factory state machine, dollar cost engine, hard budget or evidence DAG. citeturn19search8turn19search4 |
| **ZeroClaw** | **Borrow/extend; reassess as daemon/SOP control plane matures.** | MIT/Apache-2.0; v0.8.6; very active. citeturn16search0 | Daemon ownership, plugins and SOP/run-control direction are promising, but it is still an autonomous-assistant infrastructure rather than the required audit/gate spine; 2026 plugin-path advisory is a reminder to keep extensions untrusted until admitted. citeturn10search25 |
| **NanoClaw** | **Adopt as a constrained worker, or borrow its isolation model.** | MIT; v2026.10.0. citeturn17search3 | Per-agent containers/workspaces are excellent. “Skills copy code into your fork” is intentionally simple but creates runtime drift; no hard spend, factory ledger/dashboard or deterministic SDLC control plane. citeturn17search1turn17search2 |
| **Nanobot** | **Borrow ideas; worker/front-door only.** | MIT; v0.3.5; project still relatively young. citeturn16search1 | Good gateway/session/MCP/automation surface, but zero-click email injection history and optional rather than foundational isolation make it unsuitable as the privileged spine. citeturn8search16turn8search9 |
| **Letta / Letta Code** | **Borrow the memory model; use experimentally as a worker, not as trusted conductor.** | Apache-2.0; very active current Code line. citeturn23search2 | Long-horizon state is compelling; self-rewriting memory/skills/prompts/harness is the wrong default authority model for protected factory gates. You would have to build the governance boundary around it. |
| **Paperclip** | **Adopt/extend as the external control plane.** | MIT; v2026.1012.0; active and broad. citeturn20search0turn20search8 | By far the closest to your record/governance/dashboard problem: locks, persistent work, run history, scoped secrets, approvals, costs, evals, skill versions. Do **not** trust its current “hard stop” as the only monetary breaker; issue #11276 is disqualifying for that requirement until semantics change. citeturn20search3turn20search1 |
| **AutoGPT Platform** | **Avoid as the foundational spine if “open-source/permissively forkable” is a hard requirement; borrow workflow ideas.** | Platform is PolyForm Shield, not MIT; beta v0.8.4. citeturn21search0turn21search1 | Feature-rich graph runtime and cost/approval UX, but licence lock-in is materially worse than the alternatives and the system is oriented toward a general automation platform rather than your evidence/gate contract. |
| **Agent Zero** | **Use as worker only / borrow desktop-agent environment.** | MIT; v2.14. citeturn7view1turn2search1 | Useful all-purpose agent computer, browser and subagents; no compelling answer to gates, hard budgets or independent evidence. |
| **Kortix / Suna** | **Borrow the isolated-branch + human-change-request architecture; do not foundation-bet until licensing is clarified.** | Fast-moving; current white-label/open-source messaging is not clean enough for this role without licence review. citeturn8search2turn2search2 | Isolated computers/branches and human-approved landing are unusually aligned with controlled code generation; deterministic verifier gates, hard budgets and licence certainty remain gaps. |
| **Archon** | **Adopt/extend as the SDLC/workflow layer.** | MIT; v0.12.1, 2026-10-17. citeturn15search2 | Best direct match to deterministic coding workflow execution, but it is not the always-on personal-runtime replacement hypothesized. Add hard budget/evidence/release policy rather than pretending a workflow engine is an auditor. |
| **PicoClaw** | **Avoid as factory foundation; borrow only lightweight-runtime ideas.** | MIT; v0.3.1. citeturn8search0turn8search4 | Its virtue is tiny deployment footprint, not governance. Almost every scarce factory requirement would be custom. |

### The smallest composition I would trust

**[verified synthesis · 2026-10-22]** The smallest credible composition that preserves the benefit of an assistant runtime is:

```text
                         owner
                           │
                           ▼
                 OpenClaw or Moltis
                 chat / alerts / status
                           │
                 commands + run IDs only
                           │
                           ▼
             ┌─────────────────────────┐
             │   factory control plane │
             │                         │
             │ canonical item state    │
             │ deterministic gates     │
             │ budgets / kill signals  │
             │ evidence/event ledger   │
             │ approvals / promotion   │
             └───────────┬─────────────┘
                         │ stage contract
                         ▼
            Paperclip / Archon / workers
            ┌────────┬────────┬────────┐
            │ spec   │ build  │ review │ ...
            └────────┴────────┴────────┘
                isolated workspaces
                         │
                  verifier outputs
                         │
                         ▼
                  evidence storage
                         │
                approved candidate
                         ▼
              separate release broker
              short-lived capability
```

I would interpret the named components as follows:

**OpenClaw or Moltis is replaceable.** It maps conversation to factory commands and factory events to messages. It never decides that a stage passed. OpenClaw is the pragmatic choice today for ecosystem breadth; Moltis is the cleaner choice if you deliberately want the assistant’s trusted codebase and sandbox story smaller. citeturn23search0turn19search17

**Paperclip is optional but increasingly compelling as the control-plane shell.** It already solves enough of work identity, locks, permissions, run history, costs, approvals and skill/eval management that extending it may now be cheaper than implementing those management surfaces yourself. Its budget implementation must sit behind a separate synchronous spend limiter until it can interrupt live spending rather than merely preventing the next run. citeturn20search3turn20search1

**Archon is a compelling execution layer for the coding SDLC.** Its 2026 rewrite is pointed almost directly at your workflow problem—repeatable YAML workflows, scripts/decisions, provider abstraction, durable runs and an SDLC pack—without pretending the LLM’s own assessment is a deterministic verifier. citeturn15search2turn2search31

**The release broker should be boring non-agent software.** No chat model needs the raw production token. It receives a candidate identity/digest and externally verified approval, obtains or activates a narrowly scoped credential, performs the release action, writes evidence, then destroys/expires capability.

If you insist on making an assistant runtime literally “host” all of this, **OpenClaw is the best engineering substrate and Moltis the best security-oriented substrate**, but the plugin you would need to write becomes the factory control plane itself. You have adopted their chat/session/tool shell, not avoided building the scarce spine.

## Open problems and source ledger

Several gaps remain unsolved across the surveyed projects.

**[verified synthesis · 2026-10-22] Hard monetary limits across nested agents remain surprisingly weak.** Token counters, max-turn limits and post-hoc cost dashboards are common; a controller that synchronously accounts for parent calls, delegated agents, harness-side provider calls, retries, cache/reasoning tokens and concurrent runs and can stop the whole tree before crossing a monetary ceiling is not. Paperclip’s reproduced overshoot is the clearest concrete example. citeturn20search1turn23search13turn19search4

**[verified synthesis · 2026-10-22] There is no widely adopted evidence interchange format for agent-produced software.** Projects have conversation transcripts, traces, task threads, artifacts, OTEL spans and run histories, but not a shared model for:

`item → stage → attempt → agent/harness/model → inputs → tool executions → diff/artifact → verifier → screenshots → cost → decision → supersession`

That missing schema is why replacing a runtime still tends to lose provenance even when source code itself is portable. Paperclip is closest conceptually; OpenClaw’s transcript and Moltis’s OTEL are useful lower-level inputs rather than the final record. citeturn20search3turn23search13turn19search4

**[verified synthesis · 2026-10-22] Prompt injection and release authority do not compose cleanly.** A runtime can sandbox code and authenticate users, but once the same agent both reads untrusted application/email/web/repository content and holds a deploy credential, the model is part of the authorization path. The 2026 Nanobot email advisory, Hermes Telegram incident report and OpenClaw’s own one-trust-boundary guidance all point in the same direction: promotion authority needs to be external to the conversational model. citeturn8search16turn10search12turn23search0

**[verified synthesis · 2026-10-22] Controlled self-improvement is becoming plausible, but “self-improving runtime” and “safe continuous optimization system” remain very different things.** SkillsBench is negative on naive one-shot skill generation; SkillRevise and related 2026 work become positive by introducing repeated execution and external verification. Hermes’s evolution from automatic writes toward optional human write approval is the same architectural movement in product form. citeturn22search0turn22search6turn23search4

**[unverified · 2026-10-22] Nobody in this survey has demonstrated the complete software-factory assurance case.** The market is converging from both sides—assistant runtimes are acquiring sandboxes, policy and observability, while orchestrators such as Paperclip and Archon are acquiring agent chat, skills, approval and durable execution—but I found no project that simultaneously makes deterministic verification, hard spend, tamper-resistant evidence, safe self-modification and least-privilege release first-class and mutually enforced.

### Source ledger

The following are the principal sources used above. “Primary” means project/research-owner material; issue reports are hosted on the primary repository but are labelled **reported** in the analysis when the claim comes from the reporter rather than a maintainer-confirmed finding.

| Date read / published | Source | Type and relevance |
|---|---|---|
| **2026-10-22** | OpenClaw releases; identifies current 2026.10.3 train and 2026.9.33 extended-stable release. citeturn15search0 | Primary |
| **2026-10-22** | OpenClaw security architecture and hardening guidance; one-trust-boundary-per-Gateway model. citeturn23search0 | Primary |
| **2026-10-22** | OpenClaw API usage/cost documentation; transcript-derived breakdown by provider/model/agent/channel. citeturn23search13 | Primary |
| **2026-10-22** | OpenClaw maturity scorecard, dated 2026-09-19. citeturn23search9 | Primary |
| **2026** | OpenClaw security advisories including CVE-2026-8305, CVE-2026-100574 and CVE-2026-100580. citeturn9search0turn9search8turn9search16 | Primary advisories |
| **2026-06-23** | Unit 42 analysis of malicious OpenClaw/ClawHub skills and marketplace scanning. citeturn9search2 | Secondary security research |
| **2026-01-27** | The Verge reporting on real-world Moltbot/OpenClaw use and exposed credentials/messages. citeturn18news43 | Secondary |
| **2026-10-21** | Hermes Agent v0.22.3 and release history. citeturn15search1 | Primary |
| **2026-10-22** | Hermes repository description of built-in learning loop and deployment model. citeturn23search8 | Primary |
| **2026-10-22** | Hermes skill self-improvement documentation: memory/skills division and staged writes. citeturn23search12 | Primary |
| **2026-10-22** | Hermes memory documentation describing post-turn background self-improvement. citeturn23search14 | Primary |
| **2026-06-11** | Hermes issue/maintainer confirmation of memory/skill write-approval implementation. citeturn23search4 | Primary maintainer statement |
| **2026-05-22** | Hermes #30220, background review misclassification/degradation report. citeturn23search6 | Reported issue |
| **2026-08-03** | Hermes issue describing claimed unauthorized Telegram compromise. citeturn10search12 | Reported incident |
| **2026-10-19** | Moltis release 20261019.01. citeturn18search1 | Primary |
| **2026-10-22** | Moltis sandbox documentation. citeturn19search1turn19search2 | Primary |
| **2026-10-22** | Moltis security architecture and alpha deployment guidance. citeturn19search8turn19search9 | Primary |
| **2026-10-22** | Moltis instrumentation: token/model export, explicit decision not to calculate cost. citeturn19search4 | Primary |
| **2026-09-02** | Moltis changelog security fixes for sandbox homes and node execution. citeturn19search5 | Primary |
| **2026-10-18** | ZeroClaw v0.8.6 release: daemon ownership, OIDC/plugin/runtime changes. citeturn16search0 | Primary |
| **2026** | ZeroClaw CVE-2026-101885 / plugin path traversal fixed in v0.8.5. citeturn10search9turn10search25 | Primary advisory |
| **2026-10-09** | NanoClaw v2026.10.0 release history. citeturn17search3 | Primary |
| **2026-10-22** | NanoClaw repository architecture: per-group containers, skills-over-features and alternative providers. citeturn17search2turn17search1 | Primary |
| **2026-09-15** | Nanobot v0.3.5 architecture/release material. citeturn16search1 | Primary |
| **2026-03-27** | Nanobot zero-click email indirect-prompt-injection advisory. citeturn8search16 | Primary advisory |
| **2026-10-22** | Letta Code current repository; memory/identity, always-on operation and self-rewriting memory/skills/prompts/harness. citeturn23search2 | Primary |
| **2026** | Letta older-server sandbox environment disclosure advisory. citeturn11search25 | Primary advisory |
| **2026-10-12** | Paperclip v2026.1012.0 release. citeturn20search0 | Primary |
| **2026-10-22** | Paperclip repository: agent control plane, budgets, skills/evals, permissions, run history, approvals. citeturn20search3turn20search8 | Primary |
| **2026-08-12** | Paperclip #11276, reproduced hard-budget overshoot. citeturn20search1 | Reported operational issue |
| **2026-08-27** | Paperclip #12304, multi-week `max_turns` exhaustion recorded as success. citeturn20search2 | Reported operational issue |
| **2026-10-22** | Paperclip development docs describing durable skill-version pins/audits/recovery. citeturn20search7 | Primary |
| **2026-10-14** | AutoGPT Platform beta v0.8.4 release. citeturn21search0 | Primary |
| **2026-10-22** | AutoGPT repository and licensing table: PolyForm Shield for Platform, MIT elsewhere. citeturn21search1 | Primary |
| **2026-10-13** | Agent Zero v2.14 release. citeturn7view1 | Primary |
| **2026-10-22** | Agent Zero VPS deployment documentation. citeturn16search7 | Primary |
| **2026-10-22** | Kortix/Suna current repository: isolated cloud computers/branches and approval-driven landing. citeturn8search2 | Primary |
| **2026** | Kortix/Suna security advisories for XSS/access-control defects. citeturn8search10turn8search21 | Primary advisories |
| **2026-10-17** | Archon v0.12.1 release: deterministic workflow direction, durable state, provider/plugin separation and `.env` credential fix. citeturn15search2 | Primary |
| **2026-04** | Archon project discussion/rewrite describing deterministic workflow-engine direction. citeturn2search31 | Primary |
| **2026-02-13** | SkillsBench v1, self-generated vs curated skill evaluation. citeturn22search0turn22search1 | Primary research |
| **2026-09 current revision** | SkillsBench current HTML/release material. citeturn22search5turn22search19 | Primary research/project |
| **2026-05/09** | SkillRevise, execution-grounded verifier-driven skill revision. citeturn22search6turn22search10 | Primary research |
| **2026-08-06** | SkillHEX, bounded hypothesis-driven skill evolution. citeturn22search3 | Primary research |
| **2026-04/05** | SkillLearnBench and SkillEvolBench, continual/self-evolving skill evaluation. citeturn22search20turn22search23turn22search7 | Primary research |

**Bottom-line verdict, as of 2026-10-22:** the October 2026 first-survey conclusion survives contact with this skipped category. The agent runtime really is becoming a commodity layer. OpenClaw, Hermes, Moltis and peers make it increasingly unnecessary to build your own chat gateway, memory system, cron daemon, provider switchboard or generic tool loop. They do **not** make it unnecessary to build—or adopt from projects such as Paperclip/Archon—the system that decides what work exists, what may advance, what it cost, what evidence proves it, which version is trusted, and who is allowed to ship it. That remains the software factory.