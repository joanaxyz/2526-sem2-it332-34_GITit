"""Bust the cached descriptor map whenever an asset or its sprites change."""

from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from assets.descriptors import clear_descriptor_cache
from assets.models import Asset, AssetSprite, RelicAsset


@receiver(post_save, sender=Asset)
@receiver(post_delete, sender=Asset)
@receiver(post_save, sender=AssetSprite)
@receiver(post_delete, sender=AssetSprite)
@receiver(post_save, sender=RelicAsset)
@receiver(post_delete, sender=RelicAsset)
def _invalidate_descriptor_cache(**_kwargs) -> None:
    clear_descriptor_cache()
