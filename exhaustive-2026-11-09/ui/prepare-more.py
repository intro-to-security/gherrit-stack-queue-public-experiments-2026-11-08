"""Prepare fresh website failure and stale-vector cases; never repeat a write."""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'control'))
from rootlab import Lab, preserve


def main():
    lab = Lab(HERE, 'exh-1109-ui')
    ready = []
    for key, conflicting_file in [('conflict-a', 'a.txt'), ('conflict-b', 'b.txt'), ('stale-vector', None)]:
        case = lab.fixture(key, layers=2)
        files = dict(case['trees']['trunk'])
        files[conflicting_file or 'trunk-progress.txt'] = 'Independent incompatible trunk content.\n'
        new = lab.commit(files, case['commits']['trunk'], 'Advance the isolated website fixture trunk')
        lab.push(key + '-advance-trunk', {case['refs']['trunk']: (case['commits']['trunk'], new)})
        case['advanced_trunk'] = new
        for layer, number in case['prs'].items():
            case[layer + '_ready'] = lab.api(key + '-ready-' + layer.lower(), '/pulls/' + str(number))
        preserve(HERE / ('READY-' + key + '.json'), case)
        ready.append({'key': key, 'prs': case['prs'], 'group': case['stack']['number']})
    print(json.dumps(ready))


if __name__ == '__main__':
    main()
