# Preserved harness corrections

The first extension run is `followup-runs/1794194513334823000`. Its exact source,
two failure traces and all command receipts remain there. Neither was a failure
of the tested Git or importer invariant:

- L21 tried to assign object A directly in a bare sink that had received only P.
  Git correctly refused the nonexistent object. The corrected fixture first
  fetches A locally without installing a fixture ref, then runs old→A→old.
- L22 assumed a one-line patch changed from `1` to `2` would be paired with `!`
  by default `range-diff`. Git instead rendered old/new unmatched patches. The
  corrected oracle independently requires changed exact patch bytes and accepts
  either an explicitly changed pair or old/new unmatched entries, while refusing
  an unchanged `=` entry. The retained output documents heuristic matching.

The first aggregate-report writer also attempted `Path.relative_to` for a prior
artifact outside this lane. It raised before writing the aggregate report.
`report-first-path-error.py` preserves that writer; the corrected report uses
`os.path.relpath`. No experiment result or source under test changed.

No production or original prototype source was corrected. The substantive
missing-evidence/completion/concurrent-worker failures remain findings.

*Authored by an AI agent acting on joshlf's behalf.*
