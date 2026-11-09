# Native REBASE queue with only real CI

A landed, while B was removed with provider reason `invalid_merge_commit`. B then rewrote natively and its real synchronize workflow succeeded; later reads showed B open, `CLEAN` and without a queue entry. The original admission did not finish landing B during this trace.

This is one fresh two-PR fixture, native stack #33, under `exp/ci/native-no-manual-gate-rebase/**`. It used the same standard workflow and queue settings as the other method controls except for the queue merge method and unique fixture paths. These are observed method comparisons, not a universal provider rule or a production acceptance claim.

## Configuration and admission

The exact-trunk rule `26822302` required only `queue-observe`, bound to Actions app 15368, with no bypass actors, reviewers, manual release context or failure-marker files. Effective rule readback contains only that context and the queue rule: `REBASE`, `ALLGREEN`, build concurrency 1, maximum merge entries 5, minimum entries 1, minimum wait 1 minute, response timeout 5 minutes. No synthetic status was posted anywhere in this fixture; queried relevant commit-status lists are empty.

Both PRs were `CLEAN` before one selected-B REST admission. The request captured B `9ec02b2d2893201be973477ebd81f2ed8e5a968e`, supplied `merge_action: merge_queue`, omitted `merge_method`, and returned UUID `ef104847-d49e-431c-983b-cd93a8a8c59b`. Polling reached terminal `enqueued`. There was no request resend, manual source update or explicit requeue.

## Checked candidates and provider removals

| Actual workflow run | Candidate SHA | Exact parents | Tree | Check-run IDs |
| --- | --- | --- | --- | --- |
| [42546156039](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42546156039) | `36ea8be012efdf8019d08fa7822a3ae4b4721d81` | `aecb858ce2c0d6ba4e8e20dc44ac7f931f71d230` | `da7aef3c9eef8610d0009905a65e1bab43fc2b46` | `128931510604` |

For each candidate, the event `head_sha`, run SHA, `GITHUB_SHA`, checkout HEAD and required check attachment match. API commit trees/parents match the downloaded graphs, and all candidate checks succeeded.

| Native member | Provider time (UTC) | Removal reason | `beforeCommit` |
| --- | --- | --- | --- |
| A / #31 | `2026-11-09T01:33:45Z` | `merged` | `36ea8be012efdf8019d08fa7822a3ae4b4721d81` |
| B / #32 | `2026-11-09T01:33:43Z` | `invalid_merge_commit` | `null` |

Provider metadata times do not expose a cross-resource transaction order. The successful rewrite synchronize run was [42546215367](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42546215367). Its event names the new PR head, and its exact synthetic merge checkout is retained in the artifact.

## Retained work and final observations

B source head: `9ec02b2d2893201be973477ebd81f2ed8e5a968e` → `9c41d21f6f29969d33a71b1c633c73f68fa877c1`. Its own commit patch, full tree, author name/email/date and exact message are unchanged. Raw binary-diff output bytes match SHA-256 `f154249c98fd306a299af6c9c7c45ba6771f09ea04658d16d4c7af6595011e1c`. Source messages retain the AI disclosure trailer. Exact commit headers, messages, trees, verification objects and both patch files are retained in `frozen-summary.json` and the adjacent artifacts. Original A/B authored archive targets remain unchanged.

The last queue observation ended `2026-11-09T01:38:55.776253+00:00` and has both entry fields null. The final trunk was `36ea8be012efdf8019d08fa7822a3ae4b4721d81`. Re-reading the original async receipt still returned `enqueued`, which describes prior admission rather than current queue membership or landing. All actual source/group run artifacts and logs are retained here; raw write intents and read receipts are in the parent CI evidence directory.

The experiment does not establish another build-concurrency/grouping combination, every queue failure policy, provider internals, automatic recovery after an unknown write, or future settlement. No additional landing/requeue decision was inferred from agreeing reads. Shared workflows, main and global settings were not changed by this lane.

*Authored by an AI agent acting on joshlf's behalf.*
