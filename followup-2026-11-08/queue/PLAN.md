# Native queue follow-up plan

This bounded synthetic campaign tests removal, method/settings interactions, size boundaries, isolated work and recovery. It uses only the existing public repository `intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08`, new `exp/fu2/queue/**` refs/PRs, and exact `gherrit-fu2-queue-*` rules. Existing fixtures, main, shared workflow and repository settings are read-only. Publication belongs to the root coordinator.

## Evidence and controls

The live seed has all three merge methods enabled. Its existing read-only `queue-observe` workflow listens to real pull-request and merge-group events, checks exact event/checkout attachment, and uploads event/commit evidence. It fails merge-group checks only when `.queue-experiment/FAIL_MERGE_GROUP` is tracked, and PR checks only for `.queue-experiment/FAIL_PR`. The workflow and script are retained before dispatch. No shared workflow change is needed.

Every API/Git mutation receives a durable pre-dispatch intent and a sanitized receipt, followed by independent reads. A missing receipt stops re-dispatch pending reconciliation. Reads retain UTC start/end and monotonic intervals. Queue membership, original async UUID, PR lifecycle, Git refs, removal events and Actions candidates are distinct observations. Polling bounds do not prove provider settlement or permission for overlapping production writes.

Default queue: timeout 5 minutes, no bypass actor, min entries 1, min wait 1 minute, maximum merge entries 5. Real Actions `queue-observe` (app 15368) is required throughout. Held cases also require `experiment/queue-release`: source heads receive success before admission; candidate heads remain blocked until explicit release. This is a test barrier, and results identify it.

## Enumerated cases and oracles

| ID | New or reused; exact setting/discriminator | Hypothesis and outcome oracle |
| --- | --- | --- |
| Q01-C | New; ABC native stack, MERGE/ALLGREEN/build 1, held; confirmed selected-C admission then dequeue C | Distinguish upper-PR API routing from pending timing. Read returned error or success, remaining exact A/B/C membership and removal timeline. |
| Q01-B | New; same held ABC fixture after Q01-C while eligible, dequeue B | Removing middle should remove dependent C, retaining A; a routing rejection is a distinct outcome. |
| Q01-A | New; same fixture, dequeue A | Lower removal should empty dependent prefix; compare old original UUID with real membership. Prior two-member lower removal is also reused. |
| Q02-A | New; held AB, one selected-B 202 immediately followed by lower-A dequeue with no intervening read | Compare prior immediate-B rejected routing. Pending vs admitted timing is measured; success alone cannot establish pending cancellation. Poll original UUID and read membership, then remove confirmed leftovers. |
| Q03-{method}-{strategy}-{build} | Full bounded 3x2x2 method/settings matrix: methods MERGE/SQUASH/REBASE; strategies ALLGREEN/HEADGREEN; build 1/2; native AB, max merge 5, real Actions only | Reuse prior ALLGREEN/build1 controls for each method, execute the other nine cells. Exact selected-head request once; source and candidate check/graph, landed identities, upper rewrite/ejection, original receipt and removal reason determine each result. No broad all-method guarantee. |
| Q04-2/Q04-3/Q04-4 | New; MERGE/ALLGREEN/build 4, max merge 2; held stacks of 2/3/4 | Below, equal to, above `2 * 1.5 = 3` buffer. Candidate builds are distinct from merge transaction limits. Record candidate membership, ordered releases, trunk transitions and per-PR merge times; mark transaction atomicity/group size unknown if API evidence cannot expose it. Compare conflicting docs wording, rather than assume either description. |
| Q05 | New; ABC, MERGE/ALLGREEN/build2, held, select B only | A/B should enter while C stays unqueued, then release A/B and inspect native continuation C, exact patch and archive. |
| Q06-ALLGREEN/Q06-HEADGREEN | New; ABC, build3, max merge5, held; force failure on B candidate only, keep A held and C good | Discriminate failure propagation with last candidate green. These are synthetic external status failures, separate from real Actions markers. Record dependency removals and whether strategy permits or ejects B/C. Cleanup explicit remaining A. |
| Q07 | New; same trunk contains independent ordinary PR X then native AB and native CD (two stacks), MERGE/ALLGREEN/build3, held | Removing lower A should remove B while unrelated X/C/D remain eligible or queued. Observe queue order/candidate rebuilds and clean all fixture-owned entries. |
| Q08-clear/Q08-conflict | New; linear native AB then advance own trunk before rule creation: independent file or conflicting A file | Admission should reject a nonlinear stack rather than silently rewrite it. Exact failed receipt/queue/trunk/source refs establish scope; conflict is separately observed, not inferred from generic nonlinearity. |
| Q09 | New; fresh SQUASH/ALLGREEN/build1 AB, real Actions only | Follow an observed upper invalid-merge ejection/native new head. Read actual new head and real checks, send one explicitly new request and retain separate UUID. Failure to reach a new CLEAN head at bound remains unavailable rather than automatic retry. Prior successful explicit re-admission is reused corroboration. |
| Q10 | Reused; real merge-group-only failure, queued atomic head-update rejection, failing-upper admission, old UUID persistence | Prior evidence already directly exercises these controls. Link exact original sources rather than repeat them without a new discriminator. |

## Pacing and completion

At most three method fixtures are admitted in a batch. API requests are sequential within a fixture, at least 0.15 seconds apart; fixture sizes are 1–5 entries, build concurrency at most 4. Source readiness is bounded at 150 seconds, admission polling at 45 seconds, normal landing observation at 180 seconds, held-candidate discovery at 90 seconds. Longer ongoing real Actions are observed in a later bounded read; no unknown mutation is resent. Completion audits every created fixture queue, active workflow run and recorded async UUID, reconciles/cleans confirmed membership, and records every case as performed, reused or concretely unavailable. Queue cleanup uses only fixture PRs and captures the final empty observation; this is cleanup evidence, not a no-future-write guarantee.

Docs consulted: [native stack merging](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests), [troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-stacked-pull-requests), [queue settings](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue). The first describes oversize as a next-group single unit; troubleshooting describes continuation across groups. Both require observation/clarification.

*Authored by an AI agent acting on joshlf's behalf.*

## Recorded execution adjustment

The first clear-advanced-trunk request failed while source Actions were still in progress. That known failed attempt is retained, and Q08 receives a separate `checks-clean-admission` after actual Actions success. The conflict case uses the same check control. This excludes a check-timing explanation before interpreting trunk/linearity behavior. It does not resend an unknown operation.

Q04 occupied-queue controls add an independent ordinary X ahead of a native stack of two or three. Max merge2 gives combined queue sizes3/4, equal/above the buffer. Build4, minimum2/wait5, real Actions and manual candidate gate prevent an early X-only landing. After all exact candidates pass real Actions, release native members top-down and X last. Compare per-PR merge events and bounded ref/PR observations; do not equate equal timestamps with a transaction identity.

The occupied size3 control has minimum2/wait5. With X ahead, all four candidates became MERGEABLE but had not landed before the ordinary 180-second observation bound. Its read-only observer was interrupted before cleanup, and the same already-admitted case is observed for another bounded 210 seconds so the configured batching wait can expire. No admission/status mutation is resent; cleanup remains after that meaningful oracle interval.
