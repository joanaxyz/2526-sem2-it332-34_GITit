"""Asset-domain services that don't belong on the read-only descriptor path."""

from __future__ import annotations

from assets.models import Asset

# The tag marking the default kit (Blue + the starter tower pieces) that every
# player owns from the start. Mirrors ``assets/seed_data`` and ``assets/tags.py``.
DEFAULT_KIT_TAG = "arcane-spire"


def default_kit_assets():
    """Published official assets that make up the default Arcane Spire kit.

    Filtered in Python (not via a JSONField ``__contains`` lookup) so it behaves
    identically on every database backend. The set is tiny.
    """
    official = Asset.objects.filter(is_published=True, owner__isnull=True)
    return [asset for asset in official if DEFAULT_KIT_TAG in (asset.tags or [])]


def grant_default_assets(user) -> int:
    """Register the default Arcane Spire kit into a user's asset registry.

    Idempotent: re-running only adds entitlements that are missing, so it's safe
    on sign-up and as a backfill. Returns the number of new entitlements created.
    """
    # Imported here to avoid an app-load import cycle (marketplace imports assets).
    from marketplace.models import ITEM_ASSET, Entitlement

    created = 0
    for asset in default_kit_assets():
        _entitlement, was_created = Entitlement.objects.get_or_create(
            user=user,
            asset=asset,
            defaults={"item_kind": ITEM_ASSET},
        )
        created += int(was_created)
    return created
