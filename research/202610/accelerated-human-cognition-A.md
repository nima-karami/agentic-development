# Helping Humans Understand, Learn, and Decide Faster

This report answers the research brief you supplied for designing reusable agent skills around human comprehension and decision-making. fileciteturn0file0 The central finding is that **there is no single “fast comprehension” format**. The strongest evidence instead supports matching the representation to the cognitive job, reducing unnecessary search and working-memory demands, exploiting prior knowledge where it exists, and requiring some active reconstruction when genuine learning matters. citeturn21view8turn21view9turn21view5

## Executive answer

### The principles that matter most

| Rank | Principle | Evidence | Practical consequence for an agent |
|---|---|---|---|
| **A** | **Externalize structure instead of making the reader hold it in working memory.** | **Strong.** Working memory is sharply capacity-limited; the exact number is not a universal “4” or “7,” and useful chunks depend heavily on prior knowledge. Diagrams, grouping, tables, and schemas help when they make task-relevant relations explicit rather than merely decorating the material. citeturn21view8turn0search11turn21view5 | Group related facts, expose hierarchy and dependencies, keep labels next to what they describe, and avoid forcing the reader to mentally join information scattered across a response. |
| **A** | **Lead with the answer or decision, then reveal the reasoning at increasing depth.** | **Strong rationale; weaker direct evidence for BLUF itself.** Structured representations reduce search costs; Army BLUF is an explicit writing convention, while direct controlled evidence that “BLUF” as a branded method is superior is sparse. citeturn21view5turn14search13 | For decision/status work: `Bottom line → why → risks/unknowns → evidence/details`. Do not make the human read an essay to discover what the agent recommends. |
| **A** | **Match representation to relationship: comparison→table, topology→diagram, change→diff, quantity→chart, argument→prose.** | **Strong to moderate.** Tables outperform prose for many lookup/comparison tasks; diagrams help when they spatially encode relations; graphical-perception experiments show that some quantitative encodings are substantially easier to judge accurately than others. citeturn3search13turn21view5turn16search0turn16search15 | Do not ask “Would a diagram look nice?” Ask “What relationship must the reader perceive?” |
| **A** | **For learning, retrieval beats rereading. Make the human produce an answer before showing it.** | **Strong and replicated.** Retrieval practice improves delayed retention even when restudy produces more immediate fluency/confidence; spacing further improves long-term retention. citeturn21view1turn22search0turn21view3 | An AI tutor should ask for a prediction, explanation, reconstruction, or answer before supplying its own complete explanation. |
| **A** | **Design differently for novices and experts.** | **Strong.** Expertise changes what constitutes useful support. Domain experts recognize meaningful patterns and can compress information into schemas; guidance that helps novices can become redundant or counterproductive for experienced people. citeturn2search13turn11search1turn21view4 | Ask or infer familiarity. Give novices worked examples, terminology, and orientation. Give experts anomalies, deltas, evidence, edge cases, and shortcuts to source material. |
| **B** | **Relevant words plus relevant graphics can help; “visual is always better” cannot.** | **Moderate to strong for specific multimedia principles.** Integrating related text and diagram elements spatially improved integration and transfer in several experiments, but diagrams and animation can also add load or fail to improve comprehension. citeturn15search14turn15search17turn3search11 | Prefer a small, task-specific diagram with directly attached labels over a large decorative architecture picture. |
| **B** | **Make uncertainty, assumptions, alternatives, and confidence visible.** | **Strong practice in high-stakes analytic disciplines; conceptually well supported.** U.S. intelligence standards explicitly require analysts to distinguish evidence from assumptions/judgments, communicate uncertainty, describe source quality, and consider alternatives. citeturn19search10turn21view7 | A decision brief should never make a probabilistic recommendation look like a fact. Separate `known`, `inferred`, `unknown`, and `recommended`. |
| **B** | **Use independent human judgment before AI advice when error matters.** | **Moderate experimental evidence plus a mature automation-bias literature.** Incorrect automation can pull judgments in the wrong direction; experiments have found worse effects when erroneous AI advice arrives before a person's own judgment. citeturn14search0turn14search17turn14search12 | For reviews, estimates, diagnoses, or architecture choices, sometimes ask the human for an initial assessment before exposing the model's recommendation. |
| **B** | **Check understanding by production or transfer, not by “Does that make sense?”** | **Strong learning evidence.** Retrieval, self-explanation, and application reveal gaps that familiarity and rereading can conceal. citeturn21view1turn11search2turn10search20 | Ask “Explain the failure path,” “What would happen if X changed?”, or “Which option would you pick and why?” rather than “Understood?” |
| **C** | **Progressive disclosure is a useful interface heuristic, not a cognitive law.** | **Mixed direct evidence.** Layered presentation can reduce visible complexity, but experiments do not show that layering automatically improves finding or understanding information; domain knowledge often matters more. citeturn3search12 | Use layers to serve different reader intentions, not to hide information arbitrarily. The first layer must remain decision-complete. |

A useful default for agent output is therefore:

> **Answer → consequences → evidence/reasoning → uncertainty → detail on demand → comprehension check when learning or high stakes.**

That is much closer to what the evidence supports than “always summarize,” “always make a diagram,” “always use three bullets,” or “people are visual learners.” The popular **learning-styles/meshing hypothesis**—that a person learns better when instruction is matched to a diagnosed “visual,” “auditory,” or similar preference—does not have an adequate evidentiary basis and should not be implemented in an agent. citeturn22search7turn22search11

## What the science actually says

### Working memory, cognitive load, and chunking

Working memory is genuinely constrained, but software-writing advice often turns this into false precision. Miller's famous “seven plus or minus two” is not a reliable universal capacity limit, and Cowan's later synthesis argued for something closer to a small handful of independent chunks under controlled conditions. More importantly, **a chunk is not a free compression token**: what counts as one depends on learned structure and long-term knowledge. citeturn21view8turn0search11

This explains an important expert/novice difference. A senior engineer can see “OAuth authorization-code flow” or “optimistic state update” as a meaningful unit carrying many subordinate relations; a novice may need to hold each step separately. Chase and Simon's classic chess work similarly found that expertise changes perception of meaningful configurations rather than simply giving experts a larger generic short-term memory. citeturn2search13

Sweller's cognitive-load work adds a useful design implication: problem-solving activities can consume the same limited cognitive resources needed to construct useful schemas. This is why unguided struggle is not automatically good learning and why worked examples can be particularly useful early in skill acquisition. citeturn21view9

