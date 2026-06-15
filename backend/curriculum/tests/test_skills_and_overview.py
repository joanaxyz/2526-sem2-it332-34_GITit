"""Isolated tests for the learned-skills registry and the combined storey
content overview. Build minimal rows directly (no full curriculum seed) so the
selectors are exercised in isolation."""

from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from command_adventures.models import AdventureRun, CommandAdventure
from curriculum.models import CommandSkill, Storey, Tome
from curriculum.selectors import learned_command_skills, storey_content_overview


def _storey(slug="s1", number=1) -> Storey:
    return Storey.objects.create(slug=slug, number=number, title="Storey", description="d")


def test_learned_skills_empty_until_adventure_passed(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="u", email="u@example.com", password="pass12345"
    )
    storey = _storey()
    adventure = CommandAdventure.objects.create(
        storey=storey, slug="s1-adv", title="Adventure", description="d"
    )
    CommandSkill.objects.create(
        storey=storey, slug="commit", base_command="git commit", title="Commit"
    )

    # Not learned until the Command Adventure is passed.
    assert learned_command_skills(user=user) == []

    AdventureRun.objects.create(
        user=user, command_adventure=adventure, passed_at=timezone.now()
    )
    learned = learned_command_skills(user=user)
    assert [skill["base_command"] for skill in learned] == ["git commit"]
    assert learned[0]["storey_number"] == 1
    assert learned[0]["storey_title"] == "Storey"


def test_learned_skills_anonymous_returns_empty(db):
    assert learned_command_skills(user=AnonymousUser()) == []


def test_storey_overview_bundles_adventure_tomes_and_challenges(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="u2", email="u2@example.com", password="pass12345"
    )
    storey = _storey(slug="s2", number=2)
    CommandAdventure.objects.create(storey=storey, slug="s2-adv", title="Adv", description="d")
    Tome.objects.create(
        storey=storey, slug="t", title="Tome", placement="above_adventure", pages=[]
    )

    overview = storey_content_overview(user=user, storey_id=storey.id)
    assert overview["storey_id"] == storey.id
    assert overview["command_adventure"]["item_type"] == "command_adventure"
    assert overview["command_adventure"]["is_passed"] is False
    assert [tome["slug"] for tome in overview["tomes"]] == ["t"]
    assert overview["challenges"] == []
    assert overview["tower_layout"]["storeyId"] == storey.id
    assert [piece["pieceType"] for piece in overview["tower_layout"]["pieces"]] == [
        "spire",
        "window_section",
        "tome",
        "landing",
        "adventure_section",
        "landing",
        "challenge_section",
        "landing",
    ]
    tome_piece = overview["tower_layout"]["pieces"][2]
    assert tome_piece["assetSlug"] == "official-tome"
    assert tome_piece["contentBinding"] == {"kind": "tome", "id": overview["tomes"][0]["id"]}
    adventure_piece = overview["tower_layout"]["pieces"][4]
    assert adventure_piece["contentBinding"] == {
        "kind": "adventure",
        "id": overview["command_adventure"]["id"],
    }
