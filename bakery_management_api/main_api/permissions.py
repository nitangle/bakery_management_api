from rest_framework import permissions


class IsShopAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the shop owner/admin of the bakery.
        print('staff access{}'.format(request.user.is_staff))
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the shop owner/admin of the bakery.
        print('staff access{}'.format(request.user.is_staff))
        return request.user.is_staff

class IsOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.customer