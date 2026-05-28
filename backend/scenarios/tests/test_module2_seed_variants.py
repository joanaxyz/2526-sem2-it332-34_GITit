import json

from django.core.management import call_command
from django.test import override_settings

from learning.models import LearningUnit
from scenarios.models import DifficultyInstance, ScenarioSkillFocus, ScenarioVariant
from simulator.git_commands import GitCommandParser, GitCommandRegistry


def _example_command(command: str) -> str:
    replacements = {
        "<branch>": "feature/auth-timeout",
        "<remote>": "origin",
        "<commit>": "c1",
        "<path>": "src/app.py",
        "<start-point>": "c1",
    }
    example = command
    for placeholder, value in replacements.items():
        example = example.replace(placeholder, value)
    return example


@override_settings(DEBUG=True)
def test_module_two_seed_creates_branching_variants(db):
    call_command("seed_module2_scenarios", "--reset", "--confirm", "--validate-build")

    unit = LearningUnit.objects.get(slug="branching-and-collaboration")
    assert unit.number == 2

    assert unit.lessons.filter(is_published=True).count() == 9

    assert (
        list(
            ScenarioSkillFocus.objects.filter(learning_unit=unit, is_published=True)
            .order_by("lesson__sort_order", "slug")
            .values_list("slug", flat=True)
        )
        == [
            "create-and-switch-branch",
            "delete-and-clean-branches",
            "stash-and-restore-work",
            "push-branch-to-remote",
            "fetch-and-pull-updates",
            "reconcile-diverged-branches",
            "fast-forward-vs-noff-merge",
            "squash-merge-feature",
            "remote-branch-lifecycle",
        ]
    )

    assert DifficultyInstance.objects.filter(scenario__learning_unit=unit, is_published=True).count() == 27
    assert ScenarioVariant.objects.filter(scenario__learning_unit=unit, is_published=True).count() == 81

    branch_create = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="create-and-switch-branch")
    assert branch_create.primary_focus_commands == ["git switch", "git checkout -b"]
    assert "git branch" in branch_create.supporting_diagnostic_commands
    assert "git switch" in json.dumps(branch_create.command_preview_config)

    lesson_21 = branch_create.lesson
    assert lesson_21.slug == "creating-and-switching-branches"
    assert lesson_21.sort_order == 1

    branch_delete = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="delete-and-clean-branches")
    assert "git branch -d" in branch_delete.primary_focus_commands
    assert "git branch -D" in branch_delete.primary_focus_commands
    assert "git switch" in branch_delete.supporting_diagnostic_commands

    lesson_22 = branch_delete.lesson
    assert lesson_22.slug == "branch-naming-and-housekeeping"
    assert lesson_22.sort_order == 2

    stash_restore = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="stash-and-restore-work")
    assert stash_restore.primary_focus_commands == ["git stash", "git stash pop"]
    assert "git stash apply" in stash_restore.supporting_diagnostic_commands
    assert "git stash drop" in stash_restore.supporting_diagnostic_commands

    lesson_23 = stash_restore.lesson
    assert lesson_23.slug == "stashing-work-in-progress"
    assert lesson_23.sort_order == 3

    push_remote = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="push-branch-to-remote")
    assert push_remote.primary_focus_commands == ["git push"]
    assert "git remote -v" in push_remote.supporting_diagnostic_commands

    lesson_24 = push_remote.lesson
    assert lesson_24.slug == "pushing-to-a-remote"
    assert lesson_24.sort_order == 4

    fetch_pull = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="fetch-and-pull-updates")
    assert "git fetch" in fetch_pull.primary_focus_commands
    assert "git pull" in fetch_pull.primary_focus_commands

    lesson_25 = fetch_pull.lesson
    assert lesson_25.slug == "fetching-and-pulling"
    assert lesson_25.sort_order == 5

    reconcile = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="reconcile-diverged-branches")
    assert "git pull" in reconcile.primary_focus_commands
    assert "git fetch" in reconcile.primary_focus_commands
    assert "git merge" in reconcile.primary_focus_commands
    assert "git push" in reconcile.primary_focus_commands
    assert "git switch" in reconcile.supporting_diagnostic_commands

    lesson_26 = reconcile.lesson
    assert lesson_26.slug == "reconciling-diverged-histories"
    assert lesson_26.sort_order == 6

    ff_merge = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="fast-forward-vs-noff-merge")
    assert "git merge" in ff_merge.primary_focus_commands
    assert "git merge --no-ff" in ff_merge.primary_focus_commands
    assert "git log --oneline --graph --all" in ff_merge.supporting_diagnostic_commands

    lesson_27 = ff_merge.lesson
    assert lesson_27.slug == "fast-forward-vs-three-way-merges"
    assert lesson_27.sort_order == 7

    squash = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="squash-merge-feature")
    assert squash.primary_focus_commands == ["git merge --squash"]
    assert "git branch -D" in squash.supporting_diagnostic_commands

    lesson_28 = squash.lesson
    assert lesson_28.slug == "squash-merging"
    assert lesson_28.sort_order == 8

    remote_lifecycle = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="remote-branch-lifecycle")
    assert "git push --delete" in remote_lifecycle.primary_focus_commands
    assert "git fetch --prune" in remote_lifecycle.primary_focus_commands
    assert "git branch -a" in remote_lifecycle.supporting_diagnostic_commands

    lesson_29 = remote_lifecycle.lesson
    assert lesson_29.slug == "deleting-and-recovering-remote-branches"
    assert lesson_29.sort_order == 9


