# Interactive browser access and recovery

The initial UI attempt was unavailable through this session's tools. The user
later completed the four website rebases, and native Chrome control subsequently
became usable for a public history walkthrough. The chronology below preserves
the earlier failures; it does not describe the final state. API counterparts
must not be relabeled as website tests.

Observed attempts:

1. CUA inventory listed Chrome/Finder but returned no browsers and the error
   `The browser access host is unavailable`.
2. Selecting Chrome by bundle ID failed with `cgWindowNotFound`.
3. A shell attempt to open the named Chrome application failed because the
   attached shell could not find that application; it did not open a browser.
4. Selecting native Finder eventually returned only Desktop/menu state. The tool
   call reported 3,041.2713 seconds; parallel experiments continued during that
   stall. No browser operation was performed.
5. After reading the full CUA documentation, the documented Finder input fallback
   failed with `cgWindowNotFound`, and the documented optional app-launch API was
   not exposed. The CUA part was closed with an unavailable-access summary.

The session's computer-use documentation requires CUA for UI actions. No browser
cookie extraction, undocumented UI automation, or invented website action was
used to work around the missing capability.

The user was asked asynchronously to perform only **Rebase stack** on reserved
synthetic upper PR128, leaving Merge untouched. Source heads, separate-author
approvals, trunk advance and exact rules were captured first by ci-reviews.
There is no response at this checkpoint. It remains a pending participant action,
not a completed UI observation or approval inferred from elapsed time.

Four prepared website fixtures: upper128 stale-dismissal; upper130 last-push;
upper132 CODEOWNERS; upper134 signed. Only the CI lane owns their API preparation;
root owns an explicit UI handoff. Sources remain reserved while a user answer is
pending. Additional experiments continue independently.

## Later user-operated website observation

The user subsequently reported “Rebase stack completed” for upper PR128. The
CI lane independently verified changed lower/upper heads, unchanged layer
patches/author/messages, retained approvals, incorporated trunk changes and
verified replacements. This is an actual user-attested website operation with
independent API/Git outcome evidence, not an agent browser action or an inferred
REST receipt. The new report supersedes the earlier no-response checkpoint for
that fixture only. The user was then asked to run the other three ready rebases
and one reviewer-history task; those answers remain pending at this checkpoint.

## Repaired native Chrome surface

The user subsequently reported all three remaining rebases complete. CI collected
independent outcomes and removed the four completed fixture protections. Native
Chrome selection now succeeded, despite the browser-host inventory error. The
agent completed the public history-link walkthrough recorded in
[HISTORY-BROWSER-RESULTS.md](HISTORY-BROWSER-RESULTS.md). This profile is logged out
of GitHub with no saved credential offered; the user was asked to sign in directly
for owner-only queue controls. That handoff is pending. A fresh held-queue fixture
is prepared but unadmitted, so waiting for login cannot leave it armed.

## Completed authenticated extension

The user subsequently confirmed sign-in as joshlf. Native Chrome exposed owner controls on the fresh public fixture. After one API admission, actual upper and middle website removal confirmations each returned visible “Not Found”. Independent API/Git reads after each retained ABC. A single authorized lower-A cleanup removed all three manually before timeout, leaving the queue empty and PRs open/unmerged with exact source/trunk/archives. [Browser observations](QUEUE-BROWSER-RESULTS.md) and the [API result](../queue/ui-removal/RESULTS-UI.md) supersede the earlier pending-login checkpoint. No website HTTP status, initiating UUID or internal routing cause was captured or inferred. The CUA part ended with its observed-error summary.

*Authored by an AI agent acting on joshlf's behalf.*
