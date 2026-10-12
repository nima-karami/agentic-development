# Auditing the Architecture of a Mostly Agent-Written Codebase

## Ten-line answer

Recover the architecture from **code, build metadata, imports, runtime entry points, tests, CI, and history before reading the prose as truth**; this is the lesson of architecture-reconstruction and reflexion-model work since the 1990s. citeturn0search0turn0search1  
Represent the result as dependency graphs at several granularities, then compare those graphs with separately extracted architectural claims from ADRs, architecture notes, structural tests, and agent instruction files. citeturn0search0turn2search0  
Treat explicit invariants—“domain must not import UI”, “features may not import each other”, “these CI jobs are required”—as **zero-tolerance constraints**, while treating metrics such as fan-out, size, churn, and complexity as diagnostic evidence rather than laws. citeturn15view0turn12search0  
Look hardest where several signals intersect: a highly changed module that also violates boundaries, participates in cycles, co-changes with distant modules, has weak tests, or contains parallel abstractions is much more persuasive than any smell alone. citeturn0search2turn22view0  
Audit gates as versioned architecture too: diff CI configuration, lint/type settings, suppressions, exclusions, skipped tests, allowed failures, and the equivalence of local and CI commands against the previous baseline. citeturn9search9turn9search3  
Measure whether tests constrain behaviour with **targeted mutation testing and extreme mutation**, not coverage or assertion counts alone; large-scale industrial evidence supports mutating changed, covered, non-trivial code rather than everything. citeturn8search0turn8search1  
For front ends, audit **ownership of each piece of state**, server-cache ownership, URL/navigation state, feature boundaries, routing, and design-system escape hatches; duplicated state ownership is a particularly useful erosion signal. citeturn10search0turn10search8turn10search2  
For bloat, mechanically find duplication, dead exports/files, one-use abstractions, pass-through layers and outlier size/complexity, but require judgment before calling them waste because each can have a legitimate boundary or migration purpose. citeturn15view0turn24search2  
Do **not** assume that “AI code duplicates more” or that all agent-written code has one characteristic failure mode: 2026 evidence supports increased complexity/quality-warning risk in some settings, while a small clone-genealogy study actually found most clones in its sample were human-introduced. citeturn23search6turn23search2  
Run deterministic extraction first, model interpretation second, human adjudication for high-severity findings last; preserve every metric, graph, rule, finding anchor, tool version, and scope so the next audit measures **drift**, not merely re-renders opinions. citeturn17search7turn19view1

**Evidence labels used below:** **Established** means supported by mature practice and/or multiple peer-reviewed studies; **Emerging** means recent empirical evidence with material scope limitations; **Opinion** means the recommended audit design is a synthesis rather than a validated universal standard.

## What the audit is actually trying to recover

The key conceptual move is to maintain **three architectures rather than one**:

1. the **observed architecture** reconstructed from the repository;
2. the **claimed architecture** reconstructed from documentation and policies; and
3. the **enforced architecture** embodied in builds, lint rules, structural tests, package boundaries, and CI.

That separation prevents the most common brownfield mistake: assuming either “the code is the specification” or “the ADR is the specification.” In a mixed-style codebase, both can be wrong.

Murphy, Notkin and Sullivan's 1995 *Software Reflexion Models* is still the most directly applicable method. The engineer specifies a conceptual architecture, maps implementation entities to that model, and the analysis classifies observed relations as **convergences** with the model, **divergences** from it, or **absences** where an expected relationship is not found. Their case studies demonstrated that useful architectural views could be produced from substantial existing systems without first understanding every line. citeturn0search0

Ducasse and Pollet's 2009 survey of software-architecture reconstruction generalised the point: architecture is rarely present as one recoverable artefact; reconstruction combines source artefacts, tools, architectural expertise, and domain/business knowledge. Human knowledge remains essential because extraction can reveal dependencies but not necessarily their architectural meaning. citeturn0search1

### A practical recovery model

For an audit in 2026, I would make the basic graph:

`node = deployable / workspace / package / feature / module / file / symbol`

`edge = static import | build reference | runtime registration | inheritance | call | data/schema dependency | test-only dependency`

Do **not** collapse these edge types prematurely. A static import cycle, a DI-container relationship, a test dependency, and a route registration are architecturally different things even when a generic graph tool can represent all four.

Start with declared structure where available—packages, workspaces, Gradle/Maven modules, .NET projects, Nx projects, build targets—then descend to directories/files/symbols. Architecture tests can make parts of the graph directly enforceable: ArchUnit, for example, provides Java rules over classes/packages, layers, dependencies and cycles; in JavaScript/TypeScript, dependency-cruiser supports dependency rules and cycle/orphan detection, while Nx's module-boundary linting can constrain imports according to project tags. These are tool-capability statements from official documentation, not evidence that any one tool is superior. citeturn2search0turn2search1turn2search8

The historical graph is equally important. Gall, Hajek and Jazayeri's 1998 work showed that entities that repeatedly change together can reveal **logical coupling** not visible in static dependencies; their industrial case study used release history from a very large telecommunications system. Cross-module co-change is therefore evidence that the nominal decomposition may not match the change structure of the system. citeturn0search2 Later research has also linked change coupling with defect information, although it does not establish a universal co-change cutoff. citeturn1search3

Recent hotspot work reinforces the value of history while showing why naïve churn counts are dangerous. A 2026 MSR study of 91 active repositories found recurring line-level hotspot patterns and, importantly for agent-heavy repositories, found that automated accounts accounted for a large fraction of hotspot edits in its sample; the authors explicitly warn that automation can obscure meaningful maintenance churn. citeturn22view0 **Therefore split human, agent, bot/dependency-update, generated-code and mechanical-formatting changes where provenance permits it.**

### Comparing code with documentation without inventing an authority

For each architectural document—ADR, architecture note, `AGENTS.md`-style instruction file, package README, coding-agent rule file, diagram, structural test—extract atomic claims such as:

