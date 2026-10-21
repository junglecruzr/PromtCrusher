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
            if env_path.exists() and env_path not in candidates:
                candidates.append(env_path)

        for env_path in candidates:
            if load_dotenv is not None:
                load_dotenv(dotenv_path=env_path, override=True)
            key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if key and key.strip():
                return key.strip()

        return (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()

    def resolve_provider_settings(self) -> dict[str, str]:
        self.resolve_api_key()
        provider = os.getenv("API_PROVIDER", "gemini").strip() or "gemini"
        if provider == "anthropic":
            return {
                "provider": provider,
                "protocol": "anthropic",
                "api_key": os.getenv("ANTHROPIC_API_KEY", "").strip(),
                "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1").strip(),
                "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514").strip(),
            }
        if provider != "gemini":
            return {
                "provider": provider,
                "protocol": "openai-compatible",
                "api_key": os.getenv("OPENAI_API_KEY", "").strip(),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
            }
        return {
            "provider": "gemini",
            "protocol": "gemini",
            "api_key": self.resolve_api_key(),
            "base_url": "",
            "model": "gemini-3.8-flash",
        }
