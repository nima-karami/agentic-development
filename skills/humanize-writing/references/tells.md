# Tells — scan-list (a checklist, not hard bans)

Scan output for these. Each entry is a **prompt to check**, not an automatic delete.
Keep any word that is genuinely the right one; cut it when it's filler or reflex.

## Filler adjectives / adverbs (usually cut)

comprehensive, robust, seamless, powerful, cutting-edge, state-of-the-art,
transformative, vibrant, rich, crucial, vital, essential, key, significantly,
effectively, efficiently, effortlessly, seamlessly, simply, just, very, really,
actually, basically, quite, fairly

## AI-ism verbs and phrases (replace with the plain form)

- leverage → use
- utilize → use
- facilitate → help / let
- enable → let / allow
- delve into / dive into → look at
- navigate (figurative) → handle / deal with
- foster, underscore → support / show
- highlight → show / point out
- ensure → make sure
- it's worth noting / it's important to note → (cut, just say it)
- as we can see → (cut)
- in order to → to
- due to the fact that → because
- a number of → some / several
- in the realm of / when it comes to → for / with
- at the end of the day → (cut)

## Hedge stacks (collapse to one hedge or none)

- "I think it might be a good idea to maybe consider…" → "Let's…" / "Consider…"
- "It could potentially possibly…" → "It may…"
- "This should hopefully…" → "This should…"

## Structural tells

- Opening with a summary of what you're about to say ("In this PR, I will…").
- Closing with a restated summary ("In summary, …").
- Restating the diff or spec back instead of adding information.
- A trailing justification clause on every point ("…, to make sure the test
  actually exercises the broken branch").
- Three-part lists for everything ("clean, simple, and maintainable").
- Em-dash-heavy balanced clauses as a default rhythm.
- Bold-labelling every sentence ("**Note:**", "**Important:**") when prose works.

## Tone tells

- Cheerleading as filler ("Great question!", "Excellent point!", "Nice work!").
- Over-apologizing or over-hedging.
- Marketing voice in factual contexts (release notes, docs, changelogs).
