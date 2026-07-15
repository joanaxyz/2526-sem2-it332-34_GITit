from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import AccountSecurity


class VersionedJWTAuthentication(JWTAuthentication):
    """Rejects access tokens issued before a password/security change."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        token_version = int(validated_token.get("auth_version", 1))
        current_version = (
            AccountSecurity.objects.filter(user=user)
            .values_list("auth_version", flat=True)
            .first()
            or 1
        )
        if token_version != int(current_version):
            raise AuthenticationFailed("Session expired.", code="session_revoked")
        return user
