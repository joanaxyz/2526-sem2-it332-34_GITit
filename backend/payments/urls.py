from django.urls import path

from payments.views import CheckoutSessionAPIView, GitCoinPacksAPIView, StripeWebhookAPIView

urlpatterns = [
    path("payments/packs/", GitCoinPacksAPIView.as_view(), name="payments-packs"),
    path("payments/checkout/", CheckoutSessionAPIView.as_view(), name="payments-checkout"),
    path("payments/webhook/", StripeWebhookAPIView.as_view(), name="payments-webhook"),
]
