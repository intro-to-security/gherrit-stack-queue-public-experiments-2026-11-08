# Local follow-up experiment plan

This lane uses disposable repositories and evidence only under this directory.
It makes no network calls and changes no production files or configuration. The
comparison target is the retained real-Git prototype, not production GHerrit.
The current question classification is
`outputs/github-native-stack-design-2026-11-08/post-experiment-refinement/OPEN-QUESTIONS-BY-RESOLUTION.md`.

Every case below has a terminal disposition in `RESULTS.json`. A negative control
passes when it exposes the stated weakness; a prototype invariant violation is
reported as a model failure, never relabeled as a successful implementation.
Plans are recorded before mutation. Source, command/response logs, object refs,
exact input/output snapshots and failed runs are retained. All Git subprocesses
use disabled system/global configuration and fixture-local hooks.

## Matrix

| ID | Discriminator and oracle | Bound / prior coverage |
| --- | --- | --- |
| L01 | Rerun the unmodified prior local prototype under this lane; check its full assertion ledger, SIGKILL prefixes, moving source, dirty/staged/untracked bytes, F-before-B and changed-parent history controls. | One run, 122 prior assertions; exact source copied and hashed. |
| L02 | Repeated A/B native-style rewrites with independent local/hosted edits and changing parents; compare every output tree, per-layer path ownership and message bytes with independently constructed expected trees. | Six rounds, three deterministic seeds, at most two layers each. |
| L03 | Differential wrong authored baseline and wrong accepted-local-as-hosted baseline; require conflict or loss of pending content while the incorporated-hosted baseline passes. | Reuse L01 controls plus L02 repeated oracle. |
| L04 | No-op reimport: same ranges keep exact tree and change patch; characterize commit identity separately from publisher no-write decisions. | Three inputs from L02. |
| L05 | Multi-commit local and hosted ranges: compare integrated net tree, local tip message and layer ownership; record flattening as prototype scope. | Two commits each, two layers. |
| L06 | Rename plus independent content edits; executable-bit mode change; deletion plus independent hosted edit; binary edit plus independent hosted edit. Compare exact modes/blob bytes and per-layer ownership. | Four cases, blobs at most 256 bytes. |
| L07 | Rename/rename, modify/delete, same binary changed on both sides: require explicit conflict, pinned input and conflict-tree evidence. | Three conflicts; no automatic resolution. |
| L08 | Local revert and explicit reset after an import: exact expected net trees and retained original objects; no inferred author intent. | Two cases; ordinary real revert already in L01. |
| L09 | F-before-B executable dependency and layer ownership; upper-only arrangement must fail dependency oracle. | Reuse L01 and prior hosted-integration source/results; no hosted rerun. |
| L10 | Dirty/staged/untracked and source moving after capture: continuation acceptance leaves exact source/index/workfile bytes and old checkpoint intact; colliding fresh ref refuses. | Reuse L01 real fixture. |
| L11 | Kill each original durable operation prefix and recover twice; no duplicate emulator request, unknown stays blocked, exact continuation checkpoint. | Eight SIGKILL prefixes from L01 plus new duplicate recovery reads. |
| L12 | Missing binding/checkpoint/pending manifest/operation record and custody transfer: admission must withhold authority; test worker bypass separately. | Four deletions and one complete transfer; no external provider. |
| L13 | Ref/checkpoint gaps: occupied ref with wrong target, incompatible checkpoint, deleted ref after completion, deleted checkpoint after completion. Require explicit refusal or identify missing validation. | Four cases copied from L01 fixtures. |
| L14 | Lost operation evidence after applied emulator effect: never reinterpret missing evidence as known-not-dispatched. | One deliberately damaged fixture, isolated provider store. |
| L15 | Real process SIGKILL during journal replacement: old or new complete JSON at each temp-write/flush/fsync/rename/directory-fsync prefix. Preserve orphan temp state. | Seven prefixes, 64 KiB payload; process durability only. |
| L16 | Duplicate concurrent worker invocation from planned state: characterize whether one durable owner fences dispatch; count emulator requests and retained receipts independently. | Two processes, barrier before dispatch, two runs. |
| L17 | Concurrent local Git head+archive pushes with divergent targets and explicit leases: one coupled winner; loser changes neither ref. | Two writers, fresh bare sink. |
| L18 | Same desired target and absence leases: determine whether both calls report success and equal ref suppresses ownership checks. | Two writers, fresh bare sink. |
| L19 | Atomic rejection control: stale head lease prevents otherwise valid archive creation. | One push, two refs. |
| L20 | Equal-ref guard control: stale lease on an unchanged guard does not fence another updated ref. Compare actual packet trace and sink readback. | One push, two refs. |
| L21 | ABA head sequence: old→intervening→old then old-expected push succeeds; record that value CAS has no generation evidence. | Three local sink updates and one push. |
| L22 | Historic changed-parent comparison: exact range patches exclude parent drift; tip-to-tip diff includes it; range-diff matches unchanged patch and detects a changed patch. | Three tiny commits; prior same-patch evidence reused. |
| L23 | Outer push dry-run versus hook-issued inner push, destination mismatch and unrelated/deletion outer refspec. Hook inputs and both sink ref maps are independent oracles. | Reuse prior dry-run fixture; three fresh local cases. |
| L24 | Explicit publishing prototype dry-run and exact destination: no dispatch on dry-run; unrelated source ref cannot broaden chosen destination. | Two local commands; product/usability claim excluded. |
| L25 | Pinned official gh-stack v0.3.0 binary hash/help/version, parser boundaries and local adapter validator (canonical same-repository URLs, order/base/lifecycle, explicit trunk, no --open). | No network or install; 12 local validation inputs. |
| L26 | Pinned CLI local-only cost and source effect comparison: help/validation subprocess time plus retained link/submit/push source. Compare narrow link with broad submit/archive guarantees. | Five help samples; prior hosted effect tests reused. |
| L27 | Real machine power loss, production importer/mapping/signing, independent human author/reviewer usability, provider semantics and in-flight network loss. | Unavailable in this lane; exact cause stated, not simulated as established. |

## Execution bounds and evidence

No Rust compilation, network access, service installation or global configuration
changes. New object count is bounded to hundreds, concurrency to two processes,
per-child readiness waits to 15 seconds and all payloads to 64 KiB. Existing
prototype defects stay in the preserved original source; any harness correction
is separately retained with its failed run. The follow-up extension is an
experiment driver, not a proposed production migration.

*Authored by an AI agent acting on joshlf's behalf.*

## Additional discriminators after observed recovery failures

These follow directly from L13–L16 and are planned before dispatch:

| ID | Discriminator and oracle | Bound |
| --- | --- | --- |
| L28 | Hold two real processes after both read `planned`; let the first finish, then resume the stale second. Count requests in a serialized emulator store to remove lost-update ambiguity. | Two children, one ordered run; deliberately violates cooperative one-writer precondition. |
| L29 | A pending manifest names operation X but its complete record names Y. Check whether custody admission validates record identity or merely completion. | One damaged local copy; no worker dispatch. |
| L30 | Inject failure at file fsync and directory fsync during atomic JSON replacement. Check exception plus actual visible old/new file; a post-rename failure must remain distinguishable from no effect. | Two calls, no machine power loss. |
