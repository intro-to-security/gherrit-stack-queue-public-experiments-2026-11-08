# Scoped durable-ref variant

This source-only variant tests one captured gap: Git 2.34.1 returned success, then the worker returned complete, but abrupt guest loss left the new provider archive and local continuation as empty loose refs. The failure and its images remain unchanged in `actual-results-001`. This variant needs fresh disks and independent outcomes; it does not repair or replay that case.

The exact original worker, fixture, guest, init, builder, controller, and oracle are retained under `original/`, with SHA-256 pins in `ORIGINAL-PINS.json`. `variant_entry.py` calls the original guest unchanged. Immediately after the original baseline or before-recovery snapshot, it instruments `protocol.Git.run`. The original guest still verifies the worker and fixture source pins and replaces only the pause with serial output. The copied init changes one entry path. The original oracle and controller are reused unchanged; the controller entry changes only its package/output root.

`durable_refs.py` permits only these successful command forms, with the exact frozen new and old SHA-1 values:

| Repository | Ref | Old value |
| --- | --- | --- |
| case/provider/repo | refs/heads/A | frozen expected input |
| case/provider/repo | refs/archives/op-case-PREFIX | absent |
| case/repo | refs/retained/completed-case-PREFIX | absent |

The prefix must be one of the original eleven and the case must be exactly `/state/scope/case-PREFIX`. Before dispatch, the wrapper validates the old loose ref or absence. After the original command returns success, it opens the resulting ref without following symlinks, requires the exact 41 bytes `new_sha + newline`, fsyncs that file, then fsyncs each parent directory from the ref parent through the case directory. This includes the `refs` parent of a newly created `archives` directory. The case and its ancestors already existed at the original guest's deliberate baseline `os.sync()`, so the added chain stops at the case. There is no post-mutation global sync.

The outer original authority lock excludes cooperating concurrent namespace writers. This is limited to owned, normal, single-link loose-ref files and owned directories on the case filesystem. Symbolic refs, symlink components, packed refs, common-dir/worktree layouts, environment redirection, alternate update-ref forms, nonzero command success allowances, and out-of-scope refs are rejected. This is not a general Git backend or a fence against arbitrary direct writers. Read commands pass through unchanged. A command exception or nonzero result does not invoke barriers or retry. A post-command byte or fsync error propagates without a receipt, checkpoint, acknowledgement, or complete return from the source continuation; the mutation may already have occurred, so it remains an unknown/partial effect for subsequent fresh observation.

Each completed barrier emits a separate `DURABLE_REF` JSON serial line with role, repository, exact ref/new/old and synchronized paths. These lines do not replace the original `PROTOCOL` records. Serial traces establish that the wrapper returned through its calls; persistence still requires the independently retained pre/post images, recovery observations, and unchanged oracle. The runtime record identifies wrapper and entry hashes. Inspection before logical recovery retains the original guest's ordering and default `relatime` effects.

All Git objects were deliberately baseline-synced before mutation. This tests ref/receipt/checkpoint continuation durability with those existing objects; it makes no claim about creating new Git objects, reflog durability, other filesystems, physical power loss, or GitHub. Reflogs and original JSON/log behavior remain unchanged. The strict original oracle may expose a further failure. No newer Git reference-fsync configuration is assumed on Git 2.34.1.

`offline_checks.py` uses an in-memory OS descriptor model. It checks exact file-before-parent order for all three mutations, file/directory fsync failure, command failure without retry, unsupported forms/layout/bytes and read passthrough. Three altered-source controls omit the file sync, the newly linked directory's parent sync, or the case anchor sync; an independent observed-call trace rejects all three even when their self-reported path traces falsely claim completion. Process launch, network socket construction, and global sync are blocked in the check runner. These are code-path checks, not persistence results.

*Authored by an AI agent acting on joshlf's behalf.*
