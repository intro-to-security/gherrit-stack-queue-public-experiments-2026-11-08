# Protocol follow-up plan

This lane owns only new `exp/fu2/protocol/**` refs, tags and PRs in
`joshlf/gherrit-native-stack-experiments-2026-11-08`. It changes no repository
settings or main branch. Every synthetic fixture retains its branches, objects,
PRs and sanitized request/response evidence. Root owns publication.

The harness uses API version `2026-03-10`. Token material comes from `gh auth
token` into process memory only. It is never placed in command arguments, saved
requests, exception text or output. Ordinary calls retain receipts; uncertain
calls use a dedicated TLS socket, send the full HTTP request, then close without
reading any HTTP status or response. TLS send completion establishes bytes
accepted by the local TLS transport, not remote execution or remote receipt.

Before every uncertain dispatch, persist intent. After closing, persist the
client decision **unknown; do not retry or overlap** before independent read-only
oracles. A positive transition can identify an effect under the sole-writer
fixture premise. An unchanged/absent state is weaker evidence. Neither outcome
establishes general idempotency, a causal fence, or provider quiescence. Fresh
fixtures isolate uncertain operations from later writes.

## Cases and discriminators

| ID | Question / hypothesis | Oracle / control | Bound |
| --- | --- | --- | --- |
| P-T01 | Does a full-send/no-read PR creation become discoverable? | Fresh exact head/base and unique body marker; list PRs including closed; exact identity, state and refs | One write; GET immediately, +2s, +5s |
| P-T02 | Does a full-send/no-read comment creation become discoverable? | Fresh PR; unique body marker; list comments and exact body match | One write; three GETs |
| P-T03 | Can a lost base PATCH be reconciled from a positive base transition? | Fresh open PR changes from old trunk ref to a second ref at the same object; inspect exact base/head | One write; three GETs |
| P-T04 | Can stack creation be found without its receipt? | Fresh two PRs; stack list filtered by one PR and exact ordered membership | One write; three GETs |
| P-T05 | Can an append be found without its receipt? | Fresh registered pair plus third PR; GET group and exact ordered members | One write; three GETs |
| P-T06 | What does lost unstack leave? | Fresh group; group GET, filtered stack list, both PR memberships | One write; three GET cohorts; no subsequent writes |
| P-T07 | What can recover a lost direct async merge request without its UUID? | Fresh registered pair on owned trunk; inspect both PRs, group and Git refs, compare expected final tree | One request; at most 12 read cohorts / 35s; no PUT resend |
| P-T08 | Can an incomplete request produce a visible mutation? | Fresh exact-head PR creation with body truncated by one byte; explicitly distinct negative transport control | One partial write; three GETs; absence remains bounded observation |
| P-T09 | Does the exact raw TLS framing/authentication path work with acknowledgements? | Same raw request construction, read full HTTP response for repository GET and fresh acknowledged comment POST; independent comment GET | One read and one comment creation, recorded before dispatch |
| P-B00 | Minimum size boundary | Empty, one real PR, two valid linked PRs; HTTP response and independent memberships | One request each; prior singleton rejection also retained |
| P-B01 | Actual create sizes 99, 100, 101 | 101 distinct real linked PRs, workflow-free owned base; create 101 first; then create/unstack 99 and 100 separately | 101 PRs total, sequential >=2s between content writes |
| P-B02 | Append at 99→100→101 | Register first 99 of same released fixture, append item100, then item101; read exact count/order after each | One append each; stop on unexpected/unknown outcome |
| P-B03 | Duplicate/reversed order/wrong base controls | Small fresh linked PRs; malformed request variants; independent membership before valid control | At most five invalid requests then one valid registration |
| P-B04 | Closed PR registration and retained lifecycle | Fresh linked pair, close upper before registration; inspect receipt and membership; reopen only after known resolved request | One close/register/reopen and valid control, as supported |
| P-B05 | Deleted-head lifecycle | Fresh linked pair, exact tagged original head; delete owned upper head, inspect PR closure and group registration; retain tag/object and do not delete evidence | One explicit synthetic branch deletion; one registration |
| P-R01 | Resolved existing protocol behavior | Reuse prior `api/RESULTS.md` and exact raw sources: sync rejection, duplicate membership, ordinary unstack, completed-group reopening, publication atomicity, selected-head race, structural parking hazard, after-ack loss | Read-only; no replay |

On the immediate-close series, the first five writes produced no observed
positive transition. Root therefore authorized a fresh 500ms post-send/no-read
variant of P-T01..08 before its dispatch. These cases use suffix `-H500`, new
fixture identities, the same oracle separation and no replay of unknown writes.
The delay can permit processing while the client remains ignorant of the
response. It cannot establish when a response was sent or whether execution
remained in progress at close.

The original P-B01 create99 returned HTTP504 but created group330. The harness
incorrectly continued with create100 and a semantic repeat of create99, both
rejected for existing membership. These are retained policy violations and
contaminated capacity evidence. Group330 and its unknown intent remain untouched.
The corrected harness stops on every mutation5xx. Root then authorized two new
disjoint fixtures before dispatch:

| ID | Question / hypothesis | Oracle / control | Bound |
| --- | --- | --- | --- |
| P-B01-F100 | Can100 distinct linked open PRs be created as one group with a clean premise? | Fresh100-chain, one create100; read exact ordered membership; preserve any5xx as unknown and perform only reads on that fixture afterward |100 fresh PRs; one registration, no retries |
| P-B02-F101 | Do actual group sizes98/99/100 and append101 work? | Fresh101-chain; acknowledged create2, batches of at most8 to98, then one each to99/100/101; read exact count/order after every response |101 fresh PRs; at most15 appends; stop that fixture on any5xx/unknown |

Fixture cap:400 PRs (root-authorized expanded bound),450 heads and400 archive
tags, fewer than450 new REST mutations and35 pushes. Requests are sequential, no
stress or load testing.
Content creation pauses at least two seconds after each mutation. Polling is
bounded. A rate-limit response stops the affected driver rather than resending.
Unknown ordinary writes are retained and reconciled; they are never automatically
retried. Boundary fixtures have no workflow files in any branch tree, so creating
101 PRs does not schedule 101 copies of the experiment workflow.

Primary references: [Stacks API](https://docs.github.com/en/rest/pulls/stacks),
[asynchronous merge API](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously),
and [stack API/webhook semantics](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests-apis-and-webhooks).
The docs specify linked base/head order; tested size limits remain observations
unless separately present in the retrieved schema.

*Authored by an AI agent acting on joshlf's behalf.*
