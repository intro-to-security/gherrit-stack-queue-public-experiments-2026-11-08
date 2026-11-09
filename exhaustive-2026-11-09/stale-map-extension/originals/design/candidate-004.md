# GHerrit after the additional native-stack experiments

Keep the proposed commit-oriented frontend, canonical PRs, exact submitted history
and one reconciliation core. The additional evidence does not justify replacing
that architecture. It does justify a narrower rule for using observations:
**validate each input for the action that uses it, rather than require every
projection of the stack to describe the same instant.**

This is a qualified design comparison, not a production protocol or a decision
to weaken GHerrit's hosted-state promise. The
[retained design](../github-native-stack-choice-refinement-2026-11-09/candidate-002.md)
and [decision comparison](../github-native-stack-choice-refinement-2026-11-09/DECISIONS-002.md)
remain the baseline except for the explicit updates here. Its complete model
and migration obligations remain in force. This revision adds the completed
website evidence and unchanged-head timing control; the conceptual model and operating alternatives are unchanged.
No production code or setting changed.

## The retained model

Authors edit separate logical changes as commits on one local branch. The first
proposed client supports same-repository linear one-commit authoring and one
cooperating enrolled publisher, including linked worktrees. Exact hosted
base/tip ranges remain necessary even in that narrow authoring domain.

GHerrit binds a repository, change ID, owned head and canonical PR; a fresh SHA
lease supplies no ownership by itself. It preserves old immutable submission
ranges and existing discussion by default. GitHub owns native membership,
navigation, trunk rules and landing/rebases. The legacy cascade must be excluded
for enrolled work. Human prose stays human-owned; generated history has a
separately owned artifact.

Last authored submission, incorporated hosted range, accepted local result,
current captured authoring range and new hosted observation are different roles.
They may share objects or a storage record. Removing a role when its values
happen to coincide would lose pending edits or mistake observation for acceptance.
One evaluator, effect dispatcher and exact-range importer serve commands and
possible later hook, queue or website adapters. Each external effect retains
its actual intent, target scope, guards, receipt and uncertainty.

Local preparation and scratch integration retain committed inputs without
resetting the caller's branch, index or dirty/untracked workspace. Acceptance
retains the exact result and its incorporated inputs. A local successor does
not settle an old remote request or grant overlapping mutation authority.
Migration and rollback preserve canonical bindings, archives, accepted results
and pending custody; they deliberately exclude the previous writer. A mode flag
does not cancel something already dispatched.

The first proposed milestone can stage an independently landable F before
amending canonical B. That defers general insertion only when the author accepts
delayed dependent review and the actual F-only source export. Joint F–B review,
shared prefixes, nonlinear authorship, managed-head trunks and structural edits
retain their separate domain and lifecycle obligations. No indefinite refusal
is called a complete replacement.

## Exact inputs do not require one globally fresh snapshot

The
[public sequential-rebase experiment](../../experiments/native-stacks-exhaustive-2026-11-09/workflow/partial-prep/)
exposed an unnecessary precondition. Its first guard required B's PR-associated
base-OID fields to equal the newly advanced A branch before rebasing B. The
fields still named old A, while actual Git A and A's own head showed new A.
No B or C request was sent by that run.

The separately granted continuation retained the old freeze and proved that
those requests had never been sent. It kept exact canonical identity, selected
REST/GraphQL heads, head/base branch names, full native membership and all nine
actual source/archive refs as guards. It recorded the associated base-OID
discrepancy rather than treating it as a reason to reject the intended rebase.
B then acquired exactly the advanced A as its sole parent, kept its original
own patch and matched the independently prepared tree. C subsequently returned
an explicit conflict error, leaving C and the source/archive vector unchanged.
B's usable result was retained before C's request.

That trace supports the following distinction:

- A retained historical range describes the patch captured against its own base.
- A current named-parent ref describes the intended target for a new operation.
- A provider field is evidence with its own meaning and update behavior.

The historical base need not equal the new target: synchronization exists to
bridge that difference. When a validated old range is already retained, do not
invalidate it solely because the parent branch advanced or an associated base
OID did not follow. Preserve which old range was incorporated; do not claim
that its tip already includes the new parent.

This corrects the baseline's broad wording that any disagreement about direct
bases prevents an accepted input/checkpoint. It does not provide a general
algorithm for guessing missing range boundaries from ancestry or a stale field.
The concrete case already retained exact A/B/C submission ranges. Missing
canonical mapping, unavailable objects or an unjustified comparison base still
require recovery. If a PR head and its branch ref disagree about the current
selected revision, preserve both observations and withhold claims that require
that current identity to be established.

Each operation must establish the facts it actually depends on. A selected-head
guard does not freeze the base branch, every member or future jobs. Ordinary
trunk progress remains allowed; it is not excluded as a simultaneous structural
writer. If the accepted action promises one exact captured target, admission
needs a sufficient target-stability argument or a capability that guards that
target. Checking the parent afterward cannot supply that missing protection.

