# Architect alpha: separate local acceptance from remote settlement

Execution: swarm-model-refinement. Target: GHerrit native-stack decision model. This is bounded architect evidence for the coordinator, not an adjudication, convergence claim or production recommendation. Effective model and reasoning effort are unknown. The host supplies separate agent contexts, while the filesystem is shared without ACL isolation. I read only the authorized contract, discovery, incumbent, provider audit and exposed experiment reports. I did not inspect sealed cases, other architect proposals or prior swarm advocacy, and ran no new experiments.

## Result

The strongest supported reduction is surgical: **accepting a coherent hosted import into a retained local continuation does not require proof that the provider will never write again.** It records what was incorporated, rather than certifying remote finality. Retain the previous checkpoint and the unresolved external operation; keep the remote-write gate separate. This removes a false coupling without weakening the incumbent's remote-write promise.

There is also a useful narrower first-release domain: the author can stage a landed amendment as a separate follow-up F, land F, and only then publish the dependent amendment to surviving canonical B. That makes structural insertion unnecessary for this particular repeated-workflow trace. It does not replace joint F–B publication, deliberate reorder/insertion, or other structural edits. The cost is real author work and delay.

For overlapping hosted publication, the incumbent's proof-before-write promise and a retained-inputs/detect-and-reconcile promise are genuinely different. C1–C8 do not mandate the stronger one. A concrete weaker candidate is described below, but it does **not** dominate a correctly realized incumbent: it exchanges a stronger guarantee for availability and potentially repeated recovery. No observed late suffix overwrite validates or refutes that alternative, and its acceptance work remains open.

Several other listed questions are realization or release-scope decisions, not independent reconciliation mechanisms. Removing them from the semantic decision list does not make their implementation or human tradeoffs disappear.

## Governing boundary and sources

The common obligations are [C1–C8](../GOVERNING-CONTRACT.md) and the [focused contract](../CONTRACT.md). The incumbent is the complete [candidate-003.md](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/refinement/candidate-003.md), with the SHA-256 recorded in discovery. Its explanations are claims under comparison, not extra requirements.

I use these exposed witnesses:

- [Provider audit](../provider-audit/REPORT.md): direct terminal `merged` is a completed requested merge; terminal `enqueued` is completed admission. Post-terminal PR/ref disagreement does not establish a suffix write after terminal success. The official ordinary post-merge sync/push flow exists, but the inspected sources do not specify suffix completion/arbitration with later client writes.
- [Local results](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/local/RESULTS.md): repeated imports retain local amendments; a net-range test does not preserve multi-commit internal history. Invalid completion, missing evidence, mismatched operation identity and stale workers expose enforcement defects. Hook dry-run/destination ambiguity is real. Equal refs and ABA defeat treating value leases as a generation fence.
- [Protocol results](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/protocol/RESULTS.md): missing acknowledgements and received 504/502 responses can coexist with effects. Positive attribution used fresh sole-controller premises; absence was not proof of no future effect.
- [Structural results](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/structure/RESULTS.md): nine after-ack restarts retained PRs/archives; this is not unknown-response recovery, power-loss evidence or provider settlement.
- The incumbent's original connected hosted trace and the discovery inventory supply the A–B → landed A → F–B → landed F → imported B witness. It is exposed design evidence, not blind confirmation or proof of a fence.

All proposed native alternatives below preserve exact repository/change/review bindings; the distinct authored, incorporated, accepted-local and currently observed revision roles; human-owned prose; native topology/landing ownership; retained exact archives; and operation-specific partial/unknown evidence. None treats native membership, ancestry, SHA equality or a marker as authority. The unchanged-production row is compared separately and does not already meet these obligations.

## The smaller common model

Use the incumbent's evidence, without inventing a second reconciliation engine:

1. A canonical binding identifies the repository, logical change, managed head and continuing PR. Membership/group identity is observed topology, not change identity.
2. An accepted checkpoint names exact hosted ranges actually incorporated and the exact local result accepted from them. Its inputs and previous accepted checkpoint remain recoverable. A source branch may move afterward.
3. An operation captures accepted intent and exact inputs, affected scope, intended effects, dispatch evidence, receipts and unresolved results. Each effect keeps its own reconciliation semantics. Completion and mutation eligibility are derived from validated evidence, not independent booleans.
4. One local owner reloads that evidence at dispatch. Direct publication, recovery, transfer, hooks and adapters must use the same boundary. One owner is a protocol requirement; a checkout or service is a deployment choice.

