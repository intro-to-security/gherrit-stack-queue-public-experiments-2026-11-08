# Provider completion source audit

GitHub documents a completed direct merge and completed queue admission as different outcomes. It also documents automatic suffix rebasing and an ordinary sync-and-push workflow after landing. The sources inspected here do not explicitly connect the last suffix write to a REST UUID's terminal status, or specify how native rewrites arbitrate with a later client write. The retained mismatches establish inconsistent observations; they do not establish a suffix write after terminal success.

This is a discovery audit for the coordinator, not a proposed model or a production gate. C1–C8 require useful repeated work, explicit authority, recoverable uncertain outcomes and calibrated claims. They do not independently require the incumbent's strongest promise that every possible delayed native write be proved impossible before any overlapping publication. Whether a particular supported completion/read/recovery contract is sufficient remains an adjudication question.

## Source identity and scope

Fresh read-only checks at approximately 2026-11-09 06:07 UTC found these current `main` commits, each equal to the retained November 8 source identity:

| Official repository | Current commit |
| --- | --- |
| `github/docs` | [`8cd1075179df75319912891d6620c9cb78eefb4d`](https://github.com/github/docs/commit/8cd1075179df75319912891d6620c9cb78eefb4d) |
| `github/gh-stack` | [`bd0a32504f9ae9f795875a9e6bb90ff7408fda08`](https://github.com/github/gh-stack/commit/bd0a32504f9ae9f795875a9e6bb90ff7408fda08) |
| `github/rest-api-description` | [`2f8f80e47ea4d3292cf4e37ba9d9b25475e06140`](https://github.com/github/rest-api-description/commit/2f8f80e47ea4d3292cf4e37ba9d9b25475e06140) |

The exact pinned file URLs and Git blob SHAs are in [current-sources.json](current-sources.json). The rendered REST endpoint documentation was independently read during this audit. A full raw OpenAPI fetch exceeded the web tool's size limit; that is recorded in the receipt. Current source identity was checked once, not continuously.

I read the focused contract, original C1–C8, the authorized incumbent `candidate-003.md`, the retained primary source files, and the evidence identified below. I did not read sealed cases or competing architecture proposals, run tests, or mutate native resources, settings or fixtures.

## What the provider actually promises

| Boundary | Exact source and bounded wording | Supported reading and limit |
| --- | --- | --- |
| REST request completion | [REST async result](https://docs.github.com/en/rest/pulls/pulls#get-the-result-of-an-asynchronous-merge): “Once the asynchronous request completes”; `merged` means “The pull request was merged into the base branch.” | This is a positive completed-request outcome, not merely acceptance. `enqueued` is a final admission result; it stays unchanged after later queue landing. A new request's 202 only accepts background work. The source does not name suffix-rebase completion as part of that result. |
| Requested stack prefix | [API/webhook overview, Merge API](https://github.com/github/docs/blob/8cd1075179df75319912891d6620c9cb78eefb4d/content/pull-requests/reference/stacked-pull-requests-apis-and-webhooks.md#merge-api): “A stack merge request is atomic”. | It expressly promises that the requested group merges or enters the queue together, or none does; the group includes the selected PR and its downstack members. That is a narrower claim than atomic suffix rewrites, cross-resource read snapshots or arbitration with later client writes. |
| Automatic suffix work | [Merging guide](https://github.com/github/docs/blob/8cd1075179df75319912891d6620c9cb78eefb4d/content/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests.md#merging-from-the-bottom-up): “After the merge, the next unmerged pull request is automatically rebased”. | The next surviving PR targets the trunk and becomes the bottom layer. This promises an automatic result and supplies the intended repeated workflow. It does not say whether the merge UUID is withheld until that rebase's final ref/base write, or identify an additional completion token. |
| Website rebase | [Managing guide](https://github.com/github/docs/blob/8cd1075179df75319912891d6620c9cb78eefb4d/content/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests.md): “Force-pushes each rebased branch to update the remote.” It then says, “After the rebase completes”. | The button starts a bottom-up cascading rebase of every unmerged branch onto the latest trunk. At completion PRs reflect updated branches and CI retriggers. The source names no public receipt, UUID, cancellation operation or machine-observable completion protocol for this button. |
| Later ordinary client work | [Managing guide, local sync after merges](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests#syncing-your-local-environment-after-merges) | GitHub explicitly directs users to sync after a bottom-layer merge; that flow fetches, advances the trunk, rebases and pushes remaining branches, and syncs PR status. The same guide describes force-with-lease for rebased branch pushes. It therefore supports a normal post-merge updating workflow. This is not an explicit native-writer CAS or a guarantee covering arbitrary simultaneous writers. |

Do not downgrade direct terminal `merged` to queue-admission semantics. Conversely, do not upgrade `enqueued` to landing, all-PR finality or write permission. Lifecycle, imported range and authority for a later overwrite are separate questions even when the previous request's outcome is known.

Two additional source qualifications matter:

- The [official CLI Merge API reference](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/docs/src/content/docs/reference/merge-api.md) reinforces the atomic requested-group promise and describes direct `merged` as a stack merge, while directing queued callers to track the queue's final outcome. This is official public documentation, not inspected server implementation. Its bypass/auto-merge limitations also differ from newer REST options and must not be generalized into a rollout contract.
- The [troubleshooting guide](https://github.com/github/docs/blob/8cd1075179df75319912891d6620c9cb78eefb4d/content/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-stacked-pull-requests.md#merging-stopped-partway-through-the-stack) describes a partway failure leaving lower PRs landed and upper PRs open. It does not bind that example to one direct async request, queue processing, or repeated requests. This is conflicting/underspecified official guidance, so the atomic-prefix promise should be recorded with that qualification, not erased or promoted into an unconditional all-path guarantee. Lagging PR flags alone do not refute atomic Git landing.

The inspected [`merge_async.go`](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/internal/github/merge_async.go) is a client wrapper: it decodes four statuses, tests `merged` and `enqueued` separately, submits the request and fetches results by UUID. It neither implements the server rewrite nor checks a suffix completion generation. This client representation preserves per-request status semantics; it cannot reveal a hidden server CAS or prove native settlement.

## What the retained observations establish

The exact local paths, hashes and compact field extractions are in [retained-evidence.json](retained-evidence.json). These are exposed discovery traces, not new or blind confirmation.

**Concurrent observer trace.** In `experiments/native-stacks-2026-11-08/api/evidence/observer-detailed-samples.json`, cohort 8 polled terminal `merged` during 23:24:22.593665–22.816768Z. Its D PR GET ran during 22.598389–22.993028Z and returned old head `e6551ba6aff3ac8a38ca73c2efec749a3de76257`. A later ref observation recorded at 22.995235Z returned `c65becf7b6ba738ae20a9e74cef493b23f1b55df`. The next cohort's PR GET agreed with that new ref.

The overlapping intervals do not order the PR read against the internal write. The new ref could already have existed while a PR projection lagged, or the write could have progressed between reads. This proves that this cohort could not be treated as one coherent range snapshot. It does not prove that a ref write happened after the terminal response, that Git landing was partial, or that a later client update would be overwritten.

**Strictly subsequent mismatch.** In `experiments/native-stacks-2026-11-08/local-git/hosted-integration/evidence/terminal-versus-head-ref-mismatch.json`, the direct squash request's terminal `merged` response ended at 23:21:38.842657Z. B's later PR GET ran during 39.184033–39.581906Z and reported old head `f15cb29aac3b8740374c2fa3c4239cdcd5ab58f0` with the new trunk comparison base. A subsequent `ls-remote` returned `933e62a007da8cc6131e683774a34bddf644af55`; its bounds were after 39.894195Z and before 40.049230Z, without an exact command timestamp.

This establishes that the PR read began after terminal success. It still provides no authoritative old ref read at the terminal instant. It therefore establishes post-terminal observation inconsistency, while leaving cached/projection lag and progressing writes unresolved. The two B trees were equal, but the parent changed; using the old tip with the new base would still misidentify the range.

**Website rebase traces.** The four `ci-reviews/evidence/ui-*-user-ui-results.json` records retain human-attested button actions and independently verified effects on eight commits. Their initiating receipt/UUID and website-feedback fields are null. The stale-review example records replacement lower/upper heads, unchanged own-layer patches, and PRs still open in the same native group. These traces support that actual website rebases occurred. They cannot identify a completion signal that was never captured, or transfer REST UUID semantics to that button. Signing/approval observations are separately bounded to the captured fixtures.

**Unknown transport outcomes.** `protocol/RESULTS.md` retains fully sent requests with no HTTP read and natural 504/502 responses that produced effects. Those make unknown client outcomes concrete. They supply no post-terminal timing evidence because the cut clients never received terminal outcomes. A positively attributed result in a fresh sole-controller fixture may settle the requested effect without proving future-write exclusion in a multiwriter domain.

**Selected-head race.** `api/RESULTS.md` reports the old requested B revision landing while a later exact-lease B update remained on the now-merged PR head. This establishes that the request was not an indefinite freeze of the live branch. It does not establish an all-prefix snapshot or prove a breach of the REST cancellation wording: acceptance, server execution, the later push and terminal reporting are different events. The audit did not reconstruct an internal execution boundary the trace cannot expose.

## Missing premises and discriminating questions

The sources leave these narrower questions open. They are separate from choosing a representation or deployment architecture:

1. **Direct completion scope:** does terminal `merged` include completion of every automatic suffix head/base write initiated by that request? If not, what supported signal identifies those writes' completion? The current docs establish requested-prefix outcome but do not explicitly bind the suffix boundary.
2. **Native arbitration:** if a client makes a leased write after observing the native result, can an older native rebase overwrite that client write, or does the provider compare the suffix's expected head? No inspected public source supplies either behavior. Force-push wording alone proves neither unconditional overwrite nor CAS.
3. **Read usability:** which read/ref combination identifies the exact hosted range to import after terminal success, and what should a client do when PR projections lag? The mismatches establish a concrete invalid-input case. They do not require a global future-write proof before read-only import into preserved scratch state.
4. **Website completion:** what supported UI/result evidence binds the button's captured scope and successful completion? The current guide defines the effect but the retained observations do not capture the initiating response or completion feedback.
5. **Promise required by a future candidate:** is the candidate promising no possible late overwrite, or retained inputs with bounded detection/recovery under a declared collaboration domain? The former needs a provider lifecycle/arbitration premise. The latter needs a concrete usable protocol and its consequences assessed under C1–C8. Neither follows merely from the word complete, nor is either disproved by projection lag.

A future candidate can close one of these questions by supplying an authoritative scope/completion/arbitration promise, by showing its protocol does not depend on the missing premise, or by stating and validating a weaker recovery promise within the fixed contract. More quiet samples alone cannot establish an absent universal fence. This audit does not choose among those directions or make the incumbent's gate mandatory by repetition.

*Authored by an AI agent acting on joshlf's behalf.*
