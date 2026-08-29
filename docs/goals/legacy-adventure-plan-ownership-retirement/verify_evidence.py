#!/usr/bin/env python3
"""Capture and replay Slice 17 ownership, runtime, and preservation evidence."""

from __future__ import annotations

import argparse
import ast
import base64
import binascii
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
GOAL_DIR = Path(__file__).resolve().parent
BASELINE = GOAL_DIR / "PRE_SLICE_BASELINE.json"
PLAN_MANIFEST = GOAL_DIR / "PRE_CUTOVER_PLAN_MANIFEST.json"
FINAL_RESULTS = GOAL_DIR / "FINAL_COMMAND_RESULTS.json"

BASELINE_SHA256 = "1F3FB3EAF5E61B2F4F244830148DD8288E30CDC528CF4BD1CF35D7605CFB7FA9"
PLAN_MANIFEST_SHA256 = (
    "A73888EADE78980DFAA6E51AA3B366C1799A163691ADB1C961BADA7A2AF3C71C"
)

ADVENTURES = ROOT / "backend/curriculum/seed_data/adventures.py"
GENERATED_TARGETS = ROOT / "backend/curriculum/seed_data/generated/generated_targets.py"
POLICY_CHECKER = ROOT / "scripts/checks/check_curriculum_source_layout.py"
POLICY_MODULE = ROOT / "scripts/checks/adventure_plan_ownership.py"
POLICY_TEST = ROOT / "backend/curriculum/tests/test_adventure_plan_ownership.py"
LEGACY_CHAPTER_PACKAGE = ROOT / "backend/curriculum/seed_data/source/ch1"

FOUNDATIONAL_ORDER = (
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

MODIFIED_EXISTING = (
    "CONTENT_AUTHORING_GUIDE.md",
    "backend/curriculum/seed_data/adventures.py",
    "backend/curriculum/seed_data/adventure_levels.py",
    "backend/curriculum/seed_data/source/__init__.py",
    "backend/curriculum/seed_data/source/adventure_levels.py",
    "backend/curriculum/seed_data/source/adventure_level_specs/__init__.py",
    "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py",
    "backend/curriculum/management/commands/seed_curriculum_writer.py",
    "scripts/checks/check_curriculum_source_layout.py",
)
DELETED_PATHS = (
    "backend/curriculum/seed_data/source/ch1/README.md",
    "backend/curriculum/seed_data/source/ch1/__init__.py",
)
NEW_IMPLEMENTATION = (
    "backend/curriculum/tests/test_adventure_plan_ownership.py",
    "scripts/checks/adventure_plan_ownership.py",
    "scripts/checks/mutable_owner_analysis.py",
)
GOAL_ARTIFACTS = (
    "docs/goals/legacy-adventure-plan-ownership-retirement/GOAL.md",
    "docs/goals/legacy-adventure-plan-ownership-retirement/PLAN.md",
    "docs/goals/legacy-adventure-plan-ownership-retirement/PRE_SLICE_BASELINE.json",
    "docs/goals/legacy-adventure-plan-ownership-retirement/PRE_CUTOVER_PLAN_MANIFEST.json",
    "docs/goals/legacy-adventure-plan-ownership-retirement/FINAL_COMMAND_RESULTS.json",
    "docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py",
    "docs/goals/legacy-adventure-plan-ownership-retirement/EVIDENCE.md",
)
APPROVED_VISIBLE = {
    *MODIFIED_EXISTING,
    *DELETED_PATHS,
    *NEW_IMPLEMENTATION,
    *GOAL_ARTIFACTS,
}

STABLE_PLAN_FILES = (
    "docs/goals/legacy-adventure-plan-ownership-retirement/GOAL.md",
    "docs/goals/legacy-adventure-plan-ownership-retirement/PLAN.md",
)

BASELINE_COMMANDS = (
    (
        "layout",
        [sys.executable, "scripts/checks/check_curriculum_source_layout.py"],
    ),
    (
        "seed_targets",
        [sys.executable, "scripts/checks/check_seed_targets.py"],
    ),
    (
        "generated_targets",
        [sys.executable, "scripts/checks/check_generated_targets_current.py"],
    ),
)

FOCUSED_TEST_COMMAND = (
    "python -m pytest -q "
    "backend/curriculum/tests/test_adventure_plan_ownership.py "
    "backend/curriculum/tests/test_repository_foundations_source_layout.py"
)
FOCUSED_SEED_COMMAND = (
    "python -m pytest -q "
    "backend/curriculum/tests/test_seed_source_command_routing.py "
    "backend/curriculum/tests/test_blueprint_pedagogy_invariants.py "
    "backend/curriculum/tests/test_chapter_content_invariants.py "
    "backend/curriculum/tests/test_seed_curriculum_idempotency.py"
)
FULL_TEST_COMMAND = "python -m pytest -q backend/curriculum/tests"
LAYOUT_COMMAND = "python scripts/checks/check_curriculum_source_layout.py"
SEED_TARGET_COMMAND = "python scripts/checks/check_seed_targets.py"
GENERATED_TARGET_COMMAND = "python scripts/checks/check_generated_targets_current.py"
FAST_GATE_COMMAND = "python scripts/checks/check_quality_gates.py"
LEGACY_VERIFY_COMMAND = (
    "python docs/goals/legacy-adventure-plan-ownership-retirement/"
    "verify_evidence.py --phase legacy"
)
LEGACY_TEXT_COMMAND = (
    'rg -n "ADVENTURE_LEVEL_PLAN|monolithic files still drive seeding" '
    'CONTENT_AUTHORING_GUIDE.md backend/curriculum --glob "*.py" '
    '--glob "*.md" --glob "!**/test_adventure_plan_ownership.py"'
)
RUFF_COMMAND = (
    "python -m ruff check "
    "backend/curriculum/seed_data/adventures.py "
    "backend/curriculum/seed_data/adventure_levels.py "
    "backend/curriculum/seed_data/source/__init__.py "
    "backend/curriculum/seed_data/source/adventure_levels.py "
    "backend/curriculum/seed_data/source/adventure_level_specs/__init__.py "
    "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py "
    "backend/curriculum/management/commands/seed_curriculum_writer.py "
    "scripts/checks/adventure_plan_ownership.py "
    "scripts/checks/mutable_owner_analysis.py "
    "scripts/checks/check_curriculum_source_layout.py "
    "backend/curriculum/tests/test_adventure_plan_ownership.py "
    "docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py"
)
DIFF_CHECK_COMMAND = "git diff --check"

FINAL_COMMAND_SPECS = (
    (
        "canonical_verifier",
        "python docs/goals/legacy-adventure-plan-ownership-retirement/"
        "verify_evidence.py --phase final",
        [
            sys.executable,
            "docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py",
            "--phase",
            "final",
        ],
        0,
    ),
    (
        "focused_ownership",
        FOCUSED_TEST_COMMAND,
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "backend/curriculum/tests/test_adventure_plan_ownership.py",
            "backend/curriculum/tests/test_repository_foundations_source_layout.py",
        ],
        0,
    ),
    (
        "focused_seed_data",
        FOCUSED_SEED_COMMAND,
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "backend/curriculum/tests/test_seed_source_command_routing.py",
            "backend/curriculum/tests/test_blueprint_pedagogy_invariants.py",
            "backend/curriculum/tests/test_chapter_content_invariants.py",
            "backend/curriculum/tests/test_seed_curriculum_idempotency.py",
        ],
        0,
    ),
    (
        "full_curriculum",
        FULL_TEST_COMMAND,
        [sys.executable, "-m", "pytest", "-q", "backend/curriculum/tests"],
        0,
    ),
    (
        "layout",
        LAYOUT_COMMAND,
        [sys.executable, "scripts/checks/check_curriculum_source_layout.py"],
        0,
    ),
    (
        "seed_targets",
        SEED_TARGET_COMMAND,
        [sys.executable, "scripts/checks/check_seed_targets.py"],
        0,
    ),
    (
        "generated_targets",
        GENERATED_TARGET_COMMAND,
        [sys.executable, "scripts/checks/check_generated_targets_current.py"],
        0,
    ),
    (
        "fast_gate",
        FAST_GATE_COMMAND,
        [sys.executable, "scripts/checks/check_quality_gates.py"],
        0,
    ),
    (
        "semantic_legacy_census",
        LEGACY_VERIFY_COMMAND,
        [
            sys.executable,
            "docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py",
            "--phase",
            "legacy",
        ],
        0,
    ),
    (
        "supporting_text_census",
        LEGACY_TEXT_COMMAND,
        [
            "rg",
            "-n",
            "ADVENTURE_LEVEL_PLAN|monolithic files still drive seeding",
            "CONTENT_AUTHORING_GUIDE.md",
            "backend/curriculum",
            "--glob",
            "*.py",
            "--glob",
            "*.md",
            "--glob",
            "!**/test_adventure_plan_ownership.py",
        ],
        1,
    ),
    (
        "ruff",
        RUFF_COMMAND,
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "backend/curriculum/seed_data/adventures.py",
            "backend/curriculum/seed_data/adventure_levels.py",
            "backend/curriculum/seed_data/source/__init__.py",
            "backend/curriculum/seed_data/source/adventure_levels.py",
            "backend/curriculum/seed_data/source/adventure_level_specs/__init__.py",
            "backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py",
            "backend/curriculum/management/commands/seed_curriculum_writer.py",
            "scripts/checks/adventure_plan_ownership.py",
            "scripts/checks/mutable_owner_analysis.py",
            "scripts/checks/check_curriculum_source_layout.py",
            "backend/curriculum/tests/test_adventure_plan_ownership.py",
            "docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py",
        ],
        0,
    ),
    (
        "diff_check",
        DIFF_CHECK_COMMAND,
        ["git", "diff", "--check"],
        0,
    ),
)

