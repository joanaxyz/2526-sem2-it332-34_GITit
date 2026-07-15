"""Domain validation for staff story edits (difficulty + prerequisite rules)."""

from __future__ import annotations

from rest_framework.exceptions import ValidationError

from curriculum.models import Story


def story_difficulty(value, *, default: str) -> str:
    difficulty = (value or default).strip().lower()
    allowed = {choice for choice, _ in Story.DIFFICULTY_CHOICES}
    if difficulty not in allowed:
        raise ValidationError({"difficulty": f"Choose one of: {', '.join(sorted(allowed))}."})
    return difficulty


def story_prerequisite(value, *, story: Story | None = None) -> Story | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        prerequisite = Story.objects.get(pk=value)
    except (Story.DoesNotExist, TypeError, ValueError) as exc:
        raise ValidationError({"prerequisite_story": "Prerequisite story not found."}) from exc
    if story is not None:
        if prerequisite.pk == story.pk:
            raise ValidationError({"prerequisite_story": "A story cannot require itself."})
        cursor = prerequisite
        visited: set[int] = set()
        while cursor is not None and cursor.pk not in visited:
            if cursor.pk == story.pk:
                raise ValidationError({"prerequisite_story": "Story prerequisites cannot form a cycle."})
            visited.add(cursor.pk)
            cursor = cursor.prerequisite_story
    return prerequisite
