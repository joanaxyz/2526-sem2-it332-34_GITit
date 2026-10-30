"""Scenario placement: which scenario sits in which level, tier and scenario, in what order.

The single owner of placement for the Module 1-4 adventure tiers. A level in
``MODULE_SCENARIO_PLAN`` seeds its planned scenarios; scenario content comes from the
banks and repositories from the fixtures, keyed by the same Variant IDs.
"""

from __future__ import annotations

from curriculum.seed_data.source.scenario_plan.module_1 import SCENARIOS as MODULE_1
from curriculum.seed_data.source.scenario_plan.module_2 import SCENARIOS as MODULE_2
from curriculum.seed_data.source.scenario_plan.module_3 import SCENARIOS as MODULE_3
from curriculum.seed_data.source.scenario_plan.module_4 import SCENARIOS as MODULE_4
from curriculum.seed_data.source.scenario_plan.types import ROLES, LevelScenarios, ModuleScenarios, ScenarioSpec

MODULE_SCENARIO_PLAN: ModuleScenarios = {}
for _module in (MODULE_1, MODULE_2, MODULE_3, MODULE_4):
    _overlap = MODULE_SCENARIO_PLAN.keys() & _module.keys()
    if _overlap:
        raise RuntimeError(f"Levels planned twice: {sorted(_overlap)}")
    MODULE_SCENARIO_PLAN.update(_module)

__all__ = ["MODULE_SCENARIO_PLAN", "ROLES", "LevelScenarios", "ModuleScenarios", "ScenarioSpec"]
