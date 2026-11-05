import re
from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import AccountIdentity, PendingEmailChange

pytestmark = pytest.mark.django_db


@pytest.fixture
def account(django_user_model):
    return django_user_model.objects.create_user(
        username="archivist", email="archivist@example.com", password="Spire-Key-2026!"
    )


@pytest.fixture
def client(account):
    client = APIClient()
    client.force_authenticate(account)
    return client


def request_change(client, django_capture_on_commit_callbacks, **values):
    with django_capture_on_commit_callbacks(execute=True):
        return client.patch("/api/auth/me/", values, format="json")


def code():
    return re.match(r"\d{6}", mail.outbox[-1].subject).group()


def confirm(client, value):
    return client.post("/api/auth/email-change/confirm/", {"code": value}, format="json")


def test_username_update_persists_identity_and_sign_in(client, account):
    response = client.patch("/api/auth/me/", {"username": "New.Archivist"}, format="json")
    assert response.status_code == 200
    assert response.data["pending_email"] is None
    account.refresh_from_db()
    assert account.username == "New.Archivist"
    assert response.data["user"]["username"] == account.username
    assert AccountIdentity.objects.get(user=account).username_key == "new.archivist"
    assert client.get("/api/auth/me/").data["username"] == account.username
    public = APIClient()
    public.credentials(HTTP_X_GIT_IT_CLIENT="web")
    login = public.post(
        "/api/auth/login/",
        {"identifier": "New.Archivist", "password": "Spire-Key-2026!"},
        format="json",
    )
    assert login.status_code == 200


def test_email_is_only_replaced_after_code_confirmation(
    client, account, django_capture_on_commit_callbacks
):
    response = request_change(
        client, django_capture_on_commit_callbacks, username="newarchivist", email="New@Example.com"
    )
    assert response.status_code == 200
    assert response.data["pending_email"] == "new@example.com"
    account.refresh_from_db()
    assert account.username == "newarchivist"
    assert account.email == "archivist@example.com"
    assert mail.outbox[-1].to == ["new@example.com"]
    pending = PendingEmailChange.objects.get(user=account)
    assert pending.code_hash != code()
    assert "Settings" in mail.outbox[-1].body
    verified = confirm(client, code())
    assert verified.status_code == 200
    assert verified.data["email"] == "new@example.com"
    account.refresh_from_db()
    assert account.email == "new@example.com"
    assert AccountIdentity.objects.get(user=account).email_key == "new@example.com"
    assert not PendingEmailChange.objects.filter(user=account).exists()
    assert confirm(client, code()).status_code == 400


@pytest.mark.parametrize("field,value", [("username", "TAKEN"), ("email", "Taken@Example.com")])
def test_duplicates_are_field_errors_and_no_partial_update(
    client, account, django_user_model, field, value
):
    django_user_model.objects.create_user(username="taken", email="taken@example.com")
    response = client.patch("/api/auth/me/", {"username": "unused", field: value}, format="json")
    assert response.status_code == 400
    assert field in response.data
    account.refresh_from_db()
    assert account.username == "archivist"
    assert not PendingEmailChange.objects.exists()


@pytest.mark.parametrize("values", [{"username": "x"}, {"username": "bad name"}, {"email": "bad"}])
def test_invalid_identity_is_rejected(client, values):
    assert client.patch("/api/auth/me/", values, format="json").status_code == 400


def test_username_change_updates_existing_identity_and_frees_previous_name(client, account):
    AccountIdentity.objects.create(
        user=account, username_key="archivist", email_key="archivist@example.com"
    )
    assert client.patch("/api/auth/me/", {"username": "renamed"}, format="json").status_code == 200
    assert not AccountIdentity.objects.filter(username_key="archivist").exists()
    assert AccountIdentity.objects.get(user=account).username_key == "renamed"


def test_codes_are_account_bound_and_burn_after_five_failures(
    client, account, django_user_model, django_capture_on_commit_callbacks
):
    request_change(client, django_capture_on_commit_callbacks, email="new@example.com")
    valid = code()
    other = django_user_model.objects.create_user(username="other", email="other@example.com")
    other_client = APIClient()
    other_client.force_authenticate(other)
    assert confirm(other_client, valid).status_code == 400
    wrong = "000000" if valid != "000000" else "111111"
    for _ in range(5):
        assert confirm(client, wrong).status_code == 400
    assert PendingEmailChange.objects.get(user=account).failed_attempts == 5
    assert confirm(client, valid).status_code == 400
    account.refresh_from_db()
    assert account.email == "archivist@example.com"


def test_expired_code_does_not_change_email(client, account, django_capture_on_commit_callbacks):
    request_change(client, django_capture_on_commit_callbacks, email="new@example.com")
    PendingEmailChange.objects.update(code_expires_at=timezone.now() - timedelta(seconds=1))
    assert confirm(client, code()).status_code == 400
    account.refresh_from_db()
    assert account.email == "archivist@example.com"


def test_resend_cooldown_and_new_code_replace_old_code(
    client, account, django_capture_on_commit_callbacks
):
    request_change(client, django_capture_on_commit_callbacks, email="new@example.com")
    old_hash = PendingEmailChange.objects.get(user=account).code_hash
    request_change(client, django_capture_on_commit_callbacks, email="new@example.com")
    assert len(mail.outbox) == 1
    different = request_change(
        client, django_capture_on_commit_callbacks, email="different@example.com"
    )
    assert different.status_code == 429
    PendingEmailChange.objects.update(last_sent_at=timezone.now() - timedelta(minutes=2))
    request_change(client, django_capture_on_commit_callbacks, email="different@example.com")
    assert len(mail.outbox) == 2
    pending = PendingEmailChange.objects.get(user=account)
    assert pending.email == "different@example.com"
    assert pending.code_hash != old_hash
    assert confirm(client, code()).status_code == 200


def test_confirmation_rechecks_address_availability(
    client, account, django_user_model, django_capture_on_commit_callbacks
):
    request_change(client, django_capture_on_commit_callbacks, email="new@example.com")
    django_user_model.objects.create_user(username="newowner", email="new@example.com")
    response = confirm(client, code())
    assert response.status_code == 400
    assert "email" in response.data
    account.refresh_from_db()
    assert account.email == "archivist@example.com"


def test_account_updates_require_authentication_and_cannot_change_privileges(client, account):
    assert APIClient().patch("/api/auth/me/", {}, format="json").status_code == 401
    assert confirm(APIClient(), "123456").status_code == 401
    client.patch("/api/auth/me/", {"is_staff": True, "id": account.pk + 1}, format="json")
    account.refresh_from_db()
    assert not account.is_staff
