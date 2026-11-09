# Fresh-map control preserved the full A and B changes

The independent graph readback passed all three bounded cohorts for [A #667](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/667), [B #668](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/668), native group #669. The website's [separately captured actual POST](../NETWORK-A-FRESH.json) used current A2/B0, returned HTTP 200, and its captured status reads progressed PENDING → RUNNING → DONE with both members SUCCEEDED. The UI reported both Rebased. This observer independently checked the resulting graph; it made no private endpoint or status request.

The resulting chain was:

`T1 d59931dac559bd7c05d1f29f7ca867c0f628c3f2` → `A-first 4616dba9041f28552307f282afae1196b3fb3a3b` → `A 62a778098ec047a2ef449139b871355db98d0429` → `B f918555d3ba30e18caa4e83d32252afcb8ab2fcc`.

A's **full two-commit range**, actual T1..new-A, exactly matched the source patch T0..A2: both original a.txt and late-a-marker.txt additions survived. B's full new-A..new-B range contained one commit and exactly matched source A0..B0: the sole b.txt addition. B's sole parent was the actual new A, and A's first rewritten commit had sole parent T1. The A/B trees were respectively `2e488b9be1cba7d8acc168d8682ac12f35b01768` and `e90cf9dd2c6d978eccb272da5aeb7a64ec7f4a8e`, matching the independently prepared expected trees. The marker survived in **both** heads.

| Cohort | UTC interval, 2026-11-09 |
| --- | --- |
| 0 | 2026-11-09T18:36:43.915585+00:00 – 2026-11-09T18:36:44.891027+00:00 |
| 1 | 2026-11-09T18:36:53.920702+00:00 – 2026-11-09T18:36:54.839041+00:00 |
| 2 | 2026-11-09T18:37:13.917452+00:00 – 2026-11-09T18:37:14.810873+00:00 |

The actual and fetched seven-ref vectors agreed throughout. Only member A/B had the new rebase heads; the five protected refs—advanced trunk, original source, A-v1/B-v1 archives and A2 archive—matched their exact pre-operation values. Canonical PR/group identities, open states, names and ordered membership matched. No head/base projection disagreement appeared in these later cohorts. There was no failed read. They were scheduled 0/10/30 seconds from observer start, after the captured website job; they do not establish continuous silence or a future-write fence.

All three rewritten commits preserved their original author records, exact messages and one `Agent-authored-by: AI agent acting on joshlf's behalf` trailer each. Source commits had no gpgsig header. Rewritten commits recorded `GitHub <noreply@github.com>` as committer and contained gpgsig headers. Raw bytes are retained; signatures were not cryptographically verified, and these fields alone do not prove an internal producer implementation. Retained raw commit SHA1 identities recomputed correctly, and local fsck exited zero.

The actual capture used git version 2.54.0 (Apple Git-157), gh version 2.102.0 (2026-09-30) and Python 3.9.6. The unchanged executed observer SHA256 is `0c77ae4659f221bce43f08d8fb22b967b13f5fd84a11ff24e7299c73055acf46`; [source/input pins](capture-001/INPUT-PINS.json), [retained results](capture-001/RESULTS.json), [offline verification](CHECKS.json) and [command effect audit](EFFECT-AUDIT.json) identify the evidence. The audit found 106 recorded commands, including 9 API GETs, three exact ref reads and three fetches, with zero remote mutations.

This positive control shows that this clean A2/B0 divergence can complete with a current submitted map and preserve both layers. It does not by itself settle the different stale lower-A trial, isolate why another request returned 409, create a public API compatibility promise, or identify a server comparison source. The sanitized network export contains four filtered entries, whereas the operator recorded 31 whole-tab requests; the private raw HAR remains excluded.

*Authored by an AI agent acting on joshlf's behalf.*
