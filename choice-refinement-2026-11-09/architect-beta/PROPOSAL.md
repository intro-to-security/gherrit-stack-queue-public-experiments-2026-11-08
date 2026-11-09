# Architect beta: accepted intent can span several requests

Execution: swarm-model-refinement. Foundational guidance: model-refinement, robust-code, reader-oriented-explanation, Williams-style and authorship-disclosure. Target: GHerrit's native-stack decision model. This is bounded candidate material for the coordinator, not an acceptance, convergence or production-readiness decision. Model and effort were inherited; exact effective settings are not exposed. I read only the contract, exposed discovery material, the complete incumbent, the permitted provider audit and the exposed reports cited below. I did not inspect sealed cases, other architects' proposals or coordinator advocacy, and performed no live mutation or new test.

## Proposed common rule

An accepted user intent authorizes effects on captured work within an enrolled ownership scope. A dispatcher may perform a particular effect only while that effect is still justified by that intent, current custody and the evidence required for that effect. A command invocation, an API request, a queue admission and achievement of the user's goal are different boundaries.

This is mostly the incumbent's good core. The useful proposed semantic change is narrower: remove the categorical rule that a later admission must always be a newly accepted user intent. A later admission is always a distinct provider request, with its own identity and outcome; it may continue an already accepted, explicitly scoped user intent. Nothing about the new request grants permission to resend an unresolved old request, accept changed patches, bypass readiness or infer provider settlement.

The same rule also explains how an explicit command, a compatible hook or a service could use one executor. It does **not** establish that those realizations have equal cost or user value. Likewise it does not eliminate the separate authored, incorporated, accepted-local and observed revision roles, nor the necessary outcome distinctions. Renaming those things as one operation would lose information.

I favor this surgical refinement over introducing a generic workflow framework. Keep the first realization explicit, local, one commit per linear change, direct API calls and a separately owned history comment. Permit more automation only when a user actually requests the broader authorization and the implementation validates it. The one-shot path needs no persistent automation goal or extra user selection.

There is a separate, consequential possible generalization: replace the incumbent's universal future-native-write exclusion gate with a precisely stated recovery promise. I describe that alternative below, but do not claim its current evidence establishes safe production adoption or dominance. These two proposals must not be bundled: broad captured intent cannot settle an outstanding provider operation.

## Preservation boundary and retained domain

The base candidate retains the incumbent's domain and restrictions:

- One local branch, validated linear history and one authored commit per logical change initially. Explicit range boundaries remain necessary for hosted revisions. Unsupported merge histories, multi-commit grouping and shared-prefix publication are rejected before mutation with original objects retained.
- Explicit repository/change/head/canonical-PR bindings, verified Git/API destination agreement, immutable exact authored archives and human-owned prose. A new native group number does not create a new logical change or a new review.
- One cooperating authority for every conflicting scope, including hosted suffixes, shared targets, managed trunk dependencies and pending effects. It must reload durable current state under the actual owner immediately before dispatch. No arbitrary-administrator safety claim is added.
- Captured source objects, authored submissions, incorporated hosted ranges, accepted local results and current observations retain their independent meanings. The importer and fresh continuation policy remain unchanged.
- Known-not-sent, established rejection, acknowledged result and indeterminate effect remain different. A 5xx is not automatically a rejection. No unknown create, append, unstack, admission or comment write is blindly retried.
- Native membership, rules and landing remain GitHub-owned. GHerrit does not restore its cascade. Native direct merge, queue admission and queue processing retain their different outcomes.
- Existing discussions, archive refs and pending operations survive adoption, transfer and rollback. Missing evidence does not manufacture fresh authority.

The candidate supports the same successful first-publication/append/amend/import traces within the incumbent's supported authority boundary. It also preserves the incumbent's current restriction on overlapping post-native republication unless a supported completion or recovery promise is selected. Therefore the surgical change alone does **not** close the full F-before-surviving-B workflow gap.

## What captured intent means

The model needs enough captured information to answer the existing questions, rather than a new universal operation language:

1. Which enrolled repository, canonical changes, reviews, trunk, source inputs and possibly affected resources are involved?
2. What did the author accept: the exact publication mapping/differences, one admission of an exact selected head, or a broader goal that expressly permits a named continuation?
3. Which observed transitions leave that acceptance valid, and which require new acceptance?
4. Which effects have been dispatched, what do their receipts establish, and what remains unresolved?

The first and fourth are already incumbent duties. The second and third become material only when offering continuation beyond one exact request. They cannot be replaced by “same change ID,” “same PR,” “same tree” or “the command is still running.”

