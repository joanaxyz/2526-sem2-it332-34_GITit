from __future__ import annotations

import json
import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.contracts.gameplay import (  # noqa: E402
    GAMEPLAY_BACKEND_VIEWS,
    GAMEPLAY_CHALLENGE_SERIALIZERS,
    GAMEPLAY_COMMON_SERIALIZERS,
    GAMEPLAY_FRONTEND_APIS,
    GAMEPLAY_GENERATED_OPENAPI,
    GAMEPLAY_SHARED_BODY_ADAPTER,
    GAMEPLAY_SHARED_COMMAND_TYPES,
    GAMEPLAY_SHARED_WORKSPACE_TYPES,
    check_gameplay_mutation_contract_ownership,
    gameplay_mutation_backend_violations,
    gameplay_mutation_frontend_violations,
    gameplay_mutation_openapi_violations,
)
from scripts.checks.architecture_guard.repository import ROOT  # noqa: E402

del _TEST_IMPORT_ROOT

_FRONTEND = "front" + "end"


def test_gameplay_mutation_guard_rejects_frontend_contract_shadows_and_casts():
    violations = gameplay_mutation_frontend_violations(
        {
            f"{_FRONTEND}/src/features/example/shadows.ts": "type CreateFileInput = { path: string; content: string }\ninterface RenameFileInput { path: string; newPath: string }\ninterface CommandExecutionPayload { processed: boolean }\ntype WorkspaceFileRequest = WorkspaceFileInput\nexport type { WorkspaceFileInput } from '@/shared/level/workspaceFileTypes'\n",
            GAMEPLAY_FRONTEND_APIS[
                0
            ]: "import type { ApiRequestBody } from '@/shared/api/generated/apiTypes'\nconst body = value as ApiRequestBody<'adventure_runs_files_create'>\n",
        }
    )
    assert any("CreateFileInput" in row for row in violations)
    assert any("RenameFileInput" in row for row in violations)
    assert any("CommandExecutionPayload belongs" in row for row in violations)
    assert any("shared generated adapter" in row for row in violations)
    assert any("commandSubmitBody" in row for row in violations)
    assert any("required gameplay contract owner is missing" in row for row in violations)
    assert any("WorkspaceFileRequest" in row for row in violations)
    assert any("re-export facades are forbidden" in row for row in violations)


def test_gameplay_mutation_frontend_guard_allows_unrelated_structural_types():
    required_paths = {
        GAMEPLAY_SHARED_WORKSPACE_TYPES,
        GAMEPLAY_SHARED_COMMAND_TYPES,
        GAMEPLAY_SHARED_BODY_ADAPTER,
        *GAMEPLAY_FRONTEND_APIS,
    }
    sources = {path: (ROOT / path).read_text(encoding="utf-8") for path in required_paths}
    unrelated_path = f"{_FRONTEND}/src/features/archive/types.ts"
    sources[unrelated_path] = (
        "export type UnrelatedArchiveEntry = { path: string; content: string }\n"
    )
    violations = gameplay_mutation_frontend_violations(sources)
    assert not any(row.startswith(f"{unrelated_path}:") for row in violations)


def test_gameplay_mutation_frontend_guard_rejects_partial_adapter_delegation():
    required_paths = {
        GAMEPLAY_SHARED_WORKSPACE_TYPES,
        GAMEPLAY_SHARED_COMMAND_TYPES,
        GAMEPLAY_SHARED_BODY_ADAPTER,
        *GAMEPLAY_FRONTEND_APIS,
    }
    sources = {path: (ROOT / path).read_text(encoding="utf-8") for path in required_paths}
    adventure_api = GAMEPLAY_FRONTEND_APIS[0]
    sources[adventure_api] = sources[adventure_api].replace(
        "{ body: workspaceFileBody(input) }", "{ body: input }", 1
    )
    violations = gameplay_mutation_frontend_violations(sources)
    assert any(
        row.startswith(f"{adventure_api}:")
        and "createFile body must delegate to workspaceFileBody" in row
        for row in violations
    )


def test_gameplay_mutation_backend_guard_rejects_alternate_owners_and_runtime_use():
    source_paths = {
        GAMEPLAY_COMMON_SERIALIZERS,
        GAMEPLAY_CHALLENGE_SERIALIZERS,
        *GAMEPLAY_BACKEND_VIEWS,
    }
    sources = {path: (ROOT / path).read_text(encoding="utf-8") for path in source_paths}
    sources["backend/example/serializers.py"] = (
        "from rest_framework import serializers\nclass WorkspaceFileSerializer(serializers.Serializer):\n    path = serializers.CharField()\n"
    )
    sources["backend/example/facade.py"] = (
        "from common.serializers import CommandSubmitSerializer as SubmitContract\n"
    )
    violations = gameplay_mutation_backend_violations(sources)
    assert any("secondary gameplay serializer owner" in row for row in violations)
    assert any("import/re-export facade" in row for row in violations)
    challenge_path = GAMEPLAY_BACKEND_VIEWS[1]
    sources.pop("backend/example/serializers.py")
    sources.pop("backend/example/facade.py")
    sources[challenge_path] = sources[challenge_path].replace(
        "serializer = WorkspaceFileSerializer(data=request.data)",
        "serializer = LocalWorkspaceFileSerializer(data=request.data)",
        1,
    )
    violations = gameplay_mutation_backend_violations(sources)
    assert any(
        "ChallengeWorkspaceFileAPIView.post must validate with WorkspaceFileSerializer" in row
        for row in violations
    )


def test_gameplay_mutation_openapi_guard_rejects_schema_forks_and_http_drift():
    schema = json.loads((ROOT / GAMEPLAY_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    schema["components"]["schemas"]["PatchedWorkspaceFile"] = {
        "type": "object",
        "properties": {"path": {"type": "string"}},
    }
    schema["components"]["schemas"]["WorkspaceFile"]["properties"]["extra"] = {"type": "string"}
    adventure_path = "/api/adventure-runs/{run_id}/files/"
    schema["paths"][adventure_path]["patch"]["requestBody"]["content"]["application/json"][
        "schema"
    ] = {"$ref": "#/components/schemas/PatchedWorkspaceFile"}
    schema["paths"][adventure_path]["patch"]["requestBody"]["required"] = False
    query_parameter = next(
        parameter
        for parameter in schema["paths"][adventure_path]["delete"]["parameters"]
        if parameter.get("in") == "query"
    )
    query_parameter["schema"] = {"type": "string"}
    violations = gameplay_mutation_openapi_violations(schema)
    assert any("PatchedWorkspaceFile must stay absent" in row for row in violations)
    assert any("WorkspaceFile properties must be exact" in row for row in violations)
    assert any("PATCH" in row and "must use WorkspaceFile" in row for row in violations)
    assert any("PATCH" in row and "request body must be required" in row for row in violations)
    assert any("DELETE" in row and "must require string query path" in row for row in violations)


def test_gameplay_mutation_contract_runtime_obeys_shared_generated_owners():
    assert check_gameplay_mutation_contract_ownership() == []
