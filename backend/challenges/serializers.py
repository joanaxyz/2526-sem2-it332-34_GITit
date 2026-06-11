"""Input-validation serializers for challenge endpoints.

Response payloads are built in challenges/payloads.py (presenter layer).
"""

from rest_framework import serializers


class ChallengeRunStartSerializer(serializers.Serializer):
    source_entry_point = serializers.ChoiceField(
        choices=["tower_page", "retry", "review"],
        default="tower_page",
    )
    prior_run_id = serializers.IntegerField(required=False, allow_null=True)
    review = serializers.BooleanField(required=False, default=False)


class CommandSubmitSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


class WorkspaceFileCreateSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=240)
    content = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20000,
        default="",
        trim_whitespace=False,
    )
