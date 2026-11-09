# Protocol and native API follow-up results

Real unacknowledged requests produced PR, comment, base, membership and merge
effects. The 500 ms no-read variants expose positive recovery evidence that the
immediate-close variants did not. Separate creation requests for 99 and 100 real
PRs returned HTTP 504 and 502 while nevertheless creating the intended groups.
One subsequent blind retry in the boundary harness violated the plan; its effects
and correction are retained.

These are synthetic observations from November 8, 2026 in America/New_York
(November 9 in the retained UTC timestamps), using API version `2026-03-10` in
`joshlf/gherrit-native-stack-experiments-2026-11-08`. Only `exp/fu2/protocol/**` resources were mutated. No repository
settings or main branch changed.

## Actual response-loss experiments

Each fault persisted intent, sent manually framed HTTP/1.1 over standard-library
TLS, then closed the socket without reading an HTTP status or response. Complete
requests were sent for seven operations per variant; the eighth deliberately
omitted one body byte. A second variant held the connection for 500 ms after send
completion, still without any HTTP read. Each used new identities. All 16 client
decisions retained the write as unknown and prohibited resend/overlap **before**
the first separate read-only oracle request. All 16 deliberate cuts were sent
once; none was retried or followed by another controller write to its fixture.

TLS send completion means the local TLS transport accepted the recorded byte
count. It does not establish remote receipt or application. During a hold the
server might send a response into a buffer; the client never read it. These
cases therefore establish missing client acknowledgement and observed effects,
not the server's exact execution/response time or post-terminal quiescence.

