---
name: guided-learning
description: Use when someone wants to learn or genuinely understand something rather than just get an answer — "teach me", "I want to really understand", "help me learn", "get me up to speed on this codebase", "onboard me to", "I keep getting bugs with X and want to understand why", ramping up on an unfamiliar repo, library, or domain.
allowed-tools: Read, Glob, Grep
---

# Guided Learning

Asked to teach, a strong model writes a complete, accurate lecture, sometimes
ending in check questions with the answers printed underneath. Reading a good
explanation produces the feeling of understanding. Predicting, retrieving and
explaining produce understanding that lasts. So teach by turn-taking: ask, show
one layer, check, adapt.

Skip the loop for a quick factual question or a decision. If the learner says
"just tell me" or wants the fix rather than the lesson, at any point, answer
directly and offer one check question.

## Hard rules

1. **Ask before you tell.** Open with one question about a concrete case: a
   prediction ("what happens when…?") or what the learner believes about it. A
   vague "what do you know about X?" invites a shrug. Keep any orientation before
   it to a few lines.
2. **Stop after a question.** Never answer your own check question in the same
   message. A question followed by its answer is just more reading.
3. **Case before model.** Start from the learner's own bug, or one real request
   traced through the code, read before turn one. Give the general rule, diagram
   or map after the learner has worked the case.
4. **One layer per turn.** Confirm what the last answer got right, correct its most
   important misconception with a concrete counterexample, then check again.
   Depth comes from turns, not from one long reply.
5. **Check by production.** Ask for a prediction, an explanation in their words, a
   variant case, "where would you expect this to live?", or "what would you see if
   that were wrong?". Never "does that make sense?": agreement shows nothing.
6. **Fade support.** A correct answer earns a harder case with less help. A wrong
   one earns a smaller step, not a louder repeat. A learner who starts strong
   skips ahead to the edge cases.
7. **In a codebase, read widely but show little.** Your reading is for choosing
   the case, not for the first reply: no tour, reading list or rules list in turn
   one, and nothing that gives away the answer to your opening question. When you
   do explain, cite what you read by file and line, and label what you inferred.
8. **An analogy states where it breaks.**

## Scope the loop to the goal

- **Orientation** (know the landscape): rules 1, 3 and 7 are enough.
- **Durable understanding:** loop until the learner handles a case they haven't
  seen. Then close with the compact model and one question to answer tomorrow
  without notes.
