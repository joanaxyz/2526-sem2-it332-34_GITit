from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from assets.models import KIND_MONSTER, Asset
from authoring.models import ContentDefinition, ContentKind
from authoring.schemas import BOOK_BLOCK_TYPES, content_levels
from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from simulator.services import RepositoryStateSimulator


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[dict[str, str]]


class ContentDefinitionValidator:
    def __init__(self) -> None:
        self.simulator = RepositoryStateSimulator()

    def validate(self, definition: ContentDefinition) -> ValidationResult:
        errors: list[dict[str, str]] = []
        if not definition.title.strip():
            errors.append(_error("title", "Title is required."))
        if definition.kind == ContentKind.TOME:
            self._validate_tome(definition.definition, errors)
        elif definition.kind in {ContentKind.ADVENTURE, ContentKind.CHALLENGE}:
            self._validate_playable(definition, errors)
        else:
            errors.append(_error("kind", "Unknown content kind."))
        return ValidationResult(valid=not errors, errors=errors)

    def _validate_tome(self, definition: dict[str, Any], errors: list[dict[str, str]]) -> None:
        pages = definition.get("pages")
        if not isinstance(pages, list) or not pages:
            errors.append(_error("definition.pages", "At least one tome page is required."))
            return
        for page_index, page in enumerate(pages):
            path = f"definition.pages[{page_index}]"
            if not isinstance(page, dict):
                errors.append(_error(path, "Page must be an object."))
                continue
            if not str(page.get("title") or page.get("heading") or "").strip():
                errors.append(_error(f"{path}.title", "Page title or heading is required."))
            blocks = page.get("blocks", [])
            if not isinstance(blocks, list):
                errors.append(_error(f"{path}.blocks", "Page blocks must be a list."))
                continue
            for block_index, block in enumerate(blocks):
                if not isinstance(block, dict):
                    errors.append(_error(f"{path}.blocks[{block_index}]", "Block must be an object."))
                    continue
                block_type = block.get("type")
                if block_type not in BOOK_BLOCK_TYPES:
                    errors.append(
                        _error(
                            f"{path}.blocks[{block_index}].type",
                            f"Unsupported book block type: {block_type!r}.",
                        )
                    )

    def _validate_playable(self, content: ContentDefinition, errors: list[dict[str, str]]) -> None:
        levels = content_levels(content.definition)
        if not levels:
            errors.append(_error("definition.levels", "At least one level is required."))
            return
        for index, level in enumerate(levels):
            self._validate_level(level, f"definition.levels[{index}]", errors)

    def _validate_level(self, level: dict[str, Any], path: str, errors: list[dict[str, str]]) -> None:
        if not str(level.get("slug") or "").strip():
            errors.append(_error(f"{path}.slug", "Level slug is required."))
        if not str(level.get("title") or "").strip():
            errors.append(_error(f"{path}.title", "Level title is required."))
        solution_commands = level.get("solution_commands")
        if not isinstance(solution_commands, list) or not all(isinstance(command, str) for command in solution_commands):
            errors.append(_error(f"{path}.solution_commands", "Solution commands must be a list of strings."))
            return
        if not solution_commands:
            errors.append(_error(f"{path}.solution_commands", "At least one solution command is required."))
            return
        initial_state = level.get("initial_state", {})
        if not isinstance(initial_state, dict):
            errors.append(_error(f"{path}.initial_state", "Initial repository state must be an object."))
            return
        try:
            state = self.simulator.normalize_state(initial_state)
        except Exception as exc:
            errors.append(_error(f"{path}.initial_state", f"Invalid repository state: {exc}"))
            return
        executed: list[str] = []
        for command_index, command in enumerate(solution_commands):
            result = self.simulator.process(state, command)
            if not result.processed:
                errors.append(
                    _error(
                        f"{path}.solution_commands[{command_index}]",
                        f"Solution command is not supported: {command}",
                    )
                )
                return
            executed.append(result.normalized_command)
            state = self.simulator.normalize_state(result.state)
        evaluation_spec = level.get("evaluation_spec") or {"completion_policy": {"mode": "state_hash"}}
        if not isinstance(evaluation_spec, dict):
            errors.append(_error(f"{path}.evaluation_spec", "Evaluation spec must be an object."))
            return
        try:
            compiled = compile_evaluation_spec(evaluation_spec)
            outcome = EvaluationEngine().evaluate(
                spec=compiled,
                next_state=state,
                initial_state=self.simulator.normalize_state(initial_state),
                executed_commands=executed,
                next_state_hash=self.simulator.state_hash(state),
                expected_state_hash=self.simulator.state_hash(state),
            )
        except Exception as exc:
            errors.append(_error(f"{path}.evaluation_spec", f"Evaluation spec did not compile: {exc}"))
            return
        if not outcome.target_matched:
            errors.append(_error(f"{path}.evaluation_spec", f"Solution does not satisfy evaluator: {outcome.summary}"))
        self._validate_monsters(level, path, errors)

    def _validate_monsters(self, level: dict[str, Any], path: str, errors: list[dict[str, str]]) -> None:
        slugs: set[str] = set()
        for row in level.get("encounter_spec") or []:
            if isinstance(row, dict) and row.get("species"):
                slugs.add(str(row["species"]))
        boss = level.get("boss_spec") or {}
        if isinstance(boss, dict) and boss.get("species"):
            slugs.add(str(boss["species"]))
        if not slugs:
            return
        existing = set(
            Asset.objects.filter(kind=KIND_MONSTER, slug__in=slugs, is_published=True).values_list("slug", flat=True)
        )
        for slug in sorted(slugs - existing):
            errors.append(_error(path, f"Unknown monster asset slug: {slug}."))


def _error(field: str, message: str) -> dict[str, str]:
    return {"field": field, "message": message}
