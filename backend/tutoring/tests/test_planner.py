from copy import deepcopy

from adventures.models import (
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
    SkillMastery,
)
from curriculum.models import CommandForm, CommandSkill
from practice.models import CommandStep
from tutoring.models import CommandGuideHome, PlayerCommandIntroduction
from tutoring.payloads import teaching_payload
from tutoring.services.concepts import CONCEPTS
from tutoring.tests.conftest import initialized_state, solution_states, staged, trajectory_for

INIT, ADD, COMMIT = "git-init/current-directory", "git-add/file", "git-commit/message"
ADD_SEVERAL = "form:git add <path>..."


def move_to(run, state):
    run.repository_state = deepcopy(state)


def learn(run, *keys):
    for key in keys:
        PlayerCommandIntroduction.objects.create(player=run.player, teaching_key=key)


def tutor(run):
    return teaching_payload(run)["tutor"]


def tip_keys(run):
    return [tip["key"] for tip in teaching_payload(run)["tips"]]


def home_here(run, *keys):
    for key in keys:
        CommandGuideHome.objects.update_or_create(
            teaching_key=key, defaults={"scenario": run.current_scenario}
        )


def later_run(run):
    """The same problem in a later scenario, after the home of all its forms."""

    tier = AdventureLevelTier.objects.create(
        adventure_level=run.tier.adventure_level, difficulty="medium"
    )
    scenario = AdventureLevelTierScenario.objects.create(
        tier=tier, slug="later", title="Later", max_counted_commands=12
    )
    scenario.command_forms.set(run.current_scenario.command_forms.all())
    original = run.selected_variant
    variant = AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug="later",
        label="Later",
        initial_state=original.initial_state,
        evaluation_spec=original.evaluation_spec,
        solution_trajectory=original.solution_trajectory,
    )
    return AdventureLevelTierRun.objects.create(
        player=run.player,
        tier=tier,
        current_scenario=scenario,
        selected_variant=variant,
        repository_state=deepcopy(run.repository_state),
        max_counted_commands=12,
    )


def ran_successfully(run, command):
    other = AdventureLevelTierRun.objects.create(
        player=run.player,
        tier=run.tier,
        current_scenario=run.current_scenario,
        selected_variant=run.selected_variant,
        repository_state={},
        max_counted_commands=12,
        status="completed",
    )
    CommandStep.objects.create(
        adventure_tier_run=other,
        command_text=command,
        normalized_command=command,
        was_processable=True,
        result_category="target_not_yet_matched",
        command_classification="counted",
        attempt_number=1,
    )


def test_introduces_exactly_the_one_form_the_next_step_needs(teaching_run):
    payload = tutor(teaching_run)

    assert payload["phase"] == "introduction"
    assert payload["teaching_key"] == INIT
    assert payload["title"] == "git init"
    assert payload["command_form"]["usage_form"] == "git init"
    assert payload["needs"][0]["kind"] == "repository"
    assert payload["changes"] == []
    # The concrete solution command is withheld until a missed attempt.
    assert "example_command" not in payload


def test_follows_the_repository_through_the_solution(teaching_run):
    states, final = solution_states(teaching_run.selected_variant.initial_state)
    move_to(teaching_run, states[1])
    assert tutor(teaching_run)["teaching_key"] == ADD_SEVERAL
    move_to(teaching_run, states[3])
    assert tutor(teaching_run)["teaching_key"] == COMMIT
    move_to(teaching_run, final)
    assert teaching_payload(teaching_run) == {
        "tutor": None,
        "command_guides": [],
        "guide_elsewhere": None,
        "tips": [],
    }


def test_completed_guides_stay_closed_and_never_skip_ahead(teaching_run):
    learn(teaching_run, INIT)
    # `git add` is still unseen, but it is not what this repository needs yet.
    assert tutor(teaching_run) is None
    states, _ = solution_states(teaching_run.selected_variant.initial_state)
    move_to(teaching_run, states[1])
    assert tutor(teaching_run)["teaching_key"] == ADD_SEVERAL
    learn(teaching_run, ADD_SEVERAL)
    move_to(teaching_run, states[2])
    # One file left: `git add <file>` is taught nowhere, so nothing opens.
    assert tutor(teaching_run) is None
    assert teaching_payload(teaching_run)["guide_elsewhere"] is None


