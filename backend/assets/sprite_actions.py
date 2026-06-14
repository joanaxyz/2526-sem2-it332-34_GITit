"""Sprite action categories shared across seed data, upload, and the frontend.

The ``AssetSprite.action`` field is a free-form slug, but the game only renders a
known set. Centralising them here keeps the monster-upload form, validator, and
seed importer in agreement. The frontend mirrors this in
``frontend/src/shared/assets/spriteActions.ts``.
"""

from __future__ import annotations

# Ordered for display in the upload form. ``projectile`` only applies to ranged
# attackers (``attack.kind == "projectile"``).
MONSTER_ACTIONS: tuple[str, ...] = (
    "idle",
    "walk",
    "attack",
    "hurt",
    "death",
    "portrait",
    "projectile",
)

# The minimum a monster needs to stand in a battle and land a hit.
REQUIRED_MONSTER_ACTIONS: frozenset[str] = frozenset({"idle", "attack"})

# Actions that loop while displayed; everything else plays once.
LOOPING_ACTIONS: frozenset[str] = frozenset({"idle", "walk", "projectile"})