But **“minimize cognitive load” is itself too crude**. The goal is not to make the person think as little as possible. Some mental effort is exactly what creates understanding. The right goal for agent design is:

**remove effort spent locating, remembering, decoding, and reconciling information; preserve effort spent reasoning, retrieving, comparing, explaining, and deciding.** This is a synthesis of the cognitive-load and retrieval-practice findings rather than a named experimental law. citeturn21view9turn21view1turn22search0

That distinction is particularly important for AI. A beautifully summarized answer can reduce both *wasteful* effort and *productive* effort. The first is desirable; the second can leave a user able to recognize an explanation but unable to reconstruct it later. citeturn21view1turn10search20

### Dual coding and multimedia: narrower than the slogan

There is good evidence that people can benefit when complementary verbal and pictorial representations are designed so that the reader can integrate them. In three eye-tracking experiments on how car brakes work, Johnson and Mayer found that placing corresponding text close to diagram elements led to more text-diagram integration and, in two experiments, better transfer than separating the explanation from the graphic. citeturn15search14

But this does **not** imply “add an image.” Mayer and colleagues also found in four experiments that static annotated diagrams could outperform narrated animations for explanations of dynamic systems. The learner's ability to control inspection and revisit a static representation can matter more than motion itself. citeturn15search17

A separate experiment with schoolchildren found little or no comprehension advantage from adding diagrams to science texts in some conditions, illustrating that a graphic can become another representation the reader must decode rather than a shortcut. citeturn3search11

The agent rule should therefore be:

> **Use a graphic when the graphic performs cognitive work that prose would otherwise force the reader to simulate mentally.**

That includes revealing topology, spatial location, temporal ordering, causality, flow, magnitude, grouping, or dependency. It does not include a decorative box-and-arrow rendering of sentences already easy to read. This formulation follows Larkin and Simon's core insight that diagrams are valuable when they make useful information computationally and perceptually accessible—not because graphics are intrinsically superior. citeturn21view5

And none of this rescues “visual learner” classifications. Preferences exist; evidence that learning improves by matching teaching modality to an individual's purported learning style does not. citeturn22search7turn22search11

### Visual attention and “pre-attentive” processing

Visual-search experiments support a real but narrower phenomenon behind “pre-attentive processing”: some distinctive single features can be detected rapidly among distractors, while finding conjunctions or relations can require focused attention and become slower as a display becomes more complex. Treisman and colleagues' work on feature integration and search asymmetry established much of this experimental basis. citeturn15search0turn15search2turn15search11

This supports restrained use of salience in agent-created interfaces: a single status icon, one unusual value, or one highlighted changed component can attract attention efficiently. It does **not** support colouring ten categories, bolding half the response, or assuming a complex architecture can be “seen instantly.” Once many things compete for salience, the shortcut disappears. citeturn15search11turn15search7

### Quantitative displays

Cleveland and McGill turned graphical perception into an experimental question rather than an aesthetic one. Their work and subsequent experiments found that judgments based on position are generally more accurate than less direct encodings; a later Cleveland–McGill experiment found position judgments most accurate, length next, angle/slope below those, and area worst among the six types it tested. citeturn16search0turn16search15

Heer and Bostock later replicated graphical-perception experiments using crowdsourcing and extended them to area judgments and other visualization parameters, strengthening the empirical basis for treating chart encodings as perceptual choices rather than mere style. citeturn16search1turn16search3

For agents, the important consequence is simple: **when exact comparison matters, put values on a common positional scale**. A dot plot or bar chart is ordinarily a safer quantitative comparison device than bubbles, areas, perspective effects, or decorative dashboards. citeturn16search0turn16search15

Tufte's work is enormously influential design practice, but it should be categorized differently: principles such as removing non-data decoration are **practitioner/design heuristics**, whereas Cleveland and McGill provide experimental evidence for perceptual encoding accuracy. Do not turn every Tufte maxim into a “scientifically proven” rule.

### Expertise and recognition-primed decisions

Klein's fire-ground research is often caricatured into “experts trust intuition.” The original study is more specific. Interviews with 26 highly experienced fire-ground commanders examined 156 decision points; simultaneous comparison among multiple options appeared in fewer than 12%, while in more than 80% the commanders recognized a familiar situation pattern and a typical course of action. Klein synthesized this into the recognition-primed decision model. citeturn21view4

This is powerful evidence that **experienced practitioners in familiar domains can make fast decisions through pattern recognition**, but it is a field study in a particular expert population, not proof that intuition is generally superior. Recognition is only as good as the pattern repertoire and feedback history behind it. citeturn21view4turn2search13

For software work, this suggests that an agent should avoid forcing a senior engineer through a generic multi-criteria decision matrix for every familiar operational problem. Instead, it can lead with:

> “This looks like the familiar stale-cache/invalidation failure pattern. The two observations supporting that recognition are X and Y. The thing that would falsify it is Z.”

That preserves expert speed while exposing the evidence needed to catch a false match.

### Sensemaking

Sensemaking is best understood here as the construction and revision of a useful representation of a messy information space. Larkin and Simon's representation work shows why changing representation can change the amount of search and computation required; information-foraging work similarly models the costs of searching through an information environment. citeturn21view5turn5search22

Software-program comprehension provides a particularly relevant real-world example. In an observational experiment on unfamiliar-code maintenance, developers repeatedly searched for relevant code, followed incoming and outgoing dependencies, and collected information for later use. The participants spent about 35% of their time on the mechanics of navigation between and within files. citeturn18search0

A field study of 28 professional developers likewise found recurring, context-dependent comprehension strategies rather than one universal way of reading a system. Developers used interfaces, code, standards, prior experience, and communication with colleagues to build enough understanding for the maintenance task at hand. citeturn17search4

This makes one of the strongest cases for AI assistance: **an agent can accelerate sensemaking by maintaining the map while the human reasons about it**—for example, relevant files, entry points, call paths, invariants, owners, runtime observations, terminology, and unresolved questions. That removes navigation and bookkeeping without necessarily outsourcing judgment. citeturn18search0turn18search3

## Choosing the right representation

The most useful format decision is not based on content size. It is based on **the operation the human must perform on the information**.

### Content-type → format decision table

