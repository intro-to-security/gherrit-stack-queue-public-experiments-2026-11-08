# Candidate 001: bounded adversarial review

Execution: swarm-model-refinement. Target: GHerrit's integration with native GitHub stacked PRs. This is warm specialist evidence for root adjudication, not a convergence verdict. I read the fixed C1–C8 contract, the complete corrected incumbent, Candidate 001, proposal-001, FRAME, and the five exposed lane reports. I did not inspect sealed material, run hosted operations, modify a realization, or test a repaired dispatcher.

The evidence supports keeping the incumbent's semantic direction and making its dispatch boundary concrete. I found no demonstrated candidate-only violation of C1–C8. There is one small evidence-summary error to repair, one dangling explanation reference, and a continuation interpretation that needs an explicit implementation discriminator. None establishes that a service, a generic scheduler, or a new storage layout improves the comparison. The provider handoff remains a shared unmet prerequisite for a full replacement.

## Concrete comparative traces

### 1. Reload under the owner blocks the stale-worker trace; it does not settle external work

Exposed witness: local/RESULTS.md, L28. Two workers read operation X as planned. Worker A dispatches X, records the response, installs the result, and completes. Worker B resumes with its earlier cached state and dispatches X again. The serialized emulator sees two requests, so this finding does not depend on lost updates in the emulator or a temporary-file race.

The incumbent already requires operational serialization and guards at execution, so this is a violation of its promised realization domain rather than evidence that its semantic state distinctions are wrong. Its statement that a local record can coordinate cooperating processes leaves the enforcement boundary comparatively implicit.

Candidate lines 59 and 87 give a constructive repair: B must acquire the actual local owner, reload X, and re-evaluate before dispatch. B then observes completed X and has no remaining effect to send. The same rule blocks L14's direct-worker recreation after operation.json is deleted, provided missing evidence is checked inside that boundary, and blocks L29's X/Y record mismatch when admission binds the manifest to its actual operation. A separate admission command cannot supply that protection to a worker that bypasses it.

This reduction uses one owner plus the existing operation/effect record. It does not require one new database per evidence role. Its costs are owner lifetime, reload/validation and common entry-path coverage. These are necessary enforcement costs for both designs' cooperative serialization promise, made explicit by the candidate. An implementation still has to establish that the owner cannot be bypassed or expire while the dispatcher continues.

Countertrace to a stronger claim: A writes dispatch intent, sends X, then dies before recording a receipt. The local owner becomes available. B acquires it and reloads X, but still cannot know whether X took effect. Candidate lines 136–142 correctly retain unknown state and prohibit an overlapping resend. An OS lock and fresh reload do not supply provider idempotency or exactly-once effects. The positive L28 reduction must not be reported as that stronger result.

### 2. Completion validation needs both the damaged-result negative and an ordinary-authoring positive

Exposed negative: local/RESULTS.md, L13. A complete record survives after either its continuation or its checkpoint is removed. The prototype still exits successfully and transfer admission permits mutation. Candidate line 89 rejects relying on that flag alone. This addresses C2/C4 without changing which range the importer should use.

Constructive positive discriminator, derived from the candidate's own C1 path:

1. Sync accepts committed input T as result V, creates continuation R at V, retains V and its incorporated-range checkpoint, and marks operation X complete.
2. The author selects R and runs ordinary git commit --amend, making R point to U. No GHerrit command runs during that Git edit.
3. The next preparation/recovery retains V as X's accepted result, captures U, presents its mapping and differences relative to V, and records accepted successor intent before any effect.

This must remain a valid continuation. U need not descend from V, because the candidate expressly supports rebase, reset and amendment. Equating completed X with the mutable condition R == V forever would reject this valid C1 trace. Conversely, accepting any occupied R as X's original result would admit L13's corrupted-result failure.

Read as a whole, line 89 permits the positive trace: it allows later branch movement, requires retaining the old accepted result, and can obtain the successor's explicit acceptance through lines 115–117. I therefore do not identify a contradiction. The phrase “an explicitly recorded legitimate successor” must not silently become a requirement that every ordinary Git edit synchronously writes GHerrit's journal. Record/review the successor at the next GHerrit preparation or recovery boundary. A focused realization test must establish that interpretation; this review has not done so.

The extra burden is preserving a stable reference to the accepted result and checking the attachment of later authoring. It is not a second range-integration baseline or a reason to freeze the continuation branch. Count that burden under C6 rather than calling completion validation free.

### 3. Error receipts cannot collapse to rejected/no-effect

Protocol/RESULTS.md records a 99-member creation returning 504 while creating exactly the intended group, and a fresh 100-member creation returning 502 while creating exactly its intended group. The original harness then issued a blind semantic retry of the first creation, violating its own plan. The fresh capacity replacement and that deviation remain separate evidence.

Trace: persist intent X → send create → receive 504 → classify X as definitely rejected → send X again. The received HTTP response does not justify the classification; the first effect already exists. Candidate line 136's “definitely rejected” and explicit 5xx qualification prevent this shortcut. The incumbent's generic “rejected” category was not itself an instruction to treat every HTTP error as no-effect, so the main defect is the harness's response classification. The candidate improves the explanation of that boundary rather than adding a new hosted guarantee.

