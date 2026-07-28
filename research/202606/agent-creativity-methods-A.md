# Domain-General Methods to Make AI Agents Genuinely Creative

## The central finding

If you want an AI agent to stop producing competent, forgettable work, the most reliable lever is not “be more creative.” It is **forcing the search process away from the target domain, then forcing it back through a rigorous bridge**. The creativity literature and design-by-analogy research converge on the same pattern: novelty rises when creators traverse **greater semantic or analogical distance**, but quality and feasibility can fall unless the transfer is based on **shared relational structure**, not surface resemblance. In other words, “design this app like jazz” is usually fluff; “map jazz improvisation’s turn-taking, tension-release, and motif variation onto onboarding, navigation, and error recovery” is usable creativity. Reviews of design-by-analogy, analogy-distance studies, and conceptual-combination research all point in this direction, including evidence that far analogies tend to raise novelty, that moderate distance often gives the best trade-off, and that iteration is what converts far combinations into ideas that are both novel and workable. citeturn23view1turn24view1turn9search0

The cognitive-science framing also matters. Creativity is not just divergence. The strongest definitions still treat creativity as the combination of **novelty plus appropriateness or usefulness**, and process research distinguishes **divergent search** from **convergent evaluation**. Neurocognitive reviews likewise treat divergent and convergent thinking as distinct but complementary, with divergent thinking favoring flexibility and convergent evaluation favoring persistence. For agent design, that means one-shot prompting is structurally wrong for nontrivial creativity: you need a loop that first expands the search space, then evaluates against constraints, then expands again from a reframed base. citeturn27search0turn27search1turn28view0turn20view0

LLMs are generic for predictable reasons. They are trained and aligned to produce plausible, high-probability continuations, so they tend to drift toward the center of the distribution. Recent work on LLM creativity shows that originality is often the weak point, that temperature alone is only a weak novelty lever and can increase incoherence, and that collaboration with GenAI can improve average creative performance while **reducing diversity of ideas**. Other recent work argues that stronger alignment may push models toward appropriateness at the expense of novelty. So the fix is not merely “turn up temperature”; it is to add **external stimuli, controlled distance, multiple candidate generation, explicit anti-cliché critique, and a separate selection phase**. citeturn18view0turn21view9turn21view10turn21view8turn30academia51

A final practical point: early examples can lock both humans and agents into imitation. Design-fixation studies show that familiar examples and sketch-like representations can induce copying, while more abstract representations and better example presentation can reduce fixation. More recent HCI work shows that presenting examples as a flat list increases fixation, while contextualized examples help people build a model of the space and explore it. For agents, this means the sequence should be **brief → far-domain raid → bridge → only then precedent check**, not precedent first. If you start with competitor screenshots, logo boards, existing APIs, or architecture precedents, you are often injecting fixation at the exact moment you should be widening the search space. citeturn25view0turn25view1turn26view0turn26view3

## The technique catalog translated into agent procedures

What follows is the part you can encode directly as an agent skill. The important shift is to treat each creativity technique not as a workshop exercise but as a **promptable transformation operator** inside a loop.

**Forced association and random entry** use an arbitrary or weakly related stimulus to break default associations. In LLM terms, the cleanest implementation is: generate or retrieve a random object, process, organism, institution, artifact, or phenomenon; extract three properties, mechanisms, or behaviors; force the model to map each back to the brief. Associative-thinking experiments on GPT-style models found that prompting the model to connect disparate concepts improved originality across product design, storytelling, and marketing, though usefulness can fall if the bridge remains too incongruous. Use this when the problem is bland, overfamiliar, or overloaded with same-domain precedent. Avoid using it as the final stage; it is a divergence tool. citeturn32view0

**Prompt pattern**

```text
You are in forced-association mode.
Target brief: [brief]

Random source: [random source]
Extract:
- 3 properties/mechanisms from the source
- 3 verbs that describe what it does
- 2 tensions or tradeoffs it manages

Now create 6 ideas for the target that each transfer one mechanism back.
For each idea, state:
1. borrowed mechanism
2. bridge sentence
3. concrete manifestation in the target domain
4. why it is not the default solution
```

