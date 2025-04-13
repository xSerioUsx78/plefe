from django.db.models import Count
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from ipware import get_client_ip
from utils.drf.viewsets import CustomGenericViewSet
from utils.drf.pagination import CustomPageNumberPagination
from utils.drf.mixins import LimitQueryset
from activity_logger.signals import action as log_action
from activity_logger.choices import LogBadgeChoices
from .models import Log, LogDetail
from . import serializers
from . import filters


class LogViewSet(
    LimitQueryset,
    ListModelMixin, 
    CustomGenericViewSet
):
    queryset = Log.objects.annotate(
        details_count=Count('details')
    ).select_related('user').order_by('-created_at')
    serializer_class = serializers.LogSerializer
    pagination_class = CustomPageNumberPagination
    filterset_class = filters.LogFilter

    @action(
        methods=['GET'],
        detail=True,
        url_path="details",
        serializer_class=serializers.LogDetailSerializer
    )
    def get_log_details(self, request, pk):
        obj = self.get_object()
        details = LogDetail.objects.filter(
            log=obj
        )
        serializer = self.get_serializer(details, many=True)
        return Response(serializer.data)

    def before_raising_not_authenticated_error(self):
        client_ip_address = get_client_ip(self.request)
        log_action.send(
            None,
            category="log",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Authentication error",
            description=f'"{client_ip_address}" tried to access the logs.',
            ip_address=client_ip_address,
            is_authorization=True
        )

    def before_raising_permission_denied_error(self):
        user = self.request.user
        log_action.send(
            user,
            user=user,
            category="log",
            action="error",
            badge=LogBadgeChoices.RED,
            title="Permission denied error",
            description=f'"{user.username}" tried to access the logs.',
            ip_address=get_client_ip(self.request),
            is_authorization=True
        )