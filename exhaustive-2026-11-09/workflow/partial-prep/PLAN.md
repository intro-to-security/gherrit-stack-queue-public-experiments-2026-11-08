# Public B-success/C-conflict discriminator

This source preparation grants no hosted mutation. Root must review and create
an exact new control grant before `partial_once.py` runs. It reuses only the
fully inspected definitions in `workflow/core.py` and `workflow/effects.py`;
their top-level imports/constants create no Git repository or request. Their
exact bytes/hashes are retained for review. No old driver is imported or run.

The sole allocation is repository
`joshlf/gherrit-native-stack-experiments-2026-11-08`, prefix
`exh-1109-workflow-gql-partial-001`. One independent orphan trunk starts with
tiny a/b/c text files. A changes only a; B changes only b; C changes c from0 to2.
Publish trunk/A/B/C, a fixed initial `author-source` at C, and create-only A/B/C
v1 archive tags. Open the canonical three PRs and register exactly [A,B,C].

Only after registration, publish A's prepared extra commit changing c from0 to1
and its create-only A/v2 archive in one explicitly leased atomic push. The
initial source and v1 archives stay fixed. Rebase B using its exact freshly
observed selected node/head and acknowledged A base. B must acquire A's new
head as its sole parent, retain exactly B's original own patch, and match the
independently constructed expected tree. Retain that exact B prefix/checkpoint
before any C request.

Then reobserve all canonical identities, complete native membership/order,
branch heads/bases and the full branch/source/archive vector. Request C REBASE
once with its exact unchanged selected head. Its c change should conflict with
the new base inherited through B. Accept the planned outcome only for the
recorded HTTP200 GraphQL UNPROCESSABLE conflict response, unchanged C and exact
retained B/source/archive vector. Other failures remain failed premises. No
request ID is treated as an idempotency key or whole-stack operation receipt.

The complete write budget is two atomic explicit-lease Git pushes and six HTTP
mutations: three PR creates, one exact native group create, B REBASE and C
REBASE. There is no default-main, policy, workflow, queue, native async merge,
old fixture, browser action, deletion or cleanup effect. All authored commits
and PR bodies carry their required notices. Native-only B changes create no
new authored version.

The helper journals fsynced exclusive intents and request bytes before dispatch,
retains sanitized raw responses, and freezes unknown or rejected mutations.
Only readback follows the expected C rejection. An unknown/missing receipt or
unexpected head freezes without retry, repair or a successor member request.
An existing local fixture refuses reentry. Ordinary read projection lag gets
bounded read-only samples; elapsed time never clears mutation uncertainty.
The successful B response may expose an old head; actual Git/PR agreement,
parent, own patch and tree establish its usable result separately.

The root grant must reside directly under campaign `control/` and contain:
`coordinator=root`, exact `grant_path`, the repository above,
`cases={"gql-partial-001":{"prefix":"exh-1109-workflow-gql-partial-001",
"actions":["partial-once"],"effects":["push","create-pr","create-stack",
"update-branch"]}}`, exact `driver_sha256`, and `harness_sha256` equal to both
recorded core/effects hashes. Every mutation rechecks the grant/source guard.
Root then runs only:

```sh
/usr/bin/python3 workflow/partial-prep/partial_once.py --grant /absolute/campaign/control/GRANT.json
```

Offline controls challenge exact namespace, selected node/head, grant/source
identity, push-vector leases, unresolved acknowledgement/no-resend and full
source/archive drift. A disposable local Git control proves B's unchanged patch
and C's conflict before hosting. Hooks are disabled; it sends no network request.

This distinguishes a real mixed-prefix outcome for two separately fallible
public requests from the previous local second-failure simulation and website's
different operation. It supplies no transaction, rollback, cancellation,
suffix-settlement or future-write fence. Finite unchanged C reads remain finite.
All refs, PRs, source/archive objects, requests, failures and checkpoints are
retained for audit; no cleanup is needed or authorized.

*Authored by an AI agent acting on joshlf's behalf.*
