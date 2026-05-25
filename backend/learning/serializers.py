from rest_framework import serializers

from learning.models import LearningUnit, Lesson, OrientationProgress


class LessonListSerializer(serializers.ModelSerializer):
    is_complete = serializers.SerializerMethodField()
    scenario_count = serializers.IntegerField(source="published_scenario_count", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "slug",
            "title",
            "subtitle",
            "sort_order",
            "is_complete",
            "scenario_count",
        ]

    def get_is_complete(self, obj) -> bool:
        annotated_value = getattr(obj, "is_complete_for_user", None)
        if annotated_value is not None:
            return bool(annotated_value)
        progress_map = self.context.get("orientation_progress_map", {})
        progress = progress_map.get(obj.id)
        return bool(progress and progress.completed_at)


class UnitListSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True)
    lesson_count = serializers.IntegerField(source="published_lesson_count", read_only=True)
    scenario_count = serializers.IntegerField(source="published_scenario_count", read_only=True)
    practice_completion = serializers.SerializerMethodField()

    class Meta:
        model = LearningUnit
        fields = [
            "id",
            "slug",
            "number",
            "title",
            "description",
            "is_orientation",
            "sort_order",
            "lesson_count",
            "scenario_count",
            "practice_completion",
            "lessons",
        ]

    def get_practice_completion(self, obj) -> dict:
        denominator = (
            int(self.context.get("practice_completion_denominator_map", {}).get(obj.id, 0) or 0)
            if not obj.is_orientation
            else 0
        )
        numerator = int(self.context.get("practice_completion_count_map", {}).get(obj.id, 0) or 0)
        value = round((numerator / denominator) * 100, 1) if denominator else 0.0
        return {
            "value": value,
            "numerator": numerator,
            "denominator": denominator,
        }


class LessonDetailSerializer(serializers.ModelSerializer):
    module = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    scenario_count = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "slug",
            "title",
            "subtitle",
            "content_html",
            "scoped_css",
            "interaction_steps",
            "module",
            "unit",
            "is_complete",
            "scenario_count",
        ]

    def get_unit(self, obj):
        return self.get_module(obj)

    def get_module(self, obj):
        return {
            "id": obj.unit_id,
            "slug": obj.unit.slug,
            "number": obj.unit.number,
            "title": obj.unit.title,
            "is_orientation": obj.unit.is_orientation,
        }

    def get_is_complete(self, obj) -> bool:
        progress_map = self.context.get("orientation_progress_map", {})
        progress = progress_map.get(obj.id)
        return bool(progress and progress.completed_at)

    def get_scenario_count(self, obj) -> int:
        return obj.scenarios.filter(
            is_published=True,
            difficulty_instances__is_published=True,
        ).distinct().count()


class OrientationProgressSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField()
    is_complete = serializers.BooleanField()

    class Meta:
        model = OrientationProgress
        fields = ["lesson_id", "highest_step_seen", "completed_at", "is_complete"]


class OrientationCompleteSerializer(serializers.Serializer):
    highest_step_seen = serializers.IntegerField(min_value=0)
