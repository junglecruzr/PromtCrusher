import shutil
import subprocess
import sys
import webbrowser


class UILauncher:
    def launch(self, url: str) -> None:
        try:
            if sys.platform == "win32":
                browser = shutil.which("chrome") or shutil.which("msedge")
                if browser:
                    subprocess.Popen(
                        [browser, f"--app={url}"],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    webbrowser.open(url)
            elif sys.platform.startswith("linux"):
                for browser in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
                    browser_path = shutil.which(browser)
                    if browser_path:
                        subprocess.Popen([browser_path, f"--app={url}"])
                        return
                subprocess.Popen(["xdg-open", url])
            else:
                subprocess.Popen(["xdg-open", url])
        except Exception:
            try:
                webbrowser.open(url)
            except Exception:
                pass
