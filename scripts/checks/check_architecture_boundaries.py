#!/usr/bin/env python3
"""Fail CI when project layers import across forbidden boundaries.

This guard intentionally checks only high-signal rules that the current codebase
can satisfy. It prevents new architecture sediment without requiring a risky
folder rewrite.
"""

from __future__ import annotations

import ast
import re
import sys
from collections.abc import Iterable
from pathlib import Path

_REPOSITORY_IMPORT_ROOT = Path(__file__).resolve().parents[2]
if str(_REPOSITORY_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_IMPORT_ROOT))

from scripts.checks.architecture_guard.contracts.auth import (  # noqa: E402
    check_auth_contract_ownership,
)
from scripts.checks.architecture_guard.contracts.catalog import (  # noqa: E402
    check_catalog_contract_ownership,
)
from scripts.checks.architecture_guard.contracts.gameplay import (  # noqa: E402
    check_gameplay_mutation_contract_ownership,
)
from scripts.checks.architecture_guard.contracts.gameplay_response import (  # noqa: E402
    check_gameplay_response_contract_ownership,
)
from scripts.checks.architecture_guard.contracts.progress import (  # noqa: E402
    check_dashboard_summary_contract_ownership,
    check_stats_summary_contract_ownership,
)
from scripts.checks.architecture_guard.repository import (  # noqa: E402
    BACKEND,
    FRONTEND_SRC,
    PY_SUFFIXES,
    ROOT,
    TS_SUFFIXES,
    iter_files,
    rel,
)
from scripts.checks.architecture_guard.typescript_analysis import (  # noqa: E402
    canonical_ts_module_reference,
    destructured_function_props,
    jsx_component_props,
    strip_ts_comments,
    ts_module_matches_boundary,
    ts_module_specifiers,
    ts_named_import_bindings,
    ts_namespace_import_bindings,
    ts_value_module_references,
)

del _REPOSITORY_IMPORT_ROOT

SHARED_FEATURE_IMPORT = re.compile(r"@/features/")
PAGE_IMPORT = re.compile(r"@/features/[^'\"]+/pages/")
FRONTEND_PATH_REFERENCE = re.compile(r"frontend/(?:src|public|scripts)")

CONTENT_EDITOR_PAGE = "frontend/src/features/authoring/pages/ContentEditorPage.tsx"
CONTENT_EDITOR_HOOK = (
    "frontend/src/features/authoring/hooks/useContentEditorController.ts"
)
CONTENT_EDITOR_DRAFT_SUPPORT = (
    "frontend/src/features/authoring/hooks/contentEditorDraftState.ts"
)
CONTENT_EDITOR_COMPONENT_DIR = (
    "frontend/src/features/authoring/components/content-editor"
)
CONTENT_EDITOR_LINE_LIMITS = {
    "page": 150,
    "hook": 300,
    "support": 120,
    "component": 180,
}

HOME_HUB_VIEW = "frontend/src/features/home/components/HomeHubView.tsx"
HOME_PROFILE_WORKSPACE = (
    "frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx"
)
HOME_PROFILE_PANEL = (
    "frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx"
)
HOME_COMBAT_SHOWCASE = (
    "frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx"
)
HOME_COMPANION_STATUS = (
    "frontend/src/features/home/components/home-hub/HomeCompanionStatus.tsx"
)
HOME_COMPANION_PRESENTATION = (
    "frontend/src/features/home/components/home-hub/companionPresentation.ts"
)
HOME_HUB_LINE_LIMITS = {
    "hub": 140,
    "workspace": 100,
    "profile": 190,
    "combat": 250,
    "status": 120,
    "contract": 30,
}

HOME_STATS_VIEW = "frontend/src/features/home/components/HomeStatsView.tsx"
HOME_STATS_MODEL = "frontend/src/features/home/components/home-stats/homeStatsModel.ts"
HOME_STATS_DASHBOARD = (
    "frontend/src/features/home/components/home-stats/HomeStatsDashboard.tsx"
)
HOME_ACHIEVEMENT_GALLERY = (
    "frontend/src/features/home/components/home-stats/HomeAchievementGallery.tsx"
)
HOME_STATS_LINE_LIMITS = {
    "composition": 80,
    "model": 160,
    "dashboard": 220,
    "gallery": 150,
}
HOME_STATS_DISPLACED_CSS = {
    "frontend/src/styles/features/home/achievements.css",
    "frontend/src/styles/features/home/stats-actions.css",
}

# Build-time generators are allowed to call frontend tooling explicitly. Runtime
# backend code must never inspect frontend source/assets to make domain choices.
BACKEND_FRONTEND_ALLOWLIST = {
    "backend/curriculum/management/commands/generate_targets.py",
}

ALLOWED_FEATURE_DIRS = {
    "api",
    "components",
    "hooks",
    "pages",
    "preview",
    "scaffolding",
    "utils",
}
COMMON_ROOT_FORBIDDEN_MODULES = {
    "client_command_execution.py",
    "command_outcomes.py",
    "command_transition_verifier.py",
    "lru.py",
    "performance.py",
    "repository_state.py",
    "schema_validation.py",
}
SERVICE_PACKAGE_APPS = {
    path.name
    for path in BACKEND.iterdir()
    if path.is_dir() and (path / "apps.py").exists()
}
ROOT_FEATURE_ALLOWED_FILES = {"types.ts", "index.ts"}
THIN_BACKEND_PACKAGE_INIT_MAX_LINES = 100
FRONTEND_PRODUCTION_FILE_MAX_LINES = 400
BACKEND_RUNTIME_EXCLUDED_PARTS = {
    "management",
    "migrations",
    "seed_data",
    "testing",
    "tests",
}
DISPLACED_BACKEND_PATHS = {
    "backend/adventures/services/workspace_files.py",
    "backend/adminconsole/views.py",
    "backend/challenges/services/workspace_files.py",
    "backend/curriculum/selectors/core.py",
    "backend/progress/chests.py",
}


def backend_runtime_modules() -> dict[str, Path]:
    """Return maintained Django runtime modules keyed by import name."""

    modules: dict[str, Path] = {}
    for app in sorted(SERVICE_PACKAGE_APPS):
        app_dir = BACKEND / app
        for path in iter_files(app_dir, PY_SUFFIXES):
            relative = path.relative_to(BACKEND)
            if any(part in BACKEND_RUNTIME_EXCLUDED_PARTS for part in relative.parts):
                continue
            module_parts = list(relative.with_suffix("").parts)
            if module_parts[-1] == "__init__":
                module_parts.pop()
            modules[".".join(module_parts)] = path
    return modules


