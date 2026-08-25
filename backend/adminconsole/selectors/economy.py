"""Economy read models for the admin console."""

from __future__ import annotations

from progress.models import CoinTransaction
from progress.wallet import WalletService


def admin_transaction_list_payload(*, user_id=None, limit: int = 200) -> dict:
    limit = min(max(limit, 0), 200)
    queryset = CoinTransaction.objects.select_related("player__user").order_by("-id")
    if user_id:
        queryset = queryset.filter(player__user_id=user_id)
    return {
        "results": [
            {
                "id": transaction.id,
                "user_id": transaction.player.user_id,
                "username": transaction.player.user.username,
                "amount": transaction.amount,
                "reason": transaction.reason,
                "created_at": transaction.created_at,
            }
            for transaction in queryset[:limit]
        ]
    }


def admin_economy_adjustment_payload(*, player, applied: bool) -> dict:
    return {
        "wallet": WalletService().summary(player=player),
        "applied": applied,
    }
