# Research brief: Credible hypotheses about the future of software as an artifact (H2 2026)

## Why I am asking

Separate from what happens to the job, I want to know what happens to software itself
when the cost of producing it falls towards zero: what gets built, who builds it, what
it looks like, what it is made of, how it is paid for, and how it fails. Sibling briefs
cover the profession and the history of earlier abstraction jumps. This one is about
the artifact and its economics.

One thread matters especially. Software used to be bought: a perpetual licence, a box,
a binary the buyer kept. Then came maintenance contracts, subscriptions, and hosted web
applications where the buyer owns nothing and the vendor owns the state. Now agents
can decompile, reverse-engineer and reimplement existing software fast enough that
people are remaking commercial products on demand. I want to know where that
trajectory goes.

A second thread sits behind it. The value that accrued to software at every earlier
layer was taken from somewhere: it captured and disrupted markets in other sectors and
absorbed their jobs. Software as a service replaced processes inside companies. Agents
look able to replace the companies and professions themselves; a small team can run
agents as an architect, a law firm, or an accountancy. I want to know whether the
disruption radius really has jumped from processes to whole industries, where it
stops, and who pays for the gain this time.

## Who counts as a credible voice

Build the source list yourself; names below are examples, not a boundary. Rate each
voice on track record (public, dated, correct calls on earlier shifts), evidence base
(operates at scale, publishes data, runs studies), and incentive (sells models or
tools, sells software, invests, researches). Tag every claim with the speaker's
incentive; lab and platform leaders count, but as `[vendor]`. Example types:
practitioners and researchers who publish (Andrej Karpathy, Simon Willison, Geoffrey
Litt and Ink & Switch, Martin Fowler and the Thoughtworks radar authors, Bret Victor,
Leslie Lamport, Armin Ronacher), platform leaders (Satya Nadella, Dario Amodei, Sam
Altman, Jensen Huang) as `[vendor]`, investors and analysts (a16z, Benedict Evans,
Gartner, public-market analysts) as `[vendor]` or `[opinion]` by case, HCI and software
engineering researchers with published studies, and security researchers with incident
data. Exclude anonymous posts and influencer threads without data.

## Hypotheses to map

Find the strongest statement of each from a credible holder, and add hypotheses I have
missed. Where several people hold one, cite the two or three clearest.

- H1. Software becomes personal and disposable: generated on demand for one user or
  one task and thrown away; end-user programming finally arrives (malleable software,
  "vibe coding", "software for one").
- H2. The agent is the application: SaaS unbundles into data, APIs and tools that
  agents call; UI layers thin out or vanish; business logic migrates to the agent layer
  (the "SaaS is dead" argument, tool-protocol ecosystems, generative and just-in-time
  interfaces).
- H3. The counter-hypothesis: deterministic, human-legible code remains the artifact;
  LLMs are a faster way to produce conventional software; interfaces stay graphical and
  designed because conversation is a poor interface for most tasks.
- H4. Software 2.0 and 3.0: more of a system's behaviour lives in model weights and
  prompts rather than code; programs become specifications plus evals; the "LLM
  operating system".
- H5. Code volume explodes and quality falls: comprehension debt, duplication, security
  exposure, maintenance load, software nobody understands; a reliability crisis
  followed by a verification industry.
- H6. The business of software changes: seat-based pricing breaks, outcome- and
  usage-based pricing, margin compression, public-market repricing of SaaS, open-source
  sustainability under agent-generated contribution floods, app-store economics.
- H7. Languages and tooling adapt to the new author: convergence on the languages
  models know best, stricter type systems and constrained DSLs designed for agents,
  decline of niche languages, new languages built for machine authorship; or the
  opposite, language choice stops mattering.
- H8. Verification becomes the product: specs, property tests, proofs and evals are
  what humans write and own; software ships with evidence attached.
- H9. Distribution: software becomes more local, private and numerous (small models on
  device, everyone runs their own tools), or more centralised (a few platforms own the
  agent layer and therefore the software).
- H10. Security: software built by agents is attacked by agents; attack surface, supply
  chain and patch cadence change qualitatively.
- H11. Ownership flips again: agent-assisted decompilation, reimplementation and
  clone-on-demand make the application layer protected in law but trivially copyable
  in practice, so value moves to proprietary data, distribution, trust, hosted state
  and network effects; or the reverse, ownership and local-first software revive
  because anyone can regenerate a tool they control, and subscription software loses
  its grip.
- H12. The disruption radius jumps from processes to professions: software plus agents
  can substitute for entire knowledge-work firms (architecture, law, accounting,
  consulting, design, education, parts of medicine), so software engineers and
  agent-native startups can enter any expert industry and the software sector's share
  of profit and employment keeps rising at other sectors' expense; or the
  counter-hypothesis, that licensure, liability, insurance, physical delivery and
  trust hold the boundary roughly where SaaS left it, and the main effect is inside
  the sectors as productivity, not across them as capture.

