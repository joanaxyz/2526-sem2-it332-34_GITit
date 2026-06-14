from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from marketplace.access import can_remix, entitlement_kwargs_for
from marketplace.models import LISTING_ACTIVE, Entitlement, StoreListing
from progress.wallet import WalletService


class MarketplaceService:
    @transaction.atomic
    def create_listing(self, *, user, data: dict) -> StoreListing:
        listing = StoreListing(seller=user, **_listing_fields(data))
        item = listing.item
        if item is not None and getattr(item, "owner_id", None) not in {None, user.id} and not user.is_staff:
            raise PermissionDenied("You cannot list an item you do not own.")
        listing.save()
        return listing

    @transaction.atomic
    def update_listing(self, *, user, listing: StoreListing, data: dict) -> StoreListing:
        if listing.seller_id != user.id and not user.is_staff:
            raise PermissionDenied("You do not own this listing.")
        for field, value in _listing_fields(data, partial=True).items():
            setattr(listing, field, value)
        listing.save()
        return listing

    @transaction.atomic
    def purchase(self, *, user, listing: StoreListing) -> dict:
        if listing.status != LISTING_ACTIVE:
            raise PermissionDenied("This listing is not active.")
        item = listing.item
        if item is None:
            raise PermissionDenied("This listing has no item.")
        if not can_remix(user, item) and listing.price == 0:
            raise PermissionDenied("You cannot unlock this item.")
        entitlement_kwargs = entitlement_kwargs_for(item)
        entitlement = Entitlement.objects.filter(user=user, **entitlement_kwargs).first()
        if entitlement is None:
            if listing.price > 0 and getattr(item, "owner_id", None) != user.id:
                WalletService().spend(
                    user=user,
                    amount=listing.price,
                    reason="store_purchase",
                    award_key=f"purchase:{listing.id}:{user.id}",
                )
            entitlement, _created = Entitlement.objects.get_or_create(
                user=user,
                **entitlement_kwargs,
                defaults={"source_listing": listing},
            )
        return {"entitlement": entitlement, "wallet": WalletService().summary(user=user)}


def _listing_fields(data: dict, *, partial: bool = False) -> dict:
    allowed = {
        "item_kind",
        "asset_id",
        "content_definition_id",
        "tower_design_id",
        "price",
        "status",
    }
    fields = {key: data[key] for key in allowed if key in data}
    if not partial:
        fields.setdefault("price", 0)
        fields.setdefault("status", "draft")
    return fields
