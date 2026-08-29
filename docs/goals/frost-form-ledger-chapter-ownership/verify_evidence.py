#!/usr/bin/env python3
"""Verify Frost catalog identity, topology, and dirty-worktree preservation."""

from __future__ import annotations

import base64
import dataclasses
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
GOAL_DIR = Path(__file__).resolve().parent
CONTENT_BASELINE_PATH = GOAL_DIR / "PRE_SLICE_BASELINE.json"
PROTECTED_BASELINE_PATH = GOAL_DIR / "PROTECTED_BASELINE.json"
EXPECTED_CONTENT_BASELINE_SHA256 = (
    "C5A070DB75CB9E23A980DC898AD83328AFC5CF33C5716A5C2779C3FB0F9C60D2"
)
EXPECTED_PROTECTED_BASELINE_SHA256 = (
    "361DED99A124ED426E06C1D228929870797D9478DCFDE6F44A652E4295730997"
)

FROST_PACKAGE_NAME = (
    "curriculum.seed_data.source.adventure_level_specs.v3_frost_form_drills"
)
SOURCE_LIST_MODULES = {
    "choose": "choose_the_integration",
    "deliver": "deliver_the_release",
    "govern": "govern_the_remote",
    "hunt": "hunt_the_regression",
    "move": "move_the_patch",
    "publish": "publish_the_core",
    "reforge": "reforge_the_branch",
    "survive": "survive_the_conflict",
    "temper": "temper_the_commit",
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _json_default(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(type(value).__name__)


def _catalog_fingerprint(value: list[Any]) -> dict[str, int | str]:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    ).encode("utf-8")
    return {
        "bytes": len(payload),
        "items": len(value),
        "sha256": _sha256_bytes(payload),
    }


def _git_statuses() -> dict[str, str]:
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
    )
    parts = raw.decode("utf-8", errors="surrogateescape").split("\0")
    statuses: dict[str, str] = {}
    index = 0
    while index < len(parts) and parts[index]:
        item = parts[index]
        status = item[:2]
        path = item[3:].replace("\\", "/")
        index += 1
        if "R" in status or "C" in status:
            if index >= len(parts):
                raise RuntimeError("Git status ended inside a rename/copy record")
            source = parts[index].replace("\\", "/")
            index += 1
            path = f"{path} <- {source}"
        statuses[path] = status
    return statuses


def _path_state(path: str, statuses: dict[str, str]) -> list[Any]:
    target = ROOT / path.split(" <- ", 1)[0]
    exists = target.is_file()
    return [
        statuses.get(path, "  "),
        exists,
        target.stat().st_size if exists else None,
        _sha256_bytes(target.read_bytes()) if exists else None,
    ]


def _outside_allowlist_state(
    protected: dict[str, Any], statuses: dict[str, str]
) -> dict[str, list[Any]]:
    allowed_files = set(protected["allowed_files"])
    allowed_prefixes = tuple(protected["allowed_prefixes"])
    return {
        path: _path_state(path, statuses)
        for path in sorted(statuses)
        if path not in allowed_files
        and not any(path.startswith(prefix) for prefix in allowed_prefixes)
    }


