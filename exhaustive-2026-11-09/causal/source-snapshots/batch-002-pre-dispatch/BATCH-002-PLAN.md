# Proposed causal comparisons after the first batch

The first batch validated force-event capture, then encountered three rejected
post-terminal marker leases. Every direct method merged its prefix and rewrote
the surviving suffix in the retained final observation. No marker in those
native cases was acknowledged; they therefore supplied no accepted-marker
overwrite or quiet-window result. Those three fixtures remain frozen.

The next batch uses new independent trunks and branches only. Proposed cases:

| New case | Discriminator |
| --- | --- |
| `post-squash-3` | Same direct method as squash1, with three suffix PRs. This isolates suffix length from the earlier rebase3 comparison. One immediate post-terminal marker attempt; no retry. |
| `early-squash-3` | Generate/publish the marker after admission and a captured pending poll, before the first terminal observation. Preserve the actual intervals. This tests an earlier overlapping publication; it cannot certify that the provider remained pending at the marker's write instant. |
| `after-rewrite-squash-3` | After terminal response, first capture each suffix's changed ref, consistent parent chain, and matching force event from its original head. Only then generate a new unique marker and make one exact-lease publication attempt. This exercises accepted post-terminal publication after an observed rewrite, without treating that observation as a fence. |
| `ordinary-sync-3` | Create/adopt an isolated local CLI catalog before landing A. After native landing and observed suffix rewrite, run pinned official v0.3.0 `sync --remote origin --no-atomic=false` once. Compare local rebasing/push events with native events. |

Root grants may select a subset. No case is authorized until its exact name is
in a new root grant. The observed-rewrite wait is bounded to 30 seconds; missing
premises stop that case. Successful marker cases get the original 60-second
observation window. Finite absence still establishes no future exclusion rule.

## Official sync effect audit and recording

The retained official v0.3.0 binary is
`experiments/native-stacks-2026-11-08/cli-history/bin/darwin-arm64`, SHA256
`70c0cb11346ad5d4f97a02a5cf5242052254d1775d356dc0759f035457873850`.
Its hash was rechecked. No extension is installed or will be installed.

Current pinned source `bd0a32504f9ae9f795875a9e6bb90ff7408fda08` was read in
`sources/extracts/cmd-init.txt`, `cmd-sync.txt` and `gitops.txt`. Explicit
`init --base <local synthetic trunk> <existing local A B C D>` performs local
catalog/checkout work plus PR read lookups. Missing branches would be created;
the harness therefore precreates and verifies every local ref from its exact
synthetic object before adoption.

`sync` fetches, refreshes PR state, advances local trunk, rebases active branches,
pushes active branches atomically, refreshes PR state and may update the existing
native group. Its force push uses explicit per-ref leases and `pull.stacked`.
The command can warn about a failed push and still exit zero, so exit status is
not the ref-publication oracle. No `--prune` or `--accept-base-change` is used.

`sync_driver.py` will own a separate checkout and record the full CLI input,
catalog, exact local/tracking refs, output and actual hosted readback. A private
`git` wrapper will preserve each Git argument vector before dispatch, force hooks
off, restrict any push to this case's active B/C/D refs with `--atomic` and an
explicit lease for every ref, and refuse a second push dispatch. That refusal
also prevents an unreviewed CLI fallback/retry. Group side effects remain bounded
by the isolated catalog and the sole new native group. Unknown CLI/write outcomes
freeze the case for read-only reconciliation.

*Authored by an AI agent acting on joshlf's behalf.*
