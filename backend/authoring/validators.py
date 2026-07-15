from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from authoring.models import ContentDefinition, ContentKind
from authoring.schemas import (
    BOOK_BLOCK_TYPES,
    content_levels,
    level_trials,
    level_waves,
)
from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from simulator.services import RepositoryStateSimulator, normalize_command


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
        if definition.kind == ContentKind.LESSON:
            self._validate_lesson(definition.definition, errors)
        elif definition.kind in {ContentKind.ADVENTURE, ContentKind.CHALLENGE}:
            self._validate_playable(definition, errors, owner=definition.owner)
        else:
            errors.append(_error("kind", "Unknown content kind."))
        return ValidationResult(valid=not errors, errors=errors)

    def _validate_lesson(self, definition: dict[str, Any], errors: list[dict[str, str]]) -> None:
        pages = definition.get("pages")
        if not isinstance(pages, list) or not pages:
            errors.append(_error("definition.pages", "At least one lesson page is required."))
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

    def _validate_playable(self, content: ContentDefinition, errors: list[dict[str, str]], *, owner=None) -> None:
        self._validate_battle_stage(content.definition, errors, owner=owner)
        levels = content_levels(content.definition)
        if not levels:
            errors.append(_error("definition.levels", "At least one level is required."))
            return
        is_adventure = content.kind == ContentKind.ADVENTURE
        nested_key = "waves" if is_adventure else "trials"
        for index, level in enumerate(levels):
            path = f"definition.levels[{index}]"
            self._validate_level_meta(level, path, errors)
            problems = level_waves(level) if is_adventure else level_trials(level)
            has_nested = isinstance(level.get(nested_key), list) and any(
                isinstance(item, dict) for item in level.get(nested_key)
            )
            for p_index, problem in enumerate(problems):
                p_path = f"{path}.{nested_key}[{p_index}]" if has_nested else path
                self._validate_problem(problem, p_path, errors, owner=owner)

    def _validate_level_meta(self, level: dict[str, Any], path: str, errors: list[dict[str, str]]) -> None:
        if not str(level.get("slug") or "").strip():
            errors.append(_error(f"{path}.slug", "Level slug is required."))
        if not str(level.get("title") or "").strip():
            errors.append(_error(f"{path}.title", "Level title is required."))

    def _validate_problem(self, level: dict[str, Any], path: str, errors: list[dict[str, str]], *, owner=None) -> None:
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
            self.simulator.normalize_state(initial_state)
        except Exception as exc:
            errors.append(_error(f"{path}.initial_state", f"Invalid repository state: {exc}"))
            return
        # Command execution moved to the browser engine, which derives the target
        # DAG while authoring and submits it as `target_state`. The backend no
        # longer replays commands; it validates that the authored target satisfies
        # the evaluator. A missing target means an unchanged (read-only) solution.
        executed = [normalize_command(command) for command in solution_commands]
        authored_target = level.get("target_state")
        try:
            if isinstance(authored_target, dict) and authored_target:
                state = self.simulator.normalize_state(authored_target)
            else:
                state = self.simulator.normalize_state(initial_state)
        except Exception as exc:
            errors.append(_error(f"{path}.target_state", f"Invalid target repository state: {exc}"))
            return
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
        self._validate_variants(level, path, errors)

    def _validate_variants(self, level: dict[str, Any], path: str, errors: list[dict[str, str]]) -> None:
        """Extra test cases (compiled into rotating curriculum.Variant rows) are
        optional, but each must be a solvable problem in its own right so a retry
        never serves a broken case."""
        variants = level.get("variants")
        if variants in (None, []):
            return
        if not isinstance(variants, list):
            errors.append(_error(f"{path}.variants", "Extra test cases must be a list."))
            return
        seen: set[str] = set()
        for index, variant in enumerate(variants):
            v_path = f"{path}.variants[{index}]"
            if not isinstance(variant, dict):
                errors.append(_error(v_path, "Each test case must be an object."))
                continue
            slug = str(variant.get("slug") or "").strip()
            if slug:
                if slug in seen:
                    errors.append(_error(f"{v_path}.slug", f"Duplicate test-case slug: {slug}."))
                seen.add(slug)
            solution_commands = variant.get("solution_commands")
            if not isinstance(solution_commands, list) or not all(
                isinstance(command, str) for command in solution_commands
            ):
                errors.append(_error(f"{v_path}.solution_commands", "Solution commands must be a list of strings."))
                continue
            if not solution_commands:
                errors.append(_error(f"{v_path}.solution_commands", "At least one solution command is required."))
                continue
            initial_state = variant.get("initial_state", {})
            if not isinstance(initial_state, dict):
                errors.append(_error(f"{v_path}.initial_state", "Initial repository state must be an object."))
                continue
            try:
                normalized_initial = self.simulator.normalize_state(initial_state)
            except Exception as exc:
                errors.append(_error(f"{v_path}.initial_state", f"Invalid repository state: {exc}"))
                continue
            authored_target = variant.get("target_state")
            try:
                if isinstance(authored_target, dict) and authored_target:
                    state = self.simulator.normalize_state(authored_target)
                else:
                    state = normalized_initial
            except Exception as exc:
                errors.append(_error(f"{v_path}.target_state", f"Invalid target repository state: {exc}"))
                continue
            evaluation_spec = (
                variant.get("evaluation_spec")
                or level.get("evaluation_spec")
                or {"completion_policy": {"mode": "state_hash"}}
            )
            executed = [normalize_command(command) for command in solution_commands]
            try:
                compiled = compile_evaluation_spec(evaluation_spec)
                outcome = EvaluationEngine().evaluate(
                    spec=compiled,
                    next_state=state,
                    initial_state=normalized_initial,
                    executed_commands=executed,
                    next_state_hash=self.simulator.state_hash(state),
                    expected_state_hash=self.simulator.state_hash(state),
                )
            except Exception as exc:
                errors.append(_error(f"{v_path}.evaluation_spec", f"Evaluation spec did not compile: {exc}"))
                continue
            if not outcome.target_matched:
                errors.append(
                    _error(f"{v_path}.evaluation_spec", f"Test case does not satisfy evaluator: {outcome.summary}")
                )

    def _validate_battle_stage(self, definition: dict[str, Any], errors: list[dict[str, str]], *, owner=None) -> None:
        stage = (definition or {}).get("battle_stage")
        if stage is None:
            return
        if not isinstance(stage, dict):
            errors.append(_error("definition.battle_stage", "Battle stage must be an object."))
            return
        landing = stage.get("landing")
        if landing not in (None, {}) and not _is_normalized_rect(landing):
            errors.append(_error("definition.battle_stage.landing", "Land must be a normalized rectangle (x, y, width, height in 0..1)."))
        # The backdrop is story-world supplied client-side; no background slug to validate.


def _is_normalized_rect(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    try:
        coords = {key: float(value[key]) for key in ("x", "y", "width", "height")}
    except (KeyError, TypeError, ValueError):
        return False
    if any(not 0.0 <= coord <= 1.0 for coord in coords.values()):
        return False
    return coords["width"] > 0 and coords["height"] > 0


def _error(field: str, message: str) -> dict[str, str]:
    return {"field": field, "message": message}
