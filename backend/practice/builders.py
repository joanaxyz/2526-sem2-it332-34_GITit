import copy
import hashlib
import json
import re
from typing import Any

from adventures.models import AdventureQuest, AdventureVariant
from challenges.models import ChallengeQuest, ChallengeVariant
from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from evaluation.services import StateBasedEvaluator
from practice.context import ALLOWED_KEYS as SCENARIO_CONTEXT_ALLOWED_KEYS
from practice.context import ScenarioContextNormalizer
from simulator.services import RepositorySnapshotService, RepositoryStateSimulator
from simulator.workspace_files import WorkspaceFileError, WorkspaceFileStateService

PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


class ProblemVariantBuildError(ValueError):
    pass


class StaticTemplateMaterializer:
    def render(self, value: Any, context: dict[str, Any]) -> Any:
        if isinstance(value, dict):
            return {
                self.render(key, context): self.render(item, context)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self.render(item, context) for item in value]
        if not isinstance(value, str):
            return value

        exact = PLACEHOLDER_RE.fullmatch(value)
        if exact:
            return copy.deepcopy(context[exact.group(1)])

        def replace(match: re.Match) -> str:
            return str(context[match.group(1)])

        return PLACEHOLDER_RE.sub(replace, value)


class StaticProblemVariantBuilder:
    def __init__(self) -> None:
        self.simulator = RepositoryStateSimulator()
        self.snapshotter = RepositorySnapshotService()
        self.materializer = StaticTemplateMaterializer()

    def build(self, *, problem, template: dict[str, Any], case: dict[str, Any], index: int):
        context = {**case, "index": index}
        case_id = str(context.get("case_id") or "").strip()
        if not case_id:
            raise ProblemVariantBuildError("Authored practice case is missing case_id.")

        initial_state = self.simulator.normalize_state(
            self.materializer.render(template.get("initial_state_template", {}), context)
        )
        solution_commands = list(
            self.materializer.render(template.get("solution_commands_template", []), context)
        )
        solution_workspace_files = list(
            self.materializer.render(template.get("solution_workspace_files_template", []), context)
        )
        if solution_workspace_files:
            context["solution_workspace_files"] = solution_workspace_files
        target_state = self._target_state_from_solution(
            initial_state,
            solution_commands,
            workspace_files=solution_workspace_files,
        )
        evaluation_spec = self.materializer.render(
            template.get("evaluation_spec_template", {}),
            context,
        )
        if not evaluation_spec:
            evaluation_spec = {"completion_policy": {"mode": "state_hash"}}
        rendered_context = self.materializer.render(template.get("scenario_context_template", {}), context)
        self._assert_v3_context(rendered_context)
        scenario_context = ScenarioContextNormalizer().normalize(
            rendered_context,
            fallback_story="Reach the requested repository outcome cleanly.",
        )
        if isinstance(problem, AdventureQuest):
            variant_model = AdventureVariant
            parent_kwargs = {"adventure_quest": problem}
        elif isinstance(problem, ChallengeQuest):
            variant_model = ChallengeVariant
            parent_kwargs = {"challenge_quest": problem}
        else:
            raise ProblemVariantBuildError("Unknown problem type for variant build.")
        variant = variant_model(
            **parent_kwargs,
            slug=self.materializer.render(template.get("slug_template", "{{case_id}}"), context),
            label=self.materializer.render(template.get("label_template", "Variant {{index}}"), context),
            initial_state=initial_state,
            evaluation_spec=evaluation_spec,
            target_state=target_state,
            solution_commands=solution_commands,
            case_id=case_id,
            semantic_key=self.semantic_key(problem=problem, template=template, case_id=case_id),
            parameter_context=context,
            scenario_context=scenario_context,
            hint_set=list(self.materializer.render(template.get("hint_set_template", []), context)),
            scaffold_policy=dict(self.materializer.render(template.get("scaffold_policy_template", {}), context)),
            is_published=True,
        )
        self.validate(variant, objective_checks=getattr(problem, "objective_checks", None) or [])
        return variant

    def _assert_v3_context(self, rendered: Any) -> None:
        """Seed-time strictness: an authored scenario_context_template must be a
        v3 brief with only whitelisted keys, so nothing unpredictable ever
        reaches the frontend. An empty template is fine — the normalizer fills
        in the minimal fallback brief."""
        if not rendered:
            return
        if not isinstance(rendered, dict):
            raise ProblemVariantBuildError(f"scenario_context_template must render to an object: {rendered!r}")
        if rendered.get("schema_version") != 3:
            raise ProblemVariantBuildError("scenario_context_template must declare schema_version 3.")
        unknown = set(map(str, rendered)) - SCENARIO_CONTEXT_ALLOWED_KEYS
        if unknown:
            raise ProblemVariantBuildError(
                f"scenario_context_template has unknown keys: {sorted(unknown)!r}"
            )

    def validate(self, variant, *, objective_checks: list | None = None) -> None:
        if not variant.initial_state:
            raise ProblemVariantBuildError("Practice variant has no initial state.")
        if not variant.target_state:
            raise ProblemVariantBuildError("Practice variant has no target state.")
        if not variant.scenario_context:
            raise ProblemVariantBuildError("Practice variant has no scenario context.")
        flattened_context = json.dumps(variant.scenario_context, sort_keys=True).lower()
        for command in variant.solution_commands:
            if command and command.lower() in flattened_context:
                raise ProblemVariantBuildError("Scenario context exposes a solution command.")
        outcome = EvaluationEngine().evaluate(
            spec=compile_evaluation_spec(variant.evaluation_spec),
            next_state=variant.target_state,
            initial_state=variant.initial_state,
            executed_commands=variant.solution_commands,
            next_state_hash=self.simulator.state_hash(variant.target_state),
            expected_state_hash=self.simulator.state_hash(variant.target_state),
        )
        if not outcome.target_matched:
            raise ProblemVariantBuildError(f"Authored solution does not satisfy evaluation spec: {outcome.summary}")
        self._validate_objective_checks(variant, checks=objective_checks or [])

    def _validate_objective_checks(self, variant, *, checks: list) -> None:
        """Every authored objective check must (a) carry a label + requirement and
        (b) be satisfied by the solution's target state, so the live checklist
        actually reaches all-green when the learner solves the problem. Checks
        are authored once on the problem but validated against each variant's
        own target state."""
        evaluator = StateBasedEvaluator()
        for check in checks:
            if not isinstance(check, dict):
                raise ProblemVariantBuildError(f"Objective check must be an object: {check!r}")
            label = str(check.get("label", "")).strip()
            requirement = check.get("requirement") or {}
            if not label or not requirement:
                raise ProblemVariantBuildError(
                    f"Objective check needs a label and a requirement: {check!r}"
                )
            result = evaluator.evaluate(
                variant.target_state,
                requirement,
                initial_state=variant.initial_state,
                executed_commands=variant.solution_commands,
            )
            if not result.target_matched:
                raise ProblemVariantBuildError(
                    f"Objective check is not satisfied by the authored solution: {label!r} ({result.summary})"
                )

    def _target_state_from_solution(
        self,
        initial_state: dict,
        solution_commands: list[str],
        *,
        workspace_files: list[dict[str, Any]] | None = None,
    ) -> dict:
        state = self.simulator.clone_state(initial_state)
        try:
            state = self._apply_workspace_files(state, workspace_files or [], command_index=0)
        except WorkspaceFileError as exc:
            raise ProblemVariantBuildError(f"Could not apply solution workspace file: {exc}") from exc
        for index, command in enumerate(solution_commands, start=1):
            result = self.simulator.process(state, command)
            if not result.processed:
                raise ProblemVariantBuildError(f"Solution command is not processable: {command}")
            state = result.state
            try:
                state = self._apply_workspace_files(
                    state,
                    workspace_files or [],
                    command=command,
                    command_index=index,
                )
            except WorkspaceFileError as exc:
                raise ProblemVariantBuildError(
                    f"Could not apply solution workspace file after {command!r}: {exc}"
                ) from exc
        return self.simulator.normalize_state(state)

    def _apply_workspace_files(
        self,
        state: dict,
        workspace_files: list[dict[str, Any]],
        *,
        command: str | None = None,
        command_index: int,
    ) -> dict:
        next_state = state
        for spec in workspace_files:
            applies_after = spec.get("after_command")
            applies_after_index = spec.get("after_command_index")
            if applies_after is not None and applies_after != command:
                continue
            if applies_after_index is not None and int(applies_after_index) != command_index:
                continue
            next_state = WorkspaceFileStateService().write_file(
                next_state,
                path=spec["path"],
                content=spec.get("content", ""),
            )
        return next_state

    def semantic_key(self, *, problem, template: dict, case_id: str) -> str:
        payload = {
            "problem": getattr(problem, "slug", ""),
            "template": template.get("slug") or template.get("structure_key") or "variant",
            "case_id": case_id,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:40]
