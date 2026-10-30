from rest_framework import serializers

from progress.services.metrics import ACTIVITY_WINDOWS


class RateMetricSerializer(serializers.Serializer):
    value = serializers.FloatField(allow_null=True)
    numerator = serializers.FloatField()
    denominator = serializers.IntegerField()
    unit = serializers.ChoiceField(choices=["participants"], required=False)


class DashboardKpiSetSerializer(serializers.Serializer):
    scr = RateMetricSerializer()
    arc = RateMetricSerializer()
    hlcr = RateMetricSerializer()


RTA_HELP_TEXT = (
    "Retry Transfer Accuracy (Modules 3-4): successful first attempts on reserved, "
    "unseen transfer checkpoints over concluded checkpoints. Formal studies include unattempted assignments."
)
RETRY_SUCCESS_RATE_HELP_TEXT = (
    "Concluded retries following actual unsuccessful attempts that succeed."
)
# TODO(next release): drop the deprecated "rtr" alias once no deployed frontend
# reads it; it mirrors retry_success_rate so older bundles keep rendering.
RTR_DEPRECATED_HELP_TEXT = "Deprecated alias of retry_success_rate. Will be removed."


class PerformanceKpiSetSerializer(serializers.Serializer):
    scr = RateMetricSerializer()
    car = RateMetricSerializer()
    hlcr = RateMetricSerializer()
    rta = RateMetricSerializer(help_text=RTA_HELP_TEXT)
    retry_success_rate = RateMetricSerializer(help_text=RETRY_SUCCESS_RATE_HELP_TEXT)
    rtr = RateMetricSerializer(required=False, help_text=RTR_DEPRECATED_HELP_TEXT)
    arc = RateMetricSerializer()


class PerformanceModuleSerializer(serializers.Serializer):
    number = serializers.IntegerField()
    title = serializers.CharField()
    scr = RateMetricSerializer()
    car = RateMetricSerializer()
    hlcr = RateMetricSerializer()
    rta = RateMetricSerializer(help_text=RTA_HELP_TEXT)
    retry_success_rate = RateMetricSerializer(help_text=RETRY_SUCCESS_RATE_HELP_TEXT)
    rtr = RateMetricSerializer(required=False, help_text=RTR_DEPRECATED_HELP_TEXT)
    arc = RateMetricSerializer()


class TransferCheckpointSerializer(serializers.Serializer):
    tier_id = serializers.IntegerField()
    title = serializers.CharField()
    run_id = serializers.IntegerField(allow_null=True)


class PerformanceSamplesSerializer(serializers.Serializer):
    """Evidence coverage behind the KPI values; see KPI_METHODOLOGY.md."""

    participants = serializers.IntegerField()
    attempted_tiers = serializers.IntegerField(
        help_text="Tiers with an outcome: mastered, a concluded run, or commands left idle 7+ days."
    )
    in_progress_tiers = serializers.IntegerField(
        help_text="Opened tiers with no outcome yet; outside the SCR and HLCR denominators."
    )
    mastered_tiers = serializers.IntegerField()
    mastery_missing = serializers.IntegerField()
    car_scored = serializers.IntegerField()
    car_missing = serializers.IntegerField()
    transfer_assigned = serializers.IntegerField()
    transfer_pending = serializers.IntegerField()
    transfer_missing = serializers.IntegerField()


class PerformanceSummaryResponseSerializer(serializers.Serializer):
    objectives = serializers.DictField(
        child=RateMetricSerializer(),
        help_text="CAR by specific objective, scoped to the same learners and runs as this summary.",
    )
    kpis = PerformanceKpiSetSerializer()
    completed_sessions = serializers.IntegerField()
    modules = PerformanceModuleSerializer(many=True)
    samples = PerformanceSamplesSerializer()
    transfers = TransferCheckpointSerializer(many=True)


class DashboardCountsSerializer(serializers.Serializer):
    started = serializers.IntegerField()
    completed = serializers.IntegerField()
    failed = serializers.IntegerField()
    abandoned = serializers.IntegerField()


class DashboardRetryTrendSerializer(serializers.Serializer):
    level_title = serializers.CharField()
    attempts = serializers.IntegerField()
    retries = serializers.IntegerField()
    label = serializers.CharField()


class StatsSkillAxisSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    hint = serializers.CharField()
    value = serializers.FloatField(allow_null=True)
    command = serializers.CharField()


class StatsTrendPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    levels_completed = serializers.IntegerField()
    commands_run = serializers.IntegerField()


class StatsScopedCountSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    scope = serializers.CharField()


class StatsHeadlineSerializer(serializers.Serializer):
    levels_completed = serializers.IntegerField()
    finish_rate = RateMetricSerializer()
    accuracy = serializers.FloatField(allow_null=True)
    hard_tier_clears = StatsScopedCountSerializer()
    comebacks = StatsScopedCountSerializer()
    perfect_clears = serializers.IntegerField()
    gate_trial_clears = serializers.IntegerField()
    hard_gate_trial_clears = serializers.IntegerField()
    gitcoins = serializers.IntegerField()
    gitcoins_earned = serializers.IntegerField()
    commands_run = serializers.IntegerField()


class StatsSummaryResponseSerializer(serializers.Serializer):
    skill_profile = StatsSkillAxisSerializer(many=True)
    activity_trend = StatsTrendPointSerializer(many=True)
    # Echoed back so the client labels the plot with the window it actually got,
    # not the one it asked for: an unknown window resolves to the default.
    activity_window = serializers.ChoiceField(choices=sorted(ACTIVITY_WINDOWS))
    headline = StatsHeadlineSerializer()


class StatsActivityResponseSerializer(serializers.Serializer):
    activity_trend = StatsTrendPointSerializer(many=True)
    # Echo the resolved range just like the full summary so an unknown query
    # value can never make the client mislabel the returned buckets.
    activity_window = serializers.ChoiceField(choices=sorted(ACTIVITY_WINDOWS))


class DashboardSummaryResponseSerializer(serializers.Serializer):
    kpis = DashboardKpiSetSerializer()
    chapter_kpis = serializers.DictField(child=DashboardKpiSetSerializer())
    counts = DashboardCountsSerializer()
    completed_story_slug = serializers.CharField(allow_null=True)
    completed_stories = serializers.ListField(child=serializers.CharField())
    perfect_clears = serializers.IntegerField()
    mastery = serializers.FloatField()
    retry_trends = DashboardRetryTrendSerializer(many=True)
