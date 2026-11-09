# Coverage audit of the 19 open questions

Audit snapshot: **2026-11-09 04:13 UTC**. This maps the questions in their original
order from
[OPEN-QUESTIONS-BY-RESOLUTION.md](../../../outputs/github-native-stack-design-2026-11-08/post-experiment-refinement/OPEN-QUESTIONS-BY-RESOLUTION.md).
It is a read-only evidence audit, not a new experiment or a completion claim.
No sealed prior or new swarm material was opened.

**E** = executed follow-up; **R** = retained earlier evidence; **P** = new work
pending; **U** = unavailable premise/authority. A prototype failure is an executed
finding, not a passing product guarantee. Pending rows must be reconciled with
final lane readbacks before publication.

Sources: [Q: queue plan/results](../queue/RESULTS.md),
[C: CI/review plan/results](../ci-reviews/RESULTS.md),
[L: local matrix](../local/CASE-MATRIX.md),
[P: new protocol plan](../protocol/PLAN.md),
[A: prior API/structural results](../../native-stacks-2026-11-08/api/RESULTS.md),
[I: prior connected importer](../../native-stacks-2026-11-08/local-git/hosted-integration/RESULTS.md),
[H: prior CLI/history](../../native-stacks-2026-11-08/cli-history/RESULTS.md),
[HC: actual programmed concurrent history writes](../../native-stacks-2026-11-08/cli-history/CONCURRENT-HISTORY.md).
The current C matrix/report predates the resumed bot/UI/deployment work; the
updated plan, live state and worker handoff establish **pending**, not completion.
Protocol has a persisted plan but no result yet. Root UI has no completed artifact
in `ui/` at this snapshot.

