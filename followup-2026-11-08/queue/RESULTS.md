# Native queue follow-up results

The expanded tests extend the earlier build-concurrency-one evidence: **SQUASH landed both native members when build concurrency was two, while its concurrency-one controls ejected the upper member.** MERGE landed both in every tested matrix cell. REBASE ejected the upper member in all tested cells, including concurrency two. These are observed configurations, not a claim about GitHub's internal cause or a permanent method guarantee.

The experiments used only new synthetic resources in [the authorized public repository](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08), under `exp/fu2/queue/**` and exact `gherrit-fu2-queue-*` rules. Existing fixtures, main, shared Actions workflow, repository merge-method settings and organization settings were unchanged. The plan preceded the first native mutation; recorded adjustments retain confounded attempts and observation-bound corrections.

## Method, strategy and build concurrency

Each fresh matrix fixture had two native members, one selected-upper async admission with its exact hosted head, only real Actions `queue-observe` required, no bypass actor and no synthetic status writes. Maximum merge entries was five; minimum one/wait one minute; timeout five minutes. All three methods were enabled in the repository. The full 3×2×2 matrix reuses the three prior ALLGREEN/concurrency-one controls and adds the other nine cells.

| Method | ALLGREEN / build 1 | HEADGREEN / build 1 | ALLGREEN / build 2 | HEADGREEN / build 2 |
| --- | --- | --- | --- | --- |
| MERGE | AB merged (reused) | AB merged | AB merged | AB merged |
| SQUASH | A merged; B ejected (reused) | A merged; B ejected | AB merged | AB merged |
| REBASE | A merged; B ejected (reused) | A merged; B ejected | A merged; B ejected | A merged; B ejected |

Every observed upper ejection in this table had reason `invalid_merge_commit`, followed by native source rewriting. The SQUASH/build-two fixtures delivered two successful real merge-group workflows, forming A-candidate → B-candidate single-parent chains, and both members landed from the original admission. REBASE/build-two delivered only the lower merge-group workflow before the upper ejection. Configured concurrency is a maximum; two builds did not actually run in those REBASE traces. Source identities, exact rule readbacks, candidate event/head/checkout/graph records, native removal events and final ref/patch comparisons are retained per case.

This narrows a product support decision: method alone is insufficient to describe the tested native queue behavior. Build concurrency and the candidates actually delivered also matter. One trace per cell does not establish a reliable workaround or a guaranteed supported configuration.

## Confirmed upper removal and pending cancellation

In a held ABC fixture, actual queue membership confirmed all three entries before each attempted removal. `dequeuePullRequest(C)` and then `dequeuePullRequest(B)` both returned `UNPROCESSABLE`: GitHub looked for a queue on each PR's direct parent branch rather than the stack trunk. The same calls failed after admission, so the earlier immediate-upper failure did not require a pending timing explanation. Dequeuing lower A succeeded and removed all ABC. All PRs remained open and source/archive refs were unchanged. This API trace does not establish what the website's upper-removal control does.

A separate pending contrast selected B and immediately attempted to dequeue lower A, with no intervening read. The admission returned 202 at `03:22:39.916Z`; the dequeue call envelope began at `03:22:39.919Z` and returned `Failed to remove PR #68`. The next original-UUID read still reported `pending`; a subsequent read ended at `03:22:43.319Z` with `enqueued`, and both members were observed queued. Confirmed lower cleanup then succeeded. API envelopes include the harness's 180 ms request pacing; the near-zero gap between envelopes is not an exact server dispatch interval.

Together, these tests distinguish a confirmed upper/middle API routing failure from a still-pending lower removal failure. The pending lower rejection did not stop its admission; the confirmed upper/middle rejections did not remove membership. They do not establish a general cancellation contract. Original UUIDs were also read after outcomes; admission status, actual membership, lifecycle and Git refs remain separate facts.

## Size boundaries and occupied queues

With MERGE/ALLGREEN, build four, maximum merge entries two, real Actions plus a manual candidate gate, fresh native stacks of two, three and four all landed every member after release. Within each fixture, all members had the same one-second `mergedAt` timestamp. The four-member fixture was above the nominal `2 × 1.5 = 3` buffer and was not ejected or visibly left as a suffix.

Two stronger controls placed an independent ordinary X ahead of the native stack. Both used minimum two/wait five minutes and held every exact candidate until real Actions passed; native candidates were released top-down and X last:

| Queue contents | Configured maximum / buffer | Observed landing |
| --- | --- | --- |
| X + native AB, total 3 | 2 / 3 | X, A and B all recorded `03:30:20Z`. |
| X + native ABC, total 4 | 2 / 3 | All four became MERGEABLE. After the batching wait, X recorded `03:35:47Z`; A/B/C each recorded `03:35:48Z`. |

The above-buffer trace exposes a boundary between X and the intact native stack. It is consistent with moving a stack that cannot fit to the next group as a unit. It does not expose a transaction ID or prove internal atomicity from matching timestamps. The [merging documentation](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests) describes a next-group single unit, while [troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-stacked-pull-requests) describes possible continuation across groups. These traces narrow the example without settling every size/configuration or the documentation conflict.

The ordinary 180-second observer would have cleaned the above-buffer fixture before its five-minute batching wait could expire. It was interrupted while sleeping, before cleanup, and the same already-admitted case received one bounded extension. No admission or status mutation was resent. This correction is retained in the plan and case state.

## Other discriminators

- **Partial prefix:** selected B in held ABC admitted only A/B. After their MERGE landing, C remained open and unqueued, with its original per-layer patch and exact authored archive retained.
- **Strategy with a failed candidate:** both ABC controls used build three, maximum five, minimum three/wait five minutes. All exact candidates passed real Actions. A and C received a successful required manual gate; B received failure. HEADGREEN landed ABC. ALLGREEN's 45-second observer initially reported AWAITING_CHECKS; later samples spanning about 23 seconds showed A/C MERGEABLE and B UNMERGEABLE before explicit cleanup. This establishes an observed strategy contrast; it does not claim continuous observation or that ALLGREEN would never eject or land later.
- **Independent work and two stacks:** the queue contained ordinary X, native AB and native CD on one trunk. Confirmed lower-A removal removed A/B while X/C/D remained queued. Subsequent explicit cleanup removed X and then C/D. A failed/removal dependency did not erase unrelated admitted work in this trace.
- **Advanced trunk:** after real source checks passed, an independent trunk advance admitted and MERGE-landed AB. An actual conflicting trunk change rejected admission with a merge-conflict/not-mergeable reason, leaving both PRs open and the queue empty. The clear fixture's first request was retained as confounded: it failed because source Actions were still running. A separately labeled known-new request after checks passed supplies the trunk result.
- **Explicit re-admission:** a fresh SQUASH/build-one fixture first landed A and ejected/rebased B. After observing B's actual new hosted head, CLEAN checks and no membership, one explicitly new request at that new head landed canonical B. The separate original and new UUIDs remain in evidence. This is a deliberate disposable-fixture continuation, not an automatic production re-admission policy or a provider handoff guarantee.

Real Actions-only merge-group failure/ejection, failing-upper source admission, queued exact-lease atomic source-edit rejection and terminal receipt persistence were reused from the earlier campaign. Each reused case names its original evidence and why it was not repeated in `case-matrix.json`.

## Evidence, cleanup and limits

The final readback from `2026-11-09T03:36:21.747133+00:00` to `2026-11-09T03:37:22.799096+00:00` covered 23 new fixture queues and 59 synthetic PRs. All queues were observed empty; all 59 exact authored archives matched; every raw per-layer patch was preserved; all final GraphQL heads matched independently fetched Git refs. There were no unresolved API/Git dispatch intents. All 168 listed follow-up workflow runs were completed. New rules are retained only on their exact synthetic fixture trunks, with no bypass actors. 32 case dispositions are indexed: 25 performed and 7 reused.

`case-matrix.json` enumerates every planned case and disposition, actual settings, PR identities, decisive receipts and evidence paths. `cases/*/state.json` retains UTC observation envelopes, queue/PR reads, original async receipts, Git-ref read intervals, removal events, rules and workflow runs. `evidence/` retains sanitized pre-dispatch intents and receipts; `cases/*/actions/` retains available real event/checkout/commit artifacts. `lab.py`, versioned runners, `run.py`, `audit.py` and `report.py` retain the source and corrections. The final Git store retains exact input and fetched native objects for independent patch verification.

Finite observations, coherent refs, an empty queue and terminal admission receipts do not prove that no later provider write remains. These experiments do not supply the missing production handoff contract, exactly-once recovery semantics, a general cancellation API, human usability evidence or a supported configuration guarantee. Provider clarification and an explicit GHerrit intent/recovery policy remain necessary where the design would otherwise depend on those premises.

*Authored by an AI agent acting on joshlf's behalf.*
