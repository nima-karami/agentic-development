# A Domain-General Inspiration Method for AI Agents with Pluggable Domain Packs

The strongest workable answer in 2026 is not “give the agent more references.” It is to give the agent a **sequence** and a **representation**. The sequence should protect against fixation: first generate internal rough directions from the brief, then do a far-domain raid, then study same-domain precedent, then synthesize. The representation should convert references into **transferable principles and tokens** rather than screenshots to imitate. That pattern is consistent with research on design fixation, example timing, analogical reasoning, and emerging agent tooling: examples reliably help, but they also narrow exploration unless they are staged and structured carefully. citeturn1search1turn23search1turn1academia51turn21search0turn23academia41

## What the evidence supports

Design research has been unusually consistent on one point: **examples are double-edged**. Meta-analytic and review work shows that examples tend to narrow variety and increase example-related ideas, while still sometimes improving novelty or quality. In other words, precedent is useful, but it can induce fixation if it arrives too early or too passively. Newer work also shows that **how** examples are presented matters: contextualized examples within an exploration space perform better than flat lists, which are more likely to trigger fixation. citeturn1search1turn0search3turn1academia51

Timing matters too. Work on exposure timing found that **early and repeated exposure** can improve creative work, while **late exposure** increases conformity without the same creativity gains. For agent design, that does **not** mean “show precedent first.” It means the system needs an **initial divergent phase** before it lets same-domain examples dominate. With AI agents specifically, recent HCI work argues that generative systems also suffer from premature convergence and benefit from explicit separation between brainstorming and refinement stages. citeturn23search1turn23academia39turn23academia41

On cross-domain inspiration, the literature is more nuanced than the popular “farther is always better” story. Classic design-by-analogy work, contemporary creativity research, and 2026 studies on cross-domain mapping all support the value of analogical transfer, especially when the mapping is **relational** rather than superficial. But distance is not a free lunch: some studies find closer inspirations can outperform very remote ones on average, while newer work shows that forced cross-domain mapping can increase originality and that the effect rises with semantic distance in some conditions. The practical conclusion is not “always go maximal distance.” It is: **sample multiple distances, then force a bridge that explicitly maps mechanism to brief**. citeturn20academia51turn21search0turn20search0turn21academia25turn21academia27

Biomimicry is a useful model here because it already distinguishes between copying appearance and translating deeper logic. The Biomimicry Institute frames AskNature as a database of biological strategies and innovations, and biomimicry practice commonly distinguishes inspiration from **form**, **process**, and **ecosystem** levels. That is exactly the distinction an agent needs if it is going to borrow from nature, music, literature, or film without turning the result into surface styling. citeturn33search0turn33search1turn33search2

## The domain-general method

The reusable method is best thought of as a seven-step loop that every domain pack plugs into.

**Step one is brief decomposition.** The agent rewrites the brief into a problem grammar: functions to achieve, constraints to respect, tensions to balance, moods to evoke, user states to support, and failure modes to avoid. This matters because analogical transfer works best on **relations** and **functions**, not nouns. Without this step, cross-domain sourcing collapses into decorative metaphor. citeturn20academia56turn21search0turn33search2

**Step two is zero-reference self-seeding.** Before it sees any examples, the agent should generate three to five rough conceptual directions from first principles. These are deliberately underpowered and provisional. Their job is to establish an internal search frontier so that later references do not completely determine the idea space. This is the simplest way to counteract example-driven fixation and premature commitment. citeturn1search1turn23academia41turn23academia39

**Step three is the far-domain raid.** The agent samples from a shared cross-domain pool using the problem grammar, not the target-domain keywords alone. It should intentionally pull from several semantic distances: one near analogy, one medium analogy, and one remote analogy. Each candidate must be converted into a **bridge record** with four fields:  
**source logic**, **shared relation**, **target implication**, and **anti-copy note**.  
For example: “forest canopy regulates light and microclimate” becomes “layered thresholding controls exposure and transition” becomes “use progressive disclosure, nested density, and soft edge transitions in the UI/building/brand system” rather than “use leaf shapes.” This is the core move that makes cross-pollination rigorous. citeturn21search0turn21academia27turn33search2turn33search4

**Step four is provisional concept formation.** After the raid, the agent should synthesize only enough to produce two or three candidate concept frames, each named by a metaphor or governing principle and backed by bridge records. At this point the concept is still abstract: it is about structure, rhythm, contrast, pacing, hierarchy, edge conditions, and personality rather than domain-specific forms. This preserves openness while turning the far-domain sampling into something testable. citeturn20academia51turn21academia25turn22academia39

