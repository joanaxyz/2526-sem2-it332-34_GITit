from __future__ import annotations

import copy

from django.db import transaction
from django.db.models import Max
from rest_framework.exceptions import PermissionDenied, ValidationError

from assets.models import KIND_RELIC, Asset
from authoring.models import STATUS_PUBLISHED as CONTENT_STATUS_PUBLISHED
from archive.models import (
    INTERACTABLE_RELIC_KINDS,
    ORIGIN_OFFICIAL_FORK,
    ORIGIN_PERSONAL,
    RELIC_KIND_NORMAL,
    STATUS_ARCHIVED,
    STATUS_PUBLISHED,
    ArchiveDesign,
    RelicPlacement,
)

OFFICIAL_RELIC_SLUG = "official-relic"


class ArchiveDesignService:
    def assert_owner(self, *, user, design: ArchiveDesign) -> None:
        if not getattr(user, "is_staff", False) and design.owner_id != getattr(user, "id", None):
            raise PermissionDenied("You do not own this archive.")

    def assert_can_own_new_design(self, *, user, origin: str = ORIGIN_PERSONAL) -> None:
        """One archive per user PER ORIGIN (archived designs don't count)."""
        if (
            ArchiveDesign.objects.filter(owner=user, origin=origin)
            .exclude(status=STATUS_ARCHIVED)
            .exists()
        ):
            label = "official fork" if origin == ORIGIN_OFFICIAL_FORK else "archive"
            raise ValidationError(
                {"detail": f"You can only own one {label}. Edit or remix your existing one."}
            )

    def get_or_create_personal(self, *, user, data: dict | None = None) -> ArchiveDesign:
        """Return the user's single personal archive, creating it on first call."""
        existing = (
            ArchiveDesign.objects.filter(owner=user, origin=ORIGIN_PERSONAL)
            .exclude(status=STATUS_ARCHIVED)
            .order_by("-is_active", "-updated_at", "-id")
            .first()
        )
        if existing:
            return existing
        return self.create(user=user, data=data or {})

    @transaction.atomic
    def create(self, *, user, data: dict) -> ArchiveDesign:
        self.assert_can_own_new_design(user=user, origin=ORIGIN_PERSONAL)
        design = ArchiveDesign.objects.create(
            owner=user,
            slug=data.get("slug") or _unique_slug(user=user, base="your-archive"),
            title=data.get("title") or "Your Archive",
            summary=data.get("summary", ""),
            visibility=data.get("visibility", "private"),
            origin=ORIGIN_PERSONAL,
            is_active=True,
        )
        self._seed_default_relics(design=design)
        return design

    def get_or_create_official_fork(self, *, user) -> ArchiveDesign:
        """Return the user's private fork of the official Archive, creating it on
        demand from the live curriculum layout. Never active, never publishable."""
        existing = (
            ArchiveDesign.objects.filter(owner=user, origin=ORIGIN_OFFICIAL_FORK)
            .exclude(status=STATUS_ARCHIVED)
            .order_by("-updated_at", "-id")
            .first()
        )
        if existing:
            return existing
        with transaction.atomic():
            design = ArchiveDesign.objects.create(
                owner=user,
                slug=_unique_slug(user=user, base="official-fork"),
                title="The Archive (your edits)",
                summary="Your private tweaks to the official Archive.",
                visibility="private",
                origin=ORIGIN_OFFICIAL_FORK,
                is_active=False,
            )
            self._seed_official_fork_relics(design=design)
        return design

    def _relic_asset(self) -> Asset | None:
        return Asset.objects.filter(slug=OFFICIAL_RELIC_SLUG, kind=KIND_RELIC).first()

    def _seed_default_relics(self, *, design: ArchiveDesign) -> None:
        """A single decorative relic so a new personal archive opens onto
        something to drag rather than a blank canvas."""
        asset = self._relic_asset()
        if asset is None:
            return
        RelicPlacement.objects.create(
            archive_design=design,
            relic_asset=asset,
            chapter_index=1,
            x=0,
            y=0,
            scale=1,
            kind=RELIC_KIND_NORMAL,
        )

    def _seed_official_fork_relics(self, *, design: ArchiveDesign) -> None:
        """Seed the fork's relics from the live curriculum layout. Interactable
        relics are seeded WITHOUT a content binding — the official content has no
        ContentDefinition; the /archive overlay rebinds curriculum content to the
        fork's interactable relics by (kind, ordinal) at render time."""
        from curriculum.selectors import published_chapters, relic_layout_payload
        from challenges.models import Challenge
        from command_adventures.models import CommandAdventure
        from curriculum.models import Tome

        asset = self._relic_asset()
        if asset is None:
            self._seed_default_relics(design=design)
            return

        created_any = False
        for chapter in published_chapters():
            adventures = list(
                CommandAdventure.objects.filter(chapter=chapter, is_published=True)
                .order_by("sort_order", "id")
            )
            tomes = list(
                Tome.objects.filter(chapter=chapter, is_published=True).order_by("sort_order", "id")
            )
            challenges = list(
                Challenge.objects.filter(chapter=chapter, is_published=True).order_by(
                    "sort_order", "id"
                )
            )
            layout = relic_layout_payload(
                chapter=chapter,
                chapter_id=chapter.id,
                adventures=adventures,
                tomes=tomes,
                challenges=challenges,
            )
            for relic in layout["relics"]:
                RelicPlacement.objects.create(
                    archive_design=design,
                    relic_asset=asset,
                    chapter_index=chapter.id,
                    x=relic.get("x", 0),
                    y=relic.get("y", 0),
                    scale=relic.get("scale", 1),
                    width=relic.get("width", 0),
                    height=relic.get("height", 0),
                    rotation=relic.get("rotation", 0),
                    z_index=relic.get("zIndex", 0),
                    kind=relic.get("kind", RELIC_KIND_NORMAL),
                    interactive_viewbox=relic.get("interactiveViewbox", {}),
                    landing_viewbox=relic.get("landingViewbox", {}),
                )
                created_any = True
        if not created_any:
            self._seed_default_relics(design=design)

    @transaction.atomic
    def add_chapter(self, *, user, design: ArchiveDesign) -> int:
        """Reserve the next empty chapter tab and return its index. Creates no
        relics — the author drops them in afterwards (no repeating structures)."""
        self.assert_owner(user=user, design=design)
        highest = design.relics.aggregate(highest=Max("chapter_index"))["highest"]
        return (highest or 0) + 1

    @transaction.atomic
    def update(self, *, user, design: ArchiveDesign, data: dict) -> ArchiveDesign:
        self.assert_owner(user=user, design=design)
        for field in ("slug", "title", "summary", "visibility"):
            if field in data:
                setattr(design, field, data[field])
        design.full_clean()
        design.save()
        return design

    @transaction.atomic
    def set_active(self, *, user, design: ArchiveDesign) -> ArchiveDesign:
        self.assert_owner(user=user, design=design)
        ArchiveDesign.objects.filter(owner=user, is_active=True).exclude(id=design.id).update(
            is_active=False
        )
        design.is_active = True
        design.save(update_fields=["is_active", "updated_at"])
        return design

    @transaction.atomic
    def publish(self, *, user, design: ArchiveDesign) -> ArchiveDesign:
        self.assert_owner(user=user, design=design)
        if design.origin == ORIGIN_OFFICIAL_FORK:
            raise ValidationError(
                {"detail": "Your private edits to the official Archive can't be published."}
            )
        errors = self.publish_errors(design=design)
        if errors:
            raise ValidationError({"validation_errors": errors})
        design.status = STATUS_PUBLISHED
        design.save(update_fields=["status", "updated_at"])
        return design

    @transaction.atomic
    def share(self, *, user, design: ArchiveDesign) -> ArchiveDesign:
        self.assert_owner(user=user, design=design)
        if design.origin == ORIGIN_OFFICIAL_FORK:
            raise ValidationError(
                {"detail": "Your private edits to the official Archive can't be shared."}
            )
        errors = self.publish_errors(design=design)
        if errors:
            raise ValidationError({"validation_errors": errors})
        self._publish_referenced_assets(design=design)
        design.status = STATUS_PUBLISHED
        design.visibility = "public"
        design.save(update_fields=["status", "visibility", "updated_at"])
        return design

    def _publish_referenced_assets(self, *, design: ArchiveDesign) -> None:
        """Flip the author's private relic assets + content-referenced monsters the
        shared archive relies on to published + public."""
        from assets.models import KIND_MONSTER

        asset_ids = {pk for pk in design.relics.values_list("relic_asset_id", flat=True) if pk}
        if asset_ids:
            Asset.objects.filter(id__in=asset_ids, owner=design.owner).update(
                is_published=True, visibility="public"
            )

        slugs = self._referenced_monster_slugs(design=design)
        if slugs:
            Asset.objects.filter(kind=KIND_MONSTER, owner=design.owner, slug__in=slugs).update(
                is_published=True, visibility="public"
            )

    def _referenced_monster_slugs(self, *, design: ArchiveDesign) -> set[str]:
        slugs: set[str] = set()
        for placement in design.relics.select_related("content_definition"):
            if placement.kind not in INTERACTABLE_RELIC_KINDS or not placement.content_definition_id:
                continue
            definition = placement.content_definition.definition or {}
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

    def publish_errors(self, *, design: ArchiveDesign) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        for placement in design.relics.select_related("content_definition"):
            if placement.kind not in INTERACTABLE_RELIC_KINDS:
                continue
            if not placement.content_definition_id:
                errors.append(
                    {
                        "field": f"relic:{placement.id}",
                        "message": "Interactable relic needs a content binding.",
                    }
                )
                continue
            if placement.content_definition.status != CONTENT_STATUS_PUBLISHED:
                errors.append(
                    {
                        "field": f"relic:{placement.id}",
                        "message": "Bound content must be published.",
                    }
                )
        return errors

    @transaction.atomic
    def add_relic(self, *, user, design: ArchiveDesign, data: dict) -> RelicPlacement:
        self.assert_owner(user=user, design=design)
        placement = RelicPlacement.objects.create(
            archive_design=design,
            relic_asset=Asset.objects.get(id=data["relic_asset_id"]),
            chapter_index=data.get("chapter_index", 1),
            x=data.get("x", 0),
            y=data.get("y", 0),
            scale=data.get("scale", 1),
            width=data.get("width", 0),
            height=data.get("height", 0),
            rotation=data.get("rotation", 0),
            z_index=data.get("z_index", 0),
            kind=data.get("kind", RELIC_KIND_NORMAL),
            content_definition_id=data.get("content_definition_id"),
            interactive_viewbox=data.get("interactive_viewbox", {}),
            landing_viewbox=data.get("landing_viewbox", {}),
        )
        return placement

    @transaction.atomic
    def remix(self, *, user, design: ArchiveDesign) -> ArchiveDesign:
        self.assert_can_own_new_design(user=user, origin=ORIGIN_PERSONAL)
        clone = ArchiveDesign.objects.create(
            owner=user,
            source_design=design,
            visibility="private",
            status="draft",
            slug=_unique_slug(user=user, base=f"{design.slug}-remix"),
            title=f"{design.title} Remix",
            summary=design.summary,
        )
        for placement in design.relics.order_by("id"):
            RelicPlacement.objects.create(
                archive_design=clone,
                relic_asset=placement.relic_asset,
                chapter_index=placement.chapter_index,
                x=placement.x,
                y=placement.y,
                scale=placement.scale,
                width=placement.width,
                height=placement.height,
                rotation=placement.rotation,
                z_index=placement.z_index,
                kind=placement.kind,
                content_definition=placement.content_definition,
                interactive_viewbox=copy.deepcopy(placement.interactive_viewbox),
                landing_viewbox=copy.deepcopy(placement.landing_viewbox),
                config=copy.deepcopy(placement.config),
            )
        return clone


def _unique_slug(*, user, base: str) -> str:
    slug = base
    index = 2
    while ArchiveDesign.objects.filter(owner=user, slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug
