import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from assets.models import (
    KIND_TOWER_ARTIFACT,
    KIND_TOWER_PIECE,
    TOWER_PIECE_BASE,
    TOWER_PIECE_LANDING,
    TOWER_PIECE_SECTION,
    Asset,
    TowerPieceAsset,
)
from authoring.models import ContentDefinition
from tower_designs.models import BASE_STOREY_INDEX, ArtifactPlacement, TowerDesign, TowerPieceInstance


def make_user(django_user_model, username="student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


@pytest.mark.django_db
def test_user_can_create_bind_and_fetch_active_tower(django_user_model):
    user = make_user(django_user_model)
    piece_asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE,
        slug="official-section-test",
        label="Tower Section",
    )
    TowerPieceAsset.objects.create(asset=piece_asset, piece_type=TOWER_PIECE_SECTION)
    artifact_asset = Asset.objects.create(
        kind=KIND_TOWER_ARTIFACT,
        slug="official-adventure-artifact-test",
        label="Adventure Artifact",
    )
    content = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        status="published",
        slug="adventure",
        title="Adventure",
        definition={"levels": []},
    )
    client = APIClient()
    client.force_authenticate(user=user)

    created = client.post(
        "/api/tower-designs/",
        {"slug": "my-tower", "title": "My Tower"},
        format="json",
    )
    assert created.status_code == 201
    design_id = created.json()["id"]

    piece = client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": piece_asset.id, "piece_type": "section"},
        format="json",
    )
    assert piece.status_code == 201

    placement = client.post(
        f"/api/tower-designs/{design_id}/artifacts/",
        {
            "target_piece_instance_id": piece.json()["id"],
            "artifact_asset_id": artifact_asset.id,
            "role": "adventure",
            "content_definition_id": content.id,
            "x": 24,
            "y": 12,
            "width": 32,
            "height": 48,
        },
        format="json",
    )
    assert placement.status_code == 201, placement.content
    assert ArtifactPlacement.objects.count() == 1

    active = client.post(f"/api/tower-designs/{design_id}/set-active/")
    assert active.status_code == 200

    overview = client.get("/api/my-tower/overview/")
    assert overview.status_code == 200
    body = overview.json()
    assert body["design"]["id"] == design_id
    assert body["tower_layout"]["pieces"][0]["pieceType"] == "section"
    assert body["artifacts"][0]["role"] == "adventure"
    assert body["artifacts"][0]["contentBinding"] == {
        "kind": "adventure",
        "id": content.id,
    }
    assert body["artifacts"][0]["width"] == 32
    assert body["artifacts"][0]["height"] == 48


@pytest.mark.django_db
def test_raise_tower_is_idempotent(django_user_model):
    """"Raise your Tower" is get-or-create: a second call returns the existing
    personal tower instead of erroring, so the one-per-user cap reads as a fact
    of the world rather than a validation error."""
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/tower-designs/", {"slug": "spire-a", "title": "Spire A"}, format="json")
    assert first.status_code == 201

    second = client.post("/api/tower-designs/", {"slug": "spire-b", "title": "Spire B"}, format="json")
    assert second.status_code == 201
    # Same tower returned, not a second one.
    assert second.json()["id"] == first.json()["id"]
    assert TowerDesign.objects.filter(owner=user, origin="personal").count() == 1


@pytest.mark.django_db
def test_base_piece_is_non_repeatable_via_api(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)
    design_id = client.post("/api/tower-designs/", {"slug": "base-tower", "title": "Tower"}, format="json").json()["id"]
    base_a = Asset.objects.create(kind=KIND_TOWER_PIECE, slug="base-a", label="Base A")
    base_b = Asset.objects.create(kind=KIND_TOWER_PIECE, slug="base-b", label="Base B")
    TowerPieceAsset.objects.create(asset=base_a, piece_type=TOWER_PIECE_BASE)
    TowerPieceAsset.objects.create(asset=base_b, piece_type=TOWER_PIECE_BASE)

    first = client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": base_a.id, "piece_type": "base"},
        format="json",
    )
    second = client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": base_b.id, "piece_type": "base", "sort_order": 7},
        format="json",
    )

    assert first.status_code == 201, first.content
    assert second.status_code == 201, second.content
    bases = TowerPieceInstance.objects.filter(tower_design_id=design_id, piece_type="base")
    assert bases.count() == 1
    base = bases.get()
    assert base.id == first.json()["id"] == second.json()["id"]
    assert base.piece_asset_id == base_b.id
    assert base.storey_index == BASE_STOREY_INDEX
    assert base.sort_order == 7


