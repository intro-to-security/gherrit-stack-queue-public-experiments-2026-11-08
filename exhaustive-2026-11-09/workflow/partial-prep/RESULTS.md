# Public B-success/C-conflict retained the completed prefix

The real public sequential composition produced the intended mixed outcome.
B PR [#658](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/658)
rebased successfully onto advanced A; the separate C
[#659](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/659)
request was rejected with `PullRequest::RebaseConflictError`. B retained its new
head and exact original own patch, while C stayed at its original head. Native
group #660 retained canonical open A #657, B #658 and C #659. All nine branch,
initial source and authored archive refs matched the expected final vector.

| Effect | Receipt and independent result |
| --- | --- |
| B REBASE | November 9, 2026, 16:53:29.947478–32.799988 UTC; HTTP 200, GraphQL success, gh exit 0. Actual head `57a275d012a64f38fdce84fa88d46d8e9e43a20a`. |
| B usable result | Its sole parent is advanced A `a8a39b61ad98ac6987183198ea308400ca507ebc`; actual/expected tree is `ae9cd4efa5e78789c8080481f3c5a835bc0d7770`. Its `b.txt` patch exactly equals original B's patch. The local retention/checkpoint preceded C. |
| C REBASE | 16:53:41.048814–41.761949 UTC; HTTP 200 with GraphQL `UNPROCESSABLE`, `updatePullRequestBranch:null`, and `PullRequest::RebaseConflictError`; gh exit 1 is the retained semantic rejection. |
| C and retained prefix | C remained `dca811f5d210b004f6229ea1134f3fb49f1cba44`. Three post-rejection read cohorts and a separate 16:55:20 UTC read confirmed new B, unchanged C, exact source/archives and unchanged canonical identity/order. |

`continuation-001/RESULTS.json` retains the full captured bases, selected heads,
requests, receipts, B checkpoint and observations. `PATCH-CHECK.json` independently
checks actual parents, trees, patches, membership, source/archive vector and Git
object integrity. B's force-push event names exact original head
`74cd012a960d3525e00727be30dbfd6fc0b170b5` and new head `57a275d…`, actor `joshlf`;
its creation timestamp is not used as the physical ref-write time.

The initial separately granted run is retained unchanged in `fixture/`. It made
two leased atomic pushes, three PRs and one group, then stopped before sending
either update because an added base-OID equality premise did not hold. A's
actual Git ref and own PR head exposed advanced A, while B's REST base SHA and
GraphQL baseRefOid still exposed old A. That was a failed client prerequisite,
not a rejected B request or evidence that public REBASE was unavailable.

Root separately reviewed a known-not-sent continuation, binding the original
frozen case, freeze, six matching write receipts, zero old update intents and
exact sources. Only the two new B/C updates were permitted, in a separate
`continuation-001/` journal and private Git copy. The original freeze was not
cleared, and its case, audit and captured source hashes remain unchanged.

The continuation kept exact selected heads, canonical IDs, head/base names,
native membership and the full actual nine-ref vector as prerequisites. It
recorded base OIDs without requiring equality to the current named-parent ref.
Before B those projections still named old A; B's actual result nevertheless
has advanced A as its sole parent. Final reads showed the updated B and C base
OIDs. This does not establish the cause, timing or promised update ordering of
those projections, and the request has no expected-base parameter.

`MUTATION-AUDIT.json` accounts for exactly two new update requests, each with a
durable exclusive intent, exact payload and response receipt. Across both grants
there were two Git pushes, three PR creates, one group create and two selected
REBASE requests. No write was repeated, repaired or unacknowledged. The expected
C rejection leaves the new context frozen; all later work was read-only. There
was no main, setting, workflow, queue, async-merge request, old-scope or cleanup effect.

Six initial offline controls and four continuation controls passed before their
respective dispatches. The local conflict control proved B's unchanged patch and
C's conflicting edit. Final Git fsck passed with hooks disabled, and authored
inputs plus native B retain one required disclosure trailer. These checks cover
this experimental fixture; they do not establish production durability.

This supplies the previously missing hosted partial-failure trace for two public
selected-member requests. It does not make them one transaction, undo the
completed B prefix, resolve C, cancel earlier writers or establish a future
suffix-write fence. No further write, cleanup or background-worker obligation
remains. All refs, PRs/group, source/archive objects, both failures/freezes,
grants, code snapshots and sanitized raw evidence remain available for audit.

*Authored by an AI agent acting on joshlf's behalf.*
