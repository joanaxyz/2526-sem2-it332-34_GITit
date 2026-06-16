"""Phase 3: private official fork + share-link behavior."""

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from assets.models import (
    KIND_MONSTER,
    KIND_TOWER_ARTIFACT,
    KIND_TOWER_PIECE,
    TOWER_PIECE_SECTION,
    Asset,
    TowerPieceAsset,
)
from authoring.models import ContentDefinition
from command_adventures.models import CommandAdventure
from curriculum.models import Storey, Tome
from curriculum.selectors import storey_content_overview
from tower_designs.models import (
    ARTIFACT_ROLE_NORMAL,
    ORIGIN_OFFICIAL_FORK,
    ORIGIN_PERSONAL,
    ArtifactPlacement,
    TowerDesign,
    TowerPieceInstance,
)


def make_user(django_user_model, username="builder"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def make_section_asset() -> Asset:
    # A non-"official-*" slug so the default skeleton stays empty and the test
    # controls exactly one (bound) interactive piece.
    asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE, slug="custom-section", label="Tower Section"
    )
    TowerPieceAsset.objects.create(asset=asset, piece_type=TOWER_PIECE_SECTION)
    return asset


def make_official_storey(*, slug="official-storey", number=1) -> Storey:
    storey = Storey.objects.create(
        slug=slug,
        number=number,
        title="Official Storey",
        description="Seeded",
        is_published=True,
    )
    CommandAdventure.objects.create(
        storey=storey,
        slug=f"{slug}-adventure",
        title="Adventure",
        description="Seeded",
        is_published=True,
    )
    Tome.objects.create(
        storey=storey,
        slug=f"{slug}-tome",
        title="Tome",
        placement="above_adventure",
        pages=[],
        is_published=True,
    )
    return storey


