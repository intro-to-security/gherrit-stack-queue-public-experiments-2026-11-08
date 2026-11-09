# Fresh review of the first-client decision model

I found no demonstrated C1–C8 regression in the changes from the supplied incumbent. The supported result is a narrower initial-client default and clearer separation of authorization, request outcomes and local custody. It is not a demonstrated reduction in whole-system cost, a supported overlapping-publication protocol or a production migration decision. The candidate generally states those limits accurately.

## Scope and evidence

Reviewed only the assigned incumbent, candidate, decision addendum and two contracts, plus linked primary references. I did not inspect architect material, coordinator notes, discovery files, earlier reviews or sealed cases. No hosted mutations or executable historical experiments were run.

- Incumbent: `experiments/native-stacks-followup-2026-11-08/refinement/candidate-003.md`.
- Candidate: `outputs/github-native-stack-choice-refinement-2026-11-09/candidate-001.md`, SHA-256 `b61e0a55e72e8cc7361a0edc52c273e9e08e9281f93578c9b7212588ff30fd7b`.
- Addendum: `outputs/github-native-stack-choice-refinement-2026-11-09/DECISIONS-001.md`, SHA-256 `6db7f32a2a0da018121520ea72687d62ea9c86a9d706972b91ac9249fea2e8b5`.
- Focused `CONTRACT.md` and original `GOVERNING-CONTRACT.md`.

For the findings below, C means the frozen candidate and D means the frozen addendum. Line references identify those exact files. I loaded reader-oriented-explanation, williams-style, authorship-disclosure and robust-code guidance; I also read the GitHub skill before inspecting linked source.

## Findings that constrain the result

### 1. The claimed closure is mostly conditional factoring and default selection

D:7 expressly says, “Defaults are not universal dominance claims,” and D:21 says no measured whole-system cost or human preference result is claimed. Those qualifications are necessary. For example, a single enrolled checkout does not preserve a service's multi-client or offline operation, and a comment does not preserve a dedicated view's possible discovery advantages. The decision table acknowledges both excluded benefits at D:15 and D:17.

The valid reduction is that these extensions need not create independent identity, integration or recovery semantics. It does not follow that every extension can be added with a trivial adapter. A service must carry custody and dispatch authority across machines; a hook must supply missing invocation intent; a view still needs hosting and discovery. C:248–254 counts those duties rather than declaring them eliminated. Treat D's “Decisions we can close for this domain” as a first-client scope decision, not a proof that these product choices have ceased to exist.

No correction is needed to preserve that bounded reading. An implementation handoff should keep D:7 and D:21 adjacent to the table; the table by itself would invite a stronger conclusion.

### 2. F-first staging defers joint insertion only by changing when dependent work is reviewed

C:197 and D:42–46 preserve the right restriction: F must be independently landable, B′ remains retained, delayed B′ publication is accepted, and B's later remote-write gate still holds. A concrete reduction is:

1. Hosted A–B exists. Local A′ adds field `f`; B′ uses `f`. Old A lands.
2. F contains only the additional field change, against the trunk containing old A. Retain B′ and canonical B without publishing B′ yet.
3. Publish and land independent F.
4. Import/rebase B′ onto the new trunk, then update canonical B only when the relevant pending effects and write authority permit it.

This avoids publishing a new F–B native group and therefore avoids insertion for that workload. It costs an additional review/landing stage and delays review of the dependent amendment. If F itself requires B′, or reviewers need to assess F and B′ together, step 2 is unavailable; the joint path remains necessary. The candidate says this rather than claiming equivalence.

The public-source caveat at C:197/D:46 is substantive. Exporting the original F–B′ branch would expose B′ even if its canonical PR were unchanged. An accepted F-only export or an explicit broader-visibility decision is therefore part of staging, not merely a UI detail. The incumbent already allowed author-approved staging; the actual change is a more precise release milestone, not discovery of a new topology mechanism.

### 3. The strict gate still prevents a complete repeated workflow on current support