> `payments.domain` must not depend on `payments.web`.

> Feature packages communicate through exported public APIs only.

> Remote server state belongs to the query/cache layer, not the global UI store.

Then give each claim metadata:

| Claim metadata | Why it matters |
|---|---|
| Scope | A rule for `apps/web` should not be inferred to govern backend packages. |
| Status | “Accepted”, “superseded”, “experimental” and “legacy” mean different things. |
| Date / last confirmation | A 2021 ADR conflicting with an explicit 2026 migration may be stale. |
| Enforcement | A passing architecture test is stronger evidence of active policy than forgotten prose, although it may itself be obsolete. |
| Exceptions | Temporary migration seams should not automatically become erosion findings. |
| Evidence of use | Current imports, tests, code-generation templates and review rules help establish whether a convention is actually alive. |

This precedence scheme is **Opinion (2026)** rather than a published standard. In particular, I would **not** automatically declare the most common code style authoritative. In brownfield code, prevalence can simply mean “the old architecture is larger.” When two plausible conventions conflict and neither has explicit governance, report an **authority conflict** rather than an architecture violation.

The final drift record should be reflexion-model-like:

`claim → observed entities → observed edge(s) → convergence/divergence/absence → evidence anchors → first seen → current delta`

That makes architecture drift reviewable rather than rhetorical. The conceptual foundation is established by the 1995 reflexion-model work; applying the same machinery to ADRs and agent instructions is the recommended 2026 adaptation. citeturn0search0

## A step-by-step audit method

The most trustworthy design is **deterministic extraction → evidence bundles → explicit rubric → model judgment → human adjudication**, rather than asking an LLM to “review the repo for architectural problems.”

That ordering matters because repository-scale LLM review remains noisy. In the 2026 peer-reviewed SWR-Bench study of 1,000 real-world pull requests with repository context, the best evaluated code-review configuration reached only 19.38% F1; its precision was 16.65%, while four of the five automated-review approaches studied had precision below 10%. Those numbers concern PR review, not whole-codebase architecture auditing, so they cannot be transferred directly, but they are a strong warning against treating free-form LLM findings as ground truth. citeturn17search2turn17search8 RepoProbe, an architecture-aware repository-comprehension benchmark accepted at ASE 2026, likewise reports a gap between fluent answers and evidence-grounded technical correctness and argues for decomposing answers into atomic, checkable items rather than relying on opaque scalar judgment. citeturn17search7

| Audit stage | Inputs | Deterministic work first | Model / semantic work | Output | Human judgment required |
|---|---|---|---|---|---|
| **Scope and freeze** | Commit SHA, build environment, supported applications, generated/vendor exclusions | Record revision; enumerate languages, packages, workspaces, deployables and tool versions | None | Reproducible audit manifest | Confirm that excluded code really is outside architectural responsibility |
| **Recover declared structure** | Build files, package manifests, workspace definitions, entry points | Extract package/project graph, static imports, aliases, public exports, runtime registrations where statically knowable | Explain unusual graph regions only after extraction | Observed architecture graph | Decide correct architectural granularity |
| **Recover intended structure** | ADRs, architecture docs, agent instructions, architecture tests, lint configs | Parse statuses, dates, scope and existing executable rules | Convert prose to atomic candidate constraints | Claim/constraint ledger | Resolve genuinely conflicting authorities |
| **Reflexion comparison** | Observed graph + claim ledger | Map code nodes to architectural components; compute convergent/divergent/absent edges | Suggest mappings where names do not align | Architecture-drift matrix | Validate mappings and allowed exceptions |
| **Evolution analysis** | Git history | Churn, authorship class, file/module co-change, rename-aware histories, hotspot ranks | Explain likely conceptual reasons for suspicious clusters | Change-coupling and hotspot evidence | Distinguish architectural coupling from deliberate coordinated change |
| **Erosion scan** | Graph + source metrics | SCCs/cycles, forbidden edges, fan-in/out, unused files/exports, duplication, complexity/size distributions | Detect concept duplication, parallel abstractions and vocabulary fragmentation | Ranked candidate findings | Required for semantic smells |
| **Gate audit** | CI, compiler/type, test, lint, coverage and mutation configs, prior baseline | Canonicalise and diff policy; count skips/suppressions/exclusions and allowed failures | Explain consequences of policy changes | Gate-drift report | Decide whether a relaxation was approved/temporary |
| **Test-strength audit** | Tests + production code + risk ranking | Coverage eligibility, extreme mutation, sampled/full mutation on risk-selected code | Group surviving mutants by behavioural gap | Test-strength map | Triage equivalent/unimportant mutants |
| **Front-end ownership audit** | Routes, state stores, query/cache calls, component graph, design system | Inventory each mechanism and its import/use graph | Classify state/ownership and duplicate concepts | Front-end architecture findings | Framework/domain exceptions |
| **Adjudication** | All evidence bundles | Ensure every finding has file/symbol/config/commit anchors | Model states claim, consequence, alternatives and confidence | Candidate report | Human accepts/rejects all high-impact semantic findings |
| **Prioritisation** | Accepted findings + churn/risk data | Attach reach, affected modules, frequency, baseline trend | Draft remediation units | Ordered task list | Product/engineering owner selects trade-offs |
| **Baseline update** | Current measurements | Persist raw metrics, graph hashes, policy manifest and accepted findings | Summarise drift | Next-audit baseline | Confirm intentional architectural changes |

A finding should have a rigid schema, for example:

```text
Finding:
  category: architecture | gate | test-strength | bloat | front-end
  claim: one falsifiable sentence
  evidence:
    - path:symbol or config:key
    - dependency/co-change edge
    - policy/ADR claim
    - historical observation
  status: verified | likely | hypothesis
  severity: critical | high | medium | low
  confidence: high | medium | low
  first_seen: baseline or commit/window
  why_it_matters: concrete maintenance/runtime/change risk
  counter_evidence: ...
  remediation: smallest architectural move, not rewrite
```

