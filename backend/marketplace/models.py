from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

ITEM_ASSET = "asset"
ITEM_CONTENT = "content_definition"
ITEM_TOWER_DESIGN = "tower_design"
ITEM_KINDS = [
    (ITEM_ASSET, "Asset"),
    (ITEM_CONTENT, "Content definition"),
    (ITEM_TOWER_DESIGN, "Tower design"),
]

LISTING_DRAFT = "draft"
LISTING_ACTIVE = "active"
LISTING_PAUSED = "paused"
LISTING_ARCHIVED = "archived"
LISTING_STATUSES = [
    (LISTING_DRAFT, "Draft"),
    (LISTING_ACTIVE, "Active"),
    (LISTING_PAUSED, "Paused"),
    (LISTING_ARCHIVED, "Archived"),
]


class StoreListing(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="store_listings",
        on_delete=models.CASCADE,
    )
    item_kind = models.CharField(max_length=24, choices=ITEM_KINDS)
    asset = models.ForeignKey("assets.Asset", null=True, blank=True, on_delete=models.CASCADE)
    content_definition = models.ForeignKey(
        "authoring.ContentDefinition", null=True, blank=True, on_delete=models.CASCADE
    )
    tower_design = models.ForeignKey("towers.TowerDesign", null=True, blank=True, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=LISTING_STATUSES, default=LISTING_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["item_kind", "status"], name="store_listing_kind_status_idx"),
            models.Index(fields=["seller", "status"], name="store_listing_seller_idx"),
        ]

    def __str__(self) -> str:
        return f"StoreListing({self.item_kind}:{self.item_id})"

    @property
    def item(self):
        return self.asset or self.content_definition or self.tower_design

    @property
    def item_id(self) -> int | None:
        item = self.item
        return item.id if item else None

    def clean(self) -> None:
        super().clean()
        _validate_exactly_one_item(self)
        expected = {
            ITEM_ASSET: self.asset_id,
            ITEM_CONTENT: self.content_definition_id,
            ITEM_TOWER_DESIGN: self.tower_design_id,
        }.get(self.item_kind)
        if not expected:
            raise ValidationError({"item_kind": "Listing item kind must match the referenced item."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Entitlement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="entitlements",
        on_delete=models.CASCADE,
    )
    item_kind = models.CharField(max_length=24, choices=ITEM_KINDS)
    asset = models.ForeignKey("assets.Asset", null=True, blank=True, on_delete=models.CASCADE)
    content_definition = models.ForeignKey(
        "authoring.ContentDefinition", null=True, blank=True, on_delete=models.CASCADE
    )
    tower_design = models.ForeignKey("towers.TowerDesign", null=True, blank=True, on_delete=models.CASCADE)
    source_listing = models.ForeignKey(StoreListing, null=True, blank=True, on_delete=models.SET_NULL)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-granted_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "asset"],
                condition=models.Q(asset__isnull=False),
                name="unique_asset_entitlement_per_user",
            ),
            models.UniqueConstraint(
                fields=["user", "content_definition"],
                condition=models.Q(content_definition__isnull=False),
                name="unique_content_entitlement_per_user",
            ),
            models.UniqueConstraint(
                fields=["user", "tower_design"],
                condition=models.Q(tower_design__isnull=False),
                name="unique_tower_entitlement_per_user",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "item_kind"], name="entitlement_user_kind_idx"),
        ]

    @property
    def item(self):
        return self.asset or self.content_definition or self.tower_design

    def clean(self) -> None:
        super().clean()
        _validate_exactly_one_item(self)
        expected = {
            ITEM_ASSET: self.asset_id,
            ITEM_CONTENT: self.content_definition_id,
            ITEM_TOWER_DESIGN: self.tower_design_id,
        }.get(self.item_kind)
        if not expected:
            raise ValidationError({"item_kind": "Entitlement item kind must match the referenced item."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


def _validate_exactly_one_item(instance) -> None:
    count = sum(
        bool(value)
        for value in [
            instance.asset_id,
            instance.content_definition_id,
            instance.tower_design_id,
        ]
    )
    if count != 1:
        raise ValidationError("Exactly one marketplace item reference is required.")
