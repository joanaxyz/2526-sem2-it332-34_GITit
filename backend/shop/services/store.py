from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from progress.wallet import WalletService
from shop.access import has_any_companion, owns_item
from shop.catalog import KIND_COMPANION, KIND_STORY, SHOP_KINDS, is_default
from shop.catalog import get as catalog_item
from shop.models import Entitlement, PlayerLoadout


class ShopService:
    @transaction.atomic
    def purchase(self, *, player, kind: str, slug: str) -> dict:
        meta = self._require(kind, slug)
        if not owns_item(player=player, kind=kind, slug=slug):
            # A brand-new player owns no companion at all - checked before the
            # entitlement below exists, so this is only true for their first buy.
            is_first_companion = kind == KIND_COMPANION and not has_any_companion(player)
            price = int(meta.get("price") or 0)
            if price > 0:
                WalletService().spend(
                    player=player,
                    amount=price,
                    reason="shop_purchase",
                    award_key=f"shop:{kind}:{slug}:{player.id}",
                )
            if not is_default(kind, slug):
                Entitlement.objects.get_or_create(player=player, kind=kind, slug=slug)
            if is_first_companion:
                # Skip the extra "now equip it" click: your first adventurer is
                # immediately playable.
                record, _ = PlayerLoadout.objects.get_or_create(player=player)
                record.active_companion_slug = slug
                record.save()
        return {"owned": True, "wallet": WalletService().summary(player=player)}

    @transaction.atomic
    def equip(self, *, player, kind: str, slug: str) -> dict:
        self._require(kind, slug)
        if kind == KIND_STORY:
            raise ValidationError({"kind": "Stories are selected by entering the story, not equipped."})
        if not owns_item(player=player, kind=kind, slug=slug):
            raise PermissionDenied("You do not own this shop item.")
        record, _ = PlayerLoadout.objects.get_or_create(player=player)
        record.active_companion_slug = slug
        record.save()
        return {"active_companion": record.active_companion_slug}

    def _require(self, kind: str, slug: str) -> dict:
        if kind not in SHOP_KINDS:
            raise ValidationError({"kind": f"Unknown shop item kind '{kind}'."})
        meta = catalog_item(kind, slug)
        if meta is None:
            raise ValidationError({"slug": f"Unknown {kind} '{slug}'."})
        return meta
