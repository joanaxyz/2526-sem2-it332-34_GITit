from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and not user.is_staff)


class IsStaff(BasePermission):
    """Admin-console gate: only staff users may upload assets or manage data.

    Assets reach learners through the shop, so authoring/uploading is an
    admin-only capability. Mirrors DRF's ``IsAdminUser`` but kept local for a
    clearer 403 message alongside :class:`IsStudent`.
    """

    message = "Admin access is required."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)


class HasTrustedWebClientHeader(BasePermission):
    """Blocks cross-site HTML form posts from mutating the refresh cookie."""

    message = "This request must come from the application client."

    def has_permission(self, request, view) -> bool:
        return request.headers.get("X-Git-It-Client", "") == "web"