For each: core argument and mechanism, strongest evidence as of H2 2026, strongest
counter-evidence, what the holder says would change their mind, and leading indicators
to watch over the next 24 months.

## Questions to answer

1. **What has measurably changed in the artifact already (2024 to 2026).** Volume of
   code produced, repository and package-registry growth, share of AI-authored code in
   public and private repositories, defect and vulnerability rates in AI-heavy code,
   app-store submission counts, number of new software products launched. Method and
   sample for each figure.
2. **The business of software.** What has happened to SaaS and software companies in
   public markets and private funding, which pricing models have actually shifted, and
   what credible commentators say the causes are.
3. **End-user and personal software.** Are non-engineers building and keeping software
   in meaningful numbers? Retention and continued-use data, not launch announcements.
4. **Interfaces.** Adoption and abandonment of conversational and generative interfaces
   versus conventional ones; what HCI research and product telemetry say.
5. **Languages and runtimes.** Language-share shifts attributable to agents, new
   languages or DSLs aimed at machine authorship, type-system adoption, and whether
   agents entrench incumbents.
6. **Ownership, licensing and cloning.** A short history of how software has been paid
   for and who owned it (perpetual licence, maintenance contracts, shrink-wrap EULA,
   subscription, hosted SaaS, freemium and app store, usage pricing), with what each
   shift did to vendors, buyers and lock-in. Then the 2025 to 2026 evidence on
   agent-assisted decompilation, reverse engineering and reimplementation: named cases
   of commercial products cloned with agents, vendor and legal responses (takedowns,
   lawsuits, terms changes, obfuscation), and how fast and how complete the clones
   were. State the legal position plainly: copyright protects expression not function,
   the clean-room doctrine, Google v. Oracle, anti-circumvention law, the EU
   reverse-engineering exceptions, and whether agent-made clones have been tested in
   court yet. Then what credible voices say this does to moats, pricing, open source,
   and the balance between owned and rented software over the next five years.
7. **Where the value comes from and how far it now reaches.** First the baseline:
   which sectors and occupations previous software waves took value and jobs from,
   and how much, with the limits that held. Then the 2025 to 2026 evidence on
   agent-native firms entering non-software industries: named cases in architecture
   and engineering, law, accounting and tax, consulting, design, education, health,
   finance and insurance; what they actually deliver end to end, what revenue and
   customers they have, and where they stopped (licensed sign-off, liability,
   physical work, regulation, procurement, customer trust). Ask whether the sign-off
   bottleneck is itself being automated or bought. Then the macro view: measured
   movement of profit, market value and employment toward software and agent-enabled
   firms, and what credible economists and investors say about who loses, how fast,
   and whether this is capture across sectors or productivity within them.
8. **Resolved and failed predictions.** Which 2023 to 2025 predictions about software
   itself have already failed or come true, and who made them?
9. **Consensus and disagreement.** Where do credible people agree despite different
   incentives? Where do they disagree sharply, and is it about facts, timelines, or
   values? What does each speaker class get systematically wrong?
10. **Leading indicators** for each hypothesis over the next 24 months.
11. **For someone building products:** which bets are safe under most hypotheses, and
   which are hostage to a single hypothesis being right?

## Evidence rules

- Prefer first-hand sources: the speaker's own essay, talk, paper, or data release;
  telemetry and surveys with stated methodology; peer-reviewed or preprint studies with
  reproducible setups; filings and earnings transcripts for market claims.
- Grade every substantive claim: `[measured]` (numbers plus method), `[first-hand]`
  (practitioner account, no numbers), `[vendor]` (marketing or self-reported),
  `[opinion]`, `[forecast]`.
- Quote predictions verbatim with the date. Note when a quote is commonly truncated or
  stripped of a qualifier.
- Cite with title, author or organisation, date, and URL. Do not invent sources. If a
  claim cannot be sourced, say so rather than fill the gap.

## Output

A report of roughly 5,000–8,000 words, structured as:

1. **Executive summary:** the consensus zone, the three sharpest disagreements, and the
   predictions already falsified.
2. **Hypothesis map table:** hypothesis, principal holders with credibility rating,
   mechanism, evidence for, evidence against, leading indicators.
3. **Findings per question 1–11**, each ending with the evidence grades used.
4. **Scorecard** of named 2023 to 2025 predictions against the H2 2026 record.
5. **Watch-list:** ten indicators, with the direction each hypothesis predicts for each.
6. **Full source list.**
