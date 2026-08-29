from collections.abc import Mapping

from rest_framework import serializers

from curriculum.models import Story


class StrictSerializer(serializers.Serializer):
    """Reject misspelled or stale fields instead of silently ignoring them."""

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            unknown = set(data) - set(self.fields)
            if unknown:
                raise serializers.ValidationError(
                    {field: "Unknown field." for field in sorted(unknown)}
                )
        return super().to_internal_value(data)


class WalletSummarySerializer(serializers.Serializer):
    balance = serializers.IntegerField(min_value=0)


class AdminUserBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    is_staff = serializers.BooleanField()
    is_active = serializers.BooleanField()
    date_joined = serializers.DateTimeField()


class AdminUserDetailSerializer(AdminUserBriefSerializer):
    last_login = serializers.DateTimeField(allow_null=True)
    wallet = WalletSummarySerializer()
    entitlement_count = serializers.IntegerField(min_value=0)


class AdminUserListResponseSerializer(serializers.Serializer):
    results = AdminUserBriefSerializer(many=True)


class AdminUserListQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, max_length=255)


class AdminUserActionRequestSerializer(StrictSerializer):
    action = serializers.ChoiceField(choices=["grant_coins", "set_staff", "set_active"])
    amount = serializers.IntegerField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=64)
    value = serializers.BooleanField(required=False)
    request_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        action = attrs["action"]
        if action == "grant_coins":
            if "amount" not in attrs:
                raise serializers.ValidationError({"amount": "This field is required."})
            if attrs["amount"] == 0:
                raise serializers.ValidationError({"amount": "Amount must be non-zero."})
            if not attrs.get("reason", "").strip():
                raise serializers.ValidationError({"reason": "This field is required."})
            if "request_id" not in attrs:
                raise serializers.ValidationError({"request_id": "This field is required."})
        elif "value" not in attrs:
            raise serializers.ValidationError({"value": "This field is required."})
        return attrs


class AdminEconomyAdjustRequestSerializer(StrictSerializer):
    user_id = serializers.IntegerField(min_value=1)
    amount = serializers.IntegerField()
    reason = serializers.CharField(max_length=64, allow_blank=False)
    request_id = serializers.UUIDField()

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("Amount must be non-zero.")
        return value


class AdminEconomyAdjustResponseSerializer(serializers.Serializer):
    wallet = WalletSummarySerializer()
    applied = serializers.BooleanField()


class AdminFeatureFlagSerializer(serializers.Serializer):
    key = serializers.ChoiceField(choices=["shop-purchases"])
    label = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    enabled = serializers.BooleanField()


class AdminSettingsResponseSerializer(serializers.Serializer):
    feature_flags = AdminFeatureFlagSerializer(many=True)


class AdminFeatureFlagUpdateRequestSerializer(StrictSerializer):
    key = serializers.ChoiceField(choices=["shop-purchases"])
    enabled = serializers.BooleanField()


class AdminOverviewUsersSerializer(serializers.Serializer):
    total = serializers.IntegerField(min_value=0)
    new_7d = serializers.IntegerField(min_value=0)
    new_30d = serializers.IntegerField(min_value=0)


class AdminOverviewEconomySerializer(serializers.Serializer):
    coins_in_circulation = serializers.IntegerField(min_value=0)
    coins_spent = serializers.IntegerField(min_value=0)
    signup_grant = serializers.IntegerField(min_value=0)


class AdminRecentPurchaseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    amount = serializers.IntegerField(max_value=-1)
    reason = serializers.CharField()
    created_at = serializers.DateTimeField()


class AdminRecentActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    actor = serializers.CharField(allow_null=True)
    action = serializers.CharField()
    target_label = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()


class AdminOverviewResponseSerializer(serializers.Serializer):
    users = AdminOverviewUsersSerializer()
    economy = AdminOverviewEconomySerializer()
    recent_signups = AdminUserBriefSerializer(many=True)
    recent_purchases = AdminRecentPurchaseSerializer(many=True)
    recent_admin_actions = AdminRecentActionSerializer(many=True)


class AdminTransactionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    amount = serializers.IntegerField()
    reason = serializers.CharField()
    created_at = serializers.DateTimeField()


class AdminTransactionListResponseSerializer(serializers.Serializer):
    results = AdminTransactionSerializer(many=True)


class AdminTransactionListQuerySerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False, min_value=1)


class AdminOfficialChapterBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class AdminContentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kind = serializers.ChoiceField(choices=["adventure", "challenge", "lesson"])
    slug = serializers.SlugField()
    title = serializers.CharField()
    status = serializers.CharField()
    visibility = serializers.CharField()
    official_chapter = AdminOfficialChapterBriefSerializer(allow_null=True)
    updated_at = serializers.DateTimeField()


class AdminContentListResponseSerializer(serializers.Serializer):
    results = AdminContentSerializer(many=True)


class AdminContentListQuerySerializer(serializers.Serializer):
    kind = serializers.ChoiceField(
        choices=["adventure", "challenge", "lesson"],
        required=False,
    )


class AdminRunBreakdownSerializer(serializers.Serializer):
    by_status = serializers.DictField(child=serializers.IntegerField(min_value=0))
    total = serializers.IntegerField(min_value=0)
    passed = serializers.IntegerField(min_value=0)


