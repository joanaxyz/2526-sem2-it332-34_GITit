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
    # Safer default. Your local .env should explicitly set DJANGO_DEBUG=True.
    DJANGO_DEBUG=(bool, False),

    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_CORS_ALLOWED_ORIGINS=(list, []),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    CORS_ALLOW_CREDENTIALS=(bool, True),

    PERFORMANCE_TIMING_ENABLED=(bool, False),

    AUTH_LOGIN_MAX_ATTEMPTS=(int, 5),
    AUTH_LOGIN_LOCKOUT_SECONDS=(int, 300),

    JWT_ACCESS_TOKEN_LIFETIME_MINUTES=(int, 15),
    JWT_REFRESH_TOKEN_LIFETIME_DAYS=(int, 7),
    JWT_COOKIE_NAME=(str, "git_it_refresh"),
    JWT_COOKIE_PATH=(str, "/api/auth/"),
    JWT_COOKIE_DOMAIN=(str, ""),
    JWT_COOKIE_SAMESITE=(str, "Strict"),
    JWT_COOKIE_SECURE=(bool, False),

    SECURE_SSL_REDIRECT=(bool, False),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),

    API_VERSION=(str, "0.1.0"),
)

_os_database_url_before_read_env = os.environ.get("DATABASE_URL")
env.read_env(BASE_DIR / ".env")
# A system-level JDBC URL (common when copied from desktop DB tools) overrides
# backend/.env and often points at the wrong pooler/port. Prefer project .env.
if (_os_database_url_before_read_env or "").startswith("jdbc:"):
    env.read_env(BASE_DIR / ".env", overwrite=True)

DEBUG = env("DJANGO_DEBUG")

DEV_SECRET_KEY = "dev-local-change-before-production"

if DEBUG:
    SECRET_KEY = env("DJANGO_SECRET_KEY", default=DEV_SECRET_KEY)
else:
    SECRET_KEY = env("DJANGO_SECRET_KEY", default="").strip()

    if not SECRET_KEY or SECRET_KEY == DEV_SECRET_KEY:
        raise RuntimeError(
            "DJANGO_SECRET_KEY must be set to a unique secret when DJANGO_DEBUG=False."
        )
    
PERFORMANCE_TIMING_ENABLED = env("PERFORMANCE_TIMING_ENABLED", default=DEBUG)

ALLOWED_HOSTS = _clean_env_list(env("DJANGO_ALLOWED_HOSTS"))

if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

if not DEBUG and (not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS):
    raise RuntimeError("DJANGO_ALLOWED_HOSTS must be explicit when DJANGO_DEBUG=False.")

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
    "curriculum",
    "adventures",
    "challenges",
    "practice",
    "simulator",
    "evaluation",
    "progress",
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
# Persist DB connections for 60s by default so each command submit doesn't pay a
# fresh connect/handshake (notably costly against a remote Postgres pooler).
# Override with DATABASE_CONN_MAX_AGE=0 to restore close-after-request behavior.
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DATABASE_CONN_MAX_AGE", default=60)
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
    DATABASES["default"].setdefault("OPTIONS", {})["options"] = (
        "-c idle_in_transaction_session_timeout=5000"
    )

REDIS_URL = env("REDIS_URL", default="").strip()
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

if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

CORS_ALLOW_CREDENTIALS = env("CORS_ALLOW_CREDENTIALS")

CSRF_TRUSTED_ORIGINS = (
    _clean_env_list(env("DJANGO_CSRF_TRUSTED_ORIGINS"))
    or CORS_ALLOWED_ORIGINS
)

SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", default=env("JWT_COOKIE_SECURE"))
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", default=env("JWT_COOKIE_SECURE"))

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    # ScopedRateThrottle only limits views that declare a `throttle_scope`.
    # Anonymous scopes (register/refresh) key on client IP — classrooms share a
    # NAT IP, so those rates carry headroom for ~30 students behind one address.
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.ScopedRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {
        "auth_register": env("THROTTLE_AUTH_REGISTER", default="60/hour"),
        "auth_refresh": env("THROTTLE_AUTH_REFRESH", default="600/hour"),
        "command_submit": env("THROTTLE_COMMAND_SUBMIT", default="120/min"),
    },
}

JWT_ACCESS_TOKEN_LIFETIME_MINUTES = env("JWT_ACCESS_TOKEN_LIFETIME_MINUTES")
JWT_REFRESH_TOKEN_LIFETIME_DAYS = env("JWT_REFRESH_TOKEN_LIFETIME_DAYS")

if JWT_ACCESS_TOKEN_LIFETIME_MINUTES <= 0:
    raise RuntimeError("JWT_ACCESS_TOKEN_LIFETIME_MINUTES must be greater than 0.")

if JWT_REFRESH_TOKEN_LIFETIME_DAYS <= 0:
    raise RuntimeError("JWT_REFRESH_TOKEN_LIFETIME_DAYS must be greater than 0.")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=JWT_ACCESS_TOKEN_LIFETIME_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=JWT_REFRESH_TOKEN_LIFETIME_DAYS),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

GIT_IT_REFRESH_COOKIE = env("JWT_COOKIE_NAME")
GIT_IT_REFRESH_COOKIE_SECURE = env("JWT_COOKIE_SECURE")
GIT_IT_REFRESH_COOKIE_PATH = env("JWT_COOKIE_PATH").strip() or "/api/auth/"
GIT_IT_REFRESH_COOKIE_DOMAIN = env("JWT_COOKIE_DOMAIN", default="").strip() or None
GIT_IT_REFRESH_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE").strip().capitalize()

if GIT_IT_REFRESH_COOKIE_SAMESITE not in {"Strict", "Lax", "None"}:
    raise RuntimeError("JWT_COOKIE_SAMESITE must be Strict, Lax, or None.")

if GIT_IT_REFRESH_COOKIE_SAMESITE == "None" and not GIT_IT_REFRESH_COOKIE_SECURE:
    raise RuntimeError("JWT_COOKIE_SAMESITE=None requires JWT_COOKIE_SECURE=True.")

if not DEBUG and not GIT_IT_REFRESH_COOKIE_SECURE:
    raise RuntimeError("JWT_COOKIE_SECURE must be True when DJANGO_DEBUG=False.")

SPECTACULAR_SETTINGS = {
    "TITLE": "GIT it! API",
    "DESCRIPTION": "Student-facing Git scenario practice API.",
    "VERSION": env("API_VERSION"),
}
