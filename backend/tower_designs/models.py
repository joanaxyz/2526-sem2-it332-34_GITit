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
    # Which storey (floor) this piece belongs to. Pieces group into floors so the
    # editor can show storey bands and the author knows which storey content binds to.
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
        if not self.target_piece_instance_id:
            return
        if self.target_piece_instance.piece_type == TOWER_PIECE_LANDING:
            raise ValidationError(
                {"target_piece_instance": "Interactable artifacts cannot be placed on landings."}
            )
        if self.target_piece_instance.piece_type != TOWER_PIECE_SECTION:
            raise ValidationError(
                {"target_piece_instance": "Interactable artifacts must be placed on a section."}
            )
        if self.content_definition_id and self.content_definition.kind != self.role:
            raise ValidationError(
                {"content_definition": "Content kind must match the interactable artifact role."}
            )
        conflicting = ArtifactPlacement.objects.filter(
            target_piece_instance=self.target_piece_instance,
            role__in=INTERACTABLE_ARTIFACT_ROLES,
        ).exclude(role=self.role)
        if self.pk:
            conflicting = conflicting.exclude(pk=self.pk)
        if conflicting.exists():
            raise ValidationError(
                {
                    "role": (
                        "A section can hold interactable artifacts for only one content "
                        "kind."
                    )
                }
            )

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
        if not (min_x <= self.x <= max_x and min_y <= self.y <= max_y):
            raise ValidationError({"x": "Artifact placement is outside the piece safe bounds."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