The separation of **severity from confidence** is important. “This appears to be a second state mechanism” can be high impact but low confidence; it should not enter a P0 task queue until adjudicated. Conversely, “the required type-check CI job disappeared” can be mechanically certain even before anyone knows how many latent errors it permits.

For a repository too large for model reading, **scan the whole repository mechanically and sample semantic review**, rather than sampling both. The semantic sample should deliberately include:

- every new structural-policy violation and every newly enlarged cyclic SCC;
- high-change/high-complexity intersections;
- cross-module co-change clusters;
- files with concentrated suppressions, skips or weak mutation results;
- runtime entry points and shared infrastructure;
- candidate duplicate abstractions; and
- a random or low-risk control sample so the auditor does not “prove” that the entire repo is bad merely by reading only the worst files.

That sampling design is **Opinion (2026)**. It is consistent with the broader empirical finding that maintenance problems are heavily concentrated and with 2026 hotspot research, but there is no validated universal “read X% of files” rule. citeturn22view0

## Erosion and bloat signals: what is evidence, what is a heuristic

The most important distinction in this table is between a **constraint threshold** and a **statistical threshold**. If a repository explicitly declares “no dependencies from domain to UI,” one violating edge is enough. There is no need to wait until 5% of edges violate it. In contrast, a method being 45 lines long is not, by itself, proof of bad architecture.

The best-known empirical threshold work here is Alves, Ypma and Visser's 2010 benchmark of 100 Java and C# systems. Instead of asserting magic numbers, they derived thresholds from code-volume quantiles. With tests and generated code excluded, their 70/80/90% cutoffs were **6/8/14 for McCabe complexity, 30/44/74 LOC for method size, 10/22/56 for file fan-in, and 29/42/73 methods per file**; for number of parameters, 80/90/95% cutoffs were **2/3/4**. These are useful comparative triage points for similar OO systems, not universal failure limits. The paper itself stresses sensitivity to metric definition, tool and analysis scope. citeturn15view0turn15view3

| Signal | What it detects | Detection | Evidence strength | Defensible threshold / interpretation |
|---|---|---|---|---|
| **Forbidden dependency / layer violation** | Code contradicts a declared dependency direction or ownership boundary | **Mechanical** once modules and rule are defined | **Established**: reflexion models and executable architecture rules directly model this class of divergence. citeturn0search0turn2search0 | **Zero** is defensible *only when the repo declares the relation forbidden*. Otherwise it is a candidate design question, not a violation. |
| **Dependency cycle / SCC** | Loss of independent change/deployment/understanding; mutually dependent modules | **Mechanical** graph SCC detection; **judgment** on granularity and acceptability | **Established signal, contextual interpretation.** Empirical cycle-remediation work in 2023 found that surrounding design context matters to untangling cycles. citeturn0search3 | Zero only for a graph intended to be acyclic. Record **cyclic node count, SCC count and largest SCC**, not merely “cycle present.” No universal defect threshold. |
| **Unstable dependency** | A relatively stable/high-incoming-dependency component depending on a volatile/high-outgoing one | **Mechanical metric, judgment on architecture** | **Established heuristic**, originating in package-design metrics; not a validated universal quality boundary. citeturn12search0 | Martin's instability `I = Ce/(Ca+Ce)` and abstractness/main-sequence constructs are diagnostic; their original presentation explicitly treats the standard as heuristic rather than something to conform to unconditionally. citeturn12search0 |
| **High fan-out** | A module knows about many other modules, often indicating broad responsibility or orchestration leakage | Mechanical | **Moderate**; useful comparatively, weak as standalone defect predictor | Prefer repository percentiles/trend. No defensible universal cutoff located. |
| **High fan-in** | Central dependency / change blast radius; alternatively a healthy stable core | Mechanical | **Moderate** | Alves et al. 2010 derived file fan-in cutoffs **10/22/56** at 70/80/90% benchmark code-volume quantiles for their Java/C# corpus—not an “error above 56” rule. citeturn15view1 |
| **High abstractness + instability mismatch** | Packages that are rigid in an undesirable way according to the Stable Abstractions heuristic | Mechanical + judgment | **Heuristic / folklore-adjacent** rather than externally validated threshold | Track over time if the project's design style makes it meaningful; do not gate on a universal “distance from main sequence.” citeturn12search0turn12search2 |
| **Cross-module co-change** | Hidden logical dependencies and decomposition that disagrees with actual change patterns | Mechanical history analysis; judgment to explain | **Established signal** since Gall et al. 1998; later work relates change coupling to defects. citeturn0search2turn1search3 | No universal Jaccard/lift threshold. Rank within the repo; exclude bulk renames, generated updates and bots before interpreting it. |
| **Hotspot: high churn plus difficult structure** | Places where maintenance pressure and technical difficulty intersect | Mechanical ranking + judgment | **Established general idea; emerging fine-grained method** | A 2026 MSR study operationalised candidate hotspot files as `> μ+3σ` modifications **and** more than one change/month of project lifetime; this was tuned for 91 very active repositories and is not a universal gate. citeturn22view0 |
| **Duplicate code / clone families** | Multiple maintenance sites for the same implementation | Mechanical clone detector + judgment | **Established maintainability concern**; no universal safe percentage | Trend duplication and, more importantly, clones crossing architectural boundaries or repeatedly co-changing. Tools such as NiCad are used in empirical clone research; jscpd is a current multi-language detector, but its product claims should not be treated as independent evidence. citeturn23search2turn24search3 |
| **Parallel abstraction** | Two clients, repositories, error hierarchies, event buses, caches or state mechanisms solving one concern | Mechanical inventory can find candidates; conclusion is **judgment-heavy** | **Strong practitioner signal, weak threshold evidence** | No numeric threshold. “Two” is only a problem after establishing they have the **same conceptual responsibility** rather than different bounded contexts or an intentional migration. |
| **One concept under several names** | Conceptual fragmentation that causes duplicate policy and hard-to-find behaviour | Search/type/schema clustering plus semantic judgment | **Judgment-heavy** | No threshold. Stronger when differently named types/functions repeatedly map to the same data/schema/operations and co-change. |
| **Method complexity** | Difficult control flow, testing and comprehension | Mechanical | **Empirically benchmarked but context-dependent** | Alves et al. 2010: McCabe **6/8/14** at 70/80/90% code-volume quantiles. The famous “10” cutoff is older expert practice, not a universal scientific boundary; the 2010 study was explicitly motivated by inadequacy of such decontextualised limits. citeturn15view0 |
| **Long method** | Too many decisions/responsibilities in one unit—or simply a cohesive linear algorithm | Mechanical candidate, judgment for smell | **Moderate empirical evidence** | A 2022 study of roughly 785,000 Java methods across 49 OSS projects reported that methods up to **24 SLOC** were less maintenance-prone than longer methods; this is Java-specific observational evidence, not a cross-language gate. citeturn3search2 |
| **Large method/file** | Potential low cohesion, mixed responsibilities and expensive navigation | Mechanical | **Moderate** | Alves 2010 method-size cutoffs: **30/44/74 LOC** at 70/80/90% benchmark quantiles; methods-per-file **29/42/73**. Treat them as ranking aids. citeturn15view3 |
| **One-implementation interface / unused extension point** | Speculative generality | Mechanical candidate + semantic judgment | **Opinion / smell heuristic** | No defensible count threshold. One implementation alone is insufficient: ports/adapters, testing seams and stable cross-package contracts can legitimately have one implementation. |
| **Pass-through wrapper / shim chains** | Indirection with no clear semantic, policy or ownership value | Mechanical call/AST pattern + judgment | **Opinion** | Count wrapper depth and change frequency, but report bloat only when the layer adds neither abstraction stability, translation, security/telemetry policy nor migration value. |
| **Dead exports/files/dependencies** | Code that expands search space and maintenance surface without being reachable | Mechanical, with dynamic-language caveats | **Strong mechanical signal where reachability is statically reliable** | Zero is a reasonable *goal*, not always a gate. Reflection, framework registration and code generation create false positives. Knip's current JS/TS tooling, for example, builds a project-level usage graph for unused exports/files/dependencies; its findings still require review. citeturn24search2turn24search6 |
| **Defensive-code bloat** | Repeated validation, impossible fallbacks, duplicated exception handling and invariant checks at many layers | Candidate patterns mechanical; **meaning entirely contextual** | **Opinion** | No LOC or branch threshold. Require evidence that an upstream invariant already guarantees the condition and that the extra branch is not a fault-containment boundary. |
| **Comment noise** | Narrative surface larger than the code's real semantics, stale or restated comments | Semantic comparison | **Weak signal** | No credible density threshold. High severity only for comments/docstrings that actively contradict behaviour or architectural policy. |
| **Suppression density** | Static/type/lint policy gradually bypassed instead of satisfied | Mechanical | **Emerging empirical support** | Track absolute count, newly added suppressions and age by rule/module; use baseline drift, not a universal density limit. Research published in 2025 specifically studies the persistence and consequences of suppressed static-analysis warnings. citeturn9search3 |

