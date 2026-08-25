"""Ordered Repository Foundations blueprint adventure levels."""

from __future__ import annotations

from .repository_foundations.fresh_starts import LEVELS as _FRESH_STARTS_LEVELS
from .repository_foundations.history_and_status import LEVELS as _HISTORY_AND_STATUS_LEVELS
from .repository_foundations.cloning import LEVELS as _CLONING_LEVELS
from .repository_foundations.configuration import LEVELS as _CONFIGURATION_LEVELS
from .repository_foundations.founding_workflows import LEVELS as _FOUNDING_WORKFLOWS_LEVELS
from .repository_foundations.fresh_start_drills import LEVELS as _FRESH_START_DRILLS_LEVELS
from .repository_foundations.inspection_drills import LEVELS as _INSPECTION_DRILLS_LEVELS

ADVENTURE_LEVELS = [
    *_FRESH_STARTS_LEVELS,
    *_HISTORY_AND_STATUS_LEVELS,
    *_CLONING_LEVELS,
    *_CONFIGURATION_LEVELS,
    *_FOUNDING_WORKFLOWS_LEVELS,
    *_FRESH_START_DRILLS_LEVELS,
    *_INSPECTION_DRILLS_LEVELS,
]
