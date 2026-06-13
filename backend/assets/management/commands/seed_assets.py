"""Import the official visual assets (monsters today) from committed PNGs.

Idempotent: each run upserts the Asset rows and rebuilds their sprites from
``assets/seed_assets``, letting ``AssetSprite.save`` count frames from the image.
Only official assets (``owner=None``) are touched — user uploads are left alone.
"""

from __future__ import annotations

from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from assets.models import KIND_MONSTER, Asset, AssetSprite
from assets.seed_data.monsters import LOOPING_ACTIONS, MONSTER_SPECS

MONSTERS_ROOT = Path(__file__).resolve().parents[2] / "seed_assets" / "monsters"


class Command(BaseCommand):
    help = "Seed official monster (and future) visual assets from committed sheets."

    def handle(self, *args, **options):
        if not MONSTERS_ROOT.exists():
            raise CommandError(f"Missing monster sprite dir: {MONSTERS_ROOT}")

        seeded_slugs: list[str] = []
        for spec in MONSTER_SPECS:
            self._seed_monster(spec)
            seeded_slugs.append(spec["slug"])

        # Retire official monsters no longer authored; never touch user content.
        stale = (
            Asset.objects.filter(kind=KIND_MONSTER, owner__isnull=True)
            .exclude(slug__in=seeded_slugs)
            .update(is_published=False)
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(seeded_slugs)} monster assets ({stale} retired)."
            )
        )

    def _seed_monster(self, spec: dict) -> None:
        slug = spec["slug"]
        asset, _ = Asset.objects.update_or_create(
            slug=slug,
            defaults={
                "kind": KIND_MONSTER,
                "owner": None,
                "label": spec["label"],
                "default_scale": spec.get("scale", 1.0),
                "config": {
                    "tier": spec["tier"],
                    "attack": spec.get("attack", {}),
                    "metrics": spec.get("metrics", {}),
                },
                "is_published": True,
            },
        )

        # Rebuild sprites from scratch so re-seeding stays clean (old files go too).
        for old in asset.sprites.all():
            old.image.delete(save=False)
            old.delete()

        for action, (filename, fps) in spec["actions"].items():
            path = self._resolve(slug, filename)
            if not path.exists():
                raise CommandError(f"{slug}: missing sprite file {path}")
            sprite = AssetSprite(
                asset=asset, action=action, fps=fps, loops=action in LOOPING_ACTIONS
            )
            with path.open("rb") as handle:
                sprite.image.save(f"{slug}__{action}.png", File(handle), save=False)
                sprite.save()  # recompute_frames reads the stored image

    @staticmethod
    def _resolve(slug: str, filename: str) -> Path:
        # Paths with a slash (projectiles/arrow.png) are relative to the monsters
        # root; bare names live in the monster's own folder.
        if "/" in filename:
            return MONSTERS_ROOT / filename
        return MONSTERS_ROOT / slug / filename
