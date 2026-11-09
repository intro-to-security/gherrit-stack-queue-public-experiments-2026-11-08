"""Check that a received504 stops the harness and prevents a second dispatch."""
from pathlib import Path
import json
import tempfile
import lab


def run():
    dispatches = []

    class FakeResponse:
        status = 504

        def read(self):
            return b'{"message":"Synthetic timeout; effects unknown"}'

        def getheaders(self):
            return []

    class FakeConnection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, method, path, **kwargs):
            dispatches.append((method, path))

        def getresponse(self):
            return FakeResponse()

        def close(self):
            pass

    with tempfile.TemporaryDirectory(prefix='gherrit-protocol-guard-') as temporary:
        lab.EVIDENCE = Path(temporary)
        lab.TOKEN = 'synthetic-memory-only-control'
        lab.http.client.HTTPSConnection = FakeConnection
        attempts = []
        for _ in range(2):
            try:
                lab.api('synthetic-504', 'POST', lab.BASE + '/stacks', {'pull_requests': [1, 2]})
            except RuntimeError as error:
                attempts.append(type(error).__name__)
            else:
                raise AssertionError('A received504 must stop the caller')
        unknown = json.loads((Path(temporary) / 'synthetic-504.unknown.json').read_text())
        assert len(dispatches) == 1
        assert unknown['http'] == 504
        assert (Path(temporary) / 'synthetic-504.receipt.json').exists()
        result = {'test': 'Local fake transport; no native request dispatched',
                  'caller_stopped_after_received504': attempts == ['RuntimeError', 'RuntimeError'],
                  'attempts': 2, 'transport_dispatches': len(dispatches),
                  'unknown_effect_record_retained': True,
                  'cached504_blocked_before_second_transport': len(dispatches) == 1,
                  'limit': 'Checks this harness guard; no provider guarantee'}
    lab.save(lab.HOME / 'guard-test-results.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    run()
