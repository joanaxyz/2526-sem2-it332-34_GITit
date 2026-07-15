#!/usr/bin/env python3
"""Verify CI and package scripts keep the architecture guards wired.

This is a meta-guard: it does not replace the individual checks. It prevents a
future cleanup from accidentally removing a guard from CI/package scripts while
leaving the guard file in the repository.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI_FILE = ROOT / ".github" / "workflows" / "ci.yml"
FRONTEND_PACKAGE = ROOT / "frontend" / "package.json"

REQUIRED_CI_SNIPPETS = {
    "legacy vocabulary guard": "python ../scripts/check_legacy_terms.py",
    "architecture boundary guard": "python ../scripts/check_architecture_boundaries.py",
    "css architecture guard": "python ../scripts/check_css_architecture.py",
    "ui typography guard": "python ../scripts/check_ui_typography.py",
    "seed target guard": "python ../scripts/check_seed_targets.py",
    "generated target replay guard": "python scripts/check_generated_targets_current.py",
    "api contract guard": "python ../scripts/check_api_contract.py",
    "frontend api usage guard": "python ../scripts/check_frontend_api_usage.py",
    "api type adoption guard": "python ../scripts/check_api_type_adoption.py",
    "documentation currentness guard": "python ../scripts/check_documentation_current.py",
    "ci quality gate manifest": "python ../scripts/check_ci_quality_gates.py",
    "repository artifact guard": "python scripts/check_repository_artifacts.py",
    "django deploy check": "python ../scripts/check_django_deploy.py",
    "backend ruff": "ruff check .",
    "repository script ruff": "ruff check scripts",
    "migration drift check": "python manage.py makemigrations --check --dry-run",
    "clean migration apply": "python manage.py migrate --noinput",
    "postgres and redis integration job": "production-integration:",
    "backend pytest": "pytest -q --cov=. --cov-report=term-missing --cov-report=xml",
    "generated target backend install": "pip install -r backend/requirements-dev.txt",
    "generated target frontend install": "npm ci",
    "python dependency audit": "pip-audit -r backend/requirements.txt",
    "frontend dependency audit": "npm audit --audit-level=high",
    "frontend lint": "npm run lint",
    "frontend dead-code scan": "npm run lint:dead",
    "frontend tests": "npm test",
    "frontend build": "npm run build",
}

REQUIRED_FRONTEND_SCRIPTS = {
    "api:check": "python ../scripts/check_api_contract.py",
    "ui:typography-check": "python ../scripts/check_ui_typography.py",
    "api:usage-check": "python ../scripts/check_frontend_api_usage.py",
    "api:type-adoption-check": "python ../scripts/check_api_type_adoption.py",
    "targets:check": "python ../scripts/check_seed_targets.py",
    "targets:replay-check": "python ../scripts/check_generated_targets_current.py",
    "docs:check": "python ../scripts/check_documentation_current.py",
    "ci:manifest-check": "python ../scripts/check_ci_quality_gates.py",
    "deploy:check": "python ../scripts/check_django_deploy.py",
    "artifacts:check": "python ../scripts/check_repository_artifacts.py",
    "artifacts:clean": "python ../scripts/clean_repository_artifacts.py",
}


def main() -> int:
    errors: list[str] = []

    ci_text = CI_FILE.read_text(encoding="utf-8") if CI_FILE.exists() else ""
    if not ci_text:
        errors.append("Missing .github/workflows/ci.yml")
    for label, snippet in REQUIRED_CI_SNIPPETS.items():
        if snippet not in ci_text:
            errors.append(f"CI is missing {label}: {snippet}")

    try:
        package = json.loads(FRONTEND_PACKAGE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append("Missing frontend/package.json")
        package = {}
    scripts = package.get("scripts", {}) if isinstance(package, dict) else {}
    for name, expected in REQUIRED_FRONTEND_SCRIPTS.items():
        actual = scripts.get(name)
        if actual != expected:
            errors.append(
                f"frontend/package.json script {name!r} must be {expected!r}; found {actual!r}"
            )

    if errors:
        print("CI quality gate manifest failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CI quality gate manifest is complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
