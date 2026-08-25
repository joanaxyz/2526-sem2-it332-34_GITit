import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import SessionRecord
from accounts.serializers import (
    AccessTokenResponseSerializer,
    DetailResponseSerializer,
    RegisterResponseSerializer,
    SessionResponseSerializer,
    UserSerializer,
)
from accounts.services import TokenService

USER_FIELDS = {"id", "username", "email", "is_staff"}


@pytest.fixture()
def api_client():
    client = APIClient()
    client.credentials(HTTP_X_GIT_IT_CLIENT="web")
    return client


def create_user(*, username="contract-user", email="contract@example.com"):
    return get_user_model().objects.create_user(
        username=username,
        email=email,
        password="Password123!",
    )


def assert_exact_user(payload, user):
    assert set(payload) == USER_FIELDS
    assert payload == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    }


def test_auth_response_serializers_declare_exact_success_families():
    assert set(UserSerializer().fields) == USER_FIELDS
    assert set(RegisterResponseSerializer().fields) == {"user"}
    assert isinstance(RegisterResponseSerializer().fields["user"], UserSerializer)
    assert set(SessionResponseSerializer().fields) == {"access", "user"}
    assert isinstance(SessionResponseSerializer().fields["user"], UserSerializer)
    assert set(AccessTokenResponseSerializer().fields) == {"access"}
    assert set(DetailResponseSerializer().fields) == {"detail"}


@pytest.mark.django_db
def test_register_login_me_and_password_change_return_exact_contracts(api_client):
    register = api_client.post(
        "/api/auth/register/",
        {
            "username": "contract-user",
            "email": "contract@example.com",
            "password": "Password123!",
            "password_confirm": "Password123!",
        },
        format="json",
    )
    user = get_user_model().objects.get(username="contract-user")

    assert register.status_code == status.HTTP_201_CREATED
    assert set(register.data) == {"user"}
    assert_exact_user(register.data["user"], user)
    assert register.data == RegisterResponseSerializer({"user": user}).data

    login = api_client.post(
        "/api/auth/login/",
        {"identifier": "contract-user", "password": "Password123!"},
        format="json",
    )
    assert login.status_code == status.HTTP_200_OK
    assert set(login.data) == {"access", "user"}
    assert isinstance(login.data["access"], str) and login.data["access"]
    assert_exact_user(login.data["user"], user)
    assert settings.GIT_IT_REFRESH_COOKIE in login.cookies

    original_access = login.data["access"]
    api_client.credentials(
        HTTP_X_GIT_IT_CLIENT="web",
        HTTP_AUTHORIZATION=f"Bearer {original_access}",
    )
    me = api_client.get("/api/auth/me/")
    assert me.status_code == status.HTTP_200_OK
    assert_exact_user(me.data, user)
    assert me.data == UserSerializer(user).data

    password_change = api_client.post(
        "/api/auth/password-change/",
        {
            "current_password": "Password123!",
            "password": "NewPassword123!",
            "password_confirm": "NewPassword123!",
        },
        format="json",
    )
    assert password_change.status_code == status.HTTP_200_OK
    assert set(password_change.data) == {"access", "user"}
    assert_exact_user(password_change.data["user"], user)
    assert settings.GIT_IT_REFRESH_COOKIE in password_change.cookies

    stale_client = APIClient()
    stale_client.credentials(
        HTTP_X_GIT_IT_CLIENT="web",
        HTTP_AUTHORIZATION=f"Bearer {original_access}",
    )
    assert stale_client.get("/api/auth/me/").status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_refresh_returns_exact_access_contract_and_rotates_session(api_client):
    user = create_user()
    original = TokenService().issue_for_user(user)
    api_client.cookies[settings.GIT_IT_REFRESH_COOKIE] = original.refresh

    response = api_client.post("/api/auth/refresh/", format="json")

    assert response.status_code == status.HTTP_200_OK
    assert set(response.data) == {"access"}
    assert isinstance(response.data["access"], str) and response.data["access"]
    assert response.data == AccessTokenResponseSerializer(response.data).data
    assert settings.GIT_IT_REFRESH_COOKIE in response.cookies
    assert SessionRecord.objects.filter(user=user).count() == 2
    assert SessionRecord.objects.get(refresh_jti=original.refresh_jti).revoked_at is not None

    invalid_client = APIClient()
    invalid_client.credentials(HTTP_X_GIT_IT_CLIENT="web")
    invalid_client.cookies[settings.GIT_IT_REFRESH_COOKIE] = "not-a-valid-token"
    invalid = invalid_client.post("/api/auth/refresh/", format="json")
    assert invalid.status_code == status.HTTP_401_UNAUTHORIZED
    assert invalid.data == {"detail": "Session expired."}
    assert settings.GIT_IT_REFRESH_COOKIE not in invalid.cookies


@pytest.mark.django_db
def test_detail_and_empty_auth_successes_keep_exact_contracts(api_client):
    user = create_user()
    anonymous = APIClient()
    anonymous.credentials(HTTP_X_GIT_IT_CLIENT="web")
    reset = anonymous.post(
        "/api/auth/password-reset/request/",
        {"email": user.email},
        format="json",
    )
    assert reset.status_code == status.HTTP_200_OK
    assert set(reset.data) == {"detail"}
    assert isinstance(reset.data["detail"], str)
    assert reset.data == DetailResponseSerializer(reset.data).data

    confirm = anonymous.post(
        "/api/auth/password-reset/confirm/",
        {
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
            "password": "ResetPassword456!",
            "password_confirm": "ResetPassword456!",
        },
        format="json",
    )
    assert confirm.status_code == status.HTTP_200_OK
    assert confirm.data == {
        "detail": "Password reset successfully. You can now sign in."
    }
    assert confirm.data == DetailResponseSerializer(confirm.data).data
    user.refresh_from_db()

    TokenService().issue_for_user(user)
    current = TokenService().issue_for_user(user)
    api_client.cookies[settings.GIT_IT_REFRESH_COOKIE] = current.refresh
    api_client.credentials(
        HTTP_X_GIT_IT_CLIENT="web",
        HTTP_AUTHORIZATION=f"Bearer {current.access}",
    )
    revoke_others = api_client.post("/api/auth/sessions/revoke-others/", format="json")
    assert revoke_others.status_code == status.HTTP_200_OK
    assert set(revoke_others.data) == {"detail"}
    assert isinstance(revoke_others.data["detail"], str)

    logout = api_client.post("/api/auth/logout/", format="json")
    assert logout.status_code == status.HTTP_204_NO_CONTENT
    assert logout.data is None
    assert settings.GIT_IT_REFRESH_COOKIE in logout.cookies

    latest = TokenService().issue_for_user(user)
    api_client.cookies[settings.GIT_IT_REFRESH_COOKIE] = latest.refresh
    api_client.credentials(
        HTTP_X_GIT_IT_CLIENT="web",
        HTTP_AUTHORIZATION=f"Bearer {latest.access}",
    )
    revoke_all = api_client.post("/api/auth/sessions/revoke-all/", format="json")
    assert revoke_all.status_code == status.HTTP_204_NO_CONTENT
    assert revoke_all.data is None
    assert settings.GIT_IT_REFRESH_COOKIE in revoke_all.cookies