Two general lessons follow.

First, **size is not synonymous with bloat**. A 200-line parser implementing one cohesive grammar can be architecturally better than the same behaviour fractured through twelve forwarding objects. Empirical work on Long Method detection has shown why simple smell rules need caution: simple individual metrics can generate substantial misclassification, while combined contextual models do better. citeturn3search3

Second, architectural erosion is much more credible when **orthogonal evidence agrees**. A large file alone is weak evidence. A large file that is also a hotspot, has high cross-module co-change, sits at the centre of a dependency SCC, owns two state mechanisms and has weak mutation results is an excellent audit target. That conjunction-based interpretation is **Opinion (2026)**, built on the independent evidence bases for structural dependencies, change coupling and hotspots. citeturn0search2turn22view0

## Gate decay and test strength

Treat the repository's quality gates as an **architectural control plane**. A codebase can look structurally unchanged while its effective engineering policy quietly collapses because the compiler runs on fewer paths, a CI check becomes optional, or a mutation/coverage threshold stops executing.

Pipeline configuration deserves the same longitudinal treatment as source code. Vassallo and colleagues' 2020 work on continuous-delivery pipeline smells analysed 5,312 GitLab projects; their detector achieved 87% precision and 94% recall in its evaluation, and the study included patterns such as “fake success”, where pipeline configuration can allow problematic jobs to cease constraining delivery. citeturn9search9 That does not prove every `allow_failure` is debt; it does establish that CI configuration contains maintainability-relevant anti-patterns worth auditing.

### Gate-decay checklist

| Compare current audit with baseline | What constitutes a suspicious change |
|---|---|
| **Required CI job set** | Type-check, lint, unit, integration, architecture, build or other previously required jobs disappear, become conditional, are renamed without equivalent enforcement, or stop blocking merge |
| **Failure semantics** | `allow_failure`, `continue-on-error`, ignored exit codes, broad retries, warning-only modes, soft quality gates |
| **Compiler/type policy** | Strictness flags disabled; error classes skipped; project references omitted; directories moved outside checked roots |
| **Lint/static-analysis policy** | Rules disabled/downgraded; category changes from error to warning; new ignore patterns; inline suppression count/age rising |
| **Test discovery** | New skip/ignore/quarantine annotations; directories omitted; patterns narrow; package test commands no longer invoked |
| **Coverage/mutation policy** | Threshold lowered/removed; exclusions grow; changed-code testing disappears |
| **Architecture checks** | Structural-test suites stop running, boundary rules are frozen indefinitely, or exemptions accumulate |
| **Path filters** | CI no longer runs when files that can affect behaviour change |
| **Local vs CI commands** | `make test`, package scripts or documented developer commands invoke a different test/type/lint graph from CI |
| **Tool/config versions** | Migration changes defaults or silently stops loading old configuration |
| **Generated and vendor exclusions** | New exclusions accidentally cover hand-written production code |
| **Baseline files** | “Accepted violations” grow without expiry, owner or reason |
| **Branch/repository policy** | Required status checks or merge protections change outside the source-controlled pipeline where the platform exposes that information |

