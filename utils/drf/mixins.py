from rest_framework import status, mixins, exceptions
from rest_framework.response import Response


class NoPagePaginationMixin:

    def paginate_queryset(self, queryset):
        paginate = self.request.query_params.get('paginate', 'true')
        possible_param_values = ['false', '0']
        if str(paginate) in possible_param_values:
            return None
        return super().paginate_queryset(queryset)


class CustomCreateModelMixin(mixins.CreateModelMixin):
    """
    Create a model instance and return
    with the specefied serializer_response_class
    """

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer_response = self.get_serializer_response(instance)
        return Response(serializer_response.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


class CustomUpdateModelMixin(mixins.UpdateModelMixin):
    """
    Update a model instance and return
    with the specefied serializer_response_class
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        
        serializer_response = self.get_serializer_response(instance)

        return Response(serializer_response.data)

    def perform_update(self, serializer):
        return serializer.save()

class LimitQueryset:

    """
    It will override get_queryset method
    and return full queryset for "is_superuser, is_staff"
    other base on their data
    """
    user_fieldname = "user"

    def get_queryset(self):
        queryset = super().get_queryset()
        if any(self.get_allowed_user_attributes()):
            return queryset
        user = self.request.user
        parameters = {self.user_fieldname: user}
        return queryset.filter(**parameters)

    def get_allowed_user_attributes(self):
        """
        Return the default user attributes that have access
        to full queryset
        """
        user = self.request.user
        return [user.is_superuser, user.is_staff]


class LogMixin:
    """
    You can use this mixin in APIView, GenericView and GenericViewSet
    to achieve it's functionality, it will override the permission_denied method
    and set call before_raising_not_authenticated_error, before_raising_permission_denied_error
    methods before raising the exception.
    """

    def permission_denied(self, request, message=None, code=None):
        if request.authenticators and not request.successful_authenticator:
            self.before_raising_not_authenticated_error()
            raise exceptions.NotAuthenticated()
        self.before_raising_permission_denied_error()
        raise exceptions.PermissionDenied(detail=message, code=code)

    def before_raising_not_authenticated_error(self):
        """
        It will return None as default, 
        override it to perform custom actions.
        """
        return

    def before_raising_permission_denied_error(self):
        """
        It will return None as default, 
        override it to perform custom actions.
        """
        return