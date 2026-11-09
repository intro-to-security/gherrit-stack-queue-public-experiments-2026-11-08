# Round 1 adversarial comparison

Execution: `swarm-model-refinement`. Target: GHerrit's native-stack decision model. This is bounded warm-specialist evidence for root's adjudication. It selects no operating promise and claims no convergence or production acceptance. Model and reasoning effort were inherited; exact effective settings are unknown. The context is private, with a shared filesystem rather than ACL isolation. I loaded the full model-refinement, swarm, robust-code and applicable prose guidance. I read the focused contract, discovery, original C1–C8, complete incumbent, all three architect proposals, provider audit and coordinator counterexamples. I also checked the cited hosted-integration report. I read no sealed files, ran no new tests and made no external writes.

Evidence references: [focused contract](../CONTRACT.md), [C1–C8](../GOVERNING-CONTRACT.md), [incumbent](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/refinement/candidate-003.md), [alpha](../architect-alpha/PROPOSAL.md), [beta](../architect-beta/PROPOSAL.md), [gamma](../architect-gamma/PROPOSAL.md), [provider audit](../provider-audit/REPORT.md), [coordinator witnesses](../COORDINATOR-COUNTEREXAMPLES.md), [hosted integration](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/ade319107e71b6eff646a1574139e2c15486fe6d/local-git/hosted-integration/RESULTS.md). Incumbent line numbers below refer to the complete candidate003 recorded in discovery, SHA-256 `5b0c763bd6a706e88db644dd368013b2f95c7d3882a8ca79fb2febf487f6885f`.

## Main finding

The architects expose useful distinctions and conditional reductions, but the strongest apparent new reductions are already substantially permitted by candidate003. Local retained acceptance, reusable captured acceptance, automatic re-admission as an open policy, and author-approved staging all have incumbent text. Credit a clarification or a concretely specified narrower domain where that is the actual delta. Do not count these as several newly eliminated mechanisms.

The remote operating promise remains a real comparison. C1–C8 do not impose universal exclusion of future native writes. Removing that promise can enable useful work, but retaining inputs alone does not preserve submitted intent or canonical review continuity. A useful weaker protocol must pay those recovery costs explicitly. Conversely, a strict pilot that cannot finish overlapping repeated work does not become a full replacement merely because its refusal is cautious.

## 1. Local acceptance S: distinguish a clarification from an actual restriction removed

Alpha's constructive argument is sound within its stated domain: after incorporating coherent H1 into R1, a later H2 can be integrated against H1 while retaining local edits. The accepted checkpoint records an integration fact. It need not assert that H1 is the last remote revision. An unknown external operation can retain its captured inputs and outcome while a distinct local continuation is accepted.

The comparison against the actual incumbent is less decisive. Candidate003 already states:

- Line 89: retain historical accepted results independently of the mutable authoring tip; recovery can validate a successor attachment.
- Line 148: incorporation records local inclusion, without settling an outstanding request or granting overlapping write permission.
- Lines 187–193: incorporated hosted ranges, accepted local results and captured submissions advance at their own boundaries.
- Lines 203–207: accept by a fresh continuation and an exact checkpoint, without changing the caller's source/index/worktree.
- Line 217: non-destructive local staging can continue while the overlapping hosted boundary remains gated.

The potentially contrary text is line 280's gate on protected-checkpoint replacement. That wording has two readings:

| Incumbent reading | S's actual contribution |
| --- | --- |
| Replacement means consuming/overwriting custody required by a pending operation or granting new hosted-write authority. | S is already allowed. No availability difference is established. Make the non-destructive case explicit. |
| Any accepted successor checkpoint is forbidden while native settlement is unresolved, even if all prior custody remains intact. | S removes an unnecessary coupling for this local-only domain. Its benefit is earlier committed local progress, with the same hosted-write gate. |

The second reading is not forced by the rest of the incumbent. A synthesis should resolve the ambiguity before claiming dominance over a blanket rule.

Concrete realization falsifier: pending O captured P0; a new accepted P1 becomes `current`; a stale worker reloads `current` and dispatches O using P1, or a completion validator takes P1 as evidence that O completed. S fails despite retaining both Git trees. The required relation is `O → captured P0`, with independent successor acceptance and dispatch eligibility. Candidate003 already requires captured checkpoints and current dispatch-owner validation. S need not add another database or importer, but that pointer discipline still needs implementation.

