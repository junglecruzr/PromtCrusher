import shutil
import subprocess
import sys
import webbrowser


class UILauncher:
    def launch(self, url: str) -> None:
        try:
            if sys.platform == "win32":
                subprocess.Popen(
                    ["cmd.exe", "/c", f"start chrome --app={url} || start msedge --app={url}"],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
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
