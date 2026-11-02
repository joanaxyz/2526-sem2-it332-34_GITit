# ruff: noqa: F403, F405, I001

import os

os.environ.setdefault("DJANGO_DEBUG", "True")

from .settings import *  # noqa: F403

DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        "auth_register": "10000/hour",
        "auth_refresh": "10000/hour",
        "auth_password_reset": "10000/hour",
        "auth_password_reset_confirm": "10000/hour",
        "auth_email_verification": "10000/hour",
        "auth_email_verification_resend": "10000/hour",
        "auth_oauth": "10000/hour",
        "command_submit": "10000/min",
        "tutor_chat": "10000/min",
        "authenticated": "10000/min",
        "auth_login": "10000/min",
        "auth_logout": "10000/min",
        "auth_password_change": "10000/hour",
        "auth_security": "10000/hour",
        "run_start": "10000/min",
        "tutor_chat_daily": "10000/day",
        "health_ready": "10000/min",
        "public_metadata": "10000/min",
    },
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
TUTOR_PROVIDER_DAILY_LIMIT = 0
