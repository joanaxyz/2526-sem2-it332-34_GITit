# ruff: noqa: F403, F405, I001

from .settings import *  # noqa: F403


DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
DATABASES["default"]["CONN_MAX_AGE"] = 0
DATABASES["default"]["CONN_HEALTH_CHECKS"] = False

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "git-it-test-cache",
    }
}

# Throttle counters live in the shared locmem cache and user/IP keys repeat
# across tests, so real rates would trip mid-suite. Throttle tests override
# these locally.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        "auth_register": "10000/hour",
        "auth_refresh": "10000/hour",
        "command_submit": "10000/min",
    },
}
