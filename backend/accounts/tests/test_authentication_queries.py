import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

from accounts.authentication import VersionedJWTAuthentication
from accounts.models import AccountSecurity
from players.services import get_or_create_player


def access_token(user, version=1):
    token = AccessToken.for_user(user)
    token["auth_version"] = version
    return token


def test_one_query_loads_the_user_its_security_version_and_its_player(
    db, django_assert_num_queries
):
    user = get_user_model().objects.create_user(username="reader", password="pass12345")
    player = get_or_create_player(user)
    AccountSecurity.objects.create(user=user, auth_version=3)

    with django_assert_num_queries(1):
        authenticated = VersionedJWTAuthentication().get_user(access_token(user, version=3))
        assert get_or_create_player(authenticated) == player


def test_a_user_without_a_player_still_gets_one(db):
    user = get_user_model().objects.create_user(username="newcomer", password="pass12345")

    authenticated = VersionedJWTAuthentication().get_user(access_token(user))

    assert get_or_create_player(authenticated).user_id == user.id


def test_tokens_from_before_a_security_change_are_rejected(db):
    user = get_user_model().objects.create_user(username="changed", password="pass12345")
    AccountSecurity.objects.create(user=user, auth_version=2)

    with pytest.raises(AuthenticationFailed) as raised:
        VersionedJWTAuthentication().get_user(access_token(user, version=1))

    assert raised.value.get_codes() == "session_revoked"
