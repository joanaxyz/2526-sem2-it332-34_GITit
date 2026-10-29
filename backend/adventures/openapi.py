"""Schema-only success responses owned by the Adventure domain.

Runtime values stay in :mod:`adventures.tier_payloads`; these serializers
document and validate that presenter output for OpenAPI generation.
"""

from rest_framework import serializers

from common.openapi import (
    GameplayRunStatusField,
    LearnedSkillResponseSerializer,
    RuntimeStepResponseSerializer,
    StarBreakdownResponseSerializer,
)
from tutoring.openapi import TeachingResponseSerializer

# ---------------------------------------------------------------------------
# AdventureLevelTierRun response shapes - mirror challenges/openapi.py, since
# tier_payloads.py mirrors challenges/payloads.py's shape.
# ---------------------------------------------------------------------------


class AdventureLevelTierRunStepResponseSerializer(RuntimeStepResponseSerializer):
    command_classification = serializers.CharField(allow_blank=True)
    contextual_feedback = serializers.CharField(allow_blank=True)
    visualization_snapshot = serializers.DictField()
    created_at = serializers.DateTimeField()


class AdventureLevelTierCommandStepResponseSerializer(AdventureLevelTierRunStepResponseSerializer):
    evaluation_result = serializers.CharField()


class AdventureLevelTierCommandRunResponseSerializer(TeachingResponseSerializer):
    id = serializers.IntegerField()
    replay = serializers.BooleanField()
    stars = serializers.IntegerField()
    star_breakdown = StarBreakdownResponseSerializer(allow_null=True)
    status = GameplayRunStatusField()
    failure_reason = serializers.CharField(allow_null=True, allow_blank=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    counts = serializers.DictField()
    repository_state = serializers.DictField()
    visualization = serializers.DictField()
    progress = serializers.DictField(required=False)
    completion = serializers.DictField(required=False, allow_null=True)
    next_difficulty = serializers.DictField(required=False, allow_null=True)
    rewards = serializers.DictField(required=False, allow_null=True)


class AdventureLevelTierRewardResponseSerializer(serializers.Serializer):
    """The tier's first-clear GitCoin reward, shown before play."""

    coins = serializers.IntegerField()
    claimed = serializers.BooleanField()


class AdventureLevelTierScenarioPositionResponseSerializer(serializers.Serializer):
    """Which of the tier's ordered scenarios the run plays."""

    index = serializers.IntegerField(allow_null=True)
    total = serializers.IntegerField()
    title = serializers.CharField(allow_blank=True)


class AdventureLevelTierRunResponseSerializer(TeachingResponseSerializer):
    id = serializers.IntegerField()
    replay = serializers.BooleanField()
    transfer = serializers.BooleanField(required=False)
    stars = serializers.IntegerField()
    star_breakdown = StarBreakdownResponseSerializer(allow_null=True)
    status = GameplayRunStatusField()
    failure_reason = serializers.CharField(allow_null=True, allow_blank=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    tier = serializers.DictField()
    scenario_context = serializers.DictField()
    chapter = serializers.DictField(allow_null=True)
    story = serializers.DictField(allow_null=True)
    difficulty = serializers.CharField(allow_null=True)
    variant = serializers.DictField()
    scenario = AdventureLevelTierScenarioPositionResponseSerializer()
    progress = serializers.DictField()
    policy = serializers.DictField()
    counts = serializers.DictField()
    scaffolding = serializers.DictField()
    repository_state = serializers.DictField()
    visualization = serializers.DictField()
    expected_state = serializers.DictField(allow_null=True)
    steps = AdventureLevelTierRunStepResponseSerializer(many=True)
    next_difficulty = serializers.DictField(allow_null=True)
    completion = serializers.DictField(allow_null=True)
    reward = AdventureLevelTierRewardResponseSerializer()


class AdventureLevelTierCommandResponseSerializer(serializers.Serializer):
    learned_skills = LearnedSkillResponseSerializer(many=True, required=False)
    run = AdventureLevelTierCommandRunResponseSerializer()
    command_outcome = serializers.DictField()
    stdout = serializers.CharField(allow_blank=True)
    stderr = serializers.CharField(allow_blank=True)
    exit_code = serializers.IntegerField()
    command_family = serializers.CharField(allow_blank=True)
    diagnostic_metadata = serializers.ListField(child=serializers.CharField())
    step = AdventureLevelTierCommandStepResponseSerializer()
