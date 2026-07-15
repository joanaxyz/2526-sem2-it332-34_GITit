from rest_framework import serializers

from players.models import PlayerPreferences


class PlayerPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerPreferences
        fields = ("motion_mode",)
