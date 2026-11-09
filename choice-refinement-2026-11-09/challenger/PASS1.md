# Pass 1 warm specialist review

Execution: `swarm-model-refinement`. Target: GHerrit's native-stack decision model. This is a bounded review for root's comparative adjudication, not a vote, stopping decision or nested refinement loop. Exact effective model and effort remain unknown. The context is private; the filesystem is shared without ACL isolation. No sealed case, other pass review or external system was accessed. No test or native mutation was run.

I verified the frozen artifacts before review:

- [candidate-001.md](../candidate-001.md): SHA-256 `b61e0a55e72e8cc7361a0edc52c273e9e08e9281f93578c9b7212588ff30fd7b`.
- [DECISIONS-001.md](../DECISIONS-001.md): SHA-256 `6db7f32a2a0da018121520ea72687d62ea9c86a9d706972b91ac9249fea2e8b5`.

The comparison uses the fixed [focused contract](../CONTRACT.md), [C1–C8](../GOVERNING-CONTRACT.md), complete [candidate003 baseline](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/blob/740d091ca6704583d415efb714da79b33cac9352/followup-2026-11-08/refinement/candidate-003.md), exposed provider audit/discovery, and my [Round 1 report](ROUND1.md). I read both new artifacts completely and checked their exact baseline diff. I also inspected the retained pinned CLI submit/push source for the newly added delegation claims.

## Result

The candidate addresses the substantive Round 1 criticisms. It no longer credits clarification of local acceptance, accepted authorization or staging as several novel unconditional dominance results. It preserves distinct revision roles, unknown-effect evidence, canonical identity, native ownership and old-writer exclusion. It gives the strict gate its availability cost and explicitly leaves the full overlapping workflow unresolved. It does not silently adopt the weaker promise.

I found one residual decision-accounting issue and one scope-wording ambiguity. Neither demonstrates an unsafe new hosted operation or a lost required input. The first can overstate how much the decision model has closed; the second can make the claimed first-release burden unclear. Root can resolve them locally without inventing another reconciliation engine or changing C1–C8.

## Finding 1: retain support-profile selection as a release choice, not only acceptance work

**Affected layer:** semantic model of the remaining decisions and release domain; not the identity/import/effect protocol. **Materiality:** bounded claim correction. It does not require selecting an actual profile in this refinement.

The baseline's open question 3 explicitly retained selection of the first release's CI/rule/signature/queue profile as a choice combining engineering evidence with acceptable friction, availability and maintenance cost. Candidate001 line 319 and DECISIONS001 line 81 replace that with establishing the target's actual policy/producer/SHA/method behavior and implementation acceptance. The declared first-client domain in DECISIONS001 line 5 fixes local authorship, placement, API transport and one-shot authorization, but does not fix the hosted route/method or supported policy promises.

Compatibility assessment is required. It does not select which compatible workload the release promises to serve. GitHub being the policy authority settles who decides repository rules; it does not settle which repository configurations GHerrit supports, whether an observed review/signature outcome is acceptable, or which native route is worth implementing first.

Concrete discriminator, using the exposed evidence rather than a new guarantee: two permitted queue configurations can differ by method/build concurrency. The retained SQUASH trace ejected the upper at build concurrency one and landed both at two; REBASE did not actually exercise its configured second build. MERGE has positive bounded observations, without a reliability theorem. Accurately validating those facts leaves different proposed releases possible:

1. A direct-only initial release excludes queue-specific operation issuance and queue continuation promises, while retaining external-outcome recovery and the same importer.
2. A one-shot queue-capable release supports actual admission plus ejection reporting and renewed acceptance, accepting the additional queue custody/outcome work.
3. A release supports only a named target/method/profile, with explicit exclusions and configuration-drift handling.

These choices preserve the common correctness core but have different uses and burdens. Existing facts alone do not choose among them. Likewise, a repository's preference for squash history or required signatures can defeat an otherwise convenient proposed support profile without being a verifier failure.

The candidate does not claim method-only reliability or universal support, so this is not evidence of an actual C4/C5 violation. It is a false closure only if the new three-question inventory is read to mean that support-profile choice has become purely an implementation check. Keep the residual explicit, for example:

> Choose the first release's supported target routes and policy promises, then validate their actual CI/producer/SHA/method behavior and configuration drift. These are a scoped release decision followed by required acceptance work; they do not require separate recovery engines.

This preserves the smaller architecture while keeping the remaining product/value decision visible. No broad matrix rerun or new universal capability framework follows.

## Finding 2: identify which structural interface belongs to the staged first release

**Affected layer:** mapping/wording between the full design and proposed first-release subset. If root intends a single selected structural domain rather than conditional alternatives, that domain should also be recorded in the decision model. **Materiality:** clarification; no shown hard-contract violation.

