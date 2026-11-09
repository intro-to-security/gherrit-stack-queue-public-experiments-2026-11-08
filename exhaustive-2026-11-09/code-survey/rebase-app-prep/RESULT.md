# Actions installation token also received HTTP 404

The fresh Actions-token whole-stack rebase request returned HTTP 404. This job
actually had both `contents: write` and `pull-requests: write`, and the response
named those same required permissions. The original A/B heads, advanced trunk,
open PRs and canonical group remained unchanged at both later read cohorts.
No job admission, retry, named fallback or second native request occurred.

This is one current capability result for the repository's Actions installation
identity and captured permission vector. It does not distinguish enrollment,
routing, App identity restrictions, rollout or other undisclosed policy. It does
not establish universal endpoint unavailability or a suffix-write fence.

## Exact request, job and permission evidence

Root separately granted fixture creation and runner launch in
`control/rebase-app-grant-001.json` and `control/rebase-app-grant-002.json`.
The fresh scope is `exh-1109-causal-rb-app-001` in the authorized public synthetic
repository. A is PR [654](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/654),
B is [655](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/pull/655),
and their native group is 656. The original OAuth-token 404 fixture was untouched.

The create-only runner push published reviewed orphan commit
`6f7f0d9322bc6ddaf72bc3043c15463ecbd92b6e`, whose tree contains only the reviewed
probe, config and one workflow. Exactly one matching push
[run 42657475024](https://github.com/joshlf/gherrit-native-stack-experiments-2026-11-08/actions/runs/42657475024),
attempt 1, completed. The workflow's success means that it collected and uploaded
the result; it does not mean that the native endpoint succeeded.

[Actual Setup job lines](run-001/readback/effective-permissions.json) record
Contents write, PullRequests write and the implicit Metadata read permission.
All seven preflight GETs succeeded with the job token, checking repository,
group, trunk, both canonical PRs and their Git refs. These successful reads and
granted write permissions are separate evidence from an App-token write-positive
control, which was not added.

[The exact request and response](run-001/readback/artifact/put-result.json) retain
the 16:42:37.021240–37.338531 UTC interval on November 9, 2026:

```text
PUT /repositories/1450723431/stacks/656/rebase
API version: 2026-03-10
expected_head_oid_by_pr_number:
  654: 5afe9c34540002ec9554c2e9d279f4fa895d89db
  655: 11ddd6ef32afc4bca7865a22c70248a6156edee7
HTTP 404
X-Accepted-GitHub-Permissions: pull_requests=write,contents=write
```

The body is `Not Found`, with the rebase-a-pull-request-stack documentation
anchor. Matching that accepted-permission header to the actual job permissions
addresses the avoidable contents-read confound. It does not reveal every feature
gate or make the undocumented route's contract public. The known HTTP response
is retained, so this is not an unknown client acknowledgement or admitted job.

## Artifact and independent readback

[Artifact verification](run-001/readback/artifact-verification.json) checked
artifact 13693550267. Its ZIP SHA256
`69b29179b0ec85cd73b83fd169f4a668726a554c8a2cc050e8ad3ad17147b73e` matches
GitHub's recorded digest. All ten members are unique safe relative regular
UTF-8 JSON files. No absolute/traversing path, symlink, non-JSON member or
credential-token pattern passed the checks. The extracted context and intent
match the exact run, source commit, configured hashes, native path and map.
The token value was not logged or retained. Pattern scanning is bounded; it is
not a certification that arbitrary secrets are detectable.

Two read-only cohorts retained actual Git refs/fetched objects, GraphQL canonical
PR/timeline fields, native membership, commit parents and own patches:

| Cohort | Actual UTC interval | Seconds from PUT response end to first read |
| --- | --- | --- |
| [First](run-001/readback/after-0.json) | 16:45:46.077223–47.355730 | 188.739 |
| [Final](run-001/readback/after-30.json) | 16:46:24.352781–25.621122 | 227.014 |

Both show A `5afe9c34540002ec9554c2e9d279f4fa895d89db`, B
`11ddd6ef32afc4bca7865a22c70248a6156edee7`, trunk
`1eadf6cbffab4ef16d21830f06e5806cf8eb1b1a` and the exact runner commit.
Both canonical PRs remain open, the ordered group remains [654,655], and their
original own patches and parent links are unchanged. Complete fresh-scope
force/base-change timeline pages have zero nodes. Separate timed reads and absent
events do not establish continuous silence, exact physical write timing or
exclusion of a later writer.

The scope is terminal and retained. Five known fixture dispatches, one known
runner push and one known Actions PUT have receipts. There were no workflow
reruns, ref recreations, native retries or post-404 status GETs. No main,
production setting, global permission or credential change occurred. PRs,
group, refs, local objects, sources, job log, archive and extracted JSON remain
available; no cleanup mutation or further matrix is authorized by these grants.

[RESULT.json](RESULT.json) supplies exact identities, hashes, grants and limits.
The fresh two-member shape, time and specific Actions App identity differ from
the earlier OAuth case, so this is not a causal isolation of token class alone.
The remaining useful dependency is provider availability/enrollment/routing
guidance or another separately authorized App context, rather than more variants
of the same failed initiation.

*Authored by an AI agent acting on joshlf's behalf.*