**Bisociation and conceptual blending** are stronger than random association because they require two frames to coexist and form a third, emergent one. This is closer to genuine concept invention. Cognitive and computational work on conceptual blending treats it as a core engine of creative thought, and conceptual-combination studies show that distant combinations become more creative when iterated rather than accepted as first-draft outputs. In agent terms: choose two remote frames, identify their **relational structure**, then force a blended concept that preserves useful tensions from both. Use it when you want a concept platform rather than a surface variation: brand worlds, interface metaphors, architecture concepts, service models, product systems. citeturn14search1turn9search0turn23view1

**Prompt pattern**

```text
Target brief: [brief]
Source frame A: [domain A]
Source frame B: [domain B]

For each source frame:
- list underlying relations, not appearances
- list what changes over time
- list what is optimized and what is sacrificed

Create 5 blended concepts that preserve one important relation from A and one from B.
Reject any concept that only copies style, aesthetics, or vocabulary.
```

**Lateral thinking in the de Bono sense** is deliberate provocation: reverse assumptions, break sequencing, remove necessity, or step sideways from the obvious frame. As a practical operator, this works best as “state assumption → violate assumption → salvage utility.” It is strongest when the team already knows the default answer too well. Treat it as a way to produce discontinuities, not polish. The classical source is de Bono’s *Lateral Thinking*; in an agent loop, it belongs immediately after the first convergent critique, when you want a controlled jump away from the emerging cliché cluster. citeturn3search1

**Prompt pattern**

```text
List the 7 strongest assumptions embedded in the brief.
For each assumption:
- invert it
- exaggerate it
- delay it
- remove it
Generate one concept per transformation.
Then keep only the concepts that still satisfy the core user need.
```

**SCAMPER** is checklist creativity. Its real strength is not originality by itself, but making the agent traverse a wider set of transformations than generic ideation usually produces. Because it is structured, cheap, and reusable, it is excellent as a “first diverge” stage before the far-domain raid. Use it when you need breadth quickly or when improving an existing artifact rather than inventing from zero. The method derives from Bob Eberle’s adaptation of Osborn-style idea-spurring questions. citeturn3search0turn15search4

**Prompt pattern**

```text
Apply SCAMPER to [target].
For each letter, generate exactly 2 non-obvious moves.
Then rank all 14 moves by “distance from default” and keep the top 6.
```

**Oblique Strategies** are creative jolts, not analytical steps. Brian Eno and Peter Schmidt designed them as constraints or aphorisms that break local fixation, and they work well in agentic systems when the model is becoming too coherent too early. Use them as a stochastic interrupt after round one, especially for writing, brand expression, visual direction, speculative architecture, and concept development. They are less useful for tightly constrained engineering unless translated into sharper operational prompts. citeturn3news50turn3search2

**Prompt pattern**

```text
Draw one oblique constraint:
- [constraint]

Rework the current top 3 ideas under that constraint.
Do not add decoration; change the organizing principle.
Explain what became more distinctive and what got worse.
```

**Morphological analysis** is the opposite of romantic creativity: it systematically enumerates the design space by decomposing a problem into parameters and alternative values. Zwicky’s morphological approach and later general morphological analysis are especially useful for agents because they externalize the combinatorial search space instead of leaving it implicit in the model’s priors. Use it when the brief contains multiple independent dimensions: interaction model, tone, materiality, layout, structure, business model, naming phonetics, etc. It is one of the best tools for stopping the model from collapsing onto one latent template too early. citeturn5search4

**Prompt pattern**

```text
Decompose the brief into 5-8 parameters.
For each parameter, list 4-6 plausible values.
Now deliberately assemble:
- 3 conventional combinations
- 3 moderately unusual combinations
- 3 far but still viable combinations

For the far combinations, explain why the mix could work.
```

**Biomimicry** is cross-domain analogy with a disciplined translation protocol. The Biomimicry Design Spiral is valuable because it formalizes the bridge: define the challenge, biologize the function, discover natural models, abstract the mechanism, emulate, evaluate. The key move is not “make it look like nature,” but “translate the brief into function and context so you can ask how nature solves the same problem.” This is domain-general whenever the problem can be expressed as a function, behavior, or adaptive constraint. It is especially strong for service design, systems design, architecture, materials, product behavior, and information architecture. citeturn5search0turn5search3turn5search7turn5search10

