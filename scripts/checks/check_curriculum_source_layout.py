#!/usr/bin/env python3
"""Enforce maintainable ownership boundaries in authored curriculum source."""

from __future__ import annotations

import ast
import os
from pathlib import Path
import sys

try:
    from scripts.checks.adventure_plan_ownership import (
        adventure_plan_ownership_errors,
    )
except ModuleNotFoundError:  # Direct `python scripts/checks/...` execution.
    from adventure_plan_ownership import adventure_plan_ownership_errors


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_SOURCE = ROOT / "backend/curriculum/seed_data/source/blueprint"
REPOSITORY_FOUNDATIONS_COMPOSER = (
    BLUEPRINT_SOURCE / "adventure_repository_foundations.py"
)
REPOSITORY_FOUNDATIONS_PACKAGE = BLUEPRINT_SOURCE / "repository_foundations"
FROST_MONOLITH = (
    ROOT
    / "backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py"
)
FROST_PACKAGE = FROST_MONOLITH.with_suffix("")
FROST_IMPORT_SCAN_ROOTS = (ROOT / "backend", ROOT / "scripts")
FROST_IMPORT_EXCLUDED_DIRS = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tmp",
    ".venv",
    "__pycache__",
    "node_modules",
    "temp",
    "tmp",
    "venv",
}

COMPOSER_MAX_LINES = 50
LEAF_MAX_LINES = 700
REPOSITORY_FOUNDATIONS_GROUPS = (
    (
        "fresh_starts",
        (
            "start-a-repository",
            "read-the-workspace",
            "stage-and-commit",
            "the-first-snapshot",
            "practice-fresh-starts",
        ),
    ),
    (
        "history_and_status",
        (
            "read-history",
            "inspect-commits",
            "history-details",
            "status-at-a-glance",
        ),
    ),
    (
        "cloning",
        ("copy-a-project", "inspect-what-you-cloned", "clone-drills"),
    ),
    (
        "configuration",
        ("configure-identity-and-aliases", "ignore-noise"),
    ),
    ("founding_workflows", ("founding-workflows",)),
    ("fresh_start_drills", ("fresh-start-drills",)),
    ("inspection_drills", ("inspection-drills",)),
)

FROST_CHAPTERS = (
    ("temper_the_commit", 650),
    ("choose_the_integration", 300),
    ("survive_the_conflict", 450),
    ("move_the_patch", 450),
    ("reforge_the_branch", 275),
    ("govern_the_remote", 600),
    ("deliver_the_release", 350),
    ("hunt_the_regression", 200),
    ("publish_the_core", 150),
)
FROST_FIXTURE_BINDINGS = {
    "_behind_remote",
    "_broken_dirty",
    "_cherry_conflict",
    "_conflict",
    "_dirty",
    "_meta",
    "_meta_set",
    "_rebase_paused",
    "_rebase_ready",
    "_resolved_merge",
    "_retire_remote",
    "_staged",
    "_stale_remote",
    "_stashed",
    "_work",
}
FROST_SURVIVE_LOCAL_BINDINGS = {"NO_MARKERS", "_conflict_read"}
FROST_DISPLACED_SUPPORT_BINDINGS = {
    "CORE_TAGS",
    "GRAPH",
    "STATUS",
    "_broken",
    "_clean",
    "_dv",
    "_read_eval",
    "_render_value",
    "_req",
    "_required_check",
}


def _line_count(source: str) -> int:
    return len(source.splitlines())


def _parse(path: Path, errors: list[str]) -> tuple[str, ast.Module] | None:
    if not path.is_file():
        errors.append(f"missing curriculum source module: {path.name}")
        return None
    source = path.read_text(encoding="utf-8")
    try:
        return source, ast.parse(source)
    except SyntaxError as exc:
        errors.append(f"{path.name}: invalid Python: {exc.msg} (line {exc.lineno})")
        return None


def _assignment_values(tree: ast.Module, name: str) -> list[ast.AST]:
    values: list[ast.AST] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(
            isinstance(target, ast.Name) and target.id == name for target in targets
        ):
            values.append(node.value)
    return values


def _single_direct_assignment(tree: ast.Module, name: str) -> ast.Assign | None:
    """Return one plain, single-name, module-scope assignment or ``None``."""

    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == name
    ]
    return matches[0] if len(matches) == 1 else None


