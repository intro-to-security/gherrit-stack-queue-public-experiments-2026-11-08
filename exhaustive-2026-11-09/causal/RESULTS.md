# Causal direct-merge evidence

The force-push event positive control passed. An earlier acknowledged marker
was subsequently rebased by native processing, with its content preserved. A
marker generated after terminal success and an observed suffix rewrite was
published successfully and remained the exact head through a 60-second window.
No acknowledged post-terminal marker was observed to change. Four immediate
post-terminal marker attempts were rejected by exact leases and remain frozen.
None of these observations establishes a future-write fence.

These observations are from the authorized public synthetic repository on
November 9, 2026. They establish the captured cases, not a future provider
ordering guarantee. `summary.json` supplies exact refs, trees, parents, event
fields and timestamps; `evidence/` retains requests, exclusive dispatch intents,
receipts and raw sanitized responses. No historical driver was executed. No
default branch, settings, workflow, queue or website operation was changed.

| Case | Resources | Observed outcome |
| --- | --- | --- |
| force-control | A #564, B #565; no group | One exact-lease sibling push succeeded. `HeadRefForcePushedEvent` recorded original B `91b679b1e524d79eb1184a860d42398ac36c40c1` → marker `395c1d662bc0ef00d0b172fe01ecb6e036b42754`, actor `User joshlf`, and the correct ref. |
| post-squash-1 | A #566, B #567, group #568 | A merged; B stayed open, changed base A → synthetic trunk, and changed parent to the landed trunk. Marker lease rejected stale information. |
| post-rebase-3 | A #569, B #570, C #571, D #572, group #573 | A merged; B/C/D stayed open and were rewritten into a chain above the landed trunk. Marker push was remotely rejected because D was at `7cc4ad3de9009002e3cd1950a7de9f80a182bfa4` while the request expected `cd36e1197abdbd0283f8666b82f5b6aa34b4b7ca`. |
| post-merge-1 | A #574, B #575, group #576 | A merged; B stayed open, retargeted and was rewritten above the landed merge commit. Marker lease rejected stale information. |
| post-squash-3 | A #580, B #581, C #582, D #583, group #584 | Three surviving suffix PRs were rewritten. The immediate post-terminal marker lease was rejected, as in squash1. |
| early-squash-3 | A #585, B #586, C #587, D #588, group #589 | An acknowledged marker published after admission/pending observation was subsequently force-rebased. The marker and native final trees are identical. |
| after-rewrite-squash-3 | A #590, B #591, C #592, D #593, group #594 | After captured terminal success and all native rewrite premises, a new marker was acknowledged and remained the exact head in the bounded 60-second window. |
| ordinary-sync-3 | A #595, B #596, C #597, D #598, group #599 | Official v0.3.0 skipped merged A, rebased B/C/D and made one acknowledged atomic explicit-lease push. Native group stayed unchanged; B/C/D stayed open. |

## What the control establishes

The first GraphQL observation after the positive-control push still showed the
old PR head and no force-push event, while the independently timed Git read saw
the marker. The next scheduled sample exposed the correct head and force event.
This validates the fields in this controlled path and demonstrates event/PR
visibility delay. It does not establish that every native rewrite emits such an
event, or that an absent event means no write occurred.

## Why the rejected markers do not establish post-terminal overwrites

In the four immediate cases, each marker object was created only after a
terminal `merged` response. Each was
based on a newly fetched suffix head and published with an explicit expected
old head. The marker object creation began approximately 0.18–0.21 seconds after
the terminal response ended. Every push was rejected; no acknowledgement of
marker publication exists. All four failures were retained and no write was
retried.

The rebase rejection is particularly informative: receive-pack reported a ref
lock/CAS mismatch, rather than the client's stale-information rejection. That
proves the server's update boundary encountered a different actual head from the
request's expectation. The experiment does not establish whether the earlier
Git advertisement/fetch was stale or the actual rewrite happened after the
terminal response. It therefore cannot supply the missing temporal premise.

Read-only reconciliation captured force events for the native rewrites and
automatic base-change events, with exact before/after heads. The native events
also report actor `User joshlf`; the actor field alone does not distinguish the
provider's work on behalf of the initiating user from a separate user push.
The isolated fixture and retained sole-writer operation log are additional
attribution evidence. Event `createdAt` describes the event object and is not
used as the exact ref-mutation time.

All three methods did rewrite suffix refs in these current fixtures. An older
public preview report that direct API merges only retargeted a suffix is not a
description of these captured outcomes. The differing fixture scope and date
remain material; this is not a universal API promise.

