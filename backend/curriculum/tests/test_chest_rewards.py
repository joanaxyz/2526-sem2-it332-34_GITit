import pytest
from adventures.models import AdventureLevel
from common.exceptions import Locked
from progress.models import AdventureLevelCompletion, CoinTransaction, Wallet
from rest_framework.test import APIClient
from testing.runtime_factories import api_client_for, create_stage_readme_adventure_run, make_user

from curriculum.models import Story
from curriculum.services import CHEST_SCHEDULE, ChapterChestService

pytestmark = pytest.mark.django_db


@pytest.fixture
def chest_fixture(django_user_model):
    fixture = create_stage_readme_adventure_run(django_user_model, username="chest-rewards")
    for index in range(3):
        AdventureLevel.objects.create(
            chapter=fixture.chapter,
            slug=f"chest-level-{index}",
            title=f"Chest level {index}",
            sort_order=index + 1,
        )
    return fixture


def complete_levels(fixture, count):
    for level in AdventureLevel.objects.filter(chapter=fixture.chapter).order_by("id")[:count]:
        AdventureLevelCompletion.objects.get_or_create(player=fixture.player, adventure_level=level)


def test_read_checks_actual_progress_and_payment_without_awarding(chest_fixture):
    fixture = chest_fixture
    complete_levels(fixture, 1)
    client = api_client_for(fixture.user)

    response = client.get(f"/api/chapters/{fixture.chapter.id}/chests/")

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {**chest, "unlocked": chest["threshold"] == 25, "claimed": False}
            for chest in CHEST_SCHEDULE
        ],
        "balance": 0,
        "coins_awarded": 0,
    }
    assert not CoinTransaction.objects.filter(player=fixture.player).exists()


def test_open_recovers_each_earned_reward_once_and_persists_status(chest_fixture):
    fixture = chest_fixture
    client = api_client_for(fixture.user)
    url = f"/api/chapters/{fixture.chapter.id}/chests/"
    balance = 0
    for index, chest in enumerate(CHEST_SCHEDULE, start=1):
        complete_levels(fixture, index)
        balance += chest["coins"]
        for expected_award in [chest["coins"], 0]:
            response = client.post(url, {"threshold": chest["threshold"]}, format="json")
            assert response.status_code == 200
            assert response.json()["coins_awarded"] == expected_award
            assert response.json()["balance"] == balance
        saved = client.get(url).json()
        assert saved["results"][index - 1]["claimed"] is True

    assert balance == 335
    assert Wallet.objects.get(player=fixture.player).balance == 335
    assert (
        CoinTransaction.objects.filter(player=fixture.player, reason="chapter_chest").count() == 4
    )
    assert ChapterChestService().award_chests(player=fixture.player, chapter=fixture.chapter) == []


def test_automatic_payout_is_shown_as_collected_and_cannot_pay_again(chest_fixture):
    fixture = chest_fixture
    complete_levels(fixture, 4)
    assert (
        ChapterChestService().award_chests(player=fixture.player, chapter=fixture.chapter)
        == CHEST_SCHEDULE
    )
    client = api_client_for(fixture.user)
    url = f"/api/chapters/{fixture.chapter.id}/chests/"
    assert all(chest["claimed"] for chest in client.get(url).json()["results"])

    response = client.post(url, {"threshold": 100, "coins": 999999}, format="json")

    assert response.status_code == 200
    assert response.json()["coins_awarded"] == 0
    assert response.json()["balance"] == 335
    assert CoinTransaction.objects.filter(player=fixture.player).count() == 4


@pytest.mark.parametrize("threshold", [25, 100, 26, 0, 101, "invalid", None])
def test_locked_or_invalid_chest_cannot_credit_wallet(chest_fixture, threshold):
    fixture = chest_fixture
    response = api_client_for(fixture.user).post(
        f"/api/chapters/{fixture.chapter.id}/chests/", {"threshold": threshold}, format="json"
    )
    assert response.status_code == 400
    assert not CoinTransaction.objects.filter(player=fixture.player).exists()


def test_chest_rewards_are_player_scoped(chest_fixture, django_user_model):
    fixture = chest_fixture
    complete_levels(fixture, 4)
    ChapterChestService().award_chests(player=fixture.player, chapter=fixture.chapter)
    other_user = make_user(django_user_model, "other-chest-player")
    client = api_client_for(other_user)
    url = f"/api/chapters/{fixture.chapter.id}/chests/"

    summary = client.get(url).json()
    assert summary["balance"] == 0
    assert not any(chest["claimed"] or chest["unlocked"] for chest in summary["results"])
    assert client.post(url, {"threshold": 25}, format="json").status_code == 400


def test_chests_require_authentication_and_published_accessible_chapter(chest_fixture):
    fixture = chest_fixture
    url = f"/api/chapters/{fixture.chapter.id}/chests/"
    anonymous = APIClient()
    assert anonymous.get(url).status_code == 401
    assert anonymous.post(url, {"threshold": 25}, format="json").status_code == 401
    client = api_client_for(fixture.user)
    prerequisite = Story.objects.create(slug="chest-prerequisite", title="Prerequisite")
    fixture.story.prerequisite_story = prerequisite
    fixture.story.save(update_fields=["prerequisite_story"])
    assert client.get(url).status_code == Locked.status_code
    assert client.post(url, {"threshold": 25}, format="json").status_code == Locked.status_code
    fixture.chapter.is_published = False
    fixture.chapter.save(update_fields=["is_published"])
    assert client.get(url).status_code == 404
    assert client.post(url, {"threshold": 25}, format="json").status_code == 404


def test_empty_chapter_and_rounded_progress_do_not_unlock_chests(chest_fixture, monkeypatch):
    import curriculum.services.chests as chests_module

    fixture = chest_fixture
    monkeypatch.setattr(
        chests_module,
        "chapter_completion_denominator_map",
        lambda **_: {fixture.chapter.id: 100001},
    )
    monkeypatch.setattr(
        chests_module, "chapter_completion_count_map", lambda **_: {fixture.chapter.id: 25000}
    )
    service = ChapterChestService()
    assert not service.reward_summary(player=fixture.player, chapter=fixture.chapter)["results"][0][
        "unlocked"
    ]
    assert service.award_chests(player=fixture.player, chapter=fixture.chapter) == []
    monkeypatch.setattr(chests_module, "chapter_completion_denominator_map", lambda **_: {})
    assert service.award_chests(player=fixture.player, chapter=fixture.chapter) == []
