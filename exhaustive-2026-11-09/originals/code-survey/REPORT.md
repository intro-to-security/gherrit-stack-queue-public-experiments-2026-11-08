# Native Stacked PR client source survey

The inspected native-stack and async clients supply no provider promise that
direct-merge terminal success fences every later suffix write. Client
implementations reveal useful controls and assumptions. The most
consequential new avenue is an explicit native stack-rebase job with an expected
head map in Microsoft's VS Code extension. Separately granted numeric and named
REST initiations each returned 404; availability and arbitration remain
capability-limited. Static traced client calls do not establish successful
deployed API use. This survey executed no third-party source and sent no external
message.

`CASE-PINS.json` fixes all 15 repository revisions. `SOURCE-MANIFEST.json`
records exact retained UTF-8 bytes, SHA256, Git blob identity and available tree
cross-checks. `files/` retains implementation, caller, test and license sources;
`receipts/` retains public metadata, pinned trees, searches and unsuccessful
retrievals. Search results identify candidates, not implementation facts. No
claim here treats an agent walkthrough or client test as human workflow evidence.

**GitHub CLI routing.** At the inspected core revision, `gh stack` is registered
as the official `github/gh-stack` extension. Core's ordinary PR merge path uses
GraphQL `mergePullRequest`/auto-merge, with optional `--match-head-commit` binding.
The core source search returned no `merge-async` occurrence. This is a bounded
revision-specific result, not a claim about every future CLI build.
([registry](https://github.com/cli/cli/blob/736c68f674113337685e3eb1f908602a03b8f99b/pkg/extensions/official.go),
[official command stub](https://github.com/cli/cli/blob/736c68f674113337685e3eb1f908602a03b8f99b/pkg/cmd/root/official_extension_stub.go),
[core merge dispatch](https://github.com/cli/cli/blob/736c68f674113337685e3eb1f908602a03b8f99b/pkg/cmd/pr/merge/http.go))

| Client and actual call path | Selected-head and operation binding | Completion/follow-up observed in source |
| --- | --- | --- |
| [Official gh-stack](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/internal/github/merge_async.go), `cmd/merge.go` → REST adapter | Sends method/action for the selected PR number; its request model has no `sha`. 409 becomes an existing-request error. | Polls the retained UUID; distinguishes merged, enqueued and failed. A poll error stops waiting. `sync` is a separate fetch/rebase/atomic explicit-lease push operation. Our actual v0.3.0 hosted control exercised that sync path. |
| [Microsoft VS Code PR extension](https://github.com/microsoft/vscode-pull-request-github/blob/8bd445fbeee54d7fbb54b2712b29baa3de9356e5/src/github/pullRequestModel.ts#L568), `mergeStack` | Binds the selected top PR's fetched SHA and explicit action/method. A pending 409 is followed without comparing returned head/options; its parser drops those fields. | Polls every 3s for up to 5min; returns merged/enqueued/pending separately, then invalidates stack views. Local branch synchronization moves a branch only if it still equals the captured old head. |
| [Orca](https://github.com/stablyai/orca/blob/41867a2a85e6a0d3dd616472c62da6aaa58e129c/src/main/github/client/merge/merge-pr.ts) → native async adapter | The real caller supplies REST `headRefOid`; helper accepts an optional SHA. Error stdout can yield an existing pending UUID without head/options comparison. | Helper returns `{ok:true}` for merged or enqueued. Polling retries transient read failures; 180 pending polls produce an in-progress message. Reviewed path invalidates PR lookups, without a suffix-write fence. |
| [GitButler](https://github.com/gitbutlerapp/gitbutler/blob/523a411cebe4c1ce90cbf2555033160a51b1c9f6/crates/but-github/src/client.rs#L814), `pr::merge` → client | A synchronous 403 mentioning async merge triggers fallback. Its merge body has title/message/method, without SHA; 409 follows the existing UUID without option comparison. | Merged and enqueued return success; polls up to 300 times, failing on read errors. Separate real review code releases native membership before flattening reordered bases, snapshots restorable open memberships and re-registers after successful publication. |
| [Clinic](https://github.com/r0adkll/clinic/blob/0ba6f76c5d958714800cafa430a27a27a8429dbd/Packages/ClinicCore/Sources/ClinicCore/GitHub/GitHubService.swift#L275), PR page/store → service | UI passes the read PR head; service allows nil SHA. Decoded pending response can be followed after a nonzero command exit, including 409; the result model retains no expected head/options. | Distinguishes known statuses internally; merged/enqueued finish its wait, failed throws. 2s/180s bounded polling; no client suffix publication in the inspected merge path. |
| [GitLens](https://github.com/gitkraken/vscode-gitlens/blob/0cf8a5a76ed1bf350758cd679de61743b475cddc/packages/plus/git-github/src/api/github.ts#L6184), provider → native adapter | Required captured head SHA; 409 recovers only the existing UUID, without comparing its options. | Treats enqueued as transitional, continuing the same UUID for up to 300 polls at 2s. This differs from clients that switch to PR/queue state after admission. |
| [git-spice](https://github.com/abhinav/git-spice/blob/6e4c15a860f9c0e22532022ec6e9e10ffdc0f29b/internal/forge/github/merge_range.go) → forge adapter → gateway | Reloads all selected heads/bases and verifies the exact lowest open native prefix; explicitly calls these observations nontransactional. Server request binds only the top SHA. Gateway admits 400/409 result envelopes and retains their UUID, not returned option details. | Merged/enqueued mean the async operation is accepted; caller then observes change state. This avoids treating queue admission as completed landing. |
| [Git Stacks desktop](https://github.com/howarewoo/git-stacks/blob/777760d2ab07681f9ecd0e46a3c6f97df8827bd5/apps/desktop/src/main/stacks.ts#L7063) → async adapter | Required reviewed SHA/action. Caller rejects a 409 when provided expected-head/action/method fields mismatch; missing fields do not trigger those checks. Retains intent/observations and UUID for resume. | Bounded polling returns still-pending explicitly; records queue observation separately. Live-test source includes lost-response and queue scenarios, but that source is not a hosted run receipt. |
| [electron/trop](https://github.com/electron/trop/blob/450c9687627676e02eb2e280167be0e8f074ccbf/src/utils/stack-util.ts), webhook/backport callers | Reads native stack membership and derives the effective trunk/top PR. It is an actual native consumer, rather than a DTO-only match. | Before backporting a top merge, rereads lower PRs up to three times at 3s intervals and refuses an unmerged member. It does not initiate native merges or fence suffix writes. |
| [ghsync](https://github.com/ewhauser/ghsync/blob/730113d924864059b28841d20c222b8f171b4af3/internal/gh/rest.go#L431) → refresh handler → optimistic store | Actual native List/GetStack reader with conditional ETags and store observation generations. Replay's derived stacks are fixture machinery, not the client proof. | A read-only mirror: local transactional/generation controls protect its projection from stale workers. They cannot keep external GitHub refs unchanged. |
| [go-github](https://github.com/google/go-github/blob/a58c726601628c9134d5e37182a2ed98942d2239/github/pulls.go#L583) | Actual typed PUT/GET wire methods; optional SHA and returned expected head/options are exposed to callers. | Caller owns polling, queue tracking and ownership checks. Its local HTTP tests verify request/response plumbing. |
| [Octocrab](https://github.com/XAMPPRocky/octocrab/blob/c2ede077f77d6b64a0bdd4b6e78e0a4714fc54e2/src/api/pulls/merge_async.rs) | Actual builder sends optional SHA/method/action/bypass fields; no automatic adoption/poll loop in the builder. | Separate result lookup. The file named integration tests uses Wiremock, so it is not evidence of current hosted behavior. |
| [Turso merge script](https://github.com/tursodatabase/turso/blob/bc9d27537b5e7f71bedcb3535697034c2d6f8bca/scripts/merge-pr.py#L223) | Calls merge-async with merge method and custom title/message, without SHA. | Polls pending UUIDs within a monotonic deadline; prints queue admission separately. This is an actual async call path, not evidence of an application-wide native-stack custody protocol. |
| [OpenClaw merge owner](https://github.com/openclaw/openclaw/blob/245cbaf915c21c6cc02ba2edbe3c62e2725a133e/scripts/pr-lib/merge-rest.mjs#L1018) | Uses merge-async with a retained body and selected SHA; refuses a native `stack` at dispatch. A 409 asks for reconciliation instead of adoption; pending options are checked. | Included as a boundary case: a real async API consumer that explicitly declines native-stack landing. It must not be counted as an implementation of that workflow. |

**The new explicit-rebase surface.** The actual VS Code
[GitHubRepository implementation](https://github.com/microsoft/vscode-pull-request-github/blob/8bd445fbeee54d7fbb54b2712b29baa3de9356e5/src/github/githubRepository.ts#L1219)
reloads the expected ordered PR membership and sends
`expected_head_oid_by_pr_number` to
`PUT /repositories/{repository_id}/stacks/{stack_number}/rebase`. It polls the
same route and parses `job_state` plus per-PR status/before/after. Unknown states,
missing result arrays and per-PR conflicts fail explicitly. Its
[tests](https://github.com/microsoft/vscode-pull-request-github/blob/8bd445fbeee54d7fbb54b2712b29baa3de9356e5/src/test/github/pullRequestModel.test.ts#L1346)
cover pending/409, changed membership, timeout and partial conflict using mocked
Octokit responses. Comments describe responses the author observed; they are not
a retained hosted trace or provider promise that the map arbitrates every later
automatic writer. Separately granted numeric and named initiations on the same
owned fixture each returned 404; read-only route/header/version diagnosis and
final Git/PR observations are retained. No vector-enforcement test passed.
`rebase-probes/RESULTS.md` preserves the distinct requests and their limits.

**What the test evidence supports.** Official gh-stack uses stub transports and
mock client command tests. VS Code uses mocked Octokit/Git adapters. Orca uses
mocked command runners and fake timers. GitButler's async test runs a scripted
local TCP HTTP server, including a 409-follow case. Clinic separates its poll
loop for injected sleep/results. Trop mocks the API. ghsync includes fake GitHub
and conformance/database machinery. go-github uses a local HTTP mux; Octocrab uses
Wiremock. git-spice has VCR record/replay integration infrastructure and
live-update credential mode; Git Stacks has explicit live-scenario source. No
third-party tests were run here, and no current hosted pass or future semantic
guarantee is inferred from those designs.

**Further discriminators.** The numeric-repository capability probe used a
complete matching vector and returned 404. A feature/permission/token-class or
enrollment distinction remains unresolved; source-supported status alias reads
also returned 404. A separately reviewed named initiation with fresh complete
vector and canonical identity checks also returned 404.
Stale-vector, conflict and overlap controls remain unperformed and conditional,
rather than passing tests or negative controls.
The requested read-only queue discriminator is now exercised: at 14:39:38 UTC,
the original UUID for controlled public PR #29 still returned `enqueued`, while
fresh PR reads showed both members #28/#29 already merged at 01:34:12 UTC.
`queue-receipt-check/RESULT.md` and its raw responses retain this observation.
This discriminates GitLens's ticket polling from PR/queue-state tracking without
another queue write. Existing
campaign evidence that a 409 names the original options already challenges blind
operation adoption; another broad hosted merge matrix would add little.

Client comments in Clinic, Octocrab and Git Stacks describe pushes cancelling a
selected-head request. That wording also appears in the published
[OpenAPI sha description](https://github.com/github/rest-api-description/blob/2f8f80e47ea4d3292cf4e37ba9d9b25475e06140/descriptions/api.github.com/api.github.com.json).
The precise server execution point is not exposed by these clients or their
mocked tests. The earlier campaign observed the old requested revision landing
while a later selected-head edit survived on the merged PR; that observation
does not by itself date the push relative to the server's execution point.
Neither the documented selected-head condition nor these client paths supplies
an all-member snapshot or post-terminal suffix exclusion token.

**Scope and provenance.** This is a bounded, purposeful survey, not a census of
all GitHub code. Broad text search had unrelated async/merge hits, documentation,
generated models and tutorials; those were not counted as executable clients.
One search was rate-limited and two whole-tree fetches were oversized; retained
targeted pinned directories/files supplied the relevant paths. File-name guesses
that returned 404 were corrected and retained as retrieval limits, not treated
as feature absence. Pins precede later search-index head changes in some repos;
every analyzed file uses its declared pin.

`LICENSES.json` records the retained license paths and metadata. In particular,
GitButler's retained code uses FSL-1.1-MIT; GitLens's inspected paths lie under
`plus` and carry LICENSE.plus, not the root MIT grant; git-spice is GPL-3.0;
go-github is BSD-3-Clause; Octocrab declares MIT OR Apache-2.0. The remaining
inspected project roots retain MIT notices. This report offers behavioral
comparison and source links, not a proposal to copy implementation code.

The source survey, queue read and REST capability diagnosis are terminal. No
external publication or further hosted write was performed. Both rebase requests
have known rejection receipts; no admission or unknown acknowledgement remains
to reconcile. No remaining write, cleanup or background-worker obligation exists
in these scopes. Conditional rebase tests remain unperformed, and finite read
windows do not supply a provider future-write fence. The retained source,
license, request and Git-object evidence remains available for independent audit.

*Authored by an AI agent acting on joshlf's behalf.*
