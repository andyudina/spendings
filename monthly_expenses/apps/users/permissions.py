from rest_framework import permissions

from apps.bills.models import Bill


class IsBillOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a bill
    to modify any information about bill's spendings
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

