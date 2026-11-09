# Held fresh-map control: local preparation only

The new scope is `exh-1109-ui-stale-debug-held-fresh-0a10ffe99c`. No hosted preparation, native request, browser action or network call ran here. Root must review the frozen source/inputs and separately grant/run the existing `prepare` action. There is no `advance` action.

`fixture.py` is a literal copy of `fixture-a-fresh-prep/fixture.py` except for exactly two namespace-prefix replacements: generation and grant validation. The source SHA256 is `769b6e0348898e142b983f17d37ef3b07aa5220bb0a110edb1b5d6b57c4c5549`. `SOURCE-DIFF.patch`, original source/helper copies and `SOURCE-INPUTS.json` preserve provenance. The helper remains the pinned existing `rootlab.py`; no historical driver was replayed or old fixture/source changed.

LOCAL-INPUTS SHA256 is `a3ca29404b291f6c9ee3ef89b67ce6c74043bcb6c07cb342973199f84e9372ed`. The local guard allowed only commands in this new bare store and rejected network/hosted process entry paths. The nine logical commits retain the same graph shape as the fresh-map fixture. Their exact bodies/OIDs, parents, tree contents, author/trailers, three source ranges, four expected trees and full A/B patch transformations checked; hooks are disabled and fsck passed. There are no native intents, prepare START or READY file.

After a separate exact root grant, `prepare` retains the original five-effect sequence:

1. Atomic creation of trunk/A/B/source-v1/A-v1/B-v1 refs.
2. Create A PR.
3. Create B PR.
4. Register those canonical A/B outputs.
5. Atomic advance of the trunk and A to T1/A2 plus creation of archive-a-v2.

The resulting seven-ref READY basis has A2, its archive and advanced trunk present **before browser load**, with B0 unchanged. This source adds no hosted hold or mutation step; root owns native UI and read-only hold-ref checks. The existing grant schema is unchanged: exact control path, action `prepare`, coordinator/repository/prefix, source/helper/input hashes. Preparation is not authorized by this note.

For the discriminator, root should pause the same actual initiation with a **fresh A2/B0 map** and make **no ref/archive/membership mutation during the hold**. Observe the same paused call/body and exact seven-ref vector before/after the hold, Resume once, then retain the actual POST/map/response/job and independent graph/range outcome. A refreshed or unidentified payload, vector drift, spontaneous resume or unknown effect fails the intended premise and freezes without retry.

Use at least a 120-second hold from the first confirmed pause observation, and at least the maximum prior observed hold if root's complete action log establishes a longer duration. The retained pause-to-Resume-intent intervals are only lower bounds (about 46.889 seconds for B and 31.530 for A); a Resume intent is not the Resume itself, and HAR start is not a physical send clock. Root must record the actual chosen interval and comparison, rather than claim matched delay from those lower bounds alone.

This tests whether the debugger hold/request age alone can explain the prior failures. Success would strengthen the stale-member-change interpretation in these fixtures; failure needs its exact outcome retained. Neither result proves an internal comparison algorithm, public compatibility or later-write arbitration. Reuse the existing oracle/abort/cleanup rules; no second confirmation, endpoint replay, automatic repair or fixture deletion is implicit.

*Authored by an AI agent acting on joshlf's behalf.*
