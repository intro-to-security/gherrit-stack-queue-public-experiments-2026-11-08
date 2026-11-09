# Frozen fresh-map lower-A positive control

This prepare-only literal variant makes A2 current before the browser loads, while selected B remains B0. It tests whether the same clean A2/B0 divergence can proceed with a fresh submitted map. The decisive positive premise is an actual initiating POST containing current A2/B0; pre-load publication alone does not establish what the browser submits.

Scope `exh-1109-ui-stale-debug-a-fresh-0a2893d4d4` in `joshlf/gherrit-native-stack-experiments-2026-11-08`. Frozen source SHA256 `7681ce6e8649619d79c1ba3f0db4005c1ab197fcb98b3ab27142d68faa3dc000`; inputs `4d9a1b51af135c7583eecf8290f42225581d8c71fdf884eaaa7a8266e0ebc570`; helper `ae1ae63d5ee8370cbca11711f5d5e76a97669881ddf8ef8911493666393d128d`. `BASELINE.diff` is against the frozen lower-A stale variant. Neither earlier fixture was edited.

Only `prepare` is available as a hosted action, requiring an exact root grant under campaign/control bound to these source/helper/input identities. Its five effects are: atomic create-only push of six refs, two PR creations, one ordered native registration, then one atomic push leasing synthetic trunk T0→T1 and A0→A2 while creating archive-a-v2. Final exact seven-ref readback precedes READY. There is no paused-advance action, browser effect, private endpoint call, retry or cleanup in this source.

- A0: `e547ce6b7f9cbff283a88b8550dcabe71a529d78`.
- A2: `721cd407451739ef646b7434285c60b01096b400`.
- Unchanged selected B0: `fb757ca354d5e6a4e3460a7658529d13452e14ac`.
- Advanced own trunk T1: `d59931dac559bd7c05d1f29f7ca867c0f628c3f2`.
- Original full A-v2 range: `a8f7a8fd4a8d52ac1daf847a68e09998b8cf36b4..721cd407451739ef646b7434285c60b01096b400` (two commits).
- Original own B range: `e547ce6b7f9cbff283a88b8550dcabe71a529d78..fb757ca354d5e6a4e3460a7658529d13452e14ac`.

`late-a-marker.txt` retains the bounded counterpart filename and contains `Pre-load lower-A publication marker exh-1109-ui-stale-debug-a-fresh-0a2893d4d4`. A2's object is precomputed locally. It and its archive are published in the final prepare push, before READY/browser load. The marker is disjoint from A's a.txt, B's b.txt and trunk-progress.txt.

| Result | Expected tree |
| --- | --- |
| expected-A0 | `454d952847576edd8f22103e1577ce48d1ba80e3` |
| expected-B0 | `58c58b8bb6c831a26c238f9872c6360bbe3bfe17` |
| expected-A2 | `2e488b9be1cba7d8acc168d8682ac12f35b01768` |
| expected-B-over-A2 | `e90cf9dd2c6d978eccb272da5aeb7a64ec7f4a8e` |

`LOCAL-VERIFICATION.json` records all nine actual commit/tree/blob contents and parents, one disclosure trailer each, exact patch filename sets, all four expected result trees, bare origin/push URL/hooks, syntax and fsck checks. No hosted effect or native intent occurred in local preparation.

The registration response retained in READY originates before the final A/trunk push; its head projections are historical observations. READY's independently read actual ref vector is current at its read. Root should record canonical identities and any projection lag, wait/read as appropriate, and inspect the one actual initiating payload. An old/refreshed/missing payload is classified from its captured contents rather than inferred from the page. Follow only the uniquely identified job and compare actual result parents, full layer patches and marker-preserving trees. Unknown effects freeze for read-only reconciliation; do not replay to obtain a receipt. Root owns the UI, all hosted execution and outcome reporting.

*Authored by an AI agent acting on joshlf's behalf.*
