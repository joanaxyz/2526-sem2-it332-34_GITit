from django.db import transaction

from adminconsole.services.actions import record_admin_action
from progress.wallet import WalletService


class AdminEconomyService:
    """Staff-initiated GitCoin changes keyed by the caller's stable request id."""

    @transaction.atomic
    def adjust(self, *, actor, player, amount: int, reason: str, request_id) -> bool:
        wallet_service = WalletService()
        before = wallet_service.summary(player=player)
        key = f"admin_adjust:{player.id}:{request_id}"
        if amount > 0:
            applied = wallet_service.award(
                player=player,
                amount=amount,
                reason=reason,
                award_key=key,
            )
        else:
            applied = wallet_service.spend(
                player=player,
                amount=-amount,
                reason=reason,
                award_key=key,
            )
        if applied:
            record_admin_action(
                actor=actor,
                action="economy.adjust",
                target=player,
                before={"wallet": before},
                after={"wallet": wallet_service.summary(player=player)},
                metadata={"amount": amount, "reason": reason},
                request_id=str(request_id),
            )
        return applied