@override_settings(DEBUG=True)
def test_module_two_seeded_solutions_are_state_based_and_command_supported(db):
    call_command("seed_module2_scenarios", "--reset", "--confirm", "--validate-build")
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    for variant in ScenarioVariant.objects.filter(
        scenario__learning_unit__slug="branching-and-collaboration",
        is_published=True,
    ):
        assert variant.target_rule
        assert variant.target_state
        assert variant.expected_state_diagram
        assert variant.student_context
        assert variant.solution_commands
        # Evaluator must be purely state-based — no command-pattern enforcement
        assert "required_commands" not in variant.target_rule, (
            f"{variant.slug} has required_commands; all M2 variants must be state-based only"
        )
        context = json.dumps(variant.student_context).lower()
        for command in variant.solution_commands:
            assert command.lower() not in context
            parsed = parser.parse(command)
            spec = registry.get(parsed.subcommand)
            assert spec is not None, command
            assert spec.validate(parsed) is None, command

    for scenario in ScenarioSkillFocus.objects.filter(
        learning_unit__slug="branching-and-collaboration",
        is_published=True,
    ):
        preview = scenario.command_preview_config
        for ref in preview.get("command_refs", []):
            command = ref.get("command")
            if not command:
                continue
            parsed = parser.parse(_example_command(command))
            spec = registry.get(parsed.subcommand)
            assert spec is not None, command
            assert spec.validate(parsed) is None, command


