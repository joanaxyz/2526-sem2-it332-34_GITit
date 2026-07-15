from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from common.openapi import (
    ShopMutationRequestSerializer,
    ShopPurchaseResponseSerializer,
    ShopResponseSerializer,
)
from players.services import get_or_create_player
from shop.selectors import shop_payload
from shop.services import ShopService


class ShopAPIView(APIView):
    """The shop catalog: stories and companions with ownership flags."""

    @extend_schema(responses={200: ShopResponseSerializer})
    def get(self, request):
        player = get_or_create_player(request.user)
        return Response(shop_payload(player=player))


class ShopPurchaseAPIView(APIView):
    @extend_schema(request=ShopMutationRequestSerializer, responses={201: ShopPurchaseResponseSerializer})
    def post(self, request):
        kind = (request.data.get("kind") or "").strip()
        slug = (request.data.get("slug") or "").strip()
        player = get_or_create_player(request.user)
        result = ShopService().purchase(player=player, kind=kind, slug=slug)
        return Response({**result, "shop": shop_payload(player=player)}, status=201)

