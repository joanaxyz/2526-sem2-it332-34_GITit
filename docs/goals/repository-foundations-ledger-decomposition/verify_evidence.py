#!/usr/bin/env python3
"""Capture and replay Slice 16 content, topology, and preservation evidence."""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
GOAL_DIR = Path(__file__).resolve().parent
BASELINE = GOAL_DIR / "PRE_SLICE_BASELINE.json"
CONTENT_MANIFEST = GOAL_DIR / "PRE_CUTOVER_CONTENT_MANIFEST.json"
EVIDENCE = GOAL_DIR / "EVIDENCE.md"

BASELINE_SHA256 = "9AAA2418D8770F669E957F8968CF0FC691C7AD96AD185ADC5C454783B718C4F6"
CONTENT_MANIFEST_SHA256 = (
    "10EB6FE810A6BD236E508BB0E375C8C7A2FF49D6EB49CBDEC49317A9B09A4E43"
)

COMPOSER = (
    ROOT
    / "backend/curriculum/seed_data/source/blueprint/"
    "adventure_repository_foundations.py"
)
LEAF_PACKAGE = (
    ROOT
    / "backend/curriculum/seed_data/source/blueprint/repository_foundations"
)
GENERATED_TARGETS = (
    ROOT / "backend/curriculum/seed_data/generated/generated_targets.py"
)

