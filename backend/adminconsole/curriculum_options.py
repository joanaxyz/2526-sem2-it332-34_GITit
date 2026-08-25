"""Shared curriculum options used by admin reads and writes."""

from curriculum.seed_data.stories import STORIES

SUPPORTED_STORY_WORLD_SLUGS = tuple(dict.fromkeys(row["world_slug"] for row in STORIES))

__all__ = ["SUPPORTED_STORY_WORLD_SLUGS"]
