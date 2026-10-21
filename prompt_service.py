import os

from app_config import AppConfig
from workflows.models import ProjectBlueprint, WorkflowTask

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
    "SOP": """SOP (Schema, Operations, Proof), a framework for generating reliable structured-output prompts.

For SOP, define the requested output contract before the content task:
- SCHEMA: exact JSON, XML, table, or other output shape; field names; data types; required and optional fields; nesting; and allowed values.
- OPERATIONS: the role, input data, transformation steps, normalization rules, calculations, and ordering requirements.
- PROOF: validation rules, completeness checks, consistency checks, examples, invalid-input behavior, and a strict instruction to return only the requested format.

Never invent missing values without labeling them. Preserve exact source values when requested, distinguish null from unknown, and make the result usable by a parser or downstream application.""",
    "DEV": """DEV (Discovery, Engineering, Verification), a framework for implementation-ready software development prompts.

For DEV, structure the prompt into:
- DISCOVERY: repository context, existing architecture, relevant files, dependencies, runtime, interfaces, and assumptions.
- ENGINEERING: requirements, behavior, data flow, API or UI changes, error handling, security, compatibility, code style, and ordered implementation steps.
- VERIFICATION: tests, edge cases, diagnostics, acceptance criteria, migration concerns, and commands or checks used to validate the result.

Require minimal changes, reuse existing patterns, avoid invented files or APIs, preserve unrelated behavior, and identify unknowns instead of silently guessing.""",
    "AGT": """AGT (Aim, Guardrails, Tools, Workflow), a framework for safe tool-using agent prompts.

For AGT, define:
- AIM: the measurable objective, scope, priorities, and final deliverable.
- GUARDRAILS: permissions, prohibited actions, privacy and security rules, confirmation requirements, budgets, maximum steps, and stop conditions.
- TOOLS: each available tool, its inputs, outputs, limitations, and when it may be used. Never assume a tool exists unless it is listed.
- WORKFLOW: observe, plan, select a tool, validate its result, recover from errors, ask for clarification when blocked, and report completion with evidence.

Require reversible actions where possible, explicit confirmation for destructive or external side effects, no fabricated tool results, and a concise final status report.""",
    "RAG": """RAG (Request, Authorities, Grounding), a framework for research and retrieval-augmented prompts.

For RAG, specify:
- REQUEST: the research question, scope, audience, date range, definitions, and desired answer format.
- AUTHORITIES: preferred source types, source quality ranking, citation style, retrieval requirements, and how to handle inaccessible or conflicting sources.
- GROUNDING: extract evidence before making claims, connect claims to sources, separate facts from inference, report uncertainty, identify missing evidence, and never fabricate citations.

Require a source list or citation map, transparent assumptions, clear distinction between current and historical information, and a final completeness and contradiction check.""",
    "STORY": """STORY (Situation, Tension, Outline, Roles, Yield), a framework for narrative, screenplay, commercial, and scripted-content prompts.

For STORY, develop:
- SITUATION: premise, world, time, place, genre, tone, audience, and the ordinary state before change.
- TENSION: protagonist desire, obstacles, stakes, conflict, unanswered questions, and escalation.
- OUTLINE: beginning, turning points, midpoint, climax, resolution, scene or sequence order, pacing, and transitions.
- ROLES: character goals, relationships, voice, behavior, arcs, continuity, and dialogue constraints.
- YIELD: requested format, length, beat or scene requirements, emotional payoff, ending, and revision checklist.

Preserve character consistency, avoid unsupported clichés, make cause and effect clear, and match the requested medium such as prose, screenplay, commercial script, or storyboard.""",
    "RTF-3D": """RTF-3D (Role, Task, Format — Interactive 3D Extension), an implementation framework for turning a short idea into a complete Three.js browser application prompt.

For RTF-3D, expand the topic into these required sections:
- ROLE: identify the required expertise, including Three.js, JavaScript or TypeScript, browser UI, 3D scene architecture, animation, and performance optimization.
- TASK: define the interactive experience and its purpose, then describe the complete domain workflow, entities, machines, users, and state transitions.
- SCENE: specify the factory, environment, coordinate system, camera views, lighting, materials, models, labels, and visual hierarchy. Use procedural geometry or clearly named asset placeholders when external assets are unavailable.
- SIMULATION: define the data model, process stages, machine states, production sequence, timing, counters, defects, test results, and deterministic or seeded behavior.
- ANIMATION: describe conveyors, robots, tools, products, effects, transitions, interpolation, reset behavior, and how the animation stays synchronized with simulation state.
- INTERACTION: require camera orbit or inspection controls, start/pause/reset, speed control, machine selection, tooltips, accessible UI, and live status panels where appropriate.
- IMPLEMENTATION: specify project structure, entry points, Three.js modules, render loop, resize handling, resource cleanup, event handling, and how code should be delivered. State whether the result should be a single HTML file or a complete Vite project when the topic does not specify it.
- PERFORMANCE AND VALIDATION: require responsive behavior, efficient geometry and materials, instancing where useful, graceful handling of reduced hardware, and acceptance checks for the major workflow, controls, visual states, and browser errors.

Generate a standalone developer-ready prompt with concrete deliverables, ordered implementation steps, and runnable code expectations. Do not claim that unavailable 3D assets, APIs, or backend services exist; provide procedural substitutes or explicit integration points instead.""",
    "IPB": """IPB (Intent, Palette, Build, Materials, Typography, Boundaries), a framework for turning a short theme or reference idea into a complete, production-ready artistic poster prompt.

For IPB, expand the topic into these required sections:
- INTENT: poster title, subject, audience, emotional goal, cultural context, and intended use such as print, exhibition, social media, or editorial publication.
- PALETTE: dominant colors, accent colors, contrast, tonal range, seasonal references, and how color supports the subject and mood.
- BUILD: composition, aspect ratio, focal point, subject placement, scale, perspective, whitespace, visual hierarchy, background, layering, and how the viewer's eye should move through the poster.
- MATERIALS: selected artistic style, brushwork or line quality, paper or canvas surface, ink, paint, collage, torn edges, grain, halftone, print imperfections, and texture density. Combine styles only when they support the concept.
- TYPOGRAPHY: exact title and supporting copy, placement, hierarchy, lettering character, alignment, scale, legibility, and relationship between type and image. Preserve all requested text exactly and avoid inventing extra words.
- BOUNDARIES: negative prompts, anatomy and facial-detail safeguards, clean edges, no unwanted objects, no illegible or misspelled text, no watermarks, no random logos, and reference-image instructions. Include output ratio, print resolution, and adaptation guidance.

Choose the most appropriate poster style when the topic does not specify one, and explain the choice briefly. Keep the design intentional and coherent rather than adding decorative elements without purpose. Make the result a standalone image-generation prompt with a compact final production checklist covering composition, palette, materials, typography, reference handling, and output format.""",
    "VSB": """VSB (Vision, Subjects, Blocks, Behavior, Boundaries), a production framework for turning a short video concept into a detailed, standalone video-generation brief.

For VSB, expand the topic into these required sections:
- VISION: title, creative premise, duration, visual treatment, realism level, lighting, film or digital look, pacing, and intended result.
- SUBJECTS: locked descriptions of characters, vehicles, props, locations, wardrobe, identity, scale, continuity, and reference-image rules.
- BLOCKS: a complete timed scene and shot breakdown. Include timestamps that add up exactly to the requested duration, shot size, camera movement, location, action, and transitions.
- BEHAVIOR: physical motion, interactions, effects, lighting, shadows, reflections, environmental response, dialogue, and sound design. Make actions physically coherent and keep camera movement motivated by the action.
- BOUNDARIES: negative prompts, continuity locks, prohibited visual artifacts, safety or branding restrictions, and explicit checks for model failure modes.

When the topic does not provide a duration, choose a practical duration and state it. Invent useful production details that support the concept, but do not introduce named celebrities, copyrighted characters, or unrequested logos. Make the result suitable for a professional live-action or realistic video-generation workflow, with concise but complete shot-level specificity. Finish with a validation checklist confirming timing, continuity, subject identity, location consistency, and required exclusions.""",
}