**Step five is same-domain precedent study.** Only now should the agent search the domain pack. The precedent study is not “collect screenshots.” It is a structured extraction exercise. For each precedent, the agent should annotate: information architecture or spatial organization, hierarchy, rhythm, tonal logic, motion or pacing, interaction or circulation pattern, component or assembly strategy, and the project’s “personality.” Then it should compare at least three precedents and produce a **principle matrix** showing what recurs across them and what should be rejected. This is how several references become one coherent direction instead of a moodboard soup. citeturn2search1turn2search4turn1academia51

**Step six is merger and stress test.** The agent merges the preferred far-domain concept with same-domain precedent principles into a single concept direction and then attacks it with counterfactuals: what looks copied, what is unsupported by the brief, what collapses under accessibility, cost, engineering, code, or program constraints, and what can survive when the decorative layer is stripped away. This is where the method separates “inspiration” from “aesthetic citation.” citeturn23academia39turn24search1turn10search1

**Step seven is North Star emission.** The output is not a loose moodboard. It is a compact artifact that implementation can read: concept sentence, metaphor, governing principles, token palette, pattern vocabulary, do/don’t list, precedent ledger, and tests. That artifact is the contract between inspiration and execution. Emerging agent-readable design layers such as DESIGN.md and standardized design tokens are pointing in exactly this direction. citeturn36search3turn36search1turn22search0turn22search3

## The inspiration pack template

A pack should be modular enough that you can swap “front-end” for “architecture” without changing the method. The pack’s job is not to encode process. Its job is to provide **high-signal sources**, **metadata**, and **consumability clues**.

A strong pack has five layers. First, **showcase sources**: high-quality precedents. Second, **system sources**: design systems, standards, component libraries, technical details, manuals, building systems, pattern libraries. Third, **award or curation sources**: stronger signal, less noise. Fourth, **execution sources**: code examples, BIM objects, component docs, accessible patterns, materials specs. Fifth, **bridge metadata**: tags, stable identifiers, author, year, domain subtype, modality, access type, and notes on whether the source is machine-friendly. That last layer is what actually lets an agent reason over the catalog. citeturn2search1turn24search0turn32search2turn34search3

For agent-consumability, use this rubric:

| Criterion | What good looks like | Why it matters |
|---|---|---|
| Access | Public pages, free API keys, or clearly documented paid access; avoid hidden login walls when possible | Agents cannot reliably ground to sources they cannot reach or cite |
| Interface | Official API, MCP server, OpenAPI/JSON, IIIF, data dump, or stable HTML with permalinks | Structured interfaces reduce scraping fragility and hallucinated fields |
| Modality | Text, images, audio, SVG, component code, or token files exposed directly | Inspiration is multimodal; packs should preserve the original signal |
| Taxonomy | Search, filters, tags, categories, or typed entities | Agents need retrieval hooks, not just pages |
| Stability | Versioning, changelogs, archive IDs, node IDs, or canonical URLs | Good precedent study requires reproducibility |
| Legal clarity | Terms, rate limits, AI restrictions, attribution rules | Some excellent catalogs are legally poor fits for automated ingestion |
| Provenance | Source, date, author, rights, and transformation log | Prevents silent copying and supports auditability |

That legal line is not theoretical. Open Library explicitly tells developers not to scrape HTML pages and to use its APIs instead, with clear rate limits. Spotify’s developer platform explicitly says Spotify content may not be used to train machine learning or AI models, and Spotify’s 2024 Web API changes removed Audio Features and Audio Analysis access for new use cases. Those are exactly the kinds of constraints a pack has to store as first-class metadata. citeturn19search0turn14search1turn14search3

The ideal pack format in 2026 is a plain, inspectable registry. In practice, I would store each source as a record with: `name`, `domain`, `use_case`, `access`, `interface`, `modalities`, `quality_signal`, `taxonomy`, `constraints`, `example_queries`, and `bridge_prompts`. OpenAlex’s newly published API guide for LLMs is a good example of where documentation is heading: not just API reference, but instructions shaped for agent behavior. citeturn34search3turn7search1

## Worked pack for front-end

A practical front-end pack should mix showcase libraries, live design context, and implementation-grade system docs.

