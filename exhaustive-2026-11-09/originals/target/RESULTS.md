# GHerrit's actual CI/rule profile: bounded reproduction

The current target has an observed first-upper CI route: its unfiltered
`pull_request` trigger scheduled the required Actions context before native
membership. Under the reproduced effective rule profile, direct SQUASH landed
the lower and the rewritten upper received fresh eligible CI; MERGE and REBASE
failed. The producer and current-SHA controls also withheld landing. These are
synthetic minimal-payload observations, not execution of GHerrit's Rust CI or
production acceptance.

The campaign created 17 exact synthetic refs and 11 PRs under two explicit grants.
All five native request UUIDs are terminal: one merged and four failed. The
experiment-created policy was restored to its captured initial absence, with
independent 404 readbacks. PRs and refs remain as evidence: #600 is merged, the
other ten PRs remain open. No queue, production/default-main mutation, global flag,
environment, secret or human communication was performed by this lane.

## The target and the reproduced profile

The retained production GETs are [repo.json](repo.json),
[ruleset-main.json](ruleset-main.json), [protection-main.json](protection-main.json)
and [actual-ci.yml](actual-ci.yml). Main's ruleset allows only squash and requires
linear history, resolved threads and `Validate and Test` from integration 15368.
Its check strictness is false; classic protection additionally enforces admins
and sets the same required context/producer to strict=true. Zero approvals are
required, and required signatures are disabled. Repository flags allow squash
and rebase, while disallowing merge commits. The actual workflow has unfiltered
`pull_request` and no `merge_group` trigger; Windows Tests is separate from the
configured required context.

Four fresh synthetic trunks reproduced both scoped policy sources, including
their different strictness values. [Installed readback](policy-snapshot-installed.json)
and each pre-request snapshot preserve the actual effective settings. The
experiment repository's global merge-method flags were left unchanged, permitting
all three methods; the exact-ref squash-only rule supplied the relevant effective
restriction. The target job's substantial Rust/helper workload was replaced with
[minimal-ci.yml](minimal-ci.yml), preserving the trigger, exact context, Actions
producer and actual event/checkout identities. No conclusion about code correctness,
Windows testing or full CI cost follows from that substitution.

## First publication and activity types

U [#600/#601](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/601)
both received successful `Validate and Test` checks from GitHub Actions app 15368
on their exact source heads before registration. Upper
[run 42634753368](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42634753368)
captured action `opened`. A current native group was not a prerequisite for that
unfiltered-trigger path. Prior failures under explicit trunk filters must not be
transferred to the actual target unchanged.

The matched F branch-filter control initially had a successful lower check and
no upper check. Registration then produced an unexpected useful result:
upper [#603](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/603)
received successful `Validate and Test`
[run 42634983591](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42634983591)
with action `stacked`, although its own workflow had no explicit `types` list.
An independent connected source GET matched exact retained blob
`7896516952097cc09bac4f6d5ba03ad963b65743`.
[F-SOURCE-VERIFICATION.json](F-SOURCE-VERIFICATION.json) binds the source, run and
unchanged upper SHA. This is an observed implicit-types route, not a universal
contract inferred from one run.

A separately granted fresh contrast used
[#639/#640](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/640),
stack #645. Its main CI workflow explicitly listed `opened,synchronize,reopened`
and used the same kind of exact trunk filter. A second, separately named workflow
explicitly listed only `stacked`. Before membership, the lower's main CI succeeded
and upper had no check. After registration, upper's separate
[Stacked event witness](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42637588904)
succeeded with captured action `stacked`, while upper had zero `Validate and Test`
checks. Thus the positive witness distinguishes explicit exclusion from failure
to capture or execute the membership event. Exact workflows, checks and logs are
in [FOLLOWUP-RESULT.json](FOLLOWUP-RESULT.json) and
[explicit-after-membership-run-mapping.json](explicit-after-membership-run-mapping.json).
Finite observation still does not guarantee that no later run can ever appear.

## Amendment, method and producer results

U's same-order upper amendment used an exact old-SHA lease, produced source
`97c7e42ba0ff7c947119e516cff58453e79d5c25`, and scheduled a successful actual
`synchronize` run. The captured lower then landed by direct native SQUASH at
`6b9344bcb9dcb97d942e6f2c995e00f42d4c1f66`. Surviving canonical upper #601
subsequently became `b833ee61b75ad99d7c4015bd61c7149d302d5d43` against its trunk;
fresh [run 42635708790](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42635708790)
passed on that source and its observed gate was CLEAN. An earlier post-terminal
PR read had the new base and old head; it is retained as inconsistent observations,
not proof of a post-terminal provider write or a future-write exclusion fence.
No client source publication followed this landing.

| Probe | Actual terminal result and independent effect observation |
| --- | --- |
| U SQUASH, #600 | `merged`; lower landed, upper remained open with native replacement and fresh eligible CI. |
| M MERGE, #604 | `failed`: “Merge is not an allowed merge method in this repository.” Both original heads/bases remained. |
| R REBASE, #606 | `failed` with the corresponding rebase-method message. Both original heads/bases remained. |
| P same-name user status, #608 | `failed`: required context was not set by the expected GitHub app. The successful user-produced status and wrong-context Actions job did not satisfy the pinned producer/context rule. |
| P new pending head with old green evidence | `failed`: required context “is in progress.” The exact new requested head remained unmerged; its later actual check completed failure and its gate was BLOCKED. |

The method error text is retained literally; it does not identify which internal
policy layer emitted that generic wording. No method-only reliability claim or
queue-method conclusion follows. Thread resolution and zero-review requirements
were configured/read back, not challenged with a new unresolved human thread.
Prior queue, signature and review controls remain separately qualified in
[PRIOR-EVIDENCE.json](PRIOR-EVIDENCE.json): 54 exact historical records are reused,
not counted as fresh target successes. Current target signatures/approval policy
does not inherit the stricter historical fixtures' conclusions.

## Actual tested identity and the stale-read correction

The job logs distinguish the source/check association from the commit checked
out by Actions. For upper's first opened run, source/check head was `9080250…`
while `GITHUB_SHA` and checkout HEAD were `f8d18a5…`. On the native replacement,
source/check head was `b833ee6…` while checkout was `d880816…`. The opened event's
`merge_commit_sha` was null in these captured payloads; the amendment event later
contained an older merge identity than the actual checkout. These optional event
fields were not filled in from later observations. Job/run/check/actual Git tree
bindings are retained separately in the run mappings and object retention report.
No queue candidate was exercised.

The experiment also found an unsafe read premise. Immediately after P's leased
amendment, `wait_ci` returned ready against old green `a740581…`, because it did not
require the returned PR head to equal captured intended `3e44b08…`. That stale
snapshot and frozen source are retained. The merge dispatcher had its own exact
fresh-SHA comparison and sent `3e44b08…`; its refusal therefore establishes a new
pending-head gate, not a completed-failure-at-dispatch test. Later actual
[run 42636022147](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42636022147)
failed on `3e44b08…`, and independent post-request snapshots recorded BLOCKED.

[HARNESS-CORRECTIONS.md](HARNESS-CORRECTIONS.md) explains the failure and its effect
on the claim. [exact_ci_acceptance.py](exact_ci_acceptance.py) supplies a corrected
small boundary, tested against those actual retained stale, green and failed
observations. All five local probes pass, including rejection of the known-bad
returned-green control. This is experimental acceptance code, not production
integration or a claim that the original reader was safe. No hosted request was
repeated to repair the evidence premise.

## Scope, cleanup and audit

The first execution source was frozen before effects and challenged with 24 local
scope/identity/duplicate tests. The fresh contrast has its own immutable manifest,
grant and ten local guard checks. Every request has an exclusive durable attempt
identity, exact inputs, raw response and independent readback; no unknown request
was blindly retried. Native receipts, PR/ref observations, CI eligibility and
future-write authority remain separate. This lane tests a route and client
boundaries; it supplies no provider arbitration or production migration guarantee.

[CLEANUP-AUTHORITY.json](CLEANUP-AUTHORITY.json) binds four unique pre-create 404s,
the exact protection create receipts, ruleset 26858731's prior named absence and
exact four-ref scope, and all terminal UUIDs. [cleanup.json](cleanup.json) records
restoration to absence with post-delete 404s. All PRs and refs were retained.
[REF-RETENTION.json](REF-RETENTION.json) retains exact current readback and fetched
objects for all 17 owned refs, with no mismatch. [OBJECT-RETENTION.json](OBJECT-RETENTION.json)
retains the objects named by runner evidence and compares actual trees with the
logged checkout trees. Source snapshots, command logs, failed premises, job logs
and historical evidence hashes remain in this directory.

Automatic approval review rejected the initial combined PR-close/policy-removal
command before execution. Root narrowed the action to restoring only these
experiment-created controls, retaining PRs and refs. After read-only ownership
and initial-absence proof, the separately reviewed restoration succeeded. The
rejection and resolution remain in [APPROVAL-REJECTION.json](APPROVAL-REJECTION.json).

*Authored by an AI agent acting on joshlf's behalf.*