**Supported disposition:** adopt an explicit non-destructive successor rule if useful. Claim a semantic reduction only against the restrictive reading, and only for retained local acceptance. No remote gate, full repeated-workflow gap or custody verification disappears.

## 2. Continuing accepted intent: genuine variation, ambiguous incumbent delta

Beta and gamma correctly distinguish a user's authorization from each provider request. A new UUID/head/options record is required for a new request, even when the user previously authorized a continuing goal. Withdrawing future dispatch cannot cancel an already sent request. Unknown dispatch does not become known-unsent because the desired state is absent.

However, candidate003 line 158 says a later admission is a distinct intent; it does not expressly require another human interaction. Line 115 already reuses unchanged captured acceptance, and line 325 expressly leaves explicit versus automatic re-admission open under a defined intent model. The phrase distinct intent therefore needs disambiguation before treating beta's proposal as removal of a categorical incumbent ban.

Use this reduction rather than merging request identities:

`accepted authorization G → request R1 → observed outcome`

`same retained G, if still applicable → new request R2 → separate outcome`

For a one-shot authorization, G authorizes only R1 and R2 needs new acceptance. For an expressly continuing goal, G can cover R2. The one-shot path remains unchanged. This is a common representation plus a real optional authorization breadth; it does not prove fewer concepts overall.

Concrete discriminators:

1. G accepts canonical A/B, trunk T, method M and a named parent-only native transformation. R1 admits AB. A lands and B is ejected at H2. If B's own accepted patch remains valid, all prior outcomes/authority are resolved, readiness holds and the transformation is within G, R2 may use H2 with its own receipt. This is additional behavior if the incumbent is read as one-shot-only.
2. B's patch changes outside G, the method changes, or ownership moves into another layer while the cumulative tree remains equal. A validator that uses PR ID, tree equality or the still-running command to authorize R2 accepts unapproved work. It fails the proposed common rule.
3. R1 has a missing acknowledgement, and a current queue read is empty. G does not authorize blind R2: the old admission may still occur. Continuing authorization cannot repair missing outcome evidence.

The optional continuing goal adds accepted-transformation validation, durable goal custody, withdrawal/stopping behavior and explanation. Existing exact-range comparison is useful evidence infrastructure, not a proof that all native-only transformations can be classified safely. The benefit is fewer repeated interactions for users who request that automation. No universal burden or preference advantage follows.

**Supported disposition:** replace ambiguous intent wording with authorization versus request. Keep one-shot as a provisional default. Treat continuing authorization as a coherently subsumed extension, not as a required release feature or a proven simplification over the actual incumbent.

## 3. F-first staging: valid restricted use, already admitted, not an overlap solution

Candidate003 line 195 explicitly permits author-approved staging instead of joint F–B publication. Alpha/gamma make that option more concrete. They show why joint structural insertion is not mandatory for every useful first-release workload; they do not show it unnecessary for the full simultaneous-review use.

The constructive staged trace is:

1. Original hosted A–B exists; local A′/B′ remains captured. Old A lands. Preserve canonical B, its hosted inputs, B′ and all pending evidence, including suffix work not present on the selected local branch.
2. Derive fresh-ID F containing A's retained delta on the actual landed trunk. F contains no B ancestry or B-owned amendment. Obtain explicit acceptance of delayed B′ publication.
3. Publish F alone against the ordinary trunk with fresh, independently authorized targets. Leave B's canonical PR/head and B′ custody intact. Land F.
4. Import actual F/trunk and B outcomes, retaining B's change-local amendment and identity. Publish B′ to canonical B only when the selected operating promise permits that write. Complete another landing/import round.

This can avoid unstack/park/reorder/register for that continuation. It has three load-bearing qualifications.

**Omitted canonical B is not absent scope.** An F-only local input does not erase B from the earlier operation, ownership map or recovery record. If old A's requested merge is completed but possible remaining native work is confined to the known old B/C suffix, fresh F can be outside that suffix. If the old outcome, actual affected scope or other dispatch is unknown, F's fresh ID alone proves nothing. The older record remains even when F is independently publishable. Final B publication still overlaps the old suffix and retains the strict-versus-recovery question.

