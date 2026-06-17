from __future__ import annotations

import copy

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from authoring.compiler import ContentRuntimeCompiler
from authoring.models import (
    STATUS_PUBLISHED,
    STATUS_TESTABLE,
    AuthoringChapter,
    ContentDefinition,
)
from authoring.validators import ContentDefinitionValidator


class AuthoringChapterService:
    _FIELDS = (
        "slug",
        "title",
        "summary",
        "sort_order",
        "chest_rewards",
        "mob_roster",
        "boss_roster",
        "pass_bar_fraction",
        "battle_stage",
    )

    def assert_owner(self, *, user, chapter: AuthoringChapter) -> None:
        if not getattr(user, "is_staff", False) and chapter.owner_id != getattr(user, "id", None):
            raise PermissionDenied("You do not own this chapter.")

    @transaction.atomic
    def create(self, *, user, data: dict) -> AuthoringChapter:
        fields = {key: data[key] for key in self._FIELDS if key in data}
        fields.setdefault("title", "New chapter")
        fields.setdefault("slug", _unique_chapter_slug(user=user, base=fields.get("slug") or fields["title"]))
        if "sort_order" not in fields:
            fields["sort_order"] = AuthoringChapter.objects.filter(owner=user).count()
        chapter = AuthoringChapter(owner=user, **fields)
        chapter.full_clean()
        chapter.save()
        return chapter

    @transaction.atomic
    def update(self, *, user, chapter: AuthoringChapter, data: dict) -> AuthoringChapter:
        self.assert_owner(user=user, chapter=chapter)
        for field in self._FIELDS:
            if field in data:
                setattr(chapter, field, data[field])
        chapter.full_clean()
        chapter.save()
        return chapter

    @transaction.atomic
    def delete(self, *, user, chapter: AuthoringChapter) -> None:
        self.assert_owner(user=user, chapter=chapter)
        chapter.delete()  # content.chapter FK is SET_NULL, so content survives orphaned


class ContentDefinitionService:
    def assert_owner(self, *, user, content: ContentDefinition) -> None:
        if not getattr(user, "is_staff", False) and content.owner_id != getattr(user, "id", None):
            raise PermissionDenied("You do not own this content definition.")

    @transaction.atomic
    def create(self, *, user, data: dict) -> ContentDefinition:
        content = ContentDefinition(owner=user, **_content_fields(data))
        if "chapter" in data:
            content.chapter = _resolve_chapter(user=user, chapter_id=data.get("chapter"))
        content.full_clean()
        content.save()
        return content

    @transaction.atomic
    def update(self, *, user, content: ContentDefinition, data: dict) -> ContentDefinition:
        self.assert_owner(user=user, content=content)
        if content.status == STATUS_PUBLISHED and not data.get("visibility"):
            raise ValidationError({"status": "Published content can only be relisted or remixed, not edited in place."})
        for field, value in _content_fields(data, partial=True).items():
            setattr(content, field, value)
        if "chapter" in data:
            content.chapter = _resolve_chapter(user=user, chapter_id=data.get("chapter"))
        content.full_clean()
        content.save()
        return content

    @transaction.atomic
    def validate(self, *, user, content: ContentDefinition) -> dict:
        self.assert_owner(user=user, content=content)
        result = ContentDefinitionValidator().validate(content)
        content.validation_errors = result.errors
        if result.valid and content.status not in {STATUS_TESTABLE, STATUS_PUBLISHED}:
            content.status = STATUS_TESTABLE
            content.save(update_fields=["validation_errors", "status", "updated_at"])
        else:
            content.save(update_fields=["validation_errors", "updated_at"])
        return {"valid": result.valid, "errors": result.errors}

    @transaction.atomic
    def publish(self, *, user, content: ContentDefinition) -> ContentDefinition:
        self.assert_owner(user=user, content=content)
        result = ContentDefinitionValidator().validate(content)
        if not result.valid:
            content.validation_errors = result.errors
            content.save(update_fields=["validation_errors", "updated_at"])
            raise ValidationError({"validation_errors": result.errors})
        content.status = STATUS_PUBLISHED
        content.validation_errors = []
        content.published_at = timezone.now()
        content.save(update_fields=["status", "validation_errors", "published_at", "updated_at"])
        ContentRuntimeCompiler().compile(content=content)
        return content

    @transaction.atomic
    def test_run(self, *, user, content: ContentDefinition) -> dict:
        self.assert_owner(user=user, content=content)
        result = ContentDefinitionValidator().validate(content)
        if not result.valid:
            content.validation_errors = result.errors
            content.save(update_fields=["validation_errors", "updated_at"])
            raise ValidationError({"validation_errors": result.errors})
        if content.status != STATUS_PUBLISHED:
            content.status = STATUS_TESTABLE
            content.validation_errors = []
            content.save(update_fields=["status", "validation_errors", "updated_at"])
        runtime = ContentRuntimeCompiler().compile(content=content)
        return _runtime_entry(runtime)

    @transaction.atomic
    def remix(self, *, user, content: ContentDefinition) -> ContentDefinition:
        clone = ContentDefinition.objects.create(
            kind=content.kind,
            owner=user,
            source_definition=content,
            chapter=content.chapter if content.chapter_id and content.chapter.owner_id == user.id else None,
            visibility="private",
            status="draft",
            slug=_next_remix_slug(user=user, source=content),
            title=f"{content.title} Remix",
            summary=content.summary,
            tags=copy.deepcopy(content.tags),
            command_family=content.command_family,
            difficulty=content.difficulty,
            definition=copy.deepcopy(content.definition),
        )
        return clone