@pytest.mark.django_db
def test_add_piece_inserts_and_shifts_sort_order(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)
    design_id = client.post("/api/tower-designs/", {"slug": "ordered-tower", "title": "Tower"}, format="json").json()["id"]
    section_a = Asset.objects.create(kind=KIND_TOWER_PIECE, slug="section-a", label="Section A")
    section_b = Asset.objects.create(kind=KIND_TOWER_PIECE, slug="section-b", label="Section B")
    landing = Asset.objects.create(kind=KIND_TOWER_PIECE, slug="landing-a", label="Landing")
    TowerPieceAsset.objects.create(asset=section_a, piece_type=TOWER_PIECE_SECTION)
    TowerPieceAsset.objects.create(asset=section_b, piece_type=TOWER_PIECE_SECTION)
    TowerPieceAsset.objects.create(asset=landing, piece_type=TOWER_PIECE_LANDING)

    client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": section_a.id, "piece_type": "section", "sort_order": 0},
        format="json",
    )
    client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": section_b.id, "piece_type": "section", "sort_order": 1},
        format="json",
    )
    inserted = client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": landing.id, "piece_type": "landing", "sort_order": 1},
        format="json",
    )

    assert inserted.status_code == 201, inserted.content
    assert list(
        TowerPieceInstance.objects.filter(tower_design_id=design_id).order_by("sort_order", "id").values_list(
            "piece_asset__slug",
            "sort_order",
        )
    ) == [("section-a", 0), ("landing-a", 1), ("section-b", 2)]


@pytest.mark.django_db
def test_tower_piece_rejects_non_piece_asset(django_user_model):
    user = make_user(django_user_model)
    design = TowerDesign.objects.create(owner=user, slug="tower", title="Tower")
    artifact = Asset.objects.create(kind=KIND_TOWER_ARTIFACT, slug="banner", label="Banner")

    with pytest.raises(ValidationError):
        TowerPieceInstance.objects.create(
            tower_design=design,
            piece_asset=artifact,
            piece_type="section",
        )


@pytest.mark.django_db
def test_section_holds_multiple_interactables_of_one_kind(django_user_model):
    """The per-section count cap is gone: a section may hold any number of
    interactable artifacts of the same kind."""
    user = make_user(django_user_model)
    design, piece, artifact = _design_piece_and_artifact(user)
    contents = [
        ContentDefinition.objects.create(
            owner=user,
            kind="adventure",
            status="published",
            slug=f"adventure-{index}",
            title=f"Adventure {index}",
        )
        for index in range(2)
    ]

    for content in contents:
        ArtifactPlacement.objects.create(
            tower_design=design,
            target_piece_instance=piece,
            artifact_asset=artifact,
            role="adventure",
            content_definition=content,
        )

    assert design.artifact_placements.filter(role="adventure").count() == 2


@pytest.mark.django_db
def test_section_holds_mixed_interactable_kinds(django_user_model):
    """A section may mix interactable kinds and hold more than three of one. The
    only role rule left is that bound content kind matches the artifact role."""
    user = make_user(django_user_model)
    design, piece, artifact = _design_piece_and_artifact(user)
    challenges = [
        ContentDefinition.objects.create(
            owner=user,
            kind="challenge",
            status="published",
            slug=f"challenge-{index}",
            title=f"Challenge {index}",
        )
        for index in range(4)
    ]
    adventure = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        status="published",
        slug="adventure",
        title="Adventure",
    )

    for content in challenges:
        ArtifactPlacement.objects.create(
            tower_design=design,
            target_piece_instance=piece,
            artifact_asset=artifact,
            role="challenge",
            content_definition=content,
        )
    # A different kind on the same section is fine too.
    ArtifactPlacement.objects.create(
        tower_design=design,
        target_piece_instance=piece,
        artifact_asset=artifact,
        role="adventure",
        content_definition=adventure,
    )

    assert design.artifact_placements.count() == 5

    # Content kind must still match the artifact role.
    mismatched = ContentDefinition.objects.create(
        owner=user,
        kind="tome",
        status="published",
        slug="tome",
        title="Tome",
    )
    with pytest.raises(ValidationError):
        ArtifactPlacement.objects.create(
            tower_design=design,
            target_piece_instance=piece,
            artifact_asset=artifact,
            role="challenge",
            content_definition=mismatched,
        )


