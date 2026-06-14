from __future__ import annotations

import copy

from django.db import models, transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from assets.models import Asset
from authoring.models import STATUS_PUBLISHED as CONTENT_STATUS_PUBLISHED
from authoring.models import ContentDefinition
from tower_designs.models import (
    ORIGIN_OFFICIAL_FORK,
    ORIGIN_PERSONAL,
    STATUS_ARCHIVED,
    STATUS_PUBLISHED,
    ArtifactPlacement,
    TowerContentBinding,
    TowerDesign,
    TowerPieceInstance,
)


class TowerDesignService:
    def assert_owner(self, *, user, design: TowerDesign) -> None:
        if not getattr(user, "is_staff", False) and design.owner_id != getattr(user, "id", None):
            raise PermissionDenied("You do not own this tower design.")

    def assert_can_own_new_design(self, *, user, origin: str = ORIGIN_PERSONAL) -> None:
        """One tower per user PER ORIGIN (archived designs don't count).

        A user may hold one personal tower AND one official fork at once; the cap
        only blocks a second design of the same origin.
        """
        if (
            TowerDesign.objects.filter(owner=user, origin=origin)
            .exclude(status=STATUS_ARCHIVED)
            .exists()
        ):
            label = "official fork" if origin == ORIGIN_OFFICIAL_FORK else "tower"
            raise ValidationError(
                {"detail": f"You can only own one {label}. Edit or remix your existing one."}
            )

    def get_or_create_personal(self, *, user, data: dict | None = None) -> TowerDesign:
        """Return the user's single personal tower, creating it on first call.

        Idempotent so "Raise your Tower" never 400s when a tower already exists:
        the one-per-user cap reads as a fact of the world, not a validation error.
        """
        existing = (
            TowerDesign.objects.filter(owner=user, origin=ORIGIN_PERSONAL)
            .exclude(status=STATUS_ARCHIVED)
            .order_by("-is_active", "-updated_at", "-id")
            .first()
        )
        if existing:
            return existing
        return self.create(user=user, data=data or {})

    @transaction.atomic
    def create(self, *, user, data: dict) -> TowerDesign:
        self.assert_can_own_new_design(user=user, origin=ORIGIN_PERSONAL)
        # The first (and only) design becomes the active one so it renders on /my-tower.
        design = TowerDesign.objects.create(
            owner=user,
            slug=data.get("slug") or _unique_slug(user=user, base="your-tower"),
            title=data.get("title") or "Your Tower",
            summary=data.get("summary", ""),
            visibility=data.get("visibility", "private"),
            origin=ORIGIN_PERSONAL,
            is_active=True,
        )
        self._seed_default_skeleton(design=design)
        return design

    def get_or_create_official_fork(self, *, user) -> TowerDesign:
        """Return the user's private fork of the official tower, creating it on
        demand. Seeded from the official piece skeleton so they open onto a
        sensible tower to tweak. Never active (the personal tower owns /my-tower),
        never publishable/shareable."""
        existing = (
            TowerDesign.objects.filter(owner=user, origin=ORIGIN_OFFICIAL_FORK)
            .exclude(status=STATUS_ARCHIVED)
            .order_by("-updated_at", "-id")
            .first()
        )
        if existing:
            return existing
        with transaction.atomic():
            design = TowerDesign.objects.create(
                owner=user,
                slug=_unique_slug(user=user, base="official-fork"),
                title="The Arcane Spire (your edits)",
                summary="Your private tweaks to the official tower.",
                visibility="private",
                origin=ORIGIN_OFFICIAL_FORK,
                is_active=False,
            )
            self._seed_default_skeleton(design=design)
        return design

    def _seed_default_skeleton(self, *, design: TowerDesign) -> None:
        """A walkable single storey + roof from official pieces, so the editor
        opens with a sensible tower the user can customise rather than a blank slate."""
        skeleton = [
            ("official-spire", "spire"),
            ("official-adventure-section", "adventure_section"),
            ("official-landing", "landing"),
            ("official-challenge-section", "challenge_section"),
            ("official-landing", "landing"),
        ]
        for sort_order, (slug, piece_type) in enumerate(skeleton):
            asset = Asset.objects.filter(slug=slug, kind="tower_piece").first()
            if asset is None:
                continue
            TowerPieceInstance.objects.create(
                tower_design=design,
                piece_asset=asset,
                piece_type=piece_type,
                sort_order=sort_order,
            )

    # The repeating floor unit appended by "Add storey": an adventure section and
    # a challenge section, each capped by a walkable landing.
    _STOREY_FLOOR = [
        ("official-adventure-section", "adventure_section"),
        ("official-landing", "landing"),
        ("official-challenge-section", "challenge_section"),
        ("official-landing", "landing"),
    ]

    @transaction.atomic
    def add_storey(self, *, user, design: TowerDesign) -> int:
        """Append a new floor of pieces to the design and return its storey_index."""
        self.assert_owner(user=user, design=design)
        next_index = (
            design.pieces.aggregate(models.Max("storey_index"))["storey_index__max"] or 0
        ) + 1
        sort_base = (design.pieces.aggregate(models.Max("sort_order"))["sort_order__max"] or 0) + 1
        for offset, (slug, piece_type) in enumerate(self._STOREY_FLOOR):
            asset = Asset.objects.filter(slug=slug, kind="tower_piece").first()
            if asset is None:
                continue
            TowerPieceInstance.objects.create(
                tower_design=design,
                piece_asset=asset,
                piece_type=piece_type,
                storey_index=next_index,
                sort_order=sort_base + offset,
            )
        return next_index

    @transaction.atomic
    def update(self, *, user, design: TowerDesign, data: dict) -> TowerDesign:
        self.assert_owner(user=user, design=design)
        for field in ("slug", "title", "summary", "visibility"):
            if field in data:
                setattr(design, field, data[field])
        design.full_clean()
        design.save()
        return design

    @transaction.atomic
    def set_active(self, *, user, design: TowerDesign) -> TowerDesign:
        self.assert_owner(user=user, design=design)
        TowerDesign.objects.filter(owner=user, is_active=True).exclude(id=design.id).update(is_active=False)
        design.is_active = True
        design.save(update_fields=["is_active", "updated_at"])
        return design

    @transaction.atomic
    def publish(self, *, user, design: TowerDesign) -> TowerDesign:
        self.assert_owner(user=user, design=design)
        if design.origin == ORIGIN_OFFICIAL_FORK:
            raise ValidationError(
                {"detail": "Your private edits to the official tower can't be published."}
            )
        errors = self.publish_errors(design=design)
        if errors:
            raise ValidationError({"validation_errors": errors})
        design.status = STATUS_PUBLISHED
        design.save(update_fields=["status", "updated_at"])
        return design

    @transaction.atomic
    def share(self, *, user, design: TowerDesign) -> TowerDesign:
        """Make a personal tower world-readable: validate + publish, flip it
        public, and publish any uploaded monsters it relies on so other players
        can render them."""
        self.assert_owner(user=user, design=design)
        if design.origin == ORIGIN_OFFICIAL_FORK:
            raise ValidationError(
                {"detail": "Your private edits to the official tower can't be shared."}
            )
        errors = self.publish_errors(design=design)
        if errors:
            raise ValidationError({"validation_errors": errors})
        self._publish_referenced_assets(design=design)
        design.status = STATUS_PUBLISHED
        design.visibility = "public"
        design.save(update_fields=["status", "visibility", "updated_at"])
        return design

    def _publish_referenced_assets(self, *, design: TowerDesign) -> None:
        """Flip the author's private assets the shared tower relies on (its custom
        tower pieces, artifacts, and content-referenced monsters) to published +
        public, so everyone viewing/playing the shared tower can render them."""
        from assets.models import KIND_MONSTER, Asset

        piece_ids = list(design.pieces.values_list("piece_asset_id", flat=True))
        artifact_ids = list(design.artifact_placements.values_list("artifact_asset_id", flat=True))
        asset_ids = {pk for pk in [*piece_ids, *artifact_ids] if pk}
        if asset_ids:
            Asset.objects.filter(id__in=asset_ids, owner=design.owner).update(
                is_published=True, visibility="public"
            )

        slugs = self._referenced_monster_slugs(design=design)
        if slugs:
            Asset.objects.filter(
                kind=KIND_MONSTER, owner=design.owner, slug__in=slugs
            ).update(is_published=True, visibility="public")

    def _referenced_monster_slugs(self, *, design: TowerDesign) -> set[str]:
        slugs: set[str] = set()
        for piece in design.pieces.prefetch_related("content_binding__content_definition"):
            binding = getattr(piece, "content_binding", None)
            if not binding:
                continue
            definition = binding.content_definition.definition or {}
            levels = definition.get("levels") or []
            if isinstance(definition.get("level"), dict):
                levels = [definition["level"], *levels]
            for level in levels:
                if not isinstance(level, dict):
                    continue
                for row in level.get("encounter_spec") or []:
                    if isinstance(row, dict) and row.get("species"):
                        slugs.add(str(row["species"]))
                boss = level.get("boss_spec") or {}
                if isinstance(boss, dict) and boss.get("species"):
                    slugs.add(str(boss["species"]))
        return slugs

    def publish_errors(self, *, design: TowerDesign) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        for piece in design.pieces.prefetch_related("content_binding__content_definition"):
            if piece.piece_type not in {"adventure_section", "challenge_section", "tome"}:
                continue
            binding = getattr(piece, "content_binding", None)
            if not binding:
                errors.append({"field": f"piece:{piece.id}", "message": "Interactive piece needs a content binding."})
                continue
            if binding.content_definition.status != CONTENT_STATUS_PUBLISHED:
                errors.append({"field": f"piece:{piece.id}", "message": "Bound content must be published."})
        return errors

    @transaction.atomic
    def add_piece(self, *, user, design: TowerDesign, data: dict) -> TowerPieceInstance:
        self.assert_owner(user=user, design=design)
        asset = Asset.objects.get(id=data["piece_asset_id"])
        piece = TowerPieceInstance.objects.create(
            tower_design=design,
            piece_asset=asset,
            piece_type=data.get("piece_type") or asset.tower_piece.piece_type,
            sort_order=data.get("sort_order", design.pieces.count()),
            parent_instance_id=data.get("parent_instance_id"),
            transform=data.get("transform") or {},
            config=data.get("config") or {},
        )
        return piece

    @transaction.atomic
    def bind_content(self, *, user, design: TowerDesign, data: dict) -> TowerContentBinding:
        self.assert_owner(user=user, design=design)
        piece = design.pieces.get(id=data["piece_instance_id"])
        content = ContentDefinition.objects.get(id=data["content_definition_id"])
        binding, _created = TowerContentBinding.objects.update_or_create(
            piece_instance=piece,
            defaults={"content_definition": content},
        )
        return binding

    @transaction.atomic
    def place_artifact(self, *, user, design: TowerDesign, data: dict) -> ArtifactPlacement:
        self.assert_owner(user=user, design=design)
        placement = ArtifactPlacement.objects.create(
            tower_design=design,
            target_piece_instance=design.pieces.get(id=data["target_piece_instance_id"]),
            artifact_asset=Asset.objects.get(id=data["artifact_asset_id"]),
            x=data.get("x", 0),
            y=data.get("y", 0),
            scale=data.get("scale", 1),
            rotation=data.get("rotation", 0),
            anchor=data.get("anchor", ""),
            z_index=data.get("z_index", 0),
        )
        return placement

    @transaction.atomic
    def remix(self, *, user, design: TowerDesign) -> TowerDesign:
        # Remixing produces an owned editable personal copy, bound by the personal cap.
        self.assert_can_own_new_design(user=user, origin=ORIGIN_PERSONAL)
        clone = TowerDesign.objects.create(
            owner=user,
            source_design=design,
            visibility="private",
            status="draft",
            slug=_next_remix_slug(user=user, source=design),
            title=f"{design.title} Remix",
            summary=design.summary,
        )
        piece_map = {}
        for piece in design.pieces.order_by("sort_order", "id"):
            copied = TowerPieceInstance.objects.create(
                tower_design=clone,
                piece_asset=piece.piece_asset,
                piece_type=piece.piece_type,
                sort_order=piece.sort_order,
                transform=copy.deepcopy(piece.transform),
                config=copy.deepcopy(piece.config),
            )
            piece_map[piece.id] = copied
            binding = getattr(piece, "content_binding", None)
            if binding:
                TowerContentBinding.objects.create(piece_instance=copied, content_definition=binding.content_definition)
        for placement in design.artifact_placements.order_by("id"):
            ArtifactPlacement.objects.create(
                tower_design=clone,
                target_piece_instance=piece_map[placement.target_piece_instance_id],
                artifact_asset=placement.artifact_asset,
                x=placement.x,
                y=placement.y,
                scale=placement.scale,
                rotation=placement.rotation,
                anchor=placement.anchor,
                z_index=placement.z_index,
            )
        return clone


def _next_remix_slug(*, user, source: TowerDesign) -> str:
    return _unique_slug(user=user, base=f"{source.slug}-remix")


def _unique_slug(*, user, base: str) -> str:
    slug = base
    index = 2
    while TowerDesign.objects.filter(owner=user, slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug
