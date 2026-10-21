import json
from pathlib import Path
from typing import Any

from workflows.models import ProjectBlueprint


class BlueprintService:
	def __init__(self, config) -> None:
		self.path = config.exe_dir / "projects" / "active_blueprint.json"

	def load(self) -> ProjectBlueprint:
		if not self.path.exists():
			return ProjectBlueprint()
		try:
			with self.path.open("r", encoding="utf-8") as blueprint_file:
				return ProjectBlueprint.from_dict(json.load(blueprint_file))
		except (OSError, json.JSONDecodeError, TypeError):
			return ProjectBlueprint()

	def save(self, data: dict[str, Any]) -> ProjectBlueprint:
		blueprint = ProjectBlueprint.from_dict(data)
		if not blueprint.name:
			raise ValueError("A project name is required.")
		if not blueprint.summary:
			raise ValueError("A project summary is required.")

		self.path.parent.mkdir(parents=True, exist_ok=True)
		with self.path.open("w", encoding="utf-8") as blueprint_file:
			json.dump(blueprint.to_dict(), blueprint_file, indent=2)
			blueprint_file.write("\n")
		return blueprint
