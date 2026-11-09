## Proposal

Make GHerrit a commit-oriented client for GitHub's native stacked pull requests. Developers would still author separate changes as ordinary commits on one local branch. GHerrit would publish each logical change to its existing PR, preserve submitted revisions, and help the developer reconcile local edits with changes GitHub makes to the hosted stack.

GitHub would own registered stack membership, stack navigation, evaluation against the trunk, and native landing and cascading rebases. GHerrit would stop maintaining a competing parent/child graph and stop running its legacy merge cascade for native work.

The proposed first client uses explicit commands and direct GitHub APIs. A compatible hook can invoke the same core. Limited membership delegation to the official `gh stack` CLI remains an implementation comparison; the released CLI is not a drop-in full publisher under the archive contract below. Every realization must share the same identity, reconciliation and recovery rules. A publishing service is an option when several clients need to publish the same work; it is not a prerequisite for the first client.

This is a design proposal, not an implemented or production-ready GHerrit protocol. The subsequent [November 8 experiments](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/main/RESULTS.md) exercised actual native methods, structural edits, initial CI, reviews, signatures, history and local reconciliation. One connected hosted prototype completed A–B → landed A → F–B → landed F → imported B again, preserving B's canonical review. The complete production workflow still depends on an unresolved question: what evidence permits GHerrit to write branches that GitHub may still be rewriting? Real post-merge reads disagreed across PR heads and Git refs; later convergence did not prove settlement. The sections below distinguish bounded evidence from the proposed behavior.

