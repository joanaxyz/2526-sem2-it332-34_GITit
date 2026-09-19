"""Materialise composed drill content into seeded rows.

The composer derives a drill from published curriculum. This module runs it
once per level and upserts the result, so runtime reads rows instead of
re-deriving a catalog-wide scan on every request.

Upsert, never truncate: ``LevelDrillCard`` rows are matched on
``(drill, form_key)``, so re-seeding an unchanged catalog rewrites values in
place and leaves ids - and therefore anything referencing them - alone.
Cards whose form has left the level are removed, because a drill that still
asks about a command the level no longer teaches is worse than no drill.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction
from django.db.models import Prefetch

from adventures.models import (
    AdventureLevel,
    AdventureLevelTierWaveVariant,
    AdventureWaveVariant,
)
from curriculum.models import CommandForm
from drills.models import LevelDrill, LevelDrillCard
from drills.services.composer import DrillCatalog, compose_level_drill

# Written per level rather than per card. Seeding the full catalog is 1200+
# cards; one statement per card is invisible on SQLite and several minutes
# against a pooled Postgres, which is exactly where this has to run.
CARD_UPDATE_FIELDS = (
    "sort_order",
    "command_form",
    "command",
    "intent",
    "base_command",
    "summary",
    "tokens",
    "command_choices",
    "intent_choices",
    "blank",
    "bank",
)


@dataclass
class DrillSeedSummary:
    levels: int = 0
    drills_written: int = 0
    cards_written: int = 0
    cards_removed: int = 0
    empty_levels: int = 0

    def as_line(self) -> str:
        return (
            f"{self.drills_written} drills / {self.cards_written} cards "
            f"across {self.levels} levels "
            f"({self.cards_removed} stale cards removed, "
            f"{self.empty_levels} levels with nothing to drill)"
        )


def _form_ids_by_key(keys: set[str], catalog: DrillCatalog | None = None) -> dict[str, int]:
    """Resolve card keys back to their CommandForm, for provenance.

    The key is ``<skill-slug>/<form-slug>``; keeping the FK means the admin
    can jump from a drill card to the catalog entry it came from, and a
    retired form is visible as a null rather than a silent orphan.
    """
    if not keys:
        return {}
    forms = (
        catalog.forms
        if catalog is not None
        else CommandForm.objects.select_related("command_skill").only(
            "id", "slug", "command_skill__slug"
        )
    )
    resolved: dict[str, int] = {}
    for form in forms:
        key = f"{form.command_skill.slug}/{form.slug}"
        if key in keys:
            resolved.setdefault(key, form.id)
    return resolved


@transaction.atomic
def seed_level_drill(
    level: AdventureLevel,
    summary: DrillSeedSummary,
    catalog: DrillCatalog | None = None,
) -> LevelDrill | None:
    content = compose_level_drill(level, catalog)
    cards = content["cards"]
    summary.levels += 1

    if not cards:
        # Nothing to rehearse. Remove any drill seeded from earlier content
        # rather than leaving a stale one advertised on the level map.
        summary.empty_levels += 1
        LevelDrill.objects.filter(adventure_level=level).delete()
        return None

    sequence = content["sequence"] or {}
    drill, created = LevelDrill.objects.update_or_create(
        adventure_level=level,
        defaults={
            "sequence_label": sequence.get("label", "") or "",
            "sequence_task": sequence.get("task", "") or "",
            "sequence_steps": sequence.get("steps", []) or [],
            "is_published": True,
        },
    )
    summary.drills_written += 1

    form_ids = _form_ids_by_key({card["key"] for card in cards}, catalog)
    rows = [
        LevelDrillCard(
            drill=drill,
            form_key=card["key"],
            sort_order=index,
            command_form_id=form_ids.get(card["key"]),
            command=card["command"],
            intent=card["intent"],
            base_command=card["base_command"],
            summary=card["summary"],
            tokens=card["tokens"],
            command_choices=card["command_choices"],
            intent_choices=card["intent_choices"],
            blank=card["blank"] or {},
            bank=card["bank"],
        )
        for index, card in enumerate(cards)
    ]
    LevelDrillCard.objects.bulk_create(
        rows,
        update_conflicts=True,
        unique_fields=["drill", "form_key"],
        update_fields=list(CARD_UPDATE_FIELDS),
    )
    seen_keys = [card["key"] for card in cards]
    summary.cards_written += len(seen_keys)

    # A drill created in this pass cannot have stale cards, and the
    # count+delete pair is two network round trips per level against a
    # pooled Postgres - worth skipping on the common first-seed path.
    if not created:
        stale = drill.cards.exclude(form_key__in=seen_keys)
        removed, _ = stale.delete()
        summary.cards_removed += removed
    return drill


def seed_all_level_drills(*, level_ids: list[int] | None = None) -> DrillSeedSummary:
    summary = DrillSeedSummary()
    # One catalog read for the whole run: composing a level needs the
    # published command list twice, and re-reading it 261 times is the
    # difference between seconds and minutes over a pooled connection.
    catalog = DrillCatalog.load()
    # Prefetch the whole wave tree in a handful of queries rather than a
    # handful per level. Variants carry large initial/target repository
    # JSON that the drill never reads, so only the authored solution is
    # loaded - prefetching the full rows would pull hundreds of megabytes.
    variant_fields = ("id", "wave_id", "slug", "label", "solution_commands", "is_published")
    levels = (
        AdventureLevel.objects.filter(is_published=True)
        .select_related("chapter")
        .prefetch_related(
            "tiers",
            "tiers__waves",
            Prefetch(
                "tiers__waves__variants",
                queryset=AdventureLevelTierWaveVariant.objects.only(*variant_fields),
            ),
            "waves",
            Prefetch(
                "waves__variants",
                queryset=AdventureWaveVariant.objects.only(*variant_fields),
            ),
        )
    )
    if level_ids:
        levels = levels.filter(id__in=level_ids)
    for level in levels.order_by("chapter__sort_order", "sort_order", "id"):
        seed_level_drill(level, summary, catalog)
    return summary
