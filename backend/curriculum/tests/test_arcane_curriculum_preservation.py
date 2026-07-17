"""Regression locks for the detailed curriculum that existed before v3.

The expanded campaigns may add new fields, chapters, and scenarios, but they must
not silently shorten or replace the original seven Arcane Spire chapters.  The
projection below deliberately ignores additive metadata while locking all original
authored content, plus the small correctness fixes made to remote workflows.
"""

from __future__ import annotations

import hashlib
import json

from curriculum.seed_data.chapters import ARCANE_SPIRE_CHAPTERS
from curriculum.seed_data.command_catalog import COMMAND_CATALOG
from curriculum.seed_data.lessons import LESSONS
from curriculum.seed_data.source.adventure_level_specs import ADVENTURE_LEVELS
from curriculum.seed_data.source.challenge_specs import LEGACY_CHALLENGES
from curriculum.seed_data.source.challenge_specs.blueprint_generated import (
    CHALLENGES as BLUEPRINT_CHALLENGES,
)

EXPECTED_HASHES = {
    "chapters": "b3588181c71c0f83a053bc4c69666129d9923ca7736100c43a79156a3ca75b57",
    "commands": "5e4af04c91823d35b9d813f2715bc9fe3b83f5b36e2fa4dccd628c6beec2f0cc",
    "lessons": "f9f4b58f337841475c56bf31e12b2cd21ebb354a4f81fcd59b4e63a811b59c25",
    # 2026-07-17: repinned after restoring the authored Project Files edits that
    # make the stash and cherry-pick workflows produce real work before staging.
    "adventures": "79d581d205718afaa4360093612539083ddd211867fcb9330f29f7c1f4636e85",
    "challenges": "ce07591ddba92da84cf3de90e46c19ba5545bbdf53caf837e87e3180bab1d3d5",
}


def _canonical_hash(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


_ORIGINAL_ARCANE_CHAPTER_SLUGS = {
    chapter["slug"] for chapter in ARCANE_SPIRE_CHAPTERS if chapter["number"] <= 7
}


def _original_arcane_chapters() -> list[dict]:
    original_fields = (
        "slug",
        "story",
        "number",
        "title",
        "description",
        "battle_stage",
    )
    return [
        {key: chapter[key] for key in original_fields}
        for chapter in ARCANE_SPIRE_CHAPTERS
        if chapter["slug"] in _ORIGINAL_ARCANE_CHAPTER_SLUGS
    ]


def _arcane_command_catalog() -> list[dict]:
    catalog: list[dict] = []
    for skill in COMMAND_CATALOG:
        module = str(skill.get("module", ""))
        if module.startswith(("frost-", "skyline-")):
            continue
        row = {key: value for key, value in skill.items() if key != "usages"}
        row["usages"] = [
            form
            for form in skill.get("usages", [])
            if not str(form.get("module", module)).startswith(("frost-", "skyline-"))
        ]
        catalog.append(row)
    return catalog


def test_arcane_spire_authored_curriculum_is_not_degraded():
    actual = {
        "chapters": _canonical_hash(_original_arcane_chapters()),
        "commands": _canonical_hash(_arcane_command_catalog()),
        "lessons": _canonical_hash(
            [
                lesson
                for lesson in LESSONS
                if str(lesson.get("module", "")) in _ORIGINAL_ARCANE_CHAPTER_SLUGS
            ]
        ),
        "adventures": _canonical_hash(
            [
                level
                for level in ADVENTURE_LEVELS
                if not str(level.get("adventure", "")).startswith(
                    ("frost-", "skyline-", "guild-archive-handoff")
                )
            ]
        ),
        "challenges": _canonical_hash(
            {"challenges": BLUEPRINT_CHALLENGES, "legacy": LEGACY_CHALLENGES}
        ),
    }

    assert actual == EXPECTED_HASHES
