"""Read-model builders for user rows in the admin console."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Q

from players.models import Player
from progress.wallet import WalletService
from shop.models import Entitlement

User = get_user_model()


def find_admin_user(user_id):
    try:
        return User.objects.filter(pk=user_id).first()
    except (ValueError, TypeError):
        return None


def admin_user_list_payload(*, query: str = "", limit: int = 100) -> dict:
    limit = min(max(limit, 0), 100)
    queryset = User.objects.all().order_by("-date_joined")
    query = query.strip()
    if query:
        queryset = queryset.filter(Q(username__icontains=query) | Q(email__icontains=query))
    return {"results": [user_brief(user) for user in queryset[:limit]]}


def user_brief(user) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
        "date_joined": user.date_joined,
    }


def user_detail(user) -> dict:
    player = Player.objects.filter(user=user).first()
    wallet = WalletService().summary(player=player) if player else {"balance": 0}
    return {
        **user_brief(user),
        "last_login": user.last_login,
        "wallet": wallet,
        "entitlement_count": (Entitlement.objects.filter(player=player).count() if player else 0),
    }
