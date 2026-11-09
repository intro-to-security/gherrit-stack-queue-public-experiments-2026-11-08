# Frozen stale-map fixture handoff

The source and local inputs are frozen. Root owns both hosted actions and every browser interaction. This note adds no grant and changes no source, input, original receipt or Git object.

- Scope: `exh-1109-ui-stale-debug-c536c6f390` in `joshlf/gherrit-native-stack-experiments-2026-11-08`.
- Website: [B PR #662](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/662); A PR #661; native group #663.
- Exact breakpoint substring: `/pull/662/page_data/stack_rebase`.
- `fixture.py` SHA256: `e008d3c59c18ee499d6b6c5e44fe66369ceb79ade176a093189afa6666524e53`.
- `control/rootlab.py` SHA256: `ae1ae63d5ee8370cbca11711f5d5e76a97669881ddf8ef8911493666393d128d`.
- `LOCAL-INPUTS.json` SHA256: `e9c786d3e7ed59457eaf0b39cbda54bc937005ba27dce5305b0258bd8daf5a3a`.

Root's preparation action uses five durable mutation intents: one atomic create-only push of six branch refs, two PR creations, one native registration, and one explicitly leased synthetic-trunk advance. `READY.json` records the resulting IDs and exact six-ref vector. The separate `advance-b` action permits one atomic leased push only: B `47456f450de5028a2667629b92cd45ef00e0b585` → `219b947d8d655e8104e89ebba49c38253f79f0ce`, plus create-only `exh-1109-ui-stale-debug-c536c6f390-archive-b-v2` at that new B. Its grant must bind the frozen source/helper/inputs, current `READY.json`, and root's hashed pause-evidence JSON. That pause record must identify this prefix and `paused-before-dispatch` state. No native API call or browser operation occurs in `advance-b`.

The script names the advanced B input **B2**; it corresponds to the oracle's generically named later B1 marker. Its object was precomputed locally before the pause. Only publication of B2 and its archive is pause-bound. The marker is the distinct, nonconflicting `late-marker.txt`, with text `Post-pause publication marker exh-1109-ui-stale-debug-c536c6f390`. The original `b.txt` remains part of the B layer.

The exact original layer ranges are A `2471699dda3fa32eaeb3e61398b4eaaba6db46e4..5594964d25db4275eef1f1f7890f49946ac03980`, B-v1 `5594964d25db4275eef1f1f7890f49946ac03980..47456f450de5028a2667629b92cd45ef00e0b585`, and B-v2 `5594964d25db4275eef1f1f7890f49946ac03980..219b947d8d655e8104e89ebba49c38253f79f0ce`. B-v2 is a two-commit range; checking only its tip patch would omit the original B contribution. The advanced trunk is `56eb30a5c134d438dec1b54b65841ed4eaa25ab9`. Expected result **trees**, independent of server-generated commit identities, are:

| Result | Tree |
| --- | --- |
| A on advanced trunk | `487202df07c175942eb20a93f71c4103a9759882` |
| Old B on rebased A | `3ec044ee8afdb0beca4c916758846f067e1b0861` |
| Advanced B, including marker, on rebased A | `9357012ec15f4db1b72ffb77a4a84d50a4adfe71` |

Root independently verified all eight frozen commit/tree/blob inputs, parents, disclosure trailers and local fsck in `ROOT-LOCAL-VERIFICATION.json`. The script verifies the owned bare layout, HTTPS origin and push destination, and hooks disabled. It records exclusive action start and per-effect intents before dispatch, snapshots the source, and freezes on an unexpected native-action exception. Existing starts/intents are not replayable.

For the actual stale-map premise, use the causal order in `../oracle-review/REVIEW.md`: demonstrate that the exact initiating POST is held before dispatch; acknowledge the separately granted B advance and independently read its actual ref; observe the same call still paused; Resume once; capture the actual serialized old map and outcome. A refreshed map or uncertain send boundary is a failed premise. `HAR.startedDateTime` is not physical send time. An unknown response/job freezes the scope for read-only reconciliation. No cleanup, repaired write, second initiation or private endpoint replay is implicit.

*Authored by an AI agent acting on joshlf's behalf.*