The public selected-member API can offer a rebase onto the named base as it
stands when the provider executes, with that meaning recorded in the captured
intent. A preview of the current base OID is an observation, not a target lease.
It cannot offer exact captured-target semantics with the selected-head guard
alone. Verify and retain the actual result before evaluating its acceptance.
If an effect already happened against a target outside the accepted scope, keep
the original intent and actual result as an applied, unaccepted outcome. Do not
promote its checkpoint, automatically roll it back or resend the request.

Validate preservation of each change using its captured ranges and a justified
expected transformation or accepted resolution. The disjoint-file fixture's
literal patch equality is a useful check for that fixture, not a general rule:
a correct same-file rebase can change context and blob indexes. Neither literal
patch equality, range-diff pairing nor cumulative tree equality alone proves
per-layer correctness. The controlled fixture does not validate every moving
parent or writer. Neither coherent reads nor a newly accepted local result
prove suffix settlement.

## Completion follows durable dependencies

The [actual Git guest tests](../../experiments/native-stacks-exhaustive-2026-11-09/recovery/vm/protocol-guest/RESULTS.md)
found that the prototype reported complete before two new Git refs were durable.
The initial after-return recovery correctly refused a broken local attachment.
Other prefixes returned complete despite a broken local-provider archive; the
independent oracle rejected them. Original objects survived. The provider was a
local emulator sharing the guest disk, not GitHub.

A separate wrapper made the three required loose-ref file/directory writes
durable before their confirmations. It passed all eleven unchanged expectations
on fresh fixtures, with exact archives and actual barrier traces checked.
That repairs the captured realization gap within Linux Git 2.34.1/ext4. Existing
objects were synced beforehand. It proves neither new-object/backend portability
nor macOS, every interruption timing or physical host/device loss.

The common completion rule remains small: make every dependency durable before
the durable record and successful return that claim it. Do not treat subprocess
success, a live reread or unrelated JSON fsync as that guarantee. Recovery must
reject missing dependencies without manufacturing a new remote request.

If publication already refers to an immutable durable accepted-result root,
a second alias naming that same fact is unnecessary unless it serves a distinct
selection/interface role. This is a representation option, not removal of
acceptance or retention. A genuinely new continuation still needs a durable
attachment; an unknown native result cannot be accepted before it exists.
This option and verified Git barriers retain different mapping and validation
costs. No measured universal advantage has been established.

## Current GitHub capability and supported promises

The
[source survey](../../experiments/native-stacks-exhaustive-2026-11-09/sources/REPORT.md)
and [fifteen-client comparison](../../experiments/native-stacks-exhaustive-2026-11-09/code-survey/REPORT.md)
found no explicit last-suffix-write or later-write arbitration fence. Official
post-merge sync guidance is positive intended-workflow evidence. The causal
experiments observed no acknowledged post-terminal overwrite, but finite
observations cannot prove the stronger exclusion promise.

The selected-head cancellation condition is in the OpenAPI description. It is
not an all-member snapshot or a last-suffix-write guarantee. An older requested
revision landing and a later surviving head do not date that push relative to
actual merge linearization.

Source inspection found a whole-stack REST rebase route, but numeric and named
OAuth requests returned 404. A separate
[Actions installation-token probe](../../experiments/native-stacks-exhaustive-2026-11-09/code-survey/rebase-app-prep/RESULT.md)
also returned 404 with actual contents/pull-requests write grants matching the
accepted-permissions header. This is current capability evidence, not permanent
absence or a diagnosis of every enrollment/routing restriction. Do not adopt
the website's private endpoint as a supported public backend.

The website has actual partial outcomes; public GraphQL has actual selected-member
success, conflict rejection and sequential composition. These interfaces can
supply inputs to the same importer. Their receipts and fallible boundaries remain
different. Two separately guarded member requests do not form a stack transaction.

The [completed stale-request controls](../../experiments/native-stacks-exhaustive-2026-11-09/ui/stale-map-debug-prep/RESULTS.md)
add current website evidence. A prepared old-map POST returned 409 after the
selected B advanced; a second returned 409 after only lower A advanced while
selected B stayed fixed. Both responses explicitly say stack contents changed,
although the UI labels them network errors. A separate fresh A2/B0 map returned 200
and rebased both members, preserving their full patches and the lower marker.
The B intervention also created a nonmember archive; the A intervention changed
only one existing member ref after prearchiving before page load. These controls
support a stale-member-map check in those private-interface fixtures. They do
not identify the internal comparison source or establish a public contract.

A fourth fresh A2/B0 initiation was held at the same client-side breakpoint for
420.257478125 monotonic seconds, longer than conservative whole-trial envelopes
for either stale case. Three sampled seven-ref reads matched the prepared vector;
no deliberate ref changed. The same paused body then returned 200, followed by
DONE with both members SUCCEEDED. Independent graph cohorts verified complete
two-commit A and one-commit B ranges, expected trees and marker preservation.
Pause or request age alone was therefore insufficient to force rejection in that
control. Separate fixtures and sampled reads still do not reveal a unique internal
algorithm, continuous locking or future-write exclusion.

