"""Frontend success-response ownership analysis for Gameplay contracts."""

from __future__ import annotations

import re

from scripts.checks.architecture_guard.typescript_analysis import (
    TS_IMPORT_EXPORT_FROM,
    normalized_ts_type,
    strip_ts_comments,
    ts_balanced_brace_body,
    ts_exports_tainted_binding,
    ts_interface_declarations,
    ts_module_matches,
    ts_named_import_bindings,
    ts_namespace_import_bindings,
    ts_object_type_field_names,
    ts_reexports_all_from_module,
    ts_reexports_named_binding,
    ts_top_level_statements,
    ts_type_aliases,
)

GAMEPLAY_ADVENTURE_TYPES = "frontend/src/features/adventures/types.ts"


GAMEPLAY_CHALLENGE_TYPES = "frontend/src/features/challenges/types.ts"


GAMEPLAY_CHALLENGE_ENTRY_API = "frontend/src/features/challenges/api/challengesApi.ts"


GAMEPLAY_RESPONSE_FRONTEND_APIS = (
    "frontend/src/features/adventures/api/adventuresApi.ts",
    "frontend/src/features/challenges/api/challengeRunsApi.ts",
)


GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES = "frontend/src/shared/level/types.ts"


def _typescript_alias_source(source: str, alias_name: str) -> str:
    start = re.search(rf"(?m)^(?:export\s+)?type\s+{re.escape(alias_name)}\s*=", source)
    if start is None:
        return ""
    following = re.search(r"(?m)^(?:export\s+)?(?:type|interface|const)\s+", source[start.end() :])
    end = start.end() + following.start() if following else len(source)
    return source[start.start() : end]


def _typescript_omit_signature(source: str, alias_name: str) -> tuple[str, set[str]] | None:
    declaration = _typescript_alias_source(source, alias_name)
    opening = declaration.find("Omit<")
    if opening < 0:
        return None
    index = opening + len("Omit<")
    depth = 0
    quote: str | None = None
    comma = end = None
    for cursor in range(index, len(declaration)):
        char = declaration[cursor]
        if quote is not None:
            if char == quote and declaration[cursor - 1] != "\\":
                quote = None
            continue
        if char in {"'", '"', "`"}:
            quote = char
        elif char == "<":
            depth += 1
        elif char == ">":
            if depth == 0:
                end = cursor
                break
            depth -= 1
        elif char == "," and depth == 0 and comma is None:
            comma = cursor
    if comma is None or end is None:
        return None
    base = normalized_ts_type(declaration[index:comma])
    key_expression = declaration[comma + 1 : end].strip()
    key_alias = re.fullmatch(r"[A-Za-z_$][\w$]*", key_expression)
    if key_alias:
        key_expression = _typescript_alias_source(source, key_alias.group(0))
    keys = set(re.findall(r"['\"]([A-Za-z_$][\w$]*)['\"]", key_expression))
    return base, keys


def _typescript_omit_overlay_fields(
    source: str, alias_name: str
) -> tuple[set[str], int, str, str] | None:
    declaration = _typescript_alias_source(source, alias_name)
    opening = re.search(r">\s*&\s*\{", declaration)
    if opening is None:
        return None
    brace_index = declaration.find("{", opening.start())
    body = ts_balanced_brace_body(declaration, brace_index)
    if body is None:
        return None
    trailing = declaration[brace_index + len(body) + 2 :]
    return (
        set(ts_object_type_field_names(body)),
        len(ts_top_level_statements(body)),
        normalized_ts_type(body),
        normalized_ts_type(trailing),
    )


def _typescript_exported_object_body(source: str, object_name: str) -> str | None:
    match = re.search(
        rf"\bexport\s+const\s+{re.escape(object_name)}\s*=\s*\{{",
        source,
    )
    if match is None:
        return None
    return ts_balanced_brace_body(source, match.end() - 1)


def _typescript_object_method_bodies(object_body: str, method_name: str) -> list[str]:
    bodies: list[str] = []
    method_pattern = re.compile(
        rf"^(?:async\s+)?{re.escape(method_name)}\s*\([^)]*\)\s*\{{",
        re.S,
    )
    for member in _typescript_top_level_object_members(object_body):
        match = method_pattern.match(member)
        if match is None:
            continue
        body = ts_balanced_brace_body(member, match.end() - 1)
        if body is not None:
            bodies.append(body)
    return bodies


def _typescript_top_level_object_members(object_body: str) -> list[str]:
    members: list[str] = []
    start = 0
    braces = brackets = parentheses = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(object_body):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'", "`"}:
            quote = char
        elif char == "{":
            braces += 1
        elif char == "}":
            braces = max(0, braces - 1)
        elif char == "[":
            brackets += 1
        elif char == "]":
            brackets = max(0, brackets - 1)
        elif char == "(":
            parentheses += 1
        elif char == ")":
            parentheses = max(0, parentheses - 1)
        elif char == "," and not (braces or brackets or parentheses):
            member = object_body[start:index].strip()
            if member:
                members.append(member)
            start = index + 1
    tail = object_body[start:].strip()
    if tail:
        members.append(tail)
    return members


def _typescript_unsafe_api_object_members(
    object_body: str, owned_method_names: set[str]
) -> list[str]:
    unsafe: list[str] = []
    names = "|".join(re.escape(name) for name in sorted(owned_method_names))
    property_override = re.compile(
        rf"^(?:get|set)\s+(?:{names})\b|"
        rf"^(?:{names})\b(?!\s*\()|"
        rf"^(?:['\"](?:{names})['\"]|\[(?:[^\]]+)\])\s*[:(]",
        re.S,
    )
    for member in _typescript_top_level_object_members(object_body):
        normalized = member.lstrip()
        if normalized.startswith("...") or normalized.startswith("["):
            unsafe.append(member)
        elif property_override.match(normalized):
            unsafe.append(member)
    return unsafe


def _typescript_balanced_call_end(source: str, opening_index: int) -> int | None:
    if opening_index >= len(source) or source[opening_index] != "(":
        return None
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(opening_index, len(source)):
        char = source[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'", "`"}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _typescript_is_exact_operation_return(
    statement: str, operation: str, response_type: str | None
) -> bool:
    normalized = normalized_ts_type(statement)
    prefix = (
        f"returnapiOperationRequest<'{operation}',{response_type}>("
        if response_type is not None
        else f"returnapiOperationRequest('{operation}',"
    )
    if not normalized.startswith(prefix):
        return False
    opening_index = normalized.find("(", len("returnapiOperationRequest"))
    closing_index = _typescript_balanced_call_end(normalized, opening_index)
    return closing_index == len(normalized) - 1


def _typescript_api_binding_mutation_pattern(binding: str) -> re.Pattern[str]:
    escaped_binding = re.escape(binding)
    member = r"(?:\.\s*[A-Za-z_$][\w$]*|\[[^\]]+\])"
    assignment = (
        r"(?:\|\|=|&&=|\?\?=|\*\*=|>>>=|>>=|<<=|\+=|-=|\*=|/=|%=|"
        r"&=|\|=|\^=|=(?!=|>))"
    )
    return re.compile(
        rf"\b{escaped_binding}\s*{member}\s*{assignment}|"
        rf"\bdelete\s+{escaped_binding}\s*{member}|"
        rf"\bObject\s*\.\s*assign\s*\(\s*{escaped_binding}\b|"
        rf"\bReflect\s*\.\s*(?:set|deleteProperty)\s*\(\s*{escaped_binding}\b|"
        rf"\b(?:Object|Reflect)\s*\.\s*definePropert(?:y|ies)\s*\(\s*"
        rf"{escaped_binding}\b"
    )


def _typescript_local_api_bindings(source: str, seeds: set[str]) -> set[str]:
    bindings = set(seeds)
    assignments = list(
        re.finditer(
            r"\b(?:const|let|var)\s+(?P<alias>[A-Za-z_$][\w$]*)"
            r"(?:\s*:\s*[^=;\r\n]+)?\s*=\s*\(*\s*"
            r"(?P<value>[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\b\s*\)*",
            source,
        )
    )
    changed = True
    while changed:
        changed = False
        for match in assignments:
            if match.group("value") in bindings and match.group("alias") not in bindings:
                bindings.add(match.group("alias"))
                changed = True
    return bindings


def gameplay_response_frontend_violations(sources: dict[str, str]) -> list[str]:
    """Keep HTTP responses generated-derived and local optimism explicitly narrow."""

    violations: list[str] = []
    required_paths = {
        GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES,
        GAMEPLAY_ADVENTURE_TYPES,
        GAMEPLAY_CHALLENGE_TYPES,
        *GAMEPLAY_RESPONSE_FRONTEND_APIS,
        GAMEPLAY_CHALLENGE_ENTRY_API,
    }
    for missing_path in sorted(required_paths - sources.keys()):
        violations.append(f"{missing_path}: required gameplay response boundary is missing")

    terminal_source = strip_ts_comments(sources.get(GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES, ""))
    terminal_alias = _typescript_alias_source(terminal_source, "TerminalStep")
    if "exporttypeTerminalStep=ApiSchemas['RuntimeStepResponse']" not in normalized_ts_type(
        terminal_alias
    ):
        violations.append(
            f"{GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES}: TerminalStep must derive exactly from RuntimeStepResponse"
        )

    adventure_source = strip_ts_comments(sources.get(GAMEPLAY_ADVENTURE_TYPES, ""))
    challenge_source = strip_ts_comments(sources.get(GAMEPLAY_CHALLENGE_TYPES, ""))
    expected_omits = {
        (GAMEPLAY_ADVENTURE_TYPES, "AdventureRun"): (
            "AdventureRunWire",
            {
                "selected_level",
                "next_level",
                "story",
                "battle_stage",
                "mastery",
                "current_attempt",
                "results",
                "progress",
            },
        ),
        (GAMEPLAY_ADVENTURE_TYPES, "AdventureLevelLibraryResponse"): (
            "ApiSchemas['AdventureLevelLibraryResponse']",
            {"book", "run"},
        ),
        (GAMEPLAY_ADVENTURE_TYPES, "AdventureRunPatch"): (
            "RequireAdventureRunStatus<ApiSchemas['AdventureRunPatchResponse']>",
            {"current_attempt"},
        ),
        (GAMEPLAY_ADVENTURE_TYPES, "AdventureCommandResponse"): (
            "ApiSchemas['AdventureCommandResponse']",
            {"run", "step", "command_outcome"},
        ),
        (GAMEPLAY_CHALLENGE_TYPES, "ChallengeRunStepResponse"): (
            "ApiSchemas['ChallengeRunStepResponse']",
            {"visualization_snapshot"},
        ),
        (GAMEPLAY_CHALLENGE_TYPES, "ChallengeOptimisticStep"): (
            "ChallengeRunStepResponse",
            {"visualization_snapshot"},
        ),
        (GAMEPLAY_CHALLENGE_TYPES, "ChallengeRunResponse"): (
            "ApiSchemas['ChallengeRunResponse']",
            {
                "challenge",
                "scenario_context",
                "chapter",
                "story",
                "battle_stage",
                "variant",
                "mastery_progress",
                "policy",
                "counts",
                "scaffolding",
                "repository_state",
                "visualization",
                "expected_state",
                "steps",
                "next_difficulty",
                "sibling_levels",
                "completion",
            },
        ),
        (GAMEPLAY_CHALLENGE_TYPES, "ChallengeRun"): ("ChallengeRunResponse", {"steps"}),
        (GAMEPLAY_CHALLENGE_TYPES, "ChallengeCommandStep"): (
            "ApiSchemas['ChallengeCommandStepResponse']",
            {"visualization_snapshot"},
        ),
        (GAMEPLAY_CHALLENGE_TYPES, "ChallengeCommandResponse"): (
            "ApiSchemas['ChallengeCommandResponse']",
            {"run", "command_outcome", "step"},
        ),
        (GAMEPLAY_CHALLENGE_TYPES, "ChallengeRunUpdate"): (
            "ApiSchemas['ChallengeCommandRunResponse']",
            {
                "counts",
                "repository_state",
                "visualization",
                "mastery_progress",
                "completion",
                "next_difficulty",
                "sibling_levels",
            },
        ),
    }
    type_sources = {
        GAMEPLAY_ADVENTURE_TYPES: adventure_source,
        GAMEPLAY_CHALLENGE_TYPES: challenge_source,
    }
    response_type_owners = {
        "TerminalStep": GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES,
        "AdventureRun": GAMEPLAY_ADVENTURE_TYPES,
        "AdventureRunPatch": GAMEPLAY_ADVENTURE_TYPES,
        "AdventureCommandResponse": GAMEPLAY_ADVENTURE_TYPES,
        "AdventureLevelLibraryResponse": GAMEPLAY_ADVENTURE_TYPES,
        "ChallengeRunResponse": GAMEPLAY_CHALLENGE_TYPES,
        "ChallengeRunStepResponse": GAMEPLAY_CHALLENGE_TYPES,
        "ChallengeRun": GAMEPLAY_CHALLENGE_TYPES,
        "ChallengeStepLog": GAMEPLAY_CHALLENGE_TYPES,
        "ChallengeCommandResponse": GAMEPLAY_CHALLENGE_TYPES,
    }
    for path_label, raw_source in sources.items():
        source = strip_ts_comments(raw_source)
        declarations = set(ts_type_aliases(source)) | set(ts_interface_declarations(source))
        for type_name in sorted(declarations & response_type_owners.keys()):
            if path_label != response_type_owners[type_name]:
                violations.append(
                    f"{path_label}: secondary gameplay response type {type_name} is forbidden"
                )
        for match in re.finditer(
            r"(?m)^export\s+(?:type\s+)?\{(?P<clause>[^}]*)\}\s+from\s+"
            r"(?P<quote>['\"])(?P<module>[^'\"]+)(?P=quote)",
            source,
        ):
            exported_names = {
                re.split(r"\s+as\s+", re.sub(r"^type\s+", "", item.strip()))[0]
                for item in match.group("clause").split(",")
                if item.strip()
            }
            if exported_names & response_type_owners.keys():
                violations.append(
                    f"{path_label}: gameplay response type re-export facades are forbidden"
                )
        for match in re.finditer(
            r"(?m)^export\s+\*\s+from\s+(?P<quote>['\"])(?P<module>[^'\"]+)(?P=quote)",
            source,
        ):
            reexports_owner_star = any(
                ts_module_matches(
                    path_label=path_label,
                    module=match.group("module"),
                    canonical_module=owner_path,
                )
                for owner_path in set(response_type_owners.values())
            )
            if reexports_owner_star:
                violations.append(
                    f"{path_label}: gameplay response type re-export facades are forbidden"
                )
    for (path_label, alias_name), (
        expected_base,
        expected_keys,
    ) in expected_omits.items():
        signature = _typescript_omit_signature(type_sources[path_label], alias_name)
        if signature != (normalized_ts_type(expected_base), expected_keys):
            violations.append(
                f"{path_label}: {alias_name} must use its exact generated-derived Omit allowlist"
            )
        overlay = _typescript_omit_overlay_fields(type_sources[path_label], alias_name)
        if (
            overlay is None
            or overlay[0] != expected_keys
            or overlay[1] != len(expected_keys)
            or overlay[3]
        ):
            violations.append(
                f"{path_label}: {alias_name} overlay fields must equal its exact refinement allowlist"
            )

    adventure_wire = normalized_ts_type(
        _typescript_alias_source(adventure_source, "AdventureRunWire")
    )
    if "RequireAdventureRunStatus<ApiSchemas['AdventureRunResponse']>" not in adventure_wire:
        violations.append(
            f"{GAMEPLAY_ADVENTURE_TYPES}: AdventureRunWire must derive from AdventureRunResponse"
        )
    optimistic = normalized_ts_type(
        _typescript_alias_source(challenge_source, "ChallengeOptimisticStep")
    )
    optimistic_overlay = _typescript_omit_overlay_fields(
        challenge_source, "ChallengeOptimisticStep"
    )
    if (
        "visualization_snapshot?:never" not in optimistic
        or optimistic_overlay is None
        or optimistic_overlay[2] != "visualization_snapshot?:never"
    ):
        violations.append(
            f"{GAMEPLAY_CHALLENGE_TYPES}: optimistic steps may omit only visualization_snapshot"
        )
    step_log = normalized_ts_type(_typescript_alias_source(challenge_source, "ChallengeStepLog"))
    if "ChallengeRunStepResponse|ChallengeOptimisticStep" not in step_log:
        violations.append(
            f"{GAMEPLAY_CHALLENGE_TYPES}: ChallengeStepLog must be the exact wire/local union"
        )
    for path_label, source in type_sources.items():
        for alias_name in (
            "AdventureRun",
            "AdventureRunPatch",
            "AdventureCommandResponse",
            "ChallengeRunResponse",
            "ChallengeRunStepResponse",
            "ChallengeCommandResponse",
            "ChallengeRunUpdate",
        ):
            declaration = _typescript_alias_source(source, alias_name)
            if declaration and re.search(r"\b(?:Partial|Record)\s*<|\bkeyof\b", declaration):
                violations.append(
                    f"{path_label}: {alias_name} must not widen the generated wire contract"
                )
    for path_label, alias_name in (
        (GAMEPLAY_ADVENTURE_TYPES, "AdventureRunRefinementKeys"),
        (GAMEPLAY_CHALLENGE_TYPES, "ChallengeRunRefinementKeys"),
    ):
        declaration = _typescript_alias_source(type_sources[path_label], alias_name)
        if re.search(r"\b(?:Partial|Record)\s*<|\bkeyof\b", declaration):
            violations.append(
                f"{path_label}: {alias_name} must remain an explicit finite key allowlist"
            )

    expected_api_responses = {
        GAMEPLAY_RESPONSE_FRONTEND_APIS[0]: {
            "adventure_levels_runs_create": "AdventureRun",
            "adventure_runs_retrieve": "AdventureRun",
            "adventure_runs_level_library_create": "AdventureLevelLibraryResponse",
            "adventure_runs_submit_command_create": "AdventureCommandResponse",
            "adventure_runs_files_create": "AdventureRun",
            "adventure_runs_files_partial_update": "AdventureRun",
            "adventure_runs_files_update": "AdventureRun",
            "adventure_runs_files_destroy": "AdventureRun",
        },
        GAMEPLAY_RESPONSE_FRONTEND_APIS[1]: {
            "challenge_runs_retrieve": "ChallengeRunResponse",
            "challenge_runs_submit_command_create": "ChallengeCommandResponse",
            "challenge_runs_files_create": "ChallengeRunResponse",
            "challenge_runs_files_partial_update": "ChallengeRunResponse",
            "challenge_runs_files_update": "ChallengeRunResponse",
            "challenge_runs_files_destroy": "ChallengeRunResponse",
        },
        GAMEPLAY_CHALLENGE_ENTRY_API: {
            "challenge_trials_runs_create": "ChallengeRunResponse",
            "challenge_runs_retry_create": "ChallengeRunResponse",
        },
    }
    for path_label, operations in expected_api_responses.items():
        source = strip_ts_comments(sources.get(path_label, ""))
        normalized = normalized_ts_type(source)
        for operation, response_type in operations.items():
            expected_call = f"apiOperationRequest<'{operation}',{response_type}>"
            if expected_call not in normalized:
                violations.append(
                    f"{path_label}: {operation} must use exact response type {response_type}"
                )
        if path_label in {
            GAMEPLAY_RESPONSE_FRONTEND_APIS[1],
            GAMEPLAY_CHALLENGE_ENTRY_API,
        } and re.search(
            r"apiOperationRequest\s*<\s*['\"](?:challenge_runs_retrieve|challenge_runs_files_(?:create|partial_update|update|destroy)|challenge_trials_runs_create|challenge_runs_retry_create)['\"]\s*,\s*ChallengeRun\s*>",
            source,
        ):
            violations.append(
                f"{path_label}: client ChallengeRun must never be an HTTP response override"
            )
        if re.search(
            r"\bas\s+(?:Promise\s*<\s*)?"
            r"(?:AdventureRun|AdventureCommandResponse|AdventureLevelLibraryResponse|"
            r"ChallengeRun|ChallengeRunResponse|ChallengeCommandResponse)\b",
            source,
        ):
            violations.append(
                f"{path_label}: gameplay response return casts/intersections are forbidden"
            )
        if re.search(r"\.then\s*\(", source):
            violations.append(f"{path_label}: gameplay response adapters are forbidden")
    expected_generated_destroy_calls = {
        GAMEPLAY_RESPONSE_FRONTEND_APIS[0]: "adventure_runs_destroy",
        GAMEPLAY_CHALLENGE_ENTRY_API: "challenge_runs_destroy",
    }
    for path_label, operation in expected_generated_destroy_calls.items():
        normalized = normalized_ts_type(strip_ts_comments(sources.get(path_label, "")))
        if f"apiOperationRequest('{operation}'" not in normalized:
            violations.append(f"{path_label}: {operation} must use the generated response directly")
    expected_direct_methods = {
        GAMEPLAY_RESPONSE_FRONTEND_APIS[0]: {
            "startRun": ("adventure_levels_runs_create", "AdventureRun"),
            "getRun": ("adventure_runs_retrieve", "AdventureRun"),
            "openLevelLibrary": (
                "adventure_runs_level_library_create",
                "AdventureLevelLibraryResponse",
            ),
            "submitCommand": (
                "adventure_runs_submit_command_create",
                "AdventureCommandResponse",
            ),
            "createFile": ("adventure_runs_files_create", "AdventureRun"),
            "writeFile": ("adventure_runs_files_partial_update", "AdventureRun"),
            "renameFile": ("adventure_runs_files_update", "AdventureRun"),
            "deleteFile": ("adventure_runs_files_destroy", "AdventureRun"),
            "discardRun": ("adventure_runs_destroy", None),
        },
        GAMEPLAY_RESPONSE_FRONTEND_APIS[1]: {
            "getRun": ("challenge_runs_retrieve", "ChallengeRunResponse"),
            "submitCommand": (
                "challenge_runs_submit_command_create",
                "ChallengeCommandResponse",
            ),
            "createFile": ("challenge_runs_files_create", "ChallengeRunResponse"),
            "writeFile": (
                "challenge_runs_files_partial_update",
                "ChallengeRunResponse",
            ),
            "renameFile": ("challenge_runs_files_update", "ChallengeRunResponse"),
            "deleteFile": ("challenge_runs_files_destroy", "ChallengeRunResponse"),
        },
        GAMEPLAY_CHALLENGE_ENTRY_API: {
            "startChallengeRun": (
                "challenge_trials_runs_create",
                "ChallengeRunResponse",
            ),
            "retryChallengeRun": (
                "challenge_runs_retry_create",
                "ChallengeRunResponse",
            ),
            "discardChallengeRun": ("challenge_runs_destroy", None),
        },
    }
    expected_api_objects = {
        GAMEPLAY_RESPONSE_FRONTEND_APIS[0]: "adventuresApi",
        GAMEPLAY_RESPONSE_FRONTEND_APIS[1]: "challengeRunsApi",
        GAMEPLAY_CHALLENGE_ENTRY_API: "challengesApi",
    }
    for path_label, methods in expected_direct_methods.items():
        source = strip_ts_comments(sources.get(path_label, ""))
        object_name = expected_api_objects[path_label]
        object_body = _typescript_exported_object_body(source, object_name)
        if object_body is None or _typescript_unsafe_api_object_members(object_body, set(methods)):
            violations.append(
                f"{path_label}: {object_name} must not override owned methods through "
                "spread, computed, or property members"
            )
        for method_name, (operation, response_type) in methods.items():
            method_bodies = (
                _typescript_object_method_bodies(object_body, method_name)
                if object_body is not None
                else []
            )
            body = method_bodies[0] if len(method_bodies) == 1 else None
            returns = [
                statement
                for statement in ts_top_level_statements(body or "")
                if re.match(r"^return\b", statement)
            ]
            if (
                len(method_bodies) != 1
                or len(returns) != 1
                or not _typescript_is_exact_operation_return(returns[0], operation, response_type)
            ):
                violations.append(
                    f"{path_label}: {method_name} must directly return the exact {operation} response"
                )
            operation_calls = re.findall(
                rf"apiOperationRequest(?:\s*<\s*['\"]{re.escape(operation)}['\"][^>]*>)?"
                rf"\s*\(\s*['\"]{re.escape(operation)}['\"]",
                source,
            )
            if len(operation_calls) != 1:
                violations.append(f"{path_label}: {operation} must have exactly one owned API call")
    for path_label, raw_source in sources.items():
        source = strip_ts_comments(raw_source)
        for owner_path, object_name in expected_api_objects.items():
            owner_module_stem = owner_path.rsplit("/", maxsplit=1)[-1].removesuffix(".ts")
            if (
                path_label != owner_path
                and object_name not in source
                and owner_module_stem not in source
            ):
                continue
            seeds = {object_name} if path_label == owner_path else set()
            seeds.update(
                ts_named_import_bindings(
                    source,
                    path_label=path_label,
                    module=owner_path,
                    exported_names={object_name},
                )
            )
            namespace_bindings = ts_namespace_import_bindings(
                source,
                path_label=path_label,
                module=owner_path,
            )
            if path_label != owner_path and namespace_bindings:
                violations.append(f"{path_label}: gameplay API namespace imports are forbidden")
            seeds.update(f"{namespace}.{object_name}" for namespace in namespace_bindings)
            bindings = _typescript_local_api_bindings(source, seeds)
            export_bindings = _typescript_local_api_bindings(
                source,
                {binding for binding in bindings if "." not in binding} | namespace_bindings,
            )
            reexports_canonical_object = path_label != owner_path and (
                ts_reexports_named_binding(
                    source,
                    path_label=path_label,
                    module=owner_path,
                    exported_names={object_name},
                )
                or ts_reexports_all_from_module(
                    source,
                    path_label=path_label,
                    module=owner_path,
                )
                or any(
                    match.group(0).lstrip().startswith("export")
                    and ts_module_matches(
                        path_label=path_label,
                        module=match.group("module"),
                        canonical_module=owner_path,
                    )
                    and match.group("clause").strip().startswith("* as ")
                    for match in TS_IMPORT_EXPORT_FROM.finditer(source)
                )
                or ts_exports_tainted_binding(source, export_bindings)
                or any(
                    re.search(
                        rf"(?m)\bexport\s+default\s*\(+\s*"
                        rf"{re.escape(binding)}\s*\)+\s*;?\s*$",
                        source,
                    )
                    for binding in export_bindings
                )
                or any(
                    re.search(
                        rf"\bexport\s+(?:const|let|var)\s+{re.escape(binding)}"
                        rf"(?:\s*:\s*[^=;\r\n]+)?\s*=",
                        source,
                    )
                    for binding in export_bindings
                )
            )
            if reexports_canonical_object:
                violations.append(
                    f"{path_label}: gameplay API object re-export facades are forbidden"
                )
            if any(
                _typescript_api_binding_mutation_pattern(binding).search(source)
                for binding in bindings
            ):
                violations.append(f"{path_label}: {object_name} must not be reassigned or mutated")
    return violations