The recommended implementation is to generate a **canonical gate manifest** every audit:

```text
gate
  id
  command
  working-directory
  include/exclude paths
  required/blocking?
  triggers
  dependency jobs
  failure policy
  tool/config version
  relevant thresholds
```

Then diff the manifest, not just YAML text. That prevents a CI migration from appearing as thousands of irrelevant textual changes while concealing one important semantic change. This normalised-manifest approach is **Opinion (2026)**; it operationalises the kind of pipeline smells studied empirically rather than relying on a particular CI vendor. citeturn9search9

Suppressions should receive their own debt ledger. A 2025 empirical study of suppressed static-analysis warnings reinforces that suppressions can hide genuine issues and persist as maintenance artefacts, so count additions, removals, age, rule and affected module—not merely the current total. citeturn9search3

### An affordable test-strength method

Coverage answers **“did a test execute this line?”** Mutation testing asks **“would the test notice a plausible behavioural change?”** The distinction is central. Official PIT and Stryker documentation describe the basic mechanism: inject code changes (“mutants”), run the tests, and classify a mutant as killed when tests fail or surviving when they do not. citeturn24search4turn24search5

The strongest industrial affordability evidence is Google's 2018 mutation-testing deployment. Google did not indiscriminately mutate every statement in the monorepo: its system focused on code affected by changes, excluded uncovered and unsuitable (“arid”) lines, and used sampling/selection to integrate mutation findings into normal review. The reported deployment covered thousands of engineers and more than a million generated mutants, illustrating that targeted mutation can operate at very large scale. citeturn8search0

A practical periodic audit can therefore use this funnel:

**Cheap screen:** calculate ordinary coverage only to identify code that cannot possibly have strong tests. Do not score covered code as “tested well.”

**Extreme mutation:** on important covered code, replace or remove whole method effects where the language permits. Research on **pseudo-tested methods** shows that code can execute under tests while tests still pass when the method's behaviour is essentially removed; a study across 21 projects found these methods had substantially weaker conventional mutation results. citeturn8search1

**Targeted regular mutation:** run richer mutations on:
- high-churn modules;
- architecture boundaries;
- central business logic;
- modules implicated by incidents;
- code with newly relaxed gates;
- code changed materially since the last full audit.

**Incremental reuse:** cache prior results where the mutation framework safely supports it. PIT, for example, currently offers history-based incremental analysis for large codebases, while explicitly documenting the assumptions and possible errors introduced when dependency changes are not fully considered. citeturn24search1

**Human triage:** review surviving mutants in high-risk areas. Equivalent or intentionally untested implementation details make a raw “100% mutation score” an undesirable universal target.

The audit should retain at least three test-strength figures: **eligible code with no tests**, **pseudo-tested/extreme-mutant survivors**, and **regular mutation kill rate for the fixed risk-selected sample**. Keep the sampled population stable enough across audits that the trend is meaningful.

Do **not** make assertion density a major quality gate. Assertion counts say little about whether assertions encode the right behavioural distinctions, and mutation testing directly tests the relevant property. Assertion density can still identify suspicious zero-assertion patterns for investigation, but it is an input to review, not an architecture health score. citeturn8search3

## Front-end architecture needs its own audit

A front end is particularly susceptible to architecture erosion because the same concept can exist simultaneously in the router, a query cache, a global store, local component state, form state and derived render variables—all while the application still appears to work.

Current React guidance explicitly recommends a single owner for each unique piece of state and warns against redundant/duplicated state; shared state should have an appropriate common owner rather than multiple unsynchronised copies. citeturn10search0turn10search8 Redux's current guidance similarly says that not every value belongs in a global store and that local UI state should generally remain near the component that uses it, while shared/app-wide state belongs in the shared state mechanism where appropriate. citeturn10search2 These are framework practices, not universal laws, but they give a concrete audit vocabulary.

The useful audit is to assign every important stateful concept to one category:

| State category | Expected ownership question | Erosion to look for |
|---|---|---|
| **Remote/server state** | Which subsystem owns fetching, caching, freshness and invalidation? | Same server entity independently fetched/stored by components, global store and query library; multiple cache-key conventions; mutation invalidation scattered across UI |
| **URL/navigation state** | Must reload, deep linking, shareable links or browser Back/Forward preserve this value? | Filters/search/sort/page/tab duplicated in a store and query string, or navigation-significant state hidden only in memory |
| **Local UI state** | Does the value matter outside this component/subtree? | Modal/dropdown/hover/transient state moved into a global store without a real cross-tree requirement |
| **Shared client/application state** | Does genuinely non-server state need coordinated ownership across features? | Several competing global stores/context mechanisms for the same concern |
| **Form state** | Is there one form lifecycle and validation owner? | Form library state copied into component state and global state simultaneously |
| **Derived state** | Can the value be calculated from authoritative state during render/select? | Cached copy maintained by effects/subscriptions, creating synchronisation paths |
| **Persistent client state** | Which layer owns storage, migration and hydration? | Direct `localStorage`/IndexedDB access scattered through components with competing schemas |

For applications using a server-state library such as TanStack Query, current documentation makes the query key/cache a central part of server-data identity and caching. The architectural audit should therefore inventory **who constructs query keys, who performs invalidation, and which code bypasses the common fetching/cache layer**; that is more meaningful than merely counting hooks. citeturn10search5turn10search9

