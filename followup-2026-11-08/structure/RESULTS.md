# Hosted structural-prefix restart results

**Nine positive fixtures recovered after actual worker SIGKILLs; two negative
recovery runs refused before a new structural dispatch.** Ten isolated fixtures
created 32 PRs in the public synthetic repository
[`joshlf/gherrit-native-stack-experiments-2026-11-08`](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08).
The campaign ran on November 9, 2026, 04:20–04:30 UTC. All selected interruptions
followed a received acknowledgement, persisted receipt and independent readback.
They are **after-ack crashes**, not genuinely lost in-flight responses or machine
power loss.

Every planned case has a terminal, evidence-backed disposition in
[CASE-MATRIX.md](CASE-MATRIX.md) and [CASE-MATRIX.json](CASE-MATRIX.json).
[RESULTS.json](RESULTS.json) retains the controller outcomes, process IDs and
exit statuses. [FINAL-AUDIT.json](FINAL-AUDIT.json) reports **32 unique canonical
PRs, 117 receipted mutations, no audit errors and successful Git fsck**. The
executor sources remained byte-identical throughout execution.

## What actually ran

The [persisted plan](PLAN.md) uses ABC → CAB for reorder and ABC → ADBC for
insertion. Every layer owns an independent file. The worker executes unstack →
park B/C at trunk → atomic coupled head/archive push → final adjacent bases →
native registration. Insertion adds D's canonical PR creation after the atomic
push. A already targets trunk; the first member's final trunk assignment is also
an observed no-op. Neither is dispatched just to manufacture another prefix.

| Case | Acknowledged boundary selected for SIGKILL | Fresh process result |
| --- | --- | --- |
| S01 | Unstack | Resumed after effect 1; completed 7 |
| S02 | B parked | Resumed after 2; completed 7 |
| S03 | C parked | Resumed after 3; completed 7 |
| S04 | Atomic heads and archives | Resumed after 4; completed 7 |
| S05 | A's final base C | Resumed after 5; completed 7 |
| S06 | B's final base A | Resumed after 6; completed 7 |
| S07 | New native registration | Validated all 7; dispatched no further effect |
| S08 | Inserted D PR creation | Resumed after 5; completed 8 |
| S09 | Four-member registration | Validated all 8; dispatched no further effect |
| S10a | Withheld unstack receipt after the same selected crash | Refused missing dispatched-effect evidence |
| S10b | Separately journaled live B-head advance on S10 | Refused refs/head mismatch |

All ten interrupted workers exited with signal status `-9`. The controller
waited for each worker's death before starting its fresh recovery process.
Recovery read the durable manifest, custody hash, effect intents/receipts and
current hosted state. It dispatched only the remaining effect records in the
nine successful traces. Registration-only completion did not create another
group, and D's recovery did not create a replacement or duplicate PR.

## Preserved identities, work and refusal evidence

The final independent audit reread Git refs, PRs, ordered native membership and
all PRs matching each exact head. Every one of the 32 heads had exactly its
expected PR. All 30 original PR node IDs survived; all 32 PRs remained open and
unmerged. The nine completed fixtures had their expected adjacent bases, exact
new heads and new native groups.

All 30 original v1 authored archives and all 29 published v2 authored archives
matched their exact recorded objects. The stale-control archive is separate.
Each fixture retains old/new parent and tip SHAs, exact layer patches, commit
records, input refs and local Git objects. All 30 ABC old/new patch comparisons
were byte-identical, including the three proposed but unpublished S10 layers.
Each insertion's total top-tree difference was exactly its new D patch. These
checks establish topology and ownership for independent changes; they do not
make an invalid source-code-dependent reorder valid.

S10a exited before a live read or new effect because its unstack dispatch intent
had no receipt. The original receipt was then restored without changing its
bytes. S10b independently advanced B and archived that control through a leased
atomic push. Fresh recovery reported both a ref mismatch and a changed B head.
The final audit found only the original unstack executor intent on S10: neither
negative recovery dispatched another structural effect. S10 remains deliberately
unstacked and stopped with its stale head, original archives and control evidence
retained. It was not repaired or replayed into a passing fixture.

## Evidence and limits

- [Fixture manifests and process/checkpoint traces](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/raw/97b993efdda40a1cbe690d317e436e32937adb85/followup-2026-11-08/structure/evidence.tar.gz) bind canonical PRs,
  exact planned effects, custody hashes, original/new ranges and selected kills.
- [Raw intents, receipts and independent readbacks](https://github.com/intro-to-security/gherrit-stack-queue-public-experiments-2026-11-08/raw/97b993efdda40a1cbe690d317e436e32937adb85/followup-2026-11-08/structure/evidence.tar.gz) retain each request,
  response, atomic-push result and phase snapshot. REST version was `2026-03-10`;
  mutations were sequential and paced at least two seconds apart.
- [lab.py](lab.py), [run.py](run.py), [audit.py](audit.py) and
  [SOURCE-VERSION.json](SOURCE-VERSION.json) retain the scoped executor and source
  hashes. All four Python sources, including the matrix renderer, compiled in
  memory; `git fsck --full --no-reflogs` exited zero. No hosted fixture required a
  harness correction, and no mutation remained unreceipted.

This adds hosted interruption/restart evidence to the
[prior structural sequence](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/blob/ade319107e71b6eff646a1574139e2c15486fe6d/api/RESULTS.md).
Prior safe drop, fold and trunk changes remain prior evidence; this lane makes
no new interrupted-recovery claim for those operations. The
[local recovery failures](../local/RESULTS.md) remain findings about that separate
prototype, including duplicate-worker and missing-evidence weaknesses.

The executor assumes one cooperating structural publisher, fresh fixtures and
no known landing/admission work. It does not enforce exclusion across clones or
supply a provider handoff. A matching durable receipt plus current reads in these
finite traces is not a lifecycle transaction, monotonic generation or proof that
no delayed native write can occur. Approval retention, arbitrary simultaneous
writers, corrupted custody, machine power loss and genuinely unknown in-flight
outcomes are outside these positive observations. A completed marker alone grants
no mutation authority here. Production GHerrit and all settings/main branches
were untouched. Root owns integration and publication.

*Authored by an AI agent acting on joshlf's behalf.*
