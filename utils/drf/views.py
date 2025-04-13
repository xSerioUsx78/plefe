from rest_framework import views
from . import mixins


class CustomAPIView(mixins.LogMixin, views.APIView):
    pass