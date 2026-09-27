from rest_framework import serializers


class IntroductionCompleteSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=16000)
