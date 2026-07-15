"""Runtime JSON schema guards for reward-affecting command flows.

The app intentionally stores authored and runtime Git data in JSONField columns.
That flexibility is useful for curriculum authoring, but submission boundaries need
predictable shapes so malformed payloads become 4xx/validation errors instead of
runtime crashes or silent evaluator bypasses.

These validators are deliberately structural rather than semantic. Git semantics
belong in ``ClientTransitionVerifier``; this module only proves that the JSON is
safe to normalize, compare, hash, evaluate, and persist.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from common.exceptions import BadRequest

REPOSITORY_DICT_KEYS = {
    "branches",
    "head",
    "staging",
    "working_tree",
    "conflict_details",
    "remotes",
    "remote_branches",
    "upstream_tracking",
    "tags",
    "remote_tags",
    "partial_hunks",
    "replaced_commits",
    "operation_metadata",
    "remote_fixtures",
    "remote_updates",
    "config",
    "merge_abort_state",
    "merge_conflicts",
    "merge_resolutions",
    "rebase_state",
}

REPOSITORY_LIST_KEYS = {
    "commits",
    "conflicts",
    "stash_stack",
    "reflog",
    "conflict_files",
    "merge_conflict_files",
}

JSON_SCALAR_TYPES = (str, int, float, bool, type(None))
VALID_COMPLETION_MODES = {"rules", "state_hash", "rules_then_hash"}


class SchemaValidationError(ValueError):
    """Raised when authored/internal JSON has an invalid shape."""


def validate_repository_state_payload(value: Any, *, field_name: str = "repository_state") -> dict:
    """Validate a repository-state JSON object before normalization/persistence.

    The normalizer is tolerant of missing keys, so missing optional fields are
    allowed. Wrong container types are not allowed because they either crash the
    normalizer or let malformed state reach reward evaluation.
    """

    if not isinstance(value, dict):
        raise BadRequest(f"{field_name} must be an object.")

    _require_json_value(value, field_name)

    if "repository_initialized" in value and not isinstance(value.get("repository_initialized"), bool):
        raise BadRequest(f"{field_name}.repository_initialized must be a boolean.")

    for key in REPOSITORY_DICT_KEYS:
        if key in value and not isinstance(value.get(key), dict):
            raise BadRequest(f"{field_name}.{key} must be an object.")

    for key in REPOSITORY_LIST_KEYS:
        if key in value and not isinstance(value.get(key), list):
            raise BadRequest(f"{field_name}.{key} must be a list.")

    if "head" in value:
        _validate_head(value.get("head"), field_name=f"{field_name}.head")
    if "branches" in value:
        _validate_ref_map(value.get("branches"), field_name=f"{field_name}.branches")
    if "remote_branches" in value:
        _validate_ref_map(value.get("remote_branches"), field_name=f"{field_name}.remote_branches")
    if "tags" in value:
        _validate_tag_map(value.get("tags"), field_name=f"{field_name}.tags")
    if "remote_tags" in value:
        _validate_tag_map(value.get("remote_tags"), field_name=f"{field_name}.remote_tags")
    if "upstream_tracking" in value:
        _validate_string_map(value.get("upstream_tracking"), field_name=f"{field_name}.upstream_tracking")
    if "remotes" in value:
        _validate_string_map(value.get("remotes"), field_name=f"{field_name}.remotes")
    if "commits" in value:
        _validate_commits(value.get("commits"), field_name=f"{field_name}.commits")
    if "conflicts" in value:
        _validate_string_list(value.get("conflicts"), field_name=f"{field_name}.conflicts")
    if "reflog" in value:
        _validate_reflog(value.get("reflog"), field_name=f"{field_name}.reflog")
    if "stash_stack" in value:
        _validate_stash_stack(value.get("stash_stack"), field_name=f"{field_name}.stash_stack")

    return value


def validate_command_outcome_payload(value: Any, *, field_name: str = "command_outcome") -> dict:
    """Validate the neutral command outcome shape returned by submit APIs."""

    if not isinstance(value, dict):
        raise SchemaValidationError(f"{field_name} must be an object.")

    bool_fields = {"processed", "counted", "solved", "failed"}
    int_fields = {
        "previous_rules_passing",
        "rules_passing",
        "rules_delta",
        "total_rules",
        "max_counted_commands",
        "counted_command_count",
        "remaining_counted_commands",
    }
    required = bool_fields | int_fields | {"command_family"}
    missing = sorted(required - set(value))
    if missing:
        raise SchemaValidationError(f"{field_name} missing required field(s): {', '.join(missing)}.")

    for key in bool_fields:
        if not isinstance(value.get(key), bool):
            raise SchemaValidationError(f"{field_name}.{key} must be a boolean.")
    for key in int_fields:
        if not isinstance(value.get(key), int) or isinstance(value.get(key), bool):
            raise SchemaValidationError(f"{field_name}.{key} must be an integer.")
    if not isinstance(value.get("command_family"), str) or not value.get("command_family"):
        raise SchemaValidationError(f"{field_name}.command_family must be a non-empty string.")
    if value["total_rules"] < 1:
        raise SchemaValidationError(f"{field_name}.total_rules must be at least 1.")
    for key in ("previous_rules_passing", "rules_passing", "max_counted_commands", "counted_command_count", "remaining_counted_commands"):
        if value[key] < 0:
            raise SchemaValidationError(f"{field_name}.{key} must be non-negative.")
    if value["rules_delta"] != value["rules_passing"] - value["previous_rules_passing"]:
        raise SchemaValidationError(f"{field_name}.rules_delta is inconsistent.")
    expected_remaining = max(0, value["max_counted_commands"] - value["counted_command_count"])
    if value["remaining_counted_commands"] != expected_remaining:
        raise SchemaValidationError(f"{field_name}.remaining_counted_commands is inconsistent.")
    if value["rules_passing"] > value["total_rules"]:
        raise SchemaValidationError(f"{field_name}.rules_passing cannot exceed total_rules.")
    if value["previous_rules_passing"] > value["total_rules"]:
        raise SchemaValidationError(f"{field_name}.previous_rules_passing cannot exceed total_rules.")

    return value


def validate_evaluation_spec_payload(value: Any, *, field_name: str = "evaluation_spec") -> dict:
    """Validate authored evaluator JSON before compiling it.

    Unknown state-requirement keys are intentionally allowed because the content
    pipeline evolves. Known wrapper keys must still have predictable types.
    """

    if not isinstance(value, dict):
        raise SchemaValidationError(f"{field_name} must be an object.")
    _require_json_value(value, field_name, error_cls=SchemaValidationError)

    state_requirements = value.get("state_requirements", {})
    process_requirements = value.get("process_requirements", {})
    completion_policy = value.get("completion_policy", {})
    if state_requirements in (None, ""):
        state_requirements = {}
    if process_requirements in (None, ""):
        process_requirements = {}
    if completion_policy in (None, ""):
        completion_policy = {}

    if not isinstance(state_requirements, dict):
        raise SchemaValidationError(f"{field_name}.state_requirements must be an object.")
    if not isinstance(process_requirements, dict):
        raise SchemaValidationError(f"{field_name}.process_requirements must be an object.")
    if not isinstance(completion_policy, dict):
        raise SchemaValidationError(f"{field_name}.completion_policy must be an object.")

    for key in ("required_commands", "forbidden_commands"):
        _validate_string_or_string_list(
            process_requirements.get(key),
            field_name=f"{field_name}.process_requirements.{key}",
            allow_empty=True,
            error_cls=SchemaValidationError,
        )

    mode = completion_policy.get("mode", "rules")
    if mode is not None and mode != "":
        if not isinstance(mode, str):
            raise SchemaValidationError(f"{field_name}.completion_policy.mode must be a string.")
        if mode not in VALID_COMPLETION_MODES:
            raise SchemaValidationError(f"unsupported completion policy mode: {mode}")

    return value


def _validate_head(value: Any, *, field_name: str) -> None:
    if not isinstance(value, dict):
        raise BadRequest(f"{field_name} must be an object.")
    head_type = value.get("type", "branch")
    if head_type not in {"branch", "detached", "none"}:
        raise BadRequest(f"{field_name}.type must be 'branch', 'detached', or 'none'.")
    if head_type == "branch" and value.get("name") is not None and not isinstance(value.get("name"), str):
        raise BadRequest(f"{field_name}.name must be a string.")
    if value.get("target") is not None and not isinstance(value.get("target"), str):
        raise BadRequest(f"{field_name}.target must be a string or null.")


def _validate_ref_map(value: Any, *, field_name: str) -> None:
    if not isinstance(value, dict):
        raise BadRequest(f"{field_name} must be an object.")
    for key, target in value.items():
        if not isinstance(key, str) or not key:
            raise BadRequest(f"{field_name} keys must be non-empty strings.")
        if target is not None and not isinstance(target, str):
            raise BadRequest(f"{field_name}.{key} must be a string or null.")


def _validate_tag_map(value: Any, *, field_name: str) -> None:
    if not isinstance(value, dict):
        raise BadRequest(f"{field_name} must be an object.")
    for key, target in value.items():
        if not isinstance(key, str) or not key:
            raise BadRequest(f"{field_name} keys must be non-empty strings.")
        if target is None or isinstance(target, str):
            continue
        if isinstance(target, dict):
            if target.get("target") is not None and not isinstance(target.get("target"), str):
                raise BadRequest(f"{field_name}.{key}.target must be a string or null.")
            if "message" in target and target.get("message") is not None and not isinstance(target.get("message"), str):
                raise BadRequest(f"{field_name}.{key}.message must be a string or null.")
            if "annotated" in target and not isinstance(target.get("annotated"), bool):
                raise BadRequest(f"{field_name}.{key}.annotated must be a boolean.")
            continue
        raise BadRequest(f"{field_name}.{key} must be a string, object, or null.")


def _validate_string_map(value: Any, *, field_name: str) -> None:
    if not isinstance(value, dict):
        raise BadRequest(f"{field_name} must be an object.")
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise BadRequest(f"{field_name} keys must be non-empty strings.")
        if not isinstance(item, str) or not item:
            raise BadRequest(f"{field_name}.{key} must be a non-empty string.")


def _validate_commits(value: Any, *, field_name: str) -> None:
    if not isinstance(value, list):
        raise BadRequest(f"{field_name} must be a list.")
    seen: set[str] = set()
    for index, commit in enumerate(value):
        item_name = f"{field_name}[{index}]"
        if not isinstance(commit, dict):
            raise BadRequest(f"{item_name} must be an object.")
        commit_id = commit.get("id")
        if commit_id is not None:
            if not isinstance(commit_id, str) or not commit_id:
                raise BadRequest(f"{item_name}.id must be a non-empty string.")
            if commit_id in seen:
                raise BadRequest(f"{field_name} contains duplicate commit id: {commit_id}.")
            seen.add(commit_id)
        if "message" in commit and not isinstance(commit.get("message"), str):
            raise BadRequest(f"{item_name}.message must be a string.")
        if "parents" in commit:
            _validate_string_list(commit.get("parents"), field_name=f"{item_name}.parents")
        for key in ("tree", "changes", "files"):
            if key in commit and not isinstance(commit.get(key), dict):
                raise BadRequest(f"{item_name}.{key} must be an object.")
        if "order" in commit and (not isinstance(commit.get("order"), int) or isinstance(commit.get("order"), bool)):
            raise BadRequest(f"{item_name}.order must be an integer.")
        if "is_merge" in commit and not isinstance(commit.get("is_merge"), bool):
            raise BadRequest(f"{item_name}.is_merge must be a boolean.")


def _validate_reflog(value: Any, *, field_name: str) -> None:
    if not isinstance(value, list):
        raise BadRequest(f"{field_name} must be a list.")
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise BadRequest(f"{field_name}[{index}] must be an object.")
        for key in ("ref", "target", "message"):
            if key in entry and entry.get(key) is not None and not isinstance(entry.get(key), str):
                raise BadRequest(f"{field_name}[{index}].{key} must be a string or null.")


def _validate_stash_stack(value: Any, *, field_name: str) -> None:
    if not isinstance(value, list):
        raise BadRequest(f"{field_name} must be a list.")
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise BadRequest(f"{field_name}[{index}] must be an object.")
        for key in ("working_tree", "staging"):
            if key in entry and not isinstance(entry.get(key), dict):
                raise BadRequest(f"{field_name}[{index}].{key} must be an object.")
        if "conflicts" in entry:
            _validate_string_list(entry.get("conflicts"), field_name=f"{field_name}[{index}].conflicts")
        if "message" in entry and not isinstance(entry.get("message"), str):
            raise BadRequest(f"{field_name}[{index}].message must be a string.")


def _validate_string_list(value: Any, *, field_name: str) -> None:
    if not isinstance(value, list):
        raise BadRequest(f"{field_name} must be a list.")
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise BadRequest(f"{field_name}[{index}] must be a string.")


def _validate_string_or_string_list(
    value: Any,
    *,
    field_name: str,
    allow_empty: bool,
    error_cls: type[Exception],
) -> None:
    if value in (None, "") and allow_empty:
        return
    values = value if isinstance(value, list) else [value]
    for index, item in enumerate(values):
        if not isinstance(item, str) or (not item.strip() and not allow_empty):
            suffix = f"[{index}]" if isinstance(value, list) else ""
            raise error_cls(f"{field_name}{suffix} must be a string.")


def _require_json_value(value: Any, field_name: str, *, error_cls: type[Exception] = BadRequest) -> None:
    if isinstance(value, JSON_SCALAR_TYPES):
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise error_cls(f"{field_name} keys must be strings.")
            _require_json_value(item, f"{field_name}.{key}", error_cls=error_cls)
        return
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _require_json_value(item, f"{field_name}[{index}]", error_cls=error_cls)
        return
    raise error_cls(f"{field_name} contains a non-JSON value: {type(value).__name__}.")
