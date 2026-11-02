#!/usr/bin/env python3
"""Replay the Slice 15 structure, behavior, CLI, and preservation evidence."""

from __future__ import annotations

import ast
import base64
import contextlib
import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[3]
GOAL_DIR = Path(__file__).resolve().parent
SYMBOL_MANIFEST = GOAL_DIR / "PRE_CUTOVER_SYMBOL_MANIFEST.json"
TEST_MANIFEST = GOAL_DIR / "PRE_CUTOVER_TEST_MANIFEST.json"
BASELINE = GOAL_DIR / "PRE_SLICE_BASELINE.json"

POLICY_PATHS = {
    "gameplay": ROOT / "scripts/checks/architecture_guard/contracts/gameplay.py",
    "response": ROOT
    / "scripts/checks/architecture_guard/contracts/gameplay_response.py",
    "frontend": ROOT
    / "scripts/checks/architecture_guard/contracts/gameplay_response_frontend.py",
}
TEST_PATHS = (
    ROOT / "backend/common/tests/architecture_guard/test_gameplay_policy.py",
    ROOT
    / "backend/common/tests/architecture_guard/test_gameplay_response_policy.py",
)

FRONTEND_BASELINE_SYMBOLS = {
    "GAMEPLAY_ADVENTURE_TYPES",
    "GAMEPLAY_CHALLENGE_ENTRY_API",
    "GAMEPLAY_CHALLENGE_TYPES",
    "_typescript_alias_source",
    "_typescript_api_binding_mutation_pattern",
    "_typescript_balanced_call_end",
    "_typescript_exported_object_body",
    "_typescript_is_exact_operation_return",
    "_typescript_local_api_bindings",
    "_typescript_object_method_bodies",
    "_typescript_omit_overlay_fields",
    "_typescript_omit_signature",
    "_typescript_top_level_object_members",
    "_typescript_unsafe_api_object_members",
    "gameplay_response_frontend_violations",
}
RESPONSE_BASELINE_SYMBOLS = {
    "GAMEPLAY_ADVENTURE_OPENAPI",
    "GAMEPLAY_CHALLENGE_OPENAPI",
    "GAMEPLAY_COMMON_OPENAPI",
    "_response_schema_fields",
    "check_gameplay_response_contract_ownership",
    "gameplay_response_backend_violations",
    "gameplay_response_openapi_violations",
}
TRACE_SYMBOLS = (
    "gameplay_mutation_backend_violations",
    "gameplay_mutation_frontend_violations",
    "gameplay_mutation_openapi_violations",
    "gameplay_response_backend_violations",
    "gameplay_response_frontend_violations",
    "gameplay_response_openapi_violations",
    "check_gameplay_mutation_contract_ownership",
    "check_gameplay_response_contract_ownership",
)


class NameNormalizer(ast.NodeTransformer):
    def __init__(self, name_map: dict[str, str]) -> None:
        self.name_map = name_map

    def visit_Name(self, node: ast.Name) -> ast.Name:
        replacement = self.name_map.get(node.id)
        if replacement is None:
            return node
        return ast.copy_location(ast.Name(id=replacement, ctx=node.ctx), node)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def stable(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            "__dict__": [
                [stable(key), stable(item)]
                for key, item in sorted(value.items(), key=lambda row: repr(row[0]))
            ]
        }
    if isinstance(value, set):
        items = [stable(item) for item in value]
        return {
            "__set__": sorted(
                items,
                key=lambda item: json.dumps(
                    item, sort_keys=True, ensure_ascii=False
                ),
            )
        }
    if isinstance(value, tuple):
        return {"__tuple__": [stable(item) for item in value]}
    if isinstance(value, list):
        return [stable(item) for item in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"unsupported manifest value: {type(value).__name__}")


def normalized_ast_sha256(node: ast.AST, name_map: dict[str, str] | None = None) -> str:
    normalized = copy.deepcopy(node)
    if name_map:
        normalized = NameNormalizer(name_map).visit(normalized)
        ast.fix_missing_locations(normalized)
    dump = ast.dump(normalized, annotate_fields=True, include_attributes=False)
    return sha256(dump.encode("utf-8"))