Other front-end-specific signals deserve explicit treatment:

| Signal | Mechanical evidence | Judgment question |
|---|---|---|
| **Feature-boundary leakage** | Cross-feature imports; deep imports past public package entry points | Are features genuinely independent, or is the nominal boundary fictional? |
| **“Shared/common/utils” gravity well** | High fan-in/fan-out shared folders, unrelated concept clusters | Is shared code a coherent stable kernel, or simply code with no clear owner? |
| **Page/router component as God object** | Route component owns fetches, mutations, global/local state, transformations and rendering | Is it legitimate composition, or several architectural responsibilities in one file? |
| **Duplicated data-fetch mechanisms** | `fetch`/Axios/custom clients plus query framework plus store-side requests | Are there intentional protocols/bounded contexts, or did each agent invent its own client? |
| **Cache duplication** | Same entity type resident in multiple caches/stores | Which copy is authoritative, and what ensures coherence? |
| **Effect-mediated synchronisation** | Effects copy one state source into another | Could one representation be derived instead? React's guidance against redundant state makes these cases worth inspection. citeturn10search8 |
| **Route/state mismatch** | Search params parsed and then independently mirrored to stores/components | Do deep-linking and browser navigation reliably restore the application's visible state? |
| **Design-system bypass** | Raw primitives/styles/tokens used where the repo declares approved components/tokens | Is this an authorised exception or design-system erosion? |
| **Two component systems for one semantic role** | Competing Button/Dialog/Form/Error/Toast families | Is one legacy/migrating, or has a parallel design system emerged? |
| **Barrel/public API erosion** | Increasing deep imports into feature internals | Is information hiding actually being preserved? |
| **Provider/context proliferation** | Nested providers and contexts with overlapping responsibilities | Are these independent capabilities or fragmented global state? |

Design-system adherence must be judged **against the project's declared system**, not a generic front-end aesthetic. If the architecture says raw HTML controls are acceptable, an auditor should not manufacture a “must use design-system Button” rule. Conversely, where a design system is an explicit consistency/accessibility contract, imports and token usage are highly mechanisable architecture rules.

A particularly useful front-end deliverable is a **state ownership matrix**:

```text
Concept          Server cache   URL   Global store   Component   Persistent
searchFilters         -          X         X              X          -
currentUser           X          -         X              -          X
checkoutDraft         -          -         X              X          X
```

Rows with several `X`s are not automatically wrong. They are where the auditor asks for an explicit source-of-truth story. This is substantially more actionable than counting Redux slices or React components.

## What is actually known about agent-written code

The evidence in 2026 is now better than anecdotes, but it is still too early to justify a special “AI smell catalogue” as if its entries were established laws.

### Complexity and static-analysis debt: measured, but effect size unsettled

He, Miller, Agarwal, Kästner and Vasilescu's 2026 MSR study, *Speed at the Cost of Quality*, used a difference-in-differences design around adoption of Cursor, with adopting repositories matched to controls. It reported a large short-term rise in code production that dissipated after roughly two months, together with a **30% increase in static-analysis warnings and a 41% increase in code complexity** under one of its estimators. The important limitations are that it is tool-specific and detects adoption using repository-visible signals rather than attributing every changed line to an agent. citeturn23search0turn23search6

A separate July 2026 causal study of 1,888 projects, with its main difference-in-differences analysis restricted to 603 adopters having a usable pre-adoption period, reproduced the **direction** of the complexity effect but estimated much smaller magnitudes: roughly **3–4% higher cyclomatic complexity across languages and about 11% higher cognitive complexity for Python**. citeturn23search1turn23search4

So the defensible conclusion as of October 2026 is:

> **Emerging evidence suggests agent adoption can increase structural complexity in real repositories; the magnitude is not settled.**

The 41% figure should emphatically **not** become an audit threshold.

### AI-attributed technical debt: strong scale, limited architecture coverage

A 2026 preprint by Liu and colleagues assembled **302,579 analysed AI-attributed commits across 6,299 repositories** for Copilot, Claude, Cursor, Gemini and Devin using explicit Git metadata. Differential static analysis identified 484,366 introduced issues; 89.3% were classified as code smells, every studied assistant had more than 15% of analysed commits introducing at least one detected issue, and 22.7% of tracked introduced issues survived at repository HEAD. citeturn19view1

The authors manually validated samples: their issue-validity pipeline reported **85.9% precision and 100% recall** on the adjudicated sample, which is also a useful reminder that even deterministic-looking static-analysis datasets contain noise. citeturn19view1

But this study primarily measures lint/static-analysis debt in Python, JavaScript and TypeScript. It does **not** establish that AI-generated code has worse module architecture, more architectural cycles, more conceptual duplication, or poorer bounded contexts. The authors themselves frame broader architectural debt as outside what their analysis directly establishes. citeturn19view1

### “Agents duplicate instead of reuse”: not established

This claim is currently much weaker than its popularity suggests.

A peer-reviewed MSR 2026 study of **350 clone lineages across six human–agent collaborative projects** found that humans introduced **85.71%** of the studied clones and agents 14.29%; clone survival was similar at 80% for human-introduced and 76% for agent-introduced clones. Given the tiny project sample, this does not prove agents are *better* about duplication—but it directly demonstrates that “agents generally introduce more clones” is not a settled empirical fact. citeturn23search2turn20view0

Therefore duplication should absolutely be audited in an agent-heavy codebase, but because duplication is a maintainability problem, **not because provenance alone makes it an AI-specific smell**.

### Over-engineering, cargo-culting, inconsistent conventions and gate gaming

For these behaviours, the research located for this review does **not** yet provide repository-scale longitudinal evidence comparable to the complexity studies above.

There are plausible mechanisms. Agents can observe a local pattern and reproduce it without understanding whether it is legacy; they can satisfy a failing check by adding exclusions or suppressions; successive agents can create alternative abstractions when retrieval fails to reveal the first one. But as of October 2026 those should be labelled **hypotheses or practitioner observations**, not measured universal properties of agent-written repositories.

