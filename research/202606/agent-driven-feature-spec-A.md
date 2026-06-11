# How AI Agents Turn a Vague Idea Into a Complete Feature Specification

## The target capability

A strong feature-specification agent is not just a coding assistant with better prose. It must do the work a good product trio would normally do before implementation: define the user problem, map user journeys, identify implied interactions, enumerate states and exceptions, choose sensible defaults, surface settings only when they matter, and package all of that into artifacts that downstream engineering can execute without guessing. That framing matches both modern requirements engineering and the newer spec-driven AI workflows: IEEE 29148 treats requirements as iterative, recursive, and governed by defined information items and quality characteristics, while GitHub’s Spec Kit separates **specification** from **technical planning** and explicitly says the specification phase is about user journeys, experiences, and success criteria rather than stacks or architecture. Atlassian’s PRD guidance similarly defines a PRD as a document that captures product purpose, features, and behaviour. citeturn26search1turn33view0turn13search1

For your use case, the key design problem is not “how do I get an agent to write a longer PRD?” It is “how do I get an agent to systematically discover the unstated but necessary product decisions that make a feature feel complete?” The best answer in 2026 is a **spec-first, plan-second, implementation-third** workflow, reinforced by durable agent context such as `AGENTS.md`, reusable skills/custom agents, and explicit review gates. OpenAI’s Codex best-practices guide, GitHub’s Spec Kit, Cursor’s Plan Mode, Anthropic’s “interview first” guidance for larger features, and GitHub Copilot’s cloud agent all converge on that pattern: plan before building, encode durable instructions, and turn repeated workflows into reusable agent capabilities. citeturn31view0turn33view0turn23search8turn18search1turn23search1

A complete feature spec also needs to be **layered**, not bloated. Jakob Nielsen’s progressive-disclosure guidance remains the right principle: advanced or rarely used features should be deferred to secondary surfaces so the primary experience stays learnable and low-friction. Jeff Patton’s story-mapping work adds the release-slicing discipline needed to convert a rich feature definition into a sensible MVP and follow-on releases instead of a kitchen-sink first version. citeturn12search0turn12search1turn12search7

## Frameworks an agent can apply alone

A useful way to think about “solo agent design” is that the agent is not literally running a workshop with humans; it is **serializing the outputs** of proven product and UX methods into intermediate artifacts, then cross-checking those artifacts against each other. In practice, the frameworks below are the highest-value ones for turning one-line prompts into full behavioural specs.

| Framework | What question it answers | What the agent should output |
|---|---|---|
| **Jobs to Be Done** | What “job” is the user hiring this feature to do, and what outcome matters? Christensen and coauthors argue that firms innovate better when they focus on the job the customer is trying to get done rather than on the product category alone. citeturn39search0turn39search4 | A job statement, success outcomes, and explicit non-goals. |
| **User need statement** | Who is the user, what do they need, and why does that need matter? NN/g defines this as an actionable problem statement used before ideating solutions. citeturn40search9 | A concise problem frame that anchors every later design choice. |
| **User story mapping** | What does the user’s end-to-end journey look like, and what slices deliver value earliest? Patton’s material and NN/g’s story-mapping guidance both stress that maps create user-centred conversations, expose gaps, and support iterative release planning. citeturn12search7turn12search1turn40search0 | A journey backbone, tasks under each step, and release slices for MVP / next / later. |
| **EventStorming** | What domain events, triggers, handoffs, and business rules sit behind the feature? EventStorming’s official description frames it as a flexible workshop format for collaborative exploration of complex business domains. citeturn38search4 | A timeline of user actions, system events, external dependencies, and invariants. |
| **Five Whys** | Why does the user want this feature, and what deeper operational or product problem does it solve? Lean defines 5 Whys as repeatedly asking why to get past symptoms toward root cause. citeturn38search2turn38search11 | A rationale chain that clarifies intent, scope, and what not to overbuild. |
| **Scenario or cognitive walkthrough** | Can a first-time or infrequent user actually discover, understand, and complete the task? NN/g and Usability BoK define cognitive walkthroughs as structured task-based evaluations from the perspective of a new user. citeturn40search1turn40search2turn40search18 | Step-by-step scenarios, predicted user questions, and friction points. |
| **Heuristic evaluation** | Does the proposed behaviour violate established usability principles such as visibility of system status, error recovery, or consistency? NN/g’s heuristic-evaluation guidance remains one of the cleanest ways to systematically inspect a UI design. citeturn40search16turn12search15 | A polish checklist covering clarity, feedback, recoverability, and convention fit. |

