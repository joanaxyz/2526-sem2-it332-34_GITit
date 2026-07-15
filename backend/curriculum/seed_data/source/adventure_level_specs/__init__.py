"""Composed adventure level seed specs."""

from __future__ import annotations

from .blueprint_generated import LEVELS as _BLUEPRINT_GENERATED
from .catalog_completeness import LEVELS as _CATALOG_COMPLETENESS
from .chapter_1_repository_foundations import LEVELS as _CHAPTER_1_REPOSITORY_FOUNDATIONS
from .chapter_2_tracking import LEVELS as _CHAPTER_2_TRACKING
from .chapter_3_branching import LEVELS as _CHAPTER_3_BRANCHING
from .chapter_4_merging import LEVELS as _CHAPTER_4_MERGING
from .chapter_5_recovery import LEVELS as _CHAPTER_5_RECOVERY
from .chapter_6_patches import LEVELS as _CHAPTER_6_PATCHES
from .chapter_7_remotes import LEVELS as _CHAPTER_7_REMOTES
from .level_plan import ADVENTURE_LEVEL_PLAN, adventure_levels_for
from .v3_advanced_workflows import LEVELS as _ADVANCED_STORY_LEVELS
from .v3_arcane_handoff import LEVELS as _V3_ARCANE_HANDOFF
from .v3_frost_form_drills import LEVELS as _V3_FROST_FORM_DRILLS
from .v3_skyline_form_drills import LEVELS as _V3_SKYLINE_FORM_DRILLS

ADVENTURE_LEVELS = [
    *_CHAPTER_1_REPOSITORY_FOUNDATIONS,
    *_CHAPTER_2_TRACKING,
    *_CHAPTER_3_BRANCHING,
    *_CHAPTER_4_MERGING,
    *_CHAPTER_5_RECOVERY,
    *_CHAPTER_6_PATCHES,
    *_CHAPTER_7_REMOTES,
    *_CATALOG_COMPLETENESS,
    *_BLUEPRINT_GENERATED,
    *_V3_FROST_FORM_DRILLS,
    *_V3_SKYLINE_FORM_DRILLS,
    *_ADVANCED_STORY_LEVELS,
    *_V3_ARCANE_HANDOFF,
]

SPEC_BY_SLUG = {spec["slug"]: spec for spec in ADVENTURE_LEVELS}

__all__ = ["ADVENTURE_LEVELS", "ADVENTURE_LEVEL_PLAN", "SPEC_BY_SLUG", "adventure_levels_for"]
