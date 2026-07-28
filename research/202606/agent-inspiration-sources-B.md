# **A Domain-General Methodology for Agent-Driven Inspiration Sourcing and Synthesis**

The transition from monolithic large language models to modular, skill-equipped autonomous agents has initiated a fundamental architectural shift in generative design and problem-solving1. However, as agents are increasingly tasked with generating complex architectural schemas, user interfaces, and brand identities, they routinely encounter a cognitive bottleneck: heuristic regression. Because artificial neural networks optimize for statistical likelihood within their training distributions, their unconstrained outputs inherently gravitate toward the mean, producing solutions that are derivative, generic, and constrained entirely within the boundaries of the problem's native domain2.  
Furthermore, when generative agents are provided with specific, same-domain examples early in their reasoning process, they suffer from artificial "design fixation." Similar to human cognitive biases, agents anchor to the superficial, surface-level traits of the provided precedent rather than extracting the underlying functional logic, resulting in the mere cloning of visual elements4. Overcoming this limitation requires a rigorous, domain-general methodology that forces the agent to extract abstract structural relationships from far domains, strategically delays exposure to same-domain precedent, and systematically synthesizes these diverse streams into a cohesive design direction. By 2026, the maturation and widespread adoption of the Model Context Protocol (MCP) has made it possible to operationalize this cognitive scaffolding, allowing agents to dynamically query, scrape, and interact with highly curated, pluggable "inspiration packs" across any creative or technical discipline6.

## **1\. The 2026 State of the Art: Multimodal Grounding and Agentic Tooling**

The capability of an artificial agent to source and consume inspiration relies entirely on its access mechanisms, its cognitive architecture, and the structure of the data it retrieves. The ecosystem has evolved significantly past static training data and ad-hoc API scripts, converging decisively on the Model Context Protocol (MCP) as the universal standard for injecting external context into agent workflows6. MCP operates on a standardized client-server architecture, providing a unified interface where AI agents can access external resources, execute remote tools, and load context-shaping prompt templates7. This architecture enables agents to bridge the gap between their static latent knowledge and real-time, domain-specific databases via HTTP/SSE (Server-Sent Events) or local standard input/output (stdio) transports7.  
To understand what is currently achievable for agent-driven inspiration grounding across domains, it is necessary to separate established consensus technologies from emerging experimental capabilities.

| Technology Capability | 2026 Consensus (Widely Deployed) | 2026 Emerging (Pioneering & Experimental) |
| :---- | :---- | :---- |
| **Data Extraction & Scraping** | Standardized DOM scraping using tools like Firecrawl MCP (firecrawl\_scrape), converting unstructured web pages into clean, LLM-ready markdown9. | LLM-powered structured extraction (firecrawl\_extract) utilizing predefined JSON schemas to force raw web data into rigorous, typed properties without brittle CSS selectors9. |
| **Precedent Discovery** | Keyword-based querying of extensive databases, such as searching the Mobbin MCP for specific mobile app screens or simple tags13. | Multimodal semantic similarity search, where an agent inputs a raw architectural floor plan and retrieves computationally similar spatial layouts from Apify-scraped databases like ArchDaily15. |
| **Design Translation** | Translating textual descriptions into raw code or simple SVGs using standard coding agents (e.g., Cursor, Windsurf)7. | Direct generation and manipulation of W3C-standard Design Tokens via native design platform integrations, such as the Figma MCP or Canva MCP, bridging abstract ideas directly into production-ready design variables17. |
| **Multimodal Synthesis** | Basic vision-model capabilities, allowing an agent to view a screenshot and describe its general layout, color palette, and apparent purpose14. | Interactive Conceptual Blending utilizing systems like Misty, which generate "semantic diffs" to merge specific, localized layout blocks from a reference image directly into a work-in-progress codebase21. |

Despite these advanced technical capabilities, providing an agent with unfettered access to a massive repository of examples does not guarantee novel or effective design. If unconstrained by a methodological framework, the agent will simply utilize its tools to retrieve the most statistically common pattern, resulting in localized optimization rather than genuine, cross-pollinated innovation2. Therefore, the tooling must be subordinated to a strict cognitive methodology rooted in human analogical reasoning.

## **2\. Cognitive Foundations for Artificial Inspiration**

To prevent an autonomous agent from acting as a stochastic photocopier of same-domain precedents, the inspiration methodology is grounded in two established cognitive science frameworks: Structure-Mapping Theory and Conceptual Blending. These theories provide the mathematical and logical scaffolding necessary for an agent to process metaphors computationally rather than poetically.

### **2.1 Structure-Mapping Theory and the Far-Domain Raid**

