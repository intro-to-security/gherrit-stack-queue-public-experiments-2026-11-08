# Compare the submitted patches as well as their snapshots

A range-diff is a useful additional reviewer view. Compare each submission's
own historical base/tip range rather than the two tips. On the frozen PR10
fixture, this omits history-trunk-drift.txt and shows the authored value in
history-change.txt changing from1 to2. The exact patches and their immutable
range identities remain the source of truth.

The retained command is:

```text
git range-diff old_base..old_tip new_base..new_tip
```

[Git's manual](https://git-scm.com/docs/git-range-diff) describes heuristic
pairing of patches, messages and authors, and human-readable output whose
format can change. It is not a content-equivalence or machine-state protocol.

## Exact PR10 result

The frozen v1 range is
ed86001d0772bad37723d34c42172793a1065def..577c03e83eee2c544e685bcf2d7158e371d8ec85.
The frozen v2 range is
378b07ca06b99dc523d4c42b39edb0a336b6bf39..bbdc65868b6b9afb14908b888186e73382266b42.
[The request/result record](REQUEST-RESULT.json) and exact outputs retain these
inputs. No old fixture or PR comment was changed.

Default matching represented these tiny revisions as a removed and an added
commit. [Factor100](range-diff-factor-100.txt) paired them and displayed both the
message change and the authored value edit. Factor1000 produced the same paired
view. A [literal diff of the exact patches](literal-diff-of-patches.diff) likewise
excluded the unrelated file but included changed blob-index text. Changing a
matching threshold is not proof that the matched commits have one identity.

GHerrit already binds a logical change to its authored submissions. It can use
that identity to select the two corresponding ranges rather than ask a whole
series matcher to discover the logical change. A renderer still needs a policy
for multi-commit ranges, metadata, split/fold/reorder and ambiguous matching.
It must not infer acceptance or synchronization state from the display.

## Controls and limits

The [five actual local controls](controls/RESULTS.md) expose both the benefit and
the limits. Unrelated-file ancestry drift disappeared; reordered disjoint
commits were paired across positions. An unchanged authored text edit nevertheless
showed adjacent base-context drift, and default matching unpaired it.

Most decisively, two different verified binary payloads both displayed equals.
The raw exact blobs differed, as [root's independent readback](controls/ROOT-BINARY-VERIFICATION.json)
confirmed. Executable-mode changes did appear in the separate control. Neither
range-diff equals nor a clean-looking abbreviated patch is an equality test for
all file content.

A prospective GHerrit history view should therefore:

- Keep links to each exact authored patch.
- Offer changes between submissions as a derived comparison.
- Use recorded logical identity and explicit ranges when selecting versions.
- Check exact tree entries/blobs separately so changed binary files and modes
  receive truthful indicators even when the text view omits their changes.
- Keep context noise and matching uncertainty distinguishable from authored edits.
- Bound generated comment size and retain history when a view cannot be rendered.

The comparison could be included as a code block in the existing GHerrit-owned
history comment or as a linked generated artifact. Those choices reuse the
same confirmed submission history; they do not require a second canonical
history store. Comment size, discovery, update recovery and any hosting cost
still need evaluation. No production renderer or GitHub-native range-diff URL
has been established by this experiment.

The user found the intended v1 history link, supplied the drift filename and
proposed this comparison. That establishes actual interest and limited navigation
evidence. It does not establish an ease judgment or general reviewer
comprehension. Root subsequently explained the file roles, so a later walkthrough
of this same fixture would be informed.

*Authored by an AI agent acting on joshlf's behalf.*
