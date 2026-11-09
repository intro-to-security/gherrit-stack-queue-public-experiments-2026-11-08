# Independent follow-up evidence audit

The audited queue, local recovery, structural restart and selected CI claims are supported within their stated premises after one report correction. The original Q06 summary overstated how long the settled ALLGREEN states were observed. Root corrected that wording without changing raw evidence or rerunning the fixture. No further concrete contradiction was found in the decisive evidence inspected here.

This is an evidence audit, not a design review or convergence vote. It reads the follow-up plan, coordination profile, lane results/matrices and decisive retained JSON/source. It does not assess sealed refinement materials. All additional operations were local reads, Git object/diff reads and writes to this audit directory; there were no hosted calls or new experiment runs. [CHECKS.json](CHECKS.json) records independent recomputations and input hashes. Its timestamp marks this audit snapshot; protocol boundary execution was still active and is excluded from this terminal assessment.

## Queue discriminators

Q03's changed SQUASH conclusion is supported by actual delivered candidates, rather than the configured build limit alone. The captured rule readbacks match the per-case state and require only `queue-observe` from Actions App 15368, with no bypass actors and no synthetic release status. The selected-upper admission SHA matches each original B head.

| Case | Actual successful merge-group runs | Final native outcome |
| --- | --- | --- |
| SQUASH / HEADGREEN / build 1, #50/#51 | 42556303394, lower only | A merged; B open, removed for `invalid_merge_commit`, source rewritten |
| SQUASH / ALLGREEN / build 2, #53/#54 | 42556313375 and 42556315147 | Both merged from the original admission |
| SQUASH / HEADGREEN / build 2, #56/#57 | 42556324829 and 42556326159 | Both merged from the original admission |
| REBASE / ALLGREEN / build 2, #62/#63 | 42556501743, lower only | A merged; B open, removed for `invalid_merge_commit`, source rewritten |

For these runs, raw `event.json` candidate heads match `context.json` checkout heads. Independent Git reads confirm each candidate has exactly the recorded single parent; both SQUASH/build-two traces form trunk → A-candidate → B-candidate. The retained final lifecycle/timeline reads support the outcomes above. The reused SQUASH/ALLGREEN/build-one `frozen-summary.json` also records the Actions-only rule, lower landing, upper ejection and native rewrite. These traces support a configuration-dependent observation; they do not isolate GitHub's internal cause or establish a reliable workaround.

Q06 uses a separate required manual gate and must retain that qualification: A/C candidate statuses were successful and B's exact candidate status failed; all three real Actions checks also succeeded. HEADGREEN subsequently landed all three. The ALLGREEN watch initially sampled `AWAITING_CHECKS`; its first A/C `MERGEABLE`, B `UNMERGEABLE` sample began at 03:26:14.507287 UTC, and its final watch sample ended at 03:26:37.843881. Thus the settled samples span about 23 seconds, while the observer budget was 45 seconds. The revised [queue report](../../queue/RESULTS.md) and [correction record](../../queue/CLAIM-CORRECTIONS.md) now state this accurately and avoid a continuous-observation or indefinite-blocking claim. Explicit cleanup prevents inferring ALLGREEN's later outcome.

## Local failure traces

The five model failures remain visible in both prose and the per-ID matrix. Grouped driver `passed` counts describe successful probes, including probes that expose a failure; they are not a correctness score for the model.

- L13's retained JSON shows worker exit 0 and cooperative admission eligibility after deleting either the completed continuation ref or checkpoint. The unchanged worker only validates these results while `acknowledged`, then returns completion for an existing `complete` record.
- L14 preserves separate admission refusal for missing `operation.json`, followed by a direct worker invocation that recreates intent and changes the emulator request count from one to two. This challenges the worker boundary, rather than disproving the separate checklist's refusal.
- L16 preserves both shared-temporary/ref exceptions and an earlier final store containing two requests. The report correctly warns that racing store updates can undercount effects.
- L28's two real processes cache `planned` before release. The stale process waits for the first process's completion, so the retained two-request provider store does not depend on a simultaneous lost update. Both processes exit 0. The scheduling wrapper changes the read timing, while the tested worker remains unchanged.
- L29's manifest names `fixture-operation-complete` while the record ID is `different-operation-not-in-manifest`; admission still returns mutation authority. Its evidence records zero dispatches, so this is an admission-binding failure, not an observed foreign write.

