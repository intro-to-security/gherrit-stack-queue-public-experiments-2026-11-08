# A smaller set of GHerrit decisions

This addendum narrows the open-question model for the first native client. It keeps the incumbent's identity, archive, importer and effect protocol. It separates choices that can be fixed for that client from extensions, validation work and the remaining consequential promise. It does not claim a new minimal protocol or a production-ready migration.

The first-client domain is explicit: same-repository linear authoring, one local commit per change, one enrolled cooperating publishing checkout, direct API operations, one-shot landing/admission and a separately owned history comment. Existing discussions and immutable archives remain. GitHub owns native topology, rules and landing; human prose remains human-owned. Remote effects retain their individual scope, guards, receipts and unknown outcomes. The proposed first milestone uses F-first staging and omits general insertion/reorder/drop/fold commands: reject those edits before mutation with inputs retained. The full design describes that later structural extension. A service, second hook/queue/website engine, persistent landing automation or richer local history is not a prerequisite.

These defaults substantially follow the incumbent. The useful change is to stop treating every possible extension as an unresolved architectural fork and to state the narrow continuation milestone precisely. Defaults are not universal dominance claims. Their excluded benefits and costs remain below.

## Decisions we can close for this domain

| Decision | First-client rule | What is actually removed |
| --- | --- | --- |
| Separate command/hook or direct/queue/website engines | One captured-intent evaluator, dispatcher and exact-range importer. Explicit commands are the first entry point. | Duplicate ownership/recovery/integration engines are unnecessary. Interface-specific receipts remain distinct. This preserves an incumbent strength rather than discovering a new reduction. |
| Commands versus an opaque mutating pre-push hook | Require an explicit input/destination/dry-run contract. A future compatible hook is an adapter to that boundary. | The raw hook with indistinguishable dry-run/real input cannot satisfy both outcomes. Familiar push UX remains a possible benefit of a proper adapter; it is not needed to build this client. |
| Checkout versus required service | Implement one local authority for the enrolled checkout and linked worktrees. | A service is not a prerequisite for the declared single-publisher domain, and moving authority would not settle native work. Multi-client coordination or operation while the checkout is offline could justify it later. |
| Direct calls versus released broad CLI submit | Retain the current coupled archive/head/source protocol and use direct typed calls. | Stock broad submit is not an interchangeable publisher under that protocol. A narrow canonical-URL adapter or changed export protocol remains possible, but is not a first-client backend setting. |
| Archive, comment or view as competing history stores | Exact immutable ranges are the history; the bound comment projects confirmed submissions. | A comment or native edit history cannot replace the archive. A later view can read the same history without gaining publication authority. Comment discovery/size/deletion and view hosting are real remaining costs. |
| One commit versus a range-based backend | One-commit local authorship; explicit base/tip hosted ranges. | These concern different boundaries. No lossless multi-commit authoring promise follows from a range type or flattened net-range tests. Richer authorship is a named extension. |
| Which unsafe recovery mode to support | Ownership, fresh admission, exact operation identity, retained results and pending custody apply at every dispatcher. | Correctness is not an optional deployment mode. Storage layout, stale-process tests, migration, rollback and power-loss validation remain implementation/acceptance work. |

This closes first-client dependencies and removes incompatible implementations from its interchangeable options. It does not eliminate the real utility of a service, compatible hook, better reviewer surface or richer history. No measured whole-system cost or human preference result is claimed.

## One authorization rule covers manual and continuing work

Separate the user's accepted authorization from each provider request. Every new request has a new effect record, exact targets/options and its own outcome. Whether it needs a new human decision depends on what the accepted authorization permits.

The first client is one-shot: a replacement selected head or another admission needs renewed acceptance. If future automation expressly accepts a continuing goal and an allowed transformation, a later request may fulfill that same authorization after every authority, range, outcome and readiness gate holds. A native-only rewrite must be validated at each layer; the same ID, running process or cumulative tree is insufficient. Changed authored work or options outside that authorization require new acceptance. Unknown old requests cannot be replayed, and withdrawal stops unsent future effects without cancelling requests already sent.

This removes a false opposition between new request identity and reusable user acceptance. It does not establish that continuing automation is universally better or require its implementation now. The incumbent already allowed unchanged captured acceptance and left automation policy open; this is a precise common rule and a first-client default, not a claim that a new goal engine has been eliminated.

## Local acceptance does not certify remote settlement

A coherent exact hosted range can be imported into a fresh retained local continuation/checkpoint while a native operation remains unresolved. Preserve the old accepted result, each pending operation's captured checkpoint and all unknown evidence. A stale worker must still use its operation's frozen input, not the newest accepted branch. Selecting the new continuation grants no overlapping hosted-write permission and cannot mark an older request complete.

This clarifies what the incumbent already largely allowed. Only the reading that every retained local successor must wait for provider settlement is removed. Destructive custody replacement, missing evidence and changes that manufacture dispatch authority remain forbidden. There is no new provider premise or remote availability claim.

## A staged first milestone can defer general insertion

For published A–B, local A′/B′ and landed old A, derive new-ID F from A's pending delta. Two proposed paths have different costs:

- Joint F–B publication preserves simultaneous dependent review, using the structural parking/regrouping path.
- With explicit acceptance of staging, publish F alone against the ordinary trunk, retain B′ and its canonical B binding, land F, then import/rebase and publish the amended canonical B when its remote-write authority is established.

The staged path lets a named first release defer general insertion/reorder/drop/fold. It is useful for work where F can land independently and the author accepts delayed B′ publication. It does not support joint review through a hidden substitute, and it does not remove the final B handoff question. The normal repeated-workflow milestone must execute the path that release actually claims, not pass by refusing forever.

The plan must retain omitted B and the whole relevant suffix, old operations and exact checkpoints. F's fresh name is not independence proof. Its head, review, checkpoint and public source targets must be demonstrably outside the old possible effects, with actual prefix outcome known. An accepted public F–B′ source export cannot be silently suppressed or described as keeping B′ local; use an accepted F-only export or disclose the broader visibility. No B changes may be hidden in F. If F cannot land independently or reviewers need F and B′ together, staging is inapplicable and joint structural support remains necessary.

The incumbent already offered author-approved staging. The concrete change is to make that path and its first-release consequence explicit, and narrow the contrary blanket statement that every repeated-workflow milestone requires immediate insertion.

## Archive timing and CLI placement are separate comparisons

C1–C8 require exact retained inputs and truthful confirmed history, not one particular archive/head transaction. Coupled publication supplies a strong, convenient Git-level relation and remains the first-client choice. Confirmed write-ahead preservation can also protect the exact authored input before export.

That alternative is not free equivalence. Preallocating vN for rejected attempts changes raw history and version gaps; separate attempt refs plus later confirmed aliases add identity and fallible effects. Prearchives prove preserved input, not that a later head export occurred. Optional public source/head atomicity also needs its own policy. Old vN targets must stay immutable and their meaning must be preserved or an explicit migration counted.

Removing the archive-vector requirement removes one obstacle to broad CLI use, not all of them. The inspected CLI refetches tracking refs and derives its force leases from them; a newly fetched value is not necessarily incorporated by GHerrit's accepted input. Its open-head lookup is not the canonical-PR binding rule. Delegation needs an actual boundary for accepted expectations, canonical identity and every metadata effect, or a justified domain excluding those races. It retains unknown subprocess/API recovery and version coupling. Direct calls have maintenance costs too; no universal direct-API dominance has been established.

Do not change the archive protocol solely to make broad delegation possible before a concrete total-burden benefit appears. This is a retained default, with an explicit countercandidate and falsifiers rather than a claim that atomic coupling is a hard requirement.

## The substantive promise that does not collapse

