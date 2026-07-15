from adventures.models import AdventureWaveVariant
from authoring.compiler import ContentRuntimeCompiler
from authoring.models import ContentDefinition, ContentKind
from challenges.models import ChallengeLevel, ChallengeTrialVariant


def authored_level(slug="authored-level", difficulty="easy"):
    state = {
        "repository_initialized": True,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
    }
    return {
        "slug": slug,
        "title": "Authored Level",
        "difficulty": difficulty,
        "scenario_context": {"schema_version": 3, "story": "Story", "task": "Task"},
        "command_budget": {"min_counted_commands": 1, "max_counted_commands": 3},
        "initial_state": state,
        "target_state": state,
        "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
        "solution_commands": ["git status"],
        "variants": [
            {
                "slug": "alternate",
                "label": "Alternate",
                "initial_state": state,
                "target_state": state,
                "solution_commands": ["git status"],
            }
        ],
    }


def test_adventure_compile_writes_direct_level_variants(db, django_user_model):
    owner = django_user_model.objects.create_user(username="author")
    content = ContentDefinition.objects.create(
        owner=owner,
        kind=ContentKind.ADVENTURE,
        slug="direct-adventure",
        title="Direct Adventure",
        command_family="git status",
        definition={"levels": [authored_level()]},
    )

    runtime = ContentRuntimeCompiler().compile(content=content)
    level = runtime.adventure
    # A flat authored level compiles to one wave (the playable problem).
    wave = level.waves.get(slug="authored-level")

    assert level.command_forms.filter(usage_form="git status").exists()
    assert wave.command_forms.filter(usage_form="git status").exists()
    assert AdventureWaveVariant.objects.filter(wave=wave, is_published=True).count() == 2


def test_challenge_compile_writes_level_trials_and_direct_variants(db, django_user_model):
    owner = django_user_model.objects.create_user(username="challenge-author")
    content = ContentDefinition.objects.create(
        owner=owner,
        kind=ContentKind.CHALLENGE,
        slug="direct-challenge",
        title="Direct Challenge",
        command_family="git status",
        definition={
            "narrative": "Prove it.",
            "levels": [
                authored_level("easy-case", "easy"),
                authored_level("medium-case", "medium"),
                authored_level("hard-case", "hard"),
            ],
        },
    )

    runtime = ContentRuntimeCompiler().compile(content=content)
    level = runtime.challenge
    trials = list(level.trials.order_by("difficulty"))

    assert {trial.difficulty for trial in trials} == {"easy", "medium", "hard"}
    assert ChallengeTrialVariant.objects.filter(trial__in=trials, is_published=True).count() == 6


def _wave(slug):
    state = {
        "repository_initialized": True,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
    }
    return {
        "slug": slug,
        "title": slug,
        "scenario_context": {"schema_version": 3, "story": "Story", "task": "Task"},
        "initial_state": state,
        "target_state": state,
        "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
        "solution_commands": ["git status"],
    }


def test_adventure_level_compiles_ordered_waves(db, django_user_model):
    owner = django_user_model.objects.create_user(username="wave-author")
    content = ContentDefinition.objects.create(
        owner=owner,
        kind=ContentKind.ADVENTURE,
        slug="nested-adventure",
        title="Nested Adventure",
        command_family="git status",
        definition={
            "levels": [
                {
                    "slug": "level-1",
                    "title": "Level 1",
                    "brief": "Make a save.",
                    "waves": [_wave("wave-a"), _wave("wave-b"), _wave("wave-c")],
                }
            ]
        },
    )

    runtime = ContentRuntimeCompiler().compile(content=content)
    level = runtime.adventure
    waves = list(level.waves.order_by("sort_order"))

    assert [w.slug for w in waves] == ["wave-a", "wave-b", "wave-c"]
    assert [w.sort_order for w in waves] == [0, 1, 2]
    assert all(w.command_forms.filter(usage_form="git status").exists() for w in waves)
    assert all(w.variants.filter(is_published=True).count() == 1 for w in waves)


def test_nested_challenge_un_collapses_to_multiple_levels(db, django_user_model):
    owner = django_user_model.objects.create_user(username="nested-challenge-author")

    def trial(difficulty):
        return {**_wave(f"problem-{difficulty}"), "difficulty": difficulty}

    content = ContentDefinition.objects.create(
        owner=owner,
        kind=ContentKind.CHALLENGE,
        slug="nested-challenge",
        title="Nested Challenge",
        command_family="git status",
        definition={
            "narrative": "Two stages.",
            "levels": [
                {"slug": "stage-one", "title": "Stage one", "trials": [trial("easy"), trial("medium"), trial("hard")]},
                {"slug": "stage-two", "title": "Stage two", "trials": [trial("easy"), trial("hard")]},
            ],
        },
    )

    runtime = ContentRuntimeCompiler().compile(content=content)
    levels = list(ChallengeLevel.objects.filter(chapter=runtime.challenge.chapter).order_by("sort_order"))

    assert [level.slug for level in levels] == ["stage-one", "stage-two"]
    assert {t.difficulty for t in levels[0].trials.all()} == {"easy", "medium", "hard"}
    assert {t.difficulty for t in levels[1].trials.all()} == {"easy", "hard"}
