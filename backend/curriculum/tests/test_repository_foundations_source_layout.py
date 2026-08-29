from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from scripts.checks.check_curriculum_source_layout import (
    REPOSITORY_FOUNDATIONS_COMPOSER,
    REPOSITORY_FOUNDATIONS_PACKAGE,
    repository_foundations_layout_errors,
)


def _copy_layout(tmp_path: Path) -> tuple[Path, Path]:
    composer = tmp_path / REPOSITORY_FOUNDATIONS_COMPOSER.name
    package = tmp_path / REPOSITORY_FOUNDATIONS_PACKAGE.name
    shutil.copy2(REPOSITORY_FOUNDATIONS_COMPOSER, composer)
    shutil.copytree(REPOSITORY_FOUNDATIONS_PACKAGE, package)
    return composer, package


def test_live_repository_foundations_layout_is_valid():
    assert repository_foundations_layout_errors() == []


@pytest.mark.parametrize("mutation", ["missing", "unexpected"])
def test_layout_rejects_wrong_leaf_module_set(tmp_path: Path, mutation: str):
    composer, package = _copy_layout(tmp_path)
    if mutation == "missing":
        (package / "cloning.py").unlink()
    else:
        (package / "alternate_path.py").write_text("LEVELS = []\n", encoding="utf-8")

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("module set mismatch" in error for error in errors)


def test_layout_rejects_nested_alternate_owner(tmp_path: Path):
    composer, package = _copy_layout(tmp_path)
    alternate = package / "legacy" / "levels.py"
    alternate.parent.mkdir()
    alternate.write_text("LEVELS = []\n", encoding="utf-8")

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("legacy/levels.py" in error for error in errors)


def test_layout_rejects_inline_composer_content(tmp_path: Path):
    composer, package = _copy_layout(tmp_path)
    composer.write_text(
        composer.read_text(encoding="utf-8")
        + '\n_INLINE = {"slug": "second-owner"}\n'
        + '_wave("duplicate", "git-status/plain", "Duplicate", ["git status"])\n',
        encoding="utf-8",
    )

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("must not contain level dictionaries" in error for error in errors)
    assert any("must not call _wave" in error for error in errors)


def test_layout_rejects_reordered_composition(tmp_path: Path):
    composer, package = _copy_layout(tmp_path)
    source = composer.read_text(encoding="utf-8")
    source = source.replace(
        "    *_FRESH_STARTS_LEVELS,\n    *_HISTORY_AND_STATUS_LEVELS,",
        "    *_HISTORY_AND_STATUS_LEVELS,\n    *_FRESH_STARTS_LEVELS,",
    )
    composer.write_text(source, encoding="utf-8")

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("flatten each concept list once" in error for error in errors)


def test_layout_rejects_wrong_or_duplicate_slug_ownership(tmp_path: Path):
    composer, package = _copy_layout(tmp_path)
    fresh_starts = package / "fresh_starts.py"
    source = fresh_starts.read_text(encoding="utf-8").replace(
        '"start-a-repository"', '"read-the-workspace"', 1
    )
    fresh_starts.write_text(source, encoding="utf-8")

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("fresh_starts.py owns" in error for error in errors)
    assert any("incomplete or duplicated" in error for error in errors)


@pytest.mark.parametrize(
    "dependency",
    [
        "from .cloning import LEVELS as CLONING_LEVELS\n",
        "from ..adventure_repository_foundations import ADVENTURE_LEVELS\n",
    ],
)
def test_layout_rejects_leaf_dependencies(tmp_path: Path, dependency: str):
    composer, package = _copy_layout(tmp_path)
    history = package / "history_and_status.py"
    history.write_text(
        history.read_text(encoding="utf-8") + "\n" + dependency,
        encoding="utf-8",
    )

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("may import only ..helpers._wave" in error for error in errors)


@pytest.mark.parametrize("target", ["composer", "leaf"])
def test_layout_rejects_size_regressions(tmp_path: Path, target: str):
    composer, package = _copy_layout(tmp_path)
    path = composer if target == "composer" else package / "fresh_starts.py"
    path.write_text(
        path.read_text(encoding="utf-8") + "# padding\n" * 60,
        encoding="utf-8",
    )

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("maximum is" in error for error in errors)


def test_layout_rejects_package_reexports(tmp_path: Path):
    composer, package = _copy_layout(tmp_path)
    initializer = package / "__init__.py"
    initializer.write_text(
        initializer.read_text(encoding="utf-8") + "from .cloning import LEVELS as CLONING_LEVELS\n",
        encoding="utf-8",
    )

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("must contain only a package docstring" in error for error in errors)


def test_layout_rejects_fallback_leaf_ownership(tmp_path: Path):
    composer, package = _copy_layout(tmp_path)
    cloning = package / "cloning.py"
    cloning.write_text(
        cloning.read_text(encoding="utf-8") + "\nFALLBACK_LEVELS = []\n",
        encoding="utf-8",
    )

    errors = repository_foundations_layout_errors(
        composer_path=composer,
        package_path=package,
    )

    assert any("unexpected top-level ownership" in error for error in errors)
