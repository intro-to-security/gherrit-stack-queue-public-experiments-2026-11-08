# Architect beta: one publication protocol across evidence surfaces

Execution: swarm-model-refinement. Governing semantic guidance: model-refinement. Target: GHerrit's integration with native GitHub stacked PRs. This is an isolated candidate contribution for the root coordinator, not an adjudicated result or a convergence claim.

Evidence basis: [fixed contract](../../../../outputs/github-native-stack-design-2026-11-08/GOVERNING-CONTRACT.md), [incumbent](../../../../outputs/github-native-stack-design-2026-11-08/post-experiment-refinement/candidate-001-corrected.md), and exposed [queue](../../queue/RESULTS.md), [local](../../local/RESULTS.md), [structure](../../structure/RESULTS.md), [CI/reviews](../../ci-reviews/RESULTS.md) and [protocol](../../protocol/RESULTS.md) reports. Hosted claims below are bounded November 8–9, 2026 observations from those reports; no source was refreshed or live state rechecked here.

## Recommendation

Keep the incumbent's semantic center: explicit accepted ranges, canonical reviews, native topology and landing, one range importer, and durable records for individual effects. The follow-up campaign strengthens that composition rather than establishing a need for a broader orchestration model. Generalize the evidence treatment across interfaces, while repairing the local admission/dispatch boundary. Do not add separate queue, website, comment or multi-commit engines.

The useful common rule is:

> A publication operation binds accepted input, canonical targets and its individual effects. Before any new effect, the cooperating executor must establish custody of that exact operation and validate the evidence required by that effect. An observation may identify a completed effect or an importable range without establishing that all earlier external work has stopped.

Much of this rule already appears in the incumbent. Its added value is a concrete realization boundary: the same executor that can dispatch must enforce custody, identity, current admission and completion validation. A checklist in front of a worker that can recreate missing intent or use cached admission is insufficient. This is a surgical refinement, not a claim to discover a new abstract protocol.

I do not recommend a larger semantic generalization on the supplied evidence. In particular, a generic effect scheduler, a service, or a lossless multi-commit authoring model would add obligations without resolving the provider handoff. The first one-commit, one-branch path should still execute an ordinary ordered list under one cooperating publisher.

## Concrete candidate

Retain the incumbent's captured authored input, canonical bindings and archives, hosted observations, operation record, and distinct incorporated-hosted/accepted-local checkpoint roles. They may share storage. Do not introduce another state database or another integration baseline.

Apply four changes to the description and eventual realization:

1. **Put local mutation admission at the dispatch boundary.** For cooperating processes in the enrolled checkout and its linked worktrees, acquire an actual common owner before loading mutation admission, and retain it through the mutation sequence. Load or revalidate the current manifest and operation record under that owner; previously cached `planned` or `complete` state grants no dispatch authority. Direct worker entry must use this same boundary. A missing or mismatched record cannot be reconstructed as a fresh operation from command arguments.
2. **Validate the result claimed by completion.** A completed operation must identify its own manifest, captured input, receipts and accepted result. Recovery or custody transfer validates the required retained objects, continuation and checkpoint, or a recorded legitimate successor. A boolean completion marker is insufficient. This does not require an authoring branch to stay forever at its original tip: continued authoring must preserve the accepted result and its checkpoint rather than silently invalidating the old recovery claim. The exact retention/successor representation remains an implementation obligation.
3. **Describe evidence by what it establishes.** A successful response, a uniquely attributable positive transition, an observed hosted range and evidence of external completion are different claims. Use the same operation record for real no-read requests and ambiguous 5xx responses. Associate positive effects only under the stated sole-writer/unique-identity premises. Absence does not establish nonexecution, and imported work does not clear a possible future-write barrier. Website operations retain the evidence they actually expose; the client must not manufacture a REST UUID or equivalent receipt.
4. **Treat policy outcomes as observations at exact identities.** Record the rule, event/target, tested SHA, producer and actual gate relevant to an operation. Queue method, configured concurrency, review record state, signature verification and deployment state remain facts with their own semantics. Do not compress them into a global `native-ready` flag or one universal precedence rule. This can be ordinary fields in existing observations and previews; no plugin/profile framework is needed.

