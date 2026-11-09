# One bounded Actions installation-token capability probe

This is a feasible, materially different authentication probe, with an asymmetric
result. A successful initiation would establish that the discovered route is
accessible to this repository's Actions installation token under the captured
permissions. Another 404 would leave route enrollment, App identity, permission
and rollout explanations unresolved. It would not rule out all App tokens or
prove that the earlier failures were independent of token class.

Both separately granted phases have now run. PRs #654/#655 and group #656 exist;
the one reviewed runner push produced one Actions run and one known HTTP404
native request, with actual Contents/PullRequests write grants. The two final
read cohorts retained the original heads and advanced trunk.
[RESULT.md](RESULT.md) and [EXECUTION-STATE.json](EXECUTION-STATE.json) record
actual outcomes; the plan below is historical intent, not permission to rerun it.
No further mutation is authorized here. No repository setting or credential
was created or changed. The
original #650/#651/#652 group #653 remains frozen. The
source-only curation files under `publication/prep/` are unchanged.

## Why this tests a new premise

GitHub documents `GITHUB_TOKEN` as a job-specific GitHub App installation token
limited to the workflow repository. That differs from the earlier OAuth
`repo` credential. No new App registration, secret or account/global setting is
needed. This supports the authentication mechanism; it does not establish that
the source-discovered rebase endpoint accepts it. The public stack documentation
describes installation-token grants for stack reads/create, while its inspected
page still omits whole-stack rebase. The route's required permissions remain
unknown. See [GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token)
and [stack REST documentation](https://docs.github.com/en/rest/pulls/stacks?apiVersion=2026-03-10).

Read-only synthetic-repository GETs found Actions enabled, all actions allowed,
nine active workflows, default token permissions `read`, and
`can_approve_pull_request_reviews: false`. Exact selected readbacks and verified
action pins are in [READONLY-RECEIPTS.json](READONLY-RECEIPTS.json). The planned
job explicitly requests `pull-requests: write` and `contents: write`; it does not
create or approve PRs with that token. Workflow permissions can modify the
default, although higher policy can constrain writes. The actual job's Setup
job token-permission display must be retained; the YAML and repository default
are not measurements of its effective capability. See
[workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions).

The scoped contents write grant deliberately covers plausible ref-rewrite
requirements. It avoids starting with a read-only contents grant and then
thrashing permissions after another rejection. Repository/global defaults stay
unchanged. No permission/header/route matrix follows a failure.

A positive result would refute a credential-independent claim that this route
cannot be initiated in the repository. It would not isolate token class as the
sole cause: the case is fresh, time has advanced, the Actions App identity is
specific, and its permission vector differs. It would also not make this an
officially supported rebase API or a suffix-write fence. A negative result is a
bounded additional capability observation, not a general App-enrollment test.

## Exact new scope for root to instantiate

Use repository `joshlf/gherrit-native-stack-experiments-2026-11-08`, numeric ID
`1450723431`, and fresh prefix `exh-1109-causal-rb-app-001` only:

- Synthetic trunk: `.../trunk`.
- Two tiny member heads: `.../A` then `.../B`, with two new canonical PRs and
  one new native group. A third member is supported by the source but adds no
  useful capability distinction here; use two.
- Separate create-only runner branch: `.../runner`.

Create a clean tiny synthetic history: A adds only `a.txt`; B adds only `b.txt`.
Register the ordered A/B group, then advance its synthetic trunk once with
nonconflicting `trunk.txt`. Retain original own patches and expected final
tree/parent observations. There must be no merge, queue, auto-merge, conflict
injection or concurrent writer. No old fixture or default branch is used.

The runner branch should contain only reviewed `probe.py`, filled `fixture.json`
and `.github/workflows/rb-app-probe.yml` from the template, plus any required
authorship notice. Build its tiny source tree without inheriting the nine
existing workflow files. Do not edit main, repository defaults or global Actions
settings. Root must inspect the proposed tree/commit and record exact identities
before pushing its one fresh runner ref.

Fill `fixture.template.json` with the new group number/node ID, each new PR
number/node ID, exact head OIDs and advanced trunk SHA. Set `probe_sha256` to
the reviewed script's SHA256 and `root_reviewed` to true. Compute SHA256 of the
complete final config bytes and substitute it into `PROBE_CONFIG_SHA256` in
`workflow.template.yml`. This binds config and code without an impossible
self-reference to their enclosing commit SHA. Root's dispatch record binds the
complete runner commit; the job also records event `GITHUB_SHA` and run identity.
All placeholders make the unfilled templates fail before a request.

## One-shot execution and evidence boundary

The workflow listens only to creation of the exact runner branch by `joshlf`,
in the exact repository, with `run_attempt == 1`. Updates, reruns and other
events skip the job. Checkout uses the triggering immutable SHA, pinned official
action source and `persist-credentials: false`. The script additionally checks
event/ref/repository/first-attempt identities, source/config hashes, live
repository/group/membership/PR identities, adjacent bases and both PR/Git heads.
It refuses changed premises without adapting the expected map.

After successful reads, it writes an exclusive fsynced attempt record containing
the complete map and source/run identity, then calls exactly:

```text
PUT /repositories/1450723431/stacks/<NEW_GROUP_NUMBER>/rebase
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2026-03-10
{"expected_head_oid_by_pr_number":{"<NEW_A_PR>":"<EXACT_A_OID>","<NEW_B_PR>":"<EXACT_B_OID>"}}
```

The token is passed only through the step environment and Authorization header.
There is no environment/header dump, shell tracing, token-print command,
credential artifact, redirect following, PUT retry or named-route fallback.
Recorded headers are allowlisted. Response JSON/text is sanitized for the exact
token, common token forms and sensitive keys; oversized bodies are explicitly
omitted rather than represented by a publicly inspectable hash.

For a 2xx only, the script performs one immediate GET of the same status route.
It does not poll, call terminal status a complete graph, or infer a write fence.
The pinned upload action retains only `evidence/*.json`, including intent,
sanitized status/body, preflight results and selected job identities. Root must
fetch/read back that exact artifact and retain Setup job permissions plus
independent PR/Git/event/parent/patch readbacks. Known rejection, admission,
partial/successful graph and unknown acknowledgement remain separate outcomes.

The local attempt file fences one process/workspace, not all future Actions
runs. Do not delete/recreate the runner branch, rerun the job or repeat the PUT.
If a run disappears or transport fails after intent, freeze the new scope and
reconcile read-only. A missing artifact does not prove that no request occurred.
No claim of exactly-once provider execution is made.

## Interpretation and stopping rule

| Captured result | Supported conclusion and next boundary |
| --- | --- |
| Preflight/read/token permission failure | App-token experiment premise unavailable. No rebase dispatch. Retain the exact dependency; do not change settings or silently broaden permissions. |
| PUT 404, independent unchanged readbacks | This Actions installation/token/permission combination did not admit the route at this time. Enrollment, routing, App identity and other permissions remain unresolved. Stop. |
| PUT 401/403 | Authentication/permission/policy dependency, with any accepted-permission header retained. `contents: write` may be insufficient for this undocumented route; no broader grant follows. Stop. |
| PUT 409/422 | A route/validation result, not demonstrated successful execution or a universal vector guard. Keep exact body and fresh-premise evidence. Stop. |
| PUT 2xx | Current initiation capability established for this token context. Root observes the admitted job/ref outcomes read-only; do not perform a mismatch/conflict/overlap matrix under this plan. |
| Transport loss or missing request outcome | Unknown write; freeze and reconcile, with no automatic resend. |

After this one new case, stop. Another 404 would not justify a succession of
token/header/route/permission variants. The precise remaining dependency would
be provider availability/enrollment and permission guidance, or an explicitly
authorized independently registered App context. Neither is supplied by this
Actions probe. Source preparation and mocked checks are not a hosted result.

*Authored by an AI agent acting on joshlf's behalf.*
