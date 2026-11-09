# Staged continuation and public GraphQL branch-update experiments

Status: local preparation only. No hosted write is authorized by this file. Execution requires a separate exact root grant after harness review. The committed second-wave allocation is `control/COORDINATION.md`; this lane owns only workflow/ and fresh `exh-1109-workflow-` fixture resources in `joshlf/gherrit-native-stack-experiments-2026-11-08`.

## Claims to distinguish

1. A useful staged workflow can preserve local A′/B′ after old A lands, publish and land only A's new-ID follow-up F, then amend the same canonical B and import again without losing exact archives, layer ownership or pending work.
2. Private publication omits the author source ref. An explicitly accepted F-only public export publishes a fresh source ref naming F alone; it must not expose the full A′/B′ source under another name. Archive objects and canonical review heads remain intentionally public in either case.
3. F-only staging is inapplicable when F is not independently landable or when accepted intent requires joint F–B review. Such a case must refuse locally, preserving inputs and making no request.
4. Generic public GraphQL `updatePullRequestBranch(updateMethod: REBASE)` might reject native members, update only the selected branch, or cascade. Its name alone cannot decide this. Guard rejection, method acceptance, actual ref/base/group effects and any delayed effects require separate observations.

Finite successful traces will establish only their observed behavior. In particular, coherent reads, final `merged`, an unchanged event stream and client leases do not establish a universal native suffix fence. Experimental later B writes require explicit synthetic-fixture authority and retain the older native operation's unresolved suffix-settlement premise.

## Fixture scopes proposed for root grant

Each case gets its own synthetic trunk, no shared managed-head trunk, and a unique prefix `exh-1109-workflow-<case>-<nonce>/`. All branch writes stay below that exact prefix. Archive refs use the reviewer-facing form `refs/tags/gherrit/exh-1109-workflow-<case>-<nonce>-<change>/vN`; every archive is create-only and its exact base/tip is retained locally.

| Case | Hosted resources | Intended operation |
| --- | --- | --- |
| staged-private | trunk, A/B/F heads; canonical A/B/F PRs; old A–B native group; A/B/F authored archives; no author source ref | Full staged trace with private source export. |
| staged-public-f-only | Separate equivalent resources plus an initial accepted public source and a fresh F-only public source | Full staged trace; preserve full pending source locally while publicly exporting exactly F during the staged step. |
| gql-standalone | trunk and one ordinary PR | Correct-head REBASE positive control after conflict-free trunk advance. |
| gql-native-wrong | trunk, A/B/C heads and PRs, one native group | REBASE A once with a deliberately wrong expectedHeadOid; retain exact rejection/effects. |
| gql-native-lower | Separate trunk/A/B/C native group | Advance trunk, REBASE A with coherent current selected head; observe selected/suffix effects. |
| gql-native-upper | Separate trunk/A/B/C native group | Append a conflict-free commit to A, then REBASE B with coherent current selected head; observe whether C changes. |
| gql-native-conflict | Separate trunk/A/B/C native group | Conflicting lower/trunk edits, REBASE A once; retain rejection or partial/delayed effects. |

No default-main, repository settings, queues, auto-merge, website action, old fixture, external message, generated history comment or issue publication is included. Root owns any additional website operation or policy change. PR titles/bodies carry the required AI notice; commit messages carry the established agent-authorship trailer.

## Full staged trace

Use executable synthetic code under one dedicated path. A introduces a data-model API. B introduces a consumer of that API. A′ adds a backward-compatible field; B′ uses that field. A separate pending local-only B edit remains distinguishable from the hosted input. Assertions inspect each layer's patch and run both API/consumer behavior; cumulative tree equality alone is insufficient.

