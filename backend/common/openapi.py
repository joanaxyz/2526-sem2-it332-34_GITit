"""Small OpenAPI helpers shared by APIView modules.

These serializers intentionally document broad JSON contracts for presenter-built
payloads. They make the generated frontend contract useful without moving runtime
payload assembly back into serializers.
"""

from rest_framework import serializers


class EmptyRequestSerializer(serializers.Serializer):
    pass


class DetailResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class AnyObjectResponseSerializer(serializers.Serializer):
    """A documented JSON object response assembled by a service/presenter layer."""

    pass


class WalletResponseSerializer(serializers.Serializer):
    balance = serializers.IntegerField(required=False)
    transactions = serializers.ListField(required=False)


class AccessTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


class AuthUserResponseSerializer(serializers.Serializer):
    user = serializers.DictField()


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    user = serializers.DictField()


class ShopMutationRequestSerializer(serializers.Serializer):
    kind = serializers.CharField(max_length=32)
    slug = serializers.CharField(max_length=120)


class OpenDictSerializer(serializers.Serializer):
    """Response field for presenter-owned nested objects with stable top-level shape."""

    pass


class RateMetricSerializer(serializers.Serializer):
    value = serializers.FloatField(required=False, allow_null=True)
    numerator = serializers.IntegerField(required=False)
    denominator = serializers.IntegerField(required=False)


class WalletSummaryResponseSerializer(serializers.Serializer):
    balance = serializers.IntegerField()


class DashboardSummaryResponseSerializer(serializers.Serializer):
    kpis = serializers.DictField()
    chapter_kpis = serializers.DictField()
    counts = serializers.DictField()
    completed_story_slug = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    completed_stories = serializers.ListField(child=serializers.CharField())
    streak = serializers.DictField()
    perfect_clears = serializers.IntegerField()
    mastery = serializers.FloatField()
    retry_trends = serializers.DictField()


class StatsSummaryResponseSerializer(serializers.Serializer):
    skill_profile = serializers.ListField(child=serializers.DictField())
    activity = serializers.ListField(child=serializers.DictField())
    headlines = serializers.DictField()
    totals = serializers.DictField(required=False)


class ShopItemResponseSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=["story", "companion"])
    slug = serializers.CharField()
    label = serializers.CharField()
    price = serializers.IntegerField()
    owned = serializers.BooleanField()
    active = serializers.BooleanField()
    unlocks_story = serializers.DictField(required=False, allow_null=True)


class ShopResponseSerializer(serializers.Serializer):
    items = ShopItemResponseSerializer(many=True)
    active_companion = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ShopPurchaseResponseSerializer(serializers.Serializer):
    owned = serializers.BooleanField()
    wallet = WalletSummaryResponseSerializer()
    shop = ShopResponseSerializer()


class ShopEquipResponseSerializer(serializers.Serializer):
    active_companion = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    shop = ShopResponseSerializer()


class RuntimeStepResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    command_text = serializers.CharField()
    terminal_output = serializers.CharField(allow_blank=True, required=False)
    result_category = serializers.CharField(required=False, allow_blank=True)
    command_classification = serializers.CharField(required=False, allow_blank=True)
    contextual_feedback = serializers.CharField(required=False, allow_blank=True)
    visualization_snapshot = serializers.DictField(required=False)
    created_at = serializers.DateTimeField(required=False)


class ChallengeRunResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    replay = serializers.BooleanField()
    stars = serializers.IntegerField()
    status = serializers.CharField()
    failure_reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    completed_at = serializers.DateTimeField(required=False, allow_null=True)
    challenge = serializers.DictField()
    scenario_context = serializers.DictField(required=False)
    chapter = serializers.DictField()
    battle_stage = serializers.DictField(required=False, allow_null=True)
    difficulty = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    reward_coins = serializers.IntegerField(required=False)
    variant = serializers.DictField()
    mastery_progress = serializers.DictField()
    policy = serializers.DictField()
    counts = serializers.DictField()
    scaffolding = serializers.DictField()
    repository_state = serializers.DictField()
    visualization = serializers.DictField()
    expected_state = serializers.DictField(required=False, allow_null=True)
    steps = RuntimeStepResponseSerializer(many=True)
    next_difficulty = serializers.DictField(required=False, allow_null=True)
    sibling_levels = serializers.ListField(child=serializers.DictField(), required=False)
    completion = serializers.DictField(required=False, allow_null=True)


class ChallengeCommandResponseSerializer(serializers.Serializer):
    run = serializers.DictField()
    command_outcome = serializers.DictField()
    stdout = serializers.CharField(required=False, allow_blank=True)
    stderr = serializers.CharField(required=False, allow_blank=True)
    exit_code = serializers.IntegerField(required=False)
    command_family = serializers.CharField(required=False, allow_blank=True)
    diagnostic_metadata = serializers.ListField(child=serializers.CharField(), required=False)
    step = RuntimeStepResponseSerializer()


class AdventureRunResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    replay = serializers.BooleanField()
    stars = serializers.IntegerField()
    library_opened = serializers.BooleanField()
    is_passed = serializers.BooleanField()
    selected_level = serializers.DictField(required=False, allow_null=True)
    next_level = serializers.DictField(required=False, allow_null=True)
    story = serializers.DictField(required=False, allow_null=True)
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    battle_stage = serializers.DictField(required=False, allow_null=True)
    current_level_index = serializers.IntegerField()
    total_levels = serializers.IntegerField()
    current_wave = serializers.IntegerField()
    total_waves = serializers.IntegerField()
    mastery = serializers.DictField()
    completed_at = serializers.DateTimeField(required=False, allow_null=True)
    current_attempt = serializers.DictField(required=False, allow_null=True)
    results = serializers.ListField(child=serializers.DictField())
    progress = serializers.DictField()


class AdventureLevelLibraryResponseSerializer(serializers.Serializer):
    book = serializers.DictField()
    run = AdventureRunResponseSerializer()


class AdventureCommandResponseSerializer(serializers.Serializer):
    run = serializers.DictField()
    solved = serializers.BooleanField()
    stdout = serializers.CharField(allow_blank=True)
    stderr = serializers.CharField(allow_blank=True)
    exit_code = serializers.IntegerField()
    terminal_output = serializers.CharField(allow_blank=True)
    command_classification = serializers.CharField(allow_blank=True)
    step = RuntimeStepResponseSerializer()
    command_outcome = serializers.DictField()


class LearnedSkillResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.CharField()
    base_command = serializers.CharField()
    title = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    chapter_number = serializers.IntegerField()
    chapter_title = serializers.CharField(allow_blank=True)


class LearnedSkillsResponseSerializer(serializers.Serializer):
    results = LearnedSkillResponseSerializer(many=True)


class CommandFormPreviewSkillResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.CharField()
    base_command = serializers.CharField()
    title = serializers.CharField()


class CommandFormPreviewResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.CharField()
    usage_form = serializers.CharField()
    label = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)
    is_playable = serializers.BooleanField()
    skill = CommandFormPreviewSkillResponseSerializer()
    command_preview = serializers.DictField()
