from django.urls import path

from accounts.views import (
    EmailVerificationConfirmAPIView,
    EmailVerificationResendAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    OAuthCallbackAPIView,
    OAuthExchangeAPIView,
    OAuthStartAPIView,
    PasswordChangeAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    RefreshAPIView,
    RegisterAPIView,
    RevokeAllSessionsAPIView,
    RevokeOtherSessionsAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/", RefreshAPIView.as_view(), name="refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("me/", MeAPIView.as_view(), name="me"),
    path(
        "password-reset/request/",
        PasswordResetRequestAPIView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmAPIView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "email-verification/confirm/",
        EmailVerificationConfirmAPIView.as_view(),
        name="email-verification-confirm",
    ),
    path(
        "email-verification/resend/",
        EmailVerificationResendAPIView.as_view(),
        name="email-verification-resend",
    ),
    path(
        "oauth/<str:provider>/start/",
        OAuthStartAPIView.as_view(),
        name="oauth-start",
    ),
    path(
        "oauth/<str:provider>/callback/",
        OAuthCallbackAPIView.as_view(),
        name="oauth-callback",
    ),
    path("oauth/exchange/", OAuthExchangeAPIView.as_view(), name="oauth-exchange"),
    path("password-change/", PasswordChangeAPIView.as_view(), name="password-change"),
    path(
        "sessions/revoke-others/",
        RevokeOtherSessionsAPIView.as_view(),
        name="sessions-revoke-others",
    ),
    path("sessions/revoke-all/", RevokeAllSessionsAPIView.as_view(), name="sessions-revoke-all"),
]
