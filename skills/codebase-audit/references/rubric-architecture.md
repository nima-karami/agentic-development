# Rubric — architecture

The judge for this dimension checks the code against the repo's **declared** structure
(the intent ledger) and its **measured** coupling (the graph and history facts). A
violation exists only against a declared rule or a measured cost; otherwise it is an
authority conflict or taste.

Each row: what a finding looks like · how it is detected · severity guidance · where
enforcing it becomes over-engineering.

## Core rows

### A1 · Forbidden edge or layer violation
- **Finding:** an import crossing a declared boundary — domain → infrastructure, one
  feature reaching into another's internals, a shared package importing an app.
- **Detection:** mechanical once rules exist. Map files to components, diff edges
  against the allowed set. Writing the rules is judgment and is not the audit's job.
- **Severity:** zero tolerance for declared rules. A cold file is Low; the same edge in
  a top hotspot is High.
- **Over-engineering line:** inventing rules the repo never declared. That is an
  authority conflict, not a violation.

### A2 · Cycles where acyclic is intended
- **Finding:** top-level modules inside one strongly connected component.
- **Detection:** SCCs over the module graph; record cyclic-node count and the largest
  SCC; trend both.
- **Severity:** Medium to High between top-level modules. File-level cycles inside one
  module are tolerable.
- **Over-engineering line:** alarm on cycles at a level where the repo never intended
  acyclicity.

### A3 · Hotspot erosion
- **Finding:** a file that changes constantly and is also complex.
- **Detection:** churn × complexity over twelve months, rename-aware, bot and formatter
  commits removed. Relative: the top 5–10% of the repo.
- **Severity:** rarely a finding alone; it **ranks** the others. A violation in a
  hotspot outranks the same violation in a cold file.
- **Over-engineering line:** absolute churn targets.

### A4 · Hidden coupling
- **Finding:** two modules that change together in most commits with no static edge
  between them — a leaked concept or an implicit protocol.
- **Detection:** pairwise shared-commit ratio across module boundaries, bulk commits
  excluded; read the pair to name the shared concept.
- **Severity:** Medium; High when the pair spans a declared boundary.
- **Over-engineering line:** any fixed percentage cutoff. None is defensible; rank.

### A5 · Parallel abstractions
- **Finding:** two mechanisms for one concern — two HTTP clients, two error types, two
  state stores, two config paths, two loggers, two event buses.
- **Detection:** the inventory lists definitions and imports per concern class; the
  judge clusters by purpose and **confirms both do the same job** before reporting.
- **Severity:** Medium; High when call sites split roughly evenly (nobody knows which
  to use). Report it as an authority conflict when nothing declares the winner.
- **Over-engineering line:** calling two things duplicates before confirming the same
  responsibility; one-per-concern where a decision record allows two.

### A6 · One concept, several names
- **Finding:** Customer / Account / User meaning the same thing across modules;
  identical shapes under different names.
- **Detection:** judgment, guided by identifier frequency and type clustering, against
  a glossary if the repo has one.
- **Severity:** Medium when it crosses module boundaries.
- **Over-engineering line:** renaming legitimate bounded-context vocabulary — the same
  word meaning different things in two contexts is correct.

### A7 · Hubs
- **Finding:** a shared module most of the repo imports, so every change ripples.
- **Detection:** fan-in and fan-out per module, ranked by repo percentile.
- **Severity:** used to rank exposure; a finding only when the hub also churns.
- **Over-engineering line:** treating benchmark quantiles as limits.

### A8 · Docs disagree with code
- **Finding:** an accepted decision record, architecture note or agent instruction file
  describes structure the code no longer has — or the code has structure no source
  describes.
- **Detection:** the three-architectures table from the intent ledger.
- **Severity:** High for agent instruction files (agents act on them); Medium for
  prose docs.
- **Over-engineering line:** requiring a decision record for every small choice.

## Front-end rows

Judge against the repo's declared front-end structure, not a generic aesthetic. Most
front-end guidance is convention; pick the one the repo declares.

### AF1 · Upward or deep import
- **Finding:** shared UI importing a feature; a deep import past a feature's public
  entry; a barrel file hiding a cycle.
- **Detection:** boundary lint over the declared layer model; cycle detection through
  barrels.
- **Severity:** Medium; High in a design-system package.
- **Over-engineering line:** banning intentional entry-point barrels.

### AF2 · State ownership
- **Finding:** server data mirrored in a global store and a query cache; filters or
  tabs held only in memory; effect-copied state; modal flags in a global store.
- **Detection:** build a **state-ownership matrix** — rows are concepts, columns are
  server cache, URL, global store, component, persisted. A row with several marks is
  not automatically wrong; it is where the judge demands a source-of-truth story.
- **Severity:** Medium; High when two copies can disagree on screen.
- **Over-engineering line:** moving every bit of UI state into the URL.

### AF3 · Fetch-path sprawl
- **Finding:** a query library, raw fetch calls and store-side requests coexisting;
  query keys built in many places; invalidation scattered through UI code.
- **Detection:** inventory call sites by mechanism; find who builds keys and who
  invalidates.
- **Severity:** Medium.
- **Over-engineering line:** forcing a query library onto a one-screen tool.

### AF4 · Design-system bypass
- **Finding:** raw primitives where a system component exists; hard-coded color,
  spacing or z-index; forked components; two component families for one role.
- **Detection:** component-usage scan plus token lint.
- **Severity:** Medium; High in a shared library.
- **Over-engineering line:** policing one-off pages the design system never covered.

### AF5 · Route components doing everything
- **Finding:** a route file that fetches, mutates, transforms and renders.
- **Detection:** responsibility count per route file, crossed with churn.
- **Severity:** Low; Medium in a hotspot.
- **Over-engineering line:** splitting a small, cold route into five files.
