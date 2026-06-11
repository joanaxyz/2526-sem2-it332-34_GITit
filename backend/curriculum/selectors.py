from dataclasses import dataclass, field

from django.db.models import Count, Q

from adventures.models import AdventureQuest, AdventureRun, CommandAdventure
from challenges.models import Challenge, ChallengeQuest, ChallengeRun
from challenges.selectors import (
    command_accuracy_rate,
    run_meets_progress_threshold,
)
from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
    SESSION_MODE_PRIMARY,
)
from curriculum.command_content import command_content_entry_for_command
from curriculum.models import CommandForm, CommandSkill, ConceptPage, Storey


def published_foundations():
    return ConceptPage.objects.filter(is_published=True).order_by("sort_order", "title")


def published_storeys():
    return (
        Storey.objects.filter(is_published=True)
        .annotate(
            command_skill_count=Count(
                "command_skills",
                filter=Q(command_skills__is_published=True),
                distinct=True,
            ),
            challenge_count=Count(
                "challenges",
                filter=Q(challenges__is_published=True),
                distinct=True,
            ),
        )
        .order_by("sort_order", "number")
    )


def storey_completion_count_map(*, user, storey_ids: list[int]) -> dict[int, int]:
    if not getattr(user, "is_authenticated", False) or not storey_ids:
        return {}

    completion_by_storey = {storey_id: 0 for storey_id in storey_ids}
    # Count each Command Adventure at most once per storey: the milestone is
    # *passing* the adventure (passed_at), not how many times it was run. Replays
    # never set passed_at, so they cannot inflate progress past the 1-per-storey
    # denominator. Distinct on the adventure id keeps this idempotent across runs.
    for storey_id in (
        AdventureRun.objects.filter(
            user=user,
            mode=SESSION_MODE_PRIMARY,
            passed_at__isnull=False,
            command_adventure__storey_id__in=storey_ids,
        )
        .values_list("command_adventure__storey_id", flat=True)
        .distinct()
    ):
        completion_by_storey[storey_id] += 1

    challenge_counts: dict[tuple[int, int], int] = {}
    required_by_quest: dict[int, int] = {}
    storey_by_quest: dict[int, int] = {}
    for run in (
        ChallengeRun.objects.filter(
            user=user,
            mode="primary",
            status="completed",
            storey_id__in=storey_ids,
        )
        .select_related("challenge_quest")
        .only(
            "id",
            "storey_id",
            "challenge_quest_id",
            "counted_action_total",
            "command_budget_snapshot",
            "challenge_quest__required_successful_attempts",
        )
    ):
        if not run_meets_progress_threshold(run=run):
            continue
        quest_id = run.challenge_quest_id
        challenge_counts[(run.storey_id, quest_id)] = challenge_counts.get((run.storey_id, quest_id), 0) + 1
        required_by_quest[quest_id] = run.challenge_quest.required_successful_attempts
        storey_by_quest[quest_id] = run.storey_id

    for (_, quest_id), count in challenge_counts.items():
        storey_id = storey_by_quest[quest_id]
        completion_by_storey[storey_id] += min(count, required_by_quest.get(quest_id, 1))
    return completion_by_storey


def storey_completion_denominator_map(*, storey_ids: list[int]) -> dict[int, int]:
    if not storey_ids:
        return {}

    denominator_by_storey = {storey_id: 0 for storey_id in storey_ids}
    for adventure in CommandAdventure.objects.filter(storey_id__in=storey_ids, is_published=True):
        denominator_by_storey[adventure.storey_id] += 1

    for row in (
        ChallengeQuest.objects.filter(
            is_published=True,
            challenge__is_published=True,
            challenge__storey_id__in=storey_ids,
        )
        .values("challenge__storey_id", "required_successful_attempts")
    ):
        storey_id = row["challenge__storey_id"]
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
            CommandAdventure.objects.filter(storey_id=storey_id, is_published=True)
            .select_related("storey")
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
        access = _build_challenge_access(user=user, storey_id=storey_id, challenges=visible)
        return {
            "section": section,
            "results": [challenge_summary_payload(challenge=challenge, access=access) for challenge in visible],
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
        CommandSkill.objects.filter(storey_id=storey_id, is_published=True)
        .prefetch_related(
            "command_forms",
            "command_forms__adventure_quests",
            "command_forms__adventure_quests__adventure_variants",
        )
        .order_by("sort_order", "id")
    )


def storey_book(*, storey_id: int) -> dict | None:
    """The Storey Book: every command registered for the storey, each resolved to
    its rich authored content from the command library.

    There is no terminal demo here — the book is reference material. Content pages
    come from the shared command-content library (`command_content.py`); a skill's
    own authored `command_preview.pages` win when present, and a minimal summary
    page is synthesized as a last resort so a registered command never renders
    empty."""
    storey = (
        Storey.objects.filter(id=storey_id, is_published=True)
        .only("id", "slug", "number", "title", "description")
        .first()
    )
    if storey is None:
        return None

    commands = [
        book_command_payload(skill=skill)
        for skill in CommandSkill.objects.filter(storey_id=storey_id, is_published=True).order_by(
            "sort_order", "id"
        )
    ]
    return {
        "storey_id": storey.id,
        "slug": storey.slug,
        "number": storey.number,
        "title": storey.title,
        "description": storey.description,
        "command_count": len(commands),
        "commands": commands,
    }


