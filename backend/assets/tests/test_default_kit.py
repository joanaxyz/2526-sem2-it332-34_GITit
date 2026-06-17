"""The default Arcane Spire kit is granted into each player's asset registry."""

import pytest

from assets.descriptors import owned_descriptor_map
from assets.models import KIND_CHARACTER, KIND_RELIC, Asset, RelicAsset
from assets.services import DEFAULT_KIT_TAG, default_kit_assets, grant_default_assets
from marketplace.models import Entitlement


def make_user(django_user_model, username="player"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def _kit_piece(slug="official-relic"):
    asset = Asset.objects.create(
        kind=KIND_RELIC, slug=slug, label="Arcane Relic", is_published=True, tags=[DEFAULT_KIT_TAG]
    )
    RelicAsset.objects.create(asset=asset)
    return asset


@pytest.mark.django_db
def test_default_kit_lists_only_tagged_official_assets():
    tagged = _kit_piece()
    Asset.objects.create(kind=KIND_CHARACTER, slug="blue", label="Blue", is_published=True, tags=[DEFAULT_KIT_TAG])
    # Untagged official + a tagged-but-unpublished asset must be excluded.
    Asset.objects.create(kind=KIND_RELIC, slug="plain", label="Plain", is_published=True, tags=[])
    Asset.objects.create(kind=KIND_CHARACTER, slug="hidden", label="Hidden", is_published=False, tags=[DEFAULT_KIT_TAG])

    slugs = {a.slug for a in default_kit_assets()}
    assert slugs == {tagged.slug, "blue"}


@pytest.mark.django_db
def test_grant_default_assets_is_idempotent(django_user_model):
    _kit_piece()
    Asset.objects.create(kind=KIND_CHARACTER, slug="blue", label="Blue", is_published=True, tags=[DEFAULT_KIT_TAG])
    user = make_user(django_user_model)

    first = grant_default_assets(user)
    second = grant_default_assets(user)

    assert first == 2
    assert second == 0  # nothing new the second time
    assert Entitlement.objects.filter(user=user).count() == 2


@pytest.mark.django_db
def test_registration_grants_the_kit(django_user_model):
    _kit_piece()
    Asset.objects.create(kind=KIND_CHARACTER, slug="blue", label="Blue", is_published=True, tags=[DEFAULT_KIT_TAG])

    from accounts.services import UserService

    user = UserService().register_account(username="newbie", email="newbie@example.com", password="pass12345")
    assert Entitlement.objects.filter(user=user, asset__slug="blue").exists()
    assert Entitlement.objects.filter(user=user, asset__slug="official-relic").exists()


@pytest.mark.django_db
def test_granted_official_piece_stays_labelled_official(django_user_model):
    # An entitled official asset must not be downgraded to "purchased" in the
    # owned descriptor map — it is a default grant, not a purchase.
    _kit_piece()
    user = make_user(django_user_model)
    grant_default_assets(user)

    descriptors = owned_descriptor_map(user, KIND_RELIC)
    assert descriptors["official-relic"]["source"] == "official"
