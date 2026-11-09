# Current state and root handoff

`RESULTS.md` and `matrix.json` contain 31 evidence-backed case dispositions: performed new controls, explicitly reused controls, and four unavailable actual website operations. All twelve native merge requests are terminal. No queue admission was armed.

New controls are complete: external status/candidate/App identity, eligible push checks, default-branch pull_request_target adoption, multi-commit signature selection/mixed suffix signing, real CodeQL negative/positive/cascade checks, required-deployment head/candidate grid, last-push negative/complementary identities, CODEOWNERS unchanged-prefix dismissal and substantive hinted dismissal. Exact requests/receipts/readbacks and per-commit comparisons are retained.

Cleanup complete for all temporary completed controls: fourteen classic protections removed; both scanning rulesets and deployment ruleset/environment removed; three deployment records inactive. Root restored the Actions bot flag to false/default read and removed its temporary main target workflow; this lane independently confirmed false and 404. `cleanup.json` records details. No more bot operation or main workflow is needed.

Four reserved website fixtures retain their exact protections and untouched lane-owned source heads:

| Fixture | Lower / upper PR | Before-UI heads |
| --- | --- | --- |
| ui-stale | #127 / #128 | c2f7b64b7c0f009491195a8ffda21c6c29dd5c11 / 8223987f13b4b9a40a7178ddf8aabbdad6a77408 |
| ui-lastpush | #129 / #130 | bfdf982bf9e0b3eecc6130fe7405cd68d416fe7e / 66b0dded232dafc0243433b7e78b7db3b2810af9 |
| ui-codeowner | #131 / #132 | 6a6adc7ce466b1b2924fc687e1456710d5cd9221 / 3eb13a0a05b95e378b3cfb7f78727d5dffdb3747 |
| ui-signed | #133 / #134 | 7ca2b1a7a38f3b3f6f1325c121bb11b025a1c786 / 7c586aee5324ed0aed0a97c310fdab00e025b27c |

Root reported CUA/browser access unavailable. Actual website operations RV01/RV02/RV03/SG04 are not performed. Root asked the user asynchronously to perform ONLY Rebase stack on upper #128; root owns that pending human response. Do not trigger or clean #127/#128 while that handoff is pending. Other prepared fixtures likewise establish no website signing/retention result.

If the user reports completion, root should first read both #127/#128 and timelines/refs, record user evidence and exact method, then collect `lab.snapshot('ui-stale','after-ui')` and `compare.compare('ui-stale','approved','after-ui')`. The `approved` snapshot predates unrelated trunk advancement and is the intended own-layer patch baseline. Do not run `prepare-ui.py after` wholesale: that would collect other unperformed cases under a misleading label.


The bounded extensions are also complete: HC01–HC05 cover actual bot/PAT comment/body effects, permission profiles, cross-author editing and actual foreign marker recovery; MR01 covers three identical-source/actor rule controls. All five history jobs and six matched creation jobs are terminal. The first 25 results, matrix, state and exact receipt-journal prefix are preserved under their `first25` names. No further bot or settings access is needed. Current main target workflow is absent and bot flag is false; only the four reserved website fixtures remain protected. Root owns their manual follow-up.

*Authored by an AI agent acting on joshlf's behalf.*
