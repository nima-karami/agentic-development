# Research brief: Credible hypotheses about the future of software engineering as a profession (H2 2026)

## Why I am asking

By late 2026 a majority of new code in many organisations is written by coding agents.
I want a map of what credible people think happens next to the job of software
engineer: headcount, skills, the career ladder, and how the work is done day to day. I
do not want a crowd survey. I want the hypotheses held by people with a track record,
first-hand data, or recognised expertise, each stated precisely enough to be wrong,
with the evidence for and against it as of October 2026. A sibling brief covers the
history of earlier abstraction jumps; another covers the future of software as an
artifact.

## Who counts as a credible voice

Build the source list yourself; the names below are examples, not a boundary. Rate
each voice on three things and show the rating:

- Track record: did they call the web, mobile, cloud, or the 2023 to 2025 agent shift
  correctly, in public, at the time?
- Evidence base: they operate at scale, publish data, run studies, or employ many
  engineers.
- Incentive: sells models or tools, employs engineers, invests, researches, teaches.
  Tag every claim with the speaker's incentive. Lab CEOs and tool vendors count, but
  as `[vendor]`.

Example types: practitioners who publish data or detailed first-hand accounts (Simon
Willison, Gergely Orosz, Kent Beck, Martin Fowler and the Thoughtworks radar authors,
Steve Yegge, Armin Ronacher, Mitchell Hashimoto, Charity Majors); researchers (Andrej
Karpathy, Leslie Lamport, the authors of the METR developer studies, DORA, Erik
Brynjolfsson, David Autor, Daron Acemoglu); lab and platform leaders (Dario Amodei, Sam
Altman, Satya Nadella, Jensen Huang, Mark Zuckerberg, GitHub leadership) tagged
`[vendor]`; forecasters with scoring records (the AI 2027 authors, Metaculus and
superforecaster aggregates) tagged as forecasts. Exclude anonymous posts, influencer
threads without data, and recruiter or bootcamp content.

## Hypotheses to map

Find the strongest statement of each from a credible holder, and add hypotheses I have
missed. Where several people hold one, cite the two or three clearest.

- H1. Engineers become orchestrators and reviewers of agents; headcount roughly
  stable; output per engineer rises sharply.
- H2. Demand for engineers falls substantially; junior hiring collapses first; "the
  last generation of programmers".
- H3. Jevons: cheaper software raises demand for software and for engineers; the role
  changes but the population grows.
- H4. Bifurcation: deep systems engineers and product-minded generalists both thrive;
  the middle (feature implementers) hollows out.
- H5. The core skill moves to specification and verification: tests, types, formal
  specs and evals become the human-owned artifact; a formal-methods revival.
- H6. Modest change: measured productivity gains are small or negative in realistic
  settings (the METR 2025 randomised trial, DORA findings); the tooling becomes a
  better IDE and the profession adjusts incrementally.
- H7. Solo and tiny teams build what used to take departments; the one-person company
  at scale.
- H8. Skill atrophy and comprehension debt: the profession loses the ability to
  understand its own systems; a quality and security reckoning follows.
- H9. The craft becomes less attractive: enjoyment, status, and entry into the field
  decline, visible in survey data.

For each: core argument and mechanism, strongest evidence as of H2 2026, strongest
counter-evidence, what the holder says would change their mind, and leading indicators
to watch over the next 24 months.

## Questions to answer

1. **Labour market facts to date.** Engineering job postings, new-graduate employment
   and unemployment, layoffs attributed to AI, computer science enrolment, by region.
   Compensation in real terms: inflation-adjusted pay for software engineers 2015 to
   2026 by level and region, as a multiple of the median wage, with the deflator
   stated; separate base pay from equity so that stock moves do not masquerade as
   labour-market signal. Separate measured data (government statistics, job-board data,
   the Stanford "Canaries in the Coal Mine" style studies and their critiques) from
   claims about the data.
2. **Productivity evidence.** Controlled studies, telemetry at scale, vendor-reported
   figures, and the gap between them. Why do self-reports and randomised trials
   disagree, and has that gap narrowed with newer tooling?
3. **What has already changed in practice** at AI-forward organisations: team shapes,
   reviewer-to-agent ratios, spec-first workflows, roles that disappeared or were
   redefined (QA, junior developer, front-end specialist, DBA, engineering manager).
4. **Resolved and failed predictions.** Which hypotheses have been partly resolved since
   2024, and in which direction? Which prominent 2023 to 2025 predictions have already
   failed, and who made them?
5. **Consensus and disagreement.** Where do credible people agree despite different
   incentives? Where do they disagree sharply, and is the disagreement about facts,
   timelines, or values?
6. **Systematic bias by speaker class.** What does each class (lab leader, tool vendor,
   practitioner, economist, forecaster) tend to get wrong given its incentives and
   vantage point?
7. **Forecasts with numbers.** Published probabilistic forecasts (employment, share of
   tasks automated, timelines) from forecasters with scoring records, and how earlier
   forecasts from the same sources have resolved.
8. **Career investment.** For a senior engineer with a front-end and product background
   deciding where to invest the next three years: which skills does the credible
   consensus say are rising, which are falling, and where do credible voices disagree?

## Evidence rules

- Prefer first-hand sources: the speaker's own essay, talk, paper, or data release;
  survey reports with stated methodology; peer-reviewed or preprint studies with
  reproducible setups.
- Grade every substantive claim: `[measured]` (numbers plus method), `[first-hand]`
  (practitioner account, no numbers), `[vendor]` (marketing or self-reported),
  `[opinion]`, `[forecast]`.
- Quote predictions verbatim with the date. Note when a quote is commonly truncated or
  stripped of a qualifier.
- Prediction accountability: when a speaker has made dated predictions before, say
  whether they came true.
- Cite with title, author or organisation, date, and URL. Do not invent sources. If a
  claim cannot be sourced, say so rather than fill the gap.

## Output

A report of roughly 5,000–8,000 words, structured as:

1. **Executive summary:** the consensus zone, the three sharpest disagreements, and the
   predictions already falsified.
2. **Hypothesis map table:** hypothesis, principal holders with credibility rating,
   mechanism, evidence for, evidence against, leading indicators.
3. **Findings per question 1–8**, each ending with the evidence grades used.
4. **Scorecard** of named 2023 to 2025 predictions against the H2 2026 record.
5. **Watch-list:** ten indicators, with the direction each hypothesis predicts for each.
6. **Full source list.**
