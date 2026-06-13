from dataclasses import dataclass, field

from django.db.models import Count, Q

from assets.models import (
    TOWER_PIECE_ADVENTURE_SECTION,
    TOWER_PIECE_CHALLENGE_SECTION,
    TOWER_PIECE_LANDING,
    TOWER_PIECE_SPIRE,
    TOWER_PIECE_TOME,
)
from adventures.models import AdventureLevel, AdventureRun, CommandAdventure
from challenges.models import Challenge, ChallengeLevel, ChallengeRun
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
from curriculum.library import library_key_for_command
from curriculum.models import CommandForm, CommandSkill, LibraryEntry, Storey, Tome


OFFICIAL_TOWER_ASSET_SLUGS = {
    TOWER_PIECE_SPIRE: "official-spire",
    TOWER_PIECE_LANDING: "official-landing",
    TOWER_PIECE_ADVENTURE_SECTION: "official-adventure-section",
    TOWER_PIECE_CHALLENGE_SECTION: "official-challenge-section",
    TOWER_PIECE_TOME: "official-tome",
}


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
    required_by_level: dict[int, int] = {}
    storey_by_level: dict[int, int] = {}
    for run in (
        ChallengeRun.objects.filter(
            user=user,
            mode="primary",
            status="completed",
            storey_id__in=storey_ids,
        )
        .select_related("challenge_level")
        .only(
            "id",
            "storey_id",
            "challenge_level_id",
            "counted_action_total",
            "command_budget_snapshot",
            "challenge_level__required_successful_attempts",
        )
    ):
        if not run_meets_progress_threshold(run=run):
            continue
        level_id = run.challenge_level_id
        challenge_counts[(run.storey_id, level_id)] = challenge_counts.get((run.storey_id, level_id), 0) + 1
        required_by_level[level_id] = run.challenge_level.required_successful_attempts
        storey_by_level[level_id] = run.storey_id

    for (_, level_id), count in challenge_counts.items():
        storey_id = storey_by_level[level_id]
        completion_by_storey[storey_id] += min(count, required_by_level.get(level_id, 1))
    return completion_by_storey


