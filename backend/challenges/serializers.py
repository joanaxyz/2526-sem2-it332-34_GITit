"""Input-validation serializers for challenge endpoints.

Response payloads are built in challenges/payloads.py (presenter layer).
"""

from rest_framework import serializers

from common.serializers import ClientCommandExecutionSerializer


class ChallengeRunStartSerializer(serializers.Serializer):
    source_entry_point = serializers.ChoiceField(
        choices=["level_page", "retry"],
        default="level_page",
    )
    prior_run_id = serializers.IntegerField(required=False, allow_null=True)
    replay = serializers.BooleanField(required=False, default=False)


class CommandSubmitSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)
    execution = ClientCommandExecutionSerializer()


class WorkspaceFileCreateSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=240)
    content = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20000,
        default="",
        trim_whitespace=False,
    )


class WorkspaceFilePathSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=240)


class WorkspaceFileRenameSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=240)
    new_path = serializers.CharField(max_length=240)
