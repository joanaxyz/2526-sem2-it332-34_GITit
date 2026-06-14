"""Shared asset tag vocabulary.

Tags are free-form on the model, but a curated vocabulary keeps the editor /
shop filters tidy and the frontend in sync. New tags can be added here without a
migration; unknown tags on an asset are tolerated (filtering just won't surface
them as a preset chip).
"""

from __future__ import annotations

# Curated, presentable tags grouped only for documentation. The frontend mirrors
# this flat list in `frontend/src/shared/assets/tags.ts`.
ASSET_TAGS: list[str] = [
    # Era / theme
    "medieval",
    "arcane",
    "neon",
    "celestial",
    "infernal",
    "ancient",
    # The default set granted to every player's registry (Blue + the starter
    # tower pieces). Lets the editor/shop surface "your starter kit" as a group.
    "arcane-spire",
    # Material / palette
    "stone",
    "metal",
    "bone",
    "crystal",
    "verdant",
    "shadow",
    # Mood
    "ominous",
    "regal",
    "whimsical",
]

ASSET_TAG_SET = frozenset(ASSET_TAGS)


def normalize_tags(raw) -> list[str]:
    """Coerce arbitrary input into a clean, de-duplicated list of string tags."""
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [part.strip() for part in raw.split(",")]
    seen: list[str] = []
    for tag in raw:
        value = str(tag).strip().lower()
        if value and value not in seen:
            seen.append(value)
    return seen