def book_command_payload(*, skill: CommandSkill) -> dict:
    entry = command_content_entry_for_command(skill.base_command)
    preview = skill.command_preview if isinstance(skill.command_preview, dict) else {}
    authored_pages = preview.get("pages") if isinstance(preview.get("pages"), list) else []
    if authored_pages:
        pages = authored_pages
    elif entry and entry.get("pages"):
        pages = entry["pages"]
    else:
        pages = [
            {
                "id": f"{skill.slug}-overview",
                "title": "Overview",
                "heading": skill.title,
                "eyebrow": skill.base_command,
                "section_type": "overview",
                "blocks": [{"type": "paragraph", "body": skill.summary}] if skill.summary else [],
            }
        ]
    return {
        "id": skill.id,
        "slug": skill.slug,
        "base_command": skill.base_command,
        "title": skill.title,
        "summary": skill.summary,
        "tags": entry.get("tags", []) if entry else [],
        "pages": pages,
    }


def challenge_queryset(*, storey_id: int):
    return (
        Challenge.objects.filter(storey_id=storey_id, is_published=True)
        .prefetch_related("challenge_quests")
        .order_by("sort_order", "id")
    )


@dataclass(frozen=True)
class ChallengeAccessContext:
    """Per-page batch of every user-specific fact the quest payloads need, so
    serializing a page of challenges costs a fixed handful of queries instead
    of several per quest."""

    completions: dict[int, object] = field(default_factory=dict)
    active_runs: dict[int, ChallengeRun] = field(default_factory=dict)
    latest_runs: dict[int, ChallengeRun] = field(default_factory=dict)
    progress_counts: dict[int, int] = field(default_factory=dict)
    adventure_passed: bool = False


def _build_challenge_access(*, user, storey_id: int, challenges: list[Challenge]) -> ChallengeAccessContext:
    from progress.models import QuestCompletion

    if not getattr(user, "is_authenticated", False):
        return ChallengeAccessContext()
    quest_ids = [quest.id for challenge in challenges for quest in challenge.challenge_quests.all()]
    if not quest_ids:
        return ChallengeAccessContext(adventure_passed=_adventure_passed(user=user, storey_id=storey_id))

    completions = {
        completion.challenge_quest_id: completion
        for completion in QuestCompletion.objects.filter(user=user, challenge_quest_id__in=quest_ids)
    }

    active_runs: dict[int, ChallengeRun] = {}
    latest_runs: dict[int, ChallengeRun] = {}
    progress_counts: dict[int, int] = {}
    runs = (
        ChallengeRun.objects.filter(user=user, challenge_quest_id__in=quest_ids)
        .order_by("id")
        .only(
            "id",
            "mode",
            "status",
            "challenge_quest_id",
            "counted_action_total",
            "command_budget_snapshot",
            "total_attempts",
            "completed_at",
            "ended_at",
        )
    )
    for run in runs:
        # Ascending id order: the last run seen per quest is the latest one.
        latest_runs[run.challenge_quest_id] = run
        if run.mode == "primary" and run.status == "started":
            active_runs[run.challenge_quest_id] = run
        if run.mode == "primary" and run.status == "completed" and run_meets_progress_threshold(run=run):
            progress_counts[run.challenge_quest_id] = progress_counts.get(run.challenge_quest_id, 0) + 1

    return ChallengeAccessContext(
        completions=completions,
        active_runs=active_runs,
        latest_runs=latest_runs,
        progress_counts=progress_counts,
        adventure_passed=_adventure_passed(user=user, storey_id=storey_id),
    )


def command_adventure_summary_payload(*, user, adventure: CommandAdventure) -> dict:
    authenticated = getattr(user, "is_authenticated", False)
    latest = (
        AdventureRun.objects.filter(user=user, command_adventure=adventure)
        .order_by("-id")
        .first()
        if authenticated
        else None
    )
    quest_count = AdventureQuest.objects.filter(
        command_form__command_skill__storey=adventure.storey,
        is_published=True,
        command_form__is_published=True,
        command_form__command_skill__is_published=True,
    ).count()
    # Progress and the challenge gate key off whether the adventure has ever been
    # passed, not the latest run's status. Otherwise a post-pass replay that is
    # abandoned/failed would visibly relock challenges and zero out progress.
    is_passed = bool(
        authenticated
        and AdventureRun.objects.filter(
            user=user, command_adventure=adventure, passed_at__isnull=False
        ).exists()
    )
    completed = 1 if is_passed else 0
    return {
        "item_type": "command_adventure",
        "id": adventure.id,
        "slug": adventure.slug,
        "title": adventure.title,
        "description": adventure.description,
        "status": latest.status if latest else "not_started",
        "is_passed": is_passed,
        "active_run_id": latest.id if latest and latest.status == "started" else None,
        "latest_run_id": latest.id if latest else None,
        "quest_count": quest_count,
        "progress": {
            "value": 100.0 if completed else 0.0,
            "numerator": completed,
            "denominator": 1 if quest_count else 0,
        },
    }


