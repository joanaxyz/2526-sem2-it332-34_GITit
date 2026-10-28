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


class GuideHomeSerializer(serializers.Serializer):
    """The scenario whose command guide teaches a form."""

    chapter_number = serializers.IntegerField()
    level_title = serializers.CharField()
    difficulty = serializers.CharField()
    scenario_title = serializers.CharField(allow_blank=True)


class GuideElsewhereSerializer(serializers.Serializer):
    """The next move's command, whose guide opens in another scenario."""

    guide = CommandIntroductionResponseSerializer()
    home = GuideHomeSerializer()


class TipSerializer(serializers.Serializer):
    key = serializers.CharField()
    kind = serializers.ChoiceField(choices=["concept", "technique"])
    title = serializers.CharField()
    text = serializers.CharField()
    syntax = serializers.CharField(allow_null=True)


class TeachingResponseSerializer(serializers.Serializer):
    """What a tier run teaches; see ``tutoring.payloads.teaching_payload``."""

    tutor = CommandIntroductionResponseSerializer(allow_null=True)
    command_guides = CommandIntroductionResponseSerializer(many=True)
    guide_elsewhere = GuideElsewhereSerializer(allow_null=True)
    tips = TipSerializer(many=True)


class TutorTopicSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()


class TutorChatResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    suggested_topics = TutorTopicSerializer(many=True)
    # "guarded": scenario protection was active, so the reply teaches without solving,
    # or Home declined a scenario it recognised.
    response_kind = serializers.ChoiceField(choices=["answer", "guarded", "unavailable"])
    # True inside a level, and on Home only when it declined a recognised scenario;
    # a guarded reply to an uncertain match is protected without claiming a scenario.
    scenario_related = serializers.BooleanField()
    unavailable_reason = serializers.ChoiceField(
        choices=["rate_limited", "timeout", "unavailable"], required=False
    )
    retry_after_seconds = serializers.IntegerField(min_value=1, max_value=86400, required=False)


class TutorChatErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()
    retry_after_seconds = serializers.IntegerField(min_value=1, max_value=86400, required=False)
