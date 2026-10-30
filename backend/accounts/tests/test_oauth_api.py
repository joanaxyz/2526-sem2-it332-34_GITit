from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import EmailVerification, OAuthIdentity
from accounts.services import oauth as oauth_module
from accounts.services.verification import EmailVerificationService
from players.models import Player

CALLBACK_BASE = "https://app.example.com/api"


@pytest.fixture(autouse=True)
def oauth_settings(settings):
    settings.OAUTH_CALLBACK_BASE_URL = CALLBACK_BASE
    settings.FRONTEND_BASE_URL = "https://app.example.com"
    settings.OAUTH_PROVIDERS = {
        "github": {"client_id": "gh-client", "client_secret": "gh-secret"},
        "google": {"client_id": "google-client", "client_secret": "google-secret"},
    }


@pytest.fixture()
def browser():
    # Start and callback are plain browser navigations: no client header.
    return APIClient()


@pytest.fixture()
def api_client():
    client = APIClient()
    client.credentials(HTTP_X_GIT_IT_CLIENT="web")
    return client


@pytest.fixture()
def provider(monkeypatch):
    """Fake GitHub and Google HTTP APIs; tests set the profile they return."""

    state = {
        "github_user": {"id": 4242, "login": "octo-cat"},
        "github_emails": [{"email": "Octo@Example.com", "primary": True, "verified": True}],
        "google_info": {
            "sub": "google-sub-1",
            "email": "learner@gmail.com",
            "email_verified": True,
            "given_name": "Learner",
        },
        "token_error": False,
        "requests": [],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        state["requests"].append(request)
        url = str(request.url)
        if url in (
            "https://github.com/login/oauth/access_token",
            "https://oauth2.googleapis.com/token",
        ):
            if state["token_error"]:
                return httpx.Response(200, json={"error": "bad_verification_code"})
            return httpx.Response(200, json={"access_token": "provider-token"})
        if url == "https://api.github.com/user":
            return httpx.Response(200, json=state["github_user"])
        if url == "https://api.github.com/user/emails":
            return httpx.Response(200, json=state["github_emails"])
        if url == "https://openidconnect.googleapis.com/v1/userinfo":
            return httpx.Response(200, json=state["google_info"])
        return httpx.Response(404)

    monkeypatch.setattr(oauth_module, "http_transport", httpx.MockTransport(handler))
    return state


def start(browser, provider_name="github"):
    response = browser.get(f"/api/auth/oauth/{provider_name}/start/")
    assert response.status_code == status.HTTP_302_FOUND
    return response


def finish(browser, provider_name="github", *, code="provider-code", state=None):
    if state is None:
        location = start(browser, provider_name)["Location"]
        state = parse_qs(urlparse(location).query)["state"][0]
    response = browser.get(
        f"/api/auth/oauth/{provider_name}/callback/", {"code": code, "state": state}
    )
    assert response.status_code == status.HTTP_302_FOUND
    location = urlparse(response["Location"])
    assert f"{location.scheme}://{location.netloc}{location.path}" == (
        "https://app.example.com/oauth/callback"
    )
    return {key: values[0] for key, values in parse_qs(location.query).items()}


def exchange(api_client, ticket):
    return api_client.post("/api/auth/oauth/exchange/", {"ticket": ticket}, format="json")


def test_start_redirects_to_github_with_state_cookie(db, browser):
    response = start(browser)

    location = urlparse(response["Location"])
    query = parse_qs(location.query)
    assert f"{location.scheme}://{location.netloc}{location.path}" == (
        "https://github.com/login/oauth/authorize"
    )
    assert query["client_id"] == ["gh-client"]
    assert query["redirect_uri"] == [f"{CALLBACK_BASE}/auth/oauth/github/callback/"]
    assert query["scope"] == ["read:user user:email"]
    cookie = response.cookies["git_it_oauth_state"]
    assert cookie["httponly"] and cookie["samesite"] == "Lax"
    assert cookie["path"] == "/api/auth/oauth/"


def test_unconfigured_provider_sends_the_player_back_with_an_error(db, browser, settings):
    settings.OAUTH_PROVIDERS = {"github": {"client_id": "", "client_secret": ""}}

    response = browser.get("/api/auth/oauth/github/start/")

    assert response["Location"] == "https://app.example.com/oauth/callback?error=unavailable"


def test_unknown_provider_is_not_found(db, browser):
    assert browser.get("/api/auth/oauth/myspace/start/").status_code == 404


def test_github_sign_up_creates_a_verified_player_and_signs_in(db, browser, api_client, provider):
    result = finish(browser)

    user = get_user_model().objects.get(email="octo@example.com")
    assert user.username == "octo-cat"
    assert not user.has_usable_password()
    assert Player.objects.filter(user=user).exists()
    assert not EmailVerificationService.is_pending(user)
    identity = OAuthIdentity.objects.get(user=user)
    assert (identity.provider, identity.subject) == ("github", "4242")
    token_request = next(r for r in provider["requests"] if "access_token" in str(r.url))
    assert b"client_secret=gh-secret" in token_request.content

    signed_in = exchange(api_client, result["ticket"])
    assert signed_in.status_code == status.HTTP_200_OK
    assert signed_in.json()["user"]["username"] == "octo-cat"
    assert settings.GIT_IT_REFRESH_COOKIE in signed_in.cookies
    user.refresh_from_db()
    assert user.last_login is not None

    # A ticket signs in exactly once.
    assert exchange(api_client, result["ticket"]).status_code == status.HTTP_400_BAD_REQUEST


def test_returning_github_player_signs_in_to_the_same_account(db, browser, api_client, provider):
    first = finish(browser)
    provider["github_emails"] = [
        {"email": "changed@example.com", "primary": True, "verified": True}
    ]

    second = finish(browser)

    assert exchange(api_client, first["ticket"]).json()["user"]["email"] == "octo@example.com"
    assert exchange(api_client, second["ticket"]).json()["user"]["email"] == "octo@example.com"
    assert get_user_model().objects.count() == 1


def test_google_links_to_an_existing_account_with_the_same_email(
    db, browser, api_client, provider, django_user_model
):
    existing = django_user_model.objects.create_user(
        username="learner", email="learner@gmail.com", password="Password123!"
    )
    EmailVerification.objects.create(user=existing)

    result = finish(browser, "google")

    session = exchange(api_client, result["ticket"]).json()
    assert session["user"]["id"] == existing.id
    assert OAuthIdentity.objects.get(provider="google").user == existing
    # Google proved the inbox, so the pending sign-up code no longer blocks it.
    assert not EmailVerificationService.is_pending(existing)
    # The password still works alongside Google.
    password_login = api_client.post(
        "/api/auth/login/",
        {"identifier": "learner", "password": "Password123!"},
        format="json",
    )
    assert password_login.status_code == status.HTTP_200_OK


def test_unverified_provider_email_is_refused(db, browser, provider):
    provider["google_info"]["email_verified"] = False

    assert finish(browser, "google") == {"error": "email"}
    assert not get_user_model().objects.exists()


def test_github_account_without_a_verified_email_is_refused(db, browser, provider):
    provider["github_emails"] = [{"email": "octo@example.com", "primary": True, "verified": False}]

    assert finish(browser) == {"error": "email"}


def test_staff_accounts_are_never_auto_linked(db, browser, provider, django_user_model):
    django_user_model.objects.create_user(
        username="admin", email="octo@example.com", password="Password123!", is_staff=True
    )

    assert finish(browser) == {"error": "staff"}
    assert not OAuthIdentity.objects.exists()


def test_username_collision_gets_a_suffix(db, browser, provider, django_user_model):
    django_user_model.objects.create_user(
        username="Octo-Cat", email="someone@example.com", password="Password123!"
    )

    finish(browser)

    created = get_user_model().objects.get(email="octo@example.com")
    assert created.username.startswith("octo-cat-")


def test_callback_without_the_state_cookie_is_rejected(db, browser, provider):
    assert finish(browser, state="forged-state") == {"error": "state"}
    assert provider["requests"] == []


def test_callback_from_another_browser_is_rejected(db, browser, provider):
    location = start(browser)["Location"]
    state = parse_qs(urlparse(location).query)["state"][0]

    assert finish(APIClient(), state=state) == {"error": "state"}


def test_cancelled_consent_reports_denied(db, browser):
    start(browser)

    response = browser.get(
        "/api/auth/oauth/github/callback/", {"error": "access_denied", "state": "x"}
    )

    assert response["Location"] == "https://app.example.com/oauth/callback?error=denied"


def test_rejected_code_reports_a_provider_error(db, browser, provider):
    provider["token_error"] = True

    assert finish(browser) == {"error": "provider"}


def test_exchange_requires_the_web_client_header(db, browser, provider):
    result = finish(browser)

    response = APIClient().post(
        "/api/auth/oauth/exchange/", {"ticket": result["ticket"]}, format="json"
    )

    # DRF answers an anonymous caller that fails a permission with 401.
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert settings.GIT_IT_REFRESH_COOKIE not in response.cookies


def test_password_sign_in_records_last_login(db, api_client, django_user_model):
    user = django_user_model.objects.create_user(
        username="veteran", email="veteran@example.com", password="Password123!"
    )

    api_client.post(
        "/api/auth/login/",
        {"identifier": "veteran", "password": "Password123!"},
        format="json",
    )

    user.refresh_from_db()
    assert user.last_login is not None


def test_github_token_request_asks_for_json(db, browser, provider):
    finish(browser)

    token_request = next(r for r in provider["requests"] if "access_token" in str(r.url))
    assert token_request.headers["accept"] == "application/json"
    assert parse_qs(token_request.content.decode())["code"] == ["provider-code"]
