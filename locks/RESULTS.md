# Queued membership and dequeue results

The native held-prefix experiment confirmed partial unstack and dependent dequeue
on this repository. Unstack released the unqueued suffix while retaining queued
members. Dequeuing the lower member removed both queued members. The original
async UUID still reported `enqueued` afterward; that receipt described admission,
not continued queue presence or landing.

Resources in the authorized public synthetic repository:
[PR #7 / A](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/7),
[PR #8 / B](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/8),
[PR #9 / C](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/9),
former stack **#10**, exact-trunk ruleset **26821752**. The fixture owns only
`exp/locks/queued-members/**` heads/archives and that exact trunk's ruleset.
The retained PRs are all open, unmerged, unqueued and unstacked.

## Observed transitions

| Step | Exact observation |
| --- | --- |
| Initial admission preflight | All three members reported CLEAN. Queue rule started with build concurrency 1, ALLGREEN, no bypass actors, and required `queue-observe` plus `experiment/queue-release`. |
| Native admission selecting B | PUT merge-async with captured B SHA and explicit `merge_action=merge_queue` returned 202. UUID `70ce4b4f-8a53-4c09-affb-1785fd245cd3` subsequently became terminal `enqueued`. |
| Held prefix | A/#7 and B/#8 had queue entries in order. C/#9 was not queued. All PRs remained open/unmerged; owned heads and trunk remained unchanged. |
| Unstack while A/B queued | HTTP 200 retained A/B in stack #10. C was released. The same A/B queue-entry IDs remained, and PR bases/heads were preserved. |
| Dequeue A | GraphQL `dequeuePullRequest(input:{id: <A PR node ID>})` succeeded. Both A and dependent B disappeared from the queue. C remained open and unqueued. |
| Re-read original UUID | It still returned terminal `enqueued` after both members had left the queue. |
| Eligible unstack after dequeue | HTTP 204 dissolved the residual stack; subsequent stack GET returned 404. All three PR objects and their bases/heads remained. |

No group release status was posted, and no landing was attempted. Dequeue was a
single new intent after admission had completed, not a blind retry or a claimed
cancellation of a still-pending background enqueue.

## Actual merge-group graph and hold

The fresh build=1 queue initially exposed null group head commits. During the
bounded observation it produced lower group head
`619ca82c4f51c60a9bd90ee410650a6b181a0778`; upper B still had no group head at the
recorded boundary. Null fields on early reads were therefore not evidence that
the fresh queue could never build.

The group's sole parent is trunk
`5c67ceea8a77f20b71b7a5cf762bc5bcda910f55`. Its tree equals authored A's tree and
contains A's change without B/C. The provisional squash message retained the
`Agent-authored-by` trailer. Its temporary queue ref was deleted after dequeue;
the commit was fetched and pinned locally at
`refs/experiment-inputs/queued-members-group-0`.

[Observer run 42544608573](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42544608573)
completed `queue-observe` successfully on that exact group SHA. Its downloaded
artifact contains the actual `merge_group.checks_requested` payload, checkout
SHA/tree/parents and workflow decision. The required manual release context was
absent from the group's status list, whose combined state remained pending.
Thus a passing observer check did not release the held group.

## Evidence and limits

`run.py` preserves setup and transitions. `evidence/` contains the exact ruleset,
Git push, PR/group/ref snapshots, queue reads, mutation receipts, UUID polls and
workflow artifact. `capture_group.py` retains the generated commit/tree/checks
and local object pin. `verify.py` reruns only local evidence assertions; all
checks pass in `VERIFICATION.json`, including unchanged owned refs, preserved PR
bases, partial membership, dependent removal and the terminal receipt's meaning.
No API intent lacks a recorded subprocess receipt.

This is one small native prefix on one host. It does not establish cancellation
of pending admission, automatic failure ejection, successful queue landing,
large-stack grouping, arbitrary concurrent-writer safety or a universal handoff
against delayed provider writes. Root and other lanes own separate controls.
All recorded repository data are public and synthetic; no private organization
membership/settings evidence was used. No organization-wide setting, shared
workflow or main branch was changed by this lane.

*Authored by an AI agent acting on joshlf's behalf.*