| Case | Immediate close | Fresh 500 ms hold, still no HTTP read |
| --- | --- | --- |
| P-T01 PR creation | No matching PR in three bounded reads | [PR #168](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/168) matched exact fresh head/base/body |
| P-T02 comment creation | No matching comment in three reads | [Comment 6732137323](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/169#issuecomment-6732137323) matched the unique body |
| P-T03 base PATCH | Original base remained | Exact new base ref observed; head unchanged |
| P-T04 stack creation | No group observed | Group #173 with exact ordered PRs [171, 172] |
| P-T05 append | Original two members remained | Exact ordered members [174, 175, 176] |
| P-T06 unstack | Both memberships remained; group GET 200 | Both memberships absent; group GET 404; client dispatch deliberately remains unresolved |
| P-T07 async direct merge | Both PRs stayed open; trunk unchanged in bounded window | Both PRs observed merged; trunk tree exactly matched expected tree |
| P-T08 truncated request control | No matching PR | No matching PR |

P-T07-H500 knew neither a UUID nor the acceptance status and never resubmitted
the merge request. Its observed final trunk tree was
`51b693fb98da14dba61e0648cee858edf82ec488`, exactly the authored upper tree. This establishes
the resulting tree in the fresh sole-writer fixture, not a general handoff fence.

P-T09 used the same manual TLS framing and in-memory authentication but read the
full response: repository GET returned 200, fresh comment POST returned 201, and
an independent GET found that exact comment. This validates the transport path;
it does not identify why immediate-close requests had no observed effects.

Positive object/membership/base transitions are attributable here because the
fixture has one controller and fresh identities. That premise does not become
provider idempotency, field ownership or fencing for multiple writers. Membership
absence and repeated quiet reads do not prove that an older request cannot act
later. All affected resources remain retained without further controller edits.

## Actual size boundaries and natural server errors

Empty and singleton create requests returned 422. Two real linked PRs returned
201, were independently read back, and were released with 204 followed by GET
404. The original create with 101 real PRs returned 422 explicitly for 101 items.

The first create with 99 real PRs returned 504 after about 11 seconds. Read-only
reconciliation found group 330 with exactly the intended 99 ordered members. The
following creation with 100 PRs and repeated creation with 99 both returned 422
for existing membership. They are contaminated capacity evidence and are excluded. The latter
was a semantic blind retry even though its evidence label differed. Group 330 and
the original unknown intent were then retained without further controller edits.

Two fresh disjoint fixtures replace that failed capacity premise:

- P-B01-F100 created 100 distinct linked PRs and sent exactly one direct creation.
  It returned 502. The server response did not settle its effects. Read-only
  reconciliation observed group #461: 100 members in the exact intended order. No later mutation touched this fixture.
- P-B02-F101 created 101 different linked PRs, registered the first two with an
  acknowledged response, then appended batches of at most eight to 98, followed
  by separate 99/100/101 probes. Each response had exact-order readback. No old
  group 330 identity or logical create intent was replayed.

| Requested total after append | HTTP | Observed member count | Exact intended prefix |
| --- | --- | --- | --- |
| 98 | 200 | 98 | True |
| 99 | 200 | 99 | True |
| 100 | 200 | 100 | True |
| 101 | 422 | 100 | True |

The table records the actual tested membership boundary. The schema limits request-array size separately; these results do not establish behavior outside the tested totals.
The append to 101 was rejected explicitly for exceeding the maximum stack size;
the existing 100 members remained in their exact order.

No bulk group was merged or queued. These cases test registration and membership,
not landing, queue behavior or a liveness promise for a large group.

The [pinned primary OpenAPI source](https://raw.githubusercontent.com/github/rest-api-description/2f8f80e47ea4d3292cf4e37ba9d9b25475e06140/descriptions/api.github.com/api.github.com.json) specifies 2–100
items for a create request and 1–100 for one append request. Request-array bounds
and total group capacity are separate claims. Schema excerpts and the full-source
hash are retained in `sources/openapi-selected.json`.
The pinned upstream license is preserved verbatim in
`sources/upstream-rest-api-description-LICENSE.md`, with source URLs and hashes
in `sources/upstream-provenance.json`.

## Order and lifecycle controls

Duplicate members, reversed order, a skipped parent/wrong base, a nonexistent PR
and already-member registration all returned 422. A valid linked control
registered successfully. Closed-upper registration returned 422; reopening
returned 200 and valid registration then succeeded. Deleting the exact tagged
upper head closed that PR unmerged; registration returned 422. The original object
and authored tag remain retained. These are current lifecycle observations, not
promises that every closure or head deletion is recoverable.

Prior resolved evidence was reused rather than replayed for legacy synchronous
merge rejection, normal unstack, duplicate membership, completed-group reopening,
atomic publication, selected-head races and structural parking hazards. The
source hashes and scope limits are in `reused-evidence.json` (P-R01).

## Harness corrections and verification

The original boundary harness treated a received 5xx as though its mutation
effects were settled. This was wrong. Its later creation with 100 PRs and blind
repeated creation with 99 are retained in
`evidence/boundary-driver-deviation.json`; no success
label or raw receipt was rewritten. The corrected harness persists a 5xx write as
unknown and raises before the next mutation. A local fake-transport test verifies
the caller stops, unknown evidence remains, and the recorded intent cannot cause
a second transport dispatch. This checks the harness guard, not GitHub semantics.
Pre-fix source files match their recorded pre-execution hashes in `sources/`.

The first P-T06 interpretation also had an unconditional expected-absence phrase
despite its actual observations retaining membership. Its original and corrected
interpretations remain in `evidence/interpretation-corrections.json`; the raw
observations did not change.

The retained UTC and monotonic records cannot be treated as one coherent
aggregate clock. For example, the records at UTC `04:17:15.028786` / monotonic
`82.618812166` and UTC `04:20:14.026731` / monotonic `82.621309541` differ by
178.997945 seconds in their UTC timestamps but only 0.002497375 in their monotonic
readings. The retained metadata does not establish the cause or the clock
origins. The derived audit sorts UTC timestamps for its observed minimum and
uses same-client monotonic readings for cut/oracle ordering. Prior report and
derived-audit wording is preserved under
`report-corrections/clock-compatibility-2026-11-09/`; the first aggregate audit
also remains in `evidence/evidence-audit-before-clock-fix.json`.

Python source parsing and live synthetic integration completed. The evidence
audit accounts for all 26 case IDs,
checks every client-decision/oracle ordering, records zero HTTP reads for every
cut and complete planned send counts, and found no authentication-token value
in retained evidence. Sorting the retained UTC timestamps yields a minimum
adjacent PR-create timestamp difference of 2.942764 seconds. Wall-clock accuracy
was not calibrated. Every fixture trunk tree had no workflow files. This was a
paced boundary study, not a load test.
Six first/last-head samples across the three bulk fixtures each reported zero
Actions runs. Final capture retained 701 native refs and a verified Git bundle.

## Retained evidence and remaining decisions

`matrix.json` gives every case's disposition and limits. The transport, boundary
and fresh-boundary result JSON files link to sanitized intents, receipts, actual
send/timing records and independent observations in `evidence/`. `resources.json`
binds branches, authored objects and canonical PR numbers. Exact live ref capture
and a Git bundle retain authored and observed objects. Synthetic branches/tags
and PR histories remain on the host; only the planned deleted-head control
removed one branch, whose object/tag remain.

These experiments support per-operation reconciliation and safe stopping. They
do not supply general exactly-once retry, a cross-resource snapshot, cancellation
of pending native work or permission to rewrite a suffix after native work.
The natural 504/502 cases make unknown effects concrete even when an HTTP response exists.
Provider guarantees or a demonstrated protocol that avoids those dependencies
remain necessary for stronger automatic recovery promises.

*Authored by an AI agent acting on joshlf's behalf.*
