"""Analytics read model for the admin console."""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from adventures.models import AdventureRun
from challenges.models import ChallengeRun
from curriculum.models import Story
from progress.selectors import total_adventure_level_completions, total_challenge_trial_completions


def admin_analytics_payload(*, now=None) -> dict:
    """Return run, completion, learner, and per-story analytics."""

    now = now or timezone.now()
    month_ago = now - timedelta(days=30)

    adventure_by_status = {
        row["status"]: row["n"]
        for row in AdventureRun.objects.values("status").annotate(n=Count("id"))
    }
    challenge_by_status = {
        row["status"]: row["n"]
        for row in ChallengeRun.objects.values("status").annotate(n=Count("id"))
    }
    runs_by_status = dict(adventure_by_status)
    for status, count in challenge_by_status.items():
        runs_by_status[status] = runs_by_status.get(status, 0) + count

    adventure_total = sum(adventure_by_status.values())
    challenge_total = sum(challenge_by_status.values())
    adventure_passed = AdventureRun.objects.filter(passed_at__isnull=False).count()
    challenge_passed = ChallengeRun.objects.filter(
        status=ChallengeRun.Status.COMPLETED
    ).count()
    active_learners = (
        AdventureRun.objects.filter(started_at__gte=month_ago)
        .values_list("player_id", flat=True)
        .union(
            ChallengeRun.objects.filter(started_at__gte=month_ago).values_list(
                "player_id",
                flat=True,
            )
        )
        .count()
    )

    story_runs = {
        row["level__chapter__story_id"]: row["n"]
        for row in AdventureRun.objects.values("level__chapter__story_id").annotate(
            n=Count("id")
        )
    }
    story_passed = {
        row["level__chapter__story_id"]: row["n"]
        for row in AdventureRun.objects.filter(passed_at__isnull=False)
        .values("level__chapter__story_id")
        .annotate(n=Count("id"))
    }
    challenge_story_runs = {
        row["challenge_trial__challenge_level__chapter__story_id"]: row["n"]
        for row in ChallengeRun.objects.values(
            "challenge_trial__challenge_level__chapter__story_id"
        ).annotate(n=Count("id"))
    }
    challenge_story_passed = {
        row["challenge_trial__challenge_level__chapter__story_id"]: row["n"]
        for row in ChallengeRun.objects.filter(status=ChallengeRun.Status.COMPLETED)
        .values("challenge_trial__challenge_level__chapter__story_id")
        .annotate(n=Count("id"))
    }
    per_story = []
    for story in Story.objects.all().order_by("sort_order", "id"):
        adventure_story_total = story_runs.get(story.id, 0)
        challenge_story_total = challenge_story_runs.get(story.id, 0)
        per_story.append(
            {
                "slug": story.slug,
                "title": story.title,
                "runs": adventure_story_total + challenge_story_total,
                "passed": (
                    story_passed.get(story.id, 0)
                    + challenge_story_passed.get(story.id, 0)
                ),
                "adventure_runs": adventure_story_total,
                "challenge_runs": challenge_story_total,
            }
        )

    adventure_completions = total_adventure_level_completions()
    challenge_completions = total_challenge_trial_completions()
    return {
        "runs": {
            "by_status": runs_by_status,
            "total": adventure_total + challenge_total,
            "passed": adventure_passed + challenge_passed,
            "adventure": {
                "by_status": adventure_by_status,
                "total": adventure_total,
                "passed": adventure_passed,
            },
            "challenge": {
                "by_status": challenge_by_status,
                "total": challenge_total,
                "passed": challenge_passed,
            },
        },
        "completions": {
            "adventure": adventure_completions,
            "challenge": challenge_completions,
            "total": adventure_completions + challenge_completions,
        },
        "active_learners_30d": active_learners,
        "per_story": per_story,
    }
