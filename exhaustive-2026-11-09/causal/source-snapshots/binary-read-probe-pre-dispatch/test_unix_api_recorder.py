import http.client
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import harness as h
from unix_api_recorder import Recorder


class UnixRecorderTests(unittest.TestCase):
    def test_read_forwarding_write_refusal_and_credential_omission(self):
        forwarded = []

        def fake_upstream(method, path, body, headers):
            forwarded.append((method, path, headers.get("Authorization")))
            return 200, {"Content-Type": "application/json", "Set-Cookie": "secret-cookie"}, b'{"number":17}'

        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "evidence"
            evidence.mkdir()
            with patch.object(h, "EVIDENCE", evidence):
                recorder = Recorder("unix-local-test", Path(directory) / "config", fake_upstream)
                child_env = recorder.start()
                try:
                    self.assertEqual(set(child_env), {"GH_CONFIG_DIR"})
                    for method in ("GET", "POST"):
                        client = http.client.HTTPConnection("api.github.com")
                        client.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        client.sock.connect(str(recorder.socket_path))
                        client.request(method, "/repos/" + h.REPO + "/pulls/17", headers={"Authorization": "Bearer fixed-test-secret"})
                        response = client.getresponse()
                        self.assertEqual(response.status, 200 if method == "GET" else 403)
                        response.read()
                        client.close()
                finally:
                    recorder.close()
                self.assertEqual(forwarded, [("GET", "/repos/" + h.REPO + "/pulls/17", "Bearer fixed-test-secret")])
                retained = "".join(path.read_text() for path in evidence.glob("*.json"))
                self.assertNotIn("fixed-test-secret", retained)
                self.assertNotIn("secret-cookie", retained)


if __name__ == "__main__":
    unittest.main()