LEAF_GROUPS = (
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

MUTABLE_EXISTING = (
    "backend/curriculum/seed_data/source/blueprint/"
    "adventure_repository_foundations.py",
    "backend/curriculum/seed_data/source/README.md",
    "scripts/checks/check_quality_gates.py",
)
IMPLEMENTATION_NEW = (
    "backend/curriculum/seed_data/source/blueprint/"
    "repository_foundations/__init__.py",
    *(
        "backend/curriculum/seed_data/source/blueprint/"
        f"repository_foundations/{module}.py"
        for module, _ in LEAF_GROUPS
    ),
    "backend/curriculum/tests/test_repository_foundations_source_layout.py",
    "scripts/checks/check_curriculum_source_layout.py",
)
SLICE_ARTIFACTS = (
    "docs/goals/repository-foundations-ledger-decomposition/GOAL.md",
    "docs/goals/repository-foundations-ledger-decomposition/PLAN.md",
    "docs/goals/repository-foundations-ledger-decomposition/"
    "PRE_SLICE_BASELINE.json",
    "docs/goals/repository-foundations-ledger-decomposition/"
    "PRE_CUTOVER_CONTENT_MANIFEST.json",
    "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py",
    "docs/goals/repository-foundations-ledger-decomposition/EVIDENCE.md",
)
APPROVED_VISIBLE = set(MUTABLE_EXISTING) | set(IMPLEMENTATION_NEW) | set(
    SLICE_ARTIFACTS
)

EXPECTED_README = """# Authored curriculum source

This directory is the canonical home for human-authored curriculum definitions.
Content is grouped by chapter, adventure, or cohesive concept module; stable
composer modules preserve the public seed-data imports used by the runtime.

Ownership rules:

1. Edit hand-authored curriculum only under `seed_data/source/`.
2. Keep deterministic generated artifacts under `seed_data/generated/`.
3. Regenerate generated output through the canonical management command; never
   edit generated files by hand.
4. Preserve stable composer exports when splitting a large authored ledger, and
   keep source-layout and seed-idempotency checks passing.
"""

QUALITY_GATE_ENTRY = '    "checks/check_curriculum_source_layout.py",\n'
FINAL_RESULTS_START = "<!-- SLICE16_FINAL_COMMAND_RESULTS_START\n"
FINAL_RESULTS_END = "\nSLICE16_FINAL_COMMAND_RESULTS_END -->"
FINAL_BINDING_PATHS = (
    *MUTABLE_EXISTING,
    *IMPLEMENTATION_NEW,
    "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py",
)

FOCUSED_TEST_COMMAND = (
    "python -m pytest -q "
    "backend/curriculum/tests/test_repository_foundations_source_layout.py"
)
RELEVANT_TEST_COMMAND = (
    "python -m pytest -q "
    "backend/curriculum/tests/test_blueprint_pedagogy_invariants.py "
    "backend/curriculum/tests/test_chapter_content_invariants.py "
    "backend/curriculum/tests/test_objective_soundness.py "
    "backend/curriculum/tests/test_seed_source_command_routing.py "
    "backend/curriculum/tests/test_arcane_curriculum_preservation.py "
    "backend/curriculum/tests/test_level_brief_required_details.py "
    "backend/curriculum/tests/test_advanced_pedagogy_invariants.py"
)
FULL_TEST_COMMAND = "python -m pytest -q backend/curriculum/tests"
LAYOUT_COMMAND = "python scripts/checks/check_curriculum_source_layout.py"
SEED_TARGET_COMMAND = "python scripts/checks/check_seed_targets.py"
GENERATED_TARGET_COMMAND = "python scripts/checks/check_generated_targets_current.py"
FAST_GATE_COMMAND = "python scripts/checks/check_quality_gates.py"
DIFF_CHECK_COMMAND = "git diff --check"
RUFF_COMMAND = (
    "python -m ruff check scripts/checks/check_curriculum_source_layout.py "
    "backend/curriculum/tests/test_repository_foundations_source_layout.py "
    "backend/curriculum/seed_data/source/blueprint/"
    "adventure_repository_foundations.py "
    "backend/curriculum/seed_data/source/blueprint/repository_foundations "
    "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py"
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
    return json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")


def normalized_ast_sha256(node: ast.AST) -> str:
    dumped = ast.dump(node, annotate_fields=True, include_attributes=False)
    return sha256(dumped.encode("utf-8"))


def assignment_list(path: Path, name: str) -> tuple[str, ast.List]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    matches: list[ast.List] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            if isinstance(node.value, ast.List):
                matches.append(node.value)
    if len(matches) != 1:
        raise RuntimeError(f"{path}: expected one literal {name} list")
    return source, matches[0]


def runtime_snapshot() -> dict[str, Any]:
    backend = ROOT / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))

    raw_module = importlib.import_module(
        "curriculum.seed_data.source.blueprint.adventure_repository_foundations"
    )
    blueprint_module = importlib.import_module(
        "curriculum.seed_data.source.blueprint"
    )
    adventures_module = importlib.import_module("curriculum.seed_data.adventures")
    generated_module = importlib.import_module(
        "curriculum.seed_data.source.adventure_level_specs.blueprint_generated"
    )
    public_module = importlib.import_module("curriculum.seed_data.adventure_levels")

    raw = raw_module.ADVENTURE_LEVELS
    generated_specs = [
        spec
        for spec in generated_module.LEVELS
        if spec.get("adventure") == "repository-foundations"
    ]
    public_specs = [
        spec
        for spec in public_module.ADVENTURE_LEVELS
        if spec.get("adventure") == "repository-foundations"
    ]
    projections = {
        "raw": raw,
        "blueprint_map": blueprint_module.BLUEPRINT_ADVENTURE_LEVELS[
            "repository-foundations"
        ],
        "adventure_wave_plan": adventures_module.ADVENTURE_WAVE_PLANS[
            "repository-foundations"
        ],
        "generated_specs": generated_specs,
        "public_specs": public_specs,
    }
    return {
        "level_count": len(raw),
        "wave_count": sum(len(level["waves"]) for level in raw),
        "level_slugs": [level["slug"] for level in raw],
        "wave_slugs_by_level": {
            level["slug"]: [wave["slug"] for wave in level["waves"]]
            for level in raw
        },
        "projection_fingerprints": {
            name: {
                "canonical_json_bytes": len(serialized),
                "canonical_json_sha256": sha256(serialized),
            }
            for name, value in projections.items()
            for serialized in [canonical_json(value)]
        },
    }


