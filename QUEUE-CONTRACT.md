# Queue and native-stack experiment contract

This is a proposed bounded matrix for the authorized public synthetic repository
`intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08`. It is not
an implementation or a report that these queue effects have occurred. Retained
source material is public GitHub documentation, API schemas and official CLI
source. No private organization membership or settings evidence belongs here.

## Supported surface and distinctions

Use REST `PUT /repos/{owner}/{repo}/pulls/{number}/merge-async` for native-stack
admission, with the captured selected-head `sha`, explicit
`merge_action: "merge_queue"` and `bypass_rules: false`. The selected PR includes
its open downstack prefix. Avoid `default` routing in the experiment: the schema
allows it to merge directly when no queue is configured. `merge_method` and
commit-title/message options are direct-merge-only; queue merge method comes
from queue configuration. Capture actual landing messages and attribution.
[Primary REST reference](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously).

A 202 response acknowledges background processing; it does not establish queue
admission. Poll its UUID. A 409 identifies another pending request and its
options, which must be reconciled before further effects. The result `enqueued`
is terminal for that UUID and remains an admission receipt after later landing.
Actual landing requires separate PR lifecycle and trunk/ref observations. Poll
results expire 24 hours after their latest update; expiry is not cancellation.
The selected-head SHA is not a lease on all prefix heads or a documented freeze
through the queue's eventual landing. Test the admission guard separately.
[Async result reference](https://docs.github.com/en/rest/pulls/pulls#get-the-result-of-an-asynchronous-merge).

Native documentation says the queued prefix enters in order and removal/ejection
of a lower member also removes members above it. It separately documents queued
and merged members remaining after unstack. Read actual residual membership;
POST unstack can return 200 with survivors or 204 when dissolved. It does not
close PRs or prove queue removal. See [native merging](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests),
[troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-stacked-pull-requests)
and [unstack REST](https://docs.github.com/en/rest/pulls/stacks#remove-pull-requests-from-a-pull-request-stack).

GraphQL `dequeuePullRequest` uses input **`id` = PR node ID**, plus optional
`clientMutationId`; it does not use `pullRequestId` or a queue-entry ID.
`clientMutationId` is correlation, not assumed idempotency. This is queue removal,
not a documented cancellation endpoint for an async request still pending
admission. The inspected REST merge-async surface has PUT and GET, no cancellation
operation. Do not call dequeue and declare an unresolved enqueue request settled.
[Mutation reference](https://docs.github.com/en/graphql/reference/mutations#dequeuepullrequest).

`MergeQueueEntry` exposes ID, position, state, enqueue time, nullable base/head
commits and PR identity. Read both the per-PR entry and repository queue entries;
`MERGEABLE` is a queue state, not a merged PR. `sources/queue-state.graphql`
contains a reusable query; `branch` is unqualified, including any slashes.
`sources/dequeue.graphql` contains the schema-correct removal operation.

## Hold and evidence setup

Use fresh exact trunks and no bypass actors. Require `queue-observe` plus
`experiment/queue-release`, with ALLGREEN, small merge limits and no jump-to-front.
Record the accepted ruleset and effective requirements before admission. Establish
passing required checks on the current PR revision(s), then leave the actual
queue-group SHA's release check missing/pending. Do not post success to every
seen SHA indiscriminately. A head check is not proof a generated group was tested.

For queued/unstack/dequeue fixtures, `max_entries_to_build=0` is a useful optional
pause: current ruleset documentation says it stops new merge-group check dispatch,
and the REST schema permits zero. The general managing guide still describes
1–100, so retain actual acceptance/configuration rather than assuming rollout.
A fresh queue has no previously approved groups to inherit. Group-graph/failure/
landing fixtures need build concurrency at least one and a demonstrated group
hold. Never release a check merely because a fixed sleep elapsed.

A small read-only workflow should include `merge_group: types: [checks_requested]`.
Capture its event payload, `GITHUB_SHA`, `GITHUB_REF`, actual commit parents/trees
and check attachment. The Actions reference defines these as the group SHA/ref;
`pull_request` checks alone do not schedule group checks. `enqueued`/`dequeued`
PR event types may improve the trace, but event receipt does not replace state
reads. [Actions event reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#merge_group).

## Bounded discriminating matrix

Use three disposable native fixtures, each with two members except the first's
third unqueued suffix. Ordinary queue controls can run separately. Each mutation
gets one durable intent and receipt; do not blindly replay an unknown write.
Observe each transition for a bounded interval, recording a timeout as a limit.

| Case | Controlled transition | Discriminating observations |
| --- | --- | --- |
| A1: selected-SHA admission control | On A–B–C, request B with a deliberately stale valid SHA, resolve its UUID, then use captured current B SHA only after the first intent is settled. | Exact rejection/failure versus admission; no assumption a 202 or request echo validates the head. Capture every prefix head and trunk even though only selected B has an API guard. |
| A2: admission versus landing | Admit B while group release is held; C is intentionally outside the requested prefix. | UUID `enqueued`; A/B queue-entry identities/order; C's actual queue state; all PRs still unmerged and trunk unchanged while held. Later poll of the same UUID remains an admission result. |
| A3: queued unstack | While A/B are demonstrably queued and C is open/unqueued, POST unstack once. | Response 200 with locked survivors versus 204; exact remaining group members; C released without closing; all PR bases/heads and queue entries reread. Do not infer removal from the command label. |
| A4: dequeue/cancellation | After admission is terminal and entries are observed, dequeue A using its PR node ID. | A removal and native-dependent B removal; queue empty or precise residual entry; PRs remain unmerged; old UUID still `enqueued`. This tests queued removal, not cancellation of pending admission. After confirmed removal, a separate eligible-unstack may dissolve residual membership. |
| B1: automatic lower-failure ejection | Fresh D–E, both admitted and held. Report failure on D's exact current group SHA/context while E's release remains held. | D/E entry disappearance and timeline reason; original PR lifecycle and trunk unchanged; group recreation/cancellation trace; no manual dequeue mistaken for automatic ejection. |
| C1: successful queue graph and landing | Fresh F–G, capture generated group graph; release only the exact current group checks in controlled order. | Group SHA/parents/tree vs authored heads and trunk; actual landed prefix/full group; per-PR merged times, new trunk ancestry/trees, surviving suffix rewrites. UUID completion alone is insufficient. |

Optional only after those cases: a fresh held pair can test pushing the selected
head after terminal admission. Record queue invalidation/rebuild/landing rather
than treating the request SHA as an indefinite queue freeze. A separate pending-
admission cancellation/race test needs an explicit supported contract; the current
surface does not supply a general cancel receipt. Do not improvise destructive
head/base changes to manufacture one.

## What the trace cannot prove

Capture exact refs/trees; native membership; PR number/node ID, lifecycle and
bases; queue-entry/group identities and configuration; every API receipt, UUID,
expected SHA and timing; check names/conclusions/attachment; event payloads; and
any unresolved intent. Public outputs must contain synthetic/public data only.

Current docs differ on oversized-stack grouping: the merging guide describes
moving an oversized stack to a later group as one unit, while troubleshooting
describes continuation across groups. The official CLI FAQ also describes queue
members being evaluated individually. Small fixtures should record actual states
without claiming queue-wide atomic landing or resolving oversized behavior.
No stress/large-stack test is proposed.

A quiet finite trace, terminal admission UUID, dequeue receipt or matching head
reads does not establish a universal provider handoff against all delayed writes.
Keep acceptance, admission, queue processing, actual landing, suffix rewriting
and future safe publication as separate conclusions.

Primary source excerpts, immutable source identities and SHA-256 values are in
`sources/PRIMARY-EXCERPTS.json` and `sources/manifest.json`. GraphQL was inspected
read-only against the current live schema. REST source commit:
`2f8f80e47ea4d3292cf4e37ba9d9b25475e06140`; documentation commit:
`8cd1075179df75319912891d6620c9cb78eefb4d`; official CLI source commit:
`bd0a32504f9ae9f795875a9e6bb90ff7408fda08`.

*Authored by an AI agent acting on joshlf's behalf.*
