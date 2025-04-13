from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions
from utils.drf.permissions import IsSuperuserUser
from . import serializers, models


class TaskViewSet(ModelViewSet):
    permission_classes = (IsSuperuserUser,)
    serializer_class = serializers.TaskSerializer
    queryset = models.Task.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["delete"],
        detail=False,
        url_path="bulk",
        serializer_class=serializers.TaskBulkDeleteSerializer
    )
    def bulk_delete(self, *args, **kwargs):
        serializer = self.get_serializer(
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete(serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(
        methods=['GET'],
        detail=True,
        url_path='checklist',
        serializer_class=serializers.TaskChecklistSerializer,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_checklist(self, request, pk):
        obj = self.get_object()
        queryset = models.TaskChecklist.objects.filter(
            task=obj
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['PUT'],
        detail=True,
        url_path='phase',
        serializer_class=serializers.TaskPhaseSerializer,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def task_phase(self, request, pk):
        obj = self.get_object()
        context = self.get_serializer_context()
        context['task'] = obj
        serializer = self.get_serializer(
            instance=obj, 
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        methods=['PUT'],
        detail=True,
        url_path='completed',
        serializer_class=serializers.TaskCompletedSerializer
    )
    def task_completed(self, request, pk):
        obj = self.get_object()
        serializers = self.get_serializer(
            instance=obj,
            data=request.data
        )
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data)


class TaskUserViewSet(ModelViewSet):
    permission_classes = (IsSuperuserUser,)
    serializer_class = serializers.TaskUserSerializer
    queryset = models.TaskUser.objects.all()

    @action(
        methods=["delete"],
        detail=False,
        url_path="bulk",
        serializer_class=serializers.TaskUserBulkDeleteSerializer
    )
    def bulk_delete(self, *args, **kwargs):
        serializer = self.get_serializer(
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete(serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class TaskCoinViewSet(ModelViewSet):
    permission_classes = (IsSuperuserUser,)
    serializer_class = serializers.TaskCoinSerializer
    queryset = models.TaskCoin.objects.all()

    @action(
        methods=["delete", "post"],
        detail=False,
        url_path="bulk",
        url_name="bulk"
    )
    def bulk(self, *args, **kwargs):
        if self.request.method == "POST":
            self.serializer_class = serializers.TaskCoinBulkCreateSerializer
            serializer = self.get_serializer(
                data=self.request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.bulk_create(serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED)
        elif self.request.method == "DELETE":
            self.serializer_class = serializers.TaskCoinBulkDeleteSerializer
            serializer = self.get_serializer(
                data=self.request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.delete(serializer.validated_data)
            return Response(status=status.HTTP_204_NO_CONTENT)


class TaskChecklistViewSet(ModelViewSet):
    permission_classes = (IsSuperuserUser,)
    queryset = models.TaskChecklist.objects.all()
    serializer_class = serializers.TaskChecklistSerializer

    def perform_create(self, serializer):
        order = 0
        
        last_obj = self.get_queryset().filter(
            task=serializer.validated_data.get('task')
        ).order_by(
            'order'
        ).last()

        if last_obj:
            order = last_obj.order + 1

        serializer.save(order=order)

    @action(
        methods=["PUT"],
        detail=True,
        url_path='checked',
        serializer_class=serializers.TaskChecklistChangeCheckedSerializer,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def change_checked(self, request, pk):
        obj = self.get_object()
        serializer = self.get_serializer(
            instance=obj,
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)