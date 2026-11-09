*Authored by an AI agent acting on joshlf's behalf.*

The held fresh-map control completed an observed successful native rebase of both PRs. Three independent graph cohorts at 0, 10 and 30 seconds retained the same new heads, the full two-commit A range and one-commit B range, the expected result trees, and the late-A marker on both heads. All five protected refs retained their exact input OIDs. PRs [670](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/670) and [671](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/671) remained open and unmerged in canonical group 672, in A/B order. No REST-versus-named-ref projection disagreement appeared in these cohorts.

The root-owned pause/timer records report the same fresh A2/B0 request body before and after a 420.257478125-second one-process monotonic hold. Samples at 0, 210 and 420 seconds all returned the exact seven-ref READY vector. The minimized actual network record retains a POST with that same map returning 200, followed by PENDING and DONE status responses; both members ended SUCCEEDED. Root recorded one Resume, both UI rows Rebased, removal of the owned breakpoint and no remaining pause. This observer independently captured the graph after that operation; it did not operate the UI, replay status requests, or read the private HAR.

| Graph role | Exact OID |
| --- | --- |
| Unchanged trunk T1 | `5d5ad41b3bae892882940712dda83a204d66da0c` |
| Source A2, retained by archive-a-v2 | `fa8f119c706640635044d2a5129591c4598ca8d5` |
| Source B0, retained by source-v1 and archive-b-v1 | `c0f91ab8deab54ca5c07cd0b3a5ee4271236d3b9` |
| First rewritten A commit, sole parent T1 | `617a3d98eb3a7a2a28dc96d2307d654f92a5da05` |
| New A head, sole parent first rewritten A | `e289ebdcdcd6ee1cddf6df3a1e21f92129074543` |
| New B head, sole parent new A | `7d6218167cffce7a20714c3177bd8b59d7aae84b` |
| A result tree | `2067952fdbcaceee5589e9192714db3ab93cd337` |
| B result tree | `8ab913d8efc4a096f4163e09546e68f239154dd6` |

The five protected refs were trunk, source-v1, archive-a-v1, archive-b-v1 and archive-a-v2 in namespace `exh-1109-ui-stale-debug-held-fresh-0a10ffe99c`. Source A-v2 is T0..A2, including the original a.txt commit and the additional late-a-marker.txt commit. Its full binary/full-index patch equals T1..new-A. Source B-v1 is A0..B0; its one-file b.txt patch equals new-A..new-B. These literal patch equalities apply to this disjoint-file fixture. The exact marker bytes are retained in both heads. Each rewritten commit preserves its source author, message and single Agent-authored-by trailer. The rewritten committer is GitHub and each rewritten raw object has a gpgsig header; signature presence was retained, without cryptographic verification or a claim about the internal producer.

| Cohort | UTC start | UTC end |
| --- | --- | --- |
| 0 seconds | 2026-11-09 19:13:00.507322 | 19:13:01.652449 |
| 10 seconds | 2026-11-09 19:13:10.512174 | 19:13:12.578771 |
| 30 seconds | 2026-11-09 19:13:30.510472 | 19:13:31.556427 |

[observer.py](observer.py) is a literal copy of the previous positive observer with only fixture, prefix, network-record, PR/group and local observation-ref constants changed. [SOURCE-PINS.json](SOURCE-PINS.json), retained originals and literal diffs preserve that provenance. Its 106 command receipts contain nine exact REST GETs, three exact seven-ref ls-remotes, three exact-ref fetches into a new owned bare store, and 91 local commands. No remote mutation command was issued. Each cohort combines nearby reads and a later fetch; it is not a transaction across Git and REST. Agreement between each advertisement and fetched vector was checked. The final owned-store fsck exited zero.

[CHECKS.json](CHECKS.json) records the successful offline verifier run against the retained graph and pinned inputs. [OFFLINE-CHECKS.json](OFFLINE-CHECKS.json) additionally verifies every recorded stdout/stderr digest, literal source adaptation, independently reparsed commit fields, exact marker keys/output bytes, and the pause/timer/network input bindings. Its isolated positive control passed, and the frozen verifier rejected six altered records: truncated A range, missing B marker, wrong B parent, changed B patch, wrong canonical repository and missing rewritten-A disclosure trailer. Those probes blocked process/network entry points and used disposable copies beneath this outcome directory. [SUPPORT-PINS.json](SUPPORT-PINS.json) pins exact copies of the authorized sanitized inputs; [MANIFEST.json](MANIFEST.json) inventories all retained files here except itself and the Git store.

Terminal effect status is **observed successful rebase of A and B, with required source content retained across all three cohorts**. The operation uses the current private website action. The held fresh success shows that this debugger pause/request age alone was insufficient to force rejection in this control. It does not identify a unique internal checking algorithm, establish an internal job-dispatch boundary, or supply a public interface promise. The hold samples are not a continuous ref lock; the later cohorts do not prove a future-write fence. HAR timestamps are retained only as source fields, not used to infer the physical send instant. No convergence or release-readiness judgment is made here.