def storey_completion_denominator_map(*, storey_ids: list[int]) -> dict[int, int]:
    if not storey_ids:
        return {}

    denominator_by_storey = {storey_id: 0 for storey_id in storey_ids}
    for adventure in CommandAdventure.objects.filter(storey_id__in=storey_ids, is_published=True):
        denominator_by_storey[adventure.storey_id] += 1

    for row in (
        ChallengeLevel.objects.filter(
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

    if section == "tomes":
        tomes = Tome.objects.filter(storey_id=storey_id, is_published=True).order_by("sort_order", "id")
        return {
            "section": section,
            "results": [tome_summary_payload(tome=tome) for tome in tomes],
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


def storey_content_overview(*, user, storey_id: int) -> dict:
    """Every tower section for one storey in a single payload.

    The Tower renders three sections per storey — its Command Adventure (always
    one), its tomes, and its challenges — each of which was previously a separate
    request. Storeys hold only a handful of challenges/tomes, so this returns them
    all (no cursor): collapsing 2-3 round trips per storey into one is the win.
    """
    adventure = (
        CommandAdventure.objects.filter(storey_id=storey_id, is_published=True)
        .select_related("storey")
        .first()
    )
    tomes = Tome.objects.filter(storey_id=storey_id, is_published=True).order_by("sort_order", "id")
    challenges = list(challenge_queryset(storey_id=storey_id))
    access = _build_challenge_access(user=user, storey_id=storey_id, challenges=challenges)
    return {
        "storey_id": storey_id,
        "command_adventure": (
            command_adventure_summary_payload(user=user, adventure=adventure) if adventure else None
        ),
        "tomes": [tome_summary_payload(tome=tome) for tome in tomes],
        "challenges": [
            challenge_summary_payload(challenge=challenge, access=access) for challenge in challenges
        ],
        "tower_layout": tower_layout_payload(
            storey_id=storey_id,
            adventure=adventure,
            tomes=list(tomes),
            challenges=challenges,
        ),
    }


def tower_layout_payload(
    *,
    storey_id: int,
    adventure: CommandAdventure | None,
    tomes: list[Tome],
    challenges: list[Challenge],
) -> dict:
    pieces: list[dict] = [
        _tower_piece(
            storey_id=storey_id,
            name="spire",
            piece_type=TOWER_PIECE_SPIRE,
        )
    ]

    above_adventure_tomes = [tome for tome in tomes if tome.placement == "above_adventure"]
    for tome in above_adventure_tomes:
        pieces.append(
            _tower_piece(
                storey_id=storey_id,
                name=f"tome-{tome.id}",
                piece_type=TOWER_PIECE_TOME,
                content_binding={"kind": "tome", "id": tome.id},
            )
        )
    if above_adventure_tomes:
        pieces.append(
            _tower_piece(
                storey_id=storey_id,
                name="landing-after-tomes",
                piece_type=TOWER_PIECE_LANDING,
            )
        )

    pieces.append(
        _tower_piece(
            storey_id=storey_id,
            name="adventure",
            piece_type=TOWER_PIECE_ADVENTURE_SECTION,
            content_binding={"kind": "adventure", "id": adventure.id} if adventure else None,
        )
    )
    pieces.append(
        _tower_piece(
            storey_id=storey_id,
            name="landing-after-adventure",
            piece_type=TOWER_PIECE_LANDING,
        )
    )

    if challenges:
        for challenge in challenges:
            pieces.append(
                _tower_piece(
                    storey_id=storey_id,
                    name=f"challenge-{challenge.id}",
                    piece_type=TOWER_PIECE_CHALLENGE_SECTION,
                    content_binding={"kind": "challenge", "id": challenge.id},
                )
            )
    else:
        pieces.append(
            _tower_piece(
                storey_id=storey_id,
                name="challenges",
                piece_type=TOWER_PIECE_CHALLENGE_SECTION,
            )
        )
    pieces.append(
        _tower_piece(
            storey_id=storey_id,
            name="landing-after-challenges",
            piece_type=TOWER_PIECE_LANDING,
        )
    )
    return {"storeyId": storey_id, "pieces": pieces}


def _tower_piece(
    *,
    storey_id: int,
    name: str,
    piece_type: str,
    content_binding: dict | None = None,
) -> dict:
    payload = {
        "instanceId": f"storey-{storey_id}-{name}",
        "assetSlug": OFFICIAL_TOWER_ASSET_SLUGS[piece_type],
        "pieceType": piece_type,
    }
    if content_binding:
        payload["contentBinding"] = content_binding
    return payload


def command_skill_queryset(*, storey_id: int):
    return (
        CommandSkill.objects.filter(storey_id=storey_id, is_published=True)
        .prefetch_related(
            "command_forms",
            "command_forms__adventure_levels",
            "command_forms__adventure_levels__adventure_variants",
        )
        .order_by("sort_order", "id")
    )


def learned_command_skills(*, user) -> list[dict]:
    """The player's registry of learned commands.

    A CommandSkill is "learned" once the player has passed the Command Adventure
    that teaches it — the same pass milestone (`passed_at`) that unlocks the
    storey's challenges. Passing a storey's adventure therefore grants every
    published command-skill in that storey. Derived (not stored) so it can never
    drift from the progression that produced it.
    """
    if not getattr(user, "is_authenticated", False):
        return []
    passed_storey_ids = set(
        AdventureRun.objects.filter(user=user, passed_at__isnull=False)
        .values_list("command_adventure__storey_id", flat=True)
        .distinct()
    )
    if not passed_storey_ids:
        return []
    skills = (
        CommandSkill.objects.filter(storey_id__in=passed_storey_ids, is_published=True)
        .select_related("storey")
        .order_by("storey__sort_order", "sort_order", "id")
    )
    return [
        {
            "id": skill.id,
            "slug": skill.slug,
            "base_command": skill.base_command,
            "title": skill.title,
            "summary": skill.summary,
            "storey_id": skill.storey_id,
            "storey_number": skill.storey.number,
            "storey_title": skill.storey.title,
        }
        for skill in skills
    ]


def storey_book(*, storey_id: int) -> dict | None:
    """The Storey Book: every command registered for the storey, each resolved to
    its rich authored content from the library.

    There is no terminal demo here — the book is reference material. Pages come
    from the seeded ``LibraryEntry`` for the skill's command (authored in
    ``library.py``, persisted by ``seed_command_library``); a minimal summary
    page is synthesized as a fallback so a registered command never renders
    empty."""
    storey = (
        Storey.objects.filter(id=storey_id, is_published=True)
        .only("id", "slug", "number", "title", "description")
        .first()
    )
    if storey is None:
        return None

    skills = list(
        CommandSkill.objects.filter(storey_id=storey_id, is_published=True).order_by("sort_order", "id")
    )
    # One query for the whole book: resolve every skill's library entry in bulk
    # so a storey with N commands does not cost N round trips.
    keys = {library_key_for_command(skill.base_command) for skill in skills if skill.base_command}
    entries = {
        entry.command_key: entry
        for entry in LibraryEntry.objects.filter(command_key__in=keys, is_published=True)
    }
    commands = [
        book_command_payload(
            skill=skill,
            entry=entries.get(library_key_for_command(skill.base_command)) if skill.base_command else None,
        )
        for skill in skills
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


def book_command_payload(*, skill: CommandSkill, entry: LibraryEntry | None) -> dict:
    if entry and entry.pages:
        pages = entry.pages
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
        "tags": list(entry.tags) if entry and entry.tags else [],
        "pages": pages,
    }


def tome_summary_payload(*, tome: Tome) -> dict:
    """Tomes are always-unlocked reading: pages ship inline so opening the
    reader needs no second request."""
    return {
        "item_type": "tome",
        "id": tome.id,
        "slug": tome.slug,
        "title": tome.title,
        "summary": tome.summary,
        "placement": tome.placement,
        "pages": tome.pages,
    }


def challenge_queryset(*, storey_id: int):
    return (
        Challenge.objects.filter(storey_id=storey_id, is_published=True)
        .prefetch_related("challenge_levels")
        .order_by("sort_order", "id")
    )


@dataclass(frozen=True)
class ChallengeAccessContext:
    """Per-page batch of every user-specific fact the level payloads need, so
    serializing a page of challenges costs a fixed handful of queries instead
    of several per level."""

    completions: dict[int, object] = field(default_factory=dict)
    active_runs: dict[int, ChallengeRun] = field(default_factory=dict)
    latest_runs: dict[int, ChallengeRun] = field(default_factory=dict)
    progress_counts: dict[int, int] = field(default_factory=dict)
    adventure_passed: bool = False


def _build_challenge_access(*, user, storey_id: int, challenges: list[Challenge]) -> ChallengeAccessContext:
    from progress.models import LevelCompletion

    if not getattr(user, "is_authenticated", False):
        return ChallengeAccessContext()
    level_ids = [level.id for challenge in challenges for level in challenge.challenge_levels.all()]
    if not level_ids:
        return ChallengeAccessContext(adventure_passed=_adventure_passed(user=user, storey_id=storey_id))

    completions = {
        completion.challenge_level_id: completion
        for completion in LevelCompletion.objects.filter(user=user, challenge_level_id__in=level_ids)
    }

    active_runs: dict[int, ChallengeRun] = {}
    latest_runs: dict[int, ChallengeRun] = {}
    progress_counts: dict[int, int] = {}
    runs = (
        ChallengeRun.objects.filter(user=user, challenge_level_id__in=level_ids)
        .order_by("id")
        .only(
            "id",
            "mode",
            "status",
            "challenge_level_id",
            "counted_action_total",
            "command_budget_snapshot",
            "total_attempts",
            "completed_at",
            "ended_at",
        )
    )
    for run in runs:
        # Ascending id order: the last run seen per level is the latest one.
        latest_runs[run.challenge_level_id] = run
        if run.mode == "primary" and run.status == "started":
            active_runs[run.challenge_level_id] = run
        if run.mode == "primary" and run.status == "completed" and run_meets_progress_threshold(run=run):
            progress_counts[run.challenge_level_id] = progress_counts.get(run.challenge_level_id, 0) + 1

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
    level_count = AdventureLevel.objects.filter(
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
        "level_count": level_count,
        "progress": {
            "value": 100.0 if completed else 0.0,
            "numerator": completed,
            "denominator": 1 if level_count else 0,
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
                "level_count": len([level for level in form.adventure_levels.all() if level.is_published]),
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
    ordered = _ordered_levels(challenge.challenge_levels.all())
    levels = [
        challenge_level_access_payload(level=level, access=access, sibling_levels=ordered)
        for level in ordered
    ]
    return {
        "item_type": "challenge",
        "id": challenge.id,
        "slug": challenge.slug,
        "title": challenge.title,
        "summary": challenge.summary,
        "narrative": challenge.narrative,
        "levels": levels,
    }


def challenge_levels_access_payload(*, user, challenge: Challenge) -> list[dict]:
    """Per-level access for every sibling level of a challenge, ordered
    easy→hard. Reuses the same access context the Tower uses so statuses
    (locked / in_progress / completed) match exactly between the Tower and the
    in-run level navigator."""
    access = _build_challenge_access(user=user, storey_id=challenge.storey_id, challenges=[challenge])
    ordered = _ordered_levels(challenge.challenge_levels.all())
    return [
        challenge_level_access_payload(level=level, access=access, sibling_levels=ordered)
        for level in ordered
    ]


def challenge_level_access_payload(
    *,
    level: ChallengeLevel,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
) -> dict:
    completion = access.completions.get(level.id)
    active_run = access.active_runs.get(level.id)
    required = int(level.required_successful_attempts or 1)
    return {
        "id": level.id,
        "difficulty": level.difficulty,
        "status": _challenge_status(level=level, access=access, sibling_levels=sibling_levels),
        "review_available": bool(completion),
        "required_successful_attempts": level.required_successful_attempts,
        "successful_attempts": {
            "count": min(access.progress_counts.get(level.id, 0), required),
            "required": required,
        },
        "active_run_id": active_run.id if active_run else None,
        "latest_attempt": _latest_attempt_payload(access.latest_runs.get(level.id)),
        "completion": _completion_payload(completion),
        "command_budget": {
            "min_counted_commands": level.min_counted_commands,
            "max_counted_commands": level.max_counted_commands,
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
    level: ChallengeLevel,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
) -> str:
    if level.id in access.completions:
        return "completed"
    if level.id in access.active_runs:
        return "in_progress"
    if _challenge_unlocked(level=level, access=access, sibling_levels=sibling_levels):
        latest = access.latest_runs.get(level.id)
        return latest.status if latest and latest.status in {"failed", "abandoned"} else "not_started"
    return "locked"


def _challenge_unlocked(
    *,
    level: ChallengeLevel,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
) -> bool:
    if level.difficulty == DIFFICULTY_EASY:
        # Mirrors ChallengeRunService._ensure_adventure_passed: a storey's
        # challenges open once its Command Adventure has been passed.
        return access.adventure_passed
    previous = DIFFICULTY_EASY if level.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
    previous_level = next(
        (candidate for candidate in sibling_levels if candidate.difficulty == previous and candidate.is_published),
        None,
    )
    return bool(previous_level and previous_level.id in access.completions)


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


def _ordered_levels(levels) -> list[ChallengeLevel]:
    order = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: 1, DIFFICULTY_HARD: 2}
    return sorted(levels, key=lambda level: order.get(level.difficulty, 99))
