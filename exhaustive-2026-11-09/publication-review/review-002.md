# Incremental review of the final evidence selection

This review is bound to manifest SHA256 `b139252603e91e075a5298462bfda8235af6cfca0686f71b82074a4bcb55655d`. All 1,333 current selected files match its hashes: 16,847,116 bytes, comprising the earlier 893 paths plus 440 additions. Only top-level `RESULTS.md` changed among the earlier paths. This is a bounded independent curation review, not a publication approval or a manual inspection of every selected byte's meaning.

## Concrete remaining presentation correction

`history-range-diff/controls/RESULTS.md`, paragraph 3, says exact command/stdin/stdout/stderr records and object readback are “retained here.” The selected package includes the command ledger, result/verification JSON, selected comparison/patch outputs and source, but omits the raw command receipts, raw binary readback/stdin and Git store. Add an explicit local-retention qualification in the delivered presentation while preserving the original report. State which selected records remain publicly inspectable; do not imply the complete command/readback corpus ships beside the report. A general availability index does not directly qualify this prose claim.

The earlier code-survey qualifier is still pending exactly as the new plan records. Its proposed source has not been silently substituted into this manifest. Root must apply an explicit qualification or an equivalent presentation, then refresh the selected/source/delivered identities. The range-control qualification warrants the same treatment. This review does not cover future edited hashes.

## Structural and provenance checks

`inspect_selected.py` read only exact selected paths, rejected symlink/forbidden path components, checked current identities, UTF-8/NUL status, parsed every selected JSON, searched bounded token/header patterns and JSON private-visibility fields, and checked selected CI/embedded-source identities. It executed no campaign module. Compiling Python source used built-in `compile`, without imports, bytecode writes or historical-driver execution.

- All 864 JSON files parsed; all 155 Python files compiled. No token-pattern, NUL/nontext, literal unmasked credential-header or `private:true`/`visibility:"private"` result was found.
- All seventeen newly selected Markdown documents contain the required AI-agent notice. This checks notice presence; root still owns final rendered disclosure and commit/message attribution.
- The only declared base64 source payload remains public user-owned target CI. Its 2,712 decoded bytes still match selected `actual-ci.yml` and Git blob `b5632e933bcd8ec96bcaea308158823c2d806b30`.
- The long App source-retrieval receipt is not an unidentified third-party implementation: its decoded JSON `stdout` is byte-identical to selected campaign `probe.py`, 10,396 bytes, SHA256 `476029710ad48039c36e423fd6ff6c6219bd591edb96a6df82934eaec1f1e12b`.
- The fifteen selected source-survey license records still agree with their repository pins. No new full third-party implementation/license corpus was selected or opened. Upstream license interpretations were not independently recertified.

The 564 root heuristics comprise 233 credential/header words, 316 local-path occurrences, fourteen private/org/sealed words and one source payload. I manually inspected the deduplicated credential/scope contexts, the seven masked checkout-header lines, and path contexts normalized by workspace prefix/runner timestamp. The long embedded source and CI payload received identity/decoding checks rather than a claim of manual reading of their entire encoded lines. Paths identify the campaign's `/Users/codex` workspace or `/home/runner` (including two quoted prefix mentions in the initial review); no additional home identity appeared. Credential words are redaction/omission code, fixed offline examples, HTTP `Vary` names, masked Basic values or explanatory prose. Scope words remain exclusions, local synthetic stores, the initial review or an attributed public report about inaccessible private data. These observations do not establish detection of arbitrary secret formats or every identifying detail.

## Manual evidence scope and claim calibration

I read the new curation plan, inspection and heuristic-context records, all seventeen added Markdown plans/reports (including the retained initial review), current top-level results, the selected guest outcome summaries, and selected App/partial verification metadata. The prior own-lane source/audit exposure informed interpretation, but was not counted as a new manual review of every current file.

The new reports preserve the consequential distinctions:

- Original actual-Git tests have five expected outcomes and six nonpassing outcomes, including three false completions and a collection diagnostic. The separate eleven-pass barrier variant uses fresh fixtures and unchanged expectations. Its existing-object baseline, Linux Git/ext4, before-recovery replay and surviving outer caches remain qualified.
- The App job's effective write permissions and collection success are distinct from a successful native write-positive control. Its one known 404 and later unchanged observations do not isolate token class or establish a provider fence.
- The public partial trace retains B's verified successful prefix before C's separately rejected request. The original no-request freeze and new continuation authority are preserved rather than relabeled as a retry or transaction.
- Range-diff retains its useful unrelated-drift view alongside the binary-equals/context counterexamples. It is not an equality, acceptance or human-comprehension oracle.

Large guest/runtime images, archives, ZIPs, Git stores and raw binary readback remain omitted. I did not reopen or rehash them, reperform the root's archive/22-runtime-barrier/artifact verification, or manually read every JSON field, Python source line or serial-log payload. Public source permits inspection of the selected method and reported records; it does not make the omitted full forensic inputs runnable or independently inspectable. The guest report and restoration note explicitly retain that limit.

Lossless generated-metadata compaction is a formatting decision, not source deletion. The saved compact inspection retains the full JSON object; actual staged metadata, the future root review receipt, size bounds, generated hashes, link rendering and final pushed/readback bytes remain root's separate checks. This pass staged/published nothing and made no canonical edit, runtime/container/Git-fixture/network effect, or excluded-input read.

`FINDINGS.json` records the exact structural results and limitations. Root retains final semantic review, qualification edits, regeneration and publication authority.

*Authored by an AI agent acting on joshlf's behalf.*
