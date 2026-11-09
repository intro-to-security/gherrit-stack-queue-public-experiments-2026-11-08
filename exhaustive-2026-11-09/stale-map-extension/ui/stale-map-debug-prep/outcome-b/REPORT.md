# B-stale initiation: independent remote outcome capture

Three read-only cohorts retained the complete seven-ref post-advance vector, canonical open PRs 661/662 in group 663, and B-v2's complete authored range and marker. No rebase effect was observed in these cohorts. The root-reported initiating UI outcome was HTTP 409, “Stack contents have changed,” with A/B Skipped. This observer did not inspect the private HAR or independently establish the POST's send ordering/payload/response; root retains that evidence and attribution.

The scope is only `exh-1109-ui-stale-debug-c536c6f390` in `joshlf/gherrit-native-stack-experiments-2026-11-08`. Inputs are pinned from `fixture-prep/READY.json` and `B-ADVANCED.json`. The initial sandboxed read batch failed DNS/network resolution; its source, attempted-read receipts and empty independent local store remain retained. A fresh `capture-002` used technical network escalation for the authorized GETs and exact-ref fetches. No native request or remote write was retried or performed by this observer.

## Actual cohorts

Offsets are relative to this observer's start, not the initiating POST or push acknowledgement. Each interval includes separately timestamped parallel reads followed by a scoped fetch/object inspection; it is not a global atomic snapshot.

| Offset | UTC start | UTC finish |
| --- | --- | --- |
| 0 seconds | 2026-11-09 18:17:51.264289 | 18:17:52.166093 |
| 10 seconds | 18:18:01.267994 | 18:18:02.039933 |
| 30 seconds | 18:18:21.265263 | 18:18:22.076458 |

Every cohort's actual `ls-remote` vector and independently fetched vector matched these exact branch refs:

| Suffix after `refs/heads/exh-1109-ui-stale-debug-c536c6f390-` | OID |
| --- | --- |
| trunk | `56eb30a5c134d438dec1b54b65841ed4eaa25ab9` |
| a | `5594964d25db4275eef1f1f7890f49946ac03980` |
| b | `219b947d8d655e8104e89ebba49c38253f79f0ce` |
| source-v1 | `47456f450de5028a2667629b92cd45ef00e0b585` |
| archive-a-v1 | `5594964d25db4275eef1f1f7890f49946ac03980` |
| archive-b-v1 | `47456f450de5028a2667629b92cd45ef00e0b585` |
| archive-b-v2 | `219b947d8d655e8104e89ebba49c38253f79f0ce` |

REST and native membership retained PR A node `PR_kwDOVnhIZ88AAAABN6hhxA`, PR B node `PR_kwDOVnhIZ88AAAABN6hjXg`, group node `PRS_kwDOVnhIZ84AMbud`, order [661,662], and open/unmerged state. Both REST heads agreed with actual refs. **A's REST base SHA remained old T0 `2471699dda3fa32eaeb3e61398b4eaaba6db46e4` while its named trunk ref was advanced T1 `56eb30a…` in all three cohorts.** This associated-base projection disagreement is retained rather than silently replaced. B's base remained A0 and agreed with the actual A ref.

## Exact object and authored-range retention

Fetched A0 still has T0 as parent. B2 still has original B0 as its sole parent, and B0 still has A0 as parent. The actual commit bodies match their frozen inputs and recompute to their Git object identities; local Git fsck passed. Raw parents, trees and tree-entry inventories are retained for every unique fetched tip.

The retained B-v2 own range is exactly `5594964d25db4275eef1f1f7890f49946ac03980..219b947d8d655e8104e89ebba49c38253f79f0ce`. Its full binary-capable/full-index diff adds `b.txt` and `late-marker.txt`; the B0→B2 delta adds only `late-marker.txt`. The actual current B marker is exactly `Post-pause publication marker exh-1109-ui-stale-debug-c536c6f390` plus newline. The source-v1 and both v1 archives stayed at their original values, while archive-b-v2 retained B2. `verify.py` rechecks these facts from retained JSON/object bodies without a remote query.

## Terminal effect status and limits

The observer completed its three-cohort read-only assignment: nine REST GETs, three exact `ls-remote` calls and three exact seven-ref fetches into a new independent bare store. Twenty-one local observation refs retain the cohorts; the frozen fixture store was not mutated. There was no observer-issued POST, native initiation, branch push, PR/group edit or cleanup effect, and no pending mutating acknowledgement from this observer.

The initiating effect is **root-reported terminal UI rejection (409/Stack contents have changed; both members Skipped)**, with independent unchanged sampled graph/content afterward. The raw initiation evidence was not opened here. No website job-status endpoint was queried. These finite cohorts do not prove that no job ever existed, that refs were continuously unchanged, that an operation was cancelled, or that later writes are excluded. They supply a bounded graph outcome for root to combine with its exact pre-send pause, acknowledged B advance and actual stale POST evidence.

`capture-002/RESULTS.json`, per-command UTC/monotonic intervals, exact output files, `CHECKS.json`, source and `SOURCE-MANIFEST.json` retain the evidence. Monotonic values are used only within this observer. Local Git stores remain local retention, outside the source-only manifest. No HAR, sealed/private material or unrelated repository was read.

*Authored by an AI agent acting on joshlf's behalf.*
