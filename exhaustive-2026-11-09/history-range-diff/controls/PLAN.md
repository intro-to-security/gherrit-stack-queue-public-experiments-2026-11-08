# Local range-diff controls

Use one fresh local bare repository and explicit synthetic trees/parents. The five controls cover unrelated base-file drift with the same authored patch; changed same-file context with the same authored line edit; different binary replacement bytes; a changed executable mode; and two disjoint commits reordered across unrelated base drift. Retain exact base/tip identities, command arguments/stdin/output, full-index patches, a literal diff between those patches, raw tree entries, and blob bytes/hashes.

The repository has no remotes. All commands disable hooks, external diffs and textconv where applicable. Synthetic commits use Josh Liebow-Feeser <hello@joshlf.com> and the required Agent-authored-by trailer. No frozen history is changed, no old driver is replayed, and no hosted/network write or compilation occurs.

The comparison separates reviewer usefulness from proof. Commit pairing, changed context, binary placeholders, modes, and message effects are observations to inspect rather than a semantic acceptance oracle. Git documents range-diff as a human-facing comparison with heuristic commit matching and output that may change across versions. The exact authored bases remain separate inputs. [Official range-diff manual](https://git-scm.com/docs/git-range-diff).

*Authored by an AI agent acting on joshlf's behalf.*