| Human task / content | Default format | Why | Avoid |
|---|---|---|---|
| **Simple answer or status** | **One-sentence bottom line + brief evidence** | Search for the conclusion should be near zero. BLUF is an established Army writing convention, although direct experimental evidence for BLUF specifically is limited. citeturn14search13 | A chronology that ends with the answer. |
| **Decision with a recommended action** | **Decision brief** | Separates recommendation, reasons, alternatives, assumptions, uncertainty, and consequences. Intelligence tradecraft explicitly requires alternatives and uncertainty to remain visible. citeturn19search10 | Recommendation buried in neutral background. |
| **Compare options against common criteria** | **Table** | Rows/columns spatially align corresponding attributes and reduce repeated prose. Experiments have found tabular/graphical displays more efficient than textual displays for many statistical comparison tasks. citeturn3search13 | One paragraph per option that forces the reader to remember earlier values. |
| **Code change / before versus after** | **Diff + semantic summary** | Diff externalizes correspondence and isolates change; summary tells the reader which changes matter. This recommendation is a representational synthesis rather than a well-established “diff effect.” Program-comprehension research nevertheless shows that navigation and relation-finding consume substantial developer time. citeturn18search0 | Restating the entire new implementation with changed pieces hidden inside it. |
| **Architecture / components / topology** | **Node-link or container diagram + short prose** | Spatial co-location and explicit edges can make relationships directly inspectable. citeturn21view5 | Boxes that have no meaningful edge semantics or abstraction level. |
| **Execution or request flow** | **Sequence diagram / numbered flow** | Encodes temporal order and participants explicitly rather than forcing mental simulation. This is an application of the diagrammatic-representation evidence. citeturn21view5turn15search14 | Generic architecture picture with arrows pointing everywhere. |
| **State-dependent behaviour** | **State-transition diagram/table** | Makes permitted states and transitions explicit. citeturn21view5 | Long prose containing many “unless,” “except,” and “when.” |
| **Hierarchy / ownership / containment** | **Tree or indented hierarchy** | Spatial nesting mirrors the relation being understood. citeturn21view5 | Flat list with path information repeated in every item. |
| **Trend over time** | **Line chart** | Position on common aligned scales supports accurate quantitative judgment. citeturn16search0turn16search15 | Table of dozens of time points unless exact lookup is the task. |
| **Compare magnitudes** | **Dot/bar chart on a common scale** | Position and length are perceptually stronger quantitative encodings than angle or area. citeturn16search15 | Pie charts or bubbles when precise comparison matters. |
| **Exact values / lookup** | **Compact table** | Preserves precise values and supports scanning by field. citeturn3search13 | Chart when the user's task is “what exactly is X?” |
| **Causal hypothesis** | **Causal graph plus prose explaining evidence** | Graph exposes the proposed directional relationships; prose is still required to distinguish evidence from inference. citeturn21view5turn19search10 | A causal-looking arrow diagram that silently turns correlation into causation. |
| **Procedure with known mandatory steps** | **Checklist** | Checklists externalize memory for omission-prone procedural tasks; aviation and surgical work provide strong practical precedent. citeturn8search1turn8search3 | Using a checklist for a novel diagnosis or strategic problem requiring interpretation. |
| **Handoff / urgent brief** | **SBAR-like fixed schema** | Standard slots reduce ambiguity about what must be communicated; clinical studies show improved handoff quality, though patient-outcome evidence is not uniformly strong. citeturn14search4turn14search1 | Free-form chronological storytelling. |
| **Unfamiliar concept or mechanism** | **Worked example + explanatory diagram + retrieval question** | Guidance reduces novice search; integrated graphics can help; retrieval makes the learner reconstruct the model. citeturn21view9turn15search14turn22search0 | Summary-only “explanation” followed by “Got it?” |
| **Research findings** | **Key findings first + evidence table + narrative synthesis** | Lets the reader distinguish claims, source strength, uncertainty, and implications. Intelligence analytic standards offer a useful model for evidence/assumption separation. citeturn19search10 | One polished synthesis in which strong and weak evidence sound equally certain. |
| **Large reference document** | **Layered document with navigation** | Useful when readers have different depths of need, although direct evidence that progressive disclosure itself improves comprehension is mixed. citeturn3search12 | Hiding information required to evaluate the top-level conclusion. |
| **Model with many manipulable variables** | **Interactive explorable, plus static conclusion** | Interactive simulations can improve conceptual learning when manipulation makes hidden relationships observable, but benefits are highly task-dependent. citeturn17search12turn17search14 | Building interactivity merely because the medium permits it. |

### A format-selection algorithm for an agent

An agent can make the decision with five questions:

**What does the human need to do?** If they need to decide, lead with a recommendation. If they need to learn, create a mental model and test it. If they need to inspect, preserve evidence and locality. If they need to look something up, optimize scanning rather than narrative flow. These are different tasks and should not share one default response template. citeturn21view5turn21view1

**What relation dominates the content?** Similarity suggests a table; sequence suggests a flow; topology suggests a network/container diagram; hierarchy suggests nesting; magnitude suggests a quantitative chart; argument and rationale usually require prose. citeturn21view5turn16search15

**Does exactness or pattern matter more?** Tables preserve exact numbers; charts make patterns and relative magnitudes easier to see. citeturn3search13turn16search15

**How much prior knowledge does the reader have?** A novice often needs orientation, definitions, examples, and causal explanation. An expert benefits more from exceptions, evidence, deltas, and direct access to source material. citeturn11search1turn2search13

**What happens if the reader is wrong?** As stakes rise, expose assumptions, provenance, uncertainty, alternatives, and verification paths rather than making the presentation merely shorter. citeturn19search10turn14search0

### How the named presentation methods fare

**BLUF.** Excellent operational convention, weak as a separately validated scientific intervention. The U.S. Army explicitly instructs writers to place the recommendation, conclusion, or reason for writing near the beginning. Its value is highly plausible from search-cost and structured-communication research, but the evidence should be described as **practitioner doctrine supported by broader cognitive principles**, not “research proves BLUF.” citeturn14search13turn21view5

**Minto Pyramid.** The idea of leading with a conclusion and grouping supporting arguments hierarchically is cognitively plausible and commercially influential, but the direct controlled evidence is surprisingly thin. A recent preregistered study protocol explicitly frames Pyramid Principle effectiveness as needing controlled empirical examination. Treat it as **well-established practitioner technique, not replicated cognitive-science law**. citeturn9search0

**Progressive disclosure / layered documents.** Good for managing screen complexity and serving readers with different information needs, but not an automatic comprehension enhancer. In one experiment with linear versus layered financial documents, layering did not improve information finding; skill and domain knowledge were important predictors. citeturn3search12

The right version of progressive disclosure is therefore **semantic layering**, not arbitrary hiding:

> Layer 0: the answer  
> Layer 1: enough evidence to decide whether to trust or act on it  
> Layer 2: reasoning and alternatives  
> Layer 3: raw evidence, implementation detail, provenance

Each earlier layer should be a coherent compression of the next—not a teaser that requires expansion to discover caveats that reverse the conclusion.

**Executive summaries.** Useful when they function as navigational and decision aids, but dangerous when they become substitutes for the evidence needed to evaluate a consequential conclusion. The intelligence-community model is instructive: key judgments can be concise, but source credibility, uncertainty, assumptions, alternatives, and logical argument remain part of analytic quality. citeturn19search10

**Tables versus prose.** Use tables when a reader needs to perform repeated comparisons against shared attributes. Use prose when order, causality, qualification, or argument is the central structure. Experimental display research supports the efficiency of tabular and graphical formats over text for many structured statistical tasks; it does not mean prose is generally inferior. citeturn3search13

**Diagrams.** Use them for relationships. Larkin and Simon showed why informationally equivalent diagrammatic and sentential representations can differ in computational efficiency: good diagrams co-locate relevant information and make useful relations explicit. The word “sometimes” in their title is important. citeturn21view5

**Data visualization.** Use charts for perceptual questions, especially comparison and trend detection, and prefer strong quantitative encodings such as aligned position. Tufte is useful design guidance; Cleveland–McGill and later experiments are the stronger evidentiary foundation for specific perceptual claims. citeturn16search0turn16search15turn16search1

**Worked examples.** Strong for novices because they remove much of the search burden of figuring out solution procedures while the learner is still constructing schemas. As expertise rises, the same guidance can become redundant—the expertise-reversal effect. citeturn21view9turn11search1

**Analogies.** Useful when they map the *relational structure* of a known system onto an unfamiliar one. Experiments by Loewenstein, Thompson, and Gentner found that comparing analogous cases promoted schema abstraction and later transfer better than processing comparable cases separately. citeturn11search14

For an AI assistant, a stronger pattern is therefore:

> “Redis is like a shared memo board”  
> **plus:** “the useful correspondence is X→Y; the analogy breaks at A and B.”

A vivid analogy without explicit correspondence can produce memorable misunderstanding.

**Comparisons and diffs.** Strong representational rationale, but less direct cognitive-science evidence for “diff” as a named format. When the task is to identify a change, preserving alignment between old and new information reduces the search needed to establish correspondence; this is especially valuable in software, where navigation itself is a major cost. citeturn21view5turn18search0

**Interactive explorables.** The evidence supports interactivity when interaction exposes a causal or mathematical relationship through prediction, manipulation, and feedback. Simulation studies in medicine have demonstrated better conceptual knowledge and transfer under appropriately integrated instruction, and randomized case simulation has improved performance on subsequent cases. citeturn17search12turn17search14

The operative word is **appropriately**. A static chart is better than an interactive chart when the reader merely needs one conclusion. Interactivity earns its complexity when the question is “How does the system behave if I change this?”

## What high-stakes briefing disciplines contribute

High-stakes fields converge on an important pattern: **compress the message, standardize the important fields, but do not compress away the information needed to detect error**.

### Military: bottom line and intent

BLUF addresses a reading problem: expose the main message before supporting detail. The Army explicitly teaches writers to place the key message in the opening paragraph and often the first line of a section. citeturn14search6turn14search13

Commander's intent addresses a different problem: **how to preserve competent action when the detailed plan becomes obsolete**. Current Army material describes intent in terms of purpose, key tasks, and end state; the point is to let subordinates make rapid decisions consistent with the objective when circumstances diverge from the plan. citeturn19search0turn19search2

That transfers unusually well to agent-generated software plans. Instead of emitting only:

> “Change files A, B, and C; add endpoint D; migrate table E.”

include:

> **Purpose:** eliminate duplicate authorization logic.  
> **Key invariants:** existing clients remain compatible; authorization stays server-side.  
> **End state:** one policy path, old endpoint removed after migration.  
> **Freedom:** implementation details may change if those invariants remain true.

That makes an AI plan more robust to discoveries during implementation.

### Medicine: SBAR and closed-loop communication

SBAR standardizes a handoff into **Situation, Background, Assessment, Recommendation**. Clinical evidence is promising but should not be oversold: a systematic review found moderate evidence for improved patient safety but also substantial heterogeneity and a lack of high-quality studies. citeturn14search1turn14search7

Individual studies have found better handoff-quality scores after SBAR-style interventions and reductions in reported communication-related incidents in particular clinical contexts. citeturn14search4turn14search9

For software, the transferable idea is not the literal acronym. It is **fixed information slots for recurrent high-cost handoffs**. An incident handoff might be:

```text
SITUATION
Checkout error rate rose from baseline after deploy X.

CONTEXT
Only the EU path is affected. Rollout reached 40%.

ASSESSMENT
Likely failure in new VAT lookup; confidence: medium.
Evidence: logs A/B. Competing hypothesis: downstream provider latency.

ACTION
Pause rollout now.
Owner: ___
Next discriminating check: ___
```

A related medical/team practice is closed-loop communication: requests and critical information are acknowledged or repeated back so both sides can detect mismatched understanding. AHRQ's TeamSTEPPS materials explicitly include check-backs and teach-backs for this purpose. citeturn6search4

That maps directly to agents: for a destructive migration, permission change, or production incident, ask the human to confirm the consequential interpretation rather than merely click “continue.”

### Aviation and surgery: checklists

Aviation human-factors work emphasizes that checklist design, length, presentation, and the operational context all affect whether a checklist performs its job; checklists compensate for predictable omissions rather than replace pilot expertise. citeturn8search1turn8search2

The WHO surgical-safety-checklist study across eight hospitals reported reductions in deaths and inpatient complications after implementation, but it used a before/after design rather than randomized assignment, so the size of the causal effect attributable strictly to the checklist cannot be isolated cleanly. citeturn8search3

The software transfer is narrow but valuable:

**Use a checklist when the failure mode is forgetting a known mandatory condition. Do not use it when the task is figuring out what the condition should be.**

Good examples are a deploy gate, security-release gate, database-migration preflight, or incident-resolution checklist. Architecture design is not a checklist problem.

### Intelligence: evidence, alternatives, and calibrated language

This is arguably the most valuable high-stakes transfer for AI-generated research and recommendations. ODNI's analytic standards require products to describe source quality and credibility, explain uncertainty, distinguish information from analysts' assumptions and judgments, consider alternatives, address customer implications, and make the logic clear. citeturn19search10turn21view7