The practical move for an agent is to chain these methods, not choose one. JTBD and user-need statements define **why** the feature exists. Story mapping and EventStorming define **what must happen**. Cognitive walkthroughs and heuristic evaluation define **where the design will fail or feel thin**. Five Whys keeps the elaboration anchored to the real problem, which is the most reliable defence against scope explosion. That chaining is an inference from the methods above, but it is also consistent with 2025–2026 spec-driven workflows that make intermediate artifacts the source of truth rather than treating the initial prompt as sufficient. citeturn39search0turn12search7turn38search4turn40search1turn40search16turn33view0

## A reusable methodology for feature elaboration

The methodology below is designed to be explicit enough to encode as an agent skill. Each step has a concrete output and a clear stop condition.

1. **Normalize the request into a problem frame.**  
   Convert the one-line idea into three statements: a user-need statement, a JTBD statement, and a success statement. The agent should also write a short “not this” list to prevent misreads. If the request is “Add a Kanban board,” the normalized frame is not “render columns”; it is “help an operator see, prioritise, move, and manage work items spatially and quickly.” This follows the problem-first orientation in JTBD, user-need statements, and spec-driven development. citeturn39search0turn40search9turn33view0

2. **Define actors, contexts, and stakes.**  
   Identify primary, secondary, admin, read-only, and first-time users; then identify contexts such as desktop, mobile companion, high-volume usage, intermittent connectivity, and permission-constrained environments. User journeys and flows are always goal-based and examined from the user’s perspective, which is the right framing here. citeturn40search12turn13search17

3. **Generate scenarios before screens.**  
   Produce a small set of task scenarios: first-run, routine use, recovery from failure, permission-limited use, and a power-user case. Then run a cognitive walkthrough on each scenario, asking what a new user would be trying to do, what cues they would need, what action they would take next, and what feedback they would expect. This step is what turns a literal prompt into implied interactions and missing affordances. citeturn40search1turn40search2turn40search18

4. **Build both a story map and an event map.**  
   The story map organizes the feature around the user journey and release slices. The event map organizes it around triggers, state changes, and dependencies. Story mapping is especially useful for scoping; EventStorming-style event mapping is especially useful for surfacing hidden transitions, side effects, and business rules. citeturn12search7turn12search1turn38search4

5. **Create an interaction inventory.**  
   For every user goal, enumerate the actions, affordances, and feedback loops the interface needs. This should include point-and-click, touch/gesture, keyboard, contextual actions, and system-generated feedback. The reason to do this explicitly is that interaction conventions are widely distributed across platform guidance rather than implied by feature names: drag-and-drop, context menus, focus/selection, cards, sheets, and keyboard input all have documented platform expectations. citeturn6search9turn6search11turn6search15turn6search13turn6search16turn6search17

6. **Enumerate the state matrix.**  
   Do not stop at “empty/loading/error/success.” The agent should enumerate at least: first-run empty, no-results empty, deleted-or-unavailable empty, loading, partially loaded, save-in-progress, success, validation error, systemic error, offline or degraded connectivity, permission denied, and stale or conflicting data. Carbon’s empty-state and loading patterns, web.dev’s offline UX guidance, and platform permission guidance make clear that these are distinct user experiences with different copy, actions, and recovery paths. citeturn36view0turn35view0turn8search0turn9search1turn9search3turn9search19

7. **Run an edge-case and failure-mode pass.**  
   Use two lenses. First, use Five Whys to check whether an edge case points to a deeper design misunderstanding rather than a one-off exception. Second, use usability heuristics to ask whether the system will help users recognize, diagnose, and recover from bad states. This step produces a failure register with observable symptom, likely cause, expected user interpretation, UI response, and recovery action. citeturn38search2turn36view0turn40search16turn12search15

