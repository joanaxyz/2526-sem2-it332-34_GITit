from typing import Any

from common.collections import as_list

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

# The learner-facing story context is deliberately flat and whitelist-only so the
# frontend can render it without guessing. These fields mirror the authored
# scenario brief; they contain no answer-key or evaluation data.
ALLOWED_KEYS = {
    "schema_version",
    "story",
    "starting_point",
    "real_world_context",
    "task",
    "objective_checks",
    "expected_result",
    "details",
}
ORDERED_ALLOWED_KEYS = (
    "schema_version",
    "story",
    "starting_point",
    "real_world_context",
    "task",
    "objective_checks",
    "expected_result",
    "details",
)


class ScenarioContextNormalizer:
    def normalize(self, raw: dict[str, Any] | None, *, fallback_story: str = "") -> dict:
        cleaned = self._strip_leaky_keys(raw or {})
        if cleaned.get("schema_version") != 3:
            cleaned = {
                "schema_version": 3,
                "story": fallback_story,
            }
        cleaned = {key: cleaned[key] for key in ORDERED_ALLOWED_KEYS if key in cleaned}
        return self._normalize_v3(cleaned, fallback_story=fallback_story)

    def _normalize_v3(self, context: dict, *, fallback_story: str) -> dict:
        normalized = {
            "schema_version": 3,
            "story": self._text(context.get("story") or fallback_story),
            "starting_point": self._text(context.get("starting_point")),
            "real_world_context": self._text(context.get("real_world_context")),
            "task": self._text(context.get("task")),
            "objective_checks": self._text_list(context.get("objective_checks")),
            "expected_result": self._text(context.get("expected_result")),
            "details": self._details(context.get("details")),
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
        for item in as_list(value):
            if not isinstance(item, dict):
                continue
            label = self._text(item.get("label"))
            detail_value = self._text(item.get("value"))
            if detail_value:
                details.append({"label": label, "value": detail_value})
        return details

    def _text(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        if isinstance(value, dict):
            return ", ".join(f"{key}: {self._text(item)}" for key, item in value.items())
        if isinstance(value, (list, tuple, set)):
            return ", ".join(self._text(item) for item in value if item not in (None, ""))
        return str(value).strip()

    def _text_list(self, value: Any) -> list[str]:
        return [text for item in as_list(value) if (text := self._text(item))]

    def _drop_empty(self, value: Any) -> Any:
        if isinstance(value, dict):
            cleaned = {key: self._drop_empty(item) for key, item in value.items()}
            return {key: item for key, item in cleaned.items() if item not in ("", [], {}, None)}
        if isinstance(value, list):
            return [self._drop_empty(item) for item in value if item not in ("", [], {}, None)]
        return value
