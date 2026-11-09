# Actual completion did not retain two new Git refs

The actual worker returned `{"status":"complete"}` before the owned guest was
cut. On the next boot, two newly created Git refs were already broken before
logical recovery; the post-recovery raw image confirms **zero-byte files**.
The complete operation record, exact checkpoint and attributed request / receipt
survived. The worker then refused `invalid_completed_attachment`.
Independent Git fsck reported broken refs, and the host oracle rejected the
trial. This is a concrete durability gap in this experimental completion
protocol; the refusal and verifier are detecting the failure correctly.

Only two planned cases ran: `validated` passed, then `after_return` failed and
stopped the campaign. Nothing here represents the other nine unexecuted prefixes.
This audit did not replay the case or operate Git, a guest, container or network.

## Exact loss and surviving evidence

The intended result is commit
`146dd60ac30597e6b3ab3e69b31a7e74411ac7c3`. Both new refs should contain its
40 ASCII hexadecimal characters followed by a newline: 41 bytes.

| Path under `/state/scope/case-after_return` | Recovered bytes |
| --- | --- |
| `repo/.git/refs/retained/completed-case-after_return` | Empty file; inode 93, size 0. |
| `provider/repo/.git/refs/archives/op-case-after_return` | Empty file; inode 95, size 0. |
| `provider/repo/.git/refs/heads/A` | Exact 41-byte intended result, replacing the previous head. |
| `repo/.git/refs/retained/result` | Exact 41-byte intended result. |
| `operation.json` | Exact 928-byte complete operation, including its receipt. |
| `result-checkpoint.json` | Exact 370-byte checkpoint naming the now-invalid continuation. |
| `provider/state.json` | Exact 365-byte record with one intended request and one matching receipt. |

The zero SHA shown in `git fsck` is a diagnostic for an invalid reference. It is
not the literal file contents: a bounded read-only ext4 inode/extent parser finds
empty files, not forty zero characters. The post-recovery image's JSON bytes
independently match the serial snapshots. All six original Git objects in each
repository match their complete body bytes, object types, sizes and Git SHA1
identities; all twelve loose-object copies in the image independently decompress
to those same bytes. The authoring ref and retained input/result remain valid.
No commit-object or authored-tree loss was observed in this trial.

Before logical recovery, `for-each-ref` already warns that it is ignoring each
broken ref, despite returning exit0. Both local and provider Git fsck return
exit2. After the worker's refusal, those refs and diagnostics are unchanged.
The request/receipt store also remains unchanged: recovery did not dispatch a
second request. The host oracle stops at `git_fsck_failed:local`; this audit
separately exposes the provider archive failure that the short-circuited verdict
does not enumerate.

Unsynced diagnostic JSONL also contains zero-filled ranges: 1,283 NUL bytes in
the 6,097-byte local log and 722 in the 923-byte provider log before logical
recovery. These logs cannot supply a lossless sequence of pre-cut commands.
The fsynced operation/store records and actual returned serial result are the
stronger outcome evidence.

## Boundary and interpretation

The cut receipt records child 4786, the exact `after_return` barrier, an issued
kill and exit -9. Recovery child 4790 exits naturally with the clean-unmount marker.
The guest records Python 3.10.12, Linux Git 2.34.1, the pinned source hashes and
an ext4 `rw,relatime` mount. The frozen source performs a final live validation
before returning complete; therefore another ordinary read would not itself
repair the durability promise. A value can be readable in the running guest
without surviving its abrupt loss.

The source fsyncs and atomically replaces JSON records. Its Git helper waits for
`git update-ref` and appends a diagnostic log, but supplies no separately
established durability barrier for the new loose-ref contents and their names.
Fsyncing the surrounding operation/checkpoint JSON was insufficient in this
observed sequence. This is evidence about the prototype's persistence ordering
with this exact Git/ext4 configuration. It does not establish a Git bug, a
cross-version default, a GitHub storage failure or a provider-arbitration rule.

The pre-recovery raw image is preserved exactly at SHA256
`d01982283c7a24a3af7c8692e67af991fa052ba59f28fdcce9ab7e08ba672f11`;
the post-recovery image is
`fe4e991d31ab192566faab65da281da11c1fc8955147fc4a14ffbbb5b1904933`.
Both gzip files independently verify against their recorded full raw-byte hashes.
The simple image parser performs no journal replay. Its pre-image home metadata
still shows older records and is **not** treated as the effective replayed view.
The serial before-recovery view follows the disclosed RW mount/journal replay;
the exact empty-file byte proof comes from the cleanly unmounted post image.

Ext4 fsck's post-recovery exit 0 does not certify Git semantics. Its output also
contains a future-write-time warning. The independent Git checks correctly
reject the invalid ref files despite structurally recoverable filesystem data.
Outer container, host and storage caches survived; physical power loss was not
tested. Existing Git objects were deliberately synced at baseline.

## Candidate fix obligation

The candidate must establish durable Git result dependencies before installing
a durable completed checkpoint or confirming an authored archive. This includes
the relevant ref contents, required objects, namespace entries and ordering,
using a verified mechanism for the selected Git version/backend/filesystem.
Do not assume an unrelated JSON fsync, a successful subprocess exit or a live
ref reread supplies that guarantee. No particular Git configuration flag has
been validated by this audit.

Retain the current fail-closed recovery behavior when completion evidence names
a malformed or missing attachment. Repair must preserve the old intent, exact
objects and receipts and must not recreate a new request or blindly resend.
Any implemented barrier or explicit repair protocol needs a new independent
fixture and the same strict oracle; this failed image and verdict must remain
frozen. A local provider emulator's ref durability is not evidence for GitHub's
remote durability or cancellation semantics.

`FINDINGS.json` retains exact serial/object/file results, hashes, physical inode
offsets, parser limits and diagnostic-log counts. `audit.py` is the reproducible
pure reader used here. It writes only this new audit record and never changes
the evidence images or candidate package.

*Authored by an AI agent acting on joshlf's behalf.*