A software decision brief can adopt the same discipline:

```text
JUDGMENT
Option B is the best default.

CONFIDENCE
Medium-high.

OBSERVATIONS
- ...
- ...

ASSUMPTIONS
- Traffic remains below ...
- Provider X maintains ...

ALTERNATIVES CONSIDERED
A — ...
C — ...

WHAT WOULD CHANGE THE RECOMMENDATION
- ...
```

This is better than a fake “87% confidence” unless the number is derived from an actually calibrated probabilistic model. A qualitative confidence label tied to explicit evidence and assumptions is less precise-looking but often more honest.

### Executive memos: Amazon's six-pager

Amazon's narrative culture is a useful practitioner example, but not scientific evidence that six pages is an optimal cognitive length. Bezos's 2017 shareholder letter describes replacing PowerPoint with narratively structured six-page memos that attendees read silently at the start of the meeting. He also explicitly notes that memo quality varies. citeturn22search3

The transferable mechanism is more interesting than the page count:

**make the argument inspectable in a durable artefact before discussion begins.**

That reduces dependence on presenter charisma and ensures people are responding to the same information. But “six pages” is an organizational convention, not a known human-memory constant.

### What should transfer to software

The common pattern across these domains is:

| High-stakes practice | Software analogue |
|---|---|
| BLUF | Recommendation/status first |
| Commander's intent | Purpose + invariants + desired end state |
| SBAR | Fixed schema for incidents, escalations, and handoffs |
| Checklist | Deploy/release/migration omission defence |
| Closed-loop communication | Confirmation of consequential interpretation |
| Intelligence key judgments | Recommendation + evidence + assumptions + uncertainty + alternatives |
| Six-page narrative | Durable design/decision memo read before debate |

The deeper principle is **standardize the shape of recurring communication so the human does not have to rediscover where the important information is every time**. The evidence for each named format varies considerably, but that convergence across high-stakes practice is useful design evidence when kept separate from experimental claims. citeturn14search13turn19search0turn14search1turn19search10turn22search3

## Learning an unfamiliar domain or codebase quickly

### Fast orientation is not the same as durable learning

There are at least three different goals hidden inside “get me up to speed”:

**orientation** — know the landscape and vocabulary;

**operational competence** — perform a task successfully;

**durable understanding** — reconstruct the model later and transfer it to a novel case.

AI is exceptionally good at accelerating the first and often the second. The risk is mistaking success at those for the third. Retrieval-practice research is especially relevant because rereading can increase confidence while producing less delayed retention than retrieval. citeturn21view1turn10search20

### A better AI-assisted codebase-learning sequence

For an unfamiliar codebase, the agent should start **task-centred, not encyclopedia-centred**. Observational software-engineering research shows that developers commonly search for relevant code, follow dependencies, and gather information around the task they are trying to complete. Professional developers similarly use recurring comprehension strategies tied to their immediate work context. citeturn18search0turn17search4

A strong sequence is:

**Orient.** Give a one-screen map: what the system does, principal runtime boundaries, entry points, data stores, external services, and five to ten domain terms. Do not start with a complete directory tour.

**Trace one concrete path.** Choose a meaningful operation such as “user submits checkout” and trace it end-to-end through UI, API, domain logic, persistence, and external calls. A worked example gives the learner a scaffold before they must infer the system unaided. citeturn21view9

**Show the map after the path.** Now place those components in the architecture. This binds abstraction to something concrete rather than presenting unlabeled boxes first.

**Ask the learner to predict another path.** For example: “Where would you expect refund authorization to live?” Do not reveal the answer yet.

**Inspect the actual implementation and compare.** Differences between prediction and reality are especially informative because they force model revision.

**Ask for reconstruction.** “Without looking back, explain where authorization is enforced and what calls it.” Retrieval itself strengthens later access to the knowledge. citeturn21view1turn22search0

**Give a transfer problem.** “Where would you add a rule that applies only to EU refunds?” A correct answer demonstrates more than recognition of the earlier walkthrough.

**Revisit later.** Spacing learning encounters improves retention; a study with more than 1,350 participants found that the best review interval depends on how long the material must ultimately be retained. citeturn21view3

Recent research on students working in a large real codebase also found predominantly top-down and text-first approaches alongside navigation, debugging, and experimental code changes, supporting the idea that comprehension emerges from coordinated views and actions rather than reading every file in order. citeturn17search1

### Retrieval practice should be built into the agent

Roediger and Karpicke found that repeated studying gave better immediate performance at five minutes, yet testing produced substantially better retention after two days and one week—even while repeated studying produced greater confidence. citeturn21view1

Karpicke and Blunt also found retrieval practice outperforming an elaborative concept-mapping condition on subsequent comprehension and inference tests. That particular comparison drew methodological criticism about how the concept-mapping treatment was implemented, so it should not be read as “concept maps are bad”; it does reinforce a much broader retrieval-practice literature. citeturn22search0turn22search1

So a code-learning agent should periodically stop giving information and say:

```text
Before I show the call path:

1. Which component do you expect owns this rule?
2. What evidence led you there?
3. What would you inspect next to test that guess?
```

Then reveal the trace.

That is slower than simply emitting the answer, but far more likely to produce a usable mental model.

### Concept maps

Concept maps are best treated as **externalized models and diagnostic artefacts**, not magic study devices. They are useful for revealing what the learner thinks is related to what and therefore exposing omissions or incorrect relations. Retrieval has stronger evidence as a general mechanism for retention; the two can be combined by asking the learner to reconstruct a concept map from memory. citeturn22search0turn22search1

### Analogies and comparisons

One analogy is useful; **comparing multiple structurally similar cases is often better** because it encourages abstraction of the common relation rather than memorization of surface features. Gentner and colleagues' experimental work on analogous cases supports this comparison-based route to schema abstraction and transfer. citeturn11search14

An AI tutor could therefore teach event sourcing with:

```text
Case A: bank ledger
Case B: Git commit history
Case C: append-only audit log

Common structure:
- events preserved
- current state derived
- historical reconstruction possible

Where the analogies break:
- ...
```

### Self-explanation

Chi and colleagues' classic work found that more successful learners generated more self-explanations while studying worked examples, connected steps to principles, and monitored their own understanding more effectively. citeturn11search2

An agent should exploit this by changing:

> “Here is why this cache invalidation works…”

to:

> “Why does invalidating only key X suffice here? Explain it first; then I will compare your model with the implementation.”

