from __future__ import annotations

import shutil
from copy import deepcopy
from pathlib import Path

import pytest
from scripts.checks.adventure_plan_ownership import (
    FOUNDATIONAL_ADVENTURE_ORDER,
    ROOT,
    adventure_plan_ownership_errors,
)

from curriculum.seed_data import adventure_levels as public_adventure_levels
from curriculum.seed_data.adventures import (
    ADVENTURE_WAVE_PLANS,
    _merge_disjoint_adventure_wave_plans,
    _ordered_foundational_adventure_wave_plans,
)
from curriculum.seed_data.source import adventure_level_specs
from curriculum.seed_data.source import adventure_levels as source_adventure_levels
from curriculum.seed_data.source.adventure_level_specs.level_plan import (
    _wave_plan_levels,
)
from curriculum.seed_data.source.blueprint import BLUEPRINT_ADVENTURE_LEVELS

POLICY_FILES = (
    "CONTENT_AUTHORING_GUIDE.md",
    "backend/curriculum/seed_data/adventures.py",
    "backend/curriculum/seed_data/adventure_levels.py",
    "backend/curriculum/seed_data/source/__init__.py",
    "backend/curriculum/seed_data/source/adventure_levels.py",
    "backend/curriculum/seed_data/source/adventure_level_specs/__init__.py",
    "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py",
    "backend/curriculum/management/commands/seed_curriculum_writer.py",
)


def _copy_policy_fixture(tmp_path: Path) -> Path:
    fixture_root = tmp_path / "repository"
    for relative_path in POLICY_FILES:
        source = ROOT / relative_path
        destination = fixture_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return fixture_root


def _copy_blueprint_generator_sources(fixture_root: Path) -> str:
    relative_paths = (
        "backend/curriculum/seed_data/source/adventure_level_specs/blueprint_generated.py",
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "backend/curriculum/seed_data/source/command_routing.py",
        "backend/curriculum/seed_data/spec_helpers.py",
    )
    for relative_path in relative_paths:
        destination = fixture_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative_path, destination)
    return relative_paths[0]


def _mutate(
    root: Path,
    relative_path: str,
    old: str,
    new: str,
    *,
    count: int = 1,
) -> None:
    path = root / relative_path
    source = path.read_text(encoding="utf-8")
    assert old in source
    path.write_text(source.replace(old, new, count), encoding="utf-8")


def test_live_adventure_plan_ownership_is_valid():
    assert adventure_plan_ownership_errors() == []


def test_public_foundational_order_and_identity_are_stable():
    assert tuple(ADVENTURE_WAVE_PLANS)[: len(FOUNDATIONAL_ADVENTURE_ORDER)] == (
        FOUNDATIONAL_ADVENTURE_ORDER
    )
    assert set(FOUNDATIONAL_ADVENTURE_ORDER) == set(BLUEPRINT_ADVENTURE_LEVELS)
    assert all(
        ADVENTURE_WAVE_PLANS[slug] is BLUEPRINT_ADVENTURE_LEVELS[slug]
        for slug in FOUNDATIONAL_ADVENTURE_ORDER
    )


@pytest.mark.parametrize(
    ("blueprint", "order", "message"),
    [
        (
            {"alpha": [], "beta": []},
            ("alpha",),
            "Foundational adventure order mismatch: missing=['beta'], extra=[], duplicates=[]",
        ),
        (
            {"alpha": []},
            ("alpha", "beta"),
            "Foundational adventure order mismatch: missing=[], extra=['beta'], duplicates=[]",
        ),
        (
            {"alpha": []},
            ("alpha", "alpha"),
            "Foundational adventure order mismatch: missing=[], extra=[], duplicates=['alpha']",
        ),
    ],
)
def test_foundational_projection_rejects_mismatch_deterministically(
    blueprint: dict[str, list[dict]],
    order: tuple[str, ...],
    message: str,
):
    with pytest.raises(
        ValueError, match="^" + message.replace("[", "\\[").replace("]", "\\]") + "$"
    ):
        _ordered_foundational_adventure_wave_plans(blueprint, order)


def test_foundational_projection_preserves_value_identity():
    alpha: list[dict] = [{"slug": "alpha"}]
    beta: list[dict] = [{"slug": "beta"}]

    result = _ordered_foundational_adventure_wave_plans(
        {"beta": beta, "alpha": alpha},
        ("alpha", "beta"),
    )

    assert list(result) == ["alpha", "beta"]
    assert result["alpha"] is alpha
    assert result["beta"] is beta


def test_disjoint_merge_rejects_sorted_duplicate_owners():
    with pytest.raises(
        ValueError,
        match=r"^Duplicate adventure wave plan owner\(s\): alpha, beta$",
    ):
        _merge_disjoint_adventure_wave_plans(
            {"beta": [], "alpha": []},
            {"alpha": [], "beta": []},
        )


def test_disjoint_merge_preserves_owner_order_and_values():
    foundational: list[dict] = [{"slug": "foundation"}]
    advanced: list[dict] = [{"slug": "advanced"}]

    result = _merge_disjoint_adventure_wave_plans(
        {"foundation": foundational},
        {"advanced": advanced},
    )

    assert list(result) == ["foundation", "advanced"]
    assert result["foundation"] is foundational
    assert result["advanced"] is advanced


def test_wave_plan_normalization_does_not_mutate_authored_input():
    plan = [
        {
            "slug": "level-one",
            "title": "Level One",
            "waves": [["first"], ["second"]],
            "reuse_usages": ["status"],
        }
    ]
    before = deepcopy(plan)

    normalized = _wave_plan_levels(plan)

    assert plan == before
    assert normalized == [
        {
            "slug": "level-one",
            "title": "Level One",
            "wave_slugs": ["first", "second"],
            "reuse_usages": ["status"],
        }
    ]


