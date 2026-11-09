# Website queue-removal controls

Both upper-C and middle-B website removal confirmations displayed **`Not Found`**, according to the root coordinator's direct browser observations. Independent native reads after each action still showed all three PRs queued. One later, explicitly authorized normal lower-A API dequeue removed all three. These results extend the earlier confirmed-upper/middle GraphQL routing failures; they do not establish a successful upper/middle removal dependency rule.

The fresh fixture used [A #120](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/120), [B #121](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/121), [C #122](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/pull/122) and native stack #123. Its exact trunk is `exp/fu2/queue/ui-removal-20261109a/trunk`, protected only by new rule `gherrit-fu2-queue-ui-removal-20261109a`. Existing queue cases, main, shared workflow, repository settings and original queue reports were unchanged by this worker.

## Preparation and admission

ABC each became CLEAN with real Actions `queue-observe` success and a source-only `experiment/ui-removal-release` success. Preparation stopped with an empty queue until root confirmed an authenticated `joshlf` browser, visible owner controls and an explicit request to admit. The rule used MERGE, ALLGREEN, build concurrency one, maximum merge entries three, minimum one/wait one minute, timeout five minutes and no bypass actors.

The worker then sent one selected-C async admission at exact head `a107cd90fb95f5bcd11d59a3f1599be78c4fbf19`. The recorded API UUID was `9a496f02-2b84-49a4-89dc-820e2a7ab989`; it became terminal `enqueued`, separately from actual A/B/C membership at `05:31:02Z`, `05:31:03Z` and `05:31:04Z`. The worker handed website ownership to root and sent no further native mutation until the explicit cleanup request.

A's candidate `2033840eb934841346734cb6f4510f410fb7dbd2` passed real Actions. The required manual gate had no candidate status, so A remained AWAITING_CHECKS, with B/C QUEUED behind it. No candidate gate was released.

## Website controls and independent consequences

| Control | Root-attested browser action/result | Independent native read |
| --- | --- | --- |
| Upper C #122 | Clicked Remove from queue, confirmed the dialog once; visible `Not Found`; C/B/A still shown Queued. | `2026-11-09T05:32:08.814984+00:00` through refs read ending `2026-11-09T05:32:10.201570+00:00`: ABC still queued, all open/unmerged; source/trunk/archive refs exact; original API UUID `enqueued`. |
| Middle B #121 | Clicked Remove from queue, confirmed the dialog once; visible `Not Found`; B and C/B/A still shown Queued. | `2026-11-09T05:33:54.801155+00:00` through refs read ending `2026-11-09T05:33:56.413101+00:00`: ABC still queued, all open/unmerged; source/trunk/archive refs exact; original API UUID `enqueued`. |

The worker did not operate or directly observe the browser. Root owns the actual browser evidence; `state.json` preserves the attributed action reports alongside independent API/Git reads. The visible text is not reported as an HTTP status, and no initiating website request UUID or internal cause is inferred. Root reported one earlier stale accessibility-element lookup before the upper action, with no click from that failed lookup; it was not a second removal attempt.

The first worker read after the upper action encountered local network denial. That failed read is retained separately; a fresh read succeeded after restoring authorized network access. This was not a provider removal response.

## Cleanup and retained state

After root explicitly authorized cleanup, the worker verified A #120 was still queued and sent **one** normal lower-A `dequeuePullRequest`. Its API call envelope was `2026-11-09T05:33:57.931888+00:00` to `2026-11-09T05:33:59.621662+00:00` and returned a successful GraphQL dequeue payload. No dequeue was resent.

The independent final read began `2026-11-09T05:33:59.626176+00:00` and its Git-ref read ended `2026-11-09T05:34:01.052721+00:00`. The queue was empty; all ABC PRs were open and unmerged; trunk, source heads and all exact authored archives remained unchanged. All three native removal events recorded `05:33:58Z`, reason `manual`, actor `joshlf`. This occurred less than three minutes after admission, and the retained native reasons are manual rather than timeout failures. The original API admission UUID still returned `enqueued` after cleanup.

| Source | Exact preserved head and authored archive |
| --- | --- |
| A | `dedc68f2283419882f05599a1c363fef8ee84786` |
| B | `3aad3a2488ca080d1bd7408337a5bbcb74523345` |
| C | `a107cd90fb95f5bcd11d59a3f1599be78c4fbf19` |

`case-index.json` records UI-Q0 through UI-Q4 and exact evidence paths. `state.json` retains all observations, UUID reads, check attachments, root-attributed browser results and cleanup authority. `evidence/` retains sanitized pre-dispatch intents and receipts. Dedicated source and source hashes remain in this extension directory. No API/Git dispatch intent lacks a receipt.

These controls establish the visible website errors and retained queue membership under this fixture. They do not establish a successful upper/middle removal path, an HTTP error classification, a cancellation contract, or permission for later production ref mutation. Empty queues, coherent refs and a terminal admission receipt remain bounded observations rather than a provider settlement guarantee.

*Authored by an AI agent acting on joshlf's behalf.*
