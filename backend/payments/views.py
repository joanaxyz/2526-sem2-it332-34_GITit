from uuid import uuid4

import stripe
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.openapi import (
    CheckoutSessionRequestSerializer,
    CheckoutSessionResponseSerializer,
    GitCoinPacksResponseSerializer,
)
from payments.packs import listings as pack_listings
from payments.services import PaymentReconciliationError, PaymentService
from players.services import get_or_create_player


class GitCoinPacksAPIView(APIView):
    @extend_schema(responses={200: GitCoinPacksResponseSerializer})
    def get(self, request):
        return Response({"items": pack_listings()})


class CheckoutSessionAPIView(APIView):
    @extend_schema(request=CheckoutSessionRequestSerializer, responses={201: CheckoutSessionResponseSerializer})
    def post(self, request):
        pack_slug = (request.data.get("pack_slug") or "").strip()
        player = get_or_create_player(request.user)
        idempotency_key = request.headers.get("Idempotency-Key", "").strip() or uuid4().hex
        if len(idempotency_key) > 255:
            return Response({"detail": "Idempotency-Key is too long."}, status=400)
        result = PaymentService().create_checkout_session(
            player=player,
            pack_slug=pack_slug,
            idempotency_key=idempotency_key,
        )
        return Response(result, status=201)


class StripeWebhookAPIView(APIView):
    """Unauthenticated by design - Stripe calls this directly. Authenticity
    comes from the signed payload, not a session/JWT."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    @extend_schema(request=None, responses={200: None})
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            try:
                PaymentService().handle_checkout_completed(session=session)
            except PaymentReconciliationError:
                # A non-2xx response asks Stripe to retry while operators repair
                # transient data/configuration issues instead of silently losing payment.
                return Response(status=409)
        return Response(status=200)
