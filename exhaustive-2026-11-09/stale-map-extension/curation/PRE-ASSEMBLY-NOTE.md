# Four-case curation preparation

The extension logic is ready; no four-case selection has been assembled or frozen. It waits for the safe held-outcome manifest, the updated four-case master report, and the exact retained three-case master history path. The coordinator must supply the held manifest's actual base explicitly (`campaign` or `manifest-directory`); the script does not infer it.

`assemble.py` reuses the prior 933 explicit paths, permits a new master version only with an exact old-byte history, verifies unchanged prior evidence and each incoming safe-manifest identity, and adds only the new owned held-fixture/UI/monitor/grant/outcome records. It excludes the live caffeinate-session operational record and all forbidden trees/artifacts. `scan.py` reuses the reviewed structural/link/literal checks and will scan only that assembled list. Neither source invokes Git, a browser, network, staging, publication or an old driver.

After input review, run assemble.py with the three explicit arguments, then scan.py. Final counts/digests, encoded/header classifications, historical qualifications and metadata overhead remain pending those completed inputs. Source target is below 4 MiB, each file below 1 MiB; needed records will not be silently removed to reduce metadata overhead.

*Authored by an AI agent acting on joshlf's behalf.*
