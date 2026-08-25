"""Input-validation serializers for challenge endpoints.

Response payloads are built in challenges/payloads.py (presenter layer).
"""

from rest_framework import serializers


class ChallengeRunStartSerializer(serializers.Serializer):
    source_entry_point = serializers.ChoiceField(
        choices=["level_page", "retry"],
        default="level_page",
    )
    prior_run_id = serializers.IntegerField(required=False, allow_null=True)
    replay = serializers.BooleanField(required=False, default=False)