8. **Separate defaults from settings.**  
   Every meaningful decision should be classified as either a sensible default or a user-configurable setting. Android’s settings guidance, NN/g’s discussion of sensible defaults, and platform guidance on safe default actions all point in the same direction: default the common, safe, low-risk path; expose settings when preferences are durable, user-specific, or materially affect workflow. citeturn10search9turn11search0turn11search23

9. **Apply the design-system pass at the spec level.**  
   The spec should name the tokens and semantic roles it needs, not hardcoded colours and pixels. Material, Atlassian, and Fluent all frame tokens as the single source of truth for colours, typography, spacing, elevation, and theming. At the same time, the feature spec should explicitly cover interaction states, WCAG-level accessibility, keyboard use, reduced motion, colour-independent cues, right-to-left support, locale formatting, and pseudolocalization readiness. citeturn15search1turn14search1turn14search2turn15search0turn15search2turn15search14turn5search0turn9search13turn34search0turn34search2turn34search4

10. **Slice the spec into release layers and emit artifacts.**  
    The final output should include an MVP slice, a full-vision slice, and explicit deferrals. This is the point where the agent should generate the actual deliverables: behavioural PRD, interaction inventory, state matrix, user stories, and declarative acceptance criteria in Gherkin or BDD style. Story mapping, PRD guidance, and Gherkin’s emphasis on executable, declarative behaviour all support this structure. citeturn12search1turn13search1turn13search3turn13search6turn33view0

The most important behavioural rule for the agent is the **ask-versus-assume gate**. OpenAI’s guidance says to use context and reasonable assumptions and only ask for clarification when the missing information would materially change the answer or create meaningful risk; the Model Spec says to ask when the request is markedly unclear. GPT-5.1 prompting guidance recommends asking only 1–3 brief questions when key basics would change the result, and Anthropic’s guidance for larger features says to let the agent interview the user first—while also noting that autonomous scheduled tasks cannot ask clarifying questions at all. In practice, that yields a simple rule: **ask only about high-impact ambiguities; assume and document everything else.** citeturn17search6turn17search1turn17search16turn18search1turn18search5

A good decision rule is this:

| Ask the user | Assume and document |
|---|---|
| The ambiguity changes workflow semantics, permissions, billing, destructive behaviour, compliance, or who the user actually is. citeturn17search6turn17search1turn9search1turn9search19 | The ambiguity is about reversible preferences, low-risk defaults, or standard platform conventions such as default sorting, density, or whether quick actions appear on hover and focus. citeturn11search0turn10search9turn6search15 |
| The wrong assumption would force rework across multiple states or artifacts. citeturn33view0turn31view0 | The assumption can be changed later in settings without breaking the core mental model. citeturn10search9turn12search0 |
| The answer is domain-specific rather than product-generic. citeturn39search0turn38search4 | The decision is common enough that a sensible default teaches the product and reduces friction. citeturn11search0 |

My recommended completeness gate for an agent-generated feature spec is straightforward: a feature is **not fully specified** until each primary user goal has a defined happy path, discovery path, empty state, loading state, error or recovery state, permission posture, keyboard path, accessibility note, internationalization note, default-setting decision, and release-layer decision. That checklist is a synthesis, but it is directly supported by the design-system, accessibility, and spec-driven sources above. citeturn36view0turn35view0turn8search0turn5search0turn34search2turn33view0

## A spec template that feeds implementation cleanly

No single artifact captures “look, feel, and behaviour” well enough on its own. PRDs are good at purpose and scope, story maps are good at user journeys and release slicing, interaction inventories are good at affordances, state matrices are good at completeness, promptframes are useful when a design workflow includes generative tools, and Gherkin is the cleanest bridge to executable acceptance criteria because it favours declarative behaviour over implementation detail. citeturn13search1turn13search2turn12search7turn11search27turn13search3turn13search6

A practical stack for agent-generated feature specs looks like this:

| Artifact | What it captures best | Why it should be included |
|---|---|---|
| **Behavioural PRD** | Problem, users, goals, constraints, MVP, non-goals. citeturn13search1 | Keeps the feature anchored to product intent. |
| **Story map** | End-to-end user journey and release slices. citeturn12search7turn40search0 | Prevents features from becoming disconnected lists. |
| **Interaction inventory** | Actions, affordances, gestures, shortcuts, feedback. | Prevents thin, literal interpretations. |
| **State matrix** | Empty, loading, partial, offline, permission, success, error states. citeturn36view0turn35view0turn8search0 | Prevents happy-path-only design. |
| **Promptframe or annotated wireframe** | Layout intent plus AI-generation constraints where relevant. citeturn11search27 | Useful when tooling includes Figma Make, Stitch, v0, or similar tools. |
| **Declarative acceptance criteria** | Observable behaviour and testable outcomes. citeturn13search3turn13search6 | Bridges cleanly to QA, engineering, and automated validation. |

A reusable template that an agent can fill follows.

```md
# Feature Specification

## Feature name
## One-line request
## Problem frame
- User need statement:
- JTBD statement:
- Success statement:
- Non-goals:

## Users and contexts
- Primary users:
- Secondary users:
- Admin / observer roles:
- Usage contexts:
- Devices / surfaces:
- Environmental constraints:

## Assumption ledger
| Decision area | Default assumption | Confidence | Ask user? | Reason |
|---|---|---:|---|---|

## Experience principles
- What the feature should feel like:
- What it must optimise for:
- What tradeoffs are accepted:

## User scenarios
| Scenario | Trigger | Desired outcome | Frequency | Risk if it fails |
|---|---|---|---:|---|

## Story map
| Journey step | User tasks | Notes | Release layer |
|---|---|---|---|

## Interaction inventory
| Object | User can do | System responds with | Shortcut / gesture | Notes |
|---|---|---|---|---|

## Information architecture
- Entry points:
- Main surfaces:
- Secondary surfaces:
- Navigation model:

## Visual and token requirements
- Token categories needed:
- Semantic colour roles:
- Typography roles:
- Spacing / density modes:
- Elevation / layering rules:
- Motion principles:
- Light / dark / high-contrast expectations:

## State matrix
| Scope | State | What user sees | Available actions | Recovery / next step |
|---|---|---|---|---|

## Edge cases and failure modes
| Condition | User expectation | Failure / ambiguity | Required system behaviour |
|---|---|---|---|

## Defaults and settings
| Decision | Default | User-configurable? | Where configured | Why |
|---|---|---|---|---|

## Accessibility requirements
- Keyboard behaviour:
- Screen reader announcements:
- Focus management:
- Colour / contrast requirements:
- Pointer / touch requirements:
- Reduced-motion requirements:

## Internationalization requirements
- Locale-sensitive content:
- RTL behaviour:
- Text expansion handling:
- Pseudolocalization readiness:
- Sorting / collation notes:

## Permissions and privacy
- Role-based behaviour:
- Restricted actions:
- Audit / visibility expectations:

## MVP
- Included:
- Explicitly deferred:
- Why this is still coherent:

## Full vision
- Likely next slices:
- Long-term enhancements:

## Acceptance criteria
### User stories
- As a …
### Gherkin
Feature:
  Scenario:
    Given …
    When …
    Then …

## Open questions
## Appendix
- Copy notes
- Example data
- References
```

## Worked example for a Kanban board in an agent-manager console

Applying the methodology to the sentence **“I want a Kanban board for my agent-manager console”** produces a spec that is meaningfully richer than “show tasks in columns.” The job is to help an operator or manager understand work status, reprioritise work quickly, inspect or act on an item without losing context, and recover gracefully when work is blocked, failing, or inaccessible. Story-mapping, EventStorming-style event enumeration, and cognitive walkthroughs all imply that a real board must cover not just columns and cards, but discoverability, movement, quick inspection, detail inspection, filtering, feedback, and recovery. Platform guidance around drag-and-drop, cards, sheets, context menus, focus, selection, and keyboard access makes those affordances explicit rather than optional. citeturn39search0turn12search7turn38search4turn40search1turn6search9turn6search11turn6search13turn6search16turn6search15turn6search17