Structure-Mapping Theory (SMT) defines analogies as implicit rules for mapping knowledge from a familiar "Base" domain to a relatively unfamiliar "Target" domain23. SMT dictates that valid, productive analogies are formed not through surface-level object similarities, but through "relational similarity" and "structural consistency"23.  
When an agent is instructed to seek inspiration from a far domain—for example, observing a biological cell to inform the design of an urban transit hub—it must be explicitly prompted to ignore object-level attributes. The fact that a cell is microscopic, organic, and fluid is irrelevant. Instead, the agent must extract higher-order relational properties: a semi-permeable boundary filters specific inputs, a central nucleus regulates resource distribution, and specialized organelles process distinct functions in parallel23. Cognitive engines designed for structural mapping parse inputs into sets of relations and force the agent to establish an isomorphism—a strict, one-to-one mapping of corresponding nodes between the diverse domains2.  
Extensive research demonstrates that "far analogies" (cross-domain structural mappings) produce significantly more novel design concepts than "near analogies" (within-domain mappings). However, far analogies are computationally harder to map due to the lack of surface semantic similarity, requiring deliberate prompting strategies to enforce structural extraction over aesthetic imitation24.

### **2.2 Conceptual Blending and Semantic Attractors**

Conceptual Blending extends SMT by explaining how cognition constructs entirely new, emergent meaning. Instead of a direct, one-to-one transfer of properties from Base to Target, blending involves the integration of four distinct mental spaces: two separate Input Spaces (e.g., Input 1: Musical Composition, Input 2: Physical Architecture), a Generic Space representing the abstract structure they share (e.g., rhythm, hierarchy, tension), and a finalized Blended Space27.  
In the Blended Space, the agent is directed to selectively project elements from both inputs. This process results in emergent structures that inherently belong to neither original domain27. When applied to the latent spaces of artificial intelligence models, linguistic and visual inputs act as "semantic attractors"29. If an agent relies solely on same-domain inputs, the generative output remains trapped in a highly dense, conventional region of its latent space, yielding generic results29. Injecting a far-domain metaphor introduces a secondary, powerful gravitational pull, bending the generative trajectory and stretching the output into novel perceptual and semantic syntheses that exhibit structural rigor rather than random hallucination29.

## **3\. The Universal Precedent-Study Methodology: Anti-Fixation Sequencing**

To operationalize Structure-Mapping Theory and Conceptual Blending, the agent must execute its inspiration sourcing in a specific, immutable sequence. Empirical studies in design cognition reveal that showing specific, highly detailed examples to a designer—human or artificial—*prior* to a generative conceptualization task invariably causes design fixation4. The entity becomes anchored to the superficial traits of the precedent, unable to visualize alternative structural paradigms. The proposed methodology neutralizes this cognitive trap via a strict, four-phase operational sequence.

### **Phase 1: Unconstrained Structural Baseline (Anti-Fixation)**

Before the agent is permitted to query any external databases, vision models, or MCP servers, it must parse the user's brief and generate an abstract, relational model of the problem4. The agent is prompted to output pure, domain-agnostic logic: identifying the core user goals, systemic constraints, necessary data hierarchies, and required state transitions. This phase establishes the "Generic Space" required for later conceptual blending27. By committing to a structural abstraction first, the agent establishes a robust cognitive defense against being overwhelmed by the surface aesthetics of the precedents it will encounter later in the workflow.

### **Phase 2: The Far-Domain Raid (Cross-Pollination)**

With the unconstrained structural baseline established, the agent is granted access to the Shared Cross-Domain Pool. It initiates targeted searches for distant systems that solve structurally analogous problems26. The agent is systematically prompted to identify a minimum of three distinct far-domain analogs—drawn from disciplines such as biology, music, literature, or fluid dynamics—and strictly map their relational "DNA" back to the baseline.  
For example, if the agent maps musical structure to architectural design principles, it must perform rigid relational mappings rather than outputting poetic, unactionable associations:

* **Pitch** (high/low frequency) maps directly to **Spatial Height and Structural Volume**31.  
* **Rhythm** (metric repetition) maps to **Structural Spacing, Columniation, and Grid Modules**31.  
* **Polyrhythm** (multiple simultaneous time signatures) maps to **Multi-layered Facade Elevations** acting independently32.  
* **Harmony/Chords** maps to **Material Palettes** operating in simultaneous, complementary unison32.

The agent outputs a set of "Transferable Principles," defining exactly how the mechanics of the chosen far domain will dictate the structure, hierarchy, and pacing of the target design, ensuring the cross-pollination bridges rigorously to the brief.

### **Phase 3: Same-Domain Precedent Study**

