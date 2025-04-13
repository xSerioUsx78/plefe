from django.db.models import Q
from django.core.exceptions import FieldError
from django_filters import rest_framework as filters
from .models import Log


class LogFilter(filters.FilterSet):

    q = filters.CharFilter(method='q_filter')
    o = filters.CharFilter(method="o_filter")
    date = filters.DateFromToRangeFilter(field_name="created_at", method='date_filter')

    class Meta:
        model = Log
        fields = (
            'q', 
            'o',
            'is_authentication',
            'is_authorization',
            'is_accounting',
            'category', 
            'action',
            'date'
        )

    def q_filter(self, qs, _, value):
        return qs.filter(
            Q(title__icontains=value)
            |
            Q(user__username__icontains=value)
            |
            Q(ip_address__icontains=value)
        ).distinct()

    def o_filter(self, qs, _, value):
        try:
            return qs.order_by(value)
        except FieldError:
            return qs

    def date_filter(self, qs, _, value: slice):
        if value.start and value.stop:
            if value.start > value.stop:
                return qs
            
        if value.start:
            qs = qs.filter(created_at__gte=value.start)
        if value.stop:
            qs = qs.filter(created_at__lte=value.stop)

        return qs