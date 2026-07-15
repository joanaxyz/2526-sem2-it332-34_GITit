import logging

import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from payments.models import STATUS_PAID, GitCoinPurchase
from payments.packs import get as get_pack
from players.models import Player
from progress.wallet import WalletService

logger = logging.getLogger(__name__)


class PaymentReconciliationError(RuntimeError):
    pass


class PaymentService:
    """Stripe Checkout orchestration with durable local reconciliation."""

    def _client(self) -> stripe:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe

    def create_checkout_session(
        self, *, player, pack_slug: str, idempotency_key: str
    ) -> dict:
        pack = get_pack(pack_slug)
        if pack is None:
            raise ValidationError({"pack_slug": f"Unknown GitCoin pack '{pack_slug}'."})

        # Persist intent before contacting Stripe. If the process dies after
        # Stripe creates the session, metadata lets the webhook/retry reconnect
        # the paid session to this row instead of orphaning the payment.
        purchase, created = GitCoinPurchase.objects.get_or_create(
            checkout_key=idempotency_key,
            defaults={
                "player": player,
                "pack_slug": pack_slug,
                "coins": pack["coins"],
                "amount_cents": pack["price_cents"],
            },
        )
        if not created and (
            purchase.player_id != player.id
            or purchase.pack_slug != pack_slug
            or purchase.coins != pack["coins"]
            or purchase.amount_cents != pack["price_cents"]
        ):
            raise ValidationError("Checkout idempotency key collision.")
        if purchase.checkout_url and purchase.stripe_session_id:
            return {"checkout_url": purchase.checkout_url}

        session = self._client().checkout.Session.create(
            idempotency_key=idempotency_key,
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": purchase.currency,
                        "product_data": {"name": pack["label"]},
                        "unit_amount": purchase.amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            success_url=f"{settings.FRONTEND_BASE_URL}/shop?tab=gitcoins&checkout=success",
            cancel_url=f"{settings.FRONTEND_BASE_URL}/shop?tab=gitcoins&checkout=cancel",
            metadata={
                "purchase_id": str(purchase.id),
                "player_id": str(player.id),
                "pack_slug": pack_slug,
            },
        )
        purchase.stripe_session_id = session.id
        purchase.checkout_url = session.url or ""
        purchase.save(update_fields=["stripe_session_id", "checkout_url"])
        return {"checkout_url": session.url}

    @transaction.atomic
    def handle_checkout_completed(self, *, session=None, session_id: str | None = None) -> None:
        """Reconcile and award one completed Checkout Session idempotently."""
        if session is None:
            session = {"id": session_id, "metadata": {}}
        resolved_session_id = str(session.get("id") or "")
        if not resolved_session_id:
            raise PaymentReconciliationError("Stripe session id is missing.")

        metadata = session.get("metadata") or {}
        purchase = (
            GitCoinPurchase.objects.select_for_update()
            .filter(stripe_session_id=resolved_session_id)
            .first()
        )
        if purchase is None and metadata.get("purchase_id"):
            purchase = (
                GitCoinPurchase.objects.select_for_update()
                .filter(id=metadata["purchase_id"])
                .first()
            )

        # Last-resort recovery covers a deleted/missed local row while retaining
        # strict pack and player validation from signed Stripe metadata.
        if purchase is None and metadata.get("player_id") and metadata.get("pack_slug"):
            pack = get_pack(str(metadata["pack_slug"]))
            player = Player.objects.filter(id=metadata["player_id"]).first()
            if pack and player:
                purchase, _ = GitCoinPurchase.objects.select_for_update().get_or_create(
                    stripe_session_id=resolved_session_id,
                    defaults={
                        "checkout_key": f"recovered:{resolved_session_id}",
                        "player": player,
                        "pack_slug": str(metadata["pack_slug"]),
                        "coins": pack["coins"],
                        "amount_cents": pack["price_cents"],
                    },
                )

        if purchase is None:
            raise PaymentReconciliationError(
                f"No local purchase can be reconciled for Stripe session {resolved_session_id}."
            )
        if purchase.status == STATUS_PAID:
            return

        amount_total = session.get("amount_total")
        currency = session.get("currency")
        if amount_total is not None and int(amount_total) != purchase.amount_cents:
            raise PaymentReconciliationError("Stripe amount does not match the local purchase.")
        if currency and str(currency).lower() != purchase.currency.lower():
            raise PaymentReconciliationError("Stripe currency does not match the local purchase.")

        if purchase.stripe_session_id not in {None, "", resolved_session_id}:
            raise PaymentReconciliationError("Purchase is already linked to another Stripe session.")
        if not purchase.stripe_session_id:
            purchase.stripe_session_id = resolved_session_id
            purchase.save(update_fields=["stripe_session_id"])

        WalletService().award(
            player=purchase.player,
            amount=purchase.coins,
            reason="gitcoin_purchase",
            award_key=f"stripe:{resolved_session_id}",
        )
        purchase.status = STATUS_PAID
        purchase.completed_at = timezone.now()
        purchase.save(update_fields=["status", "completed_at"])
