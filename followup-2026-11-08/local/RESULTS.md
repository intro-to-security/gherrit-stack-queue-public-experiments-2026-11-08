# Local follow-up results

The range importer passed the broader synthetic tree checks, while new recovery
probes exposed gaps in the cooperative prototype. **A completed marker alone does
not validate its continuation, missing operation evidence can be replayed by the
worker, and two stale workers can dispatch the same effect twice.** These are
local prototype findings. They establish neither a production GHerrit defect nor
production correctness.

All 30 planned case IDs have evidence-backed dispositions in
[CASE-MATRIX.md](CASE-MATRIX.md) and [RESULTS.json](RESULTS.json). The unchanged
prior harness passed 122/122 assertions. Seventeen new grouped probes completed
with their intended oracles after two retained fixture corrections. Passing a
negative probe means the weakness was observed; the matrix separately marks
L13, L14, L16, L28 and L29 as **model failures**. L27 is concretely unavailable in
this lane. No network call, hosted mutation, production change, global hook or
global configuration change was made.

## What the importer evidence supports

Three deterministic seed values each went through six A/B import rounds with
changing comparison parents, independent hosted edits and retained local edits.
Every A and B tree matched an independently constructed expected file map; B's
patch owned only its three intended paths, and both exact local message bodies
survived. Three unchanged reimports preserved the final tree. The scratch commit
IDs changed, so these checks do not implement or establish a publisher's no-write
or no-new-archive policy.

New exact-object fixtures cover rename plus hosted content edits, executable-bit
mode plus hosted content edits, deletion plus independent hosted edits, and binary
local content plus independent hosted edits. The oracle compares file modes and
blob bytes, including NUL and non-UTF-8 bytes. Rename/rename, modify/delete and
binary/binary conflicts stopped explicitly with original objects and conflict
trees retained. Each fixture's input ranges, merge results, exact expected/output
entries and binary patches are saved in the final extension run.

Two-commit local and hosted ranges integrated to the expected net tree while
preserving B's ownership and the local group's tip message. The accepted A layer
was flattened to one commit; this is a net-range prototype, not evidence that
individual intermediate commit identities or messages are preserved. A revert
represented as new change R and an explicitly accepted reset behaved as supplied.
The unchanged baseline also exercises actual `commit --amend`, `rebase` and
`revert`. Author mapping/reset intent remains an input, not an inferred policy.

The baseline rerun retains F-before-B ownership and workspace protection. The
prior [hosted integration](../../native-stacks-2026-11-08/local-git/hosted-integration/RESULTS.md)
is reused for the executable dependency: B succeeds with F below it and fails
specifically for the missing field without F. That earlier hosted sequence also
retains its inconsistent observation and corrected status oracle; it is not
relabeled as an all-green service guarantee. No hosted fixture was replayed.

## Recovery findings

The unchanged baseline kills eight real child processes at its planned,
dispatch-intent, effect-applied, acknowledgement, ref, checkpoint and completion
prefixes. Repeated recovery of each retained state made no second request;
indeterminate effects remained blocked, including when the emulator had no
request. Moving committed source plus staged, unstaged and untracked bytes stayed
unchanged through fresh-continuation acceptance.

The new probes distinguish the boundary around that success:

| Case | Observation | Consequence for the prototype |
| --- | --- | --- |
| L13 | Acknowledged recovery rejects an occupied wrong ref and incompatible checkpoint. After `complete`, deleting either the continuation ref or continuation checkpoint still gives worker exit 0; transfer admission says eligible. | Completion recovery/admission lacks a check of the claimed durable result. |
| L14 | After the emulator applied an effect, deleting `operation.json` makes separate custody admission refuse. Calling the worker directly recreates planned intent and sends another request: 1→2. | Missing evidence must be enforced at the worker boundary; a separate cooperative checklist is insufficient. |
| L16 | Simultaneous workers race on shared `.new` paths or fresh Git refs. One retained run recorded two requests; another failed before a second recorded request. | The prototype assumes one cooperating writer and has no enforced concurrent owner. Final-store counts can undercount racing effects. |
| L28 | Both real processes cache `planned`; the first completes, then the stale process resumes. Both exit 0 and a serialized emulator store records exactly two requests. | Duplicate dispatch remains possible without any lost-update ambiguity or temporary-file race. |
| L29 | The pending manifest names operation X, but its completed record names Y. Admission still permits mutation. | Admission checks completion without binding record identity to the manifest. |

The original worker is preserved unchanged. These probes deliberately challenge
missing/damaged evidence or the single cooperating publisher premise; they do
not show that ordinary SIGKILL alone loses a successfully fsynced file. The next
implementation needs its admission, ownership, identity and completion checks at
the dispatch/recovery boundary. These findings do not require a new architecture
by themselves and do not justify repairing unknown provider outcomes by retry.

