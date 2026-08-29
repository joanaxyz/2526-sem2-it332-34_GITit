"""Curriculum-authored battle stage config.

The backend owns only semantic stage data: which authored parallax slug a chapter
or content definition selects, plus an optional normalized landing rectangle.
The frontend story-world registry resolves slugs to concrete asset URLs.
"""

from __future__ import annotations

import re

ASSET_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DEFAULT_CHAPTER_PARALLAX_BY_NUMBER = {
    1: "chapter-01-foundation-hall",
    2: "chapter-02-scriptorium-library",
    3: "chapter-03-branching-gallery",
    4: "chapter-04-convergence-chamber",
    5: "chapter-05-recovery-vault",
    6: "chapter-06-stash-workshop",
    7: "chapter-07-remote-relay",
}


def _landing_rect(value) -> dict | None:
    """Coerce an authored landing into a normalized 0..1 rect, or None."""
    if not isinstance(value, dict):
        return None
    rect = {}
    for key in ("x", "y", "width", "height"):
        try:
            rect[key] = min(1.0, max(0.0, float(value.get(key))))
        except (TypeError, ValueError):
            return None
    if rect["width"] <= 0 or rect["height"] <= 0:
        return None
    return rect


def _asset_slug(value) -> str | None:
    if isinstance(value, dict):
        value = value.get("slug")
    if not isinstance(value, str):
        return None
    slug = value.strip().lower()
    return slug if ASSET_SLUG_RE.fullmatch(slug) else None


def chapter_stage_config(chapter) -> dict:
    config = getattr(chapter, "battle_stage", None) or {}
    if isinstance(config, dict) and config:
        return config
    slug = DEFAULT_CHAPTER_PARALLAX_BY_NUMBER.get(getattr(chapter, "number", None))
    return {"parallax": slug} if slug else {}


def _content_battle_stage(content_owner) -> dict:
    content = getattr(content_owner, "source_content_definition", None)
    definition = getattr(content, "definition", None) or {}
    config = definition.get("battle_stage") if isinstance(definition, dict) else None
    return config if isinstance(config, dict) else {}


def merged_battle_stage(*, chapter, content_owner) -> dict:
    """Chapter-level stage config overridden by the content's authored config."""
    config = chapter_stage_config(chapter)
    config.update(_content_battle_stage(content_owner))
    return config


def stage_payload(config: dict | None) -> dict | None:
    """Normalize authored battle-stage config for API responses.

    Returns only semantic data. No frontend asset paths are generated here.
    """
    config = config or {}
    if not isinstance(config, dict):
        config = {}
    parallax_slug = _asset_slug(config.get("parallax") or config.get("background"))
    landing = _landing_rect(config.get("landing"))
    if not landing and not parallax_slug:
        return None
    return {"parallax": {"slug": parallax_slug} if parallax_slug else None, "landing": landing}
