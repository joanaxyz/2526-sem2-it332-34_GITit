"""Every seeded command guide has one home, and every variant there teaches it."""

from django.core.management import call_command

from tutoring.models import CommandGuideHome
from tutoring.services.forms import resolve_form
from tutoring.services.homes import taught_commands


def test_every_variant_of_a_home_teaches_its_guide(db):
    call_command("seed_curriculum", verbosity=0)

    homes = CommandGuideHome.objects.select_related("scenario").prefetch_related(
        "scenario__command_forms__command_skill", "scenario__variants"
    )
    assert homes.exists()
    problems = []
    for home in homes:
        scenario = home.scenario
        preferred = list(scenario.command_forms.filter(is_published=True))
        for variant in scenario.variants.all():
            if not variant.is_published or variant.is_transfer:
                continue
            taught = {
                getattr(resolve_form(command, preferred=preferred), "teaching_key", None)
                for command in taught_commands(variant.solution_trajectory)
            }
            if home.teaching_key not in taught:
                problems.append(f"{scenario.slug}/{variant.slug}: {home.teaching_key}")
    # A retry rotates variants; none of them may skip the scenario's guide.
    assert problems == [], "\n".join(problems)


def test_reseeding_keeps_each_guide_in_its_home(db):
    call_command("seed_curriculum", verbosity=0)
    before = dict(CommandGuideHome.objects.values_list("teaching_key", "scenario_id"))
    call_command("seed_curriculum", verbosity=0)
    assert dict(CommandGuideHome.objects.values_list("teaching_key", "scenario_id")) == before
