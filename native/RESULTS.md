# Native prefix queue results

These are finite synthetic trials in
`intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08`, conducted on
November 8, 2026 in America/New_York. All queue rules used SQUASH, ALLGREEN,
one concurrent build, at most five merged entries, and no bypass actors unless
the explicitly described pause set the build limit to zero. They required the
real `queue-observe` check plus the controller's `experiment/queue-release`
status. The separate `ci/native-no-manual-gate/` control removes that manual
status requirement; consult it before generalizing the native ejection result.

## Admission and landing are separate outcomes

| Fixture | PRs and original native group | Recorded outcome |
| --- | --- | --- |
| Paused prefix | A #1, B #2, C #3; group #4 | Selecting B queued A/B. Enabling builds later produced a real group. A landed; B was removed with `invalid_merge_commit`; C remained outside the queue. |
| Initially enabled prefix | A #11, B #12, C #13; group #14 | A landed; B was removed with `invalid_merge_commit`. A new explicit request at B's rewritten hosted SHA subsequently landed B; C remained open. |
| Upper group failure | A #15, B #16; group #17 | A landed; initial B was removed with `invalid_merge_commit` before its intended failure control ran. After explicit requeue, B's actual merge-group check failed and it was removed with `failed_checks`. |
| Failing upper admission | A #21, B #22, C #23; group #24 | A/B checks were CLEAN and C's actual PR check failed. Selecting C failed admission, with every PR open/unmerged, all owned fixture refs unchanged and the observed queue empty. |

Every native admission attempt used REST `merge-async` with `merge_action: merge_queue`
and the exact selected SHA. Queue configuration chose the method; requests
omitted the direct-merge-only `merge_method` field. The three successfully admitted initial prefixes, and the later explicit
re-admissions, reached terminal **`enqueued`**; their original UUIDs still
returned that result after later landing or ejection. The failing-upper request
instead ended at **`failed`**. Queue emptiness likewise did not mean every selected PR had merged.
`removal-timelines.json` records the provider's exact removal reasons and times.

The initial paused admission is particularly clear: A/B entries existed with no
group head while all PR lifecycle states and owned refs remained unchanged.
After a confirmed zero-to-one ruleset update, the first forty polling observations of the same queue
still saw no group. The queue later dispatched actual run `42544721015`, and A
landed after its checked candidate was released. Do not report pause/resume as
permanently stuck. The initial runner printed `BUILT` without checking that a head
existed; `build-stage-interpretation.json` preserves and corrects that oracle
error, while the original source/result remain retained.

## What the native ejections establish

The provider removed the upper review as the lower member landed and the native
suffix was rewritten. Removal event times and PR/ref reads are separate
observations; they do not establish one atomic cross-resource transition or an
internal causal order. The reported reason was `invalid_merge_commit`, with no
candidate `beforeCommit`, rather than the deliberately injected failed check.
An early post-ejection snapshot also preceded the suffix's later observed
rewrite. It cannot be treated as settled hosted state.

The manual release context was posted only on captured admission revisions and
actual successful group candidates. A native rewrite can lose that custom
source status. This is a real fixture confound, so the ordinary manual-gate
trials alone cannot establish a universal native queue defect. The independent
ungated fixture requires only the real Actions check and posts no statuses; its
report records whether the same behavior occurred under that simpler setup.

In the initially enabled fixture, the controller explicitly observed B's prior
ejection and an empty queue, read its new hosted head, satisfied its new source
gate, and issued a **new** request. It did not retry a lost request or force-push
a branch. B retained its canonical PR and subsequently landed. In the failure
fixture, doing the same reached B's intended actual merge-group failure. The
initial invalid-candidate removal and the later failed-check removal are
different observations and must not be combined into one passing failure test.

## Exact retained outputs and limits

`artifact-verification.json` and `verify_artifacts.py` verify the four fixture
trunks against their expected landed trees, canonical PR/node identities,
head/ref agreement, exact v1 archive targets, and each remaining open layer's
binary patch, author tuple and message. The successful second landing retained
open canonical C and its own patch. Requeue created no authored archive and made
no client branch publication.

The failing-admission runner initially assumed REST would return
`merge_commit_sha`; it did not. That runner stopped before dispatching admission.
The corrected continuation verified the actual failing check on C's source SHA,
reused acknowledged setup effects and then sent the first admission request.
Both versions and the failure remain recorded. Other unsuccessful GraphQL field
lookups were read-only and are retained as such.

All final observed queues in this lane were empty. Remaining PRs were deliberately
kept open with source/history retained. Exact synthetic rules remain as fixtures.
These results support client handling of distinct admission, ejection, native
rewrite, re-admission and landing states. They do not prove future provider
settlement, safety for arbitrary concurrent writers, all queue configurations,
or correctness of a deployed GHerrit implementation.

*Authored by an AI agent acting on joshlf's behalf.*
