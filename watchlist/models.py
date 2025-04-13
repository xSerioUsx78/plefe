from django.db import models
from django.contrib.auth import get_user_model
from model_utils.choices import Choices
from model_utils.fields import StatusField
from utils.models import TimestampedModel
from signalapp.models import SignalCoin


User = get_user_model()


class Task(TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="watchlist_tasks"
    )
    title = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True,
        null=True
    )

    PHASE_PERFORMER = 1
    PHASE_DEPUTY = 2
    PHASE_MANAGER = 3
    PHASE_CHOICES = Choices(
        (PHASE_PERFORMER, "Performer"),
        (PHASE_DEPUTY, "Deputy"),
        (PHASE_MANAGER, "Manager")
    )
    phase = StatusField(
        choices_name='PHASE_CHOICES',
        default=1
    )
    completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title


class TaskUser(TimestampedModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="users"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="watchlist_assigned_tasks"
    )

    ROLE_MANAGER = "M"
    ROLE_DEPUTY = "D"
    ROLE_PERFORMER = "P"
    ROLE_CHOICES = Choices(
        (ROLE_MANAGER, "Manager"),
        (ROLE_DEPUTY, "Deputy"),
        (ROLE_PERFORMER, "Performer")
    )
    role = StatusField(
        choices_name='ROLE_CHOICES'
    )

    has_access = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.user.username


class TaskCoin(TimestampedModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="coins"
    )
    coin = models.ForeignKey(
        SignalCoin,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    def __str__(self) -> str:
        return self.task.title


class TaskChecklist(TimestampedModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="checklists"
    )
    text = models.TextField()
    checked = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return self.task.title


class TaskComment(TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    file = models.FileField(
        blank=True,
        null=True,
        upload_to="watchlist/task/comment/"
    )
    text = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username
