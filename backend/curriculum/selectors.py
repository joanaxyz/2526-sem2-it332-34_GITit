from django.db.models import Count, Q

from adventures.models import AdventureProblem, AdventureRun, CommandAdventure
from challenges.models import Challenge, ChallengeLevel, ChallengeRun
from challenges.selectors import (
    command_accuracy_rate,
    session_meets_progress_threshold,
)
from curriculum.models import CommandForm, CommandSkill, ConceptPage, Storey


def published_foundations():
    return ConceptPage.objects.filter(is_published=True).order_by("sort_order", "title")


def published_storeys():
    return (
        Storey.objects.filter(is_published=True)
        .annotate(
            command_skill_count=Count(
                "command_topics",
                filter=Q(command_topics__is_published=True),
                distinct=True,
            ),
            challenge_count=Count(
                "workflow_scenarios",
                filter=Q(workflow_scenarios__is_published=True),
                distinct=True,
            ),
        )
        .order_by("sort_order", "number")
    )


def storey_completion_count_map(*, user, storey_ids: list[int]) -> dict[int, int]:
    if not getattr(user, "is_authenticated", False) or not storey_ids:
        return {}

    completion_by_storey = {storey_id: 0 for storey_id in storey_ids}
    for run in AdventureRun.objects.filter(
        user=user,
        status="completed",
        command_adventure__module_id__in=storey_ids,
    ).select_related("command_adventure"):
        completion_by_storey[run.command_adventure.module_id] += 1

    challenge_counts: dict[tuple[int, int], int] = {}
    required_by_level: dict[int, int] = {}
    storey_by_level: dict[int, int] = {}
    for run in (
        ChallengeRun.objects.filter(
            user=user,
            mode="primary",
            status="completed",
            module_id__in=storey_ids,
        )
        .select_related("challenge_level")
        .only(
            "id",
            "module_id",
            "challenge_level_id",
            "counted_action_total",
            "command_budget_snapshot",
            "challenge_level__required_successful_attempts",
        )
    ):
        if not session_meets_progress_threshold(session=run):
            continue
        level_id = run.challenge_level_id
        challenge_counts[(run.module_id, level_id)] = challenge_counts.get((run.module_id, level_id), 0) + 1
        required_by_level[level_id] = run.challenge_level.required_successful_attempts
        storey_by_level[level_id] = run.module_id

    for (_, level_id), count in challenge_counts.items():
        storey_id = storey_by_level[level_id]
        completion_by_storey[storey_id] += min(count, required_by_level.get(level_id, 1))
    return completion_by_storey


def storey_completion_denominator_map(*, storey_ids: list[int]) -> dict[int, int]:
    if not storey_ids:
        return {}

    denominator_by_storey = {storey_id: 0 for storey_id in storey_ids}
    for adventure in CommandAdventure.objects.filter(module_id__in=storey_ids, is_published=True):
        denominator_by_storey[adventure.module_id] += 1

    for row in (
        ChallengeLevel.objects.filter(
            is_published=True,
            scenario__is_published=True,
            scenario__module_id__in=storey_ids,
        )
        .values("scenario__module_id", "required_successful_attempts")
    ):
        storey_id = row["scenario__module_id"]
        denominator_by_storey[storey_id] += int(row["required_successful_attempts"] or 0)
    return denominator_by_storey


def storey_content_page(
    *,
    user,
    storey_id: int,
    section: str,
    cursor: int | None = None,
    limit: int = 8,
) -> dict:
    limit = max(1, min(limit, 24))
    if section == "command_adventures":
        adventure = (
            CommandAdventure.objects.filter(module_id=storey_id, is_published=True)
            .select_related("module")
            .first()
        )
        return {
            "section": section,
            "results": [command_adventure_summary_payload(user=user, adventure=adventure)] if adventure else [],
            "next_cursor": None,
        }

    if section == "challenges":
        queryset = challenge_queryset(storey_id=storey_id)
        if cursor:
            queryset = queryset.filter(id__gt=cursor)
        items = list(queryset[: limit + 1])
        visible = items[:limit]
        return {
            "section": section,
            "results": [challenge_summary_payload(user=user, challenge=challenge) for challenge in visible],
            "next_cursor": visible[-1].id if len(items) > limit and visible else None,
        }

    queryset = command_skill_queryset(storey_id=storey_id)
    if cursor:
        queryset = queryset.filter(id__gt=cursor)
    items = list(queryset[: limit + 1])
    visible = items[:limit]
    return {
        "section": "command_skills",
        "results": [command_skill_summary_payload(user=user, skill=skill) for skill in visible],
        "next_cursor": visible[-1].id if len(items) > limit and visible else None,
    }


def command_skill_queryset(*, storey_id: int):
    return (
        CommandSkill.objects.filter(module_id=storey_id, is_published=True)
        .prefetch_related(
            "usages",
            "usages__drills",
            "usages__drills__variants",
        )
        .order_by("sort_order", "id")
    )


def challenge_queryset(*, storey_id: int):
    return (
        Challenge.objects.filter(module_id=storey_id, is_published=True)
        .prefetch_related("levels", "levels__variants")
        .order_by("sort_order", "id")
    )


def command_adventure_summary_payload(*, user, adventure: CommandAdventure) -> dict:
    latest = (
        AdventureRun.objects.filter(user=user, command_adventure=adventure)
        .order_by("-id")
        .first()
        if getattr(user, "is_authenticated", False)
        else None
    )
    problem_count = AdventureProblem.objects.filter(
        usage__topic__module=adventure.module,
        is_published=True,
        usage__is_published=True,
        usage__topic__is_published=True,
    ).count()
    completed = 1 if latest and latest.status == "completed" else 0
    return {
        "item_type": "command_adventure",
        "id": adventure.id,
        "slug": adventure.slug,
        "title": adventure.title,
        "description": adventure.description,
        "status": latest.status if latest else "not_started",
        "active_run_id": latest.id if latest and latest.status == "started" else None,
        "latest_run_id": latest.id if latest else None,
        "problem_count": problem_count,
        "progress": {
            "value": 100.0 if completed else 0.0,
            "numerator": completed,
            "denominator": 1 if problem_count else 0,
        },
    }


