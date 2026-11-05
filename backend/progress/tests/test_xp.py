"""XP pays once per source, and the leaderboard exposes only what it should."""

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import AdventureLevelTierRun
from players.models import PlayerPreferences
from players.services import get_or_create_player
from progress.models import (
    AdventureLevelTierCompletion,
    CoinTransaction,
    KpiCheckpoint,
    Wallet,
    XpTransaction,
)
from progress.serializers import LeaderboardResponseSerializer
from progress.services import MetricsService
from progress.services.leaderboard import TOP_ENTRIES, leaderboard
from progress.xp import XP_PER_STAR, XpService, award_tier_xp
from shop.models import PlayerLoadout
from testing.kpi_fixtures import bundle, end, start


def _learner(django_user_model, username, **extra):
    return get_or_create_player(django_user_model.objects.create_user(username=username, **extra))


def _give_xp(player, amount, key="grant"):
    XpService().award(player=player, amount=amount, reason="tier_clear", award_key=key)


def _balance(player):
    wallet = Wallet.objects.filter(player=player).first()
    return wallet.balance if wallet else 0


@pytest.mark.django_db
def test_a_cleared_tier_pays_its_ladder_amount_and_stars_once(django_user_model):
    player, tier, _scenario, _variants = bundle(django_user_model, required=1)

    assert award_tier_xp(player=player, tier=tier, stars=1) == 50 + XP_PER_STAR
    assert award_tier_xp(player=player, tier=tier, stars=1) == 0
    assert XpService().total(player=player) == 60


@pytest.mark.django_db
def test_a_better_grade_pays_only_the_new_stars(django_user_model):
    player, tier, _scenario, _variants = bundle(django_user_model, required=1)
    award_tier_xp(player=player, tier=tier, stars=1)

    assert award_tier_xp(player=player, tier=tier, stars=3) == 2 * XP_PER_STAR
    assert award_tier_xp(player=player, tier=tier, stars=2) == 0


@pytest.mark.django_db
def test_clearing_a_tier_in_play_credits_xp_and_reports_it(django_user_model):
    player, tier, _scenario, _variants = bundle(django_user_model, required=1)

    run = end(start(player, tier))

    completion = AdventureLevelTierCompletion.objects.get(player=player, tier=tier)
    assert run.status == "completed"
    assert XpService().total(player=player) == 50 + completion.stars * XP_PER_STAR
    assert MetricsService().dashboard_summary(player=player)["xp"] == XpService().total(
        player=player
    )


@pytest.mark.django_db
def test_first_run_checkpoint_clear_pays_the_full_reward_and_practice_adds_nothing(
    django_user_model,
):
    player, tier, _scenario, _variants = bundle(django_user_model, required=1)
    end(start(player, tier))
    xp, coins = XpService().total(player=player), _balance(player)

    end(start(player, tier, transfer=True))

    assert XpService().total(player=player) == xp + 150
    assert _balance(player) == coins + 150

    practice = end(start(player, tier, transfer=True))

    assert practice.is_replay
    assert XpService().total(player=player) == xp + 150
    assert _balance(player) == coins + 150


@pytest.mark.django_db
def test_a_failed_checkpoint_can_still_earn_the_practice_reward_once(django_user_model):
    player, tier, _scenario, _variants = bundle(django_user_model, required=1)
    end(start(player, tier))
    xp, coins = XpService().total(player=player), _balance(player)

    end(start(player, tier, transfer=True), passed=False)

    assert XpService().total(player=player) == xp
    end(start(player, tier, transfer=True))
    end(start(player, tier, transfer=True))

    assert XpService().total(player=player) == xp + 50
    assert _balance(player) == coins + 50
    point = KpiCheckpoint.objects.get(player=player, tier=tier, kind="transfer")
    assert point.passed is False  # Practice earns the smaller reward; the result stands.


@pytest.mark.django_db
def test_checkpoint_gitcoins_count_as_earned_through_play(django_user_model):
    player, tier, _scenario, _variants = bundle(django_user_model, required=1)
    end(start(player, tier))
    end(start(player, tier, transfer=True))

    stats = MetricsService().stats_summary(player=player)

    assert stats["headline"]["gitcoins_earned"] == _balance(player)
    assert CoinTransaction.objects.filter(
        player=player, reason="transfer_checkpoint_reward"
    ).exists()


@pytest.mark.django_db
def test_backfill_credits_earlier_progress_once_and_dry_run_writes_nothing(django_user_model):
    player, tier, _scenario, _variants = bundle(django_user_model, required=1)
    AdventureLevelTierCompletion.objects.create(player=player, tier=tier, stars=2)
    AdventureLevelTierRun.objects.all().delete()

    call_command("award_missing_xp", "--dry-run", verbosity=0)
    assert not XpTransaction.objects.exists()

    call_command("award_missing_xp", verbosity=0)
    credited = XpService().total(player=player)
    call_command("award_missing_xp", verbosity=0)

    # The fixture's medium tier (35, no stars) and this hard tier (50, two stars).
    assert credited == 35 + 50 + 2 * XP_PER_STAR
    assert XpService().total(player=player) == credited


