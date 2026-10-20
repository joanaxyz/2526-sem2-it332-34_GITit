"""The wave grammar (docs/goals/curriculum-waves-and-repetition/PLAN.md §3).

The wave plan owns placement, so these rules are checked on the plan itself,
with the guides' real resolver and technique detectors, walking every
level's designed waves in play order.
"""

from __future__ import annotations

import json
import shlex
from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from types import SimpleNamespace

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTier
from curriculum.management.commands.seed_curriculum import (
    MODULE_1_LEVELS,
    MODULE_2_LEVELS,
    MODULE_3_LEVELS,
    MODULE_4_LEVELS,
    MODULE_COMMAND_FORMS,
    MODULE_LEVELS,
)
from curriculum.seed_data.generated.generated_targets import TARGET_STATES
from curriculum.seed_data.scenario_bank import scenario_bank, wave_scenario_bank
from curriculum.seed_data.scenario_runtime import UNPLACED_CASE_IDS
from curriculum.seed_data.source.challenge_gates import CHALLENGE_GATES
from curriculum.seed_data.source.scenario_fixtures import WAVE_FIXTURES, extension_case
from curriculum.seed_data.source.wave_plan import MODULE_WAVE_PLAN
from curriculum.seed_data.source.wave_plan.types import DEBUT
from tutoring.services.forms import command_family, resolve_form
from tutoring.services.techniques import techniques_in

TIERS = ("easy", "medium", "hard")
DIAGNOSTIC = {"status", "log", "show", "reflog", "diff"}
SETUP = {"init", "clone"}
SUBCOMMANDS = {"stash"}
ALIASES = {"--initial-branch": "-b", "--branch": "-b", "--set-upstream": "-u", "--patch": "-p"}
# Core workflow parts must come back in two later waves, one of them in a later level.
CORE = {
    ("cmd", "add"), ("opt", "add", "-p"), ("cmd", "commit"), ("opt", "commit", "-m"),
    ("opt", "commit", "--amend"), ("cmd", "restore"), ("opt", "restore", "--staged"),
    ("cmd", "switch"), ("opt", "switch", "-c"), ("cmd", "branch"), ("cmd", "stash"),
    ("sub", "stash", "pop"), ("cmd", "push"), ("opt", "push", "-u"), ("cmd", "fetch"),
    ("cmd", "pull"), ("cmd", "merge"),
}  # fmt: skip
# Time model (minutes), PLAN.md §4: brief and outcome, typed command, file edit, first guide.
PER_RUN, PER_COMMAND, PER_EDIT, PER_GUIDE = 1.0, 0.4, 1.0, 0.5
NO_FAIL_BUDGET_MINUTES = 300  # the team accepted ~4.9 h (2026-10-20); re-measure before raising

MODULE_OF = {
    level["slug"]: module
    for module, levels in enumerate((MODULE_1_LEVELS, MODULE_2_LEVELS, MODULE_3_LEVELS, MODULE_4_LEVELS), 1)
    for level in levels
}  # fmt: skip
POOLS = {
    level["slug"]: {
        case["case_id"]: case for tier in level["tiers"].values() for case in tier["cases"]
    }
    for level in MODULE_LEVELS
}
GATE_IDS = {
    case_id
    for gate in CHALLENGE_GATES.values()
    for case_ids in gate["trials"].values()
    for case_id in case_ids
}


@dataclass(frozen=True)
class Wave:
    order: int
    level: str
    tier: str
    slug: str
    role: str
    variants: tuple[str, ...]


def _level_number(level_slug: str) -> str:
    first = next(iter(POOLS[level_slug]))
    return scenario_bank()[first]["scenario_number"].rsplit(".", 1)[0]


@cache
def _case(case_id: str) -> dict:
    for pool in POOLS.values():
        if case_id in pool:
            return pool[case_id]
    return extension_case(case_id)