@pytest.mark.django_db
def test_publish_allows_any_number_of_challenges(django_user_model):
    """No per-section count rule: a section may hold any number of interactable
    artifacts. Publish only flags interactables that lack published content."""
    from tower_designs.services import TowerDesignService

    user = make_user(django_user_model)
    design, piece, artifact = _design_piece_and_artifact(user)
    challenges = [
        ContentDefinition.objects.create(
            owner=user,
            kind="challenge",
            status="published",
            slug=f"chain-{index}",
            title=f"Chain {index}",
        )
        for index in range(2)
    ]

    # Two challenges on one section — previously rejected as an "incomplete chain",
    # now perfectly valid.
    for content in challenges:
        ArtifactPlacement.objects.create(
            tower_design=design,
            target_piece_instance=piece,
            artifact_asset=artifact,
            role="challenge",
            content_definition=content,
        )
    errors = TowerDesignService().publish_errors(design=design)
    assert not any("three challenges" in error["message"] for error in errors)
    assert errors == []


@pytest.mark.django_db
def test_interactable_artifact_can_live_on_landing(django_user_model):
    from tower_designs.services import TowerDesignService

    user = make_user(django_user_model)
    piece_asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE,
        slug=f"landing-{user.id}",
        label="Tower Landing",
    )
    TowerPieceAsset.objects.create(
        asset=piece_asset,
        piece_type=TOWER_PIECE_LANDING,
        anchors={"walk_rail": {"x1": 12, "y1": 2, "x2": 580, "y2": 2}},
        bounds={
            "x": 0,
            "y": 0,
            "width": 592,
            "height": 73,
            "artifact_safe_bounds": {"x": 44, "y": 0, "width": 504, "height": 24},
        },
    )
    artifact = Asset.objects.create(
        kind=KIND_TOWER_ARTIFACT,
        slug=f"landing-artifact-{user.id}",
        label="Landing Artifact",
    )
    content = ContentDefinition.objects.create(
        owner=user,
        kind="tome",
        status="published",
        slug="landing-tome",
        title="Landing Tome",
    )
    design = TowerDesign.objects.create(owner=user, slug=f"landing-tower-{user.id}", title="Tower")
    landing = TowerPieceInstance.objects.create(
        tower_design=design,
        piece_asset=piece_asset,
        piece_type=TOWER_PIECE_LANDING,
    )

    placement = ArtifactPlacement.objects.create(
        tower_design=design,
        target_piece_instance=landing,
        artifact_asset=artifact,
        role="tome",
        content_definition=content,
        x=296,
        y=-48,
        width=80,
        height=100,
    )

    assert placement.target_piece_instance.piece_type == TOWER_PIECE_LANDING
    assert placement.y < 0
    assert TowerDesignService().publish_errors(design=design) == []


def _design_piece_and_artifact(user):
    piece_asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE,
        slug=f"piece-{user.id}",
        label="Tower Section",
    )
    TowerPieceAsset.objects.create(asset=piece_asset, piece_type=TOWER_PIECE_SECTION)
    artifact = Asset.objects.create(
        kind=KIND_TOWER_ARTIFACT,
        slug=f"artifact-{user.id}",
        label="Artifact",
    )
    design = TowerDesign.objects.create(owner=user, slug=f"tower-{user.id}", title="Tower")
    piece = TowerPieceInstance.objects.create(
        tower_design=design,
        piece_asset=piece_asset,
        piece_type=TOWER_PIECE_SECTION,
    )
    return design, piece, artifact