These are semantic roles, not four databases or a proposed storage framework. The incumbent already largely has them. I claim no new simplification merely for restating them. The new reduction is in what local acceptance is allowed to mean.

A plan's acceptance is reusable only while the relevant captured intent remains the same. Its effect may resume if genuinely unsent and still eligible. An unknown dispatch is not made unsent by rereading desired state. A newly issued landing/admission request is an effect with its own identity even if the user acceptance can legitimately be reused. This common rule should govern every entry point; it does not itself decide whether a user authorizes a persistent goal across later revisions.

## Candidate S: local acceptance is factual, not a remote fence

### Exact domain

One enrolled publishing authority controls the affected chain, linked worktrees and captured local custody. Managed mutation and native issuance are serialized operationally; the legacy cascade is excluded. No arbitrary administrator or other clone is fenced. Ordinary trunk progress and human prose edits remain allowed. The first authoring domain is a validated linear sequence with one commit per local change; exact hosted ranges can contain multiple commits.

The import has usable exact ranges, valid canonical mapping and a supported per-layer integration. Disagreement such as old PR tip combined with a new comparison base is still an invalid import input. S does not permit guessing a range from inconsistent projections.

### Operation

The importer may preserve captured inputs, integrate into scratch objects, present the mapping/differences, and accept a new continuation/checkpoint **while an external native operation remains unresolved**. Acceptance must:

- Allocate a fresh continuation ref and retain the accepted exact result and incorporated ranges.
- Retain the earlier accepted checkpoint, all pending-operation evidence and each pending operation's captured inputs.
- Leave the caller's ref, index and working tree alone.
- Record the new local acceptance without changing a pending remote operation's intent, marking it complete, replaying it, or granting authority to overwrite an overlapping hosted resource.
- Resume a local ref/checkpoint interruption against its own recorded intent. A missing or damaged old external record remains a recovery problem.

A pending publisher must continue to use its captured input. It may not substitute the newest accepted continuation. Selecting a later continuation must not make stale dispatch eligible. If the current storage layout can only replace a checkpoint while discarding pending custody, that layout needs repair; the semantic reduction does not authorize discarding it.

The incumbent's statement that protected-checkpoint replacement awaits handoff should therefore be narrowed to destructive changes or changes that grant remote mutation authority. Creating a retained successor acceptance is neither. The existing immutable accepted-result/successor-attachment concept can carry this relationship; no second queue baseline or global scheduler is needed.

### Constructive trace

Let the incorporated hosted patch be H0 (`x=0`) and the local range include unpublished `y=1`. A native operation remains pending or otherwise unresolved.

1. A coherent hosted range H1 has `x=1`. Import H1, retain `y=1`, and accept local R1 with checkpoint `(H1,R1)`. Keep `(H0,R0)` and the external operation.
2. Native work later exposes coherent H2 with `x=2`.
3. Import H2 using H1 as the incorporated baseline and R1 as local input. The accepted result retains `y=1` and takes `x=2`, or presents a real conflict.
4. If the canonical PR actually landed, transform retained local changes into a proposed new-ID follow-up under the existing lifecycle rule. Local acceptance did not promise the PR would stay open.

Nothing in this argument requires H1 to be the provider's last range. The checkpoint is evidence of integration, not a claim about future writes. The broader importer fixtures support repeated-baseline reasoning, but no new S implementation was executed.

### What S closes and what it does not

S conditionally dominates a blanket future-write-fence requirement **for local, retained continuation acceptance alone**: it preserves the old inputs and remote restrictions, while permitting useful committed local progress. It adds no new remote race and uses checkpoint history already required for recovery. It still needs correct local custody implementation and validation.

It does not close overlapping publication, queue cancellation, provider arbitration, structural lifecycle safety, or an unknown client write. It also does not establish a complete replacement workflow while all overlapping remote publication remains gated. That limitation must stay visible.

A counterexample would be a supported entry path where accepting R1 necessarily consumes the only evidence required to reconcile the old operation, or where a worker treats new local acceptance as completion of that operation. That falsifies the realization of S. A representation that retains both records avoids the counterexample without a new provider premise.

## Candidate T: stage F before publishing dependent B

C5 expressly permits a named staged restriction. For the required landed-amendment case, compare these concrete paths:

| Path | Preserved observation | Cost or lost promise |
| --- | --- | --- |
| Incumbent joint F–B regrouping | F and amended canonical B can be reviewed/published together in their dependency order. | Needs safe unstack/parking/regrouping plus overlapping-write authority. |
| Staged F, then B | Preserve canonical B and retained B edits; F is on trunk before the dependent B amendment is published. | Separate F review/landing, delayed visibility of B's amendment, extra author decisions and latency. |