**Prompt pattern**

```text
Turn the brief into “How does nature...?” questions.
Find 5 biological strategies that solve analogous functions.
For each, write an abstract mechanism with no biological nouns.
Map those abstract mechanisms back into the target.
```

**James Webb Young’s idea method** is still useful because it is a process model, not a gimmick: gather materials, digest, step away, let the idea surface, then test and revise. For agents, the “incubation” stage becomes a mode switch: leave the current draft, do a far-domain pass, or force a reformulation of the brief before returning. Empirically, incubation has a positive though contingent effect, and divergent thinking tasks appear to benefit more than some insight tasks. Use this whenever the first batch is competent but stale. citeturn17search0turn4search0turn29view0turn29view1

**Prompt pattern**

```text
Phase A: collect domain facts, user constraints, and precedents.
Phase B: collect unrelated stimuli.
Phase C: pause direct solutioning and reformulate the brief from first principles.
Phase D: return and generate only ideas that combine one domain fact with one remote stimulus.
Phase E: stress-test and revise.
```

**TRIZ** is best treated as a specialized contradiction engine rather than a universal creativity method. Its cross-domain power comes from abstracting recurring contradictions and solution principles across patents and technologies. Use it when the brief includes a clear tradeoff: quieter but more noticeable, simpler but more powerful, private but collaborative, flexible but stable, fast but trustworthy. It is far less useful for open-ended naming or literary ideation unless you can restate the problem as a contradiction. citeturn6search0turn6search2turn6search40

**Prompt pattern**

```text
State the contradiction:
We want more [A] without worsening [B].

Map A and B to abstract parameters.
Use TRIZ principles to generate 5 resolution strategies.
Then translate them into the target domain in plain language.
```

The meta-rule across all of these is simple: **the technique should change the search process, not just the wording of the final request**. That is what makes these methods operational rather than decorative. Recent LLM studies back that up: structured brainstorming plus selection improves creativity scores, multiple-LLM collaboration can improve originality, and process scaffolds that separate divergent and convergent modes outperform linear execution-first chat interfaces. citeturn34search2turn18view0turn22view0

## The recommended iterative creativity loop

This is the loop I would actually implement for a domain-agnostic agent. The exact counts below are **recommended defaults**, not literature-wide standards, but they are grounded in the evidence above and tuned for a cheap, tight cycle rather than an expensive “dump 50 ideas” workflow. citeturn22view0turn34search2turn21view9turn21view8

Start with a **brief distillation**. The agent rewrites the problem into four lines: desired effect, hard constraints, taboo defaults, and evaluation goal. Then it lists the obvious same-domain clichés and explicitly forbids them. This is the “name the cliché, then ban it” move. It directly counters anchoring and fixation. citeturn25view0turn21view7

Next run a **controlled first divergence**. Generate 8–12 quick same-domain ideas using SCAMPER or lateral transformations, but do not keep them as the solution set. Their job is to expose the center of gravity of the space. The agent then clusters these outputs and writes a short diagnosis: “the model is overusing personalization,” or “everything is copying dashboard conventions,” or “every name sounds like wellness branding.” This gives the next phase a concrete target to avoid. citeturn15search4turn22view0

Then perform a **cross-domain raid**, which should be the centerpiece. Pick 5 source domains: one near, two medium-distance, and two far. Select them by **shared function, dynamic, or constraint**, not by mood. Good selectors are: same temporal behavior, same trust pattern, same load-balancing problem, same visibility problem, same hierarchy problem, same edge condition. Less-common and farther-field examples are often more generative than common nearby ones, but you still need the bridge. citeturn23view1turn24view1turn24view2turn21view3

For each source domain, extract three things only: the **mechanism**, the **tradeoff**, and the **experience pattern**. Then convert each into a bridge sentence of the form: “In source X, Y mechanism achieves Z under constraint C; in the target, that suggests…” Reject any source that cannot produce a clean bridge sentence. This is the cheapest way to stop superficial analogy. It operationalizes the literature’s emphasis on relational structure and abstracted mechanism. citeturn23view1turn24view4turn5search7

