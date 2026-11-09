# Final experiment coverage of the 19 open questions

Evidence snapshot: **2026-11-09 05:37 UTC**, after authenticated queue cleanup. This maps the questions, in their
original order, from
[OPEN-QUESTIONS-BY-RESOLUTION.md](https://github.com/joshlf/gherrit/issues/518).
It supersedes the pending-work dispositions in [COVERAGE-AUDIT.md](COVERAGE-AUDIT.md)
without changing that earlier snapshot. It is a coverage account, not a design
refinement, a production implementation claim or a provider contract.

The completed campaign supplies the distinct transport, structural restart,
review/signature, first-CI and browser-history observations missing from the
earlier audit. It also exposes concrete recovery-model failures. The main
remaining empirical gaps include independent human author/reviewer comprehension.
The authenticated website-removal contrast is now performed with observed errors
and independently verified cleanup. Neither more quiet reads nor repeated
passing fixtures can supply a missing provider settlement guarantee.

## Evidence scope and counting

The five lane indexes contain **130 case IDs/dispositions**:

| Lane | Indexed IDs | What the count includes |
| --- | ---: | --- |
| [Q: queue](../queue/RESULTS.md), [index](../queue/case-matrix.json) | 32 | 25 performed and 7 reused dispositions; several IDs belong to one fixture or method matrix. |
| [C: CI/reviews](../ci-reviews/RESULTS.md), [index](../ci-reviews/matrix.json) | 31 | 22 performed and 9 reused dispositions; one ID can contain several controls or fixture variants. |
| [L: local](../local/RESULTS.md), [index](../local/CASE-MATRIX.md) | 30 | Reused/baseline checks, grouped probes, five model failures and the unavailable L27 are all indexed. |
| [P: protocol](../protocol/RESULTS.md), [index](../protocol/matrix.json) | 26 | 24 performed, one failed capacity premise replaced by a fresh case, and one reused-evidence disposition. |
| [S: structure](../structure/RESULTS.md), [index](../structure/CASE-MATRIX.md) | 11 | Nine positive recovery runs and two refusal runs on ten fixtures. |

**130 does not mean 130 successful experiments, independent trials, new hosted
effects, or closed questions.** The 122 baseline local assertions, 16 deliberate
transport cuts and multiple controls within a case use different units. The
browser-history walkthrough and prepared queue-removal extension are separate
records; they do not expand this count into a success total.

The independent [final audit](../audit/REPORT-FINAL.md) checked decisive terminal
protocol evidence and four website-rebase outcomes, while the unchanged [earlier audit](../audit/REPORT.md)
includes structural recomputations. Their scope is narrower than independent
reperformance of every lane case. The protocol report retains its blind-retry
deviation, contaminated capacity attempts, source correction and incompatible
clock-record correction; none is erased by the terminal dispositions. The
corrected observed minimum UTC dispatch separation is 2.942764 seconds with
uncalibrated wall-clock accuracy, not a calibrated service timing result.

In the map below, **observed** means a retained finite trace or local prototype
result; **documented** means a cited provider/API description. Reuse retains
the original trace's qualifications. A selected GHerrit obligation is a design
requirement, not evidence that production enforces it. Further checks listed
below are candidates, not experiments performed for this account.

Reused sources are the prior [API/structural report](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/ade319107e71b6eff646a1574139e2c15486fe6d/api/RESULTS.md),
[hosted importer](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/ade319107e71b6eff646a1574139e2c15486fe6d/local-git/hosted-integration/RESULTS.md),
[CLI/history report](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/ade319107e71b6eff646a1574139e2c15486fe6d/cli-history/RESULTS.md) and
[programmed concurrent-history writes](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/ade319107e71b6eff646a1574139e2c15486fe6d/cli-history/CONCURRENT-HISTORY.md).
The current lane indexes bind reused cases to their original evidence paths.

## 1. When may GHerrit safely rewrite a surviving suffix after native work, and which reads are sufficiently current?

**Ground truth.** Q retains admission receipts separately from membership,
candidates, lifecycle and source refs. P-T07-H500 observes a merge without a known
initiating UUID/status. Prior API/hosted-integration traces retain terminal-receipt
versus ref/PR disagreement; L20–21 show that equal refs and ABA do not establish
exclusive ownership or a generation. S's after-ack recoveries assume no known
landing/admission work rather than proving that assumption from quiet reads.

**Reliance and residue.** These are observations, not a documented provider
settlement fence or cross-resource snapshot. The safe handoff premise remains
missing. This is a technical guarantee/design question, not a preference.

**Further check.** Test a concrete proposed protocol against delayed writes and
stale observations, or obtain a provider contract that supplies its exact needed
ordering. Repeating coherent reads or successful suffix imports cannot prove
that no delayed native write remains.

## 2. How can genuinely unknown writes be resolved or safely retried, including PR/comment creation and membership/base edits?

**Ground truth.** P-T01–08 and their fresh H500 variants deliberately send once
and read no HTTP response; all 16 decisions retain unknown effects and prohibit
retry/overlap before oracle reads. H500 finds exact fresh PR/comment/base/create/
append/unstack effects; P-T07-H500 finds both merged PRs and the expected trunk
tree. Immediate-close and truncated samples establish only bounded absence.
P-T09 is an acknowledged transport control. Independent 99-/100-member creates
return 504/502 while creating the intended groups. The original boundary
harness's blind semantic retry is a retained plan violation; contaminated 422s
are excluded. L14/L28/L29 expose missing-evidence replay, stale duplicate dispatch
and identity-binding failures in a separate local prototype.

**Reliance and residue.** Fresh identities and a sole controller make effects
attributable in these fixtures. They supply no documented idempotency,
exactly-once semantics, field ownership or general permission to retry. Safe
stopping is demonstrated locally; complete production reconciliation is not.

**Further check.** Validate each implemented reconciliation rule, ambiguous
ownership/refusal and lost evidence at its actual dispatch boundary. A stronger
automatic-retry promise needs supported semantics or a demonstrated protocol;
more successful no-read requests cannot establish it.

## 3. Can pending admission be cancelled, and what does removing an upper admitted member do?

**Ground truth.** Q01-C/B fail after confirmed ABC membership because the API
routes to each member's direct parent rather than the trunk. Q01-A removes the
whole admitted native stack. In q02-pending-lower, immediate lower removal fails,
the original admission remains pending and later enqueues both members; confirmed
lower cleanup then succeeds. The [website extension](../queue/ui-removal/RESULTS-UI.md) is now performed. After the user signed in, root actually confirmed Remove from queue on upper C #122 and middle B #121. Each page returned visible “Not Found”; independent API/Git reads after each retained all ABC, open/unmerged lifecycle and exact source/trunk/archives. One authorized lower-A dequeue removed all three manually before timeout, leaving the queue empty. The browser exposed no initiating HTTP status or operation UUID.

**Reliance and residue.** The API routing failures and website errors are distinct observations; the visible text does not establish that they share an internal cause. No still-pending cancellation or future-write handoff follows. This answers what the tested website controls did, not what every future configuration promises.

**Further check.** Test a newly specified removal/cancellation contract or obtain provider semantics if the chosen workflow needs it. Repeating these errors is unnecessary without a discriminating support claim. Keep pending cancellation separate from removal after admission and authority for later ref edits.

## 4. What queue behavior is intended across merge methods and oversized groups?

**Ground truth.** Q03 covers the full 3×2×2 method/strategy/build-concurrency
matrix: MERGE lands AB in every tested cell; SQUASH lands AB at build two but
ejects B at build one; REBASE ejects B throughout. Q04 tests fresh stacks at
two/three/four members and occupied queues at/beyond the nominal buffer. The
above-buffer occupied trace lands X then intact ABC one second later, without a
transaction ID. Q05–09 cover prefixes, a failed candidate under two strategies,
independent work/stacks, trunk progress/conflict and explicit re-admission.

**Reliance and residue.** Observations narrow behavior but do not establish
configuration reliability or a permanent workaround. The cited merging and
troubleshooting documentation retain different oversized-group descriptions.
P's 100-member registration boundary is not evidence for 100-member queue or
landing behavior. Supported configuration selection remains a scope decision
after provider clarification.

**Further check.** A provider explanation or a narrowly specified supported
profile is useful. No further broad Cartesian product is justified by an
unchanged design claim; test a newly selected boundary only when it discriminates
that claim.

## 5. When do unchanged approvals survive, and when are replacement commits signed?

**Ground truth.** C-RV01–03/SG04 are all performed: the user attests actual
website Rebase stack, and independent API/Git reads verify eight changed heads,
unchanged own-layer patches/author/message, retained identities/membership and
open/unmerged lifecycle. RV01/RV03 retain counting approvals; RV02 retains
APPROVED records while the separate last-push gate remains REVIEW_REQUIRED.
All eight replacements verify: six sources were unsigned without required
signatures, two verified sources were under required signatures. SG02 checks
every selected multi-commit source; SG03's unprotected mixed suffix becomes
verified throughout. MR01 holds actors/source objects constant: both
stale-dismissal-enabled automatic-prefix cases dismiss the upper review,
regardless of CODEOWNERS; stale-disabled retains it. RV07–08 and prior RV04–06
retain complementary rule, actor, hinted and substantive-change controls.

**Reliance and residue.** These observed rule/path outcomes do not establish an
unconditional retention/signing contract or identify an internal algorithm.
Website initiation is human-attested, not a captured HTTP receipt. Actual review
decision, per-commit verification and preserved patch remain separate checks.
Acceptable review/signing friction is a product judgment.

**Further check.** Validate the exact repository support profile the product
chooses. No general rerun is needed to establish that website and automatic-prefix
paths differ. Human review/signing usability remains unmeasured.

## 6. What dependable first-CI route and rule/check combinations must each target repository support?

**Ground truth.** C-FC01–04 retain opened-before-membership, explicit `stacked`,
synchronize and ineffective branch-dispatch controls. FC05–06 distinguish source
head, candidate and required producer; a candidate failure can override a green
source status. FC08's real push checks make unchanged native heads CLEAN. FC07
now has a positive `pull_request_target` adoption control after root supplies its
default-branch workflow: upper `stacked` runs and becomes CLEAN. Environment SHA,
actual checkout and API/check association are retained separately. RL01 finds
successful source-head or existing-candidate deployment sufficient in its grid;
RL02 uses actual CodeQL negative, positive and rewritten-upper analyses. MD01
shows an `opened` artifact can already contain membership.

**Reliance and residue.** The Actions default-branch context is documented;
these exact trigger/gate/check bindings are observed. Explicit `stacked` activity
and candidate checkout qualifications remain. No tested route establishes every
rule combination or a cross-resource metadata snapshot. Temporary default-branch
workflow, rules/environment and bot flag were restored/read back.

**Further check.** Integrate and validate the selected target-repository profile,
including its actual producer and candidate. The earlier missing FC07 prerequisite
is closed; repeating its own-ref negatives would not answer a new question.

## 7. Can website operations supply enough retained intent and result evidence for the selected recovery promise?

**Ground truth.** The four actual website rebases have human-attested initiating
actions and independently verified effects, including exact pre/post refs,
rules, reviews, signing and membership. No initiating HTTP trace, operation UUID,
website feedback capture or website landing observation was retained. The
history browser walkthrough is a rendered-link check, not a landing receipt.

**Reliance and residue.** There is no demonstrated REST-equivalent website
receipt or expected-SHA contract. Actual effects support the four outcomes;
they do not by themselves supply recoverable intent or exclusion of later native
work. Website support may be omitted from an initial selected workflow.

**Further check.** If website initiation is supported, capture its available
intent/completion feedback and test interrupted recovery under an explicit
evidence contract. A missing receipt must remain missing rather than be inferred
from the API result or the user's successful action.

## 8. Are identity/adoption, destination/namespace checks and exact archive ownership correctly enforced?

**Ground truth.** L17–25 cover coupled atomic publication, value leases/equal
refs/ABA, exact captured source/destination, dry-run and 15 pinned-adapter identity
inputs. P-B03–05 reject duplicate/order/base/member/nonexistent/closed/deleted-head
boundaries with valid controls. S independently retains 32 expected canonical
PRs, all 30 original node IDs, exact v1/v2 archives and stale-state refusal.
C-HC02 shows a PR-write bot can edit a user-authored comment; HC04 exercises an
actual foreign duplicate marker and a locally simulated lost-ID lookup.

**Reliance and residue.** Native validation and finite exact archive checks are
observed; GHerrit adoption and ownership are selected client obligations, not
production enforcement or provider-exclusive edit authority. Equal values do not
establish unique publisher identity. Marker text alone does not establish artifact
ownership.

**Further check.** Validate production admission, adoption, namespace and archive
ownership at the real write boundary, including changed destinations and missing
custody. Another successful synthetic archive read cannot replace those checks.

## 9. Does range integration preserve each layer, local amendments, messages and signing decisions across repeated work?

**Ground truth.** L01–09 retain 122 baseline assertions, 18 changing-parent A/B
rounds, no-op trees, multi-commit net ranges, modes/rename/deletion/binary exact
objects, expected conflicts, reset/revert and local message bytes. The reused
hosted two-cycle F-before-B test preserves canonical B and verifies its executable
dependency. S adds exact patch preservation during independent-layer reorder and
insertion. L05 flattens an accepted multi-commit layer and preserves its local tip
message, not every intermediate identity/message.

**Reliance and residue.** These are algorithm/prototype observations. Mapping,
reset intent and signing choices remain explicit inputs. Production mapping,
arbitrary merge/shared-prefix policy, no-new-archive behavior and cryptographic
signing decisions are not implemented by these checks.

**Further check.** Validate the implemented mapping/conflict/signing contract.
No broader synthetic importer matrix is needed before there is a new invariant
or specified richer authoring case to distinguish.

## 10. Do journals, checkpoints, transfer, adoption and rollback survive interruption while retaining unknown effects?

**Ground truth.** L10–16/28–30 cover moving source/workspace, eight baseline
operation SIGKILL states, seven journal replacement prefixes, custody/missing
evidence, duplicate workers and fsync failures. L13/L14/L16/L28/L29 are actual
model failures: invalid completed results, replay after missing evidence,
concurrent/stale duplicate dispatch and unbound operation identity. S supplies
nine after-ack hosted restarts and missing-receipt/stale-head refusals. P supplies
genuine unacknowledged transport effects with pre-oracle unknown decisions.

**Reliance and residue.** Journal SIGKILL leaves caches alive; it is not machine
power-loss validation. Post-rename directory-fsync failure leaves new data visible.
The structural executor enforces its scoped evidence checks but assumes one
cooperating writer; it does not cure the separate local worker's failures or
exclude arbitrary legacy writers. Provider-owned pending work inherits #1–2.

**Further check.** Test corrected production dispatch/recovery admission and
completion validation, then cross-process ownership and custody transfer. Actual
power-loss testing needs a suitable environment. More ordinary SIGKILL passes
cannot close missing boundary enforcement or establish disk durability.

## 11. Can structural edits preserve canonical reviews and recover from partial effects?

**Ground truth.** S01–09 now directly restart fresh processes after acknowledged
unstack, both parking steps, atomic head/archive publication, final base steps,
registration and inserted-D creation. All nine recoveries dispatch only remaining
records; S07/S09 dispatch nothing further. S10a refuses a withheld receipt and
S10b a separately advanced head, without a new structural effect. Canonical PR
identities, archives and independent layer patches survive. Prior safe drop/fold/
trunk controls and the omitted-parking lifecycle hazard are reused; no new
interrupted drop/fold/trunk recovery is claimed.

**Reliance and residue.** This closes the earlier absence of a hosted structural
prefix-restart test for reorder/insertion. Crashes are after persisted receipt
and readback, not unknown in-flight outcomes. PR continuity is observed; approval
retention during these structural operations is not established. There is no
lifecycle transaction or provider handoff contract.

**Further check.** Test a selected production structural operation's actual
unknown-effect reconciliation and rule consequences. Extend interrupted tests
to another operation only if the supported promise includes that operation.

## 12. What safety/availability promise should the product make if a strong provider handoff cannot be established?

**Ground truth.** Q/P/prior hosted traces make native outcomes and unknown effects
concrete. L exposes refusal and recovery defects; S demonstrates bounded
after-ack continuation. None establishes a general provider settlement fence.

**Reliance and residue.** Correctness under a stated promise is technical;
acceptable refusal, manual recovery, automation and availability require an
explicit requirements choice. A replacement design must demonstrate its own
promise; a weaker promise cannot silently stand in for the selected one.

**Further check.** Compare concrete feasible protocols and test their claimed
invariants. Requirements discussion can choose among those promises. Further
quiet samples cannot supply either missing guarantee or user priorities.

## 13. Should rewritten/ejected work be re-admitted automatically or only after explicit author action?

**Ground truth.** Q09 records lower landing/upper ejection, a rewritten CLEAN
upper with no membership, then a separately explicit new exact-head admission
and UUID that lands canonical B. Original and renewed requests remain distinct.

**Reliance and residue.** This observes that explicit re-admission can work; it
does not establish inherited author permission, safe automatic re-admission,
settlement of the earlier operation or acceptable surprise. Intent/gate semantics
need design; automation level retains a product judgment.

**Further check.** Test a specified intent model and its revalidation against
changed checks, patch/head and review state; use real author walkthroughs to
measure surprise and effort. Repeating Q09 does not select the policy.

## 14. Which merge methods and richer authoring cases should the first release support?

**Ground truth.** Q establishes method/settings interactions and tested queue
size behavior. P-B00/P-B01/P-B01-F100/P-B02-F101 establish create minimums, successful observed
100-member registration and append-to-101 rejection retaining exactly 100;
99-/100-create server errors remain unknown writes despite observed membership.
L covers multi-commit net layers and varied Git objects; S covers independent
reorder/insertion. These do not validate arbitrary dependent-code reorder,
shared-prefix/merge-history mapping or native cross-fork capability.

**Reliance and residue.** P's pinned OpenAPI documents request-array bounds;
total observed capacity and queue behavior are separate. Technical feasibility
does not establish demand, maintenance budget or first-release priority. A client
scope exclusion is not evidence of a provider limitation.

**Further check.** Specify the intended mapping/support profile before new
correctness cases; discover user demand for optional cases. No 100-member landing
or cross-fork build is required merely to declare this bounded campaign's
existing experiments performed.

## 15. Explicit commands or a compatible hook?

**Ground truth.** L23 shows independent fixture-hook publication during outer
dry-run, unrelated-ref and deletion pushes; earlier identical captured dry-run/
real hook inputs remain reused. L24's explicit prototype makes no dry-run
dispatch and publishes exactly the captured SHA/destination after source movement.
Retained GHerrit source identifies the current hook's current-branch/configured-
remote behavior.

**Reliance and residue.** The technical destination/dry-run discriminator is
covered by observations. Explicit commands are a proposed starting point, not
measured human preference. Actual author error rates and acceptable interaction
style remain untested.

**Further check.** Use the prepared human author task to compare previews and
hook expectations on retained inputs. Another hook fixture cannot establish
human comprehension or make an incompatible outer-push contract adequate.

## 16. Direct APIs or a constrained official-CLI adapter?

**Ground truth.** L25–26 verify the pinned v0.3.0 binary digest/parser, 15 pure
adapter inputs and local help startup samples. Reused hosted CLI traces retain
base repair from canonical URLs, readiness effects before failure, broad submit's
missing GHerrit archives and lost subprocess success. P demonstrates unknown
effects that either publisher must account for.

**Reliance and residue.** Tested CLI/source versions and observed effects do
not establish a permanent adapter contract. The approximately 12–13 ms help
measurements exclude network, validation and maintenance. Direct APIs are the
proposed starting point; atomicity, recovery and version coupling remain
engineering constraints, while maintenance priorities require judgment.

**Further check.** Validate any actual narrow adapter against its supported
version and complete effect accounting. A broad CLI delegation prototype is not
required while that choice remains optional.

## 17. One publishing checkout or a service/multiple publishers?

**Ground truth.** L16/L28 produce duplicate dispatch without an enforced owner;
L17–21 distinguish coupled atomic refs from equal-value/ABA ownership. S works
under one cooperating structural publisher, and custody controls preserve unknown
effects only under their scoped admission model.

**Reliance and residue.** One cooperating publisher is a scoped premise,
not implemented cross-clone exclusion or a GitHub lifecycle guarantee. A service
would still inherit provider-owned outstanding effects. Collaboration demand,
operational ownership and availability requirements are unavailable here.

**Further check.** Validate a chosen ownership/exclusion mechanism with stale
processes and real custody transfer. Discover collaboration requirements before
building a service merely to resolve an architectural preference.

## 18. Is mapping acceptance and selecting fresh continuations usable for authors?

**Ground truth.** L08/L10 and reused hosted F-before-B work exercise supplied
mapping, accepted reset/revert, fresh continuation, occupied-name refusal and
dirty/staged/untracked/moving-source protection. The prepared
[H01 task](../ui/HUMAN-STUDY.md) has no completed independent participant result.

**Reliance and residue.** State preservation is observed; author understanding,
error rates and correct next-branch selection are not. Agent knowledge or a
passing technical oracle cannot substitute for comprehension. Acceptable friction
also depends on priorities after measured consequences.

**Further check.** Run H01 with an actual author, record answers/errors separately
from preference, and verify actions against retained source/workspace oracles.
No broader importer experiment is needed to ask that usability question.

## 19. Is the owned history comment an adequate reviewer interface, or is a separate view needed?

**Ground truth.** Reused CLI/history evidence covers deletion/reattachment,
identity, size, unsupported pinning and exact historical ranges. Prior programmed
overlapping writes and C-HC01 preserve independent comment/body payloads;
HC02–05 add real actor/token permissions, foreign edit capability and duplicate
marker handling. L22 separates exact base/tip ranges from parent drift. The
[actual browser walkthrough](../ui/HISTORY-BROWSER-RESULTS.md) finds rendered v1/v2
links: v1 exact patch shows only `history-change.txt`; tip-to-tip also shows
`history-trunk-drift.txt`. It is an informed, logged-out agent feasibility check.

**Reliance and residue.** PR-comment pinning is documented unsupported. Storage,
rendering and permission effects are observed, but exclusive history ownership
is a client policy; a sufficiently privileged bot can edit another actor's
comment. No naive reviewer, long-discussion discovery or human comparison-
comprehension result exists. Adequacy versus hosting cost retains a value judgment.

**Further check.** Complete H02 and, if needed, a fresh synthetic long-discussion
comparison with actual reviewers. A direct stable link can be tested without a
separate site. Repeating comment storage/size tests or agent link clicks would
not close the human question.

## What remains after the completed experiments

- **Website contrast completed:** actual signed-in upper/middle confirmations returned “Not Found”, with unchanged admitted membership after each; one lower cleanup then removed all three manually before timeout. Its result supplies no captured website HTTP status/UUID, internal routing cause, pending cancellation or provider handoff.
- **Human empirical gaps:** H01 author mapping/continuation and H02 reviewer
  history/changed-parent comprehension, plus any long-discussion discovery study.
  Four successful user-operated rebases are not those studies.
- **Engineering work:** production dispatch/admission/completion/identity checks,
  ownership enforcement, per-operation unknown reconciliation, mapping and the
  selected repository support profile. The exposed model failures need a design
  or implementation response, not relabeling as test success.
- **Missing provider premises:** settlement/handoff, current-enough cross-resource
  reads, general exactly-once recovery and pending cancellation where required.
  Experiments can falsify candidate protocols and bound observed behavior;
  repeated quiet runs cannot establish those guarantees.
- **Residual choices:** safety/availability promise, re-admission automation,
  release scope, acceptable friction and deployment/maintenance priorities after
  feasible consequences are specified. No empirical count decides these values.

This account adds no experiment, native write, external publication or refinement
verdict. No prior sealed holdout material was read. The earlier coverage audit
and evidence reports remain unchanged.

*Authored by an AI agent acting on joshlf's behalf.*