def imported_runtime_modules(
    *,
    module_name: str,
    path: Path,
    known_modules: set[str],
) -> set[str]:
    """Resolve imports from one module to other maintained runtime modules."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    is_package = path.name == "__init__.py"
    package_parts = (
        module_name.split(".") if is_package else module_name.split(".")[:-1]
    )
    imported: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                candidate = alias.name
                while candidate and candidate not in known_modules:
                    candidate = candidate.rpartition(".")[0]
                if candidate:
                    imported.add(candidate)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue

        if node.level:
            keep = len(package_parts) - (node.level - 1)
            if keep < 0:
                continue
            base_parts = [*package_parts[:keep]]
        else:
            base_parts = []
        if node.module:
            base_parts.extend(node.module.split("."))
        base = ".".join(base_parts)

        found_child = False
        for alias in node.names:
            if alias.name == "*":
                continue
            child = ".".join(part for part in (base, alias.name) if part)
            if child in known_modules:
                imported.add(child)
                found_child = True
        if base in known_modules and not found_child:
            imported.add(base)

    imported.discard(module_name)
    return imported


def strongly_connected_components(graph: dict[str, set[str]]) -> list[tuple[str, ...]]:
    """Return deterministic strongly connected components with more than one node."""

    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[tuple[str, ...]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in sorted(graph.get(node, set())):
            if neighbor not in indices:
                visit(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[neighbor])

        if lowlinks[node] != indices[node]:
            return
        component: list[str] = []
        while stack:
            member = stack.pop()
            on_stack.remove(member)
            component.append(member)
            if member == node:
                break
        if len(component) > 1:
            components.append(tuple(sorted(component)))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return sorted(components)


def check_backend_runtime_import_cycles() -> list[str]:
    modules = backend_runtime_modules()
    known_modules = set(modules)
    graph = {
        module_name: imported_runtime_modules(
            module_name=module_name,
            path=path,
            known_modules=known_modules,
        )
        for module_name, path in modules.items()
    }
    return [
        "backend runtime import cycle: " + " -> ".join((*component, component[0]))
        for component in strongly_connected_components(graph)
    ]


def check_displaced_backend_paths_are_absent(
    paths: Iterable[str] = DISPLACED_BACKEND_PATHS,
) -> list[str]:
    return [
        f"{path}: displaced architecture path must not be restored"
        for path in sorted(paths)
        if (ROOT / path).exists()
    ]


def imported_module_references(node: ast.AST) -> set[str]:
    """Return import module paths, including package aliases used for bypasses."""

    if isinstance(node, ast.Import):
        return {alias.name for alias in node.names}
    if not isinstance(node, ast.ImportFrom):
        return set()
    if not node.module:
        return {alias.name for alias in node.names if alias.name != "*"}

    modules = {node.module}
    boundary_aliases = {"auth", "db", "flags", "models", "selectors", "views", "wallet"}
    modules.update(
        f"{node.module}.{alias.name}"
        for alias in node.names
        if alias.name in boundary_aliases
    )
    return modules


def adminconsole_view_source_violations(*, source: str, path_label: str) -> list[str]:
    """Reject persistence ownership inside admin HTTP adapter modules."""

    tree = ast.parse(source, filename=path_label)
    violations: list[str] = []
    for node in ast.walk(tree):
        for module in imported_module_references(node):
            if (
                module == "models"
                or module.startswith("models.")
                or module == "django.contrib.auth"
                or module.startswith("django.contrib.auth.")
                or module.startswith("django.db")
                or module == "adminconsole.flags"
                or module.startswith("adminconsole.flags.")
                or module == "progress.selectors"
                or module.startswith("progress.selectors.")
                or module == "progress.wallet"
                or module.startswith("progress.wallet.")
                or module.endswith(".models")
                or ".models." in module
            ):
                violations.append(
                    f"{path_label}:{node.lineno}: admin HTTP adapters must delegate "
                    f"persistence reads to selectors, not import {module}"
                )
        if isinstance(node, ast.Attribute) and node.attr in {
            "_base_manager",
            "_default_manager",
            "objects",
        }:
            violations.append(
                f"{path_label}:{node.lineno}: admin HTTP adapters must not access ORM managers"
            )
    return violations


def adminconsole_selector_source_violations(
    *, source: str, path_label: str
) -> list[str]:
    """Reject HTTP-layer dependencies inside admin selector modules."""

    tree = ast.parse(source, filename=path_label)
    violations: list[str] = []
    for node in ast.walk(tree):
        for module in imported_module_references(node):
            is_view_module = (
                module == "views"
                or module.startswith("views.")
                or module == "adminconsole.views"
                or module.startswith("adminconsole.views.")
                or module.endswith(".views")
                or ".views." in module
            )
            if (
                module == "rest_framework"
                or module.startswith("rest_framework.")
                or is_view_module
            ):
                violations.append(
                    f"{path_label}:{node.lineno}: admin selectors must not import HTTP layer "
                    f"module {module}"
                )
    return violations


def adminconsole_view_init_source_violations(
    *, source: str, path_label: str
) -> list[str]:
    """Keep the public admin view initializer limited to exports."""

    tree = ast.parse(source, filename=path_label)
    violations: list[str] = []
    for index, node in enumerate(tree.body):
        is_docstring = (
            index == 0
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        is_import = isinstance(node, (ast.Import, ast.ImportFrom))
        is_all_assignment = (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__all__"
            and isinstance(node.value, (ast.List, ast.Tuple))
            and all(
                isinstance(element, ast.Constant) and isinstance(element.value, str)
                for element in node.value.elts
            )
        )
        if not (is_docstring or is_import or is_all_assignment):
            violations.append(
                f"{path_label}:{node.lineno}: admin views initializer may contain exports only"
            )
    return violations


def check_adminconsole_http_read_ownership() -> list[str]:
    views = BACKEND / "adminconsole" / "views"
    violations: list[str] = []
    for path in iter_files(views, PY_SUFFIXES):
        source = path.read_text(encoding="utf-8")
        violations.extend(
            adminconsole_view_source_violations(
                source=source,
                path_label=rel(path),
            )
        )
        if path.name == "__init__.py":
            violations.extend(
                adminconsole_view_init_source_violations(
                    source=source,
                    path_label=rel(path),
                )
            )
    return violations


def check_adminconsole_selectors_are_http_free() -> list[str]:
    selectors = BACKEND / "adminconsole" / "selectors"
    violations: list[str] = []
    for path in iter_files(selectors, PY_SUFFIXES):
        violations.extend(
            adminconsole_selector_source_violations(
                source=path.read_text(encoding="utf-8"),
                path_label=rel(path),
            )
        )
    return violations


def content_editor_source_violations(
    *,
    source: str,
    path_label: str,
    role: str,
) -> list[str]:
    """Enforce the route-controller-rendering ownership cutover."""

    violations: list[str] = []
    line_count = len(source.splitlines())
    limit = CONTENT_EDITOR_LINE_LIMITS[role]
    if line_count > limit:
        violations.append(
            f"{path_label}: content editor {role} has {line_count} lines; limit is {limit}"
        )

    modules = ts_module_specifiers(source)
    page_forbidden_modules = (
        "@tanstack/react-query",
        "frontend/src/features/admin/api",
        "frontend/src/features/authoring/api",
        "frontend/src/features/authoring/hooks/useUnsavedChangesGuard",
        "frontend/src/features/authoring/utils/authoringModel",
        "frontend/src/shared/api/queryKeys",
        "frontend/src/shared/auth/useAuth",
        "react-router-dom",
        "sonner",
    )
    component_forbidden_modules = (
        "@tanstack/react-query",
        "frontend/src/features/admin/api",
        "frontend/src/features/authoring/api",
        "frontend/src/features/authoring/hooks/useContentEditorController",
        "frontend/src/features/authoring/pages/ContentEditorPage",
        "frontend/src/shared/api/queryKeys",
        "frontend/src/shared/auth/useAuth",
        "sonner",
    )
    hook_forbidden_modules = (
        "frontend/src/features/authoring/components",
        "frontend/src/features/authoring/pages",
    )
    support_forbidden_modules = (
        "@tanstack/react-query",
        "frontend/src/features/admin",
        "frontend/src/features/authoring/api",
        "frontend/src/features/authoring/components",
        "frontend/src/features/authoring/hooks",
        "frontend/src/features/authoring/pages",
        "frontend/src/shared/api/queryKeys",
        "frontend/src/shared/auth/useAuth",
        "react",
        "react-router-dom",
        "sonner",
    )
    forbidden_modules = {
        "page": page_forbidden_modules,
        "component": component_forbidden_modules,
        "hook": hook_forbidden_modules,
        "support": support_forbidden_modules,
    }[role]
    for module in modules:
        canonical_module = canonical_ts_module_reference(
            module=module,
            path_label=path_label,
        )
        if any(
            ts_module_matches_boundary(canonical_module, boundary)
            for boundary in forbidden_modules
        ):
            violations.append(
                f"{path_label}: content editor {role} must not import {module}"
            )

    if role == "page":
        displaced_markers = (
            "DraftState",
            "buildInput",
            "formFromContent",
            "formToDefinition",
            "sameForm",
            "useMutation",
            "useNavigate",
            "useParams",
            "useQuery",
            "useSearchParams",
        )
        for marker in displaced_markers:
            if re.search(rf"\b{re.escape(marker)}\b", source):
                violations.append(
                    f"{path_label}: displaced workflow marker {marker} must stay in the controller"
                )
        if len(re.findall(r"\buseContentEditorController\s*\(", source)) != 1:
            violations.append(
                f"{path_label}: page must invoke useContentEditorController exactly once"
            )
        if re.search(
            r"\b(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*useContentEditorController\s*\(",
            source,
        ):
            violations.append(
                f"{path_label}: destructure useContentEditorController at the call site"
            )
        if re.search(
            r"\bcontroller\s*=|\{\s*\.\.\.\s*[\w$]*controller\b", source, re.I
        ):
            violations.append(
                f"{path_label}: controller objects must not be forwarded to rendering components"
            )
        for match in re.finditer(
            r"<(ContentEditorHeader|ContentDestinationSection|ContentMetadataSection)\b(?P<props>.*?)/?>",
            source,
            re.S,
        ):
            if re.search(r"\b(?:form|setForm)\s*=", match.group("props")):
                violations.append(
                    f"{path_label}: {match.group(1)} must not receive form or setForm"
                )

    if role == "component" and not path_label.endswith("ContentEditorDiagnostics.tsx"):
        if re.search(r"\bform\s*:", source) or re.search(r"\bsetForm\b", source):
            violations.append(
                f"{path_label}: only ContentEditorDiagnostics may receive the full form"
            )
    return violations


def content_editor_css_violations(*, source: str, path_label: str) -> list[str]:
    """Keep destination layout owned by editor-shell rather than battle-stage CSS."""

    violations: list[str] = []
    row = re.search(r"\.author-destination-row\s*\{(?P<body>[^}]*)\}", source, re.S)
    input_rule = re.search(
        r"\.author-destination-row\s*>\s*\.author-input\s*\{(?P<body>[^}]*)\}",
        source,
        re.S,
    )
    for property_name in ("display", "align-items", "gap", "flex-wrap"):
        if not row or not re.search(rf"\b{property_name}\s*:", row.group("body")):
            violations.append(
                f"{path_label}: .author-destination-row must own {property_name}"
            )
    if not input_rule or not re.search(r"\bflex\s*:", input_rule.group("body")):
        violations.append(f"{path_label}: destination input must own flexible sizing")
    return violations


def admin_authoring_import_violations(*, source: str, path_label: str) -> list[str]:
    """Keep the existing authoring-to-admin API edge from becoming a cycle."""

    return [
        f"{path_label}: admin feature must not import authoring feature module {module}"
        for module in ts_module_specifiers(source)
        if ts_module_matches_boundary(
            canonical_ts_module_reference(module=module, path_label=path_label),
            "frontend/src/features/authoring",
        )
    ]


def check_content_editor_workflow_ownership() -> list[str]:
    violations: list[str] = []
    targets = [
        (ROOT / CONTENT_EDITOR_PAGE, "page"),
        (ROOT / CONTENT_EDITOR_HOOK, "hook"),
        (ROOT / CONTENT_EDITOR_DRAFT_SUPPORT, "support"),
    ]
    component_dir = ROOT / CONTENT_EDITOR_COMPONENT_DIR
    targets.extend(
        (path, "component") for path in iter_files(component_dir, TS_SUFFIXES)
    )
    for path, role in targets:
        if not path.exists():
            violations.append(f"{rel(path)}: required content editor {role} is missing")
            continue
        violations.extend(
            content_editor_source_violations(
                source=path.read_text(encoding="utf-8"),
                path_label=rel(path),
                role=role,
            )
        )

    destination = component_dir / "ContentDestinationSection.tsx"
    if destination.exists() and "author-destination-row" not in destination.read_text(
        encoding="utf-8"
    ):
        violations.append(
            f"{rel(destination)}: destination must use the editor-shell-owned row selector"
        )
    css = ROOT / "frontend/src/styles/features/authoring/editor-shell.css"
    violations.extend(
        content_editor_css_violations(
            source=css.read_text(encoding="utf-8"),
            path_label=rel(css),
        )
    )
    for path in iter_files(FRONTEND_SRC / "features" / "admin", TS_SUFFIXES):
        violations.extend(
            admin_authoring_import_violations(
                source=path.read_text(encoding="utf-8", errors="ignore"),
                path_label=rel(path),
            )
        )
    return violations


def home_hub_source_violations(
    *,
    source: str,
    path_label: str,
    role: str,
) -> list[str]:
    """Enforce Home Hub URL, integration, presentation, and combat ownership."""

    violations: list[str] = []
    line_count = len(source.splitlines())
    limit = HOME_HUB_LINE_LIMITS[role]
    if line_count > limit:
        violations.append(
            f"{path_label}: Home Hub {role} has {line_count} lines; limit is {limit}"
        )

    direct_data_modules = (
        "@tanstack/react-query",
        "frontend/src/features/home/api",
        "frontend/src/shared/shop",
        "frontend/src/features/skills/api",
        "frontend/src/shared/api",
    )
    hub_forbidden_modules = (
        *direct_data_modules,
        "frontend/src/features/home/components/home-hub/HomeCombatShowcase",
        "frontend/src/features/home/components/home-hub/HomeProfilePanel",
        "frontend/src/features/skills",
        "frontend/src/shared/battle",
        "frontend/src/shared/cosmetics/companionRuntime",
        "frontend/src/shared/git/commandCatalog",
        "frontend/src/shared/progress/rank",
        "frontend/src/shared/sprites",
        "frontend/src/shared/wallet",
    )
    workspace_forbidden_modules = (
        *direct_data_modules,
        "react",
        "react-router-dom",
        "frontend/src/features/home/components/HomeRankBadge",
        "frontend/src/shared/battle",
        "frontend/src/shared/cosmetics/companionRuntime",
        "frontend/src/shared/git/commandCatalog",
        "frontend/src/shared/player-loadout",
        "frontend/src/shared/progress/rank",
        "frontend/src/shared/sprites",
        "frontend/src/shared/wallet",
    )
    profile_forbidden_modules = (
        *direct_data_modules,
        "react-router-dom",
        "frontend/src/features/home/components/home-hub/HomeCombatShowcase",
        "frontend/src/features/skills/hooks/useLearnedSkills",
        "frontend/src/shared/battle",
        "frontend/src/shared/cosmetics/companionRuntime",
        "frontend/src/shared/git/commandCatalog",
        "frontend/src/shared/player-loadout",
        "frontend/src/shared/sprites",
    )
    combat_forbidden_modules = (
        *direct_data_modules,
        "react-router-dom",
        "frontend/src/features/home/components/HomeRankBadge",
        "frontend/src/features/home/components/home-hub/HomeProfilePanel",
        "frontend/src/features/skills/hooks/useLearnedSkills",
        "frontend/src/shared/player-loadout",
        "frontend/src/shared/progress/rank",
        "frontend/src/shared/wallet",
    )
    status_forbidden_modules = (
        *direct_data_modules,
        "frontend/src/features/home/components/HomeRankBadge",
        "frontend/src/features/home/components/home-hub/HomeCombatShowcase",
        "frontend/src/features/home/components/home-hub/HomeProfilePanel",
        "frontend/src/features/skills/hooks/useLearnedSkills",
        "frontend/src/shared/battle",
        "frontend/src/shared/cosmetics/companionRuntime",
        "frontend/src/shared/git/commandCatalog",
        "frontend/src/shared/player-loadout",
        "frontend/src/shared/progress/rank",
        "frontend/src/shared/sprites",
        "frontend/src/shared/wallet",
    )
    contract_forbidden_modules: tuple[str, ...] = ()
    forbidden_modules = {
        "hub": hub_forbidden_modules,
        "workspace": workspace_forbidden_modules,
        "profile": profile_forbidden_modules,
        "combat": combat_forbidden_modules,
        "status": status_forbidden_modules,
        "contract": contract_forbidden_modules,
    }[role]
    if role != "hub":
        forbidden_modules = (
            *forbidden_modules,
            "frontend/src/features/home/components/HomeHubView",
            "frontend/src/features/home/pages/HomePage",
        )

    modules = ts_module_specifiers(source)
    canonical_modules = [
        canonical_ts_module_reference(module=module, path_label=path_label)
        for module in modules
    ]
    for module, canonical_module in zip(modules, canonical_modules, strict=True):
        if any(
            ts_module_matches_boundary(canonical_module, boundary)
            for boundary in forbidden_modules
        ):
            violations.append(f"{path_label}: Home Hub {role} must not import {module}")

    role_forbidden_markers = {
        "hub": (
            "ShowcaseMove",
            "attackWithSkill",
            "companionFromDef",
            "cssLengthToPx",
            "effectForSkill",
            "effectPlacementForSkill",
            "gitCommandFamily",
            "homeGroundPoint",
            "home-profile-panel",
            "home-profile-view",
            "home-rank-view",
            "home-ref-grid",
            "home-spellbook-panel",
            "home-sprite-panel",
            "playMove",
            "SpriteAnimator",
            "useLearnedSkills",
            "useRef",
            "useState",
        ),
        "workspace": (
            "clearTimeout",
            "cssLengthToPx",
            "deriveRank",
            "effectForSkill",
            "effectPlacementForSkill",
            "GitCoinIcon",
            "gitCommandFamily",
            "homeGroundPoint",
            "home-profile-view",
            "home-rank-view",
            "home-spellbook-panel",
            "home-sprite-panel",
            "RankBadge",
            "RANK_TIERS",
            "setTimeout",
            "SpriteAnimator",
            "useEffect",
            "useMemo",
            "usePlayerLoadout",
            "useRef",
            "useState",
        ),
        "profile": (
            "attackWithSkill",
            "clearTimeout",
            "cssLengthToPx",
            "effectForSkill",
            "effectPlacementForSkill",
            "gitCommandFamily",
            "homeGroundPoint",
            "home-spellbook-panel",
            "home-sprite-panel",
            "setTimeout",
            "SpriteAnimator",
            "Navigate",
            "useLocation",
            "useNavigate",
            "useNavigation",
            "useParams",
            "useSearchParams",
            "useEffect",
            "useRef",
        ),
        "combat": (
            "deriveRank",
            "GitCoinIcon",
            "home-profile-panel",
            "home-profile-view",
            "home-rank-view",
            "RankBadge",
            "RANK_TIERS",
            "Navigate",
            "useLearnedSkills",
            "useLocation",
            "useNavigate",
            "useNavigation",
            "useParams",
            "usePlayerLoadout",
            "useSearchParams",
        ),
        "status": (
            "Navigate",
            "useEffect",
            "useLearnedSkills",
            "useLocation",
            "useNavigate",
            "useNavigation",
            "useParams",
            "usePlayerLoadout",
            "useSearchParams",
            "useState",
        ),
        "contract": (),
    }[role]
    for marker in role_forbidden_markers:
        if re.search(rf"\b{re.escape(marker)}\b", source):
            violations.append(f"{path_label}: Home Hub {role} must not own {marker}")

    if role == "hub":
        loadout_calls = len(re.findall(r"\busePlayerLoadout\s*\(", source))
        if loadout_calls != 1:
            violations.append(
                f"{path_label}: Hub must invoke usePlayerLoadout exactly once"
            )
        loadout_binding = re.search(
            r"\bconst\s*\{(?P<body>[^}]*)\}\s*=\s*usePlayerLoadout\s*\(",
            source,
            re.S,
        )
        required_loadout_bindings = {
            "companion",
            "companionSlug",
            "hasCompanion",
            "isError",
            "isLoading",
        }
        if loadout_binding is None:
            violations.append(
                f"{path_label}: Hub must destructure usePlayerLoadout immediately"
            )
        else:
            loadout_names = {
                binding.split(":", 1)[0].split("=", 1)[0].strip()
                for binding in loadout_binding.group("body").split(",")
                if binding.strip()
            }
            if not required_loadout_bindings <= loadout_names:
                violations.append(
                    f"{path_label}: Hub must destructure the complete companion-presence contract"
                )
        workspace_module = HOME_PROFILE_WORKSPACE.removesuffix(".tsx")
        if canonical_modules.count(workspace_module) != 1:
            violations.append(
                f"{path_label}: Hub must import HomeProfileWorkspace exactly once"
            )
        if len(re.findall(r"<HomeProfileWorkspace\b", source)) != 1:
            violations.append(
                f"{path_label}: Hub must render HomeProfileWorkspace exactly once"
            )
        workspace_props, _ = jsx_component_props(source, "HomeProfileWorkspace")
        expected_workspace_props = [
            "home",
            "stats",
            "playerName",
            "gitcoins",
            "hidden",
            "companion",
        ]
        if workspace_props != expected_workspace_props:
            violations.append(
                f"{path_label}: Hub must pass only narrow Profile workspace props"
            )
        if destructured_function_props(source, "HomeHubView") != [
            "home",
            "stats",
            "playerName",
            "gitcoins",
        ]:
            violations.append(
                f"{path_label}: Hub must keep the production four-prop contract"
            )

    if role == "workspace":
        for hook in ("useLearnedSkills",):
            if len(re.findall(rf"\b{hook}\s*\(", source)) != 1:
                violations.append(
                    f"{path_label}: workspace must invoke {hook} exactly once"
                )
            if re.search(rf"\bconst\s+[A-Za-z_$][\w$]*\s*=\s*{hook}\s*\(", source):
                violations.append(
                    f"{path_label}: workspace must destructure {hook} immediately"
                )
        if "home-ref-grid" not in source:
            violations.append(
                f"{path_label}: workspace must own the home-ref-grid root"
            )
        for child in ("HomeProfilePanel", "HomeCombatShowcase"):
            if len(re.findall(rf"<{child}\b", source)) != 1:
                violations.append(
                    f"{path_label}: workspace must render {child} exactly once"
                )
        if re.search(
            r"\{\s*\.\.\.|\b(?:query|loadout|controller|integration|render[A-Z]\w*)\s*=",
            source,
        ):
            violations.append(
                f"{path_label}: workspace must pass narrow data props, not integration objects"
            )

    if role == "status":
        router_modules = [
            module
            for module in modules
            if module == "react-router-dom"
        ]
        exact_link_imports = len(
            re.findall(
                r"\bimport\s*\{\s*Link\s*\}\s*from\s*['\"]react-router-dom['\"]",
                source,
            )
        )
        if router_modules and not (
            len(router_modules) == 1 and exact_link_imports == 1
        ):
            violations.append(
                f"{path_label}: Home Hub {role} may import only static Link from react-router-dom"
            )

    if role == "profile":
        for required_marker in (
            "home-profile-panel",
            "home-profile-view",
            "home-rank-view",
        ):
            if required_marker not in source:
                violations.append(
                    f"{path_label}: Profile panel must own {required_marker}"
                )

    if role == "combat":
        for required_marker in (
            "clearTimeout",
            "effectForSkill",
            "effectPlacementForSkill",
            "homeGroundPoint",
            "home-spellbook-panel",
            "home-sprite-panel",
            "setTimeout",
            "SpriteAnimator",
        ):
            if not re.search(rf"\b{re.escape(required_marker)}\b", source):
                violations.append(
                    f"{path_label}: Combat showcase must own {required_marker}"
                )

    if role == "status":
        for required_marker in (
            "HomeProfileCompanionStatus",
            "HomeCombatCompanionStatus",
            "home-profile-companion-empty",
            "home-sprite-stage--empty",
        ):
            if required_marker not in source:
                violations.append(
                    f"{path_label}: Companion status must own {required_marker}"
                )

    if role == "contract":
        without_comments = strip_ts_comments(source)
        expected_contract = """import type { CompanionDef } from '@/shared/cosmetics/types'

