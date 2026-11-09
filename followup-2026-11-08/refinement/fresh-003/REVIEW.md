# Fresh Critic 003

Execution: `swarm-model-refinement`. Foundational guidance: `model-refinement`, `robust-code`, `reader-oriented-explanation`, `williams-style` and `authorship-disclosure`, all read in full. Target: the native-stack design in `candidate-003.md`, under the fixed C1–C8 contract. This is evidence for the root coordinator, not a convergence decision.

The candidate preserves the baseline's main model and makes several enforcement requirements more precise. The inspected evidence supports those repairs, but does not establish an implemented replacement workflow or a whole-system burden reduction. One concrete delivery defect remains: the candidate's new website-removal observations are supported locally, while its public evidence links still describe the earlier, unadmitted fixture.

## Input and isolation record

- Candidate SHA-256 verified: `5b0c763bd6a706e88db644dd368013b2f95c7d3882a8ca79fb2febf487f6885f`.
- Read the specified governing contract, baseline `post-experiment-refinement/candidate-001-corrected.md`, deliverable `refinement/candidate-003.md`, `ui/QUEUE-BROWSER-RESULTS.md`, `queue/ui-removal/RESULTS-UI.md` and `queue/ui-removal/case-index.json`. The initially supplied basename `case-index.json` was resolved in the UI-removal directory; no index exists directly under the campaign root.
- Additional directly linked evidence inspected through read-only GitHub tools: the pinned follow-up directory listing at `97b993efdda40a1cbe690d317e436e32937adb85`; its `local/RESULTS.md` and `protocol/RESULTS.md`; two exact UI-report path lookups at that pin; and linked queue issue #519. No other candidate, FRAME, architect/coordinator proposal, prior review or holdout contents were read. Directory metadata exposed the names of evidence directories; their audit contents were not read.
- No experiments, external writes, canonical edits or nested refinement loop. Only this review file was written. The context was freshly assigned with a bounded input list; the filesystem is shared, so this is scoped context/read isolation rather than an operating-system read barrier.
- Requested model and effort: inherited, with no explicit override visible in the assignment. Exact effective model and reasoning effort: **unknown; not exposed by this host context**.

## Concrete finding: publish the evidence the new UI claims actually use

Candidate lines 154, 278 and 326 report signed-in C/B website removal errors, retained ABC membership and successful lower cleanup. The supplied local reports and UI-Q0–UI-Q4 index support that account: they distinguish the original admission UUID from the missing website receipt, retain unchanged refs, and do not infer an HTTP status, internal cause or cancellation contract.