def test_only_completing_a_guide_retires_it(teaching_run):
    # Typing the command elsewhere, or solving with it, is not the lesson.
    ran_successfully(teaching_run, "git init")
    form = teaching_run.current_scenario.command_forms.get(usage_form="git init")
    SkillMastery.objects.create(player=teaching_run.player, command_form=form, solves=1)
    assert tutor(teaching_run)["teaching_key"] == INIT
    learn(teaching_run, INIT)
    assert tutor(teaching_run) is None


def test_a_guide_opens_only_in_its_home_scenario(teaching_run):
    later = later_run(teaching_run)
    payload = teaching_payload(later)

    assert payload["tutor"] is None
    elsewhere = payload["guide_elsewhere"]
    assert elsewhere["guide"]["teaching_key"] == INIT
    assert elsewhere["guide"]["phase"] == "introduction"
    assert elsewhere["guide"]["completion_token"] is None
    assert elsewhere["home"] == {
        "chapter_number": 1,
        "level_title": "Teaching",
        "difficulty": "easy",
        "scenario_title": "",
    }
    # Playing ahead leaves the home's guide waiting.
    assert tutor(teaching_run)["teaching_key"] == INIT
    learn(teaching_run, INIT)
    assert teaching_payload(later)["guide_elsewhere"] is None


def test_a_scenarios_finished_guides_stay_readable(teaching_run):
    assert teaching_payload(teaching_run)["command_guides"] == []
    learn(teaching_run, INIT)

    guides = teaching_payload(teaching_run)["command_guides"]
    assert [guide["teaching_key"] for guide in guides] == [INIT]
    assert guides[0]["phase"] == "introduction"
    assert guides[0]["needs"] == []
    assert guides[0]["completion_token"] is None
    assert guides[0]["help_token"]


def test_off_route_repository_is_silent(teaching_run):
    move_to(
        teaching_run, initialized_state(teaching_run.selected_variant.initial_state, branch="trunk")
    )
    assert tutor(teaching_run) is None
    assert tip_keys(teaching_run) == []


def test_diagnostic_solution_steps_are_skipped(teaching_run):
    variant = teaching_run.selected_variant
    states, final = solution_states(variant.initial_state)
    commands = [
        "git status",
        "git init",
        "git add README.md",
        "git add app.py",
        "git commit -m 'Save work'",
    ]
    variant.solution_trajectory = trajectory_for(commands, [states[0], *states], final)
    assert tutor(teaching_run)["teaching_key"] == INIT


def test_missing_or_stale_trajectory_is_silent(teaching_run):
    variant = teaching_run.selected_variant
    variant.solution_trajectory = {}
    assert tutor(teaching_run) is None
    variant.solution_trajectory = {"version": 0, "steps": [{"command": "git init"}]}
    assert tutor(teaching_run) is None


def test_any_seeded_command_is_taught_even_without_a_scenario_form(teaching_run):
    variant = teaching_run.selected_variant
    initial = initialized_state(variant.initial_state)
    move_to(teaching_run, initial)
    branched = deepcopy(initial)
    branched["branches"]["feature"] = None
    branched["head"] = {"type": "branch", "name": "feature", "target": None}
    variant.solution_trajectory = trajectory_for(["git switch -c feature"], [initial], branched)
    home_here(teaching_run, "form:git switch -c <value>", "form:git switch -c <branch>")

    payload = tutor(teaching_run)
    assert payload["command_form"]["usage_form"] == "git switch -c <value>"
    assert {
        "kind": "branch",
        "text": "A branch pointer changes.",
        "action": "create",
        "subjects": ["<branch>"],
    } in payload["needs"]

    # Once the catalog has the form, its authored syntax and label are used.
    skill = CommandSkill.objects.create(
        slug="git-switch",
        title="git switch",
        base_command="git switch",
        summary="Move HEAD to another branch.",
    )
    CommandForm.objects.create(
        command_skill=skill,
        slug="create",
        usage_form="git switch -c <branch>",
        label="Create and switch",
    )
    payload = tutor(teaching_run)
    assert payload["teaching_key"] == "form:git switch -c <branch>"
    assert payload["title"] == "git switch -c <branch>"
    assert payload["command_form"]["summary"]
    assert "feature" not in str(payload["needs"])


