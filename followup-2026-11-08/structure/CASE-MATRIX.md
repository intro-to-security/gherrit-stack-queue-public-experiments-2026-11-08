# Structural-prefix dispositions

| Case | Selected prefix / negative input | Disposition | Evidence |
| --- | --- | --- | --- |
| S01 | unstack | Recovered 1 → 7 | [kill](fixtures/s01/process-initial.json), [fresh recovery](fixtures/s01/completion-recovery.json) |
| S02 | park-B | Recovered 2 → 7 | [kill](fixtures/s02/process-initial.json), [fresh recovery](fixtures/s02/completion-recovery.json) |
| S03 | park-C | Recovered 3 → 7 | [kill](fixtures/s03/process-initial.json), [fresh recovery](fixtures/s03/completion-recovery.json) |
| S04 | heads-archives | Recovered 4 → 7 | [kill](fixtures/s04/process-initial.json), [fresh recovery](fixtures/s04/completion-recovery.json) |
| S05 | final-A | Recovered 5 → 7 | [kill](fixtures/s05/process-initial.json), [fresh recovery](fixtures/s05/completion-recovery.json) |
| S06 | final-B | Recovered 6 → 7 | [kill](fixtures/s06/process-initial.json), [fresh recovery](fixtures/s06/completion-recovery.json) |
| S07 | register | Recovered 7 → 7 | [kill](fixtures/s07/process-initial.json), [fresh recovery](fixtures/s07/completion-recovery.json) |
| S08 | create-D | Recovered 5 → 8 | [kill](fixtures/s08/process-initial.json), [fresh recovery](fixtures/s08/completion-recovery.json) |
| S09 | register | Recovered 8 → 8 | [kill](fixtures/s09/process-initial.json), [fresh recovery](fixtures/s09/completion-recovery.json) |
| S10a | withheld acknowledged receipt | Refused; no new executor dispatch | [S10a refusal](fixtures/s10/refusal-missing-evidence.json) |
| S10b | independently advanced live B head | Refused; no new executor dispatch | [S10b refusal](fixtures/s10/refusal-stale-live.json) |

Every selected crash exited by SIGKILL (`-9`). Each recovery used a new PID.
The receipt/readback/checkpoint had been persisted before the selected kill.
These are after-ack crashes, not lost in-flight responses or machine power loss.

*Authored by an AI agent acting on joshlf's behalf.*