Only after the far-domain principles are definitively locked does the agent query its domain-specific inspiration pack (e.g., querying Mobbin for software UIs, or ArchDaily for architectural structures)15. Because the agent is already firmly anchored to a cross-domain metaphor, it does not browse these libraries aimlessly. Instead, it conducts a highly targeted search for *execution techniques*.  
During this phase, the agent extracts the mechanics of execution: how a specific shadow token creates perceived depth, how a localized navigation pattern handles state changes, or how a specific joinery method connects two distinct materials. The agent is forced via specific prompt constraints to ignore the "content" of the precedent and extract the underlying W3C Design Tokens, API structures, or spatial parameters19. This represents the retrieval of the second Input Space for the conceptual blend.

### **Phase 4: Synthesis and Conceptual Blending**

In the final cognitive step, the agent acts as the synthesizer. It merges the structural metaphor obtained in Phase 2 with the practical execution variables obtained in Phase 3\. The agent utilizes "Localized Blending," isolating specific layout blocks or functional paradigms from the same-domain precedent, and algorithmically morphing their attributes (such as color, scale, proportion, and motion) to adhere to the far-domain principles21. The output of this synthesis is the finalized, actionable design direction.

## **4\. Multimodal Extraction: Abstracting "DNA" Over Cloning**

A critical vulnerability in agentic design is the reliance on raw visual inputs, which often leads vision-language models to simply hallucinate a visual clone of a reference image. To prevent this, the methodology mandates the use of specialized tools and MCP servers that turn a reference image, screenshot, or audio file into transferable principles and tokens.  
When an agent processes a visual reference (e.g., an interface screenshot from Refero or an architectural photograph), it does not merely pass the image to a standard multimodal model. Instead, it employs a "Visual Anchor Prompting workflow." The agent overlays a highly calibrated coordinate grid onto the reference image, identifying the exact grid positions of primary visual elements, calculating pairwise spatial overlaps, and mapping the negative space1. This translates a raw image into a topological graph, extracting the structural "DNA."  
For interactive digital design, the agent utilizes systems akin to Misty, generating a "semantic diff" between the extracted visual hierarchy and the target brief21. Rather than copying a button's specific aesthetic, the agent extracts the W3C Design Tokens—the primitive tokens (raw hex values), semantic tokens (e.g., color-background-surface), and component tokens (e.g., button-border-radius)—that define the system19.  
Similarly, in audio-driven cross-pollination, the agent does not listen to raw audio files. It leverages tooling like the Pianist Transformer, which utilizes an asymmetric encoder-decoder architecture with note-level sequence compression to read Musical Instrument Digital Interface (MIDI) data representations35. The agent extracts tempo maps, dynamic variations, and harmonic structures as mathematical arrays, mapping these directly to spatial or temporal design variables35.

## **5\. Building a Domain Inspiration Pack: The Consumability Index**

The universal methodology relies fundamentally on the availability of high-quality, domain-specific data. To allow the agent to shift seamlessly between designing a mobile application, a corporate brand identity, or a physical building, the data sources must be encapsulated in modular "Inspiration Packs." However, an inspiration source is only viable if it is computationally accessible. Human-centric curation sites hidden behind CAPTCHAs, obfuscated DOM structures, or rigid login walls without API access are utterly useless to autonomous systems.  
When building a domain pack, resources must be strictly evaluated and integrated according to their Agent-Consumability Tier, determining the exact toolset the agent must load to access the data.

| Consumability Tier | Description | Agent Implementation & Authentication Mechanism |
| :---- | :---- | :---- |
| **Tier 1: Native MCP Server** | The platform maintains an official Model Context Protocol server exposing exact tools, semantic schemas, and optimized prompts14. | Accessed via stdio or HTTP transports. Authentication is typically handled via Dynamic Client Registration (DCR) or OAuth, ensuring the agent acts within precise permission scopes without brittle credential management8. |
| **Tier 2: Headless API / GraphQL** | The platform offers a structured, documented REST or GraphQL API intended for human developers, providing raw data access. | The operator must wrap these endpoints in a lightweight custom MCP server or provide the agent with a strict OpenAPI specification document, injecting Personal Access Tokens (PATs) securely into the agent's environment17. |
| **Tier 3: MCP-Driven Scraper** | The data is hosted on public HTML without an API. The DOM is predictably structured but intended for human browsers. | The agent is routed through a specialized scraping MCP (e.g., Firecrawl, Apify). Utilizing tools like firecrawl\_extract, the agent provides a predefined JSON schema, forcing the LLM to bypass HTML markup and return clean, typed data objects, natively bypassing anti-bot measures9. |
| **Tier 4: Raw Feeds / Sitemaps** | Basic XML sitemaps or RSS feeds lacking semantic structure, requiring brute-force parsing and downloading of individual terminal URLs38. | The slowest, most token-heavy method. The agent sequentially parses the feed, executing parallel fetch requests and manually synthesizing the raw text outputs. Generally avoided for high-fidelity generative tasks. |

