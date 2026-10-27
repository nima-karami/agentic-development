# Research brief: What happened at every previous abstraction jump in software (1949 to 2024)

## Why I am asking

I am trying to understand the 2026 shift to agent-written code by comparing it with
the earlier shifts: machine code to assembly, assembly to compiled languages, and so
on up to cloud and low-code. I was not around for most of them, so I need the history
told properly, with the same questions asked of every transition, not a one-paragraph
analogy. Two sibling briefs cover current hypotheses about the future of the
profession and the future of software as an artifact; this one is the historical
baseline those hypotheses will be judged against.

The questions I most want answered, for every transition:

- What happened to the people who worked at the layer being abstracted away?
- What happened to the number of programmers needed, the open roles, and their pay?
- Did pay rise or fall in real terms, adjusted for inflation and relative to other
  professions, across the whole period?

## Scope

- Software only. Hardware abstraction (microcode, instruction sets) only where it
  changed how programmers worked.
- Period: 1949 to 2024. Stop before the agent era; it appears only in the final
  section, as the thing being compared.
- Treat each transition as a case study with the same template so they can be
  compared side by side.

## Transitions to cover

Cover all of these and add any I missed:

1. Machine code to assemblers and macro assemblers (late 1940s to 1950s).
2. Assembly to the first compiled languages (FORTRAN 1957, COBOL 1959, ALGOL, LISP),
   including the "automatic programming" debate and the efficiency objection.
3. The software crisis, structured programming, and the coining of "software
   engineering" (NATO conferences 1968 and 1969, Dijkstra, Brooks).
4. Operating systems, time-sharing, and portable systems languages (Unix and C): from
   machine-specific to portable code.
5. Relational databases and SQL: declarative programming sold as "end users will query
   their own data".
6. The 1980s promise of programmer elimination: 4GLs, CASE tools, application
   generators (James Martin, "Application Development Without Programmers", 1982),
   expert systems, Japan's Fifth Generation project.
7. Personal computers, spreadsheets as the largest programming population, and visual
   RAD tools (HyperCard, Visual Basic, Delphi).
8. Object orientation, component models, and managed runtimes with garbage collection
   (Smalltalk through Java and .NET).
9. Scripting and dynamic languages plus the web (Perl, Python, JavaScript, PHP, Ruby,
   Rails) and the appearance of the "web developer" role.
10. Open source and package ecosystems as reuse at scale (CPAN, Maven, npm): the shift
    from writing to assembling.
11. Offshoring and outsourcing (1995 to 2010). Not a technical layer, but the clearest
    previous prediction that Western programming jobs would disappear.
12. Cloud, infrastructure as code, DevOps, serverless, managed services: what happened
    to sysadmins and DBAs.
13. Mobile platforms and app stores: a new artifact type with a new economic model.
14. Low-code and no-code, the second wave of citizen-developer promises (2015 to 2024).
15. Machine learning as a programming paradigm ("Software 2.0", 2017) and the data
    scientist role.
16. Autocomplete to chat to agents (2021 to 2024), covered only as the entry point to
    the current era.

## Template per transition

- What was abstracted away, and what the programmer stopped having to know.
- Contemporary predictions, both kinds: "this will eliminate programmers" and "this
  will never be good enough for real work". Quote them with names and dates.
- What happened to the people already doing the old-layer work: retrained and moved
  up, pushed out, retired early, or stayed as a shrinking well-paid niche. Use oral
  histories, contemporary surveys and retrospectives, and say which outcome dominated.
- What happened to demand: number of programmers employed, open roles and unfilled
  positions (help-wanted indices, trade-press hiring surveys such as Datamation before
  online job boards, posting data after), and who got to be a programmer (education,
  gender, geography). Use labour statistics where they exist (US BLS and census
  occupation counts, UK and European equivalents), not anecdote.
- What happened to pay: nominal and inflation-adjusted, as a multiple of the median
  wage, and relative to comparable professions. State the deflator and the year basis.
- What happened to the skills of the previous layer: obsolete, niche but well paid, or
  absorbed as background knowledge.
- Where the complexity went. Abstraction rarely removes complexity; name the new
  problems that appeared (leaky abstractions, performance debugging, dependency
  management, configuration, integration).
