import os

from app_config import AppConfig

try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None

try:
    from google.genai import errors as genai_errors
except ImportError:  # pragma: no cover
    genai_errors = None


FRAMEWORKS = {
    "RACE": "RACE (Role, Action, Context, Expectation)",
    "RISE": "RISE (Role, Instructions/Issue, Steps, Expectation/Example)",
    "STAR": "STAR (Situation, Task, Action, Result)",
    "SOAP": "SOAP (Subject, Objective, Action, Plan)",
    "APE": "APE (Action, Purpose, Expectation)",
    "ERA": "ERA (Expectation, Role, Action)",
    "BAB": "BAB (Before, After, Bridge)",
    "TAG": "TAG (Task, Action, Goal)",
    "RTF": "RTF (Role, Task, Format)",
}

BASELINE_PROMPT_TEMPLATE = """You are an expert Prompt Engineering Engine. Your sole task is to generate a comprehensive, highly optimized, and maximized \"Super Prompt\" based on a user-provided topic.
The generated Super Prompt must be fully formed, standalone, and ready for immediate deployment in an LLM.
CRITICAL STRUCTURAL REQUIREMENT: You must explicitly structure the final generated Super Prompt using the {framework_name} framework breakdown.
[INPUT TOPIC]
{subject}"""


class PromptService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.api_key = config.resolve_api_key()
        if genai is None:
            raise RuntimeError("Missing dependency: google-genai. Install it with 'pip install google-genai'.")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def key_status(self) -> dict[str, object]:
        if self.config.user_env_file.exists():
            return {
                "custom_active": True,
                "mode": "custom",
                "message": "🔒 User override active: this session is using a personal API token.",
            }
        if self.api_key:
            return {
                "custom_active": False,
                "mode": "evaluation",
                "message": "⚡ Evaluation key active: temporary pilot token is in use.",
            }
        return {
            "custom_active": False,
            "mode": "missing",
            "message": "⚠️ No API key is loaded. Please paste your own Gemini token in the dashboard.",
        }

    def save_api_key(self, key: str) -> None:
        with open(self.config.user_env_file, "w", encoding="utf-8") as env_file:
            env_file.write(f"GOOGLE_API_KEY={key}\n")

        os.environ["GOOGLE_API_KEY"] = key
        self.api_key = key
        self.client = genai.Client(api_key=key)

    def generate(self, subject: str, framework: str) -> str:
        if self.client is None:
            raise RuntimeError("No API client is active. Please save a valid Gemini key from the UI first.")

        framework_details = FRAMEWORKS.get(framework, FRAMEWORKS["RACE"])
        prompt = BASELINE_PROMPT_TEMPLATE.replace("{subject}", subject).replace(
            "{framework_name}", framework_details
        )
        response = self.client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
        result = response.text
        with open(self.config.output_file, "a", encoding="utf-8") as output:
            output.write(f"--- FRAMEWORK: {framework} | SUBJECT: {subject} ---\n{result}\n\n")
        return result

    def read_output(self) -> str:
        if not self.config.output_file.exists():
            return ""
        with open(self.config.output_file, "r", encoding="utf-8") as output:
            return output.read()

    @staticmethod
    def error_message(exc: Exception) -> str:
        if genai_errors is not None and isinstance(exc, genai_errors.APIError):
            if getattr(exc, "code", None) == 429:
                return "⚠️ 429 Rate Limit Exceeded: Throughput outpaced. Pause 60 seconds."
        return str(exc)
