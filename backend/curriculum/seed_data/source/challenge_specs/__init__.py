"""Composed challenge seed specs."""

from __future__ import annotations

from .blueprint_generated import CHALLENGES as _BLUEPRINT_CHALLENGES
from .legacy_base import LEGACY_CHALLENGES as _LEGACY_BASE
from .legacy_extra_1 import LEGACY_CHALLENGES as _LEGACY_EXTRA_1
from .legacy_extra_2 import LEGACY_CHALLENGES as _LEGACY_EXTRA_2
from .v3_chapter_form_challenges import V3_FORM_CHALLENGES
from .v3_story_challenges import V3_CHALLENGES

LEGACY_CHALLENGES = [*_LEGACY_BASE, *_LEGACY_EXTRA_1, *_LEGACY_EXTRA_2]

CHALLENGES = [*_BLUEPRINT_CHALLENGES, *V3_CHALLENGES, *V3_FORM_CHALLENGES]

__all__ = ["CHALLENGES", "LEGACY_CHALLENGES"]