def _walk() -> list[Wave]:
    waves: list[Wave] = []
    for level in MODULE_LEVELS:
        slug = level["slug"]
        for tier in TIERS:
            for spec in MODULE_WAVE_PLAN.get(slug, {}).get(tier, ()):
                waves.append(Wave(len(waves), slug, tier, spec.slug, spec.role, spec.variants))
    return waves


@cache
def _module_forms() -> dict[int, list[SimpleNamespace]]:
    return {
        module: [
            SimpleNamespace(
                usage_form=usage,
                label=label,
                summary=label,
                is_playable=True,
                command_skill=SimpleNamespace(summary=""),
            )
            for specs in commands.values()
            for _, usage, label in specs
        ]
        for module, commands in MODULE_COMMAND_FORMS.items()
    }


def _catalog(family: str) -> list[SimpleNamespace]:
    return [
        form
        for forms in _module_forms().values()
        for form in forms
        if command_family(form.usage_form) == family
    ]


def _git_commands(case_id: str) -> list[str]:
    return [
        command for command in _case(case_id)["solution_commands"] if command.startswith("git ")
    ]


def _options(tokens: list[str]) -> set[str]:
    return {
        ALIASES.get(token.split("=", 1)[0], token.split("=", 1)[0])
        for token in tokens
        if token.startswith("-") and token != "--"
    }


@cache
def _parts(case_id: str) -> frozenset[tuple]:
    """Commands, subcommands, options and techniques a variant's answer uses."""
    found: set[tuple] = set()
    state = _case(case_id)["initial_state"]
    for command in _git_commands(case_id):
        tokens = shlex.split(command)
        family = tokens[1] if len(tokens) > 1 else ""
        if not family or family in DIAGNOSTIC:
            continue
        found.add(("cmd", family))
        rest = tokens[2:]
        if family in SUBCOMMANDS and rest and not rest[0].startswith("-"):
            found.add(("sub", family, rest[0]))
        found |= {("opt", family, option) for option in _options(rest)}
        found |= {("tech", technique.key) for technique in techniques_in(command, state)}
    return frozenset(found)


@cache
def _guide_forms(case_id: str, module: int) -> frozenset[str]:
    """The guide forms a variant's answer shows, as the resolver picks them."""
    found = set()
    for command in _git_commands(case_id):
        if command_family(command) in DIAGNOSTIC:
            continue
        guide = resolve_form(command, preferred=_module_forms()[module], catalog=_catalog)
        if guide is not None:
            found.add(guide.usage_form)
    return frozenset(found)


def _label(part: tuple) -> str:
    return f"technique:{part[1]}" if part[0] == "tech" else "git " + " ".join(part[1:])


def _wave_name(wave: Wave) -> str:
    return f"{wave.level}/{wave.tier}/{wave.slug}"


def _walk_knowledge(waves: list[Wave]):
    """Per wave: parts it introduces and guide forms first shown, in play order."""
    known_parts: set[tuple] = set()
    known_forms: set[str] = set()
    for wave in waves:
        module = MODULE_OF[wave.level]
        per_variant = {case_id: _parts(case_id) for case_id in wave.variants}
        forms = {case_id: _guide_forms(case_id, module) for case_id in wave.variants}
        union = frozenset().union(*per_variant.values())
        all_forms = frozenset().union(*forms.values())
        yield wave, per_variant, union - known_parts, forms, all_forms - known_forms
        known_parts |= union
        known_forms |= all_forms


def test_every_curriculum_level_has_a_wave_plan():
    assert sorted(set(POOLS) - set(MODULE_WAVE_PLAN)) == []


