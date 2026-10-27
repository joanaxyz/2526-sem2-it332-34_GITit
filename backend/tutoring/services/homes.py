"""Where each command form's guide opens: its home scenario.

A form's home is the first published adventure scenario, in play order, whose
solution teaches it; the scenario grammar (CONTENT_AUTHORING_GUIDE.md) makes
every variant of that scenario teach it. The guide opens only there, so playing
levels out of order never uses a guide up before the scenario written for it.
The curriculum seed derives homes once every scenario is placed.
"""

from __future__ import annotations

from collections.abc import Iterator

from django.db.models import Prefetch

from adventures.models import AdventureLevelTierScenario, AdventureLevelTierScenarioVariant
from common.constants import DIFFICULTIES
from curriculum.models import CommandForm
from simulator.trajectory import is_move
from tutoring.models import CommandGuideHome
from tutoring.services.forms import catalog_forms, resolve_form
from tutoring.services.techniques import batch_command


def taught_commands(trajectory: dict | None) -> Iterator[str]:
    """The commands a learner following the solution is guided through, in
    order: every state-changing step, merged as the planner merges them."""

    steps = (trajectory or {}).get("steps") or []
    index = 0
    while index < len(steps):
        if is_move(steps[index]):
            command, index = batch_command(steps, index)
            yield command
        index += 1


def _play_order(scenario: AdventureLevelTierScenario) -> tuple:
    tier = scenario.tier
    level = tier.adventure_level
    return (
        level.chapter.sort_order,
        level.sort_order,
        level.id,
        DIFFICULTIES.index(tier.difficulty),
        scenario.sort_order,
        scenario.id,
    )


def assign_guide_homes() -> int:
    """Rebuild every form's home from the published scenarios. Returns how many."""

    scenarios = (
        AdventureLevelTierScenario.objects.filter(
            is_published=True,
            tier__is_published=True,
            tier__adventure_level__is_published=True,
        )
        .select_related("tier__adventure_level__chapter")
        .prefetch_related(
            Prefetch(
                "command_forms",
                queryset=CommandForm.objects.filter(is_published=True).select_related(
                    "command_skill"
                ),
            ),
            Prefetch(
                "variants",
                # Transfer variants are never guided.
                queryset=AdventureLevelTierScenarioVariant.objects.filter(
                    is_published=True, is_transfer=False
                ),
            ),
        )
    )
    families: dict[str, list[CommandForm]] = {}

    def catalog(family: str) -> list[CommandForm]:
        if family not in families:
            families[family] = catalog_forms(family)
        return families[family]

    homes: dict[str, AdventureLevelTierScenario] = {}
    for scenario in sorted(scenarios, key=_play_order):
        preferred = list(scenario.command_forms.all())
        for variant in scenario.variants.all():
            for command in taught_commands(variant.solution_trajectory):
                form = resolve_form(command, preferred=preferred, catalog=catalog)
                if form is not None:
                    homes.setdefault(form.teaching_key, scenario)

    CommandGuideHome.objects.exclude(teaching_key__in=homes).delete()
    CommandGuideHome.objects.bulk_create(
        [CommandGuideHome(teaching_key=key, scenario=scenario) for key, scenario in homes.items()],
        update_conflicts=True,
        unique_fields=["teaching_key"],
        update_fields=["scenario"],
    )
    return len(homes)
