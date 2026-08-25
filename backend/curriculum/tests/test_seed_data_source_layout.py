import ast
from pathlib import Path

from scripts.checks.check_curriculum_source_layout import (
    FROST_DISPLACED_SUPPORT_BINDINGS,
)

ROOT = Path(__file__).resolve().parents[3]
SEED_DATA = ROOT / "backend" / "curriculum" / "seed_data"
SOURCE = SEED_DATA / "source"


PARTITION_PACKAGES = {
    "adventure_levels": "adventure_level_specs",
    "challenges": "challenge_specs",
    "blueprint_overlay": "blueprint",
}

NEUTRAL_SUPPORT_MODULES = {
    SOURCE / "advanced_story_support.py",
    SOURCE / "adventure_level_specs" / "form_drill_support.py",
    SOURCE / "challenge_specs" / "advanced_challenge_support.py",
}
PUBLIC_LEDGER_EXPORTS = {
    "INCIDENTS",
    "LEVELS",
    "V3_CHALLENGES",
    "V3_FORM_CHALLENGES",
}
DISPLACED_SUPPORT_PATH = SOURCE / "adventure_level_specs" / "advanced_story_support.py"
FROST_FORM_DRILL_PACKAGE = (
    SOURCE / "adventure_level_specs" / "v3_frost_form_drills"
)
DISPLACED_OWNER_BINDINGS = {
    SOURCE / "adventure_level_specs" / "v3_advanced_workflows.py": {
        "_base_commits",
        "_metadata",
        "_render",
        "_requirements",
        "_state",
    },
    SOURCE / "challenge_specs" / "v3_story_challenges.py": {
        "_DIFFICULTY",
        "_advanced_variant",
        "_difficulty_extra",
        "_family",
        "_scenario_copy",
    },
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(), filename=str(path))


def _module_name_tail(module_name: str) -> str:
    return module_name.rsplit(".", 1)[-1]


def _bound_names(path: Path) -> set[str]:
    names: set[str] = set()
    for node in _tree(path).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names.update(target.id for target in targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.Import):
            names.update(alias.asname or _module_name_tail(alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.update(alias.asname or alias.name for alias in node.names if alias.name != "*")
    return names


def test_large_authored_seed_data_lives_under_partitioned_source_packages():
    for module_name, package_name in PARTITION_PACKAGES.items():
        public_module = SEED_DATA / f"{module_name}.py"
        source_module = SEED_DATA / "source" / f"{module_name}.py"
        partition = SEED_DATA / "source" / package_name
        assert public_module.exists()
        assert source_module.exists()
        assert partition.exists()
        assert (partition / "__init__.py").exists()
        assert len(public_module.read_text().splitlines()) <= 50
        assert len(source_module.read_text().splitlines()) <= 50
        assert "curriculum.seed_data.source" in public_module.read_text()


def test_reusable_seed_helpers_do_not_live_in_authored_story_ledgers():
    violations: list[str] = []

    for path in sorted(SOURCE.rglob("*.py")):
        path_label = path.relative_to(ROOT)
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = _module_name_tail(alias.name)
                    if module_name.startswith("v3_"):
                        violations.append(
                            f"{path_label} imports authored ledger module {module_name}; "
                            "import an explicit public content export instead"
                        )
                continue
            if not isinstance(node, ast.ImportFrom):
                continue

            module_name = _module_name_tail(node.module or "")
            imported_names = {alias.name for alias in node.names}
            if module_name.startswith("v3_"):
                private_imports = imported_names - PUBLIC_LEDGER_EXPORTS
                if private_imports:
                    violations.append(
                        f"{path_label} imports non-content symbols {sorted(private_imports)} "
                        f"from authored ledger {module_name}"
                    )
                if path in NEUTRAL_SUPPORT_MODULES:
                    violations.append(
                        f"{path_label} imports authored ledger {module_name} from neutral support"
                    )

            relative_ledger_modules = {
                alias.name for alias in node.names if alias.name.startswith("v3_")
            }
            if relative_ledger_modules:
                violations.append(
                    f"{path_label} imports authored ledger modules "
                    f"{sorted(relative_ledger_modules)} through a package-relative import"
                )

    for support_module in sorted(NEUTRAL_SUPPORT_MODULES):
        authored_exports = _bound_names(support_module) & PUBLIC_LEDGER_EXPORTS
        if authored_exports:
            violations.append(
                f"{support_module.relative_to(ROOT)} defines authored exports "
                f"{sorted(authored_exports)}"
            )

    for former_owner, displaced_names in DISPLACED_OWNER_BINDINGS.items():
        restored_names = _bound_names(former_owner) & displaced_names
        if restored_names:
            violations.append(
                f"{former_owner.relative_to(ROOT)} restores displaced bindings "
                f"{sorted(restored_names)}"
            )

    for frost_module in sorted(FROST_FORM_DRILL_PACKAGE.rglob("*.py")):
        restored_names = _bound_names(frost_module) & FROST_DISPLACED_SUPPORT_BINDINGS
        if restored_names:
            violations.append(
                f"{frost_module.relative_to(ROOT)} restores displaced bindings "
                f"{sorted(restored_names)}"
            )

    if DISPLACED_SUPPORT_PATH.exists():
        violations.append(
            f"{DISPLACED_SUPPORT_PATH.relative_to(ROOT)} restores the Adventure-owned support path"
        )

    assert not violations, "\n".join(violations)


def test_migration_files_are_committed_as_schema_history():
    migration_files = sorted(
        path for path in (ROOT / "backend").glob("*/migrations/*.py") if path.name != "__init__.py"
    )
    assert migration_files, "Model changes must ship with committed migrations."
    assert all(path.stem[:4].isdigit() for path in migration_files)

    test_settings = (ROOT / "backend" / "config" / "test_settings.py").read_text()
    assert "MIGRATION_MODULES" not in test_settings
