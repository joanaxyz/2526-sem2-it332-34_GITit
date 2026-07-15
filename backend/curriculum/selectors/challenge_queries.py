from __future__ import annotations

from challenges.models import ChallengeLevel


def challenge_queryset(*, chapter_id: int):
    return (
        ChallengeLevel.objects.filter(chapter_id=chapter_id, is_published=True)
        .prefetch_related("trials__variants", "command_forms")
        .order_by("sort_order", "id")
    )
