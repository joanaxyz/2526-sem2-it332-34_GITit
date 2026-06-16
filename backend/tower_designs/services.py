from __future__ import annotations

import copy
import json
from collections import Counter

from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import PermissionDenied, ValidationError

from assets.models import Asset, TOWER_PIECE_BASE, TOWER_PIECE_CROWN
from authoring.models import STATUS_PUBLISHED as CONTENT_STATUS_PUBLISHED
from authoring.models import ContentDefinition
from tower_designs.models import (
    ARTIFACT_ROLE_NORMAL,
    BASE_STOREY_INDEX,
    INTERACTABLE_ARTIFACT_ROLES,
    ORIGIN_OFFICIAL_FORK,
    ORIGIN_PERSONAL,
    SPIRE_STOREY_INDEX,
    STATUS_ARCHIVED,
    STATUS_PUBLISHED,
    STOREY_TEMPLATE_INDEX,
    ArtifactPlacement,
    TowerContentBinding,
    TowerDesign,
    TowerPieceInstance,
)

NON_REPEATABLE_PIECE_TYPES = {TOWER_PIECE_CROWN, TOWER_PIECE_BASE}


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
            self._resync_official_fork_if_unedited(design=existing)
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
            self._seed_official_fork_skeleton(design=design)
        return design

    def _seed_default_skeleton(self, *, design: TowerDesign) -> None:
        """A walkable single storey + roof from official pieces, so the editor
        opens with a sensible tower the user can customise rather than a blank slate."""
        skeleton = [
            ("official-crown", "crown", None),
            ("official-hall-section", "section", None),
            ("official-landing", "landing", 1),
            ("official-trial-section", "section", None),
            ("official-challenge-landing", "landing", 3),
            ("official-base", "base", None),
        ]
        created: dict[int, TowerPieceInstance] = {}
        for sort_order, (slug, piece_type, parent_position) in enumerate(skeleton):
            asset = Asset.objects.filter(slug=slug, kind="tower_piece").first()
            if asset is None:
                continue
            parent = created.get(parent_position) if parent_position is not None else None
            created[sort_order] = TowerPieceInstance.objects.create(
                tower_design=design,
                piece_asset=asset,
                piece_type=piece_type,
                parent_instance=parent,
                storey_index=(
                    SPIRE_STOREY_INDEX
                    if piece_type == TOWER_PIECE_CROWN
                    else BASE_STOREY_INDEX
                    if piece_type == TOWER_PIECE_BASE
                    else STOREY_TEMPLATE_INDEX
                ),
                sort_order=sort_order,
            )

    def _refresh_legacy_official_fork_if_needed(self, *, design: TowerDesign) -> None:
        self._resync_official_fork_if_unedited(design=design)

    def _resync_official_fork_if_unedited(self, *, design: TowerDesign) -> None:
        """Rebuild generated official forks after curriculum layout drift.

        Curriculum reseeds can delete/recreate Storey rows, changing their IDs.
        Official forks store those IDs in ``storey_index`` so the /tower overlay
        can join a user's private fork back to the live curriculum. If an
        untouched fork still points at old storey IDs, the editor renders the old
        snapshot while /tower falls back to the live layout. Re-seeding here keeps
        the two surfaces in lockstep without touching forks that carry real edits.
        """
        pieces = list(
            design.pieces.select_related("piece_asset", "parent_instance").order_by(
                "sort_order", "id"
            )
        )
        placements = list(
            design.artifact_placements.select_related(
                "artifact_asset", "target_piece_instance"
            ).order_by("z_index", "id")
        )
        if not self._is_unedited_official_fork(
            design=design,
            pieces=pieces,
            placements=placements,
        ):
            return

        current_pieces, current_artifacts = self._current_official_layout_signatures()
        if (
            self._official_piece_signature(pieces=pieces) == current_pieces
            and self._official_artifact_signature(pieces=pieces, placements=placements)
            == current_artifacts
        ):
            return

        with transaction.atomic():
            design.pieces.all().delete()
            self._seed_official_fork_skeleton(design=design)

    def _is_unedited_official_fork(
        self,
        *,
        design: TowerDesign,
        pieces: list[TowerPieceInstance] | None = None,
        placements: list[ArtifactPlacement] | None = None,
    ) -> bool:
        pieces = (
            pieces
            if pieces is not None
            else list(
                design.pieces.select_related("piece_asset", "parent_instance").order_by(
                    "sort_order", "id"
                )
            )
        )
        placements = (
            placements
            if placements is not None
            else list(
                design.artifact_placements.select_related(
                    "artifact_asset", "target_piece_instance"
                ).order_by("z_index", "id")
            )
        )
        if not pieces:
            return True
        if design.pieces.filter(piece_asset__owner__isnull=False).exists():
            return False
        if design.artifact_placements.filter(artifact_asset__owner__isnull=False).exists():
            return False
        if design.artifact_placements.filter(content_definition__isnull=False).exists():
            return False
        piece_signature = self._official_piece_signature(pieces=pieces)
        artifact_signature = self._official_artifact_signature(
            pieces=pieces,
            placements=placements,
        )
        if piece_signature == self._legacy_official_piece_signature() and not placements:
            return True

        current_pieces, current_artifacts = self._current_official_layout_signatures()
        if piece_signature == current_pieces and artifact_signature == current_artifacts:
            return True
        if piece_signature == current_pieces and bool(current_artifacts) and not placements:
            return True

        legacy_pieces, legacy_artifacts = self._current_official_multistorey_layout_signatures()
        if piece_signature == legacy_pieces and artifact_signature == legacy_artifacts:
            return True
        if piece_signature == legacy_pieces and bool(legacy_artifacts) and not placements:
            return True
        if self._same_signature_items_ignoring_storey(piece_signature, current_pieces):
            return self._same_signature_items_ignoring_storey(
                artifact_signature,
                current_artifacts,
            ) or (bool(current_artifacts) and not placements)
        current_without_base = self._without_official_base_signature(current_pieces)
        if self._same_signature_items_ignoring_storey(piece_signature, current_without_base):
            return self._same_signature_items_ignoring_storey(
                artifact_signature,
                current_artifacts,
            ) or (bool(current_artifacts) and not placements)

        # Compatibility for old generated official snapshots from before the
        # window/tome section layout. With no persisted seed-version bit, keep
        # this fallback narrow: only official assets, no local config/transform,
        # and every repeatable piece points at a now-dead storey id.
        return self._looks_like_stale_generated_official_snapshot(
            pieces=pieces,
            placements=placements,
        )

    def _official_piece_signature(self, *, pieces: list[TowerPieceInstance]) -> list[tuple]:
        return [
            (
                None if piece.piece_type in NON_REPEATABLE_PIECE_TYPES else piece.storey_index,
                piece.piece_type,
                piece.piece_asset.slug,
                _json_signature(piece.transform),
                _json_signature(piece.config),
            )
            for piece in pieces
        ]

    def _official_artifact_signature(
        self,
        *,
        pieces: list[TowerPieceInstance],
        placements: list[ArtifactPlacement],
    ) -> list[tuple]:
        target_order = {piece.id: index for index, piece in enumerate(pieces)}
        return [
            (
                placement.target_piece_instance.storey_index,
                target_order.get(placement.target_piece_instance_id),
                placement.role,
                placement.artifact_asset.slug,
                placement.x,
                placement.y,
                placement.scale,
                placement.width,
                placement.height,
                placement.rotation,
                placement.anchor,
                placement.z_index,
            )
            for placement in placements
        ]

    def _legacy_official_piece_signature(self) -> list[tuple]:
        return [
            (None, "crown", "official-crown", _json_signature({}), _json_signature({})),
            (0, "section", "official-hall-section", _json_signature({}), _json_signature({})),
            (0, "landing", "official-landing", _json_signature({}), _json_signature({})),
            (0, "section", "official-trial-section", _json_signature({}), _json_signature({})),
            (
                0,
                "landing",
                "official-challenge-landing",
                _json_signature({}),
                _json_signature({}),
            ),
        ]

    def _same_signature_items_ignoring_storey(self, left: list[tuple], right: list[tuple]) -> bool:
        return Counter(row[1:] for row in left) == Counter(row[1:] for row in right)

    def _without_official_base_signature(self, signature: list[tuple]) -> list[tuple]:
        return [
            row
            for row in signature
            if not (row[1] == TOWER_PIECE_BASE and row[2] == "official-base")
        ]

    def _looks_like_stale_generated_official_snapshot(
        self,
        *,
        pieces: list[TowerPieceInstance],
        placements: list[ArtifactPlacement],
    ) -> bool:
        if not pieces:
            return True
        if any(not piece.piece_asset.slug.startswith("official-") for piece in pieces):
            return False
        if any(
            not placement.artifact_asset.slug.startswith("official-") for placement in placements
        ):
            return False
        if any(piece.transform or piece.config for piece in pieces):
            return False

        from curriculum.selectors import published_storeys

        live_storey_ids = set(published_storeys().values_list("id", flat=True))
        fork_storey_ids = {
            piece.storey_index
            for piece in pieces
            if piece.piece_type not in NON_REPEATABLE_PIECE_TYPES
        }
        return bool(fork_storey_ids) and fork_storey_ids.isdisjoint(live_storey_ids)

    def _current_official_layout_signatures(
        self,
    ) -> tuple[list[tuple], list[tuple]]:
        layout = self._official_template_layout_payload()
        if layout is None:
            return self._default_official_layout_signatures()

        piece_signature: list[tuple] = []
        target_order = {
            piece["instanceId"]: index for index, piece in enumerate(layout["pieces"])
        }
        for piece in layout["pieces"]:
            piece_signature.append(
                (
                    None if piece["pieceType"] in NON_REPEATABLE_PIECE_TYPES else STOREY_TEMPLATE_INDEX,
                    piece["pieceType"],
                    piece["assetSlug"],
                    _json_signature(piece.get("transform")),
                    _json_signature(piece.get("config")),
                )
            )

        artifact_signature: list[tuple] = []
        for artifact in layout["artifacts"]:
            artifact_signature.append(
                (
                    STOREY_TEMPLATE_INDEX,
                    target_order.get(artifact["targetInstanceId"]),
                    artifact["role"],
                    artifact["assetSlug"],
                    artifact.get("x", 0),
                    artifact.get("y", 0),
                    artifact.get("scale", 1),
                    artifact.get("width", 0),
                    artifact.get("height", 0),
                    artifact.get("rotation", 0),
                    artifact.get("anchor", ""),
                    artifact.get("zIndex", 0),
                )
            )
        return piece_signature, artifact_signature

    def _current_official_multistorey_layout_signatures(
        self,
    ) -> tuple[list[tuple], list[tuple]]:
        piece_signature: list[tuple] = []
        artifact_signature: list[tuple] = []
        non_repeatable_seen: set[str] = set()
        for storey, layout in self._official_layout_payloads():
            for piece in layout["pieces"]:
                if piece["pieceType"] in NON_REPEATABLE_PIECE_TYPES:
                    if piece["pieceType"] in non_repeatable_seen:
                        continue
                    non_repeatable_seen.add(piece["pieceType"])
                    piece_signature.append(
                        (
                            None,
                            piece["pieceType"],
                            piece["assetSlug"],
                            _json_signature(piece.get("transform")),
                            _json_signature(piece.get("config")),
                        )
                    )
                else:
                    piece_signature.append(
                        (
                            storey.id,
                            piece["pieceType"],
                            piece["assetSlug"],
                            _json_signature(piece.get("transform")),
                            _json_signature(piece.get("config")),
                        )
                    )
            target_order = {
                piece["instanceId"]: index for index, piece in enumerate(layout["pieces"])
            }
            for artifact in layout["artifacts"]:
                artifact_signature.append(
                    (
                        storey.id,
                        target_order.get(artifact["targetInstanceId"]),
                        artifact["role"],
                        artifact["assetSlug"],
                        artifact.get("x", 0),
                        artifact.get("y", 0),
                        artifact.get("scale", 1),
                        artifact.get("width", 0),
                        artifact.get("height", 0),
                        artifact.get("rotation", 0),
                        artifact.get("anchor", ""),
                        artifact.get("zIndex", 0),
                    )
                )
        return piece_signature, artifact_signature

    def _official_template_layout_payload(self) -> dict | None:
        layouts = self._official_layout_payloads()
        return layouts[0][1] if layouts else None

    def _official_layout_payloads(self) -> list[tuple[object, dict]]:
        from challenges.models import Challenge
        from command_adventures.models import CommandAdventure
        from curriculum.models import Tome
        from curriculum.selectors import published_storeys, tower_layout_payload

        payloads: list[tuple[object, dict]] = []
        for storey in published_storeys():
            adventures = list(
                CommandAdventure.objects.filter(storey=storey, is_published=True)
                .select_related("storey")
                .order_by("sort_order", "id")
            )
            tomes = list(
                Tome.objects.filter(storey=storey, is_published=True).order_by("sort_order", "id")
            )
            challenges = list(
                Challenge.objects.filter(storey=storey, is_published=True).order_by(
                    "sort_order", "id"
                )
            )
            payloads.append(
                (
                    storey,
                    tower_layout_payload(
                        storey=storey,
                        storey_id=storey.id,
                        adventures=adventures,
                        tomes=tomes,
                        challenges=challenges,
                    ),
                )
            )
        return payloads

    def _default_official_layout_signatures(self) -> tuple[list[tuple], list[tuple]]:
        return [
            (None, "crown", "official-crown", _json_signature({}), _json_signature({})),
            (
                STOREY_TEMPLATE_INDEX,
                "section",
                "official-hall-section",
                _json_signature({}),
                _json_signature({}),
            ),
            (
                STOREY_TEMPLATE_INDEX,
                "landing",
                "official-landing",
                _json_signature({}),
                _json_signature({}),
            ),
            (
                STOREY_TEMPLATE_INDEX,
                "section",
                "official-trial-section",
                _json_signature({}),
                _json_signature({}),
            ),
            (
                STOREY_TEMPLATE_INDEX,
                "landing",
                "official-challenge-landing",
                _json_signature({}),
                _json_signature({}),
            ),
            (None, "base", "official-base", _json_signature({}), _json_signature({})),
        ], []

    def _seed_official_fork_skeleton(self, *, design: TowerDesign) -> None:
        """Seed one editable Arcane Spire template: crown + storey + base."""
        layout = self._official_template_layout_payload()
        if layout is None:
            self._seed_default_skeleton(design=design)
            return
        sort_order = 0
        created_any = False
        piece_map: dict[str, TowerPieceInstance] = {}
        for piece_payload in layout["pieces"]:
            asset = Asset.objects.filter(slug=piece_payload["assetSlug"], kind="tower_piece").first()
            if asset is None:
                continue
            piece_type = piece_payload["pieceType"]
            piece = TowerPieceInstance.objects.create(
                tower_design=design,
                piece_asset=asset,
                piece_type=piece_type,
                storey_index=(
                    SPIRE_STOREY_INDEX
                    if piece_type == TOWER_PIECE_CROWN
                    else BASE_STOREY_INDEX
                    if piece_type == TOWER_PIECE_BASE
                    else STOREY_TEMPLATE_INDEX
                ),
                sort_order=sort_order,
                transform=piece_payload.get("transform") or {},
                config=piece_payload.get("config") or {},
            )
            piece_map[piece_payload["instanceId"]] = piece
            sort_order += 1
            created_any = True

        for artifact_payload in layout["artifacts"]:
            target = piece_map.get(artifact_payload["targetInstanceId"])
            asset = Asset.objects.filter(
                slug=artifact_payload["assetSlug"], kind="tower_artifact"
            ).first()
            if target is None or asset is None:
                continue
            ArtifactPlacement.objects.create(
                tower_design=design,
                target_piece_instance=target,
                artifact_asset=asset,
                x=artifact_payload.get("x", 0),
                y=artifact_payload.get("y", 0),
                scale=artifact_payload.get("scale", 1),
                width=artifact_payload.get("width", 0),
                height=artifact_payload.get("height", 0),
                rotation=artifact_payload.get("rotation", 0),
                anchor=artifact_payload.get("anchor", ""),
                z_index=artifact_payload.get("zIndex", 0),
                role=artifact_payload.get("role", ARTIFACT_ROLE_NORMAL),
            )

        if not created_any:
            self._seed_default_skeleton(design=design)

    @transaction.atomic
    def add_storey(self, *, user, design: TowerDesign) -> int:
        """Compatibility no-op.

        Tower visuals are now one spire plus one repeatable storey template, so
        callers must not create another unique visual storey.
        """
        self.assert_owner(user=user, design=design)
        return STOREY_TEMPLATE_INDEX

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
        TowerDesign.objects.filter(owner=user, is_active=True).exclude(id=design.id).update(
            is_active=False
        )
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
            Asset.objects.filter(kind=KIND_MONSTER, owner=design.owner, slug__in=slugs).update(
                is_published=True, visibility="public"
            )

    def _referenced_monster_slugs(self, *, design: TowerDesign) -> set[str]:
        slugs: set[str] = set()
        for placement in design.artifact_placements.select_related("content_definition"):
            if (
                placement.role not in INTERACTABLE_ARTIFACT_ROLES
                or not placement.content_definition_id
            ):
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

    def publish_errors(self, *, design: TowerDesign) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        # Per-artifact guardrails only: an interactable artifact must carry
        # published content. There is deliberately no per-piece
        # count rule — a section may hold any number of interactables, or none.
        for placement in design.artifact_placements.select_related(
            "content_definition", "target_piece_instance"
        ):
            if placement.role not in INTERACTABLE_ARTIFACT_ROLES:
                continue
            if not placement.content_definition_id:
                errors.append(
                    {
                        "field": f"artifact:{placement.id}",
                        "message": "Interactable artifact needs a content binding.",
                    }
                )
                continue
            if placement.content_definition.status != CONTENT_STATUS_PUBLISHED:
                errors.append(
                    {
                        "field": f"artifact:{placement.id}",
                        "message": "Bound content must be published.",
                    }
                )
        return errors

    @transaction.atomic
    def add_piece(self, *, user, design: TowerDesign, data: dict) -> TowerPieceInstance:
        self.assert_owner(user=user, design=design)
        asset = Asset.objects.get(id=data["piece_asset_id"])
        piece_type = data.get("piece_type") or asset.tower_piece.piece_type
        if piece_type in NON_REPEATABLE_PIECE_TYPES:
            existing = (
                design.pieces.filter(piece_type=piece_type)
                .order_by("sort_order", "id")
                .first()
            )
            if existing is not None:
                existing.piece_asset = asset
                if "sort_order" in data:
                    existing.sort_order = data["sort_order"]
                if "transform" in data:
                    existing.transform = data.get("transform") or {}
                if "config" in data:
                    existing.config = data.get("config") or {}
                existing.save()
                return existing
        sort_order = _optional_sort_order(data.get("sort_order"))
        if sort_order is None:
            sort_order = design.pieces.count()
        else:
            design.pieces.filter(sort_order__gte=sort_order).update(sort_order=F("sort_order") + 1)

        piece = TowerPieceInstance.objects.create(
            tower_design=design,
            piece_asset=asset,
            piece_type=piece_type,
            sort_order=sort_order,
            storey_index=(
                SPIRE_STOREY_INDEX
                if piece_type == TOWER_PIECE_CROWN
                else BASE_STOREY_INDEX
                if piece_type == TOWER_PIECE_BASE
                else STOREY_TEMPLATE_INDEX
            ),
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
            width=data.get("width", 0),
            height=data.get("height", 0),
            rotation=data.get("rotation", 0),
            anchor=data.get("anchor", ""),
            z_index=data.get("z_index", 0),
            role=data.get("role", ARTIFACT_ROLE_NORMAL),
            content_definition_id=data.get("content_definition_id"),
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
                storey_index=piece.storey_index,
                transform=copy.deepcopy(piece.transform),
                config=copy.deepcopy(piece.config),
            )
            piece_map[piece.id] = copied
        for source_id, copied in piece_map.items():
            source = next((p for p in design.pieces.all() if p.id == source_id), None)
            if source and source.parent_instance_id:
                copied.parent_instance = piece_map.get(source.parent_instance_id)
                copied.save(update_fields=["parent_instance"])
        for piece in design.pieces.order_by("sort_order", "id"):
            binding = getattr(piece, "content_binding", None)
            if binding:
                TowerContentBinding.objects.create(
                    piece_instance=piece_map[piece.id],
                    content_definition=binding.content_definition,
                )
        for placement in design.artifact_placements.order_by("id"):
            ArtifactPlacement.objects.create(
                tower_design=clone,
                target_piece_instance=piece_map[placement.target_piece_instance_id],
                artifact_asset=placement.artifact_asset,
                x=placement.x,
                y=placement.y,
                scale=placement.scale,
                width=placement.width,
                height=placement.height,
                rotation=placement.rotation,
                anchor=placement.anchor,
                z_index=placement.z_index,
                role=placement.role,
                content_definition=placement.content_definition,
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


def _json_signature(value) -> str:
    return json.dumps(value or {}, sort_keys=True, separators=(",", ":"))


def _optional_sort_order(value) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return max(parsed, 0)