| # / question | Executed, reused, pending or unavailable evidence | What still discriminates now |
| --- | --- | --- |
| 1. Safe suffix rewrite and sufficiently current reads | **R:** I/A retain terminal-receipt versus PR/ref disagreement. **E:** Q separates receipt, membership, candidates and source refs; L20–21 refute equal-ref/ABA ownership assumptions. **P:** P-T07 loses the async response before HTTP read. | Finish the assigned transport case. No finite quiet sample or boundary case supplies provider settlement; retain the contract/redesign boundary. |
| 2. Resolve genuinely unknown writes | **R:** A after-ack client kills and conservative unstack stop. **E:** L13/14/16/28/29 expose completion, missing-record, duplicate-worker and identity gaps. **P:** P-T01–08 cut a real TLS exchange before any HTTP response read for PR/comment/base/create/append/unstack/merge, with truncated-send control. | Finish P-T cases and keep client unknown decisions separate from the independent oracle. Old after-ack injection does not substitute for them. Positive observations still do not imply general exactly-once retry. |
| 3. Pending cancellation and upper admitted removal | **E:** Q01 confirms upper/middle API routing rejection after membership; lower removal clears dependencies. Q02 immediate lower removal fails while admission later becomes enqueued. | An actual website upper/middle removal is still discriminating because API rejection does not establish UI behavior. Pending cancellation remains unestablished even if a UI removal succeeds after admission. |
| 4. Queue methods/settings/oversized groups | **E/R:** complete 3×2×2 Q03 matrix; Q04 fresh and occupied below/equal/above-buffer controls; Q05–09 prefix, strategy/failure, independent stacks, trunk and explicit re-admission. SQUASH/build2 differs from build1; REBASE still ejects upper. | No further broad matrix is justified now. Retain contradictory documentation and absence of transaction IDs; trace success is not a supported-configuration contract. |
| 5. Approval retention and replacement signatures | **R:** RV04–06/SG01/SG05 retain hinted/unhinted/substantive/native-method controls. **E:** SG02 multi-commit selected-signature gates and SG03 mixed suffix verification. **P:** actual website RV01–03/SG04 and separate direct last-push/CODEOWNERS RV07–08. | Finish the existing distinct-actor rule controls and actual website button. Bot/user machine roles test provider rules, not human review or signing usability. |
| 6. First CI and rule/check combinations | **R:** FC01–04 initial/stacked/synchronize/dispatch. **E:** FC05–06 source/candidate/producer, FC08 real push route, RL02 actual CodeQL negative/positive/rewrite gates, MD01–02 metadata. **P:** RL01 exact-head versus candidate deployment control. **U currently:** FC07 own-ref target variants lack a default-branch trigger; root prerequisite proposal is pending. | Complete RL01. If root supplies the minimal default-branch prerequisite, run one positive FC07 control; otherwise keep its precise unavailability. Existing push/stacked alternatives already prevent first CI from depending on FC07. |
| 7. Website intent/result evidence | **P:** root browser receipt/rebase/landing work; C reserves four untouched website fixtures. API receipt tests are **R**, not website observations. | Capture actual available controls, initiating intent, completion feedback and independent result. Do not infer REST UUID/expected-SHA semantics from the button. |
| 8. Identity/adoption/destination/archive enforcement | **E:** L17–25 cover atomicity, leases, ABA, exact destination/dry-run and pinned adapter identity rejects; all owned archives read back in Q. **R:** A/H atomic archives and canonical review identities. **P:** P-B03–05 duplicate/order/base/closed/deleted-head boundaries. | Finish those already assigned native controls. Production adoption/enforcement remains outside this experiment's scope; do not invent a production migration merely to test the selected obligations. |
| 9. Repeated range integration/layer ownership | **E:** L01–08: baseline 122 assertions, 18 repeated changing-parent rounds, no-ops, multi-commit ranges, modes/rename/deletion/binary, conflicts/reset/revert and message bytes. **R:** I actual two-cycle F-before-B/canonical-B workflow. | No further general importer fixture is needed now. Keep manual mapping, flattened group semantics, local signing choices and unimplemented production enforcement explicit. |
| 10. Journals/checkpoints/transfer/adoption/rollback | **E:** L10–16/28–30 moving source/workspace, eight operation SIGKILL states, seven journal SIGKILL prefixes, missing evidence/custody, stale duplicates and fsync failures; several model failures. **P:** genuine transport P-T cases. **U:** real device/machine power loss and enforced exclusion of arbitrary legacy writers. | Feed the concrete gaps into refinement. SIGKILL leaves caches alive; post-rename fsync failure can leave visible new data. Do not label these as power-loss validation or an implemented owner fence. |
| 11. Structural canonical-review preservation and partial recovery | **R:** A safe release→park→refs→bases→register sequences and omitted-parking lifecycle failure; I F-before-B preserves canonical B. **P:** P-R01 explicitly reuses these; P-T03–06 add unknown individual base/membership effects. | No new interrupted structural-prefix resume/custody test is presently assigned. One bounded prototype-prefix restart is useful only if the final claim includes automated recovery across that sequence; successful old execution plus local continuation recovery does not establish it. |
| 12. Safety/availability promise without strong handoff | **E/R:** Q/A/I show concrete native failures/observation limits; L adds recovery refusals and failures. **P:** assigned transport cases and next refinement. | Evidence can narrow feasible promises. Acceptable refusal/manual recovery versus automation remains a requirements choice; no added API experiment can supply that preference or a missing contract. |
| 13. Automatic versus explicit re-admission | **E:** Q09 captures native rewrite/ejection, fresh CLEAN head and separate explicitly new request/UUID that lands canonical B. **R:** earlier corroboration. **U:** human surprise/error/effort measurements. | Already sufficient to refine the explicit-intent policy. Do not infer automatic permission from successful explicit re-admission or fabricate a human preference study. |
| 14. Merge methods/richer authoring first-release scope | **E:** Q method/configuration/size interactions and L multi-commit/mode/rename/binary cases. **P:** P-B00–05 actual min/99/100/101 create/append/order/lifecycle boundaries. **U:** demand/priorities and undefined shared-prefix/merge-history mapping policy. | Finish the assigned boundary tests. More cases with undefined intended mapping would not distinguish correctness; cross-fork or service builds are not required to close this campaign. |
| 15. Explicit commands or hook | **E:** L23 outer dry-run/unrelated/deletion publishes through independent hook; L24 exact captured source/destination with no dry-run dispatch. **R:** prior equal captured hook-input control. **U:** actual author error rates. | The technical discriminator is covered. Root's agent walkthrough may reveal interface issues but cannot establish human comprehension or preference. |
| 16. Direct API or constrained CLI | **E:** L25–26 pinned binary/parser, 15 adapter inputs, local startup samples and exact source hashes. **R:** H live URL/base/readiness/numeric/branch-only-submit effects and lost subprocess success. **P:** P-T transport effects inform required accounting for either choice. | No broader CLI delegation or API rewrite is needed. Local 12–13 ms help cost excludes network/validation/maintenance; remaining priority tradeoffs stay explicit. |
| 17. One publisher or service/multiple publishers | **E:** L16/28 duplicate dispatch and L17–21 atomic/equal-ref/ABA controls. **R:** custody unknown guard. **U:** collaboration demand, operational ownership and service availability trials. | Retain one cooperating publisher as a scoped premise and expose its unimplemented enforcement. Building a service is not necessary to demonstrate why overlapping writers require a stronger protocol. |
| 18. Mapping acceptance/fresh continuation usability | **E:** L08/10 ordinary authoring and dirty/staged/untracked/moving-source protection; explicit continuation and collision controls. **R:** I retained amendments and no-pending/pending acceptance. **U:** independent human author walkthroughs. | Root may execute a reproducible agent walkthrough. Human error/comprehension evidence remains unavailable under the no-recruitment authority; do not call the agent a human trial. |
| 19. Owned history comment versus separate reviewer view | **R:** H deletion/reattachment/identity/size/pinning and exact historical ranges; HC real overlapping programmed PATCHes preserve separate artifacts and stale whole-body control loses text. **E:** L22 changed-parent range comparison. **P:** root browser discovery/rendering inspection. **U:** independent reviewer/permission roles and human long-discussion comprehension. | A bounded browser inspection of history discovery and exact old patches still discriminates UI feasibility. Repeating API storage/size tests adds little; a separate history site is not required for this experiment. |