Every Inspiration Pack must adhere to a strict configuration schema containing a Domain Identifier, a manifest of MCP Dependencies, defined Extraction Schemas (JSON schemas dictating what fields the agent must extract), Domain-Specific Precedent Prompts, and a curated Resource Catalog to bound the search space and prevent hallucination11.

## **6\. Worked Example Packs**

The following worked examples demonstrate how to construct packs across diverse, disparate domains, proving the generalizability of the underlying methodology and detailing the specific tooling required for 2026-era agents.

### **Pack A: The Shared Cross-Domain Pool (Universal)**

This pack is universally loaded into the agent regardless of the target design domain. It contains the resources required exclusively for the "Far-Domain Raid" (Phase 2). Because the goal is to extract abstract structural principles (SMT), the tools prioritize encyclopedic, scientific, mathematical, and artistic databases.

| Source Domain | Primary Tooling / Consumability | Agent Action & Structural Extraction Focus |
| :---- | :---- | :---- |
| **Biological & Natural Systems** | Custom MCP server interfacing with PubMed, open-source biomimicry taxonomy APIs, and natural science datasets. | The agent queries mechanisms of physical efficiency, resource distribution, or systemic resilience. It abstracts principles such as fluid dynamics, fractal branching logic, and cellular structural hierarchies. |
| **Musical Theory & Composition** | Native API access to MIDI transformers, computational musicology databases, and tempo-mapping algorithms35. | The agent analyzes symbolic musical scores to extract complex timing, dynamics, and articulation patterns, mapping tempo maps, polyrhythms, and harmonic cadences to spatial or temporal variables32. |
| **Literature & Narrative** | Firecrawl MCP targeting narrative trope databases (e.g., TV Tropes) and literature structural mapping datasets9. | Utilizing frameworks like YARN (Yielding Abstractions for Reasoning in Narratives), the agent decomposes narratives into abstract units, mapping tension-and-release cycles, pacing, and character arcs to user journey flows40. |
| **History & Art Movements** | Semantic vector searches across digitized museum archives and historical epoch metadata. | The agent isolates the socio-economic constraints that birthed specific art movements (e.g., resource scarcity leading to Bauhaus minimalism), mapping these constraints to the user's current project parameters. |

### **Pack B: Software / Front-End Design**

This pack is loaded when the agent is tasked with generating user interfaces, digital experiences, or comprehensive design systems. It leverages the highly mature, Tier-1 digital design ecosystem, focusing heavily on extracting precise tokens and user flows.

* **Primary Precedent Engine: Mobbin MCP (Tier 1\)**  
  * *Consumability & Mechanics:* Mobbin provides an official, Tier 1 MCP server granting access to over 621,000 screens and 142,000 complete user flows from shipped, production-grade applications14. Authentication is handled via a secure browser-based OAuth loop33.  
  * *Agent Action:* The agent completely bypasses generic UI hallucinations by directly querying the MCP server for specific execution patterns. It can search for "B2B analytics dashboard layouts" or "error recovery states in fintech onboarding flows"14. The server returns exact semantic structures and visual anchors, allowing the agent to perform side-by-side structural comparisons against its own baseline, analyzing what is strong, weak, or missing42.  
* **Secondary Curated Galleries: Awwwards, SiteInspire, Godly, Land-book (Tier 3\)**  
  * *Consumability & Mechanics:* These highly curated sites historically relied on human browsing43. In this pack, they are accessed via the **Firecrawl MCP** server9.  
  * *Agent Action:* The agent utilizes the firecrawl\_search tool to locate award-winning reference sites9. It then deploys the firecrawl\_extract tool, passing a strict, predefined JSON schema. The LLM interprets the page content against the schema, pulling structured CSS architectures, typography pairings, grid systems, and layout hierarchies without writing brittle regex or manual DOM selectors9.  
* **Structural Grounding & Branding: Figma MCP & Canva MCP (Tier 1\)**  
  * *Consumability & Mechanics:* The official Figma MCP server and Canva's AI Connector MCP allow the agent to read existing design files, brand kits, and asset libraries17.  
  * *Agent Action:* Instead of generating arbitrary CSS, the agent uses tools like get\_variable\_defs and export\_tokens from Figma to map visual decisions to the W3C Design Tokens standard17. It leverages the Canva MCP to search brand templates, autofill data, and ensure that the extracted execution variables strictly adhere to predefined organizational brand guidelines46.

### **Pack C: Non-Software / Physical Architecture**

