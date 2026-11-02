"""Compatibility re-export for authored blueprint seed data.

The implementation lives under curriculum.seed_data.source so the public
seed_data package keeps stable imports while hand-authored content is grouped
away from thin compatibility modules.
"""
from __future__ import annotations

from curriculum.seed_data.source.blueprint_overlay import (
    BLUEPRINT_ADVENTURE_LEVELS,
    BLUEPRINT_CHALLENGE_SPECS,
)

__all__ = ["BLUEPRINT_ADVENTURE_LEVELS", "BLUEPRINT_CHALLENGE_SPECS"]
