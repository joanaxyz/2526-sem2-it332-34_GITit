from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    kpis = serializers.DictField()
    counts = serializers.DictField()
    streak = serializers.DictField()
    perfect_clears = serializers.IntegerField()
    retry_trends = serializers.ListField()
