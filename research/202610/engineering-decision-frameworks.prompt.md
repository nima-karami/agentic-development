# Research prompt: elite engineering decision-making and trade-off reasoning

## Context

The findings will feed guidance for how an agent, and the person steering it,
make engineering decisions. In agentic development most of the work is deciding,
not typing: agents make dozens of engineering choices per task, and a human
makes the higher-level ones. The target is to decide the way the CTO or a
principal engineer at an exceptionally well-run tech company decides.

"Decision frameworks" may not be the right frame. The real skill might be
judgment: knowing which few forces matter, what a decision costs to reverse, and
when to stop analysing. Part of this research is to say what the right frame is.

## Questions to answer

1. **What the skill actually is.** How do top engineering leaders describe their
   own decision-making? Is it frameworks, heuristics, mental models, calibrated
   intuition, or some mix? What separates an elite decision-maker from a merely
   competent one, according to evidence and not just anecdote?
2. **Decision frameworks worth knowing.** Survey the ones that hold up in
   engineering use. Examples to evaluate, not take for granted: one-way vs.
   two-way doors and reversibility, Cynefin, cost of delay and WSJF, real-options
   thinking, ATAM and quality-attribute trade-offs, Wardley mapping, build vs.
   buy vs. adopt, pre-mortems, expected value under uncertainty, satisficing vs.
   optimizing, RFC and ADR processes, RAPID/DACI for who decides. For each: what
   question it answers, when it fits, when it misleads, and how much it costs to
   apply.
3. **Trade-off reasoning.** How do strong engineers weigh competing forces:
   speed vs. quality, consistency vs. availability, flexibility vs. simplicity,
   build cost vs. run cost, local optimum vs. org-wide coherence, now vs. later?
   Are there general methods, or only domain-specific ones?
4. **Recurring engineering decisions.** The decisions a CTO makes again and again:
   technology and vendor selection, monolith vs. services, rewrite vs. refactor,
   build vs. buy, when to pay down tech debt, platform investment, standardization
   vs. team autonomy, staffing a bet. What does good practice look like for each?
5. **Control flow of a decision.** How does a good decision proceed from framing,
   to options, to criteria, to evidence, to commitment, to review? How much
   process does each tier of decision deserve? What is the right time-box?
6. **Failure modes.** The known biases and organizational failure patterns:
   resume-driven development, sunk cost, analysis paralysis, HiPPO, novelty bias,
   premature optimization, cargo-culting big-tech practice at small scale. How
   does each show up, and what is the antidote?
7. **Agents as decision-makers.** How do LLM agents fail at engineering
   decisions: overconfidence, defaulting to the most popular stack,
   over-engineering, never escalating? What has been shown to help: forcing
   options, explicit criteria, reversibility tags, adversarial review, escalation
   rules? When should an agent decide alone and when should it ask a human?

## Evidence rules

- Prefer named, checkable sources: books and papers on decision science,
  published engineering-leadership writing (named authors and companies), and
  documented decision processes (public RFC/ADR practices).
- Separate **evidence-backed** methods from **popular but unproven** ones. Say
  when a framework is famous but lacks evidence.
- Don't invent quotes or attribute frameworks to people without a source.

## Output I want

- A direct answer to "frameworks or judgment?" up front.
- A compact decision playbook: how to classify a decision (stakes,
  reversibility, uncertainty), then how much process each class gets.
- A table of frameworks: question answered, best fit, misuse, cost to apply.
- Trade-off heuristics that transfer across domains, each with a concrete
  engineering example.
- A catalog of failure modes with detection signals and antidotes.
- Agent-specific guidance: rules for when an agent decides, recommends, or
  escalates, and the minimum record a decision should leave behind.

## Out of scope

- People management, hiring, and org design, except where they are the decision
  being made.
- Business strategy that doesn't touch engineering choices.
