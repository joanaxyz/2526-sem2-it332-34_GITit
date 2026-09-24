from rest_framework import serializers

from progress.services.metrics import ACTIVITY_WINDOWS


class RateMetricSerializer(serializers.Serializer):
    value = serializers.FloatField(allow_null=True)
    numerator = serializers.IntegerField()
    denominator = serializers.IntegerField()


class DashboardKpiSetSerializer(serializers.Serializer):
    scr = RateMetricSerializer()
    arc = RateMetricSerializer()
    hlcr = RateMetricSerializer()


RTA_HELP_TEXT = (
    "Retry Transfer Accuracy (Modules 3-4): first retries after a failure on a "
    "structurally changed variant that complete, over all such retries."
)
RETRY_SUCCESS_RATE_HELP_TEXT = "Learner-facing share of runs with a prior run that complete."
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
    hlcr = RateMetricSerializer()
    rta = RateMetricSerializer(help_text=RTA_HELP_TEXT)
    retry_success_rate = RateMetricSerializer(help_text=RETRY_SUCCESS_RATE_HELP_TEXT)
    rtr = RateMetricSerializer(required=False, help_text=RTR_DEPRECATED_HELP_TEXT)
    arc = RateMetricSerializer()


class PerformanceSummaryResponseSerializer(serializers.Serializer):
    kpis = PerformanceKpiSetSerializer()
    completed_sessions = serializers.IntegerField()
    modules = PerformanceModuleSerializer(many=True)


class DashboardCountsSerializer(serializers.Serializer):
    started = serializers.IntegerField()
    completed = serializers.IntegerField()
    failed = serializers.IntegerField()
    abandoned = serializers.IntegerField()


class DashboardStreakSerializer(serializers.Serializer):
    current = serializers.IntegerField()
    longest = serializers.IntegerField()
    last_completed_on = serializers.DateField(allow_null=True)


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
    boss_floors = StatsScopedCountSerializer()
    comebacks = StatsScopedCountSerializer()
    perfect_clears = serializers.IntegerField()
    day_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    gitcoins = serializers.IntegerField()
    commands_run = serializers.IntegerField()


class StatsSummaryResponseSerializer(serializers.Serializer):
    skill_profile = StatsSkillAxisSerializer(many=True)
    activity_trend = StatsTrendPointSerializer(many=True)
    # Echoed back so the client labels the plot with the window it actually got,
    # not the one it asked for: an unknown window resolves to the default.
    activity_window = serializers.ChoiceField(choices=sorted(ACTIVITY_WINDOWS))
    headline = StatsHeadlineSerializer()


class DashboardSummaryResponseSerializer(serializers.Serializer):
    kpis = DashboardKpiSetSerializer()
    chapter_kpis = serializers.DictField(child=DashboardKpiSetSerializer())
    counts = DashboardCountsSerializer()
    completed_story_slug = serializers.CharField(allow_null=True)
    completed_stories = serializers.ListField(child=serializers.CharField())
    streak = DashboardStreakSerializer()
    perfect_clears = serializers.IntegerField()
    mastery = serializers.FloatField()
    retry_trends = DashboardRetryTrendSerializer(many=True)