The local owner can be an operating-system lock around the common checkout state, with mutation helpers kept inside its lifetime. Its name alone proves nothing. It needs concrete stale-worker and direct-entry checks. This proposal grants no exclusion across clones, administrators, uncooperative writers or requests already accepted by GitHub. The process may die and release its lock while an external request remains unresolved; the durable record then withholds overlapping dispatch after restart. A timeout lease would not strengthen that claim.

## Additional worthwhile cases and their limits

The campaign adds useful composition witnesses without requiring new semantic paths:

| Case | Application of the common rule | What remains unavailable |
| --- | --- | --- |
| PR/comment creation, base edit, stack creation or append with no client HTTP read | The 500 ms hold cases supply uniquely attributable positive effects in fresh sole-controller fixtures. Reconciliation may bind the exact discovered object or transition to the original operation; it does not create a new logical request. | General deduplication, arbitrary multiwriter attribution and a future-write fence. Immediate-close absence cannot authorize replay. |
| Natural 504/502 while creating 99/100 members | Preserve the received response and the original effect as unknown; independently observed exact membership can establish what happened in that fixture. The fresh incremental case separately supports a total capacity of 100 and rejection of 101. | A response-status rule saying all 5xx writes failed, safe blind retries, or a promise about landing 100 members. |
| Actual website rebase without a captured initiating HTTP response | Preserve human-attested initiation separately from independently verified replacement ranges, membership, reviews and signatures. Those exact ranges can use the ordinary scratch importer once identity and usable inputs are established. Native rewrites create no authored archive by themselves. | An equivalent REST receipt, cancellation/completion semantics, authority for overlapping republication or a general website guarantee. |
| Queue outcomes that differ by method and delivered candidates | Keep original admission evidence while importing each actual landed/rebased/ejected outcome. An explicitly new admission at the new selected head is a separate intent. | A stable “SQUASH is broken” rule, a guaranteed build-two workaround, or permission for silent re-admission. |
| Human PR prose alongside an application-owned history comment | Keep publication identity and the generated artifact bound by recorded IDs. Programmed writes to separate resources composed in the observed trace. Check known IDs and treat duplicate marker lookup as conflict. | Exclusive edit authority from comment author identity, safe unknown-create replay, or demonstrated reviewer comprehension. |
| A stale second local worker or direct worker invocation | Reload the exact operation under the same actual local owner before dispatch; reject missing/mismatched custody and validate claimed completion. | Global exactly-once delivery or exclusion of delayed provider effects. |

These broaden the **evidence for the incumbent composition**, not its contract coverage by themselves. The incumbent already admits alternate evidence surfaces and a shared importer. Credit the candidate for closing a concrete realization loophole and avoiding duplicate engines, not for adding merely broader names.

A further extension worth considering later is explicit multi-commit local groups described by accepted base/tip ranges. A singleton commit is naturally such a range, so storage need not change. However, the tested importer flattens a group and preserves its tip message, not every intermediate commit/message. A supported lossless group model would need grouping intent, per-commit identity/message/signature policy, rewrite behavior and conflicts. An explicitly accepted net-range/flattening mode could be a narrower product choice, but it still adds an author decision and a new mapping admission path. I would keep both outside the first implementation until that benefit is requested and evaluated. An existing range field is not evidence that the extension is free.

## Preservation mapping and discriminating traces

The candidate retains C1–C8 without narrowing them. Its mapping is:

| Contract | Retained behavior and candidate check |
| --- | --- |
| C1 | Ordinary commits on one branch remain the initial authoring representation. Capture and explicit mapping acceptance precede publication. No added group declaration is required for this path. |
| C2 | Repository/destination, logical change, exact range, managed head, canonical PR and immutable archives remain distinct bindings. Local completion is additionally bound to the exact operation. A SHA lease still supplies neither ownership nor incorporation. |
| C3 | GitHub owns native membership/landing; GHerrit owns cooperative publication/reconciliation; people own ordinary prose/readiness. The old cascade is excluded for enrolled work, including its already-dispatched effects. History ownership is a client policy. |
| C4 | Intent precedes dispatch; partial and unknown effects survive restart. Local serialization is enforced within its stated domain. It supplies neither API/Git atomicity nor provider settlement. Unmentioned suffix work remains in scope. |
| C5 | First publish, append, amendment, actual prefix import, F-before-surviving-B insertion, structural edits, completed groups and adoption keep their incumbent paths and restrictions. The overlapping provider handoff remains unresolved; this is a restricted design, not a full-workflow replacement. |
| C6 | Reuse existing records, evaluator and serial executor. Count local ownership/result validation, availability loss, history UI work and provider investigation; do not hide them in an adapter. |
| C7 | Keep documentation, inspected code, bounded actual observations and proposed enforcement separate. Website effects are independently observed after human attestation; initiation HTTP/UUID/UI feedback is absent. |
| C8 | Keep reversible enrollment/rollback and production acceptance gates. Do not enable legacy fallback on unresolved native work. No canonical edits, new live tests or external actions are part of this contribution. |

**Repeated-workflow trace.** Publish canonical A–B; retain local A′–B′; old A actually lands; import B's exact rewritten range while retaining A's unpublished amendment as new-ID F before B′. The importer still records incorporated-hosted and accepted-local ranges separately. F–B publication needs the existing structural path, canonical B and its old archives. Actual import does not establish that GitHub cannot later rewrite B. Until the supported handoff/recovery contract exists, the operation stops at that overlapping mutation boundary with F and B′ retained. Local record repairs do not turn that restricted trace into completed production coverage.

**Stale-worker trace.** Processes X and Y both previously saw `planned`. X acquires the common owner, reloads current intent, records dispatch and completes. Y acquires ownership later and must reload; it sees and validates X's result, then sends nothing. If X instead dies after dispatch intent, Y sees an unresolved effect and sends nothing. If the operation record is absent or names another operation, Y refuses rather than synthesizing `planned`. This addresses L14/L28/L29 in the cooperative realization. A lock taken after trusting cached admission would fail the trace.

**Unknown-outcome trace.** The client records create intent, receives 502, and has no completion evidence. It does not resend. A sole-writer exact-order lookup finds the intended native group; that observation may settle the creation fact under its attribution premises. A different unknown unstack is followed only by group absence: keep it unresolved because the absence does not prove the old request cannot later act. One status enum for both “received HTTP response” and “known rejected” would fail this trace.

**Import versus write-authority trace.** A user reports pressing website Rebase stack; API/Git reads establish new canonical ranges and retained reviews. Read-only scratch import may proceed without creating an authored submission. A subsequent publish to the same heads remains gated on supported completion/recovery evidence. A later fresh independent chain can proceed only when the old possible effects' scope is actually established as disjoint, including managed trunks, public refs, membership and checkpoints. Different group numbers alone are insufficient.

## Whole-model burden against the incumbent