export type CompanionPresentation =
  | { status: 'loading' | 'error' | 'empty' }
  | { status: 'ready'; definition: CompanionDef; slug: string }

export type UnresolvedCompanionPresentation = Exclude<
  CompanionPresentation,
  { status: 'ready' }
>
"""
        if ts_value_module_references(without_comments):
            violations.append(
                f"{path_label}: companion presentation contract must use type-only imports"
            )
        if re.search(
            r"\b(?:const|let|var|function|class|enum|namespace)\b",
            without_comments,
        ):
            violations.append(
                f"{path_label}: companion presentation contract must remain type-only"
            )
        if re.sub(r"\s+", " ", without_comments).strip() != re.sub(
            r"\s+", " ", expected_contract
        ).strip():
            violations.append(
                f"{path_label}: companion presentation contract must contain only the canonical type-only union"
            )
        for required_marker in (
            "export type CompanionPresentation",
            "export type UnresolvedCompanionPresentation",
        ):
            if required_marker not in without_comments:
                violations.append(
                    f"{path_label}: companion presentation contract must own {required_marker}"
                )

    return violations


def home_hub_hook_owner_violations(sources: dict[str, str]) -> list[str]:
    """Require one direct module owner and invocation for each Home integration hook."""

    violations: list[str] = []
    expected_owners = {
        "usePlayerLoadout": (
            HOME_HUB_VIEW,
            "frontend/src/shared/player-loadout/usePlayerLoadout",
        ),
        "useLearnedSkills": (
            HOME_PROFILE_WORKSPACE,
            "frontend/src/features/skills/hooks/useLearnedSkills",
        ),
    }
    for hook, (expected_path, module) in expected_owners.items():
        observed_imports: list[tuple[str, int]] = []
        observed_calls: list[tuple[str, int]] = []
        for path, source in sources.items():
            analyzed_source = strip_ts_comments(source)
            canonical_modules = [
                canonical_ts_module_reference(module=candidate, path_label=path)
                for candidate in ts_module_specifiers(analyzed_source)
            ]
            import_count = canonical_modules.count(module)
            if import_count:
                observed_imports.append((path, import_count))

            local_bindings = ts_named_import_bindings(
                analyzed_source,
                path_label=path,
                module=module,
                exported_names={hook},
            )
            call_sites = {
                match.start()
                for binding in local_bindings
                for match in re.finditer(
                    rf"\b{re.escape(binding)}\s*\(", analyzed_source
                )
            }
            namespace_bindings = ts_namespace_import_bindings(
                analyzed_source,
                path_label=path,
                module=module,
            )
            call_sites.update(
                match.start()
                for binding in namespace_bindings
                for match in re.finditer(
                    rf"\b{re.escape(binding)}\s*\.\s*{re.escape(hook)}\s*\(",
                    analyzed_source,
                )
            )
            if hook not in local_bindings:
                for match in re.finditer(rf"\b{hook}\s*\(", analyzed_source):
                    if re.search(r"\.\s*$", analyzed_source[: match.start()]):
                        continue
                    call_sites.add(match.start())
            call_count = len(call_sites)
            if call_count:
                observed_calls.append((path, call_count))

        observed_imports.sort()
        observed_calls.sort()
        if observed_imports != [(expected_path, 1)]:
            violations.append(
                f"Home Hub {hook} import ownership must be exactly {expected_path}; "
                f"found {observed_imports}"
            )
        if observed_calls != [(expected_path, 1)]:
            violations.append(
                f"Home Hub {hook} call ownership must be exactly {expected_path}; "
                f"found {observed_calls}"
            )
    return violations


def check_home_hub_profile_ownership() -> list[str]:
    violations: list[str] = []
    targets = (
        (ROOT / HOME_HUB_VIEW, "hub"),
        (ROOT / HOME_PROFILE_WORKSPACE, "workspace"),
        (ROOT / HOME_PROFILE_PANEL, "profile"),
        (ROOT / HOME_COMBAT_SHOWCASE, "combat"),
        (ROOT / HOME_COMPANION_STATUS, "status"),
        (ROOT / HOME_COMPANION_PRESENTATION, "contract"),
    )
    for path, role in targets:
        if not path.exists():
            violations.append(f"{rel(path)}: required Home Hub {role} owner is missing")
            continue
        violations.extend(
            home_hub_source_violations(
                source=path.read_text(encoding="utf-8"),
                path_label=rel(path),
                role=role,
            )
        )
    home_sources = {
        rel(path): path.read_text(encoding="utf-8")
        for path in iter_files(
            ROOT / "frontend/src/features/home",
            TS_SUFFIXES,
        )
        if ".test." not in path.name and ".stories." not in path.name
    }
    violations.extend(home_hub_hook_owner_violations(home_sources))
    return violations


def home_overview_source_violations(
    *,
    source: str,
    path_label: str,
    role: str,
) -> list[str]:
    """Enforce Home Overview composition, model, and rendering ownership."""

    violations: list[str] = []
    line_count = len(source.splitlines())
    limit = HOME_STATS_LINE_LIMITS[role]
    if line_count > limit:
        violations.append(
            f"{path_label}: Home Overview {role} has {line_count} lines; limit is {limit}"
        )

    direct_data_modules = (
        "@tanstack/react-query",
        "frontend/src/features/home/api",
        "frontend/src/features/stats/api",
        "frontend/src/shared/api",
    )
    reverse_modules = (
        "frontend/src/features/home/components/HomeHubView",
        "frontend/src/features/home/pages/HomePage",
    )
    forbidden_modules = {
        "composition": direct_data_modules,
        "model": (
            *direct_data_modules,
            *reverse_modules,
            "react",
            "react-router-dom",
            "lucide-react",
            "frontend/src/features/home/components",
        ),
        "dashboard": (
            *direct_data_modules,
            *reverse_modules,
            "react-router-dom",
            "frontend/src/features/home/components/HomeStatsView",
            "frontend/src/features/home/types",
            "frontend/src/features/home/utils/achievements",
            "frontend/src/features/stats/types",
        ),
        "gallery": (
            *direct_data_modules,
            *reverse_modules,
            "react-router-dom",
            "frontend/src/features/home/components/HomeStatsView",
            "frontend/src/features/home/types",
            "frontend/src/features/stats/types",
        ),
    }[role]

    modules = ts_module_specifiers(source)
    canonical_modules = [
        canonical_ts_module_reference(module=module, path_label=path_label)
        for module in modules
    ]
    for module, canonical_module in zip(modules, canonical_modules, strict=True):
        if any(
            ts_module_matches_boundary(canonical_module, boundary)
            for boundary in forbidden_modules
        ):
            violations.append(
                f"{path_label}: Home Overview {role} must not import {module}"
            )

    required_imports = {
        "composition": (
            HOME_STATS_MODEL.removesuffix(".ts"),
            HOME_STATS_DASHBOARD.removesuffix(".tsx"),
            HOME_ACHIEVEMENT_GALLERY.removesuffix(".tsx"),
        ),
        "model": (
            "frontend/src/features/home/types",
            "frontend/src/features/home/utils/achievements",
            "frontend/src/features/stats/types",
        ),
        "dashboard": (HOME_STATS_MODEL.removesuffix(".ts"),),
        "gallery": ("frontend/src/features/home/utils/achievements",),
    }[role]
    for required in required_imports:
        if canonical_modules.count(required) != 1:
            violations.append(
                f"{path_label}: Home Overview {role} must import {required} exactly once"
            )

    forbidden_markers = {
        "composition": (
            "ACHIEVEMENT_FILTERS",
            "AchievementFilter",
            "ActivityHeatmap",
            "GitCommandIcon",
            "SkillProfileBars",
            "deriveAchievements",
            "home-overview-achievements-panel",
            "home-overview-stats-panel",
            "useState",
        ),
        "model": (
            "Link",
            "document",
            "home-overview-",
            "useEffect",
            "useMemo",
            "useState",
            "window",
        ),
        "dashboard": (
            "AchievementFilter",
            "HomeSummary",
            "StatsSummary",
            "buildHomeStatsModel",
            "deriveAchievements",
            "home-overview-achievement-card",
            "home-overview-achievements-panel",
            "useState",
        ),
        "gallery": (
            "ActivityHeatmap",
            "GitCommandIcon",
            "HomeSummary",
            "SkillProfileBars",
            "StatsSummary",
            "buildHomeStatsModel",
            "deriveAchievements",
            "home-overview-activity",
            "home-overview-command",
            "home-overview-kpi",
            "home-overview-stats-panel",
            "home-overview-story",
        ),
    }[role]
    for marker in forbidden_markers:
        owns_marker = (
            bool(re.search(rf"\b{re.escape(marker)}\b", source))
            if marker.isidentifier()
            else marker in source
        )
        if owns_marker:
            violations.append(
                f"{path_label}: Home Overview {role} must not own {marker}"
            )

    if re.search(r"<[A-Z][A-Za-z0-9]*\b[^>]*\{\s*\.\.\.", source, re.S):
        violations.append(
            f"{path_label}: Home Overview owners must not spread objects across component boundaries"
        )
    if re.search(r"\brender[A-Z][A-Za-z0-9]*\s*=", source):
        violations.append(
            f"{path_label}: Home Overview owners must not accept render props"
        )

    if role == "composition":
        required_calls = {
            "useMemo": len(re.findall(r"\buseMemo\s*\(", source)),
            "buildHomeStatsModel": len(
                re.findall(r"\bbuildHomeStatsModel\s*\(", source)
            ),
            "HomeStatsDashboard render": len(
                re.findall(r"<HomeStatsDashboard\b", source)
            ),
            "HomeAchievementGallery render": len(
                re.findall(r"<HomeAchievementGallery\b", source)
            ),
        }
        for marker, count in required_calls.items():
            if count != 1:
                violations.append(
                    f"{path_label}: composition must own exactly one {marker}; found {count}"
                )
        if source.count("home-overview-grid") != 1:
            violations.append(
                f"{path_label}: composition must own the home-overview-grid root exactly once"
            )
        for component, prop in (
            ("HomeStatsDashboard", "dashboard"),
            ("HomeAchievementGallery", "achievements"),
        ):
            prop_names, tag_body = jsx_component_props(source, component)
            if prop_names != [prop] or f"{prop}={{model.{prop}}}" not in tag_body:
                violations.append(
                    f"{path_label}: {component} must receive only {prop} from the matching model slice"
                )

    if role == "model":
        for exported_type in ("HomeStatsModel", "HomeStatsDashboardModel"):
            if not re.search(rf"\bexport\s+type\s+{exported_type}\b", source):
                violations.append(f"{path_label}: model must export {exported_type}")
        achievement_value_references = [
            module
            for module in ts_value_module_references(source)
            if ts_module_matches_boundary(
                canonical_ts_module_reference(module=module, path_label=path_label),
                "frontend/src/features/home/utils/achievements",
            )
        ]
        if len(achievement_value_references) != 1:
            violations.append(
                f"{path_label}: model must own exactly one runtime achievement-ledger import"
            )

    if role == "dashboard":
        if (
            destructured_function_props(source, "HomeStatsDashboard") != ["dashboard"]
            or "HomeStatsDashboardModel" not in source
        ):
            violations.append(
                f"{path_label}: dashboard must expose only the named dashboard model prop"
            )
        for marker in (
            "GitCommandIcon",
            "SkillProfileBars",
            "ActivityHeatmap",
            "home-overview-stats-panel",
        ):
            if marker not in source:
                violations.append(f"{path_label}: dashboard must own {marker}")
        if re.search(
            r"\(\s*\{[^}]*\b(?:home|stats)\b[^}]*\}\s*(?::|,|\))",
            source,
        ):
            violations.append(
                f"{path_label}: dashboard must not receive raw home or stats summaries"
            )

    if role == "gallery":
        if destructured_function_props(source, "HomeAchievementGallery") != [
            "achievements"
        ] or not re.search(r"\bAchievement\s*\[\s*\]", source):
            violations.append(
                f"{path_label}: gallery must expose only the named Achievement[] prop"
            )
        for marker in (
            "useState",
            "ACHIEVEMENT_FILTERS",
            "home-overview-achievements-panel",
            "home-overview-achievement-card",
        ):
            if marker not in source:
                violations.append(f"{path_label}: gallery must own {marker}")
        if re.search(
            r"\(\s*\{[^}]*\b(?:home|stats)\b[^}]*\}\s*(?::|,|\))",
            source,
        ):
            violations.append(
                f"{path_label}: gallery must not receive raw home or stats summaries"
            )
    return violations


def css_top_level_rule_headers(source: str) -> list[str]:
    """Return CSS rule and at-rule headers that open at top level."""

    clean = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    headers: list[str] = []
    depth = 0
    start = 0
    for index, character in enumerate(clean):
        if character == "{" and depth == 0:
            header = clean[start:index].strip()
            if header:
                headers.append(header)
            depth = 1
        elif character == "{":
            depth += 1
        elif character == "}" and depth:
            depth -= 1
            if depth == 0:
                start = index + 1
        elif character == ";" and depth == 0:
            start = index + 1
    return headers


def css_selector_list(header: str) -> list[str]:
    """Split a selector list on top-level commas without breaking functional selectors."""

    selectors: list[str] = []
    depth = 0
    start = 0
    for index, character in enumerate(header):
        if character in "([":
            depth += 1
        elif character in ")]" and depth:
            depth -= 1
        elif character == "," and depth == 0:
            selectors.append(header[start:index].strip())
            start = index + 1
    selectors.append(header[start:].strip())
    return [selector for selector in selectors if selector]


def css_has_top_level_selector(source: str, selector: str, *, exact: bool) -> bool:
    """Match a selector branch at top level, including grouped selector lists."""

    selector_token = re.compile(rf"{re.escape(selector)}(?![\w-])")
    for header in css_top_level_rule_headers(source):
        if header.startswith("@"):
            continue
        for branch in css_selector_list(header):
            matches = (
                branch == selector if exact else bool(selector_token.search(branch))
            )
            if matches:
                return True
    return False


def css_import_specifiers(source: str) -> list[str]:
    return re.findall(r"@import\s+['\"]([^'\"]+)['\"]\s*;", source)


def home_overview_css_source_violations(
    *,
    source: str,
    path_label: str,
    role: str,
) -> list[str]:
    """Enforce canonical Home Overview entry and selector ownership."""

    violations: list[str] = []
    legacy_selector = re.search(
        r"\.home-(?:stats-|stat-|meter-|activity-|awards\b|award-)",
        source,
    )
    if legacy_selector:
        violations.append(
            f"{path_label}: displaced legacy Home selector {legacy_selector.group(0)} must stay deleted"
        )

    imports = css_import_specifiers(source)
    if role == "home-entry":
        if imports.count("./home/stats.css") != 1:
            violations.append(
                f"{path_label}: home entry must import ./home/stats.css exactly once"
            )
        for displaced in ("./home/achievements.css", "./home/stats-actions.css"):
            if displaced in imports:
                violations.append(f"{path_label}: must not import deleted {displaced}")
    elif role == "stats-entry":
        expected = [
            "./stats-layout.css",
            "./stats-achievements.css",
            "./stats-responsive.css",
            "./continue-card.css",
        ]
        if imports != expected:
            violations.append(
                f"{path_label}: stats entry imports must be exactly {expected}; found {imports}"
            )
    elif role == "achievements":
        if not css_has_top_level_selector(
            source,
            ".home-overview-achievement-card",
            exact=True,
        ):
            violations.append(
                f"{path_label}: stats-achievements must own the base achievement-card rule"
            )
    elif role == "responsive":
        headers = css_top_level_rule_headers(source)
        if not headers or any(not header.startswith("@media") for header in headers):
            violations.append(
                f"{path_label}: stats-responsive may contain breakpoint rules only"
            )
    elif role == "scan":
        owner = "frontend/src/styles/features/home/stats-achievements.css"
        if path_label != owner and css_has_top_level_selector(
            source,
            ".home-overview-achievement-card",
            exact=False,
        ):
            violations.append(
                f"{path_label}: base achievement-card selector belongs in stats-achievements.css"
            )
    return violations


def home_overview_achievement_import_violations(
    *,
    source: str,
    path_label: str,
) -> list[str]:
    """Keep every runtime achievement-ledger import in the pure model owner."""

    if path_label == HOME_STATS_MODEL:
        return []
    achievement_module = "frontend/src/features/home/utils/achievements"
    return [
        f"{path_label}: only homeStatsModel may runtime-import the achievement ledger via {module}"
        for module in ts_value_module_references(source)
        if ts_module_matches_boundary(
            canonical_ts_module_reference(module=module, path_label=path_label),
            achievement_module,
        )
    ]


def check_home_overview_ownership() -> list[str]:
    violations: list[str] = []
    targets = (
        (ROOT / HOME_STATS_VIEW, "composition"),
        (ROOT / HOME_STATS_MODEL, "model"),
        (ROOT / HOME_STATS_DASHBOARD, "dashboard"),
        (ROOT / HOME_ACHIEVEMENT_GALLERY, "gallery"),
    )
    expected_production_paths = {rel(path) for path, _ in targets}
    for path, role in targets:
        if not path.exists():
            violations.append(
                f"{rel(path)}: required Home Overview {role} owner is missing"
            )
            continue
        violations.extend(
            home_overview_source_violations(
                source=path.read_text(encoding="utf-8"),
                path_label=rel(path),
                role=role,
            )
        )

    owner_dir = ROOT / HOME_STATS_MODEL.rpartition("/")[0]
    for path in iter_files(owner_dir, TS_SUFFIXES):
        path_rel = rel(path)
        if ".test." not in path.name and path_rel not in expected_production_paths:
            violations.append(
                f"{path_rel}: unexpected Home Overview production owner; avoid compatibility paths"
            )

    child_modules = {
        HOME_STATS_MODEL.removesuffix(".ts"),
        HOME_STATS_DASHBOARD.removesuffix(".tsx"),
        HOME_ACHIEVEMENT_GALLERY.removesuffix(".tsx"),
    }
    allowed_child_edges = {
        HOME_STATS_VIEW: child_modules,
        HOME_STATS_DASHBOARD: {HOME_STATS_MODEL.removesuffix(".ts")},
    }
    achievement_utility = "frontend/src/features/home/utils/achievements.ts"
    for path in iter_files(FRONTEND_SRC, TS_SUFFIXES):
        path_rel = rel(path)
        if ".test." in path.name:
            continue
        source = path.read_text(encoding="utf-8", errors="ignore")
        violations.extend(
            home_overview_achievement_import_violations(
                source=source,
                path_label=path_rel,
            )
        )
        allowed = allowed_child_edges.get(path_rel, set())
        for module in ts_module_specifiers(source):
            canonical = canonical_ts_module_reference(
                module=module, path_label=path_rel
            )
            if canonical in child_modules and canonical not in allowed:
                violations.append(
                    f"{path_rel}: must not import Home Overview child owner {module}"
                )

    css_targets = (
        (ROOT / "frontend/src/styles/features/home.css", "home-entry"),
        (ROOT / "frontend/src/styles/features/home/stats.css", "stats-entry"),
        (
            ROOT / "frontend/src/styles/features/home/stats-achievements.css",
            "achievements",
        ),
        (ROOT / "frontend/src/styles/features/home/stats-responsive.css", "responsive"),
    )
    for path, role in css_targets:
        if not path.exists():
            violations.append(
                f"{rel(path)}: required Home Overview CSS {role} owner is missing"
            )
            continue
        violations.extend(
            home_overview_css_source_violations(
                source=path.read_text(encoding="utf-8"),
                path_label=rel(path),
                role=role,
            )
        )

    for displaced in sorted(HOME_STATS_DISPLACED_CSS):
        if (ROOT / displaced).exists():
            violations.append(
                f"{displaced}: displaced Home Overview CSS must stay deleted"
            )

    for path in iter_files(FRONTEND_SRC / "styles", {".css"}):
        source = path.read_text(encoding="utf-8", errors="ignore")
        violations.extend(
            home_overview_css_source_violations(
                source=source,
                path_label=rel(path),
                role="scan",
            )
        )

    achievements_path = ROOT / achievement_utility
    if (
        achievements_path.exists()
        and "latestAchievement" in achievements_path.read_text(encoding="utf-8")
    ):
        violations.append(
            f"{achievement_utility}: displaced latestAchievement helper must stay deleted"
        )
    return violations


def check_shared_has_no_feature_imports() -> list[str]:
    violations: list[str] = []
    shared = FRONTEND_SRC / "shared"
    for path in iter_files(shared, TS_SUFFIXES):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if SHARED_FEATURE_IMPORT.search(line):
                violations.append(
                    f"{rel(path)}:{lineno}: shared code must not import feature code: {line.strip()}"
                )
    return violations


def check_non_pages_do_not_import_pages() -> list[str]:
    violations: list[str] = []
    for path in iter_files(FRONTEND_SRC / "features", TS_SUFFIXES):
        if "/pages/" in rel(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if PAGE_IMPORT.search(line):
                violations.append(
                    f"{rel(path)}:{lineno}: only the router/page files may import feature pages: {line.strip()}"
                )
    return violations


def check_backend_frontend_references_are_allowlisted() -> list[str]:
    violations: list[str] = []
    for path in iter_files(BACKEND, PY_SUFFIXES):
        path_rel = rel(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if (
                FRONTEND_PATH_REFERENCE.search(line)
                and path_rel not in BACKEND_FRONTEND_ALLOWLIST
            ):
                violations.append(
                    f"{path_rel}:{lineno}: backend code must not depend on frontend files: {line.strip()}"
                )
    return violations


def check_frontend_feature_shape() -> list[str]:
    violations: list[str] = []
    features = FRONTEND_SRC / "features"
    if not features.exists():
        return violations
    for feature in sorted(path for path in features.iterdir() if path.is_dir()):
        for child in sorted(path for path in feature.iterdir() if path.is_dir()):
            if child.name not in ALLOWED_FEATURE_DIRS:
                violations.append(
                    f"{rel(child)}: feature folders must use the standard api/components/hooks/pages/utils shape"
                )
    return violations


def check_frontend_feature_roots_are_thin() -> list[str]:
    violations: list[str] = []
    features = FRONTEND_SRC / "features"
    if not features.exists():
        return violations
    for feature in sorted(path for path in features.iterdir() if path.is_dir()):
        for child in sorted(
            path
            for path in feature.iterdir()
            if path.is_file() and path.suffix in TS_SUFFIXES
        ):
            if child.name not in ROOT_FEATURE_ALLOWED_FILES:
                violations.append(
                    f"{rel(child)}: feature root files must be limited to types.ts/index.ts; move code into api/components/hooks/pages/utils"
                )
    return violations


def check_frontend_production_files_are_reviewable() -> list[str]:
    violations: list[str] = []
    for path in iter_files(FRONTEND_SRC, TS_SUFFIXES):
        path_rel = rel(path)
        if any(part in {"generated", "__fixtures__"} for part in path.parts):
            continue
        if path.name.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")):
            continue
        line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
        if line_count > FRONTEND_PRODUCTION_FILE_MAX_LINES:
            violations.append(
                f"{path_rel}: production frontend module has {line_count} lines; split visual/runtime responsibilities into focused child modules"
            )
    return violations


def check_backend_service_and_selector_packages() -> list[str]:
    violations: list[str] = []
    for app_dir in sorted(path for path in BACKEND.iterdir() if path.is_dir()):
        if not (app_dir / "apps.py").exists():
            continue
        for module_name in ("services", "selectors"):
            flat = app_dir / f"{module_name}.py"
            if flat.exists():
                violations.append(
                    f"{rel(flat)}: backend {module_name} layer must be a package, not a flat module"
                )
    return violations


def check_backend_layer_package_inits_are_thin() -> list[str]:
    violations: list[str] = []
    for app_dir in sorted(path for path in BACKEND.iterdir() if path.is_dir()):
        if not (app_dir / "apps.py").exists():
            continue
        for module_name in ("services", "selectors", "views"):
            init_path = app_dir / module_name / "__init__.py"
            if not init_path.exists():
                continue
            line_count = len(
                init_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
            if line_count > THIN_BACKEND_PACKAGE_INIT_MAX_LINES:
                violations.append(
                    f"{rel(init_path)}: package initializer has {line_count} lines; move implementation into named modules and keep __init__.py as exports only"
                )
    return violations


def check_backend_common_shape() -> list[str]:
    violations: list[str] = []
    common = BACKEND / "common"
    for filename in sorted(COMMON_ROOT_FORBIDDEN_MODULES):
        path = common / filename
        if path.exists():
            violations.append(
                f"{rel(path)}: common git/schema/service modules must live under common/git, common/schemas, or common/services"
            )
    for directory in [common / "git", common / "schemas", common / "services"]:
        if not directory.exists() or not (directory / "__init__.py").exists():
            violations.append(
                f"{rel(directory)}: required common subpackage is missing"
            )
    return violations


def check_backend_service_packages() -> list[str]:
    violations: list[str] = []
    for app in sorted(SERVICE_PACKAGE_APPS):
        file_path = BACKEND / app / "services.py"
        package_path = BACKEND / app / "services" / "__init__.py"
        if file_path.exists():
            violations.append(
                f"{rel(file_path)}: service layer must be a package, not a flat services.py file"
            )
        if not package_path.exists():
            violations.append(
                f"{rel(package_path)}: expected service package entrypoint"
            )
    return violations


def check_curriculum_seed_public_modules_are_thin() -> list[str]:
    violations: list[str] = []
    seed_data = BACKEND / "curriculum" / "seed_data"
    expected_partitions = {
        "adventure_levels": seed_data / "source" / "adventure_level_specs",
        "challenges": seed_data / "source" / "challenge_specs",
        "blueprint_overlay": seed_data / "source" / "blueprint",
    }
    for module_name, partition_dir in expected_partitions.items():
        public_module = seed_data / f"{module_name}.py"
        source_module = seed_data / "source" / f"{module_name}.py"
        if not public_module.exists() or not source_module.exists():
            violations.append(
                f"backend/curriculum/seed_data/{module_name}.py: expected thin public wrapper plus source/{module_name}.py compatibility module"
            )
            continue
        for module_path, label in (
            (public_module, "public"),
            (source_module, "source compatibility"),
        ):
            line_count = len(
                module_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            )
            if line_count > 50:
                violations.append(
                    f"{rel(module_path)}: {label} seed-data module has {line_count} lines; keep authored data in partitioned source packages"
                )
        if not partition_dir.exists() or not (partition_dir / "__init__.py").exists():
            violations.append(
                f"{rel(partition_dir)}: expected partitioned authored seed-data package for {module_name}"
            )
    return violations


def main() -> int:
    violations = [
        *check_shared_has_no_feature_imports(),
        *check_non_pages_do_not_import_pages(),
        *check_backend_frontend_references_are_allowlisted(),
        *check_frontend_feature_shape(),
        *check_frontend_feature_roots_are_thin(),
        *check_frontend_production_files_are_reviewable(),
        *check_content_editor_workflow_ownership(),
        *check_home_hub_profile_ownership(),
        *check_home_overview_ownership(),
        *check_stats_summary_contract_ownership(),
        *check_dashboard_summary_contract_ownership(),
        *check_auth_contract_ownership(),
        *check_catalog_contract_ownership(),
        *check_gameplay_mutation_contract_ownership(),
        *check_gameplay_response_contract_ownership(),
        *check_backend_service_and_selector_packages(),
        *check_backend_layer_package_inits_are_thin(),
        *check_backend_common_shape(),
        *check_backend_service_packages(),
        *check_curriculum_seed_public_modules_are_thin(),
        *check_adminconsole_http_read_ownership(),
        *check_adminconsole_selectors_are_http_free(),
        *check_backend_runtime_import_cycles(),
        *check_displaced_backend_paths_are_absent(),
    ]
    if violations:
        print("Architecture boundary violations found:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        print(
            "\nRules: shared cannot import features; non-page feature modules cannot import pages; "
            "backend runtime code cannot inspect frontend source/assets or form import cycles; "
            "feature folders and backend service/common layers must keep the normalized shape; "
            "Dashboard summary API contract ownership must stay generated through Home shims; "
            "Stats summary API contract ownership must stay generated and one-way; "
            "Auth success contracts must stay account-owned, generated, and one-way; "
            "gameplay mutation request contracts must stay shared, generated, and one-way; "
            "gameplay success response contracts must stay domain-owned, exact, generated, and one-way; "
            "Home Overview workflow ownership must stay one-way; "
            "content editor and Home Hub workflow ownership must stay one-way; displaced architecture paths "
            "must stay deleted.",
            file=sys.stderr,
        )
        return 1
    print("Architecture boundaries look clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