BASELINE_PROMPT_TEMPLATE = """You are an expert Prompt Engineering Engine. Your sole task is to generate a comprehensive, highly optimized, and maximized \"Super Prompt\" based on a user-provided topic.
The generated Super Prompt must be fully formed, standalone, and ready for immediate deployment in an LLM.
CRITICAL STRUCTURAL REQUIREMENT: You must explicitly structure the final generated Super Prompt using the {framework_name} framework breakdown.
[INPUT TOPIC]
{subject}"""

ENHANCEMENT_PROMPT_TEMPLATE = """You are an expert prompt editor and quality reviewer.
Enhance the existing Super Prompt using the selected framework rules below.

Requirements:
- Preserve the user's original intent, named subjects, required facts, and explicit constraints.
- Improve clarity, completeness, organization, specificity, and practical usability.
- Validate that the result visibly follows the selected framework.
- Resolve contradictions, missing transitions, ambiguous requirements, and likely model failure modes.
- Add useful details only when they support the original intent; do not invent unsupported claims, brands, people, or assets.
- Apply the user's enhancement request when provided.
- Return only the complete revised Super Prompt, with no review commentary or explanation.

[SELECTED FRAMEWORK]
{framework_name}

[USER ENHANCEMENT REQUEST]
{enhancement_request}

[EXISTING SUPER PROMPT]
{existing_prompt}"""


