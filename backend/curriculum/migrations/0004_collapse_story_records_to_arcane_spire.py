from django.db import migrations

SURVIVOR_SLUG = "git-it-legacy"
CANONICAL_SLUG = "arcane-spire"
RETIRED_SLUGS = (
    CANONICAL_SLUG,
    "frostbound-citadel",
    "neon-backstreets",
)


def collapse_to_arcane_spire(apps, schema_editor):
    Story = apps.get_model("curriculum", "Story")
    Chapter = apps.get_model("curriculum", "Chapter")

    survivor = Story.objects.filter(slug=SURVIVOR_SLUG).first()
    retired = Story.objects.filter(slug__in=RETIRED_SLUGS)

    # A freshly migrated database has no seed rows yet; seed_all creates the
    # canonical story after migrations finish.
    if survivor is None and not retired.exists():
        return
    if survivor is None:
        raise RuntimeError(
            "Cannot retire the old story records because the Runebound curriculum "
            f"({SURVIVOR_SLUG!r}) is missing. Restore it before retrying this migration."
        )

    retired_ids = list(retired.values_list("id", flat=True))
    if retired_ids:
        # The old story chain protects its prerequisite rows. Clear those links
        # before deleting the chapter trees and then the story records.
        Story.objects.filter(prerequisite_story_id__in=retired_ids).update(prerequisite_story=None)

        # These run rows protect their selected content. Remove only history
        # belonging to the retired trees; Runebound tier history is untouched.
        AdventureLevelTierRun = apps.get_model("adventures", "AdventureLevelTierRun")
        AdventureRun = apps.get_model("adventures", "AdventureRun")
        ChallengeRun = apps.get_model("challenges", "ChallengeRun")
        AdventureLevelTierRun.objects.filter(
            tier__adventure_level__chapter__story_id__in=retired_ids
        ).delete()
        AdventureRun.objects.filter(level__chapter__story_id__in=retired_ids).delete()
        ChallengeRun.objects.filter(
            challenge_trial__challenge_level__chapter__story_id__in=retired_ids
        ).delete()

        # Chapter descendants (lessons, forms, levels, waves, variants,
        # challenges, completions, and drills) are all cascade-owned.
        Chapter.objects.filter(story_id__in=retired_ids).delete()
        Story.objects.filter(id__in=retired_ids).delete()

    # Preserve the row and every child foreign key; only its public identity
    # changes. The summary and authored curriculum fields stay untouched.
    survivor.slug = CANONICAL_SLUG
    survivor.title = "The Arcane Spire"
    survivor.world_slug = "arcane-spire"
    survivor.save(update_fields=["slug", "title", "world_slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("adventures", "0010_variant_solution_trajectory"),
        ("challenges", "0004_variant_solution_trajectory"),
        ("curriculum", "0003_remove_story_price"),
        ("drills", "0002_leveldrill_drillrun_leveldrillcard"),
        ("practice", "0003_commandstep_player"),
        ("progress", "0002_adventureleveltiercompletion"),
    ]

    operations = [
        migrations.RunPython(collapse_to_arcane_spire),
    ]
