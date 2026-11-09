# Website queue-removal extension

Prepare one fresh native ABC fixture in the authorized public synthetic repository, under `exp/fu2/queue/ui-removal-20261109a/**`, with exact rule `gherrit-fu2-queue-ui-removal-20261109a`. Existing queue cases and root-owned reports remain frozen. This extension uses its own source, Git store, state, intents and receipts under `queue/ui-removal/`.

The existing real Actions `queue-observe` check (app 15368) remains required. A separate required `experiment/ui-removal-release` status is successful only at each source head. No success is posted at a merge-group candidate, so candidates remain held. Queue settings: MERGE, ALLGREEN, build concurrency one, maximum merge entries three, minimum one/wait one minute, timeout five minutes, no bypass actors. The held queue must be exercised within the timeout; if checks time out first, retain that cause rather than call it a website removal.

## Cases and handoff

| ID | Action and precondition | Outcome oracle |
| --- | --- | --- |
| UI-Q0 | Prepare ABC, native registration and exact trunk rule; wait for real source Actions and source-only gate readiness. Stop before admission. | All ABC CLEAN, refs/archives exact and queue empty. State explicitly says admission awaits root browser readiness. |
| UI-Q1 | Only after root confirms authenticated browser ready and requests admission, send one selected-C async admission at the current exact C head. | Retain 202/UUID and terminal receipt separately; confirm actual ABC membership, original source refs and candidate manual gate absent/pending. |
| UI-Q2 | Root alone uses the website's upper-C removal control. Worker only reads during root's UI ownership. | Compare exact before/after membership: C removed and A/B retained, or concrete UI refusal/error/other outcome. Bind native removal reason/timestamp to root's UI evidence without claiming causation from time alone. |
| UI-Q3 | Root alone uses the website's middle-B removal control while B remains admitted. Worker only reads. | Compare exact before/after membership and dependent suffix behavior. If C was already removed, B removal should leave A. If UI-Q2 failed, record whether B/C disappear together. |
| UI-Q4 | Cleanup only after root explicitly requests it. | Remove confirmed lowest own membership, record exact response and final empty queue. Do not retry an unknown write. |

The worker never runs a dequeue while root owns UI, never releases candidate gates, and never overlaps any source/ref mutation. Root captures actual website affordances, browser state and error messages; the worker independently captures GraphQL queue/PR state, original async UUID, owned Git refs and real check attachment. If browser authentication is unavailable, leave the fixture ready and unadmitted, with no active queue and an explicit unavailable disposition.

Requests are sequential and paced at least 180 ms. Source readiness is bounded at 180 seconds, async polling at 45 seconds and membership confirmation at 45 seconds. Reads can be repeated with new labels; missing write receipts or indeterminate outcomes stop mutation pending reconciliation. Call intervals include pacing and are not exact server dispatch instants. Empty queues and finite coherent reads are observations, not a no-future-provider-write guarantee.

*Authored by an AI agent acting on joshlf's behalf.*
