"""Wave placement: which scenario sits in which level, tier and wave, in what order.

The single owner of placement for the Module 1-4 adventure tiers. A level in
``MODULE_WAVE_PLAN`` seeds its planned waves; scenario content comes from the
banks and repositories from the fixtures, keyed by the same Variant IDs.
"""

from __future__ import annotations

from curriculum.seed_data.source.wave_plan.module_1 import WAVES as MODULE_1
from curriculum.seed_data.source.wave_plan.module_2 import WAVES as MODULE_2
from curriculum.seed_data.source.wave_plan.module_3 import WAVES as MODULE_3
from curriculum.seed_data.source.wave_plan.module_4 import WAVES as MODULE_4
from curriculum.seed_data.source.wave_plan.types import ROLES, LevelWaves, ModuleWaves, WaveSpec

MODULE_WAVE_PLAN: ModuleWaves = {}
for _module in (MODULE_1, MODULE_2, MODULE_3, MODULE_4):
    _overlap = MODULE_WAVE_PLAN.keys() & _module.keys()
    if _overlap:
        raise RuntimeError(f"Levels planned twice: {sorted(_overlap)}")
    MODULE_WAVE_PLAN.update(_module)

__all__ = ["MODULE_WAVE_PLAN", "ROLES", "LevelWaves", "ModuleWaves", "WaveSpec"]