def _assigned_names(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, ast.AnnAssign):
        targets = [node.target]
    else:
        return set()
    return {target.id for target in targets if isinstance(target, ast.Name)}


def _literal_slug(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Dict):
        return None
    for key, value in zip(node.keys, node.values):
        if (
            isinstance(key, ast.Constant)
            and key.value == "slug"
            and isinstance(value, ast.Constant)
            and isinstance(value.value, str)
        ):
            return value.value
    return None


def _verify_package_initializer(package_path: Path, errors: list[str]) -> None:
    parsed = _parse(package_path / "__init__.py", errors)
    if parsed is None:
        return
    _, tree = parsed
    if not (
        len(tree.body) == 1
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        errors.append(
            "repository_foundations/__init__.py must contain only a package docstring"
        )


def _verify_composer(path: Path, errors: list[str]) -> None:
    parsed = _parse(path, errors)
    if parsed is None:
        return
    source, tree = parsed
    line_count = _line_count(source)
    if line_count > COMPOSER_MAX_LINES:
        errors.append(
            f"adventure_repository_foundations.py has {line_count} lines; "
            f"maximum is {COMPOSER_MAX_LINES}"
        )
    if any(isinstance(node, ast.Dict) for node in ast.walk(tree)):
        errors.append(
            "Repository Foundations composer must not contain level dictionaries"
        )
    if any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_wave"
        for node in ast.walk(tree)
    ):
        errors.append("Repository Foundations composer must not call _wave")

    expected_imports = [
        (
            f"repository_foundations.{module}",
            "LEVELS",
            f"_{module.upper()}_LEVELS",
        )
        for module, _ in REPOSITORY_FOUNDATIONS_GROUPS
    ]
    actual_imports: list[tuple[str, str, str | None]] = []
    unexpected_imports: list[str] = []
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            continue
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 1
            and node.module is not None
            and len(node.names) == 1
        ):
            item = node.names[0]
            actual_imports.append((node.module, item.name, item.asname))
        else:
            unexpected_imports.append(ast.unparse(node))
    if actual_imports != expected_imports:
        errors.append(
            "Repository Foundations composer imports must match the canonical "
            "concept order exactly"
        )
    if unexpected_imports:
        errors.append(
            f"Repository Foundations composer has unexpected imports: {unexpected_imports}"
        )

    unexpected_statements = [
        ast.unparse(node)
        for index, node in enumerate(tree.body)
        if not (
            (
                index == 0
                and isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            )
            or isinstance(node, ast.ImportFrom)
            or _assigned_names(node) == {"ADVENTURE_LEVELS"}
        )
    ]
    if unexpected_statements:
        errors.append(
            "Repository Foundations composer has unexpected top-level ownership: "
            f"{unexpected_statements}"
        )

    assignments = _assignment_values(tree, "ADVENTURE_LEVELS")
    if len(assignments) != 1 or not isinstance(assignments[0], ast.List):
        errors.append(
            "Repository Foundations composer must define one ADVENTURE_LEVELS list"
        )
        return
    actual_aliases = [
        element.value.id
        for element in assignments[0].elts
        if isinstance(element, ast.Starred) and isinstance(element.value, ast.Name)
    ]
    expected_aliases = [alias for _, _, alias in expected_imports]
    if (
        len(actual_aliases) != len(assignments[0].elts)
        or actual_aliases != expected_aliases
    ):
        errors.append(
            "Repository Foundations composer must flatten each concept list once "
            "in canonical order"
        )


