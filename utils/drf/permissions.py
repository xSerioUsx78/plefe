from rest_framework.permissions import BasePermission


class IsSuperuserUser(BasePermission):
    """
    Also drf have a permission that called IsAdminUser
    it's for accesing the admin panel of django but we don't want that
    this is specefic for accesing the some views that is required the user have
    is_admin as True the base admin user for the applciation.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class HasPermsPermissions(BasePermission):

    """
    This permission will read the perms attribute that is defined in the class
    then checks if the user has those permissions or not.
    """
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.has_access_to_all():
            return True

        assert hasattr(view, 'perms'), 'You must provide an iterable of permissions in perms attribute!'
        perms = view.perms
        assert type(perms) in [list, set, tuple], "The specefied format is not iterable for perms!"

        has_all = True
        if hasattr(view, 'has_all'):
            assert type(has_all) == bool, "The has_all should be either True or False."
            has_all = view.has_all

        return user.c_has_perms(perms, has_all)