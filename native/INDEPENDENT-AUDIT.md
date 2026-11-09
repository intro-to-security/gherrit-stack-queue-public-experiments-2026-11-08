# Independent native-queue audit

The retained receipts and immutable Git objects support the reported lifecycle,
canonical-identity, archive and per-layer patch facts. Eleven independent checks
pass in `INDEPENDENT-AUDIT.json`. The initial manual-gate cases alone do not
isolate a provider cause for upper-member ejection; a separate ungated SQUASH
control reproduces the same outcome without that gate. No cross-method claim
is established by this audit.

This audit performed read-only Git inspection and public synthetic API/log reads.
It did not change fixtures, refs, checks, queue state, rules or repository settings.
The input hashes in the JSON record identify the exact evidence reviewed.

## Confirmed lifecycle and receipt facts

| Fixture | Initial native prefix outcome | Subsequent explicit operation |
| --- | --- | --- |
| `prefix-happy`, PRs #1/#2/#3 | A/#1 landed; B/#2 left the queue with timeline reason `invalid_merge_commit`; C/#3 remained open. | No B requeue is claimed by this fixture. |
| `fresh-enabled`, PRs #11/#12/#13 | A/#11 landed; B/#12 initially left as `invalid_merge_commit`. | A new explicit request used rewritten B head `21aa39443622…`, a new UUID and confirmed empty prior queue. B/#12 later landed; C/#13 remained open. |
| `late-group-failure`, PRs #15/#16 | A/#15 landed; B/#16 initially left as `invalid_merge_commit`. | A distinct request used rewritten B head `280468446730…`. Its actual merge-group check failed, and the later removal reason is `failed_checks`. |

The three original selected-B request UUIDs still return terminal `enqueued`
after the recorded landing/ejection outcomes. That is an admission receipt; it
does not say every originally admitted member remains queued or has landed.
The B12/B16 requeues are new current-head intents with new UUIDs, rather than
replays of lost original writes.

I independently read B16's public group commit
`3309d1cb9083bd35bd81fe7330cad225f239315e`, its check result and
[run 42545048985](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42545048985).
The run is `merge_group` on that exact SHA and completed failure. Its log reports
the intended `.queue-experiment/FAIL_MERGE_GROUP` marker. Its tree matches the
rewritten B16 tree. Thus the later failed-check case is exercised evidence;
the initial `invalid_merge_commit` ejection is a separate event.

## Content, history and identity

For all three fixtures, PR number, database ID and node ID match their original
creation receipts. Every authored `v1` archive target still equals the captured
authored SHA. Local Git objects confirm each archive's exact captured tree.

For rewritten B/C heads, I compared both cumulative trees and exact binary diff
bytes against their historical parent-to-tip patches. All five checked B/C
layers preserve their own original patch. Their current parents reflect the
hosted landed prefix or preceding rewritten layer. Final trunk trees match the
prefix that actually landed: A for `prefix-happy` and `late-group-failure`, and
A+B after B12's separate requeue for `fresh-enabled`. These checks do not rely
only on the final cumulative tree or a PR's nullable `merge_commit_sha` field.

## Interpretation corrections required in the overall report

**Early build observation.** The original `prefix-happy` data contain 40 no-head
queue observations from 01:11:42Z through 01:13:15Z. The historical `BUILT` label
and `group_built_at` field were not validated build results. The retained
`build-stage-interpretation.json` correctly qualifies them. Later
[run 42544721015](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42544721015),
created at 01:16:46Z, is a successful `merge_group` run on
`964781d850b7c100efbea59663f9eb9d1dfdb971`. The initial no-group interval therefore
does not establish permanent failure to resume after build concurrency changed
from zero to one.

**Sequential snapshot skew.** The first post-A snapshots for `prefix-happy` and
`fresh-enabled` span active suffix rewrites. Their PR reads still contain old B/C
heads while the later `ls-remote` lines already contain new heads. For example,
within the 01:21:52–01:21:54Z prefix-happy snapshot, B's PR read says `54a96f…`
and the later branch read says `36e68a…`. The analogous fresh-enabled snapshot
shows `483d64…` versus `21aa39…` for B. These snapshots are sequences of reads,
not coherent transactions or proof that suffix effects had settled when the
queue became empty.

**Manual gate and the ungated SQUASH control.** The three initial fixtures require
`experiment/queue-release` in addition to Actions. Their initial source-gate
writes target old source/test-merge OIDs, which do not cover the later rewritten
B OIDs. That is a real additional experimental variable; the timeline reason
alone does not identify its causal role.

I also inspected root-authorized public control
`ci/native-no-manual-gate/state.json`. Its SQUASH ruleset requires only
`queue-observe`, bound to GitHub Actions app 15368; it records zero synthetic
status writes, and neither authored head contains either failure marker.
A/#25 merged. B/#26 was removed as `invalid_merge_commit`; its rewritten head
`faabdcba56d4b3fcbcd8e4caa585e797082f0408` then received successful synchronize
[run 42545595057](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/actions/runs/42545595057)
and was observed CLEAN, open and unqueued. The SQUASH observation survives
removal of the custom gate. This rules out that gate as a necessary explanation
for this observed SQUASH trace; it does not identify the provider's root cause
or establish behavior for MERGE/REBASE.

**Failed upper admission.** PRs #21/#22 had CLEAN source checks, while selected
#23's exact source head had a failing required `queue-observe` check. The async
request was accepted with 202, then completed `failed` with the required-status
failure message. The final queue read was empty and the request never returned `enqueued`; owned
refs and all open/unmerged PR identities remained unchanged. The sampled reads
do not establish absence of every transient internal effect. The first runner's required lookup of REST
`merge_commit_sha` was an invalid availability assumption. The resumed source
uses the optional field and directly verified source-head CI. The retained
executor reuses matching acknowledged setup receipts and refuses unreceipted
intents; this audit found no API intent lacking a receipt.

## Limits

The audit supports these finite traces and their stated controls. It does not
establish provider-wide atomic landing, a general cancellation contract, a
completion fence against delayed suffix writes or a safe publication handoff.
MERGE/REBASE controls, broader rule configurations and repeatability belong to
separate evidence. All repository data used here are public and synthetic; no
private organization membership/settings evidence was required.

`independent_audit.py` reproduces the local assertions. Additional public B16
commit/check/run/log reads are retained in `independent-audit-evidence/`.

*Authored by an AI agent acting on joshlf's behalf.*
