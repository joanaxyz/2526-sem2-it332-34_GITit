from __future__ import annotations

import copy
import hashlib
import itertools
import json
import re
import uuid
from dataclasses import dataclass
from typing import Any

from django.utils.text import slugify

from common.constants import COMPLETION_INSPECTION
from evaluation.services import InspectionEvaluator, StateBasedEvaluator
from scenarios.models import (
    DifficultyInstance,
    ScenarioGenerationBlueprint,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
)
from simulator.services import RepositorySnapshotService, RepositoryStateSimulator

PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


class ScenarioVariantBuildError(ValueError):
    pass


@dataclass(frozen=True)
class VariantCandidate:
    blueprint: ScenarioGenerationBlueprint
    parameter_context: dict[str, Any]
    candidate_fingerprint: str


class TemplateRenderer:
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


class RuntimeScenarioBuilder:
    """Create concrete playable variants from seeded blueprint values."""

    def __init__(self) -> None:
        self.renderer = TemplateRenderer()
        self.simulator = RepositoryStateSimulator()
        self.snapshotter = RepositorySnapshotService()

    def generate_variant(
        self,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        prior_session: ScenarioSession | None = None,
    ) -> ScenarioVariant:
        blueprints = list(
            difficulty_instance.generation_blueprints.filter(is_published=True).order_by(
                "sort_order",
                "id",
            )
        )
        if not blueprints:
            raise ScenarioVariantBuildError(
                "Difficulty instance has no published generation blueprint."
            )

        candidates = self._candidates(blueprints)
        if not candidates:
            raise ScenarioVariantBuildError(
                "Generation blueprints did not produce any parameter cases."
            )

        candidate = self._select_candidate(
            candidates,
            user=user,
            difficulty_instance=difficulty_instance,
            prior_session=prior_session,
        )
        generation_seed = uuid.uuid4().hex
        return self._build_variant(
            candidate,
            user=user,
            difficulty_instance=difficulty_instance,
            generation_seed=generation_seed,
        )

    def _candidates(self, blueprints: list[ScenarioGenerationBlueprint]) -> list[VariantCandidate]:
        candidates = []
        rendered_solution_sequences: dict[str, str] = {}
        for blueprint in blueprints:
            for context in self._contexts(blueprint):
                rendered_solution = self.renderer.render(
                    blueprint.solution_commands_template, context
                )
                sequence_key = json.dumps(rendered_solution, sort_keys=True)
                should_enforce_duplicate = bool(context.get("case_id"))
                if (
                    should_enforce_duplicate
                    and sequence_key in rendered_solution_sequences
                    and not context.get("duplicate_solution_waiver")
                ):
                    raise ScenarioVariantBuildError(
                        "Generation blueprints produced duplicate solution command sequences "
                        f"for {context.get('case_id', 'unknown')} and {rendered_solution_sequences[sequence_key]}."
                    )
                if should_enforce_duplicate:
                    rendered_solution_sequences.setdefault(
                        sequence_key, str(context.get("case_id", "unknown"))
                    )
                stable_payload = {
                    "blueprint_signature": blueprint.blueprint_signature,
                    "subtemplate_signature": blueprint.subtemplate_signature,
                    "parameter_context": context,
                }
                candidates.append(
                    VariantCandidate(
                        blueprint=blueprint,
                        parameter_context=context,
                        candidate_fingerprint=self._hash(stable_payload),
                    )
                )
        return candidates

    def _contexts(self, blueprint: ScenarioGenerationBlueprint) -> list[dict[str, Any]]:
        pools = blueprint.parameter_pools or {}
        if "cases" in pools:
            base_contexts = [dict(item) for item in pools["cases"]]
        else:
            base_contexts = [{}]
            for key, values in pools.items():
                base_contexts = [
                    {**context, key: value}
                    for context, value in itertools.product(base_contexts, values)
                ]

        if not base_contexts:
            return []

        generation_count = max(1, blueprint.generation_count or len(base_contexts))
        if blueprint.max_combinations:
            generation_count = min(generation_count, blueprint.max_combinations)
        return [
            {**base_contexts[index % len(base_contexts)], "index": index + 1}
            for index in range(generation_count)
        ]

    def _select_candidate(
        self,
        candidates: list[VariantCandidate],
        *,
        user,
        difficulty_instance: DifficultyInstance,
        prior_session: ScenarioSession | None,
    ) -> VariantCandidate:
        attempt_count = ScenarioSession.objects.filter(
            user=user,
            difficulty_instance=difficulty_instance,
        ).count()
        offset_seed = prior_session.id if prior_session else attempt_count
        offset = offset_seed % len(candidates)
        ordered = candidates[offset:] + candidates[:offset]

        if prior_session is None:
            return ordered[0]

        prior_context = prior_session.variant.parameter_context or {}
        prior_fingerprint = prior_session.variant.variant_fingerprint or self._hash(
            {
                "blueprint_signature": prior_session.variant.blueprint_signature,
                "subtemplate_signature": prior_session.variant.subtemplate_signature,
                "parameter_context": prior_context,
            }
        )
        for candidate in ordered:
            if (
                candidate.parameter_context != prior_context
                and candidate.candidate_fingerprint != prior_fingerprint
            ):
                return candidate
        for candidate in ordered:
            if candidate.candidate_fingerprint != prior_fingerprint:
                return candidate
        return ordered[0]

    def _build_variant(
        self,
        candidate: VariantCandidate,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        generation_seed: str,
    ) -> ScenarioVariant:
        blueprint = candidate.blueprint
        scenario = difficulty_instance.scenario
        context = candidate.parameter_context

        rendered_slug = self.renderer.render(blueprint.slug_template, context)
        rendered_label = self.renderer.render(blueprint.label_template, context)
        rendered_subtemplate_signature = self.renderer.render(
            blueprint.subtemplate_signature,
            context,
        )
        initial_state = self.simulator.normalize_state(
            self.renderer.render(blueprint.initial_state_template, context)
        )
        solution_commands = list(
            self.renderer.render(blueprint.solution_commands_template, context)
        )
        target_rule = self.renderer.render(blueprint.target_rule_template, context)
        target_state = self._target_state_from_solution(initial_state, solution_commands)
        target_rule = self._augment_target_rule(
            target_rule,
            scenario=scenario,
            initial_state=initial_state,
            solution_commands=solution_commands,
            target_state=target_state,
            completion_type=difficulty_instance.completion_type,
        )
        expected_observations = self._expected_observations(
            difficulty_instance=difficulty_instance,
            initial_state=initial_state,
            target_rule=target_rule,
            template=self.renderer.render(blueprint.expected_observations_template or {}, context),
        )
        student_context = self._student_context(
            blueprint=blueprint,
            parameter_context=context,
            initial_state=initial_state,
            target_rule=target_rule,
        )
        fingerprint = self._hash(
            {
                "blueprint_signature": blueprint.blueprint_signature,
                "subtemplate_signature": rendered_subtemplate_signature,
                "parameter_context": context,
                "generation_seed": generation_seed,
            }
        )
        slug = self._variant_slug(rendered_slug, generation_seed)

        variant = ScenarioVariant(
            scenario=scenario,
            difficulty_instance=difficulty_instance,
            slug=slug,
            label=str(rendered_label)[:80],
            structure_signature=str(rendered_subtemplate_signature)[:120],
            initial_state=initial_state,
            target_rule=target_rule,
            target_state=target_state,
            expected_state_diagram=self.snapshotter.snapshot(target_state),
            expected_observations=expected_observations,
            solution_commands=solution_commands,
            is_generated=True,
            parameter_context=context,
            student_context=student_context,
            blueprint_signature=blueprint.blueprint_signature,
            subtemplate_signature=str(rendered_subtemplate_signature)[:160],
            variant_fingerprint=fingerprint,
            generation_seed=generation_seed,
            generated_from_blueprint=blueprint,
            is_published=True,
        )
        GeneratedVariantValidator().validate(
            variant=variant,
            difficulty_instance=difficulty_instance,
            scenario=scenario,
        )
        variant.save()
        return variant

    def _target_state_from_solution(self, initial_state: dict, commands: list[str]) -> dict:
        state = self.simulator.clone_state(initial_state)
        for command in commands:
            result = self.simulator.process(state, command)
            if not result.processed:
                raise ScenarioVariantBuildError(
                    f"Could not process solution command {command!r}: {result.output}"
                )
            state = result.state
        return self.simulator.normalize_state(state)

    def _augment_target_rule(
        self,
        target_rule: dict,
        *,
        scenario: ScenarioSkillFocus,
        initial_state: dict,
        solution_commands: list[str],
        target_state: dict,
        completion_type: str,
    ) -> dict:
        if completion_type == COMPLETION_INSPECTION:
            return target_rule

        augmented = dict(target_rule or {})
        required = list(augmented.get("required_commands", []))
        for command in scenario.primary_focus_commands or [scenario.focus]:
            if command and command not in required:
                required.append(command)
        if required:
            augmented["required_commands"] = required

        primary_commands = set(scenario.primary_focus_commands or [scenario.focus])
        if primary_commands & {"git clone", "git remote"}:
            remote_matches = dict(augmented.get("remote_url_matches", {}))
            remote_matches.setdefault(
                "origin", self._remote_url(initial_state, solution_commands, "app")
            )
            augmented["remote_url_matches"] = remote_matches

        if any(command.startswith("git commit") for command in solution_commands):
            latest_commit = self._head_commit(target_state)
            changed_paths = sorted(
                (latest_commit or {}).get("changes") or (latest_commit or {}).get("files", {})
            )
            if changed_paths:
                latest_rule = dict(augmented.get("latest_commit", {}))
                latest_rule.setdefault("branch", self._head_branch(target_state) or "main")
                latest_rule["contains_paths"] = sorted(
                    set(latest_rule.get("contains_paths", [])) | set(changed_paths)
                )
                excluded_paths = sorted(
                    set(initial_state.get("working_tree", {})) - set(changed_paths)
                )
                if excluded_paths:
                    latest_rule["excludes_paths"] = sorted(
                        set(latest_rule.get("excludes_paths", [])) | set(excluded_paths)
                    )
                augmented["latest_commit"] = latest_rule

        return augmented

    def _expected_observations(
        self,
        *,
        difficulty_instance: DifficultyInstance,
        initial_state: dict,
        target_rule: dict,
        template: dict | None = None,
    ) -> dict:
        template = template if isinstance(template, dict) else {}
        if difficulty_instance.completion_type != COMPLETION_INSPECTION:
            return template
        observations = InspectionEvaluator().observations_for(initial_state)
        must_identify = target_rule.get("must_identify", [])
        explicit_expected = {}
        for rule in target_rule.get("rules", []):
            if rule.get("type") == "inspection_answer_matches" and isinstance(
                rule.get("expected"), dict
            ):
                explicit_expected.update(rule["expected"])
        checks = {key: observations[key] for key in must_identify if key in observations}
        expected_answer = explicit_expected or checks
        return {
            **template,
            "required_commands": target_rule.get("required_commands", []),
            "repository_state_unchanged": target_rule.get("repository_state_unchanged", True),
            "checks": checks,
            "expected_answer": expected_answer,
        }

    def _student_context(
        self,
        *,
        blueprint: ScenarioGenerationBlueprint,
        parameter_context: dict[str, Any],
        initial_state: dict,
        target_rule: dict,
    ) -> dict:
        rendered = self.renderer.render(blueprint.student_context_template or {}, parameter_context)
        base = rendered if isinstance(rendered, dict) else {}
        auto = StudentContextFactory().build(
            parameter_context=parameter_context,
            initial_state=initial_state,
            target_rule=target_rule,
        )

        context = {
            **auto,
            **{key: value for key, value in base.items() if value not in (None, "", [], {})},
        }
        context["current_state"] = self._merge_strings(
            auto.get("current_state", []),
            base.get("current_state", []),
        )
        context["provided_values"] = self._merge_values(
            base.get("provided_values", []),
            auto.get("provided_values", []),
        )
        context["warnings"] = self._merge_strings(
            base.get("warnings", []),
            auto.get("warnings", []),
        )
        # Do not persist active-attempt scaffolds that reveal evaluator rules.
        # The frontend also ignores these legacy fields, but stripping them here
        # keeps newly generated variants clean.
        for hidden_section in ("requirements", "success_checklist", "inspection_suggestions"):
            context.pop(hidden_section, None)
        return StudentContextFactory().normalize(context)

    def _merge_values(self, primary: Any, fallback: Any) -> list[dict[str, str]]:
        items = []
        seen = set()
        for item in [*self._as_list(primary), *self._as_list(fallback)]:
            if not isinstance(item, dict):
                continue
            label = str(item.get("label", "")).strip()
            value = StudentContextFactory().format_value(item.get("value", ""))
            key = (label.lower(), value.lower())
            if not label or not value or key in seen:
                continue
            seen.add(key)
            items.append({"label": label, "value": value})
        return items

    def _merge_strings(self, primary: Any, fallback: Any) -> list[str]:
        values = []
        seen = set()
        for value in [*self._as_list(primary), *self._as_list(fallback)]:
            text = StudentContextFactory().format_value(value)
            key = text.lower()
            if text and key not in seen:
                seen.add(key)
                values.append(text)
        return values

    def _as_list(self, value: Any) -> list:
        if value in (None, ""):
            return []
        return value if isinstance(value, list) else [value]

    def _variant_slug(self, rendered_slug: Any, generation_seed: str) -> str:
        base = slugify(str(rendered_slug)) or "variant"
        suffix = generation_seed[:8]
        return f"{base[:41]}-{suffix}"[:50]

    def _hash(self, payload: dict) -> str:
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:40]

    def _remote_url(self, initial_state: dict, solution_commands: list[str], topic: str) -> str:
        for command in solution_commands:
            if command.startswith("git remote add origin "):
                return command.rsplit(" ", 1)[-1]
            if command.startswith("git clone "):
                parts = command.split()
                if len(parts) >= 3:
                    return parts[2]
        return initial_state.get("remotes", {}).get("origin", f"https://example.test/{topic}.git")

    def _head_branch(self, state: dict) -> str | None:
        head = state.get("head", {})
        return head.get("name") if head.get("type") == "branch" else None

    def _head_commit(self, state: dict) -> dict | None:
        head = state.get("head", {})
        commit_id = (
            state.get("branches", {}).get(head.get("name"))
            if head.get("type") == "branch"
            else head.get("target")
        )
        if not commit_id:
            return None
        return next(
            (commit for commit in state.get("commits", []) if commit["id"] == commit_id), None
        )