def command_skill_summary_payload(*, user, skill: CommandSkill) -> dict:
    forms = []
    for form in skill.command_forms.all():
        forms.append(
            {
                "id": form.id,
                "slug": form.slug,
                "usage_form": form.usage_form,
                "label": form.label,
                "summary": form.summary,
                "quest_count": len([quest for quest in form.adventure_quests.all() if quest.is_published]),
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


def challenge_summary_payload(*, challenge: Challenge, access: ChallengeAccessContext) -> dict:
    ordered = _ordered_quests(challenge.challenge_quests.all())
    quests = [
        challenge_quest_access_payload(quest=quest, access=access, sibling_quests=ordered)
        for quest in ordered
    ]
    return {
        "item_type": "challenge",
        "id": challenge.id,
        "slug": challenge.slug,
        "title": challenge.title,
        "summary": challenge.summary,
        "narrative": challenge.narrative,
        "quests": quests,
    }


def challenge_quests_access_payload(*, user, challenge: Challenge) -> list[dict]:
    """Per-quest access for every sibling quest of a challenge, ordered
    easy→hard. Reuses the same access context the Tower uses so statuses
    (locked / in_progress / completed) match exactly between the Tower and the
    in-run quest navigator."""
    access = _build_challenge_access(user=user, storey_id=challenge.storey_id, challenges=[challenge])
    ordered = _ordered_quests(challenge.challenge_quests.all())
    return [
        challenge_quest_access_payload(quest=quest, access=access, sibling_quests=ordered)
        for quest in ordered
    ]


def challenge_quest_access_payload(
    *,
    quest: ChallengeQuest,
    access: ChallengeAccessContext,
    sibling_quests: list[ChallengeQuest],
) -> dict:
    completion = access.completions.get(quest.id)
    active_run = access.active_runs.get(quest.id)
    required = int(quest.required_successful_attempts or 1)
    return {
        "id": quest.id,
        "difficulty": quest.difficulty,
        "status": _challenge_status(quest=quest, access=access, sibling_quests=sibling_quests),
        "review_available": bool(completion),
        "required_successful_attempts": quest.required_successful_attempts,
        "successful_attempts": {
            "count": min(access.progress_counts.get(quest.id, 0), required),
            "required": required,
        },
        "active_run_id": active_run.id if active_run else None,
        "latest_attempt": _latest_attempt_payload(access.latest_runs.get(quest.id)),
        "completion": _completion_payload(completion),
        "command_budget": {
            "min_counted_commands": quest.min_counted_commands,
            "max_counted_commands": quest.max_counted_commands,
        },
    }


def get_command_form(form_id: int) -> CommandForm:
    return CommandForm.objects.select_related("command_skill", "command_skill__storey").get(
        id=form_id,
        is_published=True,
        command_skill__is_published=True,
        command_skill__storey__is_published=True,
    )


def _challenge_status(
    *,
    quest: ChallengeQuest,
    access: ChallengeAccessContext,
    sibling_quests: list[ChallengeQuest],
) -> str:
    if quest.id in access.completions:
        return "completed"
    if quest.id in access.active_runs:
        return "in_progress"
    if _challenge_unlocked(quest=quest, access=access, sibling_quests=sibling_quests):
        latest = access.latest_runs.get(quest.id)
        return latest.status if latest and latest.status in {"failed", "abandoned"} else "not_started"
    return "locked"


def _challenge_unlocked(
    *,
    quest: ChallengeQuest,
    access: ChallengeAccessContext,
    sibling_quests: list[ChallengeQuest],
) -> bool:
    if quest.difficulty == DIFFICULTY_EASY:
        # Mirrors ChallengeRunService._ensure_adventure_passed: a storey's
        # challenges open once its Command Adventure has been passed.
        return access.adventure_passed
    previous = DIFFICULTY_EASY if quest.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
    previous_quest = next(
        (candidate for candidate in sibling_quests if candidate.difficulty == previous and candidate.is_published),
        None,
    )
    return bool(previous_quest and previous_quest.id in access.completions)


def _adventure_passed(*, user, storey_id: int) -> bool:
    adventure = CommandAdventure.objects.filter(storey_id=storey_id, is_published=True).first()
    if adventure is None:
        return True  # storey has no Command Adventure to gate on
    return AdventureRun.objects.filter(
        user=user, command_adventure=adventure, passed_at__isnull=False
    ).exists()


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


def _ordered_quests(quests) -> list[ChallengeQuest]:
    order = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: 1, DIFFICULTY_HARD: 2}
    return sorted(quests, key=lambda quest: order.get(quest.difficulty, 99))
