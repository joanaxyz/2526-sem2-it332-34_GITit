"""Schema-only success responses owned by the Drill domain.

Runtime values stay in :mod:`drills.payloads`; these serializers document
that presenter output for OpenAPI generation so the frontend consumes
generated types instead of hand-written shapes.
"""

from rest_framework import serializers


class DrillChoiceSerializer(serializers.Serializer):
    """One wrong option, and the authored line that explains it.

    ``gloss`` is always another real command form's own text, which is what
    lets a miss be answered with the truth ("-A stages all changes") rather
    than a generic "incorrect".
    """

    value = serializers.CharField()
    gloss = serializers.CharField(allow_blank=True)


class DrillBlankSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    answer = serializers.CharField()
    options = DrillChoiceSerializer(many=True)


class DrillCardSerializer(serializers.Serializer):
    key = serializers.CharField()
    command = serializers.CharField()
    intent = serializers.CharField()
    base_command = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)
    tokens = serializers.ListField(child=serializers.CharField())
    command_choices = DrillChoiceSerializer(many=True)
    intent_choices = DrillChoiceSerializer(many=True)
    blank = DrillBlankSerializer(allow_null=True)
    bank = serializers.ListField(child=serializers.CharField())


class DrillSequenceSerializer(serializers.Serializer):
    label = serializers.CharField(allow_blank=True)
    task = serializers.CharField(allow_blank=True)
    steps = serializers.ListField(child=serializers.CharField())


class DrillLevelSerializer(serializers.Serializer):
    """Where the drill came from, flat.

    Chapter and story identity are carried as plain fields rather than
    nested objects: the drill needs a breadcrumb and a way back to the
    map, not a second copy of the catalog contract that curriculum owns.
    """

    id = serializers.IntegerField()
    slug = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    chapter_id = serializers.IntegerField(allow_null=True)
    chapter_number = serializers.IntegerField(allow_null=True)
    chapter_title = serializers.CharField(allow_blank=True)
    story_slug = serializers.CharField(allow_blank=True)
    story_title = serializers.CharField(allow_blank=True)


class DrillProgressSerializer(serializers.Serializer):
    sessions = serializers.IntegerField()
    clears = serializers.IntegerField()
    cleared = serializers.BooleanField()
    best_accuracy = serializers.IntegerField()
    last_accuracy = serializers.IntegerField()
    shaky_form_keys = serializers.ListField(child=serializers.CharField())
    first_cleared_at = serializers.DateTimeField(allow_null=True)
    last_played_at = serializers.DateTimeField(allow_null=True)


class DrillResumeSerializer(serializers.Serializer):
    """An unfinished queue handed back so a return lands mid-drill."""

    id = serializers.IntegerField()
    queue_state = serializers.DictField()
    answered = serializers.IntegerField()
    correct = serializers.IntegerField()
    updated_at = serializers.DateTimeField()


class LevelDrillPlanResponseSerializer(serializers.Serializer):
    level = DrillLevelSerializer()
    available = serializers.BooleanField()
    progress = DrillProgressSerializer()
    resume = DrillResumeSerializer(allow_null=True)
    cards = DrillCardSerializer(many=True)
    sequence = DrillSequenceSerializer(allow_null=True)


class DrillReportResponseSerializer(serializers.Serializer):
    progress = DrillProgressSerializer()


class DrillRunStateResponseSerializer(serializers.Serializer):
    resume = DrillResumeSerializer(allow_null=True)
