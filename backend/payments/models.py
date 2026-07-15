from uuid import uuid4

from django.db import models

STATUS_PENDING = "pending"
STATUS_PAID = "paid"
STATUS_FAILED = "failed"
STATUS_CHOICES = [
    (STATUS_PENDING, "Pending"),
    (STATUS_PAID, "Paid"),
    (STATUS_FAILED, "Failed"),
]


class GitCoinPurchase(models.Model):
    """One Stripe Checkout Session for a GitCoin pack.

    Recorded at session-creation time (status=pending) and flipped to paid by
    the webhook, which awards the wallet through the existing idempotent
    WalletService ledger (award_key=f"stripe:{stripe_session_id}").
    """

    player = models.ForeignKey(
        "players.Player",
        related_name="gitcoin_purchases",
        on_delete=models.CASCADE,
    )
    pack_slug = models.CharField(max_length=32)
    coins = models.PositiveIntegerField()
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=8, default="usd")
    checkout_key = models.CharField(max_length=255, unique=True, default=uuid4)
    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    checkout_url = models.URLField(max_length=2048, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["player", "status"], name="gcpurchase_player_status_idx"),
        ]

    def __str__(self) -> str:
        return f"GitCoinPurchase(player={self.player_id}, pack={self.pack_slug}, status={self.status})"
