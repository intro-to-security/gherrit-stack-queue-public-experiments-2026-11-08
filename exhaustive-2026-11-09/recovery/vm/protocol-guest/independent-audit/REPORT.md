# Independent package audit

This audit used only the named package, pinned worker/helper source, offline test
data and root's newly added controller. No candidate source was edited. All
process/network entry points were blocked during the checks; driver probes used
fake streams/processes. No Git fixture, build, container, guest or network action
was performed. Exact tested source hashes and outputs are in `CHECKS.json`.

Root fixed the two controller findings and three baseline-semantic oracle
counterexamples before guest execution. The final blocked-effect retest passes:
six candidate test methods, four fake-process probes and rejection of all three
oracle mutants. No further concrete source blocker was found for the stated
bounded trials. This is not a result from executing a guest.

The initial eleven manifest file hashes matched, and both retained prototype files
also match their recorded original paths. The inspected helper import defines
functions/state but creates no fixture or subprocess. The guest assigns the
fixture's declared RUN path and replaces only `protocol.pause`; recovery does
not replace validation or dispatch. Its baseline explicitly syncs existing
objects. These cuts therefore concern ref/receipt/checkpoint continuation, not
creation of new objects under interruption.

## Actionable findings

1. **Resolved: unexpected emulator exit accepted after the marker.** In initially tested
   controller `e44e0e2329cfb4754e4bb78ee3c688a8288626c52fac3990fe4ee7f881c923e2`,
   a fake reached cut marker followed by exit0 or exit1 returns accepted data,
   without issuing a kill. Both outcomes passed `boot`'s final predicate. A
   graceful or error exit does not establish the requested abrupt guest cut.
   Root added explicit kill-issued and exit-9 requirements. The final fake
   exit0/exit1 controls now reject with the intended premise error; the normal
   alive-child control is killed/reaped once.

2. **Resolved: baseline semantic consistency was trusted.** Three initial pure
   complete-result mutants passed: replace `bindings.json` with `{review:999}`,
   replace custody with `{owner:'/foreign',token:'wrong'}`, or replace the
   original checkpoint with `{accepted_local:'foreign'}` consistently in
   baseline/before/after, while leaving frozen intent unchanged. The oracle
   compares those records with baseline but does not independently bind them to
   intent/directory/expected custody. The actual frozen source worker would
   refuse them, and the current fixture constructs valid records, so these are
   oracle trust-boundary witnesses rather than observed worker failures. Root
   added explicit binding/checkpoint, provider/directory and custody/path checks.
   The independently repeated mutants now all reject.

3. **Observer neutrality needs qualification.** Init requests a default ext4
   mount, without `noatime`. The baseline snapshot follows `os.sync`, and the
   before-recovery snapshot reads every record/ref/object before logical
   recovery. Under access-time-updating mount options these reads can queue
   metadata writes. No extra explicit fsync was found in these snapshots, and
   record contents are not deliberately changed, but they are not necessarily
   filesystem-metadata-neutral. Root retains default-relatime as part of the
   measured environment rather than changing the frozen image. RW mount journal
   replay is already correctly disclosed.

Root fixed the earlier log-open ordering finding before guest execution. The
corrected controller opens the exclusive serial log before Popen. The offline
log-open failure probe now spawns zero children. Once a process is started, the
normal probe enters the cleanup guard and kills/reaps that exact fake child.

## Concrete checked limits

- All six current offline test methods pass with external actions blocked.
  Their modeled prefix checks and eight damaged-completion controls are useful;
  they do not establish actual guest or Git behavior.
- The complete oracle independently verifies provider head/archive, exact
  request/receipt identity and count, local continuation/checkpoint, retained
  input/result, all object bodies and their Git SHA1 identities. This can expose
  a complete response that the worker's own local-only completion check accepts.
- Before-recovery Git reads use direct subprocess capture, so they do not append
  prototype command logs. The source worker's normal unsynced JSONL writes remain
  part of the actual experiment. No unexpected dispatch or explicit sync was
  found in the serial pause adapter.
- The controller verifies a granted input image/kernel and source hashes, but
  its current boot path only requires that the runtime record exists. Bind the
  runtime phase/prefix/source pins to the requested trial if independent receipt
  attribution is required; the guest/image currently supplies that trust.
- Recovery ends with a clean unmount, which flushes recovery writes. The post
  image therefore cannot alone establish durability against a second crash
  immediately after recovery returned complete. The planned first-cut outcomes
  and normal `after_return` case remain distinct from that untested claim.
- The builder's ELF closure is explicit and bounded. ELF `ldd` closure is not a
  proof of all runtime data, dlopen modules or Git helper requirements. The
  selected fixture uses local builtin Git commands; root reports chroot Python
  imports passed and Git startup reached a missing pre-devtmpfs `/dev/null`.
  Guest init mounts devtmpfs before execution. The first actual positive trial
  must still establish the full selected runtime path.
- Staging receipts follow file symlinks when hashing `stage_files`; absolute
  links can resolve against the build host rather than the staged root. Retain
  symlink text in the initramfs-content audit and do not treat that file list
  alone as a complete guest-resolution proof. The explicit Python/Git/ELF
  copies and final initramfs hash supply separate evidence.
- The root controller's verified/fsynced pre/post archives, exclusive files,
  stop-on-mismatch and raw-disk retention preserve failures. Storage/resource
  limits are fixed, and no same-case write retry was found.

This is a source/offline audit. It makes no conceptual convergence, production
acceptance, provider arbitration or physical-power-loss claim.

The final tested controller is
`876b7b223a87c714d1e86e161d07995e7c5ec0880e74da4d3348e2a2452c9f74`;
the host oracle is
`d877a1a218e0585fdf0630003dd69054b3bb5dd4c4ef8a4947043dc24cbe1e07`.
`CHECKS.json` records the complete tested identities. At the final metadata check,
the package manifest still pinned the pre-fix oracle/test hashes; root must
refresh that manifest and the exact runtime grant before execution. The guest,
init and actual prototype source remain unchanged. Earlier results and the first
report are retained in `history/1794239157693200000`.

*Authored by an AI agent acting on joshlf's behalf.*
