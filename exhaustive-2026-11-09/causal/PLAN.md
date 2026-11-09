# Causal native-write probes

This lane tests whether a captured suffix transition can establish a write after
a direct merge's terminal response. It cannot establish a future-write fence
from a quiet observation window. Only new resources in
`joshlf/gherrit-native-stack-experiments-2026-11-08` whose branch names begin
`exh-1109-causal-` are eligible. Every fixture has an independent synthetic trunk.
No settings, workflows, default-branch writes, queues, website actions, historical
drivers, historical dispatches, or external publication are part of this lane.

## Proposed bounded sequence

1. `force-control`: two ordinary PRs, with no native group or merge operation.
   Publish a unique sibling head with an exact lease on one PR. Capture the
   `HeadRefForcePushedEvent` before/after/actor/ref fields, plus the Git transition
   and PR head projection. This establishes whether the instrumentation exposes
   an intentionally caused force-push and measures event visibility delay. Do
   not count absent optional fields as passing evidence.
2. `post-squash-1`: native A–B, direct squash of A, one surviving suffix PR B.
   Receive terminal `merged`, then create a fresh random marker commit, record
   its object and creation interval, and publish it to B using an exact lease
   against a fresh Git ref observation. Keep the complete dispatch receipt.
3. `post-rebase-3`: native A–B–C–D, direct rebase of A, three surviving suffix
   PRs. Use the same post-terminal marker procedure on D. This changes both the
   direct method and the available suffix-work interval; a later same-method
   comparison will be needed if those dimensions produce different outcomes.
4. `post-merge-1`: native A–B, direct merge of A, one surviving suffix PR B.
   This covers the third documented direct method with the same causal oracle.

The root may grant that first batch as written or select a subset. After review
of its evidence, a second explicit grant may cover `post-squash-3` (isolate
suffix length), `early-squash-3` (publish after admission but before the first
terminal observation), and an ordinary post-merge `gh stack sync` control after
the command's effects have been audited. The early trial must preserve the
actual order observed; publishing before the first terminal poll does not prove
that the server was still in flight. No artificial unobservable timing claim is
an acceptance condition.

## Evidence and claim boundaries

- Preserve each HTTP/Git input, exact target identity, fresh pre-state, timestamp
  and monotonic interval before dispatch. Never retry a write after a missing
  acknowledgement. Freeze unknown or ambiguous outcomes and reconcile read-only.
- Separate async admission, terminal operation response, actual Git ref
  transition, PR projection, timeline event visibility and attribution. These
  are separate observations, not one snapshot.
- A marker commit created after the terminal receipt cannot be an old head
  merely returned by a stale read. A captured force-push event whose
  `beforeCommit` is that marker and `afterCommit` is another head establishes the
  corresponding actual transition after marker publication, subject to actor
  attribution and sole-writer controls. Event-object `createdAt` is not the exact
  mutation time. There is no assumed event-to-merge-UUID correlation.
- A missing actor, null commit or missing force-push event limits attribution.
  Final ref drift without that evidence remains a detected change requiring
  reconstruction. PR/ref disagreement alone can be projection lag.
- For each successful marker push, sample Git refs, PR projections and timeline
  events at bounded intervals through 60 seconds. Extend once to 120 seconds
  only for observed unsettled evidence. Preserve raw sanitized outputs. Finite
  silence is an observed quiet window, never quiescence or a provider guarantee.
- Pause between fixtures and writes. Stop on unexpected scope, rate-limit or
  conflict evidence. Leave resources intact for root reconciliation; no cleanup
  write is implicit.

## Harness outline and effect audit

`harness.py` will be a new driver rooted only in this directory. It will use
`gh api` for JSON REST/GraphQL and a private bare Git repository for synthetic
objects. Its own command entry point will default to local validation and require
an explicit granted case identifier to run hosted writes. Git hooks will be
disabled through the private repository's `core.hooksPath` and each Git command's
`-c core.hooksPath=...` setting.

The old `api/lab.py` was inspected as text. Importing it creates its historical
evidence directory; its `init`, `fixture`, `push` and `merge` functions can mutate
historical resources. Its write cache also treats a prior receipt as an implicit
continuation. This lane will not import it. Only the general recorded-request
pattern and exact Git lease approach are reused in newly scoped code.

The new harness will have separate functions for: an append-only intent/receipt
pair; constrained HTTP requests; exact-lease Git pushes; local object creation;
fixture resource creation; independent ref/PR/event observations; merge receipt
polling; and marker publication. Read calls use unique labels. Existing write
labels are never resent, even if a receipt exists. A partial fixture remains a
recorded case with its existing identities. This makes re-entry a reconciliation
decision, rather than a repeated mutation.

Local checks will validate namespace guards, refusal to repeat a dispatch,
missing-response classification, marker creation order, lease arguments and
case/result serialization without reaching a network. Hosted execution remains
blocked on root's explicit batch grant.

*Authored by an AI agent acting on joshlf's behalf.*
