"""The composer's pedagogy, pinned.

These are not shape tests. Each one holds a property the drill depends on
to actually teach: a question must have real alternatives, a wrong option
must be another real command (so the miss can be explained with authored
text), and the blank must fall on a slot worth hiding.
"""

from django.core.management import call_command

from adventures.models import AdventureLevel
from drills.services.composer import (
    MAX_SEQUENCE_STEPS,
    MIN_DISTRACTORS,
    MIN_SEQUENCE_STEPS,
    compose_level_drill,
    level_command_forms,
    token_kind,
    tokenize,
)


def _levels_with_forms(limit: int = 40) -> list[AdventureLevel]:
    return list(
        AdventureLevel.objects.filter(is_published=True, command_forms__is_published=True)
        .select_related("chapter")
        .order_by("chapter__sort_order", "sort_order", "id")
        .distinct()[:limit]
    )


def test_every_seeded_level_with_command_forms_composes_a_drill(db):
    call_command("seed_curriculum")
    levels = _levels_with_forms()

    assert levels, "seeding should produce levels that teach command forms"
    for level in levels:
        plan = compose_level_drill(level)
        assert plan["cards"], f"{level.slug} teaches forms but composed no cards"
        for card in plan["cards"]:
            assert card["command"].strip()
            assert card["intent"].strip()
            assert card["tokens"] == tokenize(card["command"])


def test_choices_are_real_sibling_forms_never_the_answer(db):
    call_command("seed_curriculum")

    for level in _levels_with_forms(20):
        for card in compose_level_drill(level)["cards"]:
            commands = [choice["value"] for choice in card["command_choices"]]
            intents = [choice["value"] for choice in card["intent_choices"]]
            assert card["command"] not in commands
            assert card["intent"] not in intents
            assert len(commands) == len(set(commands))
            assert len(intents) == len(set(intents))
            # An option with no gloss cannot be explained on a miss, which is
            # the whole reason distractors are drawn from real forms.
            for choice in card["command_choices"] + card["intent_choices"]:
                assert choice["gloss"].strip()
            if commands:
                assert len(commands) >= MIN_DISTRACTORS


def test_blank_hides_one_real_token_with_same_kind_options(db):
    call_command("seed_curriculum")

    checked = 0
    for level in _levels_with_forms(20):
        for card in compose_level_drill(level)["cards"]:
            blank = card["blank"]
            if blank is None:
                continue
            checked += 1
            tokens = card["tokens"]
            assert 1 <= blank["index"] < len(tokens)
            assert blank["answer"] == tokens[blank["index"]]
            assert len(blank["options"]) >= MIN_DISTRACTORS
            values = [option["value"] for option in blank["options"]]
            assert blank["answer"] not in values
            assert len(values) == len(set(values))
            # Mixing a flag answer with placeholder options would give the
            # answer away by shape alone.
            for value in values:
                assert token_kind(value) == token_kind(blank["answer"])
    assert checked, "seeded content should produce at least one fill-in-the-blank"


def test_token_bank_can_always_build_the_answer(db):
    call_command("seed_curriculum")

    for level in _levels_with_forms(20):
        for card in compose_level_drill(level)["cards"]:
            bank = card["bank"]
            assert len(bank) == len(set(bank)), "a duplicated chip is unplaceable"
            for token in card["tokens"]:
                assert token in bank


def test_sequence_finale_uses_an_authored_solution(db):
    call_command("seed_curriculum")

    sequences = [
        compose_level_drill(level)["sequence"]
        for level in _levels_with_forms(20)
    ]
    found = [sequence for sequence in sequences if sequence]
    assert found, "seeded levels should yield at least one ordering exercise"
    for sequence in found:
        steps = sequence["steps"]
        assert MIN_SEQUENCE_STEPS <= len(steps) <= MAX_SEQUENCE_STEPS
        assert all(step.strip() for step in steps)
        # Two identical chips cannot be ordered, or marked, fairly.
        assert len(set(steps)) == len(steps)


def test_an_unwired_level_still_drills_what_its_solutions_type(db):
    """A database seeded before the command_forms wiring existed has levels
    whose solutions are full of Git and whose form list is empty. Those are
    exactly the levels a learner needs a drill for, so the authored
    solutions stand in for the missing wiring."""
    call_command("seed_curriculum")
    level = _levels_with_forms(1)[0]
    level.command_forms.clear()
    for wave in level.waves.all():
        wave.command_forms.clear()
    for tier in level.tiers.all():
        for wave in tier.waves.all():
            wave.command_forms.clear()

    recovered = level_command_forms(level)

    assert recovered, "a level whose solutions type Git should still compose a drill"
    assert compose_level_drill(level)["cards"]


def test_a_level_with_nothing_to_teach_composes_no_cards(db):
    call_command("seed_curriculum")
    level = _levels_with_forms(1)[0]
    level.command_forms.clear()
    for wave in level.waves.all():
        wave.command_forms.clear()
        wave.variants.all().delete()
    for tier in level.tiers.all():
        for wave in tier.waves.all():
            wave.command_forms.clear()
            wave.variants.all().delete()

    assert level_command_forms(level) == []
    assert compose_level_drill(level)["cards"] == []
