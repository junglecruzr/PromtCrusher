import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


class AppConfig:
    def __init__(self) -> None:
        if getattr(sys, "frozen", False):
            self.exe_dir = Path(sys.executable).resolve().parent
            self.internal_dir = Path(sys._MEIPASS)
        else:
            self.exe_dir = Path(__file__).resolve().parent
            self.internal_dir = self.exe_dir

    @property
    def source_dir(self) -> Path:
        return self.internal_dir / "src"

    @property
    def output_file(self) -> Path:
        return self.exe_dir / "prompt_automation_output.txt"

    @property
    def user_env_file(self) -> Path:
        return self.exe_dir / ".env"

    def resolve_api_key(self) -> str:
        candidates = []
        for base in (self.exe_dir, self.internal_dir, self.exe_dir / "src", self.internal_dir / "src"):
            env_path = base / ".env"
            if env_path.exists():
                candidates.append(env_path)

        for env_path in candidates:
            if load_dotenv is not None:
                load_dotenv(dotenv_path=env_path, override=True)
            key = os.getenv("GOOGLE_API_KEY")
            if key:
                return key

        return os.getenv("GOOGLE_API_KEY", "")
