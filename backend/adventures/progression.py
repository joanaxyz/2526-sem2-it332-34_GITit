"""Runtime variant selection for one adventure wave."""

from __future__ import annotations

from adventures.models import AdventureRunWave


def select_wave_variant(*, player, wave):
    """Least-recently-used published variant owned by this wave for this player."""
    variants = list(wave.variants.filter(is_published=True).order_by("semantic_key", "id"))
    if not variants:
        return None
    recent = (
        AdventureRunWave.objects.filter(
            run__player=player, wave=wave, selected_variant__isnull=False
        )
        .order_by("-id")
        .values_list("selected_variant_id", flat=True)
    )
    recency: dict[int, int] = {}
    for rank, variant_id in enumerate(recent):
        if variant_id is not None:
            recency.setdefault(variant_id, rank)

    def sort_key(variant):
        rank = recency.get(variant.id)
        if rank is None:
            return (0, variant.id)
        return (1, -rank)

    variants.sort(key=sort_key)
    return variants[0]
