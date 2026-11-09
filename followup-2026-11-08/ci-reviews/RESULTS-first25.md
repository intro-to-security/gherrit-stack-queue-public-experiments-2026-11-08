# Follow-up CI, review, signature and rule experiments

These are bounded live observations in the public synthetic repository `joshlf/gherrit-native-stack-experiments-2026-11-08`, made on November 8, 2026 local time (November 9 UTC). They establish the retained traces, not a universal rollout, a provider completion fence or future API guarantees. No production repository, prior fixture ref, main workflow or repository-wide setting was changed by this lane. Root owns temporary Actions settings and website operations.

`PLAN.md` records the pre-dispatch hypotheses and discriminators. `matrix.json` gives every planned case its disposition and exact evidence paths/hashes. `state.json` binds refs, PRs, stacks and async receipts; `control/` retains write intents; `evidence/commands.jsonl` points to sanitized requests, responses, errors and independent readbacks. `lab.py`, `prepare-ui.py` and `compare.py` preserve source. Existing controls were reused explicitly rather than repeated.

## First required checks: event, SHA and producer all matter

The earlier controls remain evidence for opened-before-membership (#5/#6), explicit `stacked` adoption (#11/#12), registered synchronize (#6), and a successful manual branch `workflow_dispatch` that did not repair the PR gate (#6). Their original artifacts and snapshots are referenced case by case in the matrix.

The new [#97/#98](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/98), native stack #101, required `fu2-status` on the exact trunk, with admins enforced and no other gate. A synthetic external commit status posted successfully to each raw source head moved both PR gates from BLOCKED to CLEAN, without changing either head. This was a status-producer control, not an assertion that software had passed a real test. A failing status with the same context posted to upper candidate `ad1c82f7de0e0d91679d58803804c168d92a973e` then made upper BLOCKED despite successful source-head status. Candidate success restored CLEAN. Candidate and source results are distinct bindings.

Restricting that same required context to the observed GitHub Actions App ID 15368 made both gates BLOCKED while the successful manual statuses remained. Restoring `app_id=-1` returned both to CLEAN. A context name and SHA do not establish satisfaction when the rule also binds a producer.

A real Actions alternative succeeded in fresh [#124/#125](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/125), native stack #126. The fixture's `fu2-push` workflow listened only to pushes under `exp/fu2/ci/push/*`; the real lower/upper runs [42556760345](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42556760345) and [42556760260](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42556760260) succeeded on their raw heads. Both required native PR gates became CLEAN with those unchanged heads. The retained push payload had no PR or stack data. This establishes the tested eligible push-event route; it does not generalize the rejected manual-dispatch route into an equivalent check producer.

Two own-ref `pull_request_target` variants (#99/#100 and #115/#116) produced no target run in the finite samples, although other PR-event workflows ran. One used a new workflow path; one replaced the already known `observe.yml` path on its own branches. Main had no target trigger. The [Actions event reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request_target) describes execution in the default-branch context. The initial failures therefore retained a missing prerequisite rather than establishing unsupported behavior.

Root then supplied that prerequisite in main commit `c3b2eb62a7fc45e5bdf949720ac4a6bce473c0ac`: one read-only, exact-fixture `pull_request_target` workflow with explicit `opened,synchronize,stacked` and trunk filter. Fresh [#151/#152](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/152), stack #153, separated first-open from registration. The lower received its target check on `opened`; the upper did not. Registration scheduled upper [42560765784](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42560765784) with action `stacked`; it succeeded, and the upper became CLEAN without a head change. This establishes a second tested Actions adoption path after supplying the default-branch source, with the same explicit-activity-type qualification as ordinary PR Actions.

The target run's environment reported `GITHUB_SHA=c3b2eb62…` and `GITHUB_REF=refs/heads/main`, while its explicit read-only checkout used current PR merge object `7b1ddd40355719462600bbbc0d7fbd74f331b9c4`. The run API's `head_sha` was upper source `d43e812e…`; raw event, actual checkout, check association and PR gate were retained separately. A target workflow must choose what it actually tests; default context is not candidate checkout. Root removed the temporary main file after collection; this lane independently read back 404.

## Multi-commit signing

Every native request used its captured selected head, `merge_method=squash`, `merge_action=default`, and `bypass_rules=false`. Required-signature fixtures enforced admins and had no check or review requirement.

| Selected lower group | PRs / stack | Terminal receipt and readback |
| --- | --- | --- |
| Two independently verified source commits | #103/#104 / #105 | Lower merged at `ee637f552984f1d86b2aa40ee413262b6818010d`; unsigned upper was replaced with verified `3b308411c5ff59cc5d0e1e00d2d83b520589b3fa`. |
| Two unsigned source commits | #106/#107 / #108 | Failed: `Commits must have verified signatures.` Both original heads and bases remained. |
| Verified then unsigned source commits | #109/#110 / #111 | Same signature failure, with both original heads and bases retained. |

The all-signed sources reused exact immutable verified objects `7ca2b1a7a38f3b3f6f1325c121bb11b025a1c786` and `7c586aee5324ed0aed0a97c310fdab00e025b27c`; no old ref was changed. Verification was recorded for every selected commit. A single verified commit at the tip was not used as a proxy for verification of a multi-commit group.

Fresh unprotected [#112/#113](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/113), stack #114, had a verified lower and a two-commit upper consisting of a verified source followed by an unsigned source. Lower-prefix landing succeeded at `f65f0738cfcfdf5fa917801109ac24b1053f091e`. Both upper replacements were verified: the previously verified first source became `85b9eeab9744a8d6998f9e85096a56e721aa8542`; the previously unsigned second source became `759f0d7022097514dd06ce9c511ac36496389e0c`. The exact classic protection GET was 404, and no rule was installed on that trunk.

For each replacement, full tree, author name/email/date, message (including disclosure trailer), and exact parent-to-commit binary patch remained equal. The complete upper layer patch also remained equal. The commit IDs and signed payload/signature identity changed. Thus this mixed-source branch was signed throughout after replacement even without a signature rule; the observation does not support a strictly per-original-commit signing rule. The earlier protected unsigned-source, unprotected verified-source, and unprotected all-unsigned controls remain separately referenced in the matrix.

## Actual code-scanning gates

The negative [#118/#119](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/119), stack #120, used exact named ruleset `gherrit-fu2-ci-scan`, no bypass actors, and a CodeQL requirement with error / high-or-higher thresholds. The repository's default setup reported `not-configured`, and analysis lookup reported none. Both PR gates were BLOCKED; the one native request failed with `Waiting for Code Scanning results. Code Scanning may not be configured for the target branch.`

The positive [#121/#122](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/122), stack #123, used a separate exact ruleset and a tiny Python file. Its own-ref workflow ran actual GitHub CodeQL init/analyze, pinned to the inspected official action commit `9418214df1f2c4b8128c770156c409013b07d6b9`. The trunk push and both PR opened/stacked analyses succeeded. Both gates became CLEAN; lower-prefix landing then reached terminal merged at `6f5b00960883c938a8a1361a7a109228c49552cd`.

The replacement upper `050956faa9142a4e8ea1d7be235b4e3b59400fa6` was initially BLOCKED. The new actual synchronize analysis and trunk push analysis succeeded, and its gate later became CLEAN. The capture retains run/jobs/logs, analyses, exact candidate/head checks and rule snapshots. No arbitrary green status or fabricated SARIF substituted for scanning. This is a synthetic clean Python fixture, not a security evaluation of GHerrit. Both named scanning rulesets were deleted, with independent 404 readbacks, after their observations.

## Required deployments: successful head or candidate evidence

Authorized synthetic [#137/#138](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/138) used only environment `gherrit-fu2-ci-deploy` and exact trunk ruleset of the same name, without bypass actors. Deployment creation disabled auto-merge and required contexts; statuses represented no external software deployment. The candidate was bound through own ref `exp/fu2/ci/deploy/candidate-upper` pointing to captured merge object `a0c97a2553513214fe16bffd52d4d9664863758f`.

| Upper source-head deployment | Upper candidate deployment | Observed upper gate |
| --- | --- | --- |
| None | None | BLOCKED |
| Success | None, then failure | CLEAN in both samples |
| Failure | Success | CLEAN |
| Failure | Failure | BLOCKED |
| Success restored | Failure | CLEAN |

The lower's successful source-head deployment remained CLEAN throughout. On this path, successful head or existing candidate deployment sufficed in the tested grid; candidate failure did not override a successful head as it did for the separate required-status context. The records bind exact deployment refs, SHAs and latest statuses. These finite observations do not guarantee settlement or all deployment configurations. All records were marked inactive and the exact temporary environment/rule were removed after capture.

## Event metadata is retained context, not an assumed snapshot fence

The slower #99/#100 publication retained `opened` artifacts with `stack:null`, then `stacked` artifacts with matching top-level/nested membership, positions and trunk identity. Rapidly published and registered upper #116 instead had an actual `opened` workflow artifact already containing nested native stack #117, position 2/size 2 and trunk SHA `7cc4fd48f2d44681e0167cf4bde875fb1b9b4e5a`; the opened trunk-filter job ran as well. Creation and registration were approximately one second apart.

These observations do not identify GitHub's internal enrichment or dispatch mechanism. They prevent treating event action `opened` alone as proof that the observed payload predates membership. `evidence/metadata-events.json` retains each action, raw head, direct base, nested/top-level stack summary, and actual checkout context. Native membership, direct PR base, stack trunk and actual tested candidate remain separate recorded identities.

## Review rules and the separate website-rebase gap

Root temporarily enabled bot PR creation/review permission while retaining default read-only workflow permissions. Twelve `github-actions[bot]` PR-creation jobs and two complementary approval jobs completed successfully; their per-job intent/response artifacts are retained. Root restored the original false flag, independently confirmed by this lane. These are synthetic machine role controls, not human reviews or usability evidence.

The exact direct-review trunks enforced admins, required one review and dismissed stale approvals. They differed in last-push/CODEOWNERS requirements. Every native request selected its captured lower head, disabled bypass, and used squash.

| Direct control | Initial review / gate | Prefix result and unchanged upper |
| --- | --- | --- |
| Last-push, bot PR author; joshlf reviewer and pusher, #135/#136 | Review record APPROVED, but REVIEW_REQUIRED / BLOCKED | Failed with `New changes require approval from someone other than joshlf because they were the last pusher.` Original heads/bases remained. An APPROVED record was insufficient for this rule. |
| Last-push complement, joshlf PR author/pusher; bot reviewer, #148/#149 | Both APPROVED / CLEAN | Lower landed at `f05f138a0975dab098d4a535ee0aed7e9fc67068`. Upper review `5821587539` remained APPROVED and rebound from `2161fb5e…` to replacement `92d700bcb68cf755fc593d4ec89e34e72bc1bdfa`; upper stayed CLEAN. |
| CODEOWNERS `* @joshlf`, bot PR author; joshlf reviewer, #139/#141 | Both APPROVED | Lower landed at `16dfa0db1bc16b0a7bb94a14bf6537f7dbb176f6`. Upper review `5821585856` was dismissed with `The merge-base changed after approval.`; replacement `fba42f08…` became REVIEW_REQUIRED / BLOCKED. |

Both successful prefix controls preserved the upper's exact complete tree, parent-to-head binary patch, author name/email/date and message. The retained complementary review and dismissed CODEOWNERS review therefore demonstrate condition-dependent outcomes. Their rule and author/reviewer configurations differ together; these fixtures do not isolate one cause for the different retention result.

The CODEOWNERS survivor was explicitly reapproved at `fba42f08…`, producing review `5821604462` and APPROVED / CLEAN. A substantive amendment retained its author and message, changed its own-layer patch/tree, and force-pushed with `pull.stacked` plus the exact old-SHA lease. Replacement `c28a839c6daedb3bf95e65f5d4c0f90305384b3b` dismissed that new review and became REVIEW_REQUIRED / BLOCKED. This extends the earlier substantive-change control to the actual CODEOWNERS configuration.

Four independent website fixtures remain ready and untouched by this lane: stale-review #127/#128; stale plus last-push #129/#130; CODEOWNERS #131/#132; verified sources plus required signatures #133/#134. Each trunk advanced by an unrelated commit after the before-advance capture, then enabled admin enforcement. The first and CODEOWNERS fixtures retained APPROVED reviews before the website step; the last-push fixture already reported REVIEW_REQUIRED because its reviewer was the pusher. All exact heads, reviews, protection settings and snapshots are retained.

**The actual website Rebase stack operation was not performed by this lane.** Root reported an unavailable browser host, app/input `cgWindowNotFound`, absent Chrome executable and no supported launch path, then closed its CUA part as unavailable. Root handed only upper #128 to the user asynchronously; that response remains a root-owned follow-up, and #127/#128 stay reserved. The other ready fixtures do not establish website retention or signing. RV01/RV02/RV03/SG04 are explicitly unavailable website experiments with preparation evidence, not performed operations. The automatic-prefix controls above and the reused local/hinted controls do not fill that gap.

## Current cleanup and limits

All nine native merge requests in this lane are terminal; no queue operation was armed. Both scanning rulesets and the deployment ruleset/environment were deleted with independent 404 readbacks; all three deployment records were marked inactive. Completed fixture-only classic protections were removed after retaining their exact configurations. Only the four reserved website fixture protections remain, as recorded in `cleanup.json`; especially #127/#128 must remain untouched during the user's pending handoff. Root restored the Actions bot flag and removed its temporary default-branch target workflow; this lane independently confirmed the flag false and file 404. No unrelated branch policy changed.

Two local harness failures are preserved and corrected: Python's configured bytecode cache targeted a non-writable host cache, so syntax validation used in-memory `compile`; `gh run view --log` initially targeted a non-writable default cache, so later reads used this lane's own `XDG_CACHE_HOME`. Neither was classified as provider behavior or retried as an uncertain hosted write.

*Authored by an AI agent acting on joshlf's behalf.*