Accordingly, an audit should test them provenance-neutrally:

`multiple abstraction candidates → inspect authorship later`

is methodologically stronger than:

`agent-authored code → look for overengineering`.

That avoids confirmation bias.

### What agent-first teams should encode

The strongest response is not an “AI cleanup score.” It is to make architectural intent executable wherever intent is crisp enough to execute.

**Established practice, not agent-specific:** structural tests and dependency constraints such as ArchUnit, dependency-cruiser and module-boundary rules. citeturn2search0turn2search1turn2search8

**Emerging/reasonable:** give coding agents the same deterministic repo map, lint/type/test commands and architecture checks humans use before permitting changes. Recent work on deterministic repository maps for LLM assistants and architecture-aware repository comprehension points in this direction, but the evidence base is still young. citeturn17search3turn17search7

**Opinion:** recurring cleanup agents can be useful *executors* of accepted findings—remove verified dead exports, collapse an accepted duplicate abstraction, migrate imports—but should not be the sole authority deciding what architecture is obsolete.

**Opinion:** per-domain quality dashboards can help teams allocate cleanup effort, but a numerical domain score should expose its raw components and confidence. A score that turns eight uncertain smells into “Payments health = 63” creates spurious precision.

## Baseline, cadence, scoring, and failure modes

The audit becomes substantially more valuable on its second run. The main product is therefore not just a PDF/report; it is a **versioned evidence baseline**.

### The minimal baseline worth keeping

I would resist recording hundreds of headline metrics. Persist all raw analysis, but put roughly this set on the recurring dashboard:

| Baseline measure | Why keep it |
|---|---|
| **Production size:** logical/physical LOC plus production file/module count | Makes gross growth and pruning visible; never interpret growth alone as bloat |
| **Architecture divergence:** prohibited/undocumented boundary edges, with new/resolved counts | Closest direct measure of architecture-policy drift |
| **Cycle mass:** number of nodes in cyclic SCCs plus size of largest SCC | More informative than binary “there are cycles” |
| **Change concentration:** human/agent-authored churn distribution and identities of persistent hotspots | Detects maintenance gravity while avoiding bot noise; 2026 hotspot research specifically warns about automated-history contamination. citeturn22view0 |
| **Gate debt:** suppressions + skips/quarantines + allowed failures/exemptions, broken down by mechanism and age | Measures whether rules are being bypassed rather than satisfied |
| **Test strength:** untested eligible critical code, extreme-mutation survivors and targeted mutation score | Measures behavioural constraint rather than execution alone; supported by industrial mutation-testing practice. citeturn8search0turn8search1 |
| **Structural excess:** clone percentage/clone families plus verified unused/orphan artefacts | Captures two of the more mechanically defensible forms of code-volume debt |
| **Accepted semantic debt:** unresolved parallel abstractions/concept fragmentation findings by severity | Preserves important judgment-based problems without pretending they are machine metrics |

Alongside every number, store the **scope hash**: commit, languages, include/exclude patterns, generator/test exclusions, analysis tool/version and configuration. Alves et al.'s threshold work explicitly showed that metric values and thresholds are sensitive to tool definitions and whether test/generated code is in scope, so longitudinal comparison without this metadata can be misleading. citeturn15view0

### Cadence and triggers

I found no credible empirical research establishing that architecture audits should happen “every 30 days” or after “10,000 changed lines.” Those are management choices, not scientific thresholds.

A useful policy is therefore **event-driven plus a calendar backstop**:

| Trigger | Recommended reaction | Evidence status |
|---|---|---|
| New violation of an explicit architecture invariant | Audit affected dependency slice immediately | **Established logic:** the rule itself defines zero tolerance |
| CI/type/lint/test gate relaxed or migrated | Re-run gate-equivalence audit | **Strong practice**, supported by pipeline-smell evidence. citeturn9search9 |
| Major framework, state-management, package or monorepo migration | Refresh architectural map and intended-architecture ledger | **Opinion / prudent practice** |
| Incident reveals a cross-module or test-containment failure | Audit involved dependency/co-change neighbourhood | **Opinion**, risk-based |
| Large persistent shift in cycle mass, suppressions, duplicate code, mutation strength or hotspot distribution | Trigger focused audit | **Opinion:** use repository history/control limits rather than universal percentages |
| Introduction of materially different coding-agent workflow | Establish a new comparison point rather than silently blending regimes | **Emerging**, because current studies show outcomes differ by tool/context. citeturn19view1turn23search6 |
| No trigger for an extended period | Calendar audit as a safety net | **Opinion** |

For a high-velocity agent-first repository, monthly or release-based lightweight measurement plus a deeper quarterly/major-milestone review is a reasonable **operating choice**, but it should not be presented as evidence-backed industry law.

### Is there a credible health score?

There are serious attempts, but no universal whole-codebase architecture number should be treated like temperature.

The SIG maintainability work published in 2007 built a multi-measure model rather than trusting a single Maintainability Index, and explicitly described the model at that stage as evolving/preliminary. citeturn21search0turn21search1 The 2010 Alves study subsequently supplied empirically benchmarked thresholds for several of its underlying source metrics, which makes that family of models substantially more defensible than arbitrary red/yellow/green limits. citeturn15view0

ATDx, evaluated in 2022 across the Apache and ONAP ecosystems—237 software projects and 233 contributors in that study—offers a more architecture-specific technical-debt index. Its design is notable for deriving severities from the analysed data rather than requiring one universal set of a priori thresholds, and the empirical evaluation describes its results as promising while explicitly calling for validation in additional settings. citeturn21search6

A 2024 maintainability-metric study also illustrates why caution is warranted: even human maintainability assessment is subjective, with expert-consensus agreement imperfect, and different automated approaches do not simply collapse onto one universally reliable ranking. citeturn21search10

