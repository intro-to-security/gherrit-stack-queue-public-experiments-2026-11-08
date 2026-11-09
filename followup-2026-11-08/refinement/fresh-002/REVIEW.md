# Fresh Critic 002 review

Candidate002 makes the baseline's local enforcement and evidence limits more precise. The cited failures support the added rules; they do not establish an implemented improvement, a smaller whole system, or a complete repeated native workflow. I found no new hard-contract regression in the changed rules. The unresolved overlapping-write boundary remains material in both candidates, including the ordinary landed-amendment case. These are comparative findings for the coordinator, not an acceptance or convergence decision.

## Scope and identity

Execution: `swarm-model-refinement`. This is a newly isolated fresh-critic assignment under the fixed C1–C8 contract. The coordinator retains adjudication and stopping authority. I loaded the full `model-refinement`, `swarm-model-refinement`, `robust-code`, `reader-oriented-explanation`, `williams-style`, and `authorship-disclosure` instructions.

The three target inputs read in full were:

| Input | SHA-256 |
| --- | --- |
| `outputs/github-native-stack-design-2026-11-08/GOVERNING-CONTRACT.md` | `2b1172e0348bfaa2af2c7511df25853df2b06c1964bba718916c712dc65b3589` |
| Baseline: `outputs/github-native-stack-design-2026-11-08/post-experiment-refinement/candidate-001-corrected.md` | `fb1490a6c8a89b0532398e8dd1a3fdf9cde61c20068899c535c116a2288f5cfe` |
| Candidate: `experiments/native-stacks-followup-2026-11-08/refinement/candidate-002.md` | `84658d5380376651c9e8dd865a6f20101fa46a4d9440bcf96f5f399001bc19cb` |

