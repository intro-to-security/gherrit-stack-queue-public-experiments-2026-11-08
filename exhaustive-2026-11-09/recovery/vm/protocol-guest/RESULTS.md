# The actual Git prototype needed durable ref dependencies

All eleven original interruption prefixes were eventually exercised on separate
fresh fixtures, with twenty-two boots. Five met their original expectations; six
did not. The separate scoped durable-ref variant then met all eleven unchanged
expectations on fresh fixtures, also with twenty-two boots. These are observations
of the exact experimental Python dispatcher, Linux Git2.34.1 and ext4 guest.
Existing objects were synced before dispatch; outer host/device caches survived.

## Original outcomes

| Prefix | Actual recovery | Independent verdict |
| --- | --- | --- |
| validated | Complete after one new dispatch. | Pass. |
| marked | Unknown, no resend. | Pass. |
| request_logged | Unknown, no resend. | Pass. |
| provider_head | Unknown, no resend. | Pass. |
| provider_archive | Unknown, no resend. | Pass. |
| provider_receipt | Complete, despite a broken emulator archive. | Fail: provider Git fsck. |
| acknowledged | Complete, despite a broken emulator archive. | Fail: provider Git fsck. |
| result_ref | Complete, despite a broken emulator archive. | Fail: provider Git fsck. |
| result_checkpoint | RuntimeError when trying to update a broken continuation; no recovery result/after snapshot. | Nonpassing collection diagnostic. |
| complete | Refused invalid_completed_attachment. | Fail: local Git fsck. |
| after_return | Refused invalid_completed_attachment after the pre-cut worker had returned complete. | Fail: local Git fsck. |

The first [two-case run (retained locally)](../../../EVIDENCE-AVAILABILITY.md#local-b387ad656ed2) stopped on after_return. The
[continuation (retained locally)](../../../EVIDENCE-AVAILABILITY.md#local-8d1b760e0fbd) collected eight other fresh
cases, preserving failed verdicts but stopped on the checkpoint diagnostic.
The [final complete-only run (retained locally)](../../../EVIDENCE-AVAILABILITY.md#local-877b1374a390) exercised the sole
previously unrun prefix. No failed case was repaired or replayed. The current
controller's successful process exit is not an all-passing protocol verdict.

The [independent initial audit](independent-audit/actual-counterexample-001/REPORT.md)
proved that the two new after_return refs were zero-byte files, while the
complete JSON/checkpoint/receipt survived. All original objects and the earlier
input/result retention roots survived. Subsequent cases show the related gap:
the emulator's receipt could survive its archive dependency, and local recovery
trusted that receipt enough to report complete. The strict oracle separately
checked the actual provider repository and rejected those completions.

For result_checkpoint, the stored recovery receipt records exit0, no issued kill,
no successful clean-unmount marker, and the serial contains a Python exception
followed by kernel panic. Do not infer a recovery SIGKILL merely from the
collector's bounded deadline. The original cut itself has the exact barrier and
issued kill with exit-9. The diagnostic and both disk archives are retained;
there is no fabricated successful after-recovery snapshot.

## Scoped repair

The [variant preparation](durable-variant-prep/PLAN.md) preserves the original
worker, helper, guest and oracle. A small wrapper intercepts only the three
frozen successful update-ref operations: emulator head, emulator authored archive
and local completed continuation. It checks the exact normal owned loose-ref
contents, fsyncs the ref file, and fsyncs its required parent directories through
the already durable case directory before returning to the original protocol.
The provider receipt and local completion therefore follow their own durable
Git dependencies. Failure of a barrier prevents the corresponding acknowledgment.

This is deliberately a test of a concrete persistence repair. It is not a
production abstraction for packed refs, reftable, linked worktrees, concurrent
maintenance, newly created objects, macOS or physical storage loss.
[Versioned Git documentation](GIT-DURABILITY-SOURCES.md) provides additional
configuration context without pretending newer flags ran in Git2.34.1.

Twenty-two offline cases challenge exact barrier calls, command failure, scope,
layout, I/O errors and three executed barrier-omission mutants. Root verified
the original runtime stage inventory. The separate built image differs only in
its init entry and three added files; its SHA256 is
fa0ffb08cf61427fbc3fd35bf6679aac94343b49d1c2cb8abaa0b81017c033c9.

The [fresh variant results](durable-variant-results-001/RESULTS.json) pass all
eleven original strict expectations, including correct no-resend outcomes.
[Root verification](durable-variant-results-001/ROOT-VERIFICATION.json) reproduced
every strict verdict, checked exact runtime/wrapper attribution and all required
barrier paths in twenty-two serial records, and verified all twenty-two pre/post
disk archives. This closes the captured gap for these fixtures and positions.
It does not prove all crash timings or a general production durability guarantee.

## What the result changes

Completion must depend on facts already made durable within the declared failure
domain. A successful subprocess, a live reread and an unrelated JSON fsync did
not establish that condition here. Correct recovery refusal is valuable, but
does not make an earlier success report valid. Likewise, a local emulator cannot
promise its authored history merely by writing a durable receipt before the
archive is durable.

The core distinctions still earn their cost: retained input, confirmed remote
effect, accepted local result, current authoring source and pending uncertainty
are different facts. They may share objects and storage. If a publication already
has a durable accepted result root, it need not create another alias merely to
represent that same fact. A real newly selected continuation still needs its
own durable attachment. An unknown native output cannot be accepted in advance.

All sources, grants, failures, strict checks and images remain retained. The
public source bundle omits large disk/runtime bytes and points to their local
restoration records; omitted hashes do not make them publicly inspectable.
No GitHub service durability failure was tested: the provider in this experiment
is a local emulator on the same guest disk.

*Authored by an AI agent acting on joshlf's behalf.*
