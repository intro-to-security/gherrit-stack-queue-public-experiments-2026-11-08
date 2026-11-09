# Local recovery and migration findings

The experiments reject ordinary import as a sufficient retained-intent recovery
protocol. They also reject the first attempted restoration formula: retaining
the older operation's input and the latest accepted tree does not preserve an
explicit reset to that older value. Two narrower candidates remain: require an
exact explicit decision for every overlapping drift, or retain accepted intent
paths and validate a restoration proposal before that decision. Neither has
measured human acceptance or production implementation evidence.

The [final local run](runs/1794232632320218000/RESULTS.json) exercised R01–R18
with 188/188 assertions. This number includes expected failures, negative
controls, refusal cases and one model sanity check; it is not a production
acceptance score. The [case index](CASE-MATRIX.md) separates those outcomes.
The first run and its exact source remain at
[`runs/1794232256240038000`](runs/1794232256240038000/RESULTS.json).
R04 there caught an experimental importer bug: serializing a message using
`git show --format=%B` added a newline when that output was passed to
`commit-tree`. The corrected capture reads the raw commit-object message.
The final two-layer check preserves each layer's paths and exact message bytes.

## What drift recovery must decide

R01 constructs confirmed publication X with x=1, then injects an older x=0
range. Ordinary three-way import with incorporated=X and local=X cleanly
returns x=0. The archived X remains recoverable, but the accepted intent has
been silently reversed. The strict scope gate refuses the overlapping write;
the drift gate instead preserves the captured intent and requires a decision
before incorporating the changed observation. This injected effect tests the
client; no delayed GitHub suffix write is claimed.

R03 gives a stronger counterexample. After x=1, the author explicitly accepts
a reset to x=0. A later remote x=1 can be an old effect or a legitimate edit.
The first restoration formula, merge(old x=0, current intent x=0, remote x=1),
cleanly returns x=1. The independently specified expected value is x=0.
The retained [v1 source](runs/1794232256240038000/protocol.py),
[counterexample and exact objects](runs/1794232632320218000/R03.json), and
[raw merge evidence](runs/1794232632320218000/repetition/v1-reset-restoration-loses-intent-merge.json)
preserve this failure. A clean Git merge is insufficient evidence of intent.

| Boundary | Retained state and behavior | Cost and limit |
| --- | --- | --- |
| Strict exclusion | Exact operation input/scope/outcome; refuses overlapping hosted effects until their authority is established. | Preserves inputs but makes no progress at the unresolved B gate. The test supplies no provider fence. |
| Explicit-only drift decision | Retains submitted/incorporated/accepted/current ranges and old operations. Every overlapping changed observation stops until an exact reviewed result and any intent change are accepted. | Full drift review each time. The test supplies a correct explicit result; it does not show that a person notices every lost edit. |
| Guarded restoration proposal | Adds an explicitly accepted intent-path set, including paths reset to older values. A proposal must preserve their required values; conflict or mismatch requires explicit resolution. | More state and validation. Same-file legitimate edits can require manual resolution. Path selection is accepted input, not inferred intent. This experimental builder covers small regular text-file trees. |

R02 preserves an independent legitimate remote edit through restoration, keeps a
same-line edit as a conflict, and separately accepts the remote edit as a
deliberate change of intent. Blindly restoring the whole latest tree loses the
independent edit. R17 executes the simpler explicit-only boundary without
automatic restoration or retained path-selection state. Neither boundary can
attribute an edit to an old native writer merely from its contents.

R03 keeps three distinct A/B/A archives, keeps later source movement pending,
and creates no new authored archive for a no-op import. Authored submission,
incorporated hosted range, accepted intent/result and current captured source
are stored as distinct evidence in the cases. R12 accepts a fresh local successor
while an older request is indeterminate, without changing that request's captured
input or granting strict hosted-write authority.

## Observation, lifecycle and recovery limits

R05 refuses inconsistent PR/ref observations. A coherent stale observation can
miss a current reversal; a later current observation detects it. A real local
Git push with an explicit old-value lease succeeds after old→intervening→old
ABA. These mechanisms do not detect all transient states or provide a monotonic
generation. The weaker promise therefore admits temporarily wrong hosted state,
offline/observation delay and missed transient revisions.

