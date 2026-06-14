import pytest
from rest_framework.test import APIClient

from assets.models import KIND_TOWER_ARTIFACT, Asset
from marketplace.models import Entitlement, StoreListing
from progress.models import CoinTransaction, Wallet
from progress.wallet import WalletService


def make_user(django_user_model, username="student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


@pytest.mark.django_db
def test_purchase_debits_wallet_and_grants_entitlement_once(django_user_model):
    seller = make_user(django_user_model, "seller")
    buyer = make_user(django_user_model, "buyer")
    asset = Asset.objects.create(
        owner=seller,
        kind=KIND_TOWER_ARTIFACT,
        visibility="store",
        slug="banner",
        label="Banner",
        is_published=True,
    )
    listing = StoreListing.objects.create(
        seller=seller,
        item_kind="asset",
        asset=asset,
        price=40,
        status="active",
    )
    WalletService().award(user=buyer, amount=100, reason="seed", award_key="seed:buyer")
    client = APIClient()
    client.force_authenticate(user=buyer)

    first = client.post(f"/api/marketplace/listings/{listing.id}/purchase/")
    second = client.post(f"/api/marketplace/listings/{listing.id}/purchase/")

    assert first.status_code == 201
    assert second.status_code == 201
    assert Entitlement.objects.filter(user=buyer, asset=asset).count() == 1
    assert Wallet.objects.get(user=buyer).balance == 60
    assert CoinTransaction.objects.filter(user=buyer, amount=-40, reason="store_purchase").count() == 1


@pytest.mark.django_db
def test_store_purchase_rejects_insufficient_balance(django_user_model):
    seller = make_user(django_user_model, "seller")
    buyer = make_user(django_user_model, "buyer")
    asset = Asset.objects.create(
        owner=seller,
        kind=KIND_TOWER_ARTIFACT,
        visibility="store",
        slug="expensive-banner",
        label="Expensive Banner",
        is_published=True,
    )
    listing = StoreListing.objects.create(
        seller=seller,
        item_kind="asset",
        asset=asset,
        price=40,
        status="active",
    )
    client = APIClient()
    client.force_authenticate(user=buyer)

    response = client.post(f"/api/marketplace/listings/{listing.id}/purchase/")

    assert response.status_code == 400
    assert not Entitlement.objects.filter(user=buyer, asset=asset).exists()
