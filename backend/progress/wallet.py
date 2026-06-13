from django.db import IntegrityError, models, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from progress.models import CoinTransaction, Wallet


class WalletService:
    def award(self, *, user, amount: int, reason: str, award_key: str) -> bool:
        """Credit GitCoins once per (user, award_key).

        Returns True when newly awarded, False when this key already paid out.
        Safe to call unconditionally from completion flows.
        """
        if amount <= 0:
            return False
        with transaction.atomic():
            try:
                # Inner savepoint so a duplicate award does not poison the
                # caller's surrounding transaction.
                with transaction.atomic():
                    CoinTransaction.objects.create(
                        user=user, amount=amount, reason=reason, award_key=award_key
                    )
            except IntegrityError:
                return False
            Wallet.objects.get_or_create(user=user)
            Wallet.objects.filter(user=user).update(
                balance=models.F("balance") + amount, updated_at=timezone.now()
            )
        return True

    def summary(self, *, user) -> dict:
        wallet = Wallet.objects.filter(user=user).only("balance").first()
        recent = [
            {
                "amount": entry.amount,
                "reason": entry.reason,
                "created_at": entry.created_at,
            }
            for entry in CoinTransaction.objects.filter(user=user)[:10]
        ]
        return {"balance": wallet.balance if wallet else 0, "recent": recent}

    def spend(self, *, user, amount: int, reason: str, award_key: str) -> bool:
        """Debit GitCoins once per (user, award_key).

        Returns True when a new debit was written, False when the same debit
        key already exists. Raises ValidationError when the wallet cannot cover
        the purchase.
        """
        if amount <= 0:
            return False
        with transaction.atomic():
            wallet, _created = Wallet.objects.select_for_update().get_or_create(user=user)
            try:
                with transaction.atomic():
                    CoinTransaction.objects.create(
                        user=user,
                        amount=-amount,
                        reason=reason,
                        award_key=award_key,
                    )
            except IntegrityError:
                return False
            if wallet.balance < amount:
                raise ValidationError({"balance": "Insufficient GitCoins."})
            Wallet.objects.filter(pk=wallet.pk).update(
                balance=models.F("balance") - amount,
                updated_at=timezone.now(),
            )
        return True
