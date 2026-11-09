import fcntl
import json
import harness as h
from cleanup_authority import prove

with (h.ROOT / "executor.lock").open("a+") as owner:
    fcntl.flock(owner, fcntl.LOCK_EX)
    proof = prove()
    for record in proof["protections"]:
        trunk = record["trunk"]
        h.require(h.api("restore-created-protection-" + trunk, "DELETE",
                        "repos/" + h.REPO + "/branches/" + trunk + "/protection"), [204])
        h.require(h.get("branches/" + trunk + "/protection", "restored-initial-404"), [404])
    h.require(h.api("restore-created-ruleset-26858731", "DELETE", "repos/" + h.REPO + "/rulesets/26858731"), [204])
    h.require(h.get("rulesets/26858731", "restored-ruleset-absent"), [404])
    h.save(h.ROOT / "cleanup.json", dict(time=h.now(), restored_protections=[r["trunk"] for r in proof["protections"]],
             restored_ruleset=26858731, post_absence_verified=True, PRs_retained=True, refs_retained=True,
             scope="Initial absence restored only for settings created under target-grant-001"))
    print(json.dumps(h.read(h.ROOT / "cleanup.json")))
