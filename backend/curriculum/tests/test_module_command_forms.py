"""The module curriculum registers, attaches and credits the forms it teaches.

The authoring rules are documented in CONTENT_AUTHORING_GUIDE.md.
"""

from django.core.management import call_command

from adventures.models import AdventureLevel, AdventureLevelTierWaveVariant
from adventures.services import AdventureLevelTierRunService
from adventures.services.tier_command_processing import AdventureLevelTierCommandProcessingService
from curriculum.models import CommandForm
from players.services import get_or_create_player
from practice.models import CommandStep
from tutoring.services.forms import resolve_form
from tutoring.services.planner import plan_introduction

REGISTERED_FOR_WAVES = {
    2: ["git branch <branch> [<start-point>]"],
    3: [
        "git commit --no-edit",
        "git mergetool",
        "git merge --abort",
        "git config <key> <value>",
        "git cherry-pick -x <commit>",
        "git cherry-pick --continue",
    ],
    4: [
        "git rebase --onto <newbase> <upstream> [<branch>]",
        "git rebase --abort",
        "git rebase --continue",
        "git reset --hard <commit>",
    ],
}

# Diagnostics never debut and need no registered form (PLAN.md §3, rule 7).
UNREGISTERED_DIAGNOSTICS = {"git log --oneline", "git log --oneline <value>"}


def _level(slug: str) -> AdventureLevel:
    return AdventureLevel.objects.get(slug=slug, is_published=True)


def test_the_forms_the_waves_need_are_registered_under_their_module(db):
    call_command("seed_curriculum", verbosity=0)

    for module, usages in REGISTERED_FOR_WAVES.items():
        published = set(
            CommandForm.objects.filter(
                is_published=True, chapter__number=module, slug__startswith="legacy-m"
            ).values_list("usage_form", flat=True)
        )
        assert set(usages) <= published, (module, set(usages) - published)
    # The prepared-message merge commit replaced a form no solution ever typed.
    assert not CommandForm.objects.filter(
        is_published=True, usage_form="git commit [-m <message>]"
    ).exists()


def test_every_solution_command_resolves_to_a_registered_form(db):
    call_command("seed_curriculum", verbosity=0)

    unregistered = set()
    for variant in AdventureLevelTierWaveVariant.objects.filter(is_published=True):
        for command in variant.solution_commands:
            guide = resolve_form(command)
            assert guide is not None, command
            if not guide.summary:
                unregistered.add(guide.usage_form)
    assert unregistered <= UNREGISTERED_DIAGNOSTICS


def test_levels_attach_the_forms_their_solutions_teach(db):
    call_command("seed_curriculum", verbosity=0)

    def usages(slug: str) -> set[str]:
        return set(_level(slug).command_forms.values_list("usage_form", flat=True))

    assert "git mergetool" in usages("using-a-merge-tool")
    branching = usages("creating-and-switching-branches")
    assert {"git branch -d <branch>", "git branch -D <branch>"}.isdisjoint(branching)
    assert "git rebase --abort" in usages("completing-rebase-recovery-sequences")
    assert "git restore <path>..." in usages("unstaging-and-discarding-changes")


def test_a_veteran_still_gets_the_add_patch_guide_after_clearing_basic_commits(
    db, django_user_model
):
    call_command("seed_curriculum", verbosity=0)
    player = get_or_create_player(
        django_user_model.objects.create_user(username="veteran", password="pass12345")
    )
    runs = AdventureLevelTierRunService()

    # Clear Staging and Committing - Easy with its authored solution.
    basics = _level("staging-and-committing-basic-workflow").tiers.get(difficulty="easy")
    cleared = runs.start_run(player=player, tier=basics, source_entry_point="level_page")
    for command in cleared.selected_variant.solution_commands:
        CommandStep.objects.create(
            adventure_tier_run=cleared,
            player=player,
            command_text=command,
            normalized_command=command,
            result_category="target_not_yet_matched",
            command_classification="counted",
            attempt_number=1,
            was_processable=True,
        )
    credited = AdventureLevelTierCommandProcessingService()._credit_mastery(
        cleared, list(cleared.current_wave.command_forms.all())
    )
    assert "git add -p <path>" not in {
        CommandForm.objects.get(
            slug=item["form_slug"], command_skill__slug=item["skill_slug"]
        ).usage_form
        for item in credited
    }

    partial = _level("partial-staging-and-git-add-p").tiers.get(difficulty="easy")
    run = runs.start_run(player=player, tier=partial, source_entry_point="level_page")
    candidate = plan_introduction(run)

    assert candidate is not None
    assert candidate.form.usage_form == "git add -p <path>"
