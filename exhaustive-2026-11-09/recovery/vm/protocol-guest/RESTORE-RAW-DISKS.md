# Restore the completed raw disk copies

`retained-raw-disks.tar.gz` preserves the six raw files listed in
`RAW-DISK-ARCHIVE.json`. Every member's full bytes, size, mode, UID and GID were
verified before removing expanded copies; the manifest also preserves exact
outer modification/access timestamps. The filesystem inside each raw image is
preserved byte for byte. Pre/post gzip evidence and logs remain separate.

No guest or controller was active when the archive was made. The forensic audit
reads the retained pre/post gzip images. Old controllers refuse an existing output
directory; this archive does not authorize replaying or repairing a frozen case.

To restore a raw file for read-only inspection, first verify the archive SHA256
against the manifest, then extract that named member beneath this directory with
`tar -xzf retained-raw-disks.tar.gz path/from/manifest.raw`. Refuse any existing
target, and check its full SHA256, size and mode against the manifest afterward.
Use the recorded UID/GID only when permitted; the archive retains them even if
the extracting user's tool cannot apply ownership. Exact nanosecond outer times
can be restored with Python `os.utime(path, ns=(atime_ns, mtime_ns))` using the
manifest. No archive member has an absolute path, symlink or parent traversal.

The archive is local evidence, excluded from the public source bundle. Its hash
does not make the images publicly inspectable. Kernel/runtime images and build
receipts are retained separately; restoring a disk is not a machine-power-loss
test or permission to resume native writes.

*Authored by an AI agent acting on joshlf's behalf.*
