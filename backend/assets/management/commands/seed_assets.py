"""Import official visual assets from committed source files.

Idempotent: each run upserts the Asset rows and rebuilds their sprites from
``assets/seed_assets``, letting ``AssetSprite.save`` count frames from the image.
Only official assets (``owner=None``) are touched — user uploads are left alone.
"""

from __future__ import annotations

from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from assets.models import (
    KIND_CHARACTER,
    KIND_MONSTER,
    KIND_TOWER_PIECE,
    Asset,
    AssetSprite,
    TowerPieceAsset,
)
from assets.seed_data.characters import CHARACTER_SPECS
from assets.seed_data.monsters import LOOPING_ACTIONS, MONSTER_SPECS
from assets.seed_data.tower_pieces import OFFICIAL_TOWER_PIECE_SPECS

MONSTERS_ROOT = Path(__file__).resolve().parents[2] / "seed_assets" / "monsters"
TOWER_PIECES_ROOT = Path(__file__).resolve().parents[2] / "seed_assets" / "tower_pieces"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHARACTERS_ROOT = PROJECT_ROOT / "frontend" / "src" / "assets" / "sprites" / "character"


class Command(BaseCommand):
    help = "Seed official monster (and future) visual assets from committed sheets."

    def handle(self, *args, **options):
        if not MONSTERS_ROOT.exists():
            raise CommandError(f"Missing monster sprite dir: {MONSTERS_ROOT}")
        if not TOWER_PIECES_ROOT.exists():
            raise CommandError(f"Missing tower piece sprite dir: {TOWER_PIECES_ROOT}")

        monster_count, monster_stale = self._seed_monsters()
        character_count, character_stale = self._seed_characters()
        tower_piece_count, tower_piece_stale = self._seed_tower_pieces()
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded "
                f"{monster_count} monsters ({monster_stale} retired), "
                f"{character_count} characters ({character_stale} retired), "
                f"{tower_piece_count} tower pieces ({tower_piece_stale} retired)."
            )
        )

    def _seed_monsters(self) -> tuple[int, int]:
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
        return len(seeded_slugs), stale

    def _seed_characters(self) -> tuple[int, int]:
        if not CHARACTERS_ROOT.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping character assets; missing sprite dir: {CHARACTERS_ROOT}"
                )
            )
            return 0, 0

        seeded_slugs: list[str] = []
        for spec in CHARACTER_SPECS:
            self._seed_character(spec)
            seeded_slugs.append(spec["slug"])

        stale = (
            Asset.objects.filter(kind=KIND_CHARACTER, owner__isnull=True)
            .exclude(slug__in=seeded_slugs)
            .update(is_published=False)
        )
        return len(seeded_slugs), stale

    def _seed_tower_pieces(self) -> tuple[int, int]:
        seeded_slugs: list[str] = []
        for spec in OFFICIAL_TOWER_PIECE_SPECS:
            self._seed_tower_piece(spec)
            seeded_slugs.append(spec["slug"])

        stale = (
            Asset.objects.filter(kind=KIND_TOWER_PIECE, owner__isnull=True)
            .exclude(slug__in=seeded_slugs)
            .update(is_published=False)
        )
        return len(seeded_slugs), stale

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

    def _seed_character(self, spec: dict) -> None:
        slug = spec["slug"]
        asset, _ = Asset.objects.update_or_create(
            slug=slug,
            defaults={
                "kind": KIND_CHARACTER,
                "owner": None,
                "label": spec["label"],
                "default_scale": spec.get("scale", 1.0),
                "config": {
                    "metrics": spec.get("metrics", {}),
                    "random_actions": spec.get("random_actions", []),
                },
                "is_published": True,
            },
        )

        for old in asset.sprites.all():
            old.image.delete(save=False)
            old.delete()

        for action, sprite_spec in spec["actions"].items():
            path = CHARACTERS_ROOT / slug / sprite_spec["file"]
            if not path.exists():
                raise CommandError(f"{slug}: missing character sprite file {path}")
            sprite = AssetSprite(
                asset=asset,
                action=action,
                frame_width=256,
                frame_height=256,
                fps=sprite_spec["fps"],
                loops=sprite_spec["loops"],
            )
            with path.open("rb") as handle:
                sprite.image.save(f"{slug}__{action}.png", File(handle), save=False)
                sprite.save()

    def _seed_tower_piece(self, spec: dict) -> None:
        asset, _ = Asset.objects.update_or_create(
            slug=spec["slug"],
            defaults={
                "kind": KIND_TOWER_PIECE,
                "owner": None,
                "label": spec["label"],
                "default_scale": 1.0,
                "config": {},
                "is_published": True,
            },
        )
        TowerPieceAsset.objects.update_or_create(
            asset=asset,
            defaults={
                "piece_type": spec["piece_type"],
                "view_box": spec.get("view_box", ""),
                "anchors": spec.get("anchors", {}),
                "bounds": spec.get("bounds", {}),
                "interaction_zones": spec.get("interaction_zones", {}),
                "state_variants": spec.get("state_variants", {}),
                "svg_sanitized": True,
            },
        )

        path = TOWER_PIECES_ROOT / spec["svg"]
        if not path.exists():
            raise CommandError(f"{spec['slug']}: missing tower piece SVG {path}")
        frame_width, frame_height = _view_box_size(spec.get("view_box", ""))
        sprite, _ = AssetSprite.objects.get_or_create(
            asset=asset,
            action="default",
            defaults={
                "frame_width": frame_width,
                "frame_height": frame_height,
                "fps": 1,
                "loops": True,
            },
        )
        sprite.frame_width = frame_width
        sprite.frame_height = frame_height
        sprite.fps = 1
        sprite.loops = True

        for old in asset.sprites.exclude(pk=sprite.pk):
            old.image.delete(save=False)
            old.delete()

        with path.open("rb") as handle:
            _replace_sprite_file(sprite, f"{spec['slug']}__default.svg", handle)
            sprite.save()

    @staticmethod
    def _resolve(slug: str, filename: str) -> Path:
        # Paths with a slash (projectiles/arrow.png) are relative to the monsters
        # root; bare names live in the monster's own folder.
        if "/" in filename:
            return MONSTERS_ROOT / filename
        return MONSTERS_ROOT / slug / filename


def _replace_sprite_file(sprite: AssetSprite, filename: str, handle) -> None:
    """Replace sprite bytes without deleting the row before the new file exists."""
    if sprite.image.name:
        try:
            with sprite.image.storage.open(sprite.image.name, "wb") as target:
                target.write(handle.read())
            return
        except Exception:
            handle.seek(0)

    sprite.image.save(filename, File(handle), save=False)


def _view_box_size(view_box: str) -> tuple[int, int]:
    try:
        _x, _y, width, height = [float(part) for part in view_box.split()]
    except (TypeError, ValueError):
        return 0, 0
    return max(0, round(width)), max(0, round(height))
