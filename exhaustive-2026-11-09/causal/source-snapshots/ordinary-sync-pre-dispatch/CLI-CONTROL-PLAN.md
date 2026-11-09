# Actual official CLI sync control

Proposed exact hosted case: `ordinary-sync-3`, A–B–C–D with its independent
`exh-1109-causal-ordinary-sync-3/trunk`. Root's grant is required before fixture
creation. The driver uses the retained official v0.3.0 binary, whose SHA256 is
`70c0cb11346ad5d4f97a02a5cf5242052254d1775d356dc0759f035457873850`.
Binary strings identify its embedded `github.com/cli/go-gh/v2@v2.16.2` sources.

`sync_driver.py` creates a private normal checkout with exact local refs before
native landing. It adopts those existing refs with audited `init --base`, then
lands A through the recorded direct squash API. After a bounded captured native
rewrite premise, it executes official `sync --remote origin --no-atomic=false`
once and checks actual Git/PR/event outcomes through the standard 60-second
window. It never uses prune, base-change acceptance, queue or website actions.

The child gets an isolated `GH_CONFIG_DIR` with only `http_unix_socket`. Pinned
go-gh source implements this by routing its HTTP/HTTPS dial to an owned Unix
socket. This does not alter the API host or global trust/configuration. The
socket directory is private, the socket is mode 0600, and the socket is removed
when the child completes. The recorder preserves/fsyncs each sanitized request
before forwarding to real `https://api.github.com` through normal upstream TLS
verification. Authentication headers stay in memory and are never logged. An
existing credential is obtained into child process memory only; no token is
printed or written to a file.

The recorder accepts only public experiment-repository GETs and the audited
client's named repository GraphQL read queries. Every HTTP mutation and unknown
scope/query is refused before upstream dispatch. This deliberately prevents an
opaque CLI native-group write fallback. If the command attempts such a write,
the case reports that blocked premise rather than success.

The private Git wrapper records/fsyncs every dynamic Git input and forces hooks
off. It permits one push only, to origin, atomic, with fully qualified B/C/D
source/destination refs and an explicit expected SHA for every target. It
refuses trunk/A/unrelated targets, absent leases, and any second push, including
the official CLI's unsupported-push-option fallback. Git transport does not use
the API Unix socket and retains its normal remote TLS behavior.

Eight local checks pass. The actual binary's read-only adoption probe also
passed: two exact `FindPRForBranch` GraphQL queries were recorded before
forwarding, both returned HTTP 200, and no HTTP mutation was attempted.
`binary-recorder-read-probe.json` and its raw receipts retain that result.
This validates the recorder path used by the binary; it does not validate an
unexecuted sync path or supply provider completion semantics.

The earlier local HTTPS CONNECT recorder is a tested alternative only. Actual
CLI execution uses the Unix recorder to avoid relying on Darwin custom-CA
environment behavior. No global certificate or proxy changes are needed.

*Authored by an AI agent acting on joshlf's behalf.*
