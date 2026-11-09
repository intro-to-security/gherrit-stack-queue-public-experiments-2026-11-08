# Architect alpha: one custody record and one dispatch boundary

Execution: `swarm-model-refinement`. Target: GHerrit's integration with native GitHub stacked PRs. This is a bounded architect proposal for root's comparative adjudication, not an accepted design, implementation, convergence verdict or production acceptance.

The supported reduction is modest: **retain the incumbent's semantic distinctions, but make operation custody and dispatch one authoritative mechanism.** Derive pending/completed views from the operation evidence and actual accepted result. Do not maintain a separate pending manifest, completion flag or permissive recovery entry point that can disagree with them. Use the same guarded executor for publication, structural edits, history delivery and local continuation acceptance.

The new ground truth supports this reduction in the local prototype. It does not establish that the incumbent requires the prototype's duplicated metadata, nor that the proposed representation is cheaper than a careful surgical implementation of the incumbent. Against that surgical baseline, this proposal is chiefly a concrete realization constraint, with a possible maintenance benefit that remains to be demonstrated.

## Governing boundary and inspected evidence

The fixed requirements are C1–C8 in `outputs/github-native-stack-design-2026-11-08/GOVERNING-CONTRACT.md`. The incumbent is `outputs/github-native-stack-design-2026-11-08/post-experiment-refinement/candidate-001-corrected.md`. The responsibility map is `refinement/FRAME.md`.

I read the five exposed follow-up `RESULTS.md` reports for queue, local, structure, CI/reviews and protocol, the local case matrix and relevant stale-worker probe source, and `planning/audit/REPORT-FINAL.md`. The frame identifies the public snapshot as `intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08`, commit `97b993efdda40a1cbe690d317e436e32937adb85`, path `followup-2026-11-08`. These reports and cases are exposed design witnesses. I did not inspect sealed material or other architect proposals, run hosted effects or alter canonical files.

The useful new discriminator is local recovery evidence, not a new GitHub transaction guarantee:

- L13 accepts a completed record after its continuation ref or checkpoint disappears.
- L14 lets the direct worker recreate a missing operation record and repeat an applied effect, despite separate custody admission refusing.
- L28 makes two real stale workers dispatch twice after both cached `planned`; L29 accepts an operation identity different from the pending manifest.
- S01–S09 recover nine real after-ack structural interruptions without repeating confirmed effects; S10a/b refuse missing dispatch evidence and stale heads. That shows useful exact-effect progression, under its stated single-publisher premise.
- Actual no-read requests and natural 504/502 creation errors produce effects without settled client acknowledgement. The original 99-member semantic retry demonstrates why changing an attempt label cannot create authority for another dispatch.

These findings implicate the prototype's state representation and enforcing boundaries. They do not show that the incumbent's authored/incorporated/local distinctions are unnecessary.

## Candidate core

### Persist commitments once

Use one authoritative local custody record, or one transactional store with the same semantics, rooted in the enrolled checkout's common Git directory. Linked worktrees share it. Its logical contents are:

1. **Enrollment and canonical bindings:** verified API/Git destination, repository identity, managed namespace, change-to-head-to-canonical-PR bindings, legacy-writer exclusion and selected publication policy.
2. **Accepted results:** immutable accepted snapshots, each naming its exact continuation ref/result and per-change incorporated hosted range and accepted local range. Keep confirmed authored submission history separately identifiable within this record, including immutable historical base/tip boundaries and archive refs.
3. **Operations:** immutable captured intent and exact effect vectors, plus durable dispatch/evidence entries. An operation names its predecessor accepted snapshot, canonical identities, captured committed ranges, intended authored submissions, possibly affected resources and proposed next accepted result.

One store does not turn these meanings into one scalar current version. The last authored submission, incorporated hosted range and accepted local result remain independent commitments. Current local and newly observed hosted ranges are captured evaluation inputs; they need not become additional independently mutable current-version fields. The incumbent already permits this storage consolidation, so it is not credited as a new semantic reduction.

Every effect is addressed within its immutable operation. A separate pending manifest is unnecessary: unresolved scopes are a view of the operation records. A separate completion marker is unnecessary: completion is a view that requires evidence for the intended effects and a valid installed accepted result. If the ref/result or checkpoint linkage is missing or incompatible, admission reports damaged custody; it does not trust a cached `complete` flag or reconstruct intent from today's branch.

This is a logical design, not a requirement to rewrite a growing monolithic JSON file. A transactional embedded store or atomic replacement of a small root plus immutable records are possible realizations. Their durability and referential integrity must be checked. With separate immutable records, the root must retain the operation reference so that deleting its record fails validation; deleting the reference too may instead be an undetectable rollback. The proposal does not claim that hashes, atomic rename or a store name detect rollback to an old but internally coherent backup. Sharing storage also does not make distinct per-change checkpoints one semantic target: disjoint work may append records while preserving old unresolved operations.

