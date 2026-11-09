"""Acknowledged controls for the manually framed TLS request transport."""
from lab import *


def raw_ack(label, method, path, payload=None):
    if evidence_path(label, '.intent.json').exists():
        raise RuntimeError('Control already dispatched; no retry')
    record = request_intent(label, method, path, payload)
    body = b'' if payload is None else json.dumps(payload).encode()
    headers = {'Host': 'api.github.com', 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2026-03-10',
               'User-Agent': 'gherrit-synthetic-protocol-experiment',
               'Content-Type': 'application/json', 'Content-Length': str(len(body)),
               'Connection': 'close'}
    lines = [method + ' ' + path + ' HTTP/1.1']
    lines += [key + ': ' + value for key, value in headers.items()]
    lines += ['Authorization: Bearer ' + token(), '', '']
    wire = '\r\n'.join(lines).encode() + body
    record.update(headers_without_credentials=headers, request_bytes=len(wire))
    sock = ssl.create_default_context().wrap_socket(
        socket.create_connection(('api.github.com', 443), timeout=20),
        server_hostname='api.github.com')
    try:
        sock.sendall(wire)
        record['sent_at'] = now()
        response = http.client.HTTPResponse(sock)
        response.begin()
        raw = response.read()
        record.update(http=response.status, response_headers=dict(response.getheaders()),
                      response_body=raw.decode('utf-8', errors='replace'),
                      data=json.loads(raw) if raw else None,
                      first_status_read_after_send=True, ended_at=now())
    finally:
        sock.close()
    save(evidence_path(label, '.receipt.json'), record)
    if method != 'GET':
        time.sleep(2)
    return record


def run():
    get = raw_ack('P-T09-raw-get', 'GET', BASE)
    case = fixture('raw-ack-control', 1)
    body = 'Synthetic P-T09 raw TLS acknowledged control.\n\n' + NOTICE
    path = BASE + '/issues/' + str(case['prs'][0]) + '/comments'
    comment = raw_ack('P-T09-raw-comment', 'POST', path, {'body': body})
    oracle = read('P-T09-comment-readback', path + '?per_page=100')
    save(HOME / 'raw-control-results.json',
         {'P-T09': {'raw_get_http': get['http'], 'raw_comment_http': comment['http'],
                    'comment_id': (comment.get('data') or {}).get('id'),
                    'independent_matching_comments': [c['id'] for c in (oracle.get('data') or []) if c['body'] == body],
                    'transport': 'Same manual HTTP/1.1 framing, gh in-memory token, standard-library TLS',
                    'limit': 'Acknowledged positive control does not establish execution for prior closed transports'}})
    print(json.dumps({'get_http': get['http'], 'comment_http': comment['http']}))


if __name__ == '__main__':
    run()
