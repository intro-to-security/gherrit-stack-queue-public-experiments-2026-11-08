import json
import harness as h

for name in h.SPECS:
    h.observation(name, "final-retained-" + name)
    h.logs(name, "final-retained-" + name)
    print(json.dumps(dict(final_read=name)), flush=True)
