# Restore the retained guest experiment

`lab-evidence-v3.tar.gz` preserves the original `/lab` tree, including all v3
and failed-boot sources, exact disk images, logs, kernel/module inputs, compiled
probe and test initramfs. `ARCHIVE.json` identifies its bytes and SHA256.
`ARCHIVE-VERIFICATION.json` records316 matched file hashes after the host copy;
GNU tar also compared the original archive with the expanded container tree.
Ownership, modes, symlinks and timestamps are preserved by the tar format.

Restore into a fresh directory inside an owned disposable Linux container:

```sh
mkdir -p /lab-restore
tar -xzpf /path/to/lab-evidence-v3.tar.gz -C /lab-restore
cd /lab-restore
sha256sum -c EVIDENCE-SHA256.txt
```

To reconstruct the original recorded paths, restore into `/lab` in a new owned
container instead. Do not extract into a host root or execute guest symlinks on
macOS. Keep failed runs and results intact. To repeat a trial, create a new
output/disk namespace and preserve a new intent; existing controllers deliberately
refuse existing result directories. QEMU command lines and exact package versions
are retained. The owned runtime remains available pending the extension and
separate verified runtime preservation/cleanup.

The old raw disks have no active emulator or current consumer. Once their exact
hashes match this verified archive, their expanded copies can be removed to keep
the resource envelope bounded. Historical command paths remain evidence; they
are restored from the archive when needed. This does not authorize removing the
kernel, current test initramfs or runtime while later tests use those paths.

*Authored by an AI agent acting on joshlf's behalf.*
