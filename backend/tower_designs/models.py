import math

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from assets.models import KIND_TOWER_ARTIFACT, KIND_TOWER_PIECE, TOWER_PIECE_LANDING, TOWER_PIECE_SECTION
from authoring.models import VISIBILITY_CHOICES, VISIBILITY_PRIVATE

STATUS_DRAFT = "draft"
STATUS_PUBLISHED = "published"
STATUS_ARCHIVED = "archived"
TOWER_STATUSES = [
    (STATUS_DRAFT, "Draft"),
    (STATUS_PUBLISHED, "Published"),
    (STATUS_ARCHIVED, "Archived"),
]

# A user has two distinct design surfaces:
#   - `personal`: their own creation, publishable + shareable to everyone.
#   - `official_fork`: a private copy of the official tower they tweak; never
#     publishable/shareable, visible only to them.
ORIGIN_PERSONAL = "personal"
ORIGIN_OFFICIAL_FORK = "official_fork"
TOWER_ORIGINS = [
    (ORIGIN_PERSONAL, "Personal"),
    (ORIGIN_OFFICIAL_FORK, "Official fork"),
]

ARTIFACT_ROLE_NORMAL = "normal"
ARTIFACT_ROLE_ADVENTURE = "adventure"
ARTIFACT_ROLE_CHALLENGE = "challenge"
ARTIFACT_ROLE_TOME = "tome"
INTERACTABLE_ARTIFACT_ROLES = {
    ARTIFACT_ROLE_ADVENTURE,
    ARTIFACT_ROLE_CHALLENGE,
    ARTIFACT_ROLE_TOME,
}
ARTIFACT_ROLE_CHOICES = [
    (ARTIFACT_ROLE_NORMAL, "Normal"),
    (ARTIFACT_ROLE_ADVENTURE, "Adventure"),
    (ARTIFACT_ROLE_CHALLENGE, "Challenge"),
    (ARTIFACT_ROLE_TOME, "Tome"),
]

# Tower visuals are a template, not a floor-by-floor design. The crown/spire is
# stored once and the body is stored once, then repeated for every curriculum
# storey at render time.
SPIRE_STOREY_INDEX = 0
STOREY_TEMPLATE_INDEX = 1


class TowerDesign(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="tower_designs",
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
    status = models.CharField(max_length=16, choices=TOWER_STATUSES, default=STATUS_DRAFT)
    origin = models.CharField(max_length=16, choices=TOWER_ORIGINS, default=ORIGIN_PERSONAL)
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
                fields=["owner", "slug"], name="unique_tower_design_slug_per_owner"
            ),
            models.UniqueConstraint(
                fields=["owner"],
                condition=models.Q(is_active=True),
                name="unique_active_tower_design_per_owner",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "status"], name="tower_design_owner_status_idx"),
            models.Index(fields=["visibility", "status"], name="tower_design_vis_idx"),
        ]

    def __str__(self) -> str:
        return f"TowerDesign({self.slug})"


