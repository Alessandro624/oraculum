"""Exercise the packaged executable against a local OpenAI-compatible endpoint."""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import subprocess
import threading


class Endpoint(BaseHTTPRequestHandler):

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))

        assert body["model"] == "test"
        assert "SATISFIABLE" in body["messages"][1]["content"]

        message = json.dumps({"satisfiable": True, "assignment": {}, "oracle_comment": "So it is."})
        payload = json.dumps(
            {"id": "test", "created": 0, "object": "chat.completion", "model": "test", "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": message}}]}
        ).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 0), Endpoint)

    threading.Thread(target=server.serve_forever, daemon=True).start()

    binary = "Windows/oraculum-bridge.exe" if os.name == "nt" else "Linux/oraculum-bridge"
    path = Path(__file__).parent / "com.oraculum.npc" / "Tools~" / binary

    messages = [{"provider": "ollama", "model": "test", "url": f"http://127.0.0.1:{server.server_port}/v1"}, {"question": "Why the déjà vu?", "reverence": 8}, {"formula": "x1", "reverence": 1}]

    result = subprocess.run([path], input="".join(json.dumps(m) + "\n" for m in messages), capture_output=True, encoding="utf-8", timeout=60, check=True)

    replies = [json.loads(line) for line in result.stdout.splitlines()]

    assert replies == [{"ready": True}, {"comment": "So it is."}, {"comment": "So it is."}], replies
    print("OK:", binary)
