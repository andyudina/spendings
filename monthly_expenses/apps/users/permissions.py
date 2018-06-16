from rest_framework import permissions

from apps.bills.models import Bill


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object
    to modify or access any object related data
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

