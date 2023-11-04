from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated

from app.users.enums import Designation


class IsOrganizationAdminUser(IsAuthenticated, IsAdminUser):
    """
    Allows access only to Admin users.
    """

    def has_permission(self, request, view):
        if not IsAuthenticated.has_permission(self, request, view) or request.user.organization is None or (
                not IsAdminUser.has_permission(self, request, view) and request.user.designation != Designation.ADMIN.value):
            raise PermissionDenied(detail={'error': 'Access denied for non-admin users.'})
        return True


class IsOrganizationUser(IsAuthenticated, IsAdminUser):
    """
    Allows access only to Organization users.
    """

    def has_permission(self, request, view):
        if not IsAuthenticated.has_permission(self, request, view) or request.user.organization is None or (
                not IsAdminUser.has_permission(self, request, view) and request.user.designation == Designation.NOT_ASSIGNED.value):
            raise PermissionDenied(detail={'error': 'Access denied.'})
        return True


class IsWeigherUser(IsAuthenticated, IsAdminUser):
    """
    Allows access only to Weigher users.
    """

    def has_permission(self, request, view):
        if not IsAuthenticated.has_permission(self, request, view) or request.user.organization is None or (
                not IsAdminUser.has_permission(self, request, view) and request.user.designation != Designation.WEIGHER.value):
            raise PermissionDenied(detail={'error': 'Access only for Weighers.'})
        return True


class IsBillerUser(IsAuthenticated, IsAdminUser):
    """
    Allows access only to Biller users.
    """

    def has_permission(self, request, view):
        if not IsAuthenticated.has_permission(self, request, view) or request.user.organization is None or (
                not IsAdminUser.has_permission(self, request, view) and request.user.designation != Designation.BILLER.value):
            raise PermissionDenied(detail={'error': 'Access only for Billers.'})
        return True