def test_plan_shape_is_two_or_three_waves_of_two_or_more_variants():
    problems = []
    for level, tiers in MODULE_WAVE_PLAN.items():
        if level not in POOLS:
            problems.append(f"{level}: not a curriculum level")
            continue
        if set(tiers) != set(TIERS):
            problems.append(f"{level}: plans tiers {sorted(tiers)}")
        for tier, waves in tiers.items():
            if not 2 <= len(waves) <= 3:
                problems.append(f"{level}/{tier}: {len(waves)} waves")
            slugs = [wave.slug for wave in waves]
            if len(set(slugs)) != len(slugs):
                problems.append(f"{level}/{tier}: repeated wave slugs {slugs}")
            problems += [
                f"{level}/{tier}/{wave.slug}: fewer than two variants"
                for wave in waves
                if len(wave.variants) < 2
            ]
    assert problems == [], "\n".join(problems)


def test_every_scenario_is_placed_exactly_once():
    placed: dict[str, str] = {}
    problems = []
    for wave in _walk():
        for case_id in wave.variants:
            if case_id in placed:
                problems.append(f"{case_id}: placed in {placed[case_id]} and {_wave_name(wave)}")
            placed[case_id] = _wave_name(wave)
            in_level = case_id in POOLS[wave.level]
            authored = wave_scenario_bank().get(case_id)
            if not in_level and (authored is None or case_id not in WAVE_FIXTURES):
                problems.append(f"{case_id}: neither a {wave.level} scenario nor a new one")
            elif authored and authored["scenario_number"].rsplit(".", 1)[0] != _level_number(
                wave.level
            ):
                problems.append(f"{case_id}: authored for level {authored['scenario_number']}")
            if case_id in GATE_IDS:
                problems.append(f"{case_id}: a Challenge Gate scenario")
    for level in MODULE_WAVE_PLAN:
        number = _level_number(level)
        problems += [
            f"{case_id}: {level} scenario not placed"
            for case_id in POOLS[level]
            if case_id not in placed and case_id not in UNPLACED_CASE_IDS
        ]
        problems += [
            f"{case_id}: new {number} scenario not placed"
            for case_id, authored in wave_scenario_bank().items()
            if authored["scenario_number"].rsplit(".", 1)[0] == number and case_id not in placed
        ]
    assert problems == [], "\n".join(problems)


def test_debuts_happen_before_hard_and_in_every_variant_of_the_wave():
    problems = []
    for wave, per_variant, novel, forms, new_forms in _walk_knowledge(_walk()):
        for part in sorted(novel):
            missing = [case_id for case_id, parts in per_variant.items() if part not in parts]
            if missing:
                problems.append(f"{_wave_name(wave)}: debut {_label(part)} missing in {missing}")
            if wave.tier == "hard":
                problems.append(f"{_wave_name(wave)}: {_label(part)} debuts at hard")
        for form in sorted(new_forms):
            missing = [case_id for case_id, used in forms.items() if form not in used]
            if missing:
                problems.append(f"{_wave_name(wave)}: guide {form!r} missing in {missing}")
    assert problems == [], "\n".join(problems)


def test_roles_match_what_each_wave_introduces():
    problems = []
    for wave, _, novel, _, new_forms in _walk_knowledge(_walk()):
        if wave.role == DEBUT and not (novel or new_forms):
            problems.append(f"{_wave_name(wave)}: a debut that introduces nothing")
        if wave.role != DEBUT and novel:
            problems.append(
                f"{_wave_name(wave)}: {wave.role} introduces {[_label(p) for p in sorted(novel)]}"
            )
    assert problems == [], "\n".join(problems)