**Problem frame.**  
Primary user: an operator managing many agent tasks inside a console. Secondary user: a reviewer or manager monitoring throughput. Tertiary user: a read-only observer. The board’s primary outcome is fast spatial triage and reprioritisation. The board’s secondary outcome is low-friction access to detail and next actions. The board is desktop-first because it lives inside a management console, but it must remain responsive enough for narrower windows and zoomed interfaces. A reasonable default assumption is that the board reflects task lifecycle stages such as Backlog, In Progress, Blocked, Review, and Done, but that exact semantics may need user confirmation because workflow naming is domain-specific. citeturn40search12turn33view0turn17search6

**Core surface and feel.**  
The main surface is a board view with a persistent header, horizontally arranged columns, and vertically stacked cards. Columns must show a title, card count, overflow menu, and optional WIP indicator. Cards must make the most decision-relevant metadata scannable without opening detail: title, status or health cue, labels, owner or agent, last-updated or due-time signal, and any “needs attention” marker. Cards should feel light enough to scan quickly but substantial enough to carry one-step actions. Hover and focus should reveal quick actions without making the default card face visually noisy. Clicking a card opens a detail drawer or sheet rather than a full navigation by default, because sheets preserve board context while allowing deeper inspection. Right-click or equivalent contextual action should expose item-specific actions such as open, assign, label, duplicate, archive, move, and delete, subject to permission. Those behaviours are a direct application of current card, sheet, context-menu, and focus-selection guidance. citeturn6search16turn6search13turn6search11turn6search15

**Primary interactions.**  
The board supports drag-and-drop between columns and within a column. While dragging, the UI must show the dragged card state, insertion placeholder, eligible drop targets, and auto-scrolling near edges. After drop, the system should confirm the move with immediate visual persistence and provide undo if the move changed meaningful state. Because drag is not sufficiently discoverable or accessible on its own, every card also needs a non-drag move pathway: context menu action, card detail action, and keyboard pathway. Search and filtering belong in the board header because they change how the board is interpreted globally; filtering should at minimum cover title or ID, label, assignee or agent, and status. Board-level settings should not be buried inside individual columns because they affect the whole mental model. These decisions follow platform interaction guidance and are reinforced by accessibility guidance that interactions must remain available through different input methods. citeturn6search9turn6search11turn6search17turn9search13

**Interaction inventory.**

| Object | Behaviour |
|---|---|
| Board header | Rename board if permitted; search; filter; clear filters; open board settings; create card; switch saved view in later releases. |
| Column | Rename if permitted; reorder columns in advanced mode; collapse or expand in later release; view count; view WIP state; open column menu. |
| Card | Open detail on click or Enter; open context menu via secondary click or keyboard; drag to reorder or move; quick action for archive or assign; multi-select in later release. |
| Detail drawer or sheet | Edit descriptive fields; change labels or owner; move card; view activity timeline; copy deep link; close without losing board context. |
| Search and filters | Query cards live; show filtered result count; show explicit “no results” empty state; persist last used filters by default only if that does not create confusion. |

The inventory above is a synthesis, but it is the correct synthesis given the combination of story-mapping, cognitive walkthrough, drag-and-drop, context-menu, sheet, and keyboard-access patterns already discussed. citeturn12search7turn40search1turn6search9turn6search11turn6search13turn6search17

**State matrix.**

