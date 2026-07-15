#!/usr/bin/env python3
"""Run all fast repository quality gates from one command.

This intentionally excludes the full generated-target replay check, backend test
suite, and frontend build because those require installed project dependencies
and can be slower. CI still runs those separately.
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAST_GATES = [
    "check_legacy_terms.py",
    "check_architecture_boundaries.py",
    "check_css_architecture.py",
    "check_seed_targets.py",
    "check_api_contract.py",
    "check_frontend_api_usage.py",
    "check_api_type_adoption.py",
    "check_documentation_current.py",
    "check_ci_quality_gates.py",
    "check_repository_artifacts.py",
]


def run(script: str) -> int:
    print(f"\n==> python scripts/{script}", flush=True)
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    sys.dont_write_bytecode = True
    previous_cwd = Path.cwd()
    try:
        os.chdir(ROOT)
        runpy.run_path(str(ROOT / "scripts" / script), run_name="__main__")
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        return code
    finally:
        os.chdir(previous_cwd)
    return 0


def main() -> int:
    failures = [script for script in FAST_GATES if run(script) != 0]
    if failures:
        print("\nQuality gates failed:")
        for script in failures:
            print(f"- scripts/{script}")
        return 1
    print("\nAll fast quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
