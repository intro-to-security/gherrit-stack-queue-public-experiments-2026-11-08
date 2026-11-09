# Browser history-link walkthrough

After the user said they had repaired browser access, CUA's browser host still
reported unavailable, but the documented native Chrome surface became usable.
The agent used the already open blank tab to visit public synthetic PR10. This
profile was logged out of GitHub; no authentication was required for these reads.

Observed in the actual rendered/accessibility page:

- The conversation contains a heading “GHerrit submission history (prototype)”
  with v1/v2 historical base, tip and “Exact authored patch” links. It explicitly
  distinguishes generated history from human-owned PR prose and warns that
  tip-to-tip comparison includes parent drift.
- Clicking v1's exact link opened the comparison from
  ed86001d0772bad37723d34c42172793a1065def to
  577c03e83eee2c544e685bcf2d7158e371d8ec85. GitHub displayed one changed file,
  history-change.txt, with the added line “authored value = 1”.
- Returning to the PR and clicking the labeled tip-to-tip link opened
  577c03e83eee2c544e685bcf2d7158e371d8ec85 to
  bbdc65868b6b9afb14908b888186e73382266b42. GitHub displayed two changed files:
  history-change.txt changing value1 to2, and history-trunk-drift.txt adding
  “unrelated parent progress”. The page describes this as a direct two-commit
  comparison, rather than the default three-dot comparison.

An immediate Back observation briefly combined the new URL with the old page
tree. A subsequent full accessibility read showed the correct conversation
before another link was selected. This was treated as navigation in progress,
not as a GitHub diff defect or a stable snapshot.

The agent had already read the fixture reports and knew the expected files.
This is an informed agent browser feasibility check, not a naive human reviewer
study, a long-discussion discoverability measurement or evidence of user
preference. The user has not answered the separate reviewer task. No comment,
PR, ref, setting or credential changed. Unrelated private new-tab data was not
copied into the saved/public evidence. The CUA history part ended with its
observed successful-link summary.

*Authored by an AI agent acting on joshlf's behalf.*
