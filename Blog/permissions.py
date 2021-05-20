from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user == obj.author


class NotOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user != obj
