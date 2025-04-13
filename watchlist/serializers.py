from rest_framework import serializers
from signalapp import models as signal_models
from . import models


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Task
        fields = "__all__"


class TaskPhaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Task
        fields = ('phase',)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get('request')

        if request.user.is_superuser:
            return attrs
        
        task: models.Task = self.context.get('task')
        phase = attrs.get('phase')
        task_user = models.TaskUser.objects.filter(
            task=task,
            user=request.user
        ).first()
        error = serializers.ValidationError(
            "You don't have proper permissions to perform on this task"
        )
        if not task_user:
            raise error

        if task_user.role == models.TaskUser.ROLE_MANAGER:
            return attrs

        if task_user.role == models.TaskUser.ROLE_PERFORMER:
            if int(task.phase) != models.Task.PHASE_PERFORMER:
                raise error
            if phase != models.Task.PHASE_DEPUTY:
                raise error
            
        if task_user.role == models.TaskUser.ROLE_DEPUTY:
            if int(task.phase) != models.Task.PHASE_DEPUTY:
                raise error
        
        return attrs


class TaskCompletedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Task
        fields = ('completed',)


class TaskBulkDeleteSerializer(serializers.Serializer):

    ids = serializers.ListField(min_length=1)

    class Meta:
        fields = ('ids',)

    def delete(self, validated_data):
        models.Task.objects.filter(
            id__in=validated_data.get("ids", [])
        ).delete()


class TaskUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TaskUser
        fields = "__all__"


class TaskUserBulkDeleteSerializer(serializers.Serializer):

    ids = serializers.ListField(min_length=1)

    class Meta:
        fields = ('ids',)

    def delete(self, validated_data):
        models.TaskUser.objects.filter(
            id__in=validated_data.get("ids", [])
        ).delete()


class TaskCoinSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TaskCoin
        fields = "__all__"


class TaskCoinBulkDeleteSerializer(serializers.Serializer):

    ids = serializers.ListField(min_length=1)

    class Meta:
        fields = ('ids',)

    def delete(self, validated_data):
        models.TaskCoin.objects.filter(
            id__in=validated_data.get("ids", [])
        ).delete()


class TaskCoinBulkCreateSerializer(serializers.Serializer):

    task = serializers.IntegerField(required=True)
    coins_id = serializers.ListField(min_length=1)

    class Meta:
        fields = ('task', 'coins_id',)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        task_id = attrs.get("task")

        coins = signal_models.SignalCoin.objects.filter(
            id__in=attrs.get("coins_id")
        ).exclude(
            tasks__task_id=task_id
        )
        if not coins.exists():
            raise serializers.ValidationError("The selected coins not found!")
        
        task = models.Task.objects.filter(
            id=task_id
        ).first()

        if not task:
            raise serializers.ValidationError("Task not found!")

        attrs['task'] = task
        attrs['coins'] = coins
        return attrs

    def bulk_create(self, validated_data):
        task = validated_data.get('task')
        coins = validated_data.get('coins')

        task_coin_for_create = []
        for coin in coins:
            task_coin_for_create.append(
                models.TaskCoin(
                    task=task,
                    coin=coin
                )
            )
        
        models.TaskCoin.objects.bulk_create(
            task_coin_for_create,
            1000
        )


class TaskChecklistSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.TaskChecklist
        fields = '__all__'


class TaskChecklistChangeCheckedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TaskChecklist
        fields = ('checked',)