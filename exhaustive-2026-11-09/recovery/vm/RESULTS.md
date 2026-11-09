# Guest crash recovery evidence

The owned guest tests observed a lost unsynced rename and a surviving
directory-synced replacement. A stronger extension retained exact multi-block
records, rejected corrupt active data and false completion markers, and kept
pending output distinct from completed work. These are ext4/QEMU file-protocol
observations with outer host/device caches alive. They do not establish production GHerrit, macOS or physical power-loss durability.
The separate actual Git extension below found and repaired a narrower local gap.

## Eight initial persistence prefixes

The [verified v3 archive](7e278a42e7/ARCHIVE.json) retains all original inputs,
sources, serial logs and disks, including two unsuccessful preparation boots.
The completed v3 run has eight single trials and sixteen boots. Each trial
reached its recorded barrier, then the controller killed only its own exact
emulator child and booted a new guest against that disk.

| Prefix | Observed recovered record |
| --- | --- |
| New temporary record written without fsync | Old current record; temporary record absent. |
| Temporary file fsynced | Old current; complete new temporary record. |
| Rename without directory fsync | Old current and complete new temporary record: the rename did not survive this cut. |
| Rename plus directory fsync | Complete new current, renamed temporary absent. |
| Additional full-sync control | Complete new current. |
| Durable intent only | Old output/checkpoint with the intent retained. |
| Durable output before checkpoint | New output, old checkpoint; pending reconciliation. |
| Durable output and checkpoint | Matching new generations; no separate completed-operation receipt was modeled. |

The original small-record oracle accepted too little evidence: some checks used
only generations and the original pre-inspection disk bytes were not retained.
[Independent audit](extension/AUDIT-v3.md) checked the actual full values and
barrier receipts, preserved those limits, and motivated the extension rather
than treating the first green exit as adequate acceptance evidence.

## Twelve stronger cases and a clean-inspector control

The [extension plan](extension/PLAN.md), [source manifest](extension/SOURCE-MANIFEST.json)
and [actual results](extension/guest-results/RESULTS.json) describe twelve single
trials, twenty-five boots including a separate clean inspector, and records of
65,672 bytes containing a 65,536-byte payload. The actual serial readback carries
the complete bytes. The oracle checks exact values, payload and complete-result
SHA256, intent identity, retained result and checkpoint/output association.

All twelve expected dispositions occurred. The normal prefixes distinguish an
unpublished temporary file, a valid active record, pending intent, a completed
output prefix, pending finalization and validated local completion. Deliberately
truncated unpublished data remained unaccepted; deliberately truncated active
data was refused. A false done marker with an old checkpoint and a valid-JSON
payload with an invalid checksum both refused completion. These four bad inputs
were injected deliberately; they are not claimed as crash-caused corruption.

Every cut disk was losslessly compressed, verified and fsynced **before** the
read-write recovery mount. Each post-inspection image was separately retained.
The working raw copy was removed only after both archive verifications.
[Root's independent readback](extension/ROOT-VERIFICATION.json) matched all
complete serial bytes to recorded hashes, checked the active values and bad
controls, and verified all twenty-four pre/post image archives. The exact
resource and failure boundaries remain attached to these checks.

## Filesystem diagnostics are separate evidence

All v3 and extension second-cut inspections returned e2fsck exit 0 **with**
warnings about skipped journal recovery, wrong free counts and declined fixes.
They must not be described as clean filesystems. The inspector had mounted
read-write and replayed the first crash, then was itself killed; those diagnostics
do not inspect the first-cut image unchanged.

The separate control restored stage 4's exact pre-inspection image, read it,
successfully unmounted and powered off normally. It retained the expected file
record and produced exit 0 **without** those warnings. This validates a useful
diagnostic contrast; it does not turn the original abrupt cut into a clean
shutdown or prove physical-device behavior.

## Inputs, retention and remaining scope

The guest uses the checksum-pinned Alpine 3.22.8 kernel 6.12.115, QEMU 6.2 under
the owned Ubuntu 22.04 container, one TCG CPU, 256 MiB guest RAM and virtio/ext4
ordered data mode. It has no guest network, host device, privileged container or
shared-runtime reset. The outer container, host and device caches survive.
The two failed preparation boots exercised neither durability case; their logs
and sources remain retained.

The full v3 archive's 316 file hashes were checked after host copy; tar also
compared expanded contents and metadata before reclaiming 13 old raw disk copies
(872,415,232 logical bytes). [Restoration](7e278a42e7/RESTORE.md) preserves exact
paths and required contents. The exact runtime images are retained and their gzip/image hashes verified.
The owned container is stopped and retained for reproduction; no shared store
was pruned. This report's JSON output pointers are not Git refs or an externally
attributed provider receipt.

## Actual Python and Git completion

The [actual extension](protocol-guest/RESULTS.md) now covers all eleven original
prefixes on fresh fixtures. Five met expectations; six exposed failure or a
collection diagnostic: two correctly refused broken local completion attachments,
three returned complete with broken local-provider archive dependencies, and one
raised during recovery. Original objects survived in captured recovery snapshots.
The initial after_return case independently proved two zero-byte new ref files.
These observations invalidate a completion-durability claim based only on JSON
fsync and a successful live Git read.

A separate scoped loose-ref file/directory barrier variant passed all eleven
unchanged strict expectations, on fresh fixtures. Root reproduced each verdict,
verified all twenty-two runtime records/barrier paths and twenty-two pre/post
archives. This supports the repair for the captured Git2.34.1/ext4 fixture. It does
not validate new-object persistence, every cut timing, general Git backends,
GitHub storage, macOS or physical host/device loss.

Six redundant expanded raw copies (201,326,592 logical bytes) are preserved in a
verified 980,256-byte lossless archive with required outer metadata and a
[restoration procedure](protocol-guest/RESTORE-RAW-DISKS.md). The separately
measured free-space increase during removing those expanded copies was
122,880,000 bytes; concurrent host work and APFS accounting confound attribution.
[Exact records](protocol-guest/RAW-DISK-ARCHIVE.json) keep logical/apparent sizes
separate from measured physical free space. All source, logs, Git histories,
failed verdicts, runtime inputs and pre/post archives remain retained.

*Authored by an AI agent acting on joshlf's behalf.*
