from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProjectBlueprint:
	name: str = ""
	summary: str = ""
	stack: list[str] = field(default_factory=list)
	modules: list[str] = field(default_factory=list)
	phases: list[str] = field(default_factory=list)
	constraints: list[str] = field(default_factory=list)

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "ProjectBlueprint":
		def strings(value: Any) -> list[str]:
			if isinstance(value, list):
				return [str(item).strip() for item in value if str(item).strip()]
			return []

		return cls(
			name=str(data.get("name", "")).strip(),
			summary=str(data.get("summary", "")).strip(),
			stack=strings(data.get("stack")),
			modules=strings(data.get("modules")),
			phases=strings(data.get("phases")),
			constraints=strings(data.get("constraints")),
		)

	def to_dict(self) -> dict[str, Any]:
		return {
			"name": self.name,
			"summary": self.summary,
			"stack": self.stack,
			"modules": self.modules,
			"phases": self.phases,
			"constraints": self.constraints,
		}


@dataclass
class WorkflowTask:
	phase: str
	title: str
	description: str
	target_files: list[str] = field(default_factory=list)
	acceptance_criteria: list[str] = field(default_factory=list)

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "WorkflowTask":
		def strings(value: Any) -> list[str]:
			if isinstance(value, list):
				return [str(item).strip() for item in value if str(item).strip()]
			return []

		return cls(
			phase=str(data.get("phase", "")).strip(),
			title=str(data.get("title", "")).strip(),
			description=str(data.get("description", "")).strip(),
			target_files=strings(data.get("target_files")),
			acceptance_criteria=strings(data.get("acceptance_criteria")),
		)
