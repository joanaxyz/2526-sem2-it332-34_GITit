"""Stats and Dashboard contract-ownership architecture policies."""

from __future__ import annotations

import json
import re

from scripts.checks.architecture_guard.python_analysis import (
    python_class_field_calls,
    python_class_fields,
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
    normalized_ts_type,
    strip_ts_comments,
    ts_exported_adapter_uses_access,
    ts_exported_type_aliases,
    ts_exports_tainted_binding,
    ts_member_access_aliases,
    ts_named_import_bindings,
    ts_reexports_named_binding,
    ts_type_aliases,
)

STATS_PROGRESS_SERIALIZERS = "backend/progress/serializers.py"
STATS_COMMON_OPENAPI = "backend/common/openapi.py"
STATS_FRONTEND_TYPES = "frontend/src/features/stats/types.ts"
STATS_FRONTEND_API = "frontend/src/features/stats/api/statsApi.ts"
STATS_GENERATED_OPENAPI = "frontend/src/shared/api/generated/openapi.json"
DASHBOARD_FRONTEND_TYPES = "frontend/src/shared/progress/types.ts"
DASHBOARD_FRONTEND_API = "frontend/src/shared/progress/homeSummaryApi.ts"
DASHBOARD_HOME_TYPES_SHIM = "frontend/src/features/home/types.ts"
DASHBOARD_HOME_API_SHIM = "frontend/src/features/home/api/homeApi.ts"
DASHBOARD_GENERATED_OPENAPI = STATS_GENERATED_OPENAPI


def is_stats_contract_symbol(name: str) -> bool:
    """Identify Stats/Dashboard/Wallet response-serializer contract symbols."""

    return name.endswith("Serializer") and (
        name == "RateMetricSerializer"
        or name.startswith("Stats")
        or name.startswith("Dashboard")
        or name.startswith(("HomeSummary", "HomeOverview"))
        or name.startswith("WalletSummaryResponse")
    )


def progress_summary_secondary_backend_contract_violations(
    path_sources: dict[str, str],
) -> list[str]:
    """Reject Progress summary-contract declarations outside canonical modules."""

    violations: list[str] = []
    for path_label, source in sorted(path_sources.items()):
        symbols = [
            name
            for name in (
                *python_top_level_class_names(source),
                *python_top_level_assignment_names(source),
            )
            if is_stats_contract_symbol(name)
        ]
        for symbol in symbols:
            violations.append(
                f"{path_label}: secondary Progress response contract {symbol} is not allowed"
            )
    return violations


def progress_summary_backend_contract_violations(
    *,
    progress_serializers_source: str,
    common_openapi_source: str,
) -> list[str]:
    """Enforce the shared Progress serializer owner for Stats and Dashboard."""

    violations: list[str] = []
    expected_progress_fields = {
        "RateMetricSerializer": {
            "value": "serializers.FloatField(allow_null=True)",
            "numerator": "serializers.IntegerField()",
            "denominator": "serializers.IntegerField()",
        },
        "DashboardKpiSetSerializer": {
            "scr": "RateMetricSerializer()",
            "arc": "RateMetricSerializer()",
            "hlcr": "RateMetricSerializer()",
        },
        "DashboardCountsSerializer": {
            "started": "serializers.IntegerField()",
            "completed": "serializers.IntegerField()",
            "failed": "serializers.IntegerField()",
            "abandoned": "serializers.IntegerField()",
        },
        "DashboardStreakSerializer": {
            "current": "serializers.IntegerField()",
            "longest": "serializers.IntegerField()",
            "last_completed_on": "serializers.DateField(allow_null=True)",
        },
        "DashboardRetryTrendSerializer": {
            "level_title": "serializers.CharField()",
            "attempts": "serializers.IntegerField()",
            "retries": "serializers.IntegerField()",
            "label": "serializers.CharField()",
        },
        "StatsSkillAxisSerializer": {
            "key": "serializers.CharField()",
            "label": "serializers.CharField()",
            "hint": "serializers.CharField()",
            "value": "serializers.FloatField(allow_null=True)",
            "command": "serializers.CharField()",
        },
        "StatsTrendPointSerializer": {
            "date": "serializers.DateField()",
            "levels_completed": "serializers.IntegerField()",
            "commands_run": "serializers.IntegerField()",
        },
        "StatsScopedCountSerializer": {
            "value": "serializers.IntegerField()",
            "scope": "serializers.CharField()",
        },
        "StatsHeadlineSerializer": {
            "levels_completed": "serializers.IntegerField()",
            "finish_rate": "RateMetricSerializer()",
            "accuracy": "serializers.FloatField(allow_null=True)",
            "boss_floors": "StatsScopedCountSerializer()",
            "comebacks": "StatsScopedCountSerializer()",
            "perfect_clears": "serializers.IntegerField()",
            "day_streak": "serializers.IntegerField()",
            "longest_streak": "serializers.IntegerField()",
            "gitcoins": "serializers.IntegerField()",
            "commands_run": "serializers.IntegerField()",
        },
        "StatsSummaryResponseSerializer": {
            "skill_profile": "StatsSkillAxisSerializer(many=True)",
            "activity_trend": "StatsTrendPointSerializer(many=True)",
            "headline": "StatsHeadlineSerializer()",
        },
        "DashboardSummaryResponseSerializer": {
            "kpis": "DashboardKpiSetSerializer()",
            "chapter_kpis": ("serializers.DictField(child=DashboardKpiSetSerializer())"),
            "counts": "DashboardCountsSerializer()",
            "completed_story_slug": "serializers.CharField(allow_null=True)",
            "completed_stories": "serializers.ListField(child=serializers.CharField())",
            "streak": "DashboardStreakSerializer()",
            "perfect_clears": "serializers.IntegerField()",
            "mastery": "serializers.FloatField()",
            "retry_trends": "DashboardRetryTrendSerializer(many=True)",
        },
    }
    progress_class_names = python_top_level_class_names(progress_serializers_source)
    for class_name, expected_calls in expected_progress_fields.items():
        expected_fields = set(expected_calls)
        fields = python_class_fields(progress_serializers_source, class_name)
        if fields is None or progress_class_names.count(class_name) != 1:
            violations.append(
                f"{STATS_PROGRESS_SERIALIZERS}: require exactly one canonical {class_name}"
            )
        elif fields != expected_fields:
            violations.append(
                f"{STATS_PROGRESS_SERIALIZERS}: {class_name} fields must be exactly "
                f"{sorted(expected_fields)}; found {sorted(fields)}"
            )
        else:
            actual_calls = python_class_field_calls(progress_serializers_source, class_name)
            if actual_calls != expected_calls:
                violations.append(
                    f"{STATS_PROGRESS_SERIALIZERS}: {class_name} field signatures must be exact"
                )

    allowed_progress_contracts = set(expected_progress_fields)
    for class_name in progress_class_names:
        if class_name == "DashboardSummarySerializer":
            violations.append(
                f"{STATS_PROGRESS_SERIALIZERS}: displaced DashboardSummarySerializer must stay deleted"
            )
        elif is_stats_contract_symbol(class_name) and class_name not in allowed_progress_contracts:
            violations.append(
                f"{STATS_PROGRESS_SERIALIZERS}: secondary contract {class_name} is not allowed"
            )
    for alias_name in python_top_level_assignment_names(progress_serializers_source):
        if is_stats_contract_symbol(alias_name):
            violations.append(
                f"{STATS_PROGRESS_SERIALIZERS}: secondary contract alias {alias_name} is not allowed"
            )

    for class_name in python_top_level_class_names(common_openapi_source):
        if (
            class_name == "RateMetricSerializer"
            or class_name.startswith("Stats")
            or class_name.startswith("Dashboard")
        ):
            violations.append(
                f"{STATS_COMMON_OPENAPI}: {class_name} belongs in progress/serializers.py"
            )
    for alias_name in python_top_level_assignment_names(common_openapi_source):
        if is_stats_contract_symbol(alias_name):
            violations.append(
                f"{STATS_COMMON_OPENAPI}: secondary contract alias {alias_name} is not allowed"
            )
    if python_class_fields(common_openapi_source, "WalletSummaryResponseSerializer") is None:
        violations.append(
            f"{STATS_COMMON_OPENAPI}: shared WalletSummaryResponseSerializer must remain canonical"
        )
    if (
        python_class_fields(progress_serializers_source, "WalletSummaryResponseSerializer")
        is not None
    ):
        violations.append(
            f"{STATS_PROGRESS_SERIALIZERS}: must not duplicate the shared Wallet response contract"
        )
    return violations


def stats_contract_source_violations(
    *,
    progress_serializers_source: str,
    common_openapi_source: str,
    stats_types_source: str,
    stats_api_source: str,
) -> list[str]:
    """Enforce the shared backend owner and generated-only Stats frontend aliases."""

    violations = progress_summary_backend_contract_violations(
        progress_serializers_source=progress_serializers_source,
        common_openapi_source=common_openapi_source,
    )
    stats_types_without_comments = strip_ts_comments(stats_types_source)
    aliases = ts_exported_type_aliases(stats_types_without_comments)
    expected_aliases = {
        "StatsSummary": "ApiSchemas['StatsSummaryResponse']",
        "SkillAxis": "StatsSummary['skill_profile'][number]",
        "TrendPoint": "StatsSummary['activity_trend'][number]",
    }
    for alias_name, expected_body in expected_aliases.items():
        actual_body = aliases.get(alias_name)
        if actual_body is None or normalized_ts_type(actual_body) != normalized_ts_type(
            expected_body
        ):
            violations.append(
                f"{STATS_FRONTEND_TYPES}: {alias_name} must derive exactly from {expected_body}"
            )
    all_aliases = ts_type_aliases(stats_types_without_comments)
    extra_aliases = sorted(set(all_aliases) - set(expected_aliases))
    if extra_aliases or re.search(r"\b(?:export\s+)?interface\b", stats_types_without_comments):
        violations.append(
            f"{STATS_FRONTEND_TYPES}: may declare only the three generated Stats aliases; "
            f"extra aliases found: {extra_aliases}"
        )

    stats_api_without_comments = strip_ts_comments(stats_api_source)
    if re.search(
        r"\b(?:StatsSummaryResult|ApiSchemas|StatsSummary)\b",
        stats_api_without_comments,
    ):
        violations.append(
            f"{STATS_FRONTEND_API}: must not own or override the generated Stats response type"
        )
    operation_call = re.search(
        r"\bapiOperationRequest(?P<generics>\s*<[^>]*>)?\s*\(\s*"
        r"['\"]progress_stats_retrieve['\"]\s*,\s*['\"]/progress/stats/['\"]",
        stats_api_without_comments,
        re.S,
    )
    if operation_call is None:
        violations.append(
            f"{STATS_FRONTEND_API}: summary must use progress_stats_retrieve at /progress/stats/"
        )
    elif operation_call.group("generics") and "," in operation_call.group("generics"):
        violations.append(f"{STATS_FRONTEND_API}: must not pass a custom Stats response generic")
    summary_method = re.search(
        r"\bsummary\s*\(\s*\)\s*\{(?P<body>[^{}]*)\}",
        stats_api_without_comments,
        re.S,
    )
    expected_summary_body = (
        "returnapiOperationRequest('progress_stats_retrieve','/progress/stats/')"
    )
    actual_summary_body = (
        normalized_ts_type(summary_method.group("body")).replace(";", "")
        if summary_method is not None
        else ""
    )
    if actual_summary_body != expected_summary_body:
        violations.append(
            f"{STATS_FRONTEND_API}: summary must return the generated operation response directly"
        )
    if re.search(r"\.then\s*\(|\b(?:activity|headlines|totals)\s*:", stats_api_without_comments):
        violations.append(
            f"{STATS_FRONTEND_API}: must not adapt or alias the generated Stats response"
        )
    return violations


def stats_openapi_contract_violations(schema: dict) -> list[str]:
    """Check the committed Stats component and operation reference structurally."""

    violations: list[str] = []
    schemas = schema.get("components", {}).get("schemas", {})
    nullable_number = {"type": "number", "format": "double", "nullable": True}
    expected_schema_properties = {
        "RateMetric": {
            "value": nullable_number,
            "numerator": {"type": "integer"},
            "denominator": {"type": "integer"},
        },
        "StatsSkillAxis": {
            "key": {"type": "string"},
            "label": {"type": "string"},
            "hint": {"type": "string"},
            "value": nullable_number,
            "command": {"type": "string"},
        },
        "StatsTrendPoint": {
            "date": {"type": "string", "format": "date"},
            "levels_completed": {"type": "integer"},
            "commands_run": {"type": "integer"},
        },
        "StatsScopedCount": {
            "value": {"type": "integer"},
            "scope": {"type": "string"},
        },
        "StatsHeadline": {
            "levels_completed": {"type": "integer"},
            "finish_rate": {"$ref": "#/components/schemas/RateMetric"},
            "accuracy": nullable_number,
            "boss_floors": {"$ref": "#/components/schemas/StatsScopedCount"},
            "comebacks": {"$ref": "#/components/schemas/StatsScopedCount"},
            "perfect_clears": {"type": "integer"},
            "day_streak": {"type": "integer"},
            "longest_streak": {"type": "integer"},
            "gitcoins": {"type": "integer"},
            "commands_run": {"type": "integer"},
        },
        "StatsSummaryResponse": {
            "skill_profile": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/StatsSkillAxis"},
            },
            "activity_trend": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/StatsTrendPoint"},
            },
            "headline": {"$ref": "#/components/schemas/StatsHeadline"},
        },
    }
    for schema_name, expected_properties in expected_schema_properties.items():
        expected_fields = set(expected_properties)
        component = schemas.get(schema_name)
        actual_properties = component.get("properties", {}) if isinstance(component, dict) else {}
        actual_fields = set(actual_properties)
        required_fields = (
            set(component.get("required", [])) if isinstance(component, dict) else set()
        )
        if (
            not isinstance(component, dict)
            or component.get("type") != "object"
            or actual_fields != expected_fields
            or required_fields != expected_fields
        ):
            violations.append(
                f"{STATS_GENERATED_OPENAPI}: {schema_name} properties/required must be exactly "
                f"{sorted(expected_fields)}"
            )
        if actual_properties != expected_properties:
            violations.append(
                f"{STATS_GENERATED_OPENAPI}: {schema_name} property schemas must be exact"
            )

    response_schema = (
        schema.get("paths", {})
        .get("/api/progress/stats/", {})
        .get("get", {})
        .get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    if response_schema.get("$ref") != "#/components/schemas/StatsSummaryResponse":
        violations.append(
            f"{STATS_GENERATED_OPENAPI}: progress_stats_retrieve must return StatsSummaryResponse"
        )
    return violations


def dashboard_contract_source_violations(
    *,
    dashboard_types_source: str,
    dashboard_api_source: str,
    home_types_shim_source: str,
    home_api_shim_source: str,
) -> list[str]:
    """Enforce generated-only Dashboard types through the real Home entry path."""

    violations: list[str] = []
    dashboard_types = strip_ts_comments(dashboard_types_source)
    canonical_types_source = (
        "importtype{ApiSchemas}from'@/shared/api/generated/apiTypes'"
        "exporttypeHomeSummary=ApiSchemas['DashboardSummaryResponse']"
    )
    if normalized_ts_type(dashboard_types).replace(";", "") != canonical_types_source:
        violations.append(
            f"{DASHBOARD_FRONTEND_TYPES}: must contain only the canonical generated-types "
            "import and HomeSummary alias"
        )
    exported_aliases = ts_exported_type_aliases(dashboard_types)
    expected_alias = "ApiSchemas['DashboardSummaryResponse']"
    if normalized_ts_type(exported_aliases.get("HomeSummary", "")) != normalized_ts_type(
        expected_alias
    ):
        violations.append(
            f"{DASHBOARD_FRONTEND_TYPES}: HomeSummary must derive exactly from {expected_alias}"
        )
    all_aliases = ts_type_aliases(dashboard_types)
    extra_aliases = sorted(set(all_aliases) - {"HomeSummary"})
    if extra_aliases or re.search(r"\b(?:export\s+)?interface\b", dashboard_types):
        violations.append(
            f"{DASHBOARD_FRONTEND_TYPES}: may declare only the generated HomeSummary alias; "
            f"extra aliases found: {extra_aliases}"
        )

    dashboard_api = strip_ts_comments(dashboard_api_source)
    canonical_api_source = (
        "import{apiOperationRequest}from'@/shared/api/httpClient'"
        "exportconsthomeSummaryApi={summary(){"
        "returnapiOperationRequest('progress_dashboard_retrieve','/progress/dashboard/')"
        "},}"
    )
    if normalized_ts_type(dashboard_api).replace(";", "") != canonical_api_source:
        violations.append(
            f"{DASHBOARD_FRONTEND_API}: must contain only the canonical HTTP-client "
            "import and direct homeSummaryApi export"
        )
    if re.search(r"\b(?:HomeSummaryResult|ApiSchemas|HomeSummary)\b", dashboard_api):
        violations.append(
            f"{DASHBOARD_FRONTEND_API}: must not own or override the generated Dashboard response type"
        )
    operation_call = re.search(
        r"\bapiOperationRequest(?P<generics>\s*<[^>]*>)?\s*\(\s*"
        r"['\"]progress_dashboard_retrieve['\"]\s*,\s*['\"]/progress/dashboard/['\"]",
        dashboard_api,
        re.S,
    )
    if operation_call is None:
        violations.append(
            f"{DASHBOARD_FRONTEND_API}: summary must use progress_dashboard_retrieve "
            "at /progress/dashboard/"
        )
    elif operation_call.group("generics"):
        violations.append(
            f"{DASHBOARD_FRONTEND_API}: must not pass a custom Dashboard response generic"
        )
    summary_method = re.search(r"\bsummary\s*\(\s*\)\s*\{(?P<body>[^{}]*)\}", dashboard_api, re.S)
    expected_summary_body = (
        "returnapiOperationRequest('progress_dashboard_retrieve','/progress/dashboard/')"
    )
    actual_summary_body = (
        normalized_ts_type(summary_method.group("body")).replace(";", "")
        if summary_method is not None
        else ""
    )
    if actual_summary_body != expected_summary_body:
        violations.append(
            f"{DASHBOARD_FRONTEND_API}: summary must return the generated operation response directly"
        )

    home_types_shim = strip_ts_comments(home_types_shim_source).strip()
    if not re.fullmatch(
        r"export\s+type\s*\{\s*HomeSummary\s*,?\s*\}\s*from\s*"
        r"['\"]@/shared/progress/types['\"]\s*;?",
        home_types_shim,
    ):
        violations.append(
            f"{DASHBOARD_HOME_TYPES_SHIM}: must remain the exact HomeSummary type re-export"
        )

    home_api_shim = strip_ts_comments(home_api_shim_source).strip()
    if not re.fullmatch(
        r"export\s*\{\s*homeSummaryApi\s+as\s+homeApi\s*\}\s*from\s*"
        r"['\"]@/shared/progress/homeSummaryApi['\"]\s*;?",
        home_api_shim,
    ):
        violations.append(
            f"{DASHBOARD_HOME_API_SHIM}: must remain the exact homeSummaryApi re-export"
        )
    return violations


def dashboard_secondary_frontend_contract_violations(
    path_sources: dict[str, str],
) -> list[str]:
    """Reject secondary Dashboard DTOs and exported request adapters."""

    violations: list[str] = []
    for path_label, source in sorted(path_sources.items()):
        source = strip_ts_comments(source)
        if re.search(
            r"\b(?:type|interface|class)\s+(?:HomeSummary|Dashboard\w*"
            r"(?:Summary|Response|Contract|Dto)\w*)\b",
            source,
        ) or ("DashboardSummaryResponse" in source and "ApiSchemas" in source):
            violations.append(f"{path_label}: secondary Dashboard response DTO is not allowed")
        if re.search(r"\bprogress_dashboard_retrieve\b|/progress/dashboard/", source):
            violations.append(
                f"{path_label}: secondary Dashboard endpoint request path is not allowed"
            )

        canonical_modules = {
            "@/shared/progress/homeSummaryApi": "homeSummaryApi",
            "@/features/home/api/homeApi": "homeApi",
        }
        api_bindings: set[str] = set()
        for module, exported_name in canonical_modules.items():
            api_bindings.update(
                ts_named_import_bindings(
                    source,
                    path_label=path_label,
                    module=module,
                    exported_names={exported_name},
                )
            )
        access_patterns, tainted_bindings = ts_member_access_aliases(
            source,
            object_bindings=api_bindings,
            member_names={"summary"},
        )
        derived_export = ts_exported_adapter_uses_access(
            source,
            access_patterns,
        )
        exported_alias = ts_exports_tainted_binding(source, tainted_bindings)
        reexported_api = any(
            ts_reexports_named_binding(
                source,
                path_label=path_label,
                module=module,
                exported_names={exported_name},
            )
            for module, exported_name in canonical_modules.items()
        )
        if derived_export or exported_alias or reexported_api:
            violations.append(f"{path_label}: secondary Dashboard summary adapter is not allowed")
    return violations


def dashboard_openapi_contract_violations(schema: dict) -> list[str]:
    """Check exact Dashboard component fields, types, and operation reference."""

    violations: list[str] = []
    schemas = schema.get("components", {}).get("schemas", {})
    expected_schema_properties = {
        "DashboardCounts": {
            "started": {"type": "integer"},
            "completed": {"type": "integer"},
            "failed": {"type": "integer"},
            "abandoned": {"type": "integer"},
        },
        "DashboardKpiSet": {
            "scr": {"$ref": "#/components/schemas/RateMetric"},
            "arc": {"$ref": "#/components/schemas/RateMetric"},
            "hlcr": {"$ref": "#/components/schemas/RateMetric"},
        },
        "DashboardRetryTrend": {
            "level_title": {"type": "string"},
            "attempts": {"type": "integer"},
            "retries": {"type": "integer"},
            "label": {"type": "string"},
        },
        "DashboardStreak": {
            "current": {"type": "integer"},
            "longest": {"type": "integer"},
            "last_completed_on": {
                "type": "string",
                "format": "date",
                "nullable": True,
            },
        },
        "DashboardSummaryResponse": {
            "kpis": {"$ref": "#/components/schemas/DashboardKpiSet"},
            "chapter_kpis": {
                "type": "object",
                "additionalProperties": {"$ref": "#/components/schemas/DashboardKpiSet"},
            },
            "counts": {"$ref": "#/components/schemas/DashboardCounts"},
            "completed_story_slug": {"type": "string", "nullable": True},
            "completed_stories": {
                "type": "array",
                "items": {"type": "string"},
            },
            "streak": {"$ref": "#/components/schemas/DashboardStreak"},
            "perfect_clears": {"type": "integer"},
            "mastery": {"type": "number", "format": "double"},
            "retry_trends": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/DashboardRetryTrend"},
            },
        },
    }
    for schema_name, expected_properties in expected_schema_properties.items():
        expected_fields = set(expected_properties)
        component = schemas.get(schema_name)
        actual_properties = component.get("properties", {}) if isinstance(component, dict) else {}
        required_fields = (
            set(component.get("required", [])) if isinstance(component, dict) else set()
        )
        if (
            not isinstance(component, dict)
            or component.get("type") != "object"
            or set(actual_properties) != expected_fields
            or required_fields != expected_fields
        ):
            violations.append(
                f"{DASHBOARD_GENERATED_OPENAPI}: {schema_name} properties/required "
                f"must be exactly {sorted(expected_fields)}"
            )
        if actual_properties != expected_properties:
            violations.append(
                f"{DASHBOARD_GENERATED_OPENAPI}: {schema_name} property schemas must be exact"
            )

    response_schema = (
        schema.get("paths", {})
        .get("/api/progress/dashboard/", {})
        .get("get", {})
        .get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    if response_schema.get("$ref") != "#/components/schemas/DashboardSummaryResponse":
        violations.append(
            f"{DASHBOARD_GENERATED_OPENAPI}: progress_dashboard_retrieve must return "
            "DashboardSummaryResponse"
        )
    return violations


def check_dashboard_summary_contract_ownership() -> list[str]:
    """Keep the Dashboard contract generated through both Home feature shims."""

    path_labels = (
        STATS_PROGRESS_SERIALIZERS,
        STATS_COMMON_OPENAPI,
        DASHBOARD_FRONTEND_TYPES,
        DASHBOARD_FRONTEND_API,
        DASHBOARD_HOME_TYPES_SHIM,
        DASHBOARD_HOME_API_SHIM,
        DASHBOARD_GENERATED_OPENAPI,
    )
    missing = [path_label for path_label in path_labels if not (ROOT / path_label).is_file()]
    if missing:
        return [
            f"{path_label}: required Dashboard contract path is missing" for path_label in missing
        ]

    violations = dashboard_contract_source_violations(
        dashboard_types_source=(ROOT / DASHBOARD_FRONTEND_TYPES).read_text(encoding="utf-8"),
        dashboard_api_source=(ROOT / DASHBOARD_FRONTEND_API).read_text(encoding="utf-8"),
        home_types_shim_source=(ROOT / DASHBOARD_HOME_TYPES_SHIM).read_text(encoding="utf-8"),
        home_api_shim_source=(ROOT / DASHBOARD_HOME_API_SHIM).read_text(encoding="utf-8"),
    )
    progress_serializers_source = (ROOT / STATS_PROGRESS_SERIALIZERS).read_text(encoding="utf-8")
    common_openapi_source = (ROOT / STATS_COMMON_OPENAPI).read_text(encoding="utf-8")
    violations.extend(
        progress_summary_backend_contract_violations(
            progress_serializers_source=progress_serializers_source,
            common_openapi_source=common_openapi_source,
        )
    )
    canonical_backend_contract_paths = {
        STATS_PROGRESS_SERIALIZERS,
        STATS_COMMON_OPENAPI,
    }
    secondary_backend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(BACKEND, PY_SUFFIXES)
        if rel(path) not in canonical_backend_contract_paths
        and not any(part in {"migrations", "tests"} for part in path.parts)
        and not path.name.startswith("test_")
    }
    violations.extend(
        progress_summary_secondary_backend_contract_violations(secondary_backend_sources)
    )
    canonical_frontend_contract_paths = {
        DASHBOARD_FRONTEND_TYPES,
        DASHBOARD_FRONTEND_API,
        DASHBOARD_HOME_TYPES_SHIM,
        DASHBOARD_HOME_API_SHIM,
    }
    secondary_frontend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(FRONTEND_SRC, TS_SUFFIXES)
        if rel(path) not in canonical_frontend_contract_paths
        and "generated" not in path.parts
        and "preview" not in path.parts
        and "scaffolding" not in path.parts
        and ".test." not in path.name
        and ".spec." not in path.name
    }
    violations.extend(dashboard_secondary_frontend_contract_violations(secondary_frontend_sources))
    try:
        schema = json.loads((ROOT / DASHBOARD_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        violations.append(f"{DASHBOARD_GENERATED_OPENAPI}: invalid generated schema: {error}")
    else:
        violations.extend(dashboard_openapi_contract_violations(schema))
    return violations


def check_stats_summary_contract_ownership() -> list[str]:
    """Keep runtime, documented, generated, and feature Stats contracts one-way."""

    path_labels = (
        STATS_PROGRESS_SERIALIZERS,
        STATS_COMMON_OPENAPI,
        STATS_FRONTEND_TYPES,
        STATS_FRONTEND_API,
        STATS_GENERATED_OPENAPI,
    )
    missing = [path_label for path_label in path_labels if not (ROOT / path_label).is_file()]
    if missing:
        return [f"{path_label}: required Stats contract owner is missing" for path_label in missing]

    violations = stats_contract_source_violations(
        progress_serializers_source=(ROOT / STATS_PROGRESS_SERIALIZERS).read_text(encoding="utf-8"),
        common_openapi_source=(ROOT / STATS_COMMON_OPENAPI).read_text(encoding="utf-8"),
        stats_types_source=(ROOT / STATS_FRONTEND_TYPES).read_text(encoding="utf-8"),
        stats_api_source=(ROOT / STATS_FRONTEND_API).read_text(encoding="utf-8"),
    )
    canonical_backend_contract_paths = {
        STATS_PROGRESS_SERIALIZERS,
        STATS_COMMON_OPENAPI,
    }
    secondary_backend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(BACKEND, PY_SUFFIXES)
        if rel(path) not in canonical_backend_contract_paths
        and not any(part in {"migrations", "tests"} for part in path.parts)
        and not path.name.startswith("test_")
    }
    violations.extend(
        progress_summary_secondary_backend_contract_violations(secondary_backend_sources)
    )
    try:
        schema = json.loads((ROOT / STATS_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        violations.append(f"{STATS_GENERATED_OPENAPI}: invalid generated schema: {error}")
    else:
        violations.extend(stats_openapi_contract_violations(schema))
    return violations
