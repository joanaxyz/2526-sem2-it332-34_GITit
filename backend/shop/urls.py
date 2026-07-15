from django.urls import path

from shop.views import ShopAPIView, ShopPurchaseAPIView

urlpatterns = [
    path("shop/catalog/", ShopAPIView.as_view(), name="shop-catalog"),
    path("shop/catalog/purchase/", ShopPurchaseAPIView.as_view(), name="shop-catalog-purchase"),
]
