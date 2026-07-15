#!/usr/bin/env python3
"""Validate production settings and Django deployment security checks.

No external connection is opened here. The PostgreSQL/Redis integration job is
responsible for proving real dependency connectivity and migrations.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"

DEPLOY_ENV = {
    "DJANGO_DEBUG": "False",
    "DJANGO_SECRET_KEY": "ci-deploy-check-secret-key-change-before-production-12345",
    "DJANGO_ALLOWED_HOSTS": "example.com,localhost,127.0.0.1",
    "DJANGO_CORS_ALLOWED_ORIGINS": "https://example.com",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://example.com",
    "DATABASE_URL": "postgresql://ci:ci@localhost:5432/ci",
    "DATABASE_CONN_HEALTH_CHECKS": "True",
    "REDIS_URL": "redis://localhost:6379/15",
    "FRONTEND_BASE_URL": "https://example.com",
    "DJANGO_TRUST_PROXY_HEADERS": "True",
    "DJANGO_TRUSTED_PROXY_IPS": "127.0.0.1/32",
    "JWT_COOKIE_SECURE": "True",
    "SESSION_COOKIE_SECURE": "True",
    "CSRF_COOKIE_SECURE": "True",
    "SECURE_SSL_REDIRECT": "True",
    "SECURE_HSTS_SECONDS": "31536000",
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": "True",
    "SECURE_HSTS_PRELOAD": "True",
}


def run(*args: str, env: dict[str, str]) -> int:
    return subprocess.run(
        [sys.executable, "manage.py", *args],
        cwd=BACKEND,
        env=env,
        check=False,
    ).returncode


def main() -> int:
    env = {**os.environ, **DEPLOY_ENV}
    if run("check_runtime_config", env=env) != 0:
        return 1
    return run("check", "--deploy", "--tag", "security", "--fail-level", "WARNING", env=env)


if __name__ == "__main__":
    raise SystemExit(main())