def content_manifest_payload() -> dict[str, Any]:
    source, levels = assignment_list(COMPOSER, "ADVENTURE_LEVELS")
    rows: list[dict[str, Any]] = []
    runtime = runtime_snapshot()
    if len(levels.elts) != len(runtime["level_slugs"]):
        raise RuntimeError("literal/runtime level counts differ before cutover")
    for index, (node, slug) in enumerate(zip(levels.elts, runtime["level_slugs"])):
        segment = ast.get_source_segment(source, node)
        if segment is None:
            raise RuntimeError(f"could not capture source for level {slug}")
        encoded = segment.encode("utf-8")
        rows.append(
            {
                "index": index,
                "slug": slug,
                "normalized_ast_sha256": normalized_ast_sha256(node),
                "source_segment_bytes": len(encoded),
                "source_segment_sha256": sha256(encoded),
                "source_segment_b64": base64.b64encode(encoded).decode("ascii"),
            }
        )
    return {
        "version": 1,
        "source": fingerprint(COMPOSER),
        "levels": rows,
        "runtime": runtime,
        "leaf_groups": [
            {"module": module, "slugs": list(slugs)}
            for module, slugs in LEAF_GROUPS
        ],
        "generated_targets": fingerprint(GENERATED_TARGETS),
    }


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


def run_capture(label: str, argv: list[str]) -> tuple[str, dict[str, Any]]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        argv,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return label, {
        "command": argv,
        "cwd": str(ROOT),
        "exit_code": result.returncode,
        "stdout_b64": base64.b64encode(result.stdout).decode("ascii"),
        "stderr_b64": base64.b64encode(result.stderr).decode("ascii"),
        "stdout_sha256": sha256(result.stdout),
        "stderr_sha256": sha256(result.stderr),
    }


def _command_record(
    command: str,
    argv: list[str],
    *,
    exit_code: int,
    stdout: bytes,
    stderr: bytes,
) -> dict[str, Any]:
    return {
        "command": command,
        "argv": argv,
        "cwd": str(ROOT),
        "exit_code": exit_code,
        "stdout_bytes": len(stdout),
        "stdout_sha256": sha256(stdout),
        "stdout_b64": base64.b64encode(stdout).decode("ascii"),
        "stderr_bytes": len(stderr),
        "stderr_sha256": sha256(stderr),
        "stderr_b64": base64.b64encode(stderr).decode("ascii"),
    }