@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate", "reorder"])
def test_policy_rejects_foundational_order_mutations(
    tmp_path: Path,
    mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    path = "backend/curriculum/seed_data/adventures.py"
    if mutation == "missing":
        _mutate(fixture_root, path, '    "publish-work",\n', "")
    elif mutation == "extra":
        _mutate(
            fixture_root,
            path,
            '    "publish-work",\n)',
            '    "publish-work",\n    "extra-foundation",\n)',
        )
    elif mutation == "duplicate":
        _mutate(
            fixture_root,
            path,
            '    "publish-work",\n)',
            '    "publish-work",\n    "publish-work",\n)',
        )
    else:
        _mutate(
            fixture_root,
            path,
            '    "seal-the-snapshot",\n    "untrack-and-undo-edits",',
            '    "untrack-and-undo-edits",\n    "seal-the-snapshot",',
        )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("foundational adventure public order" in error for error in errors)


@pytest.mark.parametrize("replacement", ["unexpected-owner", "repository-foundations"])
def test_policy_rejects_wrong_advanced_owner_keys(
    tmp_path: Path,
    replacement: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/adventures.py",
        '    "frost-temper-the-commit-drills": [',
        f'    "{replacement}": [',
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("advanced drill owner keys" in error for error in errors)
    if replacement == "repository-foundations":
        assert any("must not contain foundational keys" in error for error in errors)


@pytest.mark.parametrize(
    "mutation",
    [
        "ADVENTURE_WAVE_PLANS.update(_ADVANCED_DRILL_WAVE_PLANS)",
        'ADVENTURE_WAVE_PLANS["repository-foundations"] = []',
        'ADVENTURE_WAVE_PLANS |= {"replacement": []}',
        'ADVENTURE_WAVE_PLANS.pop("repository-foundations", None)',
        "ADVENTURE_WAVE_PLANS.popitem()",
        "ADVENTURE_WAVE_PLANS.clear()",
        'del ADVENTURE_WAVE_PLANS["repository-foundations"]',
        'ADVENTURE_WAVE_PLANS["repository-foundations"].append({})',
        'ADVENTURE_WAVE_PLANS["repository-foundations"].extend([])',
        "ADVENTURE_WAVE_PLANS, sentinel = ({}, None)",
        "for ADVENTURE_WAVE_PLANS in ():\n    pass",
        "alias = ADVENTURE_WAVE_PLANS\nalias.clear()",
        "dict.clear(ADVENTURE_WAVE_PLANS)",
        'ADVENTURE_WAVE_PLANS.__ior__({"replacement": []})',
        'ADVENTURE_WAVE_PLANS.get("repository-foundations").clear()',
        "(ADVENTURE_WAVE_PLANS := {})",
        "_merge_disjoint_adventure_wave_plans = lambda *owners: owners[-1]",
    ],
)
def test_policy_rejects_public_plan_mutation(tmp_path: Path, mutation: str):
    fixture_root = _copy_policy_fixture(tmp_path)
    path = fixture_root / "backend/curriculum/seed_data/adventures.py"
    path.write_text(
        path.read_text(encoding="utf-8") + f"\n{mutation}\n",
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "must not be mutated" in error
        or "critical adventure composition symbol usage drifted" in error
        for error in errors
    )


def test_policy_rejects_mutation_through_canonical_reader(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py",
        "ADVENTURE_WAVE_PLANS.get(adventure_slug, [])",
        "ADVENTURE_WAVE_PLANS.get(adventure_slug, []).clear()",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("canonical ADVENTURE_WAVE_PLANS reader contract" in error for error in errors)


def test_policy_rejects_chained_public_plan_alias(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    adventures = fixture_root / "backend/curriculum/seed_data/adventures.py"
    source = adventures.read_text(encoding="utf-8").replace(
        "ADVENTURE_WAVE_PLANS = _merge_disjoint_adventure_wave_plans(",
        "ADVENTURE_WAVE_PLANS = alias = _merge_disjoint_adventure_wave_plans(",
        1,
    )
    adventures.write_text(source + "\nalias.clear()\n", encoding="utf-8")

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("canonical ordered disjoint composition" in error for error in errors)


def test_policy_rejects_chained_advanced_owner_alias(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    adventures = fixture_root / "backend/curriculum/seed_data/adventures.py"
    source = adventures.read_text(encoding="utf-8").replace(
        "_ADVANCED_DRILL_WAVE_PLANS = {",
        "_ADVANCED_DRILL_WAVE_PLANS = alias = {",
        1,
    )
    adventures.write_text(source + "\nalias.clear()\n", encoding="utf-8")

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("top-level topology" in error for error in errors)


def test_policy_rejects_advanced_value_named_expression_alias(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    path = "backend/curriculum/seed_data/adventures.py"
    _mutate(
        fixture_root,
        path,
        '    "frost-temper-the-commit-drills": [',
        '    "frost-temper-the-commit-drills": (alias := [',
    )
    _mutate(
        fixture_root,
        path,
        '    ],\n    "frost-choose-the-integration-drills": [',
        '    ]),\n    "frost-choose-the-integration-drills": [',
    )
    adventures = fixture_root / path
    adventures.write_text(
        adventures.read_text(encoding="utf-8") + "\nalias.clear()\n",
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("canonical literal schema" in error for error in errors)


def test_policy_rejects_second_blueprint_import_alias(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    path = "backend/curriculum/seed_data/adventures.py"
    _mutate(
        fixture_root,
        path,
        ("from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS"),
        (
            "from curriculum.seed_data.blueprint_overlay import "
            "BLUEPRINT_ADVENTURE_LEVELS, BLUEPRINT_ADVENTURE_LEVELS as alias"
        ),
    )
    adventures = fixture_root / path
    adventures.write_text(
        adventures.read_text(encoding="utf-8") + "\nalias.clear()\n",
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("canonical one-name blueprint import" in error for error in errors)


def test_policy_rejects_mutable_aliased_foundational_order(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    path = "backend/curriculum/seed_data/adventures.py"
    _mutate(
        fixture_root,
        path,
        "_FOUNDATIONAL_ADVENTURE_ORDER = (",
        "_FOUNDATIONAL_ADVENTURE_ORDER = alias = [",
    )
    _mutate(
        fixture_root,
        path,
        '    "publish-work",\n)\n\n\ndef _ordered_foundational',
        '    "publish-work",\n]\nalias.reverse()\n\n\ndef _ordered_foundational',
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("canonical sequence exactly" in error for error in errors)


def test_policy_rejects_waves_helper_drift(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/adventures.py",
        "    return [[slug] for slug in scenario_slugs]",
        "    return [list(scenario_slugs)]",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("exact literal plan-construction contract" in error for error in errors)


def test_policy_rejects_waves_helper_rebinding_in_later_data(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    path = "backend/curriculum/seed_data/adventures.py"
    _mutate(
        fixture_root,
        path,
        "ADVENTURE_SOURCES = {",
        "ADVENTURE_SOURCES = ((_waves := None), {",
    )
    _mutate(
        fixture_root,
        path,
        "    ],\n}\n\n\n# Curriculum v3 story incidents.",
        "    ],\n})[1]\n\n\n# Curriculum v3 story incidents.",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("critical adventure composition symbol binding drifted" in error for error in errors)


def test_policy_rejects_mutating_wave_plan_reader_helper(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py",
        ('    """Normalize ``adventures.py`` wave plans into the local level-plan shape."""'),
        (
            '    """Normalize ``adventures.py`` wave plans into the local '
            'level-plan shape."""\n    plan.clear()'
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("canonical ADVENTURE_WAVE_PLANS reader contract" in error for error in errors)


def test_policy_rejects_blueprint_mutation_in_canonical_reader(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py",
        ("from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS"),
        (
            "from curriculum.seed_data.blueprint_overlay import "
            "BLUEPRINT_ADVENTURE_LEVELS\n"
            'BLUEPRINT_ADVENTURE_LEVELS["repository-foundations"].clear()'
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("BLUEPRINT_ADVENTURE_LEVELS must not be mutated" in error for error in errors)


@pytest.mark.parametrize(
    "rogue_source",
    [
        (
            "from curriculum.seed_data.adventures import "
            "_ADVANCED_DRILL_WAVE_PLANS\n"
            '_ADVANCED_DRILL_WAVE_PLANS["frost-temper-the-commit-drills"].clear()\n'
        ),
        (
            "from curriculum.seed_data.blueprint_overlay import "
            "BLUEPRINT_ADVENTURE_LEVELS\n"
            'BLUEPRINT_ADVENTURE_LEVELS["repository-foundations"].clear()\n'
        ),
        (
            "from curriculum.seed_data.source.blueprint.adventure_publish_work "
            "import ADVENTURE_LEVELS\n"
            "ADVENTURE_LEVELS.clear()\n"
        ),
        (
            "from curriculum.seed_data.source.blueprint import "
            "_adventure_publish_work\n"
            "_adventure_publish_work.clear()\n"
        ),
        (
            "from curriculum.seed_data.source.blueprint.repository_foundations."
            "fresh_starts import LEVELS\n"
            'LEVELS[0]["waves"].clear()\n'
        ),
        (
            "import curriculum.seed_data.source as source\n"
            "source.blueprint._adventure_publish_work.clear()\n"
        ),
        (
            "from .source.blueprint import adventure_publish_work\n"
            "adventure_publish_work.ADVENTURE_LEVELS.clear()\n"
        ),
    ],
)
def test_policy_rejects_rogue_mutable_owner_consumer(
    tmp_path: Path,
    rogue_source: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    rogue_relative_path = (
        "backend/curriculum/seed_data/rogue.py"
        if rogue_source.startswith("from .")
        else "backend/rogue.py"
    )
    rogue = fixture_root / rogue_relative_path
    rogue.parent.mkdir(parents=True, exist_ok=True)
    rogue.write_text(rogue_source, encoding="utf-8")

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "plan owner may appear only" in error
        or "plan consumers must match" in error
        or "implementation modules are owner-private" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "escape",
    [
        (
            "def _mutate_owner(value):\n"
            '    value["repository-foundations"].clear()\n'
            "_mutate_owner(BLUEPRINT_ADVENTURE_LEVELS)"
        ),
        ('alias = BLUEPRINT_ADVENTURE_LEVELS or {}\nalias["repository-foundations"].clear()'),
        ("alias = [levels for levels in BLUEPRINT_ADVENTURE_LEVELS.values()]\nalias[0].clear()"),
        ("alias = [*BLUEPRINT_ADVENTURE_LEVELS.values()]\nalias[0].clear()"),
        (
            "def _return_owner():\n"
            "    return BLUEPRINT_ADVENTURE_LEVELS\n"
            'alias = _return_owner()\nalias["repository-foundations"].clear()'
        ),
        (
            "class _Holder:\n"
            "    value = BLUEPRINT_ADVENTURE_LEVELS\n"
            '_Holder.value["repository-foundations"].clear()'
        ),
        "BLUEPRINT_ADVENTURE_LEVELS.__init__({})",
        'BLUEPRINT_ADVENTURE_LEVELS["repository-foundations"].__init__([])',
    ],
)
def test_policy_rejects_blueprint_escape_in_approved_consumer(
    tmp_path: Path,
    escape: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = "backend/curriculum/seed_data/source/adventure_level_specs/common.py"
    common = fixture_root / relative_path
    common.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative_path, common)
    common.write_text(
        common.read_text(encoding="utf-8") + f"\n{escape}\n",
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("approved use-site structure drifted" in error for error in errors)


def test_policy_rejects_shadowed_blueprint_reader_builtin(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = "backend/curriculum/management/commands/seed_curriculum_structure.py"
    command = fixture_root / relative_path
    command.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative_path, command)
    _mutate(
        fixture_root,
        relative_path,
        ("        from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS"),
        (
            "        def set(value):\n"
            "            value.clear()\n"
            "            return {*()}\n\n"
            "        from curriculum.seed_data.blueprint_overlay import "
            "BLUEPRINT_ADVENTURE_LEVELS"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("must resolve to the unshadowed builtin" in error for error in errors)


@pytest.mark.parametrize(
    "injected_mutation",
    [
        "    row.clear()\n",
        ("    alias = row or {}\n    alias.clear()\n"),
        ("    def _erase(value):\n        value.clear()\n    _erase(row)\n"),
        ("    erase = lambda value: value.clear()\n    erase(row)\n"),
        ("    erase = row.clear\n    erase()\n"),
        ("    erase = dict.clear\n    erase(row)\n"),
        ('    getattr(row, "clear")()\n'),
        ("    erase = (row.clear,)[0]\n    erase()\n"),
        ("    def _identity(value):\n        return value\n    _identity(row).clear()\n"),
        '    import operator\n    operator.setitem(row, "audit-marker", True)\n',
        '    import operator\n    operator.delitem(row, "waves")\n',
        '    import operator\n    operator.ior(row, {"audit-marker": True})\n',
        '    import operator\n    operator.methodcaller("clear")(row)\n',
        '    import operator as op\n    op.setitem(row, "audit-marker", True)\n',
        ('    from operator import setitem as mutate\n    mutate(row, "audit-marker", True)\n'),
        ('    from operator import methodcaller as call\n    call("clear")(row)\n'),
        (
            "    from collections.abc import MutableMapping\n"
            '    MutableMapping.update(row, {"audit-marker": True})\n'
        ),
        ("    from collections.abc import MutableMapping\n    MutableMapping.clear(row)\n"),
        '    import random\n    random.Random(0).shuffle(row["waves"])\n',
        (
            "    from collections.abc import MutableMapping\n"
            "    list = MutableMapping.update\n"
            '    list(row, {"audit-marker": True})\n'
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    def _identity(value):\n"
            "        return value\n"
            "    _identity = MutableMapping.update\n"
            '    _identity(row, {"audit-marker": True})\n'
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    from types import SimpleNamespace\n"
            "    moves = SimpleNamespace(append=MutableMapping.clear)\n"
            "    moves.append(row)\n"
        ),
        "    moves = []\n    moves.append(row)\n    moves[0].clear()\n",
        (
            "    from collections.abc import MutableMapping\n"
            "    copy.deepcopy = MutableMapping.clear\n"
            "    copy.deepcopy(row)\n"
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    from types import SimpleNamespace\n"
            "    lookup = SimpleNamespace(get=MutableMapping.clear)\n"
            "    lookup.get(row)\n"
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    def _replace(_function):\n"
            "        return MutableMapping.clear\n"
            "    @_replace\n"
            "    def _identity(value):\n"
            "        return value\n"
            "    _identity(row)\n"
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    def _identity(value):\n"
            "        return value\n"
            "    match MutableMapping.clear:\n"
            "        case _identity:\n"
            "            _identity(row)\n"
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    def _identity(value):\n"
            "        return value\n"
            "    def _replace(_function):\n"
            "        return MutableMapping.clear\n"
            "    @_replace\n"
            "    def _identity(value):\n"
            "        return value\n"
            "    _identity(row)\n"
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    def _identity(value):\n"
            "        return value\n"
            "    class _identity:\n"
            "        __new__ = staticmethod(MutableMapping.clear)\n"
            "    _identity(row)\n"
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    def _identity(value):\n"
            "        return value\n"
            "    MutatingError = type(\n"
            '        "MutatingError",\n'
            "        (Exception,),\n"
            '        {"__call__": staticmethod(MutableMapping.clear)},\n'
            "    )\n"
            "    try:\n"
            "        raise MutatingError()\n"
            "    except MutatingError as _identity:\n"
            "        _identity(row)\n"
        ),
        (
            "    from collections.abc import MutableMapping\n"
            "    v = MutableMapping.clear\n"
            "    v(row)\n"
        ),
    ],
)
def test_policy_rejects_blueprint_generator_parameter_mutation(
    tmp_path: Path,
    injected_mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        relative_path,
        "def _blueprint_story(adventure_slug: str, level: dict, wave: dict) -> str:\n",
        (
            "def _blueprint_story(adventure_slug: str, row: dict, wave: dict) -> str:\n"
            f"{injected_mutation}"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_blueprint_generator_local_sink_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        relative_path,
        '        label = labels.get(family, "repository state work")',
        (
            '        label = commands["waves"]\n'
            "        moves.append(label)\n"
            "        moves[0].clear()\n"
            "        moves.clear()"
        ),
    )
    _mutate(
        fixture_root,
        relative_path,
        "def _blueprint_story(adventure_slug: str, level: dict, wave: dict) -> str:\n",
        (
            "def _blueprint_story(adventure_slug: str, level: dict, wave: dict) -> str:\n"
            "    _blueprint_move_summary(level)\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_blueprint_generator_global_lookup_rebinding(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        relative_path,
        "_BLUEPRINT_STATE_BRIEFS = {",
        (
            "from collections.abc import MutableMapping\n"
            "from types import SimpleNamespace\n"
            "_BLUEPRINT_ADVENTURE_COPY = "
            "SimpleNamespace(get=MutableMapping.clear)\n\n"
            "_BLUEPRINT_STATE_BRIEFS = {"
        ),
    )
    _mutate(
        fixture_root,
        relative_path,
        "def _blueprint_story(adventure_slug: str, level: dict, wave: dict) -> str:\n",
        (
            "def _blueprint_story(adventure_slug: str, level: dict, wave: dict) -> str:\n"
            "    _BLUEPRINT_ADVENTURE_COPY.get(level)\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_target_state_loop_rebinding(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        "for TARGET_STATES in ({},):\n    pass\n\ndef v(\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_target_state_loop_subscript_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        'for TARGET_STATES["new"] in [1]:\n    pass\n\ndef v(\n',
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_target_state_with_subscript_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "from contextlib import nullcontext\n\n"
            'with nullcontext(1) as TARGET_STATES["new"]:\n'
            "    pass\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_invalidates_fresh_sink_rebound_by_with(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "from contextlib import nullcontext\n\n"
            "_sink = []\n"
            "_external = []\n"
            "with nullcontext(_external) as _sink:\n"
            "    _sink.append(TARGET_STATES)\n"
            "_external[0].clear()\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_does_not_treat_reassigned_parameter_as_fresh_sink(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "_external = []\n\n"
            "def _attack(sink):\n"
            "    if False:\n"
            "        sink = []\n"
            "    sink.append(TARGET_STATES)\n\n"
            "_attack(_external)\n"
            "_external[0].clear()\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_destructured_owner_subscript_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        '(TARGET_STATES["new"],) = (1,)\n\ndef v(\n',
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_destructured_owner_escape_to_nested_sink(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "_external = [None]\n"
            "(_external[0],) = (TARGET_STATES,)\n"
            "_external[0].clear()\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_destructured_target_state_rebinding(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        "(TARGET_STATES,) = ({},)\n\ndef v(\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize("namespace", ["globals", "vars", "locals"])
def test_policy_rejects_target_state_namespace_rebinding(
    tmp_path: Path,
    namespace: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        f'{namespace}()["TARGET_STATES"] = {{}}\n\ndef v(\n',
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "namespace_expression",
    [
        "globals()",
        "globals() if True else globals()",
        "[globals()][0]",
        '{"namespace": globals()}["namespace"]',
    ],
)
def test_policy_rejects_target_state_namespace_alias_rebinding(
    tmp_path: Path,
    namespace_expression: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (f'namespace = {namespace_expression}\nnamespace["TARGET_STATES"] = {{}}\n\ndef v(\n'),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_destructured_namespace_alias_rebinding(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        ('(namespace,) = (globals(),)\nnamespace["TARGET_STATES"] = {}\n\ndef v(\n'),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_helper_returned_namespace_rebinding(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "def _namespace():\n"
            "    return globals()\n\n"
            '_namespace()["TARGET_STATES"] = {}\n\n'
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_factory_returned_namespace_callable(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "def _namespace_factory():\n"
            "    return lambda: globals()\n\n"
            '_namespace_factory()()["TARGET_STATES"] = {}\n\n'
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_namespace_argument_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "def _attack(namespace):\n"
            '    namespace["TARGET_STATES"] = {}\n\n'
            "_attack(globals())\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_namespace_varargs_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "def _attack(*namespaces):\n"
            '    namespaces[0]["TARGET_STATES"] = {}\n\n'
            "_attack(globals())\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_default_namespace_argument_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "def _attack(namespace=globals()):\n"
            '    namespace["TARGET_STATES"] = {}\n\n'
            "_attack()\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_default_callable_owner_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "def _attack(getter=lambda: TARGET_STATES):\n"
            "    getter().clear()\n\n"
            "_attack()\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_partial_namespace_argument_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "from functools import partial\n\n"
            "def _attack(namespace):\n"
            '    namespace["TARGET_STATES"] = {}\n\n'
            "_run = partial(_attack, globals())\n"
            "_run()\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_unbound_namespace_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        ('dict.__setitem__(globals(), "TARGET_STATES", {})\n\ndef v(\n'),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "mutation",
    [
        "sys.modules[__name__].TARGET_STATES = {}",
        'setattr(sys.modules[__name__], "TARGET_STATES", {})',
        'delattr(sys.modules[__name__], "TARGET_STATES")',
        'sys.modules[__name__].__setattr__("TARGET_STATES", {})',
        'sys.modules[__name__].__delattr__("TARGET_STATES")',
        'object.__setattr__(sys.modules[__name__], "TARGET_STATES", {})',
        'object.__delattr__(sys.modules[__name__], "TARGET_STATES")',
    ],
)
def test_policy_rejects_sys_modules_owner_rebinding(
    tmp_path: Path,
    mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (f"import sys\n\n{mutation}\n\ndef v(\n"),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "binding",
    [
        "def TARGET_STATES():\n    return None",
        "async def TARGET_STATES():\n    return None",
        "class TARGET_STATES:\n    pass",
        "import contextlib\nwith contextlib.nullcontext({}) as TARGET_STATES:\n    pass",
        "try:\n    raise RuntimeError\nexcept RuntimeError as TARGET_STATES:\n    pass",
        "match {}:\n    case TARGET_STATES:\n        pass",
        (
            "def _replace_target_states():\n"
            "    global TARGET_STATES\n"
            "    import types as TARGET_STATES"
        ),
        "from types import SimpleNamespace as TARGET_STATES",
        "type TARGET_STATES = dict",
    ],
)
def test_policy_rejects_target_state_statement_rebinding(
    tmp_path: Path,
    binding: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        f"{binding}\n\ndef v(\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_mutating_blueprint_generator_helper_contract(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ("    workspace_files: list[dict] | None = None,\n) -> dict:\n    return {"),
        (
            "    workspace_files: list[dict] | None = None,\n"
            ") -> dict:\n"
            "    if workspace_files:\n"
            "        workspace_files[0].clear()\n"
            "    return {"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_mutating_blueprint_level_builder_contract(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ('    level_type: str = "guided_workflow",\n) -> dict:\n    # `workflow=True`'),
        (
            '    level_type: str = "guided_workflow",\n'
            ") -> dict:\n"
            "    checks.clear()\n"
            "    # `workflow=True`"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_transitive_blueprint_helper_sink(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _sink_owner(value):\n"
            "    value.clear()\n\n"
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    _sink_owner(checks)\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_transitive_spec_helper_sink(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/spec_helpers.py",
        "def enrich_context_with_required_details(\n",
        (
            "def _sink_owner(value):\n"
            "    value.clear()\n\n"
            "def enrich_context_with_required_details(\n"
        ),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/spec_helpers.py",
        "    enriched = copy.deepcopy(context)\n",
        "    _sink_owner(evaluation_spec)\n    enriched = copy.deepcopy(context)\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_non_fresh_blueprint_helper_sink(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "    merged_details: list[dict] = []\n",
        "    merged_details = details\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "injected_mutation",
    [
        "    scratch += [checks]\n",
        "    scratch[0:0] += [checks]\n",
    ],
)
def test_policy_rejects_augmented_fresh_sink_alias_mutation(
    tmp_path: Path,
    injected_mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    scratch = []\n"
            f"{injected_mutation}"
            "    scratch[0].clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_nested_fresh_sink_alias_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    inner = []\n"
            "    outer = []\n"
            "    outer.append(inner)\n"
            "    inner.append(checks)\n"
            "    outer[0][0].clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_nested_fresh_sink_subscript_write(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    outer = {'inner': [None]}\n"
            "    outer['inner'][0] = checks\n"
            "    outer['inner'][0].clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "injected_mutation",
    [
        (
            "    outer = {'inner': [None]}\n"
            "    for outer['inner'][0] in [checks]:\n"
            "        pass\n"
            "    outer['inner'][0].clear()\n"
        ),
        (
            "    def holder():\n"
            "        pass\n"
            "    for holder.value in [checks]:\n"
            "        pass\n"
            "    holder.value.clear()\n"
        ),
    ],
)
def test_policy_rejects_owner_escape_through_loop_target(
    tmp_path: Path,
    injected_mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        f"def _modular_checks(checks: list[dict] | None) -> list[dict]:\n{injected_mutation}",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_enumerated_fresh_sink_alias_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    outer = []\n"
            "    outer.append(checks)\n"
            "    for _, item in enumerate(outer):\n"
            "        item.clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_preserves_owner_provenance_through_safe_helper_returns(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _variant_safe_checks(usage: str, checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _variant_safe_checks(usage: str, checks: list[dict] | None) -> list[dict]:\n"
            "    holder = []\n"
            "    holder.extend(checks or [])\n"
            "    copied = _modular_checks(holder)\n"
            "    copied[0]['requirement'].clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_preserves_owner_provenance_through_trusted_generator_returns(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        relative_path,
        "def _blueprint_variant_state(initial: dict, *, alternate: bool) -> dict:\n",
        (
            "def _blueprint_variant_state(initial: dict, *, alternate: bool) -> dict:\n"
            "    holder = []\n"
            "    holder.append(initial)\n"
            "    wrapped = v('probe', 'probe', holder, [], {})\n"
            "    wrapped['initial_state_template'][0].clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "capture_expression",
    [
        "sink.setdefault('holder', holder)",
        "sink.get('holder', holder)",
        "sink.pop('holder', holder)",
    ],
)
def test_policy_preserves_owner_provenance_through_safe_sink_returns(
    tmp_path: Path,
    capture_expression: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    holder = []\n"
            "    holder.append(checks)\n"
            "    sink = {}\n"
            f"    captured = {capture_expression}\n"
            "    captured[0].clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "capture_expression",
    [
        "holder and holder[0]",
        "holder[0] if holder else None",
    ],
)
def test_policy_preserves_owner_provenance_through_conditional_extraction(
    tmp_path: Path,
    capture_expression: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    holder = []\n"
            "    holder.append(checks)\n"
            f"    captured = {capture_expression}\n"
            "    captured.clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "capture_expression",
    [
        "[item for item in holder][0]",
        "{'item': item for item in holder}['item']",
    ],
)
def test_policy_preserves_owner_provenance_through_comprehensions(
    tmp_path: Path,
    capture_expression: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    holder = []\n"
            "    holder.append(checks)\n"
            f"    captured = {capture_expression}\n"
            "    captured.clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_preserves_owner_provenance_through_container_composition(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    holder = []\n"
            "    holder.append(checks)\n"
            "    captured = holder[0] + []\n"
            "    captured[0].clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_preserves_owner_provenance_through_named_expression(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    captured = (temporary := checks)\n"
            "    captured.clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_iterator_dunder_on_owner_container(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    holder = []\n"
            "    holder.append(checks)\n"
            "    captured = holder.__iter__().__next__()\n"
            "    captured.clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_bound_owner_mutator_in_mapping(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    operations = {'clear': checks.clear}\n"
            "    operations['clear']()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "injected_mutation",
    [
        ("    def holder():\n        pass\n    holder.value = checks\n    holder.value.clear()\n"),
        (
            "    class Holder(dict):\n"
            "        pass\n"
            "    holder = Holder()\n"
            "    holder['value'] = checks\n"
            "    holder['value'].clear()\n"
        ),
    ],
)
def test_policy_rejects_untrusted_owner_sink_assignment(
    tmp_path: Path,
    injected_mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        f"def _modular_checks(checks: list[dict] | None) -> list[dict]:\n{injected_mutation}",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_cross_scope_owner_escape(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _adventure_for_usage(usage: str) -> str:\n",
        (
            "_OWNER_STASH = None\n\n"
            "def _mutate_owner_stash():\n"
            "    _OWNER_STASH.clear()\n\n"
            "def _adventure_for_usage(usage: str) -> str:\n"
        ),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    global _OWNER_STASH\n"
            "    _OWNER_STASH = checks\n"
            "    _mutate_owner_stash()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "injected_mutation",
    [
        "    def stash(value=checks):\n        return value\n    stash().clear()\n",
        "    def stash():\n        return checks\n    stash().clear()\n",
        "    stash = lambda: checks\n    stash().clear()\n",
    ],
)
def test_policy_rejects_nested_callable_owner_capture(
    tmp_path: Path,
    injected_mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        f"def _modular_checks(checks: list[dict] | None) -> list[dict]:\n{injected_mutation}",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_module_callable_owner_default_capture(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        ("def _target_default(value=TARGET_STATES):\n    return value\n\ndef v(\n"),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        ") -> dict:\n    _target_default().clear()\n    return {\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_module_callable_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        ("def _target_global():\n    return TARGET_STATES\n\ndef v(\n"),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        ") -> dict:\n    _target_global().clear()\n    return {\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_module_lambda_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        "_target_lambda = lambda: TARGET_STATES\n\ndef v(\n",
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        ") -> dict:\n    _target_lambda().clear()\n    return {\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_module_dictionary_callable_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        'getters = {"target": lambda: TARGET_STATES}\n\ndef v(\n',
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        ') -> dict:\n    getters["target"]().clear()\n    return {\n',
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_module_iterated_callable_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        "getters = [lambda: TARGET_STATES]\n\ndef v(\n",
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (") -> dict:\n    for getter in getters:\n        getter().clear()\n    return {\n"),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_wrapped_iterated_callable_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        "getters = [lambda: TARGET_STATES]\n\ndef v(\n",
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (") -> dict:\n    for getter in iter(getters):\n        getter().clear()\n    return {\n"),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_yielded_callable_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        ("def _target_getters():\n    yield lambda: TARGET_STATES\n\ndef v(\n"),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (
            ") -> dict:\n"
            "    for getter in _target_getters():\n"
            "        getter().clear()\n"
            "    return {\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_attribute_callable_owner_escape(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "class _TargetBox:\n"
            "    pass\n\n"
            "target_box = _TargetBox()\n"
            "target_box.get = lambda: TARGET_STATES\n\n"
            "def v(\n"
        ),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        ") -> dict:\n    target_box.get().clear()\n    return {\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


@pytest.mark.parametrize(
    "injected_mutation",
    [
        (
            "    getters = []\n"
            "    getters.append(lambda: TARGET_STATES)\n"
            "    for getter in getters:\n"
            "        getter().clear()\n"
        ),
        (
            "    getters = {}\n"
            '    getters["target"] = lambda: TARGET_STATES\n'
            "    for getter in getters.values():\n"
            "        getter().clear()\n"
        ),
    ],
)
def test_policy_tracks_fresh_container_callable_owner_return(
    tmp_path: Path,
    injected_mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        f") -> dict:\n{injected_mutation}    return {{\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_tracks_aliased_fresh_container_callable_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (
            ") -> dict:\n"
            "    getters = []\n"
            "    alias = getters\n"
            "    alias.append(lambda: TARGET_STATES)\n"
            "    getters[0]().clear()\n"
            "    return {\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_tracks_conditional_fresh_container_callable_owner_return(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (
            ") -> dict:\n"
            "    getters = []\n"
            "    alias = getters if True else getters\n"
            "    alias.append(lambda: TARGET_STATES)\n"
            "    getters[0]().clear()\n"
            "    return {\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_tracks_destructured_fresh_container_callable_owner_return(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (
            ") -> dict:\n"
            "    getters = []\n"
            "    (alias,) = (getters,)\n"
            "    alias.append(lambda: TARGET_STATES)\n"
            "    getters[0]().clear()\n"
            "    return {\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_tracks_selected_fresh_container_callable_owner_return(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (
            ") -> dict:\n"
            "    getters = []\n"
            "    alias = [getters][0]\n"
            "    alias.append(lambda: TARGET_STATES)\n"
            "    getters[0]().clear()\n"
            "    return {\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_callable_owner_escape_to_helper_returned_sink(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (
            ") -> dict:\n"
            "    getters = []\n"
            "    def sink():\n"
            "        return getters\n"
            "    sink().append(lambda: TARGET_STATES)\n"
            "    getters[0]().clear()\n"
            "    return {\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_callable_owner_escape_in_dictionary_key(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        ("def _consume(items):\n    next(iter(items))().clear()\n\ndef v(\n"),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (") -> dict:\n    _consume({(lambda: TARGET_STATES): None})\n    return {\n"),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_composed_callable_owner_container(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        (
            ") -> dict:\n"
            "    getters = [lambda: TARGET_STATES] + []\n"
            "    getters[0]().clear()\n"
            "    return {\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_awaited_callable_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "async def _getter():\n"
            "    return lambda: TARGET_STATES\n\n"
            "async def _attack():\n"
            "    (await _getter())().clear()\n\n"
            "def v(\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_module_callable_class_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        ("class _TargetGetter:\n    def __call__(self):\n        return TARGET_STATES\n\ndef v(\n"),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        ") -> dict:\n    _TargetGetter()().clear()\n    return {\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_module_generator_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        ("def _target_generator():\n    yield TARGET_STATES\n\ndef v(\n"),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        ") -> dict:\n    next(_target_generator()).clear()\n    return {\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_module_async_owner_return(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "import copy\n",
        "import asyncio\nimport copy\n",
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def v(\n",
        (
            "async def _target_async():\n"
            "    return TARGET_STATES\n\n"
            "async def _clear_target_async():\n"
            "    (await _target_async()).clear()\n\n"
            "def v(\n"
        ),
    )
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        ") -> dict:\n    return {\n",
        ") -> dict:\n    asyncio.run(_clear_target_async())\n    return {\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(
        "blueprint generator helper parameters must be read-only" in error for error in errors
    )


def test_policy_rejects_nested_callable_owner_container_capture(
    tmp_path: Path,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        (
            "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n"
            "    holder = []\n"
            "    holder.append(checks)\n"
            "    def stash():\n"
            "        return holder[0]\n"
            "    stash().clear()\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    "injected_mutation",
    [
        "    match [checks]:\n        case [item]:\n            item.clear()\n",
        "    match checks:\n        case [item, *_]:\n            item.clear()\n",
    ],
)
def test_policy_rejects_match_bound_owner_alias(
    tmp_path: Path,
    injected_mutation: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "def _modular_checks(checks: list[dict] | None) -> list[dict]:\n",
        f"def _modular_checks(checks: list[dict] | None) -> list[dict]:\n{injected_mutation}",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_trusted_deepcopy_module_alias(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        "import copy\n",
        "import copy\n_COPY_ALIAS = copy\n_COPY_ALIAS.deepcopy = lambda value: value\n",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_generator_deepcopy_alias_import(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        relative_path,
        "from .common import *  # noqa: F403\n",
        (
            "from .common import *  # noqa: F403\n"
            "import copy as copy_alias\n"
            "copy_alias.deepcopy = lambda value: value\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_trusted_callable_attribute_patch(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        '\n\n__all__ = [name for name in globals() if not name.startswith("__")]\n',
        (
            "\n\ndef _rogue_q(*args, **kwargs):\n"
            "    args[5].clear()\n"
            "    return {}\n\n"
            "q.__code__ = _rogue_q.__code__\n\n"
            '__all__ = [name for name in globals() if not name.startswith("__")]\n'
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_trusted_command_mapping_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _copy_blueprint_generator_sources(fixture_root)
    path = fixture_root / "backend/curriculum/seed_data/source/command_routing.py"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nADVENTURE_BY_COMMAND.clear()\n",
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_trusted_generator_mapping_mutation(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = _copy_blueprint_generator_sources(fixture_root)
    _mutate(
        fixture_root,
        relative_path,
        "def _blueprint_story(adventure_slug: str, level: dict, wave: dict) -> str:\n",
        (
            "_BLUEPRINT_STATE_BRIEFS.clear()\n\n"
            "def _blueprint_story(adventure_slug: str, level: dict, wave: dict) -> str:\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


def test_policy_rejects_blueprint_generator_helper_import_override(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    relative_path = _copy_blueprint_generator_sources(fixture_root)
    rogue = fixture_root / "backend/curriculum/seed_data/source/adventure_level_specs/rogue.py"
    rogue.write_text(
        "from collections.abc import MutableMapping\nv = MutableMapping.clear\n__all__ = ['v']\n",
        encoding="utf-8",
    )
    _mutate(
        fixture_root,
        relative_path,
        "from .common import *  # noqa: F403",
        ("from .common import *  # noqa: F403\nfrom .rogue import *  # noqa: F403"),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("generator helper parameters must be read-only" in error for error in errors)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        (
            "    plan = _wave_plan_levels(ADVENTURE_WAVE_PLANS.get(adventure_slug, []))",
            (
                "    plan = _wave_plan_levels("
                "ADVENTURE_WAVE_PLANS.get(adventure_slug, [])\n"
                "    )\n"
                "    plan.clear()"
            ),
        ),
        ("    if not plan:", "    if not plan.clear():"),
    ],
)
def test_policy_rejects_post_read_plan_mutation(
    tmp_path: Path,
    old: str,
    new: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py",
        old,
        new,
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("canonical ADVENTURE_WAVE_PLANS reader contract" in error for error in errors)


def test_policy_rejects_transitive_canonical_reader_sink(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    path = "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py"
    _mutate(
        fixture_root,
        path,
        "def _level(slug: str, title: str, *, waves: list[str], reuse: list[str] | None = None) -> dict:\n",
        (
            "def _sink_owner(value):\n"
            "    value.clear()\n\n"
            "def _level(slug: str, title: str, *, waves: list[str], reuse: list[str] | None = None) -> dict:\n"
        ),
    )
    _mutate(
        fixture_root,
        path,
        "    plan = _wave_plan_levels(ADVENTURE_WAVE_PLANS.get(adventure_slug, []))\n",
        (
            "    plan = _wave_plan_levels(ADVENTURE_WAVE_PLANS.get(adventure_slug, []))\n"
            "    _sink_owner(plan)\n"
        ),
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("canonical ADVENTURE_WAVE_PLANS reader contract" in error for error in errors)


@pytest.mark.parametrize(
    "binding",
    [
        (
            "class _merge_disjoint_adventure_wave_plans:\n"
            "    def __new__(cls, *owners):\n"
            "        return owners[-1]"
        ),
        ("from alternate_owner import replacement as _merge_disjoint_adventure_wave_plans"),
    ],
)
def test_policy_rejects_string_bound_helper_rebinding(
    tmp_path: Path,
    binding: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    adventures = fixture_root / "backend/curriculum/seed_data/adventures.py"
    adventures.write_text(
        adventures.read_text(encoding="utf-8") + f"\n{binding}\n",
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("critical adventure composition symbol binding drifted" in error for error in errors)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        (
            "if duplicates:\n            raise ValueError(",
            "if False and duplicates:\n            raise ValueError(",
        ),
        ("        merged.update(owner)", "        merged |= owner"),
        (
            "duplicates = sorted(merged.keys() & owner.keys())",
            "duplicates = list(merged.keys() & owner.keys())",
        ),
    ],
)
def test_policy_rejects_silenced_or_nondeterministic_merge_guard(
    tmp_path: Path,
    old: str,
    new: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/adventures.py",
        old,
        new,
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("exact guard-before-merge contract" in error for error in errors)


@pytest.mark.parametrize(
    ("prefix", "replacement", "expected"),
    [
        (
            "Foundational adventure order mismatch: ",
            "Order mismatch: ",
            "exact validated order contract",
        ),
        (
            "Duplicate adventure wave plan owner(s): ",
            "Duplicate owner: ",
            "exact guard-before-merge contract",
        ),
    ],
)
def test_policy_rejects_collision_message_drift(
    tmp_path: Path,
    prefix: str,
    replacement: str,
    expected: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/adventures.py",
        prefix,
        replacement,
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any(expected in error for error in errors)


@pytest.mark.parametrize(
    "legacy_reference",
    [
        "ADVENTURE_LEVEL_PLAN = {}",
        ("from curriculum.seed_data.adventure_levels import ADVENTURE_LEVEL_PLAN"),
        "legacy.ADVENTURE_LEVEL_PLAN",
        "class ADVENTURE_LEVEL_PLAN:\n    pass",
        "def ADVENTURE_LEVEL_PLAN():\n    pass",
        "def marker[ADVENTURE_LEVEL_PLAN]():\n    pass",
        "from alternate_owner import replacement as ADVENTURE_LEVEL_PLAN",
        "ＡＤＶＥＮＴＵＲＥ_LEVEL_PLAN = {}",
    ],
)
def test_policy_rejects_restored_legacy_consumer(
    tmp_path: Path,
    legacy_reference: str,
):
    fixture_root = _copy_policy_fixture(tmp_path)
    writer = fixture_root / "backend/curriculum/management/commands/seed_curriculum_writer.py"
    writer.write_text(
        writer.read_text(encoding="utf-8") + f"\n{legacy_reference}\n",
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("legacy adventure plan references remain" in error for error in errors)


def test_policy_rejects_nfkc_equivalent_public_plan_consumer(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    rogue = fixture_root / "backend/rogue.py"
    rogue.write_text(
        (
            "from curriculum.seed_data.adventures import "
            "ＡＤＶＥＮＴＵＲＥ_WAVE_PLANS\n"
            "ＡＤＶＥＮＴＵＲＥ_WAVE_PLANS.clear()\n"
        ),
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("may appear only in its owner and canonical reader" in error for error in errors)


def test_policy_rejects_legacy_wrapper_export(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    _mutate(
        fixture_root,
        "backend/curriculum/seed_data/adventure_levels.py",
        '"ADVENTURE_LEVELS", "SPEC_BY_SLUG"',
        '"ADVENTURE_LEVELS", "ADVENTURE_LEVEL_PLAN", "SPEC_BY_SLUG"',
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("__all__" in error for error in errors)
    assert any("legacy adventure plan references remain" in error for error in errors)


def test_policy_rejects_stale_authoring_guide(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    guide = fixture_root / "CONTENT_AUTHORING_GUIDE.md"
    guide.write_text(
        guide.read_text(encoding="utf-8") + "\nGroup levels through ADVENTURE_LEVEL_PLAN.\n",
        encoding="utf-8",
    )

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("authoring guide still recommends" in error for error in errors)


def test_policy_rejects_restored_chapter_scaffold(tmp_path: Path):
    fixture_root = _copy_policy_fixture(tmp_path)
    scaffold = fixture_root / "backend/curriculum/seed_data/source/ch1/README.md"
    scaffold.parent.mkdir(parents=True)
    scaffold.write_text("Legacy migration destination.\n", encoding="utf-8")

    errors = adventure_plan_ownership_errors(root=fixture_root)

    assert any("legacy Chapter 1 scaffold path remains" in error for error in errors)


@pytest.mark.parametrize(
    "module",
    [public_adventure_levels, source_adventure_levels, adventure_level_specs],
)
def test_retained_wrappers_omit_legacy_plan_and_keep_supported_api(module):
    assert not hasattr(module, "ADVENTURE_LEVEL_PLAN")
    assert module.__all__ == [
        "ADVENTURE_LEVELS",
        "SPEC_BY_SLUG",
        "adventure_levels_for",
    ]
    assert module.ADVENTURE_LEVELS
    assert module.SPEC_BY_SLUG
    assert callable(module.adventure_levels_for)
