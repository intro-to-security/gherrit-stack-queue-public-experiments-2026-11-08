# Refinement after the follow-up experiments

Retain the proposed authoring and reconciliation model, with a stricter local dispatch boundary and an updated evidence account. The experiments do not justify replacing it with a service, a second queue/website engine or a new authoring model. They also do not establish a complete native-workflow replacement: permission to rewrite a surviving suffix after native work remains unresolved.

The deliverable is [Candidate 003](candidate-003.md), SHA-256 `5b0c763bd6a706e88db644dd368013b2f95c7d3882a8ca79fb2febf487f6885f`. It preserves ordinary commits on one branch, canonical PRs, exact authored archives, native membership/landing, one range importer and separate authored, incorporated-hosted and accepted-local revisions. It is a qualified design proposal, not an implemented migration or production acceptance.

## What changed and why

The local probes exposed ways a worker could bypass an already required protocol: recreate missing intent, trust a completed flag without its result, accept another operation's completion, or send twice from cached state. The design now puts ownership, fresh admission, exact identity and retained-result validation at every dispatch/recovery entry. A separate preflight command cannot enforce a worker that bypasses it.

This boundary must preserve ordinary Git editing. Retain the historical accepted result independently of the mutable continuation. An author can amend or rebase normally; the next preparation/recovery captures the new tip and obtains mapping/difference acceptance before recording its attachment and allowing effects. This avoids both a permanently frozen continuation and an unchecked replacement tip.

Received errors need the same evidence discipline as lost responses. Native creates returned 504/502 while creating their intended groups. The original blind retry violated the plan. The design distinguishes a definitely rejected effect from an unknown one; a new evidence label grants no retry authority. These clarifications do not supply provider idempotency or a future-write fence.

The platform findings change support assumptions, not semantic owners. SQUASH differed by tested build concurrency; configured REBASE concurrency two did not deliver two builds. Actual checks/deployments, review records/policy gates and replacement signatures need their own evidence. Three website fixtures retained existing reviews; all four produced eight verified replacements. Actual signed-in upper/middle removal controls returned “Not Found”, with membership retained after each. A separate lower cleanup removed dependents before timeout. No website HTTP status, removal UUID or internal cause was inferred.

## Comparison with alternatives

| Direction | Adjudication |
| --- | --- |
| Keep the incumbent unchanged | Necessary meanings survive, but its implicit enforcement boundary invites the observed mistakes and its factual account is stale. Leaving those duties implicit is not cost-free. |
| Surgical enforcement and evidence updates | Selected qualified direction. A common owner/reload/validation boundary addresses concrete bypass traces without adding another owner or integration baseline. Implementation and verification still cost work. |
| Require one physical custody store | Not selected as a requirement. The incumbent already permits shared storage; no whole-system advantage over a correct implementation was demonstrated. Pending/completed views may be derived from authoritative evidence without mandating one file/database. |
| Broader orchestration, richer authoring, service or CLI delegation | No demonstrated total-burden advantage for this task. A shared runner can enforce the boundary; a framework name alone cannot. Services and adapters inherit provider uncertainty unless they contribute a supported protocol. Lossless multi-commit authoring needs more than the tested flattened net range. |

The retained distinctions have concrete counterexamples. An authored archive at `x=0`, incorporated hosted range at `x=1` and accepted local result containing `y=1` cannot become one current revision before importing hosted `x=2`. An admission receipt that remains `enqueued` after manual removal cannot become one native-success flag. Different stack numbers cannot establish disjoint effects if heads, managed trunks, checkpoints or public targets overlap.

## Review and evidence limits

Three isolated architect priors supplied proposals before synthesis: minimization, generalization/composition and incumbent defense. Root compared their claims and counterexamples under the unchanged C1–C8 contract; their agreement was not an acceptance vote. Three candidate passes used a reused adversarial reviewer, an isolated stitcher and a newly spawned unanchored fresh critic for each candidate.

| Pass | Result |
| --- | --- |
| 001 | Retained the enforcement precision. Reviews required narrower website-review and comparative claims, restoration of the webhook-versus-Actions source distinction, and an explicit ordinary-authoring attachment route. |
| 002 | Those repairs held under the comparative review. No further supported conceptual change was found. The user then completed browser sign-in, allowing the final website experiment. |
| 003 | Only three obsolete website-status passages changed. Reviews found a publication gap; the new reports/index were published and the existing issue #519 link updated. Both reviewers independently rechecked that path without changing Candidate 003. No further supported conceptual change was found. |

The steward authored 20 confirmation cases and 8 reserves before inspecting a design. Pass 001 used 20; pass 002 rechecked 20 and used 8 fresh reserves; pass 003 reused all 28. All concrete premises stayed unexposed to root and architects. Their last dispositions were 9 mapped/restricted, 16 expressly open operational gates, 2 protocol exclusions and 1 partly unsupported original oracle. These are not pass rates. The original overconstrained oracle and bytes were retained; it was not converted into a clean success. The checks are synthetic reasoning traces, not live implementation trials or proofs.

Isolation used private agent contexts and allocated paths on a shared filesystem, without ACL enforcement. Model and effort were inherited; exact effective configuration was not exposed. Full completion-boundary rereads covered model-refinement, swarm-model-refinement, active technical/coordination guidance and the fixed contract. No method or contract changed. Candidate/package checks covered exact identity, issue-size budget, disclosure, whitespace and publication/readback. The large source index was independently retrieved through the Git blob API after a connector size limit, with exact bytes matching the retained copy.

The five original lane indexes contain 130 dispositions, including reuse, negative controls, an unavailable premise and a replaced failed premise. The separate website extension has five grouped preparation/admission/action/cleanup dispositions. Neither count is a number of independent fresh successes. Raw evidence, original reports, failed premises, deviations and corrections remain retained. No production GHerrit code, refs, hooks, settings or executables changed.

## Stopping and delivery

The sequence ends at a **bounded stop**, not full-workflow convergence or production acceptance. No further supported conceptual change emerged in the closing pass, but required operational obligations remain:

- Establish authoritative provider handoff semantics, or explicitly choose and validate a weaker recovery promise, before overlapping suffix publication. The F-before-surviving-B milestone remains gated; perpetual refusal is not a complete replacement.
- Implement and challenge identity/admission, local ownership, retained-result validation, unknown reconciliation, migration, pending custody, old-writer exclusion and rollback. The failed prototypes have not been repaired by this document.
- Select an actual target support/intent profile and validate author/reviewer use. Human comprehension and real machine-power-loss durability remain unmeasured. Finite quiet reads cannot supply the missing provider guarantee.

These limits do not prevent publishing the qualified design and completed evidence. They prevent enabling the full replacement or calling the experiment corpus an all-green acceptance suite. New provider semantics, a concrete weaker contract or an implemented boundary with new counterexamples can reopen refinement.

*Authored by an AI agent acting on joshlf's behalf.*
