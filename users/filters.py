from django.db.models import Q, Manager
from django_filters import rest_framework as filters
from .models import CustomPermission


class CustomPermissionsFilter(filters.FilterSet):

    q = filters.CharFilter(method='q_filter')
    c_category = filters.CharFilter(method="c_category_filter")

    class Meta:
        model = CustomPermission
        fields = ('q', 'name', 'category', 'branch', 'codename')

    def q_filter(self, qs, _, value):
        return qs.filter(
            Q(name__icontains=value)
            |
            Q(category__icontains=value)
            |
            Q(branch__icontains=value)
            |
            Q(codename__icontains=value)
            |
            Q(level__icontains=value)
        ).distinct()