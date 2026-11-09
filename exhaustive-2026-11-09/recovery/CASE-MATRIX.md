# Local case dispositions

The final run is `runs/1794232632320218000`. All 188 assertions passed, including
expected-negative controls. A passing probe can establish a candidate failure;
the outcome column states that distinction. These are local experiments, not
production acceptance.

| ID | Disposition | Outcome |
| --- | --- | --- |
| R01 | Performed, negative control exposed | Ordinary import silently loses confirmed x=1; strict overlap refuses; drift acceptance requires review. |
| R02 | Performed with conflict and negative control | Independent remote edit survives reviewed restoration; same-line edit conflicts; explicit remote acceptance changes intent; blind whole-tree restoration loses legitimate work. |
| R03 | Performed, v1 candidate rejected | A/B/A archives remain distinct; no-op creates no archive; later source remains pending. Reset-to-old-value defeats first restoration formula; revised path guard catches it and explicit resolution preserves x=0. |
| R04 | Performed after retained correction | Two-layer import preserves independently specified tree, layer paths and raw message bytes. First run's pretty-format newline bug remains retained. |
| R05 | Performed, observation bound exposed | Incoherent observations refuse; coherent stale read misses drift; current read detects it. Actual Git lease succeeds after ABA. |
| R06 | Bounded model performed | 97 states / 586 transitions, depth <=7; policy invariants hold within stated dimensions. Known-bad ordinary/blind-restoration witnesses retained. |
| R07 | Local witness and refusal performed | Actual ancestry establishes structural hazard premise; candidate excludes reorder/landing overlap. No delayed provider effect or canonical terminalization was simulated into an observation. |
| R08 | Performed | Two simultaneous processes and stale direct invocation send exactly one provider request. One same-host local owner only. |
| R09 | Performed with explicit unknowns | Ten real SIGKILL prefixes; repeated recovery completes with exact attributable receipt or blocks without resend. No power-loss inference. |
| R10 | Performed | Fifteen damaged-evidence variants refuse; ordinary later authoring remains valid through immutable retained completion evidence. |
| R11 | Injected partial outcome performed | Changed head plus missing archive remains indeterminate; matching head cannot complete or authorize retry. Not Git atomicity evidence. |
| R12 | Performed | Fresh local successor acceptance retains old pending input and does not settle its request or grant strict overlapping write authority. |
| R13 | Local rehearsal performed | Complete custody transfer invalidates old token; pending operation survives without resend. Actual destination/head/archive checks and missing/old-writer controls refuse; valid pending enrollment grants no mutation authority. |
| R14 | Local rehearsal performed | Pending rollback refuses; settled export bundle verifies and retains evidence while prior native token is invalidated. No production legacy-writer exclusion claim. |
| R15 | Capability/model performed; guest root-owned | Read-only runtime metadata and assumed persistence-prefix outcomes retained. Actual guest cuts are separately executed by root under its grant; whole-host/device power loss remains unperformed here. |
| R16 | Performed, unsafe controls exposed | Temporary identity/result/owner validation bypasses falsely complete; independent identity/ref/request evidence detects all three. |
| R17 | Explicit-only control performed | Every changed overlapping observation requires an exact reviewed decision; tested explicit result preserves reset plus legitimate edit. Human comprehension/cost unmeasured. |
| R18 | Scope policy performed | Strict B refuses; expressly accepted weaker same-order B can proceed; disjoint F-only admits; broad source/shared checkpoint/managed trunk/unknown old scope refuse. Scope completeness is supplied, not proved. |

*Authored by an AI agent acting on joshlf's behalf.*