A captured rejection at initiation is distinct from settlement of an already admitted job.
These POSTs were dispatched and received explicit 409 responses; the client-side
pause preceded dispatch, but no internal provider job-dispatch boundary was observed.
A provider can reject an old vector at initiation and still allow an older job
to write later. Neither these captures nor the bounded unchanged readbacks
exclude that trace. Keep the actual response and scope; do not treat the UI's
network-error label as missing acknowledgement or automatic retry authority.

The
[target CI controls](../../experiments/native-stacks-exhaustive-2026-11-09/target/RESULTS.md)
establish a minimal first-upper opened route matching GHerrit's unfiltered
workflow shape, plus the observed default/explicit stacked trigger contrast.
This removes a generic first-CI capability doubt for that path. It does not run
GHerrit's Rust workload or discharge actual target producer/SHA/method/queue
acceptance. Begin with the working route rather than invent a general policy
framework or declare every green check eligible.

## Compare the remaining operating promises

| Candidate | Benefit within its claimed domain | Cost and unresolved support |
| --- | --- | --- |
| Retain supported exclusion before overlapping writes | Avoids admitting an old native effect that can undo a later export when the exclusion premise holds. | No sufficient provider handoff was found. The current pilot stops at the overlap and cannot be called a complete repeated-workflow replacement. Its unavailability is a real cost. |
| Fixed-order retained intent with exact drift review | Could permit repeated publication without promising immunity from every later native write. | Admits temporary wrong hosted state, observation delay, missed transient states and recurring author decisions. It owes enforcement, a lifecycle/scope argument and an implemented useful repeated workflow. |
| Add accepted path/value intent for automatic restoration | Could reduce some repeated author decisions. | Adds intent capture/composition, rename/delete/mode/binary semantics and validation. A clean three-tree merge already failed an explicit-reset example; additional machinery has not shown a lower total burden. |

The exact-review alternative retains the first client's ordinary independent
trunk, canonical reviews and archives. Its proposed narrower domain keeps order
fixed, lands the lowest open member directly, excludes queue/external website
jobs and structural mutations, and avoids appending into an older exposed group.
These restrictions are costs, not proof of lifecycle safety. The required argument
must bound the old operation's actual possible effects; “same order” is not
itself a proof. Unknown client mutations, missing custody and unknown scopes
still block overlap. Choosing a weaker promise cannot erase their evidence.

The [reset counterexample](../../experiments/native-stacks-exhaustive-2026-11-09/recovery/RESULTS.md)
explains why archives alone are insufficient. After an author changes x=0 to 1 and explicitly resets it to 0,
restoration from old input x=0, current x=0 and observed x=1 can return 1 cleanly. Exact review can keep that
decision explicit; automatic restoration needs more information. Neither path
proves that every human recognizes a lost edit. Likewise, restoring bytes cannot
reopen a canonical review terminalized by an indirect merge. Order-changing
recovery must prevent/exclude that risk or count review replacement explicitly.

No candidate dominates across the unresolved availability, hosted-state,
continuity and human-friction priorities. Keep the strict gate in the qualified
proposal until a supported handoff or an explicitly selected and validated weaker
contract justifies the next overlap. This is not a claim that C1–C8 require the
stronger promise. A service or CLI does not make the choice disappear.

## Reviewer comparisons are derived views

The user proposed range-diff. The
[actual controls](../../experiments/native-stacks-exhaustive-2026-11-09/history-range-diff/RESULTS.md)
show it can omit unrelated ancestry changes and follow reordered patches.
They also show context noise and equals for two different binary blobs.

Keep each exact authored-patch link. A comparison between submissions can use
the recorded logical identity and two explicit ranges. Derive file/blob/mode
indicators within each base-to-tip patch, then compare those recorded changes;
whole-tip comparisons can reintroduce unrelated ancestry. For binary edits,
retain both base/result blob transitions rather than infer semantic equivalence
from a text display or label every tip difference an authored change. It can live in the
owned history comment or a linked generated artifact, subject to size, discovery,
hosting and effect-recovery costs. It is not a new canonical history store,
an integration baseline or an acceptance oracle. No production renderer or
GitHub-native range-diff URL has been established.

The actual user found the v1 entry and supplied the drift filename; no ease or
general comprehension judgment followed. Root later explained the roles, so
another walkthrough of this fixture would be informed.

## What remains open

1. Select and realize the hosted-state promise for useful overlapping repetition,
   or obtain the missing provider support. The maintainer questions were posted
   by the user; no response existed at the latest recorded read.
2. Choose first-release priorities: staged versus joint review, continuing versus
   one-shot authorization, hook convenience, multiple publishers and history
   presentation. Concrete tests narrow capability; they do not choose preferences.
3. Implement and validate the selected protocol: identity/destination/old-writer
   exclusion, exact ranges and durable dependencies, partial/unknown recovery,
   lifecycle bounds, target CI and reversible custody/migration. These prototypes
   do not constitute production acceptance.

The additional search, including the formerly blocked stale-request website
controls, has reached the identified accessible discriminators.
Repeating quiet windows cannot establish a future-write fence; a404 cannot
exercise a successful whole-stack route's conditional behavior; a shared host
is not a disposable physical-power-loss test; and agent trials do not choose
human priorities. These limits remain attached to the comparison.

*Authored by an AI agent acting on joshlf's behalf.*
