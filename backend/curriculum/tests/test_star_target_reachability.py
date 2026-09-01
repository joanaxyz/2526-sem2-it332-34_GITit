"""Star targets must be reachable.

Two stars require ``counted_commands <= min_counted_commands`` and three require
that on the first try, so a target below the counted cost of the authored
solution locks the level at one star for every player, forever. This caught two
seed bugs: blueprint waves whose "read-only" prefix heuristic handed mutating
moves a ``<= 0 commands`` target (``git branch release`` is not read-only), and
multi-command workflow waves/trials that kept the authoring default of 1.
"""

from django.core.management import call_command

from adventures.models import AdventureWave
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
    """Inspection-only waves cost nothing, but keep one command of room."""
    read_only = [{"solution_commands_template": ["git reflog"]}]
    assert star_target_for_variants(read_only, authored=0) == 1
    assert star_target_for_variants([]) == 1


def _required_counted(variants) -> int:
    return max(
        (counted_command_total(variant.solution_commands) for variant in variants),
        default=0,
    )


def test_seeded_adventure_waves_have_reachable_star_targets(db):
    call_command("seed_curriculum")

    unreachable = []
    for wave in AdventureWave.objects.filter(is_published=True).prefetch_related("variants"):
        required = _required_counted(wave.variants.all())
        if (
            wave.min_counted_commands < max(1, required)
            or wave.max_counted_commands < wave.min_counted_commands
        ):
            unreachable.append(
                f"{wave.level.slug}::{wave.slug} target={wave.min_counted_commands} "
                f"limit={wave.max_counted_commands} solution={required}"
            )

    assert unreachable == []


def test_seeded_challenge_trials_have_reachable_star_targets(db):
    call_command("seed_curriculum")

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
