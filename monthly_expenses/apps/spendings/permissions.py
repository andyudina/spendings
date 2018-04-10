from rest_framework import permissions

from apps.bills.models import Bill


class IsBillOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a bill
    to modify any information about bill's spendings

    Expects bill to be passed in request data
    """

    def has_permission(self, request, view):
        # Uses has_permission instead of has_permission_object
        # because bill id is passed in json params
        return Bill.objects.\
            filter(
                id=request.data.get('bill'),
                user=request.user).\
            exists()

