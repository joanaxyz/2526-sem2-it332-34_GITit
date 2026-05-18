from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    kpis = serializers.DictField()
    counts = serializers.DictField()
    streak = serializers.DictField()
    first_attempt_stars = serializers.IntegerField()
    retry_trends = serializers.ListField()
