"""Owned, uploadable visual assets — the foundation of the UGC tower platform.

Monsters, characters, and tower artifacts are one family: an :class:`Asset`
(metadata + gameplay config) with one or more :class:`AssetSprite` images. The
image *files* live in media storage (``ImageField`` → path in DB, bytes on
disk/object storage), never as DB blobs, so serving them is HTTP/CDN-cacheable
and never touches query latency.

Frame counts are *counted by the system*: ``AssetSprite.save`` reads the image
with Pillow and derives ``columns``/``rows``/``frame_count`` from the frame cell
size, so an admin (and, later, a user) only uploads a sheet — no manual counts.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

# Asset kinds. Monsters ship first (Phase 1); the rest are the same shape and
# arrive in later phases (characters, draggable tower artifacts, projectiles).
KIND_MONSTER = "monster"
KIND_CHARACTER = "character"
KIND_TOWER_ARTIFACT = "tower_artifact"
KIND_PROJECTILE = "projectile"
ASSET_KINDS = [
    (KIND_MONSTER, "Monster"),
    (KIND_CHARACTER, "Character"),
    (KIND_TOWER_ARTIFACT, "Tower artifact"),
    (KIND_PROJECTILE, "Projectile"),
]

# Sharing model: official content has no owner; user content is private until
# published public/to the store (the gallery + store land in later phases).
VISIBILITY_PRIVATE = "private"
VISIBILITY_PUBLIC = "public"
VISIBILITY_STORE = "store"
ASSET_VISIBILITY = [
    (VISIBILITY_PRIVATE, "Private"),
    (VISIBILITY_PUBLIC, "Public"),
    (VISIBILITY_STORE, "Store"),
]

# Monster tiers (drive default scale/roster role; mirrored in battle/state.py).
TIER_MOB = "mob"
TIER_ELITE = "elite"
TIER_BOSS = "boss"
MONSTER_TIERS = [(TIER_MOB, "Mob"), (TIER_ELITE, "Elite"), (TIER_BOSS, "Boss")]


class Asset(models.Model):
    """A single owned visual asset (sprite set + gameplay config).

    ``config`` carries kind-specific gameplay data so the table stays generic:
    for monsters it holds ``{"tier", "attack": {"kind", "hit_frame", "lunge_px"},
    "metrics": {"foot_offset", "hp_bar_fraction"}}``. Cross-kind display scale is
    first-class (``default_scale``) because levels override it per encounter.
    """

    kind = models.CharField(max_length=20, choices=ASSET_KINDS)
    # null owner = official/seeded content; set owner = user-created.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assets",
    )
    visibility = models.CharField(
        max_length=10, choices=ASSET_VISIBILITY, default=VISIBILITY_PUBLIC
    )
    # GitCoin price when sold in the store; 0 = free. Spent via progress.Wallet.
    price = models.PositiveIntegerField(default=0)

    slug = models.SlugField(unique=True)
    label = models.CharField(max_length=160)
    # Display scale relative to the source frame; a level may override per-encounter.
    default_scale = models.FloatField(default=1.0)
    config = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind", "slug"]
        indexes = [models.Index(fields=["kind", "is_published"])]

    def __str__(self) -> str:
        return f"Asset({self.kind}:{self.slug})"


class AssetSprite(models.Model):
    """One animation/image for an asset, keyed by a free-form ``action`` slug.

    The action set is open (idle/walk/attack/hurt/death/portrait/projectile/…)
    so new "action categories" need no schema change — they are discovered from
    whatever the uploader provides.
    """

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="sprites")
    action = models.CharField(max_length=40)
    image = models.ImageField(upload_to="assets/sprites/")

    # Frame cell size. Leave 0 to auto-treat the sheet as a horizontal strip of
    # square cells (cell = image height) — the common monster case. Grids
    # (e.g. 256×256 characters) set the cell size once.
    frame_width = models.PositiveIntegerField(default=0)
    frame_height = models.PositiveIntegerField(default=0)

    # Derived on save() — never entered by hand.
    columns = models.PositiveIntegerField(default=1)
    rows = models.PositiveIntegerField(default=1)
    frame_count = models.PositiveIntegerField(default=1)

    fps = models.PositiveIntegerField(default=12)
    loops = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["asset", "action"], name="unique_action_per_asset"),
        ]
        ordering = ["asset_id", "action"]

    def __str__(self) -> str:
        return f"AssetSprite({self.asset.slug}.{self.action})"

    def recompute_frames(self) -> None:
        """Read the image and derive cell size + frame grid.

        Best-effort: vector (SVG) or unreadable images fall back to a single
        frame, which is correct for static png/svg artifacts.
        """
        width, height = _image_dimensions(self.image)
        if not width or not height:
            self.columns = self.rows = self.frame_count = 1
            return
        cell_w = self.frame_width or height  # default: square cells, strip layout
        cell_h = self.frame_height or height
        self.frame_width = cell_w
        self.frame_height = cell_h
        self.columns = max(1, width // cell_w)
        self.rows = max(1, height // cell_h)
        self.frame_count = self.columns * self.rows

    def save(self, *args, **kwargs):
        if self.image:
            self.recompute_frames()
        super().save(*args, **kwargs)


def _image_dimensions(image_field) -> tuple[int, int]:
    """(width, height) of a raster image, or (0, 0) if it can't be read."""
    try:
        from PIL import Image
    except ImportError:  # Pillow optional at import time; required to upload.
        return (0, 0)
    try:
        position = image_field.tell() if image_field.closed is False else None
    except (ValueError, AttributeError):
        position = None
    try:
        image_field.open()
        with Image.open(image_field) as img:
            size = img.size
    except Exception:
        return (0, 0)
    finally:
        try:
            image_field.seek(position or 0)
        except (ValueError, AttributeError):
            pass
    return (int(size[0]), int(size[1]))
