"""Compatibility re-export for authored challenge seed data.

The implementation lives under curriculum.seed_data.source so the public
seed_data package keeps stable imports while hand-authored content is grouped
away from thin compatibility modules.
"""
from __future__ import annotations

from curriculum.seed_data.source.challenges import CHALLENGES, LEGACY_CHALLENGES

__all__ = ["CHALLENGES", "LEGACY_CHALLENGES"]