@pytest.mark.django_db
def test_official_fork_is_idempotent_and_coexists_with_personal(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/tower-designs/official-fork/")
    assert first.status_code == 201
    fork_id = first.json()["design"]["id"]
    assert first.json()["design"]["origin"] == ORIGIN_OFFICIAL_FORK

    again = client.post("/api/tower-designs/official-fork/")
    assert again.json()["design"]["id"] == fork_id  # idempotent

    # A personal tower can still be created alongside the fork (per-origin cap).
    personal = client.post("/api/tower-designs/", {"slug": "mine", "title": "Mine"}, format="json")
    assert personal.status_code == 201
    assert personal.json()["origin"] == ORIGIN_PERSONAL
    assert TowerDesign.objects.filter(owner=user).count() == 2


@pytest.mark.django_db
def test_official_fork_seeds_and_refreshes_authored_artifacts(
    django_user_model,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_assets", "--skip-grant", verbosity=0)

    storey = Storey.objects.create(
        slug="official-storey",
        number=1,
        title="Official Storey",
        description="Seeded",
        is_published=True,
    )
    CommandAdventure.objects.create(
        storey=storey,
        slug="official-storey-adventure",
        title="Adventure",
        description="Seeded",
        is_published=True,
    )
    Tome.objects.create(
        storey=storey,
        slug="official-storey-tome",
        title="Tome",
        placement="above_adventure",
        pages=[],
        is_published=True,
    )
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/tower-designs/official-fork/")
    assert first.status_code == 201, first.content
    fork_id = first.json()["design"]["id"]
    assert {artifact["role"] for artifact in first.json()["artifacts"]} == {"adventure", "tome"}
    assert ArtifactPlacement.objects.filter(tower_design_id=fork_id).count() == 2

    ArtifactPlacement.objects.filter(tower_design_id=fork_id).delete()
    refreshed = client.post("/api/tower-designs/official-fork/")

    assert refreshed.status_code == 201, refreshed.content
    assert refreshed.json()["design"]["id"] == fork_id
    assert {artifact["role"] for artifact in refreshed.json()["artifacts"]} == {
        "adventure",
        "tome",
    }


@pytest.mark.django_db
def test_official_fork_resyncs_unedited_snapshot_after_storey_reseed(
    django_user_model,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_assets", "--skip-grant", verbosity=0)
    old_storey = make_official_storey(slug="resync-storey")
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/tower-designs/official-fork/")
    assert first.status_code == 201, first.content
    fork_id = first.json()["design"]["id"]
    assert {
        piece.storey_index
        for piece in TowerPieceInstance.objects.filter(tower_design_id=fork_id)
        if piece.piece_type != "crown"
    } == {old_storey.id}

    Storey.objects.all().delete()
    new_storey = make_official_storey(slug="resync-storey")
    assert new_storey.id != old_storey.id

    refreshed = client.post("/api/tower-designs/official-fork/")
    assert refreshed.status_code == 201, refreshed.content
    assert refreshed.json()["design"]["id"] == fork_id
    assert {
        piece.storey_index
        for piece in TowerPieceInstance.objects.filter(tower_design_id=fork_id)
        if piece.piece_type != "crown"
    } == {new_storey.id}
    assert {artifact["role"] for artifact in refreshed.json()["artifacts"]} == {
        "adventure",
        "tome",
    }

    overview = storey_content_overview(user=user, storey_id=new_storey.id)
    assert all(
        piece["instanceId"].startswith(f"tower-{fork_id}-")
        for piece in overview["tower_layout"]["pieces"]
    )


@pytest.mark.django_db
def test_official_fork_resync_preserves_edited_snapshot_after_storey_reseed(
    django_user_model,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_assets", "--skip-grant", verbosity=0)
    old_storey = make_official_storey(slug="edited-resync-storey")
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    fork_id = client.post("/api/tower-designs/official-fork/").json()["design"]["id"]
    edited_piece = (
        TowerPieceInstance.objects.filter(tower_design_id=fork_id, piece_type="section")
        .order_by("sort_order", "id")
        .first()
    )
    edited_piece.transform = {"rotation": 12}
    edited_piece.save(update_fields=["transform"])

    Storey.objects.all().delete()
    new_storey = make_official_storey(slug="edited-resync-storey")
    assert new_storey.id != old_storey.id

    reopened = client.post("/api/tower-designs/official-fork/")
    assert reopened.status_code == 201, reopened.content
    assert reopened.json()["design"]["id"] == fork_id
    edited_piece.refresh_from_db()
    assert edited_piece.transform == {"rotation": 12}
    assert {
        piece.storey_index
        for piece in TowerPieceInstance.objects.filter(tower_design_id=fork_id)
        if piece.piece_type != "crown"
    } == {old_storey.id}


@pytest.mark.django_db
def test_official_view_reflects_fork_skin_transform_and_decoration(
    django_user_model,
    settings,
    tmp_path,
):
    """A user's private fork edits overlay the official storey overview:
    re-skins/transforms apply to the matching piece and decorative artifacts
    appear, while the curriculum's interactive learning artifacts stay intact."""
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_assets", "--skip-grant", verbosity=0)

    storey = Storey.objects.create(
        slug="official-storey",
        number=1,
        title="Official Storey",
        description="Seeded",
        is_published=True,
    )
    CommandAdventure.objects.create(
        storey=storey,
        slug="official-storey-adventure",
        title="Adventure",
        description="Seeded",
        is_published=True,
    )
    Tome.objects.create(
        storey=storey,
        slug="official-storey-tome",
        title="Tome",
        placement="above_adventure",
        pages=[],
        is_published=True,
    )

    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)
    fork_id = client.post("/api/tower-designs/official-fork/").json()["design"]["id"]

    # Re-skin + transform the fork's first section, and drop a decorative artifact on it.
    custom_section = make_section_asset()
    decoration = Asset.objects.create(
        kind=KIND_TOWER_ARTIFACT, owner=user, slug="custom-banner", label="Banner"
    )
    fork_section = (
        TowerPieceInstance.objects.filter(tower_design_id=fork_id, piece_type="section")
        .order_by("sort_order", "id")
        .first()
    )
    fork_section.piece_asset = custom_section
    fork_section.transform = {"rotation": 15}
    fork_section.save(update_fields=["piece_asset", "transform"])
    ArtifactPlacement.objects.create(
        tower_design_id=fork_id,
        target_piece_instance=fork_section,
        artifact_asset=decoration,
        role=ARTIFACT_ROLE_NORMAL,
        x=5,
        y=6,
        width=40,
        height=40,
        z_index=20,
    )

    # Move + re-skin the fork's seeded adventure door (an interactive artifact).
    custom_gate = Asset.objects.create(
        kind=KIND_TOWER_ARTIFACT, owner=user, slug="custom-gate", label="Gate"
    )
    fork_gate = ArtifactPlacement.objects.filter(tower_design_id=fork_id, role="adventure").first()
    fork_gate.x = 321
    fork_gate.y = 99
    fork_gate.artifact_asset = custom_gate
    fork_gate.save(update_fields=["x", "y", "artifact_asset"])

    overview = storey_content_overview(user=user, storey_id=storey.id)
    pieces = overview["tower_layout"]["pieces"]
    artifacts = overview["artifacts"]

    # The matching curriculum section now carries the fork's skin + transform.
    skinned = next(piece for piece in pieces if piece["assetSlug"] == "custom-section")
    assert skinned["transform"] == {"rotation": 15}
    assert skinned["pieceType"] == "section"

    # The decorative artifact appears, targeted at that piece.
    decor = next(a for a in artifacts if a["assetSlug"] == "custom-banner")
    assert decor["role"] == ARTIFACT_ROLE_NORMAL
    assert decor["targetInstanceId"] == skinned["instanceId"]
    assert (decor["x"], decor["y"]) == (5, 6)

    # The interactive door mirrors the fork's move + skin, but keeps the
    # curriculum's content binding (so the storey's adventure still launches).
    gate = next(a for a in artifacts if a["role"] == "adventure")
    assert (gate["x"], gate["y"]) == (321, 99)
    assert gate["assetSlug"] == "custom-gate"
    assert gate["contentBinding"]["kind"] == "adventure"

    # The curriculum's interactive learning artifacts survive the overlay.
    assert {"adventure", "tome"} <= {a["role"] for a in artifacts}


@pytest.mark.django_db
def test_official_view_unchanged_without_fork(django_user_model, settings, tmp_path):
    """No fork → the official overview is the plain curriculum layout."""
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_assets", "--skip-grant", verbosity=0)
    storey = Storey.objects.create(
        slug="plain-storey",
        number=1,
        title="Plain Storey",
        description="Seeded",
        is_published=True,
    )
    user = make_user(django_user_model)

    overview = storey_content_overview(user=user, storey_id=storey.id)

    assert all(
        a["role"] != ARTIFACT_ROLE_NORMAL or "fork-" not in str(a["id"])
        for a in overview["artifacts"]
    )
    assert not TowerDesign.objects.filter(owner=user, origin=ORIGIN_OFFICIAL_FORK).exists()


@pytest.mark.django_db
def test_official_fork_cannot_be_published_or_shared(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)
    fork_id = client.post("/api/tower-designs/official-fork/").json()["design"]["id"]

    publish = client.post(f"/api/tower-designs/{fork_id}/publish/")
    assert publish.status_code == 400
    share = client.post(f"/api/tower-designs/{fork_id}/share/")
    assert share.status_code == 400


@pytest.mark.django_db
def test_share_publishes_monster_and_serves_public_overview(django_user_model):
    author = make_user(django_user_model, "author")
    section = make_section_asset()
    artifact = Asset.objects.create(
        kind=KIND_TOWER_ARTIFACT,
        owner=author,
        slug="custom-adventure-artifact",
        label="Adventure Artifact",
        is_published=False,
    )
    monster = Asset.objects.create(
        kind=KIND_MONSTER, owner=author, slug="pet-slime", label="Pet Slime", is_published=False
    )
    content = ContentDefinition.objects.create(
        owner=author,
        kind="adventure",
        status="published",
        slug="pet-adventure",
        title="Pet Adventure",
        definition={
            "levels": [
                {
                    "slug": "s",
                    "title": "S",
                    "solution_commands": ["git status"],
                    "encounter_spec": [{"species": "pet-slime", "hp": 1}],
                }
            ]
        },
    )

    client = APIClient()
    client.force_authenticate(user=author)
    design_id = client.post(
        "/api/tower-designs/", {"slug": "mine", "title": "Mine"}, format="json"
    ).json()["id"]
    piece = client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": section.id, "piece_type": "section"},
        format="json",
    )
    client.post(
        f"/api/tower-designs/{design_id}/artifacts/",
        {
            "target_piece_instance_id": piece.json()["id"],
            "artifact_asset_id": artifact.id,
            "role": "adventure",
            "content_definition_id": content.id,
            "x": 20,
            "y": 12,
            "width": 40,
            "height": 64,
        },
        format="json",
    )

    share = client.post(f"/api/tower-designs/{design_id}/share/")
    assert share.status_code == 200, share.content
    assert share.json()["visibility"] == "public"
    assert share.json()["share_path"] == f"/tower/shared/{design_id}"

    monster.refresh_from_db()
    assert monster.is_published is True
    assert monster.visibility == "public"

    # Anyone (even anonymous) can read the shared overview.
    anon = APIClient()
    overview = anon.get(f"/api/tower-designs/shared/{design_id}/")
    assert overview.status_code == 200
    assert overview.json()["design"]["id"] == design_id


@pytest.mark.django_db
def test_unshared_tower_is_not_publicly_visible(django_user_model):
    author = make_user(django_user_model, "author")
    design = TowerDesign.objects.create(owner=author, slug="secret", title="Secret")

    anon = APIClient()
    response = anon.get(f"/api/tower-designs/shared/{design.id}/")
    assert response.status_code == 404