The bounded policy explorer covers 97 reachable states and 586 transitions at
depth at most seven: scalar values 0/1/2, one layer, up to three publications,
old effects, legitimate edits, current/stale observations, explicit acceptance,
restoration and crash/recovery. It preserves intent under observation and crash
and requires review for current coherent drift. Its known-bad ordinary-import
and blind-restoration controls have retained witnesses. This is an abstract
policy check; the separate real-Git reset case exposes an algorithmic failure
that the abstract exact-restoration action does not model.

R07 constructs the Git ancestry condition for an old B commit to become reachable
from a reordered base. Canonical-review terminalization is a provider lifecycle
consequence documented elsewhere, not observed in this local injection. Both
candidate gates refuse overlapping reorder and landing. Restoring bytes cannot
promise to reopen an indirectly merged review. R18 admits explicitly scoped
F-only work but refuses shared public-source/checkpoint/managed-trunk targets
and unknown older scope. The test supplies those scope sets; it does not prove
that they exhaust GitHub's future effects.

## What the corrected dispatch experiment establishes

The new experimental dispatcher reloads custody, manifest identity, frozen intent,
bindings and retained inputs under one local filesystem owner before sending an
effect. Missing operation evidence never recreates intent. Completion validates
the exact retained result ref, objects, checkpoint and receipt identity. Ordinary
authoring uses a separate mutable ref and remains possible after completion.
The [source](protocol.py) is a fresh local experiment, not a production GHerrit
fix or a complete integration of the drift UI with publication.

Two simultaneous processes and a later stale direct invocation send one request.
Ten real SIGKILL prefixes leave complete recovery after a valid attributed receipt,
or remain blocked without resend before one. A cut after marking intent can
block even if no request was actually sent: preserving uncertainty has an
availability cost. Fifteen damaged-evidence variants withhold authority,
including a missing object, deleted retained result, foreign identity and invalid
receipt. Three temporarily unsafe dispatcher controls bypass identity, result or
owner validation; each reports completion while an independent artifact or
request oracle detects the violation. Thus the checks can expose those defects,
not merely accept a correct worker's own success statement.

R11's deliberately separate provider head/archive effects leave a changed head
and absent archive with no receipt. Matching desired head alone cannot complete
the operation or authorize a retry. This is not evidence that Git atomic pushes
can partially update their transmitted vector. R09's receipt reconciliation is
available in this sole-writer local emulator; no equivalent GitHub attribution
mechanism is inferred.

R13 transfers complete custody to another local directory using the same stable
authority path, invalidates the old token, and preserves the unresolved operation
without resend. Actual Git destination/head/archive readback rejects mismapping,
unadopted occupied heads and changed history; missing custody and unresolved old
writer records also refuse. Valid enrollment with pending custody grants no new
mutation authority. This same-host rehearsal does not fence another host or
prove that production legacy Actions have stopped.

R14 refuses rollback while native effects remain unknown. After a settled local
operation it exports and verifies a Git bundle, retains bindings/checkpoints and
outcomes, then invalidates the prior native owner. This is a deliberate local
export/handoff, not automatic fallback, old-SHA restoration or production migration.

## Durability and provenance

R09 is process SIGKILL evidence; host caches survive. R15's persistence-prefix
sets are explicitly assumed model outcomes, not filesystem measurements.
Read-only capability checks found shared OrbStack and existing Ubuntu/Python
images. Root separately approved and exclusively owns the disposable guest
experiment under `vm/`; its results must be integrated from that lane. This
report makes no whole-host or physical-device power-loss claim.

[Historical evidence](PRIOR-EVIDENCE.json) retains hashes and exact references
for 21 prior cases, including their model failures. No historical driver or
frozen fixture was replayed or changed. [Object verification](OBJECT-VERIFICATION.json)
checks the new fixture stores; the one intentionally deleted result object is
an explicit corruption control. Raw commands, exact refs/trees, source snapshots,
failed runs and checks remain in each new run. No hosted writes, production
edits, host installation or shared-runtime disruption were performed by this lane.

*Authored by an AI agent acting on joshlf's behalf.*
