"""Import official visual assets from committed source files.

Idempotent: each run upserts the Asset rows and rebuilds their sprites from
``assets/seed_assets``, letting ``AssetSprite.save`` count frames from the image.
Only official assets (``owner=None``) are touched - user uploads are left alone.
"""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from io import BytesIO
from contextlib import ExitStack
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from assets.models import (
    KIND_BATTLE_ARTIFACT,
    KIND_CHARACTER,
    KIND_MONSTER,
    KIND_TOWER_ARTIFACT,
    KIND_TOWER_PIECE,
    Asset,
    AssetSprite,
    TowerPieceAsset,
)
from assets.svg_crop import crop_svg_markup
from assets.seed_data.battle_artifacts import BATTLE_ARTIFACT_SPECS
from assets.seed_data.characters import CHARACTER_SPECS
from assets.seed_data.monsters import LOOPING_ACTIONS, MONSTER_SPECS
from assets.seed_data.tower_pieces import OFFICIAL_TOWER_ARTIFACT_SPECS, OFFICIAL_TOWER_PIECE_SPECS

# All official sprite source files live under backend/assets/seed_assets/ and are
# the single committed source of truth (the frontend renders them from media via
# descriptors; it no longer ships its own copies).
SEED_ASSETS_ROOT = Path(__file__).resolve().parents[2] / "seed_assets"
MONSTERS_ROOT = SEED_ASSETS_ROOT / "monsters"
MONSTERS_ZIP = SEED_ASSETS_ROOT / "monsters.zip"
TOWER_ASSETS_ROOT = SEED_ASSETS_ROOT / "tower_assets"
TOWER_ASSETS_ZIP = SEED_ASSETS_ROOT / "tower_assets.zip"
LEGACY_TOWER_PIECES_ROOT = SEED_ASSETS_ROOT / "tower_pieces"
LEGACY_TOWER_PIECES_ZIP = SEED_ASSETS_ROOT / "tower_pieces.zip"
CHARACTERS_ROOT = SEED_ASSETS_ROOT / "character"
CHARACTERS_ZIP = SEED_ASSETS_ROOT / "character.zip"
# Battle artifacts (e.g. crystal/) each live in their own folder under the seed
# root, alongside character/.
BATTLE_ARTIFACTS_ROOT = SEED_ASSETS_ROOT
BATTLE_ARTIFACTS_ZIP = SEED_ASSETS_ROOT / "battle_artifacts.zip"


