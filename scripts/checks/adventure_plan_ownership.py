#!/usr/bin/env python3
"""Enforce maintainable ownership boundaries in authored curriculum source."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import sys
import unicodedata

if __package__:
    from . import mutable_owner_analysis as _owner_analysis
else:
    import mutable_owner_analysis as _owner_analysis


MUTATING_METHODS = _owner_analysis.MUTATING_METHODS
_MutableOwnerAnalyzer = _owner_analysis.MutableOwnerAnalyzer
_function_parameters = _owner_analysis.function_parameters
_literal_immutable_value = _owner_analysis.literal_immutable_value
_mutable_owner_mutations = _owner_analysis.mutable_owner_mutations
_root_name = _owner_analysis.root_name
_scope_bindings = _owner_analysis.scope_bindings


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
ADVENTURES_SOURCE = ROOT / "backend/curriculum/seed_data/adventures.py"
AUTHORING_GUIDE = ROOT / "CONTENT_AUTHORING_GUIDE.md"
PUBLIC_ADVENTURE_LEVELS = ROOT / "backend/curriculum/seed_data/adventure_levels.py"
SOURCE_ADVENTURE_LEVELS = (
    ROOT / "backend/curriculum/seed_data/source/adventure_levels.py"
)
ADVENTURE_LEVEL_SPECS = (
    ROOT / "backend/curriculum/seed_data/source/adventure_level_specs/__init__.py"
)
LEVEL_PLAN = (
    ROOT / "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py"
)
SEED_WRITER = ROOT / "backend/curriculum/management/commands/seed_curriculum_writer.py"
SOURCE_PACKAGE = ROOT / "backend/curriculum/seed_data/source/__init__.py"
LEGACY_CHAPTER_PACKAGE = ROOT / "backend/curriculum/seed_data/source/ch1"
ADVENTURE_POLICY_TEST = (
    ROOT / "backend/curriculum/tests/test_adventure_plan_ownership.py"
)

FOUNDATIONAL_ADVENTURE_ORDER = (
    "repository-foundations",
    "stage-with-intent",
    "seal-the-snapshot",
    "untrack-and-undo-edits",
    "create-and-move",
    "detach-and-clean",
    "integrate-branches",
    "resolve-conflicts",
    "manage-the-merge",
    "step-back-safely",
    "reverse-and-recover",
    "shelve-work",
    "transplant-commits",
    "connect-and-inspect",
    "integrate-upstream",
    "publish-work",
)
BLUEPRINT_ADVENTURE_MODULES = tuple(
    f"adventure_{slug.replace('-', '_')}" for slug in FOUNDATIONAL_ADVENTURE_ORDER
)
BLUEPRINT_REPOSITORY_FOUNDATION_MODULES = (
    "cloning",
    "configuration",
    "founding_workflows",
    "fresh_start_drills",
    "fresh_starts",
    "history_and_status",
    "inspection_drills",
)
ADVANCED_DRILL_ADVENTURES = (
    "frost-temper-the-commit-drills",
    "frost-choose-the-integration-drills",
    "frost-survive-the-conflict-drills",
    "frost-move-the-patch-drills",
    "frost-reforge-the-branch-drills",
    "frost-govern-the-remote-drills",
    "frost-deliver-the-release-drills",
    "frost-hunt-the-regression-drills",
    "frost-publish-the-core-drills",
    "skyline-revision-language-drills",
    "skyline-hidden-history-drills",
    "skyline-repeated-conflict-drills",
    "skyline-many-realities-drills",
    "skyline-enchant-behavior-drills",
    "skyline-guard-the-archive-drills",
    "skyline-restore-maintain-drills",
    "skyline-serve-the-city-drills",
    "skyline-migrate-the-grid-drills",
    "skyline-git-machinery-drills",
)

BLUEPRINT_PLAN_CONSUMERS = (
    "backend/curriculum/management/commands/seed_curriculum_structure.py",
    "backend/curriculum/seed_data/adventures.py",
    "backend/curriculum/seed_data/blueprint_overlay.py",
    "backend/curriculum/seed_data/source/adventure_level_specs/blueprint_generated.py",
    "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
    "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py",
    "backend/curriculum/seed_data/source/blueprint/__init__.py",
    "backend/curriculum/seed_data/source/blueprint_overlay.py",
    "backend/curriculum/tests/test_blueprint_pedagogy_invariants.py",
    "backend/curriculum/tests/test_chapter_content_invariants.py",
)
BLUEPRINT_PLAN_USAGE_HASHES = {
    "backend/curriculum/management/commands/seed_curriculum_structure.py": (
        "D5FA1A0D82A122BBD0C41E52152192841AF2EBD8BCC5ACFACE493505502B511D",
        "D6E4AB62AC906AEF9AC9FFF8E33224837AA4D29B9521F75F7AA2B3DDE7327B4E",
    ),
    "backend/curriculum/seed_data/adventures.py": (
        "633284DAC06EF977B2AEC4A1F5390AC49915760630B585A5E4028CBDA18631BD",
        "D6E4AB62AC906AEF9AC9FFF8E33224837AA4D29B9521F75F7AA2B3DDE7327B4E",
    ),
    "backend/curriculum/seed_data/blueprint_overlay.py": (
        "56247224A60FD9B06FB452FE9ABBE317A748773C6EEF2DFCF2A9EEA33C0BF6C5",
        "927F77B111117C07694319BB5C6BF38E0267D1C2FFF2B5F38834C02CDC7EF859",
    ),
    "backend/curriculum/seed_data/source/adventure_level_specs/blueprint_generated.py": (
        "5F67A4226D6A186715F96B05556515DF403ACA5133EF26696B115EEC35F1B5F6",
    ),
    "backend/curriculum/seed_data/source/adventure_level_specs/common.py": (
        "D6E4AB62AC906AEF9AC9FFF8E33224837AA4D29B9521F75F7AA2B3DDE7327B4E",
    ),
    "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py": (
        "AC8AC0D6244921C0368438A48E381AB0AAB3D67CD4D9FB16B0494CA8D8A7944B",
        "D6E4AB62AC906AEF9AC9FFF8E33224837AA4D29B9521F75F7AA2B3DDE7327B4E",
    ),
    "backend/curriculum/seed_data/source/blueprint/__init__.py": (
        "56247224A60FD9B06FB452FE9ABBE317A748773C6EEF2DFCF2A9EEA33C0BF6C5",
        "B4CC2AEEC54F10D73BC4896E01AD8A66F05952C6275D2B718E891DFAE244AA55",
    ),
    "backend/curriculum/seed_data/source/blueprint_overlay.py": (
        "56247224A60FD9B06FB452FE9ABBE317A748773C6EEF2DFCF2A9EEA33C0BF6C5",
        "C76A72CF12A7C19ACA59C5F5BBFF7A25C28AB93FB72C7E22C05D6BA8272F88D9",
    ),
    "backend/curriculum/tests/test_blueprint_pedagogy_invariants.py": (
        "D6E4AB62AC906AEF9AC9FFF8E33224837AA4D29B9521F75F7AA2B3DDE7327B4E",
        "EC2441B430F3FA92DC097E0648BB38638CA682D99734979027A10A30B3C39D26",
    ),
    "backend/curriculum/tests/test_chapter_content_invariants.py": (
        "0D9D9992A89602985D12667950CE587C45D38ABFFCB1EDE850E2414390915712",
        "12A8826C154FB7EFE7B1A357B15B0B69FE02099ACE82A4DF4848C02C2AE5E223",
        "5DE0C96EAA73430CBE3954D2364AAB3D9FBE0B694005EE7182C9588BC6ECC229",
        "A1BDB05BC225EE278E26DA0C7C99DA9DFB93BEA96039F5147885730D758CB2BF",
    ),
}

LEGACY_PLAN_SYMBOL = "ADVENTURE_LEVEL_PLAN"
READ_ONLY_PARAMETER_CALLABLES = frozenset(
    {"all", "any", "enumerate", "isinstance", "len", "list", "str"}
)

EXPECTED_WAVES_HELPER = ast.parse(
    '''
def _waves(*scenario_slugs: str) -> list[list[str]]:
    """One monster per wave: each scenario slug becomes its own single-slot wave."""
    return [[slug] for slug in scenario_slugs]
'''
).body[0]

EXPECTED_FOUNDATIONAL_PROJECTION = ast.parse(
    '''
def _ordered_foundational_adventure_wave_plans(
    blueprint_plans: dict[str, list[dict]],
    order: tuple[str, ...],
) -> dict[str, list[dict]]:
    """Project blueprint-owned plans into the stable public adventure order."""

    order_keys = set(order)
    blueprint_keys = set(blueprint_plans)
    missing = sorted(blueprint_keys - order_keys)
    extra = sorted(order_keys - blueprint_keys)
    duplicates = sorted({slug for slug in order if order.count(slug) > 1})
    if missing or extra or duplicates:
        raise ValueError(
            "Foundational adventure order mismatch: "
            f"missing={missing}, extra={extra}, duplicates={duplicates}"
        )
    return {slug: blueprint_plans[slug] for slug in order}
'''
).body[0]
EXPECTED_DISJOINT_MERGER = ast.parse(
    '''
def _merge_disjoint_adventure_wave_plans(
    *owners: dict[str, list[dict]],
) -> dict[str, list[dict]]:
    """Compose plan owners while rejecting every duplicate key."""

    merged: dict[str, list[dict]] = {}
    for owner in owners:
        duplicates = sorted(merged.keys() & owner.keys())
        if duplicates:
            raise ValueError(
                "Duplicate adventure wave plan owner(s): " + ", ".join(duplicates)
            )
        merged.update(owner)
    return merged
'''
).body[0]
EXPECTED_PUBLIC_PLAN_READ = ast.parse(
    "_wave_plan_levels(ADVENTURE_WAVE_PLANS.get(adventure_slug, []))",
    mode="eval",
).body
EXPECTED_COMMON_ALL_ASSIGNMENT = ast.parse(
    '__all__ = [name for name in globals() if not name.startswith("__")]',
).body[0]
EXPECTED_CRITICAL_NAME_CONTEXTS = {
    "ADVENTURE_WAVE_PLANS": ["Store"],
    "_merge_disjoint_adventure_wave_plans": ["Load"],
    "_ordered_foundational_adventure_wave_plans": ["Load"],
    "_FOUNDATIONAL_ADVENTURE_ORDER": ["Load", "Store"],
    "_ADVANCED_DRILL_WAVE_PLANS": ["Load", "Store"],
    "BLUEPRINT_ADVENTURE_LEVELS": ["Load"],
}
EXPECTED_CRITICAL_BINDINGS = {
    "_waves": ["function"],
    "ADVENTURE_WAVE_PLANS": ["store"],
    "_merge_disjoint_adventure_wave_plans": ["function"],
    "_ordered_foundational_adventure_wave_plans": ["function"],
    "_FOUNDATIONAL_ADVENTURE_ORDER": ["store"],
    "_ADVANCED_DRILL_WAVE_PLANS": ["store"],
    "BLUEPRINT_ADVENTURE_LEVELS": ["import"],
}


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


def _literal_string_sequence(node: ast.AST) -> list[str] | None:
    if not isinstance(node, (ast.List, ast.Tuple)):
        return None
    values: list[str] = []
    for item in node.elts:
        if not (isinstance(item, ast.Constant) and isinstance(item.value, str)):
            return None
        values.append(item.value)
    return values


def _literal_dict_keys(node: ast.AST) -> list[str] | None:
    if not isinstance(node, ast.Dict):
        return None
    keys: list[str] = []
    for key in node.keys:
        if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
            return None
        keys.append(key.value)
    return keys


def _owner_statement_label(node: ast.stmt) -> str | None:
    if isinstance(node, ast.ImportFrom):
        return "blueprint-import"
    if isinstance(node, ast.FunctionDef):
        return f"function:{node.name}"
    if (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    ):
        return f"assignment:{node.targets[0].id}"
    if (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Subscript)
        and _root_name(node.targets[0]) == "ADVENTURE_SOURCES"
    ):
        return "adventure-source-override"
    if (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute)
        and _root_name(node.value.func.value) == "ADVENTURE_SOURCES"
        and node.value.func.attr == "update"
    ):
        return "adventure-source-update"
    return None


def _valid_advanced_owner(node: ast.AST) -> bool:
    """Require literal advanced plans whose only constructor is ``_waves``."""

    if not isinstance(node, ast.Dict):
        return False
    for plan in node.values:
        if not isinstance(plan, ast.List):
            return False
        for level in plan.elts:
            if not isinstance(level, ast.Dict) or len(level.keys) != 3:
                return False
            if _literal_dict_keys(level) != ["slug", "title", "waves"]:
                return False
            slug, title, waves = level.values
            if not (
                isinstance(slug, ast.Constant)
                and isinstance(slug.value, str)
                and isinstance(title, ast.Constant)
                and isinstance(title.value, str)
                and isinstance(waves, ast.Call)
                and _is_name(waves.func, "_waves")
                and not waves.keywords
                and all(
                    isinstance(argument, ast.Constant)
                    and isinstance(argument.value, str)
                    for argument in waves.args
                )
            ):
                return False
    return True


def _named_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    return matches[0] if len(matches) == 1 else None


def _is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def _valid_public_plan_composition(node: ast.AST) -> bool:
    if not (
        isinstance(node, ast.Call)
        and _is_name(node.func, "_merge_disjoint_adventure_wave_plans")
        and len(node.args) == 2
        and not node.keywords
    ):
        return False
    foundational, advanced = node.args
    return (
        isinstance(foundational, ast.Call)
        and _is_name(
            foundational.func,
            "_ordered_foundational_adventure_wave_plans",
        )
        and len(foundational.args) == 2
        and not foundational.keywords
        and _is_name(foundational.args[0], "BLUEPRINT_ADVENTURE_LEVELS")
        and _is_name(foundational.args[1], "_FOUNDATIONAL_ADVENTURE_ORDER")
        and _is_name(advanced, "_ADVANCED_DRILL_WAVE_PLANS")
    )


def _same_function_shape(actual: ast.FunctionDef, expected: ast.AST) -> bool:
    return ast.dump(actual, include_attributes=False) == ast.dump(
        expected,
        include_attributes=False,
    )


def _public_plan_mutations(tree: ast.Module) -> list[ast.AST]:
    mutations: list[ast.AST] = []
    canonical_assignment_seen = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if _root_name(target) != "ADVENTURE_WAVE_PLANS":
                    continue
                if isinstance(target, ast.Name) and not canonical_assignment_seen:
                    canonical_assignment_seen = True
                else:
                    mutations.append(node)
        elif isinstance(node, (ast.AugAssign, ast.Delete)):
            targets = [node.target] if isinstance(node, ast.AugAssign) else node.targets
            if any(_root_name(target) == "ADVENTURE_WAVE_PLANS" for target in targets):
                mutations.append(node)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and _root_name(node.func.value) == "ADVENTURE_WAVE_PLANS"
            and node.func.attr in MUTATING_METHODS
        ):
            mutations.append(node)
    return mutations


def _verify_critical_name_census(tree: ast.Module, errors: list[str]) -> None:
    for name, expected_contexts in EXPECTED_CRITICAL_NAME_CONTEXTS.items():
        actual_contexts = sorted(
            type(node.ctx).__name__
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and node.id == name
        )
        if actual_contexts != expected_contexts:
            errors.append(
                f"critical adventure composition symbol usage drifted: {name}"
            )
    bindings = _scope_bindings(tree.body)
    for name, expected_bindings in EXPECTED_CRITICAL_BINDINGS.items():
        if bindings.get(name, []) != expected_bindings:
            errors.append(
                f"critical adventure composition symbol binding drifted: {name}"
            )


def _verify_adventure_composition(path: Path, errors: list[str]) -> None:
    parsed = _parse(path, errors)
    if parsed is None:
        return
    _, tree = parsed

    expected_topology = (
        "blueprint-import",
        "function:_waves",
        "assignment:_FOUNDATIONAL_ADVENTURE_ORDER",
        "function:_ordered_foundational_adventure_wave_plans",
        "function:_merge_disjoint_adventure_wave_plans",
        "assignment:_ADVANCED_DRILL_WAVE_PLANS",
        "assignment:ADVENTURE_WAVE_PLANS",
        "assignment:ADVENTURE_SOURCES",
        "assignment:_V3_INCIDENT_CHAPTERS",
        "adventure-source-override",
        "adventure-source-update",
    )
    actual_topology = tuple(_owner_statement_label(node) for node in tree.body)
    if actual_topology != expected_topology:
        errors.append("adventure owner module top-level topology drifted")

    blueprint_imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "curriculum.seed_data.blueprint_overlay"
    ]
    if not (
        len(blueprint_imports) == 1
        and blueprint_imports[0].level == 0
        and len(blueprint_imports[0].names) == 1
        and blueprint_imports[0].names[0].name == "BLUEPRINT_ADVENTURE_LEVELS"
        and blueprint_imports[0].names[0].asname is None
    ):
        errors.append(
            "adventure owner must use the canonical one-name blueprint import"
        )

    waves_helper = _named_function(tree, "_waves")
    if waves_helper is None or not _same_function_shape(
        waves_helper,
        EXPECTED_WAVES_HELPER,
    ):
        errors.append("_waves must retain its exact literal plan-construction contract")

    order_assignment = _single_direct_assignment(
        tree,
        "_FOUNDATIONAL_ADVENTURE_ORDER",
    )
    actual_order = (
        _literal_string_sequence(order_assignment.value)
        if order_assignment is not None
        and isinstance(order_assignment.value, ast.Tuple)
        else None
    )
    if actual_order != list(FOUNDATIONAL_ADVENTURE_ORDER):
        errors.append(
            "foundational adventure public order must match the canonical sequence exactly"
        )
    elif len(actual_order) != len(set(actual_order)):
        errors.append("foundational adventure public order contains duplicate keys")

    advanced_assignment = _single_direct_assignment(
        tree,
        "_ADVANCED_DRILL_WAVE_PLANS",
    )
    advanced_keys = (
        _literal_dict_keys(advanced_assignment.value)
        if advanced_assignment is not None
        else None
    )
    if advanced_keys != list(ADVANCED_DRILL_ADVENTURES):
        errors.append(
            "advanced drill owner keys must match the canonical sequence exactly"
        )
    if advanced_assignment is None or not _valid_advanced_owner(
        advanced_assignment.value
    ):
        errors.append("advanced drill plans must use the canonical literal schema")
    if advanced_keys is not None and set(advanced_keys) & set(
        FOUNDATIONAL_ADVENTURE_ORDER
    ):
        errors.append("advanced drill owner must not contain foundational keys")

    public_assignment = _single_direct_assignment(tree, "ADVENTURE_WAVE_PLANS")
    if public_assignment is None or not _valid_public_plan_composition(
        public_assignment.value
    ):
        errors.append(
            "ADVENTURE_WAVE_PLANS must use the canonical ordered disjoint composition"
        )

    silent_mutations = _public_plan_mutations(tree)
    if silent_mutations:
        errors.append("ADVENTURE_WAVE_PLANS must not be mutated after composition")
    _verify_critical_name_census(tree, errors)

    projection = _named_function(
        tree,
        "_ordered_foundational_adventure_wave_plans",
    )
    if projection is None:
        errors.append("missing foundational adventure order projection helper")
    elif not _same_function_shape(projection, EXPECTED_FOUNDATIONAL_PROJECTION):
        errors.append(
            "foundational projection helper must implement the exact validated order contract"
        )

    merger = _named_function(tree, "_merge_disjoint_adventure_wave_plans")
    if merger is None:
        errors.append("missing disjoint adventure plan merge helper")
    elif not _same_function_shape(merger, EXPECTED_DISJOINT_MERGER):
        errors.append(
            "disjoint merge helper must implement the exact guard-before-merge contract"
        )


def _all_exports(tree: ast.Module) -> list[str] | None:
    assignments = _assignment_values(tree, "__all__")
    if len(assignments) != 1:
        return None
    return _literal_string_sequence(assignments[0])


def _verify_wrapper_exports(
    path: Path,
    expected: tuple[str, ...],
    errors: list[str],
) -> None:
    parsed = _parse(path, errors)
    if parsed is None:
        return
    _, tree = parsed
    actual = _all_exports(tree)
    if actual != list(expected):
        errors.append(f"{path.name} __all__ must be {list(expected)}")


def _legacy_symbol_references(path: Path, tree: ast.Module) -> list[str]:
    references: list[str] = []
    for node in ast.walk(tree):
        kind: str | None = None
        if isinstance(node, (ast.Import, ast.ImportFrom)) and any(
            alias.name == LEGACY_PLAN_SYMBOL
            or alias.name.endswith(f".{LEGACY_PLAN_SYMBOL}")
            or alias.asname == LEGACY_PLAN_SYMBOL
            for alias in node.names
        ):
            kind = "import"
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
            node.name == LEGACY_PLAN_SYMBOL
        ):
            kind = "function binding"
        elif isinstance(node, ast.ClassDef) and node.name == LEGACY_PLAN_SYMBOL:
            kind = "class binding"
        elif isinstance(node, ast.arg) and node.arg == LEGACY_PLAN_SYMBOL:
            kind = "argument binding"
        elif isinstance(node, ast.ExceptHandler) and node.name == LEGACY_PLAN_SYMBOL:
            kind = "exception binding"
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and (
            node.name == LEGACY_PLAN_SYMBOL
        ):
            kind = "match binding"
        elif isinstance(node, ast.MatchMapping) and node.rest == LEGACY_PLAN_SYMBOL:
            kind = "match binding"
        elif type(node).__name__ in {"ParamSpec", "TypeVar", "TypeVarTuple"} and (
            getattr(node, "name", None) == LEGACY_PLAN_SYMBOL
        ):
            kind = "type-parameter binding"
        elif isinstance(node, ast.Name) and node.id == LEGACY_PLAN_SYMBOL:
            kind = "binding" if isinstance(node.ctx, ast.Store) else "name access"
        elif isinstance(node, ast.Attribute) and node.attr == LEGACY_PLAN_SYMBOL:
            kind = "attribute access"
        if kind is not None:
            references.append(f"{path.name}:{getattr(node, 'lineno', 0)} {kind}")
    exports = _all_exports(tree)
    if exports is not None and LEGACY_PLAN_SYMBOL in exports:
        references.append(f"{path.name} legacy __all__ export")
    return references


def _repository_python_paths(root: Path) -> tuple[Path, ...]:
    """Return project Python sources while pruning generated environment trees."""

    ignored_parts = {".git", ".mypy_cache", ".pytest_cache", ".venv", "__pycache__"}
    paths: list[Path] = []
    for scan_root in (root / "backend", root / "scripts"):
        if not scan_root.is_dir():
            continue
        paths.extend(
            path
            for path in scan_root.rglob("*.py")
            if ignored_parts.isdisjoint(path.relative_to(root).parts)
        )
    return tuple(sorted(paths))


def _verify_legacy_symbol_census(root: Path, errors: list[str]) -> None:
    excluded = {
        (root / "scripts/checks/adventure_plan_ownership.py").resolve(),
        (root / "scripts/checks/check_curriculum_source_layout.py").resolve(),
        (root / "backend/curriculum/tests/test_adventure_plan_ownership.py").resolve(),
    }
    references: list[str] = []
    for path in _repository_python_paths(root):
        if path.resolve() in excluded:
            continue
        source = path.read_text(encoding="utf-8")
        normalized_source = unicodedata.normalize("NFKC", source)
        if LEGACY_PLAN_SYMBOL not in normalized_source:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"{path.name}: invalid Python: {exc.msg} (line {exc.lineno})")
            continue
        references.extend(_legacy_symbol_references(path, tree))
    if references:
        errors.append(f"legacy adventure plan references remain: {references}")


def _normalized_token_paths(
    root: Path,
    token: str,
    *,
    excluded: set[Path],
) -> set[Path]:
    paths: set[Path] = set()
    for path in _repository_python_paths(root):
        if path.resolve() in excluded:
            continue
        source = path.read_text(encoding="utf-8")
        if token in unicodedata.normalize("NFKC", source):
            paths.add(path.resolve())
    return paths


def _owner_usage_hashes(tree: ast.Module, symbol: str) -> tuple[str, ...]:
    """Fingerprint each executable/import/export statement that names an owner."""

    parents = {
        id(child): parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    statements: dict[int, ast.stmt] = {}
    for node in ast.walk(tree):
        matches = (
            isinstance(node, ast.Name)
            and node.id == symbol
            or isinstance(node, ast.Attribute)
            and node.attr == symbol
            or isinstance(node, ast.alias)
            and (node.name == symbol or node.asname == symbol)
            or isinstance(node, ast.Constant)
            and node.value == symbol
            or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.name == symbol
            or isinstance(node, ast.arg)
            and node.arg == symbol
        )
        if not matches:
            continue
        statement: ast.AST | None = node
        while statement is not None and not isinstance(statement, ast.stmt):
            statement = parents.get(id(statement))
        if isinstance(statement, ast.stmt):
            statements[id(statement)] = statement
    return tuple(
        sorted(
            hashlib.sha256(ast.dump(statement, include_attributes=False).encode())
            .hexdigest()
            .upper()
            for statement in statements.values()
        )
    )


def _verify_approved_blueprint_reader_bindings(
    relative_path: str,
    tree: ast.Module,
    errors: list[str],
) -> None:
    if (
        relative_path
        != "backend/curriculum/management/commands/seed_curriculum_structure.py"
    ):
        return
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "set"
        and any(
            isinstance(argument, ast.Name)
            and argument.id == "BLUEPRINT_ADVENTURE_LEVELS"
            for argument in node.args
        )
    ]
    parents = {
        id(child): parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    scope: ast.AST | None = calls[0] if len(calls) == 1 else None
    while scope is not None and not isinstance(
        scope,
        (ast.FunctionDef, ast.AsyncFunctionDef),
    ):
        scope = parents.get(id(scope))
    local_bindings = (
        _scope_bindings(scope.body).get("set", [])
        if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef))
        else ["missing-scope"]
    )
    module_bindings = _scope_bindings(tree.body).get("set", [])
    if len(calls) != 1 or local_bindings or module_bindings:
        errors.append("blueprint set reader must resolve to the unshadowed builtin")


def _all_scope_binding_kinds(tree: ast.Module) -> dict[str, list[str]]:
    binding_kinds: dict[str, list[str]] = {}
    scopes = [tree.body]
    scopes.extend(
        node.body
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    for scope in scopes:
        for name, kinds in _scope_bindings(scope).items():
            binding_kinds.setdefault(name, []).extend(kinds)
    for node in ast.walk(tree):
        if isinstance(node, ast.arg):
            binding_kinds.setdefault(node.arg, []).append("argument")
        elif type(node).__name__ in {"ParamSpec", "TypeVar", "TypeVarTuple"}:
            name = getattr(node, "name", None)
            if name:
                binding_kinds.setdefault(name, []).append("type-parameter")
    return binding_kinds


def _canonical_import_binding(
    tree: ast.Module,
    *,
    module: str,
    name: str,
) -> bool:
    imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.level == 0
        and node.module == module
        and any(item.name == name and item.asname is None for item in node.names)
    ]
    return len(imports) == 1 and _scope_bindings(tree.body).get(name) == ["import"]


def _canonical_module_import_binding(tree: ast.Module, name: str) -> bool:
    imports = [
        item
        for node in tree.body
        if isinstance(node, ast.Import)
        for item in node.names
        if item.name == name
    ]
    return (
        len(imports) == 1
        and imports[0].asname is None
        and _scope_bindings(tree.body).get(name) == ["import"]
    )


def _module_attribute_calls_are_canonical(
    tree: ast.Module,
    module: str,
    attribute: str,
) -> bool:
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    uses = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id == module
    ]
    return bool(uses) and all(
        isinstance((member := parents.get(node)), ast.Attribute)
        and member.value is node
        and member.attr == attribute
        and isinstance((call := parents.get(member)), ast.Call)
        and call.func is member
        for node in uses
    )


def _callable_names_are_only_called(tree: ast.Module, names: set[str]) -> bool:
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    return all(
        isinstance((call := parents.get(node)), ast.Call) and call.func is node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in names
    )


def _attribute_is_assigned(tree: ast.Module, root: str, attribute: str) -> bool:
    return any(
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == root
        and target.attr == attribute
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete))
        for target in (
            node.targets
            if isinstance(node, (ast.Assign, ast.Delete))
            else [node.target]
        )
    )


def _callable_parameter_contracts(
    tree: ast.Module,
    contracts: dict[str, tuple[str, ...]],
) -> dict[str, tuple[tuple[str, ...], frozenset[str]]] | None:
    binding_kinds = _all_scope_binding_kinds(tree)
    if not _callable_names_are_only_called(tree, set(contracts)):
        return None
    resolved: dict[str, tuple[tuple[str, ...], frozenset[str]]] = {}
    for function_name, protected_parameters in contracts.items():
        function = _named_function(tree, function_name)
        if (
            function is None
            or function.decorator_list
            or binding_kinds.get(function_name) != ["function"]
        ):
            return None
        actual_parameters = {item.arg for item in _function_parameters(function)}
        if any(name not in actual_parameters for name in protected_parameters):
            return None
        positional_parameters = tuple(
            item.arg for item in [*function.args.posonlyargs, *function.args.args]
        )
        resolved[function_name] = (
            positional_parameters,
            frozenset(protected_parameters),
        )
    return resolved


def _mapping_owner_is_read_only(
    tree: ast.Module,
    name: str,
    *,
    allow_definition: bool,
) -> bool:
    binding_kinds = _all_scope_binding_kinds(tree)
    safe_callables = frozenset(
        item for item in READ_ONLY_PARAMETER_CALLABLES if item not in binding_kinds
    )
    return not _mutable_owner_mutations(
        tree,
        name,
        allow_definition=allow_definition,
        rich_expressions=True,
        reject_unknown_owner_calls=True,
        safe_callables=safe_callables,
    )


def _read_only_helper_definition(
    tree: ast.Module,
    name: str,
    *,
    safe_method_receivers: frozenset[str] = frozenset(),
    safe_callable_contracts: dict[
        str,
        tuple[tuple[str, ...], frozenset[str]],
    ]
    | None = None,
) -> bool:
    function = _named_function(tree, name)
    if (
        function is None
        or function.decorator_list
        or _scope_bindings(tree.body).get(name) != ["function"]
    ):
        return False
    binding_kinds = _all_scope_binding_kinds(tree)
    safe_callables = frozenset(
        item for item in READ_ONLY_PARAMETER_CALLABLES if item not in binding_kinds
    )
    analyzer = _MutableOwnerAnalyzer(function)
    return not any(
        analyzer.mutations(
            parameter.arg,
            rich_expressions=True,
            reject_unknown_owner_calls=True,
            safe_callables=safe_callables,
            safe_callable_contracts=safe_callable_contracts,
            safe_method_receivers=safe_method_receivers,
        )
        for parameter in _function_parameters(function)
    )


def _selected_helper_parameters_are_read_only(
    tree: ast.Module,
    contracts: dict[str, tuple[str, ...]],
    *,
    external_callable_contracts: dict[
        str,
        tuple[tuple[str, ...], frozenset[str]],
    ]
    | None = None,
    safe_sink_parameters: dict[str, frozenset[str]] | None = None,
    safe_deepcopy: bool = False,
    safe_method_receivers: frozenset[str] = frozenset(),
) -> bool:
    local_callable_contracts = _callable_parameter_contracts(tree, contracts)
    if local_callable_contracts is None:
        return False
    external_callable_contracts = external_callable_contracts or {}
    binding_kinds = _all_scope_binding_kinds(tree)
    if any(
        binding_kinds.get(name) != ["import"] for name in external_callable_contracts
    ) or not _callable_names_are_only_called(tree, set(external_callable_contracts)):
        return False
    safe_callable_contracts = {
        **external_callable_contracts,
        **local_callable_contracts,
    }
    safe_callables = frozenset(
        item for item in READ_ONLY_PARAMETER_CALLABLES if item not in binding_kinds
    )
    safe_sink_parameters = safe_sink_parameters or {}
    for function_name, parameter_names in contracts.items():
        function = _named_function(tree, function_name)
        assert function is not None
        actual_parameters = {item.arg for item in _function_parameters(function)}
        declared_sinks = safe_sink_parameters.get(function_name, frozenset())
        if not declared_sinks <= actual_parameters or declared_sinks & set(
            parameter_names
        ):
            return False
        analyzer = _MutableOwnerAnalyzer(function)
        if any(
            analyzer.mutations(
                parameter_name,
                rich_expressions=True,
                reject_unknown_owner_calls=True,
                safe_callables=safe_callables,
                safe_callable_contracts=safe_callable_contracts,
                additional_safe_sink_names=declared_sinks,
                safe_deepcopy=safe_deepcopy,
                safe_method_receivers=safe_method_receivers,
            )
            for parameter_name in parameter_names
        ):
            return False
    return True


def _add_detail_uses_fresh_sinks(tree: ast.Module) -> bool:
    function = _named_function(tree, "_variant_with_context")
    if function is None:
        return False
    function_bindings = _scope_bindings(function.body)
    if function_bindings.get("set") or any(
        function_bindings.get(name) != ["store"] for name in ("merged_details", "seen")
    ):
        return False
    calls = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call) and _is_name(node.func, "_add_detail")
    ]
    expected_call = ast.parse("_add_detail(merged_details, seen, detail)").body[0]
    if not (
        len(calls) == 1
        and isinstance(expected_call, ast.Expr)
        and ast.dump(calls[0], include_attributes=False)
        == ast.dump(expected_call.value, include_attributes=False)
    ):
        return False

    assignments = {
        name: [
            node
            for node in ast.walk(function)
            if isinstance(node, (ast.Assign, ast.AnnAssign))
            and any(
                isinstance(target, ast.Name) and target.id == name
                for target in (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
            )
        ]
        for name in ("merged_details", "seen")
    }
    if any(len(nodes) != 1 for nodes in assignments.values()):
        return False
    merged_value = assignments["merged_details"][0].value
    seen_value = assignments["seen"][0].value
    return (
        isinstance(merged_value, ast.List)
        and not merged_value.elts
        and isinstance(seen_value, ast.Call)
        and _is_name(seen_value.func, "set")
        and not seen_value.args
        and not seen_value.keywords
    )


def _trusted_blueprint_generator_callables(
    root: Path,
    tree: ast.Module,
    errors: list[str],
) -> frozenset[str]:
    wildcard_imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and any(item.name == "*" for item in node.names)
    ]
    if not (
        len(wildcard_imports) == 1
        and wildcard_imports[0].level == 1
        and wildcard_imports[0].module == "common"
        and [(item.name, item.asname) for item in wildcard_imports[0].names]
        == [("*", None)]
    ):
        return frozenset()

    common_parsed = _parse(
        root / "backend/curriculum/seed_data/source/adventure_level_specs/common.py",
        errors,
    )
    command_routing_parsed = _parse(
        root / "backend/curriculum/seed_data/source/command_routing.py",
        errors,
    )
    spec_helpers_parsed = _parse(
        root / "backend/curriculum/seed_data/spec_helpers.py",
        errors,
    )
    if (
        common_parsed is None
        or command_routing_parsed is None
        or spec_helpers_parsed is None
    ):
        return frozenset()
    _, common_tree = common_parsed
    _, command_routing_tree = command_routing_parsed
    _, spec_helpers_tree = spec_helpers_parsed
    common_all = _single_direct_assignment(common_tree, "__all__")
    if common_all is None or ast.dump(
        common_all,
        include_attributes=False,
    ) != ast.dump(EXPECTED_COMMON_ALL_ASSIGNMENT, include_attributes=False):
        return frozenset()

    trusted: set[str] = set()
    generator_bindings = _scope_bindings(tree.body)
    target_import_is_canonical = _canonical_import_binding(
        common_tree,
        module="curriculum.seed_data.generated.generated_targets",
        name="TARGET_STATES",
    ) and _mapping_owner_is_read_only(
        common_tree,
        "TARGET_STATES",
        allow_definition=False,
    )
    if (
        "v" not in generator_bindings
        and _callable_names_are_only_called(common_tree, {"v"})
        and target_import_is_canonical
        and _read_only_helper_definition(
            common_tree,
            "v",
            safe_method_receivers=frozenset({"TARGET_STATES"}),
        )
    ):
        trusted.add("v")
    if (
        "ev" not in generator_bindings
        and _callable_names_are_only_called(spec_helpers_tree, {"ev"})
        and _canonical_import_binding(
            common_tree,
            module="curriculum.seed_data.spec_helpers",
            name="ev",
        )
        and _read_only_helper_definition(spec_helpers_tree, "ev")
    ):
        trusted.add("ev")
    q_dependencies = {
        "_add_detail": ("entry",),
        "_adventure_for_usage": ("usage",),
        "_command_from_usage": ("usage",),
        "_modular_checks": ("checks",),
        "_normalize_detail": ("entry",),
        "_task_with_notes": ("task", "task_notes"),
        "_text": ("value",),
        "_variant_safe_checks": ("usage", "checks"),
        "_variant_with_context": (
            "variant",
            "story",
            "task",
            "details",
            "task_notes",
        ),
    }
    spec_helper_contract = {
        "_as_text_list": ("value",),
        "_commit_messages_from_command": ("command",),
        "_evaluation_message_fragments": ("value",),
        "enrich_context_with_required_details": (
            "context",
            "solution_commands",
            "evaluation_spec",
        ),
        "required_commit_message_details": (
            "solution_commands",
            "evaluation_spec",
        ),
    }
    command_routing_contract = {"adventure_for_usage": ("usage",)}
    command_routing_callables = _callable_parameter_contracts(
        command_routing_tree,
        command_routing_contract,
    )
    spec_helper_callables = _callable_parameter_contracts(
        spec_helpers_tree,
        spec_helper_contract,
    )
    q_dependency_callables = _callable_parameter_contracts(common_tree, q_dependencies)

    command_mapping_receivers = frozenset(
        name
        for name in {"ADVENTURE_BY_COMMAND", "ADVENTURE_BY_USAGE"}
        if _all_scope_binding_kinds(command_routing_tree).get(name) == ["store"]
        and (assignment := _single_direct_assignment(command_routing_tree, name))
        is not None
        and _literal_immutable_value(assignment.value)
        and _mapping_owner_is_read_only(
            command_routing_tree,
            name,
            allow_definition=True,
        )
    )
    command_routing_is_read_only = (
        command_routing_callables is not None
        and command_mapping_receivers
        == frozenset({"ADVENTURE_BY_COMMAND", "ADVENTURE_BY_USAGE"})
        and _selected_helper_parameters_are_read_only(
            command_routing_tree,
            command_routing_contract,
            safe_method_receivers=command_mapping_receivers,
        )
    )
    spec_copy_is_safe = (
        _canonical_module_import_binding(spec_helpers_tree, "copy")
        and _module_attribute_calls_are_canonical(
            spec_helpers_tree,
            "copy",
            "deepcopy",
        )
        and not _attribute_is_assigned(spec_helpers_tree, "copy", "deepcopy")
    )
    spec_shlex_is_safe = (
        _canonical_module_import_binding(spec_helpers_tree, "shlex")
        and _module_attribute_calls_are_canonical(
            spec_helpers_tree,
            "shlex",
            "split",
        )
        and not _attribute_is_assigned(spec_helpers_tree, "shlex", "split")
    )
    spec_helpers_are_read_only = (
        spec_helper_callables is not None
        and spec_copy_is_safe
        and spec_shlex_is_safe
        and _selected_helper_parameters_are_read_only(
            spec_helpers_tree,
            spec_helper_contract,
            safe_deepcopy=True,
            safe_method_receivers=frozenset({"shlex"}),
        )
    )
    common_copy_is_safe = (
        _canonical_module_import_binding(common_tree, "copy")
        and _module_attribute_calls_are_canonical(common_tree, "copy", "deepcopy")
        and not _attribute_is_assigned(common_tree, "copy", "deepcopy")
    )
    external_q_callables = (
        {
            **command_routing_callables,
            "enrich_context_with_required_details": spec_helper_callables[
                "enrich_context_with_required_details"
            ],
        }
        if command_routing_callables is not None and spec_helper_callables is not None
        else {}
    )
    q_dependencies_are_read_only = (
        q_dependency_callables is not None
        and command_routing_is_read_only
        and spec_helpers_are_read_only
        and common_copy_is_safe
        and _canonical_import_binding(
            common_tree,
            module="curriculum.seed_data.source.command_routing",
            name="adventure_for_usage",
        )
        and _add_detail_uses_fresh_sinks(common_tree)
        and _selected_helper_parameters_are_read_only(
            common_tree,
            q_dependencies,
            external_callable_contracts=external_q_callables,
            safe_sink_parameters={
                "_add_detail": frozenset({"details", "seen"}),
            },
            safe_deepcopy=True,
        )
    )
    if (
        "q" not in generator_bindings
        and _callable_names_are_only_called(common_tree, {"q"})
        and _canonical_import_binding(
            common_tree,
            module="curriculum.seed_data.spec_helpers",
            name="enrich_context_with_required_details",
        )
        and q_dependencies_are_read_only
        and _read_only_helper_definition(
            common_tree,
            "q",
            safe_callable_contracts={
                **external_q_callables,
                **q_dependency_callables,
            },
        )
    ):
        trusted.add("q")
    return frozenset(trusted)


def _verify_blueprint_generator_parameters_are_read_only(
    root: Path,
    relative_path: str,
    tree: ast.Module,
    errors: list[str],
) -> None:
    if (
        relative_path
        != "backend/curriculum/seed_data/source/adventure_level_specs/blueprint_generated.py"
    ):
        return
    function_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
    ]
    function_definitions = [
        node
        for node in function_nodes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    function_names = [node.name for node in function_definitions]
    binding_kinds = _all_scope_binding_kinds(tree)
    local_function_names = {
        node.name
        for node in function_definitions
        if function_names.count(node.name) == 1
        and not node.decorator_list
        and binding_kinds.get(node.name) == ["function"]
    }
    deepcopy_rebound = any(
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "copy"
        and target.attr == "deepcopy"
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete))
        for target in (
            node.targets
            if isinstance(node, (ast.Assign, ast.Delete))
            else [node.target]
        )
    )
    copy_imported_anywhere = any(
        item.name == "copy"
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for item in node.names
    )
    trusted_external_callables = {
        name
        for name in _trusted_blueprint_generator_callables(root, tree, errors)
        if name not in binding_kinds
    }
    if trusted_external_callables != {"ev", "q", "v"}:
        errors.append("blueprint generator helper parameters must be read-only")
        return
    safe_callables = frozenset(
        local_function_names
        | {name for name in READ_ONLY_PARAMETER_CALLABLES if name not in binding_kinds}
        | trusted_external_callables
    )
    safe_method_receivers = frozenset(
        name
        for name in {"_BLUEPRINT_ADVENTURE_COPY", "_BLUEPRINT_STATE_BRIEFS"}
        if binding_kinds.get(name) == ["store"]
        and (assignment := _single_direct_assignment(tree, name)) is not None
        and _literal_immutable_value(assignment.value)
        and _mapping_owner_is_read_only(
            tree,
            name,
            allow_definition=True,
        )
    )
    deepcopy_is_safe = (
        "copy" not in binding_kinds
        and not copy_imported_anywhere
        and not deepcopy_rebound
        and _module_attribute_calls_are_canonical(tree, "copy", "deepcopy")
    )
    for function in function_nodes:
        analyzer = _MutableOwnerAnalyzer(function)
        if any(
            analyzer.mutations(
                parameter.arg,
                rich_expressions=True,
                reject_unknown_owner_calls=True,
                safe_callables=safe_callables,
                provenance_callables=frozenset(
                    local_function_names | trusted_external_callables
                ),
                safe_deepcopy=deepcopy_is_safe,
                safe_method_receivers=safe_method_receivers,
            )
            for parameter in _function_parameters(function)
        ):
            errors.append("blueprint generator helper parameters must be read-only")
            return


def _verify_mutable_plan_owner_census(root: Path, errors: list[str]) -> None:
    excluded = {
        (root / "scripts/checks/adventure_plan_ownership.py").resolve(),
        (root / "scripts/checks/check_curriculum_source_layout.py").resolve(),
        (root / "backend/curriculum/tests/test_adventure_plan_ownership.py").resolve(),
    }
    adventures = (root / "backend/curriculum/seed_data/adventures.py").resolve()
    advanced_paths = _normalized_token_paths(
        root,
        "_ADVANCED_DRILL_WAVE_PLANS",
        excluded=excluded,
    )
    expected_advanced_paths = {adventures} if adventures.is_file() else set()
    if advanced_paths != expected_advanced_paths:
        errors.append("private advanced plan owner may appear only in adventures.py")

    blueprint_paths = _normalized_token_paths(
        root,
        "BLUEPRINT_ADVENTURE_LEVELS",
        excluded=excluded,
    )
    expected_blueprint_paths = {
        path.resolve()
        for relative_path in BLUEPRINT_PLAN_CONSUMERS
        if (path := root / relative_path).is_file()
    }
    if blueprint_paths != expected_blueprint_paths:
        errors.append(
            "blueprint adventure plan consumers must match the approved module set"
        )

    blueprint_owner = (
        root / "backend/curriculum/seed_data/source/blueprint/__init__.py"
    ).resolve()
    for path in sorted(blueprint_paths):
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"{path.name}: invalid Python: {exc.msg} (line {exc.lineno})")
            continue
        relative_path = path.relative_to(root.resolve()).as_posix()
        expected_hashes = BLUEPRINT_PLAN_USAGE_HASHES.get(relative_path)
        if expected_hashes is None:
            continue
        if _owner_usage_hashes(tree, "BLUEPRINT_ADVENTURE_LEVELS") != expected_hashes:
            errors.append(
                "BLUEPRINT_ADVENTURE_LEVELS approved use-site structure drifted"
            )
        _verify_approved_blueprint_reader_bindings(relative_path, tree, errors)
        _verify_blueprint_generator_parameters_are_read_only(
            root,
            relative_path,
            tree,
            errors,
        )
        if _mutable_owner_mutations(
            tree,
            "BLUEPRINT_ADVENTURE_LEVELS",
            allow_definition=path == blueprint_owner,
        ):
            errors.append("BLUEPRINT_ADVENTURE_LEVELS must not be mutated by consumers")
            break


def _resolved_import_module(root: Path, path: Path, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""
    try:
        relative_path = path.relative_to(root / "backend")
    except ValueError:
        return node.module or ""
    package = list(relative_path.parent.parts)
    trim = node.level - 1
    if trim > len(package):
        return ""
    if trim:
        package = package[:-trim]
    if node.module:
        package.extend(node.module.split("."))
    return ".".join(package)


def _verify_blueprint_owner_graph(root: Path, errors: list[str]) -> None:
    """Freeze owner module boundaries and forbid external implementation imports."""

    owner_dir = root / "backend/curriculum/seed_data/source/blueprint"
    if owner_dir.is_dir():
        expected_files = {
            "__init__.py",
            "challenge_specs.py",
            "helpers.py",
            *(f"{module}.py" for module in BLUEPRINT_ADVENTURE_MODULES),
            "repository_foundations/__init__.py",
            *(
                f"repository_foundations/{module}.py"
                for module in BLUEPRINT_REPOSITORY_FOUNDATION_MODULES
            ),
        }
        actual_files = {
            path.relative_to(owner_dir).as_posix() for path in owner_dir.rglob("*.py")
        }
        if actual_files != expected_files:
            errors.append(
                "blueprint owner module set drifted: "
                f"missing={sorted(expected_files - actual_files)}, "
                f"unexpected={sorted(actual_files - expected_files)}"
            )

    implementation_package = "curriculum.seed_data.source.blueprint"
    approved_overlay = (
        root / "backend/curriculum/seed_data/source/blueprint_overlay.py"
    ).resolve()
    excluded = {
        (root / "scripts/checks/adventure_plan_ownership.py").resolve(),
        (root / "scripts/checks/check_curriculum_source_layout.py").resolve(),
        (root / "backend/curriculum/tests/test_adventure_plan_ownership.py").resolve(),
    }
    illegal_imports: list[str] = []
    for path in _repository_python_paths(root):
        resolved = path.resolve()
        if resolved in excluded or resolved.is_relative_to(owner_dir.resolve()):
            continue
        source = path.read_text(encoding="utf-8")
        if "blueprint" not in unicodedata.normalize("NFKC", source):
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"{path.name}: invalid Python: {exc.msg} (line {exc.lineno})")
            continue
        for node in ast.walk(tree):
            illegal = False
            if isinstance(node, ast.Attribute) and node.attr in {
                "blueprint",
                "repository_foundations",
                *BLUEPRINT_ADVENTURE_MODULES,
                *(f"_{name}" for name in BLUEPRINT_ADVENTURE_MODULES),
            }:
                illegal = True
            elif isinstance(node, ast.Import):
                illegal = any(
                    item.name == implementation_package
                    or item.name.startswith(f"{implementation_package}.")
                    for item in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                module = _resolved_import_module(root, path, node)
                exact_public_overlay_import = (
                    resolved == approved_overlay
                    and module == implementation_package
                    and [(item.name, item.asname) for item in node.names]
                    == [
                        ("BLUEPRINT_ADVENTURE_LEVELS", None),
                        ("BLUEPRINT_CHALLENGE_SPECS", None),
                    ]
                )
                absolute_implementation_import = (
                    module == implementation_package
                    or module.startswith(f"{implementation_package}.")
                    or module == "curriculum.seed_data.source"
                    and any(item.name == "blueprint" for item in node.names)
                )
                illegal = (
                    absolute_implementation_import and not exact_public_overlay_import
                )
            if illegal:
                illegal_imports.append(
                    f"{path.relative_to(root).as_posix()}:{node.lineno}"
                )
    if illegal_imports:
        errors.append(
            "blueprint mutable implementation modules are owner-private: "
            f"{sorted(illegal_imports)}"
        )


def _verify_public_plan_consumer_census(root: Path, errors: list[str]) -> None:
    adventures_path = root / "backend/curriculum/seed_data/adventures.py"
    level_plan_path = (
        root / "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py"
    )
    excluded = {
        (root / "scripts/checks/adventure_plan_ownership.py").resolve(),
        (root / "scripts/checks/check_curriculum_source_layout.py").resolve(),
        (root / "backend/curriculum/tests/test_adventure_plan_ownership.py").resolve(),
    }
    token_paths: list[Path] = []
    for path in _repository_python_paths(root):
        if path.resolve() in excluded:
            continue
        source = path.read_text(encoding="utf-8")
        normalized_source = unicodedata.normalize("NFKC", source)
        if "ADVENTURE_WAVE_PLANS" in normalized_source:
            token_paths.append(path)
    if {path.resolve() for path in token_paths} != {
        adventures_path.resolve(),
        level_plan_path.resolve(),
    }:
        errors.append(
            "ADVENTURE_WAVE_PLANS may appear only in its owner and canonical reader"
        )
        return

    parsed = _parse(level_plan_path, errors)
    if parsed is None:
        return
    source, tree = parsed
    blueprint_imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "curriculum.seed_data.blueprint_overlay"
        and node.level == 0
        and [(item.name, item.asname) for item in node.names]
        == [("BLUEPRINT_ADVENTURE_LEVELS", None)]
    ]
    imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "curriculum.seed_data.adventures"
        and node.level == 0
        and len(node.names) == 1
        and node.names[0].name == "ADVENTURE_WAVE_PLANS"
        and node.names[0].asname is None
    ]
    plan_values = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(
            isinstance(target, ast.Name) and target.id == "plan" for target in targets
        ):
            plan_values.append(node.value)
    public_loads = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "ADVENTURE_WAVE_PLANS"
        and isinstance(node.ctx, ast.Load)
    ]
    exact_read = len(plan_values) == 1 and ast.dump(
        plan_values[0], include_attributes=False
    ) == ast.dump(EXPECTED_PUBLIC_PLAN_READ, include_attributes=False)
    reader = _named_function(tree, "adventure_levels_for")
    level_helper = _named_function(tree, "_level")
    wave_plan_reader = _named_function(tree, "_wave_plan_levels")
    module_bindings = _scope_bindings(tree.body)
    reader_helper_contract = {
        "_level": ("slug", "title", "waves", "reuse"),
        "_wave_plan_levels": ("plan",),
    }
    reader_helper_callables = _callable_parameter_contracts(
        tree,
        reader_helper_contract,
    )
    reader_helpers_are_read_only = (
        reader_helper_callables is not None
        and _selected_helper_parameters_are_read_only(
            tree,
            reader_helper_contract,
        )
    )
    reader_binding_kinds = _all_scope_binding_kinds(tree)
    reader_safe_callables = frozenset(
        item
        for item in READ_ONLY_PARAMETER_CALLABLES
        if item not in reader_binding_kinds
    )
    blueprint_contexts = sorted(
        type(node.ctx).__name__
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "BLUEPRINT_ADVENTURE_LEVELS"
    )
    reader_mutations = (
        _mutable_owner_mutations(
            reader,
            "plan",
            allow_definition=True,
            rich_expressions=True,
            reject_unknown_owner_calls=True,
            safe_callables=reader_safe_callables,
            safe_callable_contracts=reader_helper_callables,
        )
        if reader is not None and reader_helpers_are_read_only
        else [tree]
    )
    wave_plan_mutations = (
        _mutable_owner_mutations(
            wave_plan_reader,
            "plan",
            rich_expressions=True,
            reject_unknown_owner_calls=True,
            safe_callables=reader_safe_callables,
            safe_callable_contracts=reader_helper_callables,
        )
        if wave_plan_reader is not None and reader_helpers_are_read_only
        else [tree]
    )
    shadowed_reader_builtins = {
        name
        for name in ("isinstance", "list", "str")
        if module_bindings.get(name)
        or (
            wave_plan_reader is not None
            and _scope_bindings(wave_plan_reader.body).get(name)
        )
    }
    if not (
        len(blueprint_imports) == 1
        and len(imports) == 1
        and len(public_loads) == 1
        and source.count("ADVENTURE_WAVE_PLANS") == 2
        and exact_read
        and reader is not None
        and level_helper is not None
        and wave_plan_reader is not None
        and not reader_mutations
        and not wave_plan_mutations
        and not shadowed_reader_builtins
        and blueprint_contexts == ["Load"]
        and module_bindings.get("BLUEPRINT_ADVENTURE_LEVELS") == ["import"]
        and module_bindings.get("adventure_levels_for") == ["function"]
        and module_bindings.get("_level") == ["function"]
        and module_bindings.get("_wave_plan_levels") == ["function"]
    ):
        errors.append("canonical ADVENTURE_WAVE_PLANS reader contract drifted")


def adventure_plan_ownership_errors(*, root: Path = ROOT) -> list[str]:
    """Return deterministic violations for adventure plan truth ownership."""

    errors: list[str] = []
    seed_data = root / "backend/curriculum/seed_data"
    source = seed_data / "source"
    _verify_adventure_composition(seed_data / "adventures.py", errors)

    supported_exports = (
        "ADVENTURE_LEVELS",
        "SPEC_BY_SLUG",
        "adventure_levels_for",
    )
    _verify_wrapper_exports(
        seed_data / "adventure_levels.py", supported_exports, errors
    )
    _verify_wrapper_exports(source / "adventure_levels.py", supported_exports, errors)
    _verify_wrapper_exports(
        source / "adventure_level_specs/__init__.py",
        supported_exports,
        errors,
    )
    _verify_wrapper_exports(
        source / "adventure_level_specs/level_plan.py",
        ("adventure_levels_for",),
        errors,
    )

    source_package = source / "__init__.py"
    parsed_package = _parse(source_package, errors)
    if parsed_package is not None:
        _, tree = parsed_package
        package_docstring = ast.get_docstring(tree, clean=False)
        if package_docstring != "Canonical human-authored curriculum source packages.":
            errors.append("source package docstring must name canonical ownership")

    guide_path = root / "CONTENT_AUTHORING_GUIDE.md"
    if not guide_path.is_file():
        errors.append("missing content authoring guide")
    else:
        guide = guide_path.read_text(encoding="utf-8")
        forbidden_guide_text = (
            LEGACY_PLAN_SYMBOL,
            "monolithic files still drive seeding",
        )
        if any(text in guide for text in forbidden_guide_text):
            errors.append("content authoring guide still recommends a retired owner")
        required_guide_text = (
            "source/adventure_level_specs/",
            "source/blueprint/",
            "private owner map",
            "ADVENTURE_WAVE_PLANS",
        )
        if any(text not in guide for text in required_guide_text):
            errors.append(
                "content authoring guide does not identify every current owner"
            )

    legacy_package = source / "ch1"
    if legacy_package.exists():
        errors.append("legacy Chapter 1 scaffold path remains")

    _verify_legacy_symbol_census(root, errors)
    _verify_blueprint_owner_graph(root, errors)
    _verify_mutable_plan_owner_census(root, errors)
    _verify_public_plan_consumer_census(root, errors)
    return errors