Now enter **bridge generation**. Produce 10–15 concept seeds, each grounded in one bridge. Require every seed to specify the borrowed mechanism, the concrete translation, and what cliché it avoids. This is the moment to use associative prompts, conceptual blending, or biomimetic abstraction. If a seed only changes tone, style, or adjectives, kill it. citeturn32view0turn14search1turn5search10

Only after that should the agent do a **precedent pass**. In this phase it asks: does this idea secretly collapse back into a known pattern from the target domain? If yes, it either discards it or pushes it one more step away. This sequence matters. Research on example exposure and interface design suggests that examples are useful when they help formulate the space, but harmful when they anchor prematurely. Precedent therefore belongs after remote expansion, not before it. citeturn26view0turn26view3

Then do **convergent scoring and selection**. Score the seeds with a distinctiveness rubric that separates novelty from usefulness. Keep the top three concepts, but also keep one “wildcard” that scores high on novelty and medium on feasibility. Recent work repeatedly shows that creativity lives on a frontier; if you only keep the safest concept, the loop collapses back to the center. citeturn30academia51turn20view0turn27search0

Finally, run **one tightening pass**. For each shortlisted concept, ask the agent to make it *more concrete and more ownable without making it more conventional*. This is where the agent turns a mechanism into layout decisions, naming phonetics, brand verbs, API affordances, structural sections, or copy elements. One or two loops are usually enough. More than that often leads to polish-induced sameness unless you reintroduce fresh stimuli. citeturn22view0turn19view8

A reusable controller prompt for the whole loop looks like this:

```text
You are not allowed to solve the brief directly.

Phase 1
Rewrite the brief into:
- desired effect
- hard constraints
- obvious clichés
- evaluation goal

Phase 2
Generate 10 conventional ideas.
Cluster them and name the default pattern.

Phase 3
Select 5 source domains by shared function/dynamic/constraint, including at least 2 far domains.
For each source domain extract:
- mechanism
- tradeoff
- experience pattern

Phase 4
Write bridge sentences from each source to the target.
Discard any bridge based only on style or aesthetics.

Phase 5
Generate 12 concept seeds.
Each seed must specify:
- borrowed mechanism
- concrete translation
- cliché avoided

Phase 6
Check the seeds against target-domain precedents and remove those that collapse into familiar patterns.

Phase 7
Score remaining seeds with the distinctiveness rubric.
Return:
- top 3
- 1 wildcard
- why each is distinctive
- what would make each cliché again
```

## A reusable distinctiveness rubric

The following rubric is a synthesis of the standard creativity definition, semantic-distance work, design-by-analogy theory, associative-creativity benchmarks, and fixation research. It is **not** a published standard, but it is grounded in what the literature repeatedly treats as the load-bearing dimensions: novelty, usefulness, relational bridge quality, specificity, and diversity. citeturn27search0turn27search1turn30search1turn33view3turn23view1

Score each concept from 0 to 3 on each dimension.

**Distance from default.** Is the concept meaningfully outside the obvious cluster for this task, or is it just the standard answer in new language? Semantic-distance work and analogy-distance research justify using this as an explicit criterion. citeturn30search1turn23view1

**Structural transfer quality.** Is there a real bridge from source to target based on function, relation, or mechanism, rather than a mood-board resemblance? Good analogies depend on relational alignment; bad ones are just stylistic mimicry. citeturn23view1turn24view4turn5search7

**Specificity.** Could someone else distinguish this concept from near-neighbors in one sentence? The CREATE benchmark’s notion of specificity is useful here: distinctiveness plus closeness of concept connection. citeturn33view0turn33view3

**Appropriateness and feasibility.** Does it still solve the brief? The standard creativity literature keeps coming back to novelty plus appropriateness/usefulness; this dimension prevents “weirdness laundering” from being mistaken for creativity. citeturn27search0turn27search1turn20view0

**Anti-cliché resistance.** If you remove the fancy wording, does the concept collapse into a familiar pattern? This dimension is directly motivated by fixation research and by the tendency of LLMs to re-enter conventional clusters. citeturn21view7turn22view0

