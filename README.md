# Native-stack merge-queue experiments

This public repository contains only synthetic data for GHerrit queue research.
The user explicitly authorized this separate public repository in
intro-to-security. Tests use owned exp/** trunks, PRs and rules. Organization-wide
policy and production code, refs, hooks and executables remain unchanged. The
findings are reflected in [GHerrit's design issue #518](https://github.com/joshlf/gherrit/issues/518).

Read [the results and limits](RESULTS.md) first. The three-method native control
found that MERGE landed both queued members, while SQUASH and REBASE landed the
lower member and ejected the upper under the tested conditions. Other controls
captured actual group-check success/failure, partial unstack, queued-branch push
rejection and a dequeue attempt that did not cancel pending admission.

The [publication manifest](PUBLICATION-MANIFEST.json) binds the reports, original
harness source, decisive receipts and downloaded event/context samples. Full raw
HTTP/log transcripts and pinned Git object stores are retained locally by the
coordinating agent. Some report references name that deeper evidence rather than
files in this selected public subset.

The observation workflow records exact PR and merge_group event/checkout data.
An independently posted experiment/queue-release status controls queue progress
without sleeping hosted jobs. Independent native method controls required only
the real Actions check and posted no statuses. All workflows use read-only
tokens; no scheduled workflow or bot approval was enabled.

Final verification observed all twelve owned fixture queues empty and all
seventy listed workflow runs completed. Synthetic refs, PRs, archives and exact
trunk rules remain as evidence. This is a bounded experiment, not a production
GHerrit implementation or provider-settlement guarantee.

Several scripts bind to these exact repository resources and deliberately stop
on a previous unresolved dispatch. Treat them as the record of the executed
campaign. A new hosted run needs fresh, separately authorized fixtures and
explicit ownership.

*Authored by an AI agent acting on joshlf's behalf.*
