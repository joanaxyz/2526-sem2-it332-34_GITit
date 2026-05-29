import os
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent


def _normalize_database_url(url: str) -> str:
    """Django expects postgresql://, not JDBC-style jdbc:postgresql:// URLs."""
    if url.startswith("jdbc:"):
        return url.removeprefix("jdbc:")
    return url


def _clean_env_list(values: list[str]) -> list[str]:
    return [value.strip() for value in values if value.strip()]


env = environ.Env(
    DJANGO_DEBUG=(bool, True),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DJANGO_CORS_ALLOWED_ORIGINS=(list, ["http://localhost:5173", "http://127.0.0.1:5173"]),
    PERFORMANCE_TIMING_ENABLED=(bool, False),
    JWT_COOKIE_SECURE=(bool, False),
    SECURE_SSL_REDIRECT=(bool, False),
)
_os_database_url_before_read_env = os.environ.get("DATABASE_URL")
env.read_env(BASE_DIR / ".env")
# A system-level JDBC URL (common when copied from desktop DB tools) overrides
# backend/.env and often points at the wrong pooler/port. Prefer project .env.
if (_os_database_url_before_read_env or "").startswith("jdbc:"):
    env.read_env(BASE_DIR / ".env", overwrite=True)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-only-change-me")
DEBUG = env("DJANGO_DEBUG")
PERFORMANCE_TIMING_ENABLED = env("PERFORMANCE_TIMING_ENABLED", default=DEBUG)
ALLOWED_HOSTS = _clean_env_list(env("DJANGO_ALLOWED_HOSTS"))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "accounts",
    "learning",
    "scenarios",
    "simulator",
    "evaluation",
    "scaffolding",
    "retries",
    "progress",
    "review",
    "common",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

_database_url = _normalize_database_url(
    env("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
)
DATABASES = {
    "default": env.db_url_config(_database_url),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DATABASE_CONN_MAX_AGE", default=0)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = env.bool("DATABASE_CONN_HEALTH_CHECKS", default=False)
if "sqlite3" in DATABASES["default"].get("ENGINE", ""):
    from django.db.backends.signals import connection_created

    def _enable_sqlite_wal(sender, connection, **kwargs):
        if connection.vendor == "sqlite":
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA journal_mode=WAL;")

    connection_created.connect(_enable_sqlite_wal, dispatch_uid="git_it.sqlite_wal")
if "postgresql" in DATABASES["default"].get("ENGINE", ""):
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = env.bool(
        "DATABASE_DISABLE_SERVER_SIDE_CURSORS",
        default=True,
    )
    if env.bool("DATABASE_DISABLE_PREPARED_STATEMENTS", default=True):
        DATABASES["default"].setdefault("OPTIONS", {})["prepare_threshold"] = None
    DATABASES["default"].setdefault("OPTIONS", {})["options"] = "-c idle_in_transaction_session_timeout=5000"

REDIS_URL = env("REDIS_URL", default="")
# Refresh-token revocation is stored in the configured Django cache. The
# process-local fallback is useful for development, but production needs a
# shared cache so logout and rotated-token revocation apply across workers.
if not DEBUG and not REDIS_URL:
    raise RuntimeError("REDIS_URL is required in production for shared token revocation cache.")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "git-it-dev-cache",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = _clean_env_list(env("DJANGO_CORS_ALLOWED_ORIGINS"))
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")
SESSION_COOKIE_SECURE = env("JWT_COOKIE_SECURE")
CSRF_COOKIE_SECURE = env("JWT_COOKIE_SECURE")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

GIT_IT_REFRESH_COOKIE = "git_it_refresh"
GIT_IT_REFRESH_COOKIE_SECURE = env("JWT_COOKIE_SECURE")

SPECTACULAR_SETTINGS = {
    "TITLE": "GIT it! API",
    "DESCRIPTION": "Student-facing Git scenario practice API.",
    "VERSION": "0.1.0",
}