**Public source and checkpoint targets are effects too.** If the accepted public invocation captures source branch `work` at F–B′, a supposedly F-only submission must not silently publish that full source while describing B′ as local-only. Nor can it silently suppress the user's public-source intent. Use an explicitly accepted F-only source/continuation or disclose the broader public export. A reused source target or destructively replaced checkpoint can also make two otherwise fresh PR operations overlap. Native scope and unresolved client scope must both be checked.

**Staging changes the service offered.** A user may need reviewers to assess F and B′ together, or may have no independently landable F. That use still needs joint ordered publication. Staging adds a separate review/landing interval, delayed dependent visibility, more selection and a later B import. It is a named C5 restriction, not dominance over joint publication. With strict final-B refusal it remains a pilot, rather than a finished full repeated workflow.

The coordinator's late inversion witness does not directly apply to this staged order-preserving trace: F is fresh and the relative order of older B/C is retained. That absence is not a correctness proof. Native possible write scope, old/new bases, per-layer incorporation, target rules, public targets and completion reporting remain obligations.

**Supported disposition:** a concrete staged release option can remove the immediate need for structural insertion for accepted F-first workloads. Record it as domain narrowing and elaboration of an incumbent option. Do not credit it as a provider handoff or a replacement for joint review.

## 4. Recoverable overlap: archives do not preserve intent or lifecycle by themselves

The provider audit supplies the right calibration: terminal direct `merged` is a completed requested merge; terminal `enqueued` is completed admission. Post-terminal PR/ref mismatch establishes an unusable mixed observation, not a proved late suffix write. Normal provider sync-and-push guidance is positive evidence of intended repeated use. No inspected source binds every suffix write to that terminal result or specifies arbitration with later client updates.

Thus a candidate can separately record a known requested outcome, usable observed ranges and an unproved no-later-write premise. These are not synonyms for an unknown unacknowledged request. A weaker post-native promise cannot use that distinction to retry genuinely unknown client writes.

### Retained bytes can coexist with silent intent loss

Let H0 have `x=0`. Export accepted X with `x=1`; confirm X and advance the incorporated baseline to X. Suppose admitted delayed native drift N derived from H0 later restores `x=0` on a new parent. With `I=X, L=X, H=N`, ordinary three-way integration treats the removal as the hosted-side change and can produce N without conflict. The archive still contains X, but the next accepted continuation has silently consumed its published intent.

Beta/gamma identify the missing rule correctly: classify this as post-export drift and preserve/expose the retained X obligation. Either attribute an allowed native transformation and reapply the later authored delta against the right predecessor, or obtain explicit recovery acceptance with the proposed removal visible. A normal importer plus an obscure archive is insufficient. This is candidate-attributable burden in classification, custody, presentation and validation; it should not be counted as free reuse.

This is a counterfactual for the weaker promise, not an observed provider failure. If authoritative provider arbitration excludes it, the recovery requirement can be narrowed accordingly.

### Retained intent can coexist with irreversible loss of canonical continuity

Start with old B1→C1 as a possible delayed suffix result. Rebuild the current surviving canonical reviews into C2→B2, setting B's base to C's managed branch. If an admitted old effect can later install B1 and C1 on those heads while that new base relation exists, C1 contains B1. GitHub's documented indirect-merge behavior can terminalize B before the intended new-order landing. Restoring bytes cannot reopen a merged B.

This trace depends on a delayed interleaving that the evidence does not show occurred. It refutes the universal logical claim that input retention alone makes every admitted native rewrite harmless. The weaker candidate must exclude that interleaving through supported scope/arbitration, restrict the structural domain, or count canonical-review replacement/follow-up and fragmented continuation as a possible cost. It cannot promise both unrestricted admitted drift and uninterrupted canonical continuity merely by retaining archives.

C2 makes continuity a default and requires alternatives that replace reviews or change archive meaning to be counted. It does not turn this trace into a universal veto on every weaker promise. C4/C5 still require concrete recoverability and useful repeated work. A candidate that responds only by stopping forever has not supplied the latter; a candidate that proposes an explicit follow-up has changed the continuity promise and must say so.

