# Source coverage and limits

This ledger preserves the source-phase retrieval scope. Subsequent [workflow](../workflow/RESULTS.md), [CI/policy](../target/RESULTS.md), [website](../ui/RESULTS.md) and [client-source](../code-survey/REPORT.md) reports resolve some capability questions that were untested during that phase. The user posted [completion](https://github.com/github/gh-stack/discussions/622) and [CI/approval](https://github.com/github/gh-stack/discussions/623) questions; their initial and later readbacks had no comments. Historical source-phase bytes remain in `report-history/`.

This ledger records accessible, discriminating source avenues, not a claim to have read every public GitHub document or proved the absence of an unpublished contract. All writes were local evidence files. No external communication or fixture mutation occurred.

## Classes used

| Class | Meaning |
| --- | --- |
| Published provider statement | Current official documentation/schema/release text, or an explicitly attributed public collaborator statement. It can establish the statement's documented scope, with source conflicts retained. |
| Client implementation | Official CLI code or tests. It establishes client effects and expectations, not hidden server scheduling. |
| User report | Attributed public issue/discussion observations, including self-disclosed AI-written reports. Private underlying traces were not independently available. |
| Hypothesis | A proposed explanation or test premise. No passing result is inferred from its plausibility. |
| Negative search | Nothing answering the narrow question was found within the named query, selection and retrieved surface. It is not an absence theorem. |

## Coverage by avenue

| Avenue | Retrieval and coverage | Finding | Disposition |
| --- | --- | --- | --- |
| Current official source identity | Fresh `commits/main` for docs, gh-stack, rest-api-description; exact raw receipts | All equal baseline commits. | Completed once at retrieval time. |
| REST/OpenAPI | Full pinned 14,206,638-byte JSON downloaded; paths selected by `/stacks` or `merge-async`; all direct references retained in `openapi-focused.json`, plus the ordinary update-branch path | Six dedicated stack/async paths; no dedicated stack rebase/cancel endpoint or suffix generation. Generic ordinary branch-update capability is a separate question. | Completed for the published schema; server implementation unavailable. |
| GraphQL | Live introspection of twelve types: PullRequestStack, Entry, PullRequest, head force-push, automatic base success/failure, added/removed queue, Mutation, UpdatePullRequestBranch input/payload, update-method enum | No suffix-settlement field/operation. Generic updatePullRequestBranch supports REBASE in the public schema; stack acceptance/cascade remains untested. Expected-head wording is ambiguous, while the official CLI passes selected PR HeadRefOid. | Completed for public types; initial nine-alias query rejected by introspection limit, then all nine and three added types succeeded individually. Fresh isolated generic-mutation probe remains actionable. |
| General webhooks | Official push payload and sender documentation; pinned CLI stack-webhook reference | Push before/after/ref/forced support positive transition evidence. Sender may be ghost. `stacked` is membership, not rebase completion. | Completed source avenue; event emission/delivery completeness is not a future-write fence. |
| First publication/Actions | Pinned official Actions guide, its pull_request activity-types reusable, stack CI guide; collaborator answers in discussion 140 and 356 | `opened` has no membership by design. Defaults are opened/synchronize/reopened; stacked absent from published Actions types list. Test-merge SHA differs from head SHA. | Metadata boundary resolved; stacked-trigger dispatch remains an explicit capability question/probe. |
| Website operation documentation | Pinned current CLI UI guide and FAQ, baseline current GitHub Docs retained; exact effect/no-receipt distinction | Effect is cascading force-push. No published website operation token/scope snapshot/completion protocol found. | Completed documentation search; root owns actual website capture. |
| Client implementation | Current merge command/test, async wrapper/test, gitops, sync, init, utils, trunk, submit/syncStack; v0.3.0 comparisons for init/sync/utils/gitops; pinned cli/cli generic branch-update caller | CLI merge returns at terminal status; sync has hosted writes and conditional native-group writes; force producer carries pull.stacked; init argument path is local/catalog plus read-only lookups. | Completed relevant client boundaries; no server code exposed. |
| Client history/reviews | All returned path-history commits for cmd/merge.go (9), merge_async.go (1); PR 307 body, full first review page (32 comments), empty issue comments; PR 562 body/reviews; PR 586/590/596 bodies; docs API-overview path history (2) | Explicit queue routing, local repair and producer changes; no suffix CAS/completion statement. Reviewer bots were not treated as provider authority. | Completed named paths/reviews; private server links in PR 562 deliberately not accessed. |
| Releases/changelog | Entire returned gh-stack releases collection (13 releases, fewer than requested 100); October 1 async GA and October 6 stack GA notices; targeted official-web search | Hosted claims supersede some stale CLI guide prose. No lifecycle/arbitration addition found. | Completed relevant published changes; no universal rollout inferred. |
| Public discussions | All 227 discussion metadata records via three pages, final hasNextPage=false. Titles matching `merg|rebas|restack|sync|approv|trigger|check|CI|Actions|webhook|API|remote|review|force.push` selected 120 threads. Retrieved/text-screened 229 top-level comments and 105 replies with rich IDs/authors/association/URLs/times; all pageInfo false. | 17 collaborator/member/owner statements extracted; lifecycle/body screens retained separately. No suffix completion/CAS contract found. Recent adjacent-line review report and earlier UI/API contrast retained with conflicting timing/version scopes. | Completed stated selection. Unmatched-title bodies were not retrieved; title selection is a relevance boundary, not evidence of absence there. |
| Public issues | Twelve broad gh-stack query receipts, three closed-state queries, docs and REST-repo queries; exact bodies/comments for relevant reports plus merged client-fix PRs | Read/projection, partial-merge, queue, review and first-CI reports. No narrow completion/arbitration answer found. | Completed named queries. Search is indexed/ranked and bounded at 100; no claim that every possible synonym was exhausted. |
| Maintainer clarification | Original drafts in MAINTAINER-QUESTIONS.md; user-posted revised public discussions622/623 | First asks the missing completion/arbitration contract; second asks first-dispatch and producer support. | Posted by the user; no maintainer answer observed on the retained reads. No agent follow-up message authorized. |

## Issue queries

The following repository-scoped queries used `topn: 100`, with no state filter unless stated. Results are saved individually, including normalized bodies. Search result counts are output counts rather than a provider-wide census.

| Receipt | Repository | Query | State | Returned |
| --- | --- | --- | --- | ---: |
| issues-0 | github/gh-stack | suffix | omitted | 2 |
| issues-1 | github/gh-stack | rebase merge | omitted | 58 |
| issues-2 | github/gh-stack | async | omitted | 7 |
| issues-3 | github/gh-stack | overwrite | omitted | 8 |
| issues-4 | github/gh-stack | concurrent | omitted | 5 |
| issues-5 | github/gh-stack | race | omitted | 10 |
| issues-6 | github/gh-stack | head changed | omitted | 12 |
| issues-7 | github/gh-stack | rebase failed | omitted | 29 |
| issues-8 | github/gh-stack | website | omitted | 3 |
| issues-9 | github/gh-stack | ruleset | omitted | 15 |
| issues-10 | github/gh-stack | check required | omitted | 25 |
| issues-11 | github/gh-stack | first push | omitted | 37 |
| ghstack-closed-merge | github/gh-stack | rebase merge | closed | 10 |
| ghstack-closed-async | github/gh-stack | async | closed | 0 |
| ghstack-closed-race | github/gh-stack | race | closed | 1 |
| docs-stack | github/docs | stacked pull requests | omitted | 3 |
| rest-stack | github/rest-api-description | stack merge | omitted | 1 |

Exact counts are machine checked in the receipt index/verification; if this table and a receipt ever differ, the raw retained result controls.

Broad web discovery used `site:docs.github.com "stack" "rebase" "complete" "asynchronous"`, `site:github.blog/changelog "stacked pull requests"`, `site:github.com/github/gh-stack "rebase" "expected" "server"`, and `site:docs.github.com "stack" "force" "concurrent"`. This primarily recovered existing guides, GA notices and issue 519. It yielded no exact arbitration statement. Search-engine indexing is an explicit limit.

## What further repetition cannot settle

The official client and public schemas are not the hosted native writer. Neither another client test with a stub transport nor more quiet ref polls can reveal its hidden scheduling or compare-and-swap. Unanswered discussions and user reports cannot be promoted into a provider contract. The remaining source dependency is an explicit provider answer about affected suffix writes, completion signals, stale-worker arbitration and supported concurrency. A protocol may instead avoid needing a universal fence, but that requires its own bounded recovery promise and evidence.

*Authored by an AI agent acting on joshlf's behalf.*
