# What the additional investigation establishes

This campaign closes several capability questions and exposes two concrete
recovery mistakes. It does not establish a general handoff from GitHub's
background suffix work to a later client write. The remaining product choice is
still whether GHerrit requires that exclusion before overlapping publication or
supports an explicitly weaker, validated retained-intent recovery promise.

This is evidence for the design in [GHerrit issue #518](https://github.com/joshlf/gherrit/issues/518),
not a production implementation. No production GHerrit code, PR, setting or hook
was changed. Tests use synthetic repositories and a local recovery prototype.
The detailed lane reports retain exact identities, premises, failures and limits.

## Avenues and dispositions

| Avenue | Result | What remains outside the result |
| --- | --- | --- |
| Primary documentation, schemas, official implementation, issues/discussions and releases | [Source survey](sources/REPORT.md): broad source search found no explicit suffix-write completion or later-write arbitration fence. | Published intended workflows and client assumptions cannot prove that missing ordering guarantee. The user posted [question #622](https://github.com/github/gh-stack/discussions/622) and [question #623](https://github.com/github/gh-stack/discussions/623); neither had comments on the latest read. |
| Causal native writes and ordinary official-client sync | [Eight cases](causal/RESULTS.md): rejected immediate post-terminal leases, an acknowledged pre-terminal marker later rewritten with identical content, an acknowledged post-rewrite marker retained through the observation window, and a successful released-client sync. | No acknowledged post-terminal marker overwrite was observed. Neither that absence nor a quiet window proves that later writes are excluded. Event and PR projections can lag. |
| Core gh, official extension and third-party clients | [Fifteen pinned repositories](code-survey/REPORT.md), with actual callers separated from SDKs, read-only mirrors and mocked clients. Core gh routes the stack command to the official extension. | Client polling or successful examples are implementation evidence, not a provider promise. Blind adoption of an existing async UUID can confuse intents; admission completion can be mistaken for landing. |
| Discovered whole-stack rebase route | [Capability probes](code-survey/rebase-probes/RESULTS.md): both numeric and separately granted named OAuth PUTs returned 404 with fresh complete head maps. A separate [Actions installation-token probe](code-survey/rebase-app-prep/RESULT.md) also returned 404 with actual contents/pull-requests write matching the accepted-permissions header. Ordinary repository/group reads worked. | The proposed mismatch, conflict and overlap cases were not run because initiation capability was absent. The result does not distinguish rollout, token class, enrollment, permission or unpublished route differences, or prove permanent unavailability. |
| Website-only whole-stack rebase | [Actual browser jobs](ui/RESULTS.md): clean success, known-conflict refusal, latent trunk conflict with A succeeded/B conflicted, and a live modal that adopted a newer B head before submitting. | The last case did not exercise stale-map rejection. Private browser routes have no public compatibility promise. A DONE result can describe a partially changed stack, and progress feedback was lost on reload. |
| Public selected-PR rebase and composition | [GraphQL controls](workflow/RESULTS.md): standalone and selected native members rebased; wrong-head/conflict controls rejected; separately guarded B then C updates formed the intended chain. | The [actual B-success/C-conflict continuation](workflow/partial-prep/RESULTS.md) retained B before the separate C rejection. Its original guard incorrectly required associated base OIDs to equal the advanced named parent. Exact historical ranges/current targets are different inputs. These requests do not form a transaction or future fence; responses can contain old projections. |
| Complete staged authoring workflow | [Private and public-F-only traces](workflow/RESULTS.md): publish A/B, land old A, extract and land F, import/rebase and amend canonical B. Two real native import cycles retained pending local work. | This establishes mechanical feasibility, exact source visibility and canonical continuity in those traces. It does not establish a production recovery protocol, a provider handoff, human preference or applicability when F cannot land alone. |
| Actual GHerrit CI/rules and synthetic contrasts | [Target T01–T11](target/RESULTS.md): unfiltered opened runs first-upper CI; implicit/default types received stacked; explicit exclusion did not, with a separate stacked positive control. Squash-only, producer and exact-head controls distinguished eligible checks. | The workload was a minimal reproduction, not GHerrit's Rust CI. A stale-green reader was caught; dispatch independently checked the new head. Queue/other methods still need their own target paths. |
| Local drift, dispatch, custody, transfer and rollback | [Actual Git and bounded model](recovery/RESULTS.md): explicit reset defeats naive three-way restoration; stale/unsafe dispatch mutants are rejected; partial and unknown operations remain distinct. | Injected old effects are client tests, not observations of delayed GitHub writes. Human acceptance of a proposed result is not simulated into a comprehension result. |
| Guest loss and actual completion durability | [Guest report](recovery/vm/RESULTS.md) and [actual counterexample](recovery/vm/protocol-guest/independent-audit/actual-counterexample-001/REPORT.md): stronger JSON controls succeeded, but the actual Git prototype reported complete before two new refs survived the cut. | Original objects survived; recovery correctly refused. The provider was a local emulator sharing the guest. This is not GitHub failure, macOS validation or physical host power loss. All eleven original prefixes now ran: five met expectations and six did not. A separate scoped barrier variant passed all eleven unchanged expectations. See the actual extension report for the failed recovery and exact limits. |
| Actual reviewer experience | The user found the intended v1 exact-patch entry, supplied its URL and the drift filename, then proposed range-diff. [Actual controls](history-range-diff/RESULTS.md) show a useful derived view with binary/context limitations. | The supplied filename has no explicit assignment to both requested roles; no ease or general comprehension judgment followed. Root later explained roles; future same-fixture walkthroughs are informed. |

The [queue-ticket recheck](code-survey/queue-receipt-check/RESULT.md) supplies a
particularly clear distinction: its original admission UUID still said enqueued
long after the corresponding PRs had independently landed. Admission, actual
queue membership, landing and usable suffix state remain separate facts.

## Two failed shortcuts

The first shortcut is automatic restoration from three trees. Suppose an older
input has x=0, the author later sets x=1, then explicitly resets it to x=0.
If an old hosted effect produces x=1, merging the old x=0 input with the current
x=0 intent and new x=1 observation returns x=1. The merge is clean but contradicts
the explicit reset. Retained bytes and a clean merge do not select the author's
intention. Exact drift review can preserve that decision without an additional
path-intent representation; automatic restoration needs more information and a
validated policy.

The second shortcut is treating a live completed result as a durable one. The
actual worker returned complete, then a guest cut left its complete JSON and
receipt intact while the new local continuation and emulator archive were empty
files. Its original Git objects and preexisting retained result survived.
Recovery refused the malformed attachment and sent no second request. Another
ordinary reread before returning would not fix the demonstrated problem: the
original final validation had already passed. Dependencies must be durable before
their durable completion record and successful return.

These failures belong to different boundaries. The reset example challenges the
recovery policy's information and acceptance model. The empty refs expose a
concrete realization's persistence ordering. Neither supplies evidence that a
GitHub native job rewrote a later acknowledged publication.

## What can be relied on, and what cannot

Documented native membership, trunk policy, API outcomes, selected-head
expectations and Git atomicity provide the integration foundation within their
specified scope. The source survey retains exact versions. In particular, the
OpenAPI description does specify cancellation when the selected head changes
between request and execution. It does not make that head an all-member snapshot
or establish the last suffix write. An observed later head and an older revision
landing do not order the push before the merge's actual linearization point.

Successful observations remain observations: the exact Actions trigger paths,
review/signature results, queue graphs, response projection timing, private UI
routes and current third-party algorithms are not all forward-compatibility
promises. A404 is likewise a present capability result rather than a permanent
contract. The [source report](sources/REPORT.md), [code comparison](code-survey/REPORT.md)
and detailed lane reports distinguish these categories at each consequential
claim.

Git's own durability configuration is also version-specific. The actual guest
uses2.34.1; newer component-specific hardening settings were not exercised.
[The source note](recovery/vm/protocol-guest/GIT-DURABILITY-SOURCES.md) links the
official versioned manuals and keeps the loose-ref experimental repair separate
from a portable production backend.

## Why more of the same experiments will not settle the remaining promise

Finite observations can refute a claimed universal behavior or show a route is
currently usable. They cannot prove the absence of every future suffix write.
The positive controls, different direct methods/suffix lengths, actual official
sync and before/after-rewrite markers already distinguish several timing
explanations. Repeating quiet traces would add samples without establishing the
missing provider guarantee.

The whole-stack REST route cannot exercise its conditional cases while both
verified initiation forms return404. The website does expose a current operation,
but calling its private route from GHerrit would substitute an unsupported
integration surface for the missing public contract. Public selected-member
rebases are a useful distinct option; they remain separately fallible effects.

Physical/macOS crash semantics require an appropriate disposable machine and
storage failure domain. This campaign deliberately does not reset the shared
host or another stream's runtime. The bounded guest adds real evidence beyond
process SIGKILL while retaining outer-cache and platform limits.

Human priorities and comprehension need actual people, supported release choices
and implementation walkthroughs. A synthetic test cannot decide whether delayed
dependent review, repeated drift decisions, a service, a hook or a richer history
surface is worth its cost. Those are not unanswered API facts.

## Remaining work and retained evidence

Hosted lanes, their audits and the actual Git prefix/repair experiments are terminal.
The final refinement and curated publication are in progress; STATE.json and
control/ROOT-CHECKPOINT.md name the current owner and frontier. No pending hosted
mutation or temporary target setting remains. Created synthetic refs/PRs,
archives, histories and failed cases are retained.

The public evidence bundle is intentionally curated. Full local evidence remains
available in this workspace. Private HARs, sensitive/private-repository material,
third-party source caches, sealed refinement cases and large guest binaries/disks
are excluded from publication. Lossless guest archives have hashes and restoration
instructions; omitting their bytes from the public bundle does not make them
publicly independently inspectable.

*Authored by an AI agent acting on joshlf's behalf.*
