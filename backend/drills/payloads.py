"""Response-payload builders for Squire's Drill.

Presenter layer: shapes are part of the frontend contract, so change them
deliberately and keep ``drills/openapi.py`` in step. Input validation lives
in ``drills/serializers.py``.
"""

from __future__ import annotations

from adventures.models import AdventureLevel
from drills.models import DrillProgress, DrillRun
from drills.selectors.content import (
    drill_card_payloads,
    drill_sequence_payload,
    get_level_drill,
)


def drill_progress_payload(progress: DrillProgress | None) -> dict:
    """Always an object, never null: the client renders the same readout for
    a first visit as for a hundredth, with zeros instead of a branch."""
    if progress is None:
        return {
            "sessions": 0,
            "clears": 0,
            "cleared": False,
            "best_accuracy": 0,
            "last_accuracy": 0,
            "shaky_form_keys": [],
            "first_cleared_at": None,
            "last_played_at": None,
        }
    return {
        "sessions": progress.sessions,
        "clears": progress.clears,
        "cleared": progress.is_cleared,
        "best_accuracy": progress.best_accuracy,
        "last_accuracy": progress.last_accuracy,
        "shaky_form_keys": list(progress.shaky_form_keys or []),
        "first_cleared_at": progress.first_cleared_at,
        "last_played_at": progress.last_played_at,
    }


def drill_run_payload(run: DrillRun | None) -> dict | None:
    """The queue to resume into, or null to start fresh."""
    if run is None or not run.queue_state:
        return None
    return {
        "id": run.id,
        "queue_state": run.queue_state,
        "answered": run.answered,
        "correct": run.correct,
        "updated_at": run.updated_at,
    }


def level_drill_payload(
    *,
    level: AdventureLevel,
    progress: DrillProgress | None,
    run: DrillRun | None = None,
) -> dict:
    drill = get_level_drill(level_id=level.id)
    cards = drill_card_payloads(drill)
    chapter = level.chapter if level.chapter_id else None
    story = chapter.story if chapter is not None and chapter.story_id else None
    return {
        "level": {
            "id": level.id,
            "slug": level.slug,
            "title": level.title,
            "description": level.description,
            "chapter_id": chapter.id if chapter else None,
            "chapter_number": chapter.number if chapter else None,
            "chapter_title": chapter.title if chapter else "",
            # Carried so the end-of-drill screen can send the learner back to
            # the map they came from rather than guessing a route.
            "story_slug": story.slug if story else "",
            "story_title": story.title if story else "",
        },
        # False when the level has no seeded drill. Seeding is what creates
        # drill content, so an unseeded install honestly has none.
        "available": bool(cards),
        "progress": drill_progress_payload(progress),
        "resume": drill_run_payload(run),
        "cards": cards,
        "sequence": drill_sequence_payload(drill),
    }