The staged trace is:

1. Publish A–B. The author has local A′ and B′, with B′ depending on A′.
2. Old A lands. Retain the local differences and propose new-ID F for A′; keep B′ unpublished with its dependency explicit.
3. With explicit acceptance of staging, publish **F alone** against trunk as a fresh ordinary PR under native intent. Retain B's canonical binding, original review, pending edits and checkpoints. Do not make B depend on F's managed head or quietly include it in F.
4. Land F, then incorporate actual trunk/F and hosted B outcomes. Rebase the retained B amendment onto that incorporated result, preserving per-layer ownership.
5. Publish amended B to its existing PR when that candidate's remote-write authority conditions hold. Native membership/lifecycle remain observed facts; a completed group is not assumed reopenable.

This avoids structural insertion **only for this continuation when the author accepts the staging condition**. Every remote step still requires the selected candidate's authority and scope checks; a fresh F ID/head does not prove disjointness from an old operation or shared trunk/checkpoint effects. T does not create a general insertion algorithm, remove an unknown old operation, or prove B safe to update. It retains the provider question at step 5 under the strict incumbent promise.

Counterexample: the author needs reviewers to assess F and B′ together before either lands, or F cannot sensibly land independently. T does not preserve that use. Thus T is a narrower support choice, not a dominating replacement for joint F–B. For such work the structural path remains required. Deliberate reorder/drop/fold and shared-prefix publication also remain outside T.

## Candidate R: recoverable publication without a no-later-write promise

This is the strongest plausible alternative to the provider gate, not an established closure. It is separate from S, which preserves the strict promise.

### Promise and assumptions

R promises retained authored input, exact confirmed authored archives, preserved observed hosted inputs, attribution of actual outcomes, and reconciliation before subsequent use. It does **not** promise that no older native operation can later alter a published head/base, or that a successful publication leaves remote presentation unchanged indefinitely.

The domain is the same cooperating authority as S, with known destination/namespace ownership and no independent competing head/topology writer. GitHub may finish native work asynchronously. R requires eventual provider quiescence for eventual stable publication and continued connected invocations for detection; it supplies neither a time bound nor an always-on monitor. Uncaptured independent UI activity and genuinely unknown overlapping client dispatch retain explicit recovery restrictions. R does not convert a received 5xx or missing acknowledgement into permission to retry.

For an initial narrower R milestone, direct landing with a recorded terminal requested result is easier to specify than queue processing. Queue admission cannot be used as a landing-completion token. Queue support needs the separately observed lifecycle/queue state and operation evidence, without a universal no-future-write inference. This is a release-domain restriction, not a method-only reliability claim.

### Concrete protocol

1. Retain every authored input and the full affected hosted chain, including locally omitted suffix work, before mutation. Bind operations to immutable captured checkpoints.
2. Reconcile completed requested effects and actual lifecycle. For local import, require usable exact ranges; accept a retained continuation under S. Missing/indeterminate overlapping client effects remain unresolved unless operation-specific evidence settles them.
3. Capture and accept the next publication plan. Revalidate actual heads/bases/membership and use explicit leases on transmitted coupled head/archive/source updates. Do not treat unchanged refs, atomicity or leases as a future-native-write fence.
4. Journal and execute each PR/base/membership effect using the same dispatcher. Record partial progress and unknown outcomes. No blind retry, corrective overwrite loop or automatic replacement PR is implied.
5. A fully confirmed export records the exact captured authored submission and its archives. Confirmation is an observed result, not certification of future stability. A rewrite during confirmation produces divergence/partial progress; it does not permit installing an invented fully confirmed checkpoint.
6. On the next connected status, preparation, resume or publication, compare the new exact hosted ranges/lifecycle/topology with the operation's retained evidence. Import a later native range using the incorporated baseline and retained local result. Preserve unpublished amendments and make conflicts explicit. If a PR has actually merged, a retained amendment becomes a new-ID follow-up; this cannot undo effects already landed.
7. Recovery never assumes that the latest local source or latest observed hosted range is automatically the new intent. A corrective publication requires an accepted plan against the actual state. Ejection or new rewritten heads do not silently renew landing authority.

R permits the ordinary repeated workflow rather than indefinitely refusing every overlapping write. Combining it with T supplies a narrower useful F-before-B path without requiring first-release joint regrouping. Supporting joint F–B also requires the structural lifecycle protocol, and late native writes during structural parking/rebuild can have consequences beyond a changed head. They must be tested and included in the accepted recovery promise; R is not evidence that such consequences are reversible.