FINAL_OUTPUT_TOKENS = {
    "canonical_verifier": ("Slice 17 evidence verified (final).",),
    "focused_ownership": ("230 passed",),
    "focused_seed_data": ("19 passed",),
    "full_curriculum": ("1745 passed",),
    "layout": ("Curriculum source layout is consistent.",),
    "seed_targets": ("consistent (2056 cases)",),
    "generated_targets": (
        "Collected 2056 variant solutions.",
        "generated/generated_targets.py is up to date.",
    ),
    "fast_gate": ("All fast quality gates passed.",),
    "semantic_legacy_census": ("Slice 17 evidence verified (legacy).",),
    "supporting_text_census": (),
    "ruff": ("All checks passed!",),
    "diff_check": (),
}
FINAL_STDERR_TOKENS = {
    "diff_check": (
        "backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py",
        "frontend/src/shared/api/generated/apiTypes.ts",
    ),
}

FINAL_BINDING_PATHS = (
    *MODIFIED_EXISTING,
    *DELETED_PATHS,
    *NEW_IMPLEMENTATION,
    "docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def fingerprint(path: Path, *, include_content: bool = False) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False}
    data = path.read_bytes()
    result: dict[str, Any] = {
        "exists": True,
        "bytes": len(data),
        "sha256": sha256(data),
    }
    if include_content:
        result["content_b64"] = base64.b64encode(data).decode("ascii")
    return result


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def value_fingerprint(value: Any) -> dict[str, Any]:
    encoded = canonical_json(value)
    return {"bytes": len(encoded), "sha256": sha256(encoded)}


def normalized_ast_sha256(node: ast.AST) -> str:
    dumped = ast.dump(node, annotate_fields=True, include_attributes=False)
    return sha256(dumped.encode("utf-8"))


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def literal_dict_assignment(path: Path, name: str) -> tuple[str, ast.Dict]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    matches: list[ast.Dict] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(
            isinstance(target, ast.Name) and target.id == name for target in targets
        ):
            if isinstance(node.value, ast.Dict):
                matches.append(node.value)
    if len(matches) != 1:
        raise RuntimeError(f"{relative(path)}: expected one literal {name} dictionary")
    return source, matches[0]


def dict_rows(source: str, node: ast.Dict) -> list[tuple[str, ast.AST]]:
    rows: list[tuple[str, ast.AST]] = []
    for key_node, value_node in zip(node.keys, node.values):
        if not (isinstance(key_node, ast.Constant) and isinstance(key_node.value, str)):
            raise RuntimeError("adventure plan owner keys must be literal strings")
        rows.append((key_node.value, value_node))
    return rows


def source_literal_manifest(
    *, assignment_name: str, advanced_keys: set[str]
) -> list[dict[str, Any]]:
    source, owner = literal_dict_assignment(ADVENTURES, assignment_name)
    selected = [row for row in dict_rows(source, owner) if row[0] in advanced_keys]
    if {key for key, _ in selected} != advanced_keys:
        raise RuntimeError(
            "advanced source owner does not contain the exact expected keys"
        )
    result: list[dict[str, Any]] = []
    for index, (key, value) in enumerate(selected):
        segment = ast.get_source_segment(source, value)
        if segment is None:
            raise RuntimeError(f"could not capture source segment for {key}")
        encoded = segment.encode("utf-8")
        result.append(
            {
                "index": index,
                "key": key,
                "normalized_ast_sha256": normalized_ast_sha256(value),
                "source_segment_bytes": len(encoded),
                "source_segment_sha256": sha256(encoded),
                "source_segment_b64": base64.b64encode(encoded).decode("ascii"),
            }
        )
    return result


def _import(name: str) -> Any:
    backend = ROOT / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    return importlib.import_module(name)


def stable_runtime_snapshot() -> dict[str, Any]:
    adventures = _import("curriculum.seed_data.adventures")
    blueprint = _import("curriculum.seed_data.source.blueprint")
    public = _import("curriculum.seed_data.adventure_levels")
    source_public = _import("curriculum.seed_data.source.adventure_levels")
    engine = _import("curriculum.engine_capabilities")

    wave_plans = adventures.ADVENTURE_WAVE_PLANS
    ordered_plans = [[key, value] for key, value in wave_plans.items()]
    supported = {
        spec["usage"]
        for spec in public.ADVENTURE_LEVELS
        if not spec.get("engine_blocked")
    }
    supported.update(engine.ENGINE_SUPPORTED_REFERENCE_FORMS)
    blueprint_identity = {
        slug: wave_plans[slug] is blueprint.BLUEPRINT_ADVENTURE_LEVELS[slug]
        for slug in blueprint.BLUEPRINT_ADVENTURE_LEVELS
    }
    return {
        "wave_plan_keys": list(wave_plans),
        "foundational_order": [
            key for key in wave_plans if key in blueprint.BLUEPRINT_ADVENTURE_LEVELS
        ],
        "wave_plan_count": len(wave_plans),
        "level_count": sum(len(levels) for levels in wave_plans.values()),
        "wave_count": sum(
            len(level.get("waves", []))
            for levels in wave_plans.values()
            for level in levels
        ),
        "ordered_plans": value_fingerprint(ordered_plans),
        "sorted_plans": value_fingerprint(wave_plans),
        "blueprint_value_identity": blueprint_identity,
        "adventure_sources": value_fingerprint(adventures.ADVENTURE_SOURCES),
        "adventure_source_count": sum(
            len(items) for items in adventures.ADVENTURE_SOURCES.values()
        ),
        "public_levels": value_fingerprint(public.ADVENTURE_LEVELS),
        "public_level_count": len(public.ADVENTURE_LEVELS),
        "public_spec_by_slug": value_fingerprint(public.SPEC_BY_SLUG),
        "public_spec_count": len(public.SPEC_BY_SLUG),
        "source_levels": value_fingerprint(source_public.ADVENTURE_LEVELS),
        "source_spec_by_slug": value_fingerprint(source_public.SPEC_BY_SLUG),
        "canonical_supported_forms": value_fingerprint(sorted(supported)),
        "canonical_supported_form_count": len(supported),
        "generated_targets": fingerprint(GENERATED_TARGETS),
    }


def legacy_supported_snapshot() -> dict[str, Any]:
    public = _import("curriculum.seed_data.adventure_levels")
    engine = _import("curriculum.engine_capabilities")
    supported = {
        spec["usage"]
        for spec in public.ADVENTURE_LEVELS
        if not spec.get("engine_blocked")
    }
    supported.update(engine.ENGINE_SUPPORTED_REFERENCE_FORMS)
    canonical = set(supported)
    plan = getattr(public, "ADVENTURE_LEVEL_PLAN", {})
    reuse = {
        usage
        for levels in plan.values()
        for level in levels
        for usage in level.get("reuse_usages", [])
    }
    supported.update(reuse)
    return {
        "legacy_reuse_forms": sorted(reuse),
        "legacy_reuse_form_count": len(reuse),
        "canonical_contains_all_legacy_reuse": reuse <= canonical,
        "with_legacy_forms": value_fingerprint(sorted(supported)),
        "with_legacy_form_count": len(supported),
        "canonical_forms": value_fingerprint(sorted(canonical)),
        "canonical_form_count": len(canonical),
    }


def wrapper_surfaces() -> dict[str, Any]:
    module_names = (
        "curriculum.seed_data.adventure_levels",
        "curriculum.seed_data.source.adventure_levels",
        "curriculum.seed_data.source.adventure_level_specs",
    )
    surfaces: dict[str, Any] = {}
    for name in module_names:
        module = _import(name)
        surfaces[name] = {
            "has_legacy_plan": hasattr(module, "ADVENTURE_LEVEL_PLAN"),
            "all": list(getattr(module, "__all__", [])),
            "supported_attributes": {
                item: hasattr(module, item)
                for item in (
                    "ADVENTURE_LEVELS",
                    "SPEC_BY_SLUG",
                    "adventure_levels_for",
                )
            },
        }
    return surfaces


def legacy_symbol_census() -> list[dict[str, Any]]:
    excluded = {
        POLICY_CHECKER.resolve(),
        POLICY_MODULE.resolve(),
        POLICY_TEST.resolve(),
    }
    rows: list[dict[str, Any]] = []
    roots = (ROOT / "backend", ROOT / "scripts")
    for scan_root in roots:
        for path in sorted(scan_root.rglob("*.py")):
            if path.resolve() in excluded:
                continue
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError, SyntaxError) as exc:
                raise RuntimeError(f"could not parse {relative(path)}: {exc}") from exc
            if "ADVENTURE_LEVEL_PLAN" not in source:
                continue
            try:
                tree = ast.parse(source)
            except SyntaxError as exc:
                raise RuntimeError(f"could not parse {relative(path)}: {exc}") from exc
            for node in ast.walk(tree):
                kind: str | None = None
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if any(
                        alias.name == "ADVENTURE_LEVEL_PLAN" for alias in node.names
                    ):
                        kind = "import"
                elif isinstance(node, ast.Name) and node.id == "ADVENTURE_LEVEL_PLAN":
                    kind = (
                        "binding" if isinstance(node.ctx, ast.Store) else "name-access"
                    )
                elif (
                    isinstance(node, ast.Attribute)
                    and node.attr == "ADVENTURE_LEVEL_PLAN"
                ):
                    kind = "attribute-access"
                if kind is not None:
                    rows.append(
                        {
                            "path": relative(path),
                            "line": getattr(node, "lineno", 0),
                            "column": getattr(node, "col_offset", 0),
                            "kind": kind,
                        }
                    )
            for node in tree.body:
                if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                    continue
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                if not any(
                    isinstance(target, ast.Name) and target.id == "__all__"
                    for target in targets
                ):
                    continue
                value = node.value
                if isinstance(value, (ast.List, ast.Tuple)) and any(
                    isinstance(item, ast.Constant)
                    and item.value == "ADVENTURE_LEVEL_PLAN"
                    for item in value.elts
                ):
                    rows.append(
                        {
                            "path": relative(path),
                            "line": node.lineno,
                            "column": node.col_offset,
                            "kind": "export",
                        }
                    )
    return sorted(
        rows,
        key=lambda row: (row["path"], row["line"], row["column"], row["kind"]),
    )


