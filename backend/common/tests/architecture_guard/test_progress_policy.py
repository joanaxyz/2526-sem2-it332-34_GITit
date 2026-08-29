"""Progress architecture contract-policy tests."""

import json
import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.contracts.progress import (  # noqa: E402
    DASHBOARD_FRONTEND_API,
    DASHBOARD_FRONTEND_TYPES,
    DASHBOARD_GENERATED_OPENAPI,
    DASHBOARD_HOME_API_SHIM,
    DASHBOARD_HOME_TYPES_SHIM,
    STATS_COMMON_OPENAPI,
    STATS_FRONTEND_API,
    STATS_FRONTEND_TYPES,
    STATS_GENERATED_OPENAPI,
    STATS_PROGRESS_SERIALIZERS,
    check_dashboard_summary_contract_ownership,
    check_stats_summary_contract_ownership,
    dashboard_contract_source_violations,
    dashboard_openapi_contract_violations,
    dashboard_secondary_frontend_contract_violations,
    progress_summary_secondary_backend_contract_violations,
    stats_contract_source_violations,
    stats_openapi_contract_violations,
)
from scripts.checks.architecture_guard.repository import (  # noqa: E402
    ROOT,
)

del _TEST_IMPORT_ROOT

_FRONTEND = "front" + "end"


def test_stats_contract_guard_rejects_duplicate_and_manual_contract_paths():
    violations = stats_contract_source_violations(
        progress_serializers_source="from rest_framework import serializers\nclass StatsSummaryResponseSerializer(serializers.Serializer):\n    skill_profile = serializers.ListField()\n    activity = serializers.ListField()\n    headlines = serializers.DictField()\nclass DashboardSummarySerializer(serializers.Serializer):\n    pass\nclass WalletSummaryResponseSerializer(serializers.Serializer):\n    balance = serializers.IntegerField()\n",
        common_openapi_source="from rest_framework import serializers\nclass WalletSummaryResponseSerializer(serializers.Serializer):\n    balance = serializers.IntegerField()\nclass StatsSummaryResponseSerializer(serializers.Serializer):\n    activity = serializers.ListField()\nclass DashboardSummaryResponseSerializer(serializers.Serializer):\n    counts = serializers.DictField()\n",
        stats_types_source="export type StatsSummary = { activity_trend: unknown[]; headline: object }\nexport type SkillAxis = { key: string }\nexport type TrendPoint = { date: string }\n",
        stats_api_source="import type { ApiSchemas } from '@/shared/api/generated/apiTypes'\ntype StatsSummaryResult = ApiSchemas['StatsSummaryResponse'] & StatsSummary\napiOperationRequest<'progress_stats_retrieve', StatsSummaryResult>(\n  'progress_stats_retrieve', '/progress/stats/'\n)\n",
    )
    assert any("StatsSummaryResponseSerializer fields must be exactly" in row for row in violations)
    assert any("belongs in progress/serializers.py" in row for row in violations)
    assert any("displaced DashboardSummarySerializer" in row for row in violations)
    assert any("must not duplicate the shared Wallet" in row for row in violations)
    assert any("StatsSummary must derive exactly" in row for row in violations)
    assert any("must not own or override" in row for row in violations)
    assert any("custom Stats response generic" in row for row in violations)


def test_stats_openapi_guard_rejects_displaced_and_loose_schema_shapes():
    violations = stats_openapi_contract_violations(
        {
            "components": {
                "schemas": {
                    "StatsSummaryResponse": {
                        "properties": {
                            "skill_profile": {"items": {"type": "object"}},
                            "activity": {"items": {"type": "object"}},
                            "headlines": {"type": "object"},
                            "totals": {"type": "object"},
                        },
                        "required": ["skill_profile", "activity", "headlines"],
                    }
                }
            },
            "paths": {
                "/api/progress/stats/": {
                    "get": {
                        "responses": {
                            "200": {"content": {"application/json": {"schema": {"type": "object"}}}}
                        }
                    }
                }
            },
        }
    )
    assert any("StatsSummaryResponse properties/required" in row for row in violations)
    assert any("StatsSummaryResponse property schemas must be exact" in row for row in violations)
    assert any("progress_stats_retrieve must return" in row for row in violations)


def test_stats_contract_guard_rejects_wrong_field_signatures_and_shadow_contracts():
    root = ROOT
    progress_source = (root / STATS_PROGRESS_SERIALIZERS).read_text(encoding="utf-8")
    common_source = (root / STATS_COMMON_OPENAPI).read_text(encoding="utf-8")
    types_source = (root / STATS_FRONTEND_TYPES).read_text(encoding="utf-8")
    api_source = (root / STATS_FRONTEND_API).read_text(encoding="utf-8")
    violations = stats_contract_source_violations(
        progress_serializers_source=progress_source.replace(
            "value = serializers.FloatField(allow_null=True)", "value = serializers.CharField()", 1
        )
        + "\nStatsSummaryV2Serializer = StatsSummaryResponseSerializer\n",
        common_openapi_source=common_source
        + "\nclass StatsShadowSerializer(serializers.Serializer):\n"
        + "    activity = serializers.ListField()\n",
        stats_types_source=types_source + "\nexport type StatsShadow = { activity: unknown[] }\n",
        stats_api_source=api_source,
    )
    assert any("RateMetricSerializer field signatures must be exact" in row for row in violations)
    assert any("secondary contract alias StatsSummaryV2Serializer" in row for row in violations)
    assert any(
        "StatsShadowSerializer belongs in progress/serializers.py" in row for row in violations
    )
    assert any("extra aliases found: ['StatsShadow']" in row for row in violations)


def test_stats_contract_guard_rejects_secondary_backend_modules():
    violations = progress_summary_secondary_backend_contract_violations(
        {
            "backend/example/stats_contracts.py": "class StatsShadowSerializer:\n    pass\nStatsSummaryV2Serializer = StatsShadowSerializer\n"
        }
    )
    assert len(violations) == 2
    assert any("StatsShadowSerializer" in row for row in violations)
    assert any("StatsSummaryV2Serializer" in row for row in violations)


def test_stats_contract_guard_rejects_async_adapters_but_ignores_comments():
    root = ROOT
    progress_source = (root / STATS_PROGRESS_SERIALIZERS).read_text(encoding="utf-8")
    common_source = (root / STATS_COMMON_OPENAPI).read_text(encoding="utf-8")
    types_source = (root / STATS_FRONTEND_TYPES).read_text(encoding="utf-8")
    api_source = (root / STATS_FRONTEND_API).read_text(encoding="utf-8")
    comment_violations = stats_contract_source_violations(
        progress_serializers_source=progress_source,
        common_openapi_source=common_source,
        stats_types_source=types_source,
        stats_api_source="// StatsSummary and ApiSchemas stay generated.\n" + api_source,
    )
    assert comment_violations == []
    adapter_source = api_source.replace(
        "summary() {\n    return apiOperationRequest('progress_stats_retrieve', '/progress/stats/')\n  }",
        "async summary() {\n    const payload = await apiOperationRequest(\n      'progress_stats_retrieve', '/progress/stats/'\n    )\n    return normalize(payload)\n  }",
    )
    adapter_violations = stats_contract_source_violations(
        progress_serializers_source=progress_source,
        common_openapi_source=common_source,
        stats_types_source=types_source,
        stats_api_source=adapter_source,
    )
    assert any(
        "must return the generated operation response directly" in row for row in adapter_violations
    )


def test_stats_openapi_guard_rejects_wrong_nested_schema_signatures():
    schema = json.loads((ROOT / STATS_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    schemas = schema["components"]["schemas"]
    schemas["RateMetric"]["properties"]["value"] = {"type": "number", "format": "double"}
    schemas["StatsSkillAxis"]["properties"]["command"] = {"type": "integer"}
    schemas["StatsTrendPoint"]["properties"]["date"] = {"type": "string"}
    schemas["StatsTrendPoint"]["properties"]["levels_completed"] = {"type": "string"}
    schemas["StatsSummaryResponse"]["properties"]["skill_profile"] = {
        "items": {"$ref": "#/components/schemas/StatsSkillAxis"}
    }
    violations = stats_openapi_contract_violations(schema)
    for component_name in (
        "RateMetric",
        "StatsSkillAxis",
        "StatsTrendPoint",
        "StatsSummaryResponse",
    ):
        assert any(f"{component_name} property schemas must be exact" in row for row in violations)


def test_stats_contract_runtime_obeys_one_way_generated_ownership():
    assert check_stats_summary_contract_ownership() == []


def test_dashboard_contract_guard_rejects_loose_serializer_and_frontend_shadows():
    root = ROOT
    progress_source = (root / STATS_PROGRESS_SERIALIZERS).read_text(encoding="utf-8")
    common_source = (root / STATS_COMMON_OPENAPI).read_text(encoding="utf-8")
    stats_types = (root / STATS_FRONTEND_TYPES).read_text(encoding="utf-8")
    stats_api = (root / STATS_FRONTEND_API).read_text(encoding="utf-8")
    serializer_violations = stats_contract_source_violations(
        progress_serializers_source=progress_source.replace(
            "retry_trends = DashboardRetryTrendSerializer(many=True)",
            "retry_trends = serializers.DictField()",
        ),
        common_openapi_source=common_source,
        stats_types_source=stats_types,
        stats_api_source=stats_api,
    )
    assert any(
        "DashboardSummaryResponseSerializer field signatures must be exact" in row
        for row in serializer_violations
    )
    frontend_violations = dashboard_contract_source_violations(
        dashboard_types_source="export type HomeSummary = { retry_trends: Record<string, unknown> }\nexport type HomeSummaryShadow = HomeSummary & { totals: object }\n",
        dashboard_api_source="import type { ApiSchemas } from '@/shared/api/generated/apiTypes'\ntype HomeSummaryResult = ApiSchemas['DashboardSummaryResponse'] & HomeSummary\nexport const homeSummaryApi = {\n  summary() {\n    return apiOperationRequest<'progress_dashboard_retrieve', HomeSummaryResult>(\n      'progress_dashboard_retrieve', '/progress/dashboard/'\n    )\n  },\n}\n",
        home_types_shim_source="export type HomeSummary = { mastery: number }\n",
        home_api_shim_source="export const homeApi = { summary: () => homeSummaryApi.summary() }\n",
    )
    assert any("HomeSummary must derive exactly" in row for row in frontend_violations)
    assert any("extra aliases found: ['HomeSummaryShadow']" in row for row in frontend_violations)
    assert any("must not own or override" in row for row in frontend_violations)
    assert any("custom Dashboard response generic" in row for row in frontend_violations)
    assert any("exact HomeSummary type re-export" in row for row in frontend_violations)
    assert any("exact homeSummaryApi re-export" in row for row in frontend_violations)


def test_dashboard_openapi_guard_rejects_loose_dynamic_and_array_shapes():
    schema = json.loads((ROOT / DASHBOARD_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    schemas = schema["components"]["schemas"]
    summary = schemas["DashboardSummaryResponse"]
    summary["properties"]["chapter_kpis"]["additionalProperties"] = {}
    summary["properties"]["retry_trends"] = {"type": "object"}
    summary["properties"]["completed_story_slug"] = {"type": "string"}
    summary["required"].remove("completed_story_slug")
    schemas["DashboardStreak"]["properties"]["last_completed_on"] = {"type": "string"}
    schema["paths"]["/api/progress/dashboard/"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] = {"type": "object"}
    violations = dashboard_openapi_contract_violations(schema)
    assert any("DashboardSummaryResponse properties/required" in row for row in violations)
    assert any(
        "DashboardSummaryResponse property schemas must be exact" in row for row in violations
    )
    assert any("DashboardStreak property schemas must be exact" in row for row in violations)
    assert any("progress_dashboard_retrieve must return" in row for row in violations)


def test_dashboard_guard_rejects_alternate_imports_and_parallel_api_exports():
    root = ROOT
    types_source = (root / DASHBOARD_FRONTEND_TYPES).read_text(encoding="utf-8")
    api_source = (root / DASHBOARD_FRONTEND_API).read_text(encoding="utf-8")
    home_types_shim = (root / DASHBOARD_HOME_TYPES_SHIM).read_text(encoding="utf-8")
    home_api_shim = (root / DASHBOARD_HOME_API_SHIM).read_text(encoding="utf-8")
    wrong_types_import = dashboard_contract_source_violations(
        dashboard_types_source=types_source.replace(
            "@/shared/api/generated/apiTypes", "./manualDashboardSchemas"
        ),
        dashboard_api_source=api_source,
        home_types_shim_source=home_types_shim,
        home_api_shim_source=home_api_shim,
    )
    wrong_api_import = dashboard_contract_source_violations(
        dashboard_types_source=types_source,
        dashboard_api_source=api_source.replace("@/shared/api/httpClient", "./dashboardAdapter"),
        home_types_shim_source=home_types_shim,
        home_api_shim_source=home_api_shim,
    )
    extra_adapter = dashboard_contract_source_violations(
        dashboard_types_source=types_source,
        dashboard_api_source=api_source
        + "\nexport async function legacyDashboard() {\n"
        + "  const payload = await homeSummaryApi.summary()\n"
        + "  return { ...payload, retry_trends: {} }\n"
        + "}\n",
        home_types_shim_source=home_types_shim,
        home_api_shim_source=home_api_shim,
    )
    assert any("canonical generated-types import" in row for row in wrong_types_import)
    assert any("canonical HTTP-client import" in row for row in wrong_api_import)
    assert any("direct homeSummaryApi export" in row for row in extra_adapter)


def test_dashboard_guard_rejects_secondary_frontend_and_backend_owners():
    frontend_violations = dashboard_secondary_frontend_contract_violations(
        {
            f"{_FRONTEND}/src/shared/progress/manualDashboardSchemas.ts": "export type DashboardSummaryDto = ApiSchemas['DashboardSummaryResponse']\n",
            f"{_FRONTEND}/src/shared/progress/dashboardRequest.ts": "export const requestDashboard = () => apiOperationRequest('progress_dashboard_retrieve', '/progress/dashboard/')\n",
            f"{_FRONTEND}/src/shared/progress/dashboardAdapter.ts": "export async function adaptDashboard() {\n  return normalize(await homeSummaryApi.summary())\n}\n",
            f"{_FRONTEND}/src/shared/progress/aliasedWrapper.ts": "import { homeSummaryApi as legacyApi } from '@/shared/progress/homeSummaryApi'\nexport const legacyDashboard = () => legacyApi.summary()\n",
            f"{_FRONTEND}/src/shared/progress/exportedReference.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport const legacyDashboard = homeApi.summary\n",
            f"{_FRONTEND}/src/shared/progress/destructured.ts": "import { homeApi } from '@/features/home/api/homeApi'\nconst { summary: getDashboard } = homeApi\nexport const legacyDashboard = () => getDashboard()\n",
            f"{_FRONTEND}/src/shared/progress/computed.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport const legacyDashboard = () => homeApi['summary']()\n",
            f"{_FRONTEND}/src/shared/progress/transformedFunction.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome() {\n  const payload = await homeApi.summary()\n  return normalize(payload)\n}\n",
            f"{_FRONTEND}/src/shared/progress/transformedArrow.ts": "import { homeSummaryApi as api } from '@/shared/progress/homeSummaryApi'\nexport const loadHome = async () => normalize(await api.summary())\n",
            f"{_FRONTEND}/src/shared/progress/objectLoader.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport const loaders = { home: () => homeApi.summary() }\n",
            f"{_FRONTEND}/src/shared/progress/objectReturnBlock.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome() {\n  const payload = await homeApi.summary()\n  return { ...payload, retry_trends: {} }\n}\n",
            f"{_FRONTEND}/src/shared/progress/nestedObjectLoader.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport const loaders = {\n  progress: { home: () => homeApi.summary() },\n}\n",
            f"{_FRONTEND}/src/shared/progress/objectMethodReference.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport const loaders = { home: homeApi.summary }\n",
            f"{_FRONTEND}/src/shared/progress/multilineReturn.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome() {\n  return (\n    normalize(\n      await homeApi.summary()\n    )\n  )\n}\n",
            f"{_FRONTEND}/src/shared/progress/twoStepNormalize.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome() {\n  const payload = await homeApi.summary()\n  const legacy = normalize(payload)\n  return legacy\n}\n",
            f"{_FRONTEND}/src/shared/progress/twoStepObject.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome() {\n  const payload = await homeApi.summary()\n  const legacy = { ...payload, retry_trends: {} }\n  return legacy\n}\n",
            f"{_FRONTEND}/src/shared/progress/multilineAssignment.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome() {\n  const payload =\n    await homeApi.summary()\n  return payload\n}\n",
            f"{_FRONTEND}/src/shared/progress/nestedReturn.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome(enabled: boolean) {\n  const payload = await homeApi.summary()\n  if (enabled) {\n    return normalize(payload)\n  }\n}\n",
            f"{_FRONTEND}/src/shared/progress/tryReturn.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome() {\n  const payload = await homeApi.summary()\n  try {\n    return { ...payload, retry_trends: {} }\n  } finally {\n    cleanup()\n  }\n}\n",
            f"{_FRONTEND}/src/shared/progress/ordinaryConsumer.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadDashboardForView() {\n  const payload = await homeApi.summary()\n  renderDashboard(payload)\n}\n",
            f"{_FRONTEND}/src/shared/progress/earlyReturnConsumer.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome(ready: boolean) {\n  if (!ready) return null\n  const payload = await homeApi.summary()\n  renderDashboard(payload)\n}\n",
            f"{_FRONTEND}/src/shared/progress/unrelatedReturnConsumer.ts": "import { homeApi } from '@/features/home/api/homeApi'\nexport async function loadHome() {\n  const payload = await homeApi.summary()\n  renderDashboard(payload)\n  return null\n}\n",
        }
    )
    backend_violations = progress_summary_secondary_backend_contract_violations(
        {
            "backend/example/dashboard_contracts.py": "class DashboardShadowSerializer:\n    pass\nDashboardSummaryV2Serializer = DashboardShadowSerializer\nclass HomeSummarySerializer:\n    pass\nHomeOverviewResponseSerializer = HomeSummarySerializer\n"
        }
    )
    assert any("secondary Dashboard response DTO" in row for row in frontend_violations)
    assert any("secondary Dashboard endpoint request path" in row for row in frontend_violations)
    assert any("secondary Dashboard summary adapter" in row for row in frontend_violations)
    for path_name in (
        "aliasedWrapper.ts",
        "exportedReference.ts",
        "destructured.ts",
        "computed.ts",
        "transformedFunction.ts",
        "transformedArrow.ts",
        "objectLoader.ts",
        "objectReturnBlock.ts",
        "nestedObjectLoader.ts",
        "objectMethodReference.ts",
        "multilineReturn.ts",
        "twoStepNormalize.ts",
        "twoStepObject.ts",
        "multilineAssignment.ts",
        "nestedReturn.ts",
        "tryReturn.ts",
    ):
        assert any(
            path_name in row and "secondary Dashboard summary adapter" in row
            for row in frontend_violations
        )
    for path_name in (
        "ordinaryConsumer.ts",
        "earlyReturnConsumer.ts",
        "unrelatedReturnConsumer.ts",
    ):
        assert not any(path_name in row for row in frontend_violations)
    assert len(backend_violations) == 4
    assert any("DashboardShadowSerializer" in row for row in backend_violations)
    assert any("DashboardSummaryV2Serializer" in row for row in backend_violations)
    assert any("HomeSummarySerializer" in row for row in backend_violations)
    assert any("HomeOverviewResponseSerializer" in row for row in backend_violations)


def test_dashboard_contract_runtime_obeys_generated_home_shim_ownership():
    assert check_dashboard_summary_contract_ownership() == []
