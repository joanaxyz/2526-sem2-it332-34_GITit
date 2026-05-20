import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta

from accounts.models import StudentProfile
from accounts.services import TokenService


@pytest.fixture()
def api_client():
    return APIClient()


def registration_payload(**overrides):
    payload = {
        "student_id": "23-0001-001",
        "first_name": "Joana",
        "last_name": "Gako",
        "email": "student@cit.edu",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    payload.update(overrides)
    return payload


def test_register_creates_student_profile_with_cit_email(db, api_client):
    response = api_client.post("/api/auth/register/", registration_payload(), format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user"]["student_id"] == "23-0001-001"
    assert response.data["user"]["first_name"] == "Joana"
    assert response.data["user"]["last_name"] == "Gako"
    assert response.data["user"]["email"] == "student@cit.edu"
    assert StudentProfile.objects.get().student_id == "23-0001-001"


def test_register_rejects_non_cit_email(db, api_client):
    response = api_client.post(
        "/api/auth/register/",
        registration_payload(email="student@example.com"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


def test_register_rejects_invalid_student_id_format(db, api_client):
    response = api_client.post(
        "/api/auth/register/",
        registration_payload(student_id="2023-0001"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "student_id" in response.data


def test_login_accepts_student_id_or_email(db, api_client):
    user = get_user_model().objects.create_user(
        username="student@cit.edu",
        email="student@cit.edu",
        password="Password123!",
        first_name="Joana",
        last_name="Gako",
    )
    StudentProfile.objects.create(user=user, student_id="23-0001-001")

    student_id_response = api_client.post(
        "/api/auth/login/",
        {"identifier": "23-0001-001", "password": "Password123!"},
        format="json",
    )
    email_response = api_client.post(
        "/api/auth/login/",
        {"identifier": "student@cit.edu", "password": "Password123!"},
        format="json",
    )

    assert student_id_response.status_code == status.HTTP_200_OK
    assert email_response.status_code == status.HTTP_200_OK
    assert student_id_response.data["user"]["student_id"] == "23-0001-001"
    assert email_response.data["user"]["student_id"] == "23-0001-001"


def test_login_rejects_non_cit_email_identifier(db, api_client):
    user = get_user_model().objects.create_user(
        username="student@example.com",
        email="student@example.com",
        password="Password123!",
    )
    StudentProfile.objects.create(user=user, student_id="23-0001-001")

    response = api_client.post(
        "/api/auth/login/",
        {"identifier": "student@example.com", "password": "Password123!"},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_does_not_clear_refresh_cookie_on_token_error(db, api_client):
    api_client.cookies[settings.GIT_IT_REFRESH_COOKIE] = "not-a-valid-token"

    response = api_client.post("/api/auth/refresh/", format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert settings.GIT_IT_REFRESH_COOKIE not in response.cookies


def test_refresh_succeeds_with_expired_access_token_header(db, api_client):
    user = get_user_model().objects.create_user(
        username="student@cit.edu",
        email="student@cit.edu",
        password="Password123!",
    )
    StudentProfile.objects.create(user=user, student_id="23-0001-001")

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