def command_skill_summary_payload(*, user, skill: CommandSkill) -> dict:
    forms = []
    for form in skill.usages.all():
        forms.append(
            {
                "id": form.id,
                "slug": form.slug,
                "usage_form": form.usage_form,
                "label": form.label,
                "summary": form.summary,
                "problem_count": len([problem for problem in form.drills.all() if problem.is_published]),
            }
        )
    return {
        "item_type": "command_skill",
        "id": skill.id,
        "slug": skill.slug,
        "base_command": skill.base_command,
        "title": skill.title,
        "summary": skill.summary,
        "mental_model": skill.mental_model,
        "forms": forms,
    }


def challenge_summary_payload(*, user, challenge: Challenge) -> dict:
    levels = [challenge_level_access_payload(user=user, level=level) for level in _ordered_levels(challenge.levels.all())]
    return {
        "item_type": "challenge",
        "id": challenge.id,
        "slug": challenge.slug,
        "title": challenge.title,
        "summary": challenge.summary,
        "narrative": challenge.narrative,
        "command_topics": challenge.command_topics,
        "levels": levels,
    }


def challenge_level_access_payload(*, user, level: ChallengeLevel) -> dict:
    from progress.models import ProblemCompletion

    completion = ProblemCompletion.objects.filter(user=user, challenge_level=level).first()
    active_run = _active_challenge_run(user=user, challenge_level=level)
    latest_run = _latest_challenge_run(user=user, challenge_level=level)
    progress = _challenge_progress_payload(user=user, level=level)
    return {
        "id": level.id,
        "difficulty": level.difficulty,
        "status": _challenge_status(user=user, level=level, completion=completion, active_run=active_run),
        "review_available": bool(completion),
        "required_successful_attempts": level.required_successful_attempts,
        "successful_attempts": progress,
        "active_run_id": active_run.id if active_run else None,
        "latest_attempt": _latest_attempt_payload(latest_run),
        "completion": _completion_payload(completion),
        "command_budget": {
            "min_counted_commands": level.min_counted_commands,
            "max_counted_commands": level.max_counted_commands,
        },
    }


def get_command_form(form_id: int) -> CommandForm:
    return CommandForm.objects.select_related("topic", "topic__module").get(
        id=form_id,
        is_published=True,
        topic__is_published=True,
        topic__module__is_published=True,
    )


def get_challenge_level(level_id: int) -> ChallengeLevel:
    return (
        ChallengeLevel.objects.select_related("scenario", "scenario__module")
        .prefetch_related("variants")
        .get(
            id=level_id,
            is_published=True,
            scenario__is_published=True,
            scenario__module__is_published=True,
        )
    )


def _challenge_progress_payload(*, user, level: ChallengeLevel) -> dict:
    required = int(level.required_successful_attempts or 1)
    count = 0
    for run in ChallengeRun.objects.filter(user=user, challenge_level=level, mode="primary", status="completed"):
        if session_meets_progress_threshold(session=run):
            count += 1
    return {"count": min(count, required), "required": required}


def _challenge_status(*, user, level: ChallengeLevel, completion, active_run) -> str:
    if completion:
        return "completed"
    if active_run:
        return "in_progress"
    if _challenge_unlocked(user=user, level=level):
        latest = _latest_challenge_run(user=user, challenge_level=level)
        return latest.status if latest and latest.status in {"failed", "abandoned"} else "not_started"
    return "locked"


def _challenge_unlocked(*, user, level: ChallengeLevel) -> bool:
    from common.constants import DIFFICULTY_EASY, DIFFICULTY_MEDIUM
    from progress.models import ProblemCompletion

    if level.difficulty == DIFFICULTY_EASY:
        return True
    previous = DIFFICULTY_EASY if level.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
    previous_level = ChallengeLevel.objects.filter(scenario=level.scenario, difficulty=previous, is_published=True).first()
    return bool(previous_level and ProblemCompletion.objects.filter(user=user, challenge_level=previous_level).exists())


def _active_challenge_run(*, user, challenge_level=None):
    return ChallengeRun.objects.filter(
        user=user,
        challenge_level=challenge_level,
        status="started",
        mode="primary",
    ).order_by("-id").first()


def _latest_challenge_run(*, user, challenge_level=None):
    return ChallengeRun.objects.filter(user=user, challenge_level=challenge_level).order_by("-id").first()


def _latest_attempt_payload(run) -> dict | None:
    if not run:
        return None
    return {
        "id": run.id,
        "status": run.status,
        "accuracy_rate": command_accuracy_rate(
            status=run.status,
            counted_action_total=run.counted_action_total,
            minimum_counted_commands=run.command_budget_snapshot.get("min_counted_commands", 0),
        ),
        "counted_action_total": run.counted_action_total,
        "total_attempts": run.total_attempts,
        "completed_at": run.completed_at,
        "ended_at": run.ended_at,
    }


def _completion_payload(completion) -> dict | None:
    if not completion:
        return None
    return {
        "first_attempt_star": completion.first_attempt_star,
        "counted_action_total": completion.counted_action_total,
        "completed_at": completion.completed_at,
    }


def _ordered_levels(levels) -> list[ChallengeLevel]:
    from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM

    order = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: 1, DIFFICULTY_HARD: 2}
    return sorted(levels, key=lambda level: order.get(level.difficulty, 99))

