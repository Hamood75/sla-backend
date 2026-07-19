from rest_framework import permissions


class IsBackofficeUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'is_backoffice_user', False))


class IsOwnerOrBackoffice(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_backoffice_user', False) or user.is_superuser:
            return True
        owner = getattr(obj, 'owner', None) or getattr(obj, 'user', None)
        return owner == user