**Embodiment.** Has the concept reached the level of concrete manifestation for the target domain: actual interaction behavior, naming logic, section strategy, structural move, material system, visual grammar, or copy mechanism? Distinctive concepts that remain abstract often revert to default in implementation. citeturn5search8turn19view8

**Portfolio diversity.** If the agent generated several concepts, are they truly different from each other, or are they siblings? Benchmarks for associative creativity and automated creativity evaluation both stress diversity within the candidate set, not just quality of a single output. citeturn33view1turn20view0

My recommended default is: **do not commit** unless the concept scores at least 2 on structural transfer, 2 on appropriateness, and 2 on anti-cliché resistance, with a total of at least 14 out of 21. That threshold is a practical operating rule, not a research standard, but it is a good defense against elegant genericity. citeturn27search1turn33view3turn23view1

## The same method applied across unrelated domains

The important thing to prove is not that the outputs are good in the abstract, but that the **same loop** works across domains with only the embodiment layer changing. The examples below use the identical sequence: brief distillation, cliché naming, cross-domain raid, bridge generation, precedent check, convergent scoring. That generality is exactly what design-by-analogy and associative-creativity research argue for. citeturn23view1turn32view0turn21view3

For a **restaurant brand**, assume the brief is “new neighbourhood restaurant, modern but not luxury, quiet confidence, ingredient-led.” The cliché cluster will usually be rustic + handcrafted + warmth + local. A cross-domain raid might pull from **railway signaling**, **watchmaking**, and **tide pools**. Railway signaling contributes sparse high-trust cues; watchmaking contributes visible precision and ritualized calibration; tide pools contribute layered discovery in a small footprint. That yields a concept like **Signal Table**: restrained identity, few but high-certainty brand cues, menus organized by timing and tide-like seasonal layers, service rituals that emphasize calibrated shifts rather than cozy excess. What makes this better than generic “farm-to-table” branding is that the bridge is structural, not aesthetic. citeturn23view1turn24view1turn5search7

For a **residential building**, assume “narrow urban house, family home, needs privacy, airflow, and moments of surprise.” The cliché cluster is light wells, warm materials, indoor-outdoor blur. Raiding **termite mounds**, **film editing**, and **jazz improvisation** produces better mechanics: passive pressure-driven ventilation; alternating compression and release; repeated motifs with varied return. The resulting concept could be a **Cut-and-Breath House**: compressed transition zones opening to tall calm rooms, ventilation chimneys organized as the house’s spatial spine, and recurring framing devices that make the same courtyard feel different from different levels. This is not “nature-inspired architecture” as style; it is transfer of airflow logic and sequence logic. citeturn5search0turn5search9turn5search10turn23view1

For a **software UI**, assume “dashboard for engineering teams, needs calm oversight, quick interventions, and less alert fatigue.” The cliché cluster is card grids, colorful charts, and endless notification badges. Raiding **air-traffic control**, **bonsai pruning**, and **pit-lane racing** gives stronger bridges: dense information with strict signal hierarchy; deliberate reduction to preserve shape; rapid intervention in short windows. The resulting concept might be a **pit-lane dashboard**: default quiet view, issue “lanes” only when thresholds matter, one-click prune/archive flows, and calm exception-based navigation rather than constant full-spectrum status. This maps directly to interaction behavior, not merely visual styling. citeturn22view0turn26view3turn19view8

For a **product name**, assume “note-taking app for researchers; trustworthy, connected, not corporate.” The cliché cluster is “vault,” “mind,” “flow,” “lab,” “note,” and Latinate abstractions. Raiding **cartography**, **beekeeping**, and **court transcription** produces bridge mechanisms instead: paths, cells, and verified record. That can yield names such as **Contour**, **Cellscript**, or **Trace Ledger**. In the rubric, **Contour** probably wins because it feels less category-generic than “NoteFlow,” retains a map-like knowledge metaphor, and can expand into product language about routes, edges, and layers. The same procedure works for product naming as for buildings or UIs; only the embodiment checkpoint changes from structure or interaction to phonetic ownability and semantic territory. citeturn32view0turn30search1turn33view3

