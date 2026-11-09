# Native queue merge-method discriminator

Three fresh two-PR native stacks used only real Actions CI. Each required `queue-observe` from Actions app 15368, no other status/review context, no bypass actors and no failure markers. Queue settings were ALLGREEN, build concurrency 1, maximum merge entries 5, minimum entries 1, minimum wait 1 minute and response timeout 5 minutes. Each selected B was admitted once via REST with its exact head, `merge_action=merge_queue` and no requested merge method. No synthetic status or explicit requeue was sent.

| Queue method | Native PRs / stack | Observed outcome | Detailed evidence |
| --- | --- | --- | --- |
| SQUASH | #25 / #26 / stack #27 | A landed; B removed `invalid_merge_commit`, rewritten, then real CI CLEAN/open/unqueued. | [SQUASH results](native-no-manual-gate/RESULTS.md) |
| MERGE | #28 / #29 / stack #30 | Both A and B landed; source heads retained. | [MERGE results](native-no-manual-gate-merge/RESULTS.md) |
| REBASE | #31 / #32 / stack #33 | A landed; B removed `invalid_merge_commit`, rewritten, then real CI CLEAN/open/unqueued. | [REBASE results](native-no-manual-gate-rebase/RESULTS.md) |

The custom manual release context is not necessary for the SQUASH/REBASE removals in these traces. The MERGE fixture built and checked two-parent A/B candidates and landed both members; the SQUASH/REBASE fixtures checked a single-parent A candidate, then retained an unchanged B patch after its removal/rewrite. That graph difference supports a method-specific observation, not a claim about the provider’s internal cause or all native queues. There was one fixture per method; unique fixture paths/commit identities differed.

All three final observed queues were empty. In every case, raw B patch bytes, tree, author tuple and message were retained, and exact authored archives survived. Full removal reasons/times, source heads, commit headers/messages, trees, workflow/check IDs, source synchronize events and exact rule/read intervals are in each `frozen-summary.json`. `native-method-comparison.json` supplies a compact machine-readable index.

The original async receipts remained `enqueued` after landing/removal. Final collection and matching reads do not prove no delayed writes or authorize overlapping production mutation. Global settings and shared workflows were untouched.

*Authored by an AI agent acting on joshlf's behalf.*
