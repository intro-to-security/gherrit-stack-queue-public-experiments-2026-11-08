# A-stale initiation: independent remote outcome capture

Three read-only cohorts retained all seven expected refs, canonical open PRs 664/665 in group 666, A-v2's marker and full range, and both original v1 ranges. Selected B stayed at B0. No rebase effect was observed in these cohorts. The permitted minimized `NETWORK-A.json` records one selected POST carrying old A0 and unchanged selected B0, with HTTP 409 and `{"error":"Stack contents have changed"}`. Raw HAR/debugger evidence was not opened or rederived by this observer.

## The actual A-only protocol basis

This case did **not** create archive-a-v2 during the paused advance. Root first precreated it before browser load under the separate prearchive grant. `READY-A-ARCHIVED.json` is the seven-ref pre-pause basis, with archive-a-v2 already at A2. The original READY and its older planned `marker_scope` remain historical intent; that inherited text is superseded for this execution by the archived-ready scope and the root's separately granted A-only controller. The original advance-a action was unused.

Comparing archived READY with `A-ADVANCED.json` proves that the ref-name sets are identical and only the **existing A head** changed A0→A2. B and the preexisting A-v2 archive did not change. The observer enforces this distinction before any remote query; it invokes no fixture controller and changes no original evidence/store.

## Actual cohorts

Offsets are relative to this observer, not to the initiating POST. Parallel REST/ref reads and the later exact fetch have individual timestamps; a cohort is not one atomic snapshot.

| Offset | UTC start | UTC finish |
| --- | --- | --- |
| 0 seconds | 2026-11-09 18:33:12.235138 | 18:33:13.113348 |
| 10 seconds | 18:33:22.240221 | 18:33:23.047961 |
| 30 seconds | 18:33:42.240337 | 18:33:43.107699 |

Each actual `ls-remote` vector and each independently fetched vector exactly matched these branch refs:

| Suffix after `refs/heads/exh-1109-ui-stale-debug-a-5949ea0a29-` | OID |
| --- | --- |
| trunk | `72a17fe9c84d215d5dcf120dad2b1e8d0c5ad171` |
| a | `3f7c0881bb913b772784842cf7204d4640737bea` |
| b | `0d139c885ed973bb1a932e8c6771abd056d93f55` |
| source-v1 | `0d139c885ed973bb1a932e8c6771abd056d93f55` |
| archive-a-v1 | `843359d9d586da7f11a03ef4ff98bf746cbac233` |
| archive-b-v1 | `0d139c885ed973bb1a932e8c6771abd056d93f55` |
| archive-a-v2 | `3f7c0881bb913b772784842cf7204d4640737bea` |

REST/native membership retained canonical A node `PR_kwDOVnhIZ88AAAABN6qZIw`, B node `PR_kwDOVnhIZ88AAAABN6qaAA`, group node `PRS_kwDOVnhIZ84AMb3h`, ordered [664,665], and open/unmerged state. REST heads agreed with actual refs.

Both associated-base discrepancies are preserved in all cohorts: A's REST base stayed T0 `e18576ec11ecd2ec261341219eedbed1d1b2ac2b`, while its actual named trunk was T1 `72a17fe…`; B's REST base stayed A0 `843359d…`, while the actual named A head was A2 `3f7c088…`. These observations are not silently normalized or treated as accepted integration inputs.

## Ranges, graph and marker

Original A-v1 is `e18576ec11ecd2ec261341219eedbed1d1b2ac2b..843359d9d586da7f11a03ef4ff98bf746cbac233`; original B-v1 is `843359d9d586da7f11a03ef4ff98bf746cbac233..0d139c885ed973bb1a932e8c6771abd056d93f55`. Their full retained patches add only a.txt and b.txt respectively.

A-v2 is exactly `e18576ec11ecd2ec261341219eedbed1d1b2ac2b..3f7c0881bb913b772784842cf7204d4640737bea`. Its full-index/binary-capable patch adds a.txt and late-a-marker.txt; A0→A2 adds only the marker. Current A contains exactly `Post-pause lower-A publication marker exh-1109-ui-stale-debug-a-5949ea0a29` plus newline. A2 still has A0 as parent; unchanged B0 still has A0 as parent. B's old range is retained independently of its newly advanced named parent; no B rebase or marker import is asserted.

Every unique fetched tip's full commit body recomputes to its Git object identity and matches the frozen input; parent/tree/entry records are retained. Local Git fsck passed. `verify.py` checks the retained graph/ranges/marker and the only-A vector difference without another remote query.

## Terminal status and limits

`check_network.py` independently correlates the minimized root-retained request map with frozen A0/B0 and confirms its 409/error response. The root's causal-order/debugger account remains separate evidence; this observer did not derive physical send time from `HAR.startedDateTime`, inspect raw HAR, or operate Chrome. Root's minimized record also reports the generic network error and A/B Skipped.

The initiating effect has a **known 409 rejection in the minimized network record**, with independently unchanged sampled graph/content afterward. This is not evidence that no server job ever existed, of continuous silence, cancellation, public API compatibility, or a future-write fence. The fresh-map control is root-owned and outside this observer's scope.

The observer completed nine REST GETs, three exact-ref listings and three seven-ref fetches into a new independent bare store, with 21 owned local observation refs. It sent no native request or remote mutation, changed no fixture store or existing Git configuration, and has no pending mutating acknowledgement or cleanup. Inputs/source/command receipts, `capture-001/RESULTS.json`, `CHECKS.json`, `NETWORK-CHECK.json` and the source manifest are retained. Local object stores are local evidence, excluded from the source-only manifest.

*Authored by an AI agent acting on joshlf's behalf.*
