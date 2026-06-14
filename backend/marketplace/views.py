from rest_framework.response import Response
from rest_framework.views import APIView

from authoring.selectors import content_payload
from marketplace.models import StoreListing
from marketplace.selectors import (
    active_listings,
    gallery_assets,
    gallery_content,
    gallery_tower_designs,
    listing_payload,
    listing_payloads,
)
from marketplace.services import MarketplaceService
from tower_designs.selectors import tower_design_payload


class MarketplaceListingListCreateAPIView(APIView):
    def get(self, request):
        queryset = active_listings(user=request.user)
        item_kind = request.query_params.get("item_kind")
        if item_kind:
            queryset = queryset.filter(item_kind=item_kind)
        return Response({"results": listing_payloads(list(queryset), user=request.user)})

    def post(self, request):
        listing = MarketplaceService().create_listing(user=request.user, data=request.data)
        return Response(listing_payload(listing, user=request.user), status=201)


class MarketplaceListingDetailAPIView(APIView):
    def get(self, request, listing_id: int):
        listing = active_listings(user=request.user).get(id=listing_id)
        return Response(listing_payload(listing, user=request.user))

    def patch(self, request, listing_id: int):
        listing = StoreListing.objects.get(id=listing_id)
        listing = MarketplaceService().update_listing(user=request.user, listing=listing, data=request.data)
        return Response(listing_payload(listing, user=request.user))


class MarketplaceListingPurchaseAPIView(APIView):
    def post(self, request, listing_id: int):
        listing = StoreListing.objects.select_related("asset", "content_definition", "tower_design").get(id=listing_id)
        result = MarketplaceService().purchase(user=request.user, listing=listing)
        entitlement = result["entitlement"]
        return Response(
            {
                "entitlement": {
                    "id": entitlement.id,
                    "item_kind": entitlement.item_kind,
                    "asset_id": entitlement.asset_id,
                    "content_definition_id": entitlement.content_definition_id,
                    "tower_design_id": entitlement.tower_design_id,
                    "source_listing_id": entitlement.source_listing_id,
                    "granted_at": entitlement.granted_at,
                },
                "wallet": result["wallet"],
            },
            status=201,
        )


class GalleryAssetListAPIView(APIView):
    def get(self, request):
        queryset = gallery_assets(user=request.user)
        kind = request.query_params.get("kind")
        if kind:
            queryset = queryset.filter(kind=kind)
        return Response(
            {
                "results": [
                    {
                        "id": asset.id,
                        "kind": asset.kind,
                        "slug": asset.slug,
                        "label": asset.label,
                        "visibility": asset.visibility,
                        "price": asset.price,
                    }
                    for asset in queryset
                ]
            }
        )


class GalleryContentListAPIView(APIView):
    def get(self, request):
        queryset = gallery_content(user=request.user)
        kind = request.query_params.get("kind")
        if kind:
            queryset = queryset.filter(kind=kind)
        return Response({"results": [content_payload(content, include_definition=False) for content in queryset]})


class GalleryTowerDesignListAPIView(APIView):
    def get(self, request):
        queryset = gallery_tower_designs(user=request.user)
        return Response({"results": [tower_design_payload(design) for design in queryset]})
