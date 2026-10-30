import re
from datetime import timedelta

import pytest
from django.conf import settings
from django.core import mail
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import EmailVerification

PASSWORD = "Arcane-Spire-2026!"


@pytest.fixture()
def api_client():
    client = APIClient()
    client.credentials(HTTP_X_GIT_IT_CLIENT="web")
    return client


@pytest.fixture()
def register(api_client, django_capture_on_commit_callbacks):
    def _register(username="newarchivist", email="new.archivist@example.com"):
        with django_capture_on_commit_callbacks(execute=True):
            response = api_client.post(
                "/api/auth/register/",
                {
                    "username": username,
                    "email": email,
                    "password": PASSWORD,
                    "password_confirm": PASSWORD,
                },
                format="json",
            )
        assert response.status_code == status.HTTP_201_CREATED
        return response

    return _register


def latest_code() -> str:
    return re.match(r"\d{6}", mail.outbox[-1].subject).group(0)


def login(api_client, identifier="newarchivist"):
    return api_client.post(
        "/api/auth/login/",
        {"identifier": identifier, "password": PASSWORD},
        format="json",
    )


def confirm(api_client, code, email="new.archivist@example.com"):
    return api_client.post(
        "/api/auth/email-verification/confirm/",
        {"email": email, "code": code},
        format="json",
    )


def expire_cooldown(email="new.archivist@example.com"):
    EmailVerification.objects.filter(user__email=email).update(
        last_sent_at=timezone.now() - timedelta(minutes=5)
    )


def test_registration_emails_a_branded_code_and_blocks_sign_in(db, api_client, register):
    register()

    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    code = latest_code()
    assert message.to == ["new.archivist@example.com"]
    assert message.subject == f"{code} is your GIT it! verification code"
    assert code in message.body
    html = message.alternatives[0][0]
    assert code in html
    assert f"{settings.EMAIL_ASSET_BASE_URL}/email/git-it-logo.png" in html
    assert f"{settings.EMAIL_ASSET_BASE_URL}/email/guide-mascot.png" in html
    # Only a hash of the code is stored.
    assert code not in EmailVerification.objects.get().code_hash

    blocked = login(api_client)
    assert blocked.status_code == status.HTTP_403_FORBIDDEN
    assert blocked.json() == {
        "detail": "Confirm your email to finish creating your account.",
        "code": "email_unverified",
        "email": "new.archivist@example.com",
    }
    assert settings.GIT_IT_REFRESH_COOKIE not in blocked.cookies


def test_correct_code_verifies_and_signs_the_player_in(db, api_client, register):
    register()

    verified = confirm(api_client, f" {latest_code()[:3]} {latest_code()[3:]} ")

    assert verified.status_code == status.HTTP_200_OK
    assert verified.json()["user"]["username"] == "newarchivist"
    assert verified.json()["access"]
    assert settings.GIT_IT_REFRESH_COOKIE in verified.cookies
    assert EmailVerification.objects.get().verified_at is not None
    assert login(api_client).status_code == status.HTTP_200_OK
    # A spent code cannot sign anyone in a second time.
    assert confirm(api_client, latest_code()).status_code == status.HTTP_400_BAD_REQUEST


def test_wrong_codes_burn_the_code_after_five_attempts(db, api_client, register):
    register()
    code = latest_code()
    wrong = "000000" if code != "000000" else "111111"

    for _ in range(5):
        response = confirm(api_client, wrong)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "That code is incorrect or has expired. Check it or send a new one."
        }

    assert confirm(api_client, code).status_code == status.HTTP_400_BAD_REQUEST
    assert EmailVerification.objects.get().verified_at is None


def test_expired_code_is_rejected(db, api_client, register):
    register()
    EmailVerification.objects.update(code_expires_at=timezone.now() - timedelta(seconds=1))

    assert confirm(api_client, latest_code()).status_code == status.HTTP_400_BAD_REQUEST


def test_unknown_email_gets_the_same_invalid_code_answer(db, api_client):
    response = confirm(api_client, "123456", email="nobody@example.com")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"].startswith("That code is incorrect")