class TowerPieceInstance(models.Model):
    tower_design = models.ForeignKey(TowerDesign, related_name="pieces", on_delete=models.CASCADE)
    piece_asset = models.ForeignKey("assets.Asset", on_delete=models.PROTECT)
    piece_type = models.CharField(max_length=32)
    # Canonical visual group: 0 is the one-off spire/crown, 1 is the repeatable
    # storey template. Older rows may contain live curriculum Storey IDs; read
    # selectors normalize them without destroying user data.
    storey_index = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=0)
    parent_instance = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    transform = models.JSONField(default=dict, blank=True)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["tower_design_id", "sort_order", "id"]
        indexes = [models.Index(fields=["tower_design", "sort_order"], name="tower_piece_design_order_idx")]

    def __str__(self) -> str:
        return f"TowerPieceInstance({self.tower_design_id}:{self.piece_type})"

    def clean(self) -> None:
        super().clean()
        if self.piece_asset_id and self.piece_asset.kind != KIND_TOWER_PIECE:
            raise ValidationError({"piece_asset": "Tower pieces must use tower_piece assets."})
        if self.piece_asset_id:
            piece_detail = getattr(self.piece_asset, "tower_piece", None)
            if piece_detail and self.piece_type != piece_detail.piece_type:
                raise ValidationError({"piece_type": "Piece type must match the selected asset."})
        if self.parent_instance_id and self.parent_instance.tower_design_id != self.tower_design_id:
            raise ValidationError({"parent_instance": "Parent piece must belong to the same design."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class TowerContentBinding(models.Model):
    piece_instance = models.OneToOneField(
        TowerPieceInstance, related_name="content_binding", on_delete=models.CASCADE
    )
    content_definition = models.ForeignKey(
        "authoring.ContentDefinition", related_name="tower_bindings", on_delete=models.PROTECT
    )

    class Meta:
        ordering = ["piece_instance__tower_design_id", "piece_instance__sort_order"]

    def clean(self) -> None:
        super().clean()
        if self.piece_instance_id and self.content_definition_id:
            if self.piece_instance.piece_type != TOWER_PIECE_SECTION:
                raise ValidationError(
                    {"piece_instance": "Legacy content bindings can only target tower sections."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ArtifactPlacement(models.Model):
    tower_design = models.ForeignKey(
        TowerDesign, related_name="artifact_placements", on_delete=models.CASCADE
    )
    target_piece_instance = models.ForeignKey(
        TowerPieceInstance, related_name="artifact_placements", on_delete=models.CASCADE
    )
    artifact_asset = models.ForeignKey("assets.Asset", on_delete=models.PROTECT)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    scale = models.FloatField(default=1)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    rotation = models.FloatField(default=0)
    anchor = models.CharField(max_length=80, blank=True)
    z_index = models.IntegerField(default=0)
    role = models.CharField(
        max_length=16, choices=ARTIFACT_ROLE_CHOICES, default=ARTIFACT_ROLE_NORMAL
    )
    content_definition = models.ForeignKey(
        "authoring.ContentDefinition",
        null=True,
        blank=True,
        related_name="tower_artifact_placements",
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["tower_design_id", "z_index", "id"]

    def clean(self) -> None:
        super().clean()
        if self.target_piece_instance_id and self.target_piece_instance.tower_design_id != self.tower_design_id:
            raise ValidationError({"target_piece_instance": "Target piece must belong to this tower design."})
        if self.artifact_asset_id and self.artifact_asset.kind != KIND_TOWER_ARTIFACT:
            raise ValidationError({"artifact_asset": "Artifact placements require tower_artifact assets."})
        if self.scale <= 0:
            raise ValidationError({"scale": "Scale must be greater than zero."})
        if self.width < 0 or self.height < 0:
            raise ValidationError({"width": "Artifact size cannot be negative."})
        if self.role in INTERACTABLE_ARTIFACT_ROLES:
            self._validate_interactable_role()
        elif self.content_definition_id:
            raise ValidationError(
                {"content_definition": "Normal artifacts cannot bind playable content."}
            )
        self._validate_safe_bounds()

    def _validate_interactable_role(self) -> None:
        if self.content_definition_id and self.content_definition.kind != self.role:
            raise ValidationError(
                {"content_definition": "Content kind must match the interactable artifact role."}
            )
        # No per-piece count, single-kind, or structural caps: the author decides
        # where interactables go. The only role rule is that bound content matches
        # the artifact role.

    def _validate_safe_bounds(self) -> None:
        if not self.target_piece_instance_id:
            return
        detail = getattr(self.target_piece_instance.piece_asset, "tower_piece", None)
        bounds = (getattr(detail, "bounds", None) or {}).get("artifact_safe_bounds") or getattr(detail, "bounds", None) or {}
        required = {"x", "y", "width", "height"}
        if not required.issubset(bounds):
            return
        min_x = float(bounds["x"])
        min_y = float(bounds["y"])
        max_x = min_x + float(bounds["width"])
        max_y = min_y + float(bounds["height"])
        center_inside = min_x <= self.x <= max_x and min_y <= self.y <= max_y
        landing_bottom_on_rail = (
            self.target_piece_instance.piece_type == TOWER_PIECE_LANDING
            and min_x <= self.x <= max_x
            and self._bottom_edge_hits_landing_rail(detail, min_y, max_y)
        )
        if not (center_inside or landing_bottom_on_rail):
            raise ValidationError({"x": "Artifact placement is outside the piece safe bounds."})

    def _bottom_edge_hits_landing_rail(self, detail, min_y: float, max_y: float) -> bool:
        anchors = getattr(detail, "anchors", None) or {}
        rail = anchors.get("walk_rail") if isinstance(anchors, dict) else None
        if not isinstance(rail, dict):
            return False
        try:
            rail_y = (float(rail["y1"]) + float(rail["y2"])) / 2
        except (KeyError, TypeError, ValueError):
            return False
        bottom_y = self.y + self._artifact_vertical_radius()
        return min_y <= bottom_y <= max_y and abs(bottom_y - rail_y) <= 1.0

    def _artifact_vertical_radius(self) -> float:
        width = max(0.0, float(self.width or 0) * float(self.scale or 1))
        height = max(0.0, float(self.height or 0) * float(self.scale or 1))
        radians = math.radians(float(self.rotation or 0))
        return (abs(math.sin(radians)) * width + abs(math.cos(radians)) * height) / 2

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