| Source | Best use | Agent-consumability |
|---|---|---|
| **Mobbin** | Real mobile, web-app, and website UI references; strong for flows and screen-level precedent | Official MCP server on Pro/Team/Enterprise and REST API on Team/Enterprise; screen search returns images and metadata. Excellent for agents if you can pay. citeturn3search1turn3search0turn6search2 |
| **Refero MCP** | Real product interfaces and user flows for product patterns; strong for feature-level precedent | Official MCP on Refero Pro; structured metadata per screen. Very strong for agents. citeturn36search0 |
| **Refero Styles** | Turning references into agent-readable style context | Offers DESIGN.md-style extracted references with colors, type, spacing, components, and copyable DESIGN.md examples. Strong emerging format. citeturn36search1turn36search3 |
| **Figma Dev Mode / Figma MCP** | Live design-file grounding, node-level inspection, code generation, and token-aware implementation | Figma’s Dev Mode and MCP server give agents direct design context; remote server is available across seats/plans and desktop server is available on paid Dev/Full seats, with beta-era caveats. Best when your actual product source is in Figma. citeturn6search0turn37search2turn37search4 |
| **Land-book** | Website inspiration with daily curation, section-level browsing, and boarding | Strong public HTML with categories, sections, and curated guidelines; Pro adds search depth, boards, screenshot downloads, and section access. I did not locate a public API in the reviewed sources. citeturn35search0turn35search1turn35search4 |
| **Godly** | High-end web inspiration, especially motion, expressiveness, and SaaS/startup marketing surfaces | Strong public HTML taxonomy by type, style, tech, and preset. Good for browsing; I did not locate a public API in the reviewed sources. citeturn5search0turn5search8 |
| **SiteInspire** | Broad website gallery with categories, styles, types, and subjects | Public browseable HTML; useful as a stable browse source, but no official API surfaced in the reviewed materials. citeturn3search3 |
| **Awwwards** | Experimental and award-heavy web precedent, especially interaction, 3D, and tech-driven expression | Public browseable HTML with categories and technology filters such as WebGL, React, GSAP, Framer, and Webflow. Best treated as an expressive frontier source rather than a default usability baseline. citeturn4search5turn4search1 |
| **Radix, Carbon, Polaris, Material** | Same-domain system precedent at component and rules level | Official docs expose components, states, accessibility notes, and implementation guidance. These are excellent for extracting transferable patterns after the far-domain phase. citeturn10search1turn24search0turn24search1turn26search0turn26search4turn25search3turn25search2 |

For this pack, I would rank sources by **use in the sequence**, not by prestige. In the far-domain raid, front-end should not look at front-end at all. In the same-domain phase, use Refero or Mobbin for pattern precedent, then use design systems and component docs to extract implementation-safe principles. Awwwards, Godly, and Land-book are best as controlled injections for personality, pacing, and interaction language, not as the sole basis for the build. citeturn1search1turn1academia51turn36search0turn3search1turn24search0

## Worked pack for architecture and the shared cross-domain pool

An architecture pack needs both editorial precedent and higher-signal archival or award sources, because “pretty project pages” are not enough.

| Source | Best use | Agent-consumability |
|---|---|---|
| **ArchDaily** | Broad precedent discovery across built projects, topics, and contemporary materials/typologies | Massive public platform and strong metadata on many project pages; however, the site now also has subscriber-only access layers. Good for discovery, mixed for automated depth. citeturn11search0turn11search1turn11search3 |
| **Divisare** | Higher-curation project archive; better for image-by-image and typological study | Very strong curation philosophy and long-running archive, but significant archive access is subscription-gated. High quality, lower openness. citeturn27search1turn27search4turn27search3 |
| **AIA Awards** | Strong signal set of award-filtered exemplars across categories | Public award listings and winner archive access; useful as a vetted precedent subset. citeturn32search0turn32search3 |
| **RIBA International Awards** | High-signal international exemplars with jury framing | Public winner announcements and project framing; good for curated global scan. citeturn32search1 |
| **EUmies Awards** | European contemporary architecture exemplar archive | Public archive around award nominees and winners; useful for typology and discourse-level precedent. citeturn32search2 |

For a shared cross-domain pool, the strongest 2026 pattern is to prefer **open cultural, scientific, and natural-history datasets** over commercial moodboard platforms.