The positive group observation can establish attributable membership in a fresh sole-controller fixture. It does not establish safe replay for arbitrary writers or absence of every later native write. Candidate lines 138–148 preserve that difference.

### 4. Local completion and queue admission do not authorize F-before-B republication

Trace shared by both designs: publish A–B; retain local A′/B′; native A lands; observe rewritten B; importer produces accepted follow-up F before canonical B. Even if local import X is complete and both its retained objects and checkpoint validate, the earlier provider operation may still affect B's head/base. Republishing F–B would overlap it.

Candidate lines 148, 195–217 and 323 retain that barrier. Neither the new owner nor the complete-result validation discharges it. The nine after-ack structural restarts verify client resumption at receipted prefixes, not a provider handoff or general unacknowledged-write recovery. All five lane reports retain that limitation.

This is an absolute outstanding full-workflow obligation under C4/C5 for the candidate and incumbent alike. It does not favor the incumbent, and a qualified pilot remains deliverable. It prevents presenting either design as a complete repeated-workflow replacement. A service or official-CLI adapter inherits the same prerequisite unless it contributes a supported different protocol.

### 5. Fresh names cannot clear unknown scope

Adversarial trace: native operation X has unknown outcome/scope; the author allocates a new change ID, new branch and new group, then publishes through the old public workspace target or replaces its checkpoint. The names differ, but X and the new operation share a target. Candidate lines 70, 138 and 213 block this through effect/checkpoint scope. If the old scope itself is missing, it cannot be declared disjoint.

Constructive narrower case: X's evidence bounds it to already-landed A/B resources; new C uses independent managed heads, canonical PR, checkpoint and public target. Publishing C need not settle X. Its dependency on ordinary moving trunk state is still re-evaluated. This preserves useful availability without inventing a global scheduler. Both designs already admit this distinction; no candidate-only generalization should be credited for it.

## Evidence and explanation corrections

1. **Candidate line 309 over-collects the website review result.** It says four website rebases “retained/rebound reviews and produced eight verified replacements.” ci-reviews/RESULTS.md's website table explicitly states that SG04 had no reviews. The other three website fixtures retained/rebound their existing review records; the last-push fixture remained REVIEW_REQUIRED / BLOCKED because those approvals were invalid at baseline. All four fixtures produced eight verified replacements. Use those separately scoped claims. This is an evidence-summary defect under C7, not a semantic design failure or evidence against the website operations themselves.

2. **Candidate line 264 promises a clarification “described below” that the refresh removed.** The incumbent's findings table explained the precise distinction: the official webhook reference documents the membership event, while the inspected Actions/stack-CI guides did not explicitly promise that activity as an Actions trigger. The candidate's later section no longer gives that explanation or its pinned webhook source. The positive target-workflow fixture also retains the same explicit-activity qualification in ci-reviews/RESULTS.md. Either restore a concise source distinction there or change the forward reference into a direct, scoped statement. The new real push-event check path may reduce dependence on this assumption, but does not retroactively document the `stacked` Actions path.

3. The refreshed queue claims match queue/RESULTS.md: the 3×2×2 grid includes three reused cells; configured REBASE concurrency two did not produce two actual builds; a successful SQUASH/concurrency-two trace is not a reliable workaround. The candidate correctly keeps that calibration rather than promoting the matrix to a supported target profile.

4. Genuine no-HTTP-read transport loss, acknowledged SIGKILL restart and machine power-loss durability remain distinct throughout the candidate. No result inspected here establishes the third. The local failures belong to a separate prototype; production GHerrit was not changed. Multi-commit evidence retains a flattened net range and tip message rather than lossless intermediate history. These are useful corrections under C7, not new model capability.

## C1–C8 accounting

| Obligation | Comparative result from this review |
| --- | --- |
| C1 | One branch/one authored commit per change remains the first supported path. Ordinary editing survives if the completion/successor positive trace above is accepted; that realization test remains required. |
| C2 | Canonical PRs, exact authored archives, hosted incorporation and accepted local results remain distinct. Missing/mismatched operation evidence cannot be replaced by matching ref values or trailers. |
| C3 | Native ownership and human prose policy are unchanged. Actual local ownership clarifies cooperative enforcement; it supplies no cross-clone/provider fence. |
| C4 | Outcome distinctions survive. Fresh admission and complete-result validation specify how to close exposed client bypass classes; their implementation, general provider handoff and operation-specific reconciliation remain unestablished. |
| C5 | First publication, append, amendment, import and structural continuation remain described. F-before-B is still gated, so the candidate remains a restricted design rather than a full replacement. Shared-prefix/nonlinear/oversized restrictions are explicit. |
| C6 | No whole-system reduction is established merely by one physical record. Shared semantic state remains necessary; owner/reload/result-validation and continuation attachment have real verification and availability costs. |
| C7 | Most updates preserve evidence scope; repair the website-review quantifier and missing `stacked` source explanation. No newly executed behavioral verification is supplied by this review. |
| C8 | Explicit adoption, exclusion of old writers, pending custody and deliberate rollback remain. Local completion cannot settle a previously dispatched provider request during transfer. |

Root can adjudicate the surgical boundary clarification using these traces. The review supplies no acceptance vote and makes no claim of local convergence, production readiness, measured savings, or repaired implementation correctness.