C:211–217 and D:68–75 retain an unresolved premise rather than deriving one from quiet observations. I independently checked the linked [async REST reference](https://docs.github.com/en/rest/pulls/pulls#get-the-result-of-an-asynchronous-merge): a direct `merged` result is a completed-request result; an `enqueued` result finishes admission and remains unchanged through later queue activity. The candidate's new wording at C:140 and C:211 properly distinguishes those meanings.

The [stack merging guide](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests) describes automatic rebasing of the next unmerged PR after a prefix lands. These sources support the intended native continuation workflow. They do not expressly define a last suffix write or arbitrate that write against a later client update. Conversely, PR/ref disagreement alone does not establish that a late write occurred. C:211 and D:62 preserve both limits.

Thus the strict candidate cannot yet claim successful overlapping repetition merely because it has retained inputs or an F-first stage. C:217, C:274 and D:44 expressly prohibit that claim. This is an unresolved adoption condition shared with the incumbent, not a new regression and not a closed design question.

### 4. The weaker-contract counterexamples are valid only with their stated old-writer premise

D:71 gives a real information-loss witness. Let published X contain `x=1`; let an admitted older operation later restore a hosted range with `x=0`. If both the incorporated and local inputs equal X, ordinary three-way integration treats hosted deletion as the only change and can accept it. Retaining an archive proves that bytes survive; it does not decide whether removal is accepted current intent. The proposed weaker protocol therefore needs operation-aware drift handling or explicit acceptance, not just another fetch/import.

The structural witness at D:73 also has a concrete trace. After the client reorders C below B and assigns B's base to C, assume the older native operation can still restore the old B head and then the old C head, with old C containing old B. B's current head can then become reachable from its new base. The linked [indirect-merge reference](https://docs.github.com/en/pull-requests/reference/pull-request-merges#indirect-merges) makes the resulting terminal-review risk credible. Restoring branch contents does not undo a terminal PR lifecycle event.

This trace needs possible restoration of the relevant old heads, not merely stale reads or an old C object existing somewhere. It is a protocol counterexample under the hypothesized overlapping writer, not evidence that GitHub performed those late writes. D:73 and C:215 label it correctly. Same-order operation is not disproved by this reversal witness; D:73 properly refrains from claiming otherwise.

## Tests of the other claimed closures

| Claim and passage | Concrete trace or reduction | Remaining burden / result |
| --- | --- | --- |
| One evaluator/importer across interfaces, D:13; C:148, 250 | A direct merge and a queue landing produce the same canonical hosted B range. The exact-range merge inputs are the same; admission progress remains a separate record. | Shared integration semantics are supported. Receipt acquisition and unresolved-outcome handling remain interface-specific. No second queue baseline is justified merely by queue membership. |
| Opaque hook excluded, D:14; C:250 | Give a raw hook identical destination/ref input for real push and dry run. A deterministic mutating response changes remote state in both; a nonmutating response cannot publish in the real case. | The conditional impossibility is sound. The linked [pre-push contract](https://git-scm.com/docs/githooks#_pre_push) supplies destination arguments and ref tuples, not a documented dry-run discriminator. A wrapper or other explicit intent channel is still a possible extension. |
| Service not prerequisite, D:15 | One checkout holds canonical bindings, retained inputs, pending effects and the local admission/dispatch owner. Adding a server does not change any external native-completion fact. | Local realization is sufficient in the declared cooperative domain. It is not shown cheaper for multi-client/offline use, which the domain excludes. |
| Released broad submit not interchangeable, D:16, 52–58; C:244 | The pinned [push implementation](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/internal/git/gitops.go#L258) emits branch-to-branch refspecs and leases from tracking refs. The pinned [submit implementation](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/cmd/submit.go) refetches before that push. If accepted input incorporated H0 but fetch obtains H1, a lease against H1 alone permits replacing unincorporated work. | I independently inspected those pinned source paths. A GHerrit adapter must preserve accepted expectations and canonical identity, not just invoke atomic submit. Write-ahead archives remove one incompatibility, not this one. No universal direct-API cost advantage follows. |
| Archive versus comment/view, D:17; C:99–109, 254 | Delete or truncate the projection comment. Immutable historical base/tip objects still exist; reconstructing their index cannot be replaced by comment edit history. Conversely, retaining objects alone does not tell a reviewer where to find them. | Exact history and its presentation are separate responsibilities. A bound comment is a default with discovery, size, deletion and unknown-write costs; it is not a proved best reviewer interface. |
| One local commit versus hosted ranges, D:18 | Native rebasing changes ancestry while one authored local change remains one change. A hosted base/tip pair still describes the range without claiming preservation of every intermediate message. | The two boundaries do not compete. Richer authoring still requires mapping and lifecycle policy. |
| Authorization versus request identity, D:25–29 | An accepted continuing goal can allow a second admission after a validated native-only rewrite. Retain the first admission record and subsequent ejection observation; the second request gets a new target/options/outcome record. A one-shot authorization instead requires acceptance again. | This removes an artificial equivalence between new request and new human goal. It does not remove transformation validation, withdrawal handling or unknown old requests. The incumbent's unchanged-input acceptance was already compatible. |
| Local successor versus settlement, D:33–35; C:217 | Pending operation P retains captured checkpoint K. Coherent hosted ranges produce fresh continuation R/checkpoint K2. Keep K and P unchanged; later dispatch of P reloads P's frozen input, not R. | A retained local successor does not require remote settlement. Storage/retention and stale-worker checks remain; replacing K or treating K2 as authority for P would violate the claimed reduction. |
| “Unsafe recovery modes” removed, D:19 | A direct/recovery worker reloads the current operation under the same owner before dispatch. Missing evidence cannot be replaced by fresh arguments to make dispatch admissible. | This enforces already-promised identity and custody; it is acceptance work rather than an independent feature choice. It is not evidence that the current prototype enforces the rule. |

## Equal-contract comparison, including no change

| Contract | Incumbent and refined client | Minimal/no-change and larger alternatives |
| --- | --- | --- |
| C1 | Same one-branch, one-commit linear authoring restriction. Fresh continuations and mapping acceptance remain user costs. | Current code retains familiar hook authoring, but registration alone does not create an importer. A richer authoring backend needs additional mapping rules; base/tip storage alone does not supply them. |
| C2 | Same explicit repository/change/PR bindings and immutable archives. Refinement improves authorization wording without removing revision roles. | No change retains existing discussions but lacks the durable binding described in C:29. New PR generations preserve bytes while replacing review continuity; that cost is counted, not silently accepted. |
| C3 | Same native topology/landing ownership and old-cascade exclusion. | Keeping legacy cascade alongside native writes creates competing ownership. A service relocates authority; it does not by itself resolve that conflict or native work. |
| C4 | Same partial/unknown effect and custody rules. Local successor clarification adds no remote authority. | Registration-only work still acquires lifecycle, CI and old-writer obligations. CLI and service alternatives inherit unknown outcomes. A weaker drift contract changes promised observations and needs its own validated recovery protocol. |
| C5 | Refined staging gives a narrower useful workload, with delayed dependent review and the final B gate explicit. Neither draft has a supported complete overlapping-production path. | No change fails to deliver native import/repetition. Generations can avoid some in-place structural edits but retain old pending operations and fragment discussion. Service/CLI realization alone supplies no new continuation semantics. |
| C6 | Most invariant and implementation burden is unchanged. New wording makes some extension decisions nonblocking; it does not measure a whole-system saving. | No change avoids migration but keeps current hazards. Services add deployment/custody costs and useful capabilities; adapters add version/effect boundaries; write-ahead publication adds attempt/confirmed-export bookkeeping. These are real tradeoffs, not dominance findings. |
| C7 | New direct-completion and projection-lag qualifications improve evidence calibration. Counterfactual lifecycle traces remain labeled. | A released CLI, successful fixture or mock cannot establish an absent provider promise. The comparison does not use current defects as evidence that an alternative is correct. |
| C8 | Both retain adoption, old-writer exclusion and deliberate rollback/handoff. Pending-effect settlement can obstruct rollback, so this is a qualified migration plan, not demonstrated reversibility in every failure state. | No change needs no migration but does not satisfy the requested native design. Archive-protocol or PR-generation changes require their own counted translation and handoff. |

The comparison is complete enough to support the stated qualified defaults. It leaves the provider promise, actual usefulness of the narrowed domain, production enforcement and reversible handoff as explicit remaining work. Those are not failures to choose a command spelling or storage layout; they determine whether a future implementation can satisfy the useful-workflow and recovery obligations.

*Authored by an AI agent acting on joshlf's behalf.*
