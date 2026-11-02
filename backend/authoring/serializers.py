from collections.abc import Mapping

from rest_framework import serializers

from authoring.models import (
    CONTENT_STATUSES,
    VISIBILITY_CHOICES,
    ContentKind,
)


class StrictRequestSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            unknown_fields = set(data) - set(self.fields)
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: "Unknown field." for field in sorted(unknown_fields)}
                )
        return super().to_internal_value(data)


class ValidationErrorRowSerializer(serializers.Serializer):
    field = serializers.CharField()
    message = serializers.CharField()


class ContentDefinitionSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kind = serializers.ChoiceField(choices=ContentKind.choices)
    owner_id = serializers.IntegerField(allow_null=True)
    chapter_id = serializers.IntegerField(allow_null=True)
    official_chapter_id = serializers.IntegerField(allow_null=True)
    source_definition_id = serializers.IntegerField(allow_null=True)
    visibility = serializers.ChoiceField(choices=VISIBILITY_CHOICES)
    status = serializers.ChoiceField(choices=CONTENT_STATUSES)
    slug = serializers.SlugField()
    title = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)
    tags = serializers.ListField(child=serializers.CharField())
    command_family = serializers.CharField(allow_blank=True)
    difficulty = serializers.CharField(allow_blank=True)
    validation_errors = ValidationErrorRowSerializer(many=True)
    published_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class ContentDefinitionSerializer(ContentDefinitionSummarySerializer):
    definition = serializers.DictField()


class ContentDefinitionListResponseSerializer(serializers.Serializer):
    results = ContentDefinitionSummarySerializer(many=True)


class ContentDefinitionCreateRequestSerializer(StrictRequestSerializer):
    kind = serializers.ChoiceField(choices=ContentKind.choices)
    visibility = serializers.ChoiceField(choices=VISIBILITY_CHOICES, required=False)
    slug = serializers.SlugField()
    title = serializers.CharField(max_length=180)
    summary = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    command_family = serializers.CharField(required=False, allow_blank=True)
    difficulty = serializers.CharField(required=False, allow_blank=True)
    chapter = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    official_chapter = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    definition = serializers.DictField(required=False)


class ContentDefinitionUpdateRequestSerializer(ContentDefinitionCreateRequestSerializer):
    kind = serializers.ChoiceField(choices=ContentKind.choices, required=False)
    slug = serializers.SlugField(required=False)
    title = serializers.CharField(required=False, max_length=180)


class ContentValidationResultSerializer(serializers.Serializer):
    valid = serializers.BooleanField()
    errors = ValidationErrorRowSerializer(many=True)


class ContentTestRunResultSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=ContentKind.choices)
    runtime_id = serializers.IntegerField(allow_null=True)
    start_path = serializers.CharField(required=False, allow_null=True)
    pages = serializers.ListField(required=False)