| Scope | State | Required behaviour |
|---|---|---|
| Board | First-run empty | Explain what the board is for and offer the primary action to create or import the first card. |
| Board | Populated | Show columns and cards with immediate scanability and stable layout. |
| Board | Search empty | Replace prior content with a clear “no results” state plus guidance to clear or adjust filters. |
| Board | Loading | Use skeletons for columns and cards; preserve structure so the board does not feel frozen. |
| Board | Partially loaded | Allow loaded columns to appear while slower ones continue loading; announce busy state to assistive tech. |
| Board | Offline or degraded | Prefer a read-only cached board if available; show connectivity status and what actions are queued or unavailable. |
| Board | Permission denied | Explain whether the problem is board-level or item-level and offer the next valid action such as requesting access. |
| Board | System error | Replace broken content with a plain-language recovery state and a retry path. |
| Column | Empty column | Keep column shell visible and show contextual encouragement or guidance instead of blank space. |
| Column | WIP exceeded | Show a warning state that is not colour-only and clarify whether the limit is advisory or enforced. |
| Card | Default / hover / focus / selected | Each visual state must be distinct; focus must be visible and selection should not rely on colour alone. |
| Card | Dragging / drop target | Show strong spatial feedback for both the dragged card and the receiving location. |
| Card | Saving / failed save | Show in-progress feedback and clear recovery if the move or edit fails. |

This matrix is exactly the kind of thing thin AI elaborations usually omit. Yet empty-state, loading, offline, permission, and recovery patterns are all documented as distinct UX situations with different guidance. citeturn36view0turn35view0turn8search0turn9search1turn9search3

**Edge cases and failure modes.**  
If a user drags a card while a filter is active and the new state removes the card from the filtered view, the system should not make the card appear to “vanish” without explanation; it should briefly confirm the move and explain why the card is no longer shown. If another user moves or deletes the same card while its detail drawer is open, the UI needs a conflict message and a safe next step rather than silently overwriting or closing. If the board contains many columns, the design must preserve orientation through sticky headers, clear overflow handling, and predictable horizontal scrolling. If titles or labels are long, the truncation policy must preserve the ability to inspect the full value via detail or tooltip without breaking keyboard or touch access. If colour labels exist, the board must never rely on colour alone to express meaning. Those are all foreseeable failure points from heuristic evaluation, accessibility principles, and internationalization guidance. citeturn40search16turn12search15turn9search13turn34search2

**Defaults and settings.**  
A strong agent should not dump every possible configuration into “Settings.” The correct balance is to default the common path and expose durable preferences. Recommended defaults: host-app light or dark theme inheritance; compact but readable card density; advisory WIP limits off by default unless the host product already uses them; search across title, ID, labels, and assignee; card details open in side drawer rather than full-page navigation; drag-and-drop enabled where permissions allow; archived cards hidden from the default board. Recommended settings surface: visible card fields, WIP limits and enforcement mode, label taxonomy and colours, board column names and order, density, archived-card visibility, default sort inside columns where manual ordering is not used, and advanced saved views later. That distribution matches guidance on settings patterns and sensible defaults. citeturn10search9turn11search0turn11search23

**Token and visual-state requirements.**  
At spec level, the board should call for semantic tokens rather than hardcoded values: background surface, raised surface, card border, text primary, text secondary, focus ring, drag overlay, drop target, success, warning, danger, status neutral, label role colours, spacing scale, card radius, and elevation levels. It should also call for interaction-state tokens for hover, pressed, focused, selected, disabled, and dragged. Theming should support light, dark, and high-contrast variants through token substitution rather than one-off overrides. Material, Fluent, and Atlassian all describe theming in those terms, and Material’s colour system explicitly includes tokenized contrast choices. citeturn15search1turn15search0turn15search2turn15search14turn14search1turn14search2turn14search21

**Accessibility and internationalization defaults.**  
The board must be fully operable by keyboard, including card discovery, opening, menu access, and non-drag movement. Loading, busy, and failure states should be announced to screen readers; focus order must match the user’s mental model; colour must never be the only signal for urgency or category; and reduced-motion users should not depend on animated drag feedback for comprehension. For internationalization, the board should support Unicode text, locale-sensitive date and time formatting, text expansion, and right-to-left layouts. One ambiguity is important enough to ask about when the product targets RTL markets: should the workflow order itself visually reverse in RTL, or should the interface mirror while preserving the workflow’s logical left-to-right sequence? That is a good example of a high-impact ambiguity worthy of a user question rather than a silent assumption. citeturn5search0turn9search13turn35view0turn34search0turn34search2turn34search4

**MVP versus full vision.**  
The MVP should include: board view, columns, cards, drag-and-drop, detail drawer, context menu, basic labels, board search and simple filters, first-run empty state, loading and error states, permission handling, core keyboard access, and inherited theming. That is enough to make the feature internally coherent. The next slice should add WIP limits, visible saved views, archived-card workflows, richer card fields, and clearer multi-user updates. The long-term vision can add swimlanes, templates, automations, bulk actions, real-time presence indicators, analytics, and advanced saved views. This layering follows Patton’s release-slicing logic and progressive disclosure: the first release should feel complete for the primary job without shipping every advanced control. citeturn12search1turn12search7turn12search0

**Sample acceptance criteria.**  
These scenarios are intentionally declarative, because Cucumber’s guidance is right: behaviour-focused Gherkin becomes better living documentation than step-by-step UI micromanagement. citeturn13search3turn13search6

```gherkin
Feature: Kanban board for agent task management

  Scenario: First-time user sees a productive empty state
    Given I can access the board
    And the board contains no cards
    When the board loads
    Then I should see what the board is for
    And I should see the primary next action to create or import a card

  Scenario: User moves a card between columns
    Given a card is visible in "In Progress"
    When I move the card to "Blocked"
    Then the board should immediately show the card in "Blocked"
    And I should receive confirmation that the move succeeded
    And I should have a way to undo the move

  Scenario: Keyboard user can move a card without drag and drop
    Given focus is on a card
    When I invoke the move action from the keyboard
    Then I should be able to choose a destination column
    And the move should complete without requiring pointer input

  Scenario: Filtered move does not make a card disappear without explanation
    Given the board is filtered to show only "In Progress" cards
    And a visible card matches that filter
    When I move the card to "Done"
    Then I should receive confirmation that the move succeeded
    And I should be told why the card is no longer visible in the current view

  Scenario: Board handles offline access gracefully
    Given I lose network connectivity while viewing the board
    When connectivity is unavailable
    Then the board should clearly indicate degraded or offline status
    And it should distinguish which actions remain available and which do not

  Scenario: Permission-restricted user gets a recoverable denial
    Given I can view the board but cannot edit cards
    When I attempt to move a card
    Then I should be told that the action is not permitted
    And I should remain on the board without losing context
```

## What is actually state of the art in 2026

By mid-2026, it is **established practice** to use AI agents to expand vague tasks into richer plans and to execute those plans with durable repo or project context. OpenAI Codex supports planning before coding, `AGENTS.md`, skills, hooks, background cloud execution, and review. GitHub Copilot cloud agent can research a repository, create a plan, work on a branch, and raise a pull request; GitHub also ships custom agents, skills, MCP support, and an open-source Spec Kit for spec-driven development. Anthropic’s Claude Code supports `AskUserQuestion`, skill authoring, and “interview first” workflows for larger features. Cursor has Plan Mode, rules, team rules, and long-running or parallel agent workflows. Devin supports knowledge, plan-oriented “Ask Devin,” and parallel managed Devins. In other words, the infrastructure for **plan-first, context-rich, reusable agent workflows** is no longer experimental. citeturn31view0turn31view1turn20search4turn23search1turn23search13turn23search19turn23search16turn33view0turn18search8turn18search1turn18search9turn23search8turn23search2turn23search17turn24search16turn24search18turn24search6

It is also established practice to use AI systems to generate UI concepts, prototypes, and even app blueprints from prompts. Figma Make positions itself as a way to turn ideas into editable outputs and real-data-backed apps; Google’s Stitch generates UI designs and corresponding front-end code; Firebase Studio’s App Prototyping agent produces app blueprints, previews, and full-stack apps from natural language; v0 positions itself as an AI agent for real code and full-stack apps; Replit Agent 4 explicitly markets design-canvas iteration, automatic requirement fleshing, and parallel execution. That means the tooling layer is already capable of producing substantial artifacts from rough prompts. citeturn21search2turn21search4turn21search18turn22search0turn22search1turn22search4turn22search10turn22search2turn22search5turn19search2turn19search8

What is **not** fully solved is the quality of product thinking the agent applies when the prompt is vague. NN/g’s 2025 evaluation of AI design tools is especially relevant here: they tested real design scenarios, wrote controlled prompts, ran multiple tool categories, and evaluated the outputs heuristically against real human-created designs. Their methodology and lessons make two points that matter for your use case. First, vague prompts fail; specificity and context dramatically improve results. Second, tool capabilities remain jagged enough that disciplined evaluation, prompt iteration, and documentation are still required. NN/g’s related work on promptframes also reflects the same reality: in the age of generative systems, design teams increasingly need deliverables that specify prompt intent and layout or functional requirements, not just wireframes. citeturn28view0turn11search27

The strongest emerging pattern is **spec-driven development**. GitHub’s Spec Kit argues that AI works better when specifications become living, executable source-of-truth artifacts. OpenAI’s Codex best practices similarly emphasize durable context, skills, and structured prompts with goal, context, constraints, and “done when.” The open `AGENTS.md` format—now stewarded under the Linux Foundation ecosystem and used by tens of thousands of projects—shows that the agent ecosystem is converging on standard ways to package context and instructions. That convergence is important because the hard part of agent-driven feature elaboration is less about raw model intelligence and more about **context engineering**: making the right product, UX, and workflow information available in the right form. citeturn33view0turn31view0turn30view0

The most interesting but still **emerging or contested** layer is the idea of autonomous PM or designer sub-agents. Research and open-source experiments now exist: Spec Kit Agents describes a multi-agent feature-delivery system with a PM agent and developer agent coordinated by a state machine; ReqInOne proposes an LLM-based agent for SRS generation; other requirements-engineering work reports better results when LLMs are used to formalize change requests or automate requirements analysis. These are important signals, but they are not yet mature enough to treat as settled best practice for product-grade feature design. They show what is becoming possible, not what is already dependable without strong human oversight. citeturn25search23turn25search8turn25search0turn25search20turn25search14turn25search2

If I had to state the 2026 reality bluntly: **agents are already good enough to produce structured, rich first-draft feature specs from vague prompts, but only when you force them through a disciplined product-design workflow.** They are not yet reliable enough to skip that workflow and still consistently infer all the interaction, state, accessibility, and scoping decisions a senior designer would make. The state of the art is therefore not “one magic prompt.” It is a pipeline of prompting, planning, intermediate artifacts, durable instructions, and explicit evaluation. citeturn33view0turn31view0turn18search1turn28view0

## Guardrails, limitations, and open questions

The main way to avoid **under-specification** is to force coverage. If the agent has not produced user goals, scenarios, interactions, states, defaults, edge cases, accessibility, internationalization, and release slices, it has not finished the spec. The main way to avoid **over-specification** is to require that every detail either supports a user job, satisfies an established platform or accessibility rule, or clearly belongs to a later release. Progressive disclosure and release slicing are the core disciplines here. citeturn12search0turn12search1turn39search0turn5search0

A few limitations remain unavoidable. First, some decisions are genuinely domain-specific and should still be confirmed with the user or product owner: workflow semantics, permission model, destructive-action policies, audit requirements, and whether the feature must preserve existing enterprise conventions. Second, internationalization is not just string translation; features that encode directional workflow, label taxonomies, dates, and status semantics can have deeper locale implications than generic AI agents assume. Third, “design completeness” still needs review against real user goals and organisational standards, even when the draft is strong. That is exactly why the newer agent ecosystems have converged on plans, approvals, skills, and durable context instead of claiming that free-form prompting alone is sufficient. citeturn17search6turn17search1turn34search2turn34search4turn31view0turn23search1

The most useful open questions for a reusable agent skill are these. Which ambiguities should always trigger a clarifying question in your product domain? Which defaults are sacred because they match your design system or operating model? Which artifact bundle is mandatory for handoff in your team? And which evaluation loop will you run on the produced spec—heuristic review, walkthrough review, or implementation-backpropagation review—before you trust it? Those are not gaps in the research; they are the places where a generic agent becomes a high-performing, organisation-specific product-design agent. citeturn40search16turn40search1turn31view1turn30view0