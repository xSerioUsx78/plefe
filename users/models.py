import datetime
from typing import Union, List, Set, Tuple
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.utils.translation import gettext_lazy as _
from model_utils.fields import StatusField
from model_utils import Choices
from utils.models import TimestampedModel


class CustomPermission(models.Model):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50)
    branch = models.CharField(max_length=150, blank=True, null=True)
    codename = models.CharField(unique=True, max_length=150)
    level = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.codename


class User(AbstractUser):
    username_validator = ASCIIUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'), blank=True)
    permissions = models.ManyToManyField(
        CustomPermission, related_name="user_set", related_query_name="user", blank=True)
    has_full_permissions = models.BooleanField(default=False, help_text=_(
        'It shows the user has full permissions or not.'
    ))

    def c_set_permissions(self, codenames: List[str]):
        permissions = CustomPermission.objects.filter(
            codename__in=codenames
        ).values_list('id', flat=True)
        self.permissions.set(permissions)
    
    def c_add_permissions(self, codenames: List[str]):
        permissions = CustomPermission.objects.filter(
            codename__in=codenames
        ).values_list('id', flat=True)
        self.permissions.add(*permissions)

    def get_custom_permissions(self):
        return self.permissions.values_list('codename', flat=True)

    def has_access_to_all(self):
        """
        a method that will check if the user is one this:
        is_superuser, has_full_permissions
        it will return True
        """
        if any([self.is_superuser, self.has_full_permissions]):
            return True

    def c_check_perms(self, 
        user_perms: Union[List[str], Set[str], Tuple[str]], 
        perm_list: Union[List[str], Set[str], Tuple[str]], 
        has_all=True
    ):
        if has_all:
            return all(perm in user_perms for perm in perm_list)
        return any(perm in user_perms for perm in perm_list)

    def c_has_perms(self, perm_list: List[str], has_all=True):
        assert type(perm_list) == list and perm_list, 'You must provide a list of permissions'
        if self.has_access_to_all():
            return True
        user_perms = self.get_custom_permissions()
        return self.c_check_perms(user_perms, perm_list, has_all)


class UserPasswordHistory(TimestampedModel):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='password_histories'
    )
    password = models.CharField(_('password'), max_length=150)

    def __str__(self) -> str:
        return self.user.username


class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="users/profile/images", 
        default="users/profile/images/default.png"
    )

    def __str__(self):
        return self.user.username


class Setting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token_expire_duration = models.DurationField(
        default=datetime.timedelta(
            days=0, 
            hours=0, 
            minutes=30, 
            seconds=0, 
            milliseconds=0, 
            microseconds=0
        )
    )
    THEME_CHOICES = Choices('default', 'dark')
    theme = StatusField(
        choices_name='THEME_CHOICES',
        default="default"
    )

    def __str__(self):
        return self.user.username
