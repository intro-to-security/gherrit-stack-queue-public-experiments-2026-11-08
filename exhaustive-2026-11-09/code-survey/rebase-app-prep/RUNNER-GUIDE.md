# Review and grant the one fixture

`fixture_runner.py` prepares and operates only
`exh-1109-causal-rb-app-001/{trunk,A,B,runner}` in the authorized synthetic
repository. Its only shared helper is the existing `control/rootlab.py`, pinned
at SHA256 `ae1ae63d5ee8370cbca11711f5d5e76a97669881ddf8ef8911493666393d128d`.
It reuses that helper's exclusive durable intent/readback, API command, exact
atomic leased push and local object routines. The small subclass restricts the
helper's broader ref rule to these four exact refs. No historical driver runs.

The exact prior read-only-contents preparation is retained under
`history/before-contents-write-158f66a568e9/`, with byte hashes in `FREEZE.json`.
The current workflow requests `contents: write` and `pull-requests: write` only.
The credential is still job-scoped, and checkout does not persist it. No default
permission, repository flag, old fixture or main branch changes are proposed.

There are three deliberately separate phases. Root authorized only local
`prepare`, which completed and produced `run-001/PREPARED.json` at SHA256
`07c39be5858e2bde2923c8a7308f596c7f88b568fa8b60e650cd0d738296ed1d`.
Root then granted fixture creation with `control/rebase-app-grant-001.json`.
That phase created PRs #654/#655 and group #656, with all five dispatch receipts
retained. `RUNNER-READY.json` is frozen at SHA256
`b6ed669c2b6f989677b0e56ae5079ebece789b67a5cb7b258cd91db608179ffe`.
Root separately granted launch with `control/rebase-app-grant-002.json`.
It completed one runner push and one guarded Actions native request, which
returned404 with both requested write permissions actually granted. See
`RESULT.md`; all steps below are the retained protocol, not rerun instructions.

1. **`prepare`** creates only a new private local bare store under `run-001/`.
   It constructs the tiny trunk/A/B and independent advanced trunk, retains
   their exact objects, and writes `PREPARED.json` with files, trees, OIDs,
   source hashes and the five proposed hosted dispatches. It makes no network
   call. A pre-existing allocation refuses reconstruction.
2. **`create-fixture --grant <absolute control path>`** needs root's exact
   `create-fixture` grant. It reads the repository identity and proves the
   entire four-ref prefix absent, atomically creates trunk/A/B with empty
   leases, creates exactly A and B PRs, registers their returned canonical
   numbers as one group, and advances only the trunk with its exact old lease.
   It validates every returned PR/group identity and ref vector. It then fills
   config/workflow, constructs and retains a clean runner commit locally, and
   writes `RUNNER-READY.json`. **It does not push the runner branch.**
3. **`launch --grant <different absolute control path>`** needs root's separate
   `launch` grant, bound to the exact filled source hashes, runner commit,
   numeric group path, full expected-head map and requested write permissions.
   It rechecks committed bytes, remote refs, canonical PRs and group membership,
   then makes one create-only runner push. That push can launch the reviewed
   workflow's single native PUT. Root must retain/read back its exact run,
   effective token permissions, sanitized artifact and independent native
   effects. Launch does not poll or retry the workflow.

The five fixture dispatches are one atomic three-ref push, two PR POSTs, one
group POST bound to those acknowledged PR outputs, and one leased trunk push.
The later launch is one additional create-only push whose only workflow has
the separately reviewed exact native request. Unknown acknowledgements retain
their original identities and freeze the scope. PR/group creation is never
repeated merely because a receipt or artifact is missing.

Each granted phase creates an exclusive `CREATE-START.json` or
`LAUNCH-START.json` before its work. Any re-entry refuses before dispatch. The
helper also keeps exclusive per-mutation intents and actual subprocess
receipts. If a phase stops, inspect those records read-only; do not rerun the
phase or recreate this prefix. These are local process/dispatch controls, not a
claim of physical-loss durability or provider idempotency.

The root-owned grant must be a JSON file directly under `control/` with these
exact fields; additional root coordination fields are allowed:

```text
coordinator: "root"
grant_path: the grant's exact absolute path
phase: "create-fixture" or "launch"
repository: "joshlf/gherrit-native-stack-experiments-2026-11-08"
repository_id: 1450723431
prefix: "exh-1109-causal-rb-app-001"
run_directory: the exact absolute run-001 path
sources: the exact current sources() path-to-SHA256 map
frozen_record_sha256: SHA256 of PREPARED.json or RUNNER-READY.json
effects: the exact effects array from that frozen record
```

Root must review the record and source before creating that grant; copying
fields mechanically is not a review. A grant for fixture creation does not
authorize runner launch. Source changes after local preparation invalidate its
source binding, and changes after runner readiness invalidate launch.

`SOURCE-MANIFEST.json` freezes the current preparation. `OFFLINE-CHECKS.json`
distinguishes source/pure mocked checks from actual effects. The separate local
prepare used only local Git object/config/ref operations; it made no network
call. The later separately granted fixture creation has five known successful
dispatch receipts in `EXECUTION-STATE.json`. The separately granted runner push,
one workflow attempt and one known404 native request are now retained in
`RESULT.json` and `RESULT-MANIFEST.json`. No further mutation remains authorized.
Source-only curation outputs remain unchanged.

*Authored by an AI agent acting on joshlf's behalf.*
