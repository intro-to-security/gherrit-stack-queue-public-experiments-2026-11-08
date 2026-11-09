import http.client
import json
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import patch

import api_recorder
import harness as h


class RecorderTests(unittest.TestCase):
    def test_tls_read_forwarding_write_refusal_and_credential_omission(self):
        forwarded = []

        def fake_upstream(method, path, body, headers):
            forwarded.append({"method": method, "path": path, "authorization": headers.get("Authorization")})
            return 200, {"Content-Type": "application/json", "Set-Cookie": "secret-cookie"}, b'{"number":17}'

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence"
            evidence.mkdir()
            with patch.object(h, "EVIDENCE", evidence):
                recorder = api_recorder.Recorder("local-test", root / "proxy", fake_upstream)
                recorder.start()
                try:
                    for method in ("GET", "PUT"):
                        client = http.client.HTTPSConnection("127.0.0.1", recorder.server.server_port, context=ssl.create_default_context(cafile=str(recorder.cert)))
                        client.set_tunnel("api.github.com", 443)
                        client.request(method, "/repos/" + h.REPO + "/pulls/17", headers={"Authorization": "Bearer fixed-test-secret"})
                        response = client.getresponse()
                        self.assertEqual(response.status, 200 if method == "GET" else 403)
                        response.read()
                        client.close()
                finally:
                    recorder.close()
                self.assertEqual(len(forwarded), 1)
                self.assertEqual(forwarded[0]["method"], "GET")
                self.assertEqual(forwarded[0]["authorization"], "Bearer fixed-test-secret")
                retained = "".join(path.read_text() for path in evidence.glob("*.json"))
                self.assertNotIn("fixed-test-secret", retained)
                self.assertNotIn("secret-cookie", retained)
                receipts = [json.loads(path.read_text()) for path in evidence.glob("*.receipt.json")]
                self.assertEqual({item["forwarded"] for item in receipts}, {True, False})

    def test_scope_and_query_policy(self):
        self.assertFalse(api_recorder.allowed_read("GET", "/user", b""))
        self.assertFalse(api_recorder.allowed_read("GET", "/repos/other/private", b""))
        self.assertFalse(api_recorder.allowed_read("POST", "/graphql", b'{"query":"mutation { something }"}'))
        self.assertFalse(api_recorder.allowed_read("GET", "/repos/" + h.REPO + "?access_token=secret", b""))


if __name__ == "__main__":
    unittest.main()
