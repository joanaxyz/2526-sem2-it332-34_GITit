from dataclasses import dataclass, field
from typing import Any, Literal

CompletionMode = Literal["rules", "state_hash", "rules_then_hash"]


@dataclass(frozen=True)
class ProcessRequirements:
    required_commands: tuple[str, ...] = ()
    forbidden_commands: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompletionPolicy:
    mode: CompletionMode = "rules"


@dataclass(frozen=True)
class EvaluationSpec:
    state_requirements: dict[str, Any] = field(default_factory=dict)
    process_requirements: ProcessRequirements = field(default_factory=ProcessRequirements)
    completion_policy: CompletionPolicy = field(default_factory=CompletionPolicy)

    def as_rule_payload(self) -> dict[str, Any]:
        payload = dict(self.state_requirements)
        if self.process_requirements.required_commands:
            payload["required_commands"] = list(self.process_requirements.required_commands)
        if self.process_requirements.forbidden_commands:
            payload["forbidden_commands"] = list(self.process_requirements.forbidden_commands)
        return payload
