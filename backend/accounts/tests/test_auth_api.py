from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import SessionRecord
from accounts.services import TokenBlacklistService, TokenService


@pytest.fixture()
def api_client():
    return APIClient()


def registration_payload(**overrides):
    payload = {
        "username": "jcgako",
        "email": "student@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    payload.update(overrides)
    return payload


def create_student_user(**overrides):
    data = {
        "username": "jcgako",
        "email": "student@example.com",
        "password": "Password123!",
    }
    data.update(overrides)
    return get_user_model().objects.create_user(**data)


def test_register_creates_user_with_username_and_email(db, api_client):
    response = api_client.post("/api/auth/register/", registration_payload(), format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user"]["username"] == "jcgako"
    assert response.data["user"]["email"] == "student@example.com"
    assert get_user_model().objects.get().username == "jcgako"


def test_register_rejects_duplicate_username_case_insensitive(db, api_client):
    create_student_user(username="JCGako", email="existing@example.com")

    response = api_client.post(
        "/api/auth/register/",
        registration_payload(username="jcgako", email="new@example.com"),
        format="json",
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "username" in str(response.data).lower()


def test_register_rejects_duplicate_email_case_insensitive(db, api_client):
    create_student_user(username="existing", email="student@example.com")

    response = api_client.post(
        "/api/auth/register/",
        registration_payload(username="newuser", email="STUDENT@example.com"),
        format="json",
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "email" in str(response.data).lower()


def test_register_accepts_non_cit_email(db, api_client):
    response = api_client.post(
        "/api/auth/register/",
        registration_payload(email="student@gmail.com"),
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user"]["email"] == "student@gmail.com"


def test_register_rejects_invalid_username_format(db, api_client):
    response = api_client.post(
        "/api/auth/register/",
        registration_payload(username="bad username!"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data


def test_login_accepts_username_or_email(db, api_client):
    create_student_user()

    username_response = api_client.post(
        "/api/auth/login/",
        {"identifier": "jcgako", "password": "Password123!"},
        format="json",
    )
    email_response = api_client.post(
        "/api/auth/login/",
        {"identifier": "student@example.com", "password": "Password123!"},
        format="json",
    )

    assert username_response.status_code == status.HTTP_200_OK
    assert email_response.status_code == status.HTTP_200_OK
    assert username_response.data["user"]["username"] == "jcgako"
    assert email_response.data["user"]["username"] == "jcgako"


def test_login_rejects_invalid_credentials_with_generic_message(db, api_client):
    create_student_user()

    response = api_client.post(
        "/api/auth/login/",
        {"identifier": "jcgako", "password": "wrong-password"},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == "Incorrect username/email or password"


def test_refresh_does_not_clear_refresh_cookie_on_token_error(db, api_client):
    api_client.cookies[settings.GIT_IT_REFRESH_COOKIE] = "not-a-valid-token"

    response = api_client.post("/api/auth/refresh/", format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert settings.GIT_IT_REFRESH_COOKIE not in response.cookies


def test_refresh_succeeds_with_expired_access_token_header(db, api_client):
    user = create_student_user()
    tokens = TokenService().issue_for_user(user)
    api_client.cookies[settings.GIT_IT_REFRESH_COOKIE] = tokens.refresh

    expired_access = AccessToken.for_user(user)
    expired_access.set_exp(
        from_time=timezone.now() - timedelta(minutes=1),
        lifetime=timedelta(minutes=15),
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(expired_access)}")

    response = api_client.post("/api/auth/refresh/", format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert settings.GIT_IT_REFRESH_COOKIE in response.cookies


def test_refresh_for_deleted_user_returns_401(db, api_client):
    user = create_student_user(username="deleted", email="deleted@example.com")
    tokens = TokenService().issue_for_user(user)
    user.delete()
    api_client.cookies[settings.GIT_IT_REFRESH_COOKIE] = tokens.refresh

    response = api_client.post("/api/auth/refresh/", format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_revocation_uses_configured_cache(db):
    user = create_student_user(username="revoked", email="revoked@example.com")
    tokens = TokenService().issue_for_user(user)
    blacklist = TokenBlacklistService()

    assert blacklist.is_revoked(tokens.refresh) is False

    blacklist.revoke(tokens.refresh)

    assert blacklist.is_revoked(tokens.refresh) is True
    assert SessionRecord.objects.get(refresh_jti=tokens.refresh_jti).revoked_at is not None
