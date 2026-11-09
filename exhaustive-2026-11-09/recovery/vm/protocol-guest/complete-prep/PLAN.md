# One fresh complete-prefix trial: source only

The continuation's retained result lists `complete` as NOT RUN after the
`result_checkpoint` diagnostic. This new wrapper requests only that previously
unperformed prefix on one fresh 32 MiB filesystem fixture. It does not retry or
repair any earlier case. Root owns all runtime effects and must issue a new
exact grant after reviewing these source hashes.

`complete_controller.py` loads the unchanged reviewed continuation collector at
SHA256 `867796c89ff237a496735e582f311396b7be79428ce5e527130b880cb9186ced`.
It uses that collector's existing source pins, module loader, resource guards and
`collect_case("complete", ...)` exactly once. The only collector configuration
override is the private imported module's output path. No boot, pause, recovery,
archive, lifecycle or oracle rule is replaced. The original files remain intact.

New root-owned paths are:

- Wrapper: `/lab/protocol-guest/complete-prep/complete_controller.py`.
- Grant: `/lab/protocol-guest/COMPLETE-GRANT.json`.
- Output: `/lab/protocol-guest/actual-results-complete-001`.

The exact grant has coordinator `root`, these `grant_path`, `root` and `out`
values, `cases=["complete"]`, `disk_bytes=33554432`, and the existing kernel,
initramfs, Python and Git stdout identities. `source_hashes` must equal all six
unchanged collector `SOURCE_PINS`, the reviewed continuation collector path/hash,
and the new wrapper path/hash. Missing or additional scope/hash entries refuse
execution. Existing output refuses reentry. The wrapper never reads an old
runtime grant as authority.

The base creation/fsync and one-case collection retain the reviewed envelope:
one 256 MiB/one-vCPU guest, no NIC, fresh base plus one working disk, at most two
boots, exclusive fsynced intents/logs, bounded child ownership and exact
pre/post disk archives. The unchanged collector retains failed verdicts, stops
on incomplete/unknown collection and deletes only a safely archived owned
working disk. Earlier failed disks, records and oracle remain frozen.

After its separate grant, root's command is:

```sh
/usr/bin/python3 /lab/protocol-guest/complete-prep/complete_controller.py
```

The focused offline controls check the exact new grant/source vector, one
explicit forwarded `complete` call, unchanged oracle forwarding, preservation
of a failed verdict and the original NOT RUN evidence. They use fake command
results and a one-byte temporary placeholder, not a filesystem or Git fixture.
The inherited eight collector controls are rerun unchanged except that their
private temporary directory is placed under this new preparation directory.
No runtime, build, install, network, actual Git or emulator action is performed
by these checks.

This remains one observation of the exact local prototype with Linux Git 2.34.1
and ext4, including default-relatime reads and RW journal replay. It supplies no
cross-version, hardware-power-loss, production or native-provider promise.

*Authored by an AI agent acting on joshlf's behalf.*