1. Create exact A0/B0 local ranges on the fixture trunk. Pin input objects, bind canonical PR identities, then atomically publish A/B heads and A/B v1 archives, plus the expressly selected initial public source in the public case. Register only A/B as one native group.
2. Create local A′/B′ commits without changing hosted A/B. Preserve both current local ranges and the last authored/incorporated/accepted ranges in a checkpoint.
3. Direct squash-merge old A through a recorded async request with exact selected SHA. Preserve submission UUID/options and separately observe actual trunk landing, B head/base, membership and events. A terminal result alone does not advance an import checkpoint.
4. Once exact usable hosted ranges are coherent and fetched, import B using the old incorporated B range, current local B′ range and actual hosted B range. Extract A's pending delta as new-ID F and replay B's own result on it. Pin a fresh continuation and install a checkpoint only after verifying the exact result. Retain the old checkpoint/source and native-operation record.
5. Run F alone against the landed trunk. Demonstrate that B′ without F fails its dependency check, while F alone is independently landable. Capture explicit staged intent: F only now; B review/publication delayed. For private mode omit source export. For public F-only mode publish a fresh source ref naming F alone, alongside F head/archive, never the full B′ source. Record the exact remote ref vector and before/after public source targets.
6. Open F as an ordinary PR against the synthetic trunk and land it without moving canonical B. Verify B's identity/ref/archive and the whole pending local suffix remain retained. F has no membership in the old A–B group.
7. Import/replay B against the new trunk, preserving its pending edits and exact own-layer patch. Amend canonical B through an explicitly recorded experimental leased publication and create B v2 archive in the same atomic ref transaction. No new B review is allocated; no authored archive is created for an import-only native rewrite.
8. Exercise repeated imports with distinct hosted inputs and a separately retained unpublished local B edit. The implemented `repeat-hosted-control` uses two ordinary-Git synthetic collaborator adjustments and labels them accordingly; it verifies the importer without claiming native rebase evidence. Additional actual-native repetition can use generic public REBASE if its capability probe succeeds, or a specifically coordinated root-owned website rebase on this quiescent fixture. Do not silently call the ordinary-Git control native evidence.
9. Verify exact remote archives v1/v2, canonical B PR identity and body, per-layer patches, committed-input custody, public/private ref vectors, retained native-operation scope and accepted local/hosted checkpoint separation. Any cleanup is a separate granted effect after final evidence capture.

The local inseparable control uses a breaking API change whose F-only tree fails the existing consumer, plus a joint-review-required intent. Both must refuse before any hosted intent/dispatch marker. Their full proposed F/B source remains recoverable. These controls are not human-comprehension evidence.

## Generic GraphQL observations

Use the exact public mutation with captured variables: `pullRequestId`, `expectedHeadOid`, `updateMethod: REBASE`, and a distinct clientMutationId. The client identifier is not treated as an idempotency key. The selected PR node ID must resolve to this fixture's registered numeric PR and exact head/base branch names immediately before dispatch. The known official CLI caller supplies selected PR HeadRefOid; schema wording alone does not prove an all-suffix guard.

Retain before/after branch refs, PR head/base and mergeability, direct Git parents/trees, native group identity/order and timeline event IDs/before/after commits/actor/base changes. Capture the raw HTTP/GraphQL response and immediate returned PR fields, then bounded observations over time. A payload with an updated PR is not assumed to be an asynchronous operation receipt. A wrong-head test is isolated from the correct-head fixture, so an ambiguous error never becomes permission to retry.

## Harness and effect guard

New code only; no old driver is imported or run. Earlier local importer code may inform the algorithm, but any reused helper must be copied with an explicit effect audit and reduced to local Git operations. The new harness has three boundaries:

- `core.py`: local immutable Range/Layer inputs, synthetic Git object construction, normalization/three-way/replay integration, exact checkpoints, content/patch assertions. No network functions.
- `effects.py`: exact repository/ref/PR/node-ID allowlist; one exclusive durable attempt per label; request bytes and fresh basis fsynced before dispatch; atomic outcome records and directory fsync. Every Git write has an explicit expected SHA, including absence for new refs. Archive overwrites, cross-fixture PR bases and broad API requests are rejected.
- `run.py`: explicit case/state transitions. Read-only preparation and observations are available without a grant. Hosted entry points require the root-created grant to name this case, repository, prefix and allowed effect kinds. No top-level execution on import and no automatic write retry.

The grant also names permitted harness actions, so permission to set up a fixture does not authorize a later publication phase. Initial source refs remain at captured B0 until confirmed hosted publication; the local authoring-ref transition to A′/B′ is recorded afterward and before old A's merge. Precomputed local commit objects are retained test inputs, not evidence of an earlier source-ref transition.

REST mutations are restricted to create a PR, create the exact A/B(/C) group and merge the expressly selected A or F in the case. GraphQL permits only the fixed UpdatePullRequestBranch REBASE mutation for the current fixture's captured node ID. No deletion, generic PATCH, queue admission or arbitrary mutation is available in the first grant. Ref publication uses exact owned vectors and force-with-lease; Git hooks are disabled for every owned repository.

Every unknown request/push outcome freezes that fixture and leaves the attempt unresolved. Reconciliation is read-only and cannot clear the blocker by elapsed time. A known rejection still requires actual before/after reads. Root is the sole authority for a successor attempt or changed scope. Harness tests challenge wrong repository, cross-prefix ref, archive overwrite, foreign PR/node ID, missing grant and reused/unknown attempt before any network call.

*Authored by an AI agent acting on joshlf's behalf.*
