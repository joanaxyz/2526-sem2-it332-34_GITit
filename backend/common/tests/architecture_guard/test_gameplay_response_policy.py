from __future__ import annotations

import json
import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.contracts.gameplay_response import (  # noqa: E402
    GAMEPLAY_ADVENTURE_OPENAPI,
    GAMEPLAY_CHALLENGE_OPENAPI,
    GAMEPLAY_COMMON_OPENAPI,
    GAMEPLAY_RESPONSE_BACKEND_VIEWS,
    GAMEPLAY_RESPONSE_GENERATED_OPENAPI,
    check_gameplay_response_contract_ownership,
    gameplay_response_backend_violations,
    gameplay_response_openapi_violations,
)
from scripts.checks.architecture_guard.contracts.gameplay_response_frontend import (  # noqa: E402
    GAMEPLAY_ADVENTURE_TYPES,
    GAMEPLAY_CHALLENGE_ENTRY_API,
    GAMEPLAY_CHALLENGE_TYPES,
    GAMEPLAY_RESPONSE_FRONTEND_APIS,
    GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES,
    gameplay_response_frontend_violations,
)
from scripts.checks.architecture_guard.repository import ROOT  # noqa: E402

del _TEST_IMPORT_ROOT

_FRONTEND = "front" + "end"


def test_gameplay_response_backend_guard_rejects_displaced_owners_and_common_facades():
    source_paths = {
        GAMEPLAY_COMMON_OPENAPI,
        GAMEPLAY_ADVENTURE_OPENAPI,
        GAMEPLAY_CHALLENGE_OPENAPI,
        *GAMEPLAY_RESPONSE_BACKEND_VIEWS,
    }
    sources = {path: (ROOT / path).read_text(encoding="utf-8") for path in source_paths}
    sources[GAMEPLAY_COMMON_OPENAPI] += (
        "\nfrom adventures.openapi import AdventureRunResponseSerializer\n"
    )
    sources["backend/example/openapi.py"] = "class ChallengeRunResponseSerializer:\n    pass\n"
    sources["backend/example/facade.py"] = (
        "from challenges.openapi import ChallengeRunResponseSerializer\n"
    )
    sources["backend/example/assignment_facade.py"] = (
        "from challenges import openapi\n"
        "ChallengeRunResponseSerializer = openapi.ChallengeRunResponseSerializer\n"
    )
    adventure_view = GAMEPLAY_RESPONSE_BACKEND_VIEWS[0]
    sources[adventure_view] = sources[adventure_view].replace(
        "from adventures.openapi import (", "from common.openapi import (", 1
    )
    violations = gameplay_response_backend_violations(sources)
    assert any("domain response re-export facades" in row for row in violations)
    assert any("displaced gameplay response owner" in row for row in violations)
    assert any("response import/re-export facade" in row for row in violations)
    assert any("assignment_facade" in row and "displaced" in row for row in violations)
    assert any("must import directly from adventures.openapi" in row for row in violations)


def test_gameplay_response_openapi_guard_rejects_key_union_and_operation_drift():
    schema = json.loads((ROOT / GAMEPLAY_RESPONSE_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    schemas = schema["components"]["schemas"]
    schemas["AdventureRunResponse"]["properties"].pop("passed")
    schemas["ChallengeRunResponse"]["required"].remove("story")
    schemas["ChallengeCommandStepResponse"]["properties"].pop("evaluation_result")
    schemas["ChallengeCommandStepResponse"]["required"].remove("evaluation_result")
    schemas["AdventureCommandRunResponse"] = {"type": "object", "additionalProperties": {}}
    schemas["ChallengeCommandRunResponse"]["required"].append("completion")
    schema["paths"]["/api/challenge-runs/{run_id}/"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] = {"type": "object"}
    violations = gameplay_response_openapi_violations(schema)
    assert any("AdventureRunResponse properties/required" in row for row in violations)
    assert any("ChallengeRunResponse properties/required" in row for row in violations)
    assert any("ChallengeCommandStepResponse properties/required" in row for row in violations)
    assert any("exact full/patch union" in row for row in violations)
    assert any("ChallengeCommandRunResponse properties/required" in row for row in violations)
    assert any("must return ChallengeRunResponse" in row for row in violations)

    for field_name in ("mastery_progress", "completion", "next_difficulty", "sibling_levels"):
        required_schema = json.loads(
            (ROOT / GAMEPLAY_RESPONSE_GENERATED_OPENAPI).read_text(encoding="utf-8")
        )
        required_schema["components"]["schemas"]["ChallengeCommandRunResponse"]["required"].append(
            field_name
        )
        field_violations = gameplay_response_openapi_violations(required_schema)
        assert any(
            "ChallengeCommandRunResponse properties/required" in row for row in field_violations
        )

    for field_name, nullable in (
        ("mastery_progress", True),
        ("completion", False),
        ("next_difficulty", False),
        ("sibling_levels", True),
    ):
        nullable_schema = json.loads(
            (ROOT / GAMEPLAY_RESPONSE_GENERATED_OPENAPI).read_text(encoding="utf-8")
        )
        property_schema = nullable_schema["components"]["schemas"]["ChallengeCommandRunResponse"][
            "properties"
        ][field_name]
        if nullable:
            property_schema["nullable"] = True
        else:
            property_schema.pop("nullable", None)
        field_violations = gameplay_response_openapi_violations(nullable_schema)
        assert any("ChallengeCommandRunResponse nullable fields" in row for row in field_violations)

    status_schema = json.loads((ROOT / GAMEPLAY_RESPONSE_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    status_schema["components"]["schemas"]["AdventureRunResponse"]["properties"]["status"] = {
        "type": "string"
    }
    assert any(
        "AdventureRunResponse.status must reference GameplayRunStatus" in row
        for row in gameplay_response_openapi_violations(status_schema)
    )

    empty_nullable_schema = json.loads(
        (ROOT / GAMEPLAY_RESPONSE_GENERATED_OPENAPI).read_text(encoding="utf-8")
    )
    empty_nullable_schema["components"]["schemas"]["RuntimeStepResponse"]["properties"][
        "terminal_output"
    ]["nullable"] = True
    assert any(
        "RuntimeStepResponse nullable fields" in row
        for row in gameplay_response_openapi_violations(empty_nullable_schema)
    )


def test_gameplay_response_frontend_guard_rejects_wire_widening_and_client_http_types():
    source_paths = {
        GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES,
        GAMEPLAY_ADVENTURE_TYPES,
        GAMEPLAY_CHALLENGE_TYPES,
        *GAMEPLAY_RESPONSE_FRONTEND_APIS,
        GAMEPLAY_CHALLENGE_ENTRY_API,
    }
    sources = {path: (ROOT / path).read_text(encoding="utf-8") for path in source_paths}
    sources[GAMEPLAY_CHALLENGE_TYPES] = (
        sources[GAMEPLAY_CHALLENGE_TYPES]
        .replace(
            "Omit<ChallengeRunStepResponse, 'visualization_snapshot'>",
            "Omit<ChallengeRunStepResponse, 'visualization_snapshot' | 'terminal_output'>",
            1,
        )
        .replace(
            "ApiSchemas['ChallengeRunResponse'],",
            "Partial<ApiSchemas['ChallengeRunResponse']>,",
            1,
        )
    )
    challenge_api = GAMEPLAY_RESPONSE_FRONTEND_APIS[1]
    sources[challenge_api] = sources[challenge_api].replace("ChallengeRunResponse", "ChallengeRun")
    sources[f"{_FRONTEND}/src/features/example/responseFacade.ts"] = (
        "export type ChallengeRunResponse = { id: number }\n"
        "export type { AdventureRun } from '@/features/adventures/types'\n"
    )
    sources[challenge_api] += (
        "\nconst widened = value as Promise<ChallengeRunResponse & { extra: string }>\n"
    )
    violations = gameplay_response_frontend_violations(sources)
    assert any("ChallengeOptimisticStep" in row and "exact" in row for row in violations)
    assert any("ChallengeRunResponse must not widen" in row for row in violations)
    assert any("must use exact response type ChallengeRunResponse" in row for row in violations)
    assert any("must never be an HTTP response override" in row for row in violations)
    assert any("secondary gameplay response type" in row for row in violations)
    assert any("response type re-export facades" in row for row in violations)
    assert any("return casts/intersections" in row for row in violations)


def test_gameplay_response_frontend_guard_rejects_each_generated_contract_bypass():
    source_paths = {
        GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES,
        GAMEPLAY_ADVENTURE_TYPES,
        GAMEPLAY_CHALLENGE_TYPES,
        *GAMEPLAY_RESPONSE_FRONTEND_APIS,
        GAMEPLAY_CHALLENGE_ENTRY_API,
    }
    original = {path: (ROOT / path).read_text(encoding="utf-8") for path in source_paths}
    challenge_source = original[GAMEPLAY_CHALLENGE_TYPES]
    mutations = {
        "broad keyof omission": challenge_source.replace(
            "  | 'completion'",
            "  | 'completion'\n  | keyof ApiSchemas['ChallengeRunResponse']",
            1,
        ),
        "primitive omission": challenge_source.replace(
            "  | 'challenge'", "  | 'id'\n  | 'challenge'", 1
        ),
        "Partial overlay": challenge_source.replace(
            "ApiSchemas['ChallengeRunResponse'],",
            "Partial<ApiSchemas['ChallengeRunResponse']>,",
            1,
        ),
        "Record overlay": challenge_source.replace(
            "> & {\n  challenge: ChallengeRef",
            "> & Record<string, unknown> & {\n  challenge: ChallengeRef",
            1,
        ),
        "complete reconstruction": challenge_source.replace(
            "export type ChallengeRunResponse = Omit<",
            "export type ChallengeRunResponse = Pick<",
            1,
        ),
        "unrelated generated component": challenge_source.replace(
            "ApiSchemas['ChallengeRunResponse'],",
            "ApiSchemas['AdventureRunResponse'],",
            1,
        ),
        "extra client divergence": challenge_source.replace(
            "Omit<ChallengeRunStepResponse, 'visualization_snapshot'>",
            "Omit<ChallengeRunStepResponse, 'visualization_snapshot' | 'terminal_output'>",
            1,
        ),
        "extra wire overlay field": challenge_source.replace(
            "  challenge: ChallengeRef",
            "  challenge: ChallengeRef\n  shadow_field: string",
            1,
        ),
        "trailing anonymous wire intersection": challenge_source.replace(
            "  completion: LevelRunCompletion | null\n}\n\nexport type ChallengeRun =",
            "  completion: LevelRunCompletion | null\n} & { shadow_field: string }\n\n"
            "export type ChallengeRun =",
            1,
        ),
        "trailing named wire intersection": challenge_source.replace(
            "  completion: LevelRunCompletion | null\n}\n\nexport type ChallengeRun =",
            "  completion: LevelRunCompletion | null\n} & ExtraWireFields\n\n"
            "export type ChallengeRun =",
            1,
        ),
        "extra optimistic field": challenge_source.replace(
            "  visualization_snapshot?: never",
            "  visualization_snapshot?: never\n  local_only?: string",
            1,
        ),
    }
    for label, mutated_source in mutations.items():
        sources = dict(original)
        sources[GAMEPLAY_CHALLENGE_TYPES] = mutated_source
        assert gameplay_response_frontend_violations(sources), label

    terminal_sources = dict(original)
    terminal_sources[GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES] = terminal_sources[
        GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES
    ].replace(
        "ApiSchemas['RuntimeStepResponse']",
        "ApiSchemas['ChallengeRunStepResponse']",
        1,
    )
    assert any(
        "TerminalStep must derive exactly" in row
        for row in gameplay_response_frontend_violations(terminal_sources)
    )

    destroy_sources = dict(original)
    destroy_sources[GAMEPLAY_CHALLENGE_ENTRY_API] = destroy_sources[
        GAMEPLAY_CHALLENGE_ENTRY_API
    ].replace(
        "apiOperationRequest(\n      'challenge_runs_destroy'",
        "apiOperationRequest<'challenge_runs_destroy', null>(\n      'challenge_runs_destroy'",
        1,
    )
    assert any(
        "challenge_runs_destroy must use the generated response directly" in row
        for row in gameplay_response_frontend_violations(destroy_sources)
    )

    cast_sources = dict(original)
    cast_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] = cast_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]].replace(
        "return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
        "'challenge_runs_retrieve', `/challenge-runs/${runId}/`)",
        "return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
        "'challenge_runs_retrieve', `/challenge-runs/${runId}/`) as Promise<ChallengeRun>",
        1,
    )
    assert any(
        "return casts/intersections are forbidden" in row
        for row in gameplay_response_frontend_violations(cast_sources)
    )

    adapter_sources = dict(original)
    adapter_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] = adapter_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]].replace(
        "getRun(runId: number) {\n"
        "    return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
        "'challenge_runs_retrieve', `/challenge-runs/${runId}/`)\n"
        "  },",
        "async getRun(runId: number) {\n"
        "    const response = await apiOperationRequest<"
        "'challenge_runs_retrieve', ChallengeRunResponse>("
        "'challenge_runs_retrieve', `/challenge-runs/${runId}/`)\n"
        "    return { ...response, steps: [] }\n"
        "  },",
        1,
    )
    assert any(
        "getRun must directly return the exact challenge_runs_retrieve response" in row
        for row in gameplay_response_frontend_violations(adapter_sources)
    )

    then_sources = dict(original)
    then_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] = then_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]].replace(
        "return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
        "'challenge_runs_retrieve', `/challenge-runs/${runId}/`)",
        "return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
        "'challenge_runs_retrieve', `/challenge-runs/${runId}/`).then(value => value)",
        1,
    )
    assert any(
        "gameplay response adapters are forbidden" in row
        for row in gameplay_response_frontend_violations(then_sources)
    )

    for suffix in (
        " as any",
        ".catch(() => fallback)",
        ".finally(() => normalize())",
    ):
        suffix_sources = dict(original)
        suffix_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] = suffix_sources[
            GAMEPLAY_RESPONSE_FRONTEND_APIS[1]
        ].replace(
            "return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
            "'challenge_runs_retrieve', `/challenge-runs/${runId}/`)",
            "return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
            f"'challenge_runs_retrieve', `/challenge-runs/${{runId}}/`){suffix}",
            1,
        )
        assert any(
            "getRun must directly return the exact challenge_runs_retrieve response" in row
            for row in gameplay_response_frontend_violations(suffix_sources)
        ), suffix

    shadow_sources = dict(original)
    shadow_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] = (
        "function getRun(runId: number) {\n"
        "  return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
        "'challenge_runs_retrieve', `/challenge-runs/${runId}/`)\n"
        "}\n\n"
        + shadow_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]].replace(
            "getRun(runId: number) {\n"
            "    return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>("
            "'challenge_runs_retrieve', `/challenge-runs/${runId}/`)\n"
            "  },",
            "async getRun(runId: number) {\n"
            "    const response = await getRun(runId)\n"
            "    return { ...response, steps: [] }\n"
            "  },",
            1,
        )
    )
    assert any(
        "getRun must directly return the exact challenge_runs_retrieve response" in row
        for row in gameplay_response_frontend_violations(shadow_sources)
    )

    for generator_header in ("*getRun", "async *getRun"):
        generator_sources = dict(original)
        generator_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] = generator_sources[
            GAMEPLAY_RESPONSE_FRONTEND_APIS[1]
        ].replace("getRun(runId: number) {", f"{generator_header}(runId: number) {{", 1)
        assert any(
            "getRun must directly return the exact challenge_runs_retrieve response" in row
            for row in gameplay_response_frontend_violations(generator_sources)
        ), generator_header

    for label, member in (
        ("spread override", "  ...{ getRun: getRunOverride },\n"),
        ("property override", "  getRun: getRunOverride,\n"),
        ("computed override", "  [getRunKey]: getRunOverride,\n"),
    ):
        member_sources = dict(original)
        member_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] = member_sources[
            GAMEPLAY_RESPONSE_FRONTEND_APIS[1]
        ].replace("  },\n  submitCommand", f"  }},\n{member}  submitCommand", 1)
        assert any(
            "must not override owned methods through spread, computed, or property members" in row
            for row in gameplay_response_frontend_violations(member_sources)
        ), label

    for label, mutation in (
        ("post assignment", "challengeRunsApi.getRun = getRunOverride"),
        ("logical assignment", "challengeRunsApi.getRun ||= getRunOverride"),
        ("nullish assignment", "challengeRunsApi.getRun ??= getRunOverride"),
        (
            "Object.assign",
            "Object.assign(challengeRunsApi, { getRun: getRunOverride })",
        ),
        (
            "defineProperty",
            "Object.defineProperty(challengeRunsApi, 'getRun', { value: getRunOverride })",
        ),
        (
            "Reflect.set",
            "Reflect.set(challengeRunsApi, 'getRun', getRunOverride)",
        ),
        (
            "Reflect.deleteProperty",
            "Reflect.deleteProperty(challengeRunsApi, 'getRun')",
        ),
        ("delete member", "delete challengeRunsApi.getRun"),
    ):
        mutation_sources = dict(original)
        mutation_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] += f"\n{mutation}\n"
        assert any(
            "challengeRunsApi must not be reassigned or mutated" in row
            for row in gameplay_response_frontend_violations(mutation_sources)
        ), label

    for equality_operator in ("===", "=="):
        equality_sources = dict(original)
        equality_sources[GAMEPLAY_RESPONSE_FRONTEND_APIS[1]] += (
            f"\nconst sameGetRun = challengeRunsApi.getRun {equality_operator} expectedGetRun\n"
        )
        assert gameplay_response_frontend_violations(equality_sources) == []

    for label, alias_source in (
        (
            "named import alias",
            "import { challengeRunsApi as api } from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "Reflect.set(api, 'getRun', getRunOverride)\n",
        ),
        (
            "local alias chain",
            "import { challengeRunsApi } from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "const firstApi = challengeRunsApi\n"
            "const api = firstApi\n"
            "Reflect.deleteProperty(api, 'getRun')\n",
        ),
        (
            "namespace import alias",
            "import * as challengeApi from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "Object.assign(challengeApi.challengeRunsApi, { getRun: getRunOverride })\n",
        ),
    ):
        alias_sources = dict(original)
        alias_sources[f"{_FRONTEND}/src/features/example/apiMutation.ts"] = alias_source
        assert any(
            "challengeRunsApi must not be reassigned or mutated" in row
            for row in gameplay_response_frontend_violations(alias_sources)
        ), label

    for label, facade_source in (
        (
            "direct re-export",
            "export { challengeRunsApi as api } from "
            "'@/features/challenges/api/challengeRunsApi'\n",
        ),
        (
            "imported alias re-export",
            "import { challengeRunsApi as api } from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export { api }\n",
        ),
        (
            "namespace re-export",
            "export * as challengeApi from '@/features/challenges/api/challengeRunsApi'\n",
        ),
        (
            "exported let alias",
            "import { challengeRunsApi as api } from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export let facade = api\n",
        ),
        (
            "exported var alias",
            "import { challengeRunsApi as api } from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export var facade = api\n",
        ),
        (
            "named namespace facade",
            "import * as challengeApi from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export { challengeApi }\n",
        ),
        (
            "default namespace facade",
            "import * as challengeApi from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export default challengeApi\n",
        ),
        (
            "declared namespace facade",
            "import * as challengeApi from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export const apiFacade = challengeApi\n",
        ),
        (
            "typed alias facade",
            "import { challengeRunsApi as api } from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export const facade: typeof api = api\n",
        ),
        (
            "parenthesized alias facade",
            "import { challengeRunsApi as api } from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export const facade = (api)\n",
        ),
        (
            "parenthesized default facade",
            "import { challengeRunsApi as api } from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export default (api)\n",
        ),
    ):
        facade_sources = dict(original)
        facade_sources[f"{_FRONTEND}/src/features/example/apiFacade.ts"] = facade_source
        assert any(
            "gameplay API object re-export facades are forbidden" in row
            for row in gameplay_response_frontend_violations(facade_sources)
        ), label

    for label, projection_source in (
        (
            "direct namespace destructure",
            "import * as challengeApi from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export const { challengeRunsApi } = challengeApi\n",
        ),
        (
            "aliased namespace destructure",
            "import * as challengeApi from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "const { challengeRunsApi: api } = challengeApi\n"
            "export { api }\n",
        ),
        (
            "default namespace spread",
            "import * as challengeApi from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export default { ...challengeApi }\n",
        ),
        (
            "declared namespace spread",
            "import * as challengeApi from "
            "'@/features/challenges/api/challengeRunsApi'\n"
            "export const apiFacade = { ...challengeApi }\n",
        ),
    ):
        projection_sources = dict(original)
        projection_sources[f"{_FRONTEND}/src/features/example/apiProjection.ts"] = projection_source
        assert any(
            "gameplay API namespace imports are forbidden" in row
            for row in gameplay_response_frontend_violations(projection_sources)
        ), label

    duplicate_sources = dict(original)
    duplicate_sources[GAMEPLAY_CHALLENGE_ENTRY_API] += (
        "\napiOperationRequest<'challenge_runs_destroy', null>("
        "'challenge_runs_destroy', '/duplicate')\n"
    )
    assert any(
        "challenge_runs_destroy must have exactly one owned API call" in row
        for row in gameplay_response_frontend_violations(duplicate_sources)
    )


def test_gameplay_response_contract_runtime_obeys_domain_generated_owners():
    assert check_gameplay_response_contract_ownership() == []