| Pool slice | Strong source options | Agent-consumability |
|---|---|---|
| **Nature / biomimicry** | AskNature, AskNature Chat | Open-access biological strategy database and emerging AI interface for nature-language queries. Excellent for principle-first analogies. citeturn33search0turn0search1 |
| **Art / history / cultural heritage** | Europeana, The Met Collection API, Smithsonian Open Access, Wikimedia Commons API | All provide robust machine-readable access or open collections, with Europeana also exposing IIIF-facing APIs. These are among the best cross-domain pools for images and object metadata. citeturn12search0turn12search2turn16search2turn16search4turn13search1turn19search1 |
| **Literature / books** | Open Library APIs | Public APIs, low-volume guidance, and bulk dumps make it a good book-level source if you respect the service constraints. citeturn19search0 |
| **Music metadata** | MusicBrainz | Open web service with rate limits and stable identifiers; good for artist/track/release metadata. | citeturn13search0turn13search2 |
| **Science / research** | NCBI E-utilities, Crossref REST, OpenAlex | Public scientific metadata infrastructure; OpenAlex is especially notable for free API access and explicit LLM guidance. citeturn15search0turn15search1turn34search0turn34search3 |
| **Materials** | Materials Project, Materiom Commons | Materials Project is strong for scientific properties via API; Materiom Commons is strong for open-access biomaterials recipes and performance descriptions. citeturn18search3turn18search4turn18search2 |

One important negative conclusion is that **commercial music platforms are now weak default sources for agentic inspiration grounding** if you need machine-friendly descriptors. Spotify’s restrictions on AI use and its removal of Audio Features and Audio Analysis for new Web API use cases mean it is no longer a reliable foundation for inspiration mining. For music-as-inspiration, use open metadata sources like MusicBrainz plus direct multimodal audio analysis from current foundation models. citeturn14search1turn14search3turn13search0

## Multimodal grounding and DNA extraction

What is achievable now is materially better than even a year ago. Current multimodal APIs can inspect screenshots and image sets directly, and current audio stacks can transcribe, reason over, and in some cases respond in real time. OpenAI’s image/vision guide supports image input in the Responses or Chat APIs, and OpenAI’s May 2026 audio release introduced GPT‑Realtime‑2 and companion realtime translation/transcription models. Google’s Gemini 2.5 audio stack similarly emphasizes native audio dialog, live voice interactions, and translation. citeturn8search0turn8search4turn8search2turn9search1turn9search2

For inspiration work, the practical multimodal pipeline is:

First, **ingest the raw reference**: screenshots, site captures, Figma nodes, building photos, diagrams, music clips, or film stills. Second, run **structured extraction** rather than freeform summarization. Ask for the same slots every time: composition, hierarchy, density, rhythm, pacing, contrast strategy, palette logic, textural logic, emotional register, and recurring mechanisms. Third, derive **comparison tokens** across at least three references. Fourth, convert those shared traits into something implementation can consume: DTCG tokens, a DESIGN.md file, component notes, or a materials/pattern vocabulary. Fifth, run an **anti-copy pass** that removes one-off signatures tied to a single source and keeps only patterns repeated across multiple references or justified by the brief. citeturn22search0turn22search3turn36search3turn22academia39

This “DNA extraction” approach is still partly emerging rather than fully standardized, but several pieces are snapping into place. Refero Styles is literally framing extracted design context as DESIGN.md for agents. The Design Tokens Community Group reached its first stable version in late 2025 and published the 2026 format draft for token interchange. Brickify shows a closely related research direction: extracting visual elements from reference images and turning them into interactive, reusable design tokens instead of relying only on text prompts. citeturn36search1turn36search3turn22search0turn22search3turn22academia39

Where possible, prefer **source-native context over pixels**. Figma MCP can expose design context and code directly from live files. Mobbin MCP can return screen images inline for AI consumption. Shopify.dev’s MCP server now supports Polaris web components. Those are better fits for implementation phases than hoping a model “reads” every visual subtlety from screenshots alone. citeturn37search2turn37search4turn6search2turn26search4

## The North Star artifact

The implementation-phase artifact should be domain-agnostic, compact, and executable. The most useful template I found is:

| Field | What it contains |
|---|---|
| **Concept sentence** | One sentence that states the governing idea in plain language |
| **Metaphor or source logic** | The far-domain concept that shaped the direction, expressed as relational logic, not decoration |
| **User promise** | What the artifact should feel like or enable for the end user |
| **Core principles** | Five to seven design laws, phrased as verbs or decision rules |
| **Principles ledger** | Which same-domain precedents supported which principle |
| **Token layer** | Color, type, spacing, density, motion, material, or tonal tokens |
| **Pattern vocabulary** | Named components, spatial patterns, interaction/circulation patterns |
| **Mood and personality** | Adjectives with evidence, not just vibes |
| **Do / don’t** | Positive and negative boundaries to prevent drift and copying |
| **Implementation tests** | Accessibility, performance, constructability, maintainability, or brand-fit checks |
| **Open questions** | What is still unresolved and must be learned in prototyping |

