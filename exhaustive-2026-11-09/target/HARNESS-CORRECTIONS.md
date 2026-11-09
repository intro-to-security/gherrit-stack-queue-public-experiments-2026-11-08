# Retained exact-input acceptance failure

The original `wait_ci` helper accepted whatever head a PR read returned. It did
not require that head to match the newly captured amendment. Consequently
`observations/p-current-fails-final.json` says ready while its PR/check evidence
still names old green `a7405818bdf87a815dd676574236e87504d7c78d`, after the exact
leased push had installed intended `3e44b08a3f07727a57bcf1fc9392ff560f373e49`.
The file and the original frozen source are retained unchanged.

The merge dispatcher had a separate exact-SHA reread. It sent the new SHA, not
the stale returned head. Its actual native request failed with the message that
the required check was in progress. Later `p-after-stale-control.json` and
`final-retained-p.json` both show the new SHA's actual completed failed check and
BLOCKED gate. The evidence therefore establishes that old green did not permit
this new pending head to land, followed by observed current failure. It does not
establish that a completed-failure snapshot preceded the admission request.

`exact_ci_acceptance.py` supplies a small corrected acceptance boundary. It
requires the returned PR head and check-run head to match the captured intended
SHA, as well as the exact context, producer, completion and success. Its local
checks use the retained actual stale/green/failed observations, including the
known-bad returned-green control. This is exercised experimental code, not a
production GHerrit integration or a claim that the old helper was safe.

The fresh event contrast has no head amendment between capture and observation;
its immutable reviewed helper stays unchanged for that separately granted
experiment. No hosted request was repeated to repair this reporting premise.

*Authored by an AI agent acting on joshlf's behalf.*