def load_module(label: str, path: Path):
    spec = importlib.util.spec_from_file_location(label, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def top_level_definitions(tree: ast.Module) -> list[tuple[str, ast.AST]]:
    definitions: list[tuple[str, ast.AST]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions.append((node.name, node))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    definitions.append((target.id, node))
    return definitions


def imported_module_targets(tree: ast.Module) -> list[str]:
    targets: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.extend(item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module:
                targets.append(module)
            targets.extend(
                f"{module}.{item.name}" if module else item.name
                for item in node.names
            )
    return targets


def verify_symbol_manifest(errors: list[str]) -> None:
    manifest = json.loads(SYMBOL_MANIFEST.read_text(encoding="utf-8"))
    name_map = manifest["fixed_response_name_map"]
    trees = {
        owner: ast.parse(path.read_text(encoding="utf-8"))
        for owner, path in POLICY_PATHS.items()
    }
    definitions: dict[str, list[tuple[str, ast.AST]]] = {}
    for owner, tree in trees.items():
        for name, node in top_level_definitions(tree):
            definitions.setdefault(name, []).append((owner, node))
    expected_definition_names = set(manifest["symbols"]) | set(name_map)
    actual_definition_names = set(definitions)
    if actual_definition_names != expected_definition_names:
        errors.append(
            "policy definition set mismatch: "
            f"missing={sorted(expected_definition_names - actual_definition_names)}, "
            f"extra={sorted(actual_definition_names - expected_definition_names)}"
        )

    modules = {
        "gameplay": importlib.import_module(
            "scripts.checks.architecture_guard.contracts.gameplay"
        ),
        "response": importlib.import_module(
            "scripts.checks.architecture_guard.contracts.gameplay_response"
        ),
        "frontend": importlib.import_module(
            "scripts.checks.architecture_guard.contracts.gameplay_response_frontend"
        ),
    }
    normalized_functions = set(manifest["name_normalized_response_functions"])
    for name, expected in manifest["symbols"].items():
        expected_owner = (
            "frontend"
            if name in FRONTEND_BASELINE_SYMBOLS
            else "response"
            if name in RESPONSE_BASELINE_SYMBOLS
            else "gameplay"
        )
        hits = definitions.get(name, [])
        if len(hits) != 1 or hits[0][0] != expected_owner:
            errors.append(
                f"symbol owner mismatch for {name}: "
                f"{[(owner, type(node).__name__) for owner, node in hits]}"
            )
            continue
        if expected["kind"] == "function":
            actual = normalized_ast_sha256(
                hits[0][1], name_map if name in normalized_functions else None
            )
            if actual != expected["normalized_ast_sha256"]:
                errors.append(f"function AST mismatch for {name}")
        else:
            actual_value = stable(getattr(modules[expected_owner], name))
            if actual_value != expected["resolved_value"]:
                errors.append(f"constant value mismatch for {name}")

    for response_name, historical_name in name_map.items():
        response_owner = (
            "response"
            if response_name
            in {
                "GAMEPLAY_RESPONSE_BACKEND_VIEWS",
                "GAMEPLAY_RESPONSE_GENERATED_OPENAPI",
            }
            else "frontend"
        )
        hits = definitions.get(response_name, [])
        if len(hits) != 1 or hits[0][0] != response_owner:
            errors.append(
                f"response-scoped owner mismatch for {response_name}: "
                f"{[(owner, type(node).__name__) for owner, node in hits]}"
            )
        if getattr(modules[response_owner], response_name) != getattr(
            modules["gameplay"], historical_name
        ):
            errors.append(f"response-scoped value mismatch for {response_name}")

    response_imports = [
        target
        for owner in ("response", "frontend")
        for target in imported_module_targets(trees[owner])
    ]
    if any(module.rsplit(".", 1)[-1] == "gameplay" for module in response_imports):
        errors.append("response policy imports the mutation policy")
    frontend_imports = imported_module_targets(trees["frontend"])
    if any(
        module.rsplit(".", 1)[-1] == "gameplay_response"
        for module in frontend_imports
    ):
        errors.append("frontend response analysis imports its orchestrator")
    gameplay_imports = imported_module_targets(trees["gameplay"])
    if any(
        module_name.rsplit(".", 1)[-1]
        in {"gameplay_response", "gameplay_response_frontend"}
        for module_name in gameplay_imports
    ):
        errors.append("mutation policy imports or re-exports a response policy")

    function_owners: dict[str, list[str]] = {}
    for owner, tree in trees.items():
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_owners.setdefault(node.name, []).append(owner)
    duplicates = {
        name: owners for name, owners in function_owners.items() if len(owners) != 1
    }
    if duplicates:
        errors.append(f"duplicate policy functions: {duplicates}")
    if any(
        "response" in name.lower()
        for name, _ in top_level_definitions(trees["gameplay"])
    ):
        errors.append("response definition remains in gameplay.py")
    for owner, path in POLICY_PATHS.items():
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count >= 900:
            errors.append(f"oversized policy module {owner}: {line_count}")


def test_definitions() -> dict[str, tuple[Path, ast.FunctionDef | ast.AsyncFunctionDef]]:
    definitions: dict[str, tuple[Path, ast.FunctionDef | ast.AsyncFunctionDef]] = {}
    for path in TEST_PATHS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                if node.name in definitions:
                    raise RuntimeError(f"duplicate test definition: {node.name}")
                definitions[node.name] = (path, node)
    return definitions


def verify_test_manifest(errors: list[str]) -> None:
    manifest = json.loads(TEST_MANIFEST.read_text(encoding="utf-8"))
    name_map = json.loads(SYMBOL_MANIFEST.read_text(encoding="utf-8"))[
        "fixed_response_name_map"
    ]
    current = test_definitions()
    for name, expected in manifest["tests"].items():
        hit = current.get(name)
        if hit is None:
            errors.append(f"missing test {name}")
            continue
        _, node = hit
        normalization = name_map if name.startswith("test_gameplay_response_") else None
        if (
            normalized_ast_sha256(node, normalization)
            != expected["normalized_ast_sha256"]
        ):
            errors.append(f"test AST mismatch for {name}")
        assertion_count = sum(
            isinstance(child, ast.Assert) for child in ast.walk(node)
        )
        if assertion_count != expected["assertion_count"]:
            errors.append(f"assertion-count mismatch for {name}")

    response_tree = ast.parse(TEST_PATHS[1].read_text(encoding="utf-8"))
    obsolete_aliases = {
        "GAMEPLAY_BACKEND_VIEWS",
        "GAMEPLAY_FRONTEND_APIS",
        "GAMEPLAY_GENERATED_OPENAPI",
        "GAMEPLAY_SHARED_COMMAND_TYPES",
    }
    for node in ast.walk(response_tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        for item in node.names:
            if item.asname in obsolete_aliases:
                errors.append(f"obsolete response-test alias remains: {item.asname}")


def replay_ordered_trace(errors: list[str]) -> None:
    manifest = json.loads(TEST_MANIFEST.read_text(encoding="utf-8"))
    modules = [
        load_module(f"_slice15_verify_test_{index}", path)
        for index, path in enumerate(TEST_PATHS)
    ]
    actual_rows: list[dict[str, Any]] = []
    for test_name in manifest["tests"]:
        module = next(candidate for candidate in modules if hasattr(candidate, test_name))
        originals = {
            name: getattr(module, name)
            for name in TRACE_SYMBOLS
            if hasattr(module, name)
        }
        call_index = [0]

        def make_wrapper(symbol_name: str, original):
            def wrapper(*args, **kwargs):
                result = original(*args, **kwargs)
                actual_rows.append(
                    {
                        "test": test_name,
                        "call_index": call_index[0],
                        "symbol": symbol_name,
                        "ordered_result": result,
                    }
                )
                call_index[0] += 1
                return result

            return wrapper

        for symbol_name, original in originals.items():
            setattr(module, symbol_name, make_wrapper(symbol_name, original))
        try:
            getattr(module, test_name)()
        finally:
            for symbol_name, original in originals.items():
                setattr(module, symbol_name, original)

    def keyed(rows: list[dict[str, Any]]) -> dict[tuple[str, int, str], list[str]]:
        return {
            (row["test"], row["call_index"], row["symbol"]): row[
                "ordered_result"
            ]
            for row in rows
        }

    if keyed(actual_rows) != keyed(manifest["ordered_call_trace"]):
        errors.append("ordered 75-call policy trace does not match the baseline")


def verify_preservation(errors: list[str]) -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    for relative, expected in baseline["strict_visible_files"].items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing strict file: {relative}")
            continue
        data = path.read_bytes()
        if len(data) != expected["bytes"] or sha256(data) != expected["sha256"]:
            errors.append(f"strict file drift: {relative}")
    for group in ("immutable_plan_artifacts", "generated_manifest_artifacts"):
        for relative, expected in baseline[group].items():
            data = (ROOT / relative).read_bytes()
            if len(data) != expected["bytes"] or sha256(data) != expected["sha256"]:
                errors.append(f"immutable artifact drift: {relative}")

    visible_output = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    visible = {
        relative
        for raw in visible_output.split(b"\0")
        if raw
        for relative in [raw.decode("utf-8", errors="surrogateescape").replace("\\", "/")]
        if (ROOT / relative).is_file()
    }
    allowed = (
        set(baseline["strict_visible_files"])
        | set(baseline["mutable_existing"])
        | set(baseline["approved_new"])
        | set(baseline["review_approved_new"])
    )
    for relative in sorted(visible - allowed):
        errors.append(f"unapproved repository-visible file: {relative}")

    orchestrator_path = ROOT / "scripts/checks/check_architecture_boundaries.py"
    orchestrator = orchestrator_path.read_text(encoding="utf-8")
    current_import = (
        "from scripts.checks.architecture_guard.contracts.gameplay import (  # noqa: E402\n"
        "    check_gameplay_mutation_contract_ownership,\n"
        ")\n"
        "from scripts.checks.architecture_guard.contracts.gameplay_response import (  # noqa: E402\n"
        "    check_gameplay_response_contract_ownership,\n"
        ")\n"
    )
    if orchestrator.count(current_import) != 1:
        errors.append("orchestrator cutover import is not unique")
    else:
        normalized = orchestrator.replace(
            current_import, baseline["orchestrator_import_preimage"]
        ).encode("utf-8")
        expected = baseline["mutable_fingerprints"][
            "scripts/checks/check_architecture_boundaries.py"
        ]
        if len(normalized) != expected["bytes"] or sha256(normalized) != expected[
            "sha256"
        ]:
            errors.append("orchestrator changed outside the approved import cutover")

    architecture_path = ROOT / "ARCHITECTURE.md"
    architecture = architecture_path.read_text(encoding="utf-8")
    bullets = [
        line
        for line in architecture.splitlines(keepends=True)
        if line.startswith("- `scripts/check_architecture_boundaries.py` preserves")
    ]
    if len(bullets) != 1:
        errors.append("architecture-guard documentation bullet is not unique")
    else:
        normalized = architecture.replace(
            bullets[0], baseline["architecture_guard_bullet_preimage"]
        ).encode("utf-8")
        expected = baseline["mutable_fingerprints"]["ARCHITECTURE.md"]
        if len(normalized) != expected["bytes"] or sha256(normalized) != expected[
            "sha256"
        ]:
            errors.append("ARCHITECTURE.md changed outside the approved bullet")

    tree = ast.parse(orchestrator)
    main = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    calls = [
        node.func.id
        for node in ast.walk(main)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id.startswith("check_")
    ]
    mutation_index = calls.index("check_gameplay_mutation_contract_ownership")
    response_index = calls.index("check_gameplay_response_contract_ownership")
    if response_index != mutation_index + 1:
        errors.append("Gameplay checker call order drifted")

    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    if staged:
        errors.append(f"staged files present: {staged.decode(errors='replace')}")


def run_cli(label: str, argv: list[str], cwd: Path) -> tuple[str, dict[str, Any]]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        argv,
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return label, {
        "exit_code": completed.returncode,
        "stdout_b64": base64.b64encode(completed.stdout).decode("ascii"),
        "stderr_b64": base64.b64encode(completed.stderr).decode("ascii"),
    }


def verify_cli(errors: list[str]) -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = (
            pool.submit(
                run_cli,
                "direct_checker",
                [sys.executable, "scripts/checks/check_architecture_boundaries.py"],
                ROOT,
            ),
            pool.submit(
                run_cli,
                "compatibility_wrapper",
                [sys.executable, "../scripts/check_architecture_boundaries.py"],
                ROOT / "frontend",
            ),
        )
        current = dict(future.result() for future in futures)
    for label, capture in current.items():
        expected = baseline["commands"][label]
        for key in ("exit_code", "stdout_b64", "stderr_b64"):
            if capture[key] != expected[key]:
                errors.append(f"{label} {key} differs from the live baseline")

    module = importlib.import_module("scripts.checks.check_architecture_boundaries")
    tree = ast.parse(
        (ROOT / "scripts/checks/check_architecture_boundaries.py").read_text(
            encoding="utf-8"
        )
    )
    main_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    called = []
    for node in ast.walk(main_node):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id.startswith("check_")
            and node.func.id not in called
        ):
            called.append(node.func.id)
    originals = {name: getattr(module, name) for name in called}
    try:
        for name in called:
            setattr(module, name, lambda: [])
        setattr(
            module,
            "check_gameplay_response_contract_ownership",
            lambda: ["controlled-first", "controlled-second"],
        )
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = module.main()
    finally:
        for name, original in originals.items():
            setattr(module, name, original)
    failure_output = stderr.getvalue()
    if not (
        exit_code == 1
        and stdout.getvalue() == ""
        and failure_output.count("controlled-first") == 1
        and failure_output.count("controlled-second") == 1
        and failure_output.index("controlled-first")
        < failure_output.index("controlled-second")
    ):
        errors.append("controlled CLI failure rendering drifted")


def main() -> int:
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    errors: list[str] = []
    verify_symbol_manifest(errors)
    verify_test_manifest(errors)
    replay_ordered_trace(errors)
    verify_preservation(errors)
    verify_cli(errors)
    if errors:
        print("Slice 15 evidence replay failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("symbol_manifest_replay PASS (38 symbols, 4 scoped-name normalizations)")
    print("test_manifest_replay PASS (11 tests, 58 assertions)")
    print("ordered_trace_replay PASS (75 calls)")
    print("cli_parity_replay PASS (direct, wrapper, controlled failure)")
    print("preservation_replay PASS (1808 strict files, 0 staged files)")
    print("Slice 15 evidence replay passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
