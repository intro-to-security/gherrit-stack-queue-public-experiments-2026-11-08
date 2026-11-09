# Native-stack follow-up evidence

This campaign informs [GHerrit's native-stack design](https://github.com/joshlf/gherrit/issues/518).
It uses synthetic data in the existing public experiment repositories. Production
GHerrit code, refs, settings, hooks and executables were not changed.

The five completed automated/website lanes retain **130 indexed case IDs**.
That index includes fresh experiments, explicit prior controls, scoped unavailable
premises and a replaced failed premise; it is not 130 independent fresh successes.
Four website rebases were performed by the user and independently checked through
API/Git evidence. A separate five-disposition authenticated website queue-removal extension is
now complete: upper/middle controls returned “Not Found”, independent reads retained
ABC, and one lower removal cleared the held fixture before timeout. Human usability and
machine power-loss claims remain separate from these functional observations.

## Read the results

| Evidence | Main new information |
| --- | --- |
| [Queue results](queue/RESULTS.md) / [case index](queue/case-matrix.json) | SQUASH build-two landed both members where build-one ejected the upper; strategy, occupied size boundaries, routing failures and explicit re-admission were measured. |
| [CI, reviews, signatures and history](ci-reviews/RESULTS.md) / [case index](ci-reviews/matrix.json) | Real push/target checks, producer identity, actual CodeQL and deployment grids; matched review rules; explicit website rebases; actual cross-actor comment permissions and interleaving. |
| [Local results](local/RESULTS.md) / [case index](local/CASE-MATRIX.md) | Broader import checks passed; recovery probes exposed completion, missing-evidence, stale-worker and identity gaps in the prototype. Driver success does not turn those failures into correctness. |
| [Transport and boundary results](protocol/RESULTS.md) / [case index](protocol/matrix.json) | Genuine missing acknowledgements produced effects; 99/100-member creates returned 504/502 despite creating groups; clean incremental append reached 100 and rejected 101. The original blind retry and corrected guard are retained. |
| [Structural restart results](structure/RESULTS.md) / [case index](structure/CASE-MATRIX.md) | Nine actual after-ack SIGKILL/restart recoveries preserved canonical reviews/archives; missing-receipt and stale-state controls refused before dispatch. |
| [Authenticated queue-removal extension](queue/ui-removal/RESULTS-UI.md) / [browser observations](ui/QUEUE-BROWSER-RESULTS.md) | Actual upper/middle website errors retained admitted membership; one lower cleanup removed dependents. No website HTTP status, UUID or internal cause was inferred. |
| [Browser history walkthrough](ui/HISTORY-BROWSER-RESULTS.md) | Actual public links rendered exact patch versus parent-drift comparison. This was an informed agent walkthrough, not a human comprehension study. |

The [final question-by-question coverage map](planning/COVERAGE-FINAL-UI.md) separates completed observations from remaining engineering, provider and human questions. The [coverage plan](PLAN.md) records the material factors and decision mapping.
Each lane's own plan preceded its mutations. Later controls and report/oracle
corrections preserve their original evidence. Read report limits and the case
dispositions before interpreting a result.

## Source and exact evidence

Each lane exposes its reports, machine case index and top-level Python source.
Report display copies have navigation links repaired as recorded in [PUBLICATION-LINKS.json](PUBLICATION-LINKS.json); original report bytes remain inside the archives. Its `evidence.tar.gz` is a lossless copy of the UTF-8 source and raw evidence,
with a per-file content/mode/timestamp inventory in `SOURCE-INDEX.json`.
All archive entries were reopened and checked against their original bytes and
needed file metadata. Expanded local copies and Git stores remain retained;
this packaging did not remove them. Filesystem account identities are omitted
because replay does not require them. Nontext runtimes and working stores were
not bundled into the text archive.

To inspect a lane, verify its archive SHA-256 from `SOURCE-INDEX.json`, extract
into a new empty directory with `tar -xzf /path/to/evidence.tar.gz`, then verify
the extracted entries against the index. Never extract over an active checkout.
The protocol's [Git bundle](protocol/authored-and-observed.bundle) separately
retains exact authored/observed objects and 701 native refs; [BUNDLE.json](protocol/BUNDLE.json)
records its hash and clone procedure. The selected upstream OpenAPI excerpt and
its pinned license/provenance are retained together inside that lane's archive.

These sources record historical mutations. **Do not rerun mutating scripts
unchanged against retained fixture IDs.** Use a fresh authorized namespace and
follow the recorded intent/reconciliation requirements. Unknown groups 330 and
461 are intentionally frozen. A new evidence label does not make an old unknown
write safe to resend.

Finite traces do not establish provider idempotency, a cross-resource snapshot,
pending cancellation, a future-write fence or universal configuration support.
No model failure, unavailable premise or natural server error is erased by the
completion of a driver. The [post-experiment refinement](refinement/RESULT.md) retains the model with
explicit dispatch safeguards and a qualified design. Its three passes end at a
bounded stop on operational/provider obligations, not production acceptance.

*Authored by an AI agent acting on joshlf's behalf.*
