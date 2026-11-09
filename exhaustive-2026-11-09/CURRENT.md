# Additional native-stack evidence and the resulting design

The new tests narrow several implementation questions. They do not establish
when all future suffix writes from a native operation are excluded. GHerrit's
qualified design therefore keeps that question open alongside the alternative
of accepting a weaker hosted-state promise with explicit drift recovery.

Read the [updated design](design/candidate-004.md) and
[final comparison](design/DECISIONS-004.md). The latest comparison includes the completed website controls. It selects no
new operating promise and does not validate a production migration. The [full earlier design](../choice-refinement-2026-11-09/candidate-002.md)
remains the baseline except for the explicit updates here.

## Findings that matter to the next implementation

| Question | Evidence and implication |
| --- | --- |
| Must every view of a parent agree before rebasing its child? | [The public partial trace](workflow/partial-prep/RESULTS.md) rebased B successfully while its associated base-OID fields still named old A. Exact historical inputs, actual named refs and the other identity/membership guards were retained. C then conflicted; B remained usable. Validate the inputs each action needs, rather than impose this extra equality. Neither the sequence nor a response projection is a transaction. |
| Is the discovered whole-stack REST route usable here? | [OAuth probes](code-survey/rebase-probes/RESULTS.md) and a separate [Actions installation-token probe](code-survey/rebase-app-prep/RESULT.md) all returned404. The latter had actual contents and PR write permission. This is current unavailability, not permanent absence or a token-class-only causal comparison. The private website route is not a supported public substitute. |
| Can the original recovery prototype safely return complete? | [Actual Git guest tests](recovery/vm/protocol-guest/RESULTS.md) ran all eleven prefixes: five met expectations and six did not. Three returned complete with a broken local-provider archive; two correctly refused broken local attachments; one produced a recovery exception. A separate loose-ref durability wrapper passed all eleven unchanged expectations. These are Linux Git2.34.1/ext4 tests with existing objects synced first and outer caches surviving, not GitHub, macOS or general power-loss validation. |
| Can GHerrit's workflow shape run first-upper CI? | [The target controls](target/RESULTS.md) establish a working unfiltered opened route and distinguish default from explicit stacked activity selection. The payload was minimal synthetic CI, not GHerrit's Rust workload or complete release acceptance. |
| Can a clean three-tree merge restore intent automatically? | [The explicit-reset counterexample](recovery/RESULTS.md) says no: an author can set0→1→0, then a clean merge can reintroduce1. Exact review preserves an explicit decision; automatic restoration needs additional accepted intent and validation. |
| Would range-diff improve review history? | [The frozen PR10 comparison and controls](history-range-diff/RESULTS.md) show useful isolation of unrelated ancestry changes and tracking through reorder. Context can still add noise, and different binary payloads both displayed equals. Keep exact patch links and derive binary/mode indicators within each authored range. Use range-diff as an additional human view. |
| Does source inspection supply the missing handoff? | [Primary sources](sources/REPORT.md), [fifteen pinned client repositories](code-survey/REPORT.md), [actual timing cases and official sync](causal/RESULTS.md) found no explicit last-suffix-write fence. The selected-head cancellation condition is documented; it is not an all-member or future-write guarantee. No acknowledged post-terminal overwrite was observed in these cases. |

The design retains one-branch authoring, canonical PR identity, immutable
submitted ranges, pending-work custody and one reconciliation core. The
supported simplification concerns observation-to-action mapping. Exact target
admission, per-layer preservation and durable completion still need their own
arguments. A proposed named-base-at-execution intent does not establish the
provider's exact target-selection instant.

## Remaining work and evidence boundaries

The remaining choices concern the hosted-state promise, staged versus joint
review, authorization and client convenience. Lifecycle bounds, useful repeated
publication, durable backend portability, target CI and reversible migration
remain production acceptance work. The user-posted maintainer questions
[622](https://github.com/github/gh-stack/discussions/622) and
[623](https://github.com/github/gh-stack/discussions/623) had no replies at the
latest retained read. No agent follow-up was posted.

The previously blocked website discriminator is now complete. [Four actual
controls](stale-map-extension/ui/stale-map-debug-prep/RESULTS.md) capture two stale
head maps rejected with HTTP409 and two fresh maps accepted with HTTP200 and both
members rebased. One stale case changed only the lower existing member ref while
the selected upper head stayed fixed. The second positive held a fresh request
for 420.257478125 monotonic seconds with three unchanged seven-ref samples before
resuming. That success makes pause/request age alone insufficient to force
rejection in that fixture. Twelve independent read cohorts verify the resulting
vectors, full ranges and retained content after the four operations.

These are private website observations, not a supported rebase API or proof of
an internal comparison algorithm. A sent request's captured409 is rejection at
initiation, not evidence that an older admitted operation has settled. The
first failed stale-modal premise remains retained. No browser-access blocker
remains for these tests. No identified accessible discriminator remains pending for the design claims
made here;
repeating quiet windows cannot prove future-write exclusion. Provider answers,
selected-protocol acceptance and human priorities remain separate work.

The [extension overview](stale-map-extension/README.md) describes its exact
sources, sanitized records and exclusions. Historical earlier status text records
its captured stage; this page and candidate004 give the current disposition.

This is a selected public evidence package. [Availability](EVIDENCE-AVAILABILITY.md)
distinguishes included records from the full local corpus. Large runtime/disk
archives, complete Git stores, raw browser exports, third-party source caches,
private account data, raw human replies and concrete sealed cases are omitted.
Their hashes do not make their contents public. Historical report status text
describes its captured stage; this page and the final comparison give the current
qualified disposition. No production GHerrit code, PR, hook or setting changed.

*Authored by an AI agent acting on joshlf's behalf.*
