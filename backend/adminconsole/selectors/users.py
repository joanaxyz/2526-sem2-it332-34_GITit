"""Read-model builders for user rows in the admin console."""

from __future__ import annotations

from players.services import get_or_create_player
from progress.wallet import WalletService
from shop.models import Entitlement


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
    player = get_or_create_player(user)
    wallet = WalletService().summary(player=player)
    return {
        **user_brief(user),
        "last_login": user.last_login,
        "wallet": wallet,
        "entitlement_count": Entitlement.objects.filter(player=player).count(),
    }
