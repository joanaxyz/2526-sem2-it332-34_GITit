from adventures.models import (
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from common.constants import SESSION_STATUS_ABANDONED


class TierVariantSelectionService:
    """Picks a variant of one tier wave, rotating retries within that wave.

    Mirrors challenges.services.variants.VariantSelectionService: the first
    pick is the wave's first variant in authored order (not random), and a
    retry prefers a variant the learner has not seen in this wave.
    """

    def select_variant(
        self,
        *,
        player,
        wave: AdventureLevelTierWave,
        prior_run: AdventureLevelTierRun | None = None,
        published_variants: list[AdventureLevelTierWaveVariant] | None = None,
        tried_variant_keys: set[str] | None = None,
    ) -> AdventureLevelTierWaveVariant | None:
        variants = (
            published_variants if published_variants is not None else self._published_variants(wave)
        )
        variants = [variant for variant in variants if not variant.is_transfer]
        if not variants:
            return None
        if prior_run is None:
            return variants[0]
        prior_key = self.variant_identity(prior_run.selected_variant)
        tried_keys = tried_variant_keys if tried_variant_keys is not None else set()
        for variant in variants:
            identity = self.variant_identity(variant)
            if identity != prior_key and identity not in tried_keys:
                return variant
        for variant in variants:
            if self.variant_identity(variant) != prior_key:
                return variant
        return variants[0]

    def changed_between(self, *, prior, current) -> bool:
        if prior is None or current is None:
            return False
        return self.variant_identity(prior) != self.variant_identity(current)

    def is_loopback_from_keys(
        self,
        *,
        variants: list[AdventureLevelTierWaveVariant],
        selected_variant,
        tried_keys: set[str],
    ) -> bool:
        if len(variants) <= 1:
            return False
        available = {self.variant_identity(variant) for variant in variants}
        return (
            len(tried_keys.intersection(available)) >= len(available)
            and self.variant_identity(selected_variant) in tried_keys
        )

    def variant_identity(self, variant) -> str:
        return variant.semantic_key or f"id:{variant.id}"

    def _published_variants(
        self, wave: AdventureLevelTierWave
    ) -> list[AdventureLevelTierWaveVariant]:
        return list(
            AdventureLevelTierWaveVariant.objects.filter(
                wave=wave, is_published=True, is_transfer=False
            ).order_by("sort_order", "semantic_key", "id")
        )

    def _tried_variant_keys(self, *, player, wave: AdventureLevelTierWave) -> set[str]:
        variant_ids = (
            # Abandoned runs are excluded so variant rotation behaves exactly
            # as when they were deleted.
            AdventureLevelTierRun.objects.filter(player=player, current_wave=wave)
            .exclude(status=SESSION_STATUS_ABANDONED)
            .values_list("selected_variant_id", flat=True)
            .distinct()
        )
        return {
            self.variant_identity(variant)
            for variant in AdventureLevelTierWaveVariant.objects.filter(id__in=variant_ids)
        }
