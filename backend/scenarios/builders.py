from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any

from django.utils.text import slugify

from evaluation.services import StateBasedEvaluator
from scenarios.models import (
    DifficultyInstance,
    ScenarioSkillFocus,
    ScenarioVariant,
)
from simulator.services import (
    RepositorySnapshotService,
    RepositoryStateSimulator,
    normalize_command,
)
from simulator.workspace_files import WorkspaceFileError, WorkspaceFileStateService

PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


class ScenarioVariantBuildError(ValueError):
    pass


def _workspace_file_applies(file_spec: dict, *, command: str | None, command_index: int) -> bool:
    after_command = file_spec.get("after_command")
    if after_command:
        return command is not None and normalize_command(str(after_command)) == normalize_command(command)
    if "after_command_index" in file_spec:
        return int(file_spec.get("after_command_index") or 0) == command_index
    return command_index == 0


def _apply_solution_workspace_files(
    state: dict,
    workspace_files: list[dict],
    *,
    command: str | None,
    command_index: int,
) -> dict:
    workspace = WorkspaceFileStateService()
    next_state = state
    for file_spec in workspace_files:
        if not isinstance(file_spec, dict):
            raise ScenarioVariantBuildError("Workspace file creation must be an object.")
        if not _workspace_file_applies(
            file_spec,
            command=command,
            command_index=command_index,
        ):
            continue
        mode = str(file_spec.get("mode") or "create")
        writer = workspace.write_file if mode in {"write", "update", "edit"} else workspace.create_file
        next_state = writer(
            next_state,
            path=str(file_spec.get("path") or ""),
            content=str(file_spec.get("content") or ""),
        )
    return next_state


class StaticTemplateMaterializer:
    """Materialize authored static template values with a case context."""

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


class StaticCaseMaterializer:
    """Materialize authored seed cases into concrete static practice variants."""

    def __init__(self) -> None:
        self.template_materializer = StaticTemplateMaterializer()
        self.simulator = RepositoryStateSimulator()
        self.snapshotter = RepositorySnapshotService()

    def materialize_variant(
        self,
        *,
        difficulty_instance: DifficultyInstance,
        template: dict[str, Any],
        case: dict[str, Any],
        index: int,
    ) -> ScenarioVariant:
        scenario = difficulty_instance.scenario
        context = {**case, "index": index}
        case_id = str(context.get("case_id") or "").strip()
        if not case_id:
            raise ScenarioVariantBuildError("Authored practice case is missing case_id.")
        template_key = str(
            template.get("slug")
            or template.get("template_key")
            or template.get("structure_key")
            or "variant"
        )

        rendered_slug = self.template_materializer.render(template["slug_template"], context)
        rendered_label = self.template_materializer.render(template["label_template"], context)
        rendered_structure_key = self.template_materializer.render(
            template.get("structure_key", template_key),
            context,
        )
        initial_state = self.simulator.normalize_state(
            self.template_materializer.render(template.get("initial_state_template", {}), context)
        )
        solution_commands = list(
            self.template_materializer.render(
                template.get("solution_commands_template", []), context
            )
        )
        solution_workspace_files = list(
            self.template_materializer.render(
                template.get("solution_workspace_files_template", []), context
            )
        )
        if solution_workspace_files:
            context["solution_workspace_files"] = solution_workspace_files
        target_rule = self.template_materializer.render(
            template.get("target_rule_template", {}), context
        )
        target_state = self._target_state_from_solution(
            initial_state,
            solution_commands,
            workspace_files=solution_workspace_files,
        )
        target_rule = self._augment_target_rule(
            target_rule,
            scenario=scenario,
            initial_state=initial_state,
            solution_commands=solution_commands,
            target_state=target_state,
        )
        student_context = self._student_context(
            template=template,
            parameter_context=context,
            initial_state=initial_state,
            target_rule=target_rule,
        )
        slug = self._variant_slug(
            rendered_slug,
            scenario=scenario,
            difficulty=difficulty_instance.difficulty,
            case_id=case_id,
        )

        variant = ScenarioVariant(
            scenario=scenario,
            difficulty_instance=difficulty_instance,
            slug=slug,
            label=str(rendered_label)[:80],
            structure_signature=str(rendered_structure_key)[:120],
            initial_state=initial_state,
            target_rule=target_rule,
            target_state=target_state,
            expected_state_diagram=self.snapshotter.snapshot(target_state),
            solution_commands=solution_commands,
            case_id=case_id,
            semantic_key=self.semantic_key(
                difficulty=difficulty_instance.difficulty,
                template_key=template_key,
                case_id=case_id,
            ),
            parameter_context=context,
            student_context=student_context,
            is_published=True,
        )
        AuthoredVariantValidator().validate(
            variant=variant,
            difficulty_instance=difficulty_instance,
            scenario=scenario,
        )
        return variant

    def _target_state_from_solution(
        self,
        initial_state: dict,
        commands: list[str],
        *,
        workspace_files: list[dict] | None = None,
    ) -> dict:
        state = self.simulator.clone_state(initial_state)
        try:
            state = _apply_solution_workspace_files(
                state,
                workspace_files or [],
                command=None,
                command_index=0,
            )
        except WorkspaceFileError as exc:
            raise ScenarioVariantBuildError(f"Could not apply solution workspace file: {exc}") from exc

        for index, command in enumerate(commands, start=1):
            result = self.simulator.process(state, command)
            if not result.processed:
                raise ScenarioVariantBuildError(
                    f"Could not process solution command {command!r}: {result.output}"
                )
            state = result.state
            try:
                state = _apply_solution_workspace_files(
                    state,
                    workspace_files or [],
                    command=command,
                    command_index=index,
                )
            except WorkspaceFileError as exc:
                raise ScenarioVariantBuildError(
                    f"Could not apply solution workspace file after {command!r}: {exc}"
                ) from exc
        return self.simulator.normalize_state(state)

    def _augment_target_rule(
        self,
        target_rule: dict,
        *,
        scenario: ScenarioSkillFocus,
        initial_state: dict,
        solution_commands: list[str],
        target_state: dict,
    ) -> dict:
        augmented = dict(target_rule or {})
        skip_required = augmented.pop("skip_required_commands", False)
        if not skip_required:
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

    def _student_context(
        self,
        *,
        template: dict[str, Any],
        parameter_context: dict[str, Any],
        initial_state: dict,
        target_rule: dict,
    ) -> dict:
        rendered = self.template_materializer.render(
            template.get("student_context_template") or {},
            parameter_context,
        )
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
        context["required_details"] = self._merge_values(
            base.get("required_details", []),
            auto.get("required_details", []),
        )
        context["constraints"] = self._merge_strings(
            base.get("constraints", []),
            auto.get("constraints", []),
        )
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

    def _variant_slug(
        self,
        rendered_slug: Any,
        *,
        scenario: ScenarioSkillFocus,
        difficulty: str,
        case_id: str,
    ) -> str:
        base = slugify(str(rendered_slug)) or "variant"
        fallback = slugify(f"{scenario.slug}-{difficulty}-{case_id}") or "variant"
        base = base if base != "variant" else fallback
        if len(base) <= 50:
            return base
        suffix = slugify(case_id)[:18] or self._hash({"case_id": case_id})[:8]
        prefix_length = max(1, 49 - len(suffix))
        return f"{base[:prefix_length]}-{suffix}"[:50]

    def semantic_key(self, *, difficulty: str, template_key: str, case_id: str) -> str:
        key = f"{difficulty}:{slugify(template_key) or template_key}:{case_id}"
        if len(key) <= 240:
            return key
        digest = self._hash(
            {"difficulty": difficulty, "template_key": template_key, "case_id": case_id}
        )
        return f"{key[:199]}:{digest}"

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
        required_details = self.required_details(
            target_rule=target_rule, parameter_context=parameter_context
        )
        constraints = self.constraints(target_rule)
        return self.normalize(
            {
                "story": self.story(parameter_context),
                "current_state": self.current_state(initial_state),
                "required_details": required_details,
                "constraints": constraints,
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

    def required_details(
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

    def constraints(self, target_rule: dict) -> list[str]:
        latest = target_rule.get("latest_commit") or {}
        constraints = []
        for path in self._as_list(latest.get("excludes_paths")):
            constraints.append(f"Do not include {path} in the final snapshot.")
        return constraints

    def normalize(self, context: dict) -> dict:
        normalized = {
            "story": self.format_value(context.get("story", "")),
            "current_state": [
                self.format_value(item) for item in self._as_list(context.get("current_state"))
            ],
            "required_details": [
                {
                    "label": self.format_value(item.get("label")),
                    "value": self.format_value(item.get("value")),
                }
                for item in self._as_list(context.get("required_details"))
                if isinstance(item, dict)
                and item.get("label")
                and item.get("value") not in (None, "")
            ],
            "constraints": [
                self.format_value(item)
                for item in self._as_list(context.get("constraints"))
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


class AuthoredVariantValidator:
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
            raise ScenarioVariantBuildError("Practice variant difficulty does not match.")
        if variant.scenario_id and variant.scenario_id != scenario.id:
            raise ScenarioVariantBuildError("Practice variant scenario does not match.")
        if not variant.initial_state:
            raise ScenarioVariantBuildError("Practice variant has no initial state.")
        if not variant.target_rule:
            raise ScenarioVariantBuildError("State-based practice variant has no target rule.")
        if not variant.target_state:
            raise ScenarioVariantBuildError("Practice variant has no target state.")
        if not variant.expected_state_diagram:
            raise ScenarioVariantBuildError("Practice variant has no expected state diagram.")
        if not variant.student_context:
            raise ScenarioVariantBuildError("Practice variant has no student context.")
        if not variant.parameter_context:
            raise ScenarioVariantBuildError("Practice variant has no parameter context.")
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
        # State-based variants omit required_commands entirely — skip enforcement.
        if "required_commands" not in variant.target_rule:
            return
        required = set(variant.target_rule.get("required_commands", []))
        primary = set(scenario.primary_focus_commands or [scenario.focus])
        if not primary <= required:
            raise ScenarioVariantBuildError("Practice variant changed the scenario primary skill.")

    def _validate_solution(
        self,
        *,
        variant: ScenarioVariant,
        difficulty_instance: DifficultyInstance,
    ) -> None:
        simulator = RepositoryStateSimulator()
        state = simulator.clone_state(variant.initial_state)
        workspace_files = variant.parameter_context.get("solution_workspace_files", [])
        try:
            state = _apply_solution_workspace_files(
                state,
                workspace_files,
                command=None,
                command_index=0,
            )
        except WorkspaceFileError as exc:
            raise ScenarioVariantBuildError(f"Solution workspace file is invalid: {exc}") from exc

        for index, command in enumerate(variant.solution_commands, start=1):
            result = simulator.process(state, command)
            if not result.processed:
                raise ScenarioVariantBuildError(f"Solution command is not processable: {command}")
            state = result.state
            try:
                state = _apply_solution_workspace_files(
                    state,
                    workspace_files,
                    command=command,
                    command_index=index,
                )
            except WorkspaceFileError as exc:
                raise ScenarioVariantBuildError(f"Solution workspace file is invalid: {exc}") from exc

        outcome = StateBasedEvaluator().evaluate(
            state,
            variant.target_rule,
            initial_state=variant.initial_state,
            executed_commands=variant.solution_commands,
        )
        if not outcome.target_matched:
            raise ScenarioVariantBuildError(
                f"Authored solution does not satisfy target rule: {outcome.summary}"
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
