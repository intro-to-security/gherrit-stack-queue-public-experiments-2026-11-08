# Governing contract for this refinement

The user requests design alternatives for integrating GHerrit with native GitHub
Stacked PRs, informed by refreshed platform documentation and current GHerrit,
then swarm-model-refinement. The deliverable is a justified design comparison,
a concrete recommended direction or qualified shortlist, unresolved decisions,
and reusable local evidence. It is not migration implementation or authorization
for new remote experiments. Preserve the separate, already-authorized merge work.

Evaluate every candidate, including minimal change, under the same obligations:

C1. Explain how a developer authors and revises separate reviewable changes on
one local Git branch, and how they become native PR layers. Count any supported
local-history restrictions or workflow changes explicitly. Hooks and a service
are optional realizations, not requirements.

C2. Establish which repository, logical change, authored revision, hosted revision
and PR an operation affects. Preserve existing discussions and immutable archives
by default; explicitly count any alternative that replaces PRs or changes archive
meaning. Ref names, matching trailers and observed SHAs alone do not prove owner
or incorporation authority.

C3. State who owns hosted topology, text, readiness, synchronization and landing.
Use native membership and native landing where the feature supplies them. Avoid
two independent actors claiming the same responsibility without a protocol.
Ordinary Git/unmanaged use and private/public intent need an explicit policy.

C4. Account for partial, rejected, delayed, asynchronous and unknown outcomes.
Keep unsubmitted local work and unmentioned hosted work recoverable. Do not claim
Git/API atomicity, a global concurrency fence, deduplication or completed suffix
work without evidence. State the supported concurrency domain and assumptions.

C5. Cover useful repeated work: first publication, append, amendment, native
prefix landing, importing hosted outcomes and later publication. Explain reorder,
insert/drop/fold, shared prefixes, nonlinear history, completed/partial stacks,
and adoption. A staged restriction is allowed and must be named; perpetual refusal
is not a successful full-workflow replacement.

C6. Compare total reasoning, implementation, user and deployment burden. Include
invariants, mappings, adapters, coordination, testing, recovery, migration and
operational dependencies. A current weakness shared by proposals is not a reason
to prefer current code, and a shorter client is not a whole-system simplification.

C7. Distinguish documented contract, inspected implementation, user reports,
reasoning examples, inferred product goals and unresolved assumptions. Supply
source identities and discriminating evidence. Proposed probes are not results.
No live hosted guarantee may be supplied by an assumed-correct mock.

C8. Provide a reversible migration and a way to validate consequential assumptions
before adoption. Keep the existing PR work and reusable research intact. Do not
silently erase an uncertainty to make a recommendation decisive.

Useful product goals inferred from README and previous work include stable change
identity, canonical PR continuity, authored patch history and convenient Git
editing. They are important comparison criteria, not authority to discard another
obligation or assume a particular coordination architecture. No requirement for
atomicity against every arbitrary repository administrator is being added here.
A candidate that promises strong concurrency safety must justify that promise;
a weaker supported domain must be explicit and useful.

This contract remains fixed during a pass. Changing the mission or a hard
obligation requires a user decision; refining a representation or qualifying an
unsupported implementation claim does not change the mission.
