# Owned guest abrupt-power-cut plan, pending coordinator approval

Read-only inputs are available: existing local `ubuntu:22.04` image; Docker
29.4.0 on shared OrbStack/aarch64; Alpine v3.22 aarch64 `vmlinuz-virt` (HTTP 200,
9,642,496 bytes) and `initramfs-virt` (HTTP 200, 8,922,335 bytes); Ubuntu Jammy
arm64 updates package index (HTTP 200). HEAD observations were made on November
9, 2026 at approximately 13:45 UTC. These moving URLs require hashes/version
metadata to be captured at download, not an assertion that today's files are
permanently pinned.

The host has no evidenced QEMU executable. The plan installs tools only into an
owned disposable container derived from the existing Ubuntu image. It never
stops or resets OrbStack, changes host packages, mounts host devices, uses
privileged mode or touches another container. No container or emulator has yet
been launched by this lane.

## Exact preparation envelope

Use a unique name and label `gherrit-exh-1109-power-<nonce>` and bind only this
lane's newly created `recovery/vm/<nonce>` directory to `/work`. Start the owned
Ubuntu preparation container with `--cpus=1 --memory=768m --pids-limit=128`.
Its only package commands are `apt-get update`, followed first by
`apt-get --simulate --no-install-recommends install qemu-system-arm busybox-static
cpio e2fsprogs curl gcc libc6-dev`. Preserve the simulation. Reject before install
if the reported additional size exceeds 900 MiB or free host space falls below
8 GiB. Then run the same install with `-y`, confined to this container. Preserve
exact installed versions; clear only that container's downloaded apt archives.
The preparation container and its writable layer plus experiment outputs must
remain below 2 GiB, checked using `docker inspect --size` and local file sizes.

Download the two available Alpine artifacts and their `.sha256` companions into
`/work`, verify and retain the bytes/hashes. Unpack the initramfs preserving its
kernel modules. Inspect that it contains virtio block and ext4 dependencies; if
not, stop and report the missing driver rather than broadening downloads. Replace
only the guest `/init`, add static BusyBox and a statically linked small C probe
built with `gcc -static`; retain the complete source and resulting initramfs.
The init mounts proc/sys/dev, loads virtio/ext4 modules, mounts `/dev/vda`, runs
the probe and emits exact serial barrier lines. No guest network is configured.

Create a 64 MiB raw disk using `truncate -s 64M` and `mkfs.ext4 -F` inside the
owned container. Make separate copies per case. Use QEMU's TCG software engine:

```sh
qemu-system-aarch64 -machine virt -cpu cortex-a57 -accel tcg -smp 1 -m 256M \
  -nographic -no-reboot -kernel /work/vmlinuz-virt \
  -initrd /work/test-initramfs.gz \
  -append 'console=ttyAMA0 panic=-1' \
  -drive if=none,file=/work/case.raw,format=raw,cache=writeback,id=d0 \
  -device virtio-blk-device,drive=d0
```

Run only the uniquely owned QEMU process, with 60-second boot/probe deadlines.
At an observed probe barrier, send SIGKILL to that owned emulator PID, without a
guest shutdown. Reboot a fresh emulator against that same case disk, mount it
and inspect journal/ref/checkpoint bytes and filesystem recovery diagnostics.
Use an independent final synced marker to prove the control can persist state.

## Discriminators and limits

The probe writes old complete JSON, syncs it, then writes a new temporary record.
Cut once each after (1) write without fsync, (2) temporary-file fsync, (3) rename
without directory fsync, and (4) directory fsync. Repeat with an fsynced journal
before ref and checkpoint writes, and verify recovery accepts only complete
matching generations. A no-fsync negative control challenges the conclusion:
its survival does not prove that fsync is unnecessary. Capture C syscall results,
serial barriers, kernel version, filesystem options, QEMU version, raw disk
hashes and exact recovered contents.

Killing QEMU simulates abrupt loss of the guest CPU/memory and QEMU userspace
cache. The host, OrbStack guest and their filesystem/device caches remain alive.
`cache=writeback` advertises guest flushes, but this does not establish physical
hardware cache behavior or whole-host power-loss durability. Report a **guest
abrupt-power-cut experiment** with that boundary, separately from ordinary
process SIGKILL, a persistence-prefix model and real machine power loss.

Cleanup may stop/remove only the exact labeled owned container/emulator after
preserving source and evidence. Do not prune Docker, remove base images or
remove unexplained resources. Approval is requested from the coordinator before
any preparation launch, package install or guest execution.

*Authored by an AI agent acting on joshlf's behalf.*
