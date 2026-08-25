from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from adminconsole.flags import feature_enabled
from players.services import get_or_create_player
from shop.selectors import shop_payload
from shop.serializers import (
    ShopMutationRequestSerializer,
    ShopPurchaseResponseSerializer,
    ShopResponseSerializer,
)
from shop.services import ShopService


class ShopAPIView(APIView):
    """The shop catalog: stories and companions with ownership flags."""

    @extend_schema(responses={200: ShopResponseSerializer})
    def get(self, request):
        player = get_or_create_player(request.user)
        return Response(ShopResponseSerializer(shop_payload(player=player)).data)


class ShopPurchaseAPIView(APIView):
    @extend_schema(
        request=ShopMutationRequestSerializer, responses={201: ShopPurchaseResponseSerializer}
    )
    def post(self, request):
        if not feature_enabled("shop-purchases"):
            raise PermissionDenied("Shop purchases are temporarily disabled.")
        serializer = ShopMutationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kind = serializer.validated_data["kind"]
        slug = serializer.validated_data["slug"]
        player = get_or_create_player(request.user)
        result = ShopService().purchase(player=player, kind=kind, slug=slug)
        response = ShopPurchaseResponseSerializer({**result, "shop": shop_payload(player=player)})
        return Response(response.data, status=201)