def _resolve_chapter(*, user, chapter_id) -> AuthoringChapter | None:
    if not chapter_id:
        return None
    try:
        return AuthoringChapter.objects.get(id=chapter_id, owner=user)
    except AuthoringChapter.DoesNotExist as exc:
        raise ValidationError({"chapter": "Unknown chapter."}) from exc


def _unique_chapter_slug(*, user, base: str) -> str:
    from django.utils.text import slugify

    root = slugify(base) or "chapter"
    slug = root
    index = 2
    while AuthoringChapter.objects.filter(owner=user, slug=slug).exists():
        slug = f"{root}-{index}"
        index += 1
    return slug


def _content_fields(data: dict, *, partial: bool = False) -> dict:
    allowed = {
        "kind",
        "visibility",
        "slug",
        "title",
        "summary",
        "tags",
        "command_family",
        "difficulty",
        "definition",
    }
    fields = {key: data[key] for key in allowed if key in data}
    if not partial:
        fields.setdefault("summary", "")
        fields.setdefault("tags", [])
        fields.setdefault("command_family", "")
        fields.setdefault("difficulty", "")
        fields.setdefault("definition", {})
    return fields


def _runtime_entry(runtime) -> dict:
    if runtime.command_adventure_id:
        return {
            "kind": "adventure",
            "runtime_id": runtime.command_adventure_id,
            "start_path": f"/command-adventures/{runtime.command_adventure.slug}",
        }
    if runtime.challenge_id:
        level = runtime.challenge.challenge_levels.filter(is_published=True).order_by("id").first()
        return {
            "kind": "challenge",
            "runtime_id": runtime.challenge_id,
            "start_path": f"/challenge-levels/{level.id}" if level else None,
        }
    if runtime.tome_id:
        return {"kind": "tome", "runtime_id": runtime.tome_id, "pages": runtime.tome.pages}
    return {"kind": "unknown", "runtime_id": None}


def _next_remix_slug(*, user, source: ContentDefinition) -> str:
    base = f"{source.slug}-remix"
    slug = base
    index = 2
    while ContentDefinition.objects.filter(owner=user, kind=source.kind, slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug
