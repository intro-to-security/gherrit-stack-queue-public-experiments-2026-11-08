# Collect the nine unrun actual-Git prefixes

This is source-only continuation preparation. No container, install, build,
emulator, network, Git fixture or publication action was performed. Root must
review the exact source/hash vector and issue a new grant before execution.
The original guest, dispatcher, helper, oracle, controller, two actual trials and
independent audit remain unchanged; `INPUT-PINS.json` and `reviewed-inputs/`
retain their inspected identities and reports.

The actual `validated` trial passed. The separate `after_return` trial failed:
the worker returned complete, but replay exposed broken new continuation/archive
refs while the operation/checkpoint/request/receipt and original objects
survived. Recovery refused `invalid_completed_attachment`; the unchanged oracle
rejected the trial. This continuation neither reruns that case nor repairs the
prototype. It collects only the remaining prefixes:

`marked`, `request_logged`, `provider_head`, `provider_archive`,
`provider_receipt`, `acknowledged`, `result_ref`, `result_checkpoint`, `complete`.

`continuation_controller.py` reuses the reviewed root controller's exclusive
fsynced JSON writes, directory sync, hashing, byte accounting and verified/fsynced
lossless disk archive primitive. It never invokes that controller's `main` or
original all-cases loop. Explicit overrides are
`ROOT=/lab/protocol-guest` and
`OUT=/lab/protocol-guest/actual-results-continuation-001`. Each case gets one
fresh 32 MiB copy of the new private ext4 base. The image, kernel, guest, Python
dispatcher, fixture helper and strict host oracle remain the reviewed originals.
No rebuild, source fallback, alternate oracle or same-case retry is included.

The new boot collector opens and syncs the exclusive serial log before spawning
one owned child. Cut admission requires the exact full-line barrier, an issued
kill and reaped exit -9, complete unambiguous baseline/runtime records, exact
phase/prefix/source/Python/Git attribution and valid baseline identities, refs,
objects, request store and custody. A wrong or missing premise stops the matrix.
Only the exact spawned process can be killed; waits and serial draining are
bounded. Unknown/alive process state stops without reading its disk.

Recovery evidence and matrix continuation are separate from a passing verdict:

| Observation | Classification and next action |
| --- | --- |
| Exact cut, known stopped recovery, unique valid attributed worker result, all required evidence | Run the unchanged oracle. Preserve pass or failure and continue to the next fresh case. |
| Worker returns a known refusal, including before successful unmount | Preserve the failed oracle result or missing-evidence diagnostic. Archive the stopped disk. Continue only with known attributed result and reaped process. |
| Missing/malformed/duplicate result or malformed protocol serial | Nonpassing collection diagnostic. Archive a known stopped disk, retain its raw working copy and stop. |
| Bootstrap crashes before a result, runtime mismatch or cut premise failure | Archive any known stopped disk, retain logs/raw disk and stop. No repaired boot or retry. |
| Process exit/ownership is unknown or child may remain alive | Stop and retain the process receipt/PID. Do not archive or inspect a possibly live disk. |

The original guest normally returns a bounded refusal and still emits snapshots
and cleanly unmounts. If it instead stays alive after a known result, the bounded
collector terminates that owned guest; the post image is explicitly labeled as
a second emulator cut rather than a clean recovery unmount. An incomplete
snapshot never becomes a passing verdict. Both before/after snapshots must be
present and serial/capture errors absent before collecting the next independent
fixture. A failed strict verdict with complete collection can still permit that
progress; it does not mean protocol acceptance. Malformed or incomplete
collection stops even when one worker result is readable.

After the cut, make and verify/fsync the pre-recovery archive before booting
recovery. After any known stopped recovery, make the post-recovery archive
before classifying its result, so a parser error or refusal cannot discard that
disk. Retain read-only `e2fsck -fn` diagnostics separately. Delete only the owned
working raw disk, and only after both archives verify and the terminal row is
fsynced, when matrix continuation is allowed. Failed verdicts remain in exact
archives/logs/results. Unknown/premise-failed cases retain the sole raw disk and
stop. No extra raw accumulation or prior-evidence cleanup is authorized.

The fixed envelope remains one 256 MiB/one-vCPU TCG guest, no NIC, one 32 MiB
base and one working disk, at most eighteen boots, 60-second barrier limits,
bounded 10-second ownership waits and a two-second serial drain. Storage guards
reserve room for the working disk and both worst-case archives before a case;
new package usage stays below 384 MiB and total `/lab` below 2 GiB. A storage or
local evidence-write failure stops with retained artifacts.

Root copies only this new directory into the existing package, then places an
exclusive `/lab/protocol-guest/CONTINUATION-GRANT.json` with coordinator `root`,
exact `grant_path`, `root`, `out`, the ordered nine `cases`, `disk_bytes=33554432`,
the complete `source_hashes` vector, existing `initramfs_sha256` and
`kernel_sha256`, exact `runtime_python`, and SHA256 of the captured Git
build-options stdout as `runtime_git_stdout_sha256`. The source vector contains
all six fixed `SOURCE_PINS` entries plus
`continuation-prep/continuation_controller.py` at its reviewed final hash.
Existing outputs or changed/missing source identities refuse execution.

After that separate review/grant, root's one execution command is:

```sh
/usr/bin/python3 /lab/protocol-guest/continuation-prep/continuation_controller.py
```

The source-only checks use fake processes, fake disk archives and pure parsing
of the retained actual logs. They execute no Git or guest. They verify that the
real observed failure stays failed, known refusal archives/continues, missing or
malformed result archives/stops, unknown processes are not read, cut exit0/exit1
cannot masquerade as SIGKILL, log-open failure spawns nothing, and runtime or
duplicate-result mismatch is rejected. They do not establish runtime durability.

The failure boundary, default-relatime observer effects, read-write journal
replay and surviving outer caches remain disclosed. Ext4 fsck exit0 cannot
certify Git refs. No result covers another Git version, host Git, physical power
loss, production GHerrit or native provider arbitration.

*Authored by an AI agent acting on joshlf's behalf.*