For the initial one-shot landing command, accept exactly the captured request, including selected revision, intended prefix, method/options and destination. A replacement head or another admission requires renewed acceptance. This has the same user semantics as the incumbent.

An optional later automation can instead accept a precise goal such as landing the captured logical changes into the named trunk, permitting only validated native parent changes that preserve their accepted change-local patches. Such a goal must name any recoverable transition through which it may continue, such as one ancestry-only ejection; otherwise ejection or policy failure stops it. Content change, cancellation, missing evidence or ambiguity always stops this example goal. A user choosing that behavior authorizes continuation once. Each later provider request still records its own selected head, options, scope and outcome. If continuation changes the ordered work, messages in a way the user has not accepted, patch ownership, publication visibility or relevant landing options, it falls outside the accepted goal.

This is not an invitation to infer arbitrary semantic equivalence. The existing range model can compare exact change-local patches against a changed comparison parent. Where that check is ambiguous or conflicting, stop for acceptance. An unchanged cumulative stack tree is insufficient: it can hide an upstream edit moved into the wrong review.

No automatic repeating retry loop is proposed. A continuation feature needs an explicit stopping rule for an ejection or policy failure and a way to withdraw unsent future requests. A first implementation can simply stop on ejection; a later product request may justify an explicitly accepted, bounded continuation after a particular recoverable transition. Do not add a generic retry-budget configuration surface before that use exists. Withdrawing future dispatch does not cancel requests already sent.

### A discriminating queue trace

The exposed queue experiment first landed A, ejected/rebased B, then explicitly requested B at its new observed head and landed canonical B. It preserves two request UUIDs and does not establish automatic re-admission policy or suffix settlement ([queue report](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/queue/RESULTS.md), “Explicit re-admission”).

Under a one-shot accepted request, both incumbent and candidate stop after the first admission outcome; a user accepts the new B request. Under an expressly accepted continuing goal, the candidate can issue the new B request only after the same ownership, outcome-resolution, range-usability and readiness obligations are met and the replacement B falls inside the accepted transformation. This is genuine additional authorized behavior. A merely ejected B with changed authored content does not qualify. Nor does an empty queue prove that an unacknowledged admission is cancelled.

The existing evidence supports the feasibility of the second request, not a production continuation implementation. The optional feature adds transformation-validation, stopping/cancellation and durable goal-custody burdens. Its benefit is reduced repeat acceptance for explicitly requested automation, not fewer concepts overall. It is not universally better than the one-shot default.

## Completion, usable ranges and later authority must be assessed separately

The permitted [provider audit](../provider-audit/REPORT.md) changes how the gate should be stated. Direct terminal `merged` is positive completed-request evidence; terminal `enqueued` completes admission and remains unchanged after queue landing or removal. Current GitHub documentation also describes automatic suffix rebasing and a normal sync/rebase/push workflow after a bottom-layer merge. The sources do not explicitly bind the last suffix write to the direct request's terminal status, or specify arbitration between an older native rewrite and a later client write.

The retained post-terminal PR-head/ref mismatch proves an unusable mixed observation. It does not establish that a suffix ref write happened after terminal success: a lagging PR projection remains consistent with the evidence. Consequently:

- Do not classify a known completed direct merge as an unknown admission merely because suffix usability is unresolved.
- Do not import an old tip with a new comparison base or advance a checkpoint from inconsistent range evidence.
- Do not infer “no possible future write” from coherent finite reads, a local lock, request-result expiry or an empty queue.
- Do not treat the stronger no-late-write promise as a requirement supplied by C1–C8. The contract permits a useful, explicit recovery promise if it preserves the required observations and its costs are counted.

These distinctions are necessary even if the coordinator retains the incumbent gate. They are a correction to the question, not proof that the question disappears.

### Conditional alternative: recoverable post-native publication

A candidate release could choose this weaker promise instead of promising that delayed native writes are impossible:

> Within the cooperating-writer domain, GHerrit preserves each captured authored intent, every exact input it incorporates and all unresolved operation evidence. It publishes from usable observed ranges with the available guards. If later hosted work differs, it exposes and reconciles that difference; it does not silently equate observation with acceptance, erase submitted intent or automatically replay an uncertain operation. Confirmed publication means confirmed at the recorded observation, not permanent immunity from later native changes.

That promise admits useful normal repeated work without pretending to prove a universal fence. A concrete proposed protocol is:

1. Before GHerrit initiates native work, retain the entire affected chain's exact current ranges, authored inputs, canonical bindings and the request's captured scope/options. Cooperating external UI work requires equivalent captured scope; uncaptured activity remains external uncertainty.
2. Resolve the requested operation's actual outcome at the boundary the provider exposes. Direct `merged` can resolve the requested prefix. `enqueued` resolves only admission; keep following actual queue/lifecycle evidence. Missing acknowledgement, received 5xx with uncertain effect and unresolved cancellation remain unresolved and cannot be converted into success by this policy.
3. Fetch and preserve exact hosted ranges. A disagreeing head/base/ref set is not usable for import. Import usable ranges into preserved scratch state with the existing per-layer baseline algorithm. Present the accepted result and any local changes as before.
4. Before later publication, preserve all affected observed hosted inputs and bind the accepted local intent to the particular export. Apply exact leases and the required atomic coupled ref transaction; track all separate PR/topology effects. Reconcile a changed expectation rather than refreshing a lease and overwriting unincorporated work.
5. Describe successful export as a confirmation of that captured publication at the recorded observations. Retain its exact authored archive and accepted local result independently of later observations. Do not mark a moving source branch submitted.
6. On subsequent status/sync/dispatch, compare hosted work with that recorded export. If a late rewrite removes or changes an accepted patch, display that change as hosted drift requiring explicit acceptance or restoration from retained intent. A normal three-way merge must not quietly consume that difference as if the author had withdrawn the submitted edit. No new landing request is automatically authorized merely because recovery can retrieve the bytes.
7. If the late activity changes lifecycle, membership or ownership beyond an in-place repair, stop with all evidence. A merged canonical review stays terminal; the author may accept a new-ID follow-up retaining the old discussion and archive. Do not silently make a replacement PR. Rollback remains a handoff, not a jump back to a legacy writer.

Step 6 is a real added requirement, not free reuse of the existing importer. For example, after exporting a local `y=1` change, an older native rewrite could restore `y=0`. Treating the just-exported range as baseline and silently accepting the new hosted tree would remove the accepted edit. The recovery policy must expose that drift and retain the exact `y=1` submission. The existing distinction among authored, incorporated and accepted-local results is essential to this case.

This protocol gives a concrete, testable weaker promise, but it is not a proof of a safe production replacement. Its limits must be prominent:

- A delayed rewrite could temporarily remove the intended hosted patch, invalidate checks/reviews, disturb topology or cause lifecycle changes that cannot be reversed on the canonical PR. Retained objects do not prevent those outcomes or restore review continuity automatically.
- Reconciliation detects differences when a later observation occurs. No continuous watcher or guaranteed detection latency is supplied. An offline client cannot promise to record every transient hosted revision.
- Useful progress assumes a finite period of provider activity and no uncoordinated structural writer. Under sustained interference the protocol preserves inputs and stops; it cannot promise convergence or correct final landing by retrying indefinitely.
- Git leases protect the values actually updated, with the known equal-ref/ABA limitations. They do not arbitrate future native writes. The protocol has no stronger fence than the incumbent.
- A completed prefix outcome does not itself make F-before-B structural edits safe against all later lifecycle effects. The proposed recovery contract deliberately accepts some resulting repair/refusal risk. If canonical continuity through those races is an absolute release promise, this alternative cannot replace the gate without more provider semantics.

The current sources support ordinary post-merge sync-and-push as intended provider use and identify the observed inconsistent-input case. They do not establish this recovery protocol's implementation, user acceptability or acceptable lifecycle risk. The follow-up structural restart evidence covers nine after-ack recoveries under a sole-controller premise, not late-write conflict recovery. I therefore present this as a qualified release-promise alternative, not as a closed implementation task or a demonstrated dominance result.

## Mapping the open choices

