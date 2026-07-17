from rest_framework import serializers

from curriculum.models import Chapter, Story
from curriculum.selectors import chapter_locked, story_completed, story_locked
from progress.chests import CHEST_SCHEDULE
from shop.access import owns_item
from shop.catalog import KIND_STORY


class StorySerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    owned = serializers.SerializerMethodField()
    prerequisite_story = serializers.SerializerMethodField()
    locked = serializers.SerializerMethodField()
    lock_reason = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "slug",
            "title",
            "summary",
            "price",
            "sort_order",
            "is_published",
            "completed",
            "owned",
            "world_slug",
            "difficulty",
            "prerequisite_story",
            "locked",
            "lock_reason",
        ]

    def _completed(self, story) -> bool:
        completed_map = self.context.get("story_completed_map")
        if completed_map is not None and story.id in completed_map:
            return completed_map[story.id]
        return story_completed(player=self.context.get("player"), story=story)

    def get_completed(self, obj) -> bool:
        return self._completed(obj)

    def get_owned(self, obj) -> bool:
        return owns_item(
            player=self.context.get("player"),
            kind=KIND_STORY,
            slug=obj.slug,
        )

    def get_prerequisite_story(self, obj) -> dict | None:
        prerequisite = obj.prerequisite_story
        if prerequisite is None:
            return None
        return {
            "slug": prerequisite.slug,
            "title": prerequisite.title,
            "completed": self._completed(prerequisite),
        }

    def get_locked(self, obj) -> bool:
        locked, _ = story_locked(
            player=self.context.get("player"),
            story=obj,
            completed_map=self.context.get("story_completed_map"),
        )
        return locked

    def get_lock_reason(self, obj) -> str:
        _, reason = story_locked(
            player=self.context.get("player"),
            story=obj,
            completed_map=self.context.get("story_completed_map"),
        )
        return reason


class ChapterListSerializer(serializers.ModelSerializer):
    command_skill_count = serializers.IntegerField(read_only=True)
    challenge_count = serializers.IntegerField(read_only=True)
    adventure_level_count = serializers.IntegerField(read_only=True)
    level_completion = serializers.SerializerMethodField()
    story = serializers.SerializerMethodField()
    locked = serializers.SerializerMethodField()
    lock_reason = serializers.SerializerMethodField()
    chest_schedule = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            "id",
            "slug",
            "number",
            "title",
            "description",
            "sort_order",
            "is_playable",
            "story",
            "locked",
            "lock_reason",
            "command_skill_count",
            "challenge_count",
            "adventure_level_count",
            "level_completion",
            "chest_schedule",
        ]

    def get_level_completion(self, obj) -> dict:
        denominator_map = self.context.get("chapter_completion_denominator_map", {})
        count_map = self.context.get("chapter_completion_count_map", {})
        denominator = int(
            denominator_map.get(obj.id, 0) or 0
        )
        numerator = int(
            count_map.get(obj.id, 0) or 0
        )
        value = round((numerator / denominator) * 100, 1) if denominator else 0.0
        return {
            "value": value,
            "numerator": numerator,
            "denominator": denominator,
        }

    def get_story(self, obj) -> dict | None:
        if not obj.story_id:
            return None
        return {
            "id": obj.story_id,
            "slug": obj.story.slug,
            "title": obj.story.title,
            "world_slug": obj.story.world_slug,
        }

    def get_locked(self, obj) -> bool:
        locked, _ = chapter_locked(player=self.context.get("player"), chapter=obj)
        return locked

    def get_lock_reason(self, obj) -> str:
        _, reason = chapter_locked(player=self.context.get("player"), chapter=obj)
        return reason

    def get_chest_schedule(self, obj) -> list[dict]:
        # Fixed, universal schedule computed at runtime - every chapter shows
        # the same reward-per-threshold preview; nothing is authored per chapter.
        return CHEST_SCHEDULE
