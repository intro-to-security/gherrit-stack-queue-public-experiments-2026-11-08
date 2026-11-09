# Native stacks and merge queues: experimental results

The public organization repository enabled the queue tests that the earlier
repositories could not run. These synthetic trials establish actual queue
admission, merge-group checks and landing, failure/ejection, queued unstack,
head-update rejection and a pending-admission/dequeue race. The important new
finding is **method-specific native prefix behavior**: MERGE landed both queued
members, while SQUASH and REBASE landed the lower member and removed the upper
with `invalid_merge_commit` in the tested fixtures.

The repository is
[intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08).
The user explicitly authorized this separate public repository for synthetic
tests. No private membership survey, private repository contents, production
GHerrit source or organization-wide setting belongs to this publication.
The trials ran November 8, 2026 in America/New_York; raw timestamps use UTC and
therefore include November 9. REST calls used API version `2026-03-10`.

## Native prefix landing depends on the queue method

Three fresh two-member native stacks used otherwise matching queue settings:
ALLGREEN, one concurrent build, at most five merged entries, no bypass actors,
and only the real Actions `queue-observe` required check. These controls had no
failure markers, manual status context or status writes. Both source PRs were
CLEAN before one selected-B async request queued A and B.

| Queue method | PRs | Observed result after the original admission |
| --- | --- | --- |
| [SQUASH](ci/native-no-manual-gate/RESULTS.md) | A #25, B #26 | A merged; B was removed with `invalid_merge_commit`, rewritten and later CLEAN, but remained open and unqueued. |
| [MERGE](ci/native-no-manual-gate-merge/RESULTS.md) | A #28, B #29 | Both merged; both queue entries disappeared. B's source head stayed at its original SHA. |
| [REBASE](ci/native-no-manual-gate-rebase/RESULTS.md) | A #31, B #32 | A merged; B was removed with `invalid_merge_commit` and rewritten, then became CLEAN while remaining open and unqueued. |

See the [method comparison and independent checks](ci/NATIVE-METHODS.md).
These are one fresh control per method, not a universal method guarantee or a
production recommendation. Their exact graphs, rules, checks and subsequent
observations are retained under `ci/native-no-manual-gate*`. The distinction
survived removing the artificial release check used in the earlier controlled
fixtures. Thus that manual check alone does not explain the SQUASH result.
The experiments do not establish GitHub's internal cause, future rollout behavior
or all configurations.

A separate controlled SQUASH case preserved canonical B #12 through its ejection
and native rewrite. A **new explicit request at the new hosted head** then landed
B, while C #13 stayed open with its own patch and exact old archive. That was not
a resend of an unknown admission or a client branch force-push. See the
[native results](native/RESULTS.md).

## Admission is a receipt, not completion of the prefix

Successful native REST admission cases returned 202 with a UUID and later
polled terminal `enqueued`; actual queue entries showed the requested lower
prefix. The failing-upper admission control instead polled terminal `failed`. With builds
paused, all PRs remained open and owned refs stayed unchanged.

The same original UUID continued to return `enqueued` after later merges,
ejections and explicit removals. The client must read actual queue membership,
PR lifecycle and Git refs separately. An empty queue can mean that one member
landed and another was ejected. It does not mean the selected prefix completed.

The first zero-to-one build-resume observation saw no group during forty polling observations of the same queue; the queue later dispatched a real merge-group workflow. The retained
runner's premature `BUILT` label was an oracle error, corrected explicitly.
Do not turn the early interval into a permanent-stall claim. See
[native timing and limits](native/RESULTS.md).

## Real merge-group checks and failure paths

An ordinary PR control passed its actual group check and stayed held by the
separate `experiment/queue-release` context. Releasing that exact checked group
SHA landed the PR. The final trunk equaled the checked candidate commit.

Another ordinary PR passed PR checks but failed only on `merge_group` because
of a committed synthetic marker. It was ejected, remained open, and left the
trunk unchanged. GitHub's removal reason was `failed_checks`. In the native
failure case, the upper review first hit `invalid_merge_commit` as A landed;
only its later explicit requeue reached the intended actual group failure.
These are different failure paths, both retained.