To definitively prove the domain-generalization of the methodology, this pack adapts the entire system for physical space, utilizing resources that document the built environment.

* **Primary Precedent Engine: ArchDaily (Tier 3\)**  
  * *Consumability & Mechanics:* ArchDaily, a massive repository of global architectural projects, is accessed via the Apify MCP utilizing a specialized actor (e.g., jungle\_synthesizer/archdaily-architecture-projects-scraper)15.  
  * *Agent Action:* The agent executes programmatic HTTP POST requests via the Apify API to trigger the scraper, filtering the database by precise typology tags, locations, or materials16.  
  * *Extraction Focus:* The Apify scraper guarantees a highly structured JSON output schema containing the building type, floor area (sqm/sqft), structural engineers, landscape architects, and, crucially, an array of high-resolution architectural drawing URLs (plans, sections, elevations)15.  
* **Materiality & Product Sourcing: Stylepark (Tier 3\)**  
  * *Consumability & Mechanics:* Because ArchDaily's native product pages rely on heavy JavaScript rendering that blocks standard API access, the pack substitutes Stylepark.com as the material registry, scraped via an alternative Apify actor51.  
  * *Agent Action:* The agent queries specific material configurations (e.g., composite fiberglass, structural timber, architectural concrete) and retrieves precise structural specifications, manufacturer data, and physical constraints51.  
* **Multimodal Spatial Analysis**  
  * *Agent Action:* Once the architectural drawing URLs are extracted, the agent utilizes its vision-language models to perform the Visual Anchor Prompting workflow. It calculates spatial overlaps, load-bearing proportions, and abstracts the physical layout into a relational, topological graph, ensuring the physical precedent aligns with the previously established far-domain metaphor (e.g., mapping a biological cellular structure onto a physical floor plan)1.

## **7\. The Domain-Agnostic "North Star" Artifact**

The culmination of the four-phase methodology, having processed inputs from both the shared cross-domain pool and the specific domain inspiration packs, is the generation of the "North Star / Concept Direction" artifact. This serves as the definitive handoff document. It is explicitly designed to be domain-agnostic in its overarching structure, ensuring that a downstream implementation agent—whether a React coding agent generating front-end code, or a parametric CAD scripting agent generating architectural forms—can consume it immediately without ambiguity1.  
The artifact abandons vague, human-centric "mood boards" in favor of strict computational constraints. It is output as a structured payload, typically formatted as Markdown embedded with typed JSON blocks, comprising five fundamental, interconnected sections:

### **1\. The Blended Metaphor (Conceptual Logic)**

A precise narrative articulation of the Conceptual Blend28. It explicitly identifies the Far-Domain source, the Target Domain, and the specific relational isomorphism that binds them, providing the core rationale for all subsequent decisions.

* *Example:* "The architecture of this decentralized data protocol interface (Target) is structured as a Mycelial Network (Far-Domain). It relies on distributed resource sharing, localized node autonomy, and subterranean (invisible) routing mechanisms."

### **2\. Structural Mappings (The Matrix)**

A rigid table demonstrating exactly how the far-domain principles dictate same-domain execution, ensuring the metaphor is structurally active and computationally enforced, rather than merely decorative23.

| Far-Domain Principle (Base) | Target Domain Translation | Execution Precedent (from Domain Pack) |
| :---- | :---- | :---- |
| Polyrhythmic layering (Music) | Z-index elevation hierarchies and variable parallax scrolling rates. | Reference: Mobbin flow auth\_layered\_modal\_v3 \[cite: 14\] |
| Mycelial nutrient distribution (Biology) | Asynchronous background data fetching and state hydration. | Reference: Firecrawl extraction of react-query pattern |
| Staccato musical articulation (Music) | Sharp, zero-radius UI corners, and abrupt, linear motion curves. | Reference: Figma Token $radius-none, $easing-linear \[cite: 19\] |

### **3\. Anti-Patterns (Do / Don't Constraints)**

Extracted from the initial unconstrained structural baseline and refined by the precedent study, this section establishes explicit, programmatic guardrails against heuristic regression2.

* *DO:* Utilize progressive disclosure for all onboarding elements, hiding complexity until the user explicitly initiates deeper interaction.  
* *DON'T:* Utilize standard modal overlays or pop-ups that interrupt the primary user flow or obscure the underlying structural layout.

### **4\. W3C Design Tokens & Parametric DNA**

The foundational design variables extracted during the same-domain precedent study, formatted to strict industry standards so they can be immediately parsed by CI/CD pipelines, design system compilers, or programmatic rendering engines34.

* Includes typed JSON structures defining color spaces, typography scales, spatial grids, and physics-based motion curves. For software domains, this aligns perfectly with the W3C Design Tokens Community Group specification ($value, $type), ensuring cross-platform interoperability19. For architectural domains, this section includes proportional spatial ratios, material tension limits, and structural grid dimensions.

