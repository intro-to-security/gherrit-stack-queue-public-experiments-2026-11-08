# Native MERGE queue with only real CI

Both native members landed from one selected-B admission. A and B retained their original source head SHAs; the final trunk equals B’s checked candidate. Two-parent merge candidates preserved the original A/B ancestry. B was already building against A’s checked candidate while both PRs were still open.

This is one fresh two-PR fixture, native stack #30, under `exp/ci/native-no-manual-gate-merge/**`. It used the same standard workflow and queue settings as the other method controls except for the queue merge method and unique fixture paths. These are observed method comparisons, not a universal provider rule or a production acceptance claim.

## Configuration and admission

The exact-trunk rule `26822300` required only `queue-observe`, bound to Actions app 15368, with no bypass actors, reviewers, manual release context or failure-marker files. Effective rule readback contains only that context and the queue rule: `MERGE`, `ALLGREEN`, build concurrency 1, maximum merge entries 5, minimum entries 1, minimum wait 1 minute, response timeout 5 minutes. No synthetic status was posted anywhere in this fixture; queried relevant commit-status lists are empty.

Both PRs were `CLEAN` before one selected-B REST admission. The request captured B `3cf43d654b4e916e331f52ec1a625eaae468ba3f`, supplied `merge_action: merge_queue`, omitted `merge_method`, and returned UUID `945dccee-d22e-4ac5-bd6b-a8b222dea397`. Polling reached terminal `enqueued`. There was no request resend, manual source update or explicit requeue.

## Checked candidates and provider removals

| Actual workflow run | Candidate SHA | Exact parents | Tree | Check-run IDs |
| --- | --- | --- | --- | --- |
| [42546148963](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42546148963) | `085c7014c13f3dff3fe9526499915a387778bbe9` | `0a627446b784313ae83efe3f6e66bd74321612ac`, `5c50151deb726233da7e12c837c783bd1b6657c4` | `862bfe524f91558d0898461f3d58920a95b96374` | `128931489295` |
| [42546199671](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42546199671) | `02444078e1e831ce079965c858d146303df4c407` | `085c7014c13f3dff3fe9526499915a387778bbe9`, `3cf43d654b4e916e331f52ec1a625eaae468ba3f` | `88692cc9bd6e0686a964767bd03a94107a8a6194` | `128931638177` |

For each candidate, the event `head_sha`, run SHA, `GITHUB_SHA`, checkout HEAD and required check attachment match. API commit trees/parents match the downloaded graphs, and all candidate checks succeeded.

| Native member | Provider time (UTC) | Removal reason | `beforeCommit` |
| --- | --- | --- | --- |
| A / #28 | `2026-11-09T01:34:11Z` | `merged` | `085c7014c13f3dff3fe9526499915a387778bbe9` |
| B / #29 | `2026-11-09T01:34:11Z` | `merged` | `02444078e1e831ce079965c858d146303df4c407` |

Provider metadata times do not expose a cross-resource transaction order. No source-head rewrite or synchronize run was observed; the original source heads remained unchanged.

## Retained work and final observations

B source head: `3cf43d654b4e916e331f52ec1a625eaae468ba3f` → `3cf43d654b4e916e331f52ec1a625eaae468ba3f`. Its own commit patch, full tree, author name/email/date and exact message are unchanged. Raw binary-diff output bytes match SHA-256 `3f73ae2ef505321515666899d50f5cd68b886b69c77f2fa75e8c00f12862e53e`. Source messages retain the AI disclosure trailer. Exact commit headers, messages, trees, verification objects and both patch files are retained in `frozen-summary.json` and the adjacent artifacts. Original A/B authored archive targets remain unchanged.

The last queue observation ended `2026-11-09T01:38:54.883905+00:00` and has both entry fields null. The final trunk was `02444078e1e831ce079965c858d146303df4c407`. Re-reading the original async receipt still returned `enqueued`, which describes prior admission rather than current queue membership or landing. All actual source/group run artifacts and logs are retained here; raw write intents and read receipts are in the parent CI evidence directory.

The experiment does not establish another build-concurrency/grouping combination, every queue failure policy, provider internals, automatic recovery after an unknown write, or future settlement. No additional landing/requeue decision was inferred from agreeing reads. Shared workflows, main and global settings were not changed by this lane.

*Authored by an AI agent acting on joshlf's behalf.*