### Whole comparison

| Promise | Useful benefit | Cost/obligation that remains |
| --- | --- | --- |
| Strict supported exclusion before overlap | Excludes the admitted late-overwrite/interleaving traces when its premise is actually supplied. | Provider completion/arbitration premise, availability loss and incomplete repeated workflow while that premise remains unsupported. |
| Retained intent plus detected drift on later connected use | Can support ordinary repeated work without pretending to prove universal future exclusion. | Intent-aware drift recovery, possible temporarily wrong hosted state, checks/reviews invalidation, delayed detection, manual recovery and possible terminal canonical review. Requires eventual quiescence for stable completion. |
| Staged/order-preserving weaker domain | Avoids the specific old-order/new-order inversion and joint structural machinery for accepted staged work. | Does not establish all same-order lifecycle safety; still needs old scope, final B protocol and explicit staging costs. |

Root has not selected among these promises. None has a demonstrated universal total-burden advantage. A direct-only, captured, same-order domain may justify a narrower candidate, but its exact retained promises and completion trace must be reviewed before claiming closure.

## 5. Other proposed closures: exact classifications

| Claim | Supported reduction | False stronger conclusion |
| --- | --- | --- |
| One importer for direct/queue/UI outcomes | No separate integration baseline/engine has an identified purpose. Incumbent line 148 already says this. | Receipts, actual lifecycle and initiation evidence become interchangeable. |
| One dispatcher per conflicting scope | Shared enforcement and custody rules; failures identify required implementation boundaries. | Checkout and service have equal deployment/collaboration costs, or local ownership fences native work. |
| Direct API versus released broad submit | Current broad CLI is not a drop-in under the incumbent's coupled head/archive contract. Remove that interchangeable option. | Direct calls universally dominate all CLI delegation. C1–C8 do not independently require that exact atomic archive vector; a different archive/export protocol must be compared as a substantive candidate. |
| Explicit command versus hook | Raw indistinguishable pre-push dry-run/real inputs cannot support different correct independent effects. A common explicit intent boundary is required. | Every compatible wrapper/hook is dominated; familiar-push convenience disappears. |
| Comment versus body/view | Exact archive, generated index and reviewer interface have different duties. Naive whole-body overwrite fails the chosen prose policy. | A comment is universally best, or separating duties eliminates discoverability, hosting and coordination choices. |
| Linear one-commit default | Valid narrow domain; hosted ranges remain explicit. Net-range tests do not prove internal-history preservation. | Richer histories have no benefit, or an excluded use is supported merely because a range type exists. |
| Target profile and dispatch/storage/rollout | Correctness duties are not optional backend modes; eliminate unsafe choices from the product menu. | Provider configuration, concrete storage and migration validation cease to cost work, or one green/method flag determines compatibility. |

A provisional default can be supported without human preference measurements. It should name the benefit that could defeat it: hook convenience, service collaboration, a better reviewer view, richer retained history, or simultaneous dependent review. Architectural subsumption removes duplicate engines; it does not erase these value/deployment decisions.

## Synthesis constraints supplied to root

1. Do not count S, general accepted intent or staged F-first as three unconditional new dominance results. Their incumbent deltas are narrow or ambiguous; the concrete staged trace and clarified boundaries are useful evidence nonetheless.
2. A justified smaller model has one identity/custody/import/effect core, with interface-specific evidence and genuinely variable authorization/domain promises. Much of this is a preserved incumbent strength.
3. Distinguish request completion, range usability, future-write exclusion and post-drift recovery. Neither projection lag nor finite quiet reads selects the operating promise.
4. If a recovery alternative is synthesized, carry both the confirmed-edit-removal trace and irreversible canonical-lifecycle trace into its preservation claims. Same-order staging may narrow one hazard, but cannot erase unresolved scope or final B obligations.
5. State each result as already settled invariant, clarified rule, conditional incompatibility, narrowed supported domain, provisional default, genuine remaining tradeoff, or required validation. A shorter inventory is not itself a conceptual reduction.

No fresh-agent live behavior, whole-system cost measurement or human study is claimed here. Root retains comparative adjudication, required successor reviews/rereads, stopping and publication authority.

*Authored by an AI agent acting on joshlf's behalf.*
