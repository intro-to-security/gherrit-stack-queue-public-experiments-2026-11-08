# Root-owned build and launch envelope

No command here has been run by this lane. Root reviews the exact final source
manifest and grants runtime separately. Copy this package to the owned container
at `/lab/protocol-guest`; keep the original package and earlier evidence intact.
Root already reports installing the separately scoped Git package set: actual
Git 2.34.1, roughly 69 MB installed. Preserve its existing install/version logs;
this build performs no package operation.

Build only after checking the package hashes and original source pins:

```sh
cd /lab/protocol-guest
/usr/bin/python3 build-root.py
```

The builder copies the already inspected base initramfs/modules/busybox,
removes its old `/probe`, copies installed Python 3.10 and Git plus the required
stdlib, resolves and copies the full ELF `ldd` closure, and installs the new init
and guest adapter. It executes no compiler or third-party source. Missing
dependencies, unexpected Git location, existing build outputs or size overruns
fail without fallback. `BUILD-RECEIPT.json` records installed packages, exact
runtime/closure/staging bytes, kernel identity and final initramfs hash. Retain
partial failed build outputs and errors for review; do not silently loosen the
96 MiB staging/48 MiB compressed bounds.

Before cuts, root must perform a read-only initramfs-content audit and confirm
its installed interpreter can import the requested modules. Do not execute a
fixture merely as a build check. The first actual fixture boot is a reviewed
trial. Root can initially grant `validated` and `after_return`, then continue the
remaining named prefixes only under the exact reviewed case grant.

The root-owned controller must implement this fixed envelope; this package does
not import or execute an older controller:

1. Persist an exclusive run/intent naming exact source, kernel, initramfs and
   disk-size hashes, selected case list, resource/storage bounds and commands.
   Create one fresh 32 MiB ext4 base (`mkfs.ext4 -F -b 4096`) under the new output
   directory, retain its mkfs receipt, and sync it. Check total `/lab` bytes below
   2 GiB and this package below 384 MiB before each new working disk.
2. For each prefix, copy that base to the sole working raw disk. Boot one QEMU
   with `-machine virt -cpu cortex-a57 -accel tcg -smp 1 -m 256M -nographic
   -no-reboot -nic none -kernel /lab/boot/Image-virt -initrd
   /lab/protocol-guest/test-initramfs.gz`, command line
   `console=ttyAMA0 panic=-1 phase=cut prefix=PREFIX`, and an owned
   `virtio-blk-device` backed by that disk, `format=raw,cache=writeback`.
3. Retain exact serial bytes. Require `PROTOCOL` runtime and baseline records,
   then the exact `BARRIER PROTOCOL PREFIX` line within 60 seconds. Flush and
   fsync the host serial log before killing that QEMU process. Persist the
   emulator receipt. An unreached barrier or unknown process outcome stops the
   fixture; do not relaunch its cut phase.
4. Before any recovery mount, hash the entire working disk, gzip it into a new
   exclusive file, close gzip, fsync that file, decompress/hash it and require
   exact length and SHA256 equality with the raw disk, then fsync its directory.
   Persist this verified pre-recovery receipt. Retain no extra raw copy.
5. Boot the same working disk with `phase=recover prefix=PREFIX`, otherwise the
   same QEMU envelope. The guest emits raw records before logical recovery,
   invokes the real worker once with `reconcile=True`, and emits the result and
   after records. Require `BARRIER PROTOCOL CLEAN_RECOVERY_UNMOUNTED` and natural
   QEMU exit 0. No second inspector cut is planned. Preserve failures as raw
   evidence, including successful reads before a later failure.
6. Parse each boot's serial stream separately with `oracle.parse_serial`.
   Evaluate `oracle.check(prefix, cut['baseline'], recovered['before_recovery'],
   recovered['after_recovery'], recovered['recovery_result'])`. Save all checks,
   result and exact source identities; never turn a failed predicate into a
   passing prefix expectation. JSONL snapshots and all raw Git command outputs
   remain in serial, including diagnostic failures.
7. Preserve `e2fsck -fn` stdout/stderr and exit separately after the clean
   recovery unmount; no repairs. Make and verify/fsync a distinct post-recovery
   gzip archive using the same full-byte procedure. Only then delete the sole
   working raw disk and fsync its parent. Persist one terminal result per case.
   If any stage fails, retain the current disk and any completed archives, stop
   that fixture and let root reconcile the known/unknown state.

Use all eleven `guest.PREFIXES` only when granted. Two archived 32 MiB disks per
case should compress strongly, but compression is not assumed for storage
admission. Check measured bytes before each trial and stop at the cap; there is
no source fallback, disk growth or old-evidence deletion. A fixed 64 MiB base
requires root's recorded pre-run choice and the same byte checks.

The guest has no network device. The fixture has no hosted Git remote. Root's
scope is this local experimental dispatcher and exact Linux Git/ext4 build;
neither a validated local result nor the archive protocol establishes a native
server fence or machine-power-loss durability.

*Authored by an AI agent acting on joshlf's behalf.*
