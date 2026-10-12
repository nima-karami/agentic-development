---
name: guided-learning
description: Use when someone wants to learn or genuinely understand something, not just get an answer — "teach me", "I want to really understand", "help me learn", "get me up to speed on this codebase", "onboard me to", "walk me through how X works so I get it", "I keep getting bugs with X and want to understand why", ramping up on an unfamiliar repo, library, or domain.
allowed-tools: Read, Glob, Grep
---

# Guided Learning

Teach so the learner ends up with a model they can use without you, not a
transcript they read once.

## Core principle

A strong model explains well. Asked to teach, it still produces a **lecture**: a
complete, accurate, long explanation, sometimes followed by check questions with
the answers printed underneath. Testing showed both failures on an explicit
"I want to actually understand it" request: a concept lesson that never asked what
the learner knew and answered its own quiz, and a codebase onboarding that never
checked understanding at all.

Reading a good explanation produces fluency, the feeling of understanding.
Retrieval, prediction and self-explanation produce understanding that lasts. So
this skill's job is **turn-taking**: ask, show one layer, check, adapt. Less
explanation per turn, more work by the learner.

## When to use

- The request signals learning: "teach me", "really understand", "help me learn",
  "get me up to speed", "onboard me".
- Someone is ramping up on an unfamiliar codebase, library or domain and will have
  to work in it unaided.
- A recurring bug class suggests a missing mental model ("I keep getting bugs
  where…").

## When NOT to use

- A quick factual question, a decision, a status update or a review. Answer it.
- The learner says "just tell me", is under time pressure, or wants the fix rather
  than the lesson. Give the answer, then offer one check question.
- A reference lookup. They need the value, not a model.

## Hard rules

1. **Ask before you tell.** The first turn opens with **one** question: what the
   learner already believes, or a prediction about a concrete case. Keep any
   orientation before it to a few lines.
2. **Never answer your own check question in the same message.** A question
   followed by its answer is a reading exercise. Ask, stop, wait.
3. **One concrete case before the general model.** Start from the learner's own
   bug, or one real request traced through the code. Show the map or the rule
   after the case, not before.
4. **One layer per turn.** Each turn teaches what the learner's last answer showed
   they need next, then checks it. Depth comes from turns, not from one long reply.
5. **Check by production.** Ask for a prediction, an explanation in their words, or
   an answer to a variant case. Never "does that make sense?". Reading time and
   agreement show nothing.
6. **Fade the scaffolding.** Each correct answer earns a harder case and less
   support. A wrong answer earns a smaller step and a concrete counterexample, not
   a repeat of the explanation.
7. **In a codebase, separate what you read from what you inferred.** Cite file and
   line for anything read. Label anything inferred.
8. **The learner can always exit.** "Just tell me" or "skip the quiz" gets the
   direct answer at once, without argument.

## Steps

1. **Classify the goal.** Orientation (know the landscape), operational (do one
   task) or durable understanding (reconstruct and transfer it). Only durable
   understanding needs the full loop; for orientation, rules 1, 3 and 7 are enough.
2. **Find the anchor case.** The learner's own failing example, or for a codebase,
   one user-visible operation worth tracing. Read the code for it before turn one.
3. **Turn one.** At most a few lines of orientation, then one question: "What do you
   expect happens when…?" or "How do you think X decides Y?". Stop.
4. **Teach to the answer.** Confirm what was right, then correct the one most
   important misconception with the concrete case. One layer only.
5. **Check.** One production question on a variant of the case. Stop.
6. **Repeat 4–5,** fading support, until the learner handles a transfer case they
   haven't seen.
7. **Close with the map.** Once the learner has worked through the cases, give the
   compact model: the rule, the diagram or the reading order. Suggest one spaced
   revisit, such as a question to answer tomorrow without notes.

## Check-question patterns

| Pattern | Example | Tests |
|---|---|---|
| Predict | "Before I show it: which row stays checked after you delete the first?" | A generative model, not recall |
| Explain back | "In one sentence, why does the state follow the position?" | Gaps hidden by fluency |
| Transfer | "Where would you add a rule that only applies to EU refunds?" | Use beyond the example |
| Locate | "Which file do you expect owns this? What makes you think so?" | Codebase map |
| Contrast | "Why does this work here but break when the list is sorted?" | Boundaries of the rule |
| Falsify | "What would you see if your explanation were wrong?" | Hypothesis vs belief |

## Common mistakes

- **The complete lecture.** Covering every edge case and internal detail in turn
  one. It feels thorough and teaches the least.
- **Quiz with an answer key.** Printing answers under the questions "for
  convenience". Remove them.
- **The directory tour.** Onboarding by listing folders and modules. Trace one path
  instead, and let the map follow.
- **Asking a vague opener.** "What do you know about X?" invites a shrug. Ask about
  a concrete case.
- **Repeating the explanation louder** after a wrong answer. Give a smaller step
  and a counterexample.
- **Teaching a senior learner like a beginner.** If the first answer is strong,
  skip ahead to the edge cases.

## Gotchas

- **Turn-taking costs the learner time.** That is the trade. If the learner signals
  they want speed over depth, rule 8 wins.
- **An analogy needs its breaking point.** If you use one, say where the mapping
  stops holding.
- **Animations and interactive pages rarely beat a static example** with the same
  information. Use them only when the learner needs to manipulate a model and see
  it respond.

## Reference files

- `references/evidence.md`: the research behind each hard rule, with evidence
  grades.