class Command(BaseCommand):
    help = "Seed official monster (and future) visual assets from committed sheets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-grant",
            action="store_true",
            help="Don't backfill newly-seeded default-kit assets into existing players' registries.",
        )

    def handle(self, *args, **options):
        with ExitStack() as stack:
            self._monsters_root = stack.enter_context(
                self._asset_source(
                    "monster sprites",
                    MONSTERS_ROOT,
                    MONSTERS_ZIP,
                    nested_name="monsters",
                    required=True,
                )
            )
            self._characters_root = stack.enter_context(
                self._asset_source(
                    "character sprites",
                    CHARACTERS_ROOT,
                    CHARACTERS_ZIP,
                    nested_name="character",
                    required=False,
                )
            )
            self._battle_artifacts_root = stack.enter_context(
                self._asset_source(
                    "battle artifact sprites",
                    BATTLE_ARTIFACTS_ROOT,
                    BATTLE_ARTIFACTS_ZIP,
                    nested_name="battle_artifacts",
                    required=False,
                )
            )
            self._tower_assets_root = stack.enter_context(
                self._asset_source(
                    "tower assets",
                    TOWER_ASSETS_ROOT,
                    TOWER_ASSETS_ZIP,
                    nested_name="tower_assets",
                    required=True,
                    fallback_roots=[LEGACY_TOWER_PIECES_ROOT],
                    fallback_archives=[LEGACY_TOWER_PIECES_ZIP],
                    fallback_nested_names=["tower_pieces"],
                )
            )
            monster_count, monster_stale = self._seed_monsters()
            character_count, character_stale = self._seed_characters()
            artifact_count, artifact_stale = self._seed_battle_artifacts()
            tower_artifact_count, tower_artifact_stale = self._seed_tower_artifacts()
            tower_piece_count, tower_piece_stale = self._seed_tower_pieces()
        self._cleanup_uncompressed_seed_sources()
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded "
                f"{monster_count} monsters ({monster_stale} retired), "
                f"{character_count} characters ({character_stale} retired), "
                f"{artifact_count} battle artifacts ({artifact_stale} retired), "
                f"{tower_artifact_count} tower artifacts ({tower_artifact_stale} retired), "
                f"{tower_piece_count} tower pieces ({tower_piece_stale} retired)."
            )
        )
        if not options.get("skip_grant"):
            self._backfill_default_kit()

    def _backfill_default_kit(self) -> None:
        """Grant the (re)seeded default kit to existing players. Adding a piece to
        the Arcane Spire kit (e.g. the window section / portcullis) would otherwise
        only reach new sign-ups; this keeps existing authors' palettes in sync.
        Idempotent: only missing entitlements are created (see ``grant_default_assets``).
        """
        from django.contrib.auth import get_user_model

        from assets.services import grant_default_assets

        granted = 0
        for user in get_user_model().objects.filter(is_staff=False).iterator():
            granted += grant_default_assets(user)
        self.stdout.write(self.style.SUCCESS(f"Backfilled {granted} default-kit entitlements."))

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
        if not self._characters_root.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping character assets; missing sprite source: {self._characters_root}"
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

    def _seed_battle_artifacts(self) -> tuple[int, int]:
        if not self._battle_artifacts_root.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping battle artifacts; missing sprite source: {self._battle_artifacts_root}"
                )
            )
            return 0, 0

        seeded_slugs: list[str] = []
        for spec in BATTLE_ARTIFACT_SPECS:
            self._seed_battle_artifact(spec)
            seeded_slugs.append(spec["slug"])

        stale = (
            Asset.objects.filter(kind=KIND_BATTLE_ARTIFACT, owner__isnull=True)
            .exclude(slug__in=seeded_slugs)
            .update(is_published=False)
        )
        return len(seeded_slugs), stale

    def _seed_tower_artifacts(self) -> tuple[int, int]:
        seeded_slugs: list[str] = []
        for spec in OFFICIAL_TOWER_ARTIFACT_SPECS:
            self._seed_tower_artifact(spec)
            seeded_slugs.append(spec["slug"])

        stale = (
            Asset.objects.filter(kind=KIND_TOWER_ARTIFACT, owner__isnull=True)
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
                _replace_sprite_file(sprite, f"{slug}__{action}.png", handle)
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
                "tags": spec.get("tags", []),
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
            path = self._characters_root / slug / sprite_spec["file"]
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
                _replace_sprite_file(sprite, f"{slug}__{action}.png", handle)
                sprite.save()

    def _seed_battle_artifact(self, spec: dict) -> None:
        slug = spec["slug"]
        asset, _ = Asset.objects.update_or_create(
            slug=slug,
            defaults={
                "kind": KIND_BATTLE_ARTIFACT,
                "owner": None,
                "label": spec["label"],
                "default_scale": spec.get("scale", 1.0),
                "tags": spec.get("tags", []),
                "config": spec.get("config", {}),
                "is_published": True,
            },
        )

        for old in asset.sprites.all():
            old.image.delete(save=False)
            old.delete()

        for action, sprite_spec in spec["actions"].items():
            path = self._battle_artifacts_root / slug / sprite_spec["file"]
            if not path.exists():
                raise CommandError(f"{slug}: missing battle artifact sprite file {path}")
            sprite = AssetSprite(
                asset=asset,
                action=action,
                frame_width=sprite_spec.get("frame_width", 256),
                frame_height=sprite_spec.get("frame_height", 256),
                fps=sprite_spec["fps"],
                loops=sprite_spec["loops"],
            )
            with path.open("rb") as handle:
                _replace_sprite_file(sprite, f"{slug}__{action}.png", handle)
                sprite.save()

    def _seed_tower_piece(self, spec: dict) -> None:
        path = self._tower_assets_root / spec["svg"]
        if not path.exists():
            raise CommandError(f"{spec['slug']}: missing tower piece SVG {path}")
        raw_svg = path.read_bytes()
        seeded_svg, cropped_view_box = crop_svg_markup(raw_svg)
        view_box = cropped_view_box or spec.get("view_box", "")

        asset, _ = Asset.objects.update_or_create(
            slug=spec["slug"],
            defaults={
                "kind": KIND_TOWER_PIECE,
                "owner": None,
                "label": spec["label"],
                "default_scale": 1.0,
                "tags": spec.get("tags", []),
                "config": spec.get("config", {}),
                "is_published": True,
            },
        )
        TowerPieceAsset.objects.update_or_create(
            asset=asset,
            defaults={
                "piece_type": spec["piece_type"],
                "view_box": view_box,
                "anchors": spec.get("anchors", {}),
                "bounds": spec.get("bounds", {}),
                "interaction_zones": spec.get("interaction_zones", {}),
                "state_variants": spec.get("state_variants", {}),
                "svg_sanitized": True,
            },
        )

        frame_width, frame_height = _view_box_size(view_box)
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

        with BytesIO(seeded_svg) as handle:
            _replace_sprite_file(sprite, f"{spec['slug']}__default.svg", handle)
            sprite.save()

    def _seed_tower_artifact(self, spec: dict) -> None:
        asset, _ = Asset.objects.update_or_create(
            slug=spec["slug"],
            defaults={
                "kind": KIND_TOWER_ARTIFACT,
                "owner": None,
                "label": spec["label"],
                "default_scale": spec.get("scale", 1.0),
                "tags": spec.get("tags", []),
                "config": spec.get("config", {}),
                "is_published": True,
            },
        )
        TowerPieceAsset.objects.filter(asset=asset).delete()

        path = self._tower_assets_root / spec["svg"]
        if not path.exists():
            raise CommandError(f"{spec['slug']}: missing tower artifact SVG {path}")
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

    def _resolve(self, slug: str, filename: str) -> Path:
        # Paths with a slash (projectiles/arrow.png) are relative to the monsters
        # root; bare names live in the monster's own folder.
        if "/" in filename:
            return self._monsters_root / filename
        return self._monsters_root / slug / filename

    def _asset_source(
        self,
        label: str,
        root: Path,
        archive: Path,
        *,
        nested_name: str,
        required: bool,
        fallback_roots: list[Path] | None = None,
        fallback_archives: list[Path] | None = None,
        fallback_nested_names: list[str] | None = None,
    ):
        if archive.exists():
            return _ZipSource(archive, nested_name=nested_name)
        for index, fallback_archive in enumerate(fallback_archives or []):
            if fallback_archive.exists():
                nested = (
                    fallback_nested_names[index]
                    if fallback_nested_names and index < len(fallback_nested_names)
                    else nested_name
                )
                return _ZipSource(fallback_archive, nested_name=nested)
        if root.exists():
            return _StaticSource(root)
        for fallback_root in fallback_roots or []:
            if fallback_root.exists():
                return _StaticSource(fallback_root)
        if required:
            raise CommandError(f"Missing {label}: expected {archive} or {root}")
        return _StaticSource(root)

    def _cleanup_uncompressed_seed_sources(self) -> None:
        """Archives are the committed source of truth.

        If a developer or older seed flow left extracted folders beside the zip,
        remove them after a successful seed so the source tree does not drift or
        bloat. Only known seed folders under ``seed_assets`` are eligible.
        """
        targets: list[Path] = []
        if MONSTERS_ZIP.exists():
            targets.append(MONSTERS_ROOT)
        if CHARACTERS_ZIP.exists():
            targets.append(CHARACTERS_ROOT)
        if TOWER_ASSETS_ZIP.exists():
            targets.extend([TOWER_ASSETS_ROOT, LEGACY_TOWER_PIECES_ROOT])
        if BATTLE_ARTIFACTS_ZIP.exists():
            targets.extend(SEED_ASSETS_ROOT / spec["slug"] for spec in BATTLE_ARTIFACT_SPECS)

        seed_root = SEED_ASSETS_ROOT.resolve()
        for target in targets:
            resolved = target.resolve()
            if not target.exists() or resolved == seed_root or seed_root not in resolved.parents:
                continue
            shutil.rmtree(target)


class _StaticSource:
    def __init__(self, path: Path):
        self.path = path

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _ZipSource:
    def __init__(self, path: Path, *, nested_name: str):
        self.path = path
        self.nested_name = nested_name
        self._tmp: tempfile.TemporaryDirectory | None = None

    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory(prefix="git-it-seed-assets-")
        root = Path(self._tmp.name)
        with zipfile.ZipFile(self.path) as archive:
            root_path = root.resolve()
            for member in archive.infolist():
                target = (root / member.filename).resolve()
                if target != root_path and root_path not in target.parents:
                    raise CommandError(f"Unsafe path in seed archive {self.path}: {member.filename}")
            archive.extractall(root)
        nested = root / self.nested_name
        return nested if nested.exists() else root

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._tmp:
            self._tmp.cleanup()


def _replace_sprite_file(sprite: AssetSprite, filename: str, handle) -> None:
    """Store official seed sprites at deterministic paths.

    Django's storage layer appends a random suffix when the requested filename
    already exists. That is useful for user uploads, but bad for idempotent seed
    data: stale generated files would make every seed run create another copy.
    """
    storage = sprite.image.storage
    target_name = sprite.image.field.generate_filename(sprite, filename)
    previous_name = sprite.image.name

    if previous_name == target_name:
        try:
            with storage.open(target_name, "wb") as target:
                target.write(handle.read())
            return
        except Exception:
            handle.seek(0)

    if previous_name:
        sprite.image.delete(save=False)

    if storage.exists(target_name):
        storage.delete(target_name)

    handle.seek(0)
    sprite.image.save(filename, File(handle), save=False)


def _view_box_size(view_box: str) -> tuple[int, int]:
    try:
        _x, _y, width, height = [float(part) for part in view_box.split()]
    except (TypeError, ValueError):
        return 0, 0
    return max(0, round(width)), max(0, round(height))
