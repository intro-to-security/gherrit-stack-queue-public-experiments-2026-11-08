# Immediate dequeue failed; pending admission continued

One fresh native A/B fixture received a 202 pending admission receipt for B,
followed immediately by one GraphQL dequeue of B with no intervening poll. The
dequeue was rejected. The original UUID still reported pending on its next read,
then enqueued; both A/B entries were observed queued afterward.

The exact rejection named B's direct base A, rather than a generic not-queued
condition:

> No merge queue found for branch 'exp/edit/pending-admission-dequeue-1794187935360476000/A'

This failed call did not cancel the observed admission in this ordering. It does
not establish the internal cause of that routing/error or a general cancellation
contract. An upper-B dequeue after confirmed admission was not tested: cleanup
had already completed when that follow-up was suggested, and no second fixture
or requeue was created.

The fixture belongs to public repository
`intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08`, with
[A #34](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/34),
[B #35](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/35),
native group #36, and exact trunk
`exp/edit/pending-admission-dequeue-1794187935360476000/trunk`.
[`RESULTS.json`](RESULTS.json), [`state.json`](state.json), and
[`artifact-verification.json`](evidence/artifact-verification.json) retain the
full request/response identities, intervals and assertions. All times below are
UTC on November 9, 2026.

## Controlled preconditions

Both initial PRs reached CLEAN before the race. The exact trunk's active rule
required `queue-observe` and `experiment/queue-release`, with no bypass actors,
ALLGREEN, SQUASH, and queue builds zero. External success statuses were recorded
on the captured source heads and observed test-merge commits. The inherited
workflow remained unchanged; B retained the defensive merge-group failure marker.

Captured inputs were:

| Input | SHA |
| --- | --- |
| Trunk | `c487b874ed00f449b3be715d1fffcb9bc384bdd6` |
| A | `efe0e3c58d419d0c3fb7496439dcad0e7d46cc33` |
| Selected B | `7f07d3d2856d52906115d0faad892455e1079cbc` |

The queue was empty before the single admission call. The request supplied only
`merge_action: merge_queue` and selected B's exact `sha`, omitting direct-merge
method/message fields. Its receipt matched that selected SHA/action and recorded
`bypass_rules:false`.

## Exact client ordering

| Operation | Start–end | Observed result |
| --- | --- | --- |
| Enqueue B | 01:32:58.342164–58.668684 | HTTP 202, `pending`, UUID `530ad2cd-8178-4299-8d20-91eaf04b0e31` |
| Immediate dequeue B | 01:32:58.669138–58.976731 | HTTP 200 with GraphQL UNPROCESSABLE error above; null mutation result |
| First original-UUID poll | 01:32:58.984023–59.317912 | `pending` |
| Second original-UUID poll | 01:33:01.329048–01.591950 | `enqueued` |

The recorded monotonic gap between enqueue completion and dequeue intent was
0.446375 ms. This is a client timing measurement, not server arrival order or
the interval between provider state transitions. Raw source order and timestamps
confirm no request poll or queue read occurred between the 202 and dequeue.

Four subsequent cohorts observed A then B, positions 1/2, both QUEUED at their
original heads. Reported enqueue timestamps were 01:32:59Z for A and 01:33:00Z
for B. Candidate `headCommit`/`baseCommit` values were null in the build-zero
configuration. Both PRs stayed open/unmerged; native membership, source refs,
archives and trunk stayed unchanged. These observations do not distinguish why
the immediate upper-member dequeue resolved the direct base A.

## Known-membership cleanup

After actual A/B membership was confirmed, a separately labelled dequeue of
lower A #34 ran at 01:33:20.558241–22.293655. It returned without GraphQL errors.
The next queue read at 01:33:22.293998–23.170686 had zero entries and null queue
entries for both PRs. Final reads retained both open/unmerged canonical PRs,
unchanged heads, unchanged native membership, exact v1 archives and the original
trunk.

The old UUID still returned terminal `enqueued` after this cleanup. It describes
the completed admission result, not current queue membership. No admission or
dequeue write was blindly retried. The known rejected immediate-B operation and
the later acknowledged lower-A cleanup have distinct labels, targets and
confirmed state preconditions.

## Scope and retained failures

Only one fixture and one immediate race were run. An initial local syntax error
occurred before any execution or remote creation; its source and failure note
are retained. The corrected runner was syntax-checked before use. The 55 executed
case assertions passed; the dequeue rejection remains the recorded experimental
outcome rather than being relabelled as success.

This used the supported GraphQL dequeue mutation, not a guessed or hidden REST
cancellation endpoint. The inspected public async REST surface exposes admission
and result lookup; this experiment establishes neither an undiscovered cancel
operation nor a general dequeue-as-cancel promise. It demonstrates that this
failed immediate call left the one original admission progressing to observable
queued membership.

No merge-group dispatch, actual landing, upper-member dequeue after confirmed
admission, stale-selected-SHA rejection, provider settlement, or arbitrary-writer
fencing was established. No shared workflow, main, global setting, other lane,
sealed-case evidence or private organization membership was changed or inspected.
`git fsck --full --no-reflogs` succeeded; exact local author identities and the
required disclosure trailers were checked.

*Authored by an AI agent acting on joshlf's behalf.*
