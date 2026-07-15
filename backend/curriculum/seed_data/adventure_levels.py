"""Compatibility re-export for authored adventure level seed data.

The implementation lives under curriculum.seed_data.source so the public
seed_data package keeps stable imports while hand-authored content is grouped
away from thin compatibility modules.
"""
from __future__ import annotations

from curriculum.seed_data.source.adventure_levels import (
    ADVENTURE_LEVEL_PLAN,
    ADVENTURE_LEVELS,
    SPEC_BY_SLUG,
    adventure_levels_for,
)

__all__ = ["ADVENTURE_LEVELS", "ADVENTURE_LEVEL_PLAN", "SPEC_BY_SLUG", "adventure_levels_for"]
