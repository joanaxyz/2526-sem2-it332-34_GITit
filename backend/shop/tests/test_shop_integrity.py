from rest_framework.test import APIClient

from players.services import get_or_create_player
from progress.models import CoinTransaction, Wallet
from shop.catalog import KIND_COMPANION
from shop.models import Entitlement, PlayerLoadout


def make_user(django_user_model, username: str = "shop-integrity"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_unknown_companion_purchase_is_rejected(db, django_user_model):
    user = make_user(django_user_model, "unknown-companion")
    client = authenticated_client(user)

    response = client.post(
        "/api/shop/catalog/purchase/",
        {"kind": KIND_COMPANION, "slug": "ghost"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["slug"] == "Unknown companion 'ghost'."


def test_unknown_companion_equip_is_rejected(db, django_user_model):
    user = make_user(django_user_model, "unknown-companion-equip")
    client = authenticated_client(user)

    response = client.post(
        "/api/player/loadout/companion/",
        {"kind": KIND_COMPANION, "slug": "ghost"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["slug"] == "Unknown companion 'ghost'."


def test_unowned_companion_equip_is_rejected(db, django_user_model):
    user = make_user(django_user_model, "unowned-companion")
    client = authenticated_client(user)

    response = client.post(
        "/api/player/loadout/companion/",
        {"kind": KIND_COMPANION, "slug": "blue"},
        format="json",
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not own this shop item."
    assert not PlayerLoadout.objects.filter(player=get_or_create_player(user)).exists()


def test_stories_are_not_a_purchasable_kind(db, django_user_model):
    """Stories are unlocked by mastering their prerequisite, never bought."""
    user = make_user(django_user_model, "story-not-for-sale")
    player = get_or_create_player(user)
    client = authenticated_client(user)

    response = client.post(
        "/api/shop/catalog/purchase/",
        {"kind": "story", "slug": "git-it-legacy"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["kind"] == "Unknown shop item kind 'story'."
    assert not Entitlement.objects.filter(player=player).exists()


def test_stories_cannot_be_equipped(db, django_user_model):
    user = make_user(django_user_model, "story-equip")
    client = authenticated_client(user)

    response = client.post(
        "/api/player/loadout/companion/",
        {"kind": "story", "slug": "git-it-legacy"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["kind"] == "Unknown shop item kind 'story'."


def test_insufficient_funds_do_not_create_entitlement_or_charge(db, django_user_model):
    user = make_user(django_user_model, "insufficient-funds")
    player = get_or_create_player(user)
    client = authenticated_client(user)

    response = client.post(
        "/api/shop/catalog/purchase/",
        {"kind": KIND_COMPANION, "slug": "blue"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["balance"] == "Insufficient GitCoins."
    wallet = Wallet.objects.filter(player=player).first()
    assert wallet is None or wallet.balance == 0
    assert not Entitlement.objects.filter(player=player, kind=KIND_COMPANION, slug="blue").exists()
    assert not CoinTransaction.objects.filter(player=player, reason="shop_purchase").exists()
