from rest_framework import serializers


class CommandIntroductionFormSerializer(serializers.Serializer):
    teaching_key = serializers.CharField()
    usage_form = serializers.CharField()
    label = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)


class RepositoryChangeSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(
        choices=[
            "repository",
            "commit",
            "branch",
            "head",
            "staging",
            "working_tree",
            "conflict",
            "tag",
            "remote",
            "config",
            "stash",
            "operation",
        ]
    )
    text = serializers.CharField()
    # Absent on changes recorded before these fields existed.
    action = serializers.ChoiceField(
        choices=["create", "delete", "move", "add", "remove", "set", "start", "finish"],
        required=False,
    )
    subjects = serializers.ListField(child=serializers.CharField(), required=False)
    ref = serializers.CharField(required=False)


class SyntaxPartSerializer(serializers.Serializer):
    token = serializers.CharField()
    text = serializers.CharField()


class ConceptSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()
    text = serializers.CharField()


class CommandIntroductionResponseSerializer(serializers.Serializer):
    context_id = serializers.CharField()
    teaching_key = serializers.CharField()
    help_token = serializers.CharField()
    run_revision = serializers.IntegerField()
    phase = serializers.ChoiceField(choices=["introduction", "feedback"])
    title = serializers.CharField()
    needs = RepositoryChangeSerializer(many=True)
    changes = RepositoryChangeSerializer(many=True)
    verdict = serializers.ChoiceField(choices=["correct", "incorrect"], allow_null=True)
    explanation = serializers.CharField(allow_null=True)
    completion_token = serializers.CharField(allow_null=True)
    command_form = CommandIntroductionFormSerializer()
    anatomy = SyntaxPartSerializer(many=True)
    concepts = ConceptSerializer(many=True)


class IntroductionCompleteResponseSerializer(serializers.Serializer):
    tutor = CommandIntroductionResponseSerializer(allow_null=True)


class TutorTeachingSourceSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()


class TutorChatResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    sources = TutorTeachingSourceSerializer(many=True)
    suggested_topics = TutorTeachingSourceSerializer(many=True)
    response_kind = serializers.ChoiceField(choices=["explanation", "concept_redirect", "clarification", "unavailable"])
    scenario_related = serializers.BooleanField()