class StudentContextFactory:
    def build(
        self,
        *,
        parameter_context: dict[str, Any],
        initial_state: dict,
        target_rule: dict,
    ) -> dict:
        provided_values = self.provided_values(
            target_rule=target_rule, parameter_context=parameter_context
        )
        warnings = self.warnings(target_rule)
        return self.normalize(
            {
                "story": self.story(parameter_context),
                "current_state": self.current_state(initial_state),
                "provided_values": provided_values,
                "warnings": warnings,
            }
        )

    def story(self, parameter_context: dict[str, Any]) -> str:
        project = parameter_context.get("project")
        if project:
            return f"You are working in {project}. Reach the requested repository outcome cleanly."
        return "Reach the requested repository outcome cleanly."

    def current_state(self, state: dict) -> list[str]:
        items = []
        if not state.get("repository_initialized", True):
            items.append("This folder is not a Git repository yet.")
        branch = self._head_branch(state)
        if branch:
            items.append(f"You are on the {branch} branch.")
        remotes = state.get("remotes", {})
        if remotes:
            items.append(f"Configured remotes: {self.format_value(remotes)}.")
        staging = state.get("staging", {})
        if staging:
            items.append(f"Currently staged: {self.format_value(sorted(staging))}.")
        else:
            items.append("Nothing is currently staged.")
        working = state.get("working_tree", {})
        visible_working = {
            path: status for path, status in working.items() if str(status).lower() != "ignored"
        }
        ignored = sorted(
            path for path, status in working.items() if str(status).lower() == "ignored"
        )
        if visible_working:
            items.append(f"Working tree changes: {self.format_value(sorted(visible_working))}.")
        elif state.get("repository_initialized", True):
            items.append("The working tree has no visible changes.")
        if ignored:
            items.append(f"Ignored local files are present: {self.format_value(ignored)}.")
        conflicts = state.get("conflicts", [])
        if conflicts:
            items.append(f"Conflicts are present in: {self.format_value(conflicts)}.")
        return items

    def provided_values(
        self,
        *,
        target_rule: dict,
        parameter_context: dict[str, Any],
    ) -> list[dict[str, str]]:
        values = []
        latest = target_rule.get("latest_commit") or {}
        self._add(values, "Target branch", target_rule.get("head_branch") or latest.get("branch"))
        self._add(values, "Required commit message text", latest.get("message_contains"))
        self._add(values, "Target file", latest.get("contains_paths"))
        self._add(values, "File to leave out", latest.get("excludes_paths"))
        self._add(
            values,
            "File that should remain in the working tree",
            target_rule.get("working_tree_contains"),
        )
        self._add(
            values,
            "File that should be absent from the working tree",
            target_rule.get("working_tree_absent"),
        )
        self._add(values, "File that should be staged", target_rule.get("staging_contains"))
        self._add(values, "Required local branch", target_rule.get("branch_exists"))
        self._add(values, "Branch that should not exist", target_rule.get("branch_absent"))
        self._add(values, "Remote name", target_rule.get("remote_exists"))
        self._add(
            values, "Remote URL", list((target_rule.get("remote_url_matches") or {}).values())
        )
        self._add(
            values, "Upstream branch", list((target_rule.get("upstream_tracking") or {}).values())
        )
        self._add(values, "Destination folder", parameter_context.get("folder"))
        for rule in target_rule.get("rules", []):
            if rule.get("type") == "conflict_resolution_contains":
                self._add(values, "Conflict file", rule.get("path"))
                self._add(values, "Conflict resolution goal", rule.get("token"))
        return values

    def requirements(self, target_rule: dict) -> list[str]:
        items = []
        latest = target_rule.get("latest_commit") or {}
        branch = target_rule.get("head_branch") or latest.get("branch")
        if branch:
            items.append(f"End on the {branch} branch.")
        if target_rule.get("repository_initialized"):
            items.append("The folder must be a Git repository.")
        if latest:
            paths = latest.get("contains_paths") or []
            message = latest.get("message_contains") or []
            if paths:
                items.append(f"The final snapshot must include {self.format_value(paths)}.")
            if message:
                items.append(
                    f"The final snapshot message must include {self.format_value(message)}."
                )
        if target_rule.get("remote_url_matches"):
            items.append("The requested remote URL must be configured.")
        if target_rule.get("upstream_tracking"):
            items.append("The local branch must track the requested upstream branch.")
        if target_rule.get("staging_empty"):
            items.append("The staging area must be empty afterward.")
        if target_rule.get("working_tree_clean"):
            items.append("The working tree must be clean afterward.")
        for path in self._as_list(target_rule.get("working_tree_contains")):
            items.append(f"Leave {path} in the working tree.")
        for path in self._as_list(target_rule.get("working_tree_absent")):
            items.append(f"Remove or discard the working-tree change for {path}.")
        if not items:
            items.append("Reach the requested repository state.")
        return items

    def warnings(self, target_rule: dict) -> list[str]:
        latest = target_rule.get("latest_commit") or {}
        warnings = []
        for path in self._as_list(latest.get("excludes_paths")):
            warnings.append(f"Do not include {path} in the final snapshot.")
        return warnings

    def success_checklist(self, target_rule: dict) -> list[str]:
        items = []
        latest = target_rule.get("latest_commit") or {}
        branch = target_rule.get("head_branch") or latest.get("branch")
        if branch:
            items.append(f"You are on {branch}.")
        if latest:
            items.append("The required final snapshot exists.")
            for path in self._as_list(latest.get("contains_paths")):
                items.append(f"The final snapshot contains {path}.")
            for path in self._as_list(latest.get("excludes_paths")):
                items.append(f"{path} is not included in the final snapshot.")
            for message in self._as_list(latest.get("message_contains")):
                items.append(f"The final snapshot message includes {message}.")
        for remote, url in (target_rule.get("remote_url_matches") or {}).items():
            items.append(f"{remote} points to {url}.")
        for branch_name, upstream in (target_rule.get("upstream_tracking") or {}).items():
            items.append(f"{branch_name} tracks {upstream}.")
        if target_rule.get("staging_empty"):
            items.append("The staging area is empty.")
        if target_rule.get("working_tree_clean"):
            items.append("The working tree is clean.")
        for path in self._as_list(target_rule.get("working_tree_contains")):
            items.append(f"{path} is still present in the working tree.")
        for path in self._as_list(target_rule.get("working_tree_absent")):
            items.append(f"{path} is absent from the working tree.")
        return items

    def normalize(self, context: dict) -> dict:
        normalized = {
            "story": self.format_value(context.get("story", "")),
            "current_state": [
                self.format_value(item) for item in self._as_list(context.get("current_state"))
            ],
            "provided_values": [
                {
                    "label": self.format_value(item.get("label")),
                    "value": self.format_value(item.get("value")),
                }
                for item in self._as_list(context.get("provided_values"))
                if isinstance(item, dict)
                and item.get("label")
                and item.get("value") not in (None, "")
            ],
            "warnings": [
                self.format_value(item) for item in self._as_list(context.get("warnings"))
            ],
        }
        return {key: value for key, value in normalized.items() if value not in ("", [], None)}

    @staticmethod
    def format_value(value: Any) -> str:
        if value in (None, ""):
            return ""
        if isinstance(value, dict):
            return ", ".join(
                f"{key}: {StudentContextFactory.format_value(item)}" for key, item in value.items()
            )
        if isinstance(value, (list, tuple, set)):
            return ", ".join(
                StudentContextFactory.format_value(item) for item in value if item not in (None, "")
            )
        return str(value)

    def _add(self, values: list[dict[str, str]], label: str, value: Any) -> None:
        formatted = self.format_value(value)
        if formatted:
            values.append({"label": label, "value": formatted})

    def _head_branch(self, state: dict) -> str | None:
        head = state.get("head", {})
        return head.get("name") if head.get("type") == "branch" else None

    def _as_list(self, value: Any) -> list:
        if value in (None, ""):
            return []
        return value if isinstance(value, list) else [value]


class GeneratedVariantValidator:
    def validate(
        self,
        *,
        variant: ScenarioVariant,
        difficulty_instance: DifficultyInstance,
        scenario: ScenarioSkillFocus,
    ) -> None:
        if (
            variant.difficulty_instance_id
            and variant.difficulty_instance_id != difficulty_instance.id
        ):
            raise ScenarioVariantBuildError("Generated variant difficulty does not match.")
        if variant.scenario_id and variant.scenario_id != scenario.id:
            raise ScenarioVariantBuildError("Generated variant scenario does not match.")
        if not variant.initial_state:
            raise ScenarioVariantBuildError("Generated variant has no initial state.")
        if difficulty_instance.completion_type != COMPLETION_INSPECTION and not variant.target_rule:
            raise ScenarioVariantBuildError("State-based generated variant has no target rule.")
        if not variant.target_state:
            raise ScenarioVariantBuildError("Generated variant has no target state.")
        if not variant.expected_state_diagram:
            raise ScenarioVariantBuildError("Generated variant has no expected state diagram.")
        if not variant.student_context:
            raise ScenarioVariantBuildError("Generated variant has no student context.")
        if not variant.parameter_context:
            raise ScenarioVariantBuildError("Generated variant has no parameter context.")
        self._validate_primary_skill(
            variant=variant, difficulty_instance=difficulty_instance, scenario=scenario
        )
        self._validate_solution(variant=variant, difficulty_instance=difficulty_instance)
        self._validate_context_fairness(variant)

    def _validate_primary_skill(
        self,
        *,
        variant: ScenarioVariant,
        difficulty_instance: DifficultyInstance,
        scenario: ScenarioSkillFocus,
    ) -> None:
        if difficulty_instance.completion_type == COMPLETION_INSPECTION:
            return
        required = set(variant.target_rule.get("required_commands", []))
        primary = set(scenario.primary_focus_commands or [scenario.focus])
        if not primary <= required:
            raise ScenarioVariantBuildError("Generated variant changed the scenario primary skill.")

    def _validate_solution(
        self,
        *,
        variant: ScenarioVariant,
        difficulty_instance: DifficultyInstance,
    ) -> None:
        simulator = RepositoryStateSimulator()
        state = simulator.clone_state(variant.initial_state)
        for command in variant.solution_commands:
            result = simulator.process(state, command)
            if not result.processed:
                raise ScenarioVariantBuildError(f"Solution command is not processable: {command}")
            state = result.state

        if difficulty_instance.completion_type == COMPLETION_INSPECTION:
            outcome = InspectionEvaluator().evaluate(
                initial_state=variant.initial_state,
                current_state=state,
                expected_observations=variant.expected_observations,
                executed_commands=variant.solution_commands,
                submitted_answer=variant.expected_observations.get("expected_answer")
                or variant.expected_observations.get("checks"),
            )
        else:
            outcome = StateBasedEvaluator().evaluate(
                state,
                variant.target_rule,
                initial_state=variant.initial_state,
                executed_commands=variant.solution_commands,
            )
        if not outcome.target_matched:
            raise ScenarioVariantBuildError(
                f"Generated solution does not satisfy target rule: {outcome.summary}"
            )

    def _validate_context_fairness(self, variant: ScenarioVariant) -> None:
        flattened_context = json.dumps(variant.student_context, sort_keys=True).lower()
        for command in variant.solution_commands:
            if command and command.lower() in flattened_context:
                raise ScenarioVariantBuildError("Student context exposes a solution command.")
        for value in self._exact_values(variant.target_rule):
            if value.lower() not in flattened_context:
                raise ScenarioVariantBuildError(
                    f"Student context does not expose checked value {value!r}."
                )

    def _exact_values(self, target_rule: dict) -> set[str]:
        values: set[str] = set()
        latest = target_rule.get("latest_commit") or {}
        self._collect(values, target_rule.get("head_branch"))
        self._collect(values, latest.get("branch"))
        self._collect(values, latest.get("message_contains"))
        self._collect(values, latest.get("contains_paths"))
        self._collect(values, latest.get("excludes_paths"))
        self._collect(values, target_rule.get("branch_exists"))
        self._collect(values, target_rule.get("branch_absent"))
        self._collect(values, target_rule.get("working_tree_contains"))
        self._collect(values, target_rule.get("working_tree_absent"))
        self._collect(values, target_rule.get("staging_contains"))
        self._collect(values, target_rule.get("remote_exists"))
        self._collect(values, target_rule.get("remote_branch_exists"))
        self._collect(values, target_rule.get("remote_url_matches"))
        self._collect(values, target_rule.get("upstream_tracking"))
        self._collect(values, target_rule.get("remote_branch_matches_local"))
        for rule in target_rule.get("rules", []):
            if rule.get("type") == "conflict_resolution_contains":
                self._collect(values, rule.get("path"))
                self._collect(values, rule.get("token"))
            if rule.get("type", "").startswith("operation_metadata"):
                self._collect(values, rule.get("value"))
            if rule.get("type") in {
                "working_tree_contains_tokens",
                "working_tree_excludes_tokens",
                "staging_contains_tokens",
                "staging_excludes_tokens",
                "commit_changes_include_tokens",
                "commit_changes_exclude_tokens",
                "commit_tree_contains_tokens",
                "commit_tree_excludes_tokens",
            }:
                self._collect(values, rule.get("tokens"))
                self._collect(values, rule.get("paths"))
            if rule.get("type") in {
                "partial_hunks_committed",
                "partial_hunks_left_in_working_tree",
            }:
                self._collect(values, rule.get("paths"))
        return {
            value
            for value in values
            if value
            and len(value) > 1
            and not value.startswith("$")
            and not value.startswith("git ")
        }

    def _collect(self, values: set[str], value: Any) -> None:
        if value in (None, "", True, False):
            return
        if isinstance(value, dict):
            for key, item in value.items():
                self._collect(values, key)
                self._collect(values, item)
            return
        if isinstance(value, (list, tuple, set)):
            for item in value:
                self._collect(values, item)
            return
        values.add(str(value))
