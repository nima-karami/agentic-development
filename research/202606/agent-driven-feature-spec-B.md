# From One Line to a Living Spec: How an AI Coding Agent Can Autonomously Elaborate "Look, Feel & Behavior" Specifications

## TL;DR
- In 2026 an AI agent in Claude Code can reliably take a one-line idea and autonomously produce a layered, look-and-feel-focused feature spec by chaining three established moves: **plan-before-implement** (Anthropic's Explore→Plan→Implement→Commit), **spec-driven development** (GitHub Spec Kit, AWS Kiro, Tessl turn the spec into the durable artifact), and **structured requirement notation** (EARS + Gherkin) — and the whole methodology is portable as a reusable Claude Code skill/slash command.
- The hard part is not generating text but covering the right surfaces: classic design/PM frameworks (JTBD, Patton story mapping, Brandolini event storming, Nielsen heuristics, Scott Hurff's UI Stack, design-token tiers, WCAG/ARIA) give an agent a *checkable enumeration* of states, interactions, edge cases, accessibility, and i18n that prevents thin literal interpretation — while progressive disclosure (MVP vs. full vision) prevents scope explosion.
- The single most consequential design decision is **ask vs. assume**: published practitioner skills and 2026 research converge on a rule — ask only when the answer *materially changes what you build* and is not inferable, cap clarifying questions at roughly 1–5, recommend a default for each, and otherwise proceed on **documented, defensible assumptions** rather than blocking. In the "Ask or Assume?" study, an uncertainty-aware multi-agent scaffold (OpenHands + Claude Sonnet 4.5) hit a **69.40% resolve rate vs. 61.20%** for a standard single agent — nearly matching the **70.80%** of an agent handed the fully-specified issue.

## Key Findings

1. **Spec-driven development (SDD) is the dominant 2026 paradigm and the right home for this workflow.** Every major coding tool — GitHub Spec Kit, AWS Kiro, Claude Code, Cursor, Tessl, OpenSpec, BMAD — now ships an SDD flavor. The shared idea: the *spec* is the durable, primary artifact; code is a regenerable output. This is exactly the framing needed when the goal is "look, feel, and behavior" rather than implementation.

2. **The agent should run a staged pipeline with explicit gates**, mirroring Kiro's `requirements.md → design.md → tasks.md` and Spec Kit's `constitution → specify → clarify → plan → tasks → analyze → implement`. Each stage produces a checkable Markdown artifact; gates let the user (or a reviewer subagent) catch misunderstandings cheaply before they propagate.

3. **EARS notation makes behavioral requirements unambiguous and AI-parseable.** EARS was authored by Alistair Mavin, Philip Wilkinson, Adrian Harwood and Mark Novak of Rolls-Royce PLC and published at the 17th IEEE International Requirements Engineering Conference (RE'09) in 2009 — developed while analysing an aero-engine control system's airworthiness regulation, and now used by Airbus, Bosch, NASA, Intel and Siemens. It has five patterns (ubiquitous, state-driven "While", event-driven "When", unwanted-behavior "If/Then", optional "Where"). Kiro adopted EARS as its default acceptance-criteria format precisely because it forces complete, testable statements and is easy for an LLM to parse.

4. **State enumeration is the highest-leverage "look and feel" technique.** Scott Hurff's *UI Stack* defines five states every screen must design — Ideal, Empty, Error, Partial, Loading — and the Atlassian Design System documents component states (enabled, hover, disabled, loading, empty, error) as first-class. An agent that walks a fixed state checklist for every component catches the gaps human designers usually miss.

5. **Ask-vs-assume has converging guidance.** Community Claude skills ("asking-questions", "ask-questions-if-underspecified") and the 2026 academic study "Ask or Assume?" agree: well-calibrated agents conserve questions on easy tasks and ask on hard/ambiguous ones; the uncertainty-aware multi-agent scaffold beat the autonomous baseline on underspecified SWE-bench Verified.

6. **The methodology must be tool-agnostic but Claude-Code-native.** It maps cleanly onto CLAUDE.md (persistent conventions/defaults), slash commands (the repeatable flow), plan mode (read-only elaboration), skills (SKILL.md with progressive disclosure), and subagents (independent spec review in a fresh context).

## Details

### A. The requirements elicitation toolkit — and how a solo agent applies each without a workshop

These methods were built for human workshops. The agent's job is to *simulate the multiple perspectives internally* — which is exactly what role-prompting and subagents are for. Run them as reasoning passes:

- **Jobs-to-be-Done (Tony Ulwick's Outcome-Driven Innovation; popularized by Clayton Christensen, *The Innovator's Solution*, 2003).** JTBD reframes a feature around the functional/emotional "job" the user hires it to do, plus measurable desired outcomes. *Agent application:* before listing UI, write the job statement ("When I'm triaging work, I want to see status at a glance, so I can decide what to pull next") and 3–5 outcome metrics (time-to-find, glance-ability). Ulwick's "job mapping" (HBR 2008) decomposes the job into steps — a natural source of user tasks.

- **User Story Mapping (Jeff Patton, O'Reilly 2014).** A two-dimensional map: the *backbone* (left-to-right narrative of user activities) over *tasks/stories* (top-to-bottom detail), with a horizontal slice marking the MVP. Patton's six steps: frame the problem; map the big picture (breadth first); explore (alternatives, what-goes-wrong); slice a release strategy; slice a learning strategy. *Agent application:* generate the backbone of user activities first, fan out tasks under each, then draw the MVP slice — this directly produces the progressive-disclosure layering.

- **Event Storming (Alberto Brandolini, 2013; *Introducing EventStorming*).** Map *domain events* (orange, past tense) on a timeline, then add commands (blue), actors/people (yellow), policies (purple), read models (green), external systems, and **hot spots** (magenta = pain/uncertainty). Three levels: Big Picture, Process Modeling, Software Design. *Agent application:* enumerate every event a feature emits ("CardMoved", "WipLimitExceeded", "FilterApplied"), then derive the commands that cause them and the read models the UI must show. Hot spots become the agent's clarifying-question candidates.

- **The 5 Whys (Toyota/Ohno).** Iteratively ask "why" to reach root cause. *Agent application:* chain-of-thought from the literal request down to the underlying need, so the agent designs for the job, not the literal words ("add a Kanban board" → why → to see work status → why → to decide what to work on next → implies WIP limits, filtering, glance-ability).

- **Scenario walkthroughs / cognitive walkthrough.** *Agent application:* write concrete Given-When-Then narratives for first-run, returning-power-user, error-recovery, and edge personas, then check the UI supports each.

The deeper product layer: **Marty Cagan/SVPG** (build empowered teams solving problems, not feature factories) and **Teresa Torres' Opportunity Solution Tree** (*Continuous Discovery Habits*, 2021): root = desired outcome; branches = opportunities (unmet needs); leaves = solutions; below = assumption tests. *Agent application:* the OST keeps the agent honest — every proposed UI element must trace to an opportunity that traces to the outcome, or it's scope creep.

### B. Interaction design coverage — enumerate actions, affordances, gestures, shortcuts

A thorough agent systematically lists, for each component:
- **Actions/affordances:** every verb the user can perform (create, edit, move, delete, reorder, filter, search, assign, label, archive). Nielsen's "recognition rather than recall" and "user control and freedom" (undo/redo, emergency exits) are the checklist lenses.
- **Input modalities:** pointer (click, drag, hover, right-click context menu), keyboard (Tab order, arrow navigation, Enter/Space activation, Escape cancel, shortcuts), touch (tap, long-press, swipe), voice/AT.
- **Keyboard shortcuts & focus management:** every drag action needs a keyboard equivalent (see accessibility below).

### C. Systematic state enumeration — the UI Stack + design-system practice

Reference frameworks: **Scott Hurff's UI Stack** (Ideal, Empty, Error, Partial, Loading) and design-system state docs (Atlassian, Material). The agent walks this fixed list for *every* screen and component:
- **Empty / first-run (blank slate)** vs. **empty-after-action** — Atlassian distinguishes a "blank slate" (never used; encourage trying) from an "empty state" (cleared/completed; celebrate) and prescribes a clear title + one CTA with an imperative verb.
- **Loading** — skeletons preferred over spinners; match indicator to wait time; avoid multiple spinners; place indicator where content will appear; collapse long jobs to background state (Hurff / Smart Interface Design Patterns).
- **Partial** — some data present, more loading or sparse.
- **Error** — component-level (inline alert + Retry) vs. page-level; plain-language message, cause, constructive next step (Nielsen #9).
- **Success / populated (Ideal).**
- **Offline, permission-denied, not-found (404), unauthorized** — each needs explicit copy and recovery.

### D. Edge cases & failure modes a thorough designer anticipates

Long cards/titles (truncation, wrapping), huge lists (virtualization, pagination), zero/one/many, concurrency (two users move the same card — optimistic UI + conflict resolution), network loss mid-action (optimistic update + rollback + toast), slow APIs (queue-jumping: a later request finishing first), rapid repeated clicks (debounce, disable), invalid input, hitting WIP limits, drag cancelled mid-flight, very small/large viewports, RTL languages, reduced-motion preference, high-contrast/forced-colors mode.

### E. Settings & configuration surface — configurable vs. sensible default

Heuristic (synthesized from ChatPRD's AI-PRD guidance and Material/Polaris defaults thinking): **make it a default when there is a defensible best answer for ~80% of users; make it configurable only when real users legitimately diverge and the cost of the wrong default is high.** Document each default and its rationale. For most features the agent should ship opinionated defaults and expose a small settings surface (e.g., theme, WIP-limit on/off + value, default sort/filter, card density), not a sprawling preferences panel.

### F. Theming, visual states & design-token thinking at the spec level

The agent specifies *token roles*, not hex values, using the three-tier model documented by **Material Design 3** (reference → system → component) and echoed by Shopify Polaris / Atlassian: **primitive/reference** (raw values), **semantic/system/alias** (purpose: `color-action-primary`, `surface-raised`), **component** (`card-background`, `column-header-text`). Themes (light/dark/high-contrast) are token remaps, not duplicated styles. Spec rule: name tokens by *purpose* not appearance; define the semantic layer so dark mode and rebrand are token swaps. Visual states (hover, focus ring, selected, dragging, disabled) each reference state-specific tokens.

### G. Accessibility & i18n as DEFAULT spec concerns

- **Accessibility:** WCAG 2.2 (perceivable/operable/understandable/robust); keyboard operability for everything; visible focus indicators (never remove the outline without replacing it; test in forced-colors mode); ARIA roles/states; for drag-and-drop, WCAG 2.5.7 Dragging Movements requires a non-dragging alternative. Adobe's React Aria and Atlassian's Pragmatic drag-and-drop are the reference implementations.
- **i18n/l10n:** externalize all strings; support pluralization, date/number/currency formats, text expansion (German averages 20–35% longer per SimpleLocalize, and short strings far worse — "Settings"→"Einstellungen" is +75%; design for up to 2× on short strings), RTL mirroring, locale-aware sorting. The agent should never hardcode user-facing copy in the spec's component definitions.

### H. Progressive disclosure & scoping — layered, not bloated

Use Patton's MVP slice and Torres' "start with a teeny tiny opportunity." The spec should be explicitly layered: **MVP (must-have)** → **v1 (should-have)** → **Full vision (could-have)**, MoSCoW-tagged. This is also how the agent avoids over-specification: deep detail on the MVP layer, lighter sketches on later layers, an explicit **Out of Scope** section (Kiro's template includes one).

### I. Clarify vs. assume — the critical balance

The strongest, most-cited operational rule comes from community Claude skills and is corroborated by 2026 research:

- **Ask only when the answer materially changes what you build** and cannot be inferred from the codebase, conventions, or reasonable defaults ("asking-questions" skill). Over-clarification (questions that don't change the build, or that re-ask inferable things) is an anti-pattern; so is silent wrong assumption.
- **Cap the first pass at ~1–5 questions**, prefer questions that "eliminate whole branches of work," and present each as 2–5 lettered options with a **bolded recommended default** and a "not sure — use default" escape ("ask-questions-if-underspecified" skill).
- **Otherwise proceed on documented, defensible assumptions** and record them in an Assumptions section so they're reviewable and reversible.
- Research backing: the 2026 study *"Ask or Assume? Uncertainty-Aware Clarification-Seeking in Coding Agents"* (Edwards & Schuster, University of Vienna; arXiv:2603.26233) built an uncertainty-aware multi-agent scaffold on an underspecified variant of SWE-bench Verified. Using OpenHands + Claude Sonnet 4.5, it **"achieves a 69.40% task resolve rate, significantly outperforming a standard single-agent setup (61.20%),"** nearly matching the **70.80%** of an agent given the fully-specified issue — and it conserved queries on simple tasks while proactively asking on complex ones. Amazon Alexa AI's earlier work framed the same tradeoff (asking too often hampers UX). Earlier LLM research shows models often detect ambiguity internally but answer anyway unless explicitly taught to clarify — which is why the *prompt/skill must instruct the agent to surface uncertainty*.

### J. Spec artifacts & formats — what captures "look and feel" AND feeds implementation

- **PRD** (problem, users, JTBD, outcomes, scope) — the "why/what."
- **User stories** ("As a…, I want…, so that…") with **acceptance criteria**.
- **EARS** for behavioral/state requirements (testable, unambiguous, AI-parseable).
- **Gherkin / BDD Given-When-Then** for scenario-level acceptance — human-readable and executable, ideal for "behavior." Keep scenarios *declarative* (behavior, not implementation: "When I submit my credentials," not "When I click #submit"); 1–3 criteria per story; use Background for shared setup. Note the practitioner caution: not everything fits GWT — use bullet lists for simple stuff, reserve BDD for complex/high-risk flows.
- **Interaction inventory** (a table: component × action × states × shortcuts × ARIA).
- **State table** (component × UI-Stack state × copy × CTA).
- **Design-token table** (role → semantic token → theme variants).

Best practice for AI consumption (Addy Osmani, "How to write a good spec for AI agents"): clean parseable structure, explicit headings, the "why" behind each requirement, and a self-verification step ("after drafting, list any spec items not yet addressed").

### K. Avoiding both under- and over-specification

- **Under-spec (thin/literal):** mitigated by the elicitation passes (JTBD/5-Whys reach the real need) and the mandatory state/edge/a11y/i18n checklists.
- **Over-spec (scope explosion):** mitigated by OST traceability (every element ties to an opportunity), MoSCoW layering, an Out-of-Scope section, and the ChatPRD rule "be thorough yet concise; trust the AI/defaults with routine decisions; don't over-specify implementation."

### L. 2026 state of the art — tools as evidence

**Established practice:**
- **Claude Code** (Anthropic): Explore→Plan→Implement→Commit; **plan mode** (Shift+Tab twice, read-only); **CLAUDE.md** for persistent conventions; **skills** (SKILL.md + progressive disclosure via references/ scripts/ subdirs; description field is a trigger); **subagents** (fresh-context review — "have a second Claude review the plan as a staff engineer"); **slash commands** for repeated inner-loop workflows. Anthropic's own guidance is to give the agent a way to verify its own work — Boris Cherny (@bcherny, Jan 3, 2026): *"probably the most important thing to get great results out of Claude Code -- give Claude a way to verify its work. If Claude has that feedback loop, it will 2-3x the quality of the final result."*
- **AWS Kiro:** agentic IDE; three-file spec (`requirements.md` in EARS user stories + acceptance criteria, `design.md` architecture/diagrams, `tasks.md`); explicitly "expands vague asks and highlights edge cases"; auto-includes loading states, responsive design, accessibility, tests in its task breakdown; steering files (product.md, structure.md, tech.md). Quick Plan mode auto-generates all three artifacts without approval gates for well-understood features.
- **GitHub Spec Kit:** open-source, model-agnostic; slash-command flow `/speckit.constitution → /speckit.specify → /speckit.clarify → /speckit.plan → /speckit.tasks → /speckit.analyze → /speckit.implement`; the **constitution** (`.specify/memory/constitution.md`) holds non-negotiable principles; **`/speckit.clarify`** runs sequential, coverage-based questioning recording answers in a Clarifications section; works with Claude Code, Copilot, Cursor, Gemini and 30+ agents; created at GitHub by Den Delimarsky (@localden), influenced by John Lam, announced on The GitHub Blog **September 2, 2025** (Delimarsky's framing: *"We treat coding agents like search engines when we should be treating them more like literal-minded pair programmers"*).
- **Cursor** (Plan Mode), **v0 by Vercel** (best-in-class React/Tailwind/shadcn UI generation, image/Figma-to-code, frontend-only), **Lovable** (fastest full-stack MVP, Supabase), **Bolt** (WebContainer, fast prototypes), **Figma Make** (Figma-native, runs on Claude). **ChatPRD** is a dedicated PRD-generation agent.

**Emerging / contested:**
- **Tessl** (Guy Podjarny; "spec-as-source" — code is fully regenerated from specs and never hand-edited) is the most radical bet and not yet broadly proven.
- Martin Fowler's team and others report SDD tools can be *too verbose* (spec-kit generated many repetitive Markdown files; Kiro "a sledgehammer to crack a nut" for small bugs), and that agents frequently *don't follow all the instructions* even with large context windows — so SDD pays off mainly for large/complex features, not small fixes.
- Security caveat: Veracode's 2025 GenAI Code Security Report (100+ LLMs, 80 coding tasks) found **45% of AI-generated code samples failed security tests and introduced OWASP Top 10 vulnerabilities** (86% failure rate on cross-site scripting; Java riskiest at 72%), and that AI-generated code contains **2.74× more vulnerabilities than human-written code** — specs and output need security review.

**Notable practitioners to cite:** Marty Cagan (SVPG), Teresa Torres (continuous discovery), Jeff Patton (story mapping), Alberto Brandolini (event storming), Tony Ulwick/Clayton Christensen (JTBD), Alistair Mavin (EARS), Jakob Nielsen & Rolf Molich (heuristics), Scott Hurff (UI Stack), Brad Frost (atomic design), Simon Willison & Addy Osmani (agentic coding/specs in 2025–26), Anthropic's Boris Cherny (Claude Code).

---

## The Reusable Methodology (encode as a Claude Code skill / slash command)

Package as `.claude/skills/feature-spec/SKILL.md` (or a `/spec` slash command). Description field as trigger: *"Use when the user gives a short feature idea and wants a full look-and-feel/behavior specification."* Run in **plan mode** so it stays read-only until the spec is approved. Progressive disclosure: keep step detail in `references/` files the agent loads on demand.

**Step 0 — Intake & repo grounding.** Read CLAUDE.md, existing design tokens, component library, conventions. Restate the request in one sentence.

**Step 1 — Understand the job (don't design yet).** Apply 5-Whys + JTBD: write the job statement, the actors, and 3–5 desired-outcome metrics. Build a mini Opportunity Solution Tree (outcome → opportunities). *Gate output: Problem & Outcomes.*

**Step 2 — Map the experience.** Story-map the backbone (user activities) → tasks. Event-storm the domain events, commands, read models, hot spots. *Gate output: Activity/Story map + event list.*

**Step 3 — Ask-or-assume triage.** For each hot spot/ambiguity, decide: does the answer materially change the build AND is it non-inferable? If yes → queue a question (max ~5, lettered options, bolded recommended default, "use default" escape). If no → record a documented assumption. Present questions in one batch; otherwise proceed.

**Step 4 — Enumerate interactions.** Build the interaction inventory table: component × actions/affordances × input modalities (pointer/keyboard/touch) × shortcuts × right-click/context menus.

**Step 5 — Enumerate states.** For every screen/component, walk the UI Stack + (empty/first-run, loading, partial, ideal, error, success, offline, permission-denied, not-found). Write copy + CTA for each.

**Step 6 — Edge cases & failure modes.** Generate the failure list (concurrency, long content, zero/one/many, network loss, slow/queue-jumping, repeated clicks, limits, viewports, RTL, reduced motion).

**Step 7 — Cross-cutting defaults: a11y + i18n + theming.** WCAG/ARIA per component (keyboard equivalents for drag, focus order, live-region announcements, alternatives per WCAG 2.5.7); i18n (externalized strings, pluralization, RTL, expansion); design-token roles (semantic layer + theme variants).

**Step 8 — Settings surface.** Apply the default-vs-configurable heuristic; list each setting, its default, and rationale; keep the surface minimal.

**Step 9 — Layer & scope.** MoSCoW-tag everything; draw the MVP slice; write the Out-of-Scope section. Ensure every element traces to an opportunity (kill orphans).

**Step 10 — Write requirements formally.** EARS for behavioral/state rules; Gherkin Given-When-Then for key acceptance scenarios; acceptance criteria per story.

**Step 11 — Self-verify + subagent review.** Agent lists any checklist items not yet addressed; spawn a fresh-context reviewer subagent to critique the spec as a senior designer/PM against the template and report gaps. Revise. *Final gate before implementation.*

---

## The Reusable Spec Template (the agent fills this in)

```markdown
# Feature Spec: <Name>
## 1. Summary & Problem  (one-paragraph; the WHY)
## 2. Job-to-be-Done & Outcomes
   - Job statement; Actors/personas; Desired-outcome metrics
## 3. Opportunity → Solution trace (every feature ties to an opportunity)
## 4. Scope  (MoSCoW)
   - MVP (must) / v1 (should) / Vision (could) / **Out of Scope**
## 5. Experience Map
   - Activity backbone → tasks; Domain events / commands / read models
## 6. Interaction Inventory  (table)
   | Component | Actions/Affordances | Pointer | Keyboard/Shortcuts | Touch | Context menu | ARIA role/states |
## 7. State Catalog  (table, per component)
   | Component | State (ideal/empty/first-run/loading/partial/error/offline/perm-denied/not-found) | Trigger | Copy | CTA |
## 8. Edge Cases & Failure Modes
## 9. Accessibility  (WCAG 2.2 / ARIA / keyboard / focus / drag-alt 2.5.7)
## 10. Internationalization  (strings, plurals, dates/numbers, RTL, expansion)
## 11. Theming & Design Tokens  (role → semantic token → light/dark/high-contrast)
## 12. Settings & Configuration  (setting | default | rationale | configurable?)
## 13. Requirements
   - EARS statements (ubiquitous/state/event/unwanted/optional)
   - User stories + acceptance criteria
   - Gherkin scenarios (Given/When/Then) for key flows
## 14. Assumptions  (documented defaults taken instead of asking)
## 15. Open Questions  (only those that materially change the build)
## 16. Success Metrics & Definition of Done
```

---

## Worked Example: "Add a Kanban board to my agent-manager console"

**Step 1 — Job & outcomes.** *Job:* "When I'm overseeing many running agents, I want to see each agent's task status at a glance and move work between stages, so I can decide what needs attention next." *Outcomes:* time-to-find a stalled agent ↓; glance-to-decision time ↓; mis-drops ↓. *5-Whys* surfaces that the real need is *triage*, which implies WIP limits, filtering, and status glance-ability — not just columns.

**Step 2 — Experience map.** Backbone: *View board → Triage → Act on a card → Organize → Configure.* Domain events: `BoardLoaded, CardCreated, CardMoved, CardMovedWithinColumn, WipLimitReached, CardLabeled, FilterApplied, SearchPerformed, CardArchived, BoardConfigChanged`.

**Step 3 — Ask-or-assume.** Most choices are inferable → assume + document. The 1–2 questions that *materially* change the build, each with a recommended default:
- *Persistence/scope:* "Is the board per-user or shared across the team? **(a) Per-user [recommended default]** / (b) Shared/real-time / (c) not sure — use default."
- *Columns:* "Fixed columns mapped to agent lifecycle, or user-editable? **(a) Editable, seeded with Backlog/Running/Blocked/Done [recommended]** / (b) Fixed."
Everything else → Assumptions section.

**Step 4 — Interaction inventory (excerpt).**
- *Card:* open detail (click/Enter), drag between & within columns (pointer + keyboard pickup), right-click context menu (Open, Edit, Label, Move to ▸, Archive), quick-label, assign. Shortcuts: `N` new card, `/` focus search, `F` filter, `E` edit focused card, `Esc` cancel drag/close, arrow keys move focus, `Space` pick up/drop.
- *Column:* collapse/expand, set/clear WIP limit, sort, add card.
- *Board:* filter, search, theme toggle, settings.

**Step 5 — State catalog (excerpts).**
- *Board empty / first-run (blank slate):* illustration + "No agents yet. Create your first card to start tracking." + primary CTA **Create card**. (Atlassian blank-slate pattern.)
- *Column empty:* dashed drop zone "Drop cards here" / "Nothing in Blocked 🎉".
- *Loading:* skeleton cards (not spinners) per column; board chrome renders immediately.
- *Partial:* columns stream in; show count badges as they resolve.
- *Error (board):* page-level error + Retry; *Error (single card move):* optimistic move rolls back + inline toast "Couldn't move card. Retry / Undo."
- *Offline:* banner "You're offline — changes will sync when reconnected"; queue moves.
- *Permission-denied:* "You don't have access to this board" + Request access.
- *WIP limit reached:* target column header turns warning color; drop allowed-but-flagged or blocked-with-explanation per config; live-region announces it.

**Step 6 — Edge cases.** Long card titles (truncate + tooltip/full in detail); 500-card column (virtualized scroll + count); concurrent move of same card (last-write + conflict toast if shared); drag cancelled (returns to origin, focus restored); queue-jumping async moves (sequence + reconcile); rapid `N` presses (debounce); reduced-motion (disable drag animation); RTL (mirror column order & drag direction); forced-colors mode (focus ring survives).

**Step 7 — A11y / i18n / tokens.**
- *Drag-and-drop a11y* (the make-or-break detail): full keyboard pickup/move/drop (`Space` lift, arrows move, `Space` drop, `Esc` cancel), live-region announcements ("Lifted card in Running. Use arrow keys to move, space to drop, escape to cancel" → "Moved to Blocked, position 2 of 5"), a visible **Move to ▸** menu as the non-drag alternative (WCAG 2.5.7), focus returns to the card in its new column after drop. Reference: Adobe React Aria Kanban + Atlassian Pragmatic drag-and-drop.
- *i18n:* all column names/labels/empty-copy externalized; counts pluralized; dates relative + locale-aware; RTL mirrored; layouts tolerate 20–35%+ text expansion.
- *Tokens:* `column-header-bg`, `card-surface`, `card-surface-dragging`, `wip-warning`, `focus-ring` → semantic → light/dark/high-contrast remaps. Label colors map to a fixed accessible palette with text contrast ≥ 4.5:1, and never rely on color alone (pair with text/icon).

**Step 8 — Settings (minimal).** Theme (default: system); WIP limits (default: off, per-column integer when on); default sort (default: manual/drag order); card density (default: comfortable); show/hide Done column (default: show). Each documented with rationale; everything else hardcoded to a sensible default.

**Step 9 — Scope.** *MVP:* columns, cards, drag between columns (+ keyboard alt), card detail, empty/loading/error states, persistence, basic a11y. *v1:* labels/colors, filter/search, WIP limits, context menu, reorder within column. *Vision:* swimlanes, real-time multi-user, automation rules, saved filter views, analytics (cycle time). *Out of scope:* time tracking, billing, mobile-native app.

**Step 10 — Requirements (samples).**
- *EARS (event):* "**When** a card is dropped on a different column, the board **shall** update the card's status, persist the change, and announce the move via an ARIA live region."
- *EARS (unwanted):* "**If** a card move fails to persist, **then** the board **shall** revert the card to its original position and display a retry toast."
- *EARS (state):* "**While** the board is loading, the board **shall** display skeleton cards in each column."
- *EARS (optional):* "**Where** WIP limits are enabled, the board **shall** visually flag a column that exceeds its limit."
- *Gherkin:* `Given the "Running" column has its WIP limit of 3 reached / When I drag a fourth card into "Running" / Then the column header shows a warning state / And a live-region announces the limit / And the drop is blocked per board configuration.`

**Step 11 — Review.** Self-verify against the template checklist; subagent reviews as a senior designer ("are all five UI-Stack states covered for every component? is every drag action keyboard-operable? does every element trace to an opportunity?"); revise; present for approval before any implementation.

## Recommendations

1. **Build it as a Claude Code skill now.** Create `.claude/skills/feature-spec/SKILL.md` with the 11-step methodology, put the heavy per-step detail in `references/` (progressive disclosure), and trigger it via a `/spec` slash command. Run it in **plan mode** so the agent elaborates read-only and you approve before code. Keep your durable defaults (token names, a11y baseline, i18n policy, the ask-vs-assume rule) in **CLAUDE.md** so they apply to every spec.

2. **Make the checklists non-negotiable and explicit.** The agent's quality comes from *enumeration*, not eloquence. Hard-code the UI-Stack state list, the interaction-inventory columns, the WCAG/ARIA + drag-alt rule, and the i18n list as literal checklists in the skill. Tell the agent to end every spec with a self-audit listing any unaddressed checklist item (Addy Osmani's self-verification pattern).

3. **Encode the ask-vs-assume rule verbatim.** Instruct: "Ask only if the answer materially changes the build and is not inferable; cap at 5 questions, each with lettered options and a bolded recommended default and a 'use default' escape; otherwise proceed and log a documented assumption." This is the single biggest driver of whether the agent feels smart or annoying — and the "Ask or Assume?" data shows calibrated questioning closes most of the gap to a fully-specified brief (69.4% vs. 70.8%).

4. **Always run the fresh-context reviewer subagent.** A second agent that sees only the spec + template criteria catches the gaps the author rationalized away — Anthropic's own recommended pattern and worth the tokens.

5. **Use EARS + Gherkin as the requirement spine, PRD prose as the wrapper.** EARS for state/behavior (testable, AI-parseable, the format Kiro and Spec Kit converged on); Gherkin for key acceptance flows; keep it declarative (behavior, not implementation).

6. **Optionally interoperate with Spec Kit/Kiro.** If you want a fuller pipeline, your skill can emit the same artifact shape (`requirements.md`/`design.md`/`tasks.md` or Spec Kit's `spec.md`), so the look-and-feel spec drops straight into those tools' plan/implement phases. But keep your own methodology tool-agnostic — it's the portable asset.

**Thresholds that change the approach:** For a *small* change (one component, bug fix), skip the full pipeline — SDD is "a sledgehammer to crack a nut" (Fowler's team). Trigger the full skill only when the feature touches multiple screens/states or is user-facing and novel. If the user answers the gate questions with rich detail, collapse the gates (Kiro's "Quick Plan" mode). If they say "just sketch it," produce MVP-layer only.

## Caveats

- **SDD tools can over-produce.** Independent reviews (Martin Fowler's team) found Spec Kit/Kiro generate verbose, repetitive Markdown and that agents *still* skip instructions even with large context windows. Bias toward concise specs and human review of the spec, not just the code.
- **The "ask vs assume" research is early.** The "Ask or Assume?" result (69.40% vs. 61.20% resolve rate) is a 2026 preprint on a code-resolution benchmark (SWE-bench Verified), not a design-spec benchmark; treat the *direction* (calibrated questioning helps) as sound and the exact numbers as provisional.
- **AI-generated UI code has a measurable security/quality tax.** Veracode's 2025 GenAI Code Security Report found 45% of AI-generated samples introduced OWASP Top 10 vulnerabilities and 2.74× more vulnerabilities than human-written code; a polished spec does not remove the need for security and accessibility review of the implementation.
- **Vague-to-spec quality still depends on grounding.** The agent is only as good as the repo context (CLAUDE.md, existing tokens/components) it reads first; on a greenfield repo with no conventions, expect more assumptions and more gate questions.
- **Tool details move fast.** Specific product capabilities, pricing, and command names (v0, Lovable, Bolt, Kiro, Spec Kit's `/speckit.*` prefix) changed repeatedly across 2025–2026; verify current docs before relying on a specific command or feature.