def test_same_syntax_is_the_same_lesson_whatever_the_seed_slug(teaching_run):
    for form in teaching_run.current_scenario.command_forms.all():
        form.slug = f"renamed-by-another-seed-{form.pk}"
        form.save(update_fields=["slug"])
    assert tutor(teaching_run)["teaching_key"] == INIT


def test_selection_is_read_only(teaching_run):
    state = deepcopy(teaching_run.repository_state)
    teaching_payload(teaching_run)
    assert teaching_run.repository_state == state
    assert not PlayerCommandIntroduction.objects.exists()


def test_staging_the_other_file_first_is_still_on_a_known_step(teaching_run):
    states, _ = solution_states(teaching_run.selected_variant.initial_state)
    learn(teaching_run, INIT)
    move_to(teaching_run, staged(states[1], "app.py"))
    # Off the authored order: the tutor stays quiet rather than guess.
    assert tutor(teaching_run) is None


def test_back_to_back_steps_are_offered_as_one_command(teaching_run):
    states, _ = solution_states(teaching_run.selected_variant.initial_state)
    move_to(teaching_run, states[1])
    payload = tutor(teaching_run)
    assert payload["title"] == "git add <path>..."
    assert payload["command_form"]["usage_form"] == "git add <path>..."
    assert [change["text"] for change in payload["needs"]] == [
        "The staging area changes for the paths you choose.",
    ]


def test_a_guide_reads_its_syntax_part_by_part(teaching_run):
    assert tutor(teaching_run)["anatomy"] == [
        {"token": "git", "text": "runs Git"},
        {"token": "init", "text": "the Git command to run"},
    ]
    states, _ = solution_states(teaching_run.selected_variant.initial_state)
    move_to(teaching_run, states[1])
    assert tutor(teaching_run)["anatomy"][2] == {
        "token": "<path>...",
        "text": "you fill this in: a file or folder path, one or more",
    }


def test_ideas_a_move_touches_are_tips_until_dismissed(teaching_run):
    tips = teaching_payload(teaching_run)["tips"]
    # What a command is comes first of all.
    assert [tip["key"] for tip in tips] == ["concept:commands", "concept:repository"]
    assert tips[0] == {
        "key": "concept:commands",
        "kind": "concept",
        "title": "Commands",
        "text": CONCEPTS["commands"][1],
        "syntax": None,
    }
    assert "concepts" not in tutor(teaching_run)

    learn(teaching_run, "concept:commands", "concept:repository")
    assert tip_keys(teaching_run) == []
    states, _ = solution_states(teaching_run.selected_variant.initial_state)
    move_to(teaching_run, states[1])
    assert tip_keys(teaching_run) == [
        "concept:working-tree",
        "concept:staging-area",
        "technique:several-paths",
    ]


def at_reset_step(run):
    variant = run.selected_variant
    base = initialized_state(variant.initial_state)
    base["commits"] = [
        {"id": "c0", "parents": [], "tree": {"README.md": "v1"}, "message": "One"},
        {"id": "c1", "parents": ["c0"], "tree": {"README.md": "v2"}, "message": "Two"},
    ]
    base["branches"]["main"] = "c1"
    base["working_tree"] = {}
    rewound = deepcopy(base)
    rewound["branches"]["main"] = "c0"
    variant.solution_trajectory = trajectory_for(["git reset --hard HEAD~1"], [base], rewound)
    move_to(run, base)


def test_a_technique_is_a_tip_wherever_it_first_comes_up(teaching_run):
    at_reset_step(teaching_run)
    payload = teaching_payload(teaching_run)

    # `git reset --hard` has no home here; its technique is tipped anyway.
    assert payload["tutor"] is None
    assert payload["tips"][-1] == {
        "key": "technique:relative-commit",
        "kind": "technique",
        "title": "Count back from a commit",
        "text": "HEAD~2 is two commits before HEAD, and HEAD^ is the one right before it.",
        "syntax": "git reset HEAD~<n>",
    }
    learn(teaching_run, "technique:relative-commit")
    assert "technique:relative-commit" not in tip_keys(teaching_run)


def test_a_technique_already_run_needs_no_tip(teaching_run):
    ran_successfully(teaching_run, "git log HEAD~2")
    at_reset_step(teaching_run)
    assert "technique:relative-commit" not in tip_keys(teaching_run)
