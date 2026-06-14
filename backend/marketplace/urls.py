from django.urls import path

from marketplace.views import (
    GalleryAssetListAPIView,
    GalleryContentListAPIView,
    GalleryTowerDesignListAPIView,
    MarketplaceListingDetailAPIView,
    MarketplaceListingListCreateAPIView,
    MarketplaceListingPurchaseAPIView,
)

urlpatterns = [
    path("marketplace/listings/", MarketplaceListingListCreateAPIView.as_view(), name="marketplace-listing-list"),
    path(
        "marketplace/listings/<int:listing_id>/",
        MarketplaceListingDetailAPIView.as_view(),
        name="marketplace-listing-detail",
    ),
    path(
        "marketplace/listings/<int:listing_id>/purchase/",
        MarketplaceListingPurchaseAPIView.as_view(),
        name="marketplace-listing-purchase",
    ),
    path("gallery/assets/", GalleryAssetListAPIView.as_view(), name="gallery-assets"),
    path("gallery/content/", GalleryContentListAPIView.as_view(), name="gallery-content"),
    path("gallery/tower-designs/", GalleryTowerDesignListAPIView.as_view(), name="gallery-tower-designs"),
]
