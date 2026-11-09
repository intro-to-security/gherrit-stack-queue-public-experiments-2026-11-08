# Candidate 003 provenance recheck

Execution: swarm-model-refinement. This is a read-only C7 follow-up to `review-003.md`, which remains unchanged. Candidate 003 still has SHA-256 `5b0c763bd6a706e88db644dd368013b2f95c7d3882a8ca79fb2febf487f6885f`. No model revision, sealed read, browser operation or native mutation was performed.

The delivery finding is resolved by the existing issue-to-immutable-evidence path. A further candidate edit is not required to satisfy that finding.

I independently fetched [GHerrit issue 519](https://github.com/joshlf/gherrit/issues/519) through the GitHub connector. Its returned body, updated at `2026-11-09T05:40:23Z`, describes the actual signed-in upper/middle `Not Found` results, independent retained ABC membership, one manual lower-A cleanup, unchanged refs, and the original admission UUID remaining `enqueued`. It explicitly withholds website HTTP status, initiating UUID, internal cause, successful upper/middle-removal semantics, pending cancellation and provider handoff.

The issue links these three reports at exact public commit `958470f1f185e5c84ca3f5664a3136b37391be5b`. Each independent fetch succeeded with substantive content:

| Immutable path under `followup-2026-11-08/` | Returned Git blob SHA | Content checked |
| --- | --- | --- |
| [ui/QUEUE-BROWSER-RESULTS.md](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/958470f1f185e5c84ca3f5664a3136b37391be5b/followup-2026-11-08/ui/QUEUE-BROWSER-RESULTS.md) | `8d612dd42e28ec04db932e6a2221a4cbdc512329` | Actual browser actions/errors, independent observations and manual cleanup; no inferred request status/cause. |
| [queue/ui-removal/RESULTS-UI.md](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/958470f1f185e5c84ca3f5664a3136b37391be5b/followup-2026-11-08/queue/ui-removal/RESULTS-UI.md) | `e50b16077106df76f64098e2b42493cd3dbe4106` | Separate after-each API/Git reads, admission versus website evidence, one authorized cleanup and exact preservation. |
| [queue/ui-removal/case-index.json](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/958470f1f185e5c84ca3f5664a3136b37391be5b/followup-2026-11-08/queue/ui-removal/case-index.json) | `189c6c146efaf042aabf85304b0e8b8eb78938b9` | Five separate UI-Q0–UI-Q4 dispositions, evidence paths, unknown website status/operation ID, cleanup and retained refs. |

Candidate line 305 already links issue 519 as the queue evidence discussion and states that the child issues link frozen evidence. That route now reaches the exact new reports. The issue preserves the extension separately from the original 32 queue dispositions. Candidate line 286's older `97b993e` snapshot and five-index/130-ID statement can continue to identify the original campaign without pretending the new UI cases were present at that older commit.

The earlier check that `97b993e` lacks the UI report remains factually correct; publication and the verified issue links have supplied the missing delivery path. This recheck does not revise the reviewed UI outcome, establish new hosted guarantees, or validate the underlying protocol beyond the report-level provenance claim. The semantic and production limitations in review-003 remain.
