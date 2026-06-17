from dataclasses import dataclass, field

from django.db.models import Count, Q

from challenges.models import Challenge, ChallengeLevel, ChallengeRun
from challenges.selectors import (
    command_accuracy_rate,
    run_meets_progress_threshold,
)
from command_adventures.models import AdventureLevel, AdventureRun, CommandAdventure
from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
    SESSION_MODE_PRIMARY,
)
from curriculum.library import library_key_for_command
from curriculum.models import CommandForm, CommandSkill, LibraryEntry, Chapter, Tome

# The single official relic art every interactable uses for now (skinned later).
OFFICIAL_RELIC_SLUG = "official-relic"

# Free-canvas default geometry for one chapter's relics. The public Archive
# scrolls vertically through chapters, so relics scatter down a tall band; the
# kind is what drives the relic overview, not the position.
RELIC_DEFAULT_WIDTH = 200
RELIC_DEFAULT_HEIGHT = 120
# A relic's default interactive/landing regions, relative to its own box.
_DEFAULT_INTERACTIVE_VIEWBOX = {"x": 30, "y": 24, "width": 140, "height": 72}
_DEFAULT_LANDING_VIEWBOX = {"x1": 12, "y1": 112, "x2": 188, "y2": 112}
# Where each kind lands on the chapter canvas (x, y in canvas px).
_RELIC_TOME_POS = {"x": 40, "y": 0}
_RELIC_ADVENTURE_POS = {"x": 260, "y": 200}
_RELIC_CHALLENGE_ROW_Y = 440
_RELIC_CHALLENGE_X = {DIFFICULTY_EASY: 80, DIFFICULTY_MEDIUM: 300, DIFFICULTY_HARD: 520}


