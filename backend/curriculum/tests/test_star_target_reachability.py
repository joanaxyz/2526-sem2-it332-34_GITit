"""Star targets must be reachable.

Two stars require ``counted_commands <= min_counted_commands`` and three require
that with at most one retry, so a target below the counted cost of the authored
solution locks the level at one star for every player, forever. This caught two
seed bugs: blueprint scenarios whose "read-only" prefix heuristic handed mutating
moves a ``<= 0 commands`` target (``git branch release`` is not read-only), and
multi-command workflow scenarios/trials that kept the authoring default of 1.
"""

from django.core.management import call_command

from adventures.models import AdventureLevelTierScenarioVariant
from adventures.services.tier_budget import command_budget
from challenges.models import ChallengeTrial
from common.runtime import counted_command_total, star_target_for_variants


def test_counted_command_total_bills_like_the_runtime():
    """The engine classifier - not a prefix list - decides what is free."""
    assert counted_command_total(["git branch", "git status", "git reflog"]) == 0
    assert counted_command_total(["git branch release"]) == 1
    assert counted_command_total(["git remote -v", "git remote add origin url"]) == 1
    assert counted_command_total(None) == 0


def test_star_target_covers_the_costliest_variant():
    variants = [
        {"solution_commands_template": ["git add a.txt"]},
        {"solution_commands_template": ["git status", "git add a.txt", "git commit -m 'x'"]},
    ]
    assert star_target_for_variants(variants) == 2
    # An authored value may raise the target, never lower it below the cost.
    assert star_target_for_variants(variants, authored=4) == 4
    assert star_target_for_variants(variants, authored=1) == 2
    assert star_target_for_variants(variants, authored=0) == 2


def test_star_target_never_renders_as_zero_commands():
    """Inspection-only scenarios cost nothing, but keep one command of room."""
    read_only = [{"solution_commands_template": ["git reflog"]}]
    assert star_target_for_variants(read_only, authored=0) == 1
    assert star_target_for_variants([]) == 1


def _required_counted(variants) -> int:
    return max(
        (counted_command_total(variant.solution_commands) for variant in variants),
        default=0,
    )


def test_seeded_adventure_tier_variants_have_reachable_star_targets(db):
    """A tier run takes its budget from the served variant (falling back to the
    scenario's), so every published variant must be able to earn three stars."""
    call_command("seed_curriculum", verbosity=0)

    unreachable = []
    variants = AdventureLevelTierScenarioVariant.objects.filter(
        is_published=True, scenario__is_published=True
    ).select_related("scenario__tier__adventure_level")
    for variant in variants:
        target, limit = command_budget(variant)
        required = counted_command_total(variant.solution_commands)
        if target < max(1, required) or limit < target:
            unreachable.append(
                f"{variant.scenario.tier.adventure_level.slug}::{variant.scenario.tier.difficulty}::"
                f"{variant.slug} target={target} limit={limit} solution={required}"
            )

    assert variants.exists()
    assert unreachable == []


def test_seeded_challenge_trials_have_reachable_star_targets(db):
    call_command("seed_curriculum", verbosity=0)

    unreachable = []
    for trial in ChallengeTrial.objects.filter(is_published=True).prefetch_related("variants"):
        required = _required_counted(trial.variants.all())
        if (
            trial.min_counted_commands < max(1, required)
            or trial.max_counted_commands < trial.min_counted_commands
        ):
            unreachable.append(
                f"{trial.challenge_level.slug}::{trial.difficulty} "
                f"target={trial.min_counted_commands} limit={trial.max_counted_commands} "
                f"solution={required}"
            )

    assert unreachable == []
