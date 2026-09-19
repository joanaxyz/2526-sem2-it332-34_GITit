import json

from rest_framework import serializers

# A drill session is a handful of cards answered a handful of times; these
# bounds exist to keep a malformed or hostile report from writing nonsense
# into the progress row, not to grade anyone.
MAX_REPORTED_ANSWERS = 500
MAX_REPORTED_SHAKY_KEYS = 64


class DrillReportSerializer(serializers.Serializer):
    answers_total = serializers.IntegerField(min_value=0, max_value=MAX_REPORTED_ANSWERS)
    answers_correct = serializers.IntegerField(min_value=0, max_value=MAX_REPORTED_ANSWERS)
    completed = serializers.BooleanField()
    shaky_form_keys = serializers.ListField(
        child=serializers.CharField(max_length=160),
        max_length=MAX_REPORTED_SHAKY_KEYS,
        allow_empty=True,
        required=False,
        default=list,
    )

    def validate(self, attrs):
        if attrs["answers_correct"] > attrs["answers_total"]:
            raise serializers.ValidationError(
                {"answers_correct": "Correct answers cannot exceed answers given."}
            )
        return attrs


# A real session is a handful of cards with a short ladder each. The cap is
# generous enough for the longest authored level and small enough that a
# hostile payload cannot park megabytes in a JSON column.
MAX_QUEUE_CARDS = 64
MAX_QUEUE_LENGTH = 512
MAX_QUEUE_BYTES = 64 * 1024


class DrillRunStateSerializer(serializers.Serializer):
    """The client's in-progress queue, bounded before it is stored.

    Deliberately structural: the queue drives which questions the learner
    resumes into, not what anything pays, so this proves the payload is
    small and well-shaped and leaves the card keys to
    ``sanitize_queue_state`` - which checks them against the level's own
    seeded vocabulary.
    """

    cards = serializers.DictField(child=serializers.DictField(), allow_empty=True)
    queue = serializers.ListField(
        child=serializers.CharField(max_length=160),
        allow_empty=True,
        max_length=MAX_QUEUE_LENGTH,
    )
    sequence_pending = serializers.BooleanField(default=False)
    answered = serializers.IntegerField(min_value=0, max_value=MAX_REPORTED_ANSWERS)
    correct = serializers.IntegerField(min_value=0, max_value=MAX_REPORTED_ANSWERS)

    def validate_cards(self, value):
        if len(value) > MAX_QUEUE_CARDS:
            raise serializers.ValidationError(
                f"A drill cannot hold more than {MAX_QUEUE_CARDS} cards."
            )
        return value

    def validate(self, attrs):
        if attrs["correct"] > attrs["answered"]:
            raise serializers.ValidationError(
                {"correct": "Correct answers cannot exceed answers given."}
            )
        if len(json.dumps(attrs["cards"])) > MAX_QUEUE_BYTES:
            raise serializers.ValidationError({"cards": "Queue state is too large."})
        return attrs
