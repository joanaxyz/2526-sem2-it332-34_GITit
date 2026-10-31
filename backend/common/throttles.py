"""DRF policies; ordinary cache throttles are best effort, not a DoS boundary."""

from rest_framework.throttling import ScopedRateThrottle, UserRateThrottle

from common.http import get_client_ip


class TrustedScopedRateThrottle(ScopedRateThrottle):
    def get_ident(self, request):
        return get_client_ip(request) or "unknown"

    def get_cache_key(self, request, view):
        if getattr(view, "throttle_by_ip", False):
            return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}
        return super().get_cache_key(request, view)


class AuthenticatedRateThrottle(UserRateThrottle):
    """No anonymous fallback: classmates must not share the general API bucket."""

    scope = "authenticated"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return super().get_cache_key(request, view)


class TutorDailyRateThrottle(AuthenticatedRateThrottle):
    scope = "tutor_chat_daily"

    def get_cache_key(self, request, view):
        if getattr(view, "throttle_scope", None) != "tutor_chat":
            return None
        return super().get_cache_key(request, view)
