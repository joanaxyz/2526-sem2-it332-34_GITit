"""Read-model builders for user rows in the admin console."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Q

from players.models import Player
from progress.services import MetricsService
from progress.services.kpi_range import ALL_TIME, KpiRange
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


def admin_user_kpis_payload(user, *, kpi_range: KpiRange = ALL_TIME) -> dict:
    """Per-user learning KPIs for the admin detail panel.

    Uses the same KPI scope as the admin dashboard (staff accounts excluded,
    optional date range) and the same MetricsService code path, so RTA cannot
    drift between them. A staff account therefore shows no KPI data.
    """
    player = Player.objects.filter(user=user).first()
    if player is None:
        return {"has_data": False, "kpis": None, "modules": []}
    summary = MetricsService().admin_player_performance_summary(player=player, kpi_range=kpi_range)
    kpis = summary["kpis"]
    return {
        "has_data": summary["completed_sessions"] > 0 or kpis["rta"]["denominator"] > 0,
        "kpis": kpis,
        "modules": summary["modules"],
    }
