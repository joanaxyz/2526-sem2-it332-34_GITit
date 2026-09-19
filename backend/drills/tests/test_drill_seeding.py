"""Drill content is seed data, and these pin what that buys.

The composer's pedagogy is covered in ``test_drill_composer``; this file
is about the move from deriving content per request to seeding it: that
seeding is idempotent, that it tracks the curriculum when that changes,
and that runtime reads the rows rather than recomputing them.
"""

from django.core.management import call_command

from adventures.models import AdventureLevel
from drills.models import LevelDrill, LevelDrillCard
from drills.selectors import drillable_level_ids, get_level_drill
from drills.services.seeding import seed_all_level_drills


def seeded_level() -> AdventureLevel:
    return (
        AdventureLevel.objects.filter(is_published=True, drill__cards__isnull=False)
        .order_by("chapter__sort_order", "sort_order", "id")
        .distinct()
        .first()
    )


def test_seeding_writes_a_drill_for_every_drillable_level(db):
    call_command("seed_curriculum")
    summary = seed_all_level_drills()

    assert summary.drills_written > 0
    assert summary.cards_written > summary.drills_written
    assert LevelDrill.objects.count() == summary.drills_written
    assert LevelDrillCard.objects.count() == summary.cards_written


def test_re_seeding_is_idempotent_and_keeps_card_ids(db):
    """Upsert, not truncate: a reseed must not churn primary keys.

    Keyed on (drill, form_key), which is the real uniqueness - a command
    like ``git add <file>`` is taught by many levels, so form_key alone
    collapses most of the catalog into one entry and would assert almost
    nothing.
    """
    call_command("seed_curriculum")
    call_command("seed_drills")
    before = {
        (drill_id, key): card_id
        for drill_id, key, card_id in LevelDrillCard.objects.values_list(
            "drill_id", "form_key", "id"
        )
    }

    call_command("seed_drills")
    after = {
        (drill_id, key): card_id
        for drill_id, key, card_id in LevelDrillCard.objects.values_list(
            "drill_id", "form_key", "id"
        )
    }

    assert before == after
    assert LevelDrillCard.objects.count() == len(before)


def test_seeding_drops_cards_the_level_no_longer_teaches(db):
    call_command("seed_curriculum")
    call_command("seed_drills")
    level = seeded_level()
    stray = LevelDrillCard.objects.create(
        drill=level.drill,
        form_key="git-not-taught-here/made-up",
        sort_order=99,
        command="git made-up",
        intent="Nothing",
        base_command="git",
        tokens=["git", "made-up"],
        bank=["git", "made-up"],
    )

    call_command("seed_drills")

    assert not LevelDrillCard.objects.filter(id=stray.id).exists()


def test_an_unseeded_install_reports_no_drills(db):
    """Seeding is what creates drill content, so before it runs the level
    map honestly shows no drill rather than advertising an empty one."""
    call_command("seed_curriculum")
    level_ids = list(AdventureLevel.objects.values_list("id", flat=True))

    assert drillable_level_ids(level_ids=level_ids) == set()

    call_command("seed_drills")

    assert drillable_level_ids(level_ids=level_ids)


def test_availability_matches_the_rows_the_drill_page_reads(db):
    """The map and the page read the same rows, so they cannot disagree
    about whether a level has a drill."""
    call_command("seed_curriculum")
    call_command("seed_drills")
    level_ids = list(AdventureLevel.objects.filter(is_published=True).values_list("id", flat=True))

    advertised = drillable_level_ids(level_ids=level_ids)

    for level_id in level_ids:
        drill = get_level_drill(level_id=level_id)
        has_cards = bool(drill and drill.cards.exists())
        assert has_cards is (level_id in advertised)
