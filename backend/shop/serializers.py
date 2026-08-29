from rest_framework import serializers

from common.openapi import WalletSummaryResponseSerializer
from curriculum.models import Story


class StrictStringField(serializers.CharField):
    """Reject non-string JSON values before DRF can coerce numbers to text."""

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail("invalid")
        return super().to_internal_value(data)


class ShopMutationRequestSerializer(serializers.Serializer):
    kind = StrictStringField(max_length=32)
    slug = StrictStringField(max_length=120)


class ShopUnlockResponseSerializer(serializers.Serializer):
    slug = serializers.CharField()
    title = serializers.CharField()
    chapter_count = serializers.IntegerField()
    world_slug = serializers.CharField()
    difficulty = serializers.ChoiceField(choices=Story.DIFFICULTY_CHOICES)
    prerequisite_story = serializers.CharField(allow_null=True)


class ShopItemResponseSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=["story", "companion"])
    slug = serializers.CharField()
    label = serializers.CharField()
    price = serializers.IntegerField()
    owned = serializers.BooleanField()
    active = serializers.BooleanField()
    unlocks_story = ShopUnlockResponseSerializer(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("unlocks_story") is None:
            data.pop("unlocks_story", None)
        return data


class ShopResponseSerializer(serializers.Serializer):
    items = ShopItemResponseSerializer(many=True)
    active_companion = serializers.CharField(allow_null=True, allow_blank=True)
    purchases_enabled = serializers.BooleanField()


class ShopPurchaseResponseSerializer(serializers.Serializer):
    owned = serializers.BooleanField()
    wallet = WalletSummaryResponseSerializer()
    shop = ShopResponseSerializer()


class ShopEquipResponseSerializer(serializers.Serializer):
    active_companion = serializers.CharField(allow_null=True, allow_blank=True)
    shop = ShopResponseSerializer()
