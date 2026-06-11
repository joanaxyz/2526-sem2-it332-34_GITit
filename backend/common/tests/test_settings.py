import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]


def run_settings_import(*, debug: str, redis_url: str):
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1",
            "DJANGO_CORS_ALLOWED_ORIGINS": "http://localhost:5173",
            "DJANGO_DEBUG": debug,
            "DJANGO_SECRET_KEY": "test-secret",
            "REDIS_URL": redis_url,
        }
    )
    return subprocess.run(
        [sys.executable, "-c", "import config.settings"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_production_settings_require_redis_url():
    result = run_settings_import(debug="False", redis_url="")

    assert result.returncode != 0
    assert "REDIS_URL is required in production for shared token revocation cache." in result.stderr


def test_development_settings_allow_locmem_without_redis():
    result = run_settings_import(debug="True", redis_url="")

    assert result.returncode == 0


def test_jdbc_database_url_is_normalized_to_postgresql():
    env = {
        "DATABASE_URL": "jdbc:postgresql://localhost:5432/git_it",
        "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1",
        "DJANGO_CORS_ALLOWED_ORIGINS": "http://localhost:5173",
        "DJANGO_DEBUG": "True",
        "DJANGO_SECRET_KEY": "test-secret",
        "REDIS_URL": "",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import config.settings as s; print(s.DATABASES['default']['ENGINE'])",
        ],
        cwd=BACKEND_DIR,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "postgresql" in result.stdout
