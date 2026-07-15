import json

from rest_framework import serializers

MAX_EXECUTION_TEXT_LENGTH = 100_000
MAX_EXECUTION_STATE_BYTES = 256 * 1024


class StrictBooleanField(serializers.BooleanField):
    def to_internal_value(self, data):
        if not isinstance(data, bool):
            self.fail("invalid", input=data)
        return data


class ClientCommandExecutionSerializer(serializers.Serializer):
    """Strict validation for the browser-owned simulator result."""

    processed = StrictBooleanField()
    next_state = serializers.DictField()
    output = serializers.CharField(
        allow_blank=True,
        trim_whitespace=False,
        max_length=MAX_EXECUTION_TEXT_LENGTH,
    )
    normalized_command = serializers.CharField(
        allow_blank=True,
        trim_whitespace=False,
        max_length=500,
    )
    exit_code = serializers.IntegerField(min_value=-255, max_value=255)
    diagnostic = StrictBooleanField()
    stdout = serializers.CharField(
        allow_blank=True,
        trim_whitespace=False,
        max_length=MAX_EXECUTION_TEXT_LENGTH,
    )
    stderr = serializers.CharField(
        allow_blank=True,
        trim_whitespace=False,
        max_length=MAX_EXECUTION_TEXT_LENGTH,
    )
    command_family = serializers.CharField(
        allow_blank=True,
        trim_whitespace=False,
        max_length=80,
    )
    diagnostic_metadata = serializers.ListField(
        child=serializers.CharField(max_length=200),
        max_length=100,
    )
    client_run_revision = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    def validate_next_state(self, value: dict) -> dict:
        encoded = json.dumps(value, separators=(",", ":"), default=str).encode("utf-8")
        if len(encoded) > MAX_EXECUTION_STATE_BYTES:
            raise serializers.ValidationError("Repository state is too large.")
        return value
