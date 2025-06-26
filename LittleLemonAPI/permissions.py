from rest_framework.permissions import BasePermission
# from django.contrib.auth.models import Group


class IsManager(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='Manager').exists()
        )


class IsDeliveryCrew(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='Delivery crew').exists()
        )


class IsCustomer(BasePermission):

    def has_permission(self, request, view):
        """
        Customers are authenticated users not
        in Manager or Delivery crew groups
        """
        return request.user.is_authenticated and not (
            request.user.groups.filter(name='Manager').exists() or
            request.user.groups.filter(name='Delivery crew').exists()
        )
