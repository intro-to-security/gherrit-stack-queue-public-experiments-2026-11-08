# Prepared human tasks and evidence limits

No independent participant has yet completed these tasks. Tool-driven or agent
walkthroughs are not human usability evidence. Only the user may be invited here;
no third-party recruitment or messages are authorized. These tasks do not require
production GHerrit or changes to the user's real Git work.

## H01 author preparation and continuation

Use a retained local fixture with published A–B, pending A′ introducing a field,
pending B′ consuming it, and old A landed. Present the exact captured source T,
fresh continuation F–B′, later source U and dirty/staged/untracked work summary.
Ask a participant to identify what is included, what remains unsubmitted, where
the dirty work lives, and which branch they would select next. Record their
answers, misunderstandings and requested actions; do not infer preference from
task success. Compare explicit preview versus the hook-triggered sequence using
the same retained inputs. The objective oracle is local per-layer/working-tree
evidence, not the wording the agent hoped would be clear.

## H02 reviewer history and changed parents

Use the retained public synthetic
[history PR10](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/10)
and [owned history comment](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/10#issuecomment-6728278369).
Ask a participant to find the earlier exact submitted patch, identify the file
changed by that patch, and distinguish it from unrelated parent movement in the
tip-to-tip comparison. Ask whether the entrypoint was discoverable and what they
expected “changes since review” to mean. Record observed success and confusion
separately from subjective preference. Do not delete/edit the old fixture or
manufacture a long discussion merely to claim human testing.

For a long-discussion study, prepare a fresh explicitly synthetic fixture and
compare native timeline discovery with a direct stable artifact link; that test
requires an actual participant and interactive browser access. A new hosted
history site is not required to test whether the current presentation is clear.

Neither task settles acceptable interaction cost, automation or operational
priorities on its own. If no participant is available, retain unavailable status
and these reproducible tasks rather than filling the study with agent answers.

*Authored by an AI agent acting on joshlf's behalf.*
