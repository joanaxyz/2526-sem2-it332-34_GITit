"""Dashboard overview read model for the admin console."""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from adminconsole.models import AdminActionLog
from common.constants import PLAN_SIGNUP_GRANT
from progress.models import CoinTransaction, Wallet

from .users import user_brief

User = get_user_model()


def admin_overview_payload(*, now=None) -> dict:
    """Return the complete overview response read model."""

    now = now or timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    shop_transactions = CoinTransaction.objects.filter(
        amount__lt=0,
        reason__in=["shop_purchase", "cosmetic_purchase"],
    )
    spent = shop_transactions.aggregate(total=Sum("amount"))["total"] or 0

    return {
        "users": {
            "total": User.objects.count(),
            "new_7d": User.objects.filter(date_joined__gte=week_ago).count(),
            "new_30d": User.objects.filter(date_joined__gte=month_ago).count(),
        },
        "economy": {
            "coins_in_circulation": Wallet.objects.aggregate(total=Sum("balance"))["total"] or 0,
            "coins_spent": abs(spent),
            "signup_grant": PLAN_SIGNUP_GRANT,
        },
        "recent_signups": [
            user_brief(user) for user in User.objects.order_by("-date_joined")[:5]
        ],
        "recent_purchases": [
            {
                "user_id": transaction.player.user_id,
                "username": transaction.player.user.username,
                "amount": transaction.amount,
                "reason": transaction.reason,
                "created_at": transaction.created_at,
            }
            for transaction in shop_transactions.select_related("player__user").order_by("-id")[:5]
        ],
        "recent_admin_actions": [
            {
                "id": log.id,
                "actor": log.actor.username if log.actor_id else None,
                "action": log.action,
                "target_label": log.target_label,
                "created_at": log.created_at,
            }
            for log in AdminActionLog.objects.select_related("actor").order_by("-id")[:8]
        ],
    }
