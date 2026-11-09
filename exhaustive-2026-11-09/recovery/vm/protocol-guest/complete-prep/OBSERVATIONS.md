# Read-only summary of the continuation

Eight fresh prefixes ran; `complete` remained NOT RUN. The strict oracle passed
the four `marked`, `request_logged`, `provider_head` and `provider_archive`
unknown-outcome controls. Recovery returned `blocked_unknown_no_resend`, retained
indeterminate state and did not add a request. All four recovery guests recorded
clean unmount and natural exit 0.

The next three prefixes—`provider_receipt`, `acknowledged`, and `result_ref`—
returned `complete` from recovery, but the strict oracle rejected each with
`git_fsck_failed:provider`. Before recovery, Git already warned that the local
provider emulator's `refs/archives/op-case-PREFIX` was broken; provider Git fsck
returned 2. That archive fault remained afterward, while local Git fsck passed
and the exact store still had one request/receipt. The durable receipt allowed
local finalization without proving the provider archive still existed. These
are false completions against the experiment's full contract. They do not show
a GitHub provider failure. The new serial traces show an invalid archive ref;
this summary has not independently read its raw inode bytes.

This differs from the initial `after_return` trial, where the completed record's
local continuation was also broken and the worker correctly refused
`invalid_completed_attachment`. Correct refusal there did not establish a
provider-side archive check on the other recovery paths. Both results expose
the same unestablished durability dependencies at different acceptance paths.

At `result_checkpoint`, replay exposed a broken local continuation and provider
archive while the operation remained acknowledged. The worker attempted to
create the continuation with an expected-zero update, but Git returned 128 because
the reference was broken. This raised `RuntimeError`, emitted `harness_failure`
and produced no `recovery_result` or after-recovery snapshot. The collector
retained both disk archives, classified a nonpassing collection diagnostic and
stopped; it did not retry or run `complete`.

The stored recovery receipt is authoritative: exit 0, clean-unmount target not
reached, `kill_issued=false`, `natural_shutdown=false`, known stopped. Its log
contains a kernel panic. No recovery SIGKILL or clean shutdown is established.
The original cut receipt separately records the exact issued kill and exit -9.

These observations come only from the copied `actual-results-continuation-001`
JSON and serial records. They preserve failed verdicts and do not imply that
fsck exit 0 certifies Git semantics, that default Git ref writes are durable, or
that the local provider emulator establishes native server behavior. Input
hashes are retained in `INPUT-PINS.json`.

*Authored by an AI agent acting on joshlf's behalf.*
