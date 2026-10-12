# Research prompt: helping humans understand, learn, and decide faster

## Context

The findings will feed guidance for agents that write for people: plans,
reviews, diffs, research reports, status updates, design options. Agents now
produce this material faster than a reader can absorb it, so the bottleneck has
moved from producing to **understanding and deciding**. Tone, wording, and
removing AI tells are already covered. This is about **structure and
presentation**: how information should be shaped so a person can take in
something complex, learn it, and make a good decision quickly.

Agents manage their own context with progressive disclosure. The same idea, and
others such as visuals, diagrams, and layered summaries, may apply to humans.
The question is what is actually known about this.

## Questions to answer

1. **The science.** What do cognitive science and human-factors research say
   about comprehension speed and decision speed? Areas to cover: cognitive load
   theory, working-memory limits, chunking, dual coding and multimedia learning
   (Mayer), pre-attentive processing, expertise and recognition-primed decision
   making (Klein), sensemaking. What is solid, and what is a popular myth
   (learning styles, for example)?
2. **Presentation methods.** Which methods measurably speed up understanding?
   Evaluate: bottom-line-up-front and the Minto pyramid, progressive disclosure
   and layered documents, executive summaries, tables vs. prose, diagrams (which
   kinds, for which content), data visualization (Tufte, Cleveland & McGill),
   worked examples, analogies, comparisons and diffs, and interactive
   explorables. For each: what kind of content it suits and the evidence behind it.
3. **Decision-ready information.** How do high-stakes fields brief decision
   makers quickly? Military (BLUF, commander's intent), aviation and medicine
   (checklists, SBAR), intelligence analysis (structured analytic techniques,
   confidence language), and executive memos (for example, the Amazon six-pager).
   What transfers to software work?
4. **Learning fast.** How does a person get up to speed on an unfamiliar complex
   domain or codebase quickly? Look at evidence on retrieval practice, spacing,
   elaboration, concept maps, and the expert-novice gap. How can an AI tutor or
   assistant speed this up without creating the illusion of understanding?
5. **AI-specific risks.** What does research say about over-reliance, automation
   bias, skimming polished AI output, and lost skill when AI does the summarizing?
   How do you design output so the human's understanding is real and can be checked?
6. **Choosing a format.** Given some content (a plan, an architecture, a code
   review, a status update, research findings, a trade-off), how should an agent
   decide between prose, a table, a diagram, an interactive page, or a short
   answer with detail on demand?

## Evidence rules

- Prefer peer-reviewed research and named practitioner sources. Separate
  **replicated findings** from **single studies** and from **practitioner
  folklore**.
- Call out debunked or contested ideas explicitly.
- Don't invent effect sizes or studies; if a number has no source, leave it out.

## Output I want

- A short answer up front: the few principles that matter most, ranked by
  evidence and impact.
- A content-type → format decision table that an agent could apply.
- Concrete templates or patterns: layered summary, decision brief, diagram
  selection guide, comparison table, with when to use each.
- Anti-patterns, such as walls of text, decorative diagrams, false precision, or
  summaries that hide uncertainty, and why each one slows a reader down.
- Guidance for agents writing for a human in a terminal, chat, or doc: what to
  lead with, what to defer, and how to signal confidence and what is left out.
- Ways to check that a reader understood correctly, not just that they read it.

## Out of scope

- Tone, voice, and wording style (covered elsewhere).
- Speed-reading techniques and nootropics.
