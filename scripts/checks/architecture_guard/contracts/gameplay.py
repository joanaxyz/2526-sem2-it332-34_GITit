"""Shared gameplay mutation contract-ownership architecture policy."""

from __future__ import annotations

import ast
import json
import re

from scripts.checks.architecture_guard.python_analysis import (
    python_class_field_calls,
    python_class_method_called_names,
    python_top_level_assignment_names,
    python_top_level_class_names,
)
from scripts.checks.architecture_guard.repository import (
    BACKEND,
    FRONTEND_SRC,
    PY_SUFFIXES,
    ROOT,
    TS_SUFFIXES,
    iter_files,
    rel,
)
from scripts.checks.architecture_guard.typescript_analysis import (
    TS_IMPORT_EXPORT_FROM,
    strip_ts_comments,
    ts_interface_declarations,
    ts_module_matches,
    ts_named_import_bindings,
    ts_object_method_body,
    ts_type_aliases,
)

GAMEPLAY_COMMON_SERIALIZERS = "backend/common/serializers.py"


GAMEPLAY_ADVENTURE_SERIALIZERS = "backend/adventures/serializers.py"


GAMEPLAY_CHALLENGE_SERIALIZERS = "backend/challenges/serializers.py"


GAMEPLAY_GENERATED_OPENAPI = "frontend/src/shared/api/generated/openapi.json"


GAMEPLAY_SHARED_WORKSPACE_TYPES = "frontend/src/shared/level/workspaceFileTypes.ts"


GAMEPLAY_SHARED_COMMAND_TYPES = "frontend/src/shared/level/types.ts"


GAMEPLAY_SHARED_BODY_ADAPTER = "frontend/src/shared/level-runtime/runMutationInputs.ts"


GAMEPLAY_BACKEND_VIEWS = (
    "backend/adventures/views.py",
    "backend/challenges/views.py",
)


GAMEPLAY_FRONTEND_APIS = (
    "frontend/src/features/adventures/api/adventuresApi.ts",
    "frontend/src/features/challenges/api/challengeRunsApi.ts",
)


GAMEPLAY_SHARED_SERIALIZERS = {
    "CommandSubmitSerializer",
    "WorkspaceFileSerializer",
    "WorkspaceFilePathSerializer",
    "WorkspaceFileRenameSerializer",
}


GAMEPLAY_WORKSPACE_TYPE_NAMES = {
    "CreateFileInput",
    "RenameFileInput",
    "WorkspaceFileInput",
    "WorkspaceFileRenameInput",
    "WorkspaceFileRequest",
    "WorkspaceFileRenameRequest",
}


GAMEPLAY_FRONTEND_CONTRACT_NAMES = {
    *GAMEPLAY_WORKSPACE_TYPE_NAMES,
    "CommandExecutionPayload",
}


def gameplay_mutation_frontend_violations(
    sources: dict[str, str],
) -> list[str]:
    """Reject duplicate gameplay mutation inputs outside their shared owners."""

    violations: list[str] = []
    required_paths = {
        GAMEPLAY_SHARED_WORKSPACE_TYPES,
        GAMEPLAY_SHARED_COMMAND_TYPES,
        GAMEPLAY_SHARED_BODY_ADAPTER,
        *GAMEPLAY_FRONTEND_APIS,
    }
    for missing_path in sorted(required_paths - sources.keys()):
        violations.append(f"{missing_path}: required gameplay contract owner is missing")

    for path_label, source in sources.items():
        without_comments = strip_ts_comments(source)
        declared_names = set(ts_type_aliases(without_comments)) | set(
            ts_interface_declarations(without_comments)
        )
        for name in sorted(declared_names & GAMEPLAY_WORKSPACE_TYPE_NAMES):
            if path_label != GAMEPLAY_SHARED_WORKSPACE_TYPES or name not in {
                "WorkspaceFileInput",
                "WorkspaceFileRenameInput",
            }:
                violations.append(
                    f"{path_label}: {name} duplicates or facades the shared workspace input"
                )
        if (
            path_label != GAMEPLAY_SHARED_COMMAND_TYPES
            and "CommandExecutionPayload" in declared_names
        ):
            violations.append(
                f"{path_label}: CommandExecutionPayload belongs in {GAMEPLAY_SHARED_COMMAND_TYPES}"
            )

        for match in TS_IMPORT_EXPORT_FROM.finditer(without_comments):
            if not match.group(0).lstrip().startswith("export"):
                continue
            clause = re.sub(r"^type\s+", "", match.group("clause").strip())
            canonical_reexport = clause == "*" and any(
                ts_module_matches(
                    path_label=path_label,
                    module=match.group("module"),
                    canonical_module=canonical_module,
                )
                for canonical_module in (
                    "@/shared/level/workspaceFileTypes",
                    "@/shared/level/types",
                )
            )
            named_exports: set[str] = set()
            if clause.startswith("{"):
                for item in clause.strip("{} ").split(","):
                    parts = re.split(r"\s+as\s+", re.sub(r"^type\s+", "", item.strip()))
                    named_exports.update(part.strip() for part in parts if part.strip())
            if canonical_reexport or named_exports & GAMEPLAY_FRONTEND_CONTRACT_NAMES:
                violations.append(
                    f"{path_label}: gameplay contract type re-export facades are forbidden"
                )

        if path_label in GAMEPLAY_FRONTEND_APIS:
            if "ApiRequestBody" in without_comments or re.search(
                r"\bas\s+ApiRequestBody\b", without_comments
            ):
                violations.append(
                    f"{path_label}: gameplay API bodies must use the shared generated adapter"
                )
            helpers = {
                "commandSubmitBody",
                "workspaceFileBody",
                "workspaceFileRenameBody",
            }
            imported_helpers = ts_named_import_bindings(
                without_comments,
                path_label=path_label,
                module="@/shared/level-runtime/runMutationInputs",
                exported_names=helpers,
            )
            if imported_helpers != helpers:
                violations.append(
                    f"{path_label}: gameplay API must import the exact shared body adapters"
                )
            expected_method_adapters = {
                "submitCommand": "commandSubmitBody",
                "createFile": "workspaceFileBody",
                "writeFile": "workspaceFileBody",
                "renameFile": "workspaceFileRenameBody",
            }
            for method_name, helper in expected_method_adapters.items():
                method_body = ts_object_method_body(without_comments, method_name)
                if method_body is None or not re.search(
                    rf"\bbody\s*:\s*{re.escape(helper)}\s*\(", method_body
                ):
                    violations.append(f"{path_label}: {method_name} body must delegate to {helper}")
        elif path_label == GAMEPLAY_SHARED_BODY_ADAPTER:
            for schema_name in (
                "CommandSubmit",
                "WorkspaceFile",
                "WorkspaceFileRename",
            ):
                if f"ApiSchemas['{schema_name}']" not in without_comments:
                    violations.append(
                        f"{path_label}: shared adapter must return generated {schema_name}"
                    )
        elif path_label == GAMEPLAY_SHARED_WORKSPACE_TYPES:
            expected_names = {"WorkspaceFileInput", "WorkspaceFileRenameInput"}
            if not expected_names.issubset(declared_names):
                violations.append(
                    f"{path_label}: canonical workspace input declarations are incomplete"
                )
            for schema_name in ("WorkspaceFile", "WorkspaceFileRename"):
                if f"ApiSchemas['{schema_name}']" not in without_comments:
                    violations.append(
                        f"{path_label}: workspace inputs must refine generated {schema_name}"
                    )
        elif path_label == GAMEPLAY_SHARED_COMMAND_TYPES and (
            "CommandExecutionPayload" not in declared_names
            or "ApiSchemas['ClientCommandExecution']" not in without_comments
        ):
            violations.append(
                f"{path_label}: CommandExecutionPayload must refine generated "
                "ClientCommandExecution"
            )
    return violations


def gameplay_mutation_openapi_violations(schema: dict) -> list[str]:
    """Keep both gameplay modes on one exact generated request family."""

    violations: list[str] = []
    schemas = schema.get("components", {}).get("schemas", {})
    expected_components = {
        "CommandSubmit": {
            "required": ["command", "execution"],
            "properties": {
                "command": {"type": "string", "maxLength": 500},
                "execution": {"$ref": "#/components/schemas/ClientCommandExecution"},
            },
        },
        "WorkspaceFile": {
            "required": ["path"],
            "properties": {
                "path": {"type": "string", "maxLength": 240},
                "content": {"type": "string", "default": "", "maxLength": 20000},
            },
        },
        "WorkspaceFileRename": {
            "required": ["new_path", "path"],
            "properties": {
                "path": {"type": "string", "maxLength": 240},
                "new_path": {"type": "string", "maxLength": 240},
            },
        },
    }
    for name, expected in expected_components.items():
        component = schemas.get(name, {})
        if component.get("required") != expected["required"]:
            violations.append(f"{GAMEPLAY_GENERATED_OPENAPI}: {name} required fields must be exact")
        if component.get("properties") != expected["properties"]:
            violations.append(f"{GAMEPLAY_GENERATED_OPENAPI}: {name} properties must be exact")
    for displaced in (
        "WorkspaceFileCreate",
        "PatchedWorkspaceFile",
        "PatchedWorkspaceFileCreate",
    ):
        if displaced in schemas:
            violations.append(
                f"{GAMEPLAY_GENERATED_OPENAPI}: displaced {displaced} must stay absent"
            )

    expected_refs = {
        "post": "WorkspaceFile",
        "patch": "WorkspaceFile",
        "put": "WorkspaceFileRename",
    }
    for prefix in ("adventure-runs", "challenge-runs"):
        path = f"/api/{prefix}/{{run_id}}/files/"
        operations = schema.get("paths", {}).get(path, {})
        for method, component in expected_refs.items():
            operation = operations.get(method, {})
            request_schema = (
                operation.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            if request_schema != {"$ref": f"#/components/schemas/{component}"}:
                violations.append(
                    f"{GAMEPLAY_GENERATED_OPENAPI}: {method.upper()} {path} must use {component}"
                )
            if method == "patch" and operation.get("requestBody", {}).get("required") is not True:
                violations.append(
                    f"{GAMEPLAY_GENERATED_OPENAPI}: PATCH {path} request body must be required"
                )
        delete_parameters = operations.get("delete", {}).get("parameters", [])
        query_parameters = [
            parameter for parameter in delete_parameters if parameter.get("in") == "query"
        ]
        if query_parameters != [
            {
                "in": "query",
                "name": "path",
                "schema": {"type": "string", "maxLength": 240},
                "required": True,
            }
        ]:
            violations.append(
                f"{GAMEPLAY_GENERATED_OPENAPI}: DELETE {path} must require string query path"
            )
    return violations


def gameplay_mutation_backend_violations(sources: dict[str, str]) -> list[str]:
    """Reject secondary backend owners and noncanonical runtime serializer use."""

    violations: list[str] = []
    common_source = sources.get(GAMEPLAY_COMMON_SERIALIZERS, "")
    if not common_source:
        violations.append(
            f"{GAMEPLAY_COMMON_SERIALIZERS}: required gameplay serializer owner is missing"
        )
    common_classes = set(python_top_level_class_names(common_source))
    if not GAMEPLAY_SHARED_SERIALIZERS.issubset(common_classes):
        violations.append(
            f"{GAMEPLAY_COMMON_SERIALIZERS}: shared gameplay request serializers are incomplete"
        )
    expected_serializer_fields = {
        "CommandSubmitSerializer": {
            "command": "serializers.CharField(max_length=500)",
            "execution": "ClientCommandExecutionSerializer()",
        },
        "WorkspaceFileSerializer": {
            "path": "serializers.CharField(max_length=240)",
            "content": (
                "serializers.CharField(allow_blank=True,default='',max_length=20000,"
                "required=False,trim_whitespace=False)"
            ),
        },
        "WorkspaceFilePathSerializer": {"path": "serializers.CharField(max_length=240)"},
        "WorkspaceFileRenameSerializer": {
            "path": "serializers.CharField(max_length=240)",
            "new_path": "serializers.CharField(max_length=240)",
        },
    }
    for class_name, expected_fields in expected_serializer_fields.items():
        actual_fields = python_class_field_calls(common_source, class_name)
        if actual_fields != expected_fields:
            violations.append(f"{GAMEPLAY_COMMON_SERIALIZERS}: {class_name} fields must be exact")

    if GAMEPLAY_ADVENTURE_SERIALIZERS in sources:
        violations.append(
            f"{GAMEPLAY_ADVENTURE_SERIALIZERS}: displaced serializer module must stay deleted"
        )
    challenge_source = sources.get(GAMEPLAY_CHALLENGE_SERIALIZERS, "")
    challenge_classes = set(python_top_level_class_names(challenge_source))
    if challenge_classes != {"ChallengeRunStartSerializer"}:
        violations.append(
            f"{GAMEPLAY_CHALLENGE_SERIALIZERS}: only ChallengeRunStartSerializer "
            "may remain feature-owned"
        )
    allowed_binding_paths = {GAMEPLAY_COMMON_SERIALIZERS, *GAMEPLAY_BACKEND_VIEWS}
    for path_label, source in sorted(sources.items()):
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        definitions = set(python_top_level_class_names(source)) | set(
            python_top_level_assignment_names(source)
        )
        secondary_definitions = sorted(definitions & GAMEPLAY_SHARED_SERIALIZERS)
        if path_label != GAMEPLAY_COMMON_SERIALIZERS and secondary_definitions:
            violations.append(
                f"{path_label}: secondary gameplay serializer owner is forbidden: "
                + ", ".join(secondary_definitions)
            )
        imported_origins = {
            item.name
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            for item in node.names
        }
        facades = sorted(imported_origins & GAMEPLAY_SHARED_SERIALIZERS)
        if path_label not in allowed_binding_paths and facades:
            violations.append(
                f"{path_label}: gameplay serializer import/re-export facade is forbidden: "
                + ", ".join(facades)
            )

    expected_runtime_calls = {
        "backend/adventures/views.py": {
            ("AdventureRunSubmitCommandAPIView", "post"): "CommandSubmitSerializer",
            (
                "AdventureWorkspaceFileAPIView",
                "_mutate_file",
            ): "WorkspaceFileSerializer",
            ("AdventureWorkspaceFileAPIView", "put"): "WorkspaceFileRenameSerializer",
            ("AdventureWorkspaceFileAPIView", "delete"): "WorkspaceFilePathSerializer",
        },
        "backend/challenges/views.py": {
            ("ChallengeCommandSubmitAPIView", "post"): "CommandSubmitSerializer",
            ("ChallengeWorkspaceFileAPIView", "post"): "WorkspaceFileSerializer",
            ("ChallengeWorkspaceFileAPIView", "patch"): "WorkspaceFileSerializer",
            ("ChallengeWorkspaceFileAPIView", "put"): "WorkspaceFileRenameSerializer",
            ("ChallengeWorkspaceFileAPIView", "delete"): "WorkspaceFilePathSerializer",
        },
    }
    for view_path in GAMEPLAY_BACKEND_VIEWS:
        source = sources.get(view_path, "")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            tree = ast.Module(body=[], type_ignores=[])
        imported_from_owner = {
            item.name
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module == "common.serializers"
            for item in node.names
        }
        missing_imports = sorted(GAMEPLAY_SHARED_SERIALIZERS - imported_from_owner)
        if missing_imports:
            violations.append(
                f"{view_path}: gameplay request serializers must come from common.serializers; "
                f"missing={missing_imports}"
            )
        for (class_name, method_name), serializer_name in expected_runtime_calls[view_path].items():
            called_names = python_class_method_called_names(source, class_name, method_name)
            if called_names is None or serializer_name not in called_names:
                violations.append(
                    f"{view_path}: {class_name}.{method_name} must validate with {serializer_name}"
                )
    return violations


def check_gameplay_mutation_contract_ownership() -> list[str]:
    """Keep shared gameplay mutation contracts single-owner and generated."""

    backend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(BACKEND, PY_SUFFIXES)
        if not any(part in {"migrations", "tests"} for part in path.parts)
        and not path.name.startswith("test_")
    }
    violations = gameplay_mutation_backend_violations(backend_sources)

    frontend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(FRONTEND_SRC, TS_SUFFIXES)
    }
    violations.extend(gameplay_mutation_frontend_violations(frontend_sources))
    try:
        schema = json.loads((ROOT / GAMEPLAY_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        violations.append(f"{GAMEPLAY_GENERATED_OPENAPI}: invalid generated schema: {error}")
    else:
        violations.extend(gameplay_mutation_openapi_violations(schema))
    return violations
