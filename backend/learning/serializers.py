from rest_framework import serializers

from learning.models import LearningUnit, Lesson, OrientationProgress


class LessonListSerializer(serializers.ModelSerializer):
    is_complete = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "slug",
            "title",
            "subtitle",
            "kind",
            "sort_order",
            "is_complete",
        ]

    def get_is_complete(self, obj) -> bool:
        progress_map = self.context.get("orientation_progress_map", {})
        progress = progress_map.get(obj.id)
        return bool(progress and progress.completed_at)


class UnitListSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True)
    lesson_count = serializers.IntegerField(source="published_lesson_count", read_only=True)
    scenario_count = serializers.IntegerField(source="published_scenario_count", read_only=True)

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
            "lessons",
        ]


class LessonDetailSerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "slug",
            "title",
            "subtitle",
            "kind",
            "overview_html",
            "scoped_css",
            "interaction_steps",
            "unit",
            "is_complete",
        ]

    def get_unit(self, obj):
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


class OrientationProgressSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField()
    is_complete = serializers.BooleanField()

    class Meta:
        model = OrientationProgress
        fields = ["lesson_id", "highest_step_seen", "completed_at", "is_complete"]


class OrientationCompleteSerializer(serializers.Serializer):
    highest_step_seen = serializers.IntegerField(min_value=0)
