from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from assets.models import KIND_RELIC
from authoring.models import VISIBILITY_CHOICES, VISIBILITY_PRIVATE

STATUS_DRAFT = "draft"
STATUS_PUBLISHED = "published"
STATUS_ARCHIVED = "archived"
ARCHIVE_STATUSES = [
    (STATUS_DRAFT, "Draft"),
    (STATUS_PUBLISHED, "Published"),
    (STATUS_ARCHIVED, "Archived"),
]

# A user has two distinct design surfaces:
#   - `personal`: their own creation, publishable + shareable to everyone.
#   - `official_fork`: a private copy of the official Archive they tweak; never
#     publishable/shareable, visible only to them.
ORIGIN_PERSONAL = "personal"
ORIGIN_OFFICIAL_FORK = "official_fork"
ARCHIVE_ORIGINS = [
    (ORIGIN_PERSONAL, "Personal"),
    (ORIGIN_OFFICIAL_FORK, "Official fork"),
]

# Every relic placement is decor or one of the three playable kinds. The kind
# lives on the placement (not the relic asset) since one relic art serves any.
RELIC_KIND_NORMAL = "normal"
RELIC_KIND_ADVENTURE = "adventure"
RELIC_KIND_CHALLENGE = "challenge"
RELIC_KIND_TOME = "tome"
INTERACTABLE_RELIC_KINDS = {
    RELIC_KIND_ADVENTURE,
    RELIC_KIND_CHALLENGE,
    RELIC_KIND_TOME,
}
RELIC_KIND_CHOICES = [
    (RELIC_KIND_NORMAL, "Normal"),
    (RELIC_KIND_ADVENTURE, "Adventure"),
    (RELIC_KIND_CHALLENGE, "Challenge"),
    (RELIC_KIND_TOME, "Tome"),
]


class ArchiveDesign(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="archive_designs",
        on_delete=models.CASCADE,
    )
    source_design = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="remixes",
        on_delete=models.SET_NULL,
    )
    visibility = models.CharField(
        max_length=10, choices=VISIBILITY_CHOICES, default=VISIBILITY_PRIVATE
    )
    status = models.CharField(max_length=16, choices=ARCHIVE_STATUSES, default=STATUS_DRAFT)
    origin = models.CharField(max_length=16, choices=ARCHIVE_ORIGINS, default=ORIGIN_PERSONAL)
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "slug"], name="unique_archive_design_slug_per_owner"
            ),
            models.UniqueConstraint(
                fields=["owner"],
                condition=models.Q(is_active=True),
                name="unique_active_archive_design_per_owner",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "status"], name="archive_owner_status_idx"),
            models.Index(fields=["visibility", "status"], name="archive_vis_status_idx"),
        ]

    def __str__(self) -> str:
        return f"ArchiveDesign({self.slug})"


class RelicPlacement(models.Model):
    """One relic floating freely on an Archive canvas.

    Replaces the old TowerPieceInstance + ArtifactPlacement split: a relic is a
    single free-positioned asset that carries its playable ``kind`` and (for
    interactable kinds) the bound content. ``chapter_index`` groups relics into
    the chapter they belong to; for the official Archive this is the curriculum
    Chapter id, so the fork overlay can rejoin live content.
    """

    archive_design = models.ForeignKey(
        ArchiveDesign, related_name="relics", on_delete=models.CASCADE
    )
    relic_asset = models.ForeignKey("assets.Asset", on_delete=models.PROTECT)
    chapter_index = models.PositiveIntegerField(default=0)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    scale = models.FloatField(default=1)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    rotation = models.FloatField(default=0)
    z_index = models.IntegerField(default=0)
    kind = models.CharField(
        max_length=16, choices=RELIC_KIND_CHOICES, default=RELIC_KIND_NORMAL
    )
    content_definition = models.ForeignKey(
        "authoring.ContentDefinition",
        null=True,
        blank=True,
        related_name="relic_placements",
        on_delete=models.PROTECT,
    )
    # Per-placement overrides of the relic asset's default regions. Empty falls
    # back to the asset defaults at render time.
    interactive_viewbox = models.JSONField(default=dict, blank=True)
    landing_viewbox = models.JSONField(default=dict, blank=True)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["archive_design_id", "chapter_index", "z_index", "id"]
        indexes = [
            models.Index(
                fields=["archive_design", "chapter_index"],
                name="relic_design_chapter_idx",
            )
        ]

    def __str__(self) -> str:
        return f"RelicPlacement({self.archive_design_id}:{self.kind})"

    def clean(self) -> None:
        super().clean()
        if self.relic_asset_id and self.relic_asset.kind != KIND_RELIC:
            raise ValidationError({"relic_asset": "Relics must use relic assets."})
        if self.scale <= 0:
            raise ValidationError({"scale": "Scale must be greater than zero."})
        if self.width < 0 or self.height < 0:
            raise ValidationError({"width": "Relic size cannot be negative."})
        if self.kind in INTERACTABLE_RELIC_KINDS:
            if self.content_definition_id and self.content_definition.kind != self.kind:
                raise ValidationError(
                    {"content_definition": "Content kind must match the relic kind."}
                )
        elif self.content_definition_id:
            raise ValidationError(
                {"content_definition": "Decorative relics cannot bind playable content."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