I inspected their direct diff, the linked issue reports [#519](https://github.com/joshlf/gherrit/issues/519), [#520](https://github.com/joshlf/gherrit/issues/520), [#521](https://github.com/joshlf/gherrit/issues/521), [#522](https://github.com/joshlf/gherrit/issues/522), and [#523](https://github.com/joshlf/gherrit/issues/523), and the immutable [local RESULTS.md at `97b993e`](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/97b993efdda40a1cbe690d317e436e32937adb85/followup-2026-11-08/local/RESULTS.md) (Git blob `63e5c0b989d09a41998ba33548464fc4f0b3dde7`). I did not inspect other candidates, FRAME, proposals, coordinator notes, prior reviews, sealed material, holdouts, or the issue reports' parent #518. I did not inspect executable evidence archives or rerun their experiments. Report consistency is therefore checked more strongly than the underlying empirical claims.

No new experiment, external write, canonical edit, or nested convergence was performed. The host provides a separate child context and a shared filesystem; input isolation here rests on the assigned read boundary, not filesystem access controls. Exact effective model and reasoning effort are unknown.

## What the changes support

### One enforcement boundary can address the demonstrated local failures

Candidate lines 59 and 89 add current ownership, reload-before-dispatch, exact operation identity, and validation of the retained completed result. The frozen local report gives concrete reasons for all four:

1. In L28, processes P and Q both cache operation X as `planned`. P dispatches and completes. Q resumes its stale plan and dispatches again. The serialized emulator records two requests. A unique operation ID alone does not stop this trace. Ownership that covers rereading the durable state and recording dispatch intent before the send does: Q must reread completed/indeterminate X and cannot dispatch the stale plan.
2. In L14, an effect has applied, its operation record is removed, and a direct worker reconstructs intent from arguments. Requests increase from one to two despite separate custody admission refusing. The new prohibition on reconstructing intent, applied at every dispatch entry path, blocks that bypass. A wrapper-only check would still fail.
3. In L29, a pending manifest names X while a completed record names Y. Testing only a completed flag admits the wrong operation. The new exact-identity rule rejects this state without creating another lifecycle mechanism.
4. In L13, completion survives deletion of the continuation ref or checkpoint and transfer still succeeds. Checking the claimed retained result or a validated successor attachment exposes the missing result. Checking only the mutable tip would introduce a different failure: ordinary author amendment R→R′ would invalidate an otherwise intact historical result R. Candidate line 89 explicitly retains R independently and obtains acceptance of R′ at preparation/recovery, preserving ordinary Git editing.

These are enforcement/mapping findings. Several already contradict the baseline's intended coordination, captured-intent, or retained-result promises; they do not prove that four new semantic concepts are necessary. Candidate002 usefully closes underspecified implementation boundaries. Its own lines 278 and 324 correctly leave production closure outstanding. No final executor was inspected, so this review supplies no claim that the boundary is implemented or resistant to bypass.

A constructive reduction remains available within the proposed design: keep captured intent, scope, operation identity, progress, receipts, and any accepted result in one authoritative operation representation; derive pending/completed views from it. Under the local owner, reload that representation, validate the manifest identity, and persist the next dispatch state before sending. Recovery uses the same transition boundary. Keep the current authoring attachment mutable while retaining the historical accepted result. This removes duplicate admission paths and independent success flags; it does not merge the authored submission, incorporated range, local result, and external effect facts. The candidate permits this representation already. A separate custody database, queue importer, or website importer has not been shown necessary.

### Error receipts need the narrower meaning the revision gives them

The baseline's bare `rejected` category could be misimplemented as “any non-2xx response.” Candidate line 136 changes it to `definitely rejected` and explicitly preserves error responses with possible effects as unknown. [#523](https://github.com/joshlf/gherrit/issues/523) supplies a discriminating trace: create group X → receive 504 → X actually exists → blindly repeat/create overlapping work → existing-membership rejection. A durable record that calls the first response a no-effect failure permits the second dispatch. The revised rule blocks it pending justified reconciliation.

The no-HTTP-read fixtures strengthen the evidence that a missing acknowledgement can coexist with effects. They do not establish that an absent effect will never appear, that all positive observations settle every future effect, or that a retry is safe. Candidate lines 138, 146, and 211–217 retain those distinctions. This correction has a real availability cost: an unresolved effect may block overlapping work indefinitely without a supported resolution path. That cost belongs to both candidates' strong promise and cannot be hidden by storing fewer files.

## Repeated workflow and preservation

The important counterexample to a complete-workflow claim remains:

`publish A–B → author A′ and B′ depending on A′ → native-land old A → retain A′ as new-ID F below canonical B → publish F–B`.

Both candidates explain why appending F above B is wrong and why insertion/regrouping is required. Both also stop the overlapping structural write until provider handoff or a selected recovery contract is supported. More restart evidence does not change that boundary: an acknowledged unstack/park/push/register sequence is different from permission to begin it while a previous native suffix rewrite may remain possible. Candidate002 states this limitation at lines 195–217, 280, and 323. It is therefore a qualified design/pilot, not evidence that C5's full replacement milestone has been achieved. This shared limit does not favor the baseline.

The disjoint-work exception survives a useful challenge. After A/B land, a fresh C may proceed only if it has independent refs, checkpoint, and public target with evidence-backed old-effect scope. Reusing the same public workspace ref or managed-head trunk defeats that independence even with a new stack number. Lines 70 and 213 retain this guard. The exception is coherent, but a concrete scope evaluator and its acceptance evidence remain work; new naming alone cannot supply them.

The rest of the retained boundary is materially unchanged: one-commit linear local authoring; explicit canonical adoption and destination binding; immutable old archives and discussion continuity; human-owned prose/readiness; native topology and landing; per-layer range import; fresh continuation acceptance; explicit private/public intent; retained unsupported histories; and deliberate rollback after handoff. Shared-prefix, nonlinear, multi-commit, oversized, and structural restrictions remain named. Flattened multi-commit net-range tests are correctly not presented as support for preserving intermediate commit/message identity. No changed rule requires replacing canonical PRs or retargeting old archives.

## Total burden and strength of the evidence

Relative to the baseline, Candidate002 retains the same client, archive, canonical-binding, importer, journal, history-comment, single-checkout, and migration architecture. Its additional local enforcement obligations add implementation and verification work: a real owner, current-state checks at every dispatcher, exact identity validation, completed-result checks, and successor attachment handling. Some work was implicit in the baseline's promises; leaving it unstated never made the baseline cost-free. The changes improve the account of the burden rather than demonstrate its reduction.

The substantial author costs also remain: accepted mapping/differences, conflict decisions, explicit continuation selection, coordinated publication intervals, and possibly blocked overlapping work. No human study or production deployment comparison was inspected. The candidate correctly leaves command/hook, checkout/service, comment/view, target policy, and usability decisions open. It should not be summarized downstream as a measured usability improvement, a lower-cost implementation, or a service-free solution to provider handoff.

The new evidence changes particular comparisons without eliminating their controls:

- Queue results now refute a method-only explanation: SQUASH differs by tested build concurrency, while configured REBASE concurrency two did not produce a second build. One trace per cell does not select a reliable release profile. Candidate lines 156 and 307 preserve that limit.
- The website cases support path-dependent observed review/signature outcomes. User-attested initiation plus independent Git/API effects is weaker than captured initiating receipts. Candidate line 326 preserves that evidence gap and does not turn it into a supported UI recovery protocol.
- Nine structural restarts support resumption after acknowledged durable prefixes. They do not cover unknown in-flight effects, arbitrary dependency reorder, interrupted drop/fold/trunk changes, or machine power loss. The candidate's nearby qualifications prevent treating them as a general transaction proof.
- Distinct-actor history-comment tests improve feasibility evidence, while the bot's ability to edit user-authored comments disproves exclusive edit authority from visible authorship. Candidate line 107 preserves this. Rendered-link reachability remains separate from discovery/comprehension.

The relevant C7 risk is downstream claim inflation, not a demonstrated false statement in the changed rules. The 130 IDs are explicitly dispositions including reuse, negative controls, and unavailable/replaced premises. Preserve those qualifications when extracting the evidence summary. The linked reports support the narrower claims compared here; this review did not independently verify every archived receipt, all 130 dispositions, or fresh platform documentation.

The remaining decision-bearing obligations are the common ones the candidate already names: choose a supported handoff/recovery promise and target profile, implement and challenge the shared boundary, validate normal authoring through result attachment, and test the author/reviewer experience. Those obligations permit a qualified design handoff. They prevent treating this evidence refresh as production acceptance or completion of the overlapping repeated workflow.

*Authored by an AI agent acting on joshlf's behalf.*