The observation workflow listened to `pull_request` activity including
`stacked`, and `merge_group: checks_requested`, with one stable check name.
Downloaded event artifacts bind event head, workflow run, `GITHUB_SHA`, checkout
HEAD, tree, parents and check-run attachment. The SQUASH candidates were
single-parent commits atop their event base. Other methods' actual graphs are
recorded separately; a group SHA or graph from one event/method must not stand
in for another. See [ordinary CI results](ci/RESULTS.md) and
`merge-group-artifacts/`.

A failing upper PR check also rejected native whole-prefix admission before
any observed landing: lower A/B were CLEAN, C's actual check failed, the request
failed with that required-check reason, all PRs stayed open, owned fixture refs stayed
unchanged and the observed queue was empty. See [native admission
control](native/RESULTS.md).

## Queued members have concrete lifecycle restrictions

**Unstack is a partial release.** With A #7 and B #8 queued and C #9 unqueued,
unstack returned 200, retained A/B in the original group and released C. One
dequeue of lower A removed both A and dependent B. A subsequent unstack returned
204 and dissolved the remaining group. Every PR stayed open/unmerged and owned
refs were unchanged. See [locks results](locks/RESULTS.md).

**Queued source branches rejected client edits.** An exact-lease atomic push
trying to replace queued B #19 and add its v2 archive failed with GH006:
queued branches cannot be updated until the associated PR is dequeued. The
atomic transaction published neither the head nor the archive. Both entries
kept their original heads during later observations; cleanup removed them.
This is stronger protection than the earlier direct-merge race, but is still
the observed queued-state restriction, not a guarantee covering every future
native write. See [edit results](edit/RESULTS.md).

**A dequeue attempt did not cancel pending admission.** In one fresh fixture,
the controller received 202 and immediately sent a selected-B dequeue, with no
intervening read. GitHub rejected it because no queue was found for B's direct
base branch. The original UUID then still polled `pending`, and later became
`enqueued` with both entries present. Cleanup dequeued confirmed queued A and
emptied the queue. This does not isolate timing from upper-PR routing behavior;
dequeue of upper B after confirmed admission was not tested. It does show that
this rejected call did not stop the pending operation. There is no dedicated
cancel endpoint in the inspected async REST surface. See
[pending-admission race](edit/pending-cancel/RESULTS.md).

## What this changes for the GHerrit design

Queue admission, queued ownership, removal, native rewriting, re-admission and
landing need separate observations. Treating terminal `enqueued` as full
success would hide the observed upper ejections. A selected-head guard does not
turn a prefix into an immutable all-member snapshot, although the queued-branch
push rejection provides an actual provider-enforced restriction while queued.

Queue method is a consequential policy choice. The successful MERGE control and
SQUASH/REBASE ejections prevent treating all native queue configurations as
interchangeable. The experiment does not select a method for GHerrit or justify
silently requeueing changed work: current hosted heads, rule/check state and
author intent still matter.

Provider handoff remains unresolved. Some post-ejection snapshots returned old
PR heads while later Git-ref reads showed native rewrites. Neither queue
emptiness, a terminal receipt nor a finite run of coherent reads proves that no
later provider write remains. A deliberate continuation in a disposable fixture
is not a production admission rule.

Actual native UI receipt capture, website Rebase stack, independent human
walkthroughs, broader rule/review/signature combinations, lost network responses
and general concurrent-writer safety remain outside this campaign. Successful
hosted traces validate their own conditions, not deployed GHerrit code.

## Reusable evidence and retained state

Reports, original harnesses, exact fixture bindings, decisive receipts and
comparison summaries are retained here and locally. Full local transcripts,
downloaded artifacts and Git stores retain additional depth. Source scripts
bind to this exact repository and deliberately stop on existing unresolved
intents; they are experiment records, not a general-purpose queue client.

Failed assumptions and runner versions remain visible. Real local workflow
validation exercised pass/fail markers and head-attachment guards. Independent
audits checked native identities, per-layer patches, exact archive targets,
receipt meaning and timing qualifications. Exact synthetic refs, PRs and trunk
rules remain available for inspection.

The workflow tokens stayed read-only, and Actions PR-create/approve remained
disabled. No scheduled workflow, bot review or organization-wide setting was
introduced. Final verification records current visibility, permissions, queue
entries and completed runs; all twelve observed fixture queues were empty and
all seventy listed workflow runs were completed.

*Authored by an AI agent acting on joshlf's behalf.*