The deeper lesson from these examples is that the agent should not ask, “What do good restaurant brands/buildings/UIs/names usually do?” until **after** it has already formed remote bridges. If it asks that first, it will anchor inside the local genre and decorate the known answer. citeturn25view0turn26view0turn22view0

## What the current evidence says in 2025 and 2026

The most defensible **established findings** are these. Creativity still has to be evaluated as some version of **novel plus appropriate**; divergence and convergence are distinct but both necessary; fixation is real and is amplified by familiar examples and premature exposure to precedents; incubation helps in aggregate, with divergent tasks benefiting especially; and design-by-analogy can raise novelty, particularly when the analogy is less common and farther-field, though the bridge needs to be structurally meaningful and often iterative. Those claims are supported by older, well-established cognitive and design research, not just recent GenAI papers. citeturn27search0turn27search1turn28view0turn25view0turn29view0turn23view1turn24view1

On **LLM creativity**, the picture is more mixed. Peer-reviewed work in 2025–2026 suggests that LLMs can perform competitively with humans on some divergent-thinking tasks, and in some studies they match or exceed humans on originality-related measures. At the same time, more fine-grained work finds that LLM originality is unstable, often weaker than fluency or elaboration, and highly sensitive to prompting and sampling. A large 2025 meta-analysis preprint reports that humans working with GenAI outperform humans working alone on creative performance overall, but idea diversity falls substantially. That combination—better average ideas, narrower spread—is exactly why a creativity agent needs an explicit diversity-preservation loop. citeturn18view0turn11search1turn11search2turn21view8

The strongest **emerging claims** in 2026 are especially relevant to your request. One preprint finds that randomly assigned cross-domain mappings reliably help humans, and that for both humans and LLMs the impact grows as the source becomes more semantically distant from the target; however, the average effect on LLMs was not statistically significant in that study. Another 2026 preprint on scientific idea generation argues that analogical reasoning can reduce LLM mode collapse and dramatically increase diversity and novelty. A separate 2025–2026 line of HCI work shows that interfaces which explicitly separate divergent exploration from convergent refinement can outperform linear chatbot-style creation flows and reduce fixation. These are promising, but some of them are still preprint-stage and should be treated as **highly useful but not yet fully settled**. citeturn21view3turn21view4turn21view0turn21view1turn22view0

A second emerging area is **evaluation**. New proposals like CDAT, CREATE, and automated semantic-entropy frameworks are trying to score creativity in more domain-general ways. These are important because older tests often overreward raw divergence or fluency and ignore appropriateness. CREATE is especially useful conceptually because it foregrounds **specificity** and **diversity** within a candidate set, while CDAT tries to evaluate novelty conditional on appropriateness. That shift aligns well with practical agent design: you do not want random weirdness; you want multiple, specific, defensible departures from the default. citeturn33view0turn33view3turn30academia51turn20view0

The clearest practitioner-level implication from this body of work is that the best creative agent is probably **not** a single prompt or a single monologue. It is a compact process with explicit divergence, explicit remote association, explicit anti-fixation checks, and explicit convergence. Brainstorm-then-select improves creativity over brainstorming alone; multiple-LLM collaboration can improve originality; and recent work on creative software design still finds that human traits like analogy use, empathy, and prior experience remain central, with the LLM often contributing by elaborating or extending rather than supplying the deepest leap on its own. So the right design target is not “replace the creative act,” but “engineer a search procedure that gives genuine novelty more chances to appear.” citeturn34search2turn18view0turn21view11

Open questions remain. The exact “best” analogical distance is task-dependent; recent evidence suggests far distance raises novelty, but other work and reviews still point to a moderate-distance optimum for balanced novelty and feasibility. The most reliable automated domain-agnostic creativity metric is still unsettled. And many 2025–2026 findings about LLM creativity, design fixation, and analogical prompting remain preprints rather than long-settled consensus. But those uncertainties do **not** weaken the operational conclusion: if you want a domain-general creative agent, the safest bet is a **process intervention**, not a personality prompt. Force remote sources in, force structural bridges, name clichés early, keep divergence and convergence separate, and score for distinctiveness before you commit. citeturn23view1turn21view3turn20view0turn21view7