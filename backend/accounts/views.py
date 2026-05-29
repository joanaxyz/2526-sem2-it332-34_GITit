from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

from accounts.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from accounts.services import (
    TokenBlacklistService,
    TokenService,
    UserService,
    clear_refresh_cookie,
    set_refresh_cookie,
)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService().register_student(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
        )
        return Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_service = TokenService()
        identifier = serializer.validated_data["identifier"]
        ip_address = request.META.get("REMOTE_ADDR")
        lockout_remaining = token_service.get_lockout_remaining(
            identifier=identifier,
            ip_address=ip_address,
        )
        if lockout_remaining > 0:
            return Response(
                {
                    "detail": "Too many failed attempts. Try again later.",
                    "retry_after": lockout_remaining,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = token_service.authenticate_student(
            identifier=serializer.validated_data["identifier"],
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
                    {
                        "detail": "Too many failed attempts. Try again later.",
                        "retry_after": lockout_remaining,
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            return Response(
                {"detail": "Incorrect email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token_service.clear_failed_login(identifier=identifier, ip_address=ip_address)
        tokens = token_service.issue_for_user(user, request=request)
        response = Response({"access": tokens.access, "user": UserSerializer(user).data})
        set_refresh_cookie(response, tokens.refresh)
        return response


class RefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.GIT_IT_REFRESH_COOKIE)
        try:
            tokens = TokenService().refresh_access(refresh_token)
        except TokenError:
            # Avoid clearing the refresh cookie here: refresh token rotation can cause
            # concurrent refresh requests (e.g., multiple tabs) where one succeeds and
            # another fails with a revoked token. Clearing the cookie on the failing
            # response can race and wipe a newly-rotated refresh cookie.
            return Response({"detail": "Session expired."}, status=status.HTTP_401_UNAUTHORIZED)
        response = Response({"access": tokens.access})
        set_refresh_cookie(response, tokens.refresh)
        return response


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.GIT_IT_REFRESH_COOKIE)
        if refresh_token:
            TokenBlacklistService().revoke(refresh_token)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
