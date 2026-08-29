import re
from unittest import mock

import pytest
from django.conf import settings
from django.core import mail
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import AccountSecurity, SessionRecord
from accounts.services import TokenService


@pytest.fixture()
def api_client():
    client = APIClient()
    client.credentials(HTTP_X_GIT_IT_CLIENT="web")
    return client


def create_user(django_user_model, *, username="resetuser", email="reset@example.com"):
    return django_user_model.objects.create_user(
        username=username,
        email=email,
        password="Password123!",
    )


def reset_link_parts(message_body: str) -> tuple[str, str]:
    match = re.search(r"/reset-password/([^/\s]+)/([^/\s]+)", message_body)
    assert match is not None
    return match.group(1), match.group(2).rstrip(".\n\r")


def test_password_reset_request_is_generic_and_only_emails_existing_active_user(
    db, api_client, django_user_model
):
    user = create_user(django_user_model)

    existing = api_client.post(
        "/api/auth/password-reset/request/",
        {"email": user.email},
        format="json",
    )
    missing = api_client.post(
        "/api/auth/password-reset/request/",
        {"email": "missing@example.com"},
        format="json",
    )

    expected = "If an account exists for that email, a reset link has been sent."
    assert existing.status_code == status.HTTP_200_OK
    assert missing.status_code == status.HTTP_200_OK
    assert existing.json() == {"detail": expected}
    assert missing.json() == {"detail": expected}
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [user.email]
    assert f"{settings.FRONTEND_BASE_URL}/reset-password/" in mail.outbox[0].body


def test_password_reset_changes_password_revokes_sessions_and_invalidates_old_access(
    db, api_client, django_user_model
):
    user = create_user(django_user_model)
    old_tokens = TokenService().issue_for_user(user)

    request_response = api_client.post(
        "/api/auth/password-reset/request/",
        {"email": user.email},
        format="json",
    )
    assert request_response.status_code == status.HTTP_200_OK
    uid, token = reset_link_parts(mail.outbox[0].body)

    response = api_client.post(
        "/api/auth/password-reset/confirm/",
        {
            "uid": uid,
            "token": token,
            "password": "NewPassword456!",
            "password_confirm": "NewPassword456!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("NewPassword456!")
    assert AccountSecurity.objects.get(user=user).auth_version == 2
    assert SessionRecord.objects.get(refresh_jti=old_tokens.refresh_jti).revoked_at is not None

    old_access_client = APIClient()
    old_access_client.credentials(HTTP_AUTHORIZATION=f"Bearer {old_tokens.access}")
    assert old_access_client.get("/api/auth/me/").status_code == status.HTTP_401_UNAUTHORIZED

    reused = api_client.post(
        "/api/auth/password-reset/confirm/",
        {
            "uid": uid,
            "token": token,
            "password": "AnotherPassword789!",
            "password_confirm": "AnotherPassword789!",
        },
        format="json",
    )
    assert reused.status_code == status.HTTP_400_BAD_REQUEST


def test_password_change_issues_fresh_versioned_session_and_rejects_old_access(
    db, api_client, django_user_model
):
    user = create_user(django_user_model, username="changeuser", email="change@example.com")
    old_tokens = TokenService().issue_for_user(user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {old_tokens.access}",
        HTTP_X_GIT_IT_CLIENT="web",
    )

    response = api_client.post(
        "/api/auth/password-change/",
        {
            "current_password": "Password123!",
            "password": "ChangedPassword456!",
            "password_confirm": "ChangedPassword456!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["username"] == user.username
    assert "access" in response.json()
    user.refresh_from_db()
    assert user.check_password("ChangedPassword456!")
    assert AccountSecurity.objects.get(user=user).auth_version == 2
    assert SessionRecord.objects.get(refresh_jti=old_tokens.refresh_jti).revoked_at is not None

    old_access_client = APIClient()
    old_access_client.credentials(HTTP_AUTHORIZATION=f"Bearer {old_tokens.access}")
    assert old_access_client.get("/api/auth/me/").status_code == status.HTTP_401_UNAUTHORIZED

    fresh_access_client = APIClient()
    fresh_access_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")
    assert fresh_access_client.get("/api/auth/me/").status_code == status.HTTP_200_OK


def test_password_change_rejects_wrong_current_password(db, api_client, django_user_model):
    user = create_user(django_user_model, username="wrongcurrent", email="wrong@example.com")
    tokens = TokenService().issue_for_user(user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {tokens.access}",
        HTTP_X_GIT_IT_CLIENT="web",
    )

    response = api_client.post(
        "/api/auth/password-change/",
        {
            "current_password": "not-the-password",
            "password": "ChangedPassword456!",
            "password_confirm": "ChangedPassword456!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert user.check_password("Password123!")


def test_password_reset_request_keeps_generic_response_when_email_delivery_fails(
    db, api_client, django_user_model
):
    user = create_user(django_user_model, username="mailfailure", email="mailfailure@example.com")
    with mock.patch(
        "accounts.services.passwords.EmailMultiAlternatives.send",
        side_effect=RuntimeError("mail provider unavailable"),
    ):
        response = api_client.post(
            "/api/auth/password-reset/request/",
            {"email": user.email},
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "detail": "If an account exists for that email, a reset link has been sent."
    }
