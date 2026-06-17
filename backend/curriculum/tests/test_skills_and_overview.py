"""Isolated tests for the learned-skills registry and the combined chapter
content overview. Build minimal rows directly (no full curriculum seed) so the
selectors are exercised in isolation."""

from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from challenges.models import Challenge, ChallengeLevel
from command_adventures.models import AdventureRun, CommandAdventure
from curriculum.models import CommandSkill, Chapter, Tome
from curriculum.selectors import learned_command_skills, chapter_content_overview


def _chapter(slug="s1", number=1) -> Chapter:
    return Chapter.objects.create(slug=slug, number=number, title="Chapter", description="d")


def test_learned_skills_empty_until_adventure_passed(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="u", email="u@example.com", password="pass12345"
    )
    chapter = _chapter()
    adventure = CommandAdventure.objects.create(
        chapter=chapter, slug="s1-adv", title="Adventure", description="d"
    )
    CommandSkill.objects.create(
        chapter=chapter, slug="commit", base_command="git commit", title="Commit"
    )

    # Not learned until the Command Adventure is passed.
    assert learned_command_skills(user=user) == []

    AdventureRun.objects.create(
        user=user, command_adventure=adventure, passed_at=timezone.now()
    )
    learned = learned_command_skills(user=user)
    assert [skill["base_command"] for skill in learned] == ["git commit"]
    assert learned[0]["chapter_number"] == 1
    assert learned[0]["chapter_title"] == "Chapter"


def test_learned_skills_anonymous_returns_empty(db):
    assert learned_command_skills(user=AnonymousUser()) == []


def test_chapter_overview_bundles_adventure_tomes_and_challenges(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="u2", email="u2@example.com", password="pass12345"
    )
    chapter = _chapter(slug="s2", number=2)
    CommandAdventure.objects.create(chapter=chapter, slug="s2-adv", title="Adv", description="d")
    Tome.objects.create(
        chapter=chapter, slug="t", title="Tome", placement="above_adventure", pages=[]
    )

    overview = chapter_content_overview(user=user, chapter_id=chapter.id)
    assert overview["chapter_id"] == chapter.id
    assert overview["command_adventure"]["item_type"] == "command_adventure"
    assert overview["command_adventure"]["is_passed"] is False
    assert [tome["slug"] for tome in overview["tomes"]] == ["t"]
    assert overview["challenges"] == []
    relics = overview["relic_layout"]["relics"]
    assert overview["relic_layout"]["chapterId"] == chapter.id
    # Every relic uses the single official relic art; the kind drives behaviour.
    assert {relic["assetSlug"] for relic in relics} == {"official-relic"}
    assert [relic["kind"] for relic in relics] == ["tome", "adventure"]
    tome_relic = relics[0]
    assert tome_relic["contentBinding"] == {"kind": "tome", "id": overview["tomes"][0]["id"]}
    assert tome_relic["interactiveViewbox"]
    assert tome_relic["landingViewbox"]
    adventure_relic = relics[1]
    assert adventure_relic["contentBinding"] == {
        "kind": "adventure",
        "id": overview["command_adventure"]["id"],
    }


def test_chapter_overview_emits_challenge_artifact_per_difficulty(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="u3", email="u3@example.com", password="pass12345"
    )
    chapter = _chapter(slug="s3", number=3)
    CommandAdventure.objects.create(chapter=chapter, slug="s3-adv", title="Adv", description="d")
    challenge = Challenge.objects.create(
        chapter=chapter,
        slug="challenge",
        title="Challenge",
        summary="d",
    )
    levels = [
        ChallengeLevel.objects.create(challenge=challenge, difficulty=difficulty)
        for difficulty in ("easy", "medium", "hard")
    ]

    overview = chapter_content_overview(user=user, chapter_id=chapter.id)
    challenge_relics = [
        relic for relic in overview["relic_layout"]["relics"] if relic["kind"] == "challenge"
    ]

    assert {relic["assetSlug"] for relic in challenge_relics} == {"official-relic"}
    # One relic per difficulty, laid out left-to-right in a row.
    assert [relic["x"] for relic in challenge_relics] == [80, 300, 520]
    assert len({relic["y"] for relic in challenge_relics}) == 1
    assert [relic["contentBinding"]["difficulty"] for relic in challenge_relics] == [
        "easy",
        "medium",
        "hard",
    ]
    assert [relic["contentBinding"]["levelId"] for relic in challenge_relics] == [
        level.id for level in levels
    ]