### Expertise reversal

Instructional scaffolding must decay as expertise increases. Reviews of the expertise-reversal effect document cases where methods that help low-knowledge learners lose their benefit or become detrimental as prior knowledge grows. citeturn11search1

A reusable skill should therefore have at least three information modes:

```text
ORIENTATION MODE
Definitions, worked path, important landmarks, rationale.

WORKING MODE
Answer, relevant context, evidence, exceptions.

EXPERT MODE
Delta, anomaly, risk, source locations, counterexample.
```

The distinction should be based on demonstrated task knowledge where possible, not personality labels or “learning styles.”

## AI-specific risks and how to keep the human genuinely in the loop

### Automation bias is older than generative AI

Decision automation can improve speed and accuracy when correct, but it changes how humans allocate attention. In one Human Factors experiment, a correct decision aid produced faster and more accurate diagnoses with lower workload; after repeated correct performance, an unexpected **wrong recommendation** caused a substantially larger accuracy degradation than simply having the automation disappear. citeturn14search0

The broader automation-bias literature reports both omission errors—failing to act because automation failed to flag something—and commission errors—following incorrect automated advice. These effects are not confined to novices and are not eliminated by simple instructions or practice. citeturn14search2

LLMs inherit this problem and add an especially dangerous property: wrong output can be articulate, internally coherent, and customized to the user's question.

### Letting the human think first can matter

Two experiments on AI-supported judgments found that incorrect algorithmic advice reduced accuracy particularly when participants received the AI's judgment **before** forming their own. citeturn14search17

A separate pair of experiments with decision support under time pressure found that support was more useful when automation advice followed the person's own inspection rather than preceding it. citeturn14search12

This suggests a powerful interaction pattern for consequential tasks:

```text
Human forms initial view
        ↓
AI provides independent view
        ↓
System highlights disagreement
        ↓
Human resolves the disagreement using evidence
```

rather than:

```text
AI gives polished recommendation
        ↓
Human searches for reasons to accept/reject it
```

The first protects an independent signal. It should not be used for trivial work where the added friction costs more than it saves.

### “Explainable AI” does not automatically solve over-reliance

This is an important anti-myth. Explanations can themselves become persuasive output.

In a mixed-method human-AI study, feature-based explanations did not reliably improve outcomes and could increase over-reliance, while example-based explanations produced better complementary performance in that experimental setting. citeturn21view11

Five preregistered experiments in personnel selection likewise found that incorrect AI advice consistently harmed performance because participants failed to reject it, while the tested forms of explainability had limited protective effect. citeturn14search20

Therefore:

> **Do not equate “the model showed reasoning” with “the human can safely trust it.”**

For agent output, provenance, counterevidence, inspectable artefacts, and falsification tests are usually more valuable than a persuasive paragraph explaining why the model is right.

### Show the evidence context, not merely a confidence badge

Experiments with imperfect automation have found that exposing contextual information relevant to the recommendation's reliability can reduce some performance costs of automation failure. Other studies find greater transparency can increase accuracy and speed, though transparency does not eliminate misuse of highly reliable automation. citeturn14search8turn14search16

For code review, that means:

```text
Potential race at queue.ts:118

WHY FLAGGED
write() and close() can run on different callbacks.

DIRECT EVIDENCE
- close() mutates `closed`
- write() checks `closed` before asynchronous enqueue
- no lock / serialization found in this path

UNCERTAINTY
Medium. I may be missing serialization in caller X.

FASTEST CHECK
Run test Y with concurrent callbacks, or inspect caller Z.
```

That is safer than:

> “⚠️ High-confidence race condition. Here's why…”

because it gives the human an independent verification path.

### Polished summaries can create an illusion of understanding

There is much stronger evidence for the underlying memory mechanism than for a unique “polished-AI-summary effect.” Retrieval studies show that rereading or restudying can increase subjective confidence while producing worse delayed retention than active retrieval. citeturn21view1turn10search20

So the responsible conclusion is **not** “research has proven that AI summaries make people stupid.” Direct AI-specific causal evidence on durable skill loss remains comparatively young. The better-supported inference is that **replacing retrieval, explanation, and practice with passive consumption removes learning processes already known to matter**. citeturn21view1turn22search0

Emerging GenAI evidence is consistent with concern but should be labelled accordingly. A CHI 2025 survey of 319 knowledge workers found that greater confidence in GenAI was associated with less self-reported critical-thinking activity, while greater task self-confidence was associated with more. Because this is observational/self-report work, it cannot establish that AI caused the cognitive changes. citeturn20search0

A January 2026 controlled preprint on cognitive forcing functions for AI-generated writing plans found that asking users to inspect assumptions reduced over-reliance without increasing measured cognitive load in that experiment. It is promising, but still **preliminary evidence**, not a mature design law. citeturn20search1

### The right target is calibrated reliance

The goal should not be “trust AI less.” Blind distrust wastes useful automation just as blind trust creates errors. Human-factors work shows that automation reliability, error patterns, task difficulty, and contextual transparency all influence reliance. citeturn14search5turn14search14turn14search16

An agent should therefore help the human answer:

**What does the AI know?**

**What evidence is directly observed?**

**What has been inferred?**

**Where is the model uncertain?**

**What independent check is cheap?**

**What failure would matter?**

**Is the human deciding, or merely ratifying the model?**

### Ways to verify understanding rather than reading

The strongest checks require the reader to **produce something not immediately visible in the output**.

| Check | Prompt | What it reveals |
|---|---|---|
| **Free recall** | “Without scrolling up, name the three invariants.” | Whether key structure is retrievable. Retrieval itself also strengthens memory. citeturn21view1 |
| **Teach-back** | “Explain the request path in your own words.” | Missing links and misconceptions; closed-loop communication provides an operational analogue. citeturn6search4turn11search2 |
| **Prediction** | “Before we open the file, where do you expect authorization to occur?” | Whether the learner has a generative mental model. |
| **Transfer** | “How would this architecture behave if service B were unavailable?” | Whether understanding extends beyond the exact example. citeturn22search0 |
| **Contrast** | “Why is option B better here but not under condition X?” | Whether the reader knows decision boundaries rather than memorizing the recommendation. |
| **Error detection** | “One statement in this summary is wrong. Find it.” | Forces verification rather than acquiescence; useful sparingly as a training device. |
| **Reconstruction** | “Sketch the components and arrows from memory.” | Mental-model completeness. |
| **Confidence-before-answer** | “Give your answer and confidence first; then reveal the agent's.” | Preserves an independent human signal and makes calibration visible. citeturn14search17turn14search12 |
| **Falsification** | “What observation would prove this diagnosis wrong?” | Whether a hypothesis is being treated as a hypothesis. This mirrors high-quality analytic practice around alternatives and uncertainty. citeturn19search10 |

