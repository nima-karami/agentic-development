# Rubric — verbosity

Code larger than it needs to be: machinery for needs that never arrived, layers that
add nothing, defenses against impossible states, words that restate code, files nobody
reaches. Every row here has a legitimate twin — a port at a real boundary, a wrapper
that translates, a check at a public entry — so **the verdict is always judgment**, and
the over-engineering line matters as much as the finding.

Size is never judged alone. Long, cold and cohesive is fine; long, hot and splitting
internally is the finding.

## Rows

### V1 · Speculative generality
- **Finding:** an interface or abstract type with one implementation; an extension
  point nothing extends; config nobody sets; a parameter every caller passes the same
  value; a factory for one product.
- **Detection:** count implementers; find always-identical arguments and never-set
  config keys.
- **Severity:** Low to Medium; Medium in a hotspot.
- **Over-engineering line:** ports at real external boundaries, test seams, and
  published contracts are legitimate even with one implementation.

### V2 · Pass-through layers
- **Finding:** a function whose body only forwards the same arguments to another;
  chains of such wrappers; a repository that wraps the data layer one-to-one.
- **Detection:** single-delegation bodies and wrapper-chain depth.
- **Severity:** Low to Medium.
- **Over-engineering line:** report only when the layer adds no translation, policy,
  stability or migration value.

### V3 · Defensive bloat
- **Finding:** null checks on non-nullable values; the same guard in handler, service
  and repository; "can't happen" branches that silently default.
- **Detection:** redundant-condition checks where types are honest; duplicate-condition
  search across layers.
- **Severity:** Medium; High when the layers' conditions disagree (they drifted).
- **Over-engineering line:** public library methods may defend themselves; checks at a
  real trust boundary belong there.

### V4 · Comment noise
- **Finding:** comments that restate the line below; narration of a past change;
  section banners describing what the next block does.
- **Detection:** model classification on a sample: what vs why.
- **Severity:** Low; **High** only when a comment contradicts behavior or policy.
- **Over-engineering line:** stripping why-comments, invariant notes, tool directives,
  or doc comments on a public API.

### V5 · Dead code and orphans
- **Finding:** unused exports, files and dependencies; leftovers from abandoned
  attempts; feature flags fully rolled out but never removed.
- **Detection:** reachability from entry points, **after** checking framework routing,
  dependency injection, plugin registries and other dynamic registration.
- **Severity:** Low to Medium.
- **Over-engineering line:** deleting dynamically registered code a scan cannot see.
  Deleting as dead requires proving zero consumers through indirection.

### V6 · Size judged with churn
- **Finding:** a long unit that is also a hotspot, whose internal parts change
  independently.
- **Detection:** unit and file size ranked by repo percentile, crossed with churn and
  internal co-change.
- **Severity:** Medium in a hotspot; nothing in a cold, cohesive file.
- **Over-engineering line:** fixed line limits; splitting that creates pass-throughs.

### V7 · Clone families
- **Finding:** copy-pasted blocks, weighted when they cross module boundaries or change
  together.
- **Detection:** token or AST clone detection; trend against baseline.
- **Severity:** Medium; High when clones have already diverged in behavior.
- **Over-engineering line:** a universal duplication percentage; a shared helper that
  couples two unrelated domains to remove syntactic duplication.

### V8 · Restated artifacts
- **Finding:** documentation, types or config that restate another artifact at lower
  fidelity and drift from it; generated-looking boilerplate repeated per module.
- **Detection:** similarity between docs and code, types and schemas.
- **Severity:** Low; Medium once they disagree.
- **Over-engineering line:** removing a short summary that orients readers.
