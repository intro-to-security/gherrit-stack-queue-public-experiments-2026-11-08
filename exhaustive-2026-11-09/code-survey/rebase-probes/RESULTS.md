# Explicit REST rebase: capability not exercised

Two separately granted initiations, one numeric and one named, each returned
HTTP 404 on the same owned fixture. The fixture remains frozen. No admitted job,
marker or additional fixture was produced. These known rejections do not
establish permanent endpoint unavailability or a universal lack of native
server-side rebasing: root separately captured a website job through a different
private interface.

The independent fixture is A #650, B #651, C #652, native group #653 in
`joshlf/gherrit-native-stack-experiments-2026-11-08`. Immediately before the
request, the full expected vector matched the captured owned refs. Only its
synthetic trunk had advanced, with a nonconflicting file addition. The numeric
repository identity `1450723431` was checked before publication and again during
diagnosis. `capability-summary.json` preserves exact identities/graphs/trees.

| Read or single initiation | API version / configuration | Result |
| --- | --- | --- |
| PUT `/repositories/1450723431/stacks/653/rebase` | 2026-03-10, complete expected-head map | 404 Not Found; request interval 14:56:18.077010–19.297714 UTC on November 9, 2026 |
| PUT `/repos/joshlf/gherrit-native-stack-experiments-2026-11-08/stacks/653/rebase` | Separate grant, 2026-03-10, freshly verified complete expected-head map | 404 Not Found; request interval 15:14:20.526517–20.712607 UTC |
| GET same numeric status route | 2026-03-10 | 404 |
| GET named `/repos/joshlf/gherrit-native-stack-experiments-2026-11-08/stacks/653/rebase` alias | 2026-03-10 | 404 |
| GET numeric repository baseline | 2026-03-10 | 200; exact repository ID and full name agree |
| GET ordinary owned stack | 2026-03-10 | 200; #653 contains exactly [#650, #651, #652] |
| GET both status aliases | 2022-11-28, explicit recommended JSON Accept | Both 404 |
| GET both status aliases | 2026-03-10, source-configured VS Code preview Accept values and user agent | Both 404 |

Five bounded ref/PR/event observation cohorts followed the numeric request through 30 seconds.
All three PRs stayed open, all member heads stayed at their originals and the
trunk stayed at the deliberately advanced SHA. No successful job premise was
obtained, so no capability proof or marker was produced. The other matrix
controls remain unrun because their positive premise is missing.

After the numeric request's known rejection and read-only diagnosis, root
separately reviewed and granted one exact named initiation. Fresh repository,
group, canonical PR node IDs, ordered membership, adjacent bases, Git and PR heads,
and advanced trunk checks passed before dispatch. This was new coordinator
authority; it was not a repeated numeric request or authority inferred from a
status URL. `named-alias.case.json` preserves its separate intent and receipt.
Immediate readback was unchanged. An independent final read at 15:14:57 UTC
again found the exact original member heads, advanced trunk, three open PRs and
no force-push/base-change timeline events; repository/group GETs were 200 and
both status aliases were 404. `terminal-readback.json` retains the raw observations.
Git and PR projection reads remain separate observations: for example, A's
GraphQL `baseRefOid` still reported the original trunk while Git reported its
deliberately advanced ref.

**Source and documentation diagnosis.** Current VS Code HEAD remains
`8bd445fbeee54d7fbb54b2712b29baa3de9356e5`, the inspected pin. Its implementation
uses the numeric route, header version 2026-03-10, and ordinary Octokit REST
dispatch. The current credential factory defaults to `https://api.github.com`
and configures shadow-cat/merge-info previews; the logging wrapper limits/logs
calls without rewriting this route. The corresponding mocked accepted response
contains a named-repository status URL, which supplied the read-only alias probe.
`DIAGNOSTIC-SOURCES.json` fixes the additional source identities.

The current public OpenAPI HEAD remains
`2f8f80e47ea4d3292cf4e37ba9d9b25475e06140`. The already retained complete-schema
hash/focused extraction contains the native stack create/list/get/add/unstack
paths and merge-async paths, with no rebase path. The current public
[stack REST page](https://docs.github.com/en/rest/pulls/stacks?apiVersion=2026-03-10)
also has no rebase section. The returned error's documentation anchor therefore
does not supply a published route or semantic promise.

The response reports accepted OAuth scope `repo`, while this request's existing
OAuth credential includes `repo`; ordinary repository, stack and creation paths
worked. That rules out several simple identity/scope mistakes, but not a feature
gate, token-class restriction, undisclosed permission, route enrollment or
another implementation difference. A status GET can also return 404 when no job
was created. These reads and the two exact PUT failures do not distinguish those
possibilities or establish what another enrolled client or token class would see.

The bounded route diagnosis is complete. No further alternate initiation was
sent. The useful unresolved dependency is authoritative availability,
permission or routing guidance. The failures are not passing vector-CAS,
partial-conflict, overlap or future-write-fence tests.

`dispatch-audit.json` accounts for six native API write dispatches (three PRs,
one group, the two separately granted rejected rebase requests) and two
exact-lease Git pushes. All have receipts; no request was repeated. The bare repository passes Git object checking
with hooks disabled. A bounded credential-pattern scan found no matches in the
retained evidence. Initial and refreshed pre-execution source snapshots and the
exact root grants/hashes remain retained. Thirteen offline guard tests pass;
these test the experimental helpers, not provider correctness.

Both requests are known HTTP rejections, not unknown client acknowledgements or
admitted pending jobs. Unchanged bounded reads still do not establish an
unlimited provider quiescence guarantee. There are no remaining write, cleanup
or background-worker obligations. Owned refs, PRs, group, local objects, source
snapshots and sanitized raw requests/responses remain available for independent
audit. No cleanup write is needed or authorized.

The exact published OpenAPI SHA-condition wording is separately preserved in
`sha-condition-source.json`. Selected-head timing must not be overread: old
requested-revision landing plus a surviving later PR head does not date that
push relative to actual server merge linearization. Neither that race nor the
documented selected-head condition settles post-terminal suffix arbitration.

*Authored by an AI agent acting on joshlf's behalf.*