@override_settings(DEBUG=True)
def test_module_two_variant_slugs_match_expected_pattern(db):
    call_command("seed_module2_scenarios", "--reset", "--confirm", "--validate-build")

    slugs = set(
        ScenarioVariant.objects.filter(
            scenario__learning_unit__slug="branching-and-collaboration",
            is_published=True,
        ).values_list("slug", flat=True)
    )

    # Lesson 2.1
    assert {
        "branch-create-easy-v21e-auth",
        "branch-create-easy-v21e-login",
        "branch-create-easy-v21e-ui",
        "branch-create-medium-v21m-payments",
        "branch-create-medium-v21m-notifications",
        "branch-create-medium-v21m-export",
        "branch-create-hard-v21h-hotfix-c1",
        "branch-create-hard-v21h-detach-save",
        "branch-create-hard-v21h-from-develop",
    } <= slugs
    # Lesson 2.2
    assert {
        "branch-delete-easy-v22e-auth",
        "branch-delete-easy-v22e-fix",
        "branch-delete-easy-v22e-release",
        "branch-delete-medium-v22m-on-feature",
        "branch-delete-medium-v22m-on-hotfix",
        "branch-delete-medium-v22m-on-release",
        "branch-delete-hard-v22h-unmerged-feat",
        "branch-delete-hard-v22h-stale-wip",
        "branch-delete-hard-v22h-old-experiment",
    } <= slugs
    # Lesson 2.3
    assert {
        "stash-save-easy-v23e-auth",
        "stash-save-easy-v23e-notify",
        "stash-save-easy-v23e-cache",
        "stash-save-medium-v23m-to-main",
        "stash-save-medium-v23m-to-hotfix",
        "stash-save-medium-v23m-to-release",
        "stash-save-hard-v23h-dropped-auth",
        "stash-save-hard-v23h-dropped-api",
        "stash-save-hard-v23h-dropped-refactor",
    } <= slugs
    # Lesson 2.4
    assert {
        "push-first-easy-v24e-auth",
        "push-first-easy-v24e-orders",
        "push-first-easy-v24e-parser",
        "push-tracking-medium-v24m-auth",
        "push-tracking-medium-v24m-orders",
        "push-tracking-medium-v24m-parser",
        "push-force-hard-v24h-auth",
        "push-force-hard-v24h-orders",
        "push-force-hard-v24h-parser",
    } <= slugs
    # Lesson 2.5
    assert {
        "fetch-update-easy-v25e-main",
        "fetch-update-easy-v25e-feature",
        "fetch-update-easy-v25e-develop",
        "pull-integrate-medium-v25m-main",
        "pull-integrate-medium-v25m-feature",
        "pull-integrate-medium-v25m-develop",
        "fetch-then-pull-hard-v25h-main",
        "fetch-then-pull-hard-v25h-feature",
        "fetch-then-pull-hard-v25h-develop",
    } <= slugs
    # Lesson 2.6
    assert {
        "reconcile-merge-easy-v26e-auth",
        "reconcile-merge-easy-v26e-payments",
        "reconcile-merge-easy-v26e-hotfix",
        "reconcile-fetch-merge-medium-v26m-auth",
        "reconcile-fetch-merge-medium-v26m-payments",
        "reconcile-fetch-merge-medium-v26m-hotfix",
        "reconcile-switch-merge-hard-v26h-auth",
        "reconcile-switch-merge-hard-v26h-payments",
        "reconcile-switch-merge-hard-v26h-hotfix",
    } <= slugs
    # Lesson 2.7
    assert {
        "ff-merge-easy-v27e-auth",
        "ff-merge-easy-v27e-payments",
        "ff-merge-easy-v27e-hotfix",
        "noff-merge-medium-v27m-auth",
        "noff-merge-medium-v27m-payments",
        "noff-merge-medium-v27m-hotfix",
        "noff-merge-hard-v27h-auth",
        "noff-merge-hard-v27h-payments",
        "noff-merge-hard-v27h-hotfix",
    } <= slugs
    # Lesson 2.8
    assert {
        "squash-merge-easy-v28e-auth",
        "squash-merge-easy-v28e-orders",
        "squash-merge-easy-v28e-parser",
        "squash-merge-medium-v28m-auth",
        "squash-merge-medium-v28m-orders",
        "squash-merge-medium-v28m-parser",
        "squash-merge-hard-v28h-auth",
        "squash-merge-hard-v28h-orders",
        "squash-merge-hard-v28h-parser",
    } <= slugs
    # Lesson 2.9
    assert {
        "remote-delete-easy-v29e-auth",
        "remote-delete-easy-v29e-orders",
        "remote-delete-easy-v29e-parser",
        "remote-prune-medium-v29m-auth",
        "remote-prune-medium-v29m-orders",
        "remote-prune-medium-v29m-parser",
        "remote-cleanup-hard-v29h-auth",
        "remote-cleanup-hard-v29h-orders",
        "remote-cleanup-hard-v29h-parser",
    } <= slugs
    assert len(slugs) == 81