- Effect on the artifact: what kinds of software became possible or cheap, how program
  size changed, what got worse (bloat, reliability, security).
- Adoption timeline: invention to majority practice, and who stayed on the old layer
  and why (performance, regulation, installed base).
- Productivity claims at the time versus retrospective measurement. Where did the
  tenfold claims end up?
- Who captured the economic gain: programmers, employers, tool vendors, or end users.
- From whom the value was taken. Software's growth at each layer displaced work and
  revenue elsewhere (clerks and typists, typesetters, travel agents, bank tellers,
  retail, media, logistics). Name the sectors and occupations that shrank as this
  layer made new software cheap, with employment data where it exists.

## Cross-cutting questions

1. Demand effects. In which transitions did cheaper software produce far more software
   and more programmers (the Jevons pattern), and in which did it not? What decided it?
2. The failed or stalled abstractions (CASE, 4GLs, UML and model-driven architecture,
   visual programming, formal methods, expert systems). What do they have in common,
   and which of those traits does the LLM layer share?
3. The lost-layer problem. Once a layer becomes invisible, how long until practitioners
   can no longer debug it, and what did that cost (garbage collection pauses, ORM
   performance, framework magic, dependency chains)?
4. The entry-level pipeline. Did any transition remove the bottom rung of the career
   ladder, and how did the profession replace it?
5. Analogies and disanalogies with the agent layer. Every previous layer was
   deterministic, composable, specifiable, and verifiable from above. Natural-language
   programming was dismissed on exactly these grounds (Dijkstra, "On the foolishness of
   natural language programming", 1978). Assess, with evidence, whether these
   differences break the analogy or only change the timeline.
6. Who was right. For each transition, what did the best observers get right and wrong,
   and is there a pattern in which class of observer was right (practitioners,
   academics, vendors, economists)?
7. The capture radius. At each transition, how far outside the software industry did
   software reach? Track the sectors disrupted per layer, the share of economy-wide
   profit and employment moving to software and software-enabled firms, and the limits
   that held (regulation, licensure, liability, physical delivery, trust). Was the
   radius growing steadily, or in jumps tied to specific layers (PCs, the web, mobile,
   cloud)?
8. The long series. Build one longitudinal table, 1960 to 2024, of programmer headcount
   and median pay in constant dollars, with pay also expressed as a multiple of the
   national median wage and against two or three comparison professions (accountants,
   civil or electrical engineers, physicians or lawyers). Note every change in the
   occupation definition (programmer, systems analyst, software developer, software
   engineer) that breaks the series, and the inflation measure used. Do the same at
   lower resolution for one or two non-US markets if the data exists. The question to
   settle: across all previous abstraction jumps, did the real value of a programmer's
   labour go up or down, and when?

## Evidence rules

- Prefer primary sources: contemporary articles and proceedings, Turing lectures, books
  from the period, official labour statistics, retrospectives written by participants.
  Pop-history retellings only as pointers to primary material.
- Grade every substantive claim: `[measured]` (numbers plus method), `[first-hand]`
  (participant account), `[vendor]` (marketing or self-reported), `[opinion]`.
- Cite with title, author, date, and URL (ISBN for books). Do not invent sources. Where
  the history is contested, say who disagrees and why.
- Keep quotations verbatim and in context. Many famous "end of programming" quotes are
  truncated or misattributed; flag those cases.

## Output

A report of roughly 6,000–9,000 words, structured as:

1. A one-page timeline of the transitions.
2. One section per transition following the template. Write for a senior engineer who
   works today and has never seen a punched card: explain the pre-1995 working world
   concretely (how a program was written, submitted, debugged, and shipped; what a
   team looked like; what a programmer was paid relative to other professions).
3. A comparison table across transitions: years to majority adoption, what happened to
   the old-layer workers, predicted versus actual headcount effect, real-wage effect,
   where complexity moved, who captured the gain.
4. The longitudinal headcount and real-wage table from cross-cutting question 8, with
   a short reading of it.
5. Patterns that repeated every time, and patterns that did not.
6. The failed abstractions and what they share.
7. What this history does and does not license us to predict about the agent layer,
   with the disanalogies stated explicitly.
8. Full source list.
