# Baseline

`docs/audits/baseline.json` is what turns the next audit into a drift measurement
instead of a fresh opinion. It is overwritten each audit; history lives in version
control. Keep it small: numbers and short lists, never findings prose.

## Schema

```json
{
  "schema": 1,
  "audit": { "date": "YYYY-MM-DD", "mode": "drift|inherited|run", "depth": "quick|standard|deep",
             "commit": "<sha>", "range": "<base>..<head> | null", "report": "docs/audits/<dir>/report.md" },
  "profile": { "path": "docs/audits/<dir>/profile.md", "hash": "<hash of the profile's identity, load, stakes and attributes>",
               "dominant_attributes": ["…"], "unknowns": ["…"] },
  "scope": { "fingerprint": "<hash>", "include": ["…"], "exclude": ["…"],
             "tools": { "<tool>": "<version>" }, "scan_commands": { "<extractor>": "<command>" } },
  "architecture": {
    "violations_by_rule": { "<rule-id>": 0 },
    "cycle_nodes": 0, "largest_scc": 0,
    "hotspots_top20": [ { "path": "…", "churn": 0, "complexity": 0 } ],
    "cochange_top": [ { "a": "…", "b": "…", "ratio": 0.0 } ],
    "parallel_abstractions": [ { "concern": "http-client", "members": ["…"], "status": "open|accepted" } ]
  },
  "gates": {
    "manifest_hash": "<hash>", "required_checks": ["…"],
    "debt": { "suppressions": { "<mechanism>": { "count": 0, "median_age_days": 0 } },
              "skips": 0, "allowed_failures": 0, "exemptions": 0 },
    "escape_hatches": { "total": 0, "at_ingestion": 0 }
  },
  "tests": {
    "sample_files": ["…"],
    "eligible_untested": 0, "pseudo_tested": 0, "kill_rate": 0.0
  },
  "verbosity": { "clone_families": 0, "cross_module_clones": 0, "dead_files": 0, "dead_exports": 0 },
  "security": { "scanner_manifest_hash": "<hash>", "unguarded_mutating_entry_points": 0,
                "entry_points": 0, "permissive_flags": 0, "secrets_live": 0,
                "reachable_known_cves": 0, "unpinned_ci_actions": 0 },
  "performance": { "flows": [ { "name": "…", "fan_out": 0, "serial_depth": 0,
                                "measured": { "p95_ms": null, "bundle_kb": null } } ],
                   "calls_in_loops": 0, "unbounded_reads": 0, "blocking_calls_on_critical_threads": 0,
                   "uncapped_caches": 0, "unpaired_lifecycles": 0, "clients_missing_timeouts": 0 },
  "audit_quality": { "findings_sampled": 0, "confirmed": 0, "confirmed_share": 0.0,
                     "refuted_by_verifier": 0 },
  "accepted_exceptions": [ { "what": "…", "anchor": "…", "owner": "…", "reason": "…", "expires": "YYYY-MM-DD" } ]
}
```

**Counting conventions:** every count is production code only (tests excluded) unless
the field name says otherwise — escape hatches, suppressions, clones, dead code. Record
an excluded-tests figure in a sibling `note` field when it is useful. `confirmed_share`
is `null`, never `0`, until a human has confirmed a sample.

**Assembly:** one mechanical-tier agent builds this file from `work/facts/`,
`work/tests.md` and the profile, parses it back, and returns the list of fields it
could not fill. The orchestrator reviews that list; it does not hand-assemble.

## Drift comparison rules

0. **Profile next to fingerprint.** If `profile.hash` differs, the system's
   requirements changed; re-calibrate severity and declare a new comparison point
   rather than reporting the shift as drift.
1. **Fingerprint first.** If `scope.fingerprint` differs, the numbers are not
   comparable. Either rerun with the old scope (the stored `scan_commands` make that
   possible) or declare a new comparison point and say so in `TREND` (`new`).
2. **Rerun the old scripts when the method changes.** A tool upgrade that changes
   counts is not drift; note it and rebase.
3. **Same sample.** Test strength is measured on `tests.sample_files`, extended — never
   replaced — by code changed since the last audit.
4. **Direction per dimension.** `worse` when any ratchet number moved the wrong way
   beyond noise or a new Critical/High finding appeared; `better` when ratchets
   improved and no new serious findings appeared; otherwise `same`.
5. **Ratchets** (each breach is a `TRIGGERS` entry): a new unguarded mutating entry
   point, a new permissive flag, or a newly reachable known CVE; a measured flow
   getting slower or a new call-in-loop on a representative flow; a new cycle between top-level
   modules; a new violation of a declared rule; suppressions or skips rising; kill
   rate or pseudo-tested count worsening on the fixed sample; a new parallel
   abstraction; a gate removed, made non-blocking, or relaxed.
6. **Expired exceptions** return as findings at their original severity.
7. **`run` mode** writes its numbers under the same schema, with `range` set, and does
   not overwrite a whole-repo baseline unless the run covered the whole repo.
