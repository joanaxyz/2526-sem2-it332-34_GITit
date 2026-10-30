from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt import exceptions as jwt_exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import get_md5_hash_password


class VersionedJWTAuthentication(JWTAuthentication):
    """Rejects access tokens issued before a password/security change.

    Every authenticated request runs this before its view, so the user, its
    security version, and its player load in one query instead of three. The
    checks match ``JWTAuthentication.get_user``.
    """

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError as exc:
            raise jwt_exceptions.InvalidToken(
                _("Token contained no recognizable user identification")
            ) from exc
        try:
            user = self.user_model.objects.select_related("account_security", "player").get(
                **{api_settings.USER_ID_FIELD: user_id}
            )
        except self.user_model.DoesNotExist as exc:
            raise jwt_exceptions.AuthenticationFailed(
                _("User not found"), code="user_not_found"
            ) from exc
        if api_settings.CHECK_USER_IS_ACTIVE and not user.is_active:
            raise jwt_exceptions.AuthenticationFailed(_("User is inactive"), code="user_inactive")
        if api_settings.CHECK_REVOKE_TOKEN and validated_token.get(
            api_settings.REVOKE_TOKEN_CLAIM
        ) != get_md5_hash_password(user.password):
            raise jwt_exceptions.AuthenticationFailed(
                _("The user's password has been changed."), code="password_changed"
            )

        token_version = int(validated_token.get("auth_version", 1))
        security = getattr(user, "account_security", None)
        current_version = (security.auth_version if security else None) or 1
        if token_version != int(current_version):
            raise AuthenticationFailed("Session expired.", code="session_revoked")
        return user
