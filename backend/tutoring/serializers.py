from rest_framework import serializers


class IntroductionCompleteSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=16000)


class TutorChatContextSerializer(serializers.Serializer):
    surface = serializers.ChoiceField(choices=["home", "command_guide"])
    run_id = serializers.IntegerField(min_value=1, required=False)
    teaching_key = serializers.CharField(max_length=160, required=False)
    usage_form = serializers.CharField(max_length=200, required=False)
    guide_token = serializers.CharField(max_length=4000, required=False)

    def validate(self, attrs):
        if attrs["surface"] == "command_guide" and not all(
            attrs.get(key) for key in ("run_id", "teaching_key", "guide_token")
        ):
            raise serializers.ValidationError("A command guide needs a run and teaching key.")
        if attrs["surface"] == "home" and any(
            key in attrs for key in ("run_id", "teaching_key", "usage_form", "guide_token")
        ):
            raise serializers.ValidationError("Home help does not use a workspace guide.")
        return attrs


class TutorChatTurnSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    text = serializers.CharField(max_length=6000, trim_whitespace=True)


class TutorChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000, trim_whitespace=True)
    context = TutorChatContextSerializer()
    history = TutorChatTurnSerializer(many=True, required=False, default=list)

    def validate_history(self, value):
        if len(value) > 20:
            raise serializers.ValidationError("Conversation context is too long.")
        if sum(len(turn["text"]) for turn in value) > 32000:
            raise serializers.ValidationError("Conversation context is too long.")
        return value
