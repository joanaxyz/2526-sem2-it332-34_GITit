import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.http import Http404, HttpResponseRedirect
from django.utils.crypto import constant_time_compare
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    AccessTokenResponseSerializer,
    DetailResponseSerializer,
    EmailVerificationConfirmSerializer,
    EmailVerificationRequiredSerializer,
    EmailVerificationResendSerializer,
    LoginSerializer,
    OAuthTicketExchangeSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
    SessionResponseSerializer,
    UserSerializer,
)
from accounts.services import (
    EmailVerificationService,
    OAuthError,
    OAuthService,
    PasswordResetService,
    TokenBlacklistService,
    TokenService,
    UserService,
    clear_refresh_cookie,
    set_refresh_cookie,
)
from common.http import get_client_ip
from common.permissions import HasTrustedWebClientHeader


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth_register"

    @extend_schema(request=RegisterSerializer, responses={201: RegisterResponseSerializer})
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

    @extend_schema(
        request=LoginSerializer,
        responses={200: SessionResponseSerializer, 403: EmailVerificationRequiredSerializer},
    )
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
                {
                    "detail": "Too many failed attempts. Try again later.",
                    "retry_after": lockout_remaining,
                },
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
                    {
                        "detail": "Too many failed attempts. Try again later.",
                        "retry_after": lockout_remaining,
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            return Response(
                {"detail": "Incorrect username/email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token_service.clear_failed_login(identifier=identifier, ip_address=ip_address)
        verification = EmailVerificationService()
        if verification.is_pending(user):
            # The password was right, so naming the account's email is safe and
            # lets the client open the code screen for it.
            verification.send_if_no_live_code(user)
            return Response(
                {
                    "detail": "Confirm your email to finish creating your account.",
                    "code": "email_unverified",
                    "email": user.email,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        update_last_login(None, user)
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
        responses={
            200: DetailResponseSerializer,
            400: OpenApiResponse(description="Invalid or expired reset link"),
        },
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


class EmailVerificationConfirmAPIView(APIView):
    permission_classes = [AllowAny, HasTrustedWebClientHeader]
    throttle_scope = "auth_email_verification"

    @extend_schema(
        request=EmailVerificationConfirmSerializer,
        responses={
            200: SessionResponseSerializer,
            400: OpenApiResponse(description="Incorrect, expired, or spent code"),
        },
    )
    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = EmailVerificationService()
        user = service.confirm(
            email=serializer.validated_data["email"],
            code=serializer.validated_data["code"],
        )
        if user is None:
            return Response(
                {"detail": service.invalid_code_message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # The code proves the inbox, so the player goes straight into the game
        # instead of retyping the password they set a minute ago.
        update_last_login(None, user)
        tokens = TokenService().issue_for_user(user, request=request)
        response = Response({"access": tokens.access, "user": UserSerializer(user).data})
        set_refresh_cookie(response, tokens.refresh)
        return response


class EmailVerificationResendAPIView(APIView):
    permission_classes = [AllowAny, HasTrustedWebClientHeader]
    throttle_scope = "auth_email_verification_resend"

    @extend_schema(
        request=EmailVerificationResendSerializer,
        responses={200: DetailResponseSerializer},
    )
    def post(self, request):
        serializer = EmailVerificationResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = EmailVerificationService()
        service.resend(email=serializer.validated_data["email"])
        return Response({"detail": service.resend_message})


OAUTH_STATE_COOKIE = "git_it_oauth_state"
OAUTH_STATE_SALT = "accounts.oauth.state"
OAUTH_STATE_MAX_AGE_SECONDS = 600
OAUTH_STATE_COOKIE_PATH = "/api/auth/oauth/"


def _oauth_result_redirect(**params) -> HttpResponseRedirect:
    """Send the browser back to the SPA, which finishes or explains the sign-in."""

    return HttpResponseRedirect(f"{settings.FRONTEND_BASE_URL}/oauth/callback?{urlencode(params)}")


class OAuthStartAPIView(APIView):
    """Browser navigation, not an API call: no session, no client header."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "auth_oauth"

    @extend_schema(exclude=True)
    def get(self, request, provider: str):
        service = OAuthService()
        if not service.is_known(provider):
            raise Http404
        if not service.is_configured(provider):
            return _oauth_result_redirect(error="unavailable")
        state = secrets.token_urlsafe(32)
        response = HttpResponseRedirect(service.authorization_url(provider, state))
        # Lax, not Strict: the provider's redirect back is a cross-site
        # top-level navigation, and the callback must still receive this cookie.
        response.set_signed_cookie(
            OAUTH_STATE_COOKIE,
            f"{provider}:{state}",
            salt=OAUTH_STATE_SALT,
            max_age=OAUTH_STATE_MAX_AGE_SECONDS,
            path=OAUTH_STATE_COOKIE_PATH,
            secure=settings.GIT_IT_REFRESH_COOKIE_SECURE,
            httponly=True,
            samesite="Lax",
        )
        return response


class OAuthCallbackAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "auth_oauth"

    @extend_schema(exclude=True)
    def get(self, request, provider: str):
        service = OAuthService()
        if not service.is_known(provider):
            raise Http404
        expected_state = request.get_signed_cookie(
            OAUTH_STATE_COOKIE,
            default=None,
            salt=OAUTH_STATE_SALT,
            max_age=OAUTH_STATE_MAX_AGE_SECONDS,
        )
        state = request.query_params.get("state", "")
        code = request.query_params.get("code", "")
        if request.query_params.get("error"):
            response = _oauth_result_redirect(error="denied")
        elif not expected_state or not constant_time_compare(expected_state, f"{provider}:{state}"):
            # Missing or mismatched state: this callback was not started here.
            response = _oauth_result_redirect(error="state")
        elif not code or not service.is_configured(provider):
            response = _oauth_result_redirect(error="provider")
        else:
            try:
                user = service.resolve_user(provider, service.fetch_profile(provider, code))
            except OAuthError as exc:
                response = _oauth_result_redirect(error=exc.code)
            else:
                response = _oauth_result_redirect(ticket=service.issue_ticket(user))
        response.delete_cookie(OAUTH_STATE_COOKIE, path=OAUTH_STATE_COOKIE_PATH, samesite="Lax")
        return response


class OAuthExchangeAPIView(APIView):
    permission_classes = [AllowAny, HasTrustedWebClientHeader]
    throttle_scope = "auth_oauth"

    @extend_schema(
        request=OAuthTicketExchangeSerializer,
        responses={
            200: SessionResponseSerializer,
            400: OpenApiResponse(description="Expired or already used sign-in ticket"),
        },
    )
    def post(self, request):
        serializer = OAuthTicketExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = OAuthService().redeem_ticket(serializer.validated_data["ticket"])
        if user is None:
            return Response(
                {"detail": "This sign-in has expired. Try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        update_last_login(None, user)
        tokens = TokenService().issue_for_user(user, request=request)
        response = Response({"access": tokens.access, "user": UserSerializer(user).data})
        set_refresh_cookie(response, tokens.refresh)
        return response


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=PasswordChangeSerializer, responses={200: SessionResponseSerializer})
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
