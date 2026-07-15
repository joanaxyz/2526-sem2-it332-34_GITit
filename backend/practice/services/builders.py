import copy
import hashlib
import json
import re
from typing import Any

from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from evaluation.services import StateBasedEvaluator
from practice.services.context import ALLOWED_KEYS as SCENARIO_CONTEXT_ALLOWED_KEYS
from practice.services.context import ScenarioContextNormalizer
from simulator.services import RepositorySnapshotService, RepositoryStateSimulator

PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


class LevelVariantBuildError(ValueError):
    pass


class StaticTemplateMaterializer:
    def render(self, value: Any, context: dict[str, Any]) -> Any:
        if isinstance(value, dict):
            return {
                self.render(key, context): self.render(item, context) for key, item in value.items()
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


class StaticLevelVariantBuilder:
    def __init__(self) -> None:
        self.simulator = RepositoryStateSimulator()
        self.snapshotter = RepositorySnapshotService()
        self.materializer = StaticTemplateMaterializer()

    def build(self, *, level, template: dict[str, Any], case: dict[str, Any], index: int):
        context = {**case, "index": index}
        case_id = str(context.get("case_id") or "").strip()
        if not case_id:
            raise LevelVariantBuildError("Authored practice case is missing case_id.")

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
        target_state_template = self.materializer.render(
            template.get("target_state_template", {}), context
        )
        if not target_state_template:
            raise LevelVariantBuildError("Practice variant has no authored target state.")
        target_state = self.simulator.normalize_state(target_state_template)
        evaluation_spec = self.materializer.render(
            template.get("evaluation_spec_template", {}),
            context,
        )
        if not evaluation_spec:
            evaluation_spec = {"completion_policy": {"mode": "state_hash"}}
        rendered_context = self.materializer.render(
            template.get("scenario_context_template", {}), context
        )
        self._assert_v3_context(rendered_context)
        scenario_context = ScenarioContextNormalizer().normalize(
            rendered_context,
            fallback_story="Reach the requested repository outcome cleanly.",
        )
        variant_model, parent_field = self._variant_model_for(level)
        variant = variant_model(
            **{parent_field: level},
            slug=self.materializer.render(template.get("slug_template", "{{case_id}}"), context),
            label=self.materializer.render(
                template.get("label_template", "Variant {{index}}"), context
            ),
            initial_state=initial_state,
            evaluation_spec=evaluation_spec,
            target_state=target_state,
            solution_commands=solution_commands,
            case_id=case_id,
            semantic_key=self.semantic_key(level=level, template=template, case_id=case_id),
            parameter_context=context,
            scenario_context=scenario_context,
            scaffold_policy=dict(
                self.materializer.render(template.get("scaffold_policy_template", {}), context)
            ),
            is_published=True,
        )
        try:
            self.validate(variant, objective_checks=getattr(level, "objective_checks", None) or [])
        except LevelVariantBuildError as exc:
            level_slug = getattr(level, "slug", "<unknown-level>")
            raise LevelVariantBuildError(
                f"{level_slug}/{case_id}: {exc}"
            ) from exc
        return variant

    def _variant_model_for(self, level):
        from adventures.models import AdventureWave, AdventureWaveVariant
        from challenges.models import ChallengeTrial, ChallengeTrialVariant

        if isinstance(level, AdventureWave):
            return AdventureWaveVariant, "wave"
        if isinstance(level, ChallengeTrial):
            return ChallengeTrialVariant, "trial"
        raise LevelVariantBuildError("Variant build expects an AdventureWave or ChallengeTrial.")

    def _assert_v3_context(self, rendered: Any) -> None:
        """Seed-time strictness: an authored scenario_context_template must be a
        v3 story context with only whitelisted keys, so nothing unpredictable ever
        reaches the frontend. An empty template is fine - the normalizer fills
        in the minimal fallback story."""
        if not rendered:
            return
        if not isinstance(rendered, dict):
            raise LevelVariantBuildError(
                f"scenario_context_template must render to an object: {rendered!r}"
            )
        if rendered.get("schema_version") != 3:
            raise LevelVariantBuildError("scenario_context_template must declare schema_version 3.")
        unknown = set(map(str, rendered)) - SCENARIO_CONTEXT_ALLOWED_KEYS
        if unknown:
            raise LevelVariantBuildError(
                f"scenario_context_template has unknown keys: {sorted(unknown)!r}"
            )

    def validate(self, variant, *, objective_checks: list | None = None) -> None:
        if not variant.initial_state:
            raise LevelVariantBuildError("Practice variant has no initial state.")
        if not variant.target_state:
            raise LevelVariantBuildError("Practice variant has no target state.")
        if not variant.scenario_context:
            raise LevelVariantBuildError("Practice variant has no scenario context.")
        flattened_context = json.dumps(variant.scenario_context, sort_keys=True).lower()
        for command in variant.solution_commands:
            if command and command.lower() in flattened_context:
                raise LevelVariantBuildError("Scenario context exposes a solution command.")
        outcome = EvaluationEngine().evaluate(
            spec=compile_evaluation_spec(variant.evaluation_spec),
            next_state=variant.target_state,
            initial_state=variant.initial_state,
            executed_commands=variant.solution_commands,
            next_state_hash=self.simulator.state_hash(variant.target_state),
            expected_state_hash=self.simulator.state_hash(variant.target_state),
        )
        if not outcome.target_matched:
            raise LevelVariantBuildError(
                f"Authored solution does not satisfy evaluation spec: {outcome.summary}"
            )
        self._validate_objective_checks(variant, checks=objective_checks or [])

    def _validate_objective_checks(self, variant, *, checks: list) -> None:
        """Every authored objective check must (a) carry a label + requirement and
        (b) be satisfied by the solution's target state, so the live checklist
        actually reaches all-green when the learner solves the level. Checks
        are authored once on the level but validated against each variant's
        own target state."""
        evaluator = StateBasedEvaluator()
        for check in checks:
            if not isinstance(check, dict):
                raise LevelVariantBuildError(f"Objective check must be an object: {check!r}")
            label = str(check.get("label", "")).strip()
            requirement = check.get("requirement") or {}
            if not label or not requirement:
                raise LevelVariantBuildError(
                    f"Objective check needs a label and a requirement: {check!r}"
                )
            result = evaluator.evaluate(
                variant.target_state,
                requirement,
                initial_state=variant.initial_state,
                executed_commands=variant.solution_commands,
            )
            if not result.target_matched:
                raise LevelVariantBuildError(
                    f"Objective check is not satisfied by the authored solution: {label!r} ({result.summary})"
                )

    def semantic_key(self, *, level, template: dict, case_id: str) -> str:
        # The "problem" payload key is frozen: it feeds the content hash that is
        # every seeded variant's stored identity (semantic_key). Renaming it would
        # re-key all existing variants on the next seed run.
        payload = {
            "problem": getattr(level, "slug", ""),
            "template": template.get("slug") or template.get("structure_key") or "variant",
            "case_id": case_id,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:40]
