"""Prepare one fresh clean website rebase fixture; re-entry never repeats writes."""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "control"))
from rootlab import Lab, preserve


def main():
    lab = Lab(HERE, "exh-1109-ui")
    case = lab.fixture("clean-rebase", layers=2)
    files = dict(case["trees"]["trunk"])
    files["trunk-progress.txt"] = "Independent trunk progress for actual website rebase.\n"
    new_trunk = lab.commit(files, case["commits"]["trunk"], "Advance the synthetic website-test trunk")
    lab.push("clean-rebase-advance-trunk", {case["refs"]["trunk"]: (case["commits"]["trunk"], new_trunk)})
    case["advanced_trunk"] = new_trunk
    for layer, number in case["prs"].items():
        case[layer + "_ready"] = lab.api("clean-rebase-ready-" + layer.lower(), "/pulls/" + str(number))
    preserve(HERE / "READY-clean-rebase.json", case)
    print(json.dumps({"prs": case["prs"], "trunk": case["refs"]["trunk"], "phase": "ready for browser; no website action yet"}))


if __name__ == "__main__":
    main()
