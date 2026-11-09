"""Per-child loopback HTTPS recorder. It forwards scoped reads and refuses writes."""
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import ssl
import subprocess
import threading
from urllib.parse import urlsplit
import uuid

import harness as h


SAFE_REQUEST_HEADERS = {"accept", "content-type", "user-agent", "x-github-api-version"}
SAFE_RESPONSE_HEADERS = {"content-type", "date", "etag", "x-github-request-id", "x-ratelimit-remaining"}


def allowed_read(method, path, body):
    parsed = urlsplit(path)
    if parsed.scheme or parsed.netloc or any(word in parsed.query.lower() for word in ("access_token", "client_secret", "authorization")):
        return False
    repository = "/repos/" + h.REPO
    if method == "GET" and (parsed.path == repository or parsed.path.startswith(repository + "/")):
        return True
    if method == "POST" and parsed.path == "/graphql":
        try:
            value = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return False
        query = value.get("query", "")
        variables = value.get("variables") or {}
        # Only the audited client's named repository read operations are accepted.
        return bool(re.match(r"^query (FindPRForBranch|FindPRDetailsForBranch|FindPRByNumber|RepositoryID)\(", query)) and "mutation" not in query.lower() and "viewer" not in query.lower() and query.count("repository(") == 1 and variables.get("owner") == "joshlf" and variables.get("name") == h.REPO.split("/")[1]
    return False


def upstream(method, path, body, headers):
    # The proxy's generated certificate is never used to validate GitHub upstream.
    connection = http.client.HTTPSConnection("api.github.com", timeout=30, context=ssl.create_default_context())
    cleaned = {name: value for name, value in headers.items() if name.lower() not in {"host", "connection", "proxy-connection", "transfer-encoding", "accept-encoding", "content-length"}}
    cleaned["Accept-Encoding"] = "identity"
    try:
        connection.request(method, path, body=body, headers=cleaned)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


class Recorder:
    def __init__(self, name, directory, forward=upstream):
        self.name = name
        self.directory = Path(directory)
        self.directory.mkdir(mode=0o700)
        self.forward = forward
        self.cert = self.directory / "child-ca.pem"
        self.key = self.directory / "child-ca.key"
        config = self.directory / "openssl.cnf"
        config.write_text("[req]\ndistinguished_name=dn\nx509_extensions=ext\nprompt=no\n[dn]\nCN=api.github.com\n[ext]\nsubjectAltName=DNS:api.github.com\nbasicConstraints=critical,CA:TRUE\nkeyUsage=critical,keyCertSign,digitalSignature,keyEncipherment\n")
        result = subprocess.run(["/usr/bin/openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-keyout", str(self.key), "-out", str(self.cert), "-config", str(config)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError("Local child certificate creation failed")
        self.key.chmod(0o600)
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(self.cert, self.key)
        self.context.set_alpn_protocols(["http/1.1"])
        recorder = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format, *args):
                pass

            def do_CONNECT(self):
                if self.path != "api.github.com:443":
                    self.send_error(403, "Recorder only accepts api.github.com")
                    return
                self.send_response(200, "Connection established")
                self.end_headers()
                self.connection = recorder.context.wrap_socket(self.connection, server_side=True)
                self.rfile = self.connection.makefile("rb", buffering=-1)
                self.wfile = self.connection.makefile("wb", buffering=0)
                self.close_connection = False
                try:
                    while not self.close_connection:
                        self.handle_one_request()
                finally:
                    self.close_connection = True
                    self.connection.close()

            def dispatch(self):
                if self.headers.get("Transfer-Encoding") or int(self.headers.get("Content-Length", "0")) > 1000000:
                    self.send_error(403, "Unsupported request framing")
                    return
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                permitted = allowed_read(self.command, self.path, body)
                label = recorder.name + "-cli-http-" + uuid.uuid4().hex[:12]
                safe_headers = {name: value for name, value in self.headers.items() if name.lower() in SAFE_REQUEST_HEADERS}
                # Credentials remain only in memory for upstream authentication.
                # Unsafe URLs are never retained because query strings can carry secrets.
                intent = h.begin(label, {"kind": "cli-http", "method": self.command, "path": self.path if permitted else urlsplit(self.path).path, "headers": safe_headers, "body": body.decode("utf8") if permitted else "[blocked request body omitted]", "permitted": permitted})
                try:
                    if permitted:
                        status, headers, data = recorder.forward(self.command, self.path, body, dict(self.headers.items()))
                    else:
                        status, headers, data = 403, {"Content-Type": "application/json"}, b'{"message":"Causal recorder refused mutating or out-of-scope HTTP request"}'
                    safe_response_headers = {name: value for name, value in headers.items() if name.lower() in SAFE_RESPONSE_HEADERS}
                    intent.update(end=h.stamp(), http=status, response_headers=safe_response_headers, response_body=data.decode("utf8"), forwarded=permitted)
                    h.save(h.EVIDENCE / (label + ".receipt.json"), intent)
                    self.send_response(status)
                    for name, value in safe_response_headers.items():
                        self.send_header(name, value)
                    self.send_header("Content-Length", str(len(data)))
                    self.send_header("Connection", "close")
                    self.end_headers()
                    self.wfile.write(data)
                except Exception as error:
                    h.save(h.EVIDENCE / (label + ".unknown.json"), {"at": h.stamp(), "error_type": type(error).__name__, "forwarded_read_only": permitted})
                    self.send_error(502, "Recorder could not complete read forwarding")
                self.close_connection = True

            do_GET = dispatch
            do_POST = dispatch
            do_PUT = dispatch
            do_PATCH = dispatch
            do_DELETE = dispatch
            do_HEAD = dispatch

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        return {"HTTPS_PROXY": "http://127.0.0.1:" + str(self.server.server_port), "HTTP_PROXY": "http://127.0.0.1:" + str(self.server.server_port), "SSL_CERT_FILE": str(self.cert), "NO_PROXY": "127.0.0.1,localhost"}

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.key.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit("Import Recorder into a separately granted isolated child process")