### Make dispatch the enforcing boundary

All cooperating writers acquire one process-lifetime exclusive lock for the enrolled checkout's custody store, then reread authoritative state before admission and dispatch. No worker may use a cached pre-lock `planned` state. Hold the lock across persisting dispatch intent, the actual request and recording its outcome. Use a kernel-managed advisory lock for the declared cooperating process domain; do not turn a timeout or a stale lock file into permission to steal ownership. Another clone or delayed provider request remains outside that exclusion.

The only network mutation path accepts an effect from an existing, validated operation in this store. Recovery cannot initialize a missing operation, and an adapter cannot bypass admission to send directly. A fresh operation is created only through explicit preparation after custody validation. Missing, corrupted or unverified transferred custody withholds mutation authority. The same boundary checks operation identity, its captured predecessor, exact targets and required durable evidence.

Record dispatch intent durably before sending. Once an effect might have been sent, losing its response retains uncertainty. A received 5xx is not a generic rejection. Receipts retain their actual scope: 202 is acceptance; terminal `enqueued` establishes admission; neither establishes landing or suffix settlement. An operation-specific, attributable positive observation may justify recording the effect it establishes in the sole-writer domain. Absence, quiet time or a generic desired-state match cannot justify replay or settle possible future effects.

Known-not-sent, documented rejection, acknowledgement and indeterminacy remain distinguishable from the evidence. This proposal removes independently writable status flags; it does not remove those required observations. Likewise, a resolved API effect and permission to perform a later overlapping effect remain separate judgments.

When a process dies, the lock releases, but the persisted dispatch intent remains. The next process rereads it and reconciles or stops. It never interprets acquiring the lock as proof that the provider did nothing. Failed durability calls stop new dispatch; their visible local replacement is not proof of crash durability or of nonexecution.

### Compile all writes to exact effects

Use one planner and executor, with typed effect kinds for coupled Git publication, PR creation/reopen, base edits, membership edits, native admission/landing, history-comment delivery and local continuation installation. Their request, guard and evidence meanings remain specific. This is a small closed set of effects, not a generic plugin framework or a universal hosted-state oracle.

The planner takes accepted commitments, captured author intent and observed facts. It emits a fixed operation; recovery resumes that operation rather than regenerating it from the latest state. A changed plan is a deliberate successor after the predecessor's applicable barriers are resolved. Merely assigning a new operation ID cannot evade an unresolved overlapping request.

- First publication, append and same-order amendment emit only their necessary effects. The Git effect couples changed heads, new authored archives and deliberately public source refs, with explicit leases and no non-atomic fallback. Equal omitted refs are not full-vector guards; ABA remains outside value-lease guarantees.
- Any changed active order, including F-before-surviving-B after old A lands, uses the same structural compilation rule: release eligible membership, park affected open bases at trunk, publish coupled heads/archives, establish final bases and register the resulting order. Actual residual membership is an input. Do not issue already-satisfied base assignments merely to create another stage.
- Every usable hosted rewrite enters the same exact-range importer. Queue, direct landing and website rebase do not get independent import baselines. Incorporation advances its hosted/local pair; only a confirmed authored submission advances authored history.
- Continuation installation is an exact local effect in that operation: journal the intended new ref and accepted snapshot, create with an absence expectation, install the accepted result and validate their linkage on recovery. This retains the incumbent's fresh-continuation policy and its protection of source, index and working tree.
- History-comment delivery uses the same operation/effect rules but never supplies publication confirmation or integration authority. Its recorded canonical comment ID and expected content are client-owned bindings, not proof of exclusive provider edit authority. An observed changed or conflicting artifact requires reconciliation or explicit reattachment; an unchanged REST author field cannot justify overwriting another actor's edit. A read before an unconditional PATCH is not a concurrent-edit guarantee.

The incumbent already calls for one evaluator, one range importer and shared identity/recovery rules. Those are retained strengths, not new savings claimed by this proposal. The added commitment is that no alternate worker or adapter can enter mutation below that shared boundary.

## Required distinctions that should survive

Several attractive collapses fail the exposed evidence:

| Proposed collapse | Counterexample and retained distinction |
| --- | --- |
| One last revision instead of authored submission plus incorporated/local pair | Import hosted `x=1` while retaining local `y=1`, then import hosted `x=2`. The hosted baseline must be `x=1`; neither the older archive nor the local result containing `y=1` can replace it. Broader importer rounds reinforce this distinction. |
| One native success state | The same terminal admission receipt survives landing, ejection and dequeue. Keep receipt, membership, lifecycle and usable ranges separate. |
| One queue-method policy | SQUASH/build-two landed both; its build-one controls ejected upper. Configured REBASE/build-two did not deliver two actual builds. Record actual configuration and outcomes; do not manufacture a method-only guarantee. |
| One universal check-precedence rule | Candidate failure overrode successful source status in the tested status context; successful source deployment survived candidate deployment failure. Keep producer, subject and rule kind identifiable. Readiness is observed under current policy, not a generic green flag. |
| Comment author means exclusive ownership | The authorized bot edited a user-authored comment while the REST author stayed unchanged. Preserve explicit artifact identity and detect content conflict. |
| Completed receipt or matching reads means safe next write | No-read effects, natural 5xx effects and the unresolved suffix handoff defeat that inference. Keep possible provider effects even after local progress. |

Website rebase and automatic-prefix review results also remain separate evidence paths. The four human-attested website actions preserved/rebound review records and produced eight verified replacements; matched automatic-prefix controls dismissed unchanged reviews with stale dismissal enabled, with or without CODEOWNERS. Neither observation becomes a universal review/signing promise, and neither replaces last-push eligibility.

## Preservation mapping

| Contract | Candidate treatment and limits |
| --- | --- |
| C1 | Preserve ordinary committed authoring on one local branch, initially one commit per linear change. Explicit preparation captures exact intent and accepts mappings/differences. Retain unsupported originals and offer deliberate linearization; do not silently group duplicate IDs or flatten richer histories. The new broader net-range tests do not establish preservation of intermediate multi-commit history. |
| C2 | Preserve repository/destination enrollment, logical IDs, canonical PR continuity, explicit adoption, immutable vN archives and exact historical base/tip patches. The custody store does not create owner or incorporation authority from names, trailers or matching SHAs. Keep human prose separate from the generated history artifact. |
| C3 | GitHub still owns membership, trunk policy and native landing/rebases. GHerrit owns publication/reconciliation within its declared cooperating domain. Authors choose intent and readiness; participants own human prose. Ordinary unmanaged Git and deliberate private/public publication retain the incumbent policy. No service or CLI adapter is required. |
| C4 | One validated dispatch boundary realizes local cooperation; per-effect evidence retains partial/unknown outcomes. Whole affected scope and omitted suffix work are considered. No local lock, receipt, finite readback, atomic Git push or empty queue claims a provider fence. Transfers preserve pending records, and stopped old processes do not settle their requests. |
| C5 | One exact-effects planner covers initial publication, append, amendment and structural order changes; one importer covers actual hosted outcomes. F-before-B remains ordinary insertion preserving B's canonical PR. Closed-unmerged PRs require explicit reopen/withdrawal, merged IDs remain terminal, completed groups use a fresh eligible group, and omission alone does not close reviews. Shared prefixes, nonlinear/cross-fork history and oversized groups retain explicit restrictions. **Overlapping post-native publication remains gated by the unresolved handoff; this is still a restricted design, not a full-workflow replacement.** |
| C6 | Reduce duplicated custody metadata and gate placement where they exist, while retaining necessary evidence and effect-specific semantics. Count storage/locking/durability work, adapter duties and availability costs below. Do not treat fewer filenames or statuses as a demonstrated total saving. |
| C7 | Distinguish local prototype failures, inspected source, bounded hosted traces and design arguments. The proposed gate is not implemented or tested here. No inferred internal GitHub cause, idempotency, cancellation or future-write settlement is supplied. |
| C8 | Keep the incumbent's reversible enrollment/export/handoff. Preserve old archives, canonical reviews, accepted snapshots and pending operations. Disable legacy/native competing writers only for enrolled work; rollback waits for applicable resolution and translates custody deliberately. Do not restore legacy publication automatically after a failure. |

## Discriminating traces for adjudication

These are proposed candidate checks and arguments, not executed successes:

1. **Stale workers:** W1 and W2 both start before dispatch. W1 holds the custody lock, records dispatch/evidence and exits. W2 acquires it and rereads; no cached `planned` value can drive a second send. After W1 dies following send but before evidence, W2 instead finds indeterminacy and stops. This targets L28 without claiming a network fence.
2. **Missing evidence:** remove the operation after an effect while its root reference remains. Every mutation entry point, including the direct recovery worker, fails custody validation; none creates a replacement operation. An internally coherent old backup cannot generally reveal missing later intent, so unverified transfer remains recovery-only. This distinguishes the intended boundary from L14 and limits the claim.
3. **False completion:** delete or replace the continuation ref/result after installation. The completed view no longer validates; no new mutation authority appears. No mutable completion flag can bypass that check. This targets L13 without promising protection from arbitrary filesystem rollback.
4. **Foreign operation identity:** substitute Y's record for X. A single typed operation entry and its effect addressing cannot be admitted as X merely because Y is complete; deserialization/reference validation rejects the mismatch. This targets L29. A content hash alone is insufficient if the root points to the wrong operation without checking its predecessor and intent.
5. **Actual 504/502 creation:** record the sent create and server error, then observe the exact intended group. The initial request remains the reconciliation subject; a new label cannot authorize another create. Positive attribution may establish creation, but does not establish a future provider fence. Fresh disjoint work needs evidence-backed disjoint scope.
6. **After-ack structural restart:** kill after each S01–S09-style receipt. Resume only effects after the validated prefix. Missing receipt or changed B head stops as in S10a/b. These traces support a common executor; they do not justify assuming unknown effects acknowledged.
7. **Amended landed prefix:** capture A′/B′, observe old A landed, integrate hosted B and form new-ID F before canonical B. A single order planner emits the insertion plan when its handoff requirements are met. If they are not met, retain F/B and explain the restricted boundary. Appending F above B fails the dependency witness and is not a simplification.
8. **Independent text write:** change the owned history comment through a different authorized actor while preserving its author field. A later GHerrit projection that observes changed expected content withholds automatic overwrite. Human body changes remain in another artifact. If the API lacks a suitable conditional write, concurrent edits of that same comment need an explicit cooperation policy; the proposal supplies no field-level CAS by assertion.

## Whole-system burden and comparative recommendation

| Area | Difference from the incumbent and attributable cost |
| --- | --- |
| Semantic model | Preserve the incumbent's independently necessary identity, revision and outcome facts. No demonstrated semantic minimum has been found. A second generic desired-state engine would increase burden and is excluded. |
| Local state | Compared with the exposed prototype, remove cross-checks between a separately mutable pending manifest, operation identity and completion marker by deriving views from authoritative records. Replace them with transactional integrity and exact accepted-result validation. Those checks remain real work; consolidation alone is not enforcement. |
| Coordination | Add a concrete process-lifetime exclusion boundary and authoritative reread. That is required to realize the incumbent's one-cooperating-publisher premise, not an optional tax unique to this candidate. Cross-clone/service coordination is still excluded. |
| Executor and adapters | One mutation entry point reduces bypass opportunities and duplicated resume logic. Each effect still needs specific request encoding, guards, outcome interpretation and probes. Direct API calls avoid adding CLI version/side-effect adaptation. A service would inherit this protocol and add deployment burden. |
| Storage and recovery | The store needs crash-consistent updates, schema/version checks, retained objects and complete custody transfer. Accepted refs still require validation outside the store. SIGKILL evidence is useful; actual power loss remains untested. A failed fsync cannot be reclassified as known-not-written. |
| Users and availability | No additional command or acceptance interaction is required. Existing costs of preparation, fresh continuations, explicit conflicts and unknown-effect stops remain. Scope accounting remains necessary for safe disjoint work; deleting it by freezing the whole repository would shift burden to users. |
| Migration | Import current bindings/checkpoints/pending evidence into one validated representation, preserve old artifacts and refuse missing/ambiguous records. Verify predecessor/operation/result correspondence before enabling writes. This is a schema migration with recovery obligations, not free housekeeping. |
| Verification | Reuse the five-lane evidence as design witnesses, then check the direct dispatch boundary, stale-worker schedule, damaged custody, exact ref/checkpoint linkage and every alternate adapter entry. Add blind confirmation through root's steward; this architect provides none. |

The best comparison is therefore **the incumbent with this surgical realization constraint**, not a new broad semantic architecture. It should beat the known prototype on the demonstrated bypasses if implemented as specified. It has not yet beaten a correctly realized incumbent on measured implementation size, human comprehension, latency or operational cost; those comparisons remain open.

The provider handoff remains unresolved for both candidates. Authenticated website queue removal remains prepared/unadmitted, and independent author/reviewer studies remain unperformed. These facts limit particular behavior and usability claims; they do not prevent the grounded local-authority reduction above. The broader queue, CI, review, signing and protocol evidence should update the incumbent's factual assessment without being converted into extra GHerrit machinery or universal guarantees.

Root alone should decide whether to include the concrete custody/dispatch requirement in the next candidate, retain it as an implementation acceptance item, or select no conceptual change. No nested convergence was attempted. Requested model/effort was inherited; the host has not revealed the exact effective model or reasoning effort.

*Authored by an AI agent acting on joshlf's behalf.*
