"""Small OpenAPI helpers shared by APIView modules.

These serializers intentionally document broad JSON contracts for presenter-built
payloads. They make the generated frontend contract useful without moving runtime
payload assembly back into serializers.
"""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from common.constants import (
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)

GAMEPLAY_RUN_STATUSES = (
    SESSION_STATUS_STARTED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_ABANDONED,
)


class EmptyRequestSerializer(serializers.Serializer):
    pass


class AnyObjectResponseSerializer(serializers.Serializer):
    """A documented JSON object response assembled by a service/presenter layer."""

    pass


class WalletResponseSerializer(serializers.Serializer):
    balance = serializers.IntegerField(required=False)
    transactions = serializers.ListField(required=False)


class OpenDictSerializer(serializers.Serializer):
    """Response field for presenter-owned nested objects with stable top-level shape."""

    pass


class WalletSummaryResponseSerializer(serializers.Serializer):
    balance = serializers.IntegerField()


@extend_schema_field(
    {"type": "string", "enum": list(GAMEPLAY_RUN_STATUSES)},
    component_name="GameplayRunStatus",
)
class GameplayRunStatusField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(choices=GAMEPLAY_RUN_STATUSES, **kwargs)


class RuntimeStepResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    command_text = serializers.CharField()
    terminal_output = serializers.CharField(allow_blank=True)
    result_category = serializers.CharField(allow_blank=True)


class StarCriterionResponseSerializer(serializers.Serializer):
    key = serializers.ChoiceField(
        choices=(
            "clear",
            "command_target",
            "retry_allowance",
            "generous_target",
            "efficient_target",
        )
    )
    state = serializers.ChoiceField(choices=("earned", "pending", "missed"))
    reason = serializers.ChoiceField(
        choices=(
            "not_cleared",
            "command_target_exceeded",
            "generous_target_exceeded",
            "efficient_target_exceeded",
            "retry_allowance_exceeded",
            "previous_scoring_rules",
        ),
        allow_null=True,
    )


class StarBreakdownResponseSerializer(serializers.Serializer):
    stars = serializers.IntegerField(min_value=0, max_value=3)
    available_stars = serializers.IntegerField(min_value=0, max_value=3)
    counted_commands = serializers.IntegerField(min_value=0)
    command_target = serializers.IntegerField(min_value=0)
    generous_target = serializers.IntegerField(min_value=1, required=False)
    maximum_commands = serializers.IntegerField(min_value=1, required=False)
    scoring_policy_version = serializers.IntegerField(min_value=1, required=False)
    retry_count = serializers.IntegerField(min_value=0)
    graded_under_previous_rules = serializers.BooleanField()
    criteria = StarCriterionResponseSerializer(many=True)


class CommandKnowledgeResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    kind = serializers.ChoiceField(choices=("command", "option", "argument"))
    command = serializers.CharField()
    title = serializers.CharField()
    token = serializers.CharField(allow_blank=True)
    syntax = serializers.CharField()
    text = serializers.CharField()
    when_to_use = serializers.CharField(allow_blank=True)


class LearnedSkillResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.CharField()
    base_command = serializers.CharField()
    title = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    chapter_number = serializers.IntegerField()
    chapter_title = serializers.CharField(allow_blank=True)
    learned_at = serializers.DateTimeField()
    knowledge = CommandKnowledgeResponseSerializer(many=True, required=False)


class LearnedSkillsResponseSerializer(serializers.Serializer):
    results = LearnedSkillResponseSerializer(many=True)


class CommandFormPreviewSkillResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.CharField()
    base_command = serializers.CharField()
    title = serializers.CharField()


class CommandFormPreviewResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.CharField()
    usage_form = serializers.CharField()
    label = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)
    is_playable = serializers.BooleanField()
    skill = CommandFormPreviewSkillResponseSerializer()
    command_preview = serializers.DictField()


class CommandComparisonResponseSerializer(serializers.Serializer):
    learner_count = serializers.IntegerField(min_value=0)
    example_count = serializers.IntegerField(min_value=0)
    relation = serializers.ChoiceField(choices=("fewer", "equal", "more"))