class AdminRunsSerializer(AdminRunBreakdownSerializer):
    adventure = AdminRunBreakdownSerializer()
    challenge = AdminRunBreakdownSerializer()


class AdminCompletionsSerializer(serializers.Serializer):
    adventure = serializers.IntegerField(min_value=0)
    challenge = serializers.IntegerField(min_value=0)
    total = serializers.IntegerField(min_value=0)


class AdminStoryAnalyticsSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    title = serializers.CharField()
    runs = serializers.IntegerField(min_value=0)
    passed = serializers.IntegerField(min_value=0)
    adventure_runs = serializers.IntegerField(min_value=0)
    challenge_runs = serializers.IntegerField(min_value=0)


class AdminAnalyticsResponseSerializer(serializers.Serializer):
    runs = AdminRunsSerializer()
    completions = AdminCompletionsSerializer()
    active_learners_30d = serializers.IntegerField(min_value=0)
    per_story = AdminStoryAnalyticsSerializer(many=True)


class AdminModerationContentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kind = serializers.CharField()
    title = serializers.CharField()
    owner = serializers.CharField(allow_null=True)
    updated_at = serializers.DateTimeField()


class AdminModerationListResponseSerializer(serializers.Serializer):
    content = AdminModerationContentSerializer(many=True)


class AdminModerationUnpublishRequestSerializer(StrictSerializer):
    kind = serializers.ChoiceField(choices=["content"])
    id = serializers.IntegerField(min_value=1)


class AdminOkayResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField()


class AdminStoryPrerequisiteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.SlugField()
    title = serializers.CharField()


class AdminStorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.SlugField()
    title = serializers.CharField()
    summary = serializers.CharField(allow_blank=True)
    price = serializers.IntegerField(min_value=0)
    world_slug = serializers.SlugField()
    difficulty = serializers.ChoiceField(choices=Story.DIFFICULTY_CHOICES)
    prerequisite_story = AdminStoryPrerequisiteSerializer(allow_null=True)
    sort_order = serializers.IntegerField(min_value=0)
    is_published = serializers.BooleanField()
    chapter_count = serializers.IntegerField(min_value=0)
    management_source = serializers.CharField()


class AdminStoryListResponseSerializer(serializers.Serializer):
    results = AdminStorySerializer(many=True)
    world_options = serializers.ListField(child=serializers.SlugField())


class AdminStoryCreateRequestSerializer(StrictSerializer):
    slug = serializers.SlugField(max_length=50)
    title = serializers.CharField(max_length=160)
    summary = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
        default="",
    )
    price = serializers.IntegerField(required=False, min_value=0, default=0)
    world_slug = serializers.SlugField(max_length=64)
    difficulty = serializers.ChoiceField(
        choices=Story.DIFFICULTY_CHOICES,
        required=False,
        default=Story.DIFFICULTY_BEGINNER,
    )
    prerequisite_story = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        default=None,
    )
    sort_order = serializers.IntegerField(required=False, min_value=0)
    is_published = serializers.BooleanField(required=False, default=False)


class AdminStoryUpdateRequestSerializer(StrictSerializer):
    title = serializers.CharField(required=False, max_length=160)
    summary = serializers.CharField(required=False, allow_blank=True, max_length=4000)
    price = serializers.IntegerField(required=False, min_value=0)
    world_slug = serializers.SlugField(required=False, max_length=64)
    difficulty = serializers.ChoiceField(
        choices=Story.DIFFICULTY_CHOICES,
        required=False,
    )
    prerequisite_story = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    sort_order = serializers.IntegerField(required=False, min_value=0)
    is_published = serializers.BooleanField(required=False)


class AdminChapterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    story_id = serializers.IntegerField(allow_null=True)
    slug = serializers.SlugField()
    number = serializers.IntegerField(min_value=1)
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    is_published = serializers.BooleanField()
    is_playable = serializers.BooleanField()
    sort_order = serializers.IntegerField(min_value=0)
    battle_stage = serializers.DictField()
    management_source = serializers.CharField()


class AdminChapterListResponseSerializer(serializers.Serializer):
    results = AdminChapterSerializer(many=True)


class AdminChapterListQuerySerializer(serializers.Serializer):
    story = serializers.IntegerField(required=False, min_value=1)


class AdminChapterCreateRequestSerializer(StrictSerializer):
    story_id = serializers.IntegerField(min_value=1)
    slug = serializers.SlugField(max_length=50)
    number = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=160)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=8000,
        default="",
    )
    is_published = serializers.BooleanField(required=False, default=False)
    is_playable = serializers.BooleanField(required=False, default=False)
    sort_order = serializers.IntegerField(required=False, min_value=0)
    battle_stage = serializers.DictField(required=False, default=dict)


class AdminChapterUpdateRequestSerializer(StrictSerializer):
    number = serializers.IntegerField(required=False, min_value=1)
    title = serializers.CharField(required=False, max_length=160)
    description = serializers.CharField(required=False, allow_blank=True, max_length=8000)
    is_published = serializers.BooleanField(required=False)
    is_playable = serializers.BooleanField(required=False)
    sort_order = serializers.IntegerField(required=False, min_value=0)
    battle_stage = serializers.DictField(required=False)