The delivered source mapping does not yet carry that evidence. Candidate line 286 pins the follow-up snapshot to `97b993efdda40a1cbe690d317e436e32937adb85`, and line 305 directs readers to [queue issue #519](https://github.com/joshlf/gherrit/issues/519). At review time:

1. The repository and pinned follow-up directory were accessible.
2. Exact lookups of `followup-2026-11-08/ui/QUEUE-BROWSER-RESULTS.md` and `followup-2026-11-08/queue/ui-removal/RESULTS-UI.md` at that pin both returned GitHub API 404.
3. Issue #519, last updated `2026-11-09T05:28:30Z`, still described the extension as “prepared but unadmitted, with login pending” and said it contributed no removal result.

This is a reproducible C7 evidence/publication mapping defect, not evidence that the observed UI facts are false. It also matters to C8's reusable-evidence handoff: an external reader cannot recover the new result from the identified snapshot, and the linked issue contradicts the candidate's newer account.

The narrow repair is to publish the already-retained UI reports/index and their necessary evidence, identify the resulting immutable source, and link that source at the new UI claim. Update or explicitly supersede the issue's old fixture-status statement. Keep the original 130-ID/five-index snapshot count scoped to that original snapshot; the five UI extension IDs should not silently become part of its count. No new experiment or semantic model change is needed. If publication is deferred, label the latest result as local evidence and provide its local source identity in the local handoff.

**Falsifier:** this finding is discharged by a readable immutable source containing the actual UI-Q0–UI-Q4 evidence, connected from the deliverable, together with a noncontradictory explanation of the earlier issue status. Another finite queue read would not address it.

## Preservation and useful scope

| Obligation | Comparison with the baseline |
| --- | --- |
| C1: local authorship | The same one-commit linear first path, captured committed input and explicit continuation selection remain. Expanded importer tests do not silently authorize multi-commit message/history preservation. |
| C2: identity and archives | Canonical PR continuity, explicit repository/change/head binding, immutable archive targets and historical patch boundaries remain. The added operation-identity and completed-result checks reinforce that separation. |
| C3: responsibility | Native membership and landing remain GitHub's responsibility; prose/readiness remain human-owned after creation. The local owner requirement sharpens cooperating-process control without claiming to fence GitHub or another clone. |
| C4: partial/unknown effects | Separate dispatch evidence, actual hosted outcomes and incorporated local ranges remain. The explicit treatment of 5xx responses prevents an error response from being mistaken for a no-effect rejection. |
| C5: repeated work | F-before-surviving-B insertion, partial/completed groups, structural operations, adoption and the named unsupported histories remain covered as design paths or restrictions. The surviving-suffix handoff is still unresolved; the candidate explicitly limits the result to a pilot at that boundary. |
| C6: total burden | The candidate adds concrete enforcement and result-validation work, while reusing the existing evidence roles and importer. It does not demonstrate lower total cost, a new supported deployment domain or a second recovery architecture. |
| C7: claim support | The transport and local recovery additions inspected have discriminating evidence and appropriately bounded claims. The new UI facts need the source-mapping repair above. Other follow-up claims were not independently re-audited here. |
| C8: migration | New-work-first enrollment, scoped old-writer exclusion, retained custody and explicit rollback/handoff remain. None becomes production-ready merely because the follow-up matrix completed. |

The handoff limitation is shared by the baseline and candidate. It supplies no comparative reason to revert to the baseline, but it still prevents treating either document as a completed native-workflow replacement. The candidate's opening proposal and implementation sequence are usable as a qualified direction, provided the explicit pilot and production gates remain attached.

## Discriminating traces and their limits

**Stale worker dispatch.** The pinned [local results](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/97b993efdda40a1cbe690d317e436e32937adb85/followup-2026-11-08/local/RESULTS.md) record L28: two processes cache `planned`; the first completes; the second resumes; the serialized emulator records two requests. Candidate line 59 requires a real owner across admission/dispatch and reloading under that owner. Applying that rule means the resumed process sees the completed/unknown live operation and cannot dispatch using its cached `planned` state. Direct-worker, recovery and transfer entry paths cannot bypass this boundary. This is a concrete repair of the baseline's less explicit coordination rule. It is a design argument; the unchanged failing worker has not been repaired or retested by this review.

**Missing or mismatched evidence and completed results.** L14 records a direct worker recreating intent after deletion of the operation record; L29 records a manifest naming X with completion evidence for Y; L13 records deleted continuation/checkpoint data still permitting admission after completion. Candidate line 89 forbids each admission path and requires actual retained output or a validated successor attachment. A control must also permit legitimate ordinary authoring: complete at A, amend the working continuation to B, retain A's historical result, then capture/accept B's mapping and attach it before a new effect. Requiring the current tip to equal A forever would violate the candidate's own rule. These are focused implementation falsifiers, not evidence that the proposed checks already exist.

**Received server error with an actual effect.** The pinned [protocol results](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/97b993efdda40a1cbe690d317e436e32937adb85/followup-2026-11-08/protocol/RESULTS.md) retain actual 504/502 responses with the intended groups present, plus a retained blind-retry deviation. Candidate line 136 now makes the response/effect distinction explicit. Its additional words do not create another outcome concept; they constrain when the existing rejected/indeterminate distinction may be used. Fresh sole-controller positive attribution can explain the observed group, while absence cannot discharge a delayed write. Nothing here supplies future suffix-write settlement.

**Attempted reductions that lose a required observation.** One “current revision” cannot represent archived `x=0`, incorporated hosted `x=1`, and accepted local `x=1,y=1` before the next hosted `x=2` import. One native-success flag cannot represent an admission receipt that remains `enqueued` after a later manual dequeue. These counterexamples preserve the need for the existing semantic distinctions; neither the follow-up nor storage consolidation removes them.

## Burden accounting and a constructive reduction boundary

Relative to leaving the baseline unchanged, candidate 003 requires an actual local owner, live operation identity checks at every effect path, retained-result validation, successor attachment and correct error classification. Those are implementation, testing and recovery costs. Leaving the baseline unchanged retains the demonstrated stale-worker/direct-worker/result-validation gaps; it is not a cost-free safe alternative.

The candidate permits a useful implementation reduction without changing the model: normal publication, direct worker, recovery and transferred custody can all enter one guarded effect boundary. Transfer supplies retained custody evidence to that same boundary rather than maintaining a second mutable “eligible” authority. Pending/completed permission is derived from the identified operation, its effect evidence and validated accepted result, rather than from an independently trusted completion flag. The L14/L28/L29 traces show why this removes duplicated admission authority. Local storage may be one record or several; neither layout removes the distinctions needed by the range importer or external uncertainty.

This reduction is an allowed realization, not a measured saving or a reason to introduce a general workflow framework. Per-effect reconciliation, archive allocation, destination ownership, history-comment delivery, continuation selection, CI eligibility, migration and provider handoff remain. A service inherits the provider uncertainty and adds deployment work; a CLI adapter retains archive coupling and its observed side effects. Human author/reviewer burden remains unmeasured. No supportable scope extension or further independent semantic reduction was established by this bounded review.

The full `model-refinement` and execution guidance, and the fixed C1–C8 contract, were reread after substantive review. Root retains comparative adjudication, any successor pass, stopping and publication decisions.

*Authored by an AI agent acting on joshlf's behalf.*
