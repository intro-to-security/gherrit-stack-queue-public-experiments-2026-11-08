# Actual stale website requests, with a fresh-map control

The website rejected two captured stale head maps with HTTP 409 and
`{"error":"Stack contents have changed"}`. One changed the selected upper
member; the other changed only the lower member while the selected upper head
stayed fixed. A separate control sent a fresh map for the same kind of lower
branch divergence and successfully rebased both members, preserving the edit.

These are observations of GitHub's private website interface on November 9,
2026. They do not establish a supported public rebase API, an internal comparison
algorithm or a guarantee about writes from an already admitted operation.
The earlier modal-refresh attempt remains a failed stale-map premise; these
new fixtures do not relabel or modify it.

## Three separate fixtures

All fixtures are synthetic, same-repository two-PR stacks with their own trunks
in `joshlf/gherrit-native-stack-experiments-2026-11-08`. No default branch,
production GHerrit, shared policy, workflow or queue setting changed.

| Case | Actual input and intervention | Response and observed outcome |
| --- | --- | --- |
| [Selected B](outcome-b/REPORT.md): PRs 661/662, group 663 | Pause the initiating POST with the original A0/B0 map; acknowledge B0→B2 plus a new immutable B2 archive; independently read seven refs; observe the same paused old body; resume once. | [Captured POST](NETWORK-B.json) still names A0/B0 and returns 409. The UI reports a network error and both members Skipped. Three later cohorts retain A0, B2, its marker and all source/archive refs. B is the only stack member changed, but the simultaneous nonmember archive creation is an explicit confound. |
| [Lower A](outcome-a/REPORT.md): PRs 664/665, group 666 | Retain the A2 archive before browser load. Pause an original A0/B0 initiation; acknowledge a lease changing only the existing A ref to A2; independently read seven refs; observe the same old body; resume once. Selected B stays B0 throughout. | [Captured POST](NETWORK-A.json) still names A0/B0 and returns the same 409/error. The UI again labels it a network error and both members Skipped. Three later cohorts retain A2, its marker, B0 and all other refs. No new ref/archive was created during this pause. |
| [Fresh lower-A map](outcome-a-fresh/RESULTS.md): PRs 667/668, group 669 | Publish A2, its archive and trunk progress before page load. B stays B0, still descended from old A0. Use the ordinary confirmation once, with no paused advance. | [Actual POST](NETWORK-A-FRESH.json) names current A2/B0 and returns 200. Captured status progresses PENDING→RUNNING→DONE, both SUCCEEDED; the UI says both Rebased. Three independent cohorts verify the new graph, complete patches and marker preservation. |

These controls support a stale-member-map check in this website path, including
a lower-member case where the selected head stayed unchanged. The fresh control
shows that lower-head divergence itself is not always a rejection condition.
The cases differ in fixture and time, and the server's internal comparison source
was not inspected. Do not turn that comparison into an undocumented universal
rule or infer that every conceivable member/map condition was tested.

## Why the stale premise is established

Chrome's documented XHR/fetch breakpoint paused the actual initiation at
`fetch-patch.ts:11`, at the call to `globalFetch(input, init)`. Native DevTools
showed the exact owned initiation URL, POST method and complete serialized
`expectedHeadOids` body. The request headers remained collapsed.

Root retained a causal sequence for each stale case: observed pre-dispatch
pause → exact leased push acknowledgement → independent actual Git-ref read →
same paused initiation and original body → one Resume → captured old-map POST
and response. The CLI receipt and ref read completed before the second pause
observation and Resume. There was no step, reload or second confirmation.

The pause notes are exact transcriptions of native accessibility observations,
not raw browser debugger protocol traces. [The oracle review](oracle-review/REVIEW.md)
states the premise, abort rules and limits. The raw HAR start field is request
creation/debugger metadata, not a physical send-time measurement. The argument
uses the documented pre-dispatch boundary and ordered actions rather than
comparing clocks from different systems.

The source and grants remain separate. `fixture-prep/` prepared the B case;
`fixture-a-prep/` prepared the lower-A case. Its original six-ref READY and
unused planned `advance-a` action are retained. The separately reviewed
`a-only-continuation.py` first created the archive before page load and wrote
`READY-A-ARCHIVED.json`, then changed only A under a new pause-bound grant.
It did not execute, clear or repair the unused old action.

## Actual graph and content checks

Each independent observer captured three cohorts at offsets 0, 10 and 30 seconds
from its own start. These are separately timestamped reads followed by fetches,
not atomic snapshots, continuous silence or windows measured from the POST.

The two rejected cases retain their exact post-push vectors. They also retain
PR-associated base-OID differences: the REST base fields can still name old T0
or A0 while the actual named target has advanced. The reports preserve these
values rather than normalize them or treat the historical patch base as the
current target.

In the successful control, actual A is
`62a778098ec047a2ef449139b871355db98d0429` and B is
`f918555d3ba30e18caa4e83d32252afcb8ab2fcc`. A's full new range has two commits,
starting at the independently advanced trunk. B's full new range has one commit
and its sole parent is the actual new A head. Both expected trees and full
source patches match for this disjoint-file fixture. The lower marker survives
in both heads. The five protected source/archive/trunk refs remain exact;
canonical PRs stay open and ordered in group 669. Checking only A's last commit
would have omitted part of its authored change.

The rewritten commits preserve authors, messages and their single agent
trailers. Their committer becomes GitHub and they contain `gpgsig` headers;
this is observed producer/signature presence, not cryptographic verification
or a signing-policy guarantee. The independent source and retained-data
verifiers record their own limits.

## What this changes in the design

The result closes the earlier unperformed stale-request discriminator within
these fixtures. It reinforces the existing distinction between a definite
response, a provider job, actual branch state and an accepted integration.
The UI's network-error label is not a transport-loss diagnosis: these requests
have captured 409 responses. A client must retain the actual response and its
target scope rather than infer a safe retry from a screen label.

It does not close the later-write question. A provider could reject stale maps
at initiation yet still let a previously admitted job write after a later
client push. These tests do not exercise or exclude that trace. No new public
compatibility promise, handoff or operating-policy preference follows. The
strict gate and weaker retained-intent alternatives keep their existing costs
and proof obligations.

## Retention and cleanup

The browser exports followed the active `stack_rebase` filter: the private raw
exports contain respectively 1, 1 and 4 entries. Whole-tab counters were 14, 6
and 31 at the recorded observations. An export entry count is not a claim that
the tab made no other requests. `NETWORK-*.json` contains only reviewed URLs,
maps, statuses, response bodies and selected response headers. Complete filtered
HARs remain private with mode 0600; hashes do not make them public.

Owned breakpoints were removed, and no owned document was left paused. Each
browser part received its completion summary. No initiation was retried. All
CLI fixture writes were acknowledged; the source archives and fixture PRs are
retained rather than deleted. The B observer's initial sandbox DNS failures are
preserved separately from its later successful read-only capture.

At the user's request, two temporary `caffeinate` processes supplied idle/display
and user-activity assertions for the remaining browser work. Their exact owned
assertion IDs were checked before termination; both assertions were independently
confirmed released afterward. No persistent power, screen-lock or authentication
setting changed.

*Authored by an AI agent acting on joshlf's behalf.*
