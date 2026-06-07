from rest_framework import serializers

from curriculum.models import ConceptPage, Storey


class FoundationTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptPage
        fields = [
            "id",
            "slug",
            "title",
            "summary",
            "body",
            "icon",
            "cards",
            "sort_order",
        ]


class StoreyListSerializer(serializers.ModelSerializer):
    command_skill_count = serializers.IntegerField(read_only=True)
    challenge_count = serializers.IntegerField(read_only=True)
    practice_completion = serializers.SerializerMethodField()

    class Meta:
        model = Storey
        fields = [
            "id",
            "slug",
            "number",
            "title",
            "description",
            "sort_order",
            "command_skill_count",
            "challenge_count",
            "practice_completion",
        ]

    def get_practice_completion(self, obj) -> dict:
        denominator_map = self.context.get("storey_completion_denominator_map", {})
        count_map = self.context.get("storey_completion_count_map", {})
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