The recommendation is therefore:

> **Use a vector as the source of truth; generate a scalar only for portfolio communication.**

A defensible per-module vector might be:

`[boundary violations, cycle involvement, change pressure, co-change leakage, gate debt, test strength, structural excess, accepted semantic debt]`

If management requires one red/amber/green value, calibrate it **within the repository or comparable portfolio**, publish the formula, never hide the components, and keep **confidence/evidence coverage separate from health**. There is no research basis for universal weights such as “coupling 25%, complexity 20%, duplication 15%.”

### The audit's own failure modes

This is where an LLM-assisted audit can do the most damage: it can produce many individually plausible observations and accidentally convert quantity into apparent authority.

| Failure mode | How it manifests | Defence |
|---|---|---|
| **Judging style as architecture** | “These files should be feature folders”, “use repositories everywhere”, “200 lines is too long” | Require either an explicit repo constraint or a concrete coupling/change/test consequence |
| **Treating documentation as unquestionable truth** | Old ADR causes working replacement architecture to be labelled wrong | Track status/date/scope; report policy conflict when authority is uncertain |
| **Treating implementation prevalence as truth** | Legacy style wins because 70% of code is legacy | Separate observed architecture from intended/enforced architecture |
| **Cycle alarmism** | Every SCC becomes high severity | Determine graph level and whether acyclicity is actually an architectural requirement; empirical cycle-remediation research stresses context. citeturn0search3 |
| **Metric threshold cargo culting** | “McCabe 11 is a defect”, “75 LOC is unacceptable” | Record threshold provenance. Benchmark-derived cutoffs are population quantiles, not universal failure boundaries. citeturn15view0 |
| **Size-as-bloat fallacy** | Cohesive algorithm is split solely to satisfy length metric | Demand evidence of multiple responsibilities/change reasons, not just LOC |
| **Abstraction-count fallacy** | One-implementation interface automatically deleted | Check whether it forms a deliberate port, public API, testing seam or migration boundary |
| **Duplicate-abstraction false positive** | Two “clients” serve different protocols/contexts | Compare responsibility, call sites, data models and lifecycle before merging |
| **Dead-code false positive** | Dynamic route/plugin/reflection registration appears unused | Validate framework registries/build/runtime entry points; auto-delete only high-confidence cases |
| **History contamination** | Dependency bots/formatters make files look hot | Classify automated/mechanical edits separately; 2026 hotspot results show this can materially change conclusions. citeturn22view0 |
| **LLM verbosity masquerading as coverage** | Auditor emits hundreds of weak smells | Require deterministic evidence anchors and cap reports to findings that pass a rubric |
| **Hallucinated relationship** | Model claims A depends on B because names are semantically related | Dependency edges must come from an extractor or direct anchored code evidence |
| **LLM false positives** | Plausible reviews swamp valid issues | Human-adjudicate semantic findings; SWR-Bench 2026 found very low precision for contemporary automated code-review approaches. citeturn17search2 |
| **Static-analysis false positives treated as fact** | Every lint detector result enters debt totals | Preserve detector provenance and validate samples; a 2026 large-scale AI-debt pipeline itself measured only 85.9% precision for issue validity. citeturn19view1 |
| **Hotspot-only sampling** | Audit concludes whole repository is disastrous because only worst files were read | Add random/stable controls to the semantic sample |
| **Severity inflation on running code** | Naming inconsistency receives “critical” severity | Separate maintainability risk from observed operational/gate failure |
| **Repeated rediscovery** | Same accepted exception appears every quarter | Baseline accepted findings/exceptions with owner, reason and expiry |
| **Score gaming** | Teams remove cheap warnings while core boundary debt worsens | Preserve components; never optimise a single aggregate without inspecting raw measures |

For **severity calibration**, a practical 2026 rubric is:

**Critical** should normally require a *verified* failure of an important containment mechanism: for example, a required gate no longer runs and unvalidated code can merge, or a structural violation has demonstrated severe runtime/operational consequence. Merely being ugly or complex is not critical.

**High** fits a verified architectural invariant breach or major conceptual split with broad reach **and** material change pressure: for example, core modules forming an expanding prohibited cycle while repeatedly co-changing across boundaries.

**Medium** fits real drift whose cost is currently maintenance/evolution risk rather than observed behaviour: an accumulating second error hierarchy, repeated feature-boundary leakage, a growing server-state duplication problem.

**Low** fits local bloat and cleanup with limited blast radius: dead helpers, unnecessary forwarding layers, comment noise, isolated oversizing.

This rubric is **Opinion (2026)**; there is no universal empirical conversion from cyclomatic complexity, fan-out or LOC into incident severity. Severity should describe the consequence of **this finding in this system**, while confidence describes how certain the auditor is that the finding is real.

The final task list should therefore favour, in order: **broken explicit constraints and gates; structural problems at high-change/high-reach locations; test-strength holes on important behaviour; consolidation of verified parallel concepts; then low-risk pruning and verbosity cleanup**. That order reflects the evidence hierarchy: an anchored invariant violation is much stronger than a smell; an evolutionary hotspot makes a structural problem more urgent; and a stylistic complaint without measurable architectural consequence belongs at the bottom. citeturn0search0turn0search2turn22view0

The overall conclusion is that an architecture audit for an agent-written repository should **not become an AI detector or an automated style review**. The durable method is the same one the best architecture-recovery work has implied for decades: reconstruct what exists, state separately what was intended, measure where they disagree, add evolutionary evidence to distinguish dormant oddities from costly pressure points, verify that enforcement has not weakened, and reserve semantic judgment for questions that graphs and counters cannot answer. Agent-heavy development raises the value of doing that frequently because code can be produced faster and recent studies indicate quality/complexity pressure may rise with agent adoption, but the architecture still has to be judged on observable structure and behaviour rather than on who—or what—typed it. citeturn0search1turn23search6turn23search4