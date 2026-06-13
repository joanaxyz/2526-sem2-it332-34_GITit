from django.urls import path

from marketplace.views import (
    GalleryAssetListAPIView,
    GalleryContentListAPIView,
    GalleryTowerDesignListAPIView,
    StoreListingDetailAPIView,
    StoreListingListCreateAPIView,
    StoreListingPurchaseAPIView,
)

urlpatterns = [
    path("store/listings/", StoreListingListCreateAPIView.as_view(), name="store-listing-list"),
    path("store/listings/<int:listing_id>/", StoreListingDetailAPIView.as_view(), name="store-listing-detail"),
    path("store/listings/<int:listing_id>/purchase/", StoreListingPurchaseAPIView.as_view(), name="store-listing-purchase"),
    path("gallery/assets/", GalleryAssetListAPIView.as_view(), name="gallery-assets"),
    path("gallery/content/", GalleryContentListAPIView.as_view(), name="gallery-content"),
    path("gallery/tower-designs/", GalleryTowerDesignListAPIView.as_view(), name="gallery-tower-designs"),
]
