"""Phase 1 monster-upload + owner-aware registry/validation tests."""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from assets.descriptors import owned_descriptor_map
from assets.models import KIND_MONSTER, Asset, AssetSprite
from authoring.models import ContentDefinition
from authoring.validators import ContentDefinitionValidator
from marketplace.models import ITEM_ASSET, Entitlement


def make_user(django_user_model, username="builder"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def strip_png(cells: int = 4, cell: int = 32) -> bytes:
    """A horizontal sprite strip of `cells` square cells (raw RGBA PNG)."""
    from PIL import Image

    img = Image.new("RGBA", (cell * cells, cell), (10, 20, 30, 255))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def sprite_file(name: str, cells: int = 4) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, strip_png(cells), content_type="image/png")


@pytest.mark.django_db
def test_monster_upload_creates_owned_monster_with_counted_frames(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/assets/monsters/",
        {
            "label": "Gloom Slime",
            "tier": "mob",
            "attack": '{"kind": "melee", "hit_frame": 3, "lunge_px": 40}',
            "metrics": '{"hp_bar_fraction": 0.4}',
            "tags": "neon,ominous",
            "sprite_idle": sprite_file("idle.png", cells=6),
            "fps_idle": "8",
            "sprite_attack": sprite_file("attack.png", cells=4),
            "fps_attack": "11",
        },
        format="multipart",
    )

    assert response.status_code == 201, response.content
    asset = Asset.objects.get(owner=user, kind=KIND_MONSTER, label="Gloom Slime")
    assert asset.visibility == "private"
    assert asset.is_published is False
    assert asset.config["tier"] == "mob"
    assert asset.config["attack"]["hit_frame"] == 3
    assert asset.tags == ["neon", "ominous"]

    idle = AssetSprite.objects.get(asset=asset, action="idle")
    assert idle.frame_count == 6  # counted from the 6-cell strip
    assert idle.loops is True
    attack = AssetSprite.objects.get(asset=asset, action="attack")
    assert attack.frame_count == 4
    assert attack.loops is False


@pytest.mark.django_db
def test_monster_upload_requires_idle_and_attack(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/assets/monsters/",
        {"label": "Half Beast", "tier": "mob", "sprite_idle": sprite_file("idle.png")},
        format="multipart",
    )
    assert response.status_code == 400
    assert "attack" in str(response.content)


@pytest.mark.django_db
def test_owned_descriptor_map_stamps_source_and_includes_entitled(django_user_model):
    owner = make_user(django_user_model, "owner")
    seller = make_user(django_user_model, "seller")

    # An official monster (no owner, published) is the baseline "official" source.
    Asset.objects.create(kind=KIND_MONSTER, slug="official-mob", label="Official Mob", is_published=True)
    # The owner's own private monster.
    Asset.objects.create(kind=KIND_MONSTER, owner=owner, slug="my-mob", label="My Mob", is_published=False)
    # A monster sold by someone else, which `owner` has purchased.
    bought = Asset.objects.create(
        kind=KIND_MONSTER, owner=seller, slug="bought-mob", label="Bought Mob",
        visibility="store", is_published=True,
    )
    Entitlement.objects.create(user=owner, item_kind=ITEM_ASSET, asset=bought)

    result = owned_descriptor_map(owner, KIND_MONSTER)
    assert result["official-mob"]["source"] == "official"
    assert result["my-mob"]["source"] == "owned"
    assert result["bought-mob"]["source"] == "purchased"


@pytest.mark.django_db
def test_validator_accepts_authors_own_private_monster(django_user_model):
    owner = make_user(django_user_model, "owner")
    Asset.objects.create(
        kind=KIND_MONSTER, owner=owner, slug="my-mob", label="My Mob", is_published=False
    )
    content = ContentDefinition.objects.create(
        owner=owner,
        kind="adventure",
        slug="own-monster-adventure",
        title="Own Monster Adventure",
        command_family="git status",
        definition={
            "levels": [
                {
                    "slug": "status-check",
                    "title": "Check status",
                    "initial_state": {},
                    "solution_commands": ["git status"],
                    "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
                    "encounter_spec": [{"species": "my-mob", "hp": 1}],
                }
            ]
        },
    )

    result = ContentDefinitionValidator().validate(content)
    assert result.valid, result.errors
    assert all("my-mob" not in error["message"] for error in result.errors)


@pytest.mark.django_db
def test_validator_rejects_unknown_monster(django_user_model):
    owner = make_user(django_user_model, "owner")
    content = ContentDefinition.objects.create(
        owner=owner,
        kind="adventure",
        slug="ghost-monster-adventure",
        title="Ghost Monster Adventure",
        command_family="git status",
        definition={
            "levels": [
                {
                    "slug": "status-check",
                    "title": "Check status",
                    "initial_state": {},
                    "solution_commands": ["git status"],
                    "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
                    "encounter_spec": [{"species": "does-not-exist", "hp": 1}],
                }
            ]
        },
    )

    result = ContentDefinitionValidator().validate(content)
    assert not result.valid
    assert any("does-not-exist" in error["message"] for error in result.errors)