def test_what_a_wave_debuts_comes_back_later():
    waves = _walk()
    level_of = {wave.order: wave.level for wave in waves}
    tier_of = {wave.order: wave.tier for wave in waves}
    # Reuse counts only where every variant of the later wave uses it.
    every = {
        wave.order: frozenset.intersection(*(_parts(case_id) for case_id in wave.variants))
        for wave in waves
    }
    every_form = {
        wave.order: frozenset.intersection(
            *(_guide_forms(case_id, MODULE_OF[wave.level]) for case_id in wave.variants)
        )
        for wave in waves
    }

    def spaced(start: int, order: int) -> bool:
        return level_of[order] != level_of[start] or TIERS.index(tier_of[order]) > TIERS.index(
            tier_of[start]
        )

    problems = []
    for wave, _, novel, _, new_forms in _walk_knowledge(waves):
        for part in sorted(novel):
            if part[0] != "tech" and part[1] in SETUP:
                continue
            later = [
                order for order, parts in every.items() if order > wave.order and part in parts
            ]
            later_levels = {level_of[order] for order in later} - {wave.level}
            if not any(spaced(wave.order, order) for order in later):
                problems.append(
                    f"{_label(part)} ({_wave_name(wave)}) is never reused at a harder tier or later level"
                )
            elif part in CORE and (len(later) < 2 or not later_levels):
                problems.append(
                    f"core {_label(part)} ({_wave_name(wave)}) needs two later waves, one in a later level"
                )
        for form in sorted(new_forms):
            if form.split()[1] in SETUP:
                continue
            if not any(
                order > wave.order and form in forms and spaced(wave.order, order)
                for order, forms in every_form.items()
            ):
                problems.append(
                    f"guide {form!r} ({_wave_name(wave)}) is never reused at a harder tier or later level"
                )
    assert problems == [], "\n".join(problems)


def test_no_two_variants_repeat_a_scenario():
    """Never repeat: no two variants share both a starting repository and a target."""
    seen: dict[str, tuple[Wave, str]] = {}
    problems = []
    for wave in _walk():
        for case_id in wave.variants:
            key = json.dumps(
                [_case(case_id)["initial_state"], TARGET_STATES.get(case_id)], sort_keys=True
            )
            earlier, first = seen.setdefault(key, (wave, case_id))
            if first != case_id:
                problems.append(
                    f"{case_id} ({_wave_name(wave)}) repeats {first} ({_wave_name(earlier)})"
                )
    assert problems == [], "\n".join(problems)


def _no_fail_minutes(waves: list[Wave]) -> float:
    """A learner who never fails plays the first variant of every wave."""
    minutes = 0.0
    known: set[str] = set()
    for wave in waves:
        case_id = wave.variants[0]
        forms = _guide_forms(case_id, MODULE_OF[wave.level])
        minutes += (
            PER_RUN
            + PER_COMMAND * len(_git_commands(case_id))
            + PER_EDIT * len(_case(case_id).get("solution_workspace_files") or [])
            + PER_GUIDE * len(forms - known)
        )
        known |= forms
    return minutes


def test_no_fail_path_stays_within_the_agreed_time():
    minutes = _no_fail_minutes(_walk())
    assert minutes <= NO_FAIL_BUDGET_MINUTES, f"no-fail path is ~{minutes / 60:.1f} h"


@pytest.mark.django_db
def test_seed_publishes_exactly_the_planned_waves_and_is_idempotent():
    call_command("seed_curriculum", verbosity=0)

    def published() -> dict[tuple[str, str], list[tuple[str, list[str]]]]:
        result = defaultdict(list)
        for tier in AdventureLevelTier.objects.filter(
            adventure_level__slug__in=list(POOLS)
        ).prefetch_related("waves__variants", "adventure_level"):
            for wave in sorted(tier.waves.all(), key=lambda row: (row.sort_order, row.id)):
                if not wave.is_published:
                    continue
                variants = sorted(
                    (variant for variant in wave.variants.all() if variant.is_published),
                    key=lambda row: (row.sort_order, row.semantic_key, row.id),
                )
                result[(tier.adventure_level.slug, tier.difficulty)].append(
                    (wave.slug, [v.slug for v in variants])
                )
        return dict(result)

    first = published()
    assert first == {
        (level, tier): [(wave.slug, list(wave.variants)) for wave in waves]
        for level, tiers in MODULE_WAVE_PLAN.items()
        for tier, waves in tiers.items()
    }

    call_command("seed_curriculum", verbosity=0)
    assert published() == first