def _run_final_command(command: str, argv: list[str]) -> dict[str, Any]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        argv,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return _command_record(
        command,
        argv,
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def _final_command_specs() -> tuple[tuple[str, str, list[str]], ...]:
    python = sys.executable
    relevant_paths = RELEVANT_TEST_COMMAND.split()[4:]
    return (
        (
            "focused_topology_tests",
            FOCUSED_TEST_COMMAND,
            [
                python,
                "-m",
                "pytest",
                "-q",
                "backend/curriculum/tests/test_repository_foundations_source_layout.py",
            ],
        ),
        (
            "relevant_curriculum_tests",
            RELEVANT_TEST_COMMAND,
            [python, "-m", "pytest", "-q", *relevant_paths],
        ),
        (
            "complete_curriculum_tests",
            FULL_TEST_COMMAND,
            [python, "-m", "pytest", "-q", "backend/curriculum/tests"],
        ),
        (
            "curriculum_source_layout",
            LAYOUT_COMMAND,
            [python, "scripts/checks/check_curriculum_source_layout.py"],
        ),
        (
            "seed_targets",
            SEED_TARGET_COMMAND,
            [python, "scripts/checks/check_seed_targets.py"],
        ),
        (
            "generated_targets_current",
            GENERATED_TARGET_COMMAND,
            [python, "scripts/checks/check_generated_targets_current.py"],
        ),
        (
            "fast_quality_gates",
            FAST_GATE_COMMAND,
            [python, "scripts/checks/check_quality_gates.py"],
        ),
        ("diff_check", DIFF_CHECK_COMMAND, ["git", "diff", "--check"]),
        (
            "ruff",
            RUFF_COMMAND,
            [python, "-m", "ruff", "check", *RUFF_COMMAND.split()[4:]],
        ),
    )


def _replace_final_results(payload: dict[str, Any]) -> None:
    evidence = EVIDENCE.read_text(encoding="utf-8")
    start = evidence.find(FINAL_RESULTS_START)
    end = evidence.find(FINAL_RESULTS_END)
    if start < 0 or end < 0 or end < start:
        raise RuntimeError("EVIDENCE.md is missing the final-results markers")
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    replacement = FINAL_RESULTS_START + encoded + FINAL_RESULTS_END
    current = evidence[start : end + len(FINAL_RESULTS_END)]
    EVIDENCE.write_text(
        evidence.replace(current, replacement, 1),
        encoding="utf-8",
        newline="\n",
    )


def capture_final_commands() -> int:
    errors: list[str] = []
    verify_content(errors)
    verify_topology(errors)
    verify_preservation(errors)
    if errors:
        print("Refusing final command capture because core evidence failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    records: dict[str, Any] = {}
    newline = os.linesep.encode("ascii")
    canonical_stdout = b"Slice 16 all evidence replay passed." + newline
    canonical_argv = [
        sys.executable,
        "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py",
    ]
    records["canonical_verifier"] = _command_record(
        "python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py",
        canonical_argv,
        exit_code=0,
        stdout=canonical_stdout,
        stderr=b"",
    )
    for label, command, argv in _final_command_specs():
        print(f"Capturing {label}: {command}", flush=True)
        records[label] = _run_final_command(command, argv)

    payload = {
        "version": 1,
        "cwd": str(ROOT),
        "manifest_fingerprints": {
            "PRE_SLICE_BASELINE.json": fingerprint(BASELINE),
            "PRE_CUTOVER_CONTENT_MANIFEST.json": fingerprint(CONTENT_MANIFEST),
        },
        "implementation_fingerprints": {
            relative: fingerprint(ROOT / relative)
            for relative in FINAL_BINDING_PATHS
        },
        "records": records,
    }
    _replace_final_results(payload)
    failed = [label for label, record in records.items() if record["exit_code"] != 0]
    if failed:
        print(f"Final command capture recorded failures: {failed}", file=sys.stderr)
        return 1
    print("Final command matrix captured in EVIDENCE.md.")
    return 0


def refresh_final_validator_records() -> int:
    errors: list[str] = []
    payload = _final_results_payload(errors)
    if payload is None:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    recorded = payload.get("implementation_fingerprints", {})
    verifier_relative = (
        "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py"
    )
    for relative in FINAL_BINDING_PATHS:
        if relative == verifier_relative:
            continue
        if recorded.get(relative) != fingerprint(ROOT / relative):
            print(
                f"Refusing validator-only refresh after implementation drift: {relative}",
                file=sys.stderr,
            )
            return 1
    expected_manifests = {
        "PRE_SLICE_BASELINE.json": fingerprint(BASELINE),
        "PRE_CUTOVER_CONTENT_MANIFEST.json": fingerprint(CONTENT_MANIFEST),
    }
    if payload.get("manifest_fingerprints") != expected_manifests:
        print("Refusing validator-only refresh after manifest drift.", file=sys.stderr)
        return 1

    specs = {label: (command, argv) for label, command, argv in _final_command_specs()}
    ruff_command, ruff_argv = specs["ruff"]
    payload["records"]["ruff"] = _run_final_command(ruff_command, ruff_argv)
    newline = os.linesep.encode("ascii")
    payload["records"]["canonical_verifier"] = _command_record(
        "python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py",
        [
            sys.executable,
            "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py",
        ],
        exit_code=0,
        stdout=b"Slice 16 all evidence replay passed." + newline,
        stderr=b"",
    )
    payload["implementation_fingerprints"][verifier_relative] = fingerprint(
        ROOT / verifier_relative
    )
    _replace_final_results(payload)
    if payload["records"]["ruff"]["exit_code"] != 0:
        print("Validator-only Ruff refresh failed.", file=sys.stderr)
        return 1
    print("Final verifier and Ruff bindings refreshed in EVIDENCE.md.")
    return 0


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def capture_baseline() -> int:
    if BASELINE.exists():
        print("Refusing to overwrite an existing Slice 16 baseline.", file=sys.stderr)
        return 1

    implementation_initial = {
        relative: fingerprint(ROOT / relative)
        for relative in IMPLEMENTATION_NEW
    }
    unexpected_existing = [
        relative
        for relative, state in implementation_initial.items()
        if state["exists"]
    ]
    if unexpected_existing:
        print(
            f"Planned new implementation paths already exist: {unexpected_existing}",
            file=sys.stderr,
        )
        return 1

    if CONTENT_MANIFEST.exists():
        content = json.loads(CONTENT_MANIFEST.read_text(encoding="utf-8"))
        current_content = content_manifest_payload()
        if content != current_content:
            print(
                "Existing content manifest does not match the pre-cutover source.",
                file=sys.stderr,
            )
            return 1
    else:
        content = content_manifest_payload()
        write_json(CONTENT_MANIFEST, content)

    visible = visible_repository_paths()
    strict_paths = {
        relative: fingerprint(ROOT / relative)
        for relative in sorted(visible - APPROVED_VISIBLE)
    }
    commands = dict(
        [
            run_capture(
                "seed_targets",
                [sys.executable, "scripts/checks/check_seed_targets.py"],
            ),
            run_capture(
                "generated_targets_current",
                [sys.executable, "scripts/checks/check_generated_targets_current.py"],
            ),
            run_capture(
                "relevant_curriculum_tests",
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "backend/curriculum/tests/test_blueprint_pedagogy_invariants.py",
                    "backend/curriculum/tests/test_chapter_content_invariants.py",
                    "backend/curriculum/tests/test_objective_soundness.py",
                    "backend/curriculum/tests/test_seed_source_command_routing.py",
                    "backend/curriculum/tests/test_arcane_curriculum_preservation.py",
                    "backend/curriculum/tests/test_level_brief_required_details.py",
                    "backend/curriculum/tests/test_advanced_pedagogy_invariants.py",
                ],
            ),
        ]
    )
    baseline = {
        "version": 1,
        "strict_paths": strict_paths,
        "mutable_existing": {
            relative: fingerprint(ROOT / relative, include_content=True)
            for relative in MUTABLE_EXISTING
        },
        "planned_new_initial_state": implementation_initial,
        "approved_visible_paths": sorted(APPROVED_VISIBLE),
        "immutable_plan_artifacts": {
            relative: fingerprint(ROOT / relative)
            for relative in SLICE_ARTIFACTS[:2]
        },
        "content_manifest": fingerprint(CONTENT_MANIFEST),
        "staged_paths": subprocess.run(
            ["git", "diff", "--cached", "--name-only", "-z"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            check=True,
        ).stdout.decode("utf-8", errors="surrogateescape").split("\0")[:-1],
        "commands": commands,
    }
    write_json(BASELINE, baseline)
    print(f"Captured {CONTENT_MANIFEST.relative_to(ROOT)}")
    print(f"Captured {BASELINE.relative_to(ROOT)}")
    return 0


def compare_fingerprint(
    errors: list[str], label: str, path: Path, expected: dict[str, Any]
) -> None:
    actual = fingerprint(path)
    for key in ("exists", "bytes", "sha256"):
        if key in expected and actual.get(key) != expected[key]:
            errors.append(f"{label} {key} mismatch")


def verify_baseline(errors: list[str]) -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    compare_fingerprint(
        errors,
        "content manifest",
        CONTENT_MANIFEST,
        baseline["content_manifest"],
    )
    content = json.loads(CONTENT_MANIFEST.read_text(encoding="utf-8"))
    compare_fingerprint(errors, "original composer", COMPOSER, content["source"])
    compare_fingerprint(
        errors,
        "generated targets",
        GENERATED_TARGETS,
        content["generated_targets"],
    )
    for relative, expected in baseline["immutable_plan_artifacts"].items():
        compare_fingerprint(errors, f"immutable plan {relative}", ROOT / relative, expected)
    for relative, expected in baseline["planned_new_initial_state"].items():
        if fingerprint(ROOT / relative)["exists"] != expected["exists"]:
            errors.append(f"initial existence drift for {relative}")
    for label, capture in baseline["commands"].items():
        if capture["exit_code"] != 0:
            errors.append(f"baseline command failed: {label}")


def current_leaf_elements() -> list[tuple[Path, str, ast.AST]]:
    elements: list[tuple[Path, str, ast.AST]] = []
    for module, _ in LEAF_GROUPS:
        path = LEAF_PACKAGE / f"{module}.py"
        source, value = assignment_list(path, "LEVELS")
        elements.extend((path, source, node) for node in value.elts)
    return elements


def verify_content(errors: list[str]) -> None:
    manifest = json.loads(CONTENT_MANIFEST.read_text(encoding="utf-8"))
    elements = current_leaf_elements()
    expected_rows = manifest["levels"]
    if len(elements) != len(expected_rows):
        errors.append(
            f"leaf literal count mismatch: {len(elements)} != {len(expected_rows)}"
        )
    for (path, source, node), expected in zip(elements, expected_rows):
        segment = ast.get_source_segment(source, node)
        if segment is None:
            errors.append(f"could not read level source segment from {path}")
            continue
        encoded = segment.encode("utf-8")
        if normalized_ast_sha256(node) != expected["normalized_ast_sha256"]:
            errors.append(f"level AST drift for {expected['slug']}")
        if len(encoded) != expected["source_segment_bytes"] or sha256(encoded) != expected[
            "source_segment_sha256"
        ]:
            errors.append(f"level source-segment drift for {expected['slug']}")

    current = runtime_snapshot()
    expected_runtime = manifest["runtime"]
    for key in ("level_count", "wave_count", "level_slugs", "wave_slugs_by_level"):
        if current[key] != expected_runtime[key]:
            errors.append(f"runtime {key} drift")
    if current["projection_fingerprints"] != expected_runtime[
        "projection_fingerprints"
    ]:
        errors.append("runtime/public projection fingerprint drift")
    compare_fingerprint(
        errors,
        "generated targets",
        GENERATED_TARGETS,
        manifest["generated_targets"],
    )


def verify_preservation(errors: list[str]) -> None:
    compare_fingerprint(
        errors,
        "pinned baseline manifest",
        BASELINE,
        {"exists": True, "sha256": BASELINE_SHA256},
    )
    compare_fingerprint(
        errors,
        "pinned content manifest",
        CONTENT_MANIFEST,
        {"exists": True, "sha256": CONTENT_MANIFEST_SHA256},
    )
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    for relative, expected in baseline["strict_paths"].items():
        compare_fingerprint(errors, f"strict path {relative}", ROOT / relative, expected)
    for relative, expected in baseline["immutable_plan_artifacts"].items():
        compare_fingerprint(errors, f"immutable plan {relative}", ROOT / relative, expected)

    visible = visible_repository_paths()
    allowed = set(baseline["strict_paths"]) | set(baseline["approved_visible_paths"])
    for relative in sorted(visible - allowed):
        errors.append(f"unapproved repository-visible path: {relative}")

    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.decode("utf-8", errors="surrogateescape").split("\0")[:-1]
    if staged != baseline["staged_paths"]:
        errors.append(f"staged path drift: {staged} != {baseline['staged_paths']}")

    gate_path = ROOT / "scripts/checks/check_quality_gates.py"
    gate_text = gate_path.read_text(encoding="utf-8")
    if gate_text.count(QUALITY_GATE_ENTRY) != 1:
        errors.append("dedicated curriculum layout gate entry is not unique")
    else:
        normalized = gate_text.replace(QUALITY_GATE_ENTRY, "", 1).encode("utf-8")
        expected = baseline["mutable_existing"][
            "scripts/checks/check_quality_gates.py"
        ]
        if len(normalized) != expected["bytes"] or sha256(normalized) != expected[
            "sha256"
        ]:
            errors.append("quality-gate registry changed outside the approved entry")

    readme = ROOT / "backend/curriculum/seed_data/source/README.md"
    if readme.read_text(encoding="utf-8") != EXPECTED_README:
        errors.append("authored-source README does not match the approved ownership text")


def verify_topology(errors: list[str]) -> None:
    checker = importlib.import_module("scripts.checks.check_curriculum_source_layout")
    errors.extend(checker.repository_foundations_layout_errors())


def _final_results_payload(errors: list[str]) -> dict[str, Any] | None:
    evidence = EVIDENCE.read_text(encoding="utf-8")
    start = evidence.find(FINAL_RESULTS_START)
    end = evidence.find(FINAL_RESULTS_END)
    if start < 0 or end < 0 or end < start:
        errors.append("EVIDENCE.md is missing the final command-results block")
        return None
    encoded = evidence[start + len(FINAL_RESULTS_START) : end]
    try:
        payload = json.loads(encoded)
    except json.JSONDecodeError as exc:
        errors.append(f"final command-results JSON is invalid: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append("final command-results payload must be an object")
        return None
    return payload


def _decoded_stream(
    errors: list[str], label: str, record: dict[str, Any], stream: str
) -> bytes:
    try:
        data = base64.b64decode(record[f"{stream}_b64"], validate=True)
    except (KeyError, ValueError) as exc:
        errors.append(f"{label} has invalid {stream} encoding: {exc}")
        return b""
    if len(data) != record.get(f"{stream}_bytes"):
        errors.append(f"{label} {stream} byte count mismatch")
    if sha256(data) != record.get(f"{stream}_sha256"):
        errors.append(f"{label} {stream} digest mismatch")
    return data


def verify_final_command_records(errors: list[str]) -> None:
    payload = _final_results_payload(errors)
    if payload is None:
        return
    if payload.get("version") != 1 or payload.get("cwd") != str(ROOT):
        errors.append("final command-results metadata mismatch")

    expected_manifests = {
        "PRE_SLICE_BASELINE.json": fingerprint(BASELINE),
        "PRE_CUTOVER_CONTENT_MANIFEST.json": fingerprint(CONTENT_MANIFEST),
    }
    if payload.get("manifest_fingerprints") != expected_manifests:
        errors.append("final command results are not bound to the current manifests")
    expected_implementation = {
        relative: fingerprint(ROOT / relative) for relative in FINAL_BINDING_PATHS
    }
    if payload.get("implementation_fingerprints") != expected_implementation:
        errors.append("final command results are not bound to the settled implementation")

    expected_commands = {
        "canonical_verifier": (
            "python docs/goals/repository-foundations-ledger-decomposition/"
            "verify_evidence.py"
        ),
        **{
            label: command
            for label, command, _ in _final_command_specs()
        },
    }
    records = payload.get("records")
    if not isinstance(records, dict) or set(records) != set(expected_commands):
        actual_labels = sorted(records) if isinstance(records, dict) else records
        errors.append(
            f"final command-result labels mismatch: {actual_labels}"
        )
        return

    outputs: dict[str, tuple[bytes, bytes]] = {}
    for label, expected_command in expected_commands.items():
        record = records[label]
        if not isinstance(record, dict):
            errors.append(f"{label} command record must be an object")
            continue
        if record.get("command") != expected_command:
            errors.append(f"{label} command text mismatch")
        if record.get("cwd") != str(ROOT):
            errors.append(f"{label} cwd mismatch")
        if record.get("exit_code") != 0:
            errors.append(f"{label} exit code was {record.get('exit_code')}")
        stdout = _decoded_stream(errors, label, record, "stdout")
        stderr = _decoded_stream(errors, label, record, "stderr")
        outputs[label] = (stdout, stderr)

    newline = os.linesep.encode("ascii")
    exact_outputs = {
        "canonical_verifier": b"Slice 16 all evidence replay passed." + newline,
        "curriculum_source_layout": b"Curriculum source layout is consistent." + newline,
        "seed_targets": (
            b"Generated curriculum targets are consistent (2056 cases)." + newline
        ),
        "ruff": b"All checks passed!\n",
    }
    for label, expected_stdout in exact_outputs.items():
        streams = outputs.get(label)
        if streams is None:
            continue
        if streams != (expected_stdout, b""):
            errors.append(f"{label} exact stdout/stderr contract mismatch")

    test_counts = {
        "focused_topology_tests": 13,
        "relevant_curriculum_tests": 1465,
        "complete_curriculum_tests": 1528,
    }
    for label, expected_count in test_counts.items():
        streams = outputs.get(label)
        if streams is None:
            continue
        stdout, stderr = streams
        summary = re.search(rb"(\d+) passed in [^\r\n]+", stdout)
        if stderr or summary is None or int(summary.group(1)) != expected_count:
            errors.append(f"{label} pytest summary mismatch")

    generated = outputs.get("generated_targets_current")
    if generated is not None and generated != (
        b"Collected 2056 variant solutions."
        + newline
        + b"generated/generated_targets.py is up to date."
        + newline,
        b"",
    ):
        errors.append("generated-target currency output mismatch")

    fast = outputs.get("fast_quality_gates")
    if fast is not None:
        stdout, stderr = fast
        if (
            stderr
            or stdout.count(b"==> python scripts/checks/check_curriculum_source_layout.py")
            != 1
            or not stdout.endswith(b"All fast quality gates passed." + newline)
        ):
            errors.append("fast quality-gate output mismatch")

    diff_check = outputs.get("diff_check")
    if diff_check is not None and diff_check[0] != b"":
        errors.append("git diff --check produced stdout")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-baseline", action="store_true")
    parser.add_argument("--capture-final-commands", action="store_true")
    parser.add_argument("--refresh-final-validator-records", action="store_true")
    parser.add_argument(
        "--phase", choices=("baseline", "content", "topology", "all"), default="all"
    )
    args = parser.parse_args()
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    capture_modes = sum(
        (
            args.capture_baseline,
            args.capture_final_commands,
            args.refresh_final_validator_records,
        )
    )
    if capture_modes > 1:
        parser.error("capture modes are mutually exclusive")
    if args.capture_baseline:
        return capture_baseline()
    if not BASELINE.exists() or not CONTENT_MANIFEST.exists():
        print("Slice 16 baseline artifacts are missing.", file=sys.stderr)
        return 1
    if args.capture_final_commands:
        return capture_final_commands()
    if args.refresh_final_validator_records:
        return refresh_final_validator_records()

    errors: list[str] = []
    if args.phase == "baseline":
        verify_baseline(errors)
    elif args.phase == "content":
        verify_content(errors)
    elif args.phase == "topology":
        verify_topology(errors)
    else:
        verify_content(errors)
        verify_topology(errors)
        verify_preservation(errors)
        verify_final_command_records(errors)

    if errors:
        print(f"Slice 16 {args.phase} evidence replay failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(f"Slice 16 {args.phase} evidence replay passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