def test_malformed_code_is_a_field_error(db, api_client):
    response = confirm(api_client, "12ab56")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ["Enter the 6-digit code from the email."]


def test_resend_replaces_the_code_after_the_cooldown(
    db, api_client, register, django_capture_on_commit_callbacks
):
    register()
    first_code = latest_code()

    with django_capture_on_commit_callbacks(execute=True):
        too_soon = api_client.post(
            "/api/auth/email-verification/resend/",
            {"email": "new.archivist@example.com"},
            format="json",
        )
    assert too_soon.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1

    expire_cooldown()
    with django_capture_on_commit_callbacks(execute=True):
        resent = api_client.post(
            "/api/auth/email-verification/resend/",
            {"email": "New.Archivist@Example.com"},
            format="json",
        )
    assert resent.json() == {
        "detail": "If that account still needs verification, a new code is on its way."
    }
    assert len(mail.outbox) == 2
    second_code = latest_code()
    if second_code != first_code:
        assert confirm(api_client, first_code).status_code == status.HTTP_400_BAD_REQUEST
    assert confirm(api_client, second_code).status_code == status.HTTP_200_OK


def test_resend_is_generic_for_unknown_and_verified_emails(
    db, api_client, register, django_user_model, django_capture_on_commit_callbacks
):
    django_user_model.objects.create_user(
        username="veteran", email="veteran@example.com", password=PASSWORD
    )
    with django_capture_on_commit_callbacks(execute=True):
        for email in ("nobody@example.com", "veteran@example.com"):
            response = api_client.post(
                "/api/auth/email-verification/resend/", {"email": email}, format="json"
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["detail"].startswith("If that account still needs")

    assert mail.outbox == []


def test_blocked_sign_in_mails_a_new_code_only_when_the_old_one_is_unusable(
    db, api_client, register, django_capture_on_commit_callbacks
):
    register()
    expire_cooldown()

    with django_capture_on_commit_callbacks(execute=True):
        login(api_client)
    assert len(mail.outbox) == 1, "a live code is still in the inbox"

    EmailVerification.objects.update(
        code_expires_at=timezone.now() - timedelta(seconds=1),
        last_sent_at=timezone.now() - timedelta(minutes=20),
    )
    with django_capture_on_commit_callbacks(execute=True):
        blocked = login(api_client, identifier="new.archivist@example.com")
    assert blocked.status_code == status.HTTP_403_FORBIDDEN
    assert len(mail.outbox) == 2
    assert confirm(api_client, latest_code()).status_code == status.HTTP_200_OK


def test_accounts_without_a_verification_record_sign_in_normally(db, api_client, django_user_model):
    django_user_model.objects.create_user(
        username="veteran", email="veteran@example.com", password=PASSWORD
    )

    assert login(api_client, identifier="veteran").status_code == status.HTTP_200_OK


def test_password_reset_verifies_a_pending_account(
    db, api_client, register, django_capture_on_commit_callbacks
):
    register()

    with django_capture_on_commit_callbacks(execute=True):
        api_client.post(
            "/api/auth/password-reset/request/",
            {"email": "new.archivist@example.com"},
            format="json",
        )
    reset_email = mail.outbox[-1]
    assert reset_email.subject == "Reset your GIT it! password"
    html = reset_email.alternatives[0][0]
    assert f"{settings.EMAIL_ASSET_BASE_URL}/email/git-it-logo.png" in html
    uid, token = re.search(r"/reset-password/([^/\s]+)/([^/\s]+)", reset_email.body).groups()

    new_password = "Fresh-Spire-Key-77!"
    with django_capture_on_commit_callbacks(execute=True):
        reset = api_client.post(
            "/api/auth/password-reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "password": new_password,
                "password_confirm": new_password,
            },
            format="json",
        )
    assert reset.status_code == status.HTTP_200_OK
    assert mail.outbox[-1].subject == "Your GIT it! password was changed"

    signed_in = api_client.post(
        "/api/auth/login/",
        {"identifier": "newarchivist", "password": new_password},
        format="json",
    )
    assert signed_in.status_code == status.HTTP_200_OK
    assert EmailVerification.objects.get().verified_at is not None
