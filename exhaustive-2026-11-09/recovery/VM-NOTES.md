# Guest probe recommendations

Use a static C probe with `open`, complete checked `write`, `fsync`, `rename` and
directory `fsync`. Keep console barrier output separate from disk writes: write
the barrier to the serial console only after the named syscall returns, then
block on a pipe/read or `pause`. Do not call `sync` after a cut barrier. The host
must kill the owned QEMU process after observing the serial barrier, not merely
after elapsed time. A guest `/init` should mount proc/sys/dev first, load only
the retained initramfs's virtio/ext4 dependencies and report mount options.

Use `old` JSON generation 0 with complete payload and checksum, then call file
and directory fsync before starting generation 1. The new temp record should
include a different checksum and at least 64 KiB of distinct payload. Capture
every syscall return and errno. After reboot, compare parsed complete records,
generation, byte hash, length and referenced object identities. Do not treat
either a new visible file or an exception as a completed cross-resource result.

The journal/ref/checkpoint probe should keep a durable intent naming exact old
and new generations. Cut between each write and its fsync. Recovery must refuse
missing or mismatched result evidence even if a completion-looking scalar file
survives. Include a deliberately bad scalar-only recovery control to demonstrate
that the independent artifact oracle catches the inconsistent combination.

Prefer an additional QEMU `cache=none` run if supported after the writeback
control, retaining exact flush/cache configuration. Neither setting makes killing
QEMU a whole-host/device power-loss test. Guest driver/module availability is a
boot premise; report it separately from journal correctness if it fails.

*Authored by an AI agent acting on joshlf's behalf.*