### **5\. Multimodal Anchors (The Seed Context)**

Rather than providing raw, unannotated images that invite visual cloning, this section contains the precise semantic diffs and coordinate-mapped data extracted from the visual references21. It includes the explicit URLs of the reference precedents, the specific geometric bounding boxes of the features to emulate, and the programmatic code snippets or topological graphs that represent the abstracted structural layout.  
By isolating the inspiration methodology into these rigorous computational structures, autonomous agents can consistently synthesize radically diverse disciplines into coherent, highly functional, and genuinely novel design solutions.

#### **Works cited**

1. Automating Skill Acquisition through Large-Scale Mining of Open-Source Agentic Repositories: A Framework for Multi-Agent Procedural Knowledge Extraction \- arXiv, [https://arxiv.org/html/2603.11808v1](https://arxiv.org/html/2603.11808v1)  
2. Unlocking LLM Creativity in Science through Analogical Reasoning \- arXiv, [https://arxiv.org/html/2605.11258v1](https://arxiv.org/html/2605.11258v1)  
3. Generative analogical intelligence: Speculative co-design through the fabric of analogy \- DRS Digital Library, [https://dl.designresearchsociety.org/cgi/viewcontent.cgi?article=4226\&context=drs-conference-papers](https://dl.designresearchsociety.org/cgi/viewcontent.cgi?article=4226&context=drs-conference-papers)  
4. Cognitive strategies of analogical reasoning in design: Differences between expert and novice designers \- GCRIS, [https://gcris.iyte.edu.tr/bitstreams/2a76f9b4-2c33-4bb1-8b2a-5fc253b40883/download](https://gcris.iyte.edu.tr/bitstreams/2a76f9b4-2c33-4bb1-8b2a-5fc253b40883/download)  
5. The inadvertent use of prior knowledge in a generative ... \- SciSpace, [https://scispace.com/pdf/the-inadvertent-use-of-prior-knowledge-in-a-generative-f06niugozw.pdf](https://scispace.com/pdf/the-inadvertent-use-of-prior-knowledge-in-a-generative-f06niugozw.pdf)  
6. Model Context Protocol (MCP) explained: A practical technical overview for developers and architects \- CodiLime, [https://codilime.com/blog/model-context-protocol-explained/](https://codilime.com/blog/model-context-protocol-explained/)  
7. MCP Server: The Complete Guide for Developers (2026) \- Cosmic JS, [https://www.cosmicjs.com/blog/mcp-server-complete-guide](https://www.cosmicjs.com/blog/mcp-server-complete-guide)  
8. What Is the Model Context Protocol (MCP) and How It Works \- Descope, [https://www.descope.com/learn/post/mcp](https://www.descope.com/learn/post/mcp)  
9. How to Set Up and Use Firecrawl MCP in Cursor, [https://www.firecrawl.dev/blog/firecrawl-mcp-in-cursor](https://www.firecrawl.dev/blog/firecrawl-mcp-in-cursor)  
10. 10 Best MCP Servers for Developers in 2026 \- Firecrawl, [https://www.firecrawl.dev/blog/best-mcp-servers-for-developers](https://www.firecrawl.dev/blog/best-mcp-servers-for-developers)  
11. firecrawl/firecrawl-mcp-server at ajianaz.dev \- GitHub, [https://github.com/firecrawl/firecrawl-mcp-server?ref=ajianaz.dev](https://github.com/firecrawl/firecrawl-mcp-server?ref=ajianaz.dev)  
12. AI Agent Tools for Web Data 2026: Firecrawl vs Apify vs Bright Data MCP, [https://use-apify.com/blog/ai-agent-web-tools-comparison-2026](https://use-apify.com/blog/ai-agent-web-tools-comparison-2026)  
13. The UI Professional's Design Manual | PDF | User Experience \- Scribd, [https://www.scribd.com/document/713568662/The-UI-Professional-s-Design-Manual-600-Pages-2022](https://www.scribd.com/document/713568662/The-UI-Professional-s-Design-Manual-600-Pages-2022)  
14. How Designers Are Using Mobbin With Claude for UI Design \- UI UX Showcase, [https://uiuxshowcase.com/shorts/how-designers-are-using-mobbin-with-claude-for-ui-design/](https://uiuxshowcase.com/shorts/how-designers-are-using-mobbin-with-claude-for-ui-design/)  
15. ArchDaily Architecture Projects Scraper \- Apify, [https://apify.com/jungle\_synthesizer/archdaily-architecture-projects-scraper](https://apify.com/jungle_synthesizer/archdaily-architecture-projects-scraper)  
16. ArchDaily Architecture Projects Scraper API \- Apify, [https://apify.com/jungle\_synthesizer/archdaily-architecture-projects-scraper/api](https://apify.com/jungle_synthesizer/archdaily-architecture-projects-scraper/api)  
17. README.md \- superdoccimo/figma-mcp-free \- GitHub, [https://github.com/superdoccimo/figma-mcp-free/blob/main/README.md](https://github.com/superdoccimo/figma-mcp-free/blob/main/README.md)  
18. Canva Model Context Protocol (MCP) \- Canva MCP Documentation \- Canva Developers, [https://www.canva.dev/docs/mcp/](https://www.canva.dev/docs/mcp/)  
19. What Is a Design System? (Defining Components, Styles & Tokens) \- Magic Patterns, [https://www.magicpatterns.com/blog/what-is-a-design-system](https://www.magicpatterns.com/blog/what-is-a-design-system)  
20. Exploring design inspiration: A comparative analysis of three inspiring websites \- UX Planet, [https://uxplanet.org/exploring-design-inspiration-a-comparative-analysis-of-three-inspiring-websites-945be37d3dc4](https://uxplanet.org/exploring-design-inspiration-a-comparative-analysis-of-three-inspiring-websites-945be37d3dc4)  
21. Conceptual Blending in UI Prototyping: A New Frontier in Creative Design | by H | Medium, [https://medium.com/@harsh.mudgal\_27075/conceptual-blending-in-ui-prototyping-a-new-frontier-in-creative-design-7c6f3f63e103](https://medium.com/@harsh.mudgal_27075/conceptual-blending-in-ui-prototyping-a-new-frontier-in-creative-design-7c6f3f63e103)  
22. (PDF) Misty: UI Prototyping Through Interactive Conceptual Blending \- ResearchGate, [https://www.researchgate.net/publication/384266610\_Misty\_UI\_Prototyping\_Through\_Interactive\_Conceptual\_Blending](https://www.researchgate.net/publication/384266610_Misty_UI_Prototyping_Through_Interactive_Conceptual_Blending)  
23. Examining Student and AI Generated Personalized Analogies in Introductory Physics \- arXiv, [https://arxiv.org/html/2511.04290v1](https://arxiv.org/html/2511.04290v1)  
24. Modelling Analogies and Analogical Reasoning: Connecting Cognitive Science Theory and NLP Research. \- arXiv, [https://arxiv.org/html/2509.09381v2](https://arxiv.org/html/2509.09381v2)  
25. The Analogical Mind \- UCLA Reasoning Lab, [https://reasoninglab.psych.ucla.edu/wp-content/uploads/sites/273/2021/04/HolyoakThagard.1997pdf.pdf](https://reasoninglab.psych.ucla.edu/wp-content/uploads/sites/273/2021/04/HolyoakThagard.1997pdf.pdf)  
26. Comparing Analogy-Based Methods—Bio-Inspiration and Engineering-Domain Inspiration for Domain Selection and Novelty \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11201427/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11201427/)  
27. Conceptual Blending and the Quest for the Holy Creative Process, [https://eden.dei.uc.pt/\~camara/files/QuestCRC.pdf](https://eden.dei.uc.pt/~camara/files/QuestCRC.pdf)  
28. Conceptual Blending \- FunBlocks AI, [https://www.funblocks.net/thinking-matters/classic-mental-models/conceptual-blending](https://www.funblocks.net/thinking-matters/classic-mental-models/conceptual-blending)  
29. From the represenationalist stance to conceptual blending in AI-generated images \- Riviste UNIMI, [https://riviste.unimi.it/index.php/itinera/article/download/30244/25035/88899](https://riviste.unimi.it/index.php/itinera/article/download/30244/25035/88899)  
30. From the represenationalist stance to conceptual blending in AI-generated images \- R Discovery, [https://discovery.researcher.life/article/from-the-represenationalist-stance-to-conceptual-blending-in-ai-generated-images/cc4e599586fd3600b124ec2a3732797b](https://discovery.researcher.life/article/from-the-represenationalist-stance-to-conceptual-blending-in-ai-generated-images/cc4e599586fd3600b124ec2a3732797b)  
31. Music as Architectural Design Catalyst | PDF | Harmony | Space \- Scribd, [https://www.scribd.com/document/637175655/Untitled](https://www.scribd.com/document/637175655/Untitled)  
32. VISUALIZING MUSIC COMPOSITIONS IN ARCHITECTURAL CONCEPTUAL DESIGN \- Digital Commons @ BAU \- Beirut Arab University, [https://digitalcommons.bau.edu.lb/cgi/viewcontent.cgi?article=1078\&context=apj](https://digitalcommons.bau.edu.lb/cgi/viewcontent.cgi?article=1078&context=apj)  
33. Mobbin MCP — Design reference for AI agents, [https://mobbin.com/mcp](https://mobbin.com/mcp)  
34. Design Tokens — Latest documentation, [https://docs.openedx.org/en/latest/developers/concepts/design\_tokens.html](https://docs.openedx.org/en/latest/developers/concepts/design_tokens.html)  
35. 1 Introduction \- arXiv, [https://arxiv.org/html/2512.02652](https://arxiv.org/html/2512.02652)  
36. Simplifying Figma MCP Server: How to Start in Minutes \- DEV Community, [https://dev.to/denyherianto/figma-mcp-server-3o8p](https://dev.to/denyherianto/figma-mcp-server-3o8p)  
37. Building a Web Research Agent Using UiPath OpenAI Agents SDK and Firecrawl MCP, [https://medium.com/@jagtapabhi13/building-a-web-research-agent-using-uipath-openai-agents-sdk-and-firecrawl-mcp-14ede515e6c3](https://medium.com/@jagtapabhi13/building-a-web-research-agent-using-uipath-openai-agents-sdk-and-firecrawl-mcp-14ede515e6c3)  
38. Website and Service Recommendations \- Sevensoft, [https://sevensoft.com/sites](https://sevensoft.com/sites)  
39. FAQ | Design Tokens Community Group, [https://www.designtokens.org/faq/](https://www.designtokens.org/faq/)  
40. Enhancing Structural Mapping with LLM-derived Abstractions for Analogical Reasoning in Narratives \- arXiv, [https://arxiv.org/html/2603.29997v1](https://arxiv.org/html/2603.29997v1)  
41. Mobbin Launches MCP Server, Giving AI Tools 621500 Real App Screens to Reference, [https://www.morningstar.com/news/business-wire/20260511053592/mobbin-launches-mcp-server-giving-ai-tools-621500-real-app-screens-to-reference](https://www.morningstar.com/news/business-wire/20260511053592/mobbin-launches-mcp-server-giving-ai-tools-621500-real-app-screens-to-reference)  
42. I Connected Mobbin MCP to AI and Unlocked 1000s of Real UI Screens to Design With, [https://designerup.co/blog/mobbin-mcp-to-ai-1000s-of-real-ui-screen-designs/](https://designerup.co/blog/mobbin-mcp-to-ai-1000s-of-real-ui-screen-designs/)  
43. Siteinspire \- Studio Mast, [https://www.studiomast.co/projects/siteinspire/](https://www.studiomast.co/projects/siteinspire/)  
44. siteInspire \- Dev Resources, [https://devresourc.es/resource/siteinspire/6fc33cc7-13c3-4bd5-aba7-501d2fa7ae8c](https://devresourc.es/resource/siteinspire/6fc33cc7-13c3-4bd5-aba7-501d2fa7ae8c)  
45. Figma skills for MCP, [https://help.figma.com/hc/en-us/articles/39166810751895-Figma-skills-for-MCP](https://help.figma.com/hc/en-us/articles/39166810751895-Figma-skills-for-MCP)  
46. Design smarter than ever with Canva's AI Connector, [https://www.canva.com/ai-connector/](https://www.canva.com/ai-connector/)  
47. Design Tokens in 2026: Auto-Generate Them in Seconds | OneMinuteBranding, [https://www.oneminutebranding.com/blog/design-tokens-2026](https://www.oneminutebranding.com/blog/design-tokens-2026)  
48. Canva MCP server \- 22 tools \- Speakeasy, [https://www.speakeasy.com/product/mcp-gateway/catalog/canva](https://www.speakeasy.com/product/mcp-gateway/catalog/canva)  
49. Input · ArchDaily Architecture Projects Scraper \- Apify, [https://apify.com/jungle\_synthesizer/archdaily-architecture-projects-scraper/input-schema](https://apify.com/jungle_synthesizer/archdaily-architecture-projects-scraper/input-schema)  
50. Output · ArchDaily Architecture Projects Scraper \- Apify, [https://apify.com/jungle\_synthesizer/archdaily-architecture-projects-scraper/output-schema](https://apify.com/jungle_synthesizer/archdaily-architecture-projects-scraper/output-schema)  
51. ArchDaily Scraper — Architecture Products Directory \- Apify, [https://apify.com/crawlergang/archdaily-scraper](https://apify.com/crawlergang/archdaily-scraper)  
52. Design Systems as Living Architecture \- UI Project | Chris West, [https://www.chriswest.tech/article/design-systems-living-architecture](https://www.chriswest.tech/article/design-systems-living-architecture)