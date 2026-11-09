# Queued selected-head edit was rejected

The held native queue accepted captured B, but GitHub rejected the attempted
substantive B2 head update while B remained queued. The exact-lease atomic push
also rejected its new v2 archive. Both original queue entries remained; there was
no successful edit whose ejection/requeue behavior could be observed.

One explicit dequeue of lower A then removed both A/B entries. Both PRs remained
open and unmerged at their original heads. The old async UUID still returned
`enqueued` after the queue was empty: that receipt describes admission, not current
membership or eventual landing.

All resources belong to
`intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08` under
`exp/edit/selected-head-edit-1794187135707147000/**`. The fixture is
[A #18](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/18),
[B #19](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/19),
native group #20. The exact trunk is
`exp/edit/selected-head-edit-1794187135707147000/trunk`.
[`RESULTS.json`](RESULTS.json) and [`state.json`](state.json) retain full identities,
timing, receipts, cohorts, and checks. All times below are UTC on November 9, 2026.

## Preconditions and actual admission

The immutable bootstrap seed was
`3a9df32f515072950fac44b3f0bb9ab2b549170e`. The fixture inherited the read-only
`queue-observe` workflow unchanged. Rule #26821828 applied only to this exact
trunk, with no bypass actors, ALLGREEN, SQUASH, minimum one, maximum two, and
`max_entries_to_build: 0`. Its two required contexts were `queue-observe` and
`experiment/queue-release`; independent rule readback confirmed them.

The controller set the external status to success on both captured source heads
and both observed test-merge SHAs. Actual workflow checks completed successfully,
and both PRs reached `mergeStateStatus: CLEAN` before dispatch. B also contained
`.queue-experiment/FAIL_MERGE_GROUP` as a defensive marker; it does not fail the PR
event and would fail the observer's merge-group event. No shared workflow changed.

The one async PUT supplied only `merge_action: merge_queue` and B's exact SHA,
omitting `merge_method`. HTTP 202 returned pending UUID
`04cf64a9-76b6-4b8b-b819-8a7529285b67`, queue action, default method, matching
expected head, and `bypass_rules:false`. Polling reached terminal `enqueued`.

The 01:20:17.255564–19.438898 admission cohort recorded:

| PR | Position/state | Captured head |
| --- | --- | --- |
| A #18 | 1 / QUEUED | `421ebcc5668832bb51751412ba17a18a9e0d1ea1` |
| B #19 | 2 / QUEUED | `00d3461ec9cc92155ae2ff0a8f1327e982da48ad` |

Both queue entries had null candidate `headCommit`/`baseCommit`, consistent with
the build-zero setup. This case did not depend on merge-group dispatch or check
completion. The trunk stayed
`9e89e98c71df5d763887ff827af7c12e11555345`.

## The queued branch could not be amended

The proposed B2 was
`7c5baafffdc6f509a4f8996c87cfdd63835c8b7d`, directly parented by unchanged A.
Its only diff from old B was the fixture's `B.txt`, changing `B=1` to a substantive
B=2 value. The defensive merge-group marker remained identical. Exact headers,
messages, author identity and disclosure trailers are preserved locally, including
B2's pinned input ref and [`proposed-substantive-B2.patch`](evidence/proposed-substantive-B2.patch).

The single push ran at 01:20:19.558250–20.794479. It requested `--atomic` for B's
head and the new B/v2 tag, with an explicit old-B lease and an absence expectation
for the tag. Immediately before dispatch, the ref matched that old-B expectation.
The server rejected B with GH006:

> Branches that are queued for merging cannot be updated.

The accompanying message required dequeuing the associated PR before modification.
The tag was rejected with `atomic transaction failed`. The raw
[`push receipt`](evidence/substantive-B2-and-archive.push.json) retains exact args,
expected values, exit 1, stdout and full stderr. There was no push retry,
non-atomic fallback, bypass, settings change, or requeue.

The original driver's success assertion failed and remains in the evidence;
runner v1 and the failure trace were retained. Runner v2 added a separate
post-rejection observation/cleanup phase. It did not mark the failed assertion
passing or retry the rejected operation. The state records **96 assertions, 95
successful and one retained failed success oracle**.

Seven later cohorts, from 01:22:19.792941 through 01:23:00.371427, retained the
same A/B queue-entry IDs, positions and original heads. Both PRs stayed open and
unmerged, their refs and the trunk stayed unchanged, B/v1 retained its exact
original target, and B/v2 was absent. These are bounded samples; they do not fill
the gap before the first later cohort or establish server quiescence.

## Cleanup and the old receipt

Cleanup made one `dequeuePullRequest` mutation using lower A's PR node ID in the
input `id` field, with `clientMutationId` as the requested payload field. The
mutation returned without GraphQL errors. Its next queue read, at
01:23:02.669759–03.312428, had zero entries and null per-PR queue entries for both
A and B. Final reads retained the native A/B membership, canonical identities,
original heads, open/unmerged lifecycle, original archives and unchanged trunk.
No rule was weakened or removed to force this result.

The old UUID returned `enqueued` both after rejection and after this acknowledged
dequeue/empty-queue observation. It did not become a live indicator of queue
membership. This is expected to be read as a terminal admission result, not as an
armed request or proof of landing.

## What this resolves and what it does not

The expected selected SHA matched at admission. A later substantive forced push,
despite a matching ref lease, was blocked by the observed queued-branch guard.
Consequently, this case does **not** test queue ejection after a successful
selected-head edit, stale-SHA admission rejection, or an all-prefix snapshot
guard. Dequeueing lower A did remove the queued upper B in this fixture, but this
is one acknowledged cleanup sequence, not a general cancellation fence.

Build-zero operation, null candidate commits, and the unlanded trunk mean that
merge-group checks, dispatch, and actual queue landing remain outside this case.
There was no unknown write retry, and no inference that finite stable samples or
an empty queue settle every possible delayed provider effect.

[`artifact-verification.json`](evidence/artifact-verification.json) checks exact
source/B2 authorship and trailers, the single-file substantive diff, admitted and
later entry identities, original PR/head/archive retention, the single lower
dequeue and empty queue, and `git fsck` success. No main, shared workflow,
repository-wide setting, unrelated lane, sealed-case data, or private organization
membership was changed or inspected.

*Authored by an AI agent acting on joshlf's behalf.*