## Remaining work worth executing now

1. Finish assigned **P-T/P-B**, **RV01–03/SG04**, **RV07–08** and **RL01** cases,
   with their actual native readbacks and cleanup. They close distinct transport,
   boundary, website, review-rule and deployment premises.
2. Root browser: inspect actual receipt/rebase/landing feedback, the history
   access path and, if a held fixture can be supplied within existing allocation,
   upper/middle queue removal. These are agent-operated UI observations.
3. Root may supply the proposed default-branch FC07 prerequisite for one positive
   target-event control. Until then retain **unavailable-prerequisite**; the
   own-ref negatives are not a positive/negative conclusion about event support.
4. If refinement retains an automatic structural-resume claim, add one small
   restart/custody test across the existing sequence using retained exact intent
   and identities. Otherwise report that recovery boundary without requiring a
   new production implementation. The current protocol plan reuses the old
   structural sequence rather than testing every restart prefix.

No further queue Cartesian product, importer expansion, service build, separate
history site, global installation or production migration is needed merely to
make this campaign complete. Humans, machine power loss, a permanent provider
handoff contract and priorities remain honestly unavailable or unresolved.

Before canonical integration, replace stale C summary/matrix dispositions with
its completed continuation records, reconcile protocol unknown outcomes without
retries, confirm temporary bot/environment/rule restoration and final queue
state, then publish exact readback and perform the requested new refinement.
This audit neither performs those coordinator actions nor marks them complete.

*Authored by an AI agent acting on joshlf's behalf.*
