from rest_framework import serializers

from common.serializers import ClientCommandExecutionSerializer


class CommandSubmitSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)
    execution = ClientCommandExecutionSerializer()


class WorkspaceFileSerializer(serializers.Serializer):
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
