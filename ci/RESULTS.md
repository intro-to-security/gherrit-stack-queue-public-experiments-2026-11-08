# Ordinary PR queue controls

Two ordinary, non-native PRs exercised actual merge queues in the authorized public repository `intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08`. Hosted events below occurred on November 9, 2026 UTC, still November 8 in the user's timezone. Each fixture had its own exact-trunk active ruleset, with no bypass actors, queue method `SQUASH`, one entry per build/merge, a five-minute response timeout, and required contexts `queue-observe` and `experiment/queue-release`.

## Held candidate, then release and landing

[PR #5](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/5) targeted `exp/ci/single-held-release/trunk`, ruleset `26821687`. Its ordinary PR workflow succeeded. Admission release statuses were posted on exact authored head `9598ba41dda1477617af3a36c0a43abf2ec04c93` and PR test-merge `e92b676e858f55beae541790c1845c19d947376f`. One GraphQL enqueue with an expected-head guard returned `QUEUED`, initially without a candidate head/base. No enqueue request was resent.

The later `merge_group.checks_requested` event created candidate `4f7a5a72b1e974577dec4a2154c96e5daad0636f`, atop trunk `0e953601b9aeea3630f7e02e3308c53d7cb5ac4a`. Its [workflow run 42544350945](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42544350945) succeeded. The event head SHA, Actions run SHA, `GITHUB_SHA`, actual checkout HEAD and check-run attachment all matched that candidate. Its single-parent graph and tree were retained; the candidate tree equaled the authored PR tree. It was a new checked candidate, distinct from both earlier PR SHAs.

No old successful release status existed on that candidate. The controller posted `pending` only there. A later observation at 01:13:41.972727Z still showed PR #5 open/unmerged, entry `AWAITING_CHECKS`, the same candidate, and the original trunk. Thus the successful observation job finished without a sleeping runner, while the separate status held admission to landing.

The controller then posted `success` only to that observed candidate SHA. The immediate read was still open/awaiting checks; a later read confirmed `mergedAt: 2026-11-09T01:14:09Z`, no queue entry, and the trunk **exactly equal to the previously checked candidate SHA**. The source head and authored archive stayed unchanged. A green job or the release acknowledgement alone was not treated as proof of landing.

## Group-only failure and ejection

[PR #6](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/6) targeted `exp/ci/single-group-failure/trunk`, ruleset `26821690`. Its authored tree already contained `.queue-experiment/FAIL_MERGE_GROUP` and a unique trial nonce. The ordinary PR check passed because that marker affects only merge-group events. Admission release statuses were posted on its exact head and PR test-merge SHA, then it was enqueued once.

Candidate `e21c969e40d7b5e57cb316bd986bf08f3e72931d` ran [workflow 42544352472](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42544352472). The actual checked-out candidate matched the event/run/check SHA and the authored tree, with the original trunk as its sole parent. The observer recorded `Synthetic failure marker present: .queue-experiment/FAIL_MERGE_GROUP` and failed immediately; artifact upload still succeeded.

The PR was removed from the queue and remained open/unmerged with its trunk unchanged. The actual GraphQL `RemovedFromMergeQueueEvent` records reason **`failed_checks`**, `beforeCommit` equal to that candidate, and timestamp **01:13:24Z**. This is provider evidence for check-driven ejection, rather than an inference from a timeout, a manual removal, or a source push raced against queue construction. No group release success was posted.

## Evidence, scope and current state

`run.py` uses the coordinator's shared lane helper, preserving write intents and exact receipts. `results.json` records both fixtures and their transitions. `evidence/actions/<run-id>/` contains exact event JSON and GitHub/checkout context for all four relevant runs; raw workflow logs, candidate commit metadata, check-run attachments, status responses, timelines, ruleset requests and ref snapshots are retained. The deployed workflow/script blobs match the local proposal exactly. `verify.py` checks these artifacts locally without replaying hosted effects; its output is `evidence/verification.json`.

The first attempt to collect a group ran before its Actions event existed and stopped with an explicit “read again without re-enqueueing” assertion. Later reads found the original admitted candidates; no mutation retry repaired that timing condition. The separate local workflow validation harness also corrected a root-commit parent assumption before completing ten offline executions. These are retained harness observations, not provider failures.

The last recorded states have no queue entry for either CI fixture: #5 merged, #6 ejected and open. Writes were confined to the CI fixture refs/PRs, their exact-trunk rulesets, admission/release statuses and queue entries. The source heads stayed unchanged; main, shared workflows, repository-wide settings, organization settings and other lanes' resources were untouched by this lane. Exact fixture rulesets and synthetic refs remain for inspection. These controls establish their observed queue traces and required-check attachments, not native-stack queue behavior, batching, every ejection policy, automatic retries or a guarantee against later provider writes.

The separately requested native, real-CI-only discriminator is documented in [NATIVE-METHODS.md](NATIVE-METHODS.md). Its three fresh method fixtures are separate from these two ordinary-PR controls.

*Authored by an AI agent acting on joshlf's behalf.*