@pytest.mark.django_db
def test_board_orders_by_xp_and_the_first_to_reach_a_total_ranks_higher(django_user_model):
    first = _learner(django_user_model, "first")
    second = _learner(django_user_model, "second")
    leader = _learner(django_user_model, "leader")
    _give_xp(first, 100)
    _give_xp(second, 100)
    _give_xp(leader, 300)

    board = leaderboard(player=second)

    assert [(row["rank"], row["username"]) for row in board["entries"]] == [
        (1, "leader"),
        (2, "first"),
        (3, "second"),
    ]
    assert board["you"] == {"rank": 3, "value": 100, "hidden": False}


@pytest.mark.django_db
def test_equal_counts_share_a_rank(django_user_model):
    one, tier_one, _scenario, _variants = bundle(django_user_model, username="one", required=1)
    two, tier_two, _scenario, _variants = bundle(django_user_model, username="two", required=1)
    three, tier_three, _scenario, _variants = bundle(
        django_user_model, username="three", required=1
    )
    AdventureLevelTierCompletion.objects.create(player=one, tier=tier_one, stars=3)
    AdventureLevelTierCompletion.objects.create(player=one, tier=tier_two, stars=3)
    AdventureLevelTierCompletion.objects.create(player=two, tier=tier_two, stars=3)
    AdventureLevelTierCompletion.objects.create(player=three, tier=tier_three, stars=3)

    board = leaderboard(player=one, category="perfect_clears")

    assert sorted((row["rank"], row["value"]) for row in board["entries"]) == [
        (1, 2),
        (2, 1),
        (2, 1),
    ]


@pytest.mark.django_db
def test_hidden_and_staff_accounts_stay_off_the_board(django_user_model):
    viewer = _learner(django_user_model, "viewer")
    hidden = _learner(django_user_model, "hidden")
    staff = _learner(django_user_model, "staff", is_staff=True)
    PlayerPreferences.objects.create(player=hidden, leaderboard_visible=False)
    for player in (viewer, hidden, staff):
        _give_xp(player, 100)

    assert [row["username"] for row in leaderboard(player=viewer)["entries"]] == ["viewer"]

    own = leaderboard(player=hidden)
    assert [row["username"] for row in own["entries"]] == ["viewer"]
    assert own["you"] == {"rank": None, "value": 100, "hidden": True}
    assert leaderboard(player=staff)["you"]["rank"] is None


@pytest.mark.django_db
def test_board_shows_the_top_entries_and_still_places_you(django_user_model):
    players = [_learner(django_user_model, f"learner{i}") for i in range(TOP_ENTRIES + 2)]
    for index, player in enumerate(players):
        _give_xp(player, 100 + index)

    board = leaderboard(player=players[0])

    assert len(board["entries"]) == TOP_ENTRIES
    assert all(not row["is_you"] for row in board["entries"])
    assert board["you"]["rank"] == TOP_ENTRIES + 2


@pytest.mark.django_db
def test_a_learner_without_a_score_is_not_listed(django_user_model):
    viewer = _learner(django_user_model, "fresh")

    board = leaderboard(player=viewer)

    assert board["entries"] == []
    assert board["you"] == {"rank": None, "value": 0, "hidden": False}


@pytest.mark.django_db
def test_leaderboard_endpoint_returns_public_identity_only_and_rejects_unknown_categories(
    django_user_model,
):
    user = django_user_model.objects.create_user(username="api", email="private@example.com")
    _give_xp(get_or_create_player(user), 100)
    client = APIClient()
    client.force_authenticate(user)

    response = client.get("/api/progress/leaderboard/?category=xp")

    assert response.status_code == 200
    assert LeaderboardResponseSerializer(data=response.json()).is_valid(raise_exception=True)
    assert set(response.json()["entries"][0]) == {
        "rank",
        "username",
        "companion_slug",
        "value",
        "is_you",
    }
    assert "private@example.com" not in response.content.decode()
    assert client.get("/api/progress/leaderboard/?category=mastery").status_code == 400


@pytest.mark.django_db
def test_board_avatars_follow_equipped_companions_without_per_player_queries(
    django_user_model, django_assert_num_queries
):
    equipped = _learner(django_user_model, "equipped")
    unequipped = _learner(django_user_model, "unequipped")
    missing_loadout = _learner(django_user_model, "missing")
    PlayerLoadout.objects.update_or_create(
        player=equipped, defaults={"active_companion_slug": "white"}
    )
    PlayerLoadout.objects.update_or_create(
        player=unequipped, defaults={"active_companion_slug": None}
    )
    PlayerLoadout.objects.filter(player=missing_loadout).delete()
    for player in (equipped, unequipped, missing_loadout):
        _give_xp(player, 100)

    with django_assert_num_queries(4):
        board = leaderboard(player=equipped)

    assert {row["username"]: row["companion_slug"] for row in board["entries"]} == {
        "equipped": "white",
        "unequipped": None,
        "missing": None,
    }
    PlayerLoadout.objects.filter(player=equipped).update(active_companion_slug="black")
    assert leaderboard(player=equipped)["entries"][0]["companion_slug"] == "black"


@pytest.mark.django_db
def test_leaderboard_preference_saves_through_the_preferences_api(django_user_model):
    user = django_user_model.objects.create_user(username="prefs")
    client = APIClient()
    client.force_authenticate(user)

    assert client.get("/api/player/preferences/").json()["leaderboard_visible"] is True
    response = client.patch(
        "/api/player/preferences/", {"leaderboard_visible": False}, format="json"
    )

    assert response.json()["leaderboard_visible"] is False
