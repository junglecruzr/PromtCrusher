import json
import os
import socketserver
import threading
import time
from http.server import BaseHTTPRequestHandler
from typing import cast

from app_config import AppConfig
from prompt_service import PromptService


class PromptHTTPServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, config: AppConfig, service: PromptService) -> None:
        self.config = config
        self.service = service
        super().__init__(server_address, PromptRequestHandler)


class PromptRequestHandler(BaseHTTPRequestHandler):
    @property
    def app_server(self) -> PromptHTTPServer:
        return cast(PromptHTTPServer, self.server)

    def log_message(self, format, *args) -> None:
        return

    def _send_json(self, data: object, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self) -> None:
        src_dir = self.app_server.config.source_dir
        path = self.path.strip("/")

        if path in ("", "index.html"):
            file_to_serve = src_dir / "index.html"
            content_type = "text/html"
        elif path == "app.js":
            file_to_serve = src_dir / "app.js"
            content_type = "application/javascript"
        elif path == "styles.css":
            file_to_serve = src_dir / "styles.css"
            content_type = "text/css"
        elif path == "ui-config.json":
            file_to_serve = src_dir / "ui-config.json"
            content_type = "application/json"
        elif path == "check-key":
            self._send_json(self.app_server.service.key_status())
            return
        elif path == "log":
            self._send_json({"content": self.app_server.service.read_output()})
            return
        elif path == "shutdown":
            self._send_json({"status": "shutdown_confirmed"})
            threading.Thread(target=self._shutdown_process, daemon=True).start()
            return
        else:
            file_to_serve = src_dir / path
            content_type = "text/plain"

        if file_to_serve.exists() and file_to_serve.is_file():
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(file_to_serve, "rb") as asset:
                self.wfile.write(asset.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Asset File Not Found.")

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        path = self.path.strip("/")
        service = self.app_server.service

        if path == "save-key":
            data = json.loads(post_data.decode("utf-8"))
            new_key = data.get("key", "").strip()
            if not new_key:
                self._send_json(
                    {"status": "error", "message": "⚠️ Input Error: Please paste a valid token string first."},
                    status=400,
                )
                return

            service.save_api_key(new_key)
            self._send_json({"status": "success"})
            return

        data = json.loads(post_data.decode("utf-8"))
        user_subject = data.get("subject", "").strip()
        if len(user_subject) > 200:
            self._send_json(
                {
                    "status": "error",
                    "message": "⚠️ SECURITY REFUSAL: Submitted topic exceeds 200 characters limit.",
                }
            )
            return

        try:
            result = service.generate(user_subject, data["framework"])
            self._send_json({"status": "success", "prompt": result})
        except Exception as exc:
            self._send_json({"status": "error", "message": service.error_message(exc)})

    @staticmethod
    def _shutdown_process() -> None:
        time.sleep(0.5)
        os._exit(0)