def visible_repository_paths() -> set[str]:
    output = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    return {
        raw.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for raw in output.split(b"\0")
        if raw
    }


def immutable_repository_snapshot() -> dict[str, Any]:
    paths = sorted(visible_repository_paths() - APPROVED_VISIBLE)
    return {path: fingerprint(ROOT / path) for path in paths}


def staged_paths() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    return sorted(
        raw.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for raw in result.stdout.split(b"\0")
        if raw
    )


def run_capture(
    argv: list[str],
    *,
    environment_updates: dict[str, str] | None = None,
) -> dict[str, Any]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.update(environment_updates or {})
    result = subprocess.run(
        argv,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "argv": argv,
        "cwd": str(ROOT),
        "exit_code": result.returncode,
        "stdout_b64": base64.b64encode(result.stdout).decode("ascii"),
        "stderr_b64": base64.b64encode(result.stderr).decode("ascii"),
        "stdout_sha256": sha256(result.stdout),
        "stderr_sha256": sha256(result.stderr),
    }


def capture_final_results() -> None:
    if FINAL_RESULTS.exists():
        raise RuntimeError("refusing to overwrite existing final command results")
    records: dict[str, Any] = {}
    failures: list[str] = []
    for label, command, argv, expected_exit in FINAL_COMMAND_SPECS:
        print(f"Running final gate: {label}", flush=True)
        record = run_capture(
            argv,
            environment_updates={"SLICE17_ALLOW_MISSING_FINAL_RESULTS": "1"},
        )
        record["command"] = command
        record["expected_exit_code"] = expected_exit
        records[label] = record
        record_errors: list[str] = []
        verify_command_record(
            label,
            record,
            command,
            argv,
            expected_exit,
            record_errors,
        )
        failures.extend(record_errors)
    if failures:
        raise RuntimeError("; ".join(failures))
    payload = {
        "version": 1,
        "baseline": fingerprint(BASELINE),
        "plan_manifest": fingerprint(PLAN_MANIFEST),
        "bindings": {path: fingerprint(ROOT / path) for path in FINAL_BINDING_PATHS},
        "commands": records,
        "staged_paths": staged_paths(),
    }
    write_json(FINAL_RESULTS, payload)
    print(f"Captured {relative(FINAL_RESULTS)}")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def capture_baseline() -> None:
    if BASELINE.exists() or PLAN_MANIFEST.exists():
        raise RuntimeError("refusing to overwrite an existing Slice 17 baseline")
    runtime = stable_runtime_snapshot()
    blueprint_keys = set(FOUNDATIONAL_ORDER)
    source, owner = literal_dict_assignment(ADVENTURES, "ADVENTURE_WAVE_PLANS")
    literal_keys = [key for key, _ in dict_rows(source, owner)]
    advanced_keys = set(literal_keys) - blueprint_keys
    plan_manifest = {
        "version": 1,
        "foundational_order": list(FOUNDATIONAL_ORDER),
        "literal_foundational_keys": [
            key for key in literal_keys if key in blueprint_keys
        ],
        "advanced_keys": [key for key in literal_keys if key in advanced_keys],
        "advanced_literals": source_literal_manifest(
            assignment_name="ADVENTURE_WAVE_PLANS",
            advanced_keys=advanced_keys,
        ),
        "runtime": runtime,
        "legacy_supported": legacy_supported_snapshot(),
        "legacy_symbol_census": legacy_symbol_census(),
        "wrapper_surfaces": wrapper_surfaces(),
        "planned_preimages": {
            path: fingerprint(ROOT / path, include_content=True)
            for path in (*MODIFIED_EXISTING, *DELETED_PATHS)
        },
        "new_implementation_absences": {
            path: fingerprint(ROOT / path) for path in NEW_IMPLEMENTATION
        },
    }
    baseline = {
        "version": 1,
        "approved_visible_paths": sorted(APPROVED_VISIBLE),
        "immutable_repository": immutable_repository_snapshot(),
        "stable_plan_files": {
            path: fingerprint(ROOT / path) for path in STABLE_PLAN_FILES
        },
        "staged_paths": staged_paths(),
        "commands": {label: run_capture(argv) for label, argv in BASELINE_COMMANDS},
    }
    write_json(PLAN_MANIFEST, plan_manifest)
    write_json(BASELINE, baseline)
    print(f"Captured {relative(BASELINE)}")
    print(f"Captured {relative(PLAN_MANIFEST)}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def verify_manifest_hashes(errors: list[str]) -> None:
    require(BASELINE.is_file(), "missing PRE_SLICE_BASELINE.json", errors)
    require(PLAN_MANIFEST.is_file(), "missing PRE_CUTOVER_PLAN_MANIFEST.json", errors)
    if not (BASELINE.is_file() and PLAN_MANIFEST.is_file()):
        return
    if BASELINE_SHA256 != "TO_BE_PINNED":
        require(
            fingerprint(BASELINE)["sha256"] == BASELINE_SHA256,
            "PRE_SLICE_BASELINE.json hash drifted",
            errors,
        )
    if PLAN_MANIFEST_SHA256 != "TO_BE_PINNED":
        require(
            fingerprint(PLAN_MANIFEST)["sha256"] == PLAN_MANIFEST_SHA256,
            "PRE_CUTOVER_PLAN_MANIFEST.json hash drifted",
            errors,
        )


def verify_stable_runtime(manifest: dict[str, Any], errors: list[str]) -> None:
    current = stable_runtime_snapshot()
    require(current == manifest["runtime"], "stable runtime snapshot drifted", errors)
    require(
        current["wave_plan_keys"][: len(FOUNDATIONAL_ORDER)]
        == list(FOUNDATIONAL_ORDER),
        "public foundational key order drifted",
        errors,
    )
    require(current["wave_plan_count"] == 35, "expected 35 wave plans", errors)
    require(current["level_count"] == 95, "expected 95 plan levels", errors)
    require(current["wave_count"] == 437, "expected 437 plan waves", errors)
    require(current["public_level_count"] == 663, "expected 663 public specs", errors)
    require(current["public_spec_count"] == 663, "expected 663 indexed specs", errors)
    require(
        current["canonical_supported_form_count"] == 159,
        "expected 159 canonical supported forms",
        errors,
    )
    require(
        all(current["blueprint_value_identity"].values()),
        "a foundational public plan lost blueprint object identity",
        errors,
    )


def verify_advanced_literals(manifest: dict[str, Any], errors: list[str]) -> None:
    expected_keys = set(manifest["advanced_keys"])
    try:
        current = source_literal_manifest(
            assignment_name="_ADVANCED_DRILL_WAVE_PLANS",
            advanced_keys=expected_keys,
        )
    except RuntimeError as exc:
        errors.append(str(exc))
        return
    require(
        current == manifest["advanced_literals"],
        "advanced plan source literals drifted during cutover",
        errors,
    )


def verify_legacy_retirement(manifest: dict[str, Any], errors: list[str]) -> None:
    require(
        manifest["legacy_supported"]["canonical_contains_all_legacy_reuse"],
        "baseline did not prove legacy reuse forms were redundant",
        errors,
    )
    require(
        manifest["legacy_supported"]["canonical_forms"]
        == manifest["legacy_supported"]["with_legacy_forms"],
        "baseline canonical/legacy supported sets differ",
        errors,
    )
    census = legacy_symbol_census()
    require(not census, f"live legacy symbol consumers remain: {census}", errors)
    surfaces = wrapper_surfaces()
    expected_supported = {
        "curriculum.seed_data.adventure_levels": {
            "ADVENTURE_LEVELS",
            "SPEC_BY_SLUG",
            "adventure_levels_for",
        },
        "curriculum.seed_data.source.adventure_levels": {
            "ADVENTURE_LEVELS",
            "SPEC_BY_SLUG",
            "adventure_levels_for",
        },
        "curriculum.seed_data.source.adventure_level_specs": {
            "ADVENTURE_LEVELS",
            "SPEC_BY_SLUG",
            "adventure_levels_for",
        },
    }
    for module_name, expected_names in expected_supported.items():
        surface = surfaces[module_name]
        require(
            not surface["has_legacy_plan"],
            f"{module_name} still exposes ADVENTURE_LEVEL_PLAN",
            errors,
        )
        require(
            "ADVENTURE_LEVEL_PLAN" not in surface["all"],
            f"{module_name} still exports ADVENTURE_LEVEL_PLAN",
            errors,
        )
        require(
            expected_names <= set(surface["all"]),
            f"{module_name} lost a supported __all__ export",
            errors,
        )
        require(
            all(surface["supported_attributes"].values()),
            f"{module_name} lost a supported attribute",
            errors,
        )
    for path in DELETED_PATHS:
        require(not (ROOT / path).exists(), f"legacy scaffold remains: {path}", errors)
    require(
        not LEGACY_CHAPTER_PACKAGE.exists(),
        "legacy source/ch1 package path remains",
        errors,
    )


def verify_preservation(baseline: dict[str, Any], errors: list[str]) -> None:
    require(
        immutable_repository_snapshot() == baseline["immutable_repository"],
        "an immutable visible repository path changed after baseline capture",
        errors,
    )
    require(
        {path: fingerprint(ROOT / path) for path in STABLE_PLAN_FILES}
        == baseline["stable_plan_files"],
        "GOAL.md or approved PLAN.md drifted after baseline capture",
        errors,
    )
    require(not staged_paths(), "Slice 17 must leave the index unstaged", errors)


def _decode_record_stream(
    label: str,
    record: dict[str, Any],
    stream: str,
    errors: list[str],
) -> bytes | None:
    encoded = record.get(f"{stream}_b64")
    if not isinstance(encoded, str):
        errors.append(f"{label} {stream} payload is missing")
        return None
    try:
        payload = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        errors.append(f"{label} {stream} payload is not strict base64")
        return None
    require(
        record.get(f"{stream}_sha256") == sha256(payload),
        f"{label} {stream} digest does not match its payload",
        errors,
    )
    return payload


def verify_command_record(
    label: str,
    record: dict[str, Any],
    command: str,
    argv: list[str],
    expected_exit: int,
    errors: list[str],
) -> None:
    require(record.get("command") == command, f"{label} command drifted", errors)
    require(record.get("argv") == argv, f"{label} argv drifted", errors)
    require(record.get("cwd") == str(ROOT), f"{label} cwd drifted", errors)
    require(
        record.get("expected_exit_code") == expected_exit,
        f"{label} expected exit drifted",
        errors,
    )
    require(
        record.get("exit_code") == expected_exit,
        f"{label} did not produce its accepted exit",
        errors,
    )
    stdout = _decode_record_stream(label, record, "stdout", errors)
    stderr = _decode_record_stream(label, record, "stderr", errors)
    if stdout is not None:
        for token in FINAL_OUTPUT_TOKENS[label]:
            require(
                token.encode("utf-8") in stdout,
                f"{label} stdout lacks required proof token: {token}",
                errors,
            )
    if stderr is not None:
        for token in FINAL_STDERR_TOKENS.get(label, ()):
            require(
                token.encode("utf-8") in stderr,
                f"{label} stderr lacks preserved warning token: {token}",
                errors,
            )
    if label not in FINAL_STDERR_TOKENS:
        require(stderr == b"", f"{label} recorded unexpected stderr", errors)
    if label in {"supporting_text_census", "diff_check"}:
        require(stdout == b"", f"{label} expected empty stdout", errors)


def verify_final_results(errors: list[str]) -> None:
    if not FINAL_RESULTS.is_file():
        if os.environ.get("SLICE17_ALLOW_MISSING_FINAL_RESULTS") != "1":
            errors.append("missing FINAL_COMMAND_RESULTS.json")
        return
    payload = load_json(FINAL_RESULTS)
    require(payload.get("version") == 1, "final results version drifted", errors)
    require(
        payload.get("baseline") == fingerprint(BASELINE),
        "final results are not bound to the baseline manifest",
        errors,
    )
    require(
        payload.get("plan_manifest") == fingerprint(PLAN_MANIFEST),
        "final results are not bound to the cutover manifest",
        errors,
    )
    require(
        payload.get("bindings")
        == {path: fingerprint(ROOT / path) for path in FINAL_BINDING_PATHS},
        "settled implementation differs from final command bindings",
        errors,
    )
    expected_labels = [label for label, _, _, _ in FINAL_COMMAND_SPECS]
    records = payload.get("commands", {})
    require(
        list(records) == sorted(expected_labels),
        "final command record set is incomplete",
        errors,
    )
    for label, command, argv, expected_exit in FINAL_COMMAND_SPECS:
        record = records.get(label, {})
        verify_command_record(
            label,
            record,
            command,
            argv,
            expected_exit,
            errors,
        )
    require(
        not payload.get("staged_paths"), "final results recorded staged files", errors
    )


def verify_baseline_phase(
    baseline: dict[str, Any], manifest: dict[str, Any], errors: list[str]
) -> None:
    verify_preservation(baseline, errors)
    require(
        staged_paths() == baseline["staged_paths"] == [],
        "baseline expected an empty staged index",
        errors,
    )
    require(
        {
            path: fingerprint(ROOT / path, include_content=True)
            for path in (*MODIFIED_EXISTING, *DELETED_PATHS)
        }
        == manifest["planned_preimages"],
        "a planned preimage changed before cutover",
        errors,
    )
    require(
        {path: fingerprint(ROOT / path) for path in NEW_IMPLEMENTATION}
        == manifest["new_implementation_absences"],
        "new implementation path appeared before cutover",
        errors,
    )
    require(
        all(record["exit_code"] == 0 for record in baseline["commands"].values()),
        "a direct baseline command did not pass",
        errors,
    )
    require(
        len(manifest["advanced_keys"]) == 19,
        "baseline expected 19 advanced owner keys",
        errors,
    )
    require(
        manifest["foundational_order"] == list(FOUNDATIONAL_ORDER),
        "baseline foundational order differs from the approved contract",
        errors,
    )
    verify_stable_runtime(manifest, errors)


def verify(phase: str) -> list[str]:
    errors: list[str] = []
    verify_manifest_hashes(errors)
    if errors:
        return errors
    baseline = load_json(BASELINE)
    manifest = load_json(PLAN_MANIFEST)
    if phase == "baseline":
        verify_baseline_phase(baseline, manifest, errors)
        return errors

    verify_stable_runtime(manifest, errors)
    verify_advanced_literals(manifest, errors)
    if phase in {"legacy", "final"}:
        verify_legacy_retirement(manifest, errors)
    if phase == "final":
        verify_preservation(baseline, errors)
        require(POLICY_TEST.is_file(), "missing focused ownership test", errors)
        require(POLICY_MODULE.is_file(), "missing adventure ownership policy", errors)
        verify_final_results(errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--capture-baseline",
        action="store_true",
        help="capture immutable pre-cutover manifests once",
    )
    parser.add_argument(
        "--capture-final-results",
        action="store_true",
        help="run and capture the settled command matrix once",
    )
    parser.add_argument(
        "--phase",
        choices=("baseline", "plans", "legacy", "final"),
        default="final",
    )
    args = parser.parse_args()
    try:
        if args.capture_baseline:
            capture_baseline()
            return 0
        if args.capture_final_results:
            capture_final_results()
            return 0
        errors = verify(args.phase)
    except Exception as exc:  # pragma: no cover - evidence CLI hard failure
        print(f"Slice 17 evidence verification failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("Slice 17 evidence problems found:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(f"Slice 17 evidence verified ({args.phase}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