| Question | What the common rule settles | What remains a real choice or required check |
| --- | --- | --- |
| Renewed versus continuing admission | Fresh provider request identity and fresh user authorization are not the same thing. Continuing authorization must be explicit in the captured goal; unknown requests are never replayed. | Whether users want continuing landing and which transitions they authorize. The first default remains one-shot. No cost or preference evidence establishes universal superiority. |
| Direct versus queued versus website outcomes | Use one range importer and retain the actual evidence boundary of each operation. Complete requested merge, complete admission, lifecycle, range usability and overwrite authority are separate facts. | Exact provider completion/arbitration semantics; website capture/completion; release recovery promise. A universal scalar success status is excluded. |
| Explicit commands versus hook | Invocation must supply actual destination, captured input, dry-run intent and the intended effect. A shared evaluator/executor avoids a second semantic engine. | Convenience and reliable intent transport. The ordinary pre-push input cannot distinguish the observed dry-run case; a compatible hook needs a GHerrit-aware wrapper or another reliable capture mechanism, with its added cost counted. The two invocations are not unconditionally interchangeable. |
| Checkout versus service | One current authority must own each conflicting scope and pending-operation custody. Transfer moves that custody and excludes old dispatch; location alone does not settle pending provider effects. | A local checkout minimizes deployment for one publisher; a service may earn its credentials, availability and operational costs through multiple clients/automation. This is a deployment tradeoff after a shared correctness requirement, not a vanished decision. |
| Typed API versus released CLI | Every delegated side effect must fit captured intent and use the same recovery/ownership protocol. A versioned subprocess is a realization, not a second publisher with looser semantics. | The released broad submit cannot meet the coupled source/archive push contract. PR-URL link avoids the observed push but can repair bases; a constrained adapter needs side-effect and unknown-outcome validation. Direct calls remain the narrow default; no whole-system cost measurement proves dominance. |
| History comment/body/view | Immutable exact submissions are data; the owned generated index and the reader interface are separate duties. Human prose remains owned by participants. | A comment avoids a new host and whole-body races but has discovery, deletion, permissions and size obligations. A coordinated body section needs its concurrency protocol; a separate view needs hosting/discovery. All must reach exact historical patches and explain changed-parent comparisons. Human preference is unmeasured. |
| One commit versus richer ranges | The existing backend range representation does not require every hosted revision to contain one commit. One-commit local authoring is a restriction, not a provider law. | Lossless internal local history/messages, grouping identity and merge/shared-prefix lifecycle need real policies. Existing multi-commit tests prove net-range integration, not lossless richer authoring. Adding that domain now would add mapping burden. |
| Target support profile | Compatibility is checked against the target's actual event/check/producer/SHA/rule/method path; correctness is not an optional backend mode. | Which release workload is worth supporting. MERGE's observed success is a proposed starting profile, not a method-only guarantee; SQUASH/build concurrency and REBASE's missing second build prevent a universal shortcut. |
| Storage, dispatch, transfer and rollback | The same durable operation identity and validated result must govern every effect entry path. Completion is not a bare flag; authority is not a stale admission result. | A concrete implementation and acceptance checks. The local failures prove boundaries must be enforced, not that a service, database or general framework is mandatory. |

Most rows are a common invariant plus a retained tradeoff. I would not report them as eliminated choices merely because the common invariant is clearer. In particular, “one executor” was already substantially present in the incumbent, and a deployment parameter is not a proven complexity reduction.

## Discriminating traces and obligations

| Trace | Candidate observation | What it discriminates |
| --- | --- | --- |
| Source T is accepted; source moves to U during publication. | Effects and checkpoint name T; U remains pending. Hook, command and service have the same obligation. | Accepted intent versus reading the current branch at dispatch. |
| One-shot AB admission lands A and ejects B at a replacement head. | Report actual A/B outcomes and original receipt; no automatic B request. | Queue receipt versus goal completion; default unchanged. |
| An expressly accepted continuing goal sees that same transition with a validated unchanged B patch. | A new B request may continue that goal only after all outcome, authority and readiness conditions hold. | Genuine extension beyond mandatory renewed user acceptance; not replay of the first UUID. |
| Replacement B changes its patch or messages outside the accepted transformation. | Stop for new acceptance even if B's ID/PR and final stack tree match. | Broader goal versus blanket authorization. |
| A request loses its HTTP response; state is absent in one read. | Retain unknown and withhold overlapping dispatch. | Goal continuation cannot manufacture no-effect evidence. |
| Direct merge UUID says merged, but B's PR head and Git ref disagree. | Requested prefix may be known merged; B is not an importable mixed range. | Completed request versus usable observation. |
| Export E is confirmed, then a delayed native range N removes E's accepted `y=1`. | Base candidate retains the gate. Weaker alternative retains E and N, exposes drift and requires acceptance/restoration rather than consuming it silently. | Actual cost and weaker promise of recoverable overlap. |
| Local A′–B′ needs new-ID F below surviving canonical B after A lands. | Same range importer and structural insertion path; preserve B and exact inputs. Base remains gated; recovery alternative proposes the full F–B trace under its declared weaker promise. | No credit for append-only refusal as complete repeated work. |
| Completed record loses continuation/checkpoint; a direct worker is invoked. | Refuse before mutation unless a validated successor attachment exists. | A shared actual boundary versus a cooperative preflight ritual. |
| Service takes over while an old native request is unresolved. | Transfer includes the exact pending intent and checkpoints; old dispatch is excluded; unresolved request remains unresolved. | Moving the authority does not settle external work. |
| Human edits body while a privileged bot can edit the history comment. | Preserve human prose; comment identity alone proves no exclusive ownership. Detect lost/deleted/ambiguous index and recover through recorded effects. | Owned artifact contract versus marker/author-name inference. |

