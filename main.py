import os
import datetime
import multiprocessing
import socketserver
import sys

from app_config import AppConfig
from prompt_service import PromptService
from ui_launcher import UILauncher
from web_server import PromptHTTPServer


EXPIRATION_DATE = datetime.date(2027, 12, 31)


def show_message_box(title: str, message: str, style: int = 0) -> None:
    if sys.platform == "win32":
        import ctypes

        try:
            ctypes.windll.user32.MessageBoxW(0, message, title, style)
        except Exception:
            print(f"{title}: {message}")
    else:
        print(f"{title}: {message}")


def main() -> None:
    if datetime.date.today() > EXPIRATION_DATE:
        show_message_box(
            "PromptCrusher Beta - Expired Build",
            "This test distribution build has EXPIRED.\n\nPlease contact the developer for an updated release version.",
            0x10,
        )
        return

    config = AppConfig()
    service = PromptService(config)
    if not service.api_key:
        show_message_box(
            "PromptCrusher - Configuration Warning",
            "No GOOGLE_API_KEY was found. The local UI will start and let you apply a Gemini API key from the dashboard.",
            0x40,
        )

    multiprocessing.freeze_support()
    port = 8124
    url = f"http://127.0.0.1:{port}/index.html"

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with PromptHTTPServer(("", port), config, service) as httpd:
            UILauncher().launch(url)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.shutdown()
    except OSError as exc:
        raise SystemExit(f"Port {port} is already in use: {exc}") from exc


if __name__ == "__main__":
    main()
