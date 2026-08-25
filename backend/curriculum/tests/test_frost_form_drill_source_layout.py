from __future__ import annotations

from pathlib import Path

import pytest
from scripts.checks.check_curriculum_source_layout import (
    FROST_CHAPTERS,
    FROST_FIXTURE_BINDINGS,
    FROST_IMPORT_SCAN_ROOTS,
    FROST_MONOLITH,
    FROST_PACKAGE,
    frost_form_drill_layout_errors,
)


def _write(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def _catalog_source() -> str:
    imports: list[str] = []
    aliases: list[str] = []
    for module_name, _ in FROST_CHAPTERS:
        for list_name in ("DRILLS", "WORKFLOWS"):
            alias = f"_{module_name.upper()}_{list_name}"
            imports.append(f"from .{module_name} import {list_name} as {alias}")
            aliases.append(f"    *{alias},")
    return (
        '"""Ordered Frost form-drill catalog."""\n\n'
        "from __future__ import annotations\n\n"
        + "\n".join(imports)
        + "\n\nLEVELS = [\n"
        + "\n".join(aliases)
        + "\n]\n"
    )


def _create_layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    source_root = tmp_path / "source"
    specs = source_root / "adventure_level_specs"
    monolith = specs / "v3_frost_form_drills.py"
    package = specs / "v3_frost_form_drills"

    _write(
        package / "__init__.py",
        '"""Public Frost form-drill catalog."""\n\n'
        "from __future__ import annotations\n\n"
        "from ._catalog import LEVELS\n\n"
        '__all__ = ["LEVELS"]\n',
    )
    _write(package / "_catalog.py", _catalog_source())
    fixture_source = ['"""Frost-only repository fixtures."""', ""]
    for name in sorted(FROST_FIXTURE_BINDINGS):
        fixture_source.extend([f"def {name}():", "    return None", ""])
    _write(package / "_fixtures.py", "\n".join(fixture_source))

    for module_name, _ in FROST_CHAPTERS:
        owned = ['"""One Frost chapter catalog."""', ""]
        if module_name == "survive_the_conflict":
            owned.extend(
                [
                    "NO_MARKERS = {}",
                    "",
                    "def _conflict_read():",
                    "    return None",
                    "",
                ]
            )
        owned.extend(["DRILLS = []", "", "WORKFLOWS = []", ""])
        _write(package / f"{module_name}.py", "\n".join(owned))

    _write(
        source_root / "challenge_specs" / "consumer.py",
        "from curriculum.seed_data.source.adventure_level_specs."
        "v3_frost_form_drills import LEVELS\n",
    )
    return monolith, package, source_root


def _errors(
    monolith: Path,
    package: Path,
    source_root: Path,
    *additional_import_roots: Path,
) -> list[str]:
    return frost_form_drill_layout_errors(
        monolith_path=monolith,
        package_path=package,
        import_roots=(source_root, *additional_import_roots),
    )


def test_live_frost_form_drill_layout_is_valid():
    assert frost_form_drill_layout_errors(
        monolith_path=FROST_MONOLITH,
        package_path=FROST_PACKAGE,
        import_roots=FROST_IMPORT_SCAN_ROOTS,
    ) == []


def test_canonical_frost_form_drill_layout_is_valid(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)

    assert _errors(monolith, package, source_root) == []


def test_layout_rejects_restored_monolith(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    _write(monolith, "LEVELS = []\n")

    errors = _errors(monolith, package, source_root)

    assert any("monolith must be absent" in error for error in errors)


@pytest.mark.parametrize(
    "mutation", ["missing", "unexpected", "nested", "non_python"]
)
def test_layout_rejects_wrong_module_manifest(tmp_path: Path, mutation: str):
    monolith, package, source_root = _create_layout(tmp_path)
    if mutation == "missing":
        (package / "choose_the_integration.py").unlink()
    elif mutation == "unexpected":
        _write(package / "alternate.py", "DRILLS = []\nWORKFLOWS = []\n")
    elif mutation == "nested":
        _write(package / "legacy" / "catalog.py", "LEVELS = []\n")
    else:
        _write(package / "README.md", "stale package notes\n")

    errors = _errors(monolith, package, source_root)

    assert any("module set mismatch" in error for error in errors)


@pytest.mark.parametrize(
    ("relative_path", "padding"),
    [
        ("__init__.py", 12),
        ("_catalog.py", 60),
        ("_fixtures.py", 230),
        ("temper_the_commit.py", 660),
    ],
)
def test_layout_rejects_size_regressions(
    tmp_path: Path,
    relative_path: str,
    padding: int,
):
    monolith, package, source_root = _create_layout(tmp_path)
    path = package / relative_path
    path.write_text(
        path.read_text(encoding="utf-8") + "# padding\n" * padding,
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("maximum" in error for error in errors)


def test_layout_rejects_initializer_ownership(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    initializer = package / "__init__.py"
    initializer.write_text(
        initializer.read_text(encoding="utf-8") + "SECOND_LEVELS = []\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("initializer has unexpected top-level ownership" in error for error in errors)


def test_layout_rejects_catalog_order_drift(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    catalog = package / "_catalog.py"
    source = catalog.read_text(encoding="utf-8").replace(
        "    *_TEMPER_THE_COMMIT_DRILLS,\n    *_TEMPER_THE_COMMIT_WORKFLOWS,",
        "    *_TEMPER_THE_COMMIT_WORKFLOWS,\n    *_TEMPER_THE_COMMIT_DRILLS,",
    )
    catalog.write_text(source, encoding="utf-8")

    errors = _errors(monolith, package, source_root)

    assert any("flatten every chapter list once" in error for error in errors)


def test_layout_rejects_inline_catalog_content(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    catalog = package / "_catalog.py"
    catalog.write_text(
        catalog.read_text(encoding="utf-8") + '_INLINE = {"slug": "duplicate"}\n',
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("must not contain content dictionaries" in error for error in errors)
    assert any("unexpected top-level ownership" in error for error in errors)


@pytest.mark.parametrize("target", ["fixtures", "chapter"])
def test_layout_rejects_unexpected_symbol_ownership(tmp_path: Path, target: str):
    monolith, package, source_root = _create_layout(tmp_path)
    path = package / ("_fixtures.py" if target == "fixtures" else "move_the_patch.py")
    path.write_text(
        path.read_text(encoding="utf-8") + "\ndef alternate_owner():\n    pass\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("symbol ownership mismatch" in error for error in errors)


@pytest.mark.parametrize("helper", ["_work", "_conflict_read"])
def test_layout_rejects_duplicate_helper_truth(tmp_path: Path, helper: str):
    monolith, package, source_root = _create_layout(tmp_path)
    target = package / "temper_the_commit.py"
    target.write_text(
        target.read_text(encoding="utf-8") + f"\ndef {helper}():\n    pass\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any(f"helper {helper} has duplicate owners" in error for error in errors)


def test_layout_rejects_duplicate_chapter_catalog_binding(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    target = package / "temper_the_commit.py"
    target.write_text(
        target.read_text(encoding="utf-8") + "\nDRILLS = []\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("duplicate top-level owners" in error for error in errors)


@pytest.mark.parametrize("target", ["fixtures", "chapter"])
def test_layout_rejects_top_level_side_effect(tmp_path: Path, target: str):
    monolith, package, source_root = _create_layout(tmp_path)
    path = package / ("_fixtures.py" if target == "fixtures" else "move_the_patch.py")
    path.write_text(
        path.read_text(encoding="utf-8") + "\nprint('unexpected side effect')\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("unexpected top-level statements" in error for error in errors)


def test_layout_rejects_destructuring_assignment(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    target = package / "move_the_patch.py"
    target.write_text(
        target.read_text(encoding="utf-8") + "\nDRILLS, WORKFLOWS = [], []\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("unexpected top-level statements" in error for error in errors)


def test_layout_rejects_sibling_chapter_import(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    target = package / "temper_the_commit.py"
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\nfrom .choose_the_integration import DRILLS as OTHER_DRILLS\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("imports a sibling chapter" in error for error in errors)


@pytest.mark.parametrize(
    "dependency",
    [
        "from curriculum.seed_data.source.adventure_level_specs."
        "v3_frost_form_drills._fixtures import _work\n",
        "from .v3_frost_form_drills._catalog import LEVELS\n",
        "import curriculum.seed_data.source.adventure_level_specs."
        "v3_frost_form_drills.temper_the_commit\n",
    ],
)
def test_layout_rejects_external_internal_imports(tmp_path: Path, dependency: str):
    monolith, package, source_root = _create_layout(tmp_path)
    _write(source_root / "external.py", dependency)

    errors = _errors(monolith, package, source_root)

    assert any("imports Frost package internals" in error for error in errors)


def test_layout_rejects_external_internal_import_outside_source(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    scripts_root = tmp_path / "scripts"
    _write(
        scripts_root / "external.py",
        "from curriculum.seed_data.source.adventure_level_specs."
        "v3_frost_form_drills._catalog import LEVELS\n",
    )

    errors = _errors(monolith, package, source_root, scripts_root)

    assert any("imports Frost package internals" in error for error in errors)


def test_layout_external_scan_excludes_non_repository_directories(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    _write(
        tmp_path / ".venv" / "leak.py",
        "from curriculum.seed_data.source.adventure_level_specs."
        "v3_frost_form_drills._catalog import LEVELS\n",
    )

    errors = frost_form_drill_layout_errors(
        monolith_path=monolith,
        package_path=package,
        import_roots=(tmp_path,),
    )

    assert errors == []


def test_layout_external_scan_ignores_unrelated_invalid_python(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    scripts_root = tmp_path / "scripts"
    _write(scripts_root / "unrelated.py", "this is not valid Python !!!\n")

    errors = _errors(monolith, package, source_root, scripts_root)

    assert errors == []


def test_layout_rejects_external_non_public_binding(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    _write(
        source_root / "external.py",
        "from curriculum.seed_data.source.adventure_level_specs."
        "v3_frost_form_drills import _catalog\n",
    )

    errors = _errors(monolith, package, source_root)

    assert any("imports non-public Frost bindings" in error for error in errors)


def test_layout_rejects_displaced_support_alias(tmp_path: Path):
    monolith, package, source_root = _create_layout(tmp_path)
    target = package / "move_the_patch.py"
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\nfrom ..form_drill_support import CORE_FORM_TAGS as CORE_TAGS\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("restores displaced support bindings" in error for error in errors)


@pytest.mark.parametrize("target", ["fixtures", "chapter"])
def test_layout_rejects_wildcard_imports(tmp_path: Path, target: str):
    monolith, package, source_root = _create_layout(tmp_path)
    path = package / ("_fixtures.py" if target == "fixtures" else "move_the_patch.py")
    path.write_text(
        path.read_text(encoding="utf-8") + "\nfrom ..common import *\n",
        encoding="utf-8",
    )

    errors = _errors(monolith, package, source_root)

    assert any("must not use wildcard imports" in error for error in errors)