def _mapping_differences(
    label: str,
    expected: dict[str, Any],
    actual: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    for key in sorted(expected.keys() | actual.keys()):
        if key not in actual:
            errors.append(f"{label} missing current key: {key}")
        elif key not in expected:
            errors.append(f"{label} has unexpected current key: {key}")
        elif actual[key] != expected[key]:
            errors.append(
                f"{label} mismatch for {key}: expected={expected[key]!r}, "
                f"actual={actual[key]!r}"
            )
    return errors


def _content_errors(content: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    frost_package = importlib.import_module(FROST_PACKAGE_NAME)
    adventure_specs = importlib.import_module(
        "curriculum.seed_data.source.adventure_level_specs"
    )
    form_challenges = importlib.import_module(
        "curriculum.seed_data.source.challenge_specs.v3_chapter_form_challenges"
    )

    source_lists: dict[str, dict[str, int | str]] = {}
    for prefix, module_name in SOURCE_LIST_MODULES.items():
        module = importlib.import_module(f"{FROST_PACKAGE_NAME}.{module_name}")
        for binding in ("DRILLS", "WORKFLOWS"):
            source_lists[f"{prefix}_{binding.lower()}"] = _catalog_fingerprint(
                getattr(module, binding)
            )
    errors.extend(
        _mapping_differences(
            "Frost source-list fingerprint",
            content["source_lists"],
            source_lists,
        )
    )

    catalogs = {
        "adventure_levels": _catalog_fingerprint(adventure_specs.ADVENTURE_LEVELS),
        "frost_levels": _catalog_fingerprint(frost_package.LEVELS),
        "v3_form_challenges": _catalog_fingerprint(
            form_challenges.V3_FORM_CHALLENGES
        ),
    }
    errors.extend(
        _mapping_differences(
            "Frost composed-catalog fingerprint",
            content["catalogs"],
            catalogs,
        )
    )

    generated_path = ROOT / "backend/curriculum/seed_data/generated/generated_targets.py"
    expected_generated = content["files"][
        "backend/curriculum/seed_data/generated/generated_targets.py"
    ]["sha256"]
    actual_generated = _sha256_bytes(generated_path.read_bytes())
    if actual_generated != expected_generated:
        errors.append(
            "generated target hash mismatch: "
            f"expected={expected_generated}, actual={actual_generated}"
        )
    return errors


def _protection_errors(protected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    statuses = _git_statuses()
    actual_protected = {
        path: _path_state(path, statuses) for path in protected["protected_files"]
    }
    errors.extend(
        _mapping_differences(
            "protected-file state",
            protected["protected_files"],
            actual_protected,
        )
    )

    compressed = base64.b64decode(protected["outside_allowlist_gzip_base64"])
    baseline_bytes = gzip.decompress(compressed)
    if len(baseline_bytes) != protected["outside_allowlist_json_bytes"]:
        errors.append("outside-allowlist baseline byte count is corrupt")
    if _sha256_bytes(baseline_bytes) != protected["outside_allowlist_sha256"]:
        errors.append("outside-allowlist baseline hash is corrupt")
    expected_outside = json.loads(baseline_bytes)
    if len(expected_outside) != protected["outside_allowlist_entries"]:
        errors.append("outside-allowlist baseline entry count is corrupt")
    actual_outside = _outside_allowlist_state(protected, statuses)
    errors.extend(
        _mapping_differences(
            "outside-allowlist state",
            expected_outside,
            actual_outside,
        )
    )

    allowed_files = set(protected["allowed_files"])
    allowed_prefixes = tuple(protected["allowed_prefixes"])
    for path, status in sorted(statuses.items()):
        is_slice_path = path in allowed_files or any(
            path.startswith(prefix) for prefix in allowed_prefixes
        )
        if is_slice_path and status != "??" and status[0] != " ":
            errors.append(f"slice path is staged: {path} ({status})")
    return errors


def _topology_errors() -> list[str]:
    checker = importlib.import_module("scripts.checks.check_curriculum_source_layout")
    return [
        f"Frost topology: {error}"
        for error in checker.frost_form_drill_layout_errors()
    ]


def main() -> int:
    sys.path.insert(0, str(ROOT / "backend"))
    sys.path.insert(0, str(ROOT))
    content_bytes = CONTENT_BASELINE_PATH.read_bytes()
    protected_bytes = PROTECTED_BASELINE_PATH.read_bytes()
    baseline_errors = []
    if _sha256_bytes(content_bytes) != EXPECTED_CONTENT_BASELINE_SHA256:
        baseline_errors.append("PRE_SLICE_BASELINE.json raw hash drifted")
    if _sha256_bytes(protected_bytes) != EXPECTED_PROTECTED_BASELINE_SHA256:
        baseline_errors.append("PROTECTED_BASELINE.json raw hash drifted")
    if baseline_errors:
        print("Frost evidence verification failed:", file=sys.stderr)
        for error in baseline_errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    content = json.loads(content_bytes)
    protected = json.loads(protected_bytes)

    monolith_key = (
        "backend/curriculum/seed_data/source/adventure_level_specs/"
        "v3_frost_form_drills.py"
    )
    if (
        protected["planned_existing"][monolith_key][3]
        != content["files"][monolith_key]["sha256"]
    ):
        print("Frost evidence verification failed:", file=sys.stderr)
        print("  content/protection baselines disagree on the monolith", file=sys.stderr)
        return 1

    errors = [
        *_content_errors(content),
        *_protection_errors(protected),
        *_topology_errors(),
    ]
    if errors:
        print("Frost evidence verification failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("Frost form ledger evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