### Discriminating counterfactual

A direct A landing completes. A coherent surviving B range H1 is imported; the author publishes a new B revision with an immutable archive. An older native suffix rewrite subsequently installs H2 over B. Under R, the next connected evaluation detects B's divergence and preserves both the archived submission and H2, then proposes integration/republication. Under a correctly supported strict incumbent, this trace is excluded before the later publication.

The retained observations do not show this counterfactual actually happened. The provider audit says the observed PR/ref mismatches could be projection lag. R must therefore be evaluated for the trace as a possible failure model, not advertised as an empirically needed fix.

If a delayed structural/native effect makes a canonical PR terminal or changes membership while publication is in progress, preserving bytes alone does not preserve an open canonical review. A new-ID follow-up may be necessary; the old discussion remains, but continuity/latency can worsen. If the required promise is that this can never happen, R needs additional provider semantics or a narrower domain and cannot replace the strict candidate. Treating a follow-up as equivalent to undoing an unintended landing would be false.

### Comparative conclusion for R

R removes the strict candidate's *dependency on proving future native exclusion* by offering a different promise. Most retention/import machinery is already required by C2/C4/C5; the additional work is precise divergence classification, operator presentation and corrective-plan acceptance. Recovery episodes, delayed review state and possibly terminal-review follow-ups are additional user costs. There is no whole-system measurement establishing that these costs are lower.

Therefore: R is not a dominance result. It is an explicit candidate for a product decision and targeted validation. A production recommendation requires the coordinator to judge that recovery promise acceptable and validate the actual protocol. The missing fence is not thereby proved or supplied by an adapter. Conversely, its absence is not by itself a proof that R violates C1–C8.

## Collapse the inventory without hiding real choices

| Inventory item | Correct classification / proposed first boundary | Exactly what disappears; what remains |
| --- | --- | --- |
| Local checkpoint acceptance versus provider handoff | Apply S. | The handoff prerequisite for retained local acceptance disappears. Remote-write authority stays separate. |
| Landing versus queue/UI integration | One exact-range importer; retain interface-specific effect evidence. | A second integration baseline/engine has no demonstrated purpose. Admission, landing and unknown UI initiation remain distinct facts. The incumbent already mostly makes this reduction; no new credit. |
| Complete marker, missing evidence, stale worker, mismatched operation identity | Required dispatcher/accepted-result invariants, not optional backends. | No product choice to support unsafe recovery. Storage layout and implementation verification remain work. One journal design is not mandated by the failures. |
| Explicit renewed request versus continuing authorization | One accepted-intent rule, with exact effect identities. Start with renewed acceptance when relevant intent changes. | No need for separate reconciliation engines. A broader persistent landing goal is a real additional authorization promise; automatic re-admission is not proved equivalent. |
| Commands versus hook | Start with explicit invocation; any hook invokes the same accepted-intent boundary. | No hook-specific publisher. An opaque mutating pre-push hook cannot preserve dry-run/destination semantics when its inputs do not distinguish them. A hook whose invocation carries adequate intent remains a convenience option, not a dominated universal alternative. |
| Checkout versus service | One authority per conflicting scope; start with one checkout if collaboration permits. | Independent clients are not a new correctness mode. A service remains a real deployment/collaboration/security/availability tradeoff. No deployment wins universally. |
| Direct typed calls versus released CLI | Select direct calls for the archive-coupled first publisher. Treat narrow CLI linking as an effect implementation. | Broad released submit is not an interchangeable realization under the same archive coupling. Narrow URL linking still needs its base/readiness effects and version/recovery costs. A future compatible adapter could reduce maintenance, so direct calls do not universally dominate delegation. |
| Comment, body section, separate view | Archive exact objects; project a generated index; choose a reviewer surface. Start with the tested owned comment. | Archive and generated index cannot replace each other. Concurrent human-body preservation makes naive body read/modify/write invalid. A coordinated section or dedicated view can win on discovery; human preference remains unmeasured. |
| One commit versus richer history | First release is one commit per local change with exact hosted ranges. | Internal-history preservation is not inferred from net-range tests. Richer authoring is a real extension, not a first-release configuration knob. Its excluded uses stay named. |
| Queue methods/checks/rules/signing | One target compatibility assessment, using actual provider policy and outcome evidence. | No universal green flag or method-only reliability rule. A release must still choose supported promises/routes; this table does not magically select them. |
| F-before-B after landed amendment | Apply T only with author acceptance. | Mandatory structural insertion for this staged use disappears. Joint publication and deliberate structural edits retain their mechanism and safety obligations. |
| Rollout, transfer and rollback | Preserve custody and exclude old dispatch; translate/export on deliberate handoff. | No automatic legacy fallback or mode-flag cancellation. Concrete migration and transfer validation remain mandatory. |

The honest smaller *semantic* decision set is: the remote publication promise (strict versus specified recovery), accepted authorization breadth, and supported authoring/structural domain. Invocation, transport, placement and history surface remain consequential realization/product defaults with measurable tradeoffs. Listing fewer headings would not eliminate those tradeoffs, and I claim no general lower bound on the number of decisions.

## Whole-burden comparison

| Candidate | Preserved benefit and burden removed | Burden retained, added or shifted |
| --- | --- | --- |
| Current production publisher unchanged | No migration or new deployment; existing hook familiarity. | No native ownership/import protocol, local-only version allocation, no durable canonical binding, competing cascade and partial-publication hazards. These are shared-contract deficits, not a free baseline. |
| Correctly realized incumbent strict protocol | Canonical reviews, exact archives, explicit identity, local authoring and strong exclusion of older possible native writes before overlap. | Identity/import/dispatcher/custody implementation, single-authority friction, provider completion/arbitration premise, human acceptance and migration checks. If the premise stays unavailable it remains a pilot, not full C5 fulfillment. |
| S surgical incumbent | All strict hosted promises retained; local continuation need not await a remote fence. | Correct successor/checkpoint custody and stale-worker validation remain. No new remote engine. Full overlapping publication remains gated. |
| S + staged T, still strict | Adds a useful author-approved staging option; avoids insertion solely for that continuation. | Separate F landing and delayed B edit; final B overlap still needs strict authority. This is not a complete solution to the provider question. |
| R, optionally using T | Useful repeated overlapping work under a recoverable-state promise; no proof-before-write future-fence dependency. | Same core evidence/identity/import/dispatch work; recovery classification and corrective author acceptance; more remote drift/review disruption risk; eventual-quiescence assumption; production validation unperformed. Joint structural support remains harder than same-order/staged support. |
| Service or CLI variant of any row | May centralize collaboration/credentials or reuse provider integration code. | Inherits that row's promise and recovery duties. Adds its actual hosting/version/adaptor/transfer burden; no handoff theorem follows from placement or reuse. |

S is the only reduction here that preserves the incumbent's remote promise without a product-value exchange. T is conditional domain narrowing. R is a promise exchange with potential practical benefit, not a demonstrated lower total burden. New PR generations, replacing archives with comment history, or duplicating the native/legacy cascade do not improve this comparison under the retained defaults.

## Falsifiers and remaining checks

These are proposed discriminators, not executed experiments:

1. **S custody/dispatch:** accept a new retained checkpoint with an unresolved older operation, interrupt local acceptance at its durable prefixes, and resume a stale publisher. Any lost old input, erased unknown record, substituted newer intent or newly admitted overlap refutes the realization.
2. **S repeated import:** accept H1/R1 while an operation remains unresolved, then integrate H2 with independent local amendments. Check per-layer patches, messages, accepted checkpoints and actual pending-operation identity. Cumulative tree equality is insufficient.
3. **T applicability:** an author requires joint F–B review or F is not independently landable. This defeats T for that work; it is not an implementation bug to fix with hidden staging.
4. **R delayed effect:** a controlled native completion/rewrite race after a confirmed export must leave every original/new authored input and observed hosted range recoverable, classify actual lifecycle correctly, and require accepted correction. An archive cannot be cited as evidence that an already landed effect was undone.
5. **R scope:** a native effect outside the declared preserved scope, an unobserved external author edit treated as incorporated, or a new dispatch after genuinely unknown overlapping client effects refutes the claimed protocol/domain.
6. **R liveness:** under an eventually quiescent provider, a normal A–B / landed-A / staged-F / canonical-B repeated trace must complete rather than remain permanently gated. A refusal-only prototype does not meet the proposed promise.
7. **Transport/human defaults:** demonstrate a compatible hook with accurate dry-run/destination intent, a cheaper CLI adapter with the same effects/archives, a service with a concrete collaboration benefit, or a reviewer surface with better actual discovery/comprehension. Any can defeat a default's claimed practical advantage; no human comparison was performed here.

The coordinator should retain the strict incumbent and R as distinct promise candidates unless further evidence or an explicit product decision resolves them. Adopting S does not require that decision. Root owns comparative adjudication, further review, rereads, stopping and any publication.

*Authored by an AI agent acting on joshlf's behalf.*
