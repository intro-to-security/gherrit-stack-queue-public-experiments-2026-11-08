# Native SQUASH queue with only real CI

The fresh two-PR discriminator reproduced upper-member queue removal **without any manual release context or synthetic status writes**. Lower A [#25](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/25) landed; upper B [#26](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/26) left the queue with provider reason `invalid_merge_commit`, then its native rewrite received successful real CI and became `CLEAN` while remaining open and unqueued in later samples.

This is a bounded observation of native stack #27 under the exact configuration below. It rules out the earlier synthetic release context as a necessary cause of this trace. It does not identify the internal cause, establish every merge method's behavior, or prove that no delayed operation can occur.

## Conditions and one admission

The fixture owns `exp/ci/native-no-manual-gate/**` in the authorized public repository. Exact-trunk ruleset **26821953** has no bypass actors and requires only **`queue-observe`**, bound to GitHub Actions app 15368. Effective branch-rule readback confirms no additional required context. Queue parameters were `SQUASH`, `ALLGREEN`, build concurrency **1**, maximum merge entries **5**, minimum entries **1**, minimum wait **1 minute**, and check response timeout **5 minutes**. There were no review rules or failure-marker files in either authored tree.

Both source PRs were observed `CLEAN` at 01:25:34.570671–35.466723Z on November 9, 2026 UTC. Their actual workflow checks supplied eligibility; no commit statuses were posted. One REST request selected B's captured head `e0bba642dfb010d659204b842391f2671c533e9b`, supplied `merge_action: merge_queue`, and omitted `merge_method`. UUID `a3549937-89c0-479c-b1a0-460eb14bf611` became terminal `enqueued` at 01:25:39.359967Z. The following queue read contained A and B in positions 1 and 2. No request was resent or requeued.

## Actual group, removal and source rewrite

A's candidate `f2ed13bbdd7839e5e83e1ac131cff4ddd542d32d` was observed `AWAITING_CHECKS`, then `MERGEABLE`. Its actual [merge-group workflow 42545538666](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42545538666) succeeded. The downloaded `checks_requested` event, Actions run, `GITHUB_SHA`, checkout and check-run attachment all name that candidate. Its sole parent was original trunk `6d9310de15493dc854f50b39698d314df124a588`, and its tree contained A's authored change.

Provider timeline records show B removed at **01:26:27Z**, reason **`invalid_merge_commit`**, with `beforeCommit: null`. A's queue removal reason is **`merged`** at **01:26:28Z**, naming the checked candidate. These are provider metadata timestamps around the lower landing; they do not reveal an internal transaction order. Subsequent reads showed A merged and the trunk equal to that checked candidate, with both queue entries absent.

B's head changed natively to `faabdcba56d4b3fcbcd8e4caa585e797082f0408`, based directly on the landed trunk. The real [synchronize workflow 42545595057](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42545595057) ran for that exact new PR head and succeeded. Its checkout was synthetic PR merge `ee2ca110c7e40bae733eaa34e8c18ad287830c71`, whose parents were landed trunk and new B. Earlier samples showed the new source check pending; later separate reads through **01:27:59.805357Z** showed B `CLEAN`, open, and without a queue entry. No B merge-group run was observed in this capture.

Exact old/new B parent-to-head binary diffs, complete tree, full author tuple and message were equal. Its author/message disclosure remained; both source and replacement were unsigned. The original A/B authored archives and A head stayed unchanged. Local pins retain the exact landed A and rewritten B objects. Queried original/new B and landed-group commit-status lists were empty, corroborating the absence of the synthetic release context.

Re-reading the original async UUID after removal still returned `enqueued`. It described completed admission, not present queue membership or full-prefix landing.

## Evidence and limits

`state.json` preserves the source-ready samples, exact rule, one admission receipt, both queue entries, non-atomic observation intervals and workflow/removal data. `effective-rules.json`, `B-comparison.json`, `commits.json`, `old-receipt-after-ejection.json`, `hosted-object-pins.json` and raw CI-lane receipts retain the supporting boundaries. All six relevant opened/stacked/synchronize/group run artifacts and logs are under this directory. `runner-squash-v1.py` preserves the executed runner before the separately requested method variants were added.

Only fixture creation/rule creation and one native queue admission were written. The source heads were not manually amended after admission; no synthetic status, reviewer, requeue, shared workflow or global setting was used. The final observed own queue was empty, with B deliberately retained open. This discriminator does not establish how a different build concurrency, grouping policy, merge method, repository or future provider revision behaves. Matching finite samples do not prove provider settlement or authorize overlapping production writes.

The later final read and artifact freeze retained the same outcome. `frozen-summary.json` now supplies raw-byte patch hashes, full check identities, exact effective rules and a fresh empty-queue observation. Separate fresh method variants are compared in [NATIVE-METHODS.md](../NATIVE-METHODS.md); this original SQUASH fixture was not readmitted.

*Authored by an AI agent acting on joshlf's behalf.*