def published_chapters():
    return (
        Chapter.objects.filter(is_published=True)
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


def chapter_completion_count_map(*, user, chapter_ids: list[int]) -> dict[int, int]:
    if not getattr(user, "is_authenticated", False) or not chapter_ids:
        return {}

    completion_by_chapter = {chapter_id: 0 for chapter_id in chapter_ids}
    # Count each Command Adventure at most once per chapter: the milestone is
    # *passing* the adventure (passed_at), not how many times it was run. Replays
    # never set passed_at, so they cannot inflate progress past the 1-per-chapter
    # denominator. Distinct on the adventure id keeps this idempotent across runs.
    for chapter_id, _adventure_id in (
        AdventureRun.objects.filter(
            user=user,
            mode=SESSION_MODE_PRIMARY,
            passed_at__isnull=False,
            command_adventure__chapter_id__in=chapter_ids,
        )
        .values_list("command_adventure__chapter_id", "command_adventure_id")
        .distinct()
    ):
        completion_by_chapter[chapter_id] += 1

    challenge_counts: dict[tuple[int, int], int] = {}
    required_by_level: dict[int, int] = {}
    chapter_by_level: dict[int, int] = {}
    for run in (
        ChallengeRun.objects.filter(
            user=user,
            mode="primary",
            status="completed",
            chapter_id__in=chapter_ids,
        )
        .select_related("challenge_level")
        .only(
            "id",
            "chapter_id",
            "challenge_level_id",
            "counted_action_total",
            "command_budget_snapshot",
            "challenge_level__required_successful_attempts",
        )
    ):
        if not run_meets_progress_threshold(run=run):
            continue
        level_id = run.challenge_level_id
        challenge_counts[(run.chapter_id, level_id)] = (
            challenge_counts.get((run.chapter_id, level_id), 0) + 1
        )
        required_by_level[level_id] = run.challenge_level.required_successful_attempts
        chapter_by_level[level_id] = run.chapter_id

    for (_, level_id), count in challenge_counts.items():
        chapter_id = chapter_by_level[level_id]
        completion_by_chapter[chapter_id] += min(count, required_by_level.get(level_id, 1))
    return completion_by_chapter


def chapter_completion_denominator_map(*, chapter_ids: list[int]) -> dict[int, int]:
    if not chapter_ids:
        return {}

    denominator_by_chapter = {chapter_id: 0 for chapter_id in chapter_ids}
    for adventure in CommandAdventure.objects.filter(chapter_id__in=chapter_ids, is_published=True):
        denominator_by_chapter[adventure.chapter_id] += 1

    for row in ChallengeLevel.objects.filter(
        is_published=True,
        challenge__is_published=True,
        challenge__chapter_id__in=chapter_ids,
    ).values("challenge__chapter_id", "required_successful_attempts"):
        chapter_id = row["challenge__chapter_id"]
        denominator_by_chapter[chapter_id] += int(row["required_successful_attempts"] or 0)
    return denominator_by_chapter


def chapter_content_page(
    *,
    user,
    chapter_id: int,
    section: str,
    cursor: int | None = None,
    limit: int = 8,
) -> dict:
    limit = max(1, min(limit, 24))
    if section == "command_adventures":
        adventures = list(
            CommandAdventure.objects.filter(chapter_id=chapter_id, is_published=True)
            .select_related("chapter")
            .order_by("sort_order", "id")
        )
        return {
            "section": section,
            "results": [
                command_adventure_summary_payload(user=user, adventure=adventure)
                for adventure in adventures
            ],
            "next_cursor": None,
        }

    if section == "tomes":
        tomes = Tome.objects.filter(chapter_id=chapter_id, is_published=True).order_by(
            "sort_order", "id"
        )
        return {
            "section": section,
            "results": [tome_summary_payload(tome=tome) for tome in tomes],
            "next_cursor": None,
        }

    if section == "challenges":
        queryset = challenge_queryset(chapter_id=chapter_id)
        if cursor:
            queryset = queryset.filter(id__gt=cursor)
        items = list(queryset[: limit + 1])
        visible = items[:limit]
        access = _build_challenge_access(user=user, chapter_id=chapter_id, challenges=visible)
        return {
            "section": section,
            "results": [
                challenge_summary_payload(challenge=challenge, access=access)
                for challenge in visible
            ],
            "next_cursor": visible[-1].id if len(items) > limit and visible else None,
        }

    queryset = command_skill_queryset(chapter_id=chapter_id)
    if cursor:
        queryset = queryset.filter(id__gt=cursor)
    items = list(queryset[: limit + 1])
    visible = items[:limit]
    return {
        "section": "command_skills",
        "results": [command_skill_summary_payload(user=user, skill=skill) for skill in visible],
        "next_cursor": visible[-1].id if len(items) > limit and visible else None,
    }


def chapter_content_overview(*, user, chapter_id: int) -> dict:
    """Every relic for one chapter in a single payload.

    The Archive renders a chapter's Command Adventure (always one), its tomes,
    and its challenges as floating relics - each of which was previously a
    separate request. Chapters hold only a handful, so this returns them all (no
    cursor): collapsing 2-3 round trips per chapter into one is the win.
    """
    adventures = list(
        CommandAdventure.objects.filter(chapter_id=chapter_id, is_published=True)
        .select_related("chapter")
        .order_by("sort_order", "id")
    )
    tomes = Tome.objects.filter(chapter_id=chapter_id, is_published=True).order_by("sort_order", "id")
    challenges = list(challenge_queryset(chapter_id=chapter_id))
    access = _build_challenge_access(user=user, chapter_id=chapter_id, challenges=challenges)
    chapter = Chapter.objects.get(id=chapter_id)
    layout = relic_layout_payload(
        chapter=chapter,
        chapter_id=chapter_id,
        adventures=adventures,
        tomes=list(tomes),
        challenges=challenges,
    )
    # If the viewer has a private fork of the official Archive, render the FORK's
    # relics — the exact positions/regions its editor shows — and bind only the
    # curriculum's content (what each relic opens) onto its interactable relics.
    # Falls back to the plain curriculum layout when the fork has no relics here.
    fork = _viewer_official_fork(user=user)
    if fork is not None:
        fork_layout = _fork_chapter_layout(fork=fork, chapter_id=chapter_id, curriculum_layout=layout)
        if fork_layout is not None:
            layout = fork_layout
    adventure_payloads = [
        command_adventure_summary_payload(user=user, adventure=adventure)
        for adventure in adventures
    ]
    return {
        "chapter_id": chapter_id,
        "command_adventure": adventure_payloads[0] if adventure_payloads else None,
        "command_adventures": adventure_payloads,
        "tomes": [tome_summary_payload(tome=tome) for tome in tomes],
        "challenges": [
            challenge_summary_payload(challenge=challenge, access=access)
            for challenge in challenges
        ],
        "relic_layout": {"chapterId": chapter_id, "relics": layout["relics"]},
    }


def _viewer_official_fork(*, user):
    """The viewer's own private fork of the official Archive, or None.

    Imported lazily to avoid an import cycle (archive.services already
    imports this module for the fork seed)."""
    if not getattr(user, "is_authenticated", False):
        return None
    from archive.models import (
        ORIGIN_OFFICIAL_FORK,
        STATUS_ARCHIVED,
        ArchiveDesign,
    )

    return (
        ArchiveDesign.objects.filter(owner=user, origin=ORIGIN_OFFICIAL_FORK)
        .exclude(status=STATUS_ARCHIVED)
        .order_by("-updated_at", "-id")
        .first()
    )


def _fork_chapter_layout(*, fork, chapter_id: int, curriculum_layout: dict) -> dict | None:
    """Build one rendered chapter from the viewer's fork relics.

    The fork stores its relics grouped by ``chapter_index`` (the curriculum
    Chapter id). Interactable fork relics carry no content of their own; the
    curriculum's content is rebound to them by (kind, ordinal) so positions are
    the author's but the content is always live.
    """
    from archive.models import RELIC_KIND_NORMAL, RelicPlacement

    placements = list(
        RelicPlacement.objects.filter(archive_design=fork, chapter_index=chapter_id)
        .select_related("relic_asset", "relic_asset__relic")
        .order_by("z_index", "id")
    )
    if not placements:
        return None

    from archive.selectors import relic_placement_payload

    # Curriculum content bindings in order, grouped by kind.
    bindings_by_kind: dict[str, list] = {}
    for relic in curriculum_layout["relics"]:
        kind = relic["kind"]
        if kind == RELIC_KIND_NORMAL:
            continue
        bindings_by_kind.setdefault(kind, []).append(relic.get("contentBinding"))

    relics = []
    seen: dict[str, int] = {}
    for placement in placements:
        payload = relic_placement_payload(placement)
        payload["id"] = f"{placement.id}:chapter:{chapter_id}"
        payload["contentBinding"] = None
        if placement.kind != RELIC_KIND_NORMAL:
            ordinal = seen.get(placement.kind, 0)
            seen[placement.kind] = ordinal + 1
            options = bindings_by_kind.get(placement.kind) or []
            binding = options[ordinal] if ordinal < len(options) else None
            if binding:
                payload["contentBinding"] = binding
        relics.append(payload)

    return {"chapterId": chapter_id, "relics": relics}


def relic_layout_payload(
    *,
    chapter: Chapter | None = None,
    chapter_id: int,
    adventures: list[CommandAdventure] | None = None,
    tomes: list[Tome],
    challenges: list[Challenge],
) -> dict:
    """Flat list of floating relics for one chapter.

    Every interactable (each adventure, each tome, each challenge level) becomes
    one relic with a free canvas position, its ``kind``, and a content binding.
    Positions are sensible defaults; the official fork (and later per-chapter
    overrides) can move them.
    """
    relics: list[dict] = []
    z = 10

    for index, tome in enumerate(tomes or []):
        relics.append(
            _relic(
                chapter_id=chapter_id,
                name=f"tome-{tome.id}",
                kind="tome",
                content_binding={"kind": "tome", "id": tome.id},
                x=_RELIC_TOME_POS["x"] + index * 60,
                y=_RELIC_TOME_POS["y"] + index * 40,
                z_index=z,
            )
        )
        z += 1

    for index, adventure in enumerate(adventures or []):
        relics.append(
            _relic(
                chapter_id=chapter_id,
                name=f"adventure-{adventure.id}",
                kind="adventure",
                content_binding={"kind": "adventure", "id": adventure.id},
                x=_RELIC_ADVENTURE_POS["x"] + index * 60,
                y=_RELIC_ADVENTURE_POS["y"] + index * 40,
                z_index=z,
            )
        )
        z += 1

    for challenge_index, challenge in enumerate(challenges or []):
        levels = [
            level
            for level in _ordered_levels(challenge.challenge_levels.all())
            if getattr(level, "is_published", True)
        ]
        row_y = _RELIC_CHALLENGE_ROW_Y + challenge_index * 200
        for level in levels:
            difficulty = str(level.difficulty)
            relics.append(
                _relic(
                    chapter_id=chapter_id,
                    name=f"challenge-{challenge.id}-{difficulty}",
                    kind="challenge",
                    content_binding={
                        "kind": "challenge",
                        "id": challenge.id,
                        "levelId": level.id,
                        "difficulty": difficulty,
                    },
                    x=_RELIC_CHALLENGE_X.get(difficulty, 300),
                    y=row_y,
                    z_index=z,
                )
            )
            z += 1

    return {"chapterId": chapter_id, "relics": relics}


def _relic(
    *,
    chapter_id: int,
    name: str,
    kind: str,
    content_binding: dict | None,
    x: float,
    y: float,
    z_index: int,
    width: float = RELIC_DEFAULT_WIDTH,
    height: float = RELIC_DEFAULT_HEIGHT,
) -> dict:
    payload = {
        "id": f"chapter-{chapter_id}-relic-{name}",
        "assetSlug": OFFICIAL_RELIC_SLUG,
        "kind": kind,
        "x": x,
        "y": y,
        "scale": 1,
        "width": width,
        "height": height,
        "rotation": 0,
        "zIndex": z_index,
        "interactiveViewbox": dict(_DEFAULT_INTERACTIVE_VIEWBOX),
        "landingViewbox": dict(_DEFAULT_LANDING_VIEWBOX),
    }
    if content_binding:
        payload["contentBinding"] = content_binding
    return payload


def command_skill_queryset(*, chapter_id: int):
    return (
        CommandSkill.objects.filter(chapter_id=chapter_id, is_published=True)
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
    that teaches it - the same pass milestone (`passed_at`) that unlocks the
    chapter's challenges. Passing a chapter's adventure therefore grants every
    published command-skill in that chapter. Derived (not stored) so it can never
    drift from the progression that produced it.
    """
    if not getattr(user, "is_authenticated", False):
        return []
    passed_chapter_ids = set(
        AdventureRun.objects.filter(user=user, passed_at__isnull=False)
        .values_list("command_adventure__chapter_id", flat=True)
        .distinct()
    )
    if not passed_chapter_ids:
        return []
    skills = (
        CommandSkill.objects.filter(chapter_id__in=passed_chapter_ids, is_published=True)
        .select_related("chapter")
        .order_by("chapter__sort_order", "sort_order", "id")
    )
    return [
        {
            "id": skill.id,
            "slug": skill.slug,
            "base_command": skill.base_command,
            "title": skill.title,
            "summary": skill.summary,
            "chapter_id": skill.chapter_id,
            "chapter_number": skill.chapter.number,
            "chapter_title": skill.chapter.title,
        }
        for skill in skills
    ]


def chapter_book(*, chapter_id: int) -> dict | None:
    """The Chapter Book: every command registered for the chapter, each resolved to
    its rich authored content from the library.

    There is no terminal demo here - the book is reference material. Pages come
    from the seeded ``LibraryEntry`` for the skill's command (authored in
    ``library.py``, persisted by ``seed_command_library``); a minimal summary
    page is synthesized as a fallback so a registered command never renders
    empty."""
    chapter = (
        Chapter.objects.filter(id=chapter_id, is_published=True)
        .only("id", "slug", "number", "title", "description")
        .first()
    )
    if chapter is None:
        return None

    skills = list(
        CommandSkill.objects.filter(chapter_id=chapter_id, is_published=True).order_by(
            "sort_order", "id"
        )
    )
    # One query for the whole book: resolve every skill's library entry in bulk
    # so a chapter with N commands does not cost N round trips.
    keys = {library_key_for_command(skill.base_command) for skill in skills if skill.base_command}
    entries = {
        entry.command_key: entry
        for entry in LibraryEntry.objects.filter(command_key__in=keys, is_published=True)
    }
    commands = [
        book_command_payload(
            skill=skill,
            entry=entries.get(library_key_for_command(skill.base_command))
            if skill.base_command
            else None,
        )
        for skill in skills
    ]
    return {
        "chapter_id": chapter.id,
        "slug": chapter.slug,
        "number": chapter.number,
        "title": chapter.title,
        "description": chapter.description,
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


def challenge_queryset(*, chapter_id: int):
    return (
        Challenge.objects.filter(chapter_id=chapter_id, is_published=True)
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


def _build_challenge_access(
    *, user, chapter_id: int, challenges: list[Challenge]
) -> ChallengeAccessContext:
    from progress.models import LevelCompletion

    if not getattr(user, "is_authenticated", False):
        return ChallengeAccessContext()
    level_ids = [level.id for challenge in challenges for level in challenge.challenge_levels.all()]
    if not level_ids:
        return ChallengeAccessContext(
            adventure_passed=_adventure_passed(user=user, chapter_id=chapter_id)
        )

    completions = {
        completion.challenge_level_id: completion
        for completion in LevelCompletion.objects.filter(
            user=user, challenge_level_id__in=level_ids
        )
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
        if (
            run.mode == "primary"
            and run.status == "completed"
            and run_meets_progress_threshold(run=run)
        ):
            progress_counts[run.challenge_level_id] = (
                progress_counts.get(run.challenge_level_id, 0) + 1
            )

    return ChallengeAccessContext(
        completions=completions,
        active_runs=active_runs,
        latest_runs=latest_runs,
        progress_counts=progress_counts,
        adventure_passed=_adventure_passed(user=user, chapter_id=chapter_id),
    )


def command_adventure_summary_payload(*, user, adventure: CommandAdventure) -> dict:
    authenticated = getattr(user, "is_authenticated", False)
    latest = (
        AdventureRun.objects.filter(user=user, command_adventure=adventure).order_by("-id").first()
        if authenticated
        else None
    )
    level_count = AdventureLevel.objects.filter(
        command_adventure=adventure,
        is_published=True,
        command_form__is_published=True,
        command_form__command_skill__is_published=True,
    ).count()
    if level_count == 0:
        level_count = AdventureLevel.objects.filter(
            command_adventure__isnull=True,
            command_form__command_skill__chapter=adventure.chapter,
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
                "level_count": len(
                    [level for level in form.adventure_levels.all() if level.is_published]
                ),
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
    easy-to-hard. Reuses the same access context the Tower uses so statuses
    (locked / in_progress / completed) match exactly between the Tower and the
    in-run level navigator."""
    access = _build_challenge_access(
        user=user, chapter_id=challenge.chapter_id, challenges=[challenge]
    )
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
    return CommandForm.objects.select_related("command_skill", "command_skill__chapter").get(
        id=form_id,
        is_published=True,
        command_skill__is_published=True,
        command_skill__chapter__is_published=True,
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
        return (
            latest.status if latest and latest.status in {"failed", "abandoned"} else "not_started"
        )
    return "locked"


def _challenge_unlocked(
    *,
    level: ChallengeLevel,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
) -> bool:
    if level.difficulty == DIFFICULTY_EASY:
        # Mirrors ChallengeRunService._ensure_adventure_passed: a chapter's
        # challenges open once its Command Adventure has been passed.
        return access.adventure_passed
    previous = DIFFICULTY_EASY if level.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
    previous_level = next(
        (
            candidate
            for candidate in sibling_levels
            if candidate.difficulty == previous and candidate.is_published
        ),
        None,
    )
    return bool(previous_level and previous_level.id in access.completions)


def _adventure_passed(*, user, chapter_id: int) -> bool:
    adventure_ids = list(
        CommandAdventure.objects.filter(chapter_id=chapter_id, is_published=True).values_list(
            "id", flat=True
        )
    )
    if not adventure_ids:
        return True  # chapter has no Command Adventure to gate on
    passed_ids = set(
        AdventureRun.objects.filter(
            user=user, command_adventure_id__in=adventure_ids, passed_at__isnull=False
        ).values_list("command_adventure_id", flat=True)
    )
    return set(adventure_ids).issubset(passed_ids)


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
