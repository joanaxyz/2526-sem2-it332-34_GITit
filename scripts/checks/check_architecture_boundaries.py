#!/usr/bin/env python3
"""Fail CI when project layers import across forbidden boundaries.

This guard intentionally checks only high-signal rules that the current codebase
can satisfy. It prevents new architecture sediment without requiring a risky
folder rewrite.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_SRC = ROOT / "frontend" / "src"
BACKEND = ROOT / "backend"

TS_SUFFIXES = {".ts", ".tsx"}
PY_SUFFIXES = {".py"}

SHARED_FEATURE_IMPORT = re.compile(r"@/features/")
PAGE_IMPORT = re.compile(r"@/features/[^'\"]+/pages/")
FRONTEND_PATH_REFERENCE = re.compile(r"frontend/(?:src|public|scripts)")

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
SERVICE_PACKAGE_APPS = {path.name for path in BACKEND.iterdir() if path.is_dir() and (path / "apps.py").exists()}
ROOT_FEATURE_ALLOWED_FILES = {"types.ts", "index.ts"}
THIN_BACKEND_PACKAGE_INIT_MAX_LINES = 100
FRONTEND_PRODUCTION_FILE_MAX_LINES = 400



def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_files(root: Path, suffixes: set[str]) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        if any(part in {"node_modules", "dist", "build", "__pycache__", ".venv"} for part in path.parts):
            continue
        out.append(path)
    return out


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
            if FRONTEND_PATH_REFERENCE.search(line) and path_rel not in BACKEND_FRONTEND_ALLOWLIST:
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
        for child in sorted(path for path in feature.iterdir() if path.is_file() and path.suffix in TS_SUFFIXES):
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
        for module_name in ("services", "selectors"):
            init_path = app_dir / module_name / "__init__.py"
            if not init_path.exists():
                continue
            line_count = len(init_path.read_text(encoding="utf-8", errors="ignore").splitlines())
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
            violations.append(f"{rel(directory)}: required common subpackage is missing")
    return violations


def check_backend_service_packages() -> list[str]:
    violations: list[str] = []
    for app in sorted(SERVICE_PACKAGE_APPS):
        file_path = BACKEND / app / "services.py"
        package_path = BACKEND / app / "services" / "__init__.py"
        if file_path.exists():
            violations.append(f"{rel(file_path)}: service layer must be a package, not a flat services.py file")
        if not package_path.exists():
            violations.append(f"{rel(package_path)}: expected service package entrypoint")
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
        for module_path, label in ((public_module, "public"), (source_module, "source compatibility")):
            line_count = len(module_path.read_text(encoding="utf-8", errors="ignore").splitlines())
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
        *check_backend_service_and_selector_packages(),
        *check_backend_layer_package_inits_are_thin(),
        *check_backend_common_shape(),
        *check_backend_service_packages(),
        *check_curriculum_seed_public_modules_are_thin(),
    ]
    if violations:
        print("Architecture boundary violations found:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        print(
            "\nRules: shared cannot import features; non-page feature modules cannot import pages; "
            "backend runtime code cannot inspect frontend source/assets; feature folders and backend service/common layers must keep the normalized shape.",
            file=sys.stderr,
        )
        return 1
    print("Architecture boundaries look clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
