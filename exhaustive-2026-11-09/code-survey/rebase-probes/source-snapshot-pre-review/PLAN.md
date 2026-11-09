# Numeric-repository native rebase probes

This proposed lane tests the explicit rebase API discovered in pinned Microsoft
VS Code source. No hosted write is authorized until root grants exact cases.
The only repository is `joshlf/gherrit-native-stack-experiments-2026-11-08`,
expected numeric ID `1450723431`, read back before fixture publication. Branches
are confined to `exh-1109-causal-rb-<case>/{trunk,A,B,C,D,E}`. Every case has its
own synthetic trunk; no main/settings/workflow/queue/browser effects occur.

The source-derived request is
`PUT /repositories/1450723431/stacks/{owned_stack_number}/rebase`, with JSON
`expected_head_oid_by_pr_number` mapping every member PR number to its expected
SHA. The same route is polled with GET. This is a hypothesis about an accessible
provider capability. Client source and mocked responses do not establish it.

| Exact proposed case | Fixture and deliberate request | Required observations |
| --- | --- | --- |
| `capability` | A–B–C; advance only its trunk with a nonconflicting file, then send the complete correct vector once. | HTTP admission, job result, each actual head/parent/tree, PR lifecycle/base and force/base events. If the route/premise fails, freeze this case and do not create the other hosted fixtures. |
| `wrong-lower` | Independent A–B–C/trunk advance; complete map, but A's expected SHA is the valid original trunk SHA. | Whether mismatch rejects admission or yields a failed/partial job; compare every ref, rather than assuming vector atomicity. |
| `wrong-upper` | Independent A–B–C/trunk advance; complete map, but C expects original B's valid SHA. | Whether earlier members change before detecting the upper mismatch. This distinguishes whole-vector admission from per-member checking. |
| `conflict-middle` | Original trunk contains shared=base; A changes only A.txt, B changes shared.txt, C changes only C.txt. Advance trunk with a conflicting shared.txt value and submit all correct heads. | Whether A progresses, B conflicts, C is skipped/changed, or the provider rolls back. Retain per-PR job results and actual refs independently. |
| `overlap-vector` | Independent A–B–C–D–E/trunk advance. After known first pending admission, deliberately send one second request with a mismatched E entry before any completion poll. | Whether the second response is an existing-job 409, validation rejection, or a distinct accepted request. Capture both exact inputs/outputs. If the first had already finished, classify the missing overlap premise honestly. |
| `stale-vector` (conditional later case) | Independent A–B–C. Retain a complete vector, then atomically publish legitimate same-order B′/C′ edits with exact leases and `pull.stacked`; submit the retained older vector. | Whether a formerly valid but now stale observation is rejected, partially applied or otherwise handled. Run only if it distinguishes a remaining hypothesis after the simpler mismatch controls. |

The initial proposed batch is `capability`, `wrong-lower`, `wrong-upper`,
`conflict-middle`, `overlap-vector`, in that order and conditional on the actual
capability premise. Root may grant a smaller subset. This is 17 PRs and 22 new
heads across independent fixtures; `stale-vector` would require another grant.
No failure is followed by an automatic repaired request.

After a successful `capability` job, and only after capturing each changed
head/parent chain consistently, create a unique new marker commit on the top
head and attempt one exact-lease push. Marker generation must start after the
completion receipt. Observe refs, PR projections and events through 60 seconds.
This can detect an actual transition from the new marker; silence cannot prove
a future-write fence. A rejected marker lease freezes that scope without retry.

`job_state: done` and per-PR `status: succeeded` are the initial expected shapes.
Unknown states, missing results, HTTP error bodies and partial results remain raw
evidence. A `done` response does not substitute for actual ref/lifecycle reads or
an all-stack snapshot. There is no assumed per-request UUID: the source polls a
per-stack route, so a later request may complicate ownership of its result.
The overlap case must not invent a correlation identifier that the API lacks.

The new harness will own a private bare Git repository with hooks disabled. It
will record/fsync every exact intended request and fresh scope before dispatch,
atomically retain receipts/state and refuse a repeated write label or existing
case execution. An unacknowledged write freezes the fixture; read-only
reconciliation can continue. Git pushes are atomic with an explicit lease for
every owned target. All mutation endpoints and refs are checked against the
case's durable resource identities. No historical driver or third-party source
will be executed.

Local checks must exercise full-vector construction, correct numeric-repository
and owned-stack binding, wrong-lower/upper construction, refusal of unrelated
refs/settings/endpoints, refusal to repeat an uncertain dispatch, and completion
versus per-PR/result parsing. Source snapshots/hashes and passing check output
must precede the eventual granted dispatch.

*Authored by an AI agent acting on joshlf's behalf.*