“Do you understand?” tests politeness and subjective familiarity far more than it tests a mental model.

## A reusable agent-writing playbook

The research suggests that the skill you are building should control **information architecture**, not merely length or formatting.

### A layered summary pattern

Use for research, plans, architectural investigations, long code reviews, and incident analyses.

```text
BOTTOM LINE
One to three sentences answering the actual question.

WHAT MATTERS
The few consequences, findings, or decisions that change what the reader does.

CONFIDENCE / UNCERTAINTY
What is established, inferred, disputed, or still unknown.

EVIDENCE
Enough evidence for the reader to independently evaluate the bottom line.

DETAIL
Supporting analysis, implementation specifics, edge cases.

APPENDIX / SOURCES
Raw observations, references, exhaustive lists.
```

The crucial distinction from ordinary “progressive disclosure” is that **uncertainty belongs near the top when it could change the decision**. It must not be hidden in the appendix. That follows directly from intelligence analytic standards, while the layering itself should be treated as a design heuristic rather than a proven universal comprehension accelerator. citeturn19search10turn3search12

### A decision brief

Use when the human must choose among consequential alternatives.

```text
DECISION
What decision is required, and by when?

RECOMMENDATION
Choose B.

WHY
1. B satisfies ...
2. B avoids ...
3. The main cost is ...

OPTIONS
              A          B          C
Requirement  ...
Cost         ...
Reversibility...
Risk         ...

ASSUMPTIONS
- ...
- ...

UNCERTAINTIES
- ...

WHAT WOULD CHANGE MY RECOMMENDATION
- ...

REVERSIBILITY
Easy / moderate / difficult.
What is the recovery path?

NEXT ACTION
The smallest step that preserves optionality.
```

Tables are doing the comparison work; prose is doing the argumentative work. Assumptions and uncertainty remain visible rather than being folded into confident-sounding prose. citeturn3search13turn19search10

### A software version of commander's intent

Use for implementation plans given to another agent or engineer.

```text
PURPOSE
Why this change exists.

SUCCESS / END STATE
What must be true when complete.

INVARIANTS
What must remain true throughout.

KEY TASKS
Only the actions that are genuinely necessary.

NON-GOALS
What is deliberately not being solved.

FREEDOM
Which implementation details may change as new facts emerge.

VERIFY
How we know the end state has been achieved.
```

The `purpose + key tasks + end state` core comes directly from commander's-intent practice; invariants/non-goals/verification are a software adaptation. citeturn19search0turn19search2

### A diagram selection guide

Choose the diagram from the relation, not the aesthetic.

| Question | Diagram |
|---|---|
| “What calls what, and in which order?” | **Sequence diagram** |
| “What components exist and how are they connected?” | **Architecture/container graph** |
| “What can transition to what?” | **State diagram** |
| “What are the decision branches?” | **Decision tree / flow chart** |
| “What contains what?” | **Hierarchy/tree** |
| “What caused what?” | **Causal graph**, with evidence/uncertainty separately stated |
| “Where is it?” | **Spatial/map view** |
| “How do values change?” | **Chart**, not an architecture diagram |
| “What changed?” | **Diff**, not a before/after architecture drawing unless topology changed |

A diagram should normally have **one semantic job**. Edge types, direction, grouping, and abstraction level should be explicit. This is an applied design rule derived from evidence that diagram utility comes from making task-relevant relations easier to access. citeturn21view5

### A comparison table pattern

Use only when options share meaningful dimensions.

```text
| Criterion        | Option A | Option B | Option C |
|------------------|----------|----------|----------|
| Primary benefit  |          |          |          |
| Main drawback    |          |          |          |
| Complexity       |          |          |          |
| Failure mode     |          |          |          |
| Reversibility    |          |          |          |
| Evidence         |          |          |          |
| Unknowns         |          |          |          |
```

Do not force everything into cells. Put nuanced causal reasoning underneath the table. Tables are effective when they align repeated comparisons; turning an argument into a spreadsheet can destroy the very structure the reader needs to understand. citeturn3search13turn21view5

### A research-results pattern

```text
ANSWER
...

KEY FINDINGS

Finding                    Evidence        Confidence
----------------------------------------------------
...                        replicated      high
...                        single study    medium
...                        practitioner    low/direct evidence

WHAT IS CONTESTED
...

WHAT IS NOT SUPPORTED
...

IMPLICATION FOR THIS DECISION
...

SOURCES / METHODS
...
```

This prevents a common failure of AI research reports: a smooth narrative that makes one small experiment, a systematic body of evidence, an expert opinion, and an organizational tradition sound epistemically identical. ODNI's insistence on source quality, uncertainty, alternatives, and separation of evidence from analyst judgment is a particularly good model. citeturn19search10

### Output in a terminal

A terminal is hostile to wide layouts and expensive scrolling. The agent should optimize for **one-screen orientation followed by inspectable detail**.

A good terminal response looks like:

```text
Result: the regression comes from cache.ts, not the API change.

Why:
- cache key dropped tenant ID in 3f07c2a
- failing requests all share cross-tenant key collisions
- API response itself is correct

Risk: high in multi-tenant production; low locally.

Fix: restore tenant ID to the key and add a cross-tenant regression test.

Files:
  src/cache.ts:81
  test/cache.test.ts:144

Details / evidence:
...
```

A poor terminal response begins with three screens of methodology.

The terminal should usually favour short sections, narrow two-column structures, literal paths/commands, and small ASCII flows where they actually clarify sequence. That is a design synthesis from the broader findings on search costs and representations rather than a terminal-specific controlled result. citeturn18search0turn21view5

### Output in chat

Chat supports conversational progressive disclosure, so the first message should normally be **decision-complete but not evidence-exhaustive**:

```text
Recommendation: use B.

It wins mainly because X and Y.
The meaningful downside is Z.
Confidence: medium; the unresolved question is Q.

Evidence:
...
```

Do not create artificial conversational turns by withholding essential caveats. Progressive disclosure should reduce irrelevant detail, not force the human to ask “What are the risks?” every time. Direct evidence that layering universally improves information finding is mixed. citeturn3search12

For learning interactions, chat should become less answer-first and more Socratic:

```text
Before I explain this:
what do you think component X owns?

[human answers]

Here is what the code actually does...
```

That preserves retrieval and prediction. citeturn21view1turn11search2

### Output in a durable document

Docs should optimize for **multiple passes by multiple readers**, not merely initial speed.

A strong structure is:

```text
Title

Executive answer
Decision / key judgments
Important uncertainty

Context and scope

Evidence / analysis

Options and trade-offs

Recommendation

Implementation / consequences

Appendix and sources
```

The document's top should orient; its body should permit auditing. Amazon's memo culture provides a practitioner example of deliberately making a substantive written artefact the common basis for discussion, while intelligence standards provide the stronger model for preserving evidence and uncertainty. citeturn22search3turn19search10

### Anti-patterns

| Anti-pattern | Why it fails | Better move |
|---|---|---|
| **Wall of text** | Relationships and conclusions must be repeatedly searched for and retained while reading. citeturn21view8turn21view5 | Expose hierarchy; move repeated comparisons to a table; isolate the bottom line. |
| **Decorative diagram** | Adds another representation to decode without reducing search or inference. Experiments show diagrams do not automatically improve comprehension. citeturn3search11turn21view5 | Draw only relations that are easier to perceive graphically. |
| **Diagram plus duplicated prose everywhere** | Can create redundant processing rather than complementary representation. Multimedia benefits depend on integration and relevance. citeturn15search14 | Let each representation do a distinct job; integrate labels locally. |
| **Animation because the phenomenon moves** | Dynamic media can disappear before the learner has integrated it; static annotated diagrams have beaten animation in controlled multimedia experiments. citeturn15search17 | Use animation only when change itself is the information and controls allow inspection. |
| **Everything is bold / coloured** | Salience works through contrast; when everything competes, nothing reliably pops out. citeturn15search11turn15search7 | Reserve salience for exceptions, changes, warnings, and the current focus. |
| **Pie/bubble chart for close quantitative comparison** | Angle and area are less accurately judged than aligned position/length. citeturn16search15 | Dot/bar chart on a common scale. |
| **Table for an argument** | Cells align facts but often destroy causal or rhetorical sequence. | Put comparable attributes in the table; reasoning below it. |
| **Chronology before conclusion** | Reader spends time reconstructing relevance before learning the requested outcome. BLUF practice exists specifically to counter this in operational writing. citeturn14search13 | Answer first unless chronology itself is the question. |
| **Summary that hides caveats** | Speeds reading by removing information required for correct judgment. Intelligence standards explicitly require uncertainty and assumptions to remain visible. citeturn19search10 | Promote decision-relevant uncertainty into the summary. |
| **False numerical confidence** | A number looks calibrated even when it is merely subjective. | Use evidence-linked qualitative confidence unless probabilities are actually calibrated. |
| **Three-option matrix for an expert-recognition problem** | Experts can often recognize familiar patterns quickly; forced comparison may add overhead without value. citeturn21view4 | State the recognized pattern, evidence for it, and falsifier. |
| **“Trust your intuition” for novices** | Recognition-primed expertise depends on substantial domain experience; it is not generic intuition. citeturn21view4turn2search13 | Give novices examples, constraints, and explicit reasoning. |
| **One tutorial for every expertise level** | Guidance useful to novices can become redundant as expertise increases. citeturn11search1 | Adapt depth to demonstrated knowledge. |
| **AI answer before human judgment on a consequential question** | Incorrect advice can anchor or distort subsequent human judgment. citeturn14search17turn14search12 | Elicit an independent view first when stakes justify the friction. |
| **AI explanation as proof** | Explanations do not reliably prevent over-reliance and can sometimes worsen it. citeturn21view11turn14search20 | Provide evidence, provenance, alternative hypotheses, and checks. |
| **Summary-only learning** | Recognition and confidence are not equivalent to retrievable understanding. citeturn21view1turn10search20 | Ask for retrieval, explanation, prediction, and transfer. |
| **Interaction for interaction's sake** | Controls add navigation and cognitive overhead unless manipulation exposes an important relation. Simulation benefits are context-dependent. citeturn17search12turn17search14 | Use an interactive explorable only when counterfactual manipulation is part of the task. |
| **“Visual/auditory learner” personalization** | The learning-styles meshing hypothesis lacks adequate evidentiary support. citeturn22search7turn22search11 | Adapt to prior knowledge, task, modality constraints, and the structure of the content. |

### A compact rule set for a reusable skill

The research can be compressed into an implementable policy:

```text
1. Identify the human job:
   decide | understand | learn | inspect | reference | explore

2. Put the conclusion at the earliest point compatible with that job.
   Exception: when learning or independent judgment matters,
   elicit a prediction/judgment first.

3. Identify the dominant information relationship:
   comparison -> table
   quantitative pattern -> chart
   topology -> diagram
   sequence -> flow/sequence diagram
   hierarchy -> tree
   change -> diff
   argument/rationale -> prose
   procedure -> checklist

4. Externalize dependencies and repeated comparisons.
   Do not make the reader remember them across paragraphs.

5. Adapt for expertise:
   novice -> orientation + worked example + explanation
   expert -> delta + evidence + exceptions + source

6. Surface epistemic status:
   observed | inferred | assumed | unknown
   plus confidence when useful.

7. Keep the first layer decision-complete.
   Details may be deferred; decision-changing caveats may not.

8. For consequential AI recommendations:
   expose evidence and falsifiers;
   consider human-first judgment.

9. For learning:
   explanation is not completion.
   require retrieval, prediction, self-explanation, or transfer.

10. Use a diagram or interactive view only when it removes
    real mental simulation/search work.
```

The most important conceptual shift is this:

**An agent should optimize neither for minimum words nor minimum human effort. It should minimize the wrong kinds of effort.**

The human should not have to expend scarce attention finding the conclusion, remembering five earlier options, mentally tracing arrows through prose, discovering hidden assumptions, or navigating twenty files the agent could map. But the human **should** sometimes expend effort predicting, retrieving, explaining, comparing evidence, noticing uncertainty, and making the final judgment. Cognitive-load research, program-comprehension studies, retrieval-practice research, naturalistic expert decision research, and human–automation experiments all point in that direction. citeturn21view9turn18search0turn21view1turn21view4turn14search0

For reusable agent skills, that gives a more defensible objective than “make it easy to read”:

> **Make the structure easy to perceive, the evidence easy to inspect, the decision easy to locate, and genuine understanding impossible to confuse with mere fluency.**