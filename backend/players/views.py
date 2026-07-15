from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from common.openapi import ShopEquipResponseSerializer, ShopMutationRequestSerializer
from players.models import PlayerPreferences
from players.serializers import PlayerPreferencesSerializer
from players.services import get_or_create_player
from shop.selectors import shop_payload
from shop.services import ShopService


class PlayerPreferencesAPIView(APIView):
    def _record(self, request):
        player = get_or_create_player(request.user)
        record, _created = PlayerPreferences.objects.get_or_create(player=player)
        return record

    @extend_schema(responses={200: PlayerPreferencesSerializer})
    def get(self, request):
        return Response(PlayerPreferencesSerializer(self._record(request)).data)

    @extend_schema(request=PlayerPreferencesSerializer, responses={200: PlayerPreferencesSerializer})
    def patch(self, request):
        record = self._record(request)
        serializer = PlayerPreferencesSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CompanionLoadoutAPIView(APIView):
    @extend_schema(request=ShopMutationRequestSerializer, responses={200: ShopEquipResponseSerializer})
    def post(self, request):
        serializer = ShopMutationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kind = serializer.validated_data["kind"].strip()
        slug = serializer.validated_data["slug"].strip()
        player = get_or_create_player(request.user)
        result = ShopService().equip(player=player, kind=kind, slug=slug)
        return Response({**result, "shop": shop_payload(player=player)})
