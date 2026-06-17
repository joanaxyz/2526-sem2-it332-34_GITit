from rest_framework.response import Response
from rest_framework.views import APIView

from common.performance import timing
from curriculum.selectors import (
    get_command_form,
    learned_command_skills,
    published_chapters,
    chapter_book,
    chapter_completion_count_map,
    chapter_completion_denominator_map,
    chapter_content_overview,
    chapter_content_page,
)
from curriculum.serializers import ChapterListSerializer


class ChapterListAPIView(APIView):
    def get(self, request):
        chapters = list(published_chapters())
        chapter_ids = [chapter.id for chapter in chapters]
        serializer = ChapterListSerializer(
            chapters,
            many=True,
            context={
                "chapter_completion_count_map": chapter_completion_count_map(
                    user=request.user,
                    chapter_ids=chapter_ids,
                ),
                "chapter_completion_denominator_map": chapter_completion_denominator_map(
                    chapter_ids=chapter_ids,
                ),
            },
        )
        return Response(serializer.data)


class ChapterContentAPIView(APIView):
    def get(self, request, chapter_id: int):
        section = request.query_params.get("section") or "command_skills"
        cursor = _int_param(request.query_params.get("cursor"))
        # Clamp so a client can't request an unbounded page (?limit=999999).
        limit = min(max(_int_param(request.query_params.get("limit")) or 8, 1), 50)
        with timing("curriculum.chapter_content", chapter_id=chapter_id, section=section):
            return Response(
                chapter_content_page(
                    user=request.user,
                    chapter_id=chapter_id,
                    section=section,
                    cursor=cursor,
                    limit=limit,
                )
            )


class ChapterContentOverviewAPIView(APIView):
    def get(self, request, chapter_id: int):
        with timing("curriculum.chapter_overview", chapter_id=chapter_id):
            return Response(
                chapter_content_overview(user=request.user, chapter_id=chapter_id)
            )


class ChapterBookAPIView(APIView):
    def get(self, request, chapter_id: int):
        with timing("curriculum.chapter_book", chapter_id=chapter_id):
            book = chapter_book(chapter_id=chapter_id)
        if book is None:
            return Response({"detail": "Chapter not found."}, status=404)
        return Response(book)


class LearnedSkillsAPIView(APIView):
    """The player's registry of learned commands (their spellbook)."""

    def get(self, request):
        with timing("curriculum.learned_skills"):
            return Response({"results": learned_command_skills(user=request.user)})


class CommandFormPreviewAPIView(APIView):
    def get(self, request, form_id: int):
        form = get_command_form(form_id)
        return Response(
            {
                "id": form.id,
                "slug": form.slug,
                "usage_form": form.usage_form,
                "label": form.label,
                "summary": form.summary,
                "skill": {
                    "id": form.command_skill_id,
                    "slug": form.command_skill.slug,
                    "base_command": form.command_skill.base_command,
                    "title": form.command_skill.title,
                },
                "command_preview": form.command_preview or form.command_skill.command_preview or {},
            }
        )


def _int_param(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
