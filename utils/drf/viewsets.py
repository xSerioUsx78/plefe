from rest_framework.viewsets import ViewSetMixin
from rest_framework import mixins
from . import generics
from . import mixins as c_mixins


class CustomGenericViewSet(ViewSetMixin, generics.CustomGenericAPIView):
    pass


class CustomModelViewSet(
    c_mixins.CustomCreateModelMixin,
    mixins.RetrieveModelMixin,
    c_mixins.CustomUpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    CustomGenericViewSet
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass