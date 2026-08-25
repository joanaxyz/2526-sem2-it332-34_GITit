"""Replay the complete pre-cutover symbol manifest against canonical owners."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.contracts.auth import (  # noqa: E402
    AUTH_BACKEND_SERIALIZERS,
    AUTH_BACKEND_VIEWS,
    AUTH_COMMON_OPENAPI,
    AUTH_FRONTEND_API,
    AUTH_FRONTEND_TYPES,
    AUTH_GENERATED_OPENAPI,
    AUTH_HTTP_CLIENT,
    AUTH_OPERATION_IDS,
)
from scripts.checks.architecture_guard.contracts.catalog import (  # noqa: E402
    CATALOG_BACKEND_SERIALIZERS,
    CATALOG_CHAPTER_FIELDS,
    CATALOG_FRONTEND_API,
    CATALOG_FRONTEND_TYPES,
    CATALOG_GENERATED_OPENAPI,
    CATALOG_RESPONSE_FIELD_SETS,
    CATALOG_STORY_FIELDS,
)
from scripts.checks.architecture_guard.contracts.gameplay import (  # noqa: E402
    GAMEPLAY_ADVENTURE_SERIALIZERS,
    GAMEPLAY_BACKEND_VIEWS,
    GAMEPLAY_CHALLENGE_SERIALIZERS,
    GAMEPLAY_COMMON_SERIALIZERS,
    GAMEPLAY_FRONTEND_APIS,
    GAMEPLAY_FRONTEND_CONTRACT_NAMES,
    GAMEPLAY_GENERATED_OPENAPI,
    GAMEPLAY_SHARED_BODY_ADAPTER,
    GAMEPLAY_SHARED_COMMAND_TYPES,
    GAMEPLAY_SHARED_SERIALIZERS,
    GAMEPLAY_SHARED_WORKSPACE_TYPES,
    GAMEPLAY_WORKSPACE_TYPE_NAMES,
)
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
)
from scripts.checks.architecture_guard.repository import (  # noqa: E402
    BACKEND,
    FRONTEND_SRC,
    PY_SUFFIXES,
    ROOT,
    TS_SUFFIXES,
)
from scripts.checks.architecture_guard.typescript_analysis import (  # noqa: E402
    TS_IMPORT_EXPORT_FROM,
    TS_MODULE_SPECIFIER,
    TS_QUERY_CONSUMER_CALL,
    TS_TRIVIA,
)

del _TEST_IMPORT_ROOT


CANONICAL_CONSTANTS = (
    ("AUTH_BACKEND_SERIALIZERS", AUTH_BACKEND_SERIALIZERS),
    ("AUTH_BACKEND_VIEWS", AUTH_BACKEND_VIEWS),
    ("AUTH_COMMON_OPENAPI", AUTH_COMMON_OPENAPI),
    ("AUTH_FRONTEND_API", AUTH_FRONTEND_API),
    ("AUTH_FRONTEND_TYPES", AUTH_FRONTEND_TYPES),
    ("AUTH_GENERATED_OPENAPI", AUTH_GENERATED_OPENAPI),
    ("AUTH_HTTP_CLIENT", AUTH_HTTP_CLIENT),
    ("AUTH_OPERATION_IDS", AUTH_OPERATION_IDS),
    ("BACKEND", BACKEND),
    ("CATALOG_BACKEND_SERIALIZERS", CATALOG_BACKEND_SERIALIZERS),
    ("CATALOG_CHAPTER_FIELDS", CATALOG_CHAPTER_FIELDS),
    ("CATALOG_FRONTEND_API", CATALOG_FRONTEND_API),
    ("CATALOG_FRONTEND_TYPES", CATALOG_FRONTEND_TYPES),
    ("CATALOG_GENERATED_OPENAPI", CATALOG_GENERATED_OPENAPI),
    ("CATALOG_RESPONSE_FIELD_SETS", CATALOG_RESPONSE_FIELD_SETS),
    ("CATALOG_STORY_FIELDS", CATALOG_STORY_FIELDS),
    ("DASHBOARD_FRONTEND_API", DASHBOARD_FRONTEND_API),
    ("DASHBOARD_FRONTEND_TYPES", DASHBOARD_FRONTEND_TYPES),
    ("DASHBOARD_GENERATED_OPENAPI", DASHBOARD_GENERATED_OPENAPI),
    ("DASHBOARD_HOME_API_SHIM", DASHBOARD_HOME_API_SHIM),
    ("DASHBOARD_HOME_TYPES_SHIM", DASHBOARD_HOME_TYPES_SHIM),
    ("FRONTEND_SRC", FRONTEND_SRC),
    ("GAMEPLAY_ADVENTURE_SERIALIZERS", GAMEPLAY_ADVENTURE_SERIALIZERS),
    ("GAMEPLAY_BACKEND_VIEWS", GAMEPLAY_BACKEND_VIEWS),
    ("GAMEPLAY_CHALLENGE_SERIALIZERS", GAMEPLAY_CHALLENGE_SERIALIZERS),
    ("GAMEPLAY_COMMON_SERIALIZERS", GAMEPLAY_COMMON_SERIALIZERS),
    ("GAMEPLAY_FRONTEND_APIS", GAMEPLAY_FRONTEND_APIS),
    ("GAMEPLAY_FRONTEND_CONTRACT_NAMES", GAMEPLAY_FRONTEND_CONTRACT_NAMES),
    ("GAMEPLAY_GENERATED_OPENAPI", GAMEPLAY_GENERATED_OPENAPI),
    ("GAMEPLAY_SHARED_BODY_ADAPTER", GAMEPLAY_SHARED_BODY_ADAPTER),
    ("GAMEPLAY_SHARED_COMMAND_TYPES", GAMEPLAY_SHARED_COMMAND_TYPES),
    ("GAMEPLAY_SHARED_SERIALIZERS", GAMEPLAY_SHARED_SERIALIZERS),
    ("GAMEPLAY_SHARED_WORKSPACE_TYPES", GAMEPLAY_SHARED_WORKSPACE_TYPES),
    ("GAMEPLAY_WORKSPACE_TYPE_NAMES", GAMEPLAY_WORKSPACE_TYPE_NAMES),
    ("PY_SUFFIXES", PY_SUFFIXES),
    ("ROOT", ROOT),
    ("STATS_COMMON_OPENAPI", STATS_COMMON_OPENAPI),
    ("STATS_FRONTEND_API", STATS_FRONTEND_API),
    ("STATS_FRONTEND_TYPES", STATS_FRONTEND_TYPES),
    ("STATS_GENERATED_OPENAPI", STATS_GENERATED_OPENAPI),
    ("STATS_PROGRESS_SERIALIZERS", STATS_PROGRESS_SERIALIZERS),
    ("TS_IMPORT_EXPORT_FROM", TS_IMPORT_EXPORT_FROM),
    ("TS_MODULE_SPECIFIER", TS_MODULE_SPECIFIER),
    ("TS_QUERY_CONSUMER_CALL", TS_QUERY_CONSUMER_CALL),
    ("TS_SUFFIXES", TS_SUFFIXES),
    ("TS_TRIVIA", TS_TRIVIA),
)


def _stable_value(value: object) -> object:
    if isinstance(value, Path):
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            pass
        return {"type": "Path", "value": value.as_posix()}
    if isinstance(value, re.Pattern):
        return {"type": "Pattern", "pattern": value.pattern, "flags": value.flags}
    if isinstance(value, (set, frozenset)):
        items = [_stable_value(item) for item in value]
        items.sort(key=lambda item: json.dumps(item, sort_keys=True))
        return {"type": type(value).__name__, "items": items}
    if isinstance(value, tuple):
        return {"type": "tuple", "items": [_stable_value(item) for item in value]}
    if isinstance(value, list):
        return [_stable_value(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _stable_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return value


def test_canonical_owners_match_complete_pre_cutover_symbol_manifest() -> None:
    manifest_path = (
        ROOT / "docs/goals/architecture-guard-policy-modularization/"
        "PRE_CUTOVER_SYMBOL_MANIFEST.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))["symbols"]
    actual_functions: dict[str, tuple[str, str]] = {}

    package_root = ROOT / "scripts/checks/architecture_guard"
    for source_path in sorted(package_root.rglob("*.py")):
        owner = ".".join(source_path.relative_to(ROOT).with_suffix("").parts)
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name not in manifest:
                continue
            fingerprint = hashlib.sha256(
                ast.dump(
                    node,
                    annotate_fields=True,
                    include_attributes=False,
                ).encode()
            ).hexdigest()
            actual_functions[node.name] = (owner, fingerprint)

    expected_functions = {
        name: (record["owner"], record["normalized_ast_sha256"])
        for name, record in manifest.items()
        if record["kind"] == "function"
    }
    actual_constants = {}
    for name, value in CANONICAL_CONSTANTS:
        encoded = json.dumps(
            _stable_value(value),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        actual_constants[name] = hashlib.sha256(encoded).hexdigest()
    expected_constants = {
        name: record["resolved_value_sha256"]
        for name, record in manifest.items()
        if record["kind"] == "constant"
    }

    assert len(manifest) == 118
    assert actual_functions == expected_functions
    assert actual_constants == expected_constants
