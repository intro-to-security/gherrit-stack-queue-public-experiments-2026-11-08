# Range-diff isolates useful revision views, with limits

Yes: comparing the two exact authored ranges can remove unrelated ancestry drift from the revision view. It does not generally isolate authored intent or prove that two revisions are equivalent. These local controls show both the useful case and concrete failures of that stronger interpretation.

The command shape is `git range-diff old_base..old_tip new_base..new_tip`. The bases remain explicit inputs. Git documents commit pairing as a cost-based comparison of patches, author information, and messages; its output is intended for people and is not a stable machine interface. The creation factor adjusts pairing rather than establishing identity. [Official range-diff manual](https://git-scm.com/docs/git-range-diff).

One fresh bare repository on Git 2.54.0 (Apple Git-157) contains 14 synthetic commits. The harness ran 101 commands, then one independent batch read verified all 29 unique commit/blob objects against their object hashes and expected bytes. Every synthetic commit has the established user name/email and Agent-authored-by trailer. Git fsck passed. There are no remotes or hosted effects. The source, exact command/stdin/stdout/stderr records, base/tip identities, patches and object readback are retained here.

> **Public evidence subset.** “Retained here” refers to the full local control
> corpus. This public subset includes `COMMANDS.json`, result/verification JSON,
> the control source, and selected comparison and patch outputs. The complete
> command stdin/stdout/stderr corpus, raw binary readback and Git store remain
> local. Those omitted bytes are not publicly inspectable from this package;
> the selected records alone do not reproduce the full object-readback check.

| Control | Observed range-diff | What it establishes |
| --- | --- | --- |
| A: Same alpha edit, unrelated base-file drift | `=` at default and factor 100; exact patches identical | The useful case: unrelated ancestry change disappears from this revision view. |
| B: Same `value = 0` to `value = 1` edit, adjacent base context changes | Default shows removed/added commits. Factor 100 pairs `!` and displays `context = old` to `context = new`; the value edit remains unchanged. | Base context still enters the patch comparison. A displayed revision difference can be ancestry context rather than a change to the fixture's authored edit. |
| C: Different binary replacement bytes | `=` at default and factor 100 | `=` does not establish equal binary content. |
| D: Same script text, executable bit present only in old revision | `!` and a `100644 => 100755` mode difference | This mode change is visible. Binary and mode behavior must not be conflated. |
| E: Same two disjoint edits, reversed commit order and unrelated base drift | Old commit 2 pairs with new 1; old 1 with new 2; both `=` | Series matching helps a reviewer follow reorderings rather than compare commit ordinals. This two-commit case does not validate ambiguous matching in general. |

Control C is an actual content counterexample. Old and new binary result blobs are respectively `5a62bfb9a7a28166d474c1c8af3e3a19e59e262d` and `712c2ecd69edb961f77f71c43519d7d77cbb4629`. Independent Git readback verified the distinct 15-byte values `007265766973696f6e2d6f6e65ff0a` and `007265766973696f6e2d74776ffe0a`. Both range-diff outputs still show `=`. The literal diff of the full-index patches notices only the changed target blob ID because both ordinary patches contain the same binary placeholder. Separately retained `--binary` patches contain the encoded payloads. Equality of that abbreviated human view would have missed the revision.

For text, a literal diff of the exact patches is also useful: A has no diff; B includes context and blob-index changes. It lacks range-diff's commit pairing and can include presentation details that are not authored changes. Keeping exact snapshot/blob identities and the original per-version patches makes either view auditable. Neither view supplies a general operation for inferring the author's semantic intent from changed bases.

The frozen PR10 history binding and root's `REQUEST-RESULT.json` were read without mutation. Their exact old/new ranges match. Root's retained default matcher output shows removal/addition for the tiny revision; its factor-100 output pairs the authored value 1-to-2 change without trunk drift. These controls qualify that successful example; they do not replace it or alter the old fixture. No merge, rename, textconv, ambiguous series, arbitrary language semantics, or other Git-version coverage is claimed.

*Authored by an AI agent acting on joshlf's behalf.*