def _verify_leaf(
    path: Path, expected_slugs: tuple[str, ...], errors: list[str]
) -> list[str]:
    parsed = _parse(path, errors)
    if parsed is None:
        return []
    source, tree = parsed
    line_count = _line_count(source)
    if line_count > LEAF_MAX_LINES:
        errors.append(
            f"{path.name} has {line_count} lines; maximum is {LEAF_MAX_LINES}"
        )

    imports = [
        node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    non_future_imports = [
        node
        for node in imports
        if not (isinstance(node, ast.ImportFrom) and node.module == "__future__")
    ]
    valid_helper_import = (
        len(non_future_imports) == 1
        and isinstance(non_future_imports[0], ast.ImportFrom)
        and non_future_imports[0].level == 2
        and non_future_imports[0].module == "helpers"
        and len(non_future_imports[0].names) == 1
        and non_future_imports[0].names[0].name == "_wave"
        and non_future_imports[0].names[0].asname is None
    )
    if not valid_helper_import:
        errors.append(f"{path.name} may import only ..helpers._wave")

    unexpected_statements = [
        ast.unparse(node)
        for index, node in enumerate(tree.body)
        if not (
            (
                index == 0
                and isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            )
            or isinstance(node, ast.ImportFrom)
            or _assigned_names(node) == {"LEVELS"}
        )
    ]
    if unexpected_statements:
        errors.append(
            f"{path.name} has unexpected top-level ownership: {unexpected_statements}"
        )

    if _assignment_values(tree, "ADVENTURE_LEVELS"):
        errors.append(f"{path.name} must not define the public ADVENTURE_LEVELS export")
    assignments = _assignment_values(tree, "LEVELS")
    if len(assignments) != 1 or not isinstance(assignments[0], ast.List):
        errors.append(f"{path.name} must define one literal LEVELS list")
        return []
    actual_slugs = [_literal_slug(element) for element in assignments[0].elts]
    if any(slug is None for slug in actual_slugs):
        errors.append(
            f"{path.name} LEVELS entries must be literal dictionaries with slugs"
        )
    if actual_slugs != list(expected_slugs):
        errors.append(
            f"{path.name} owns {actual_slugs}; expected {list(expected_slugs)}"
        )
    return [slug for slug in actual_slugs if slug is not None]


def repository_foundations_layout_errors(
    *,
    composer_path: Path = REPOSITORY_FOUNDATIONS_COMPOSER,
    package_path: Path = REPOSITORY_FOUNDATIONS_PACKAGE,
) -> list[str]:
    """Return deterministic violations for the Repository Foundations cutover."""

    errors: list[str] = []
    expected_files = {"__init__.py"} | {
        f"{module}.py" for module, _ in REPOSITORY_FOUNDATIONS_GROUPS
    }
    actual_files = (
        {
            path.relative_to(package_path).as_posix()
            for path in package_path.rglob("*.py")
        }
        if package_path.is_dir()
        else set()
    )
    if actual_files != expected_files:
        errors.append(
            "repository_foundations module set mismatch: "
            f"missing={sorted(expected_files - actual_files)}, "
            f"unexpected={sorted(actual_files - expected_files)}"
        )

    _verify_package_initializer(package_path, errors)
    _verify_composer(composer_path, errors)
    all_slugs: list[str] = []
    for module, expected_slugs in REPOSITORY_FOUNDATIONS_GROUPS:
        all_slugs.extend(
            _verify_leaf(package_path / f"{module}.py", expected_slugs, errors)
        )
    expected_all = [
        slug for _, slugs in REPOSITORY_FOUNDATIONS_GROUPS for slug in slugs
    ]
    if all_slugs != expected_all:
        errors.append(
            "Repository Foundations leaf slug sequence is incomplete or duplicated"
        )
    return errors


def _top_level_owned_names(tree: ast.Module) -> set[str]:
    """Return module-scope definitions, excluding imported bindings."""

    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        else:
            names.update(_assigned_names(node))
    return names


def _top_level_owner_counts(tree: ast.Module) -> dict[str, int]:
    """Count module-scope definitions without collapsing duplicate owners."""

    counts: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            owned_names = {node.name}
        else:
            owned_names = _assigned_names(node)
        for name in owned_names:
            counts[name] = counts.get(name, 0) + 1
    return counts


def _top_level_bound_names(tree: ast.Module) -> set[str]:
    """Return all module-scope bindings, including import aliases."""

    names = _top_level_owned_names(tree)
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(alias.asname or alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.update(alias.asname or alias.name for alias in node.names)
    return names


def _frost_alias(module_name: str, list_name: str) -> str:
    return f"_{module_name.upper()}_{list_name}"


def _verify_frost_initializer(path: Path, errors: list[str]) -> None:
    parsed = _parse(path, errors)
    if parsed is None:
        return
    source, tree = parsed
    if _line_count(source) > 10:
        errors.append("Frost package __init__.py exceeds its 10-line maximum")

    imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
    expected_import = (
        len(imports) == 2
        and imports[0].module == "__future__"
        and imports[1].level == 1
        and imports[1].module == "_catalog"
        and [(alias.name, alias.asname) for alias in imports[1].names]
        == [("LEVELS", None)]
    )
    if not expected_import:
        errors.append("Frost package initializer must import only public LEVELS")

    all_values = _assignment_values(tree, "__all__")
    valid_all = (
        len(all_values) == 1
        and isinstance(all_values[0], ast.List)
        and [
            element.value
            for element in all_values[0].elts
            if isinstance(element, ast.Constant)
        ]
        == ["LEVELS"]
        and len(all_values[0].elts) == 1
    )
    if not valid_all:
        errors.append('Frost package initializer must declare __all__ = ["LEVELS"]')

    allowed_statements = []
    for index, node in enumerate(tree.body):
        is_docstring = (
            index == 0
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        if not (
            is_docstring
            or isinstance(node, ast.ImportFrom)
            or _assigned_names(node) == {"__all__"}
        ):
            allowed_statements.append(ast.unparse(node))
    if allowed_statements or _top_level_owned_names(tree) != {"__all__"}:
        errors.append(
            "Frost package initializer has unexpected top-level ownership: "
            f"{allowed_statements or sorted(_top_level_owned_names(tree))}"
        )
    if any(isinstance(node, ast.Dict) for node in ast.walk(tree)):
        errors.append("Frost package initializer must not contain content dictionaries")


def _verify_frost_catalog(path: Path, errors: list[str]) -> None:
    parsed = _parse(path, errors)
    if parsed is None:
        return
    source, tree = parsed
    if _line_count(source) > 50:
        errors.append("Frost _catalog.py exceeds its 50-line maximum")
    if any(isinstance(node, ast.Dict) for node in ast.walk(tree)):
        errors.append("Frost _catalog.py must not contain content dictionaries")

    actual_imports: list[tuple[str | None, str, str | None]] = []
    unexpected_imports: list[str] = []
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            continue
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 1
            and node.module is not None
            and len(node.names) == 1
        ):
            alias = node.names[0]
            actual_imports.append((node.module, alias.name, alias.asname))
        else:
            unexpected_imports.append(ast.unparse(node))

    expected_imports = [
        (module_name, list_name, _frost_alias(module_name, list_name))
        for module_name, _ in FROST_CHAPTERS
        for list_name in ("DRILLS", "WORKFLOWS")
    ]
    if actual_imports != expected_imports or unexpected_imports:
        errors.append("Frost _catalog.py imports must match canonical chapter order")

    assignments = _assignment_values(tree, "LEVELS")
    if len(assignments) != 1 or not isinstance(assignments[0], ast.List):
        errors.append("Frost _catalog.py must define one literal LEVELS composition")
    else:
        actual_aliases = [
            element.value.id
            for element in assignments[0].elts
            if isinstance(element, ast.Starred) and isinstance(element.value, ast.Name)
        ]
        expected_aliases = [alias for _, _, alias in expected_imports]
        if (
            len(actual_aliases) != len(assignments[0].elts)
            or actual_aliases != expected_aliases
        ):
            errors.append(
                "Frost _catalog.py must flatten every chapter list once in canonical order"
            )

    unexpected_statements = [
        ast.unparse(node)
        for index, node in enumerate(tree.body)
        if not (
            (
                index == 0
                and isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            )
            or isinstance(node, ast.ImportFrom)
            or _assigned_names(node) == {"LEVELS"}
        )
    ]
    if unexpected_statements or _top_level_owned_names(tree) != {"LEVELS"}:
        errors.append(
            "Frost _catalog.py has unexpected top-level ownership: "
            f"{unexpected_statements or sorted(_top_level_owned_names(tree))}"
        )


def _verify_frost_fixtures(path: Path, errors: list[str]) -> None:
    parsed = _parse(path, errors)
    if parsed is None:
        return
    source, tree = parsed
    if _line_count(source) > 225:
        errors.append("Frost _fixtures.py exceeds its 225-line maximum")
    owned_names = _top_level_owned_names(tree)
    if owned_names != FROST_FIXTURE_BINDINGS:
        errors.append(
            "Frost _fixtures.py symbol ownership mismatch: "
            f"missing={sorted(FROST_FIXTURE_BINDINGS - owned_names)}, "
            f"unexpected={sorted(owned_names - FROST_FIXTURE_BINDINGS)}"
        )
    if owned_names & {"DRILLS", "WORKFLOWS", "LEVELS"}:
        errors.append("Frost _fixtures.py must not define content catalogs")

    duplicate_owners = {
        name: count
        for name, count in _top_level_owner_counts(tree).items()
        if count > 1
    }
    if duplicate_owners:
        errors.append(
            f"Frost _fixtures.py has duplicate top-level owners {duplicate_owners}"
        )

    unexpected_statements: list[str] = []
    for index, node in enumerate(tree.body):
        is_docstring = (
            index == 0
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        if isinstance(node, ast.Import):
            errors.append("Frost _fixtures.py must use only explicit relative imports")
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            allowed = (node.level, node.module) in {
                (2, "common"),
                (3, "advanced_story_support"),
            }
            if not allowed:
                errors.append(
                    "Frost _fixtures.py imports an unauthorized owner: "
                    f"{ast.unparse(node)}"
                )
            if any(alias.name == "*" for alias in node.names):
                errors.append("Frost _fixtures.py must not use wildcard imports")
        elif not (
            is_docstring
            or isinstance(node, ast.ImportFrom)
            or (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name in FROST_FIXTURE_BINDINGS
            )
        ):
            unexpected_statements.append(ast.unparse(node))
    if unexpected_statements:
        errors.append(
            "Frost _fixtures.py has unexpected top-level statements: "
            f"{unexpected_statements}"
        )


def _verify_frost_chapter(
    path: Path,
    module_name: str,
    max_lines: int,
    errors: list[str],
) -> None:
    parsed = _parse(path, errors)
    if parsed is None:
        return
    source, tree = parsed
    if _line_count(source) > max_lines:
        errors.append(
            f"Frost {path.name} exceeds its {max_lines}-line maximum"
        )

    expected_owned = {"DRILLS", "WORKFLOWS"}
    if module_name == "survive_the_conflict":
        expected_owned |= FROST_SURVIVE_LOCAL_BINDINGS
    owned_names = _top_level_owned_names(tree)
    if owned_names != expected_owned:
        errors.append(
            f"Frost {path.name} symbol ownership mismatch: "
            f"missing={sorted(expected_owned - owned_names)}, "
            f"unexpected={sorted(owned_names - expected_owned)}"
        )
    if "LEVELS" in owned_names:
        errors.append(f"Frost {path.name} must not define LEVELS")

    duplicate_owners = {
        name: count
        for name, count in _top_level_owner_counts(tree).items()
        if count > 1
    }
    if duplicate_owners:
        errors.append(
            f"Frost {path.name} has duplicate top-level owners {duplicate_owners}"
        )

    chapter_names = {name for name, _ in FROST_CHAPTERS}
    unexpected_statements: list[str] = []
    for index, node in enumerate(tree.body):
        is_docstring = (
            index == 0
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        if isinstance(node, ast.Import):
            errors.append(f"Frost {path.name} must use only explicit relative imports")
            continue
        if not isinstance(node, ast.ImportFrom):
            allowed_definition = (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name in expected_owned
            ) or (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in expected_owned
            ) or (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id in expected_owned
            )
            if not (is_docstring or allowed_definition):
                unexpected_statements.append(ast.unparse(node))
            continue
        if node.module == "__future__":
            continue
        allowed = (node.level, node.module) in {
            (1, "_fixtures"),
            (2, "common"),
            (2, "form_drill_support"),
        }
        if not allowed:
            errors.append(
                f"Frost {path.name} imports an unauthorized owner: {ast.unparse(node)}"
            )
        if any(alias.name == "*" for alias in node.names):
            errors.append(f"Frost {path.name} must not use wildcard imports")
        if (
            node.module in chapter_names
            or node.module == "_catalog"
            or (node.module is None and any(alias.name in chapter_names for alias in node.names))
            or any(
                (node.module or "").endswith(
                    f"v3_frost_form_drills.{chapter_name}"
                )
                for chapter_name in chapter_names
            )
        ):
            errors.append(f"Frost {path.name} imports a sibling chapter")
    if unexpected_statements:
        errors.append(
            f"Frost {path.name} has unexpected top-level statements: "
            f"{unexpected_statements}"
        )


def _frost_external_import_errors(
    import_roots: tuple[Path, ...], package_path: Path
) -> list[str]:
    errors: list[str] = []
    package_name = "v3_frost_form_drills"
    package_marker = package_name.encode()
    monolith_path = package_path.with_suffix(".py")
    for import_root in import_roots:
        if not import_root.is_dir():
            continue
        paths: list[Path] = []
        for directory, child_dirs, filenames in os.walk(import_root):
            child_dirs[:] = sorted(
                child_dir
                for child_dir in child_dirs
                if child_dir not in FROST_IMPORT_EXCLUDED_DIRS
                and not child_dir.startswith((".pytest-", "pytest-"))
            )
            paths.extend(
                Path(directory) / filename
                for filename in sorted(filenames)
                if filename.endswith(".py")
            )
        for path in paths:
            if path == monolith_path or package_path in path.parents:
                continue
            source = path.read_bytes()
            if package_marker not in source:
                continue
            try:
                tree = ast.parse(source, filename=str(path))
            except SyntaxError as exc:
                errors.append(
                    f"{path.name}: invalid Python: {exc.msg} (line {exc.lineno})"
                )
                continue
            try:
                path_label = path.relative_to(ROOT)
            except ValueError:
                path_label = path.relative_to(import_root)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        marker = f"{package_name}."
                        if marker in alias.name:
                            errors.append(
                                f"{path_label} imports Frost package internals"
                            )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if f"{package_name}." in module:
                        errors.append(
                            f"{path_label} imports Frost package internals"
                        )
                    elif module.endswith(package_name):
                        private_names = sorted(
                            alias.name for alias in node.names if alias.name != "LEVELS"
                        )
                        if private_names:
                            errors.append(
                                f"{path_label} imports non-public Frost bindings "
                                f"{private_names}"
                            )
    return errors


def frost_form_drill_layout_errors(
    *,
    monolith_path: Path = FROST_MONOLITH,
    package_path: Path = FROST_PACKAGE,
    import_roots: tuple[Path, ...] = FROST_IMPORT_SCAN_ROOTS,
) -> list[str]:
    """Return deterministic violations for the Frost same-path package cutover."""

    errors: list[str] = []
    if monolith_path.exists():
        errors.append("legacy v3_frost_form_drills.py monolith must be absent")

    expected_files = {"__init__.py", "_catalog.py", "_fixtures.py"} | {
        f"{module_name}.py" for module_name, _ in FROST_CHAPTERS
    }
    actual_files = (
        {
            path.relative_to(package_path).as_posix()
            for path in package_path.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        if package_path.is_dir()
        else set()
    )
    if actual_files != expected_files:
        errors.append(
            "Frost form-drill module set mismatch: "
            f"missing={sorted(expected_files - actual_files)}, "
            f"unexpected={sorted(actual_files - expected_files)}"
        )

    _verify_frost_initializer(package_path / "__init__.py", errors)
    _verify_frost_catalog(package_path / "_catalog.py", errors)
    _verify_frost_fixtures(package_path / "_fixtures.py", errors)
    for module_name, max_lines in FROST_CHAPTERS:
        _verify_frost_chapter(
            package_path / f"{module_name}.py",
            module_name,
            max_lines,
            errors,
        )

    package_bindings: dict[str, list[str]] = {}
    if package_path.is_dir():
        for path in sorted(package_path.rglob("*.py")):
            parsed = _parse(path, errors)
            if parsed is None:
                continue
            _, tree = parsed
            for name in _top_level_owned_names(tree):
                package_bindings.setdefault(name, []).append(path.name)
            displaced = _top_level_bound_names(tree) & FROST_DISPLACED_SUPPORT_BINDINGS
            if displaced:
                errors.append(
                    f"Frost {path.name} restores displaced support bindings "
                    f"{sorted(displaced)}"
                )

    unique_helper_names = FROST_FIXTURE_BINDINGS | FROST_SURVIVE_LOCAL_BINDINGS
    for name in sorted(unique_helper_names):
        owners = package_bindings.get(name, [])
        if len(owners) > 1:
            errors.append(f"Frost helper {name} has duplicate owners {owners}")

    errors.extend(_frost_external_import_errors(import_roots, package_path))
    return errors


def main() -> int:
    errors = [
        *repository_foundations_layout_errors(),
        *frost_form_drill_layout_errors(),
        *adventure_plan_ownership_errors(),
    ]
    if errors:
        print("Curriculum source layout problems found:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("Curriculum source layout is consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
