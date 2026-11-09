# Frozen lower-A stale-map fixture

This literal variant of `../fixture-prep/fixture.py` advances only the lower member after the initiating POST is demonstrably held before dispatch. The selected top B head remains `0d139c885ed973bb1a932e8c6771abd056d93f55`. It can distinguish rejection of this stale lower-member map from a guard that checks only that selected B head.

Scope: `exh-1109-ui-stale-debug-a-5949ea0a29` in `joshlf/gherrit-native-stack-experiments-2026-11-08`. Frozen source SHA256 `91c4a317145202a640cc348f2cef6358518589e5db495f0e8d2f3d70cc814dfc`; inputs `db41a6aba4751aa2e69914b4bdd80ad2267cfa1fd10b42ce920003c1eda7dfe3`; helper `ae1ae63d5ee8370cbca11711f5d5e76a97669881ddf8ef8911493666393d128d`. `BASELINE.diff` records the bounded source changes; the first fixture is unchanged.

`prepare` requires an exact root grant and has the same five-effect budget as the first fixture: atomic create-only push of six refs, two PR creations, registration of their ordered group, and a leased synthetic-trunk advance to `72a17fe9c84d215d5dcf120dad2b1e8d0c5ad171`. `READY.json` captures canonical IDs and the exact six-ref vector.

A separately granted `advance-a` requires root's hashed same-scope `paused-before-dispatch` evidence plus the READY hash. It sends one atomic push only: A `843359d9d586da7f11a03ef4ff98bf746cbac233` → `3f7c0881bb913b772784842cf7204d4640737bea` and create-only archive-a-v2 at A2. It independently reads the exact seven-ref result, including unchanged selected B0. No browser or native API request is in that action. Root owns all actual hosted and UI effects.

A2's distinct `late-a-marker.txt` object is precomputed locally; publication and its archive are pause-bound. Preserve A's full two-commit range `e18576ec11ecd2ec261341219eedbed1d1b2ac2b..3f7c0881bb913b772784842cf7204d4640737bea` and B's unchanged own range `843359d9d586da7f11a03ef4ff98bf746cbac233..0d139c885ed973bb1a932e8c6771abd056d93f55`. Four independent expected trees cover old A/B and advanced A/B results:

| Result | Tree |
| --- | --- |
| expected-A0 | `3791dd692e5491165abaeeb46e4495e2cbc1a552` |
| expected-B0 | `1eb7db43899584e14264ac801d64671e08db83d0` |
| expected-A2 | `80614ff782ec6c6e71e5054c82a6e55115eda893` |
| expected-B-over-A2 | `f21e7fb07bf8a8a97bb00ad865d3a8f8a220a418` |

`LOCAL-VERIFICATION.json` records actual local objects/parents/trees/blobs/trailers, exact disjoint filename changes, expected trees, bare origin/push URL/hooks, syntax and fsck checks. No hosted call or native intent occurred during this preparation.

Use the existing oracle in `../oracle-review/REVIEW.md`: exact pre-send pause → acknowledged A push → independent actual seven-ref read → same old-map call still paused → one Resume → actual serialized map and response/job readback. Uncertain ordering or a refreshed map fails the stale-map premise. Unknown effects freeze the scope without replay. No cleanup, extra fixture or repaired request is implicit.

*Authored by an AI agent acting on joshlf's behalf.*