| Area | Incumbent burden | Candidate difference |
| --- | --- | --- |
| Semantic rules and representations | Accepted ranges, identity, distinct revision roles and effect recovery already exist. | Little semantic growth. Make the admission/result boundary explicit; avoid counting restated common rules as simplification. |
| Local coordination and storage | One cooperating publisher and retained operation/checkpoint evidence are already required. The separate prototype fails important admissions. | Implement a real common local owner, exact record identity and result validation at dispatch/recovery. This is additional implementation/check work, partly replacing unenforced assumptions. It is not a new service or distributed lock. |
| API/CLI adapters | Exact intents, outcomes and side effects require adapter work. The pinned CLI cannot publish the archive vector with its broad submit path. | Share the existing record/evaluator across surfaces. No new wrapper is justified by the local parser test. Unknown-write reconciliation remains per actual API semantics. |
| User work | Preparation, continuation selection, explicit structural intent and blocked ambiguous work already cost time. | No new mode selection or mandatory workflow step on the simple path. Better diagnostics and fewer accidental duplicate effects are proposed benefits; author time and comprehension have not been measured. |
| CI/reviews/history | First-check eligibility and policy identities require validation; history discovery remains a product duty. | Replace outdated empirical claims with exact observed alternatives. Do not add a universal policy engine. Preserve distinct deployment/check semantics and nonexclusive comment edit authority. |
| Operations and migration | Provider handoff, pending custody, old-writer exclusion, recovery and rollback remain. | No reduction in the principal unresolved provider/deployment burden. No production-acceptance claim follows from nine after-ack structural recoveries. |

The supported comparison is narrow: the proposed boundary eliminates known ways a cooperating worker can bypass an already required protocol and keeps several interfaces on the same model. It should cost less than separate recovery engines for each surface, but the incumbent already advocates reuse, so there is no demonstrated whole-system complexity win over a correctly realized incumbent. There is no measured human comprehension or cost improvement. A larger generalization currently has a weaker burden case than this surgical candidate.

## Counterexamples and remaining obligations

- **Cached state after taking a lock:** the stale-worker duplicate still occurs if the worker does not reload. The required property is ownership plus fresh admission at dispatch, not a lock-shaped object.
- **A command bypasses admission:** L14 shows a worker can recreate missing evidence even when transfer admission refuses. Every mutation entry path, helper and recovery path must enforce the boundary. This has not been implemented or verified here.
- **A completed continuation is missing or legitimately advanced:** L13 exposes the missing-output case. The realization must validate retained accepted results while supporting recorded continuation evolution. A permanent equality check on a mutable authoring branch is not a sufficient design.
- **A received error follows successful mutation:** the natural 504/502 cases refute “response received means safely rejected.” The corrected harness guard is evidence about that harness, not a provider guarantee or a completed GHerrit fix.
- **An apparent positive match has another possible author:** real cross-actor comment editing and duplicate markers refute attribution from visible author/marker alone. Bind known IDs; use sole-writer uniqueness only where established. Conflicts need recovery, not arbitrary selection.
- **Uniform readiness from a green record:** the last-push website fixture retained APPROVED records but stayed blocked; producer pinning rejected successful manual statuses; deployments followed different precedence from required statuses. The observation model must preserve the relevant distinctions.
- **Serialization substitutes for provider settlement:** a single local process and finite coherent reads do not prevent a delayed GitHub rewrite. Queue admission, landing, ejection and usable suffix state remain separate. This is the main unresolved full-workflow obligation shared with the incumbent.

Before enabling mutations, implement and adversarially exercise the local boundary, including stale/direct-worker entry, operation-identity mismatch, missing continuation/checkpoint and legitimate continuation movement. Preserve the existing range/structural fixtures and exact archive checks. Do not convert SIGKILL evidence into a machine-power-loss claim. Establish provider handoff semantics or explicitly choose and validate a weaker recovery contract before claiming repeated overlapping publication works end to end. Separately validate human author/reviewer use of continuation selection and historical comparisons.

Website queue removal remains unperformed with login pending; no inference here supplies its result. All four actual website-rebase paths are distinct bounded observations, not substitutes for that missing queue action. This contribution used only the frame, fixed contract, incumbent and exposed five reports. No sealed cases, other architect proposals, coordinator advocacy or new live tests were inspected. Exact effective model and reasoning effort were not exposed by the host; isolation was private context plus allocated file boundaries on the shared filesystem, without OS ACL isolation.

*Authored by an AI agent acting on joshlf's behalf.*
