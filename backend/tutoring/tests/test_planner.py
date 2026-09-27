from copy import deepcopy

from adventures.models import AdventureLevelTierRun, SkillMastery
from curriculum.models import CommandForm, CommandSkill
from practice.models import CommandStep
from tutoring.models import PlayerCommandIntroduction
from tutoring.payloads import tutor_payload
from tutoring.tests.conftest import initialized_state, solution_states, staged, trajectory_for

INIT, ADD, COMMIT = "git-init/current-directory", "git-add/file", "git-commit/message"


def move_to(run, state):
    run.repository_state = deepcopy(state)


def learn(run, *keys):
    for key in keys:
        PlayerCommandIntroduction.objects.create(player=run.player, teaching_key=key)


def test_introduces_exactly_the_one_form_the_next_step_needs(teaching_run):
    payload = tutor_payload(teaching_run)

    assert payload["phase"] == "introduction"
    assert payload["teaching_key"] == INIT
    assert payload["title"] == "Start a repository here"
    assert payload["command_form"]["usage_form"] == "git init"
    assert payload["needs"][0]["kind"] == "repository"
    assert payload["changes"] == []
    # The concrete solution command is withheld until a missed attempt.
    assert payload["example_command"] is None


def test_follows_the_repository_through_the_solution(teaching_run):
    states, final = solution_states(teaching_run.selected_variant.initial_state)
    move_to(teaching_run, states[1])
    assert tutor_payload(teaching_run)["teaching_key"] == ADD
    move_to(teaching_run, states[3])
    assert tutor_payload(teaching_run)["teaching_key"] == COMMIT
    move_to(teaching_run, final)
    assert tutor_payload(teaching_run) is None


def test_known_forms_stay_quiet_and_never_skip_ahead(teaching_run):
    learn(teaching_run, INIT)
    # `git add` is still unseen, but it is not what this repository needs yet.
    assert tutor_payload(teaching_run) is None
    states, _ = solution_states(teaching_run.selected_variant.initial_state)
    move_to(teaching_run, states[1])
    assert tutor_payload(teaching_run)["teaching_key"] == ADD
    learn(teaching_run, ADD)
    move_to(teaching_run, states[2])
    assert tutor_payload(teaching_run) is None  # second file: same form, no repeat


def test_a_form_used_successfully_before_counts_as_known(teaching_run):
    other = AdventureLevelTierRun.objects.create(
        player=teaching_run.player, tier=teaching_run.tier, current_wave=teaching_run.current_wave,
        selected_variant=teaching_run.selected_variant, repository_state={}, max_counted_commands=12,
        status="completed",
    )
    CommandStep.objects.create(
        adventure_tier_run=other, command_text="git init", normalized_command="git init",
        was_processable=True, result_category="target_not_yet_matched",
        command_classification="counted", attempt_number=1,
    )
    assert tutor_payload(teaching_run) is None


def test_a_failed_earlier_attempt_does_not_count_as_known(teaching_run):
    other = AdventureLevelTierRun.objects.create(
        player=teaching_run.player, tier=teaching_run.tier, current_wave=teaching_run.current_wave,
        selected_variant=teaching_run.selected_variant, repository_state={}, max_counted_commands=12,
        status="failed",
    )
    CommandStep.objects.create(
        adventure_tier_run=other, command_text="git init", normalized_command="git init",
        was_processable=False, result_category="unprocessable",
        command_classification="unprocessable", attempt_number=1,
    )
    assert tutor_payload(teaching_run)["teaching_key"] == INIT


def test_practised_mastery_counts_as_known(teaching_run):
    form = teaching_run.current_wave.command_forms.get(usage_form="git init")
    SkillMastery.objects.create(player=teaching_run.player, command_form=form, solves=1)
    assert tutor_payload(teaching_run) is None


def test_off_route_repository_is_silent(teaching_run):
    move_to(teaching_run, initialized_state(teaching_run.selected_variant.initial_state, branch="trunk"))
    assert tutor_payload(teaching_run) is None


def test_diagnostic_solution_steps_are_skipped(teaching_run):
    variant = teaching_run.selected_variant
    states, final = solution_states(variant.initial_state)
    commands = ["git status", "git init", "git add README.md", "git add app.py", "git commit -m 'Save work'"]
    variant.solution_trajectory = trajectory_for(commands, [states[0], *states], final)
    assert tutor_payload(teaching_run)["teaching_key"] == INIT


def test_missing_or_stale_trajectory_is_silent(teaching_run):
    variant = teaching_run.selected_variant
    variant.solution_trajectory = {}
    assert tutor_payload(teaching_run) is None
    variant.solution_trajectory = {"version": 0, "steps": [{"command": "git init"}]}
    assert tutor_payload(teaching_run) is None


def test_any_seeded_command_is_taught_even_without_a_wave_form(teaching_run):
    variant = teaching_run.selected_variant
    initial = initialized_state(variant.initial_state)
    move_to(teaching_run, initial)
    branched = deepcopy(initial)
    branched["branches"]["feature"] = None
    branched["head"] = {"type": "branch", "name": "feature", "target": None}
    variant.solution_trajectory = trajectory_for(["git switch -c feature"], [initial], branched)

    payload = tutor_payload(teaching_run)
    assert payload["command_form"]["usage_form"] == "git switch -c <value>"
    assert {"kind": "branch", "text": "Branch feature is created."} in payload["needs"]

    # Once the catalog has the form, its authored syntax and label are used.
    skill = CommandSkill.objects.create(slug="git-switch", title="git switch", base_command="git switch",
                                        summary="Move HEAD to another branch.")
    CommandForm.objects.create(command_skill=skill, slug="create", usage_form="git switch -c <branch>",
                               label="Create and switch")
    payload = tutor_payload(teaching_run)
    assert payload["teaching_key"] == "form:git switch -c <branch>"
    assert payload["title"] == "Create and switch"
    assert payload["command_form"]["summary"] == "Move HEAD to another branch."


def test_same_syntax_is_the_same_lesson_whatever_the_seed_slug(teaching_run):
    teaching_run.current_wave.command_forms.update(slug="renamed-by-another-seed")
    assert tutor_payload(teaching_run)["teaching_key"] == INIT


def test_selection_is_read_only(teaching_run):
    state = deepcopy(teaching_run.repository_state)
    tutor_payload(teaching_run)
    assert teaching_run.repository_state == state
    assert not PlayerCommandIntroduction.objects.exists()


def test_staging_the_other_file_first_is_still_on_a_known_step(teaching_run):
    states, _ = solution_states(teaching_run.selected_variant.initial_state)
    learn(teaching_run, INIT)
    move_to(teaching_run, staged(states[1], "app.py"))
    # Off the authored order: the tutor stays quiet rather than guess.
    assert tutor_payload(teaching_run) is None