The original experiments and the November 8–9 follow-up establish actual native and queue capability, including partial outcomes. The follow-up extends the earlier build-one queue evidence with a different SQUASH outcome at build concurrency two, verifies four website rebases, exercises genuine missing acknowledgements, and exposes recovery-prototype failures. CI scheduling, approval retention, signing and completed-group continuation still depend on the tested path and policy. The [findings below](#what-the-experiments-establish-and-what-may-change) separate documented foundations from conflicting promises and observed details. None of those observations supplies a general provider handoff.

## Goals and scope

The design should preserve GHerrit's useful authoring model:

- One local branch holds a sequence of separately reviewable changes.
- A logical change keeps its review identity through amendment and rebasing.
- Existing PR discussions and exact submitted revisions remain available.
- Local edits and unmentioned hosted work remain recoverable when an operation fails, is interrupted or has an unknown outcome.
- Ordinary unmanaged Git use remains ordinary Git use.

The first version would support a validated linear sequence with one authored commit per change. The backend must nevertheless describe revisions with explicit base and tip commits: a native PR may contain several commits, and GitHub may rewrite its commits. Multiple commits per local change, merge histories, cross-fork workflows, shared-prefix publication and groups beyond GitHub's size limit need separate policies. They are not implied by adopting native membership.

Convenience still matters. Explicit preparation, continuation branches and a single publishing checkout add work for the author. They must earn that cost through clear previews, reliable recovery and a usable repeated workflow. A client that can only refuse indefinitely is not a complete replacement.

## Where we are starting

The code at [main commit `7ba3451`](https://github.com/joshlf/gherrit/tree/7ba3451cc279122ea1fefed431f875916e3d1ebd) still publishes a predecessor chain through a pre-push hook. It allocates archive versions from local tags, finds PRs by head branch, updates whole PR descriptions, and ships an independent merge-cascade Action. It has no public native-stack sync command or durable record binding a logical change to one canonical PR.

The recent cleanup work improves boundaries and validation; it does not implement the native reconciliation model described here. Earlier proposals for owned comparison bases, canonical markers or staged reconciliation must not be mistaken for guarantees already present in main.

## What GitHub supplies

The trunk is the branch the stack ultimately aims to land in; it need not be the repository default branch. The following describes the public surface inspected on November 8, 2026:

| Capability | Consequence for GHerrit |
| --- | --- |
| A stack is an explicit ordered chain in one repository. Each next PR bases on the preceding PR's head branch; the trunk may be any branch. | Branch ancestry and adjacent PR bases do not, by themselves, establish native membership. |
| A new group requires 2–100 PRs. A PR cannot belong to two groups. | A single change starts as an ordinary PR under native intent. Shared-prefix forks and oversized groups need an explicit policy. |
| Public membership writes create, append at the top, and unstack eligible members. | Insert, reorder, selected removal and deliberate trunk changes need a rebuild policy. There is no general membership replacement or compare-and-swap API. |
| Unstack preserves PR objects and bases; locked or merged members can remain in the old group. | Reuse PR identities, inspect the actual residual group, and allow the grouping number to change. |
| Direct native landing merges the open prefix through the selected PR and rewrites the remaining suffix. Queue admission separately enqueues the prefix; members may later be ejected. | GHerrit must import actual hosted outcomes, report partial queue results and preserve local amendments before publishing again. |
| Async REST is required for programmatic native-stack merges. | Request acceptance, queue admission, landing and usable suffix state are distinct. |
| Rules and checks are evaluated against the trunk. | Enrollment changes the rule context and requires a deliberate CI transition. |

See the [stack reference](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests), [REST API](https://docs.github.com/en/rest/pulls/stacks), [API and webhook overview](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests-apis-and-webhooks), and [merging guide](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests).

The official CLI's [v0.3.0 release](https://github.com/github/gh-stack/releases/tag/v0.3.0) makes branch pushes atomic by default. Its [command reference](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands) expressly limits that atomicity to Git refs: PR creation, base changes and stack registration remain separate operations. The [`pull.stacked` push option](https://github.com/github/gh-stack/pull/562) signals an unchanged force-push rebase for approval retention; it does not describe membership or create a transaction.

The [managing guide](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests), [troubleshooting guide](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-stacked-pull-requests), [stack reference](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests) and [CLI FAQ](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/docs/src/content/docs/faq.md) contain differing statements about queue failure, signatures and auto-merge rollout. This proposal does not rely on auto-merge being universally available or on a successful merge result proving that every later suffix effect has finished. Target-host capability and observed final state still matter.

## Ownership and the first collaboration model

Enrollment records which repository, reviews and publication protocol a checkout is allowed to manage. Use one enrolled publishing checkout for an affected chain, including its linked worktrees. Here, the affected chain means every canonical PR whose head, base, membership or landing can be changed by the operation, including any hosted suffix omitted from the local branch.

For that chain, publication, topology edits, queue changes and native landing/rebase must be serialized operationally. Other people can review and edit human-owned text. Ordinary trunk progress and unrelated chains are not globally frozen; GHerrit must detect changed bases and reconcile them.

This is a collaboration restriction, not a global lock. Cooperating processes in that checkout need one actual local owner across admission and dispatch. Each process must reload the current operation under that owner before sending an effect; cached admission and a lock-shaped record are insufficient. The same boundary must apply to direct worker, recovery and transfer entry paths. It cannot fence another clone, an administrator or delayed GitHub work. The design does not claim safety under arbitrary simultaneous structural writers. Whether this initial restriction is useful enough, or whether a service is needed early, remains an open product choice.

The responsibilities are:

| Owner | Responsibility |
| --- | --- |
| Author | Choose the logical changes and intended local edits; resolve conflicts; choose private/public publication and review readiness. |
| GHerrit | Capture intent, bind changes to reviews, preserve submissions, reconcile hosted outcomes, and record partial or unknown effects. |
| GitHub | Maintain native membership/navigation, apply trunk rules, and perform native landing/rebases. |
| PR participants | Own title, body and readiness after initial creation, subject to the separately chosen history presentation. |

Scope includes all relevant Git refs, PRs, membership, public source targets and local checkpoints, plus managed trunk dependencies and indirect lifecycle/base effects. A different grouping number or a fresh branch name alone does not prove that two operations are independent. Missing intent or an unknown possible write scope cannot be classified as harmless. This can reuse the captured bindings and effect targets; it does not require a general concurrent scheduler.

The legacy cascade must be excluded for an enrolled native chain before native landing is enabled. A mode flag alone does not revoke a request the old writer already dispatched.

## Identity and retained evidence

A change ID identifies a logical change. It does not grant permission to overwrite a remote branch. A commit ID identifies an exact revision, including its message and ancestry. A PR number/node ID identifies the review. A native stack number locates a grouping that may change after a rebuild.

The canonical PR is the one review GHerrit continues to update for a logical change. GHerrit must explicitly bind the repository, change ID, managed head and canonical PR. New heads are allocated in an enrolled namespace after absence and prefix-conflict checks. Existing heads and PRs require explicit adoption. The actual Git destination and API repository must agree; ambiguous multiple destinations or rewritten transports require a verified mapping before publication. A fresh SHA lease proves neither ownership nor incorporation of the work it names.

Keep four kinds of evidence. They can share a storage representation; they need not become four independent databases:

1. The captured authored input: exact source tip, ordered changes, messages and base/tip boundaries.
2. Canonical review bindings and exact submission history.
3. Current hosted observations: membership, trunk, PR lifecycle, heads/bases, branch refs and queue state.
4. A durable operation record: captured checkpoint, intended effects, dispatch state, receipts and unresolved outcomes.

Pin recoverable local inputs before remote effects. Status, preview and execution should use one evaluator and the same admission rules. A preview does not keep external facts true; execution must still apply each effect's guards.

A checkpoint records the hosted ranges actually incorporated and the exact local result accepted from them. Fetching a revision alone does not advance it. A backup or publisher transfer must retain accepted checkpoints and relevant pending operations as well as canonical bindings. Stopping the old process prevents new dispatch but does not settle an earlier request. Importing a binding file alone cannot make a replacement checkout ready to write. If pending evidence is missing or names a different operation, enter recovery and withhold new mutation authority. Do not reconstruct fresh intent from command arguments. Recovery and transfer must also validate the accepted result claimed by a completed record: its retained objects, continuation and checkpoint, or a validated successor attachment. A completion flag alone grants no authority. Retain the historical accepted result independently of the mutable authoring tip. Ordinary amend/rebase need not journal each Git edit: the next preparation or recovery captures the new tip and obtains mapping/difference acceptance before recording its attachment and allowing effects.

### Review lifecycle

Status distinguishes open, closed-unmerged, merged and unknown PRs. Normal submission stops on a closed-unmerged canonical PR and preserves the binding and local work. Resuming requires an explicit request to reopen that same PR, where permitted, or an explicit withdrawal/new-change decision retaining the old history. Reopening is itself a recorded API effect whose outcome can be unknown.

A merged change is terminal. A later amendment becomes an explicit new-ID follow-up. Unknown lifecycle grants no permission to reopen, replace or publish. Missing local bindings require recovery/adoption rather than automatic replacement PR creation.

### Submission history and reviewer access

Retain existing `gherrit/<id>/vN` refs and their exact targets. Initially use that same reviewer-facing format for new authored submissions, with version allocation based on remote history and the owned local record rather than local tags alone. Never retarget an older archive. Repeated A/B/A submissions are separate historical positions; an unchanged submission is a no-op.

Preserve exact historical base/tip boundaries. A comparison against today's mutable parent branch does not describe the historical patch. Native rewrites are recorded/imported as hosted outcomes; they do not silently become new authored submissions. An offline client cannot promise to capture every transient remote revision. The generated history surface projects confirmed authored submissions. It is not a range-integration input, a substitute for archive objects, or evidence that native work has settled. Comment delivery and recovery retain their own effect records and cannot manufacture publication confirmation.

Seed the PR's title and body from the authored text, then leave them human-owned by default. Use native navigation rather than rewriting a second parent/child graph. This deliberately gives up today's automatic whole-description projection.

The replacement must still give reviewers a stable way to find exact old submissions and compare them. Archive reachability and native navigation do not supply that interface. Give generated history an explicitly owned artifact separate from the human prose. The tested prototype uses one GHerrit-owned history comment bound to the canonical PR. A production implementation must apply the same durable effect rules to its creation and updates as to other API writes. This avoids a new hosting service and avoids reading an old body, racing a human edit, then overwriting the person's prose with a machine-updated section.

That prototype is not yet a complete reviewer interface. Identity binding, ordinary updates, explicit reattachment after deletion, exact historical ranges and bounded size handling were tested. Overlapping same-account body/comment PATCHes preserved both; a stale whole-body control overwrote newer synthetic prose. Pinning the PR comment was rejected despite a positive permission boolean. Follow-up tests establish actual distinct-actor permissions, programmed interleaving and duplicate-marker conflict handling. A privileged bot could edit a user-authored comment, so visible authorship is not exclusive edit authority. Genuine no-HTTP-read comment creation also produced its exact fresh comment. These observations do not provide general deduplication, ownership from a marker, or safe unknown-create replay. An informed browser agent reached the exact old patch and the labeled tip comparison; discovery in a long discussion and human comprehension remain untested. A dedicated view may earn its hosting/maintenance cost. A body section remains an alternative only with a tested update/ownership protocol that preserves concurrent human edits. A link stored only in an editable body is insufficient.

The history surface must distinguish each exact authored patch (its historical base-to-tip range) from a comparison between versions. When the parents differ, a raw tip-to-tip comparison can show unrelated trunk changes. Show what a comparison means and how to reach both exact patches. An ancestry-independent “changes since review” view would require additional range-to-range comparison validation; it is not supplied merely by stable links.

## Preparing and publishing work

Command names below are illustrative. Preparation is a semantic step, not necessarily a separate command or mandatory extra invocation. A submission command can capture, preview and accept the plan in one interaction.

For an existing workspace, preparation selects its retained accepted local ranges and incorporated hosted ranges, maps current authored ranges to canonical changes, and shows the change-local differences. The author accepts that mapping and those differences as current intent before effects. An unchanged captured mapping can reuse its acceptance; a moving branch name cannot change the accepted input.

This rule supports ordinary amend/rebase even when every commit ID changes. It also handles a deliberate revert or reset: show the differences from the retained checkpoint as proposed local edits and require explicit acceptance. Do not pretend Git history proves how the rewrite happened. Another branch with the same IDs needs explicit checkpoint attachment and mapping review, or a fresh import/adoption. Unknown or ambiguous mappings stop before remote effects and retain their inputs.

Order changes, omission, folding and new changes enter their corresponding structural/append path. The first client rejects unresolved merge/side-history inputs before mutation and offers a deliberate linearization route with original objects retained. Duplicate IDs are not silently interpreted as multi-commit grouping.

### First publication, append and amendment

The normal publication sequence is:

1. Capture accepted committed intent and pin its objects. Resolve the entire affected hosted chain, canonical bindings and incorporated baselines. Local A cannot amend hosted A–B–C while ignoring B/C.
2. Check names, ownership, object availability, arguments, request sizes and known host limits. Inaccessible data does not authorize deleting or replacing a suffix.
3. Push coupled changed heads, new authored archives and any intentionally public source ref in one atomic Git transaction with explicit leases. Reject an oversized coupled transaction rather than split it at today's 80-target boundary or retry non-atomically. Unchanged refs are not effective guards if Git omits them before lease enforcement.
4. Create missing PRs once and durably bind returned identities. A singleton remains an ordinary PR under native intent. At two members, register the exact ordered PRs; append only a new suffix to a compatible active group. Missing membership never silently selects legacy publication.
5. Re-read actual heads, bases and membership, and report Git, PR and registration progress separately. Use fresh-group continuation after completion unless GitHub clarifies support for reopening: an observed fully merged group accepted append and landed new work, but the current merging guide still prohibits extension. A separate eligible-suffix release and regrouping also succeeded. Choose the supported path explicitly, retaining old reviews/history and inspecting actual membership; neither trial supplies a future API guarantee.
6. Once the captured submission is fully confirmed, advance the checkpoint for exactly those captured ranges. Any later local edits stay pending.

Partial progress is durable. A Git push can succeed before a PR or registration operation fails. A later invocation resumes/reconciles that operation before another mutation of possibly affected resources; it does not call the entire attempt unsuccessful and blindly replay everything.

### Outcomes and recovery

Distinguish known-not-sent, definitely rejected, acknowledged and indeterminate effects. A received response is evidence of what it actually establishes: a timeout or server-error response may coexist with a completed mutation. Direct native group creations returned HTTP 504 and 502 while producing the intended 99- and 100-member groups. Preserve those writes as unknown until justified reconciliation; do not classify every error status as a no-effect rejection. Record dispatch intent before mutation. Losing a create, append, unstack or base-edit response does not prove the server did nothing and does not authorize a resend.

Within the declared sole-writer domain, a uniquely attributable positive transition may resolve an operation. Mere absence, elapsed time, or a desired state another actor could have produced cannot prove an older write is settled. Unknown effects block overlapping work until provider/operator evidence resolves them or an explicitly supported recovery contract applies. Keep the unresolved record even when demonstrably disjoint work can proceed. That availability and scope-accounting cost is part of the design.

A response establishes only the result it describes. HTTP 202 confirms background acceptance; terminal `enqueued` completes admission only. Current queue entries, PR lifecycle, rewritten ranges and remaining possible native effects are separate facts. A rejected removal does not settle the admission it attempted to interrupt.

The local lock and journal make client intent durable; they do not provide cross-resource atomicity, global exclusion or server idempotency. Local types should make confirmed and unknown outcomes hard to confuse, but cannot keep an external observation true.

## Landing and local reconciliation

Use GitHub’s native UI or async REST to land the selected open prefix. For GHerrit-issued REST requests, record intent before dispatch and retain the returned UUID/options; a REST conflict may identify a different pending intent. Do not assume a native-UI operation exposes an equivalent receipt. A cooperating UI operation needs recorded intent and affected scope; if that evidence was not captured or is unavailable, treat it as external activity with missing/unknown evidence. Preserve inputs and block possibly overlapping writes until recovery establishes the supported handoff. The concrete UI capture/recovery path remains an implementation acceptance gate. A selected-head SHA is not an all-member snapshot; queue admission, actual landing and usable suffix state remain distinct. Expiry of an API result does not prove completion; observe actual state after failure or uncertainty.

Hosted changes enter the same exact-range reconciliation path once their canonical mapping and usable ranges are established, whether they follow direct landing, queue activity, a website rebase or other hosted edits. Each interface retains the intent, receipt and unknown-effect evidence it actually supplies. Incorporating a range records what local work includes; it does not settle an outstanding request or grant permission for an overlapping hosted write.

### Observed queue behavior

The [queue experiment report](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/main/RESULTS.md) now supplies bounded evidence. A terminal async `enqueued` receipt remained unchanged after actual merges, ejections and dequeues; actual membership, lifecycle and refs must be read separately. Empty queues included cases where only the lower member landed. A queued branch update was rejected with GH006, including its coupled archive update in the atomic push. This is an observed queued-state restriction, not a universal fence against future native writes.

Queued unstack retained queued A/B while releasing unqueued C. After confirmed ABC admission, upper-C and middle-B API removal failed a direct-base queue lookup; lower-A removal removed dependents. Failed removal immediately after 202 did not cancel its pending admission. The inspected async API has no dedicated cancellation endpoint. The signed-in website contrast also returned visible “Not Found” errors for C and B. Independent reads after each action retained ABC; one lower-A cleanup then removed all three, with unchanged source/trunk/archives. No initiating website HTTP status or operation UUID was captured, so the UI error supplies no internal routing diagnosis.

Across the tested method/strategy/build-concurrency grid, MERGE landed both members. SQUASH ejected the upper at build concurrency one but landed both at two. REBASE ejected the upper; only its lower build ran even when two were configured. One trace per cell does not establish reliability or a permanent workaround. A separately explicit request at an observed replacement head landed a previously ejected canonical upper; that supplies no silent retry or automatic re-admission policy.

If A lands and B is rewritten and removed, report each actual outcome and import B through the ordinary importer. Any later admission is a distinct intent with its own handoff/readiness gates. Import or admission alone creates no authored archive when no authored edit/publication is needed. Keep the original admission receipt.

### The revisions sync must distinguish

For each open logical change, keep these roles separate:

| Name | Meaning |
| --- | --- |
| Last authored submission | The exact revision last submitted and archived by GHerrit. |
| Incorporated hosted revision | The hosted range actually used as an integration input or confirmed export basis. |
| Accepted local result | The exact local range accepted after integration; it may contain unpublished edits. |
| Current local range | The committed range captured from the source for evaluation. Preparation accepts its mapping and differences as publication intent; reading it does not accept it. Later source movement is separate pending work. |
| Newly observed hosted range | What GitHub currently reports and the corresponding fetched branch objects. Observation alone does not incorporate it. |

These roles sometimes coincide, but cannot always be replaced by one “current version.” For example, a native rebase may change the hosted revision while the last authored archive remains unchanged, and the accepted local result may also contain an unpublished amendment.

### Proposed integration algorithm

Fetch and preserve the old submitted, current local and current hosted ranges on scratch refs. Identify landed changes through canonical PR lifecycle rather than ancestry, which can change under squash/rebase. Disagreement between PR heads, branch refs or direct bases leaves a partial import, not an advanced checkpoint.

For each open change:

1. Use the last incorporated hosted range as the merge baseline, the current local range as the local input, and the new hosted range as the hosted input.
2. Normalize the old and local change ranges onto the hosted comparison parent, then three-way integrate their change-local trees.
3. Replay that result onto the preceding output layer so that an upstream local amendment stays in its own change.
4. Make conflicts, messages and signing explicit author decisions. Preserve every input.

The real-Git prototype exercised this algorithm through repeated import, ordinary Git rewrites, retained local amendments and conflicts, with 122 baseline assertions and broader follow-up checks across changing parents, modes, renames, deletion and binary content. Multi-commit tests preserve a flattened net range and its tip message, not every intermediate commit or message. A connected hosted fixture then imported actual native outcomes twice and preserved canonical B through the required F-before-B publication. Per-layer diffs, executable dependency controls and a subsequent lower-only amendment were checked; final cumulative tree equality alone would have missed wrong ownership. These fixtures support the direction, not equivalence for every Git history or production implementation correctness.

Accepting a sync records the newly imported hosted range as the incorporated baseline, and separately records the resulting local range. Do not use the resulting local range as the hosted baseline: it may contain a still-pending local edit. The last authored submission remains unchanged until a real submission.

For example, import hosted `x=1` while retaining unpublished `y=1`, then import hosted `x=2`. The second merge uses the incorporated `x=1` baseline and keeps `y=1`. Returning to the older submitted `x=0` baseline can manufacture a conflict or preserve an obsolete value.

A fully confirmed submission advances both the authored submission and the incorporated basis to the exact captured exported ranges. If the live branch gained another edit during publication, that later edit remains pending relative to the captured export. Do not mark the whole live branch submitted. Partial or indeterminate publication does not install a completed checkpoint. A meanwhile native rewrite requires import rather than an assertion that the captured export is still the hosted head.

If a native import left local ranges equal to confirmed hosted ranges and no ref/topology effect is needed, submission is a no-op with no new authored archive, even if an older authored archive has different ancestry. Observation alone neither creates a submission nor consumes pending local work.

Edits to an already landed change become a proposed new-ID follow-up or a retained conflict; they do not resurrect its review. This can require structural insertion on the ordinary one-commit path. Suppose hosted A–B is published, local A′ adds a field and local B′ uses it, then old A lands. The retained continuation is a new-ID follow-up F before B′, preserving B's canonical PR. Appending F above B would change the dependency. Publishing F–B together therefore needs regrouping, or an explicit author-approved staging decision that delays/rearranges publication while preserving the work.

This is the same ordered-review reconciliation used for deliberate insertion; it is not a separate sync-only topology mechanism. The full repeated-workflow milestone must include this case. A pilot with append only can cover a narrower workload, but cannot claim complete landed-amendment recovery.

### Accepting a local result

Sync operates on captured committed objects in scratch storage. It does not reset the caller's source ref, index or working tree. Make clear that dirty, staged and untracked changes are excluded from the committed snapshot and leave them in place; do not automatically stash them.

Accept the result by creating a new continuation ref with an absence expectation and installing an atomic checkpoint record naming that ref, its exact result and its per-change incorporated ranges. Journal this intent first. A crash between ref creation and checkpoint installation resumes from the record and actual ref; it must not advance the old branch's checkpoint.

If source T advances to U while sync runs, retain U and the continuation R. Report that R reflects captured T and offer another sync from U. Selecting R for further authoring is explicit and uses ordinary Git worktree protections. A dirty edit can block that switch; the UI must explain how to retain the old workspace, deliberately carry the edit, or commit it and prepare another input.

In-place acceptance into the caller's checked-out branch is outside the first version. A branch lease alone would not protect concurrent file or index edits. The fresh-continuation policy costs selection and preparation steps; its benefit is a precise capture/recovery boundary without silently displacing ongoing authoring.

### The unresolved provider handoff

Before mutating resources that a pending native operation may still change, GHerrit needs a supported handoff or an explicitly supported recovery contract. A terminal merge UUID, matching current reads, or a successful finite experiment does not prove that no delayed suffix rewrite remains. In particular, republishing or rebuilding a surviving suffix overlaps the possible native effects and retains this gate.

The gate need not freeze every later operation. If A/B have actually landed and later C has a new ID, fresh managed head, new PR and an independent checkpoint/public target, old effects limited to A/B's resources do not have to be proved finished before publishing C. This requires an evidence-backed effect scope, including indirect effects and shared targets; a new group number alone is no proof. Uncertain actual landing, missing operation evidence, shared refs/checkpoints or a managed-head trunk retain the gate. Ordinary trunk progress remains an input to reconcile. Disjoint work does not settle or clear the old operation.

There are two possible directions. Authoritative provider semantics could establish when further writes are safe. Alternatively, we could explicitly choose a weaker contract that retains inputs and detects/recovers from later conflicting writes. The latter needs its own precise limits and user experience; it is not established by this document.

Until one direction is supported, a pilot stops at the overlapping boundary and cannot be described as a complete replacement. A service or CLI adapter inherits this question. Observation and local staging that do not overwrite protected checkpoints can continue without claiming hosted settlement.

## Structural changes and other histories

Reorder, insertion, dropping, folding and trunk changes are explicit whole-chain operations. Require a cooperative maintenance interval, no known queued/pending work, and resolved earlier effects.

The proposed sequence follows the official CLI's [submit implementation](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/cmd/submit.go):

1. Unstack once and observe which active members were actually released. Historical or locked members may remain in the old group.
2. Temporarily park affected open PR bases at the trunk before moving their heads. Confirm each parking effect or retain an unresolved barrier.
3. Atomically move coupled heads and archives.
4. Establish the final adjacent bases, then register the surviving order.

Reuse canonical PRs; a new native grouping number is normal. Dropping or folding explicitly selects which review is withdrawn and which continues. Retain old heads, archives and discussions. Omission from local history alone does not close a review.

Nine follow-up fixtures resumed this sequence after actual SIGKILL and fresh-process recovery at acknowledged durable prefixes, including inserted-PR creation and completed registration. They preserved canonical PRs and exact archives without repeating completed effects. Missing-receipt and stale-head controls refused. These are after-ack recoveries; separate transport experiments cover genuinely unacknowledged writes. The sequence remains client evidence, not a server transaction or proof that every lifecycle race is safe. Keep the structural executor disabled until its provider lifecycle, approval and completion behavior is supported. A successful finite trial establishes its observed trace, not the absence of later writes.

For local A–B and A–C, one canonical A cannot belong to both native groups. The first version keeps the second fork local until A lands, or requires an explicit copy/new-review decision. Do not silently invent A–B–C dependence. Using A's managed head as another stack's trunk changes the problem: landing into it changes A's authored head and requires a cross-chain authority protocol.

For more than 100 members, use a deliberate staged-publication policy or refuse that operation with retained work. Splitting groups does not preserve one atomic landing. Adopting/importing a multi-commit layer likewise needs a defined local mapping: retain its range or stage a reviewed one-commit representation with originals preserved. No automatic squash or attribution change is assumed. Editing unsupported input stops before effects.

## User interface and open tradeoffs

The proposed default is an explicit local client with preparation, submission, status, sync, structural editing and optional landing operations. Exact command names and whether preparation is a separate invocation are UI choices. Unmanaged Git is unaffected. Private submission omits the author's workspace branch name; public submission includes it deliberately in the coupled Git push. “Private” does not mean draft or access-private review. The explicit path needs no loopback upstream configuration.

Canonical review continuity and human-owned prose are selected defaults in this proposal. Creating new immutable PR generations remains a product-policy alternative when replacing reviews and fragmenting discussion are worth the avoided in-place edits; it is not a per-submission implementation switch. Likewise, restoring automatic whole-body ownership would reopen the prose policy. The appendix explains why those are not the defaults.

The current CLI also has a concrete capability boundary. Its inspected [push implementation](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/internal/git/gitops.go#L258) constructs explicit branch refspecs and cannot include GHerrit's archive-ref vector in that transaction. Its [submit command](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/cmd/submit.go#L24) has no skip-push path. Pre-pushing with GHerrit and then calling submit adds another head publisher with its own fetched expectations. Broad delegation needs an integration that meets the contract, an upstream extension, or an explicitly reconsidered publication/archive protocol; it is not an interchangeable wrapper today.

A narrower [link path](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/cmd/link.go#L443) skips branch pushing for recognized PR URLs. A controlled adapter can therefore be investigated using canonical PR URLs, with exact effects and recovery verified. Bare numeric identifiers can collide with local branch names and are not the same inspected boundary. The released v0.3.0 adapter was dynamically tested: recognized URLs with correct bases and no `--open` preserved the tested refs, prose and readiness. A separate URL trial repaired a wrong base, and `--open` made drafts ready before a later order refusal. URLs therefore avoid the tested branch push but do not guarantee membership-only effects. Broad submit published branch refs atomically and omitted the archive tag, confirming the publication boundary above.

The remaining realization and extension choices are:

| Choice | Proposed starting point | What could change the choice |
| --- | --- | --- |
| Explicit commands or a compatible hook | Start with explicit effects and one evaluator. | A thin hook preserves familiar push if its destination, dry-run, drift and outer-push contract is acceptable. It must not promise ordinary `git push --dry-run` behavior without receiving that intent reliably. |
| Membership API implementation | Start with direct typed calls. | A constrained PR-URL membership adapter may earn its encoding/maintenance cost after verification. Count version coupling and unknown-outcome recovery; the broader integration described above requires additional work. |
| One publishing checkout or a service | Start with one cooperating publisher per affected chain. | Multiple clients/automation may justify a service that genuinely controls writes and preserves pending operations. Hosting, credentials, outages and recovery are additional work. A timeout lease or required check is not a universal fence. |
| History presentation | Continue the tested separately owned history comment; keep human prose human-owned. | Identity, updates, exact ranges, bounded size handling, distinct-actor permissions and programmed body/comment concurrency have evidence. An informed browser walkthrough verified the rendered links. Human discovery/comprehension and production unknown-write recovery still need validation; comment author identity does not enforce exclusive editing. A dedicated view or safely coordinated body section may earn its extra cost. |
| Richer authoring | Keep the one-commit linear path simple. | Multi-commit groups, shared prefixes and richer graphs should be added only with explicit mapping and lifecycle policies that justify their total cost. |

Provider completion is an evidence gate, not another backend setting. Choosing weaker detection/recovery would change promised outcomes and needs a separate explicit contract; this proposal has not made that choice.

Some choices concern the same core at different boundaries. A hook changes invocation; a service changes publication authority; CLI delegation changes implementation ownership. They should not produce independent, subtly different reconciliation engines.

## CI, migration and validation

Before enrollment, establish an eligible required-check path for every layer's first publication and adoption, plus `merge_group` coverage. Follow-up fixtures supplied real push-event checks and a positive stacked target-workflow route after installing its required default-branch definition. Check context, SHA and producer identity all mattered. Actual CodeQL needed a fresh analysis after a native rewrite; deployment success on either tested source or candidate behaved differently from ordinary status-context precedence. Validate each actual rule path rather than deriving readiness from one generic green flag. Upper PRs can open before native metadata exists. Explicit `types: [opened, synchronize, reopened, stacked]` with a trunk filter supplied first CI in our fixture; excluding `stacked` did not. The [pinned webhook reference](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/docs/src/content/docs/reference/webhooks.md) documents stacked membership events; the inspected Actions/stack-CI guides did not explicitly promise that activity as an Actions trigger. The successful trigger remains observed, while real push checks provide a separately tested route. A manual dispatch did not repair the required gate. Begin without position-based optimizations and verify event, source, candidate and check SHA identities on each target. The public organization supplied actual queue CI with method-dependent graphs; the earlier user-owned repo could not enable a queue. Availability remains target-specific and is not required for all native use. Do not use close/reopen as generic CI repair. See the [CI guide](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/optimizing-ci-for-stacked-pull-requests) and [Actions reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request).

Prefer new native work after current legacy reviews finish. Existing chains require explicit destination, binding and history adoption, plus exclusion of old publisher/cascade effects. Scope that exclusion to the enrolled work; unrelated legacy work need not be disabled globally.

Rollback is an export/handoff after pending effects resolve, not automatic fallback to legacy publication. Unstack only releases eligible members. Retain PRs, archives, checkpoints and observed native outcomes. Re-enabling the old publisher/cascade requires deliberate translation and exclusion of native writers. Rollback does not promise to restore old remote SHAs or grouping identity.

Before recommending production use, require:

- Real Git fixtures for repeated import, ordinary amend/rebase/revert/reset, native squash/rebase landing, per-layer attribution, messages/signing and retained local amendments.
- Identity/destination/namespace admission and archive tests, including A/B/A history and unchanged imported work.
- Interruption tests at every durable effect prefix, including ref/checkpoint gaps, lost responses and transfer of an unresolved operation to another publisher.
- Author walkthroughs with dirty/staged/untracked work and blocked continuation selection, and reviewer walkthroughs finding the owned history comment, understanding comparisons with changed parents, and reaching exact old patches after human text edits.
- Authorized provider tests for first CI scheduling, same-order atomic amendment, structural parking, partially merged/queued unstack, complete-group continuation, scope-disjoint admission and prefix landing that requires a follow-up below a surviving canonical PR.

Provider tests should retain exact refs/trees, PR identities and bases, membership, queue/rule state, sanitized responses and timing. Mocks can test client policy and fault handling; they cannot supply a missing hosting guarantee. The original [experiment report](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/ade319107e71b6eff646a1574139e2c15486fe6d/RESULTS.md) and subsequent campaigns supply bounded evidence, not production acceptance. The follow-up adds real transport loss, natural server errors with effects, broader queue/rule/review/signature controls, four user-operated website rebases and nine hosted after-ack structural restarts. It also exposes local completion, missing-evidence, stale-worker and operation-identity failures. The eventual executor must close those failures at the dispatch boundary and validate its accepted outputs. SIGKILL tests leave filesystem caches alive and do not establish machine-power-loss durability. Human walkthroughs, production mapping/recovery and provider settlement remain separate obligations. The authenticated queue UI contrast now has observed error and cleanup evidence, not a cancellation or handoff guarantee. Production GHerrit was not changed.

A useful implementation sequence is to establish identity/capture and read-only status, validate local import on real Git fixtures, then add journaled first publication/append/amendment. Observation and scratch integration can proceed while preserving inputs and unresolved records; inconsistent ranges cannot advance an accepted checkpoint. Enable landing, overlapping republication, structural mutation and protected-checkpoint replacement only when their corresponding authority, handoff and lifecycle requirements are supported. Recovery of a landed amendment below a surviving review can require both, so the full repeat-workflow milestone cannot postpone all insertion support as an advanced extension. A narrowed experiment must remain labelled as such.

Related discussions include [overwrite authority and leases](https://github.com/joshlf/gherrit/issues/139), [concurrency and partial publication](https://github.com/joshlf/gherrit/issues/264), and [stack merge queues](https://github.com/joshlf/gherrit/issues/281). Those discussions supply problem history, not evidence that their proposed fixes are implemented or that old platform restrictions still apply.

## What the experiments establish, and what may change

The documentary foundation was checked on November 8, 2026; the follow-up observations run into November 9. Original sources remain in the [personal campaign](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/ade319107e71b6eff646a1574139e2c15486fe6d/RESULTS.md) and [first queue campaign](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/7ad9f79d1ec562146c685170135454ed84ff240f/RESULTS.md). The [follow-up evidence snapshot](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/tree/97b993efdda40a1cbe690d317e436e32937adb85/followup-2026-11-08) retains reports, source, verified lossless archives, case dispositions and independent audits. Its five indexes contain 130 IDs, including reused evidence, negative controls, an unavailable premise and a replaced failed premise. This is not 130 fresh successes or a production acceptance score. Failures and report/harness corrections remain retained.
Use four evidence categories: an explicit documented contract; published intent with conflicting documentation or observations; an observed implementation detail; and a mechanism whose correctness belongs to GHerrit. A passing experiment does not move a behavior into the first category. Documentation is the strongest practical integration basis, but does not rule out service defects.

### Documented foundations

| Finding | Contract and consequence |
| --- | --- |
| Native topology and trunk policy | Native groups are same-repository ordered chains with adjacent bases; policy is evaluated against the ultimate trunk, which need not be the default branch. New groups contain 2–100 PRs, and a PR belongs to at most one group. Membership is distinct from ancestry and from merge readiness. [Stack reference](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests), [stack API](https://docs.github.com/en/rest/pulls/stacks). |
| Async acceptance, admission and landing differ | HTTP 202 accepts background work after basic state checks; rule evaluation follows. `pending`, `merged`, `enqueued` and `failed` have distinct meanings. `enqueued` is final for admission and does not later change when the queue lands or removes the PR. UUID results expire 24 hours after their latest update; expiry is not cancellation. A selected-head expectation is not an all-prefix snapshot or an indefinite freeze. A 409 can identify an existing, different intent, whose options must be compared. [Async API](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously). |
| Unstack is partial and preserves PR objects | Eligible members are released while merged/queued members can remain: the API distinguishes residual membership, dissolution and an all-locked refusal. PR objects and their current bases survive. This does not promise approval retention, remove queue entries or cancel pending requests. [Unstack API](https://docs.github.com/en/rest/pulls/stacks#remove-pull-requests-from-a-pull-request-stack). |
| Removing lower queued work removes its dependents | The native queue guide explicitly describes removal of members above a removed/ejected PR. Our lower-dequeue control matched it. The dequeue mutation takes the PR node ID, not the async request UUID or queue-entry ID. It is not a documented cancellation protocol for pending admission. [Queue guide](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests#merging-using-a-merge-queue), [dequeue mutation](https://docs.github.com/en/graphql/reference/pulls#dequeuepullrequest). |
| Queue CI checks a generated candidate | `merge_group: checks_requested` supplies the candidate SHA/ref. Green source-head CI cannot replace checks on that candidate. Exact parent count, group scheduling delay and candidate graph shape are not the general contract. [Actions reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#merge_group). |
| Manual dispatch does not repair the required PR gate | GitHub now explicitly documents that workflow-job checks from `workflow_dispatch` do not appear as eligible PR checks or satisfy required ruleset checks. Our successful dispatch with a still-blocked PR matched this boundary. The restriction is about workflow jobs; it is not a claim that every external App check producer is ineligible. [Required-check limitations](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks#checks-from-some-workflow-jobs-are-not-evaluated). |
| Conversation comments support CRUD, with bounded history | PR conversation comments use the issue-comment API and stable IDs; line-review comments are separate. Pinning PR comments is explicitly unsupported, even when a generic permission field is true. Native edit history retains the original plus the latest 99 versions, and revision contents can be deleted. It is not an unbounded submitted-revision archive. [Comment API](https://docs.github.com/en/rest/issues/comments), [pin restriction](https://docs.github.com/en/graphql/reference/issues#pinissuecommentinput), [history limits](https://docs.github.com/en/communities/moderating-comments-and-conversations/tracking-changes-in-a-comment#editing-history-limits). |
| Indirect merges explain the reordering hazard | GitHub can mark a PR merged when its commits become reachable from its base through another PR or a direct push, even if that PR's own protections were not met. Our unsafe reorder reproduced an unreopenable merged review. This is a documented lifecycle hazard, not merely an unexplained transient closure. [Indirect merges](https://docs.github.com/en/pull-requests/reference/pull-request-merges#indirect-merges). |
| Atomic refs and explicit leases have limited scope | Git promises all transmitted ref updates or none for `--atomic`, and explicit leases compare expected values for refs actually updated. Equal refs may be omitted; this is not a full-vector snapshot check. Neither primitive covers PR metadata, membership or future native writes. Commit objects are immutable; archive refs remain immutable only if our protocol and permissions keep them so. Value comparison also does not prove a monotonic generation or exclude ABA changes. [Git push](https://git-scm.com/docs/git-push). |

### Conflicting promises and observed details

The follow-up results are split into five child issues so each method and its limits remain reviewable: [queue behavior #519](https://github.com/joshlf/gherrit/issues/519), [local import and recovery #520](https://github.com/joshlf/gherrit/issues/520), [structural restart #521](https://github.com/joshlf/gherrit/issues/521), [CI, reviews and signatures #522](https://github.com/joshlf/gherrit/issues/522), and [transport loss and capacity #523](https://github.com/joshlf/gherrit/issues/523). Each links to frozen source and evidence. The following states what those observations change in the design.

The queue matrix does not support a method-only policy: SQUASH landed both members at build concurrency two but ejected the upper at one; REBASE's configured second build never actually ran. Size/occupied-queue traces do not expose internal atomicity. Genuine no-HTTP-read requests and natural 504/502 responses produced effects; absence remained bounded unknown. A fresh incremental native group reached 100 and rejected 101, separately from request-array bounds or large-stack landing.

Actual CI, producer, deployment and scanning rules had different eligibility conditions. Three website fixtures retained/rebound their existing reviews; the fourth had no reviews. All four user-operated rebases produced eight verified replacements, including six originally unsigned under rules without required signatures; matched automatic-prefix stale-review controls dismissed unchanged approvals. These observations do not resolve conflicting documentation into one unconditional signing or review rule. Local prototype failures require boundary enforcement, while nine after-ack structural recoveries supply bounded restart evidence. Cross-actor comment permissions and the informed browser walkthrough establish feasibility, without exclusive edit authority or human comprehension.

Earlier observations remain qualified: completed-group append conflicted with the guide, queued atomic writes were rejected, hinted unchanged pushes retained reviews, auto-merge was unavailable on the tested path, and the pinned broad CLI could not include GHerrit archives. Exact comment limits, error strings, graph shapes and convergence times remain implementation details. The linked original reports retain their precise conditions and sources.

Pin REST versions and handle additive fields and unknown enum values. [REST versioning](https://docs.github.com/en/rest/about-the-rest-api/api-versions) and [GraphQL's change policy](https://docs.github.com/en/graphql/overview/breaking-changes) protect documented compatibility with stated exceptions; neither freezes undocumented behavior or prevents service defects. Current Actions [bot-trigger rules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request) also require their actual approval/permission path; missing ordinary runs in our bot fixtures do not prove universal suppression.

### What this changes in the proposed model

The new evidence supports the existing separation between authored submissions, incorporated hosted ranges, accepted local results and external effect records. It does not justify collapsing them into one version or one success flag. A smaller implementation can keep custody, operation identity and results together and derive pending/completed views from that evidence. Whether it uses one record or several files, every dispatcher must enforce the same boundary. A proposed storage layout is not proof that the boundary holds.

The main new obligation is concrete enforcement of an existing promise: a cooperating process must not bypass admission, trust stale state or manufacture a new intent after evidence loss. Completion must name a valid retained result without preventing later ordinary authoring. The evidence does not require a general framework or establish that separate website/queue engines, a service or multi-commit authoring reduces total burden. A shared runner can enforce the boundary; its generality alone supplies no provider handoff.

### Questions still open

1. **Provider handoff and usable repeated publication.** What establishes that native suffix writes have finished and that the ranges used for an overlapping write are usable? Neither terminal admission status, finite coherent reads, a local lock nor successful restart tests supplies that general guarantee. Obtain authoritative semantics or explicitly choose and validate a weaker detection/recovery promise. Until then the overlapping boundary remains a restricted pilot, including F-before-surviving-B publication; this is not a complete replacement workflow.
2. **Production enforcement and recovery.** Implement the common dispatch boundary, exact identity, complete-result validation and operation-specific unknown reconciliation. Validate stale/direct workers, legitimate continuation movement, missing evidence, archive/destination ownership, old-writer exclusion, custody transfer and rollback. Positive attribution in a fresh sole-controller fixture does not establish multiwriter ownership or safe replay. Power-loss durability needs a suitable test environment; SIGKILL is not that test.
3. **Selected target support and intent policy.** Choose the first release's actual CI/rule/signature/queue profile and richer-authoring scope. Choose explicit versus automatic re-admission under a defined intent model; the successful explicit example does not choose it. These decisions combine engineering evidence with acceptable friction, availability and maintenance costs. No broad matrix rerun will choose those values.
4. **Website evidence and cancellation.** The four website rebases have human-attested initiation and independent API/Git effects, but no captured initiating HTTP trace, UUID or completion feedback. Actual signed-in upper/middle removals returned “Not Found”; independent reads retained ABC until successful lower cleanup. These functional observations do not establish pending cancellation or later write authority, and supply no captured initiating HTTP status or UUID. Website support needs its own supported intent/recovery evidence or a named initial exclusion.
5. **Author and reviewer experience.** Real people still need to validate mapping acceptance, continuation selection, long-discussion history discovery and changed-parent comparisons. The browser link check establishes rendering and reachability, not comprehension or preference. Commands versus hook, comment versus separate view, and checkout versus service remain choices judged by the consequences people actually experience.

The completed matrix now replaces earlier proposals to rerun broad CI, signing, queue, transport and structural probes. Further experiments should target a selected protocol or support promise. They can expose a counterexample and measure a bounded consequence; repeated quiet runs cannot establish a missing future-write fence or choose a subjective priority.

## Appendix: considered approaches not chosen for this proposal

### Leave the existing publisher unchanged

This has no migration cost and retains actual implementation/test evidence. It also retains local-only version allocation, no durable canonical binding, no native import path, independent cascade writes and partial publication hazards. It is a serious baseline, but does not deliver the requested native workflow.

### Add native registration and call the migration complete

A restricted registration/append experiment can gain native presentation with little publisher change. It still introduces native rule/lifecycle behavior, enrollment, first-CI and old-writer exclusion duties. Registration does not solve identity, archives, import or recovery. It is useful as a bounded experiment rather than the complete design.

### Create new PR generations for every structural revision

Immutable generations avoid many in-place graph rewrites. They also replace reviews and fragment discussions, and old generations can still have pending landing operations. We prefer canonical PR continuity by default. New-generation review remains a possible product choice when that cost is explicitly accepted; it is not an automatic repair for unknown writes.

### Retain the independent legacy cascade alongside native rebasing

Both writers would claim responsibility for the same branches and bases without a shared protocol. Native work therefore excludes the old cascade. Merely adding another check or local lock does not coordinate an already dispatched external writer.

### Require a new archive format before native enrollment

A per-submission nonce/event archive could replace version counters, but would also require a new history reader, index and reviewer experience. Existing exact archives can be preserved independently of native membership. Coupling the two migrations adds work before native integration earns its benefit; reconsider the archive representation separately if it reduces total cost.

### Treat Git atomicity as the whole transaction

Atomic refs and explicit leases are valuable, but neither covers PR lifecycle, bases, membership or pending server work. Git can omit an equal ref before lease enforcement. The push hint does not change that boundary. This proposal records separate effects and unresolved outcomes rather than declaring a single cross-resource linearization point.

### Collapse native outcomes into one success state

The same admission receipt can survive landing, ejection or removal, so one scalar success flag loses necessary facts. Direct, queue and UI outcomes use the same range importer; a second queue-specific integration baseline would need a distinct purpose. Queue-progress evidence can be stored separately. Choosing MERGE does not remove recovery obligations or guarantee every prefix will land.

### Use a comment or one submitted revision as the whole history

The authored archive, incorporated hosted range and accepted local result can differ. Collapsing them loses pending edits or selects the wrong next import baseline. A generated comment is a projection of exact confirmed submissions; bounded, deletable edit history cannot replace the archive or the operation record. Storing these roles together is allowed and does not erase their meanings.

*Authored by an AI agent acting on joshlf's behalf.*