## A captured earlier rewrite preserved the marker content

In `early-squash-3`, the marker push was acknowledged during
14:01:34.760601–36.170457Z. Terminal success was received at 14:01:39.932580Z.
The force event records marker
`7f0cb6d75feefdb7e76feb3b48df83bdb6c23c37` → native head
`6f934284e5fa49f477f6916a38b5c03d936e279d`. This is an actual transition from
the uniquely published marker, supported by the event's before/after fields and
the sole-writer fixture. The marker existed before the terminal response, so the
transition does not establish a post-terminal write.

Both immutable commits have tree
`2e8ae7266334605e2a7a1efd2c427aca90cb2b39`, and the final marker file retains
the exact unique value. This is a ref rewrite with content preservation, not
demonstrated data loss. `early-squash-3-marker-tree-and-headers.json` retains
the comparison and raw commit headers. The three-layer suffix length comparison
again rejected an immediate marker; increasing suffix length did not supply an
accepted post-terminal trial in that fixture.

## One post-terminal publication remained unchanged in its window

`after-rewrite-squash-3` first captured every suffix's changed Git ref, matching
PR projection, correct rewritten parent chain and force event from its initial
head. Those were the declared publication premises, not a settlement oracle.
The unique marker was created 3.376 seconds after the terminal receipt ended.
Its exact-lease push succeeded, publishing
`8be2c7aa1929d0c95650bbc6b17db1135f93dea4`. All seven scheduled observations
retained that exact head; the last Git read began 60.009 seconds after the push
acknowledgement. No captured force event has that marker as `beforeCommit`.

This establishes the successful finite sequence and its quiet observation
window. It does not turn prior rewrite visibility, a terminal UUID, multiple
coherent reads, or silence into a future-write exclusion guarantee.

## Actual official client sync completed

The pinned official v0.3.0 binary hash was rechecked. A child-only Unix HTTP
recorder was exercised against the actual binary's read-only `init` command in
a new local checkout: both repository-scoped GraphQL read queries were forwarded
with HTTP 200, while local tests demonstrate native HTTP write refusal and
credential/cookie omission. The recorder forwards upstream using normal TLS
certificate verification. No global certificate, trust, proxy or gh config was
changed.

Under grant003, actual `ordinary-sync-3` completed with the same recorded binary.
The CLI skipped merged A, rebased B/C/D and sent one atomic force push with
explicit per-ref leases and `pull.stacked`. All three final client trees equal
their preceding native trees; force events record each native-head → client-head
transition. Canonical PRs stayed open and group #599 retained merged A plus the
same B/C/D members. The 60-second observation window completed.

The Unix recorder retained all 12 CLI HTTP read requests and HTTP 200 responses.
It forwarded no HTTP mutation; no refusal or unknown request occurred. The CLI
recognized the existing group as already up to date. `ordinary-sync-summary.json`
retains exact dynamic push arguments, before/after heads, trees, events and read
intervals. This is an actual hosted client-sync control, not a mocked transport
test or provider ordering promise.

Eight local effect-boundary and recorder tests pass: unknown writes remain recorded and cannot
be redispatched, pushes need complete scoped leases, pending status cannot
authorize post-terminal generation, cross-fixture/settings mutations are
refused, and the CLI Git gate accepts only an atomic explicitly leased active
ref vector. The recorder tests exercise local HTTPS and Unix-socket read
forwarding, native write refusal and credential omission. These tests validate
local guard behavior, not provider semantics. Source snapshots and hashes are in
`source-snapshots/`; the two first-batch driver variants were reconstructed after
execution from retained edits and are explicitly labelled as such. Later
executed helper snapshots were captured before their dispatches.

`dispatch-audit.json` accounts for 40 hosted native API write
dispatches and 16 Git push dispatches across these eight cases. Every one has a
retained receipt, including the four rejected marker pushes. The audit found no
common GitHub credential-token pattern in the retained evidence. This is a
bounded file audit, not a claim that arbitrary secret formats are detectable.

The private bare repository passes `git fsck --full --no-reflogs`, with hooks
disabled. `authorship-verification.json` checks the final commit notices: all
checked authored/suffix commits retain one `Agent-authored-by` trailer, but the
provider-generated merge-method trunk commit `08b9f4f97fe272b20bfecb8b563097dccc1125e2`
contains none. Its source commits and PR body retain their notices. The frozen
trunk was not rewritten; this provider merge-message path did not preserve the
commit disclosure trailer.

*Authored by an AI agent acting on joshlf's behalf.*
