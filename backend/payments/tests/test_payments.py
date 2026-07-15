
from rest_framework.test import APIClient

from payments.models import STATUS_PAID, GitCoinPurchase
from payments.services import PaymentService
from players.services import get_or_create_player
from progress.models import CoinTransaction, Wallet


def make_user(django_user_model, username: str = "buyer"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


class _FakeSession:
    def __init__(self, id: str, url: str):
        self.id = id
        self.url = url


def test_packs_endpoint_lists_the_catalog(db, django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/payments/packs/")

    assert response.status_code == 200
    slugs = {item["slug"] for item in response.json()["items"]}
    assert {"starter", "adventurer", "hero"} <= slugs


def test_checkout_session_rejects_unknown_pack(db, django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post("/api/payments/checkout/", {"pack_slug": "nonexistent"}, format="json")

    assert response.status_code == 400


def test_checkout_session_creates_a_pending_purchase_record(db, django_user_model, monkeypatch):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return _FakeSession(id="cs_test_123", url="https://checkout.stripe.com/pay/cs_test_123")

    monkeypatch.setattr("payments.services.core.stripe.checkout.Session.create", fake_create)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/payments/checkout/",
        {"pack_slug": "starter"},
        format="json",
        HTTP_IDEMPOTENCY_KEY="checkout-test-key",
    )

    assert response.status_code == 201
    assert captured["idempotency_key"] == "checkout-test-key"
    assert response.json()["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_123"
    purchase = GitCoinPurchase.objects.get(stripe_session_id="cs_test_123")
    assert purchase.player_id == player.id
    assert purchase.coins == 150
    assert purchase.status == "pending"


def test_handle_checkout_completed_awards_wallet_once(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    GitCoinPurchase.objects.create(
        player=player,
        pack_slug="starter",
        coins=150,
        amount_cents=99,
        stripe_session_id="cs_test_abc",
    )

    PaymentService().handle_checkout_completed(session_id="cs_test_abc")
    # Re-delivered webhook for the same session must not double-pay.
    PaymentService().handle_checkout_completed(session_id="cs_test_abc")

    assert Wallet.objects.get(player=player).balance == 150
    assert CoinTransaction.objects.filter(
        player=player, reason="gitcoin_purchase", award_key="stripe:cs_test_abc"
    ).count() == 1
    assert GitCoinPurchase.objects.get(stripe_session_id="cs_test_abc").status == STATUS_PAID


def test_webhook_view_verifies_signature_and_awards(db, django_user_model, monkeypatch):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    GitCoinPurchase.objects.create(
        player=player,
        pack_slug="starter",
        coins=150,
        amount_cents=99,
        stripe_session_id="cs_test_webhook",
    )
    fake_event = {
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test_webhook"}},
    }
    monkeypatch.setattr(
        "payments.views.stripe.Webhook.construct_event", lambda payload, sig, secret: fake_event
    )
    client = APIClient()

    response = client.post(
        "/api/payments/webhook/",
        data=b"{}",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="test-sig",
    )

    assert response.status_code == 200
    assert Wallet.objects.get(player=player).balance == 150
