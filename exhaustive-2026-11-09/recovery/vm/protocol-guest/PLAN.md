# Actual prototype and Linux Git: source-only proposal

This package prepares a bounded crash discriminator for the existing experimental
Python dispatcher. It changes no protocol rule. Root owns installation, image
construction, emulator execution and disk lifecycle; none has been performed by
this lane. A new exact root review/grant is required before running these sources.
Earlier causal, source-survey and rebase evidence remains frozen.

`source/protocol.py` and `source/run.py` are byte-for-byte snapshots of the actual
corrected recovery files. `SOURCE-PINS.json` records their identities. The guest
verifies both SHA256 values before importing them. It sets only the fixture
helper's explicitly assigned `RUN=/state/scope`, calls `fixture` once on a fresh
disk, and invokes the actual `worker`. It never calls the old full driver's
`main`, cases, mutations or historical run directories. The helper's imports and
top-level assignments were inspected; import creates no fixture or subprocess.

The only dispatcher instrumentation is replacing `protocol.pause` with a serial
line followed by `signal.pause`. The original callback writes/fsyncs
`paused.json`; that extra persistence is deliberately absent. No write, sync,
validation, effect or recovery routine is replaced. The source's existing
unsynced Git-command logs remain part of the prototype. Before dispatch, the
entire fresh fixture is synced once with `os.sync`, and exact baseline JSON plus
all local/provider Git refs and objects are emitted to serial. No extra guest
sync occurs at the selected cut or after the actual worker returns.

| Cut after actual source prefix | Planned logical recovery result |
| --- | --- |
| `validated` | One first dispatch, independently validated completion |
| `marked` | Unknown outcome; no dispatch/resend |
| `request_logged` | Unknown outcome; existing request never repeated |
| `provider_head` | Unknown outcome; no archive/receipt-based inference |
| `provider_archive` | Unknown outcome; matching refs alone cannot settle |
| `provider_receipt` | Reconcile exact receipt, then validate all outputs |
| `acknowledged` | Finish local continuation/checkpoint, validate all outputs |
| `result_ref` | Finish checkpoint; ref alone is insufficient |
| `result_checkpoint` | Finish operation record; checkpoint alone is insufficient |
| `complete` | Revalidate exact persisted complete state |
| `after_return` | Cut after the actual worker returned `complete`; revalidate |

Each is one new independent filesystem fixture, not a repaired-write retry.
`oracle.py` checks the captured fsynced JSON prefix, frozen intent/manifest,
authority and binding, retained input/result, full Git-object bytes and hashes,
and no extra request when any earlier effect is unknown. A `complete` verdict
additionally requires the exact local continuation, full checkpoint and receipt,
provider head, immutable archive, exactly one matching request and exactly one
matching receipt. It independently rejects a complete worker response when a
provider ref is absent or different. This matters because the prototype's own
completed-record validation does not reread those provider refs. Passing source
validation is not substituted for this oracle.

Root should retain all failures, malformed/missing records, fsck diagnostics and
unreached barriers. The planned prefix expectations stay fixed if reality
differs. Unknown emulator/guest outcomes stop that fixture; there is no automatic
same-case retry. No result grants hosted/native authority.

The recovery boot mounts ext4 read-write, so journal replay precedes observation.
It emits all actual Git refs, all Git-object bodies and complete JSON/JSONL bytes
before calling the same worker with `reconcile=True`. Independent direct Git
reads do not append the prototype's command logs. It then captures the same
evidence after recovery. Successful recovery inspection unmounts and powers off
cleanly. The exact cut disk is archived before that boot, and the cleanly
unmounted post-recovery disk is separately archived.

Use one private 32 MiB ext4 base and one 32 MiB working raw disk. A 64 MiB size is
permitted only if root records that size before the first trial; all cases use
that fixed size. Run one 256 MiB/one-vCPU TCG guest at a time, `-nic none`, at most
22 boots for eleven cases, with a 60-second barrier limit. Keep verified/fsynced
compressed pre/post disks and serial logs; remove a working raw disk only after
both exact archives verify. No additional raw images accumulate. The new
package's measured files must stay below 384 MiB, and root's total remains below
2 GiB. These are stop bounds, not measured sizes or permission to reclaim other
evidence. `ROOT-RECIPE.md` specifies the launch/archive envelope.

Root reports the installed candidate as Git 2.34.1 and Python 3.10. Build-time
version and byte identities must be retained. The build uses installed trusted
executables, stdlib and their `ldd` dependency closure; it installs, downloads and
compiles nothing. Its staging bound is 96 MiB and compressed-initramfs bound is
48 MiB. Required modules include fcntl, subprocess/_posixsubprocess, signal,
hashlib, json, pathlib, shutil and traceback. The copied stdlib excludes tests,
GUI modules, installers, third-party modules and bytecode caches.

`OFFLINE-CHECKS.json` will record only local pure/source controls: all eleven
modeled prefix outcomes, eight damaged-completion components, unknown resend,
exact original source/injection checks and `ldd` parser rejection. They invoke
no prototype worker, actual Git, VM, container, install or image construction.

The failure boundary is abrupt termination of the owned guest emulator; outer
container, host and storage caches survive. Default Git fsync behavior is
observed, not assumed durable. This tests this prototype on ext4 with the exact
recorded Linux Git, not host Git, latest Git, production GHerrit, hardware power
loss, all filesystems, native server behavior or a forward-compatibility promise.

*Authored by an AI agent acting on joshlf's behalf.*
