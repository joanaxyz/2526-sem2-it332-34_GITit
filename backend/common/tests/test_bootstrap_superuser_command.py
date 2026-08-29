from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

ENVIRONMENT_KEYS = (
    "DJANGO_SUPERUSER_USERNAME",
    "DJANGO_SUPERUSER_EMAIL",
    "DJANGO_SUPERUSER_PASSWORD",
)


def clear_bootstrap_environment(monkeypatch):
    for key in ENVIRONMENT_KEYS:
        monkeypatch.delenv(key, raising=False)


@pytest.mark.django_db
def test_bootstrap_superuser_skips_when_unconfigured(monkeypatch):
    clear_bootstrap_environment(monkeypatch)

    call_command("bootstrap_superuser", verbosity=0)

    assert get_user_model().objects.count() == 0


@pytest.mark.django_db
def test_bootstrap_superuser_creates_and_updates_admin(monkeypatch):
    clear_bootstrap_environment(monkeypatch)
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "preview-admin")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "preview@example.com")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "FirstStrongPassword123!")

    call_command("bootstrap_superuser", verbosity=0)
    user = get_user_model().objects.get(username="preview-admin")
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password("FirstStrongPassword123!") is True

    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "SecondStrongPassword456!")
    call_command("bootstrap_superuser", verbosity=0)

    user.refresh_from_db()
    assert user.check_password("SecondStrongPassword456!") is True
    assert get_user_model().objects.count() == 1


@pytest.mark.django_db
def test_bootstrap_superuser_rejects_partial_configuration(monkeypatch):
    clear_bootstrap_environment(monkeypatch)
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "preview-admin")

    with pytest.raises(CommandError, match="configuration is incomplete"):
        call_command("bootstrap_superuser", verbosity=0)
