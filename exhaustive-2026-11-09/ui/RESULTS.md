# Website stack-rebase observations

The website has an explicit, multi-branch rebase job. Three actual button
operations were captured in Chrome's Network panel, with initiation bodies and
per-PR results. The clean job succeeded. A conflict introduced on the trunk after
the confirmation opened left A rebased and B unchanged. A member-head update
while another confirmation remained open was incorporated into the submitted
expected-head map; that trial did not exercise rejection of a stale map.

These observations describe the website on November 9, 2026. Its
`page_data/stack_rebase` and `stack_rebase_status` endpoints are browser
implementation details. No public compatibility or future-write exclusion
promise was found for them. They must not be promoted into GHerrit's supported
API merely because authenticated Chrome could use them.

## Clean completion

The two-member fixture is A [#577](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/577)
and B [#578](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/578),
group 579, on its own advanced trunk. The actual confirmation said that branches
are rebased from the first unmerged branch, each result is force-pushed, and the
operation stops at the first conflict or failed rebase. It also said original
authors are retained and resulting commits are signed by GitHub.

[clean-rebase-network.json](clean-rebase-network.json) retains the selected
sanitized requests. At 14:04:08.394 UTC the browser POSTed a complete A/B
`expectedHeadOids` map. HTTP200 returned `{}`. Status reads reported PENDING,
then RUNNING with A SUCCEEDED/B PENDING, then DONE with both SUCCEEDED at
14:04:11.488 UTC. No request UUID was present in those retained bodies.
The visible result was “Rebasing complete,” with both branches “Rebased.”

[Independent Git/PR/event readback](clean-rebase-final-retry-read-outcome.json)
confirms A `99305ac…` has the advanced trunk as its sole parent and
B `6d26f02…` has that exact new A as its sole parent. Each commit's own patch
equals its original patch. The separate REST commit readback records valid
GitHub signatures on both results. The initiation result alone did not establish
that graph or a durable suffix-write fence.

## Known conflict and conflict after confirmation

For A [#629](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/629)
and B [#630](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/630),
the conflicting trunk was already visible before interaction. The website
offered Resolve conflicts, whose dialog instructed the author to use the
command line and `gh stack rebase`. It offered no Rebase stack button.
No native rebase was dispatched. [The observation](conflict-a-browser-result.json)
and [unchanged exact heads](conflict-a-preflight-refused-outcome.json) retain this
failed execution premise separately from a server-side job failure.

The independent A [#635](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/635)/
B [#636](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/636)
fixture initially had a clean advanced trunk. After its Rebase stack
confirmation opened, one exact-lease push added a conflicting `b.txt` only to
that fixture's trunk. The member heads stayed unchanged. Clicking the existing
confirmation submitted their complete expected-head map without a trunk SHA.

[The actual trace](latent-conflict-network.json) records HTTP200 `{}` followed
by PENDING and DONE, with A SUCCEEDED/B CONFLICTED. The page was reloaded after
the visible “0 of 2 branches rebased” observation. Its refreshed state showed A
Ready, B Not ready and current-branch conflict guidance, without the prior job's
progress panel. The HAR had retained the final job result. This tests recovery
of observable page state, not cancellation: reloading did not roll back A.

[Git readback](stale-vector-latent-conflict-after-outcome.json) confirms new
A `ea6275b…` directly atop the advanced trunk `bc45937…`, while B remained
exactly `595b124…` atop the old A. Both original own patches survived. A DONE
job can therefore have a mixed, incomplete graph. Per-member disposition and
actual refs matter independently of the aggregate terminal state.

## Member update while the dialog is open

The untouched known-middle-conflict fixture A #632/B #633 was repurposed with a
separately recorded trunk update that removed that conflict and retained an
independent trunk advance. The initial inputs and all intermediate commits
remain retained. A clean Rebase stack confirmation was opened, then one leased
push advanced only B to `fb9b179…` with a distinct `late-head.txt` commit.

The website incorporated the new B head into its eventual request map.
[stale-head-network.json](stale-head-network.json) records that exact value,
followed by PENDING, RUNNING and DONE with both SUCCEEDED. This is a successful
live-refresh case. It supplies no evidence that a stale map was rejected or
that a newer member was overwritten; the stale-vector premise was absent.
The [full-layer check](stale-head-full-layer-check.json) confirms that both B commits and their combined patch survived on the new A. The generic reader's one-commit `new^..new` comparison is retained as a raw observation; it is not a valid full-layer oracle for this deliberately two-commit input. Numeric REST mismatch controls have a separate capability dependency.

## Evidence and limits

Only the owned `exh-1109-ui-` trunks/heads and their synthetic PRs/groups were
changed. Merge was never clicked; no queue, production/default-main or account
setting was changed. Every button operation has a retained pre-action intent.
Independent source/ref/patch/event outcomes accompany successful or partial jobs.
The opening known-conflict case used only guidance and produced no job.

Chrome's sanitized HAR exports were further restricted to the exact rebase
request/status paths and safe response headers. Their original copies are
private, mode 0600 under `private/`, and must not be published: unrelated
telemetry can remain in a browser export even when credential headers have been
removed. Public selected evidence includes no cookies, credentials or telemetry
URLs. Operation-local polling and finite unchanged observations do not promise
that no future writer can ever act.

*Authored by an AI agent acting on joshlf's behalf.*
