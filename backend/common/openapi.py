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


class LearnedSkillResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.CharField()
    base_command = serializers.CharField()
    title = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    chapter_number = serializers.IntegerField()
    chapter_title = serializers.CharField(allow_blank=True)


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
