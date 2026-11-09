# Bounded guest extension: source only, root executes

This extension uses the existing owned QEMU/container/kernel/module inputs. It
installs nothing and downloads nothing. Root retains exclusive runtime authority.
The prepared sources write only `/lab/extension`; they do not modify the v3
sources, initramfs tree, results, disks or full archive. The build copies the v3
initramfs tree, then replaces the copy's init/probe. All sources and offline
checks are under this extension directory.

The new records contain a 65,536-byte deterministic payload, an independent
payload SHA256, and exact generation/value fields. Journal pointers bind the
SHA256 of the complete serialized result, not merely a generation. The recovery
probe prints the complete bytes as hex. The host oracle checks byte length,
canonical full values, independent checksum, retained result, exact operation
identity and checkpoint/ref values. A missing or corrupt unpublished temp is
separate from an invalid accepted current record. It cannot grant completion.

| Stage | Cut/negative control and required oracle |
| --- | --- |
| 1 | Unsynced new temp; exact active old required. Unpublished temp is unaccepted regardless of survival. |
| 2 | File-synced new temp; exact active old still required. Temp validity is reported separately. |
| 3 | Rename without directory fsync; active must be exact complete old or new. |
| 4 | Rename plus directory fsync; exact complete new and absent renamed temp required. |
| 5 | Deliberately malformed unpublished temp, durably stored; exact old active remains valid and the precise bad temp is ignored. |
| 6 | Deliberately malformed active replacement, durably stored; exact malformed bytes must be observed and acceptance refused. |
| 7 | Durable new retained result and exact intent, old ref/checkpoint; pending intent only. |
| 8 | New ref, old checkpoint, no done record; pending output prefix. |
| 9 | New ref and checkpoint, no done record; pending finalization, distinct from done. |
| 10 | Exact done record plus exact outputs/retained result; validated local completion. |
| 11 | Deliberately false done marker with old checkpoint; refuse invalid completion. |
| 12 | Done/outputs present but one payload byte in the retained result changed while its JSON/checksum field remain; refuse invalid completion and prove checksum mismatch. |

Stages 5/6/11/12 are deliberately bad controls, not claims that the guest crash
created those corruptions. The journal/ref objects remain JSON proxies. These
cases do not run actual Git, a production native client or the separate corrected
Python executor. No local completion verdict grants hosted dispatch authority.

Before any recovery mount, the controller makes a lossless compressed copy of
the complete cut disk, verifies its decompressed SHA256 and retains it. Recovery
then mounts read-write, replays as needed, reads bytes and receives a second
emulator cut. Post-inspection disk bytes are also losslessly archived. Only the
new working raw disk is removed after both verified archives exist; v3 artifacts
are untouched. Raw fsck diagnostics are classified independently of exit code.

A separate inspector control clones stage4's exact pre-inspection image, mounts
and reads it, successfully unmounts, then powers off the guest normally. This
contrasts with the second-cut inspector path; it does not make the original cut
a clean shutdown. Its records and fsck diagnostics must satisfy their own oracle.

Root can copy this directory to `/lab/extension`, then run these separately:

```sh
bash /lab/extension/build-extension.sh
python3 /lab/extension/controller.py
```

Expected additions are one static C executable and copied initramfs, a 32MiB base
plus one 32MiB working disk at a time, compressed exact disk archives and full-byte
logs. No persistent extra raw disk accumulates. The controller refuses before a
new working disk if regular extension files plus that disk would exceed 192 MiB.
It uses one 256 MiB/one-vCPU TCG guest at a time, no guest network, twelve single
trials plus one clean-inspector control (25 boots), and 60-second barrier deadlines.
The root's total container/host storage cap still takes precedence; root may
reclaim its verified expanded v3 disks before execution.

The failure boundary remains abrupt loss of the owned emulator/guest memory;
outer container, host and device caches survive. Even a successful extension
would not establish hardware-power-loss behavior, all filesystems, repeated
reliability, actual Git durability or production acceptance.

`OFFLINE-CHECKS.json` is not guest evidence. It checks12 modeled record sets,
full-value/checksum mutants and bad completion classifiers, and challenges a
reference-only classifier with actual v3 case7's ref1/checkpoint0 records.
`AUDIT-v3.md` preserves the observed v3 limitations and raw diagnostic findings.

*Authored by an AI agent acting on joshlf's behalf.*
