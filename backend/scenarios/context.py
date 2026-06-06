from typing import Any

LEAKY_KEYS = {
    "solution_commands",
    "solution_command",
    "exact_command_sequence",
    "evaluation_spec",
    "state_requirements",
    "process_requirements",
    "required_commands",
    "forbidden_commands",
}


class StudentContextNormalizer:
    def normalize(self, raw: dict[str, Any] | None, *, fallback_story: str = "") -> dict:
        cleaned = self._strip_leaky_keys(raw or {})
        if cleaned.get("schema_version") != 2:
            cleaned = {
                "schema_version": 2,
                "brief": {"story": fallback_story},
            }
        return self._normalize_v2(cleaned, fallback_story=fallback_story)

    def _normalize_v2(self, context: dict, *, fallback_story: str) -> dict:
        brief = context.get("brief") if isinstance(context.get("brief"), dict) else {}
        repository = (
            context.get("repository") if isinstance(context.get("repository"), dict) else {}
        )
        objective = context.get("objective") if isinstance(context.get("objective"), dict) else {}
        normalized = {
            "schema_version": 2,
            "brief": {
                "story": self._text(brief.get("story") or fallback_story),
                "task": self._text(brief.get("task")),
            },
            "repository": {
                "current_state": self._string_list(repository.get("current_state")),
            },
            "objective": {
                "outcome": self._text(objective.get("outcome")),
                "required_details": self._details(objective.get("required_details")),
            },
            "constraints": self._string_list(context.get("constraints")),
            "process_notes": self._string_list(context.get("process_notes")),
        }
        return self._drop_empty(normalized)

    def _strip_leaky_keys(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: self._strip_leaky_keys(item)
                for key, item in value.items()
                if str(key) not in LEAKY_KEYS
            }
        if isinstance(value, list):
            return [self._strip_leaky_keys(item) for item in value]
        return value

    def _details(self, value: Any) -> list[dict[str, str]]:
        details = []
        for item in self._as_list(value):
            if not isinstance(item, dict):
                continue
            label = self._text(item.get("label"))
            detail_value = self._text(item.get("value"))
            if label and detail_value:
                details.append({"label": label, "value": detail_value})
        return details

    def _string_list(self, value: Any) -> list[str]:
        return [self._text(item) for item in self._as_list(value) if self._text(item)]

    def _as_list(self, value: Any) -> list:
        if value in (None, ""):
            return []
        return value if isinstance(value, list) else [value]

    def _text(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        if isinstance(value, dict):
            return ", ".join(f"{key}: {self._text(item)}" for key, item in value.items())
        if isinstance(value, (list, tuple, set)):
            return ", ".join(self._text(item) for item in value if item not in (None, ""))
        return str(value).strip()

    def _drop_empty(self, value: Any) -> Any:
        if isinstance(value, dict):
            cleaned = {
                key: self._drop_empty(item)
                for key, item in value.items()
            }
            return {
                key: item
                for key, item in cleaned.items()
                if item not in ("", [], {}, None)
            }
        if isinstance(value, list):
            return [self._drop_empty(item) for item in value if item not in ("", [], {}, None)]
        return value