Direct terminal `merged` is completed-request evidence. Terminal `enqueued` completes admission only. Post-terminal PR/ref disagreement demonstrates inconsistent observations; its cause may be projection lag or progressing work, and no suffix write after terminal success has been established. Official post-merge sync/push guidance is positive intended-workflow evidence. The sources still do not explicitly bind the last suffix write or later-write arbitration to that UUID.

Two operating promises remain meaningfully different:

| Promise | Benefit | Cost and missing support |
| --- | --- | --- |
| Supported exclusion before overlapping hosted writes | Avoids an admitted older native write undoing a later publication when that exclusion premise is established. | Needs a sufficient provider/coordination argument; the current pilot cannot complete overlapping repetition while that premise is missing. |
| Retained intent plus detected drift and explicit recovery | Could permit useful repetition without promising immunity from every later native write. | Requires intent-aware recovery, may expose temporarily wrong hosted state, detects on later connected observation, and can lose canonical continuity in an admitted lifecycle race. No validated production protocol or acceptable user-cost result is established. |

The weaker candidate must preserve confirmed intent, not just bytes. If X with x=1 is published and an admitted older native transformation later yields x=0, ordinary three-way import using X as both incorporated and local input can silently accept the deletion. Retain the exact published X and the native operation's older input; expose that drift for explicit acceptance or a validated restoration plan. An archive alone does not make the current intent safe.

Structural overlap has an additional cost. Reordering surviving B/C while a possible old B1→C1 suffix write remains can make B's new base contain B1 when that old write appears. Indirect-merge behavior can terminalize canonical B. Restoring its contents cannot reopen that review. This is a counterfactual protocol witness, not an observed delayed-provider failure. A weaker promise must prevent/exclude it, narrow its structural domain or count replacement/follow-up and lost continuity explicitly. Staging avoids this particular inversion but is not a proof of all same-order safety.

Neither promise dominates the other under all relevant values. This assessment therefore keeps the strict gate in the qualified incumbent, without treating it as a universal C1–C8 requirement. It does not silently select the weaker promise or call the pilot a complete replacement. The narrowed question is which supported contract can justify the **next overlapping hosted effect**, with direct, queued and external UI evidence kept distinct.

## What remains open

1. **The operating promise and its realization.** Obtain sufficient completion/arbitration semantics for the strict path, or choose a specific retained-intent recovery promise and validate its edit-loss, lifecycle, scope and useful-repetition traces. A service, CLI or quiet-read window cannot choose or prove it.
2. **First-client fit and release scope.** Staging versus joint dependent review, one-shot versus expressly continuing authorization, hook convenience, multiple-client collaboration and a richer reviewer surface have real benefits/costs. Choose the first release's supported target routes and policy promises for their useful workloads, friction, availability and maintenance cost; then validate actual compatibility. GitHub's policy authority does not select GHerrit's supported domain. These are release/extension choices, not prerequisites for a second reconciliation architecture. Human comprehension remains unmeasured.
3. **The selected target and implementation acceptance.** Establish an eligible first-CI route and actual repository policy/producer/SHA/method behavior, then implement identity, ownership, retention, effect recovery and migration. GitHub remains the policy authority. No method-only reliability rule, global green flag or generic compatibility framework is introduced. These checks are required work, not optional design modes.

This is a smaller dependency/decision model, not a claim that every tradeoff disappeared. Most structural principles were already sound. The concrete narrowing is a defined initial client, a clarified local/remote boundary, precise authorization/request semantics and an explicit staged milestone. The principal hosted-write promise remains open, with sharper countercandidates and failure costs.

## Evidence and detailed checks

The [provider source audit](provider-audit/REPORT.md) distinguishes documented completion from observed read inconsistency. The integrated [design](candidate-002.md) retains its exact experiment and primary-source links. [Warm](challenger/PASS1.md), [fresh](fresh-001/REVIEW.md) and [held-out](holdout-PASS1.md) reports record pass-one comparisons and their limits. Further review records and the final disposition are linked from README.md; those records supply evidence, not votes.

*Authored by an AI agent acting on joshlf's behalf.*
