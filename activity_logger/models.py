from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from model_utils.fields import StatusField
from . import choices


User = get_user_model()


class Log(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs"
    )
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True
    )
    category = models.CharField(
        max_length=50
    )
    action = models.CharField(
        max_length=50
    )
    BADGE_CHOICES = choices.LogBadgeChoices.choices
    badge = StatusField(
        choices_name='BADGE_CHOICES',
        blank=True,
        null=True,
        default=None
    )
    title = models.CharField(
        max_length=50
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    is_authentication = models.BooleanField(default=False)
    is_authorization = models.BooleanField(default=False)
    is_accounting = models.BooleanField(default=False)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        blank=True, 
        null=True
    )
    object_id = models.PositiveBigIntegerField(
        blank=True, 
        null=True
    )
    content_object = GenericForeignKey(
        'content_type',
        'object_id',
    )
    public = models.BooleanField(default=False)
    track = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        ordering = ['-created_at']


class LogDetail(models.Model):
    log = models.ForeignKey(
        Log,
        on_delete=models.CASCADE,
        related_name='details'
    )
    title = models.CharField(max_length=50)
    description = models.CharField(
        max_length=256, 
        blank=True, 
        null=True
    )

    def __str__(self) -> str:
        return f'{self.title}: {self.description}'