import pytest
from django.core.management import call_command
from django.utils import timezone

from adventures.models import (
    AdventureMastery,
    AdventureProblemAttempt,
    AdventureRun,
    AdventureVariant,
    CommandAdventure,
)
from adventures.scheduler import (
    AdventureScheduler,
    interval_for,
    is_passed,
    pass_bar_for,
    total_achievable,
)
from adventures.scoring import mastery_points
from adventures.services import ordered_problems_for
from common.exceptions import Locked
from curriculum.management.commands.seed_curriculum_v2 import _find_prerequisite_cycle


def make_user(django_user_model, username="sched"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def _adventure_with_at_least(n):
    for adventure in CommandAdventure.objects.filter(is_published=True):
        if len(ordered_problems_for(adventure)) >= n:
            return adventure
    raise AssertionError(f"no seeded adventure with >= {n} problems")


# ---- pure helpers ---------------------------------------------------------

def test_interval_for_clamps_beyond_schedule():
    assert interval_for(0) == 1
    assert interval_for(1) == 3
    assert interval_for(2) == 6
    assert interval_for(99) == 6  # boxes beyond the schedule reuse the last gap


def test_mastery_points_only_awarded_on_box_advance():
    assert mastery_points(box_advanced=True, final_score=100, box_value=10) == 10
    assert mastery_points(box_advanced=True, final_score=70, box_value=10) == 7
    # re-solving a mastered command advances no box -> earns nothing (no farming)
    assert mastery_points(box_advanced=False, final_score=100, box_value=10) == 0


def test_find_prerequisite_cycle_detects_back_edges():
    assert _find_prerequisite_cycle({1: [2], 2: [3], 3: []}) is None
    cycle = _find_prerequisite_cycle({1: [2], 2: [3], 3: [1]})
    assert cycle is not None and set(cycle) >= {1, 2, 3}


# ---- scheduler ------------------------------------------------------------

def test_warmup_introduces_first_command_in_sort_order(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_at_least(2)
    problems = ordered_problems_for(adventure)

    nxt = AdventureScheduler().next_problem(user=user, adventure=adventure)
    assert nxt.id == problems[0].id


def test_prerequisite_blocks_introduction_until_solved(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_at_least(2)
    problems = ordered_problems_for(adventure)
    p0, p1 = problems[0], problems[1]
    p1.prerequisites.set([p0])
    scheduler = AdventureScheduler()

    # p0 introduced but unsolved (box 0): p1 is gated, so it is never served next
    # even though it is the next command in order — the scheduler falls back to p0.
    AdventureMastery.objects.create(
        user=user, adventure_problem=p0, strength=0, introduced=True, last_seen_seq=0
    )
    assert scheduler.next_problem(user=user, adventure=adventure).id != p1.id

    # Solve p0 (box 1): p1's prerequisite is met, so it unblocks and goes next.
    AdventureMastery.objects.filter(user=user, adventure_problem=p0).update(strength=1)
    assert scheduler.next_problem(user=user, adventure=adventure).id == p1.id


def test_variant_selection_prefers_unused(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_at_least(1)
    problem = ordered_problems_for(adventure)[0]
    base = problem.variants.filter(is_published=True).first()
    AdventureVariant.objects.create(
        adventure_problem=problem,
        slug=f"{base.slug}-b",
        label="Variant B",
        initial_state=base.initial_state,
        evaluation_spec=base.evaluation_spec,
        target_state=base.target_state,
        solution_commands=base.solution_commands,
        semantic_key=f"{base.semantic_key}-b",
        scenario_context=base.scenario_context,
        is_published=True,
    )
    scheduler = AdventureScheduler()
    run = AdventureRun.objects.create(user=user, command_adventure=adventure)

    first = scheduler.select_variant(user=user, problem=problem)
    AdventureProblemAttempt.objects.create(
        run=run, adventure_problem=problem, selected_variant=first, order=0, repository_state={}
    )
    # Next pick rotates to the variant this user has not seen yet.
    assert scheduler.select_variant(user=user, problem=problem).id != first.id


# ---- pass bar + unlock ----------------------------------------------------

def test_is_passed_requires_both_floor_and_bar(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_at_least(2)
    problems = ordered_problems_for(adventure)
    ceiling = int(total_achievable(adventure))

    # Max score but the last command was never solved -> floor unmet -> not passed.
    for problem in problems[:-1]:
        AdventureMastery.objects.create(
            user=user,
            adventure_problem=problem,
            strength=problem.required_successful_attempts,
            introduced=True,
        )
    assert is_passed(user=user, adventure=adventure, session_score=ceiling) is False

    # Give the last command its first solve (box 1) -> floor met -> passes.
    AdventureMastery.objects.create(
        user=user, adventure_problem=problems[-1], strength=1, introduced=True
    )
    assert pass_bar_for(adventure) <= ceiling
    assert is_passed(user=user, adventure=adventure, session_score=ceiling) is True


def test_easy_challenge_locked_until_adventure_passed(db, django_user_model):
    from challenges.models import ChallengeLevel
    from challenges.services import ChallengeRunService

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = ChallengeLevel.objects.get(scenario__slug="stage-commit-switch", difficulty="easy")

    with pytest.raises(Locked):
        ChallengeRunService().start_run(
            user=user, level=level, source_entry_point="tower_page"
        )

    adventure = CommandAdventure.objects.get(module=level.module)
    AdventureRun.objects.create(
        user=user, command_adventure=adventure, passed_at=timezone.now()
    )
    run = ChallengeRunService().start_run(
        user=user, level=level, source_entry_point="tower_page"
    )
    assert run.status == "started"
