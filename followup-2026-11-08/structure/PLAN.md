# Hosted structural-prefix restart plan

This lane tests a narrow cooperative structural executor in the existing public
synthetic repository `joshlf/gherrit-native-stack-experiments-2026-11-08`. Its only
hosted write authority is fresh `exp/fu2/structure/**` heads, archives, PRs and
native groups of those PRs. It changes no repository policy, main branch, queue,
prior experiment resources, production GHerrit or published reports.

Ten isolated fixtures use three initial PRs each; two insertion fixtures add one
PR each, for a bound of **32 new PRs**. Every layer changes its own file. Reorder
therefore changes logical order without fabricating a source-code dependency.
Original and proposed exact objects, per-layer patches and archives survive.

The prototype persists the entire intended effect sequence and canonical review
IDs before executing it. Each effect has a durable dispatch intent and a raw
receipt. It unpacks the native group, observes release, parks each affected open
PR at the fixture trunk, atomically updates heads and new immutable archive tags,
restores adjacent bases and registers a new group. A base already at its target
is an observed no-op, not a hosted write. The executor checks lifecycle, node IDs,
heads, bases, membership and all original/new archive refs against the exact
journal prefix before each subsequent effect.

The controller starts a real worker process, waits for a durable marker written
after the selected hosted acknowledgement and independent readback, sends
SIGKILL, waits for process death, then starts a fresh recovery process. Recovery
loads only the on-disk manifest, receipts and live hosted state. It validates the
completed prefix and dispatches only remaining effects. These are **after-ack
crashes**, not unknown in-flight transport losses or machine power failures.

| ID | Topology / selected interruption boundary | Expected discriminator |
| --- | --- | --- |
| S01 | ABC → CAB; unstack acknowledged | No second unstack; resume parking onward |
| S02 | ABC → CAB; B parked at trunk | No repeat release/B parking |
| S03 | ABC → CAB; C parked at trunk | No head movement before all parking is observed |
| S04 | ABC → CAB; atomic heads/archive push acknowledged | Both generations retained; no repeated push |
| S05 | ABC → CAB; A final base C acknowledged | Resume B base and registration only |
| S06 | ABC → CAB; B final base A acknowledged | Registration only remains |
| S07 | ABC → CAB; new native registration acknowledged | Fresh process validates completion without another registration |
| S08 | ABC → ADBC; D creation acknowledged | Exactly one new canonical D PR; restore remaining bases/register |
| S09 | ABC → ADBC; registration acknowledged | Completion validates all four identities and archives |
| S10a | ABC → CAB; crash after unstack, withhold that receipt | Missing evidence refuses before mutation; restore original bytes afterwards |
| S10b | Same isolated negative fixture, inject a separately journaled live B-head advance | Stale live state refuses before mutation; stop fixture rather than replay |

All seven material reorder prefixes have separate fixtures. A's initial parking
and C's final trunk base are checked no-ops; their before/after boundaries add no
new hosted effect and are covered by the adjacent prefix readbacks. Insertion
adds the distinct canonical-PR-creation boundary. It shares the already exercised
release/park/ref/base effect types, and tests final four-member registration.

Writes are sequential and paced at least two seconds apart. Polling is bounded.
A network exception or unreceipted dispatch stops that fixture with its ambiguity
retained; independent fixtures may continue. No absent state alone authorizes a
retry. A failed precondition is a finding, not permission to adjust another
writer's resources. Current positive state plus a matching durable receipt is
used only inside the declared sole-writer experiment. It is not a provider fence,
a monotonic generation, a lifecycle transaction or proof of quiescence.

Machine results enumerate every ID, process exit status, receipt/journal paths,
readback and final disposition. `RESULTS.md` will distinguish prototype behavior,
observed native effects, oracle limitations and unavailable provider guarantees.
Root alone owns final integration and publication.

*Authored by an AI agent acting on joshlf's behalf.*