The local follow-up report supplies concrete failures for missing evidence, mismatched operation identity, stale workers and invalid completion, as well as the hook/dry-run and range-history controls. The structural report supplies the bounded acknowledged restart evidence. These are exposed design witnesses, not reserved confirmation or production acceptance ([local report](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/local/RESULTS.md), [structural report](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/structure/RESULTS.md)).

## Comparative burden and changed promises

**No change is defensible.** The incumbent already separates revision roles, native ownership and partial/unknown outcomes; starts with a local explicit client; permits compatible hooks/services; and acknowledges the provider gap. It adds no new continuing-goal policy. Its material cost is that a strong overlapping-write gate leaves the full repeated workflow restricted, including ordinary landed-amendment recovery. That is an availability and adoption limitation, not proof of superior correctness under the governing contract.

**The surgical candidate** removes one unconditional semantic restriction: every later admission requiring renewed user acceptance. It replaces that restriction with the already-required accepted-intent boundary and explicitly permits a broader user goal. It preserves exact request identity and every effect gate. A user who chooses the existing one-shot path sees no new interaction. If continuation is implemented, it adds accepted-transformation validation and goal stopping/custody, and may reduce repeated interaction for users requesting automation. No measurement establishes net maintenance or human benefit. Keeping the one-shot default therefore has a strong narrow-domain case.

**The recoverable-overlap alternative** changes one additional promise: exclusion of every possible late native write becomes preserved intent plus exposed drift and repair under a stated collaboration domain. That is a real weakening in hosted stability, not an equivalent rewrite. It adds a drift/repair path, explicit reporting, possible extra reviews/follow-ups and validation. It could unlock useful repeated work that the incumbent currently gates. It does not dominate if stable canonical-review continuity or avoiding temporary incorrect hosted state is prioritized, and it has not yet earned a production recommendation. “Implement a recovery contract” is not a closure until these behaviors, lifecycle consequences and stopping paths are concrete and checked.

Other counted restrictions are unchanged: one-commit linear local authoring; no automatic shared-prefix publication; one authority per conflicting scope; canonical PR continuity by default; human-owned prose; explicit source visibility; fresh continuation acceptance; no blind unknown-write replay; exclusions for unsupported target rules and UI capture. No archive-format migration, new hosting service or lossless multi-commit policy is introduced. The existing importer, owned history surface, exact records, migration and provider support checks remain substantial work under all candidates.

## Remaining falsifiers and adjudication questions

1. Can an accepted continuing-goal validator distinguish parent-only native rewriting from a changed patch without assigning another layer's edit to B? A concrete incorrect acceptance would refute the proposed authorization extension for that domain. Existing net-tree equality cannot answer it.
2. Does the continuing authorization add enough value to justify its stopping, custody and explanation costs? A high-friction user study could favor the one-shot default; no such study is claimed.
3. Can delayed native work change lifecycle or topology after a later client publication in a way that violates a release's required continuity promise? Authoritative completion/arbitration semantics could eliminate this risk; a concrete trace could disqualify the weaker promise for canonical continuity. Current mismatches alone establish neither answer.
4. Does the weaker recovery path retain and clearly expose an accepted submitted patch that later hosted input removes? A default sync that silently accepts the removal falsifies its no-silent-loss claim even if the bytes remain in an obscure archive.
5. Can the full A–B → landed A → retained F–B → later landed F → imported B trace finish with per-layer ownership, canonical B and pending local amendments under the chosen promise? A pilot that only refuses at F–B has not discharged C5.
6. Are all dispatch, direct-worker, recovery and transfer paths subject to current authority and identity/result validation? The exposed local failures show what a bypass looks like. A storage name or self-reported success supplies no evidence of enforcement.
7. A supported hook could provide familiar Git convenience the explicit command lacks; a service could enable collaboration unavailable to a sole checkout; a separate history view could measurably improve comprehension. Any such evidence defeats blanket dominance claims for the narrow defaults without invalidating the shared core.

The coordinator can adopt the accepted-intent clarification independently of choosing a post-native recovery promise. The first is a bounded semantic extension with a preserved one-shot default. The second remains an explicit release tradeoff and a required validation target; it must not be hidden inside that extension or declared resolved merely because C1–C8 do not demand the incumbent's strongest fence.

*Authored by an AI agent acting on joshlf's behalf.*
