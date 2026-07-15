import uuid

from rest_framework.exceptions import ValidationError

from progress.wallet import WalletService


class AdminEconomyService:
    """Staff-initiated GitCoin grants/deductions, with a fresh idempotency key
    per call (each admin action is its own, once-only ledger entry)."""

    def adjust(self, *, player, amount, reason) -> None:
        try:
            amount = int(amount)
        except (TypeError, ValueError) as exc:
            raise ValidationError({"amount": "A whole-number amount is required."}) from exc
        if amount == 0:
            raise ValidationError({"amount": "Amount must be non-zero."})
        reason = (reason or "admin_adjust").strip()[:64]
        key = f"admin_adjust:{player.id}:{uuid.uuid4()}"
        if amount > 0:
            WalletService().award(player=player, amount=amount, reason=reason, award_key=key)
        else:
            WalletService().spend(player=player, amount=-amount, reason=reason, award_key=key)
