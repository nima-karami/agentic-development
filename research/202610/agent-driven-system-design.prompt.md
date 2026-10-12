# Research prompt: an agent that designs a system's high-level architecture

## Context

The findings will feed an agent skill that *produces* a system-level
architecture. Given a product requirements document, the agent should design
the architecture of a whole application or system: the components and their
responsibilities, data and its ownership, integration and communication,
deployment topology, technology choices, and the quality attributes that drive
them, written so humans can review it and downstream agents can build from it.
*Reviewing* a written design before code, with a fresh-context architecture
critic, is already covered.

This sits between a PRD (what to build and why) and feature specs and
implementation plans (how each piece behaves and gets built).

## Questions to answer

1. **The process.** How do strong architects go from requirements to a
   system design? Cover quality-attribute elicitation and scenarios, constraints,
   domain modeling and boundaries (DDD, bounded contexts), option generation,
   trade-off evaluation (ATAM-style), and documenting the result. Which steps can
   an agent run alone, and which need a human?
2. **Right-sizing.** How should design depth scale with the system: a small
   internal tool, a single product app, a multi-team platform? How do you avoid
   over-engineering (microservices, event sourcing, or Kubernetes because it
   looks senior) and under-engineering (no thought about data ownership,
   failure, or scale until it hurts)?
3. **The decisions that matter.** Which decisions are architecturally
   significant at system level: decomposition (monolith, modular monolith,
   services), data storage and ownership, sync vs. async communication, state and
   consistency, identity and auth, front-end architecture (rendering model,
   app-shell vs. micro-frontends, state management), deployment and environments,
   observability, security boundaries, build vs. buy. For each: the forces that
   decide it and sensible defaults.
4. **Documentation.** Which formats work for humans *and* agents: C4 model,
   arc42, ADRs, diagrams-as-code (Mermaid, Structurizr, D2), fitness functions,
   architecture decision logs? What is the minimum useful set?
5. **Technology selection.** How should an agent pick a stack without defaulting
   to whatever is most popular in its training data? How should it check what is
   current, mature, and suited to the team?
6. **Agents designing systems.** What is the current evidence on LLM agents
   producing system designs? Known failure modes, benchmarks, and techniques that
   work (multiple options, explicit trade-off tables, adversarial review, design
   followed by a spike). How do you keep a design honest once code starts and
   reality pushes back (evolutionary architecture, conformance checks)?
7. **What changed since June 2026.** Focus on new tools, papers, and practices
   since then, especially for agent-generated architecture and architecture
   conformance checking.

## Evidence rules

- Cite named, checkable sources: architecture books and papers, SEI material,
  vendor architecture guidance, published engineering case studies, and recent
  papers on LLMs in software architecture. Date each claim.
- Separate **established practice**, **emerging**, and **opinion**.
- Don't invent benchmarks, frameworks, product names, or statistics.

## Output I want

- A short answer up front: how an agent should go from PRD to system design.
- A step-by-step method with clear inputs, outputs, and human checkpoints.
- A table of the significant system-level decisions with their forces,
  defaults, and red flags.
- A recommended design-document structure, right-sized for small, medium,
  and large systems.
- Guidance on choosing diagram types and notation.
- Failure modes (agent-specific and general) with defences.
- The handoff contract: what the design passes downstream to feature specs,
  implementation plans, and a build pipeline, and what it expects from the PRD
  upstream.

## Out of scope

- Reviewing an existing written design (already covered).
- Low-level code design: classes, functions, and patterns inside a module.
- Infrastructure-as-code specifics for any single cloud provider.
