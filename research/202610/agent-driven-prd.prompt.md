# Research prompt: an agent that writes a good product requirements document

## Context

The findings will feed an agent skill for **kicking off a product**. Given a
product idea, the agent should produce the documents that define what the
product is and what it is not, who it's for, its requirements, and its
boundaries, before anyone specifies features or designs architecture. Turning a
vague **feature** idea into a full behavioral spec (states, interactions, edge
cases, acceptance criteria) is already covered; this is the level above it.

Assume no product-management expertise on the receiving side. The research must
say which documents a good product kickoff needs and what separates a strong PRD
from a long, generic one, so the agent can do this well and a reviewer can judge
its output.

## Questions to answer

1. **Which documents.** What does a product kickoff produce at strong product
   organizations? Candidates to evaluate: vision and strategy statements,
   PR/FAQ (working backwards), product brief or one-pager, PRD, Lean Canvas,
   opportunity solution tree, positioning statement, and success metrics or
   north-star definitions. Which are essential, which are optional, and in what
   order? How has the PRD itself changed (classic long PRD vs. lean or living PRDs)?
2. **What a good PRD contains.** Problem, target users and their jobs, goals and
   **non-goals**, scope and explicit out-of-scope, requirements (functional and
   non-functional), assumptions and risks, constraints, success metrics, release
   slicing, open questions. Which sections actually earn their place, and which
   are ceremony?
3. **Boundaries.** How do good product people define what a product *is not*?
   Methods for scoping, non-goals, anti-personas, and MVP cuts (story mapping,
   MoSCoW, Kano, RICE), and how to keep scope from creeping during elaboration.
4. **From idea to requirements.** Which discovery and framing methods can an
   agent apply without a team or real users: JTBD, problem framing, assumption
   mapping, competitor and alternative analysis, risk categories (value,
   usability, feasibility, viability)? How does it tell validated facts from
   assumptions, and mark the difference in the document?
5. **Ask vs. assume.** At product level the human owns intent. What should an
   agent always ask, what can it infer, and how should it present choices
   (recommended defaults, a small number of questions, one at a time)? What does
   current research and practitioner experience say about agent elicitation?
6. **Agent failure modes.** How do LLMs fail at PRDs: generic boilerplate,
   invented personas and metrics, scope inflation, solution-first framing,
   confident requirements resting on no evidence? What has been shown to help?
7. **Handoff downstream.** What should the PRD hand to the next stages (feature
   specs, architecture design, an autonomous build pipeline) so that a downstream
   agent can work from it without guessing? What is the right level of
   detail, and how should the document stay in sync as things change?

## Evidence rules

- Cite named, checkable sources: published templates and writing from named
  product leaders and companies, product-management books, research on
  requirements engineering and LLM elicitation. Date each source.
- Separate **widely adopted practice** from **one company's custom** and from
  **opinion**.
- Don't invent templates, quotes, or company practices. If a well-known template
  can't be traced to a source, say so.

## Output I want

- A short answer up front: the minimum document set for a product kickoff, and
  what each document is for.
- A recommended PRD structure, with each section's purpose, what "good" looks
  like, and a common mistake. Right-sized: show how it shrinks for a small
  internal tool and grows for a new product line.
- A step-by-step method an agent can follow from a one-paragraph idea to a
  reviewed PRD, including where it stops to ask the human.
- A quality rubric for judging a PRD, usable by a reviewer agent.
- Failure modes and defences.
- The handoff contract to feature specs and architecture design.

## Out of scope

- Feature-level behavioral specs (states, interactions, edge cases), which are
  already covered.
- Go-to-market, pricing, and sales planning beyond what the PRD must state.