DECISIONS001 lines 37–48 and candidate001 lines 197/274 correctly permit a named staged release to defer general insertion/reorder/drop/fold. The full candidate still says the proposed default client includes structural editing (line 240); preparation routes order changes, omission and folding to their structural path (line 119); and lines 221–232 specify that path. The declared first-client domain at DECISIONS001 line 5 does not say whether that broader structural interface is included or only described for later extension.

Concrete reader/implementation trace: an author presents A–C–B instead of A–B–C on the supported one-commit linear branch. Following line 119 leads to the described structural executor, whereas following the staged-release cost comparison can legitimately lead to a pre-mutation unsupported-operation result with retained inputs. Those have different first-release work and user capability. Both are defensible scoped proposals; they should not be accidentally counted as the same already fixed domain.

The current conditional language can be read consistently as a full design plus an optional staged subset. Under that reading this finding is only presentation/mapping. A small explicit boundary would suffice:

> The full design includes structural editing. A staged first release may omit those commands, reject those edits before mutation with inputs retained, and complete the accepted F-first path instead. Joint dependent review requires the broader structural release.

Alternatively, keep joint structural support in the proposed first client and describe staging as a user option rather than a reason that release implementation can omit it. Neither version changes C5's permission for a named staged restriction, nor removes the still-open final B write gate. The correction should not introduce a new generic mode switch or pretend staging serves users who need joint F–B review.

## Discriminating checks that did not produce further findings

### Local acceptance and stale custody

I replayed the Round 1 P0/P1 argument against candidate001 lines 89, 203 and 217 and DECISIONS001 lines 33–35. A pending operation retains its captured checkpoint; a new continuation retains old results; selecting it grants no hosted-write authority or old-operation completion. A stale worker substituting P1 for its frozen P0 violates the delivered rule. The proposal does not claim this boundary is already implemented. No additional semantic coupling needs to be restored to prevent that trace.

### One-shot versus continuing authorization

Candidate001 line 158 and DECISIONS001 lines 25–29 now distinguish a new effect record from a new human decision. The actual first-client default is one-shot. Optional continuing authorization retains per-layer transformation, authority, range, outcome and readiness checks; an unknown old request cannot be replayed. The proposal does not promise a free or implemented continuing-goal validator. There is no new evidence-backed dominance claim to refute here.

### F-first staging, omitted B and public targets

Candidate001 line 197 and DECISIONS001 line 46 expressly retain omitted B/suffix custody, old operations and checkpoints. They require F's direct/indirect effect independence, independently landable A-only content and accepted actual public-source export. The prior counterexample where a full F–B′ public source is silently described as local-only now violates explicit text. Final B publication stays gated. Staging's simultaneous-review loss is counted. No completion claim is manufactured by F-only progress.

### Drift and irreversible lifecycle

The `I=X, L=X, H=N` confirmed-edit-removal trace and old-order/new-order indirect-merge trace are both retained as counterfactual protocol witnesses, not observations of delayed native writes. DECISIONS001 lines 71–75 require intent-aware recovery and counted continuity consequences; candidate001 line 215 retains the strict gate instead of enabling that unvalidated alternative. The candidate therefore does not rely on archives alone as proof that an admitted late native rewrite is harmless.

### Completion evidence and source calibration

Direct terminal `merged`, terminal admission `enqueued`, actual lifecycle, usable ranges and later overwrite permission remain distinct. The post-terminal mismatch is described as inconsistent observations with projection lag still possible. No observed late suffix write or future-write fence is invented. The first-client defaults remain proposals rather than hard C1–C8 obligations or measured human preferences.

### CLI burden is not collapsed into one archive obstacle

The retained pinned [submit source](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/cmd/submit.go) fetches active branches at lines 213–216 before calling push at lines 252–254. The retained [push source](https://github.com/github/gh-stack/blob/bd0a32504f9ae9f795875a9e6bb90ff7408fda08/internal/git/gitops.go) derives expected SHAs from tracking refs at lines 265–274. This supports the narrower claim that a refreshed lease does not itself establish incorporation by GHerrit's accepted input. `ensurePR` also performs branch-based discovery at submit lines 415–444 instead of treating the captured GHerrit canonical PR binding as authority. I did not infer additional server behavior from those calls.

The new text presents these as inspected-source obstacles, counts direct-call maintenance too, and keeps a changed archive/export protocol as a countercandidate. It does not say write-ahead input retention proves publication or that atomic coupling is independently mandated by C1–C8. No universal CLI/API dominance is claimed.

## Limits and root-facing disposition

This was static comparative reasoning over exposed material, with frozen-hash and source/diff inspection. It supplies no new live behavior, blind confirmation, implementation acceptance, human preference or total-cost measurement. I found no additional core protocol semantic change justified beyond retaining the release-profile decision explicitly. The structural-domain issue can be resolved as a full-design/first-release mapping clarification unless root intends to choose a different domain. Root owns that layer diagnosis and the pass transition.

*Authored by an AI agent acting on joshlf's behalf.*
