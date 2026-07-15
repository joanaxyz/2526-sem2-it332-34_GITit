from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)
from accounts.services import (
    PasswordResetService,
    TokenBlacklistService,
    TokenService,
    UserService,
    clear_refresh_cookie,
    set_refresh_cookie,
)
from common.http import get_client_ip
from common.openapi import (
    AccessTokenResponseSerializer,
    AuthUserResponseSerializer,
    DetailResponseSerializer,
    LoginResponseSerializer,
)
from common.permissions import HasTrustedWebClientHeader


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth_register"

    @extend_schema(request=RegisterSerializer, responses={201: AuthUserResponseSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService().register_account(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny, HasTrustedWebClientHeader]

    @extend_schema(request=LoginSerializer, responses={200: LoginResponseSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_service = TokenService()
        identifier = serializer.validated_data["identifier"]
        ip_address = get_client_ip(request)
        lockout_remaining = token_service.get_lockout_remaining(
            identifier=identifier,
            ip_address=ip_address,
        )
        if lockout_remaining > 0:
            return Response(
                {"detail": "Too many failed attempts. Try again later.", "retry_after": lockout_remaining},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = token_service.authenticate_account(
            identifier=identifier,
            password=serializer.validated_data["password"],
            request=request,
        )
        if user is None:
            lockout_remaining = token_service.register_failed_login(
                identifier=identifier,
                ip_address=ip_address,
            )
            if lockout_remaining > 0:
                return Response(
                    {"detail": "Too many failed attempts. Try again later.", "retry_after": lockout_remaining},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            return Response(
                {"detail": "Incorrect username/email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token_service.clear_failed_login(identifier=identifier, ip_address=ip_address)
        tokens = token_service.issue_for_user(user, request=request)
        response = Response({"access": tokens.access, "user": UserSerializer(user).data})
        set_refresh_cookie(response, tokens.refresh)
        return response


class RefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny, HasTrustedWebClientHeader]
    throttle_scope = "auth_refresh"

    @extend_schema(request=None, responses={200: AccessTokenResponseSerializer})
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.GIT_IT_REFRESH_COOKIE)
        try:
            tokens = TokenService().refresh_access(refresh_token, request=request)
        except TokenError:
            return Response({"detail": "Session expired."}, status=status.HTTP_401_UNAUTHORIZED)
        response = Response({"access": tokens.access})
        set_refresh_cookie(response, tokens.refresh)
        return response


class LogoutAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny, HasTrustedWebClientHeader]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.GIT_IT_REFRESH_COOKIE)
        if refresh_token:
            TokenBlacklistService().revoke(refresh_token)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny, HasTrustedWebClientHeader]
    throttle_scope = "auth_password_reset"

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={200: DetailResponseSerializer},
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PasswordResetService()
        service.request(email=serializer.validated_data["email"])
        return Response({"detail": service.public_message})


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny, HasTrustedWebClientHeader]
    throttle_scope = "auth_password_reset_confirm"

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={200: DetailResponseSerializer, 400: OpenApiResponse(description="Invalid or expired reset link")},
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = PasswordResetService()
        user = service.resolve_user(
            uid=serializer.validated_data["uid"],
            token=serializer.validated_data["token"],
        )
        if user is None:
            return Response(
                {"detail": "This password reset link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service.reset(user=user, password=serializer.validated_data["password"])
        return Response({"detail": "Password reset successfully. You can now sign in."})


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=PasswordChangeSerializer, responses={200: LoginResponseSerializer})
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService().change(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            password=serializer.validated_data["password"],
        )
        tokens = TokenService().issue_for_user(request.user, request=request)
        response = Response({"access": tokens.access, "user": UserSerializer(request.user).data})
        set_refresh_cookie(response, tokens.refresh)
        return response


class RevokeOtherSessionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: DetailResponseSerializer})
    def post(self, request):
        current_jti = None
        refresh_token = request.COOKIES.get(settings.GIT_IT_REFRESH_COOKIE)
        if refresh_token:
            try:
                current_jti = str(RefreshToken(refresh_token)["jti"])
            except TokenError:
                current_jti = None
        count = TokenBlacklistService().revoke_all_for_user(request.user, except_jti=current_jti)
        return Response({"detail": f"Signed out {count} other session{'s' if count != 1 else ''}."})


class RevokeAllSessionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        TokenBlacklistService().revoke_all_for_user(request.user)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        return Response(UserSerializer(request.user).data)
