from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and not user.is_staff)