If you are encoding this into an agent skill, the critical thing is that the North Star should be both **human-readable** and **agent-readable**. In 2026, the obvious serialization choices are a markdown contract such as DESIGN.md plus a token file aligned to DTCG-style structure. That combination gives you narrative guidance and machine-actionable decisions in the same bundle. citeturn36search3turn36search2turn22search2turn22search3

A useful litmus test is this: if you delete all source images, can the implementation agent still build in the same spirit from the artifact alone? If not, the work is still a collage of references instead of a real concept direction. That is the point of the artifact. It should survive reference removal. The references are there to justify the direction, not to be continuously copied from. citeturn1search1turn0search3turn23academia41

## What is state of the art in 2026

There is a meaningful split between what now looks like **consensus** and what is still **emerging**.

The consensus layer is clear. Multimodal models can inspect screenshots and images directly; audio-capable models can now transcribe, converse, and in some cases reason in real time; and MCP has become the dominant tool-connection protocol for many agent workflows. On the product side, there are already first-party or official inspiration-relevant integrations: Figma MCP, Mobbin MCP/API, Refero MCP, Shopify.dev MCP, and documentation being rewritten to be more agent-legible. On the method side, the safest high-confidence position is that structured precedent use and staged example timing outperform naive “show me some inspiration” prompting. citeturn8search0turn8search2turn9search1turn7search1turn36search0turn6search2turn37search2turn26search4turn1academia51turn23search1

The emerging layer is where the most interesting movement is happening. DESIGN.md is becoming a de facto plain-text design layer for AI-assisted frontend work, but it is still informal and tool-led rather than standardized. DTCG tokens are much more formal, and the 2025–2026 stabilization of the spec matters a lot because it gives agents a vendor-neutral way to consume visual decisions. We are also seeing early signs of domain-specific agent infrastructures outside software, such as MCP-oriented BIM architectures for building-model interaction. Research on LLM analogical creativity is promising, but still not stable enough to replace explicit bridge prompts, evaluation rubrics, or human review. citeturn36search3turn22search0turn22search3turn36academia38turn21academia25turn1search0turn0academia52

There is also a real risk layer. MCP is growing very quickly, but empirical studies and security analyses are already finding maintainability problems, tool poisoning, prompt injection pathways, and composition risks. So for inspiration packs specifically, I would keep them mostly **read-only**, provenance-heavy, and capability-scoped. Inspiration sources should enrich context, not silently modify codebases or design files unless the user explicitly wants that. citeturn7search1turn7academia62turn6academia74turn36academia39

The most notable practitioners and institutions in this space are not a single canon yet, but a cluster. On the research side, the most relevant lineage runs through design-by-analogy, fixation, and analogy-generation work associated with scholars such as Joel Chan, Keith Holyoak, and collaborators. On the practice and tooling side, the Biomimicry Institute provides the cleanest model for principle-first cross-domain sourcing; Figma, Mobbin, Refero, Shopify, and OpenAlex are among the clearest examples of platforms adapting resources for agents rather than only for humans. citeturn0search3turn21search0turn21academia25turn33search0turn37search2turn6search2turn36search0turn26search4turn34search3

## Open questions and limitations

Film and music remain the weakest parts of a public, rights-clean, agent-ready inspiration stack. I found strong open metadata for music and strong multimodal model support for audio analysis, but much weaker open, first-party, machine-friendly cultural catalogs for contemporary film language than for art, books, science, or architecture. For those slices, I would currently treat the pack as hybrid and somewhat incomplete. citeturn13search0turn14search3turn8search2turn9search2

The other open question is standardization. DTCG tokens are stabilizing fast, but DESIGN.md is still an emerging practice rather than a formal standard. That means the best current setup is pragmatic: use DESIGN.md-like narrative context for concept direction, use DTCG-aligned tokens for exact decisions, and keep provenance attached to every extracted principle. citeturn22search0turn22search3turn36search3

The practical bottom line is straightforward: build one universal method, keep the cross-domain pool shared and first-class, delay same-domain precedent until after the agent has rough ideas of its own, and make every domain pack a curated retrieval layer with explicit access, modality, and legal metadata. That is the most robust path to agent-driven inspiration grounding that is operational today. citeturn1search1turn23academia39turn36search0turn22search3