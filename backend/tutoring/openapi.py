from rest_framework import serializers


class CommandIntroductionFormSerializer(serializers.Serializer):
    teaching_key = serializers.CharField()
    usage_form = serializers.CharField()
    label = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)


class RepositoryChangeSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=[
        "repository", "commit", "branch", "head", "staging", "working_tree", "conflict",
        "tag", "remote", "config", "stash", "operation",
    ])
    text = serializers.CharField()


class CommandIntroductionResponseSerializer(serializers.Serializer):
    context_id = serializers.CharField()
    teaching_key = serializers.CharField()
    run_revision = serializers.IntegerField()
    phase = serializers.ChoiceField(choices=["introduction", "feedback"])
    title = serializers.CharField()
    needs = RepositoryChangeSerializer(many=True)
    changes = RepositoryChangeSerializer(many=True)
    verdict = serializers.ChoiceField(choices=["correct", "incorrect"], allow_null=True)
    explanation = serializers.CharField(allow_null=True)
    example_command = serializers.CharField(allow_null=True)
    completion_token = serializers.CharField(allow_null=True)
    command_form = CommandIntroductionFormSerializer()


class IntroductionCompleteResponseSerializer(serializers.Serializer):
    tutor = CommandIntroductionResponseSerializer(allow_null=True)
