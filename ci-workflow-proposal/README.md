# Proposed queue observation workflow

This is a local-only proposal for `intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08`. It has not been deployed. The coordinator owns repository creation, workflows, rules and remote effects.

Copy `.github/workflows/queue-observe.yml` and `.github/scripts/queue_observe.py` into the coordinator's bootstrap. The workflow listens to unfiltered PR `opened`, `synchronize`, `reopened` and `stacked`, plus merge-group `checks_requested`. Its stable check-run name is **`queue-observe`** for both event classes. It checks out exactly `github.sha`, records the unchanged event JSON, a whitelist of GitHub variables, workflow/script blob IDs, and the actual checkout SHA, tree, parents and graph. A merge-group run also checks that its payload's `head_sha` equals checkout HEAD. Artifact upload runs after a synthetic failure. No credentials are persisted, printed or placed in the artifact; workflow permissions are limited to `contents: read`.

The checkout and artifact-upload action SHAs are copied verbatim from the first repository's already exercised bootstrap workflow: `11d5960a326750d5838078e36cf38b85af677262` and `ea165f8d65b6e75b540449e92b4886f43607fa02`. There is no mutable action tag, sleep job, cancellation group, status writer or approval job.

## Immediate synthetic controls

| Tracked marker in the checked-out commit | PR check | Merge-group check |
| --- | --- | --- |
| Neither marker | Pass | Pass |
| `.queue-experiment/FAIL_PR` | Fail immediately | Pass |
| `.queue-experiment/FAIL_MERGE_GROUP` | Pass | Fail immediately |

Marker presence is read from the Git tree; no marker text is executed or interpreted. Both markers may exist, causing each event class to fail for its own marker. The five-minute job timeout bounds provisioning/action failures; successful observation work itself has no delay loop.

To test check-driven queue failure, commit `FAIL_MERGE_GROUP` before enqueueing. The PR check passes, while every candidate merge-group tree containing that marker fails the same required `queue-observe` check. This avoids racing a later branch push against queue admission. Save every resulting group event, since batching or retry rules may rebuild groups before a PR is finally ejected. Use fresh fixtures for positive and failure paths rather than deleting the marker while a group is pending.

## Hold a group without a sleeping Actions job

Require both **`queue-observe`** and the separate commit-status context **`experiment/queue-release`** on the exact experimental trunk. The release context must accept the coordinator's status source; binding it only to the GitHub Actions app would exclude a PAT-created commit status. The workflow never produces a check or status with the release name.

Before enqueueing, satisfy the release context on each PR's exact current head and, where required by observed PR gating, its current synthetic merge SHA. These are admission statuses, not permission to release a later queue candidate. For each `merge_group.checks_requested`, retain `head_ref`, `head_sha`, `base_ref` and `base_sha` from the event, then inspect check/status attachment at that **actual group `head_sha`**. The missing release context holds a fresh group; the coordinator can post `pending` there to make the held state explicit. No Actions runner remains occupied while it is held.

For the positive path, post `success` only to the observed group SHA after its exact PR membership, trunk, candidate tree and `queue-observe` success have been recorded. For a status-driven failure control, post `failure` to that same group SHA. A removal/unstack experiment can instead leave the status pending while the coordinator performs its explicitly scoped queue operation and observes the result. A recreated group is a new candidate requiring another observation; do not transfer release to a guessed branch head or an old event's SHA.

Use a unique committed trial nonce, such as `.queue-experiment/trial-id`, for each trial. Before relying on a held candidate, confirm its group SHA has no old successful release context: statuses belong to commit SHAs and cannot distinguish separate queue attempts that reuse the same SHA. A new label or PR number alone does not reset those statuses. Do not release the same candidate in more than one control. Keep the group's response timeout long enough to record the held state, monitor it, and retain any timeout/retry/ejection trace; no pending group should be abandoned.

The workflow's artifact confirms what the job actually evaluated. A green PR check, or a check at a PR head, does not establish success of the queue's new candidate. A successful finite queue trace will still not establish a provider guarantee against later writes.

*Authored by an AI agent acting on joshlf's behalf.*