The raw traces and [worker source](../../local/baseline-harness.py) support the [local report's](../../local/RESULTS.md) distinction between prototype failures and production behavior. Deleted evidence, stale concurrent workers and a foreign record deliberately challenge damaged-evidence or one-cooperating-writer premises. They do not show ordinary SIGKILL losing a successfully fsynced file. Fsync-error probes likewise distinguish old/new visibility from power-loss durability.

## Structural restart evidence

All ten initial process records show exit `-9`, a persisted selected boundary and distinct recovery PIDs. Source inspection confirms the controller waits for process death before starting recovery. The selected boundary is saved after a received receipt and live verification, followed by SIGSTOP and controller SIGKILL. These are actual process deaths after acknowledgement, with the after-ack limitation prominent in the report.

Independent checks matched each positive recovery's initial receipt prefix and remaining dispatch timestamps. S07 and S09 resume at their full effect counts and add no structural dispatch; S08 resumes beyond D creation. Receipt reuse and refusal of an unreceipted intent are enforced by the inspected executor. S10's two refusals retain only its original unstack structural intent. This supports no repeated executor effects in these recorded single-writer traces; it supplies no cross-clone exclusion or provider settlement guarantee.

The independent recomputation found 32 canonical PR identities, 117 raw mutation intents with receipts, 30 v1 archives and 29 published v2 archives. Retained final readbacks satisfy original node identity, exact archive targets, open/unmerged lifecycle and one expected PR per exact head. All 30 ABC old/new patches were independently regenerated from Git objects and matched each other and the saved patch bytes, including S10's unpublished proposal. Executor hashes match the pre-campaign source record. The existing successful fsck result establishes object integrity only. The report correctly excludes dependent-code validity, arbitrary writers, power loss and unknown in-flight outcomes.

## CI gates and matched review control

FC05/FC06 snapshots keep the same source and candidate SHAs throughout. Successful manual source statuses make both gates CLEAN; an upper candidate failure makes upper BLOCKED; candidate success restores CLEAN. Restricting the same required context to App 15368 blocks the manual producer, and restoring its unbound form restores CLEAN. This supports the event/SHA/producer distinction without treating a synthetic status as an actual test run.

RL01's deployment-only ruleset has no bypass actors. Deployment IDs 7646813146/7646813697 bind lower/upper source heads, while 7646815987 binds the captured upper candidate through its own ref. Raw status-list readbacks and PR snapshots support the reported grid: upper CLEAN with head success/candidate failure and with head failure/candidate success, BLOCKED with both failure, then CLEAN after restored head success. All source/candidate identities remain unchanged across that grid. This is bounded gate behavior for the tested configuration, not deployment safety or a universal head/candidate rule.

The final MR01 extension strengthens the review discriminator. Its three fixtures use identical trunk/lower/upper objects, bot PR authors and joshlf reviews. Exact protections differ as reported: stale dismissal true with CODEOWNERS false/true dismisses reviews 5821674287/5821675153, both citing changed merge-base; stale dismissal false/CODEOWNERS false retains review 5821676170 and rebinds it to the replacement. All lower requests merged. Independent Git reads confirm upper patch and tree equality in every fixture. Baseline review decisions were APPROVED, while overall gate snapshots were UNSTABLE; the final report accurately claims approval rather than an initially CLEAN gate. These finite matched traces narrow the earlier confounding but do not establish an internal algorithm.

The CI report's website-rebase and human-study gaps remain explicit. Prepared fixtures, machine identities and automatic prefix behavior do not count as those unperformed observations. The final inspected CI matrix contains 31 dispositions; this audit did not independently re-audit every reused CI control or claim terminal protocol coverage.

*Authored by an AI agent acting on joshlf's behalf.*
