from unittest.mock import Mock

import pytest
from rest_framework.test import APIClient

from adminconsole.models import FeatureFlag
from players.models import Player
from players.services import get_or_create_player
from progress.models import CoinTransaction, Wallet
from progress.wallet import WalletService
from shop.models import Entitlement, PlayerLoadout
from shop.services import ShopService


def make_user(django_user_model, username: str = "student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def companion_by_slug(payload: dict, slug: str) -> dict:
    return next(
        item for item in payload["items"] if item["kind"] == "companion" and item["slug"] == slug
    )


def test_shop_catalog_lists_companions_none_equipped_by_default(db, django_user_model):
    user = make_user(django_user_model)
    client = authenticated_client(user)

    response = client.get("/api/shop/catalog/")

    assert response.status_code == 200
    body = response.json()
    assert body["active_companion"] is None
    assert [item["slug"] for item in body["items"]] == ["blue", "white", "black"]
    assert {item["kind"] for item in body["items"]} == {"companion"}
    for slug in ("blue", "white", "black"):
        assert companion_by_slug(body, slug)["owned"] is False
        assert companion_by_slug(body, slug)["active"] is False
        assert companion_by_slug(body, slug)["price"] > 0


def test_shop_catalog_projects_the_exact_companion_contract(db, django_user_model):
    client = authenticated_client(make_user(django_user_model, "exact-shop-contract"))

    response = client.get("/api/shop/catalog/")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "active_companion", "purchases_enabled"}
    assert set(companion_by_slug(body, "blue")) == {
        "kind",
        "slug",
        "label",
        "price",
        "owned",
        "active",
    }


@pytest.mark.parametrize("field", ["kind", "slug"])
@pytest.mark.parametrize("value", [7, True, ["blue"], {"slug": "blue"}, None])
def test_purchase_rejects_non_string_fields_before_service_or_player_creation(
    db,
    django_user_model,
    monkeypatch,
    field,
    value,
):
    user = make_user(django_user_model, f"strict-{field}-{type(value).__name__}")
    client = authenticated_client(user)
    purchase = Mock()
    monkeypatch.setattr(ShopService, "purchase", purchase)
    payload = {"kind": "companion", "slug": "blue"}
    payload[field] = value

    response = client.post("/api/shop/catalog/purchase/", payload, format="json")

    assert response.status_code == 400
    assert field in response.json()
    purchase.assert_not_called()
    assert not Player.objects.filter(user=user).exists()


def test_first_companion_purchase_spends_wallet_and_auto_equips(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    WalletService().award(
        player=player, amount=150, reason="test_seed", award_key="test-seed:white"
    )
    client = authenticated_client(user)

    purchase = client.post(
        "/api/shop/catalog/purchase/",
        {"kind": "companion", "slug": "white"},
        format="json",
    )

    assert purchase.status_code == 201
    assert Entitlement.objects.filter(player=player, kind="companion", slug="white").exists()
    assert Wallet.objects.get(player=player).balance == 0
    assert CoinTransaction.objects.filter(
        player=player,
        amount=-150,
        reason="shop_purchase",
        award_key=f"shop:companion:white:{player.id}",
    ).exists()
    assert purchase.json()["shop"]["active_companion"] == "white"
    assert PlayerLoadout.objects.get(player=player).active_companion_slug == "white"
    assert companion_by_slug(purchase.json()["shop"], "white")["owned"] is True


def test_second_companion_purchase_does_not_auto_equip(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    WalletService().award(player=player, amount=300, reason="test_seed", award_key="test-seed:both")
    client = authenticated_client(user)

    client.post(
        "/api/shop/catalog/purchase/", {"kind": "companion", "slug": "white"}, format="json"
    )
    purchase = client.post(
        "/api/shop/catalog/purchase/", {"kind": "companion", "slug": "black"}, format="json"
    )

    assert purchase.status_code == 201
    assert Entitlement.objects.filter(player=player, kind="companion", slug="black").exists()
    assert PlayerLoadout.objects.get(player=player).active_companion_slug == "white"

    equip = client.post(
        "/api/player/loadout/companion/",
        {"kind": "companion", "slug": "black"},
        format="json",
    )

    assert equip.status_code == 200
    assert equip.json()["active_companion"] == "black"
    assert PlayerLoadout.objects.get(player=player).active_companion_slug == "black"


def test_equipping_companion_only_changes_companion_loadout(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    Entitlement.objects.create(player=player, kind="companion", slug="white")
    Entitlement.objects.create(player=player, kind="companion", slug="black")
    PlayerLoadout.objects.create(
        player=player,
        active_companion_slug="white",
    )

    equip = ShopService().equip(player=player, kind="companion", slug="black")

    assert equip["active_companion"] == "black"
    record = PlayerLoadout.objects.get(player=player)
    assert record.active_companion_slug == "black"


def test_repeat_companion_purchase_is_idempotent_and_does_not_double_charge(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    WalletService().award(
        player=player, amount=300, reason="test_seed", award_key="test-seed:repeat"
    )
    client = authenticated_client(user)

    first = client.post(
        "/api/shop/catalog/purchase/",
        {"kind": "companion", "slug": "blue"},
        format="json",
    )
    second = client.post(
        "/api/shop/catalog/purchase/",
        {"kind": "companion", "slug": "blue"},
        format="json",
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert Wallet.objects.get(player=player).balance == 150
    assert Entitlement.objects.filter(player=player, kind="companion", slug="blue").count() == 1
    assert (
        CoinTransaction.objects.filter(
            player=player,
            amount=-150,
            reason="shop_purchase",
            award_key=f"shop:companion:blue:{player.id}",
        ).count()
        == 1
    )


def test_unknown_shop_kind_is_rejected(db, django_user_model):
    user = make_user(django_user_model)
    client = authenticated_client(user)

    response = client.post(
        "/api/shop/catalog/purchase/",
        {"kind": "weapon", "slug": "blue"},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["kind"] == "Unknown shop item kind 'weapon'."


def test_disabled_shop_keeps_catalog_visible_and_blocks_purchase(db, django_user_model):
    FeatureFlag.objects.create(
        key="shop-purchases",
        label="Shop purchases",
        enabled=False,
    )
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    WalletService().award(
        player=player,
        amount=150,
        reason="test_seed",
        award_key="test-seed:disabled-shop",
    )
    client = authenticated_client(user)

    catalog = client.get("/api/shop/catalog/")
    purchase = client.post(
        "/api/shop/catalog/purchase/",
        {"kind": "companion", "slug": "white"},
        format="json",
    )

    assert catalog.status_code == 200
    assert catalog.json()["purchases_enabled"] is False
    assert catalog.json()["items"]
    assert purchase.status_code == 403
    assert not Entitlement.objects.filter(player=player, slug="white").exists()
    assert Wallet.objects.get(player=player).balance == 150
