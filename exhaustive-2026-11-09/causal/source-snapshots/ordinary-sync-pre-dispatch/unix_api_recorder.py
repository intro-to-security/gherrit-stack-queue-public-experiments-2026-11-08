"""Record child-only go-gh Unix-socket HTTP; only scoped reads reach real TLS."""
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import socketserver
import tempfile
import threading
from urllib.parse import urlsplit
import uuid

import api_recorder
import harness as h


class ThreadingUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class Recorder:
    def __init__(self, name, config_directory, forward=api_recorder.upstream):
        self.name = name
        self.config_directory = Path(config_directory)
        self.config_directory.mkdir(mode=0o700)
        self.socket_directory = Path(tempfile.mkdtemp(prefix="gherrit-causal-", dir="/private/tmp"))
        self.socket_path = self.socket_directory / "api.sock"
        self.forward = forward
        recorder = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format, *args):
                pass

            def address_string(self):
                return "owned-unix-socket"

            def dispatch(self):
                if self.headers.get("Transfer-Encoding") or int(self.headers.get("Content-Length", "0")) > 1000000:
                    self.send_error(403, "Unsupported request framing")
                    return
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                permitted = api_recorder.allowed_read(self.command, self.path, body)
                label = recorder.name + "-cli-http-" + uuid.uuid4().hex[:12]
                safe_headers = {name: value for name, value in self.headers.items() if name.lower() in api_recorder.SAFE_REQUEST_HEADERS}
                intent = h.begin(label, {"kind": "cli-http-unix", "method": self.command, "path": self.path if permitted else urlsplit(self.path).path, "headers": safe_headers, "body": body.decode("utf8") if permitted else "[blocked request body omitted]", "permitted": permitted, "upstream": "https://api.github.com; normal certificate verification"})
                try:
                    if permitted:
                        status, headers, data = recorder.forward(self.command, self.path, body, dict(self.headers.items()))
                    else:
                        status, headers, data = 403, {"Content-Type": "application/json"}, b'{"message":"Causal Unix recorder refused mutating or out-of-scope HTTP request"}'
                    safe_response_headers = {name: value for name, value in headers.items() if name.lower() in api_recorder.SAFE_RESPONSE_HEADERS}
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

        self.server = ThreadingUnixServer(str(self.socket_path), Handler)
        self.socket_path.chmod(0o600)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        config = self.config_directory / "config.yml"
        config.write_text("http_unix_socket: " + str(self.socket_path) + "\n")
        h.flush_directory(self.config_directory)

    def start(self):
        self.thread.start()
        return {"GH_CONFIG_DIR": str(self.config_directory)}

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.socket_path.unlink(missing_ok=True)
        self.socket_directory.rmdir()


if __name__ == "__main__":
    raise SystemExit("Import Recorder into a separately granted isolated child process")
