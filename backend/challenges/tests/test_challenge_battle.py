"""Battle layer on the challenge submit path: authoritative boss on the run,
ordered events per command, defeat = the existing budget exhaustion."""

import pytest
from django.core.management import call_command

from battle.state import _target_hp
from challenges.models import ChallengeLevel
from challenges.services import ChallengeRunService
from common.constants import RESULT_TARGET_MATCHED
from practice.services import CommandProcessingService


@pytest.fixture
def runner(db, django_user_model, monkeypatch):
    """A started run on the first published level with a solution, with the
    adventure-pass gate bypassed (battle behavior is difficulty-agnostic)."""
    call_command("seed_curriculum_v2")
    monkeypatch.setattr(ChallengeRunService, "_ensure_unlocked", lambda self, **kwargs: None)
    user = django_user_model.objects.create_user(
        username="bossfighter", email="boss@example.com", password="pass12345"
    )

    def start():
        level = (
            ChallengeLevel.objects.filter(
                is_published=True,
                challenge__is_published=True,
                challenge_variants__is_published=True,
            )
            .order_by("challenge__sort_order", "difficulty")
            .first()
        )
        assert level is not None, "seed should publish at least one challenge level"
        return ChallengeRunService().start_run(
            user=user, level=level, source_entry_point="test"
        )

    return start


def test_run_starts_with_a_living_boss(runner):
    run = runner()
    battle = run.battle_state
    assert battle["schema_version"] == 1
    (boss,) = battle["monsters"]
    assert boss["tier"] == "boss"
    assert boss["alive"] is True
    # Boss HP equals the variant's rule count (distance to target).
    assert boss["hp"] == boss["max_hp"] == _target_hp(run.variant.evaluation_spec)


def test_miss_makes_the_boss_attack(runner):
    run = runner()
    result = CommandProcessingService().submit_command(
        run=run, command="git nonsense-subcommand"
    )
    assert [e["type"] for e in result["battle_events"]] == ["monster_attack"]
    assert result["battle_events"][0]["cause"] == "miss"
    (boss,) = run.battle_state["monsters"]
    assert boss["alive"] is True


def test_solving_kills_the_boss(runner):
    run = runner()
    solution = run.variant.solution_commands
    assert solution, "seed variants carry an official solution"

    result = None
    for command in solution:
        result = CommandProcessingService().submit_command(run=run, command=command)
    assert result["evaluation_result"] == RESULT_TARGET_MATCHED

    types = [e["type"] for e in result["battle_events"]]
    assert "encounter_cleared" in types
    assert "monster_attack" not in types, "a solve is never a miss"
    (boss,) = run.battle_state["monsters"]
    assert boss["alive"] is False and boss["hp"] == 0
    run.refresh_from_db()
    assert run.status == "completed"
    assert run.battle_state["monsters"][0]["alive"] is False


def test_budget_exhaustion_is_player_defeat(runner):
    run = runner()
    budget = run.command_budget_snapshot["max_counted_commands"]

    result = None
    for _ in range(budget):
        result = CommandProcessingService().submit_command(
            run=run, command="git nonsense-subcommand"
        )
    types = [e["type"] for e in result["battle_events"]]
    assert types[-1] == "player_defeat"
    run.refresh_from_db()
    assert run.status == "failed"
    assert "Action limit" in run.failure_reason
