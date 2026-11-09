# Maintainer questions and original drafts

The user posted revised questions as [completion discussion622](https://github.com/github/gh-stack/discussions/622) and [CI/approval discussion623](https://github.com/github/gh-stack/discussions/623). Both were read back as open, unanswered and without comments on the first check. Exact posted text is retained in `posted-inquiries-snapshot.json`. The longer drafts below are historical preparation, not additional messages awaiting dispatch.

## Draft 1: Async merge completion and automatic suffix rewrites

Suggested destination: `github/gh-stack` Q&A or a documentation clarification issue, following the project's support policy.

Suggested title: **What completes when a partial stack merge UUID becomes `merged`?**

We are integrating GitHub native stacks with a client that preserves local work and later updates the surviving branches. The [merge guide](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests) says the next unmerged PR automatically rebases and retargets after a partial merge. The [async result documentation](https://docs.github.com/en/rest/pulls/pulls#get-the-result-of-an-asynchronous-merge) defines final direct `merged` and final queue admission `enqueued` separately.

For a linear stack `trunk <- A <- B <- C`, when a direct request to merge A reaches final `merged`:

1. Have all head-ref writes, PR base changes and stack metadata changes initiated by that request for B/C finished? If some may still run or retry, what supported signal identifies their completion and their exact affected refs?
2. Suppose a client then reads B's authoritative branch ref, publishes a distinct new B head with an exact Git lease, and that push succeeds. Can native work from the older request subsequently replace that head? Does the native writer compare its originally expected head, replan against the newer head, skip the rewrite, or fail the operation? Which state/result exposes that disposition?
3. Which read surface identifies the suffix's current import range if branch refs, PR head/base fields or stack metadata temporarily disagree? Is there a supported revision/generation or reconciliation rule clients should use?
4. Does the answer differ by merge method, suffix length, direct versus merge-queue landing, retry/failure path, or the website's Rebase stack button? For that button, is there a supported operation ID, captured starting scope, completion observation or cancellation interface? Does the generic GraphQL `updatePullRequestBranch(updateMethod: REBASE)` support native stack members, and if so does it update just that branch or cascade through the stack? What does its `expectedHeadOid` guard, and what establishes completion of any cascade?
5. What concurrency domain is supported? For example, is ordinary local sync-and-push after direct completion supported when only that client and the native operation can write the managed branches? What changes if another collaborator or a second native operation can write them?

We have observed transient PR/ref disagreement after direct terminal success, but that observation alone does not distinguish projection lag from still-progressing writes and does not prove a later overwrite. We want to avoid inferring a suffix fence from a requested-prefix outcome. An explicit documented completion/arbitration rule, including any weaker supported recovery contract, would let clients implement the intended workflow accurately.

*Authored by an AI agent acting on joshlf's behalf.*

## Draft 2: First stack-aware CI and the official force-push producer

Suggested title: **Supported first-CI dispatch after stack membership, and `pull.stacked` producer semantics**

The [official webhook reference](https://github.github.com/gh-stack/reference/webhooks/) says PRs are created before they join a stack, so `pull_request.opened` never includes stack metadata; `pull_request.stacked` later carries membership. The [stack CI guide](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/optimizing-ci-for-stacked-pull-requests) says workflow branch filters use the stack's base. The public Actions activity-types list does not currently list `stacked`.

For an API/CLI-created three-layer stack whose PRs are created before the stack object:

1. Is `on: pull_request: types: [stacked]` a supported GitHub Actions trigger, or is `stacked` currently webhook-only? If supported, which workflow revision, GITHUB_REF, GITHUB_SHA and branch-filter base does it use?
2. Is stack registration required to re-evaluate or dispatch trunk-filtered workflows for every existing member, or must clients cause a separate event? What supported operation ensures the first stack-aware run without changing the reviewed content?
3. Current `gh-stack` force pushes send `push.pushOption=pull.stacked` ([PR 562](https://github.com/github/gh-stack/pull/562)). What public support contract applies to other clients using this option: its availability, authorization, diff-equivalence check, approval retention and failure behavior? Does the same equivalence rule apply to website rebases and automatic rebases after partial merges?

We will keep head checks, test-merge checks, merge-group checks, workflow/check producer identity and review retention separate. The question is which first-dispatch and producer behaviors are supported, so an integration can request and attribute the correct evidence rather than treating missing membership in an early event as a standalone PR.

*Authored by an AI agent acting on joshlf's behalf.*
