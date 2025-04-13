from rest_framework import generics
from . import mixins


class CustomGenericAPIView(mixins.LogMixin,
                          generics.GenericAPIView):
    """
    Overriding drf GenericAPIView class
    to implementing custom usefull stuff.
    """
    serializer_response_class = None

    def get_serializer_response(self, *args, **kwargs):
        """
        Return the serializer response instance that should be only 
        for serializing output.
        """
        serializer_response_class = self.get_serializer_response_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_response_class(*args, **kwargs)

    def get_serializer_response_class(self):
        return self.serializer_response_class or self.serializer_class


class CustomListAPIView(mixins.LogMixin,
                        generics.ListAPIView):
    pass


class CustomRetrieveAPIView(mixins.LogMixin,
                            generics.RetrieveAPIView):
    pass