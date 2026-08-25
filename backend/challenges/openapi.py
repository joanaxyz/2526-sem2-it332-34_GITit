"""Schema-only success responses owned by the Challenge domain.

Runtime values stay in :mod:`challenges.payloads`; these serializers document
and validate that presenter output for OpenAPI generation.
"""

from rest_framework import serializers

from common.openapi import GameplayRunStatusField, RuntimeStepResponseSerializer


class ChallengeRunStepResponseSerializer(RuntimeStepResponseSerializer):
    command_classification = serializers.CharField(allow_blank=True)
    contextual_feedback = serializers.CharField(allow_blank=True)
    visualization_snapshot = serializers.DictField()
    created_at = serializers.DateTimeField()


class ChallengeCommandStepResponseSerializer(ChallengeRunStepResponseSerializer):
    evaluation_result = serializers.CharField()


class ChallengeCommandRunResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    replay = serializers.BooleanField()
    stars = serializers.IntegerField()
    status = GameplayRunStatusField()
    failure_reason = serializers.CharField(allow_null=True, allow_blank=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    counts = serializers.DictField()
    repository_state = serializers.DictField()
    visualization = serializers.DictField()
    mastery_progress = serializers.DictField(required=False)
    completion = serializers.DictField(required=False, allow_null=True)
    next_difficulty = serializers.DictField(required=False, allow_null=True)
    sibling_levels = serializers.ListField(child=serializers.DictField(), required=False)


class ChallengeRunResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    replay = serializers.BooleanField()
    stars = serializers.IntegerField()
    status = GameplayRunStatusField()
    failure_reason = serializers.CharField(allow_null=True, allow_blank=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    challenge = serializers.DictField()
    scenario_context = serializers.DictField()
    chapter = serializers.DictField()
    story = serializers.DictField(allow_null=True)
    battle_stage = serializers.DictField(allow_null=True)
    difficulty = serializers.CharField(allow_null=True)
    reward_coins = serializers.IntegerField()
    variant = serializers.DictField()
    mastery_progress = serializers.DictField()
    policy = serializers.DictField()
    counts = serializers.DictField()
    scaffolding = serializers.DictField()
    repository_state = serializers.DictField()
    visualization = serializers.DictField()
    expected_state = serializers.DictField(allow_null=True)
    steps = ChallengeRunStepResponseSerializer(many=True)
    next_difficulty = serializers.DictField(allow_null=True)
    sibling_levels = serializers.ListField(child=serializers.DictField())
    completion = serializers.DictField(allow_null=True)


class ChallengeCommandResponseSerializer(serializers.Serializer):
    run = ChallengeCommandRunResponseSerializer()
    command_outcome = serializers.DictField()
    stdout = serializers.CharField(allow_blank=True)
    stderr = serializers.CharField(allow_blank=True)
    exit_code = serializers.IntegerField()
    command_family = serializers.CharField(allow_blank=True)
    diagnostic_metadata = serializers.ListField(child=serializers.CharField())
    step = ChallengeCommandStepResponseSerializer()