Missing bindings, accepted checkpoint, pending manifest or operation record each
withheld cooperative transfer admission. A full custody copy retained the
unknown-effect guard and completed from the emulator's explicitly attributable
receipt without resending. That local receipt has deliberately defined semantics;
it supplies no GitHub idempotency or settlement contract.

## Journal and Git controls

Seven further real SIGKILL prefixes surround temporary creation, buffered partial
write, full write, flush, file fsync, rename and directory fsync of a 64 KiB JSON
journal. Every visible checkpoint parsed as the complete old or new document:
old before rename, new after rename. Orphan temporary files remain as evidence.
SIGKILL leaves kernel/filesystem caches running. Device power loss, torn writes,
controller behavior and actual fsync durability remain untested.

Injected file-fsync failure raised before replacement and left the old JSON.
Injected directory-fsync failure raised after replacement and left the new JSON
visible. A failed durability call therefore cannot be interpreted as proof that
the replacement did not happen; crash durability after that failure is unknown.

Two divergent concurrent Git publications used explicit old-head and absent-tag
leases with `--atomic`. Exactly one coupled head/archive target won; the losing
push changed neither ref. With identical targets the simultaneous attempts raced,
but a subsequent identical stale-lease retry succeeded with both refs reported
`up to date`. A stale lease on an equal, unchanged head also failed to guard a
new archive write. Its packet trace is retained. Finally, old→intervening→old ABA
returned the head to its expected value and allowed the next value-based lease.
Atomicity couples actual updates; equal lightweight refs and value leases do not
establish unique operation ownership or generations.

Historical exact base/tip patches excluded unrelated parent drift, while the
tip-to-tip patch included it. `range-diff` recognized the identical authored
patch. For a very small changed patch it rendered unmatched old/new entries
rather than pairing them with `!`; exact patch bytes independently established
the change. This is why matching heuristics are not the whole comparison oracle.

## Commands and the pinned adapter

Fresh hook fixtures show that outer `git push --dry-run`, an unrelated outer
refspec and an outer deletion can each run a hook that publishes the current
branch to its own different local sink. The prior dry-run experiment is reused
for the exact captured hook-input equality between dry-run and actual push.
Retained GHerrit source also states its current pre-push path chooses the current
branch and `gherrit.remote`, ignoring outer destination/ref records. No production
hook was invoked or changed.

A tiny explicit local publishing prototype made no dispatch on dry-run and then
published only its captured SHA and exact sink, even after the live source moved.
That demonstrates a feasible command boundary, not human usability or a completed
GHerrit command.

The retained `github/gh-stack` v0.3.0 darwin-arm64 binary matched SHA-256
`70c0cb11346ad5d4f97a02a5cf5242052254d1775d356dc0759f035457873850`.
Its version/help and parser rejection paths ran locally. Fifteen pure adapter
inputs accepted the canonical adjacent/open same-repository case and rejected
numeric ambiguity, host spoofing, another repository, duplicate identity,
reversed order/wrong base, merged/auto-merge/cross-fork state, implicit trunk,
`--open`, `--no-atomic`, its environment override and URL suffixes.

Five `link --help` subprocess samples took approximately 12–13 ms each here.
This measures local startup/help cost only. Network, live validation, API calls,
transport and human work are excluded. Exact samples, source hashes, the release
versus inspected-source relationship and source/license copies are retained.
The earlier [CLI effects](../../native-stacks-2026-11-08/cli-history/RESULTS.md)
remain the evidence that canonical URLs can still repair bases, `--open` can
change readiness before failure, and broad submit does not publish GHerrit's
archive tags. The local validator does not make those writes atomic or supply a
provider handoff.

## Evidence and limits

- [PLAN.md](PLAN.md) records cases and bounds before execution; its three later
  discriminators follow the observed recovery failures.
- [RESULTS.json](RESULTS.json) binds each ID to its precise run and evidence.
  Inputs, output refs, command receipts, byte snapshots, raw errors and exact
  source versions remain in the run directories.
- [HARNESS-CORRECTIONS.md](HARNESS-CORRECTIONS.md) explains the two retained first-run
  fixture errors. The corrected probe run did not edit the original prototype.
- [OBJECT-VERIFICATION.json](OBJECT-VERIFICATION.json) reports successful
  `git fsck --full --no-reflogs` for all **111** retained local Git stores,
  including copied negative fixtures. Object integrity does not verify protocol
  correctness.

Actual machine power loss is outside this lane's authority/capability. Production
mapping, arbitrary merge/shared-prefix authoring, cryptographic signing choices,
independent author/reviewer usability, provider guarantees and genuine in-flight
network loss remain unestablished here. Root and other lanes own the authorized
hosted experiments. No synthetic probe is substituted for a human study or a
service contract.

*Authored by an AI agent acting on joshlf's behalf.*