class PromptService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.api_key = config.resolve_api_key()
        if genai is None:
            raise RuntimeError("Missing dependency: google-genai. Install it with 'pip install google-genai'.")
        self.client = genai.Client(api_key=self.api_key) if self._is_gemini_api_key(self.api_key) else None

    def key_status(self) -> dict[str, object]:
        if self.api_key and self.client is None:
            return {
                "custom_active": self.config.user_env_file.exists(),
                "mode": "invalid",
                "message": "⚠️ Invalid Gemini API key format. Use a Google AI Studio API key, not an OAuth token.",
            }
        if self.config.user_env_file.exists():
            return {
                "custom_active": True,
                "mode": "custom",
                "message": "🔒 User override active: this session is using a personal Gemini API key.",
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
            "message": "⚠️ No API key is loaded. Please paste a Gemini API key from Google AI Studio in the dashboard.",
        }

    def save_api_key(self, key: str) -> None:
        key = key.strip()
        if not self._is_gemini_api_key(key):
            raise ValueError(
                "Please use a Gemini API key from Google AI Studio, "
                "not an OAuth access token or bearer token."
            )

        with open(self.config.user_env_file, "w", encoding="utf-8") as env_file:
            env_file.write(f"GOOGLE_API_KEY={key}\n")

        os.environ["GOOGLE_API_KEY"] = key
        self.api_key = key
        self.client = genai.Client(api_key=key)

    @staticmethod
    def _is_gemini_api_key(key: str) -> bool:
        """Reject common OAuth/bearer token formats before they reach the SDK."""
        if not key or key.lower().startswith("bearer "):
            return False
        # OAuth access tokens are commonly ya29.*; JWTs contain two dots.
        if key.startswith("ya29.") or key.count(".") == 2:
            return False
        # Google may issue API keys with different prefixes. Let the API
        # validate the opaque key rather than enforcing a prefix or length.
        return bool(key)

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

    def generate_iterative(self, blueprint: ProjectBlueprint, task: WorkflowTask) -> str:
        if self.client is None:
            raise RuntimeError("No API client is active. Please save a valid Gemini key from the UI first.")
        if not blueprint.name or not blueprint.summary:
            raise ValueError("A project name and summary are required before generating a workflow prompt.")
        if not task.title or not task.description:
            raise ValueError("A workflow task title and description are required.")

        def bullets(values: list[str]) -> str:
            return "\n".join(f"- {value}" for value in values) or "- None specified"

        prompt = f"""You are a principal software engineer continuing an incremental project.
Generate one complete, implementation-ready prompt for the next development task.
Do not implement the code yourself. Return only the prompt that another coding AI should follow.

PROJECT BLUEPRINT
Name: {blueprint.name}
Summary: {blueprint.summary}
Technology stack:
{bullets(blueprint.stack)}
Architecture modules:
{bullets(blueprint.modules)}
Roadmap phases:
{bullets(blueprint.phases)}
Coding constraints:
{bullets(blueprint.constraints)}

CURRENT PHASE
{task.phase or "Not specified"}

CURRENT TASK
Title: {task.title}
Description: {task.description}
Target files:
{bullets(task.target_files)}
Acceptance criteria:
{bullets(task.acceptance_criteria)}

PROMPT REQUIREMENTS
- Inspect the existing project before changing code.
- Preserve the blueprint architecture and unrelated behavior.
- Do not invent dependencies, files, or APIs without explaining why.
- Provide complete implementation instructions with no TODO placeholders.
- Include tests, validation steps, edge cases, and integration notes.
- State assumptions and unknowns explicitly.
"""
        response = self.client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
        result = response.text
        with open(self.config.output_file, "a", encoding="utf-8") as output:
            output.write(f"--- ITERATIVE BUILD: {blueprint.name} / {task.title} ---\n{result}\n\n")
        return result

    def enhance(self, existing_prompt: str, framework: str, enhancement_request: str = "") -> str:
        if self.client is None:
            raise RuntimeError("No API client is active. Please save a valid Gemini key from the UI first.")
        if not existing_prompt.strip():
            raise ValueError("An existing Super Prompt is required before enhancement.")

        framework_details = FRAMEWORKS.get(framework, FRAMEWORKS["RACE"])
        prompt = ENHANCEMENT_PROMPT_TEMPLATE.format(
            framework_name=framework_details,
            enhancement_request=enhancement_request.strip() or "Improve the prompt using the selected framework without changing its intent.",
            existing_prompt=existing_prompt,
        )
        response = self.client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
        result = response.text
        with open(self.config.output_file, "a", encoding="utf-8") as output:
            output.write(f"--- ENHANCED FRAMEWORK: {framework} ---\n{result}\n\n")
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
            if getattr(exc, "code", None) == 401:
                return (
                    "⚠️ Gemini authentication failed. Use a Gemini API key from Google AI Studio "
                    "(usually starts with AIza), not an OAuth access token."
                )
        return str(exc)
