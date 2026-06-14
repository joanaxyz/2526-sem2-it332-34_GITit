"""Phase 4: authored storey settings (reward checkpoints, rosters, pass bar)
reach the compiled runtime storey/adventure instead of being hard-coded."""

import pytest

from authoring.compiler import ContentRuntimeCompiler
from authoring.models import AuthoringStorey, ContentDefinition
from authoring.validators import ContentDefinitionValidator


def _playable_definition() -> dict:
    return {
        "levels": [
            {
                "slug": "s",
                "title": "S",
                "initial_state": {},
                "solution_commands": ["git status"],
                "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
            }
        ]
    }


def make_user(django_user_model, username="author"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def make_admin(django_user_model, username="admin"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345", is_staff=True
    )


@pytest.mark.django_db
def test_admin_authored_chest_rewards_and_pass_bar_reach_runtime(django_user_model):
    # Coins are reserved for official/admin-authored towers.
    user = make_admin(django_user_model)
    content = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        slug="rewarding-adventure",
        title="Rewarding Adventure",
        command_family="git status",
        definition={
            "chest_rewards": [{"threshold": 50, "coins": 80}, {"threshold": 100, "coins": 200}],
            "pass_bar_fraction": 0.75,
            "levels": [
                {
                    "slug": "s",
                    "title": "S",
                    "initial_state": {},
                    "solution_commands": ["git status"],
                    "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
                }
            ],
        },
    )

    runtime = ContentRuntimeCompiler().compile(content=content)

    assert runtime.storey.chest_rewards == [
        {"threshold": 50, "coins": 80},
        {"threshold": 100, "coins": 200},
    ]
    assert float(runtime.command_adventure.pass_bar_fraction) == 0.75


@pytest.mark.django_db
def test_custom_tower_storey_grants_no_coins(django_user_model):
    # A regular player's custom tower never drops coins, even if checkpoints
    # were entered — the compiler strips them. The pass bar is unaffected.
    user = make_user(django_user_model)
    storey = AuthoringStorey.objects.create(
        owner=user,
        slug="player-floor",
        title="Player Floor",
        chest_rewards=[{"threshold": 50, "coins": 80}, {"threshold": 100, "coins": 200}],
        pass_bar_fraction=0.7,
    )
    content = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        slug="player-adventure",
        title="Player Adventure",
        storey=storey,
        command_family="git status",
        definition=_playable_definition(),
    )

    runtime = ContentRuntimeCompiler().compile(content=content)

    assert runtime.storey.chest_rewards == []
    assert float(runtime.command_adventure.pass_bar_fraction) == 0.7


@pytest.mark.django_db
def test_missing_chest_rewards_fall_back_to_defaults(django_user_model):
    user = make_admin(django_user_model)
    content = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        slug="default-rewards",
        title="Default Rewards",
        command_family="git status",
        definition={
            "levels": [
                {
                    "slug": "s",
                    "title": "S",
                    "initial_state": {},
                    "solution_commands": ["git status"],
                    "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
                }
            ]
        },
    )

    runtime = ContentRuntimeCompiler().compile(content=content)
    # Defaults applied instead of the old hard-coded empty list.
    assert len(runtime.storey.chest_rewards) == 4


@pytest.mark.django_db
def test_storey_groups_content_into_one_runtime_storey_with_its_rewards(django_user_model):
    user = make_admin(django_user_model)
    storey = AuthoringStorey.objects.create(
        owner=user,
        slug="floor-1",
        title="Floor One",
        chest_rewards=[{"threshold": 100, "coins": 500}],
        pass_bar_fraction=0.8,
    )
    adventure = ContentDefinition.objects.create(
        owner=user, kind="adventure", storey=storey, slug="adv", title="Adv",
        command_family="git status", definition=_playable_definition(),
    )
    challenge_a = ContentDefinition.objects.create(
        owner=user, kind="challenge", storey=storey, slug="cha", title="Cha A",
        command_family="git status", definition=_playable_definition(),
    )
    challenge_b = ContentDefinition.objects.create(
        owner=user, kind="challenge", storey=storey, slug="chb", title="Cha B",
        command_family="git status", definition=_playable_definition(),
    )

    compiler = ContentRuntimeCompiler()
    runtimes = [compiler.compile(content=c) for c in (adventure, challenge_a, challenge_b)]

    # A storey holds 1 adventure + 1+ challenges, all sharing ONE runtime storey.
    storey_ids = {r.storey_id for r in runtimes}
    assert len(storey_ids) == 1
    shared = runtimes[0].storey
    assert shared.chest_rewards == [{"threshold": 100, "coins": 500}]
    assert float(runtimes[0].command_adventure.pass_bar_fraction) == 0.8
    # Both challenges live under the shared storey.
    assert runtimes[1].challenge.storey_id == shared.id
    assert runtimes[2].challenge.storey_id == shared.id


@pytest.mark.django_db
def test_invalid_chest_rewards_fail_validation(django_user_model):
    user = make_user(django_user_model)
    content = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        slug="bad-rewards",
        title="Bad Rewards",
        command_family="git status",
        definition={
            "chest_rewards": [{"threshold": 150, "coins": -5}],
            "levels": [
                {
                    "slug": "s",
                    "title": "S",
                    "initial_state": {},
                    "solution_commands": ["git status"],
                    "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
                }
            ],
        },
    )

    result = ContentDefinitionValidator().validate(content)
    assert not result.valid
    assert any("threshold" in e["field"] or "coins" in e["field"] for e in result.errors)
