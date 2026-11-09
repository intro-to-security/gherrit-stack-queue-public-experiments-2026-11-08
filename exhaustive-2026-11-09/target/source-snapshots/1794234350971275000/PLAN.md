# Actual GHerrit target profile: proposed synthetic reproduction

This lane is read-only until root issues an exact execution grant. It writes
artifacts only in `target/` and proposes fresh personal-experiment-repository
refs beginning `exh-1109-target-`. It never mutates production GHerrit, default
main, repository flags, environments, secrets, queue state or another lane's
fixture. Root owns all rule/protection changes and their restoration unless a
later grant expressly delegates an exact owned-trunk mutation.

The retained production GETs show two concurrent policy sources. The main ruleset
requires squash, linear history, resolved threads and `Validate and Test` from
Actions integration 15368; its required-check strictness is false. Classic main
protection additionally sets required-check strictness true, enforces admins and
requires the same context/producer. Zero approvals are required. Repository flags
allow squash and rebase but not merge commits. Required signatures are disabled.
The actual workflow is unfiltered `pull_request` and has no `merge_group` entry.
Its Validate and Test job runs substantive Rust/helper checks; Windows Tests is
separate and is not the configured required context.

Unfiltered `pull_request` matters: an upper PR's opened event may already schedule
CI before membership. A prior trunk-filter failure cannot establish a first-CI
failure for this target. The new job will preserve the trigger, context name,
Actions producer and event/SHA behavior while using a clearly labeled minimal
payload. It will not run or claim to reproduce the full Rust CI workload.

## Proposed bounded first batch

All fixtures use their own trunk and tiny isolated tree with one workflow. The
base is not main. Hook/global Git configuration is disabled per local checkout.
No fixture exists yet; the initial target-prefix GET returned an empty list.
The concrete names in `harness-outline.json` are reserved for review, not a
license to write. A fresh read and absence leases remain required at execution.

| Case | Fixture and discriminator | Exact observations |
| --- | --- | --- |
| T01 | U: actual unfiltered trigger; open lower A then upper B before native registration. | PR event/run/check IDs, app ID, source/base/merge SHAs and minimal job logs before membership. Require a lower positive control before interpreting absent upper CI. |
| T02 | F: same tiny job with a trunk branch filter, default pull_request activity types. | Matched lower positive control; upper opened and post-membership scheduling. Bound absence with completed observations and distinguish parser/runner delay from missing trigger. |
| T03 | U: register A–B, then amend B at the same order with an exact lease. | Separate membership effects from synchronize runs, exact old/new head and check binding. Retain archived inputs and public source scope. |
| T04 | U: root-applied effective target rules, green minimal Validate and Test, direct native SQUASH of A. | Fresh rule/protection readback, request UUID and terminal result separately from actual A landing, B rewrite/base/lifecycle and rewritten-SHA CI. No client publication overlaps a still-unknown effect. |
| T05 | M: fresh matched pair, same effective rule profile, direct MERGE request. | Expected policy/linear rejection versus actual response and effects. A method error cannot be interpreted as a check/SHA failure. |
| T06 | R: fresh matched pair, same profile, direct REBASE request. | Isolate squash-only policy from linear-history compatibility. Record actual rejection or surprising landing and exact rule readback. |
| T07 | P: ordinary one-layer PR, minimal wrong-context Actions job plus same-name user status at its source SHA. | Wrong producer/context must not silently stand in for required Actions integration 15368. Actual admission attempt and check/status payloads, not a computed green flag. |
| T08 | P: replace workflow with required context and pass, then amend to a known failing tiny job. | Old green/source/merge check evidence must not satisfy the new failing head; capture actual gate result and current run. Each request is a distinct retained attempt. |
| T09 | U/P: map job environment to REST workflow run, check suite/run and fetched Git objects. | GITHUB_SHA, checkout HEAD, source head, PR test-merge SHA, check-run head_sha and required status producer remain separate. No queue candidate claim follows. |
| T10 | Readback and prior-evidence mapping. | Effective policy matches target, while repo flags and minimal workload differences remain explicit. Prior queue/signature/review results are reused only with exact source/evidence hashes and their different conditions. |

The first batch proposes 14 new refs and 9 PRs: four two-layer fixtures U/F/M/R
and one one-layer P. Each job times out in three minutes, case check observations
are bounded to five minutes and native polling is bounded without resending an
unknown request. Further cases require a new recorded discriminator and any
needed grant. No auto-merge or queue is enabled. A synthetic unresolved-thread
probe is not included in this batch; thread policy is configured/read back only.

## Rule reproduction and authorization boundary

`branch-protection.proposed.json` is a proposed classic protection payload for
exact owned U/M/R/P trunks. `ruleset.proposed.json` names only those exact refs
and reproduces squash-only plus the target rule set. Classic protection preserves
strict=true while the ruleset remains strict=false, matching the two captured
sources rather than pretending they are one setting. Root should GET and retain
their initial absence, apply/read back only those scoped settings after the
fixture trunks exist, and restore/delete only the settings it created after
outcomes settle. The F diagnostic trunk remains unprotected.

The experiment repository globally permits MERGE/REBASE/SQUASH. We will not change
those flags. The scoped squash-only rule must therefore establish the relevant
effective restriction; the remaining global mismatch is retained in conclusions.
If the exact scoped profile cannot be installed, policy cases become unavailable
or explicitly different-profile probes, not successful target reproduction.

Before every hosted effect, the eventual executor must validate the grant, reload
the fixture identity and capture fresh state, exact payload/refs and a durable
attempt marker. API errors with uncertain effects stop that scope for read-only
reconciliation. No automatic PR, membership, status, merge or push retry occurs.
Raw readbacks must confirm outcomes independently of the command's return code.

The outline currently has no hosted mutation entry point. After root reviews it,
the executing harness will enforce the exact repo, namespace, owned PR IDs,
rule ownership, accepted methods and one-request-per-attempt boundary. Cleanup
closes only known owned open PRs and retains refs/results until pending outcomes
are reconciled; root restores its scoped policy. Production compatibility remains
an implementation/target acceptance task, not a conclusion from tiny job success.

*Authored by an AI agent acting on joshlf's behalf.*
